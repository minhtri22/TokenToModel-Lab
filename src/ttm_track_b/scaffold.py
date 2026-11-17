"""Track B B0/B1 deterministic synthetic engineering adapter, never science training.

Imports the original P02 architecture and P03 schedule; preserves T4's
valid-target-sum normalization and AdamW(beta=.9/.95, eps=1e-8) semantics.
"""
from __future__ import annotations
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time

import torch
from torch.nn import functional as F
from src.p02.transformer_core import GPT, P02Config
from src.p03.train_loop import TrainConfig, scheduled_lr

SCHEMA = "ttm.track_b.synthetic.train_checkpoint.v1"
DATA_SCHEMA = "ttm.track_b.synthetic.byte_windows.v1"
P04_SCHEMA = "ttm.p04.model_checkpoint.v1"
T4_SCHEMA = "ttm.t4.science.checkpoint.v1"
P02_GIT_BLOB = "9762343e06cf800b50574c2871ae1ed58537fb18"
EOS_ID = 256
VOCAB = 2048
T4_CONFIG = dict(vocab_size=2048, max_seq_len=256, n_embd=256,
                 n_layer=4, n_head=4, norm_type="layernorm")


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def require_sha(sha):
    if not isinstance(sha, str) or len(sha) != 64 or any(ch not in "0123456789abcdef" for ch in sha):
        raise ValueError("EXPECTED_LOWERCASE_SHA256")


def safe_file(path, root):
    root = Path(root).resolve(strict=True)
    path = Path(path)
    if not path.is_absolute():
        raise ValueError("ABSOLUTE_PATH_REQUIRED")
    if not path.is_file() or path.is_symlink():
        raise ValueError("MISSING_FILE_OR_SYMLINK")
    real = path.resolve(strict=True)
    if not real.is_relative_to(root) or any(p.is_symlink() for p in [path, *path.parents] if p != root):
        raise ValueError("PATH_OUTSIDE_ALLOWED_ROOT")
    return real


def write_new(path, data):
    path = Path(path)
    if path.exists() or path.is_symlink() or path.parent.is_symlink():
        raise FileExistsError("NO_OVERWRITE_OR_SYMLINK")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())
    return file_hash(path)


def spec(config):
    keys = {"seed", "context", "n_embd", "n_layer", "n_head", "steps", "batch_windows",
            "accumulation_steps", "peak_lr", "warmup_steps", "min_lr_ratio", "max_grad_norm", "weight_decay"}
    if set(config) != keys:
        raise ValueError("CONFIG_KEYS_MISMATCH")
    if any(type(config[k]) is not int for k in ("seed", "context", "n_embd", "n_layer", "n_head", "steps", "batch_windows", "accumulation_steps", "warmup_steps")):
        raise ValueError("INVALID_INTEGER_CONFIG")
    if not 1 <= config["context"] <= 256 or not 1 <= config["steps"] <= 64 or not 1 <= config["batch_windows"] <= 16 or config["batch_windows"] % config["accumulation_steps"]:
        raise ValueError("RESOURCE_OR_ACCUMULATION_BOUND")
    cfg = P02Config(vocab_size=VOCAB, max_seq_len=config["context"],
                    n_embd=config["n_embd"], n_layer=config["n_layer"],
                    n_head=config["n_head"], norm_type="layernorm")
    tr = TrainConfig(steps=config["steps"], peak_lr=config["peak_lr"],
                     warmup_steps=config["warmup_steps"], min_lr_ratio=config["min_lr_ratio"],
                     accumulation_steps=config["accumulation_steps"], max_grad_norm=config["max_grad_norm"],
                     weight_decay=config["weight_decay"])
    if config["seed"] < 0 or cfg.n_layer > 2 or cfg.n_embd > 64:
        raise ValueError("SYNTHETIC_SCAFFOLD_RESOURCE_CAP")
    return cfg, tr


def synthetic_stories():
    # Original artificial byte patterns, not excerpts from any corpus.
    train = [(f"train-{i:02d}", (bytes([65+i, 97+i, 48+i]) + b" ") * (7+i)) for i in range(6)]
    val = [(f"val-{i:02d}", (bytes([75+i, 107+i, 55+i]) + b" ") * (6+i)) for i in range(3)]
    return {"TRAIN": train, "VAL": val}


