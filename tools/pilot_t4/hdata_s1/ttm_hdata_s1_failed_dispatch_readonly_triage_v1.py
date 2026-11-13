#!/usr/bin/env python3
"""Read-only triage of failed H-DATA-S1 owner T4 science dispatch.

No model forward, optimizer update, file write, overwrite, deletion, or resume.
No AES key, no FINAL text, no private TRAIN arrays. Only metadata, file names,
SHA-256 of small public/manifest files and fixed status fields.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys

EXPECTED_ROOT = pathlib.Path("/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_h_data_s1_20261113/science_one_shot_v1")
ARM_NAMES = ("H0", "H1")
READY_STEPS = (1056, 1088, 1120, 1152)

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def readable(path):
    if not path.is_file() or path.is_symlink():
        return None
    try:
        return json.loads(path.read_text("utf-8"))
    except (OSError, ValueError):
        return None

def markers(armdir):
    if not armdir.is_dir():
        return {"exists": False, "begin_count": 0, "done_count": 0, "ready_steps": []}
    b=list(armdir.glob("STEP_BEGIN_*.json"))
    d=list(armdir.glob("STEP_DONE_*.json"))
    begin=sorted(x.stem.removeprefix("STEP_BEGIN_") for x in b)
    done=sorted(x.stem.removeprefix("STEP_DONE_") for x in d)
    ready=[]
    orphan=[]
    for step in READY_STEPS:
        x=armdir / ("checkpoint_%04d"%step)
        cp=x/"state.pt"; flag=x/"READY.json"
        if cp.exists() and flag.exists() and not cp.is_symlink() and not flag.is_symlink():
            r=readable(flag)
            ready.append({"step":step,
                          "reported_step":r.get("step") if isinstance(r,dict) else None,
                          "sha256_matches":sha(cp)==r.get("checkpoint_sha256") if isinstance(r,dict) else False,
                          "checkpoint_bytes":cp.stat().st_size})
        elif cp.exists() or flag.exists() or x.exists():
            orphan.append(step)
    bad_inflight=sorted(set(begin)-set(done))
    return {"exists":True,
            "begin_count":len(begin),"done_count":len(done),
            "first_begin":begin[0] if begin else None,
            "last_begin":begin[-1] if begin else None,
            "last_done":done[-1] if done else None,
            "begin_without_done":bad_inflight[:8],
            "begin_without_done_count":len(bad_inflight),
            "ready_steps":ready,
            "orphan_ready_steps":orphan,
            "final_unadjudicated_file_exists":(armdir/"FINAL_UNADJUDICATED.json").is_file()}

def triage(root):
    result={
      "operation":"TTM_HDATA_S1_SCIENCE_DISPATCH_FAILURE_READONLY_TRIAGE",
      "status":"HOLD_NO_RERUN_NO_RESUME_PENDING_ROOT_AND_ORIGINAL_STDERR",
      "run_root_exists":root.exists(),
      "run_root_is_symlink":root.is_symlink(),
      "root_is_directory":root.is_dir(),
      "root_resolved_matches_frozen":str(root.resolve())==str(EXPECTED_ROOT),
      "owner_private_key_read":False,
      "new_FINAL_read":False,
      "TEST_Q1_Q2_OOD_read":False,
      "model_forward_from_triage":False,
      "optimizer_updates_from_triage":0,
      "file_writes_from_triage":0,
      "source_stderr_available_in_this_triage":False
    }
    if not root.exists():
        result["phase_hint"]="BEFORE_RUN_ROOT_CREATION_OR_DRIVE_MOUNT_VISIBILITY_DELAY"
        return result
    if not root.is_dir() or root.is_symlink():
        result["phase_hint"]="ROOT_TYPE_OR_SYMLINK_BLOCKER"
        return result
    manifest=readable(root/"RUN_MANIFEST.json")
    result["run_manifest_exists"]=(root/"RUN_MANIFEST.json").is_file()
    result["run_manifest_present_and_parseable"]=isinstance(manifest,dict)
    if isinstance(manifest,dict):
        result["run_manifest_sha256"]=sha(root/"RUN_MANIFEST.json")
        result["run_id_matches"]=manifest.get("run_id")=="TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1"
        result["arms_match"]=manifest.get("arms")==["H0","H1"]
    result["root_entry_names"]=sorted(p.name for p in root.iterdir())[:20]
    result["arms"]={arm:markers(root/("ARM_"+arm)) for arm in ARM_NAMES}
    if any(v.get("begin_count",0)>v.get("done_count",0) for v in result["arms"].values()):
        result["phase_hint"]="IN_FLIGHT_STEP_DETECTED__DO_NOT_RESUME_AUTOMATICALLY"
    elif any(v.get("done_count",0)>0 for v in result["arms"].values()):
        result["phase_hint"]="SOME_COMPLETE_STEPS_OBSERVED__AUDIT_READY_LAST_BEFORE_DECISION"
    elif any(v.get("exists",False) for v in result["arms"].values()):
        result["phase_hint"]="ARM_CREATED_BEFORE_STEP_JOURNAL"
    else:
        result["phase_hint"]="RUN_ROOT_CREATED_BEFORE_ARM_STEPS"
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=str(EXPECTED_ROOT))
    args=ap.parse_args()
    root=pathlib.Path(args.root)
    print(json.dumps(triage(root),ensure_ascii=False,sort_keys=True,indent=2))
    print("HDATA_S1_DIAG_READ_ONLY=TRUE")
    print("HDATA_S1_SCIENCE_RESUME=NOT_AUTHORIZED_BY_TRIAGE")
if __name__=="__main__":
    main()
