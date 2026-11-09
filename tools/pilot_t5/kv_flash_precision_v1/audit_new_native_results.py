#!/usr/bin/env python3
"""Fail-closed evaluator of the NEW 4x8 synthetic KV/Flash probe.

No modification to old parity evidence. Requires the independent F32 P02
reference generated on the same fresh frozen token-ID set.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

EXPECTED_ARMS={
    "S0":("F16","ENABLED"),
    "S1":("F32","DISABLED"),
    "S2":("F32","ENABLED"),
    "S3":("F16","DISABLED"),
}
PREREG_SCHEMA="ttm.t5.f32_kv_flash_single_synthetic_discrimination.prereg.v1"

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as fp:
        for chunk in iter(lambda:fp.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()

def jsonl(path):
    with open(path,"r",encoding="utf-8") as handle:
        for i,line in enumerate(handle,1):
            if not line.strip():raise ValueError(f"BLANK_JSONL_LINE:{i}")
            yield json.loads(line)

def valid_logits(v):
    return (isinstance(v,list) and len(v)==2048 and
            all(isinstance(x,(float,int)) and not isinstance(x,bool) and math.isfinite(x) for x in v))

def argmax(v):
    return max(range(len(v)),key=lambda i:v[i])

def evaluate(plan, references, samples):
    if plan.get("schema")!=PREREG_SCHEMA:raise ValueError("PREREG_SCHEMA_MISMATCH")
    if plan["original_pins"]["final_logits_acceptance_max_abs"]!=0.001:
        raise ValueError("FROZEN_THRESHOLD_CHANGED")
    fixtures={v["fixture_id"]:v["ids"] for v in plan["control_design"]["new_fixtures"]}
    if len(fixtures)!=8:raise ValueError("BAD_FIXTURE_COUNT")
    if len(references)!=8 or len(samples)!=32:raise ValueError("REQUIRES_8_REFERENCES_AND_32_NATIVE_ROWS")
    ref={}
    for row in references:
        name=row.get("fixture_id")
        if name not in fixtures or name in ref or row.get("token_ids")!=fixtures[name] or not valid_logits(row.get("logits")):
            raise ValueError("REFERENCE_SOURCE_OR_LOGITS_INVALID")
        ref[name]=row["logits"]
    readings={}
    for row in samples:
        key=(row.get("fixture_id"),row.get("arm_id"))
        if key in readings or key[0] not in fixtures or key[1] not in EXPECTED_ARMS:
            raise ValueError("MISSING_OR_DUPLICATE_OR_UNEXPECTED_ARM")
        expected_kv,expected_flash=EXPECTED_ARMS[key[1]]
        if (row.get("token_ids")!=fixtures[key[0]] or row.get("kv_type")!=expected_kv or
            row.get("flash")!=expected_flash or not valid_logits(row.get("logits"))):
            raise ValueError("NATIVE_SOURCE_CONFIG_OR_LOGITS_INVALID")
        nodes=row.get("flash_nodes_observed")
        if not isinstance(nodes,int) or isinstance(nodes,bool) or nodes<0:
            raise ValueError("FLASH_NODE_COUNTER_INVALID")
        if (expected_flash=="ENABLED" and nodes==0) or (expected_flash=="DISABLED" and nodes!=0):
            raise ValueError("ACTUAL_FLASH_GRAPH_MISMATCH")
        result=row["logits"]
        delta=[abs(a-b) for a,b in zip(ref[key[0]],result)]
        readings[key]={
            "fixture_id":key[0],"arm_id":key[1],
            "max_abs_vs_p02_f32":max(delta),
            "mean_abs_vs_p02_f32":sum(delta)/len(delta),
            "top1_equal":argmax(ref[key[0]])==argmax(result),
            "strict_pass_at_0_001":max(delta)<=0.001,
            "flash_nodes_observed":nodes,
        }
    if len(readings)!=32:raise ValueError("MISSING_NATIVE_ARM_FIXTURE_PAIR")
    ordered=[readings[(f,a)] for f in fixtures for a in EXPECTED_ARMS]
    contrasts={}
    for f in fixtures:
        errs={a:readings[(f,a)]["max_abs_vs_p02_f32"] for a in EXPECTED_ARMS}
        contrasts[f]={
            "cache_effect_without_flash_S3_minus_S1":errs["S3"]-errs["S1"],
            "flash_effect_with_F32_cache_S2_minus_S1":errs["S2"]-errs["S1"],
            "flash_effect_with_F16_cache_S0_minus_S3":errs["S0"]-errs["S3"],
            "full_2x2_interaction":(errs["S0"]-errs["S3"])-(errs["S2"]-errs["S1"]),
        }
    return {
        "schema":"ttm.t5.kvflash.fresh_synthetic_diagnostic.adjudication.v1",
        "status":"COMPLETED_NEW_SYNTHETIC_MEASUREMENT_NOT_HISTORICAL_PARITY_REWRITE",
        "note":"Root cause still requires interpretation of counters, context provenance and effect patterns.",
        "frozen_historical_strict_failures":7,
        "fixed_final_logit_threshold":0.001,
        "rows":ordered,"descriptive_contrasts":contrasts,
        "arm_strict_pass_counts":{a:sum(readings[(f,a)]["strict_pass_at_0_001"] for f in fixtures) for a in EXPECTED_ARMS},
        "old_8_fixture_rerun":False,"new_training":False,"test_used":False
    }

def main():
    p=argparse.ArgumentParser()
    for n in ("prereg","reference","native","out"):
        p.add_argument("--"+n,required=True,type=Path)
    a=p.parse_args()
    prereg=json.loads(a.prereg.read_text(encoding="utf-8"))
    result=evaluate(prereg,list(jsonl(a.reference)),list(jsonl(a.native)))
    result["provenance"]={n+"_sha256":sha256(getattr(a,n)) for n in ("prereg","reference","native")}
    with a.out.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False)
        f.write("\n")
    print(json.dumps({"status":"NEW_SYNTHETIC_AUDIT_COMPLETE","path":str(a.out),"sha256":sha256(a.out),
                      "arm_pass_counts":result["arm_strict_pass_counts"]},sort_keys=True))

if __name__=="__main__":
    try:main()
    except (OSError,ValueError,KeyError,json.JSONDecodeError) as e:
        print("T5_NEW_SYNTHETIC_AUDIT_FAIL_CLOSED:"+str(e),file=sys.stderr)
        raise SystemExit(2)
