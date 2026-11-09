#!/usr/bin/env python3
"""T6 synthetic CPU fixture: P02 no-cache vs P05 Dense KV vs P06 Paged KV.

No checkpoint, tokenizer/corpus files, GPU, TRAIN, TEST, or optimizer access.
This is a scoped engineering benchmark, NOT an inference-speedup claim or P07/P08 gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import time
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.p02.transformer_core import GPT, P02Config
from src.p05.dense_kv_cache import DenseKVCache, dense_forward_tokens
from src.p06.paged_kv_manager import PagedKVCache, paged_forward_tokens
from tools.t6.path_containment import resolve_t6_artifact

PINNED_GIT_BLOBS = {
    "src/p02/transformer_core.py": "9762343e06cf800b50574c2871ae1ed58537fb18",
    "src/p05/dense_kv_cache.py": "d835e5d7bb07fea447c5a869b13c70327ab05a53",
    "src/p06/paged_kv_manager.py": "4d52188adaf55674b6965513ea1beb38ec9a8e9b",
}
DEV_SEED = 60609
ABS_TOL = 2e-5
REL_TOL = 2e-5
WORKLOADS = {
    "short": {"prompt": [2, 19, 256, 2047], "continuation_tokens": 6},
    "medium": {"prompt": [5, 80, 14, 700, 9, 105, 1011, 22, 13, 2000, 3], "continuation_tokens": 6},
    "cross_pages": {"prompt": [7, 19, 37, 56, 9, 28, 93, 176, 2, 202, 8, 17, 1024, 31, 55, 2047], "continuation_tokens": 6},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()


def source_pins() -> dict[str, dict[str, str]]:
    receipt = {}
    for relative, expected in PINNED_GIT_BLOBS.items():
        path = ROOT / relative
        observed = git_blob(path)
        if observed != expected:
            raise RuntimeError(f"FROZEN_SOURCE_GIT_BLOB_MISMATCH:{relative}")
        receipt[relative] = {"git_blob": observed, "sha256": sha256(path)}
    return receipt


def new_cache(model: GPT, mode: str, *, block_size: int):
    cfg = model.cfg
    head_dim = cfg.n_embd // cfg.n_head
    if mode == "no_cache":
        return None
    if mode == "dense":
        return DenseKVCache(n_layers=cfg.n_layer, max_seq_len=cfg.max_seq_len,
                            n_heads=cfg.n_head, head_dim=head_dim, max_requests=1)
    if mode == "paged":
        return PagedKVCache(n_layers=cfg.n_layer,
                            n_blocks=(cfg.max_seq_len + block_size - 1) // block_size,
                            block_size=block_size, n_heads=cfg.n_head, head_dim=head_dim,
                            max_seq_len=cfg.max_seq_len, max_requests=1)
    raise ValueError("unknown backend")


def forward_last(model: GPT, mode: str, ids: list[int], cache: Any, request_id: str) -> torch.Tensor:
    if mode == "no_cache":
        return model(torch.tensor([ids], dtype=torch.long))[0][0, -1, :]
    if mode == "dense":
        return dense_forward_tokens(model, ids, cache, request_id)
    if mode == "paged":
        return paged_forward_tokens(model, ids, cache, request_id)
    raise ValueError("unknown backend")


def rss_sample_bytes() -> int | None:
    try:
        import psutil
        return int(psutil.Process(os.getpid()).memory_info().rss)
    except ImportError:
        return None


def _cache_memory(cache: Any, mode: str) -> dict[str, int]:
    if mode == "no_cache":
        return {"kv_pool_allocated_bytes": 0, "kv_request_reserved_bytes": 0,
                "kv_used_logical_bytes": 0, "kv_fragmented_bytes": 0}
    info = cache.stats()
    allocated = int(info["allocated_bytes"])
    logical = int(info["used_logical_bytes"])
    if mode == "dense":
        reserved = allocated
        fragmented = allocated - logical
    else:
        reserved = int(info["reserved_bytes"])
        fragmented = int(info["fragmented_bytes"])
        assert logical + fragmented == reserved
    return {"kv_pool_allocated_bytes": allocated,
            "kv_request_reserved_bytes": reserved,
            "kv_used_logical_bytes": logical,
            "kv_fragmented_bytes": fragmented}


@torch.inference_mode()
def run_once(model: GPT, mode: str, prompt: list[int], continuation_tokens: int,
             *, block_size: int = 4) -> dict[str, Any]:
    """Request-start through first argmax => TTFT; each subsequent argmax => TPOT.

    Cache construction/pre-allocation is measured separately (not counted in TTFT).
    Cache.start(request) is included in TTFT. Paged construction allocates full
    physical pool while Dense.start allocates its per-request storage; report both.
    """
    if not isinstance(prompt, list) or not prompt or any(type(i) is not int or not 0 <= i < 2048 for i in prompt):
        raise ValueError("invalid synthetic prompt")
    if type(continuation_tokens) is not int or not 2 <= continuation_tokens <= 16:
        raise ValueError("continuation_tokens must be 2..16 to define TPOT")
    if len(prompt) + continuation_tokens - 1 > model.cfg.max_seq_len:
        raise ValueError("context overflow")
    if model.training:
        raise ValueError("model.eval() required")
    init_t0 = time.perf_counter_ns()
    cache = new_cache(model, mode, block_size=block_size)
    init_ms = (time.perf_counter_ns() - init_t0) / 1e6
    rid = "synthetic-request"
    start_rss = rss_sample_bytes()
    start = time.perf_counter_ns()
    if cache is not None:
        cache.start(rid)
    logits = forward_last(model, mode, prompt.copy(), cache, rid)
    first = int(torch.argmax(logits).item())
    ttft_ms = (time.perf_counter_ns() - start) / 1e6
    prefill_cache_stats = _cache_memory(cache, mode)
    rss_after_prefill = rss_sample_bytes()
    generated = [first]
    all_logits = [logits.detach().clone()]
    latencies = []
    prefix = prompt.copy()
    for _ in range(continuation_tokens - 1):
        previous = generated[-1]
        step_start = time.perf_counter_ns()
        if mode == "no_cache":
            prefix.append(previous)
            next_logits = forward_last(model, mode, prefix, cache, rid)
        else:
            next_logits = forward_last(model, mode, [previous], cache, rid)
        token = int(torch.argmax(next_logits).item())
        latencies.append((time.perf_counter_ns() - step_start) / 1e6)
        generated.append(token)
        all_logits.append(next_logits.detach().clone())
    completed_cache_stats = _cache_memory(cache, mode)
    rss_end = rss_sample_bytes()
    if cache is not None:
        cache.release(rid)
        assert _cache_memory(cache, mode)["kv_used_logical_bytes"] == 0
    return {"mode": mode, "generated_tokens": generated, "all_logits": all_logits,
            "ttft_ms": ttft_ms, "tpot_step_ms": latencies, "cache_init_ms": init_ms,
            "prefill_kv": prefill_cache_stats, "after_decode_kv": completed_cache_stats,
            "rss_samples_bytes": {"request_start": start_rss,
                                  "after_prefill": rss_after_prefill,
                                  "after_decode": rss_end}}


def _max_abs_and_close(a: torch.Tensor, b: torch.Tensor) -> tuple[float, bool]:
    d = (a - b).abs()
    return float(d.max().item()), bool(torch.allclose(a, b, atol=ABS_TOL, rtol=REL_TOL))


def validate_triplet(runs: dict[str, dict]) -> dict[str, Any]:
    expected = runs["no_cache"]
    details = {}
    for other in ("dense", "paged"):
        actual = runs[other]
        if expected["generated_tokens"] != actual["generated_tokens"]:
            raise AssertionError(f"GENERATED_TOKEN_IDS_DIFFER:{other}")
        if len(expected["all_logits"]) != len(actual["all_logits"]):
            raise AssertionError("LOGITS_COUNT_DIFFER")
        max_diff = 0.0
        for i, (ref, got) in enumerate(zip(expected["all_logits"], actual["all_logits"])):
            if ref.shape != (2048,) or got.shape != (2048,):
                raise AssertionError(f"LOGIT_SHAPE_INVALID:{other}:{i}")
            if not (torch.isfinite(ref).all() and torch.isfinite(got).all()):
                raise AssertionError(f"NONFINITE_LOGITS:{other}:{i}")
            diff, close = _max_abs_and_close(ref, got)
            max_diff = max(max_diff, diff)
            if not close:
                raise AssertionError(f"LOGITS_PARITY_FAIL:{other}:position={i}:diff={diff}")
        details[other] = {"max_abs_logit_error_vs_no_cache": max_diff,
                          "matched_generated_tokens": len(actual["generated_tokens"]),
                          "logits_steps_compared": len(actual["all_logits"]),
                          "allclose_atol": ABS_TOL, "allclose_rtol": REL_TOL}
    # Non-cache is the reference for both. Also compare Dense/Paged directly.
    errs = [_max_abs_and_close(a, b) for a, b in zip(runs["dense"]["all_logits"],
                                                      runs["paged"]["all_logits"])]
    if not all(is_close for _, is_close in errs):
        raise AssertionError("DENSE_PAGED_DIRECT_LOGITS_FAIL")
    details["dense_vs_paged"] = {"max_abs_logit_error": max(d for d, _ in errs),
                                  "matched_generated_tokens": len(expected["generated_tokens"])}
    return details


def _aggregate(times: list[float]) -> dict[str, float]:
    if not times or any(not math.isfinite(t) or t <= 0 for t in times):
        raise AssertionError("INVALID_TIMING_SAMPLE")
    ordered = sorted(times)
    p95 = ordered[min(len(ordered)-1, math.ceil(0.95 * len(ordered))-1)]
    return {"median_ms": round(statistics.median(times), 6),
            "p95_nearest_rank_ms": round(p95, 6),
            "min_ms": round(ordered[0], 6),
            "max_ms": round(ordered[-1], 6)}


def measure_workload(model: GPT, name: str, spec: dict[str, Any], *, repeats: int,
                     warmups: int, block_size: int) -> dict[str, Any]:
    prompt, count = spec["prompt"], spec["continuation_tokens"]
    modes = ("no_cache", "dense", "paged")
    # Sanity comparison BEFORE measuring; measurement does not perform QA inside timings.
    correctness_runs = {m: run_once(model, m, prompt, count, block_size=block_size) for m in modes}
    correctness = validate_triplet(correctness_runs)
    # Warm up each path, then rotate measurement order by repeat to reduce order bias.
    for _ in range(warmups):
        for m in modes:
            run_once(model, m, prompt, count, block_size=block_size)
    bucket: dict[str, list[dict]] = {m: [] for m in modes}
    for r in range(repeats):
        order = modes[r % 3:] + modes[:r % 3]
        for m in order:
            run = run_once(model, m, prompt, count, block_size=block_size)
            if run["generated_tokens"] != correctness_runs["no_cache"]["generated_tokens"]:
                raise AssertionError("BENCHMARK_TOKENS_DRIFT")
            bucket[m].append(run)
    perf = {}
    for mode in modes:
        rows = bucket[mode]
        flat_tpot = [v for row in rows for v in row["tpot_step_ms"]]
        perf[mode] = {
            "ttft": _aggregate([r["ttft_ms"] for r in rows]),
            "tpot_pooled_steps": _aggregate(flat_tpot),
            "tpot_per_request_mean_ms": _aggregate([statistics.mean(r["tpot_step_ms"]) for r in rows]),
            "cache_initialization_ms": _aggregate([r["cache_init_ms"] for r in rows]) if mode != "no_cache" else None,
            "kv_after_prefill": rows[-1]["prefill_kv"],
            "kv_after_decode": rows[-1]["after_decode_kv"],
            "rss_sampled_after_decode_bytes": [r["rss_samples_bytes"]["after_decode"] for r in rows],
        }
    return {"name": name, "prompt_token_count": len(prompt),
            "continuation_token_count": count, "synthetic_prompt_sha256": hashlib.sha256(json.dumps(prompt).encode()).hexdigest(),
            "correctness": correctness, "generated_ids_sha256": hashlib.sha256(json.dumps(correctness_runs["no_cache"]["generated_tokens"]).encode()).hexdigest(),
            "performance": perf, "warmups_per_mode": warmups, "measured_repeats_per_mode": repeats}


@torch.inference_mode()
def dual_request_memory(model: GPT, *, block_size: int = 4) -> dict[str, Any]:
    """Accounting scenario: two interleaved independent requests; no timing claim.

    Compare physical allocation, request reservation and logical usage, not a
    'Paged uses less RAM' claim; its global pool is preallocated at full capacity.
    """
    cfg = model.cfg
    bpt = cfg.n_layer * 2 * cfg.n_head * (cfg.n_embd // cfg.n_head) * 4
    dense = DenseKVCache(n_layers=cfg.n_layer, max_seq_len=cfg.max_seq_len,
                         n_heads=cfg.n_head, head_dim=cfg.n_embd//cfg.n_head,
                         max_requests=2)
    paged = PagedKVCache(n_layers=cfg.n_layer,
                         n_blocks=2 * math.ceil(cfg.max_seq_len / block_size),
                         block_size=block_size, n_heads=cfg.n_head,
                         head_dim=cfg.n_embd//cfg.n_head, max_seq_len=cfg.max_seq_len,
                         max_requests=2)
    streams = {"a": list(range(1, 14)), "b": [2047, 170, 16, 30, 29]}
    for rid in streams:
        dense.start(rid)
        paged.start(rid)
    maxdiff = 0.0
    for j in range(max(map(len, streams.values()))):
        for rid, ids in streams.items():
            if j >= len(ids):
                continue
            a = dense_forward_tokens(model, [ids[j]], dense, rid)
            b = paged_forward_tokens(model, [ids[j]], paged, rid)
            err, ok = _max_abs_and_close(a, b)
            if not ok:
                raise AssertionError("MULTIREQUEST_LOGITS_PARITY_FAIL")
            maxdiff = max(maxdiff, err)
    if set(paged.page_table("a")) & set(paged.page_table("b")):
        raise AssertionError("CROSS_REQUEST_PAGE_ALIAS")
    stats_d = _cache_memory(dense, "dense")
    stats_p = _cache_memory(paged, "paged")
    if stats_d["kv_used_logical_bytes"] != stats_p["kv_used_logical_bytes"] or stats_p["kv_used_logical_bytes"] != 18*bpt:
        raise AssertionError("DUAL_REQUEST_LOGICAL_BYTES_INCONSISTENT")
    if stats_p["kv_request_reserved_bytes"] > stats_p["kv_pool_allocated_bytes"]:
        raise AssertionError("PAGED_RESERVATION_EXCEEDS_POOL")
    for rid in streams:
        freed = paged.page_table(rid)
        dense.release(rid)
        paged.release(rid)
        for pg in freed:
            if torch.count_nonzero(paged.storage[:, :, pg]).item() != 0:
                raise AssertionError("PAGED_RELEASE_NOT_SCRUBBED")
    if paged.stats()["used_blocks"] != 0 or dense.stats()["active_requests"] != 0:
        raise AssertionError("CACHE_RELEASE_LEAK")
    return {"active_requests": 2, "request_tokens": {k: len(v) for k,v in streams.items()},
            "max_abs_logit_error_dense_vs_paged": maxdiff,
            "bytes_per_token": bpt, "dense": stats_d, "paged": stats_p,
            "pool_preallocation_note": "Paged total allocated pool is not its active reservation; preallocated pool counts in physical bytes.",
            "zeroed_after_release": True}


def _ensure_safe_output(relative: str) -> Path:
    """F-01: guard direct Python entry point against junction/reparse traversal.

    No directory creation or benchmark execution before this validation.
    """
    return resolve_t6_artifact(ROOT, relative, for_write=True, suffix=".json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TTM T6 P02/P05/P06 synthetic CPU benchmark fixture")
    parser.add_argument("--output", default="artifacts/qa/t6/TTM_T6_SYNTHETIC_CPU_AB_20261109.json")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--block-size", type=int, default=4)
    args = parser.parse_args(argv)
    if type(args.repeats) is not int or not 1 <= args.repeats <= 12:
        parser.error("repeats must be 1..12")
    if not 0 <= args.warmups <= 5:
        parser.error("warmups must be 0..5")
    if not 1 <= args.block_size <= 16:
        parser.error("block-size must be 1..16")
    pins = source_pins()  # FAIL before any GPU, dataset read or result writing
    output = _ensure_safe_output(args.output)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(DEV_SEED)
    config = P02Config(vocab_size=2048, max_seq_len=32, n_embd=64,
                       n_layer=2, n_head=4, norm_type="layernorm")
    model = GPT(config).cpu().float().eval()
    if any(p.device.type != "cpu" for p in model.parameters()):
        raise AssertionError("CPU_ONLY_GATE_FAILED")
    results = [measure_workload(model, name, spec, repeats=args.repeats,
                                warmups=args.warmups, block_size=args.block_size)
               for name, spec in WORKLOADS.items()]
    dual = dual_request_memory(model, block_size=args.block_size)
    model_bytes = sum(p.numel()*p.element_size() for p in model.parameters())
    report = {
        "schema": "ttm.t6.cpu_cache_ab.synthetic.v1", "status": "PASS_SCOPED_SYNTHETIC_CPU_NO_SPEEDUP_CLAIM",
        "scope": "Synthetic BPE ID fixtures only; no real checkpoint/corpus/TEST/GPU/P07/P08/science evaluation",
        "source_pins": pins, "hardware": {"platform": platform.platform(),
                        "python": sys.version.split()[0], "torch": torch.__version__,
                        "processor": platform.processor(), "torch_threads": torch.get_num_threads(),
                        "logical_cpus": os.cpu_count(), "device": "cpu", "dtype": "float32"},
        "model": {"architecture": "P02", "seed": DEV_SEED, "model_weight_bytes": model_bytes,
                  "config": vars(config), "checkpoint": "NOT_APPLICABLE_SYNTHETIC_WEIGHTS"},
        "measurement_contract": {"ttft": "request.start (including per-request cache.start) through first argmax after prompt prefill",
                                 "tpot": "individual subsequent argmax steps on same generated-token trajectory",
                                 "cache_construction": "outside TTFT; initialization duration reported separately",
                                 "warmup_per_mode": args.warmups, "repeats_per_mode": args.repeats,
                                 "predefined_workloads": list(WORKLOADS),
                                 "fixed_order": "rotating no_cache/dense/paged order each repeat",
                                 "correctness_atol": ABS_TOL, "correctness_rtol": REL_TOL,
                                 "rss": "process RSS sampled snapshots, NOT per-path peak or exclusive allocation",
                                 "kv_memory": "exact cache tensor physical allocation, active reservation and logical bytes; model weight bytes separate",
                                 "device": platform.platform() + " CPU (measurement host)",
                                 "no_performance_claim": True},
        "workloads": results, "two_request_memory": dual,
        "non_claims": ["No T4 checkpoint or real-token model quality", "Not P07/P08 GPU capability",
                        "No universal speedup based on small CPU timings", "Not a process peak RSS measurement",
                        "No TEST or Q1/Q2 run", "No energy measurement"]}
    with output.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\n")
    print("T6_BENCHMARK_STATUS=" + report["status"])
    print("T6_OUTPUT=" + str(output.relative_to(ROOT)))
    print("T6_OUTPUT_SHA256=" + sha256(output))
    for item in results:
        print("T6_WORKLOAD=" + item["name"] + " " + json.dumps({k: {"ttft_ms": v["ttft"]["median_ms"],
                       "tpot_ms": v["tpot_per_request_mean_ms"]["median_ms"]} for k, v in item["performance"].items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
