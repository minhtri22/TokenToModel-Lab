#!/usr/bin/env python3
"""Read-only validator for frozen TTM T5 F32 numeric evidence.

No model/llama invocation, training, TEST, data modification, or original
parity replay. All thresholds and provenance pins are immutable.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

CHECKPOINT = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
GGUF = "5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
LLAMA = "372dc5ca157276beb6c67b2e92477e8d662e964a"
LIMIT = 0.001
SENSITIVITY = 1e-5

class TraceError(ValueError):
    pass

def diagnose(data: dict) -> dict:
    if data.get("schema") != "ttm.t5.f32.numeric.localization.single.v1":
        raise TraceError("SCHEMA_MISMATCH")
    if data.get("checkpoint_sha256") != CHECKPOINT or data.get("gguf_sha256") != GGUF:
        raise TraceError("FROZEN_SOURCE_PIN_MISMATCH")
    if data.get("llama_source_commit") != LLAMA:
        raise TraceError("PINNED_LLAMA_SOURCE_MISMATCH")
    if data.get("fixed_absolute_logit_threshold") != LIMIT or data.get("non_acceptance_local_sensitivity") != SENSITIVITY:
        raise TraceError("FROZEN_THRESHOLDS_CHANGED")
    if data.get("test_read") is not False or data.get("train_steps") != 0:
        raise TraceError("SOURCE_SCOPE_MISMATCH")
    rows = data.get("rows")
    if not isinstance(rows, list) or len(rows) != 8:
        raise TraceError("REQUIRES_8_FROZEN_FIXTURES")
    outputs = []
    stage_signature = None
    for idx, row in enumerate(rows):
        if row.get("fixture_index") != idx:
            raise TraceError("FIXTURE_ORDER_MISMATCH")
        stages = row.get("stages")
        if not isinstance(stages, list) or len(stages) != 35:
            raise TraceError("STAGE_COUNT_MISMATCH")
        names = [st.get("stage") for st in stages]
        if len(set(names)) != 35:
            raise TraceError("DUPLICATE_STAGES")
        if stage_signature is None:
            stage_signature = names
        elif names != stage_signature:
            raise TraceError("STAGE_ORDER_MISMATCH")
        if names[0] != "inpL" or "ffn_inp-0" not in names or names[-1] != "result_output":
            raise TraceError("CRITICAL_STAGE_ABSENT")
        values = [st.get("max_abs") for st in stages]
        if not all(isinstance(v, (int,float)) and not isinstance(v,bool) and 0 <= v < float("inf") for v in values):
            raise TraceError("INVALID_STAGE_ERRORS")
        first_sensitive = next((st["stage"] for st in stages if st["max_abs"] > SENSITIVITY), None)
        first_stage_gt_001 = next((st["stage"] for st in stages if st["max_abs"] > LIMIT), None)
        if first_sensitive != row.get("first_over_1e5") or first_stage_gt_001 != row.get("first_over_0_001"):
            raise TraceError("FIRST_THRESHOLD_CROSSING_MISMATCH")
        if abs(stages[-1]["max_abs"] - row.get("final_max_abs", -1)) > 1e-6:
            raise TraceError("FINAL_STAGE_INCONSISTENT")
        outputs.append({
            "fixture":idx, "id_count":row.get("n_ids"),
            "inpL_max_abs":values[0],
            "ffn_inp_0_max_abs":values[names.index("ffn_inp-0")],
            "final_max_abs":row["final_max_abs"],
            "first_sensitive_stage":first_sensitive,
            "first_stage_over_0_001_diagnostic_only":first_stage_gt_001,
            "strict_final_pass":row["final_max_abs"] <= LIMIT,
        })
    if any(r["first_sensitive_stage"]!="ffn_inp-0" or r["inpL_max_abs"]!=0 for r in outputs):
        raise TraceError("FIRST_DIVERGENCE_CONTRACT_CHANGED")
    if sum(not r["strict_final_pass"] for r in outputs) != 7:
        raise TraceError("HISTORICAL_PARITY_RESULT_CHANGED")
    return {
        "schema":"ttm.t5.f32.static_numeric_recheck.v1",
        "status":"PASS_SCOPED_TRACE_CONSISTENCY_NOT_NATIVE_PARITY_PASS",
        "fixed_threshold":LIMIT, "n_fixtures":8, "n_stages_each":35,
        "strict_failures":7, "strict_max_abs":max(r["final_max_abs"] for r in outputs),
        "first_sensitive_stage_all":"ffn_inp-0",
        "root_cause_operation":"NOT_ISOLATED",
        "pending_runtime_params":["type_k","type_v","flash_attn_type"],
        "rows":outputs,
        "training":False,"test_used":False,"new_native_execution":False,
        "historical_7_of_8_fail_preserved":True,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path, help="Existing GitHub-pinned T5_F32_NUMERIC_LOCALIZATION_UNADJUDICATED.json")
    args=parser.parse_args()
    data_bytes=args.trace.read_bytes()
    report=diagnose(json.loads(data_bytes.decode("utf-8-sig")))
    report["input_sha256"]=hashlib.sha256(data_bytes).hexdigest()
    print(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True))

if __name__=="__main__":
    try:
        main()
    except (TraceError, OSError, json.JSONDecodeError) as exc:
        print("T5_STATIC_DIAGNOSTIC_FAIL_CLOSED: "+str(exc),file=sys.stderr)
        raise SystemExit(2)
