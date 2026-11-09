#!/usr/bin/env python3
"""NEW frozen SYN01..SYN08 PyTorch F32 logits, CPU-only, no training/TEST.

Inputs must be inside TTM project root; worktree and checkpoint need not be
in the same directory. No overwrite, no model mutation, no old fixtures.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

P02_BLOB = "9762343e06cf800b50574c2871ae1ed58537fb18"
PREREG_BLOB = "3b12cc1883ab20e2d9e3a92e6907586c1b4cad36"
CHECKPOINT_SHA = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
PREREG_SCHEMA = "ttm.t5.f32_kv_flash_single_synthetic_discrimination.prereg.v1"
EXPECTED_CONFIG = {
    "vocab_size": 2048, "max_seq_len": 256, "n_embd": 256,
    "n_layer": 4, "n_head": 4, "norm_type": "layernorm",
}
LENGTHS = [1, 2, 4, 6, 9, 12, 20, 31]

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()

def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def inside(root: Path, path: Path, *, must_exist: bool = True) -> Path:
    candidate = path.resolve(strict=must_exist)
    if not candidate.is_relative_to(root):
        raise ValueError("PATH_OUTSIDE_TTM_PROJECT")
    return candidate

def validate_prereg(plan: dict) -> list[dict]:
    if plan.get("schema") != PREREG_SCHEMA:
        raise ValueError("PREREG_SCHEMA_MISMATCH")
    pins = plan["original_pins"]
    if pins.get("checkpoint_sha256") != CHECKPOINT_SHA or pins.get("p02_git_blob_sha1") != P02_BLOB:
        raise ValueError("PREREG_MODEL_PINS_CHANGED")
    if pins.get("final_logits_acceptance_max_abs") != 0.001:
        raise ValueError("FROZEN_THRESHOLD_CHANGED")
    control = plan["control_design"]
    if control.get("expected_runs") != 32 or len(control.get("arms", [])) != 4:
        raise ValueError("FROZEN_DESIGN_CHANGED")
    rows = control["new_fixtures"]
    if len(rows) != 8:
        raise ValueError("FROZEN_FIXTURE_COUNT_CHANGED")
    for i, item in enumerate(rows):
        ids = item["ids"]
        if item["fixture_id"] != f"SYN{i + 1:02d}" or len(ids) != LENGTHS[i]:
            raise ValueError("FROZEN_FIXTURE_ID_OR_LENGTH_CHANGED")
        if any(not isinstance(v, int) or isinstance(v, bool) or v < 257 or v >= 2048 for v in ids):
            raise ValueError("INVALID_SYNTHETIC_IDS")
        if len(ids) > EXPECTED_CONFIG["max_seq_len"]:
            raise ValueError("TOO_MANY_TOKENS")
    return rows

def produce(project_root: Path, worktree_root: Path, checkpoint_path: Path, output_path: Path):
    root = project_root.resolve(strict=True)
    if not (root / ".git").exists():
        raise ValueError("NOT_PROJECT_GIT_ROOT")
    work = inside(root, worktree_root)
    if not (work / ".git").exists():
        raise ValueError("NOT_PINNED_GIT_WORKTREE")
    checkpoint = inside(root, checkpoint_path)
    output_parent = inside(root, output_path.parent)
    output = output_parent / output_path.name
    if output.exists() or output.is_symlink():
        raise FileExistsError("REFERENCE_ALREADY_EXISTS")
    p02 = inside(root, work / "src/p02/transformer_core.py")
    prereg_path = inside(root, work / "artifacts/qa/ttm-t5-parity/TTM_T5_KV_FLASH_2X2_FRESH_SYNTHETIC_PREREG_20261109.json")
    if git_blob(p02) != P02_BLOB or git_blob(prereg_path) != PREREG_BLOB:
        raise ValueError("FROZEN_GIT_BLOB_MISMATCH")
    if sha256(checkpoint) != CHECKPOINT_SHA:
        raise ValueError("CHECKPOINT_SHA_MISMATCH")
    plan = json.loads(prereg_path.read_text("utf-8"))
    fixtures = validate_prereg(plan)

    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    spec = importlib.util.spec_from_file_location("ttm_p02_step1024_frozen", p02)
    if spec is None or spec.loader is None:
        raise ValueError("P02_MODULE_NOT_LOADABLE")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    cfg = mod.P02Config(**EXPECTED_CONFIG)
    model = mod.GPT(cfg).float().eval()
    payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if not isinstance(payload, dict) or payload.get("schema") != "ttm.t4.science.checkpoint.v1":
        raise ValueError("CHECKPOINT_SCHEMA_MISMATCH")
    if payload.get("step") != 1024 or payload.get("p02_git_blob") != P02_BLOB:
        raise ValueError("CHECKPOINT_STEP_OR_SOURCE_MISMATCH")
    recorded_cfg = payload.get("config")
    if not isinstance(recorded_cfg, dict) or any(recorded_cfg.get(k) != v for k, v in EXPECTED_CONFIG.items()):
        raise ValueError("CHECKPOINT_CONFIG_MISMATCH")
    model.load_state_dict(payload["model"], strict=True)
    if sum(p.numel() for p in model.parameters()) != 3749376:
        raise ValueError("CHECKPOINT_MODEL_SIZE_MISMATCH")

    results = []
    with torch.inference_mode():
        for item in fixtures:
            ids = item["ids"]
            logits, _ = model(torch.tensor([ids], dtype=torch.long))
            scores = logits[0, -1, :].float().tolist()
            if len(scores) != 2048 or not all(math.isfinite(x) for x in scores):
                raise ValueError("REFERENCE_NONFINITE_OR_WRONG_DIM")
            results.append({
                "fixture_id": item["fixture_id"],
                "token_ids": ids,
                "logits": scores,
                "checkpoint_sha256": CHECKPOINT_SHA,
                "p02_git_blob": P02_BLOB,
                "prereg_git_blob": PREREG_BLOB,
            })
    if len(results) != 8:
        raise ValueError("REFERENCE_NOT_8_ROWS")
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        for row in results:
            handle.write(json.dumps(row, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n")
    return {
        "schema": "ttm.t5.kvflash.fresh8.reference_receipt.v1",
        "status": "REFERENCE_8_NEW_FIXTURES_COMPLETED",
        "reference_sha256": sha256(output),
        "output": str(output),
        "source_p02_git_blob": P02_BLOB,
        "prereg_git_blob": PREREG_BLOB,
        "checkpoint_sha256": CHECKPOINT_SHA,
        "torch_version": torch.__version__,
        "rows": 8, "logit_dim": 2048,
        "new_training": False, "test_read": False, "native_2x2_ran": False,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True, type=Path)
    ap.add_argument("--worktree-root", required=True, type=Path)
    ap.add_argument("--checkpoint", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    print(json.dumps(produce(args.project_root, args.worktree_root, args.checkpoint, args.output),
                     ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError, TypeError, ImportError) as err:
        print("TTM_T5_REFERENCE_FAIL_CLOSED:" + str(err), file=sys.stderr)
        raise SystemExit(2)
