"""TTM matched TinyStories 3,749,376-parameter P02 GPT runner, Python 3.12.
Pure source QA is default; native Torch QA uses toy synthetic tensors only.
Real model training and paired checkpoint evaluation require explicit exact Q4.
Historical TinyStories TEST is never read; source files and packs are SHA pinned.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import unittest

BASE_MAIN = "59ee3f30b996405fddc087ab60102b59a021f8ea"
PIN = {
    "src/p02/transformer_core.py": "9762343e06cf800b50574c2871ae1ed58537fb18",
    "tools/pilot_t4/integrated/t4_capacity_smoke.py": "c9a6f256ba975228683ee7de2a1090e649110e97",
    "tools/pilot_t4/integrated/t4_eval.py": "bef006bdff173fba6d8ba4aa0ef687a1732fd7c4",
    "tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py": "76c4d0155cd0736919f41682f240b47ad3d7c428",
}
P02_CONFIG = {"vocab_size": 2048, "max_seq_len": 256, "n_embd": 256,
              "n_layer": 4, "n_head": 4, "norm_type": "layernorm"}
DATA_SHA = "184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913"
MANIFEST_SHA = "ef2e6e67d49b1d5a921b1051df329f15574f1c10cece49468acb53322d650"
BPE_SHA = "cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
SPLIT_SHA = "9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9"
HISTORIC_STEP1024_SHA = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
TOKENS_PER_STEP = 4096
CHECKPOINTS = {1024: (256, 512, 768, 1024), 2048: (256, 512, 768, 1024, 1536, 2048)}
PARAMETERS = 3749376
PLANS = {
    "replica_1024": {"steps": 1024, "seed": 20261108, "schedule": "COSINE_1024"},
    "control_2048": {"steps": 2048, "seed": 20261108, "schedule": "COSINE_2048"},
    "replica_2048": {"steps": 2048, "seed": 20261109, "schedule": "COSINE_2048"},
}
TOTAL_GPU_SECONDS_CAP = 5400
CUDA_RESERVED_CAP_RATIO = .80
SOURCE_SCHEMA = "ttm.matched_4m.tinystories.onepack.v1"

def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def source_blob():
    return git_blob(Path(__file__).read_bytes())

def require_sha(value):
    if not isinstance(value, str) or re.fullmatch("[0-9a-f]{64}", value) is None:
        raise ValueError("SHA256_REQUIRED")
    return value

def write_new(path, raw):
    path = Path(path)
    if path.is_symlink() or path.exists() or path.parent.is_symlink():
        raise FileExistsError("ONE_SHOT_NO_OVERWRITE")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())

def source_path(root, relative):
    root = Path(root).resolve(strict=True)
    p = root.joinpath(*relative.split("/"))
    if not p.is_file() or p.is_symlink() or not p.resolve(strict=True).is_relative_to(root):
        raise ValueError("SOURCE_PATH_INVALID:" + relative)
    return p

def verify_sources(root):
    identities = {}
    for relative, expected in PIN.items():
        path = source_path(root, relative)
        actual = git_blob(path.read_bytes())
        if actual != expected:
            raise ValueError("GIT_BLOB_DRIFT:" + relative + ":" + actual)
        identities[relative] = expected
    return identities

def plan_of(arm):
    if arm not in PLANS:
        raise ValueError("UNKNOWN_ARM")
    return dict(PLANS[arm])

def recipe(arm):
    p = plan_of(arm)
    return {"model": P02_CONFIG, "steps": p["steps"], "schedule": p["schedule"],
            "warmup_steps": 32, "base_lr": .0003, "min_lr_ratio": .1,
            "optimizer": "AdamW", "betas": [.9, .95], "eps": 1e-8,
            "weight_decay": .1, "max_grad_norm": 1., "precision": "fp16",
            "microbatch_windows": 8, "tokens_per_step": TOKENS_PER_STEP,
            "bpe_file_sha256": BPE_SHA, "pack_sha256": DATA_SHA,
            "split_sha256": SPLIT_SHA, "p02_blob": PIN["src/p02/transformer_core.py"]}

def recipe_hash(arm):
    return sha_bytes(canonical(recipe(arm)))

def provenance_check(arm, checkpoint_step, recipe_digest, pack_digest):
    p = plan_of(arm)
    if type(checkpoint_step) is not int or checkpoint_step not in CHECKPOINTS[p["steps"]]:
        raise ValueError("UNEXPECTED_CHECKPOINT_STEP")
    if recipe_digest != recipe_hash(arm) or pack_digest != DATA_SHA:
        raise ValueError("RECIPE_OR_PACK_MISMATCH")
    return True

def assert_owner_go(path, action, arm, run_id, capacity_sha=None, left_sha=None, right_sha=None):
    if not path:
        raise ValueError("Q4_OWNER_FILE_REQUIRED")
    obj = json.loads(Path(path).read_text("utf-8"))
    expected = {
        "schema": "ttm.matched_4m.owner_q4.v1",
        "action": action, "decision": "GO_EXACT_ONE_SHOT",
        "arm": arm, "run_id": run_id, "runner_git_blob": source_blob(),
        "source_main": BASE_MAIN, "recipe_sha256": recipe_hash(arm),
        "train_val_pack_sha256": DATA_SHA, "rights_reference": obj.get("rights_reference"),
        "resource_receipt_sha256": capacity_sha,
        "left_checkpoint_sha256": left_sha, "right_checkpoint_sha256": right_sha,
    }
    if (obj != expected or not isinstance(run_id, str)
            or re.fullmatch("[A-Za-z0-9_-]{8,80}", run_id) is None
            or not isinstance(obj.get("rights_reference"), str)
            or len(obj["rights_reference"].strip()) < 8):
        raise ValueError("EXACT_Q4_OWNER_DECISION_REQUIRED")
    return sha_file(path)

def validate_pack_files(data_path, manifest_path, check_bytes=True):
    # Never discovers/fetches data automatically; caller supplies two exact private files.
    manifest_path = Path(manifest_path)
    data_path = Path(data_path)
    for p in (manifest_path, data_path):
        if not p.is_file() or p.is_symlink():
            raise ValueError("PRIVATE_INPUT_MISSING_OR_SYMLINK")
    if (sha_file(manifest_path) != MANIFEST_SHA or sha_file(data_path) != DATA_SHA
            or data_path.stat().st_size != 1186107):
        raise ValueError("HISTORICAL_TRAIN_VAL_BYTES_NOT_IDENTICAL")
    m = json.loads(manifest_path.read_text("utf-8"))
    if (m.get("schema") != "ttm.t4.private.train_val.windowpack.v1"
            or m.get("contains_test") is not False
            or m.get("contains_raw_text") is not False
            or m.get("npz_sha256") != DATA_SHA
            or m.get("t1_bpe_file_sha256") != BPE_SHA
            or m.get("t1_split_sha256") != SPLIT_SHA
            or m.get("context") != 256
            or m.get("counts", {}).get("train_stories") != 2048
            or m.get("counts", {}).get("val_stories") != 256
            or m.get("counts", {}).get("test_stories_tokenized") != 0
            or m.get("counts", {}).get("train_next_token_targets_unique") != 498287
            or m.get("counts", {}).get("val_next_token_targets") != 61122):
        raise ValueError("T4_DATA_MANIFEST_CONTRACT_MISMATCH")
    return m

def runtime_sources(root):
    verify_sources(root)
    import importlib.util
    import torch
    import numpy as np
    core = source_path(root, "src/p02/transformer_core.py")
    old_path = source_path(root, "tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py")
    cap_path = source_path(root, "tools/pilot_t4/integrated/t4_capacity_smoke.py")
    eval_path = source_path(root, "tools/pilot_t4/integrated/t4_eval.py")
    dirs = [str(cap_path.parent), str(old_path.parent)]
    for item in dirs:
        if item not in sys.path:
            sys.path.insert(0, item)
    # Import exact original source after hash verification.
    import t4_capacity_smoke as cap
    import t4_train_science_a2 as legacy
    import t4_eval as score
    p02 = cap.p02_module(core)
    if cap.CONFIG != P02_CONFIG or cap.TOKENS_PER_STEP != TOKENS_PER_STEP:
        raise ValueError("ORIGINAL_T4_CORE_CONFIG_DRIFT")
    return torch, np, p02, legacy, score, cap

def cuda_guard(torch):
    if sys.version_info[:2] != (3, 12):
        raise ValueError("PYTHON312_REQUIRED")
    if not torch.cuda.is_available() or "T4" not in torch.cuda.get_device_name(0):
        raise ValueError("COLAB_T4_REQUIRED")
    free, total = torch.cuda.mem_get_info()
    if free < 10 * (1024 ** 3):
        raise MemoryError("GPU_FREE_BELOW_10_GIB")
    return {"gpu": torch.cuda.get_device_name(0), "torch": str(torch.__version__),
            "cuda": str(torch.version.cuda), "free_mib": int(free / (1024 ** 2)),
            "total_mib": int(total / (1024 ** 2)),
            "python": sys.version.split()[0]}

def capacity(args):
    torch, _, p02, _, _, cap = runtime_sources(args.sources)
    env = cuda_guard(torch)
    if Path(args.out).exists():
        raise FileExistsError("RESOURCE_REPORT_ALREADY_EXISTS")
    t0 = time.monotonic()
    trial = cap.single_trial(p02, microbatch=8, precision="fp16", warmup=2, timed=3)
    worst = float(trial["worst_seconds"])
    projected = 2 * 2048 * worst / .75  # two prospective 2048-step arms
    reserved = int(trial["peak_cuda_reserved_bytes"])
    ratio = reserved / torch.cuda.get_device_properties(0).total_memory
    status = "PASS_SYNTHETIC_RESOURCE_ONLY" if (projected <= TOTAL_GPU_SECONDS_CAP
        and ratio <= CUDA_RESERVED_CAP_RATIO and time.monotonic() - t0 < 150) else "HOLD_RESOURCE_CAP"
    result = {"schema": "ttm.matched_4m.capacity.v1", "status": status,
        "science_executed": False, "test_accessed": False, "synthetic_only": True,
        "runner_git_blob": source_blob(), "source_main": BASE_MAIN,
        "recipe_2048_sha256": recipe_hash("control_2048"), "env": env,
        "trial": trial, "two_arm_projection_seconds_with_25pct_reserve": projected,
        "reserved_ratio": ratio, "gpu_seconds_cap_both_arms": TOTAL_GPU_SECONDS_CAP,
        "measurement_limit": "FIXED_RANDOM_WINDOWS_NOT_REAL_STORY_LENGTHS_OR_CHECKPOINT_IO",
        "owner_q4": "HOLD"}
    write_new(args.out, canonical(result))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if status != "PASS_SYNTHETIC_RESOURCE_ONLY":
        raise SystemExit(3)

def require_capacity(path, arm):
    if not path or not Path(path).is_file():
        raise ValueError("CAPACITY_RECEIPT_REQUIRED")
    cap = json.loads(Path(path).read_text("utf-8"))
    if (cap.get("schema") != "ttm.matched_4m.capacity.v1"
            or cap.get("status") != "PASS_SYNTHETIC_RESOURCE_ONLY"
            or cap.get("runner_git_blob") != source_blob()
            or cap.get("recipe_2048_sha256") != recipe_hash("control_2048")
            or cap.get("reserved_ratio", 1.) > CUDA_RESERVED_CAP_RATIO
            or cap.get("two_arm_projection_seconds_with_25pct_reserve", 999999) > TOTAL_GPU_SECONDS_CAP):
        raise ValueError("PROSPECTIVE_RESOURCE_PROOF_NOT_ACCEPTED")
    return sha_file(path)

def prepare_model(arm, p02, legacy, device):
    p = plan_of(arm)
    legacy.TOTAL_STEPS = p["steps"]
    legacy.SEED = p["seed"]
    model, opt, sch, sampler, scaler = legacy.model_context(p02, device, "fp16")
    if sum(p.numel() for p in model.parameters()) != PARAMETERS:
        raise ValueError("PARAMETER_COUNT_DRIFT")
    return model, opt, sch, sampler, scaler

def checkpoint_dir(root, step):
    return Path(root) / "checkpoints" / ("step_%04d" % step)

def durable_checkpoint(root, step, model, opt, sch, sampler, scaler,
                       legacy, torch, go_sha, progress):
    directory = checkpoint_dir(root, step)
    if directory.is_symlink() or directory.exists():
        raise FileExistsError("CHECKPOINT_NO_OVERWRITE")
    directory.mkdir(parents=True)
    elapsed = float(progress[-1]["cumulative_seconds"])
    payload = legacy.checkpoint_payload(model, opt, sch, sampler, scaler, step,
                                        go_sha, DATA_SHA, elapsed,
                                        next(model.parameters()).device)
    payload["runner_git_blob"] = source_blob()
    payload["arm"] = Path(root).name.split("__")[0]
    # Prefix log and SHA are immutable within this checkpoint directory.
    tmp = directory / "checkpoint.partial"
    torch.save(payload, tmp)
    file_hash = sha_file(tmp)
    dst = directory / "checkpoint.pt"
    os.replace(tmp, dst)
    write_new(directory / "progress.json", canonical({
        "schema": "ttm.matched_4m.progress.v1", "records": progress, "step": step}))
    ready = {"schema": "ttm.matched_4m.ready_last.v1", "step": step,
        "checkpoint": "checkpoint.pt", "sha256": file_hash,
        "bytes": dst.stat().st_size, "progress_sha256": sha_file(directory / "progress.json"),
        "go_sha256": go_sha, "pack_sha256": DATA_SHA,
        "runner_git_blob": source_blob(),
        "recipe_sha256": recipe_hash(payload["arm"])}
    write_new(directory / "READY.json", canonical(ready))
    if sha_file(dst) != file_hash:
        raise ValueError("CHECKPOINT_POSTWRITE_SHA_READBACK_MISMATCH")
    return ready

def checked_ready(path, step=None):
    folder = Path(path).resolve(strict=True)
    ready_path = folder / "READY.json"
    if not ready_path.is_file() or ready_path.is_symlink():
        raise ValueError("READY_LAST_MISSING")
    ready = json.loads(ready_path.read_text("utf-8"))
    if (ready.get("schema") != "ttm.matched_4m.ready_last.v1"
            or ready.get("checkpoint") != "checkpoint.pt"
            or ready.get("runner_git_blob") != source_blob()
            or ready.get("pack_sha256") != DATA_SHA
            or (step is not None and ready.get("step") != step)):
        raise ValueError("READY_SCHEMA_OR_STEP_INVALID")
    cp = folder / "checkpoint.pt"
    progress = folder / "progress.json"
    if (not cp.is_file() or cp.is_symlink() or not progress.is_file()
            or sha_file(cp) != ready["sha256"] or cp.stat().st_size != ready["bytes"]
            or sha_file(progress) != ready["progress_sha256"]):
        raise ValueError("READY_CHECKPOINT_OR_PROGRESS_SHA_MISMATCH")
    return ready

def resume_state(folder, model, opt, sch, sampler, scaler, legacy, torch, go_sha, arm):
    ready = checked_ready(folder)
    if ready["go_sha256"] != go_sha or ready["recipe_sha256"] != recipe_hash(arm):
        raise ValueError("RESUME_ORIGINAL_RUN_LOCK_MISMATCH")
    step, elapsed = legacy.checkpoint_load(Path(folder), model, opt, sch, sampler, scaler,
                                           next(model.parameters()).device, go_sha, DATA_SHA)
    if step != ready["step"] or step >= plan_of(arm)["steps"]:
        raise ValueError("RESUME_STEP_INVALID_OR_ALREADY_FINAL")
    progress = json.loads((Path(folder) / "progress.json").read_text("utf-8"))
    records = progress["records"]
    if (len(records) != step or records[-1]["step"] != step
            or sum(int(v["valid_targets"]) for v in records) != step * TOKENS_PER_STEP):
        raise ValueError("RESUME_PROGRESS_PREFIX_INVALID")
    return step, elapsed, records

def train(args):
    if args.arm not in PLANS or not args.run_id or not args.capacity or not args.go:
        raise ValueError("RUN_REQUIRES_ARM_CAPACITY_AND_EXACT_GO")
    cap_sha = require_capacity(args.capacity, args.arm)
    go_sha = assert_owner_go(args.go, "TRAIN_OR_RESUME", args.arm, args.run_id, cap_sha)
    validate_pack_files(args.data, args.manifest)
    torch, _, p02, legacy, score, _ = runtime_sources(args.sources)
    env = cuda_guard(torch)
    data, _ = score.load_private_pack(args.data, args.manifest)
    root = Path(args.out).absolute()
    if root.name != args.arm + "__" + args.run_id or root.is_symlink():
        raise ValueError("RUN_ROOT_MUST_BE_ARM_AND_RUN_ID")
    if args.resume_step is None:
        if root.exists() or root.parent.is_symlink():
            raise FileExistsError("ONE_SHOT_RUN_ALREADY_EXISTS")
        root.mkdir(parents=True)
        write_new(root / "RUN_LOCK.json", canonical({
            "schema": SOURCE_SCHEMA, "arm": args.arm, "run_id": args.run_id,
            "runner_git_blob": source_blob(), "go_sha256": go_sha,
            "capacity_sha256": cap_sha, "pack_sha256": DATA_SHA,
            "recipe_sha256": recipe_hash(args.arm), "started_from_random": True,
            "historic_checkpoint_used_as_initialization": False}))
    else:
        if not root.is_dir() or root.is_symlink():
            raise ValueError("RESUME_REQUIRES_OWNED_ORIGINAL_RUN")
        lock = json.loads((root / "RUN_LOCK.json").read_text("utf-8"))
        if (lock.get("arm") != args.arm or lock.get("run_id") != args.run_id
                or lock.get("go_sha256") != go_sha
                or lock.get("runner_git_blob") != source_blob()
                or lock.get("capacity_sha256") != cap_sha
                or lock.get("pack_sha256") != DATA_SHA
                or lock.get("recipe_sha256") != recipe_hash(args.arm)
                or (root / "FINAL.json").exists()):
            raise ValueError("RESUME_RUN_LOCK_OR_FINAL_CONFLICT")
    torch.set_num_threads(2)
    model, opt, sch, sampler, scaler = prepare_model(args.arm, p02, legacy, torch.device("cuda"))
    if args.resume_step is None:
        start, spent, progress = 0, 0., []
    else:
        if args.resume_step not in CHECKPOINTS[plan_of(args.arm)["steps"]]:
            raise ValueError("RESUME_CHECKPOINT_NOT_FROZEN")
        start, spent, progress = resume_state(checkpoint_dir(root, args.resume_step),
                                             model, opt, sch, sampler, scaler,
                                             legacy, torch, go_sha, args.arm)
        # Prevent implicitly overriding or jumping over existing READY.
        for future in CHECKPOINTS[plan_of(args.arm)["steps"]]:
            if future > start and checkpoint_dir(root, future).exists():
                raise ValueError("LATER_CHECKPOINT_EXISTS_REFUSE_FORK")
    torch.cuda.reset_peak_memory_stats()
    wall_start = time.monotonic()
    spent_at_resume = spent
    for step in range(start + 1, plan_of(args.arm)["steps"] + 1):
        if spent_at_resume + (time.monotonic() - wall_start) > TOTAL_GPU_SECONDS_CAP:
            raise TimeoutError("ARM_GPU_WALL_CAP_NO_AUTO_RETRY")
        torch.cuda.synchronize()
        before = time.perf_counter()
        loss, drawn = legacy.train_one_step(model, opt, sch, sampler, scaler,
                                            data, torch.device("cuda"), "fp16", 8)
        torch.cuda.synchronize()
        duration = time.perf_counter() - before
        spent += duration
        if not math.isfinite(loss):
            raise ValueError("NONFINITE_TRAIN_LOSS")
        if torch.cuda.max_memory_reserved() / torch.cuda.get_device_properties(0).total_memory > CUDA_RESERVED_CAP_RATIO:
            raise MemoryError("VRAM_RESERVED_CAP_AFTER_STEP")
        progress.append({"step": step, "train_loss": loss, "windows_drawn": drawn,
                         "valid_targets": TOKENS_PER_STEP,
                         "cumulative_seconds": spent})
        if step in CHECKPOINTS[plan_of(args.arm)["steps"]]:
            durable_checkpoint(root, step, model, opt, sch, sampler, scaler,
                               legacy, torch, go_sha, progress)
            print("READY_STEP=" + str(step), flush=True)
    # Final VAL same pinned 256 stories; historical VAL is development, not new TEST.
    sums = score.model_story_scores(model, data, torch.device("cuda"))
    counts = data["val_count"]
    aggregate = float(sums.sum() / counts.sum())
    result = {"schema": "ttm.matched_4m.train_result.v1",
              "status": "FINISHED_REQUIRES_DISTINCT_QA",
              "arm": args.arm, "last_step": plan_of(args.arm)["steps"],
              "val_nll_per_bpe_target": aggregate,
              "val_targets": int(counts.sum()), "checkpoint_ready_sha256":
              sha_file(checkpoint_dir(root, plan_of(args.arm)["steps"]) / "READY.json"),
              "total_target_exposures": plan_of(args.arm)["steps"] * TOKENS_PER_STEP,
              "running_seconds_compute_only": spent, "env": env,
              "peak_reserved_mib": torch.cuda.max_memory_reserved() // (1024 ** 2),
              "test_accessed": False, "science_conclusion": "UNADJUDICATED",
              "run_lock_sha256": sha_file(root / "RUN_LOCK.json")}
    write_new(root / "FINAL.json", canonical(result))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))

def paired_bootstrap(left, right, counts, seed=20261117, reps=2000):
    # Independent arithmetic contract: paired story bootstrap, no per-story raw output.
    import numpy as np
    a, b, n = (np.asarray(z, dtype=np.float64) for z in (left, right, counts))
    if (a.ndim != 1 or b.shape != a.shape or n.shape != a.shape
            or len(a) != 256 or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b))
            or np.any(a < 0) or np.any(b < 0) or np.any(n <= 0)):
        raise ValueError("PAIRED_STORY_INPUT_INVALID")
    avg_l, avg_r = float(a.sum() / n.sum()), float(b.sum() / n.sum())
    rng = np.random.default_rng(seed)
    boot = []
    for _ in range(reps):
        ix = rng.integers(0, len(n), size=len(n))
        boot.append(float((a[ix].sum() - b[ix].sum()) / n[ix].sum()))
    lo, hi = (float(x) for x in np.quantile(boot, [.025, .975]))
    return {"stories": 256, "target_count": int(n.sum()), "left_nll": avg_l,
            "right_nll": avg_r, "left_minus_right_nll": avg_l - avg_r,
            "paired_95pct_ci": [lo, hi], "bootstrap_reps": reps, "seed": seed,
            "scope": "HISTORICAL_VAL_DEVELOPMENT_ONLY_NO_NEW_TEST"}

def compare(args):
    if not args.go or not args.left or not args.right or not args.arm:
        raise ValueError("COMPARE_REQUIRES_EXPLICIT_INPUTS")
    validate_pack_files(args.data, args.manifest)
    l = Path(args.left).resolve(strict=True)
    r = Path(args.right).resolve(strict=True)
    lh, rh = sha_file(l), sha_file(r)
    if l.name != "checkpoint.pt" or r.name != "checkpoint.pt" or l == r or l.is_symlink() or r.is_symlink():
        raise ValueError("TWO_DISTINCT_CHECKPOINT_FILES_REQUIRED")
    assert_owner_go(args.go, "COMPARE", args.arm, args.run_id, left_sha=lh, right_sha=rh)
    torch, _, p02, _, score, _ = runtime_sources(args.sources)
    data, _ = score.load_private_pack(args.data, args.manifest)
    vals = []
    steps = []
    kind = []
    for path, sha in ((l, lh), (r, rh)):
        # Historical source is allowed ONLY in 1024 comparison at exact hash.
        historical = (sha == HISTORIC_STEP1024_SHA)
        if historical and args.arm != "replica_1024":
            raise ValueError("HISTORICAL_1024_CANNOT_COMPARE_TO_2048")
        if not historical:
            rd = checked_ready(path.parent)
            if rd["sha256"] != sha or rd["recipe_sha256"] != recipe_hash(args.arm):
                raise ValueError("PROSPECTIVE_CHECKPOINT_RECIPE_DRIFT")
        ckpt = torch.load(path, map_location="cpu", weights_only=True)
        if (ckpt.get("schema") != "ttm.t4.science.checkpoint.v1"
                or ckpt.get("config") != P02_CONFIG
                or ckpt.get("p02_git_blob") != PIN["src/p02/transformer_core.py"]
                or ckpt.get("train_pack_sha256") != DATA_SHA):
            raise ValueError("CHECKPOINT_MODEL_OR_DATA_MISMATCH")
        step = ckpt["step"]
        if step != plan_of(args.arm)["steps"]:
            raise ValueError("PAIR_STEP_MISMATCH")
        model = p02.GPT(p02.P02Config(**P02_CONFIG))
        model.load_state_dict(ckpt["model"], strict=True)
        model.eval()
        vals.append(score.model_story_scores(model, data, torch.device("cpu")))
        steps.append(step)
        kind.append("HISTORICAL_T4_1024" if historical else "PROSPECTIVE_MATCHED")
    outcome = paired_bootstrap(vals[0], vals[1], [
        int(data["val_count"][data["val_story_index"] == idx].sum()) for idx in range(256)])
    outcome.update({"schema": "ttm.matched_4m.paired_val_comparison.v1",
                    "status": "COMPARISON_REQUIRES_DISTINCT_QA",
                    "arm": args.arm, "step": steps[0], "checkpoints_sha256": [lh, rh],
                    "checkpoint_types": kind, "same_bpe": True, "same_train_val_pack": True,
                    "full_vocab": 2048, "test_accessed": False})
    write_new(args.out, canonical(outcome))
    print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))

def native_resume_qa(args):
    """CPU toy parity tests actual T4 checkpoint save/load; no TinyStories, model or GPU."""
    torch, np, _, legacy, _, _ = runtime_sources(args.sources)
    import random
    torch.set_num_threads(1)
    def make_state(seed):
        torch.manual_seed(seed); random.seed(seed); np.random.seed(seed)
        m = torch.nn.Linear(4, 4)
        opt = torch.optim.AdamW(m.parameters(), lr=.001)
        sch = torch.optim.lr_scheduler.LambdaLR(opt, lambda _: 1.)
        sampler = torch.Generator(device="cpu").manual_seed(seed + 71)
        return m, opt, sch, sampler
    def do_step(state):
        m, opt, sch, gen = state
        opt.zero_grad(set_to_none=True)
        ix = torch.randint(0, 4, (4,), generator=gen)
        x = torch.randn(4, 4)
        y = m(x)[torch.arange(4), ix].square().mean()
        y.backward(); opt.step(); sch.step()
        return float(y.detach())
    orig = make_state(71)
    orig_losses = [do_step(orig) for _ in range(4)]
    first = make_state(71)
    first_losses = [do_step(first) for _ in range(2)]
    with tempfile.TemporaryDirectory(prefix="ttm-matched-native-qa-") as d:
        go_sha = sha_bytes(b"synthetic-native-test-lock")
        root = Path(d) / "replica_1024__toy_native"
        root.mkdir()
        progress = [{"step": i, "valid_targets": TOKENS_PER_STEP,
                     "cumulative_seconds": float(i)} for i in (1, 2)]
        durable_checkpoint(root, 2, first[0], first[1], first[2], first[3],
                           None, legacy, torch, go_sha, progress)
        folder = checkpoint_dir(root, 2)
        ready = checked_ready(folder, 2)
        restored = make_state(7)
        step, _, loaded_progress = resume_state(folder, *restored, None, legacy,
                                                torch, go_sha, "replica_1024")
        if step != 2 or loaded_progress != progress or ready["step"] != 2:
            raise ValueError("RESUME_STEP_OR_PROGRESS_NOT_2")
        resumed_losses = first_losses + [do_step(restored) for _ in range(2)]
        delta = max(float((a - b).abs().max()) for a, b in
                    zip(orig[0].parameters(), restored[0].parameters()))
        if delta > 1e-8 or any(abs(a - b) > 1e-8 for a, b in zip(orig_losses, resumed_losses)):
            raise ValueError("SYNTHETIC_CPU_RESUME_PARITY_FAIL")
        # Mutating checkpoint bytes must fail before torch.load.
        with (folder / "checkpoint.pt").open("ab") as handle:
            handle.write(b"tamper")
        with unittest.TestCase().assertRaisesRegex(ValueError, "READY_CHECKPOINT_OR_PROGRESS_SHA"):
            checked_ready(folder, 2)
    out = {"schema": "ttm.matched_4m.synthetic_native_resume_qa.v1",
           "status": "PASS_CPU_TOY_STATE_AND_RNG_RESUME_PARITY_SCOPED",
           "steps_compared": 4, "split_at": 2, "max_abs_parameter_diff": delta,
           "checkpoint_tamper_rejected": True, "data": "SYNTHETIC_ONLY",
           "python": sys.version.split()[0], "torch": str(torch.__version__),
           "real_4m_fp16_resume": "NOT_EXECUTED",
           "science_executed": False, "owner_q4": "HOLD"}
    if args.out:
        write_new(args.out, canonical(out))
    print(json.dumps(out, sort_keys=True))

class SourceQA(unittest.TestCase):
    def test_plans(self):
        self.assertEqual([p["steps"] for p in PLANS.values()], [1024, 2048, 2048])
        self.assertEqual(PARAMETERS, 3749376)
    def test_config(self):
        self.assertEqual(P02_CONFIG["vocab_size"], 2048)
        self.assertEqual(P02_CONFIG["max_seq_len"], 256)
        self.assertEqual(P02_CONFIG["n_layer"], 4)
    def test_target_budget(self):
        self.assertEqual(TOKENS_PER_STEP * 1024, 4194304)
        self.assertEqual(TOKENS_PER_STEP * 2048, 8388608)
    def test_match2048_recipe_excluding_seed(self):
        self.assertEqual(recipe_hash("control_2048"), recipe_hash("replica_2048"))
        self.assertNotEqual(recipe_hash("replica_1024"), recipe_hash("replica_2048"))
    def test_historical_pin(self):
        self.assertEqual(len(HISTORIC_STEP1024_SHA), 64)
        self.assertEqual(PIN["src/p02/transformer_core.py"], "9762343e06cf800b50574c2871ae1ed58537fb18")
    def test_wrong_q4_rejected(self):
        with self.assertRaisesRegex(ValueError, "Q4_OWNER_FILE_REQUIRED"):
            assert_owner_go(None, "TRAIN_OR_RESUME", "replica_1024", "xxxxxxxx")
    def test_wrong_checkpoint_step(self):
        with self.assertRaisesRegex(ValueError, "UNEXPECTED_CHECKPOINT_STEP"):
            provenance_check("replica_1024", 2048, recipe_hash("replica_1024"), DATA_SHA)
    def test_checkpoint_recipe_drift(self):
        with self.assertRaisesRegex(ValueError, "RECIPE_OR_PACK"):
            provenance_check("replica_1024", 1024, recipe_hash("replica_2048"), DATA_SHA)
    def test_unsafe_sha(self):
        with self.assertRaises(ValueError):
            require_sha("x" * 64)
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as t:
            path = Path(t) / "x"
            write_new(path, b"fixture")
            with self.assertRaises(FileExistsError):
                write_new(path, b"overwrite")
    def test_byte_git_hash(self):
        self.assertEqual(git_blob(b"abc"), "f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")
    def test_rights_pack_requires_exact(self):
        with self.assertRaises(ValueError):
            validate_pack_files("nonexistent.npz", "none.json")
    def test_no_fake_1024_control2048(self):
        self.assertNotEqual(plan_of("replica_1024")["schedule"], plan_of("control_2048")["schedule"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["qa", "native-qa", "capacity", "preflight", "train", "compare"])
    ap.add_argument("--sources")
    ap.add_argument("--data")
    ap.add_argument("--manifest")
    ap.add_argument("--capacity")
    ap.add_argument("--arm")
    ap.add_argument("--run-id")
    ap.add_argument("--go")
    ap.add_argument("--out")
    ap.add_argument("--resume-step", type=int)
    ap.add_argument("--left")
    ap.add_argument("--right")
    args = ap.parse_args()
    if args.mode == "qa":
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(SourceQA))
        if not result.wasSuccessful():
            raise SystemExit(1)
        print("PASS_SOURCE_ONLY_13_OF_13")
        return
    if not args.sources:
        raise ValueError("EXACT_PINNED_SOURCES_REQUIRED")
    if args.mode == "native-qa":
        native_resume_qa(args)
    elif args.mode == "capacity":
        if not args.out:
            raise ValueError("CAPACITY_OUT_REQUIRED")
        capacity(args)
    elif args.mode == "preflight":
        verify_sources(args.sources)
        m = validate_pack_files(args.data, args.manifest)
        print(json.dumps({"status": "PASS_MATCHED_HISTORICAL_PACK_BYTES_SCOPED",
                          "manifest_sha256": MANIFEST_SHA,
                          "pack_sha256": DATA_SHA, "train": m["counts"]["train_stories"],
                          "val": m["counts"]["val_stories"], "test_accessed": False,
                          "q4": "HOLD"}, sort_keys=True))
    elif args.mode == "train":
        if not args.out or not args.data or not args.manifest:
            raise ValueError("TRAIN_ARGUMENTS_REQUIRED")
        train(args)
    elif args.mode == "compare":
        if not args.out or not args.data or not args.manifest:
            raise ValueError("COMPARE_ARGUMENTS_REQUIRED")
        compare(args)

if __name__ == "__main__":
    main()
