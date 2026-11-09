#!/usr/bin/env python3
"""Independent read-only check of T6 synthetic CPU report + source/protocol pins.

Checks persisted numbers by separate arithmetic, not timing repeat or model inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
 sys.path.insert(0, str(ROOT))
from tools.t6.path_containment import resolve_t6_artifact
BLOBS={
 "src/p02/transformer_core.py":"9762343e06cf800b50574c2871ae1ed58537fb18",
 "src/p05/dense_kv_cache.py":"d835e5d7bb07fea447c5a869b13c70327ab05a53",
 "src/p06/paged_kv_manager.py":"4d52188adaf55674b6965513ea1beb38ec9a8e9b",
}


def file_sha(path: Path) -> str:
 return hashlib.sha256(path.read_bytes()).hexdigest()


def blob_sha(path: Path) -> str:
 b=path.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()


def audit(report: dict, *, unittest_log: str | None=None) -> dict:
 checks={}
 def ck(name,ok):
  checks[name]="PASS" if ok else "FAIL"
  if not ok:raise AssertionError("T6_INDEPENDENT_QA_FAIL:"+name)
 ck("status_exact",report["status"]=="PASS_SCOPED_SYNTHETIC_CPU_NO_SPEEDUP_CLAIM")
 ck("synthetic_scope",report["scope"].startswith("Synthetic BPE ID fixtures only") and report["model"]["checkpoint"]=="NOT_APPLICABLE_SYNTHETIC_WEIGHTS")
 ck("device_cpu_fp32",report["hardware"]["device"]=="cpu" and report["hardware"]["dtype"]=="float32")
 ck("no_speedup_claim",report["measurement_contract"]["no_performance_claim"] is True)
 ck("source_blobs_exact",all(blob_sha(ROOT/k)==v==report["source_pins"][k]["git_blob"] for k,v in BLOBS.items()))
 ck("source_sha256_recomputed",all(file_sha(ROOT/k)==report["source_pins"][k]["sha256"] for k in BLOBS))
 cfg=report["model"]["config"]
 ck("model_fixture_configuration",cfg=={"vocab_size":2048,"max_seq_len":32,"n_embd":64,"n_head":4,"n_layer":2,"norm_type":"layernorm"})
 ck("seed_exact",report["model"]["seed"]==60609)
 ck("all_workload_names",[w["name"] for w in report["workloads"]]==["short","medium","cross_pages"])
 ck("same_generated_token_budget",all(w["continuation_token_count"]==6 for w in report["workloads"]))
 ck("prompt_lengths",[w["prompt_token_count"] for w in report["workloads"]]==[4,11,16])
 ck("three_methods_present",all(set(w["performance"])=={"no_cache","dense","paged"} for w in report["workloads"]))
 ck("each_method_synthetic_timing_positive",all(
  all(w["performance"][m][k]["median_ms"]>0 and w["performance"][m][k]["p95_nearest_rank_ms"]>=w["performance"][m][k]["median_ms"] for k in ["ttft","tpot_pooled_steps","tpot_per_request_mean_ms"])
  for w in report["workloads"] for m in ("no_cache","dense","paged")))
 ck("correctness_logits_six_positions",all(w["correctness"][m]["logits_steps_compared"]==6 for w in report["workloads"] for m in ("dense","paged")))
 ck("allclose_thresholds_locked",all(w["correctness"][m]["allclose_atol"]==2e-5 and w["correctness"][m]["allclose_rtol"]==2e-5 for w in report["workloads"] for m in ("dense","paged")))
 ck("max_abs_logits_below_threshold",all(w["correctness"][m]["max_abs_logit_error_vs_no_cache"]<=2e-5 for w in report["workloads"] for m in ("dense","paged")))
 ck("dense_paged_direct_exact_in_this_fixture",all(w["correctness"]["dense_vs_paged"]["max_abs_logit_error"]==0 for w in report["workloads"]))
 bpt=cfg["n_layer"]*2*cfg["n_head"]*(cfg["n_embd"]//cfg["n_head"])*4
 ck("bytes_per_token_exact",bpt==1024 and report["two_request_memory"]["bytes_per_token"]==bpt)
 ck("model_bytes_separate",report["model"]["model_weight_bytes"]>0)
 ck("noncached_persistent_kv_zero",all(all(w["performance"]["no_cache"][stage][k]==0 for k in ("kv_pool_allocated_bytes","kv_request_reserved_bytes","kv_used_logical_bytes","kv_fragmented_bytes")) for w in report["workloads"] for stage in ("kv_after_prefill","kv_after_decode")))
 ck("dense_memory_math",all(w["performance"]["dense"][stage]["kv_pool_allocated_bytes"]==32768 and w["performance"]["dense"][stage]["kv_request_reserved_bytes"]==32768 and w["performance"]["dense"][stage]["kv_fragmented_bytes"]==32768-w["performance"]["dense"][stage]["kv_used_logical_bytes"] for w in report["workloads"] for stage in ("kv_after_prefill","kv_after_decode")))
 ck("paged_memory_math",all(w["performance"]["paged"][stage]["kv_pool_allocated_bytes"]==32768 and w["performance"]["paged"][stage]["kv_fragmented_bytes"]==w["performance"]["paged"][stage]["kv_request_reserved_bytes"]-w["performance"]["paged"][stage]["kv_used_logical_bytes"] for w in report["workloads"] for stage in ("kv_after_prefill","kv_after_decode")))
 ck("logical_usage_matches_prefill_and_decode",all(w["performance"][m]["kv_after_prefill"]["kv_used_logical_bytes"]==w["prompt_token_count"]*bpt and w["performance"][m]["kv_after_decode"]["kv_used_logical_bytes"]==(w["prompt_token_count"]+5)*bpt for w in report["workloads"] for m in ("dense","paged")))
 dual=report["two_request_memory"]
 ck("dual_request_inputs",dual["active_requests"]==2 and dual["request_tokens"]=={"a":13,"b":5})
 ck("dual_request_logical_bytes",dual["dense"]["kv_used_logical_bytes"]==dual["paged"]["kv_used_logical_bytes"]==18*bpt)
 ck("dual_request_dense_allocated",dual["dense"]["kv_pool_allocated_bytes"]==64*bpt)
 ck("dual_request_paged_allocated_pool",dual["paged"]["kv_pool_allocated_bytes"]==64*bpt)
 ck("dual_request_paged_reserved",dual["paged"]["kv_request_reserved_bytes"]==24*bpt)
 ck("dual_request_zeroed",dual["zeroed_after_release"] is True)
 ck("dual_request_logit_parity",math.isfinite(dual["max_abs_logit_error_dense_vs_paged"]) and dual["max_abs_logit_error_dense_vs_paged"]<=2e-5)
 ck("no_real_dataset_fields",all("dataset" not in str(x).lower() for x in (report["model"]["checkpoint"],report["model"]["config"])) )
 ck("no_model_training_metadata",not any("optimizer" in key or "train_loss" in key for key in report))
 if unittest_log is not None:
  ck("unittest_16_success",bool(re.search(r"Ran 16 tests in [\d.]+s\s+OK\s*$",unittest_log)))
 return {"schema":"ttm.t6.independent_material_qa.v1","status":f"PASS_{len(checks)}_OF_{len(checks)}_SCOPED_MATERIAL_AND_ARITHMETIC", "checks":checks,
 "independence":"Separate QA parser and formulas; NOT external scientific reviewer or hardware cross-platform validation",
 "no_new_inference":True,"no_test_data":True,"no_training":True,"no_gpu":True}


def main(argv=None):
 ap=argparse.ArgumentParser()
 ap.add_argument("--report",default="artifacts/qa/t6/TTM_T6_SYNTHETIC_CPU_AB_20261109.json")
 ap.add_argument("--unittest-log",default="artifacts/qa/t6/TTM_T6_UNITTEST_20261109.log")
 ap.add_argument("--output",default="artifacts/qa/t6/TTM_T6_INDEPENDENT_QA_20261109.json")
 args=ap.parse_args(argv)
 # Guard all three direct-Python paths before reading or writing any file.
 source = resolve_t6_artifact(ROOT, args.report, for_write=False, suffix=".json")
 logfile = resolve_t6_artifact(ROOT, args.unittest_log, for_write=False, suffix=".log")
 out = resolve_t6_artifact(ROOT, args.output, for_write=True, suffix=".json")
 report=json.loads(source.read_text(encoding="utf8"))
 res=audit(report,unittest_log=logfile.read_text(encoding="utf8"))
 res["inputs"]={"benchmark_report_sha256":file_sha(source),"unittest_log_sha256":file_sha(logfile)}
 with out.open("x",encoding="utf8") as f:json.dump(res,f,indent=2,sort_keys=True);f.write("\n")
 print(res["status"])
 print("T6_INDEPENDENT_QA_SHA256="+file_sha(out))
 return 0

if __name__=='__main__':sys.exit(main())
