#!/usr/bin/env python3
"""A0E four-arm preexecution RUNNER CONTRACT only; NOT a runnable science trainer.

Fail closed until independently verified gold custody, source rights, exact null
and full science runner are signed and admitted. No training, inference or GPU.
"""
import argparse,json
ARMS=["P-A","P-C","N-A","N-C"]
REQUIRED=["N_mapped_PN_null_receipt_sha256","gold_custodian_signed_receipt_sha256","original_TRAIN_VAL_rights_and_neardup_sha256","full_pretrained_weight_extraction_receipt_sha256","A0E_science_runner_sha256","A0E_scorer_sha256","optimizer_sampler_val_roster_sha256","explicit_independent_T4_authorization_sha256"]
def ishash(x):return isinstance(x,str) and len(x)==64 and all(c in "0123456789abcdef" for c in x.lower())
def audit(m):
    gates={}
    def gate(k,x):gates[k]="PASS" if bool(x) else "HOLD"
    gate("FOUR_ARMS",m.get("arms")==ARMS)
    gate("TRAIN_SEEDS",m.get("train_seeds")==[41031,41032,41033])
    gate("N_SEEDS",m.get("official_N_init_seeds")==[61031,61032,61033])
    gate("NULL_SEEDS",m.get("control_null_seeds")==[51031,51032,51033])
    gate("BUDGET",m.get("steps_per_block")==512 and m.get("target_tokens_per_step")==4096 and m.get("target_token_presentations")==25165824)
    for field in REQUIRED:gate(field,ishash((m.get("admission_evidence") or {}).get(field)))
    # These are technical SHA checks only. A signed paper or a literal hash is
    # NOT self-authenticating; an EXTERNAL independent reviewer must authorize.
    gate("EXTERNAL_CUSTODY_SIGNATURE_INDEPENDENTLY_VERIFIED",False)
    gate("EXPLICIT_T4_AUTHORIZATION_INDEPENDENTLY_VERIFIED",False)
    return {"schema":"ttm.gemma2.a0e.fourarm.runner_contract.v1","status":"NO_GO_HOLD",
            "source_checks_passed":sum(v=="PASS" for v in gates.values()),
            "gates":gates,"full_science_runner_implemented":False,
            "model_forward":False,"training":False,"GPU":False,"T4_authorized":False}
def fixture():
    m={"arms":ARMS,"train_seeds":[41031,41032,41033],"official_N_init_seeds":[61031,61032,61033],
       "control_null_seeds":[51031,51032,51033],"steps_per_block":512,
       "target_tokens_per_step":4096,"target_token_presentations":25165824}
    d=audit(m);assert d["source_checks_passed"]==5 and d["status"]=="NO_GO_HOLD"
    m["arms"]=["P-A","P-C","N-A","P-A"]
    assert audit(m)["gates"]["FOUR_ARMS"]=="HOLD"
    return {"status":"PASS_PREEXEC_SOURCE_FIXTURE_FAIL_CLOSED","T4_authorized":False,"GPU":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--fixture",action="store_true");g.add_argument("--manifest")
    a=p.parse_args()
    if a.fixture:print(json.dumps(fixture(),sort_keys=True))
    else:
        print(json.dumps(audit(json.load(open(a.manifest,encoding="utf-8"))),sort_keys=True))
        raise SystemExit(2)
