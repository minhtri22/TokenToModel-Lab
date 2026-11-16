"""BC-F01..F04 additive v2 C-string→B-byte bridge; engineering-only, no SFT training.

V1 adapter, its canonical bytes, SHA evidence and prior CI are deliberately untouched.
Source-of-truth C reference is the exact C Part A oracle pinned separately in tests.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from typing import Any
import json
import math
import os

from src.ttm_track_b import bc_sft_interface as b

BYTE_MAX = 255
VOCAB = 2048
SPECIAL = dict(b.SPECIAL)
IGNORE = -100
OLD_B_SCHEMA = "ttm.track_b.synthetic.byte_windows.v1"
OLD_BC_SCHEMA = "ttm.bc.synthetic.sft.pack.v1"
C_V1_SCHEMA = "ttm.bc.synthetic.sft_pack.v1"
SCHEMA = "ttm.bc.synthetic.sft_pack.v2"
CHECKPOINT_SCHEMA = "ttm.bc.synthetic.sft_checkpoint.v2"
CHAT_TEMPLATE_SCHEMA = "ttm.bc.synthetic.chat_template.v2"
CANONICAL_SCHEMA = "ttm.bc.canonical_json_utf8_sorted_compact_lf.v2"
BRIDGE_SCHEMA = "ttm.bc.c_string_to_b_bytes.v2"
MAX_MODEL_CONTEXT = 32
B_BASE_HEAD = b.B_BASE_HEAD
C_ORACLE_HEAD = "56c18e2a00714c8a1c118dabc0ede9d2a1b34b17"
C_ORACLE_BLOB = "233c678c89afc3471af4addc55f827e0c52b0383"
PM_HANDOFF_HEAD = "40788f557799c7c8a688df32271510aab73a9180"
ARTIFACT_NAMES = {
    "tokenizer_sha256": "tokenizer.json",
    "chat_template_sha256": "chat_template.json",
    "serialized_inputs_sha256": "serialized_inputs.json",
    "target_masks_sha256": "target_masks.json",
    "target_labels_sha256": "target_labels.json",
    "config_sha256": "config.json",
    "checkpoint_schema_sha256": "checkpoint_schema.json",
}
REQUIRED = frozenset(ARTIFACT_NAMES)
ROLES = {"system": SPECIAL["SYS"], "user": SPECIAL["USER"],
         "assistant": SPECIAL["ASSIST"]}
ORACLE_SEED = 20261116


def canonical(obj: Any) -> bytes:
    """V2: UTF-8, sorted, compact, no NFC, exactly one terminal LF, binary IO."""
    # Strict JSON rejects NaN and invalid surrogate code points during UTF8 encoding.
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8", errors="strict")


def sha(data: bytes) -> str:
    if type(data) is not bytes:
        raise TypeError("HASH_ONLY_ACTUAL_BYTES")
    return sha256(data).hexdigest()


def encode_bytes(raw: bytes) -> list[int]:
    return b.encode_bytes(raw)


def decode_bytes(ids: list[int]) -> bytes:
    return b.decode_bytes(ids)


def validate_codec() -> bool:
    assert SPECIAL == {"EOS": 256, "PAD": 257, "BOS": 258, "SYS": 259,
                       "USER": 260, "ASSIST": 261, "EOT": 262}
    assert len(set(SPECIAL.values())) == 7 and max(SPECIAL.values()) < VOCAB
    return True


def to_byte_messages(messages: list[dict]) -> list[dict]:
    """Strict C typed entry: exact role/str, no lossy conversion, NFC or coercion."""
    if not isinstance(messages, list) or not messages:
        raise ValueError("C_MESSAGES_NOT_LIST")
    out = []
    for msg in messages:
        if type(msg) is not dict or set(msg) != {"role", "content"}:
            raise ValueError("C_MESSAGE_SHAPE")
        role, content = msg["role"], msg["content"]
        if type(role) is not str or role not in ROLES or type(content) is not str or not content:
            raise ValueError("C_ROLE_OR_CONTENT_TYPE")
        # A lone surrogate fails here; it must never be replaced with U+FFFD.
        raw = content.encode("utf-8", errors="strict")
        if not raw or raw.decode("utf-8", errors="strict") != content:
            raise ValueError("UTF8_ROUNDTRIP_FAIL")
        out.append({"role": role, "content": list(raw)})
    return out


def from_byte_messages(messages: list[dict]) -> list[dict]:
    """Only valid UTF-8 bytes may be materialized as C strings; raw B bytes stay B."""
    if not isinstance(messages, list) or not messages:
        raise ValueError("B_MESSAGES_NOT_LIST")
    out = []
    for msg in messages:
        if type(msg) is not dict or set(msg) != {"role", "content"}:
            raise ValueError("B_MESSAGE_SHAPE")
        role, content = msg["role"], msg["content"]
        if type(role) is not str or role not in ROLES:
            raise ValueError("B_ROLE_INVALID")
        raw = decode_bytes(content)
        if not raw:
            raise ValueError("EMPTY_BYTE_CONTENT")
        out.append({"role": role, "content": raw.decode("utf-8", errors="strict")})
    return out


def serialize(messages: list[dict], max_len: int) -> tuple[list[int], list[int]]:
    """C typed string wire; same grammar as C Part A, including 256-token source QA."""
    validate_codec()
    if type(max_len) is not int or not 8 <= max_len <= 257:
        raise ValueError("MAX_LEN_OUTSIDE_SYNTHETIC_BOUND")
    payload = to_byte_messages(messages)
    ids, flags = [SPECIAL["BOS"]], [0]
    expected = "user"
    for i, msg in enumerate(payload):
        role = msg["role"]
        if role == "system" and i == 0:
            pass
        elif role != expected:
            raise ValueError("ROLE_ORDER_INVALID")
        else:
            expected = "assistant" if role == "user" else "user"
        content = msg["content"]
        mark = int(role == "assistant")
        ids.extend([ROLES[role], *content, SPECIAL["EOT"]])
        flags.extend([0, *([mark] * len(content)), mark])
    if payload[-1]["role"] != "assistant":
        raise ValueError("FINAL_ASSISTANT_REQUIRED")
    ids.append(SPECIAL["EOS"])
    flags.append(1)
    if len(ids) > max_len:
        raise ValueError("NO_SILENT_TRUNCATION")
    if flags != b._derive_assistant_mask(ids):
        raise ValueError("ROLE_MASK_PROVENANCE_MISMATCH")
    return ids, flags


def derive_mask(ids: list[int]) -> list[int]:
    return b._derive_assistant_mask(ids)


def targets(ids: list[int], flags: list[int], max_len: int) -> tuple[list[int],list[int]]:
    if type(max_len) is not int or not 8 <= max_len <= 257:
        raise ValueError("MAX_LEN_OUTSIDE_SYNTHETIC_BOUND")
    # b.shifted_padded_targets accepts C-shaped max length only up to 33.
    if not isinstance(ids, list) or len(ids) > max_len:
        raise ValueError("INVALID_IDS_LENGTH")
    if (not isinstance(flags, list) or len(flags) != len(ids)
            or any(type(f) is not int or f not in (0,1) for f in flags)):
        raise ValueError("FLAGS_INVALID")
    if flags != derive_mask(ids):
        raise ValueError("ROLE_MASK_PROVENANCE_MISMATCH")
    padded = ids + [SPECIAL["PAD"]] * (max_len - len(ids))
    m = flags + [0] * (max_len - len(ids))
    x = padded[:-1]
    y = [padded[j] if m[j] else IGNORE for j in range(1, max_len)]
    if not any(v != IGNORE for v in y):
        raise ValueError("ALL_IGNORE")
    return x,y


def build(messages: list[dict], max_len: int) -> tuple[list[int],list[int]]:
    ids, flags = serialize(messages, max_len)
    return targets(ids, flags, max_len)


def raw_b_byte_only(messages: list[dict], max_len: int) -> tuple[list[int],list[int]]:
    """Explicit separate byte path. Does NOT claim C text provenance or roundtrip."""
    if type(max_len) is not int or not 8 <= max_len <= MAX_MODEL_CONTEXT + 1:
        raise ValueError("B_NATIVE_CONTEXT_BOUND")
    for msg in messages:
        if type(msg) is not dict or type(msg.get("content")) is not list:
            raise ValueError("RAW_B_BYTES_REQUIRED")
    return b.build_sft_targets(messages, max_len)


def synthetic_fixture() -> list[dict]:
    return [
        {"id": "bc-v2-tr-01", "split": "TRAIN", "messages": [
            {"role": "user", "content": "\u0000🇻🇳"},
            {"role": "assistant", "content": "chào"}]},
        {"id": "bc-v2-tr-02", "split": "TRAIN", "messages": [
            {"role": "user", "content": "[ASSIST]"},
            {"role": "assistant", "content": "ok"}]},
        {"id": "bc-v2-val-01", "split": "VAL", "messages": [
            {"role": "system", "content": "P"},
            {"role": "user", "content": "é"},
            {"role": "assistant", "content": "ạ"}]}
    ]


def _bundle_documents() -> dict[str,dict]:
    fixture = synthetic_fixture()
    rows_input, rows_masks, rows_labels = [], [], []
    distinct = set()
    for row in fixture:
        ids, flags = serialize(row["messages"], MAX_MODEL_CONTEXT + 1)
        x, y = targets(ids, flags, MAX_MODEL_CONTEXT + 1)
        fingerprint = sha(canonical(row["messages"]))
        if fingerprint in distinct:
            raise ValueError("SPLIT_SOURCE_DUPLICATE")
        distinct.add(fingerprint)
        unshifted = flags.copy()
        shifted = [int(v!=IGNORE) for v in y]
        rows_input.append({"id":row["id"],"split":row["split"],
                           "messages":row["messages"],"declared_roles_authenticated":False,
                           "source_sha256":fingerprint,"serialized_ids":ids,
                           "x":x})
        rows_masks.append({"id":row["id"],"unshifted_assistant_flags":unshifted,
                           "shifted_target_mask":shifted})
        rows_labels.append({"id":row["id"],"y":y,
                            "valid_target_count":sum(shifted)})
    return {
        "tokenizer_sha256": {
            "schema":"ttm.bc.synthetic.byte_codec.v2","bridge_schema":BRIDGE_SCHEMA,
            "vocab_size":VOCAB, "byte_content_ids":[0,BYTE_MAX], "special_ids":SPECIAL,
            "real_t4_bpe_compatible":False,
        },
        "chat_template_sha256": {
            "schema":CHAT_TEMPLATE_SCHEMA,"role_order":"optional_system_then_user_assistant_pairs",
            "content":"C_STR_UTF8_IDENTITY_TO_B_BYTES_0_255",
            "normalization":"NONE", "utf8_errors":"strict",
            "stop":"ASSISTANT_EOT_AND_SINGLE_FINAL_EOS",
            "padding":"RIGHT_ONLY","packing":"DISABLED",
            "target_shift":1,"ignore_index":IGNORE,
            "canonical_format":CANONICAL_SCHEMA,
        },
        "serialized_inputs_sha256": {
            "schema":"ttm.bc.synthetic.serialized_inputs.v2","rows":rows_input,
            "source_role_authenticity":"DECLARED_UNVERIFIED","input_source":"LOCAL_SYNTHETIC_ONLY",
        },
        "target_masks_sha256": {
            "schema":"ttm.bc.synthetic.target_masks.v2", "rows":rows_masks,
        },
        "target_labels_sha256": {
            "schema":"ttm.bc.synthetic.target_labels.v2", "rows":rows_labels,
        },
        "config_sha256": {
            "schema":"ttm.bc.synthetic.run_config.v2",
            "model":{"vocab_size":2048,"max_seq_len":32,"n_embd":32,"n_layer":1,
                     "n_head":4,"norm_type":"layernorm"},
            "execution":{"device":"CPU_ONLY","optimizer_steps":0,
                         "max_model_context":MAX_MODEL_CONTEXT,
                         "max_minutes_ci":15,"max_threads":2,
                         "hard_memory_job_object":"NOT_ATTESTED_ON_OWNER_HOST"},
            "frozen_sources":{"b_base_sha":B_BASE_HEAD,"c_oracle_sha":C_ORACLE_HEAD,
                              "c_oracle_git_blob":C_ORACLE_BLOB,
                              "pm_handoff_sha":PM_HANDOFF_HEAD},
        },
        "checkpoint_schema_sha256": {
            "schema":CHECKPOINT_SCHEMA,"scope":"METADATA_ONLY_NO_ACTUAL_CHECKPOINT",
            "resume_enabled":False,"weights":"NOT_CREATED",
            "optimizer_state":"NOT_CREATED","incompatible_with":[
                OLD_B_SCHEMA, OLD_BC_SCHEMA, C_V1_SCHEMA,
                "ttm.bc.synthetic.sft.resume.v1",
                "ttm.p04.model_checkpoint.v1",
                "ttm.t4.science.checkpoint.v1"],
            "required_artifact_hash_fields":sorted(REQUIRED),
        },
    }


def _check_manifest_shape(m:dict) -> None:
    if not isinstance(m,dict) or m.get("schema")!=SCHEMA:
        raise ValueError("NOT_BC_SFT_PACK_V2")
    if m.get("checkpoint_schema")!=CHECKPOINT_SCHEMA:
        raise ValueError("CHECKPOINT_SCHEMA_VERSION")
    if m.get("canonical_schema")!=CANONICAL_SCHEMA:
        raise ValueError("CANONICAL_POLICY_MISMATCH")
    if m.get("source_c_oracle_head")!=C_ORACLE_HEAD or m.get("source_b_head")!=B_BASE_HEAD:
        raise ValueError("SOURCE_PIN_MISMATCH")
    if m.get("synthetic_only") is not True or m.get("no_science") is not True:
        raise ValueError("SCIENCE_SCOPE_VIOLATION")
    if any(type(m.get(k)) is not str or len(m[k]) != 64 or any(c not in "0123456789abcdef" for c in m[k]) for k in REQUIRED):
        raise ValueError("SHA_FIELD_INVALID")


def _check_contents(documents:dict) -> None:
    # Verify C typed inputs have B same target bytes, not just SHA labels.
    sources=set(); splits=set()
    ins=documents["serialized_inputs_sha256"]["rows"]
    masks=documents["target_masks_sha256"]["rows"]
    labels=documents["target_labels_sha256"]["rows"]
    if not (len(ins)==len(masks)==len(labels)==3):
        raise ValueError("ROWS_MISSING")
    for original,mask,label in zip(ins,masks,labels):
        key=original.get("id")
        if key != mask.get("id") or key != label.get("id"):
            raise ValueError("ROW_ID_MISMATCH")
        if original.get("declared_roles_authenticated") is not False:
            raise ValueError("UNAUTHENTICATED_ROLE_CLAIM")
        msgs=original["messages"]
        source=sha(canonical(msgs))
        if source!=original.get("source_sha256") or source in sources:
            raise ValueError("DUPLICATE_OR_BAD_SOURCE_SHA")
        sources.add(source); splits.add(original["split"])
        ids, flags=serialize(msgs,MAX_MODEL_CONTEXT+1)
        x,y=targets(ids,flags,MAX_MODEL_CONTEXT+1)
        if original["serialized_ids"] != ids or original["x"]!=x:
            raise ValueError("WRONG_SERIALIZED_INPUT_OR_SHIFT")
        if mask["unshifted_assistant_flags"]!=flags or mask["shifted_target_mask"] != [int(z!=IGNORE) for z in y]:
            raise ValueError("WRONG_ROLE_MASK")
        if label["y"]!=y or label["valid_target_count"]!=sum(z!=IGNORE for z in y):
            raise ValueError("WRONG_TARGET_LABELS")
    if splits!={"TRAIN","VAL"}:
        raise ValueError("SPLITS_NOT_DISJOINT")
    expected=_bundle_documents()
    # Lock all present source/config/template bytes; forged recomputed digest cannot
    # silently mutate the frozen engineering fixture.
    if documents != expected:
        raise ValueError("FROZEN_DOCUMENTS_CHANGED")


def write_bundle(root: Path | str) -> dict:
    """Create binary-encoded seven files + manifest. No overwrite ever."""
    path=Path(root)
    if path.is_symlink():
        raise ValueError("SYMLINK_OUTPUT_FORBIDDEN")
    path.mkdir(parents=False,exist_ok=False)
    documents=_bundle_documents()
    _check_contents(documents)
    digests={}
    for key,name in ARTIFACT_NAMES.items():
        raw=canonical(documents[key])
        destination=path/name
        with destination.open("xb") as w:
            w.write(raw)
            w.flush()
            os.fsync(w.fileno())
        readback=destination.read_bytes()
        if readback!=raw:
            raise ValueError("ARTIFACT_BYTE_READBACK_MISMATCH")
        digests[key]=sha(readback)
    manifest={
        "schema":SCHEMA,
        "checkpoint_schema":CHECKPOINT_SCHEMA,
        "canonical_schema":CANONICAL_SCHEMA,
        "bridge_schema":BRIDGE_SCHEMA,
        "synthetic_only":True,"no_science":True,
        "source_b_head":B_BASE_HEAD,
        "source_c_oracle_head":C_ORACLE_HEAD,
        "artifact_filenames":ARTIFACT_NAMES.copy(),
        "input_record_count":3,
        **digests,
    }
    (path/"manifest.json").write_bytes(canonical(manifest))
    verify_bundle(path)
    return manifest


def verify_bundle(root:Path | str) -> dict:
    """Read actual file bytes anew, not only manifest-provided digest labels."""
    path=Path(root)
    if not path.is_dir() or path.is_symlink():
        raise ValueError("BUNDLE_PATH_INVALID")
    if set(p.name for p in path.iterdir()) != {*ARTIFACT_NAMES.values(),"manifest.json"}:
        raise ValueError("BUNDLE_FILE_SET_MISMATCH")
    raw_manifest=(path/"manifest.json").read_bytes()
    m=json.loads(raw_manifest.decode("utf-8",errors="strict"))
    if raw_manifest != canonical(m):
        raise ValueError("MANIFEST_CANONICAL_BYTES_MISMATCH")
    _check_manifest_shape(m)
    if m.get("artifact_filenames")!=ARTIFACT_NAMES or m.get("input_record_count")!=3:
        raise ValueError("ARTIFACT_FILENAME_OR_COUNT_MISMATCH")
    documents={}
    for key,name in ARTIFACT_NAMES.items():
        p=path/name
        if p.is_symlink() or not p.is_file():
            raise ValueError("SYMLINK_OR_MISSING_ARTIFACT")
        raw=p.read_bytes()
        if len(raw)>1000000 or raw!=canonical(json.loads(raw.decode("utf-8",errors="strict"))):
            raise ValueError("NONCANONICAL_OR_OVERSIZED_ARTIFACT:"+key)
        if sha(raw)!=m[key]:
            raise ValueError("ARTIFACT_SHA_READBACK_MISMATCH:"+key)
        documents[key]=json.loads(raw.decode("utf-8"))
    _check_contents(documents)
    return m


def verify_legacy_rejected(value:dict) -> bool:
    _check_manifest_shape(value)
    return True


def synthetic_cpu_probe_v2():
    """One P02 CPU forward/backward on C text-originated tokens, no optimizer."""
    import torch
    from src.p02.transformer_core import GPT,P02Config
    from src.ttm_track_b.scaffold import cross_entropy_valid
    torch.set_num_threads(2)
    torch.manual_seed(20261117)
    m=synthetic_fixture()[0]["messages"]
    ids, flags=serialize(m,MAX_MODEL_CONTEXT+1)
    x, y=targets(ids,flags,MAX_MODEL_CONTEXT+1)
    tx=torch.tensor([x],dtype=torch.long)
    ty=torch.tensor([y],dtype=torch.long)
    model=GPT(P02Config(vocab_size=2048,max_seq_len=32,n_embd=32,
                        n_layer=1,n_head=4,norm_type="layernorm")).cpu().train()
    captures=[]
    def capture(_mod,_args,out):
        if out.requires_grad:
            out.retain_grad()
            captures.append(out)
    hook=model.tok.register_forward_hook(capture)
    try:
        logits,_=model(tx)
        logits.retain_grad()
        valid=ty.ne(IGNORE)
        loss=cross_entropy_valid(logits,ty)
        independent=-(torch.log_softmax(logits.detach().double(),dim=-1)[valid]
                      .gather(1,ty[valid].unsqueeze(1))).mean()
        if not math.isfinite(loss.item()) or abs(loss.item()-independent.item())>1e-5:
            raise AssertionError("V2_CE_ORACLE_MISMATCH")
        loss.backward()
        if torch.count_nonzero(logits.grad[~valid]).item()!=0:
            raise AssertionError("V2_DIRECT_PROMPT_LOGIT_CE_NOT_ZERO")
        user_byte_position=ids.index(SPECIAL["USER"])+1
        grad_l1=captures[0].grad[0,user_byte_position].abs().sum().item()
        if grad_l1<=1e-12:
            raise AssertionError("V2_PROMPT_CONTEXT_GRADIENT_ZERO")
        if not all(p.grad is not None and torch.isfinite(p.grad).all().item() for p in model.parameters()):
            raise AssertionError("V2_PARAMETER_GRADIENT_NONFINITE")
        model.eval()
        future_position=ids.index(SPECIAL["ASSIST"])+1
        future=tx.clone();future[0,future_position]=73
        with torch.inference_mode():
            orig,_=model(tx);new_future,_=model(future)
        if not torch.equal(orig[:,:future_position],new_future[:,:future_position]):
            raise AssertionError("V2_CAUSAL_FUTURE_LEAK")
        if len(ids)<tx.shape[1]:
            padding=tx.clone();padding[0,len(ids)]=21
            with torch.inference_mode():
                new_pad,_=model(padding)
            if not torch.equal(orig[:,:len(ids)],new_pad[:,:len(ids)]):
                raise AssertionError("V2_RIGHT_PADDING_LEAK")
        return dict(mode="C_STRING_TO_B_BYTE_P02_CPU",valid=int(valid.sum().item()),
                    ignored=int((~valid).sum().item()),loss=loss.item(),
                    oracle=independent.item(),prompt_context_grad_l1=grad_l1,
                    direct_prompt_target_ce_zero=True,causal_isolated=True,
                    padding_isolated=True,optimizer_steps=0,
                    historical_weights_loaded=False,science_executed=False)
    finally:
        hook.remove()
