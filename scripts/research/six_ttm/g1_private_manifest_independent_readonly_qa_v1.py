#!/usr/bin/env python3
"""Independent metadata-only QA of private G1 128/64/64 manifest.

Cannot produce a manifest, read any TinyStories text, download tokenizer/weights,
train or issue a science permit. Modes: selftest (no file access) / verify (read-only).
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys
from pathlib import Path

ROOT=Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
WORK=ROOT/"_tmp/ttm_six_g1_private_manifest_v1"
T1=ROOT/"_tmp/ttm_t1_real_source_v1/T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json"
T1_SHA="9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9"
DATA=WORK/"G1_PREFIX_IDS_128_64_64_PRIVATE_METADATA.json"
READY=WORK/"G1_PREFIX_MANIFEST_READY.json"
PIN=WORK/"G1_TOKENIZER_METADATA_PIN.json"
COUNTS={"TRAIN":128,"DEV":64,"TEST":64}
SEED="TTM_SIX_G1_V1|"

def check(condition,msg):
    if not condition: raise RuntimeError(msg)

def digest(b): return hashlib.sha256(b).hexdigest()
def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def assert_boundary():
    check(os.name=="nt","WINDOWS_ONLY")
    check(ROOT.is_dir() and not ROOT.is_symlink() and not ROOT.is_junction(),"ROOT_INVALID")
    for p in (WORK,T1,DATA,READY,PIN):
        check(p.exists() and not p.is_symlink() and not p.is_junction(),"REQUIRED_PATH_INVALID:"+str(p))
        check(p.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)),"ESCAPED_ROOT")
    result=subprocess.run(["git","-C",str(ROOT),"remote","get-url","origin"],
                           check=False,capture_output=True,text=True,timeout=12)
    check(result.returncode==0,"ORIGIN_LOOKUP_FAIL")
    check(result.stdout.strip().lower() in {
        "https://github.com/minhtri22/tokentomodel-lab",
        "https://github.com/minhtri22/tokentomodel-lab.git",
        "git@github.com:minhtri22/tokentomodel-lab",
        "git@github.com:minhtri22/tokentomodel-lab.git"
    },"WRONG_GITHUB_ORIGIN")

def qa(g1,t1,ready,data_sha,pin_sha):
    checks={}
    def gate(name,ok):
        check(ok,"QA_FAIL_"+name);checks[name]="PASS"
    gate("SCHEMA",g1.get("schema")=="ttm.six.g1.private.prefix.ids.v1" and
         ready.get("schema")=="ttm.six.g1.private.prefix.ready.v1")
    gate("CANONICAL_METADATA_ONLY",g1.get("story_hashes_only_no_raw_text") is True and
         g1.get("science_executed") is False and ready.get("science_executed") is False)
    gate("T1_SHA",g1.get("t1_split_manifest_sha256")==T1_SHA and
         ready.get("t1_split_manifest_sha256")==T1_SHA)
    gate("SOURCE_TRAIN_SHA",g1.get("source_original_train_sha256")==
         "c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f")
    gate("REVISION",g1.get("source_revision")==
         "f54c09fd23315a6f9c86f9dc80f725de7d8f9c64")
    gate("SPLIT_SIZES",g1.get("counts")==COUNTS and ready.get("split_counts")==COUNTS
         and all(len(g1.get("splits",{}).get(split,[]))==size for split,size in COUNTS.items()))
    gate("READY_MANIFEST_SHA",ready.get("manifest_sha256")==data_sha)
    gate("READY_FILE_NAME",ready.get("manifest_filename")==DATA.name)
    gate("TOKENIZER_PIN",g1.get("tokenizer_pin_sha256")==pin_sha)
    gate("SCOPE_PRIVATE",g1.get("scope")=="OWNER_OPT_IN_PRIVATE_COMPUTATIONAL_G1_CDLASHARING_1_0")
    gate("NO_PRIVILEGED_TEXT",g1.get("original_ttm_VAL_TEST_story_text_accessed") is False
         and ready.get("original_ttm_VAL_TEST_story_text_accessed") is False)
    gate("NO_MODEL_TRAIN",ready.get("qwen_model_weights_downloaded") is False and
         ready.get("g1_science_permit")=="NOT_GRANTED")
    gate("SOURCE_MAPPING",g1.get("source_mapping")=="FIRST_OCCURRENCE_ZERO_BASED_FOR_DUPLICATE_RAW_SHA")
    gate("PREFIX_DEDUP_RULE",g1.get("g1_prefix_dedup_rule")==
         "KEEP_FIRST_SELECTION_KEY_PER_NORMALIZED_STORY_AND_PREFIX_SHA")
    ttrain=set(t1["splits"]["TRAIN"])
    tval=set(t1["splits"]["VAL"]);ttest=set(t1["splits"]["TEST"])
    gate("T1_ID_COUNTS",len(ttrain)==2048 and len(tval)==256 and len(ttest)==64)
    gate("T1_IDS_NONOVERLAP",not(ttrain&tval or ttrain&ttest or tval&ttest))
    entries=[x for split in ("TRAIN","DEV","TEST") for x in g1["splits"][split]]
    raw_keys=("text","story_text","prefix","raw","raw_text","content","continuation")
    gate("NO_RAW_STORY_FIELDS",all(not any(k in e for k in raw_keys) for e in entries))
    ids=[e.get("source_story_sha256") for e in entries]
    gate("TRAIN_ONLY_IDS",all(s in ttrain and s not in tval and s not in ttest for s in ids))
    gate("ID_UNIQUENESS",len(set(ids))==256)
    prefixes=[e.get("normalized_prefix_utf8_sha256") for e in entries]
    gate("PREFIX_UNIQUENESS",len(set(prefixes))==256)
    norm=[e.get("normalized_story_utf8_sha256") for e in entries]
    gate("NORMALIZED_STORY_UNIQUENESS",len(set(norm))==256)
    keys=[e.get("selection_key_sha256") for e in entries]
    gate("DETERMINISTIC_ORDER",keys==sorted(keys) and len(set(keys))==256)
    gate("HASH_FORMAT",all(re.fullmatch(r"[0-9a-f]{64}",h or "") for h in ids+prefixes+norm+keys))
    gate("SOURCE_ROW_INDEX",all(isinstance(e.get("source_row_index"),int) and
         e["source_row_index"]>=0 for e in entries))
    gate("SELECTION_KEY_RECOMPUTE",all(
        digest((SEED+str(e["source_row_index"])+"|"+e["normalized_story_utf8_sha256"])
              .encode("utf-8"))==e["selection_key_sha256"] for e in entries))
    gate("TOKEN_COUNTS",all(8<=e.get("qwen06_token_count",0)<=96 and
         8<=e.get("qwen17_token_count",0)<=96 for e in entries))
    gate("PREFIX_BOUNDARIES",all(80<=e.get("prefix_end_unicode_codepoint_offset",-1)<=192
         for e in entries))
    gate("ROW_SPLIT_TAG",all(e.get("g1_split")==split for split in COUNTS
         for e in g1["splits"][split]))
    gate("NO_OTHER_TOPLEVEL_KEYS",not any(k in g1 for k in ("raw_stories","training_text","texts")))
    return checks

def synthetic_test():
    def identity(i):
        base=digest(f"story-{i}".encode())
        prefix=digest(f"prefix-{i}".encode())
        norm=digest(f"norm-{i}".encode())
        row=i
        return {"source_row_index":row,"source_story_sha256":base,
                "normalized_story_utf8_sha256":norm,
                "normalized_prefix_utf8_sha256":prefix,
                "prefix_end_unicode_codepoint_offset":128,
                "qwen06_token_count":24,"qwen17_token_count":25,
                "selection_key_sha256":digest((SEED+str(row)+"|"+norm).encode()),
                "g1_split":""}
    entries=[identity(i) for i in range(256)]
    entries.sort(key=lambda e:e["selection_key_sha256"])
    splits={}
    for split,items in zip(COUNTS,(entries[:128],entries[128:192],entries[192:])):
        for e in items:e["g1_split"]=split
        splits[split]=items
    t1={"splits":{"TRAIN":[e["source_story_sha256"] for e in entries]+
          [digest(f"extra-{i}".encode()) for i in range(1792)],
          "VAL":[digest(f"v-{i}".encode()) for i in range(256)],
          "TEST":[digest(f"t-{i}".encode()) for i in range(64)]}}
    g1={"schema":"ttm.six.g1.private.prefix.ids.v1","story_hashes_only_no_raw_text":True,
        "science_executed":False,"t1_split_manifest_sha256":T1_SHA,
        "source_original_train_sha256":"c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f",
        "source_revision":"f54c09fd23315a6f9c86f9dc80f725de7d8f9c64",
        "counts":COUNTS,"tokenizer_pin_sha256":"pinned-metadata",
        "scope":"OWNER_OPT_IN_PRIVATE_COMPUTATIONAL_G1_CDLASHARING_1_0",
        "original_ttm_VAL_TEST_story_text_accessed":False,
        "source_mapping":"FIRST_OCCURRENCE_ZERO_BASED_FOR_DUPLICATE_RAW_SHA",
        "g1_prefix_dedup_rule":"KEEP_FIRST_SELECTION_KEY_PER_NORMALIZED_STORY_AND_PREFIX_SHA",
        "splits":splits}
    ready={"schema":"ttm.six.g1.private.prefix.ready.v1",
           "science_executed":False,"t1_split_manifest_sha256":T1_SHA,
           "split_counts":COUNTS,"manifest_sha256":"dummy",
           "manifest_filename":DATA.name,"original_ttm_VAL_TEST_story_text_accessed":False,
           "qwen_model_weights_downloaded":False,"g1_science_permit":"NOT_GRANTED"}
    checks=qa(g1,t1,ready,"dummy","pinned-metadata")
    check(len(checks)==29,"SYNTHETIC_POSITIVE_GATE_COUNT")
    g1["splits"]["DEV"][0]["normalized_prefix_utf8_sha256"]=g1["splits"]["TRAIN"][0]["normalized_prefix_utf8_sha256"]
    try:qa(g1,t1,ready,"dummy","pinned-metadata")
    except RuntimeError as e:check(str(e)=="QA_FAIL_PREFIX_UNIQUENESS","NEGATIVE_GATE_WRONG")
    else:raise RuntimeError("NEGATIVE_LEAK_FIXTURE_NOT_CAUGHT")
    return {"status":"PASS_SYNTHETIC_QA","positive_gates":len(checks),
            "negative_prefix_leak_detected":True,"science_executed":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=["selftest","verify"])
    args=p.parse_args()
    if args.mode=="selftest":
        print(json.dumps(synthetic_test(),sort_keys=True))
        return
    assert_boundary()
    rawT1=T1.read_bytes()
    check(digest(rawT1)==T1_SHA,"T1_BYTES_HASH_MISMATCH")
    manifestBytes=DATA.read_bytes()
    checks=qa(json.loads(manifestBytes.decode("utf-8")),json.loads(rawT1.decode("utf-8")),
              load(READY),digest(manifestBytes),digest(PIN.read_bytes()))
    print(json.dumps({"schema":"ttm.six.g1.independent.private_manifest.qa.v1",
        "status":"PASS_G1_PRIVATE_METADATA_29_GATES",
        "g1_manifest_sha256":digest(manifestBytes),
        "t1_manifest_sha256":T1_SHA,"gate_count":len(checks),
        "checks":checks,"read_raw_story_text":False,
        "writes_performed":False,"science_executed":False,
        "science_permit":"NOT_GRANTED"},sort_keys=True))

if __name__=="__main__":
    try:main()
    except Exception as e:
        print(json.dumps({"status":"STOP_FAIL_CLOSED","error":str(e)[:500],
                          "science_executed":False},sort_keys=True),file=sys.stderr)
        raise SystemExit(1)
