#!/usr/bin/env python3
"""New P02 step-1024 F32 reference for preregistered FL01..FL04 only.
No training, no TEST/Q1Q2, no GGUF or Ollama, no overwrites.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

ROOT_ID = "TokenToModel-Lab"
P02_BLOB = "9762343e06cf800b50574c2871ae1ed58537fb18"
PREREG_BLOB = "fdcb81064a6c55b3dca5f71e18defff0895c0568"
CHECKPOINT_SHA = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
CONFIG = {
    "vocab_size": 2048, "max_seq_len": 256, "n_embd": 256,
    "n_layer": 4, "n_head": 4, "norm_type": "layernorm",
}
FIXTURES = [
    ("FL01", [97, 98, 99]),
    ("FL02", [257, 304, 111]),
    ("FL03", [97, 10, 98]),
    ("FL04", [88, 267, 628, 195, 160, 111]),
]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def project_member(root: Path, path: Path, *, file: bool = True, exists: bool = True) -> Path:
    canonical = path.resolve(strict=exists)
    if canonical == root or not canonical.is_relative_to(root):
        raise ValueError("TTM_PROJECT_PATH_BOUNDARY_FAIL")
    if exists and (not canonical.is_file() if file else not canonical.is_dir()):
        raise ValueError("PROJECT_FILE_OR_DIRECTORY_TYPE_MISMATCH")
    return canonical

def frozen_inputs(root: Path, worktree: Path, checkpoint: Path, output: Path) -> tuple:
    if root.name != ROOT_ID or not (root / ".git").exists():
        raise ValueError("EXPECTED_TTM_GIT_ROOT")
    worktree = project_member(root, worktree, file=False)
    if not (worktree / ".git").exists():
        raise ValueError("EXACT_GIT_WORKTREE_REQUIRED")
    if output.exists() or output.is_symlink():
        raise FileExistsError("REFERENCE_ALREADY_EXISTS_NO_REPLAY")
    output = project_member(root, output, exists=False)
    project_member(root, output.parent, file=False)
    checkpoint = project_member(root, checkpoint)
    p02 = project_member(root, worktree / "src/p02/transformer_core.py")
    prereg = project_member(root, worktree / "artifacts/qa/ttm-ollama-full-logits/TTM_OLLAMA_FULL_LOGITS_F32_PREREG_20261111.json")
    if git_blob(p02) != P02_BLOB or git_blob(prereg) != PREREG_BLOB:
        raise ValueError("SOURCE_OR_PREREG_GIT_BLOB_MISMATCH")
    if sha256(checkpoint) != CHECKPOINT_SHA:
        raise ValueError("ORIGINAL_STEP1024_CHECKPOINT_SHA_MISMATCH")
    plan = json.loads(prereg.read_text(encoding="utf-8"))
    if (plan.get("schema") != "ttm.ollama.full_logits.independent_prereg.v1"
        or plan.get("model", {}).get("p02_checkpoint_sha256") != CHECKPOINT_SHA
        or plan.get("model", {}).get("vocab_size") != 2048
        or [(f["fixture_id"], f["token_ids"]) for f in plan["fixtures"]] != FIXTURES
        or plan.get("measurement", {}).get("logits_per_row") != 2048):
        raise ValueError("FROZEN_FOUR_FIXTURES_OR_MODEL_METADATA_CHANGED")
    return p02, checkpoint, output

def produce(root: Path, work: Path, checkpoint: Path, output: Path) -> dict:
    p02, checkpoint, output = frozen_inputs(root, work, checkpoint, output)
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.set_default_dtype(torch.float32)
    spec = importlib.util.spec_from_file_location("ttm_ollama_fl_p02_pin", p02)
    if spec is None or spec.loader is None:
        raise ValueError("P02_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    checkpoint_payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if (not isinstance(checkpoint_payload, dict)
        or checkpoint_payload.get("schema") != "ttm.t4.science.checkpoint.v1"
        or checkpoint_payload.get("step") != 1024
        or checkpoint_payload.get("p02_git_blob") != P02_BLOB
        or checkpoint_payload.get("config") != CONFIG):
        raise ValueError("CHECKPOINT_SCHEMA_STEP_OR_CONFIG_MISMATCH")
    model = module.GPT(module.P02Config(**CONFIG)).float().cpu().eval()
    model.load_state_dict(checkpoint_payload["model"], strict=True)
    if sum(p.numel() for p in model.parameters()) != 3749376:
        raise ValueError("CHECKPOINT_PARAM_COUNT_MISMATCH")
    if any(b.mlp[1].approximate != "none" for b in model.blocks):
        raise ValueError("REFERENCE_NOT_GELU_ERF")
    rows = []
    with torch.inference_mode():
        for fid, ids in FIXTURES:
            tokens = torch.tensor([ids], dtype=torch.long, device="cpu")
            logits, loss = model(tokens)
            if loss is not None or logits.dtype != torch.float32 or logits.device.type != "cpu":
                raise ValueError("NOT_CPU_F32_EVAL")
            data = logits[0, -1, :].detach().tolist()
            if len(data) != 2048 or not all(math.isfinite(v) for v in data):
                raise ValueError("BAD_REFERENCE_VECTOR")
            rows.append({
                "fixture_id": fid, "token_ids": ids,
                "source": "P02_F32_STEP1024_GELU_ERF",
                "checkpoint_sha256": CHECKPOINT_SHA,
                "p02_git_blob": P02_BLOB,
                "prereg_git_blob": PREREG_BLOB,
                "logits": data,
            })
    # One new output file; on interruption, preserve partial evidence instead of overwriting.
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        for item in rows:
            stream.write(json.dumps(item, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n")
    return {
        "status": "P02_REFERENCE_F32_4_OF_4_PRODUCED_UNADJUDICATED",
        "reference_sha256": sha256(output),
        "checkpoint_sha256": CHECKPOINT_SHA,
        "p02_git_blob": P02_BLOB,
        "prereg_git_blob": PREREG_BLOB,
        "rows": len(rows),
        "values": 8192,
        "torch_version": torch.__version__,
        "training": False, "test_access": False, "ollama_inference": False,
    }

def main() -> None:
    ap = argparse.ArgumentParser()
    for name in ("project_root", "worktree", "checkpoint", "output"):
        ap.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    args = ap.parse_args()
    root = args.project_root.resolve(strict=True)
    report = produce(root, args.worktree, args.checkpoint, args.output)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, ImportError) as e:
        print("TTM_OLLAMA_P02_REFERENCE_HOLD:" + type(e).__name__ + ":" + str(e), file=sys.stderr)
        raise SystemExit(2)
