"""P04: CPU reference checkpoint, token sampling and synthetic heldout evaluation.

Only caller-supplied token IDs; no corpus reader, training loop or external downloads.
P01 F1 WP30 was permitted for BPE E0 only, not GPT train/test or publication.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import math
from pathlib import Path
import re

import torch
from torch.nn import functional as F

from src.p02.transformer_core import GPT, P02Config

SCHEMA = "ttm.p04.model_checkpoint.v1"
_SPLIT = "SYNTHETIC_HELDOUT"
_SHA = re.compile(r"[0-9a-f]{64}\Z")


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as inp:
        for chunk in iter(lambda: inp.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cpu(model: GPT) -> None:
    if any(p.device.type != "cpu" for p in model.parameters()):
        raise ValueError("P04 candidate is CPU-only")
    if model.cfg.vocab_size != 2048:
        raise ValueError("P04 requires the 2048-token P02 core")


def save_checkpoint_new(path: str | Path, model: GPT, bpe_merges_sha256: str) -> str:
    """Create, never overwrite, a weights-only checkpoint and return file SHA256."""
    _cpu(model)
    if not isinstance(bpe_merges_sha256, str) or not _SHA.fullmatch(bpe_merges_sha256):
        raise ValueError("exact BPE merges SHA256 required")
    dest = Path(path)
    if dest.is_symlink():
        raise FileExistsError("checkpoint symlink forbidden")
    payload = {
        "schema": SCHEMA,
        "config": asdict(model.cfg),
        "bpe_merges_sha256": bpe_merges_sha256,
        "state_dict": {k: v.detach().cpu().clone() for k, v in model.state_dict().items()},
    }
    with dest.open("xb") as output:
        torch.save(payload, output)
    return _sha_file(dest)


def load_checkpoint_verified(path: str | Path, expected_file_sha256: str,
                             expected_bpe_merges_sha256: str) -> GPT:
    """Hash-verify before restricted weights-only deserialization; strict keys."""
    if any(not isinstance(s, str) or not _SHA.fullmatch(s)
           for s in (expected_file_sha256, expected_bpe_merges_sha256)):
        raise ValueError("two exact SHA256 values are required")
    src = Path(path)
    if src.is_symlink():
        raise ValueError("checkpoint symlink forbidden")
    if _sha_file(src) != expected_file_sha256:
        raise ValueError("CHECKPOINT_SHA256_MISMATCH")
    data = torch.load(src, map_location="cpu", weights_only=True)
    if not isinstance(data, dict) or set(data) != {"schema", "config", "bpe_merges_sha256", "state_dict"}:
        raise ValueError("invalid checkpoint schema")
    if data["schema"] != SCHEMA or data["bpe_merges_sha256"] != expected_bpe_merges_sha256:
        raise ValueError("checkpoint schema or tokenizer pin mismatch")
    if not isinstance(data["config"], dict) or set(data["config"]) != set(asdict(P02Config())):
        raise ValueError("checkpoint config invalid")
    cfg = P02Config(**data["config"])
    if cfg.vocab_size != 2048:
        raise ValueError("checkpoint vocab not 2048")
    model = GPT(cfg)
    model.load_state_dict(data["state_dict"], strict=True)
    if not all(bool(torch.isfinite(p).all().item()) for p in model.parameters()):
        raise ValueError("checkpoint parameters nonfinite")
    return model.eval()


def generate_tokens(model: GPT, prefix: list[int], new_tokens: int,
                    *, temperature: float = 1.0, top_k: int = 1, seed: int = 123) -> list[int]:
    """Deterministic CPU sampling with a local generator, no global RNG mutation."""
    _cpu(model)
    if not isinstance(prefix, list) or not prefix or any(type(v) is not int or not 0 <= v < 2048 for v in prefix):
        raise ValueError("prefix must be nonempty token IDs in [0,2048)")
    if type(new_tokens) is not int or new_tokens < 1 or len(prefix) + new_tokens > model.cfg.max_seq_len:
        raise ValueError("generation length exceeds context")
    if type(top_k) is not int or not 1 <= top_k <= 2048:
        raise ValueError("top_k outside vocabulary")
    if not isinstance(temperature, (float, int)) or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be finite positive")
    if type(seed) is not int or seed < 0:
        raise ValueError("seed must be nonnegative integer")
    g = torch.Generator(device="cpu").manual_seed(seed)
    seq = list(prefix)
    old_mode = model.training
    try:
        model.eval()
        with torch.inference_mode():
            for _ in range(new_tokens):
                logits, _ = model(torch.tensor([seq], dtype=torch.long))
                scores = logits[0, -1].to(torch.float64) / temperature
                values, indices = torch.topk(scores, top_k)
                probabilities = torch.softmax(values, dim=0)
                sampled = int(torch.multinomial(probabilities, 1, generator=g).item())
                seq.append(int(indices[sampled].item()))
    finally:
        model.train(old_mode)
    return seq


def evaluate_synthetic_heldout(model: GPT, samples: list[tuple[list[int], list[int]]],
                               *, split: str = _SPLIT) -> dict:
    """No updates; scores only explicitly labeled synthetic-heldout token sequences."""
    _cpu(model)
    if split != _SPLIT or not isinstance(samples, list) or not samples:
        raise ValueError("only nonempty SYNTHETIC_HELDOUT is allowed")
    old_mode = model.training
    total = 0
    summed_loss = 0.0
    try:
        model.eval()
        with torch.inference_mode():
            for ids, targets in samples:
                if not isinstance(ids, list) or not isinstance(targets, list) or len(ids) != len(targets) or not 1 <= len(ids) <= model.cfg.max_seq_len:
                    raise ValueError("invalid heldout token tensors")
                if any(type(x) is not int or x < 0 or x >= 2048 for x in ids + targets):
                    raise ValueError("heldout token ID outside vocabulary")
                logits, _ = model(torch.tensor([ids], dtype=torch.long))
                loss = F.cross_entropy(logits[0], torch.tensor(targets, dtype=torch.long), reduction="sum")
                if not bool(torch.isfinite(loss).item()):
                    raise FloatingPointError("heldout loss nonfinite")
                summed_loss += float(loss.item())
                total += len(ids)
    finally:
        model.train(old_mode)
    nll = summed_loss / total
    return {"status": "SYNTHETIC_HELDOUT_SCORED", "token_count": total,
            "mean_nll": nll, "perplexity": math.exp(nll), "split": _SPLIT,
            "training_performed": False, "evaluation_only": True}
