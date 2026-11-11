#!/usr/bin/env python3
"""Pre-outcome A0E scalar P/N source-aggregate audit. No model, gold, VAL or GPU."""
from __future__ import annotations
import argparse,json
from pathlib import Path

SEEDS=(61031,61032,61033)
def need(ok,code):
    if not ok:raise ValueError("A0E_SCALAR_HOLD_"+code)

def audit(data):
    if "paired_seeds" in data:  # private frozen source receipt, NEVER its private tensor bytes
        rows=data["paired_seeds"]
        need([z["official_N_init_seed"] for z in rows]==list(SEEDS),"SEED_ORDER")
        need(data["human_gold_read"] is False and data["no_model_forward"] is True,"SOURCE_SCOPE")
        need(all(z["P_C_matched_null"]["status"]=="PASS_SOURCE_SCOPED_NULL_MOMENTS" and
                 z["N_C_matched_null"]["status"]=="PASS_SOURCE_SCOPED_NULL_MOMENTS" for z in rows),"WITHIN_NULL_QA")
        pair=[(z["official_N_init_seed"],float(z["cross_source_PN_median_row_norm_ratio"]),
              float(z["cross_source_PN_total_trace_covariance_ratio"])) for z in rows]
    else:
        need(data.get("schema")=="ttm.gemma2.a0e.scalar_aggregate_fixture.v1","SCHEMA")
        pair=[(int(v[0]),float(v[1]),float(v[2])) for v in data["precommitted_source_aggregates"]]
    need(len(pair)==3 and [a for a,_,_ in pair]==list(SEEDS),"PAIRS")
    need(all(2.0<norm<2.5 and 4.0<trace<5.5 for _,norm,trace in pair),"SOURCE_AGGREGATES")
    q=[{"seed":seed,"alpha_P_s":1.0/norm,"original_norm_P_over_N":norm,
        "original_trace_P_over_N":trace,"scaled_trace_P_over_N":trace/(norm*norm)}
       for seed,norm,trace in pair]
    need(all(abs(x["scaled_trace_P_over_N"]-1.0)<=0.05 for x in q),"SCALED_TRACE_TOLERANCE")
    return {"status":"PASS_SCALAR_ALGEBRA_AGGREGATES_ONLY",
            "schema":"ttm.gemma2.a0e.scalar_amendment_source_audit.v1",
            "rule":"alpha_s=median_norm(N_s_mapped)/median_norm(P_mapped); apply same positive alpha_s to P-A and P-C; N-A/N-C unchanged; do not scale 131 fallback/special IDs",
            "per_seed":q,
            "scalar_positive_cosine_invariant":True,
            "within_P_A_C_relative_covariance_invariant":True,
            "cross_source_full_covariance_eigenspectrum_match":"NOT_TESTED",
            "cross_source_frequency_morphology_SMD":"NOT_TESTED",
            "new_scaled_tensor_SHA_frozen":False,"untrained_model_reinitialized":False,
            "human_gold_read":False,"model_forward":False,"GPU":False,"T4_authorized":False}
def fixture():
    x={"schema":"ttm.gemma2.a0e.scalar_aggregate_fixture.v1",
       "precommitted_source_aggregates":[
        [61031,2.2129199504852295,4.774143326626136],
        [61032,2.2103381156921387,4.7749307334828455],
        [61033,2.2117035388946533,4.780100462329466]]}
    ok=audit(x)
    assert len(ok["per_seed"])==3 and all(.95<z["scaled_trace_P_over_N"]<1.05 for z in ok["per_seed"])
    x["precommitted_source_aggregates"][0][1]=0.1
    try:audit(x)
    except ValueError as e:assert "SOURCE_AGGREGATES" in str(e)
    else:raise AssertionError("NEGATIVE_BAD_RATIO_NOT_REJECTED")
    return {"status":"PASS_SCALAR_AGGREGATE_SOURCE_FIXTURE_AND_NEGATIVE","GPU":False}
if __name__=="__main__":
    a=argparse.ArgumentParser();q=a.add_mutually_exclusive_group(required=True)
    q.add_argument("--fixture",action="store_true");q.add_argument("--prior-receipt")
    m=a.parse_args()
    try:result=fixture() if m.fixture else audit(json.loads(Path(m.prior_receipt).read_bytes()))
    except Exception as e:
        print(json.dumps({"status":"HOLD_FAIL_CLOSED","error":str(e),"GPU":False},sort_keys=True))
        raise SystemExit(2)
    print(json.dumps(result,sort_keys=True))