def make_windows(ids, context):
    if len(ids) < 2 or ids[-1] != EOS_ID or any(type(a) is not int or not 0 <= a <= EOS_ID for a in ids):
        raise ValueError("BAD_SYNTHETIC_TOKEN_IDS")
    windows = []
    for start in range(0, len(ids)-1, context):
        segment = ids[start:start+context+1]
        count = len(segment)-1
        windows.append({"x": segment[:-1] + [0]*(context-count),
                        "y": segment[1:] + [-100]*(context-count), "valid": count, "window_index": start // context})
    if sum(w["valid"] for w in windows) != len(ids)-1:
        raise AssertionError("TARGET_COVERAGE")
    return windows


def prepare(config):
    cfg, _ = spec(config)
    groups = synthetic_stories()
    manifest = {"schema": DATA_SCHEMA, "synthetic_only": True,
                "tokenizer": {"kind": "SYNTHETIC_BYTE_IDENTITY_V1_NOT_T4_BPE", "vocab_size": VOCAB,
                              "eos_id": EOS_ID, "byte_ids": [0,255], "unused_ids": [257,2047],
                              "tokenizer_sha256": digest(b"SYNTHETIC_BYTE_IDENTITY_V1:byte0-255:eos256:vocab2048")},
                "context": cfg.max_seq_len, "splits": {}, "windows": {}}
    for name, stories in groups.items():
        records = []
        windows = []
        for group_id, raw in stories:
            raw.decode("utf-8", errors="strict")
            ids = list(raw) + [EOS_ID]
            rec = {"group_id": group_id, "byte_sha256": digest(raw), "utf8_bytes": len(raw), "target_tokens": len(ids)-1}
            records.append(rec)
            for w in make_windows(ids, cfg.max_seq_len):
                windows.append({**w, "group_id": group_id, "source_sha256": rec["byte_sha256"]})
        manifest["splits"][name] = records
        manifest["windows"][name] = windows
    validate_pack(manifest, cfg.max_seq_len)
    manifest["data_sha256"] = digest(canonical(manifest))
    return manifest


def validate_pack(pack, context, expected_hash=None):
    if not isinstance(pack, dict) or pack.get("schema") != DATA_SCHEMA or pack.get("synthetic_only") is not True:
        raise ValueError("ONLY_SYNTHETIC_PACK_ALLOWED")
    tok = pack.get("tokenizer", {})
    if tok != {"kind": "SYNTHETIC_BYTE_IDENTITY_V1_NOT_T4_BPE", "vocab_size": VOCAB,
               "eos_id": EOS_ID, "byte_ids": [0,255], "unused_ids": [257,2047],
               "tokenizer_sha256": digest(b"SYNTHETIC_BYTE_IDENTITY_V1:byte0-255:eos256:vocab2048")}:
        raise ValueError("TOKENIZER_IDENTITY_MISMATCH")
    if pack.get("context") != context or set(pack.get("splits", {})) != {"TRAIN", "VAL"} or set(pack.get("windows", {})) != {"TRAIN", "VAL"}:
        raise ValueError("SPLIT_OR_CONTEXT_MISMATCH")
    source_ids = {}
    for split in ("TRAIN", "VAL"):
        items = pack["splits"][split]
        if not items or len({r["group_id"] for r in items}) != len(items):
            raise ValueError("DUPLICATE_GROUP")
        for r in items:
            require_sha(r["byte_sha256"])
            if r["utf8_bytes"] <= 0 or r["target_tokens"] != r["utf8_bytes"]:
                raise ValueError("BAD_SOURCE_COUNTS")
            if r["group_id"] in source_ids or r["byte_sha256"] in source_ids.values():
                raise ValueError("SPLIT_OVERLAP")
            source_ids[r["group_id"]] = r["byte_sha256"]
        by_group = {r["group_id"]: 0 for r in items}
        reconstructed = {r["group_id"]: [] for r in items}
        expected_window_index = {r["group_id"]: 0 for r in items}
        for w in pack["windows"][split]:
            n = w["valid"]
            if type(n) is not int or not 1 <= n <= context or len(w["x"]) != context or len(w["y"]) != context:
                raise ValueError("WINDOW_SHAPE")
            if w["group_id"] not in by_group or w["source_sha256"] != source_ids[w["group_id"]]:
                raise ValueError("WINDOW_SPLIT_LEAK")
            if any(type(v) is not int or not 0 <= v < VOCAB for v in w["x"]):
                raise ValueError("INPUT_IDS")
            if any(type(v) is not int or not 0 <= v <= EOS_ID for v in w["y"][:n]) or w["y"][n:] != [-100]*(context-n) or w["x"][n:] != [0]*(context-n):
                raise ValueError("MASK_OR_PADDING_INVALID")
            if n > 1 and w["x"][1:n] != w["y"][:n-1]:
                raise ValueError("SHIFTED_TARGET_ALIGNMENT")
            g = w["group_id"]
            if type(w.get("window_index")) is not int or w["window_index"] != expected_window_index[g]:
                raise ValueError("WINDOW_ORDER")
            expected_window_index[g] += 1
            if not reconstructed[g]:
                reconstructed[g].append(w["x"][0])
            elif reconstructed[g][-1] != w["x"][0]:
                raise ValueError("WINDOW_CONTINUITY")
            reconstructed[g].extend(w["y"][:n])
            by_group[g] += n
        if any(by_group[r["group_id"]] != r["target_tokens"] for r in items):
            raise ValueError("GROUP_TARGET_COVERAGE")
        for r in items:
            seq = reconstructed[r["group_id"]]
            if len(seq) != r["utf8_bytes"]+1 or seq[-1] != EOS_ID or EOS_ID in seq[:-1] or any(z>255 for z in seq[:-1]):
                raise ValueError("EOS_OR_SOURCE_LENGTH")
            raw = bytes(seq[:-1])
            raw.decode("utf-8",errors="strict")
            if digest(raw) != r["byte_sha256"]:
                raise ValueError("SOURCE_BYTE_SHA_MISMATCH")
    if expected_hash is not None:
        require_sha(expected_hash)
        if pack.get("data_sha256") != expected_hash or digest(canonical({k: v for k,v in pack.items() if k != "data_sha256"})) != expected_hash:
            raise ValueError("DATA_HASH_MISMATCH")
    return True


def cross_entropy_valid(logits, target):
    if logits.ndim != 3 or target.shape != logits.shape[:2] or target.dtype != torch.long:
        raise ValueError("LOGITS_TARGET_SHAPE")
    if not ((target == -100) | ((target >= 0) & (target < logits.shape[-1]))).all().item():
        raise ValueError("TARGET_RANGE_OR_BAD_IGNORE")
    n = int((target != -100).sum().item())
    if n == 0:
        raise ValueError("NO_VALID_TARGETS")
    return F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]), target.reshape(-1),
                           ignore_index=-100, reduction="sum") / n


