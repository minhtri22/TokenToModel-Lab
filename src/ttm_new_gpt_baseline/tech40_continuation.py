"""Owner-scoped, one-shot continuation of old TECH40 into matched TinyStories@1024.

DOES NOT rerun synthetic40. Original receipt must exist as original bytes.
One PM Q4 decision file covers new random-init 1024 + paired historical VAL.
No original TinyStories TEST access. Separate fresh output on durable owner Drive.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
import time

SCHEMA = "ttm.pm.tech40_to_1024.bridge.v1"
SOURCE_MAIN = "59ee3f30b996405fddc087ab60102b59a021f8ea"
OLD_RUNNER_BLOB = "113434e25fe19cff27b47f428cf99a0a57ae4fcf"
NEW_RUNNER_BLOB = "933f42b514de5fac650bfa2a421844c51b9b7c64"
Q4_DECISION_BLOB = "8b99e436dd1c31bde3c684167be8a475a73b0dcc"
TECH40_SHA_FROM_USER_STDOUT = "1a273db7f175578cdc9cf6a976d4679835a42d86a1c0c1604a6ea4e64596a1d9"
DATA_SHA = "184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913"
MANIFEST_SHA = "ef2e6e67d49b1d5a921b1051df329f15574f1c10cece49468acb53322d650"
HISTORICAL_CHECKPOINT_SHA = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
RECIPE_SHA = "d116c92ee1126a91acb1e54d1ff80f08a18ca97bdc8220467a4898426d01d1e3"
GO_DECISION = "GO_CONDITIONAL_EXACT_OLD_TECH40_CUSTODY_FOR_1024_REPLICATION_VAL_ONLY"
ROOT_PREFIX = "TTM_40_1024__"
CLAIM_NAME = "PM_TECH40_CONTINUATION_ONCE_CLAIM.json"
CUSTODY_FUNCTIONS = (
    "canonical", "sha_bytes", "sha_file", "git_blob", "source_blob",
    "plan_of", "recipe", "recipe_hash", "provenance_check",
    "validate_pack_files", "runtime_sources", "capacity", "require_capacity",
    "prepare_model", "checkpoint_dir", "durable_checkpoint", "checked_ready",
    "resume_state", "train", "paired_bootstrap", "compare", "synthetic_40",
)
ALLOWED_WRAPPER_DIFFS = ("cuda_guard", "one_session", "main", "live_t4_preflight")

def jbytes(v):
    return (json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")

def hash_bytes(raw):
    return hashlib.sha256(raw).hexdigest()

def hash_file(path):
    obj = hashlib.sha256()
    with Path(path).open("rb") as f:
        for data in iter(lambda: f.read(1 << 20), b""):
            obj.update(data)
    return obj.hexdigest()

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def require_plain_file(path):
    p = Path(path)
    if not p.is_file() or p.is_symlink():
        raise ValueError("MISSING_OR_SYMLINK_FILE:" + p.name)
    return p

def read_exact_json(path):
    p = require_plain_file(path)
    return json.loads(p.read_bytes())

def write_once(path, data):
    p = Path(path)
    if p.is_symlink() or p.exists() or p.parent.is_symlink():
        raise FileExistsError("ONE_SHOT_OUTPUT_EXISTS:" + p.name)
    with p.open("xb") as f:
        f.write(jbytes(data))
        f.flush()
        os.fsync(f.fileno())

def import_runner(path):
    path = require_plain_file(path)
    if git_blob(path.read_bytes()) != OLD_RUNNER_BLOB:
        raise ValueError("EXECUTED_OLD_RUNNER_BLOB_DRIFT")
    spec = importlib.util.spec_from_file_location("ttm_frozen_old_runner_tech40_science", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    if mod.source_blob() != OLD_RUNNER_BLOB:
        raise ValueError("ORIGINAL_RUNNER_SELF_BLOB_DRIFT")
    return mod

def _function_texts(raw):
    text = raw.decode("utf-8")
    tree = ast.parse(text)
    return {n.name: ast.get_source_segment(text, n)
            for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

def source_equivalence(old_file, new_file):
    old = require_plain_file(old_file).read_bytes().replace(b"\r\n", b"\n")
    new = require_plain_file(new_file).read_bytes().replace(b"\r\n", b"\n")
    if git_blob(old) != OLD_RUNNER_BLOB or git_blob(new) != NEW_RUNNER_BLOB:
        raise ValueError("BRIDGE_OLD_NEW_EXACT_GIT_BLOB_MISMATCH")
    of, nf = _function_texts(old), _function_texts(new)
    for function in CUSTODY_FUNCTIONS:
        if function not in of or function not in nf or of[function] != nf[function]:
            raise ValueError("BRIDGE_SCIENCE_FUNCTION_DRIFT:" + function)
    if "cuda_guard" not in of or "cuda_guard" not in nf:
        raise ValueError("BRIDGE_GPU_GUARD_MISSING")
    # Only wrappers changed; if a new unrelated function appears, reject it.
    old_functions = set(of)
    new_functions = set(nf)
    if (new_functions - old_functions) != {"live_t4_preflight"} or (old_functions - new_functions):
        raise ValueError("BRIDGE_FUNCTION_SET_UNEXPECTED_CHANGE")
    differing = sorted(n for n in old_functions & new_functions if of[n] != nf[n])
    if differing != sorted(x for x in ALLOWED_WRAPPER_DIFFS if x != "live_t4_preflight"):
        raise ValueError("BRIDGE_UNREVIEWED_FUNCTION_DIFFERENCE:" + repr(differing))
    return {
        "old_runner_blob": OLD_RUNNER_BLOB, "new_runner_blob": NEW_RUNNER_BLOB,
        "science_functions_identical_exact_bytes": list(CUSTODY_FUNCTIONS),
        "wrapper_changes_only": differing + ["live_t4_preflight"],
        "status": "PASS_EXACT_BYTE_FUNCTION_SCOPE_NOT_FULL_SEMANTIC_EQUIVALENCE",
    }

def q4_readback(path):
    p = require_plain_file(path)
    raw = p.read_bytes().replace(b"\r\n", b"\n")
    if git_blob(raw) != Q4_DECISION_BLOB:
        raise ValueError("Q4_GITHUB_GIT_BLOB_DRIFT")
    o = json.loads(raw)
    expected = {
        "schema": "ttm.pm.tech40_reuse_tinystories1024.q4.onepacket.v1",
        "decision": GO_DECISION,
        "expected_original_tech40_receipt_sha256_from_owner_stdout_canonical_candidate": TECH40_SHA_FROM_USER_STDOUT,
        "frozen_old_runner_git_blob": OLD_RUNNER_BLOB,
        "source_repair_runner_git_blob": NEW_RUNNER_BLOB,
        "historical_train_val_pack_sha256": DATA_SHA,
        "historical_pack_manifest_sha256": MANIFEST_SHA,
        "historical_original_checkpoint_1024_sha256": HISTORICAL_CHECKPOINT_SHA,
        "science_recipe_sha256": RECIPE_SHA,
        "scope": "INTERNAL_RESEARCH_DEVELOPMENT_VAL_ONLY",
    }
    if any(o.get(k) != v for k, v in expected.items()) or o.get("main_merge") is not False:
        raise ValueError("Q4_DECISION_CONTENT_DRIFT")
    if o.get("historical_test") != "SEALED_ALREADY_CONSUMED_NOT_USED":
        raise ValueError("Q4_HISTORICAL_TEST_SCOPE_DRIFT")
    return {"q4_sha256": hash_bytes(raw), "decision": o["decision"], "q4_git_blob": Q4_DECISION_BLOB}

def original_receipt_readback(root, frozen_runner):
    root = Path(root).resolve(strict=True)
    if not root.is_dir() or root.is_symlink() or not root.name.startswith(ROOT_PREFIX):
        raise ValueError("ORIGINAL_TECH40_SESSION_ROOT_INVALID")
    old_run_id = root.name[len(ROOT_PREFIX):]
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,80}", old_run_id):
        raise ValueError("ORIGINAL_SESSION_RUN_ID_INVALID")
    paths = {k: require_plain_file(root / k) for k in
             ("TECHNICAL_SYNTHETIC_40.json", "SESSION_LOCK.json", "SESSION_STATUS.json")}
    tech_path = paths["TECHNICAL_SYNTHETIC_40.json"]
    raw = tech_path.read_bytes()
    sha = hash_bytes(raw)
    if sha != TECH40_SHA_FROM_USER_STDOUT:
        raise ValueError("HOLD_RECEIPT_RAW_BYTES_NOT_EQUAL_TO_TRANSCRIPT_CANDIDATE:" + sha)
    tech = json.loads(raw)
    lock = json.loads(paths["SESSION_LOCK.json"].read_bytes())
    status = json.loads(paths["SESSION_STATUS.json"].read_bytes())
    expected_lock = {
        "schema": "ttm.matched_4m.one_session_lock.v1",
        "run_id": old_run_id,
        "runner_git_blob": OLD_RUNNER_BLOB,
        "recipe_sha256": RECIPE_SHA,
        "private_train_val_sha256": DATA_SHA,
        "historic_left_sha256": HISTORICAL_CHECKPOINT_SHA,
        "integrated_go_sha256": None,
        "synthetic40_independent_initialization": True,
        "test_accessed": False,
    }
    expected_status = {
        "schema": "ttm.matched_4m.one_session_status.v1",
        "status": "TECHNICAL_40_PASS_SCIENCE_HOLD_NO_Q4",
        "technical_receipt_sha256": sha,
        "science_executed": False,
        "compare_executed": False,
        "test_accessed": False,
    }
    if lock != expected_lock or status != expected_status:
        raise ValueError("ORIGINAL_SESSION_LOCK_OR_TERMINAL_STATUS_MISMATCH")
    if ((root / "runs").exists() or (root / "PAIRED_HISTORICAL_VAL_1024.json").exists()):
        raise ValueError("ORIGINAL_TECH40_SESSION_CONTAINS_SCIENCE")
    required = {
        "schema": "ttm.matched_4m.synthetic40.v1",
        "status": "PASS_FULL_P02_SYNTHETIC_40_SCOPED",
        "runner_git_blob": OLD_RUNNER_BLOB,
        "recipe_1024_sha256": RECIPE_SHA,
        "steps_executed": 40,
        "tokens_per_step": 4096,
        "synthetic_target_exposures": 163840,
        "architecture_parameters": 3749376,
        "context": 256,
        "data_kind": "UNIFORM_RANDOM_SYNTHETIC_NO_TINYSTORIES",
        "training_weights_exported": False, "transfer_to_new_science": False,
        "checkpoint_created": False,
        "test_accessed": False, "science_executed": False,
        "owner_q4": "HOLD_WITHOUT_EXPLICIT_INTEGRATED_GO",
    }
    if any(tech.get(k) != v for k, v in required.items()):
        raise ValueError("ORIGINAL_TECH40_METADATA_DRIFT")
    env = tech.get("env") or {}
    trial = tech.get("trial") or {}
    if (env.get("gpu") != "Tesla T4" or not str(env.get("python", "")).startswith("3.12.")
            or env.get("cuda") != "12.8" or env.get("torch") != "2.11.0+cu128"
            or env.get("total_mib") != 14912
            or trial.get("warmup_steps") != 2 or trial.get("timed_steps") != 38
            or trial.get("scored_target_tokens_per_optimizer_step") != 4096
            or trial.get("precision") != "fp16" or trial.get("context") != 256
            or trial.get("microbatch_windows") != 8
            or trial.get("gradient_accumulation") != 2
            or len(trial.get("sample_seconds", [])) != 38):
        raise ValueError("ORIGINAL_TECH40_T4_RUNTIME_CONTRACT_DRIFT")
    measured = trial["sample_seconds"]
    if any(not isinstance(s, (int, float)) or not math.isfinite(s) or s <= 0 for s in measured):
        raise ValueError("ORIGINAL_TECH40_STEP_TIMES_INVALID")
    if abs(max(measured) - trial.get("worst_seconds", -1)) > 0.00001:
        raise ValueError("ORIGINAL_TECH40_MEASURED_WORST_STEP_DRIFT")
    if (tech.get("reserved_ratio", 1) > .8
            or tech.get("projected_1024_seconds_with_reserve", 999999) > 5400):
        raise ValueError("ORIGINAL_TECH40_RESOURCE_BUDGET_FAIL")
    if frozen_runner.recipe_hash("replica_1024") != RECIPE_SHA:
        raise ValueError("ORIGINAL_RECIPE_DRIFT")
    if frozen_runner.require_capacity(tech_path, "replica_1024") != sha:
        raise ValueError("ORIGINAL_RECEIPT_RESOURCE_READBACK_DRIFT")
    return {
        "original_run_id": old_run_id,
        "original_session": str(root),
        "original_tech40_receipt_sha256": sha,
        "original_session_lock_sha256": hash_file(paths["SESSION_LOCK.json"]),
        "original_terminal_status_sha256": hash_file(paths["SESSION_STATUS.json"]),
        "technical_steps": 40, "real_t4": True,
        "science_executed": False, "historic_test_accessed": False,
        "status": "PASS_REAL_T4_TECH40_RAW_BYTE_READBACK",
    }

def find_original(root_parent, requested=None):
    if requested:
        return Path(requested)
    base = Path(root_parent)
    if not base.is_dir() or base.is_symlink():
        raise ValueError("ORIGINAL_SESSION_PARENT_MISSING")
    found = []
    for d in base.glob(ROOT_PREFIX + "*"):
        if d.is_dir() and not d.is_symlink() and (d / "TECHNICAL_SYNTHETIC_40.json").is_file():
            found.append(d)
    if len(found) != 1:
        raise ValueError("ORIGINAL_TECH40_SESSION_NOT_UNIQUE_OR_MISSING:" + str(len(found)))
    return found[0]

def durable_output_path(parent, original_run_id):
    p = Path(parent).resolve(strict=True)
    required = Path("/content/drive/MyDrive/TTM/ttm-small-pilot").resolve(strict=True)
    if p.is_symlink() or not p.is_dir() or not p.is_relative_to(required):
        raise ValueError("DURABLE_OUTPUT_MUST_BE_IN_OWNER_MOUNTED_TTM_DRIVE")
    new_run_id = "adopt_" + original_run_id
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,80}", new_run_id):
        raise ValueError("CONTINUATION_RUN_ID_TOO_LONG")
    return p / ("replica_1024__" + new_run_id), new_run_id

def claim_payload(custody, equivalence, decision, output_root):
    return {
        "schema": SCHEMA + ".single_use_claim",
        "old_session": custody["original_session"],
        "old_run_id": custody["original_run_id"],
        "raw_receipt_sha256": custody["original_tech40_receipt_sha256"],
        "terminal_status_sha256": custody["original_terminal_status_sha256"],
        "old_runner_blob": OLD_RUNNER_BLOB, "new_runner_blob": NEW_RUNNER_BLOB,
        "verified_science_functions": equivalence["science_functions_identical_exact_bytes"],
        "pm_q4_sha256": decision["q4_sha256"],
        "target_run_path": str(output_root),
        "target_run_id": output_root.name.split("__", 1)[-1],
        "test_accessed": False,
    }

def preflight(args):
    old = import_runner(args.old_runner)
    equivalence = source_equivalence(args.old_runner, args.new_runner)
    decision = q4_readback(args.q4)
    source_root = find_original(args.old_sessions_parent, args.original_session)
    custody = original_receipt_readback(source_root, old)
    # Private file byte readback only at preflight, no model initialization.
    old.verify_sources(args.sources)
    old.validate_pack_files(args.data, args.manifest)
    checkpoint = require_plain_file(args.historical_checkpoint)
    if hash_file(checkpoint) != HISTORICAL_CHECKPOINT_SHA:
        raise ValueError("HISTORICAL_LEFT_CHECKPOINT_SHA_DRIFT")
    output_root, new_run_id = durable_output_path(args.durable_output_parent, custody["original_run_id"])
    old_cuda = None
    if args.mode == "continue":
        import torch
        old_cuda = old.cuda_guard(torch)
    if args.mode == "preflight":
        if (source_root / CLAIM_NAME).exists() or output_root.exists():
            raise ValueError("BRIDGE_ALREADY_CLAIMED_OR_OUTPUT_EXISTS")
    record = {
        "schema": SCHEMA + ".preflight",
        "status": "PASS_EXACT_RECEIPT_AND_Q4_CONDITIONAL_ADMISSION" if args.mode == "continue"
                  else "PASS_SOURCE_BYTES_ONLY_NOT_TRAINED",
        "custody": custody, "source_equivalence": equivalence,
        "pm_q4": decision, "fresh_run_id": new_run_id,
        "target_run_path": str(output_root),
        "private_pack_sha256": DATA_SHA,
        "historical_1024_checkpoint_sha256": HISTORICAL_CHECKPOINT_SHA,
        "t4_readback": old_cuda, "science_executed": False,
        "test_accessed": False,
    }
    return old, source_root, output_root, record

def continue_1024(args):
    old, source_root, target, result = preflight(args)
    custody = result["custody"]
    q4_hash = result["pm_q4"]["q4_sha256"]
    new_run_id = result["fresh_run_id"]
    claim = claim_payload(custody, result["source_equivalence"], result["pm_q4"], target)
    claim_file = source_root / CLAIM_NAME
    if claim_file.exists():
        previous = read_exact_json(claim_file)
        if previous != claim:
            raise ValueError("CONTINUATION_CLAIM_ALREADY_USED_DIFFERENT_SCOPE")
        if not target.exists():
            raise ValueError("CONTINUATION_CLAIM_PRESENT_BUT_TARGET_MISSING_HOLD")
        if args.resume_step is None and not (target / "FINAL.json").is_file():
            raise ValueError("REPEAT_ATTEMPT_REQUIRES_EXACT_RESUME_STEP")
    else:
        if args.resume_step is not None or target.exists():
            raise ValueError("NO_RESUME_OF_UNCLAIMED_SOURCE_OR_EXISTING_TARGET")
        write_once(claim_file, claim)
    # This retains *original* receipt bytes. No synthetic T4 re-execution.
    authorized = {
        "go_sha256": q4_hash,
        "capacity_sha256": custody["original_tech40_receipt_sha256"],
        "run_id": new_run_id,
    }
    trainargs = argparse.Namespace(
        arm="replica_1024", run_id=new_run_id,
        data=args.data, manifest=args.manifest,
        sources=args.sources,
        capacity=str(source_root / "TECHNICAL_SYNTHETIC_40.json"),
        go=str(args.q4), out=str(target),
        resume_step=args.resume_step,
    )
    if not (target / "FINAL.json").exists():
        old.train(trainargs, verified_integrated=authorized)
    else:
        if args.resume_step is not None:
            raise ValueError("FINAL_ALREADY_EXISTS_NO_RETRAIN")
        lock = read_exact_json(target / "RUN_LOCK.json")
        if (lock.get("arm") != "replica_1024" or lock.get("run_id") != new_run_id
                or lock.get("go_sha256") != q4_hash
                or lock.get("capacity_sha256") != custody["original_tech40_receipt_sha256"]
                or lock.get("runner_git_blob") != OLD_RUNNER_BLOB):
            raise ValueError("EXISTING_FINAL_CUSTODY_MISMATCH")
    right = old.checkpoint_dir(target, 1024) / "checkpoint.pt"
    ready = old.checked_ready(right.parent, 1024)
    if ready.get("go_sha256") != q4_hash:
        raise ValueError("CHECKPOINT_Q4_CUSTODY_MISMATCH")
    paired_file = target.parent / ("TTM_1024_PAIRED_VAL__" + new_run_id + ".json")
    if not paired_file.exists():
        compareargs = argparse.Namespace(
            sources=args.sources, data=args.data, manifest=args.manifest,
            arm="replica_1024", run_id=new_run_id, go=str(args.q4),
            left=str(args.historical_checkpoint), right=str(right),
            out=str(paired_file),
        )
        old.compare(compareargs, verified_integrated=authorized)
    else:
        paired = read_exact_json(paired_file)
        if (paired.get("checkpoints_sha256") != [HISTORICAL_CHECKPOINT_SHA, hash_file(right)]
                or paired.get("step") != 1024
                or paired.get("test_accessed") is not False):
            raise ValueError("EXISTING_PAIRED_VAL_NOT_SAME_CHECKPOINTS")
    closure_file = target.parent / ("TTM_1024_BRIDGE_CLOSURE__" + new_run_id + ".json")
    closure = {
        "schema": SCHEMA + ".closure",
        "status": "NEW1024_AND_PAIRED_HISTORICAL_VAL_COMPLETED_UNADJUDICATED",
        "original_tech40_receipt_sha256": custody["original_tech40_receipt_sha256"],
        "original_tech40_rerun": False,
        "pm_q4_sha256": q4_hash,
        "fresh_training_checkpoint_sha256": hash_file(right),
        "paired_val_sha256": hash_file(paired_file),
        "scoped_research_interpretation": "REPLICATION_VAL_ONLY_NO_NEW_MODEL_CLAIM",
        "test_accessed": False,
    }
    if closure_file.exists():
        if read_exact_json(closure_file) != closure:
            raise ValueError("EXISTING_BRIDGE_CLOSURE_CHANGED")
    else:
        write_once(closure_file, closure)
    print(json.dumps(closure, sort_keys=True, ensure_ascii=False), flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["preflight", "continue"])
    for key in ("old_runner", "new_runner", "q4", "sources",
                "data", "manifest", "historical_checkpoint", "durable_output_parent",
                "old_sessions_parent"):
        parser.add_argument("--" + key.replace("_", "-"), required=True)
    parser.add_argument("--original-session")
    parser.add_argument("--resume-step", type=int, choices=[256, 512, 768])
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        raise ValueError("PYTHON312_REQUIRED")
    if args.mode == "preflight":
        _, _, _, result = preflight(args)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    else:
        continue_1024(args)

if __name__ == "__main__":
    main()
