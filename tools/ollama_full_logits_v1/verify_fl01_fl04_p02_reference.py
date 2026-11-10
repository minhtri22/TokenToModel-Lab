#!/usr/bin/env python3
"""Independent reference structure/seal QA; never loads PyTorch or the checkpoint."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

P02 = "9762343e06cf800b50574c2871ae1ed58537fb18"
PREREG = "fdcb81064a6c55b3dca5f71e18defff0895c0568"
CKPT = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
FIX = {
    "FL01": [97, 98, 99],
    "FL02": [257, 304, 111],
    "FL03": [97, 10, 98],
    "FL04": [88, 267, 628, 195, 160, 111],
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def gitblob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def checked_rows(text: str):
    if not text.endswith("\n") or text.count("\n") != 4:
        raise ValueError("REFERENCE_EXACT_4_LINES_REQUIRED")
    rows = [json.loads(x) for x in text.splitlines()]
    if [x.get("fixture_id") for x in rows] != list(FIX):
        raise ValueError("REFERENCE_ORDER_OR_DUPLICATE_IDS")
    for x in rows:
        if set(x) != {"fixture_id", "token_ids", "source", "checkpoint_sha256", "p02_git_blob", "prereg_git_blob", "logits"}:
            raise ValueError("REFERENCE_EXACT_KEYS_REQUIRED")
        fid = x["fixture_id"]
        if (x["token_ids"] != FIX[fid] or x["source"] != "P02_F32_STEP1024_GELU_ERF"
            or x["checkpoint_sha256"] != CKPT or x["p02_git_blob"] != P02
            or x["prereg_git_blob"] != PREREG):
            raise ValueError("REFERENCE_PROVENANCE_OR_FIXTURE_MISMATCH")
        vals = x["logits"]
        if not isinstance(vals, list) or len(vals) != 2048 or any(type(v) not in (int, float) or not math.isfinite(v) for v in vals):
            raise ValueError("REFERENCE_NONFINITE_OR_NOT_FULL_2048")
    return rows

def audit(root: Path, prereg_path: Path, reference: Path, seal: Path):
    if root.name != "TokenToModel-Lab":
        raise ValueError("TTM_PROJECT_ROOT_ID_MISMATCH")
    for p in (prereg_path, reference, seal):
        q = p.resolve(strict=p != seal)
        if q == root or not q.is_relative_to(root):
            raise ValueError("PATH_OUTSIDE_PROJECT_ROOT")
    if seal.exists() or seal.is_symlink():
        raise FileExistsError("REFERENCE_SEAL_ALREADY_EXISTS")
    if gitblob(prereg_path) != PREREG:
        raise ValueError("PREREG_BLOB_MISMATCH")
    p = json.loads(prereg_path.read_text("utf-8"))
    if (p["schema"] != "ttm.ollama.full_logits.independent_prereg.v1"
        or [(x["fixture_id"], x["token_ids"]) for x in p["fixtures"]] != list(FIX.items())):
        raise ValueError("PREREG_FIXTURES_CHANGED")
    rows = checked_rows(reference.read_text(encoding="utf-8"))
    result = {
        "schema": "ttm.ollama.full_logits.independent_reference_seal.v1",
        "status": "PASS_REFERENCE_4_OF_4_X_2048",
        "reference_sha256": sha(reference),
        "prereg_git_blob": PREREG,
        "checkpoint_sha256": CKPT,
        "p02_git_blob": P02,
        "rows": len(rows), "logits_evaluated": len(rows)*2048,
        "scientific_parity_verdict": "NOT_EXECUTED",
        "ollama_runtime": "NOT_EXECUTED",
        "no_model_loaded_by_auditor": True,
        "no_training": True,
    }
    with seal.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write("\n")
    return result

def main():
    ap = argparse.ArgumentParser()
    for name in ("project_root", "prereg", "reference", "seal"):
        ap.add_argument("--" + name.replace("_", "-"), type=Path, required=True)
    a = ap.parse_args()
    print(json.dumps(audit(a.project_root.resolve(strict=True), a.prereg, a.reference, a.seal), sort_keys=True))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as e:
        print("TTM_OLLAMA_REFERENCE_SEAL_HOLD:" + type(e).__name__ + ":" + str(e), file=sys.stderr)
        raise SystemExit(2)