def sample_batch(pack, generator, batch_windows):
    windows = pack["windows"]["TRAIN"]
    indices = torch.randint(len(windows), (batch_windows,), generator=generator).tolist()
    chosen = [windows[i] for i in indices]
    return torch.tensor([w["x"] for w in chosen], dtype=torch.long), torch.tensor([w["y"] for w in chosen], dtype=torch.long)


def train_state(config):
    cfg, tr = spec(config)
    torch.manual_seed(config["seed"])
    random.seed(config["seed"])
    model = GPT(cfg).cpu()
    opt = torch.optim.AdamW(model.parameters(), lr=tr.peak_lr, betas=(0.9,0.95),
                            eps=1e-8, weight_decay=tr.weight_decay)
    scheduler = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda=lambda i: scheduled_lr(min(i,tr.steps-1), tr)/tr.peak_lr)
    sampler = torch.Generator(device="cpu").manual_seed(config["seed"]+71)
    return model, opt, scheduler, sampler


def train_step(model, optimizer, scheduler, sampler, pack, config):
    _, tr = spec(config)
    model.train()
    x, y = sample_batch(pack, sampler, config["batch_windows"])
    optimizer.zero_grad(set_to_none=True)
    valid = int((y!=-100).sum().item())
    partial = 0.0
    micro_size = len(x)//tr.accumulation_steps
    for a in range(0, len(x), micro_size):
        b = a + micro_size
        logits, _ = model(x[a:b])
        # Sum / full step target count, not mean over windows or padded labels.
        loss = F.cross_entropy(logits.float().reshape(-1, VOCAB), y[a:b].reshape(-1),
                               ignore_index=-100, reduction="sum") / valid
        if not torch.isfinite(loss).item():
            raise FloatingPointError("NONFINITE_LOSS")
        loss.backward()
        partial += float(loss.item())
    norm = torch.nn.utils.clip_grad_norm_(model.parameters(), tr.max_grad_norm, error_if_nonfinite=True)
    for param in model.parameters():
        if param.grad is not None and not bool(torch.isfinite(param.grad).all().item()):
            raise FloatingPointError("NONFINITE_GRADIENT")
    used_lr = optimizer.param_groups[0]["lr"]
    optimizer.step()
    scheduler.step()
    return {"train_loss": partial, "valid_targets": valid, "lr_used": used_lr, "raw_grad_norm": float(norm.item())}


