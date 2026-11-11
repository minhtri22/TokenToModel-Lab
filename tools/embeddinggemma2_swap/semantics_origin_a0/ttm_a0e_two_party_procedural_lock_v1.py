#!/usr/bin/env python3
"""A0E two-party outcome hash-lock; never reads public gold labels.
No human independent custody claimed. CPU source-only, no model calls.
"""
from __future__ import annotations
import argparse, hashlib, json, re, tempfile
from pathlib import Path

ARMS=("P-A","P-C","N-A","N-C")
SEEDS=(41031,41032,41033)
NAMES=tuple(f"seed{seed}__{arm}.json" for seed in SEEDS for arm in ARMS)
GOLD_SHA="b58f68454cf9354b94ecd8bfd778ff2cc784a25fc7dca02bc695319ad2b4157e"
PREREG="d6e5d82709b2bc31458f73e7720cdae1e5f5e54e"

def need(v,k):
    if not v:raise ValueError("A0E_TWO_PARTY_HOLD_"+k)

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def check_m(m):
    need(m.get("schema")=="ttm.gemma2.a0e.two_party_amendment_preexec.v1","SCHEMA")
    need(m.get("original_prereg_git_blob")==PREREG,"ORIGINAL_PREREG")
    need(m.get("gold_source_sha256")==GOLD_SHA,"GOLD_PIN")
    need(m.get("arms")==list(ARMS) and m.get("paired_training_seeds")==list(SEEDS),"ARMS_SEEDS")
    need(m.get("N_init_seeds")==[61031,61032,61033] and m.get("null_seeds")==[51031,51032,51033],"NULL_SEEDS")
    need(m.get("target_token_presentations")==25165824,"BUDGET")
    need(m.get("procedural_blinding_mode")=="TWO_PARTY_HASH_LOCK_NO_THIRD_PARTY","CUSTODY_MODE")
    need(m.get("scientific_claim_scope")=="EXPLORATORY_PRETRAINING_ASSOCIATED_NOT_PURE_SEMANTIC_CAUSALITY","CLAIM")
    need(m.get("gold_scores_read_prelock") is False and m.get("label_appears_in_training_inputs") is False,"PREMATURE_GOLD_READ")

def paths(directory):
    d=Path(directory);need(d.is_dir(),"OUTCOMES_DIRECTORY")
    entries=[p for p in d.iterdir() if p.is_file()]
    need({p.name for p in entries}==set(NAMES) and len(entries)==12,"EXACT_TWELVE_OUTCOMES_AND_NO_GOLD")
    return {n:d/n for n in NAMES}

def lock(manifest,directory,receipt):
    mpath=Path(manifest);need(mpath.is_file(),"MANIFEST_MISSING")
    check_m(json.loads(mpath.read_text(encoding="utf8")))
    rp=Path(receipt);need(not rp.exists(),"NO_RECEIPT_OVERWRITE")
    files=paths(directory)
    entries={n:{"sha256":sha(p),"bytes":p.stat().st_size} for n,p in files.items()}
    need(all(x["bytes"]>0 for x in entries.values()),"NONEMPTY_OUTCOMES")
    record={"schema":"ttm.gemma2.a0e.two_party_hash_locked_outcomes.v1",
        "original_prereg_git_blob":PREREG,"manifest_sha256":sha(mpath),
        "gold_source_sha256_reference_only":GOLD_SHA,
        "outcomes":entries,"outcome_count":12,
        "human_custodian":"NONE_THIRD_PARTY",
        "gold_scores_read":False,"unblind_allowed":False,
        "model_forward":False,"training":False,"gpu":False}
    rp.parent.mkdir(parents=True,exist_ok=True)
    with rp.open("x",encoding="utf8",newline="\n") as f:
        json.dump(record,f,sort_keys=True,indent=2);f.write("\n")
    return {"status":"LOCKED_12_OUTCOME_HASH_ONLY","receipt_sha256":sha(rp),"gold_read":False}

def verify(manifest,directory,receipt):
    mpath=Path(manifest);rp=Path(receipt)
    need(mpath.is_file() and rp.is_file(),"LOCK_FILES_MISSING")
    check_m(json.loads(mpath.read_text(encoding="utf8")))
    record=json.loads(rp.read_text(encoding="utf8"))
    need(record.get("schema")=="ttm.gemma2.a0e.two_party_hash_locked_outcomes.v1","LOCK_SCHEMA")
    need(record.get("manifest_sha256")==sha(mpath),"MANIFEST_CHANGED")
    need(record.get("gold_source_sha256_reference_only")==GOLD_SHA,"GOLD_CHANGED")
    need(record.get("outcome_count")==12 and set(record.get("outcomes",{}))==set(NAMES),"LOCK_SET")
    need(record.get("gold_scores_read") is False and record.get("unblind_allowed") is False,"PREMATURE_UNBLIND")
    for name,p in paths(directory).items():
        need(record["outcomes"][name]["sha256"]==sha(p) and
             record["outcomes"][name]["bytes"]==p.stat().st_size,"OUTCOME_CHANGED_"+name)
    return {"status":"PASS_LOCKED_TWELVE_HASHES_UNCHANGED","receipt_sha256":sha(rp),"gold_read":False}

