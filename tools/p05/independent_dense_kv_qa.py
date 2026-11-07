"""Independent P05 reference using PyTorch SDPA and explicit per-layer KV lists.

No P05 KV implementation is used by the oracle. No corpus access or training.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.p02.transformer_core import GPT, P02Config
from src.p05.dense_kv_cache import DenseKVCache, dense_forward_tokens, benchmark_dense_vs_recompute


@torch.inference_mode()
def independent_sdpa_incremental(model: GPT, token_ids: list[int]) -> list[torch.Tensor]:
    """Independent sequential decode: SDPA over explicit per-layer history lists."""
    keys = [[] for _ in model.blocks]
    values = [[] for _ in model.blocks]
    outputs = []
    for pos, token in enumerate(token_ids):
        x = model.tok(torch.tensor([[token]])) + model.pos(torch.tensor([[pos]]))
        for layer, block in enumerate(model.blocks):
            attn = block.attn
            qkv = attn.qkv(block.ln1(x))
            q, k, v = qkv.reshape(1, 1, 3, attn.heads, attn.head_dim).permute(2, 0, 3, 1, 4).unbind(0)
            keys[layer].append(k)
            values[layer].append(v)
            hk = torch.cat(keys[layer], dim=2)
            hv = torch.cat(values[layer], dim=2)
            z = F.scaled_dot_product_attention(q, hk, hv, dropout_p=0.0, is_causal=False)
            z = z.transpose(1, 2).contiguous().reshape(1, 1, -1)
            x = x + attn.proj(z)
            x = x + block.mlp(block.ln2(x))
        outputs.append(model.head(model.final_ln(x))[0, -1].clone())
    return outputs


def check_sdpa_oracle() -> None:
    torch.manual_seed(505)
    m = GPT(P02Config()).eval()
    c = DenseKVCache(n_layers=2, max_seq_len=64, n_heads=4, head_dim=16)
    c.start("SDPA")
    seq = [2047, 256, 17, 1001, 0, 1024, 96, 45]
    expected = independent_sdpa_incremental(m, seq)
    for t, tok in enumerate(seq):
        got = dense_forward_tokens(m, [tok], c, "SDPA")
        torch.testing.assert_close(got, expected[t], atol=2e-5, rtol=2e-5)
    c.release("SDPA")


def check_interleaved_vs_full() -> None:
    torch.manual_seed(506)
    m = GPT(P02Config()).eval()
    c = DenseKVCache(n_layers=2, max_seq_len=64, n_heads=4, head_dim=16)
    seqs = {"alice": [0, 256, 2047, 4, 2004, 18],
            "bob": [31, 1337, 15, 2046, 0, 17]}
    for k in seqs:
        c.start(k)
    for t in range(6):
        for key, seq in seqs.items():
            got = dense_forward_tokens(m, [seq[t]], c, key)
            with torch.inference_mode():
                logits, _ = m(torch.tensor([seq[:t + 1]], dtype=torch.long))
            torch.testing.assert_close(got, logits[0, -1], atol=2e-5, rtol=2e-5)
    c.release("alice")
    c.release("bob")
    if c.stats()["allocated_bytes"] != 0:
        raise AssertionError("cache allocation retained after release")


def check_capacity_bytes() -> None:
    c = DenseKVCache(n_layers=2, max_seq_len=64, n_heads=4, head_dim=16, max_requests=2)
    c.start("a")
    expected = 2 * 2 * 64 * 4 * 16 * 4
    if c.stats()["allocated_bytes"] != expected:
        raise AssertionError("KV allocated byte count mismatch")
    c.allocate_token("a")
    if c.stats()["used_logical_bytes"] != 2 * 2 * 4 * 16 * 4:
        raise AssertionError("logical byte count mismatch")
    c.release("a")
    if c.stats()["allocated_bytes"] != 0 or c.stats()["used_logical_bytes"] != 0:
        raise AssertionError("KV not released")


def check_time_measurements_only() -> dict:
    torch.manual_seed(507)
    m = GPT(P02Config()).eval()
    r = benchmark_dense_vs_recompute(m, [0, 256, 2047, 17, 25, 1024], repeats=2)
    if not all(math.isfinite(t) and t > 0 for t in r["dense_ms"] + r["recompute_ms"]):
        raise AssertionError("timing invalid")
    if r["allocated_kv_bytes"] <= 0 or r["logical_kv_bytes"] <= 0:
        raise AssertionError("KV byte metrics missing")
    return r


def main() -> int:
    torch.set_num_threads(2)
    checks = {}
    result = None
    try:
        check_sdpa_oracle()
        checks["explicit_sdpa_incremental_oracle"] = True
        check_interleaved_vs_full()
        checks["interleaved_dense_vs_uncached"] = True
        check_capacity_bytes()
        checks["independent_kv_byte_accounting"] = True
        result = check_time_measurements_only()
        checks["cpu_wall_time_measured_no_speedup_claim"] = True
    except Exception as exc:
        import traceback
        traceback.print_exc(file=sys.stderr)
        checks["failure"] = repr(exc)
    status = "PASS" if len(checks) == 4 and all(v is True for v in checks.values()) else "FAIL"
    print(json.dumps({"schema": "ttm.p05.independent_cpu_synthetic_qa.v1", "status": status,
                      "checks": checks, "measurements": result,
                      "P01_TEST": "NOT_READ", "P03_TRAINING": "NOT_EXECUTED",
                      "no_real_corpus": True, "torch": torch.__version__}, sort_keys=True))
    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
