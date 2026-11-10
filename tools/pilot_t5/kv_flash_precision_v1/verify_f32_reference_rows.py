#!/usr/bin/env python3
"""Independent read-only 8x2048 P02 F32 synthetic reference validator.

No checkpoint load or native decode; validates already-produced JSONL
against exact GitHub prereg, SHA pins, and finite logits.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

PLAN_BLOB = "3b12cc1883ab20e2d9e3a92e6907586c1b4cad36"
CHECKPOINT = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
P02 = "9762343e06cf800b50574c2871ae1ed58537fb18"
EXPECTED_COLUMNS = 2048

def git_blob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def validate(plan, rows):
    if plan.get("schema") != "ttm.t5.f32_kv_flash_single_synthetic_discrimination.prereg.v1":
        raise ValueError("PREREG_SCHEMA")
    fixtures=plan["control_design"]["new_fixtures"]
    if len(fixtures)!=8 or len(rows)!=8:
        raise ValueError("FIXTURE_REFERENCE_COUNT")
    for i,(expect,r) in enumerate(zip(fixtures,rows)):
        if set(r)!={"fixture_id","token_ids","logits","checkpoint_sha256","p02_git_blob","prereg_git_blob"}:
            raise ValueError("REFERENCE_COLUMNS")
        if r["fixture_id"] != expect["fixture_id"] or r["token_ids"] != expect["ids"]:
            raise ValueError("REFERENCE_IDS_OR_ORDER")
        if (r["checkpoint_sha256"]!=CHECKPOINT or r["p02_git_blob"]!=P02
                or r["prereg_git_blob"]!=PLAN_BLOB):
            raise ValueError("REFERENCE_PROVENANCE_MISMATCH")
        values=r["logits"]
        if (not isinstance(values,list) or len(values)!=EXPECTED_COLUMNS or
                any(not isinstance(v,(int,float)) or isinstance(v,bool)
                    or not math.isfinite(v) for v in values)):
            raise ValueError("REFERENCE_NONFINITE_OR_SIZE")
    return {"status":"PASS_REFERENCE_8_OF_8_X_2048_F32_SCHEMA",
            "rows":8,"columns":EXPECTED_COLUMNS,
            "native_executed":False,"training":False,"test":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--prereg",required=True,type=Path)
    p.add_argument("--reference",required=True,type=Path)
    args=p.parse_args()
    if git_blob(args.prereg)!=PLAN_BLOB:raise ValueError("PREREG_GIT_BLOB_MISMATCH")
    plan=json.loads(args.prereg.read_text("utf-8"))
    lines=args.reference.read_text("utf-8").splitlines()
    if any(not x.strip() for x in lines):raise ValueError("BLANK_LINES")
    data=[json.loads(x) for x in lines]
    result=validate(plan,data)
    result["reference_sha256"]=sha(args.reference)
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,TypeError,OSError,json.JSONDecodeError) as exc:
        print("REFERENCE_AUDIT_FAIL_CLOSED:"+str(exc),file=sys.stderr)
        raise SystemExit(2)
