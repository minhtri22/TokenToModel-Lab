"""Track-B integration adapter derived from pinned C M4 role/mask grammar.
Finite synthetic CPU model probe is allowed; no training or private data.
This synthetic byte codec is NOT the historical T4/P01 tokenizer.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from hashlib import sha256
import json
import re
import unicodedata

PAD, BOS, SYS, USER, ASSIST, EOT, EOS = 257, 258, 259, 260, 261, 262, 256
IGNORE = -100
ROLES = {"system": SYS, "user": USER, "assistant": ASSIST}
SPLITS = {"train", "val", "test"}

def serialize(messages: list[dict], max_len: int) -> tuple[list[int], list[int]]:
    """Return (ids, label_mask); assistant content + end/stop targets only."""
    if not isinstance(max_len, int) or isinstance(max_len, bool) or max_len < 8 or max_len > 33:
        raise ValueError("invalid max_len")
    if not isinstance(messages, list) or not messages:
        raise ValueError("empty conversation")
    ids, flags = [BOS], [0]
    expect = "user"
    for i, message in enumerate(messages):
        if not isinstance(message, dict) or set(message) != {"role", "content"}:
            raise ValueError("invalid message shape")
        role, content = message["role"], message["content"]
        if role == "system" and i == 0:
            pass
        elif role != expect:
            raise ValueError("invalid role alternation")
        else:
            expect = "assistant" if role == "user" else "user"
        if not isinstance(content, list) or not content or any(
            not isinstance(t, int) or isinstance(t, bool) or (t < 0 or t > 255) for t in content
        ):
            raise ValueError("content must be nonempty synthetic byte ids 0..255")
        mark = int(role == "assistant")
        ids.extend([ROLES[role], *content, EOT])
        flags.extend([0, *([mark] * len(content)), mark])
    if messages[-1]["role"] != "assistant":
        raise ValueError("SFT conversation must end with assistant")
    ids.append(EOS)
    flags.append(1)
    if len(ids) > max_len:
        raise ValueError("no silent truncation allowed")
    return ids, flags

def _derive_assistant_mask(ids: list[int]) -> list[int]:
    """Reparse a complete toy dialogue; caller flags cannot declare a new target.

    This establishes structural role provenance for reserved toy token IDs, NOT
    cryptographic authenticity or trust in the originating training corpus.
    """
    if not isinstance(ids, list) or len(ids) < 8 or ids[0] != BOS or ids[-1] != EOS:
        raise ValueError("invalid SFT dialogue boundary")
    if any(type(t) is not int or t < 0 for t in ids):
        raise ValueError("invalid token IDs")
    mask = [0] * len(ids)
    i, limit = 1, len(ids) - 1
    if i < limit and ids[i] == SYS:
        i += 1
        start = i
        while i < limit and 0 <= ids[i] <= 255:
            i += 1
        if i == start or i >= limit or ids[i] != EOT:
            raise ValueError("invalid system span")
        i += 1
    expect, num_turns = USER, 0
    while i < limit:
        if ids[i] != expect:
            raise ValueError("invalid role alternation or reserved ID")
        role = expect
        i += 1
        start = i
        while i < limit and 0 <= ids[i] <= 255:
            if role == ASSIST:
                mask[i] = 1
            i += 1
        if i == start or i >= limit or ids[i] != EOT:
            raise ValueError("invalid content/EOT boundary")
        if role == ASSIST:
            mask[i] = 1
        i += 1
        num_turns += 1
        expect = ASSIST if expect == USER else USER
    if num_turns < 2 or expect != USER:
        raise ValueError("SFT dialogue must end after assistant")
    mask[-1] = 1
    return mask

def build_sft_targets(messages: list[dict], max_len: int, *, codec_sha256=None, template_sha256=None, padding_side='right', packing='none'):
    """B-facing toy boundary: derive labels internally from role-checked messages.

    Never accept free-standing (ids, flags) as proof of source authenticity.
    """
    if (codec_sha256 not in (None, CODEC_SHA256) or template_sha256 not in (None, TEMPLATE_SHA256)):
        raise ValueError('TOKENIZER_OR_TEMPLATE_SHA_MISMATCH')
    if padding_side != 'right' or packing != 'none':
        raise ValueError('UNSUPPORTED_LEFT_PADDING_OR_PACKING')
    ids, flags = serialize(messages, max_len)
    return shifted_padded_targets(ids, flags, max_len)

def shifted_padded_targets(ids: list[int], flags: list[int], max_len: int):
    """Role-validate caller flags then shift; pad to IGNORE=-100 (not model auth)."""
    if not isinstance(max_len, int) or isinstance(max_len, bool) or max_len < 8 or max_len > 33:
        raise ValueError("invalid max_len")
    if not isinstance(ids, list) or not isinstance(flags, list) or len(ids) != len(flags):
        raise ValueError("invalid ids/mask")
    if len(ids) > max_len or any(type(f) is not int or f not in (0, 1) for f in flags):
        raise ValueError("invalid length or flags")
    if flags != _derive_assistant_mask(ids):
        raise ValueError("mask provenance/role mismatch")
    padded = ids + [PAD] * (max_len - len(ids))
    mask = flags + [0] * (max_len - len(ids))
    x = padded[:-1]
    y = [padded[i] if mask[i] else IGNORE for i in range(1, max_len)]
    if not any(t != IGNORE for t in y):
        raise ValueError("no supervised targets")
    return x, y


# B-owned integration contract. C source above is a grammar derivative; exact
# C version is separately frozen byte-identical at tests/ttm_track_bc/.
PACK_SCHEMA = "ttm.bc.synthetic.sft.pack.v1"
RESUME_SCHEMA = "ttm.bc.synthetic.sft.resume.v1"
CODEC_VERSION = "ttm.bc.synthetic.byte_chat_codec.v1"
TEMPLATE_VERSION = "ttm.bc.synthetic.role_bound_template.v1"
B_BASE_HEAD = "43896bcd034c82e8433bc6a2b53eefbd936616fb"
C_DESIGN_HEAD = "185d465c31f5f4bef6220be95e39dac1ae81c5b8"
C_SOURCE_BLOB = "83c6d5abe0948c24c9e49375ffc2a17e3143a793"
C_SOURCE_SHA256 = "522618430f32fd0cc74da945a7bf208aad3a146c1f113a320a13e9490f9e2b88"
SPECIAL = dict(EOS=EOS, PAD=PAD, BOS=BOS, SYS=SYS, USER=USER, ASSIST=ASSIST, EOT=EOT)
MODEL_CONFIG = dict(vocab_size=2048, max_seq_len=32, n_embd=32, n_layer=1,
                    n_head=4, norm_type="layernorm")

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf8")

def digest(obj):
    return sha256(canonical(obj)).hexdigest()

def codec_contract():
    return dict(version=CODEC_VERSION, vocab_size=2048, byte_min=0, byte_max=255,
                special=SPECIAL, historical_t4_bpe_compatible=False)

def template_contract():
    return dict(version=TEMPLATE_VERSION, layout="BOS SYS? USER ASSIST pairs EOS",
                content="raw byte ids 0..255", supervise="assistant content EOT final EOS",
                ignored="system user headers and padding", target_shift=1,
                ignore_index=-100, padding="right", packing="none")

CODEC_SHA256 = digest(codec_contract())
TEMPLATE_SHA256 = digest(template_contract())
MODEL_SHA256 = digest(MODEL_CONFIG)

def encode_bytes(data):
    if type(data) is not bytes:
        raise ValueError("EXPECTED_BYTES")
    return list(data)

def decode_bytes(ids):
    if not isinstance(ids, list) or any(type(v) is not int or not 0 <= v <= 255 for v in ids):
        raise ValueError("NON_BYTE_CONTENT_OR_SPECIAL_COLLISION")
    return bytes(ids)

def synthetic_records():
    return [
        dict(id="bc-tr-01",split="TRAIN",messages=[
            dict(role="system",content=[0,1,2]),
            dict(role="user",content=[3,4,5,6]),
            dict(role="assistant",content=[65,66])]),
        dict(id="bc-tr-02",split="TRAIN",messages=[
            dict(role="user",content=[77,78]),dict(role="assistant",content=[88]),
            dict(role="user",content=[79]),dict(role="assistant",content=[89])]),
        dict(id="bc-val-01",split="VAL",messages=[
            dict(role="user",content=[117,118]),
            dict(role="assistant",content=[119,120])])
    ]

def make_pack(max_len=33):
    rows=[]
    for row in synthetic_records():
        x,y=build_sft_targets(row["messages"],max_len)
        rows.append(dict(**row,source_sha256=digest(row["messages"]),x=x,y=y,
                         valid_targets=sum(t!=IGNORE for t in y)))
    pack=dict(schema=PACK_SCHEMA,synthetic_only=True,
              codec_sha256=CODEC_SHA256,template_sha256=TEMPLATE_SHA256,
              model_sha256=MODEL_SHA256,source_b_head=B_BASE_HEAD,
              source_c_head=C_DESIGN_HEAD,source_c_blob=C_SOURCE_BLOB,
              max_len=max_len,padding="right",packing="none",rows=rows)
    pack["pack_sha256"]=digest(pack)
    validate_pack(pack)
    return pack

def validate_pack(pack):
    if not isinstance(pack,dict) or pack.get("schema")!=PACK_SCHEMA or pack.get("synthetic_only") is not True:
        raise ValueError("OLD_B_PACK_OR_UNTRUSTED_SCHEMA")
    expected=dict(codec_sha256=CODEC_SHA256,template_sha256=TEMPLATE_SHA256,
                  model_sha256=MODEL_SHA256,source_b_head=B_BASE_HEAD,
                  source_c_head=C_DESIGN_HEAD,source_c_blob=C_SOURCE_BLOB,
                  padding="right",packing="none")
    if any(pack.get(k)!=v for k,v in expected.items()):
        raise ValueError("CODEC_TEMPLATE_SOURCE_OR_MODEL_PIN_MISMATCH")
    limit=pack.get("max_len")
    if type(limit) is not int or not 8<=limit<=33:
        raise ValueError("PACK_CONTEXT_INVALID")
    rows=pack.get("rows")
    if not isinstance(rows,list) or not 1<=len(rows)<=16:
        raise ValueError("SYNTHETIC_ROWS_INVALID")
    ids=set();sources=set();splits=set()
    for r in rows:
        if not isinstance(r,dict) or set(r)!={"id","split","messages","source_sha256","x","y","valid_targets"}:
            raise ValueError("ROW_FIELDS_INVALID")
        if not isinstance(r["id"],str) or not r["id"] or r["id"] in ids:
            raise ValueError("DUPLICATE_GROUP_ID")
        ids.add(r["id"])
        if r["split"] not in ("TRAIN","VAL"):
            raise ValueError("TRAIN_VAL_ONLY")
        splits.add(r["split"])
        source=digest(r["messages"])
        if r["source_sha256"]!=source or source in sources:
            raise ValueError("SOURCE_HASH_OR_CROSS_SPLIT_DUPLICATE")
        sources.add(source)
        x,y=build_sft_targets(r["messages"],limit)
        if r["x"]!=x or r["y"]!=y or type(r["valid_targets"]) is not int or r["valid_targets"]!=sum(t!=-100 for t in y):
            raise ValueError("SHIFT_MASK_OR_TARGET_COUNT_MISMATCH")
    if splits!={"TRAIN","VAL"}:
        raise ValueError("SPLITS_NOT_DISJOINT")
    pin=pack.get("pack_sha256")
    if not isinstance(pin,str) or len(pin)!=64 or digest({k:v for k,v in pack.items() if k!="pack_sha256"})!=pin:
        raise ValueError("PACK_SHA256_MISMATCH")
    return True

def resume_manifest(pack):
    validate_pack(pack)
    return dict(schema=RESUME_SCHEMA,codec_sha256=CODEC_SHA256,
                template_sha256=TEMPLATE_SHA256,model_sha256=MODEL_SHA256,
                pack_sha256=pack["pack_sha256"],weights="NOT_CREATED",
                optimizer="NOT_CREATED",science_executed=False)

def verify_resume_compatible(candidate,pack):
    if not isinstance(candidate,dict) or candidate!=resume_manifest(pack):
        raise ValueError("SFT_CHECKPOINT_SCHEMA_OR_TOKENIZER_INCOMPATIBLE")
    return True

def synthetic_cpu_probe():
    """One CPU P02 forward+backward, not an optimizer step or SFT train."""
    import math
    import torch
    from src.p02.transformer_core import GPT,P02Config
    from src.ttm_track_b.scaffold import cross_entropy_valid
    torch.set_num_threads(2)
    torch.manual_seed(20261116)
    pack=make_pack()
    row=pack["rows"][0]
    model=GPT(P02Config(**MODEL_CONFIG)).cpu().train()
    x=torch.tensor([row["x"]],dtype=torch.long)
    y=torch.tensor([row["y"]],dtype=torch.long)
    captured=[]
    def record(_mod,_inputs,emb):
        emb.retain_grad()
        captured.append(emb)
    hook=model.tok.register_forward_hook(record)
    try:
        logits,_=model(x)
        logits.retain_grad()
        loss=cross_entropy_valid(logits,y)
        valid=y!=-100
        oracle=(-torch.log_softmax(logits.detach().double(),dim=-1)[valid]
                .gather(1,y[valid].unsqueeze(1))).mean()
        if not math.isfinite(float(loss.item())) or abs(float(loss.item()-oracle.item()))>1e-5:
            raise AssertionError("MASKED_CE_ORACLE_DIFF")
        loss.backward()
        if not torch.equal(logits.grad[~valid],torch.zeros_like(logits.grad[~valid])):
            raise AssertionError("MASKED_DIRECT_LOGITS_GRADIENT_NONZERO")
        ids,_=serialize(row["messages"],33)
        prompt_position=ids.index(USER)+1
        context_l1=float(captured[0].grad[0,prompt_position].abs().sum().item())
        if context_l1 <= 1e-12:
            raise AssertionError("PROMPT_CONTEXT_GRADIENT_MISSING")
        if not all(p.grad is not None and torch.isfinite(p.grad).all().item() for p in model.parameters()):
            raise AssertionError("NONFINITE_GRADIENT")
        model.eval()
        candidate=x.clone()
        future_position=ids.index(ASSIST)+1
        candidate[0,future_position]=91
        with torch.inference_mode():
            a,_=model(x); b,_=model(candidate)
        if not torch.allclose(a[:,:future_position],b[:,:future_position],rtol=0,atol=0):
            raise AssertionError("CAUSAL_FUTURE_LEAK")
        first_padded_position=len(ids)
        if first_padded_position<x.shape[1]:
            candidate=x.clone()
            candidate[0,first_padded_position]=17
            with torch.inference_mode():
                pad_changed,_=model(candidate)
            if not torch.allclose(a[:,:len(ids)],pad_changed[:,:len(ids)],rtol=0,atol=0):
                raise AssertionError("RIGHT_PAD_CAUSAL_LEAK")
        return dict(status="PASS_SYNTHETIC_FORWARD_BACKWARD_ONLY",loss=float(loss.item()),
                    independent_ce_oracle=float(oracle.item()),
                    scored_assistant_targets=int(valid.sum().item()),
                    ignored_direct_targets=int((~valid).sum().item()),
                    prompt_context_grad_l1=context_l1,
                    prompt_direct_ce_grad_zero=True,causal_future_isolation=True,
                    right_padding_isolation=True,optimizer_steps=0,
                    historical_checkpoint_loaded=False,sft_science_executed=False,
                    codec_sha256=CODEC_SHA256,template_sha256=TEMPLATE_SHA256,
                    pack_sha256=pack["pack_sha256"])
    finally:
        hook.remove()
