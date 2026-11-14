#!/usr/bin/env python3
"""H-DATA-S1 blind240 score template source check / future score-freeze validator.

--mode source-only (default): checks only public EMPTY score template and locked
rubric. No generated text, FINAL, model, AES mapping or source TRAIN is opened.
--mode verify-scored (future): checks exactly 240 integer judgments+24 notes and
prints SHA256(exact file bytes) and canonical score-array SHA. Never unblinds.
"""
import argparse
import hashlib
import json
from pathlib import Path

AXES = ("actor_retention","object_relation_retention","goal_or_rule_progress","coherence","consistency")
BINARY = AXES[:3]
ORDINAL = AXES[3:]
RUN_ID="TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1"

def need(b,code):
    if not b: raise RuntimeError("HDATA_S1_BLIND240_HOLD:"+code)
def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf8")
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def load(path):
    p=Path(path)
    need(p.is_file() and not p.is_symlink(),"MISSING_OR_LINKED_FILE")
    raw=p.read_bytes()
    return json.loads(raw),raw
def verify(contract_path,score_path,mode):
    c,_=load(contract_path)
    d,raw=load(score_path)
    need(c.get("schema")=="ttm.small4m.hdata_s1.scoring_protocol.v1" and
         c.get("run_id")==RUN_ID,"CONTRACT_LOCK")
    need(c.get("total_fields")=="24 pairs x 2 sides x 5 axes = 240 integer judgments, plus 24 nonempty notes",
         "FROZEN_FIELDS")
    need(tuple(x["name"] for x in c["primary_components"])==BINARY and
         tuple(x["name"] for x in c["secondary_scored_axes"])==ORDINAL,
         "FROZEN_AXIS_NAMES")
    need(d.get("run_id")==RUN_ID and
         d.get("blind")=="MODEL_IDENTITY_LEFT_RIGHT_UNKNOWN" and
         d.get("total_integer_scores_required")==240 and
         d.get("notes_required")==24,"SCORE_SCOPE")
    records=d.get("records")
    need(isinstance(records,list) and len(records)==24,"PAIR_COUNT")
    numeric=[]
    for i,item in enumerate(records,1):
        need(item.get("pair_id")==f"R{i:02d}" and
             set(item.keys())=={"pair_id","LEFT","RIGHT","note"},
             "PAIR_ORDER_OR_HIDDEN_FIELDS")
        note=item["note"]
        if mode=="source-only":
            need(note is None,"UNSCORED_NOTE_NOT_EMPTY")
        else:
            need(isinstance(note,str) and bool(note.strip()),"NONEMPTY_NOTE_REQUIRED")
        for side in ("LEFT","RIGHT"):
            scores=item[side]
            need(isinstance(scores,dict) and set(scores)==set(AXES),
                 "AXES_OR_HIDDEN_FIELD")
            for key in AXES:
                x=scores[key]
                if mode=="source-only":
                    need(x is None,"SCORES_PRESENT_IN_TEMPLATE")
                else:
                    limit=1 if key in BINARY else 3
                    need(type(x) is int and 0<=x<=limit,"INTEGER_SCORE_RANGE_"+key)
                    numeric.append({"pair_id":item["pair_id"],"side":side,"axis":key,"score":x})
    if mode=="source-only":
        need(d.get("score_status")=="UNSCORED_TEMPLATE_ONLY" and
             d.get("score_file_sha256_after_freeze") is None and
             d.get("canonical_score_array_sha256_after_freeze") is None,
             "TEMPLATE_ALREADY_USED")
        return {"status":"PASS_SOURCE_ONLY_240_BLANK_SLOTS_24_BLANK_NOTES",
                "rubric":"EXACT_FROZEN_5_AXES","score_file_sha256":sha(raw),
                "model_forward":0,"FINAL_read":False,"mapping_access":False,
                "unblind":"NOT_EXECUTED"}
    need(len(numeric)==240,"SCORE_COUNT_240")
    return {"status":"PASS_BLIND240_SCORE_CONTENT_VALIDATED_PENDING_OWNER_UNBLIND",
            "score_file_sha256":sha(raw),
            "canonical_score_array_sha256":sha(canonical(numeric)),
            "score_count":len(numeric),"note_count":len(records),
            "unblind":"NOT_EXECUTED"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("source-only","verify-scored"),default="source-only")
    ap.add_argument("--contract",required=True)
    ap.add_argument("--scores",required=True)
    args=ap.parse_args()
    print(json.dumps(verify(args.contract,args.scores,args.mode),
                     ensure_ascii=False,sort_keys=True,indent=2))

if __name__=="__main__":main()
