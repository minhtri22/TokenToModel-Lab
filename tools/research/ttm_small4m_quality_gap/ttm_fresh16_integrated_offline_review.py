#!/usr/bin/env python3
"""Read-only native offline QA for frozen TTM fresh16 continuation study.
No torch import, model forward, generation, TEST read, network or training.
Only writes one project-local receipt after all checks, never overwrites.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

ROOT=Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
BRANCH="research/ttm-small4m-prompt-adherence-continuation-design-20261111"
FOLDER="artifacts/research/ttm-small4m-quality-gap/"
PROMPTS=FOLDER+"TTM_FRESH_CONTINUATION_PROMPT_SET_CANDIDATE_V1_20261111.json"
HISTORY=FOLDER+"TTM_FRESH16_ALLOWED_PUBLIC_HISTORICAL_PROMPTS_20261111.json"
RUBRIC=FOLDER+"TTM_FRESH16_FROZEN_RUBRIC_AND_PREREG_CANDIDATE_20261111.json"
BPE="tools/pilot_t1t3/source_t2/ttm_gpt2_bpe2048.py"
BPE_BLOB="fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6"
BPE_FILE_SHA="cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
MERGES_SHA="aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af"
CKPTS={
 "1024":"cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b",
 "1280":"ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc"}
EXPECTED_HIST_BLOBS={
 "Q1_PUBLIC":"0a7cb5c2125b69b062d8e5559dbbe47cb07eb788",
 "FRESH12_PUBLIC":"919c43f2c919fa733b20a9be5d6b965e9649339c"}

def hfile(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def require(cond,reason):
    if not cond:raise ValueError(reason)

def local(root,path):
    p=path.resolve(strict=True)
    require(p.is_relative_to(root) and p!=root,"PATH_OUTSIDE_TTM")
    require(p.is_file() and not p.is_symlink(),"MISSING_OR_SYMLINK_FILE:"+str(path))
    return p

def git(git_path,work,*args):
    p=subprocess.run([git_path,"-C",str(work),*args],capture_output=True,text=True,
                     timeout=30,check=False)
    require(p.returncode==0,"GIT_READ_FAILED:"+p.stderr[-300:])
    return p.stdout.strip()

def terms(text):
    return re.findall(r"[a-z0-9]+",text.lower())

def gramset(text,n):
    words=terms(text)
    return set(" ".join(words[i:i+n]) for i in range(len(words)-n+1))

def jaccard(a,b):
    union=len(a|b)
    return len(a&b)/union if union else 0.0

def assess_public(prompts,history,rubric):
    rows=prompts["new_prompts"]
    earlier=history["history"]
    require(len(rows)==16 and len(earlier)==28,"INPUT_COUNTS_WRONG")
    require(len({r["id"] for r in rows})==16,"PROMPT_IDS_DUPLICATE")
    require(len({r["prompt_text"] for r in rows})==16,"PROMPT_TEXT_DUPLICATE")
    require(len({r["id"] for r in earlier})==28,"HISTORY_IDS_DUPLICATE")
    ids=[r["id"] for r in rows]
    require(ids==[f"CP{i:02d}-{v}" for i in range(1,9) for v in ("A","B")],
            "PROMPT_ORDER_CHANGED")
    cats={}
    for row in rows:
        t=row["prompt_text"]
        require(t and t==t.rstrip() and t==t.lstrip() and
                "\n" not in t and "\r" not in t and "\t" not in t,"PROMPT_SERIALIZATION_CHANGED")
        require(all(ord(c)<128 for c in t),"PROMPT_NONASCII")
        cats[row["category"]]=cats.get(row["category"],0)+1
    require(cats=={"entity_location":4,"causal_reasoning":4,"rule_constraint":4,
                  "goal_persistence":4},"UNBALANCED_CATEGORIES")
    require(rubric["fixture_contract"]["n_prompts"]==16
            and rubric["fixture_contract"]["n_pairs"]==8
            and rubric["fixture_contract"]["primary"]["H1"]["required_min"]==12
            and rubric["fixture_contract"]["primary"]["H2"]["required_min"]==6
            and rubric["fixture_contract"]["primary"]["H2"]["require_min_one_pass_each_of_four_categories"],
            "H1_H2_PREREG_CHANGED")
    require(rubric["status"].startswith("SOURCE_AND_METRIC_RULES_FROZEN"),"NOT_FROZEN_RUBRIC")
    hdict={x["name"]:x["git_blob_sha"] for x in history["sources"]}
    require(hdict==EXPECTED_HIST_BLOBS,"HIST_SOURCE_PIN_CHANGED")
    comparisons=[]
    exact=0
    nearest=[]
    for row in rows:
        a=row["prompt_text"]
        sim=[]
        for old in earlier:
            same=" ".join(terms(a))==" ".join(terms(old["text"]))
            exact+=int(same)
            sim.append((jaccard(gramset(a,3),gramset(old["text"],3)),
                        jaccard(gramset(a,5),gramset(old["text"],5)),old["id"]))
        top=max(sim,key=lambda x:(x[0],x[1]))
        nearest.append({"id":row["id"],"nearest_historical":top[2],
                        "jaccard_3gram":top[0],"jaccard_5gram":top[1]})
    require(exact==0,"PUBLIC_EXACT_OVERLAP")
    require(max(x["jaccard_3gram"] for x in nearest)<.35,"PUBLIC_NEAR_OVERLAP")
    for i in range(0,16,2):
        a,b=rows[i:i+2]
        require(a["pair_id"]==b["pair_id"] and a["category"]==b["category"] and
                a["contrast_fact"]!=b["contrast_fact"],"PAIR_NOT_MINIMAL")
        marker_a=a["contrast_fact"];marker_b=b["contrast_fact"]
        ia=a["prompt_text"].rfind(marker_a); ib=b["prompt_text"].rfind(marker_b)
        require(ia>=0 and ib>=0 and
                a["prompt_text"][:ia]==b["prompt_text"][:ib] and
                a["prompt_text"][ia+len(marker_a):]==b["prompt_text"][ib+len(marker_b):],
                "PAIR_PREFIX_SUFFIX_NOT_IDENTICAL")
    return {"status":"PASS_PUBLIC_FROZEN_SOURCE","prompt_count":16,"pairs":8,
            "historical_count":28,"exact_collisions":exact,
            "max_3gram_jaccard":max(x["jaccard_3gram"] for x in nearest),
            "max_5gram_jaccard":max(x["jaccard_5gram"] for x in nearest),
            "nearest_public":nearest}

def check_native_bpe(root,work,rows):
    src=local(root,work/BPE)
    require(blob(src)==BPE_BLOB,"BPE_SOURCE_GIT_BLOB_MISMATCH")
    manifest=local(root,root/"_tmp/ttm_t1_real_source_v1/T1_BPE2048_REAL_TRAIN_MANIFEST.json")
    require(hfile(manifest)==BPE_FILE_SHA,"REAL_TRAIN_BPE_MANIFEST_SHA_MISMATCH")
    obj=json.loads(manifest.read_text(encoding="utf-8"))
    require(obj["source_kind"]=="PINNED_TINYSTORIES_TRAIN" and
            obj.get("token_merges_sha256")==MERGES_SHA and obj.get("vocab_size")==2048,
            "REAL_BPE_SOURCE_KIND_OR_MERGES_DRIFT")
    sp=importlib.util.spec_from_file_location("ttm_fresh16_true_bpe",src)
    module=importlib.util.module_from_spec(sp)
    sys.modules[sp.name]=module
    sp.loader.exec_module(module)
    bpe=module.BPE2048.from_manifest(obj)
    lengths=[]
    for row in rows:
        ids=bpe.encode(row["prompt_text"])
        require(ids and len(ids)<=192 and 256 not in ids and
                all(0<=x<2048 for x in ids),"PROMPT_TOKEN_LIMIT_OR_IDS_FAIL:"+row["id"])
        require(bpe.decode(ids)==row["prompt_text"],"BPE_DECODE_ROUNDTRIP_FAIL:"+row["id"])
        raw=b"".join(struct.pack("<H",i) for i in ids)
        lengths.append({"id":row["id"],"n_bpe_tokens":len(ids),
                        "tokens_le_u16_sha256":hashlib.sha256(raw).hexdigest()})
    return {"status":"PASS_NATIVE_TRAIN_ONLY_BPE","manifest_sha256":BPE_FILE_SHA,
            "source_blob":BPE_BLOB,"merges_sha256":MERGES_SHA,
            "max_prompt_tokens":max(x["n_bpe_tokens"] for x in lengths),
            "min_prompt_tokens":min(x["n_bpe_tokens"] for x in lengths),
            "rows":lengths}

def check_ckpt(root,path,which):
    if not path: return {"status":"HOLD_CHECKPOINT_NOT_SUPPLIED","expected_sha256":CKPTS[which]}
    p=local(root,Path(path))
    actual=hfile(p)
    require(actual==CKPTS[which],"CHECKPOINT_SHA_MISMATCH_STEP_"+which)
    return {"status":"PASS_EXACT_SHA256","step":int(which),"expected_sha256":actual,
            "local_path":str(p),"bytes":p.stat().st_size}

def run():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",required=True,type=Path)
    ap.add_argument("--worktree",required=True,type=Path)
    ap.add_argument("--expected-head",required=True)
    ap.add_argument("--checkpoint-1024",default=None)
    ap.add_argument("--checkpoint-1280",default=None)
    args=ap.parse_args()
    require(os.name=="nt" and sys.version_info[:2]==(3,12),"WIN_PYTHON312_REQUIRED")
    root=args.project_root.resolve(strict=True)
    require(root==ROOT.resolve(strict=True),"WRONG_TTM_ROOT")
    work=args.worktree.resolve(strict=True)
    require(work!=root and work.is_relative_to(root),"WORKTREE_OUTSIDE_PROJECT")
    cmd=shutil.which("git.exe")
    require(cmd is not None,"GIT_NOT_FOUND")
    require(git(cmd,work,"branch","--show-current")==BRANCH and
            git(cmd,work,"rev-parse","HEAD")==args.expected_head and
            not git(cmd,work,"status","--porcelain","--untracked-files=all"),
            "SOURCE_BRANCH_HEAD_OR_CLEAN_GATE_FAILED")
    artifacts={name:local(root,work/path) for name,path in
               (("prompts",PROMPTS),("history",HISTORY),("rubric",RUBRIC))}
    require(blob(artifacts["prompts"])=="6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f",
            "PROMPT_FROZEN_SOURCE_BLOB_CHANGED")
    for name,path in (("prompts",PROMPTS),("history",HISTORY),("rubric",RUBRIC)):
        require(git(cmd,work,"rev-parse","HEAD:"+path)==blob(artifacts[name]),
                "SOURCE_GIT_INDEX_BLOB_MISMATCH:"+name)
    p=json.loads(artifacts["prompts"].read_text("utf-8"))
    h=json.loads(artifacts["history"].read_text("utf-8"))
    r=json.loads(artifacts["rubric"].read_text("utf-8"))
    public=assess_public(p,h,r)
    receipt={"schema":"ttm.fresh16.integrated_offline_preexec_review.v1",
             "status":"HOLD_PRIVATE_NATIVE_SOURCE_OR_REVIEWER",
             "source_head":args.expected_head,"public_source":public,
             "rubric_source_blob":blob(artifacts["rubric"]),
             "history_source_blob":blob(artifacts["history"]),
             "reviewer_source":r["reviewer_contract"]["candidate_model"],
             "reviewer_custody":r["reviewer_contract"]["custody"],
             "checkpoint_1024":None,"checkpoint_1280":None,"BPE":None,
             "inference_executed":False,"training_executed":False,
             "TEST_read":False,"original_science_replayed":False,
             "owner_science_execution_approved":False}
    failures=[]
    try:receipt["BPE"]=check_native_bpe(root,work,p["new_prompts"])
    except (OSError,ValueError,RuntimeError,ImportError,KeyError,ModuleNotFoundError) as e:
        failures.append("BPE:"+type(e).__name__+":"+str(e))
    for which,path in (("1024",args.checkpoint_1024),("1280",args.checkpoint_1280)):
        try:
            receipt["checkpoint_"+which]=check_ckpt(root,path,which)
            if receipt["checkpoint_"+which]["status"]!="PASS_EXACT_SHA256":
                failures.append("CHECKPOINT_"+which+"_MISSING_LOCAL_SHA")
        except (OSError,ValueError,RuntimeError) as e:
            failures.append("CHECKPOINT_"+which+":"+type(e).__name__+":"+str(e))
    source_pass=(not failures and
                 receipt["BPE"]["status"]=="PASS_NATIVE_TRAIN_ONLY_BPE")
    receipt["status"]=("PASS_SOURCE_BYTES_PREREG_FROZEN_REVIEWER_UNASSIGNED"
                       if source_pass else "HOLD_PRIVATE_NATIVE_SOURCE")
    receipt["blockers"]=failures+["REVIEWER_IDENTITY_AND_INDEPENDENCE_NOT_ATTESTED"]
    receipt["execution_decision"]="NOT_AUTHORIZED_NO_MODEL_FORWARD"
    out=root/"_tmp/ttm_fresh16_integrated_offline_review_20261111"
    require(not out.exists() and not out.is_symlink(),"PREEXEC_RECEIPT_ALREADY_EXISTS_NO_REWRITE")
    out.mkdir(parents=True,exist_ok=False)
    dest=out/"INTEGRATED_OFFLINE_REVIEW_RECEIPT.json"
    with dest.open("x",encoding="utf-8",newline="\n") as f:
        json.dump(receipt,f,indent=2,ensure_ascii=False,sort_keys=True)
        f.write("\n")
    print("TTM_FRESH16_PUBLIC_SOURCE="+public["status"],flush=True)
    print("TTM_FRESH16_BPE="+(receipt["BPE"]["status"] if receipt["BPE"] else "HOLD"),flush=True)
    print("TTM_FRESH16_CHECKPOINT_1024="+(receipt["checkpoint_1024"]["status"] if receipt["checkpoint_1024"] else "HOLD"),flush=True)
    print("TTM_FRESH16_CHECKPOINT_1280="+(receipt["checkpoint_1280"]["status"] if receipt["checkpoint_1280"] else "HOLD"),flush=True)
    print("TTM_FRESH16_REVIEW_STATUS="+receipt["status"],flush=True)
    print("TTM_FRESH16_REVIEW_RECEIPT_SHA256="+hfile(dest),flush=True)
    print("TTM_FRESH16_INFERENCE=NOT_EXECUTED",flush=True)
    print("TTM_FRESH16_TRAINING=NOT_EXECUTED",flush=True)
    if not source_pass:raise SystemExit(2)

if __name__=="__main__":
    try:run()
    except (OSError,ValueError,RuntimeError,KeyError,TypeError) as exc:
        print("TTM_FRESH16_PREFLIGHT_HOLD="+type(exc).__name__+":"+str(exc),
              file=sys.stderr,flush=True)
        raise SystemExit(3)
