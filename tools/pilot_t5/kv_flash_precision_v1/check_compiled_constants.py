#!/usr/bin/env python3
"""Validate a NO-MODEL --self-check JSON against pinned F32 KV/Flash prereg.

Never invokes llama.cpp or reads checkpoint. Must run after a separately
attested binary build and its self-check (no native inference).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

SCHEMA = "ttm.t5.kvflash.compiled_constants.v1"
PREREG_SHA1 = "3b12cc1883ab20e2d9e3a92e6907586c1b4cad36"
EXPECTED_ARMS = [
    {"id":"S0","kv":"F16","flash":"ENABLED"},
    {"id":"S1","kv":"F32","flash":"DISABLED"},
    {"id":"S2","kv":"F32","flash":"ENABLED"},
    {"id":"S3","kv":"F16","flash":"DISABLED"},
]

def git_blob(path):
    b = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def check(plan, probe):
    if plan.get("schema") != "ttm.t5.f32_kv_flash_single_synthetic_discrimination.prereg.v1":
        raise ValueError("FROZEN_PREREG_SCHEMA_MISMATCH")
    if (probe.get("schema") != SCHEMA or probe.get("native_inference") is not False
            or probe.get("model_loaded") is not False):
        raise ValueError("NOT_NONINFERENCE_SELF_CHECK")
    expected = [{"fixture_id":f["fixture_id"],"token_ids":f["ids"]}
                for f in plan["control_design"]["new_fixtures"]]
    if probe.get("fixtures") != expected:
        raise ValueError("BINARY_FIXTURES_DIVERGE_FROM_GITHUB_PREREG")
    if probe.get("arms") != EXPECTED_ARMS:
        raise ValueError("BINARY_2X2_ARM_MAPPING_DIVERGES")
    if len(expected)!=8 or len(probe["arms"])!=4 or plan["control_design"]["expected_runs"]!=32:
        raise ValueError("PROTOCOL_SIZE_CHANGED")
    return {"status":"PASS_COMPILED_CONSTANTS_SCOPED","fixtures":8,"arms":4,
            "native_decode_executed":False,"training":False,"test":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True,type=Path)
    ap.add_argument("--self-check-json",required=True,type=Path)
    args=ap.parse_args()
    if git_blob(args.prereg)!=PREREG_SHA1:
        raise ValueError("GITHUB_PREREG_GIT_BLOB_MISMATCH")
    plan=json.loads(args.prereg.read_text(encoding="utf-8"))
    probe=json.loads(args.self_check_json.read_text(encoding="utf-8"))
    print(json.dumps(check(plan,probe),sort_keys=True))

if __name__=="__main__":
    try:
        main()
    except (ValueError,KeyError,OSError,json.JSONDecodeError) as ex:
        print("TTM_COMPILED_CONSTANTS_FAIL_CLOSED:"+str(ex),file=sys.stderr)
        raise SystemExit(2)
