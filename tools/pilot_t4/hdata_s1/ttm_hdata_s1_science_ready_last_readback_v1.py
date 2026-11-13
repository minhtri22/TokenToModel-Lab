#!/usr/bin/env python3
"""H-DATA-S1 owner-side READY-last readback, never trains or opens FINAL prompts.

Defaults to inventory; verify-complete checks durable SHA for all eight
checkpoints and both complete 128-step journals. It reads no TRAIN data.
A verified result remains UNADJUDICATED until independent scientific review.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os
from pathlib import Path

RUN_ID = "TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1"
RUN_ROOT = "/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_h_data_s1_20261113/science_one_shot_v1"
PARENT_SHA = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
PACK_SHA = "184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913"
RUNNER_SHA = "eae016e92adc862e71d98920844ebd7c36bacbc3c9157c5a5e33d31aa77ded28"
READY_STEPS = (1056, 1088, 1120, 1152)
STEP_RANGE = tuple(range(1025, 1153))
ARMS = ("H0", "H1")


def need(ok, code):
    if not ok:
        raise RuntimeError("HOLD_HDATA_S1_READY_LAST:" + code)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def read_json(path):
    p = Path(path)
    need(p.is_file() and not p.is_symlink(), "MISSING_OR_LINKED:" + str(p.name))
    return json.loads(p.read_text("utf-8"))


def inventory(root):
    output = {}
    for arm in ARMS:
        d = root / ("ARM_" + arm)
        output[arm] = {
            "exists": d.is_dir(),
            "ready_steps": [
                step for step in READY_STEPS
                if (d / ("checkpoint_%04d" % step) / "READY.json").is_file()
            ],
            "step_begin": len(list(d.glob("STEP_BEGIN_*.json"))) if d.is_dir() else 0,
            "step_done": len(list(d.glob("STEP_DONE_*.json"))) if d.is_dir() else 0,
            "final_unadjudicated": (d / "FINAL_UNADJUDICATED.json").is_file(),
        }
    return {
        "schema": "ttm.hdata_s1.owner_ready_inventory.v1",
        "status": "INVENTORY_ONLY_NOT_PROOF_OF_COMPLETION",
        "arms": output,
        "no_training_or_model_forward": True,
    }


def validate_arm(root, arm, lock_sha):
    import torch

    d = root / ("ARM_" + arm)
    need(d.is_dir() and not d.is_symlink(), "MISSING_ARM_" + arm)
    expected = set(STEP_RANGE)
    for prefix in ("STEP_BEGIN_", "STEP_DONE_"):
        files = list(d.glob(prefix + "*.json"))
        steps = []
        for p in files:
            need(p.is_file() and not p.is_symlink(), "STEP_JOURNAL_LINKED")
            suffix = p.stem[len(prefix):]
            need(len(suffix) == 4 and suffix.isdigit(), "STEP_JOURNAL_NAME")
            steps.append(int(suffix))
            obj = read_json(p)
            need(obj == {"step": int(suffix), "arm": arm}, "STEP_JOURNAL_CONTENT")
        need(len(files) == 128 and set(steps) == expected,
             "INCOMPLETE_128_JOURNAL_" + prefix + arm)

    folders = sorted(p.name for p in d.glob("checkpoint_*"))
    need(folders == ["checkpoint_%04d" % x for x in READY_STEPS],
         "UNKNOWN_OR_MISSING_READY_FOLDERS_" + arm)
    out = []
    last_payload = None
    for step in READY_STEPS:
        folder = d / ("checkpoint_%04d" % step)
        need(folder.is_dir() and not folder.is_symlink(), "CHECKPOINT_FOLDER_PATH")
        need(sorted(p.name for p in folder.iterdir()) == ["READY.json", "state.pt"],
             "CHECKPOINT_ORPHAN_OR_EXTRA")
        ready = read_json(folder / "READY.json")
        required = {
            "schema": "ttm.hdata_s1.ready.last.v1",
            "run_id": RUN_ID,
            "arm": arm,
            "step": step,
            "science_lock_sha256": lock_sha,
            "parent_sha256": PARENT_SHA,
            "pack_sha256": PACK_SHA,
        }
        need(all(ready.get(k) == v for k, v in required.items()),
             "READY_SCOPE_" + arm + "_" + str(step))
        cp = folder / "state.pt"
        need(cp.is_file() and not cp.is_symlink(), "CHECKPOINT_MISSING")
        digest = sha(cp)
        need(digest == ready.get("checkpoint_sha256"),
             "CHECKPOINT_SHA_" + arm + "_" + str(step))
        out.append({"step": step, "checkpoint_sha256": digest,
                    "checkpoint_bytes": cp.stat().st_size})
        if step == 1152:
            last_payload = torch.load(cp, map_location="cpu", weights_only=True)

    need(last_payload is not None and last_payload.get("step") == 1152 and
         last_payload.get("arm") == arm and last_payload.get("run_id") == RUN_ID,
         "LAST_CHECKPOINT_SCOPE_" + arm)
    state_fields = ("model", "optimizer", "scheduler", "sampler_state",
                    "grad_scaler_state", "h1_exposure", "torch_cpu_rng",
                    "torch_cuda_rng", "python_rng", "numpy_rng")
    need(all(k in last_payload for k in state_fields),
         "LAST_CHECKPOINT_STATE_INCOMPLETE_" + arm)
    need(len(last_payload["h1_exposure"]) == 2048,
         "H1_EXPOSURE_STATE_INCOMPLETE_" + arm)
    need(int(last_payload["scheduler"]["last_epoch"]) == 1152,
         "SCHEDULER_NOT_1152_" + arm)
    steps = [float(s["step"]) for s in last_payload["optimizer"]["state"].values()]
    need(steps and all(x == 1152 for x in steps),
         "ADAMW_OPTIMIZER_NOT_1152_" + arm)
    need(isinstance(last_payload["model"], dict) and last_payload["model"],
         "MODEL_STATE_NOT_FOUND_" + arm)

    final = read_json(d / "FINAL_UNADJUDICATED.json")
    last_sha = out[-1]["checkpoint_sha256"]
    need(final.get("run_id") == RUN_ID and final.get("arm") == arm and
         final.get("step") == 1152 and
         final.get("last_ready_checkpoint_sha256") == last_sha and
         final.get("valid_target_presentations") == 128 * 4096 and
         final.get("science_outcome") == "UNADJUDICATED_NO_FINAL_INFERENCE",
         "FINAL_RECEIPT_MISMATCH_" + arm)
    val = final.get("val") or {}
    need(val.get("val_target_count") == 61122 and
         val.get("val_story_count") == 256 and
         val.get("never_test") is True and
         isinstance(val.get("val_nll"), (int, float)) and
         math.isfinite(val["val_nll"]),
         "VAL_RECEIPT_INVALID_" + arm)

    return {
        "arm": arm, "status": "PASS_FULL_128_READY_LAST",
        "steps": 128, "start_step": 1025, "end_step": 1152,
        "valid_target_presentations": 128 * 4096,
        "ready": out,
        "model_optimizer_scheduler_rng_checkpoint_present": True,
        "val_nll": val["val_nll"],
        "val_target_count": 61122,
        "FINAL_prompt_text_read": False,
    }


def verify(root, lock, lock_sha):
    need(str(root.resolve()) == RUN_ROOT and root.is_dir() and not root.is_symlink(),
         "RUN_ROOT_NOT_EXACT")
    need(sha(lock) == lock_sha, "GO_LOCK_SHA")
    locked = read_json(lock)
    need(locked.get("authorization") == "TTM_HDATA_S1_SCIENCE_ONE_SHOT_GO" and
         locked.get("run_id") == RUN_ID and
         locked.get("science_run_root") == RUN_ROOT and
         locked.get("science_runner_sha256") == RUNNER_SHA,
         "SCIENCE_LOCK_SCOPE")
    manifest = read_json(root / "RUN_MANIFEST.json")
    need(manifest == {
        "run_id": RUN_ID,
        "owner_lock_sha256": lock_sha,
        "science_source_sha256": RUNNER_SHA,
        "arms": ["H0", "H1"],
    }, "RUN_MANIFEST")
    expected_subdirs = {"ARM_H0", "ARM_H1", "RUN_MANIFEST.json"}
    need(set(p.name for p in root.iterdir()) == expected_subdirs,
         "UNKNOWN_RUN_ROOT_CHILD")
    arm_data = [validate_arm(root, arm, lock_sha) for arm in ARMS]
    return {
        "schema": "ttm.hdata_s1.ready_last_owner_readback.v1",
        "status": "PASS_TWO_ARM_128_STEP_READY_LAST_UNADJUDICATED",
        "run_id": RUN_ID,
        "owner_science_lock_sha256": lock_sha,
        "science_runner_sha256": RUNNER_SHA,
        "frozen_parent_sha256": PARENT_SHA,
        "frozen_train_pack_sha256": PACK_SHA,
        "arms": arm_data,
        "science_optimizer_updates_attested": 256,
        "valid_target_presentations_attested": 2 * 128 * 4096,
        "science_inference": "NOT_EXECUTED_BY_THIS_CHECKER",
        "NEW_FINAL": "SEALED_NOT_READ",
        "TEST_Q1_Q2_OOD": "SEALED_NOT_READ",
        "independent_scientific_adjudication": "PENDING",
        "no_model_forward_by_checker": True,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("inventory", "verify-complete"),
                    default="inventory")
    ap.add_argument("--root", required=True)
    ap.add_argument("--lock")
    ap.add_argument("--lock-sha")
    ap.add_argument("--out")
    a = ap.parse_args()
    root = Path(a.root)
    if a.mode == "inventory":
        print(json.dumps(inventory(root), indent=2, sort_keys=True))
        return
    need(bool(a.lock and a.lock_sha and a.out), "MISSING_VERIFY_ARGUMENT")
    need(not Path(a.out).exists(), "RECEIPT_ALREADY_EXISTS_NO_OVERWRITE")
    receipt = verify(root, Path(a.lock), a.lock_sha)
    with open(a.out, "x", encoding="utf-8") as f:
        json.dump(receipt, f, sort_keys=True, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    print("HDATA_S1_SCIENCE_READY_LAST=" + receipt["status"])
    print("HDATA_S1_READY_LAST_RECEIPT_SHA256=" + sha(a.out))
    print("HDATA_S1_NEW_FINAL=SEALED")


if __name__ == "__main__":
    main()
