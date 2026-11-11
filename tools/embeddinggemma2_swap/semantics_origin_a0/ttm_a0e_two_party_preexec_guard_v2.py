#!/usr/bin/env python3
"""Amended A0E preexecution one-gate read-only guard. Never authorizes T4 itself.
Unlike v1 this does NOT require a third-party gold custodian. Exact file SHA,
source-rights and science runner evidence still required. Fail closed.
"""
from __future__ import annotations
import argparse,hashlib,json,re,tempfile
from pathlib import Path

FROZEN={"arms":["P-A","P-C","N-A","N-C"],"paired_training_seeds":[41031,41032,41033],
 "N_init_seeds":[61031,61032,61033],"null_seeds":[51031,51032,51033],
 "target_token_presentations":25165824,
 "original_prereg_git_blob":"d6e5d82709b2bc31458f73e7720cdae1e5f5e54e",
 "gold_source_sha256":"b58f68454cf9354b94ecd8bfd778ff2cc784a25fc7dca02bc695319ad2b4157e",
 "scientific_claim_scope":"EXPLORATORY_PRETRAINING_ASSOCIATED_NOT_PURE_SEMANTIC_CAUSALITY",
 "gold_scores_read_prelock":False,"label_appears_in_training_inputs":False}
REQUIRED=("scaled_P_A_P_C_three_seed_sha_receipt","cross_origin_full_spectrum_and_SMD_QA",
 "projector_source_negative_QA","train_val_raw_rights_and_neardup_QA",
 "original_pretrained_weight_extraction_QA","full_A0E_training_runner_source",
 "optimizer_sampler_schedule_source","fresh_VAL_roster_receipt",
 "independent_NLL_and_lexical_scorer_source","procedural_blind_lock_source_QA",
 "owner_no_peek_declaration")
def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()
def audit(m,root):
    gates={}
    def g(k,ok):gates[k]="PASS" if bool(ok) else "HOLD"
    g("AMENDMENT_SCHEMA",m.get("schema")=="ttm.gemma2.a0e.two_party_amendment_preexec.v1")
    for k,v in FROZEN.items():g("FROZEN_"+k,m.get(k)==v)
    g("TWO_PARTY_NOT_EXTERNAL_CUSTODY",m.get("procedural_blinding_mode")=="TWO_PARTY_HASH_LOCK_NO_THIRD_PARTY")
    g("SCALAR_RULE",m.get("normalization_rule")=="SCALAR_P_TO_N_MEDIAN_T1_MAPPED_BY_SEED_P_C_SAME_FACTOR")
    g("PROJECTOR_CAUSAL_SCOPE",m.get("projector_interpretation")=="GRADIENT_ADAPTATION_CONFOUND_PRETRAINING_ASSOCIATED_ONLY")
    base=Path(root).resolve()
    artifacts=m.get("local_evidence",{})
    for key in REQUIRED:
        entry=artifacts.get(key,{}) if isinstance(artifacts,dict) else {}
        name=entry.get("path") if isinstance(entry,dict) else None
        expected=entry.get("sha256") if isinstance(entry,dict) else None
        passed=False
        if isinstance(name,str) and isinstance(expected,str) and re.fullmatch(r"[0-9a-f]{64}",expected):
            relative=Path(name)
            if not relative.is_absolute() and ".." not in relative.parts and "\\" not in name:
                f=(base/relative).resolve()
                passed=base in f.parents and f.is_file() and digest(f)==expected
        g("REAL_SHA_"+key,passed)
    g("OWNER_TWO_PARTY_PROTOCOL_ADOPTED",m.get("owner_two_party_protocol_adopted") is True)
    g("OWNER_SOURCE_RIGHTS_AND_BUDGET_ACK",m.get("owner_source_rights_and_budget_acknowledged") is True)
    ready=all(s=="PASS" for s in gates.values())
    return {"schema":"ttm.gemma2.a0e.two_party_preexec_integrated_adjudication.v2",
       "status":"GO_CANDIDATE_REQUIRES_SEPARATE_OWNER_T4_DECISION" if ready else "NO_GO_HOLD",
       "passed":sum(x=="PASS" for x in gates.values()),"total":len(gates),
       "missing":[k for k,v in gates.items() if v=="HOLD"],"gates":gates,
       "third_party_gold_custodian_required":False,"gold_read":False,
       "model_forward":False,"training":False,"GPU":False,"T4_authorized":False}
def fixture():
    m={"schema":"ttm.gemma2.a0e.two_party_amendment_preexec.v1",**FROZEN,
       "procedural_blinding_mode":"TWO_PARTY_HASH_LOCK_NO_THIRD_PARTY",
       "normalization_rule":"SCALAR_P_TO_N_MEDIAN_T1_MAPPED_BY_SEED_P_C_SAME_FACTOR",
       "projector_interpretation":"GRADIENT_ADAPTATION_CONFOUND_PRETRAINING_ASSOCIATED_ONLY",
       "owner_two_party_protocol_adopted":False,
       "owner_source_rights_and_budget_acknowledged":False,
       "local_evidence":{}}
    with tempfile.TemporaryDirectory(prefix="ttm_a0e_guard_") as temp:
        root=Path(temp)
        x=audit(m,root)
        assert x["status"]=="NO_GO_HOLD" and not x["third_party_gold_custodian_required"]
        for k in REQUIRED:
            f=root/(k+".txt");f.write_text("synthetic verified file "+k)
            m["local_evidence"][k]={"path":f.name,"sha256":digest(f)}
        m["owner_two_party_protocol_adopted"]=True
        m["owner_source_rights_and_budget_acknowledged"]=True
        x=audit(m,root)
        assert x["status"].startswith("GO_CANDIDATE") and x["T4_authorized"] is False
        (root/(REQUIRED[0]+".txt")).write_text("tampered")
        x=audit(m,root)
        assert x["status"]=="NO_GO_HOLD" and x["gates"]["REAL_SHA_"+REQUIRED[0]]=="HOLD"
        m["local_evidence"][REQUIRED[0]]["sha256"]="a"*64
        assert audit(m,root)["status"]=="NO_GO_HOLD"
        m["owner_two_party_protocol_adopted"]=False
        assert audit(m,root)["status"]=="NO_GO_HOLD"
    return {"status":"PASS_TWO_PARTY_PREEXEC_REAL_SHA_GATES_AND_NEGATIVE_FIXTURE",
            "third_party_custodian_required":False,"T4_authorized":False,"GPU":False}
def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--fixture",action="store_true");g.add_argument("--manifest")
    p.add_argument("--root");a=p.parse_args()
    if a.fixture:out=fixture()
    else:
        if not a.root:raise SystemExit("A0E_HOLD_PROJECT_ROOT")
        out=audit(json.loads(Path(a.manifest).read_bytes()),a.root)
    print(json.dumps(out,sort_keys=True))
    if out["status"]=="NO_GO_HOLD":raise SystemExit(2)
if __name__=="__main__":main()