def checkpoint_payload(model, opt, scheduler, sampler, step, config_hash, data_hash):
    return {"schema": SCHEMA, "step": step, "model_config": asdict(model.cfg),
            "config_sha256": config_hash, "data_sha256": data_hash,
            "model": model.state_dict(), "optimizer": opt.state_dict(), "scheduler": scheduler.state_dict(),
            "sampler_state": sampler.get_state(), "torch_rng": torch.get_rng_state(),
            "python_rng": random.getstate(), "p02_git_blob": P02_GIT_BLOB}


def save_training_checkpoint(path, payload):
    path = Path(path)
    if path.exists() or path.is_symlink() or path.parent.is_symlink():
        raise FileExistsError("CHECKPOINT_NO_OVERWRITE")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as out:
        torch.save(payload, out)
        out.flush()
        os.fsync(out.fileno())
    return file_hash(path)


def load_training_checkpoint(path, sha, model, opt, scheduler, sampler, expected_config_hash, expected_data_hash):
    require_sha(sha)
    if Path(path).is_symlink() or file_hash(path) != sha:
        raise ValueError("CHECKPOINT_SHA_MISMATCH")
    data = torch.load(path, map_location="cpu", weights_only=True)
    if not isinstance(data, dict) or set(data) != {"schema", "step", "model_config", "config_sha256", "data_sha256", "model", "optimizer", "scheduler", "sampler_state", "torch_rng", "python_rng", "p02_git_blob"}:
        raise ValueError("CHECKPOINT_FIELDS")
    if data["schema"] != SCHEMA or data["p02_git_blob"] != P02_GIT_BLOB or data["model_config"] != asdict(model.cfg) or data["config_sha256"] != expected_config_hash or data["data_sha256"] != expected_data_hash:
        raise ValueError("CHECKPOINT_CONTRACT_MISMATCH")
    if type(data["step"]) is not int or not 0 <= data["step"] < 64 or scheduler.last_epoch != 0:
        raise ValueError("CHECKPOINT_STEP_OR_FRESH_STATE")
    model.load_state_dict(data["model"], strict=True)
    if any(not bool(torch.isfinite(p).all().item()) for p in model.parameters()):
        raise ValueError("NONFINITE_WEIGHTS")
    opt.load_state_dict(data["optimizer"])
    scheduler.load_state_dict(data["scheduler"])
    if scheduler.last_epoch != data["step"]:
        raise ValueError("SCHEDULER_STEP_MISMATCH")
    sampler.set_state(data["sampler_state"])
    torch.set_rng_state(data["torch_rng"])
    random.setstate(data["python_rng"])
    return data["step"]


def read_historical_checkpoint(path, sha, expected_config, tokenizer_sha, *, schema, root):
    """Read-only strict P04 or T4 adapter; rejects foreign paths and artifacts."""
    require_sha(sha)
    require_sha(tokenizer_sha)
    src = safe_file(path, root)
    if file_hash(src) != sha:
        raise ValueError("HISTORICAL_SHA_MISMATCH")
    if schema not in (P04_SCHEMA, T4_SCHEMA):
        raise ValueError("HISTORICAL_SCHEMA_DISALLOWED")
    if schema == T4_SCHEMA and expected_config != T4_CONFIG:
        raise ValueError("T4_EXACT_CONFIG_REQUIRED")
    if set(expected_config) != set(asdict(P02Config())):
        raise ValueError("CONFIG_FIELDS")
    model = GPT(P02Config(**expected_config))
    cp = torch.load(src, map_location="cpu", weights_only=True)
    if not isinstance(cp, dict) or cp.get("schema") != schema or cp.get("config") != expected_config:
        raise ValueError("HISTORICAL_CONFIG_OR_SCHEMA")
    if schema == P04_SCHEMA:
        if set(cp) != {"schema", "config", "bpe_merges_sha256", "state_dict"} or cp["bpe_merges_sha256"] != tokenizer_sha:
            raise ValueError("P04_TOKENIZER_MISMATCH")
        state = cp["state_dict"]
    else:
        if cp.get("p02_git_blob") != P02_GIT_BLOB or not isinstance(cp.get("science_lock_sha256"),str) or not isinstance(cp.get("train_pack_sha256"),str):
            raise ValueError("T4_PROVENANCE_MISSING")
        require_sha(cp["science_lock_sha256"])
        require_sha(cp["train_pack_sha256"])
        # T4's supplied tokenizer pin is external: pack manifest must attest to it before science use.
        if tokenizer_sha != cp["train_pack_sha256"]:
            raise ValueError("T4_PACK_PIN_MISMATCH")
        state = cp["model"]
        if sum(p.numel() for p in model.parameters()) != 3749376:
            raise ValueError("T4_PARAMETER_COUNT")
    if not isinstance(state, dict) or set(state) != set(model.state_dict()):
        raise ValueError("STATE_KEYS_MISMATCH")
    for key, expected in model.state_dict().items():
        if not isinstance(state[key], torch.Tensor) or state[key].shape != expected.shape or state[key].dtype != expected.dtype or not torch.isfinite(state[key]).all().item():
            raise ValueError("STATE_SHAPE_OR_FINITE_MISMATCH:"+key)
    model.load_state_dict(state, strict=True)
    return model.eval()