def readiness(manifest,directory,receipt,published_sha,commit):
    res=verify(manifest,directory,receipt)
    need(re.fullmatch(r"[0-9a-f]{64}",published_sha or "") is not None,"PUBLISHED_SHA_FORMAT")
    need(res["receipt_sha256"]==published_sha,"PUBLISHED_SHA_MISMATCH")
    need(re.fullmatch(r"[0-9a-f]{40}",commit or "") is not None,"PUBLISHED_COMMIT_FORMAT")
    # This offline step does NOT verify commit existence or chronology.
    return {"status":"READY_FOR_SEPARATE_GITHUB_COMMIT_READBACK_THEN_GOLD",
            "published_commit_existence_verified":False,"gold_read":False}

def fixture():
    base={"schema":"ttm.gemma2.a0e.two_party_amendment_preexec.v1",
      "original_prereg_git_blob":PREREG,"gold_source_sha256":GOLD_SHA,
      "arms":list(ARMS),"paired_training_seeds":list(SEEDS),
      "N_init_seeds":[61031,61032,61033],"null_seeds":[51031,51032,51033],
      "target_token_presentations":25165824,
      "procedural_blinding_mode":"TWO_PARTY_HASH_LOCK_NO_THIRD_PARTY",
      "scientific_claim_scope":"EXPLORATORY_PRETRAINING_ASSOCIATED_NOT_PURE_SEMANTIC_CAUSALITY",
      "gold_scores_read_prelock":False,"label_appears_in_training_inputs":False}
    with tempfile.TemporaryDirectory(prefix="a0e_blind_fixture_") as folder:
        root=Path(folder);d=root/"out";d.mkdir()
        manifest=root/"manifest.json";manifest.write_text(json.dumps(base))
        for name in NAMES:(d/name).write_text(json.dumps({"fake_case":name,"nll":0.3}))
        receipt=root/"lock.json"
        assert lock(manifest,d,receipt)["status"].startswith("LOCKED_")
        assert verify(manifest,d,receipt)["status"].startswith("PASS_")
        try:lock(manifest,d,receipt)
        except ValueError as e:assert "NO_RECEIPT_OVERWRITE" in str(e)
        else:raise AssertionError("OVERWRITE_NEGATIVE_NOT_REJECTED")
        with (d/NAMES[0]).open("a") as f:f.write("tamper")
        try:verify(manifest,d,receipt)
        except ValueError as e:assert "OUTCOME_CHANGED" in str(e)
        else:raise AssertionError("TAMPER_NEGATIVE_NOT_REJECTED")
        try:readiness(manifest,d,receipt,"0"*64,"a"*40)
        except ValueError as e:assert "OUTCOME_CHANGED" in str(e)
        else:raise AssertionError("PREMATURE_UNBLIND_NOT_REJECTED")
        base["gold_scores_read_prelock"]=True
        try:check_m(base)
        except ValueError as e:assert "PREMATURE_GOLD_READ" in str(e)
        else:raise AssertionError("PREMATURE_GOLD_NOT_REJECTED")
    return {"status":"PASS_TWO_PARTY_LOCK_4_NEGATIVE_FIXTURES","third_party_custodian_required":False,
            "gold_read":False,"model_forward":False,"training":False,"GPU":False}
def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True)
    for key in ("fixture","lock","verify","unblind-ready"):g.add_argument("--"+key,action="store_true")
    for arg in ("manifest","outcomes-dir","receipt","published-receipt-sha","published-lock-commit"):ap.add_argument("--"+arg)
    a=ap.parse_args()
    try:
        if a.fixture:out=fixture()
        elif a.lock:out=lock(a.manifest,a.outcomes_dir,a.receipt)
        elif a.verify:out=verify(a.manifest,a.outcomes_dir,a.receipt)
        else:out=readiness(a.manifest,a.outcomes_dir,a.receipt,a.published_receipt_sha,a.published_lock_commit)
        print(json.dumps(out,sort_keys=True))
    except Exception as e:
        print(json.dumps({"status":"HOLD_FAIL_CLOSED","error":str(e),"gold_read":False,"GPU":False},sort_keys=True))
        raise SystemExit(2)
if __name__=="__main__":main()
