#!/usr/bin/env python3
"""A0E integrated semantic pre-execution audit, never authorizes GPU.
Unlike v2: checks pinned artifact byte hashes AND parsed content/status/source relationships.
Unknown schemas are rejected. Missing private evidence means HOLD, never simulated GO.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

AMENDMENT="95257120d1450cf05871c9b134a62fb3c84bf890"
PREREG="d6e5d82709b2bc31458f73e7720cdae1e5f5e54e"
GOLD="b58f68454cf9354b94ecd8bfd778ff2cc784a25fc7dca02bc695319ad2b4157e"
SEEDS=[61031,61032,61033]
REQUIRED={
 "scaled_P_A_P_C_three_seed_sha_receipt":("ttm.gemma2.a0e.scaled_private_tensor_readback.v1",["PASS_REAL_TENSOR_TRANSFORM_SCOPED_HOLD_CROSS_ORIGIN_SHAPE"]),
 "cross_origin_full_spectrum_and_SMD_QA":("ttm.gemma2.a0e.cross_origin_full_source_review.v1",["PASS_FULL_SPECTRUM_SMD_PREDECLARED"]),
 "projector_source_negative_QA":("ttm.gemma2.a0e.projector_negative_readback.v1",["PASS_PROJECTOR_NEGATIVE_SCOPED"]),
 "train_val_raw_rights_and_neardup_QA":("ttm.gemma2.a0e.raw_source_rights_neardup.v1",["PASS_RIGHTS_AND_NEW_VAL"]),
 "original_pretrained_weight_extraction_QA":("ttm.gemma2.a0e.full_official_weight_extraction.v1",["PASS_RAW_WEIGHT_AND_TOKENIZER"]),
 "full_A0E_training_runner_source":("ttm.gemma2.a0e.full_trainer_source_audit.v1",["PASS_REAL_TRAINER_IMPLEMENTATION_AND_IMPORT"]),
 "optimizer_sampler_schedule_source":("ttm.gemma2.a0e.sampler_optimizer_source_audit.v1",["PASS_FROZEN_SCHEDULE"]),
 "fresh_VAL_roster_receipt":("ttm.gemma2.a0e.fresh_val_roster.v1",["PASS_NEW_FRESH_VAL_ROSTER"]),
 "independent_NLL_and_lexical_scorer_source":("ttm.gemma2.a0e.scorers_independent_qa.v1",["PASS_BOTH_SCORERS_NEGATIVE"]),
 "procedural_blind_lock_source_QA":("ttm.gemma2.a0e.blinding_procedure_audit.v1",["PASS_TWO_PARTY_LOCK_PROCEDURE"]),
 "owner_no_peek_declaration":("ttm.gemma2.a0e.owner_no_peek_statement.v1",["PASS_OWNER_DECLARED_BEFORE_T4"]),
}
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def audit(m,root):
    root=Path(root).resolve(strict=True)
    checks={}
    def setg(k,ok):checks[k]="PASS" if bool(ok) else "HOLD"
    setg("SCHEMA",m.get("schema")=="ttm.gemma2.a0e.two_party_amendment_preexec.v1")
    setg("FROZEN_PREREG",m.get("original_prereg_git_blob")==PREREG)
    setg("GOLD_PIN",m.get("gold_source_sha256")==GOLD)
    setg("AMENDMENT_RELATION",m.get("amendment_document_path")=="docs/pilot/TTM_GEMMA2_A0E_TWO_PARTY_PROCEDURAL_BLINDING_CAUSAL_CONTROL_SINGLE_AMENDMENT_20261111.md")
    setg("ARMS",m.get("arms")==["P-A","P-C","N-A","N-C"])
    setg("SEEDS",m.get("paired_training_seeds")==[41031,41032,41033]
         and m.get("N_init_seeds")==SEEDS and m.get("null_seeds")==[51031,51032,51033])
    setg("BUDGET",m.get("target_token_presentations")==25165824
         and m.get("optimizer_steps_per_arm_seed")==512 and m.get("target_tokens_per_step")==4096)
    setg("TWO_PARTY_BLIND",m.get("procedural_blinding_mode")=="TWO_PARTY_HASH_LOCK_NO_THIRD_PARTY"
         and m.get("external_custodian_required") is False
         and m.get("gold_scores_read_prelock") is False
         and m.get("label_appears_in_training_inputs") is False)
    setg("SCALAR_PROJECTOR_SCOPE",m.get("normalization_rule")=="SCALAR_P_TO_N_MEDIAN_T1_MAPPED_BY_SEED_P_C_SAME_FACTOR"
         and m.get("projector_interpretation")=="GRADIENT_ADAPTATION_CONFOUND_PRETRAINING_ASSOCIATED_ONLY"
         and m.get("scientific_claim_scope")=="EXPLORATORY_PRETRAINING_ASSOCIATED_NOT_PURE_SEMANTIC_CAUSALITY")
    setg("OWNER_PROTOCOL",m.get("owner_two_party_protocol_adopted") is True)
    setg("OWNER_RIGHTS",m.get("owner_source_rights_and_budget_acknowledged") is True)
    entries=m.get("local_evidence",{})
    for key,(schema,statuses) in REQUIRED.items():
        ok=False
        item=entries.get(key) if isinstance(entries,dict) else None
        try:
            name=item["path"];expected=item["sha256"]
            if not isinstance(name,str) or not re.fullmatch(r"[0-9a-f]{64}",expected):raise ValueError("ENTRY")
            rel=Path(name)
            if rel.is_absolute() or ".." in rel.parts or '\\' in name:raise ValueError("ESCAPE")
            path=(root/rel).resolve(strict=True)
            if root not in path.parents or path.is_symlink() or not path.is_file():raise ValueError("PATH")
            if sha(path)!=expected:raise ValueError("HASH")
            ev=json.loads(path.read_text('utf8'))
            if ev.get("schema")!=schema or ev.get("status") not in statuses:raise ValueError("SCHEMA_STATUS")
            if ev.get("source_prereg_blob",ev.get("original_prereg_blob"))!=PREREG:raise ValueError("PREREG_BIND")
            if ev.get("gold_read") is True or ev.get("GPU") is True or ev.get("model_forward") is True:raise ValueError("SCIENCE_BOUNDARY")
            if key=="scaled_P_A_P_C_three_seed_sha_receipt":
                rows=ev["seeds"]
                if len(rows)!=3 or [z["seed"] for z in rows]!=SEEDS or not all(
                    len(z["new_f32le_SHA"])==4 and
                    all(re.fullmatch(r"[0-9a-f]{64}",s) for s in z["new_f32le_SHA"].values())
                    for z in rows):raise ValueError("TENSOR_SOURCE")
                # This only demonstrates scoped transformation, never full cross-origin match.
            ok=True
        except (OSError,ValueError,KeyError,TypeError,AttributeError,UnicodeError,IndexError):
            ok=False
        setg("REAL_CONTENT_"+key,ok)
    # Honest: even all checks passing here would be a candidate only, not an authorization.
    ready=all(v=="PASS" for v in checks.values())
    return {"schema":"ttm.gemma2.a0e.integrated_content_adjudication.v3",
      "status":"GO_CANDIDATE_OWNER_T4_APPROVAL_STILL_REQUIRED" if ready else "NO_GO_HOLD",
      "pass_count":sum(v=="PASS" for v in checks.values()),"total":len(checks),
      "missing":[k for k,v in checks.items() if v=="HOLD"],"checks":checks,
      "gold_read":False,"GPU":False,"T4_authorized":False,"science_executed":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",required=True);p.add_argument("--root",required=True)
    a=p.parse_args()
    try:
        m=json.loads(Path(a.manifest).read_text('utf8'))
        out=audit(m,a.root)
    except Exception as e:out={"status":"NO_GO_HOLD","error":str(e),"GPU":False,"T4_authorized":False}
    print(json.dumps(out,sort_keys=True))
    if out['status']=="NO_GO_HOLD":raise SystemExit(2)
if __name__=="__main__":main()