def evaluate(model, pack):
    model.eval()
    totals = {"nll_sum": 0., "all_targets": 0, "non_eos_nll_sum": 0., "utf8_bytes": 0, "top1_hits": 0}
    with torch.inference_mode():
        for win in pack["windows"]["VAL"]:
            x = torch.tensor([win["x"]], dtype=torch.long)
            y = torch.tensor([win["y"]], dtype=torch.long)
            logits, _ = model(x)
            valid = y!=-100
            nlls = F.cross_entropy(logits.float().reshape(-1,VOCAB), y.reshape(-1),
                                   reduction="none",ignore_index=-100).reshape_as(y)
            non_eos = valid & (y != EOS_ID)
            totals["nll_sum"] += float(nlls[valid].double().sum().item())
            totals["non_eos_nll_sum"] += float(nlls[non_eos].double().sum().item())
            totals["all_targets"] += int(valid.sum().item())
            totals["utf8_bytes"] += int(non_eos.sum().item())
            totals["top1_hits"] += int((logits.argmax(dim=-1)[valid] == y[valid]).sum().item())
    return {"split": "VAL_SYNTHETIC_DISJOINT", "nll_sum": totals["nll_sum"],
            "scored_target_tokens": totals["all_targets"],
            "mean_token_nll": totals["nll_sum"]/totals["all_targets"],
            "non_eos_nll_sum": totals["non_eos_nll_sum"],
            "scored_utf8_bytes_excluding_first_byte_and_eos": totals["utf8_bytes"],
            "bpb_excluding_first_byte_and_eos": totals["non_eos_nll_sum"]/(totals["utf8_bytes"]*math.log(2)),
            "full_vocab_top1_accuracy": totals["top1_hits"]/totals["all_targets"],
            "independent_val_targets": sum(r["target_tokens"] for r in pack["splits"]["VAL"]),
            "val_target_reuse_factor": totals["all_targets"]/sum(r["target_tokens"] for r in pack["splits"]["VAL"]),
            "semantic_quality": "NOT_VALIDATED"}


def sample(model, prefix, max_new=6, seed=1, top_k=1):
    if type(max_new) is not int or not 1 <= max_new <= model.cfg.max_seq_len or type(top_k) is not int or not 1 <= top_k <= VOCAB:
        raise ValueError("SAMPLING_BOUNDS")
    if not prefix or any(type(t) is not int or not 0 <= t <= EOS_ID for t in prefix):
        raise ValueError("PREFIX_IDS")
    if len(prefix)>=model.cfg.max_seq_len:
        raise ValueError("CONTEXT_EXCEEDED")
    generated = list(prefix)
    sampler = torch.Generator(device="cpu").manual_seed(seed)
    model.eval()
    with torch.inference_mode():
        for _ in range(min(max_new, model.cfg.max_seq_len-len(prefix))):
            logits,_ = model(torch.tensor([generated],dtype=torch.long))
            vals,idx = logits[0,-1].topk(top_k)
            if top_k==1:
                nxt = int(idx[0].item())
            else:
                p = torch.softmax(vals.double(),dim=-1)
                nxt = int(idx[int(torch.multinomial(p,1,generator=sampler).item())].item())
            generated.append(nxt)
            if nxt == EOS_ID:
                break
    return generated
