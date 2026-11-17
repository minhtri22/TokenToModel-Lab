"""Fail-closed recovery when original Colab ephemeral TECH40 receipts are missing.

This is NOT a reuse or reconstruction of original TECH40 bytes. A NEW synthetic
40-step full P02 diagnostic writes its own raw receipt to owner Google Drive.
Then a fresh seed-pinned TinyStories 1024 and paired historical VAL may run
under a separate, prospective PM single Q4 on a user-operated Tesla T4.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

SCHEMA = "ttm.pm.fresh40_recovery_science.v1"
Q4_BLOB = "e819caf233d285606bd20af52e22702f54ba0917"
EXPECTED_DECISION = "GO_CONDITIONAL_FRESH_TECH40_RECOVERY_1024_VAL_ONLY"
RUN_PREFIX = "TTM_FRESH40_RECOVERY__"
VALID_RUN_ID = r"[A-Za-z0-9_-]{8,65}"
ORIGINAL_PARENT = "/content/TTM_MATCHED_4M_SESSIONS"
DRIVE_ROOT = "/content/drive/MyDrive/TTM/ttm-small-pilot"
RECOVERY_LOCK = "RECOVERY_Q4_LOCK.json"
TECH40_RECEIPT = "TECHNICAL_SYNTHETIC_40.json"

def raw_hash(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()

def git_blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()

def write_once(path,data):
    path=Path(path)
    if path.exists() or path.is_symlink() or path.parent.is_symlink():
        raise FileExistsError("ONE_SHOT_ALREADY_EXISTS:"+path.name)
    with path.open("xb") as f:
        f.write((json.dumps(data,sort_keys=True,ensure_ascii=False,separators=(",",":"))+"\n").encode("utf8"))
        f.flush();os.fsync(f.fileno())

def read_json(path):
    p=Path(path)
    if not p.is_file() or p.is_symlink():
        raise ValueError("MISSING_LOCK_OR_SYMLINK:"+p.name)
    return json.loads(p.read_bytes())

def read_q4(path,bridge):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or git_blob(p.read_bytes().replace(b"\r\n", b"\n"))!=Q4_BLOB:
        raise ValueError("EXACT_RECOVERY_Q4_GIT_BLOB_REQUIRED")
    o=json.loads(p.read_bytes())
    expected={
        "schema":"ttm.pm.fresh_40_recovery_then_1024.val.q4.v1",
        "decision":EXPECTED_DECISION,
        "exact_original_runner_git_blob":bridge.OLD_RUNNER_BLOB,
        "exact_repaired_runner_git_blob":bridge.NEW_RUNNER_BLOB,
        "private_train_val_sha256":bridge.DATA_SHA,
        "private_manifest_sha256":bridge.MANIFEST_SHA,
        "historical_left_1024_checkpoint_sha256":bridge.HISTORICAL_CHECKPOINT_SHA,
        "recipe_sha256":bridge.RECIPE_SHA,
    }
    if any(o.get(k)!=v for k,v in expected.items()) or o.get("no_merge") is not True or o.get("test")!="SEALED_NO_ACCESS":
        raise ValueError("RECOVERY_Q4_AUTHORIZATION_CONTRACT_DRIFT")
    return raw_hash(p)

def guard_not_original_available(original_parent,drive_root):
    """Reject recovery if an actual original receipt appears in known locations."""
    parent=Path(original_parent)
    if parent.is_symlink():
        raise ValueError("ORIGINAL_PARENT_SYMLINK")
    if parent.exists():
        if not parent.is_dir():
            raise ValueError("ORIGINAL_PARENT_NOT_DIRECTORY")
        for candidate in parent.glob("TTM_40_1024__*/TECHNICAL_SYNTHETIC_40.json"):
            if candidate.is_file():
                raise ValueError("USE_ORIGINAL_TECH40_BRIDGE_INSTEAD:"+str(candidate))
    # Search only the owner TTM subtree, with a bounded directory count.
    base=Path(drive_root)
    if base.is_symlink() or not base.is_dir():
        raise ValueError("OWNER_GOOGLE_DRIVE_ROOT_NOT_MOUNTED_OR_SYMLINK")
    checked=0
    for folder, dirs, files in os.walk(base, followlinks=False):
        checked+=1
        if checked>2500:
            raise ValueError("DRIVE_SEARCH_CAP_EXCEEDED_HOLD")
        # Fresh recovery receipts are distinct events, never old TECH40 backups.
        # Skip these on both first-run and checkpoint resume.
        dirs[:]=[d for d in dirs if not (Path(folder)/d).is_symlink()
                 and not d.startswith(RUN_PREFIX)]
        if "TECHNICAL_SYNTHETIC_40.json" in files:
            raise ValueError("POSSIBLE_ORIGINAL_RECEIPT_BACKUP_USE_BRIDGE:"+str(Path(folder)/TECH40_RECEIPT))
    return checked

def load_bridge(path):
    p=Path(path)
    if not p.is_file() or p.is_symlink():
        raise ValueError("BRIDGE_MODULE_MISSING")
    spec=importlib.util.spec_from_file_location("ttm_tech40_recovery_bridge",p)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

def preflight(args):
    bridge=load_bridge(args.bridge)
    original=bridge.import_runner(args.old_runner)
    equivalence=bridge.source_equivalence(args.old_runner,args.new_runner)
    q4_sha=read_q4(args.q4,bridge)
    if not re.fullmatch(VALID_RUN_ID,args.run_id):
        raise ValueError("FRESH_RECOVERY_RUN_ID_INVALID")
    original.verify_sources(args.sources)
    original.validate_pack_files(args.data,args.manifest)
    checkpoint=bridge.require_plain_file(args.historical_checkpoint)
    if raw_hash(checkpoint)!=bridge.HISTORICAL_CHECKPOINT_SHA:
        raise ValueError("HISTORICAL_LEFT_CHECKPOINT_SHA_DRIFT")
    base=Path(args.durable_parent)
    if base.is_symlink() or not base.is_dir() or base.resolve(strict=True)!=Path(DRIVE_ROOT).resolve(strict=True):
        raise ValueError("RECOVERY_PARENT_MUST_BE_OWNER_DRIVE_ROOT")
    scanned=guard_not_original_available(args.original_parent,DRIVE_ROOT)
    root=base/(RUN_PREFIX+args.run_id)
    if args.mode in ("preflight","onepack") and root.exists():
        raise FileExistsError("RECOVERY_RUN_ALREADY_EXISTS_NO_OVERWRITE")
    if args.mode=="resume" and (root.is_symlink() or not root.is_dir()):
        raise ValueError("RECOVERY_RESUME_ORIGINAL_ROOT_REQUIRED")
    gpu=None
    if args.mode in ("onepack","resume"):
        import torch
        gpu=original.cuda_guard(torch)
    result={
        "schema":SCHEMA+".preflight",
        "status":"PASS_RECOVERY_ADMISSION_SCOPED_NOT_SCIENCE" if args.mode=="preflight" else "PASS_Q4_RESOURCE_AND_CUSTODY_BEFORE_DISPATCH",
        "action":args.mode,"q4_sha256":q4_sha,
        "original_session": "NOT_FOUND_AT_EXPECTED_PARENT",
        "root":str(root),"run_id":args.run_id,
        "source_equivalence":equivalence,"drive_directories_scanned":scanned,
        "private_train_val_sha256":bridge.DATA_SHA,
        "historical_checkpoint_sha256":bridge.HISTORICAL_CHECKPOINT_SHA,
        "tesla_t4_readback":gpu,
        "test_accessed":False,"science_executed":False}
    return original,bridge,root,result

def run(args):
    old,bridge,root,pre=preflight(args)
    receipt=root/TECH40_RECEIPT
    lockfile=root/RECOVERY_LOCK
    training=root/"runs"/("replica_1024__"+args.run_id)
    paired=root/"PAIRED_HISTORICAL_VAL_1024.json"
    closure=root/"RECOVERY_FINAL_UNADJUDICATED.json"
    if args.mode=="onepack":
        root.mkdir(exist_ok=False)
        write_once(lockfile,{
            "schema":SCHEMA+".lock",
            "run_id":args.run_id,"q4_sha256":pre["q4_sha256"],
            "old_runner_blob":bridge.OLD_RUNNER_BLOB,
            "new_runner_blob":bridge.NEW_RUNNER_BLOB,
            "recipe_sha256":bridge.RECIPE_SHA,
            "pack_sha256":bridge.DATA_SHA,
            "historical_left_sha256":bridge.HISTORICAL_CHECKPOINT_SHA,
            "fresh_tech40":True,
            "old_tech40_receipt_reused":False,
            "test_accessed":False})
        print("RECOVERY_SYNTHETIC40_FRESH_RUN_NOT_REUSE",flush=True)
        old.synthetic_40(argparse.Namespace(sources=args.sources,out=str(receipt)))
        print("RECOVERY_TECH40_SHA256="+raw_hash(receipt),flush=True)
    else:
        lock=read_json(lockfile)
        if (lock.get("run_id")!=args.run_id or lock.get("q4_sha256")!=pre["q4_sha256"]
                or lock.get("old_runner_blob")!=bridge.OLD_RUNNER_BLOB
                or lock.get("recipe_sha256")!=bridge.RECIPE_SHA
                or lock.get("old_tech40_receipt_reused") is not False):
            raise ValueError("RECOVERY_RESUME_LOCK_DRIFT")
        if not receipt.is_file() or receipt.is_symlink():
            raise ValueError("RECOVERY_RECEIPT_MISSING")
    capacity_sha=old.require_capacity(receipt,"replica_1024")
    if args.mode=="resume":
        if args.resume_step is None and not (training/"FINAL.json").is_file():
            raise ValueError("RECOVERY_RESUME_EXPLICIT_READY_STEP_REQUIRED")
        if args.resume_step is not None and (training/"FINAL.json").is_file():
            raise ValueError("RECOVERY_ALREADY_TRAINED_NO_RESUME_STEP")
    train_args=argparse.Namespace(
        arm="replica_1024",run_id=args.run_id,
        data=args.data,manifest=args.manifest,sources=args.sources,
        capacity=str(receipt),go=str(args.q4),out=str(training),
        resume_step=args.resume_step)
    authorized={"go_sha256":pre["q4_sha256"],
                "capacity_sha256":capacity_sha,"run_id":args.run_id}
    if not (training/"FINAL.json").is_file():
        training.parent.mkdir(parents=True,exist_ok=True)
        old.train(train_args,verified_integrated=authorized)
    ready=old.checked_ready(old.checkpoint_dir(training,1024),1024)
    right=old.checkpoint_dir(training,1024)/"checkpoint.pt"
    if ready.get("go_sha256")!=pre["q4_sha256"]:
        raise ValueError("RECOVERY_FINAL_READY_GO_SHA_DRIFT")
    if not paired.exists():
        old.compare(argparse.Namespace(
            sources=args.sources,data=args.data,manifest=args.manifest,
            arm="replica_1024",run_id=args.run_id,go=str(args.q4),
            left=str(args.historical_checkpoint),right=str(right),out=str(paired)),
            verified_integrated=authorized)
    else:
        p=read_json(paired)
        if p.get("checkpoints_sha256")!=[bridge.HISTORICAL_CHECKPOINT_SHA,raw_hash(right)]:
            raise ValueError("RECOVERY_EXISTING_PAIRED_VAL_DRIFT")
    result={
        "schema":SCHEMA+".closure",
        "status":"NEW40_NEW1024_PAIRED_HISTORICAL_VAL_COMPLETE_UNADJUDICATED",
        "fresh_40_rerun_due_to_lost_old_session":True,
        "old_40_receipt_reused":False,
        "fresh_tech40_receipt_sha256":capacity_sha,
        "new_checkpoint_sha256":raw_hash(right),
        "paired_val_sha256":raw_hash(paired),
        "q4_sha256":pre["q4_sha256"],
        "test_accessed":False,"science_interpretation":"REPLICATION_ONLY"}
    if closure.exists():
        if read_json(closure)!=result:
            raise ValueError("RECOVERY_FINAL_CLOSURE_DRIFT")
    else:
        write_once(closure,result)
    print(json.dumps(result,sort_keys=True),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["preflight","onepack","resume"])
    for key in ["old_runner","new_runner","bridge","q4","sources","data","manifest",
                "historical_checkpoint","durable_parent","original_parent","run_id"]:
        p.add_argument("--"+key.replace("_","-"),required=True)
    p.add_argument("--resume-step",type=int,choices=[256,512,768])
    args=p.parse_args()
    if sys.version_info[:2]!=(3,12):
        raise ValueError("PYTHON312_REQUIRED")
    if args.mode=="preflight":
        _,_,_,result=preflight(args)
        print(json.dumps(result,sort_keys=True),flush=True)
    else:run(args)

if __name__=="__main__":
    main()
