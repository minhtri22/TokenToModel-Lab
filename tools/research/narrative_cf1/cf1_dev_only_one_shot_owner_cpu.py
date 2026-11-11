#!/usr/bin/env python3
"""Owner-local one-shot CPU DEV-only runner. No FINAL, GPU or training.

Run with Python 3.12:
 python cf1_dev_only_one_shot_owner_cpu.py --repo-root D:\\WORK\\RESEARCH\\TokenToModel-Lab --checkpoint <exact-local-step1024-checkpoint.pt>
Git blob sources are staged inside project _tmp without checkout or merge.
This helper has not been executed on the owner's Windows machine as of 2026-11-11.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

SOURCES = {
    "transformer_core.py": "9762343e06cf800b50574c2871ae1ed58537fb18",
    "cf1_teacher_forced_scorer.py": "d7214a4514ecb52e98c0abccd3cecb7180c705e8",
    "cf1_exact_t1_bpe.py": "98be7c264c6fcacf2c5177153ece1aac611e1f51",
    "cf1_dev_once_readonly.py": "c5f319a038a67885f191641b949f60f46d215d1d",
    "CF1_DEV_MODEL_INPUT_ONLY.json": "4fac79c16bc337926060fa21a6e22944d74259b7",
    "CF1_DEV_PUBLIC_ORACLE.json": "3f5a38069c918fd27c033ab48fce6fac9b8c5e4b",
}
EXPECTED_SHA256 = {
    "checkpoint": "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b",
    "manifest": "cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc",
    "dev": "81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed",
    "oracle": "3a425188077f24041a02fe9675e5a503221fe5cc0247ebd53a8cc266329c046d",
}
RUN_REL = Path("_tmp") / "TTM_CF1_STEP1024_DEV36_ONE_SHOT_20261111"
MANIFEST_REL = Path("_tmp") / "ttm_t1_real_source_v1" / "T1_BPE2048_REAL_TRAIN_MANIFEST.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()


def git_read(repo: Path, blob_id: str) -> bytes:
    p = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "blob", blob_id],
        check=True, capture_output=True
    )
    raw = p.stdout
    if git_blob_id(raw) != blob_id:
        raise RuntimeError("GIT_BLOB_INTEGRITY_FAIL")
    return raw


def check_within(path: Path, root: Path) -> Path:
    result = path.resolve(strict=True)
    if not result.is_relative_to(root.resolve()):
        raise RuntimeError("PROJECT_BOUNDARY_VIOLATION")
    return result


def write_new_json(path: Path, obj: dict) -> None:
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=True, indent=2)
        f.write("\\n")
        f.flush()
        os.fsync(f.fileno())


def main() -> None:
    p = argparse.ArgumentParser(description="One-shot frozen O0 DEV36 CPU; strict pinned source and no GPU")
    p.add_argument("--repo-root", required=True)
    p.add_argument("--checkpoint", required=True)
    a = p.parse_args()
    root = Path(a.repo_root).resolve(strict=True)
    if root.name != "TokenToModel-Lab" or not (root / ".git").exists():
        raise RuntimeError("NOT_EXACT_TTM_WORKSPACE")
    checkpoint = check_within(Path(a.checkpoint), root)
    manifest = check_within(root / MANIFEST_REL, root)
    if sha256(checkpoint.read_bytes()) != EXPECTED_SHA256["checkpoint"]:
        raise RuntimeError("CHECKPOINT_PIN_MISMATCH_NO_EXECUTION")
    if sha256(manifest.read_bytes()) != EXPECTED_SHA256["manifest"]:
        raise RuntimeError("BPE_MANIFEST_PIN_MISMATCH_NO_EXECUTION")

    # Preflight *all* sources before creating the one-shot directory.
    source_bytes = {name: git_read(root, blob) for name, blob in SOURCES.items()}
    if sha256(source_bytes["CF1_DEV_MODEL_INPUT_ONLY.json"]) != EXPECTED_SHA256["dev"]:
        raise RuntimeError("DEV_INPUT_PIN_MISMATCH_NO_EXECUTION")
    if sha256(source_bytes["CF1_DEV_PUBLIC_ORACLE.json"]) != EXPECTED_SHA256["oracle"]:
        raise RuntimeError("DEV_ORACLE_PIN_MISMATCH_NO_EXECUTION")
    run = root / RUN_REL
    if run.exists():
        raise RuntimeError("ONE_SHOT_RUN_DIRECTORY_EXISTS_REFUSE_REPLAY")
    run.mkdir(parents=True, exist_ok=False)
    for name, raw in source_bytes.items():
        with (run / name).open("xb") as f:
            f.write(raw)
    output = run / "CF1_FROZEN_O0_DEV36_SCORES.json"
    argv = [
        sys.executable, str(run / "cf1_dev_once_readonly.py"),
        "--p02", str(run / "transformer_core.py"),
        "--checkpoint", str(checkpoint),
        "--t1-manifest", str(manifest),
        "--dev-model-input", str(run / "CF1_DEV_MODEL_INPUT_ONLY.json"),
        "--out", str(output),
        "--allow-frozen-o0-dev-only",
    ]
    execution = subprocess.run(argv, cwd=str(run), capture_output=True, text=True)
    (run / "ONE_SHOT_STDOUT.txt").write_text(execution.stdout, encoding="utf-8")
    (run / "ONE_SHOT_STDERR.txt").write_text(execution.stderr, encoding="utf-8")
    if execution.returncode != 0:
        write_new_json(run / "CF1_ONE_SHOT_FAILURE.json", {
            "status": "FAIL_NO_REPLAY", "exit_code": execution.returncode,
            "stdout_sha256": sha256(execution.stdout.encode()),
            "stderr_sha256": sha256(execution.stderr.encode()),
            "optimizer_updates": 0, "gpu_calls": 0
        })
        raise RuntimeError("ONE_SHOT_DEV_SCORER_FAILED_DO_NOT_RETRY_SAME_RUN")

    data = json.loads(output.read_text(encoding="utf-8"))
    oracle = json.loads((run / "CF1_DEV_PUBLIC_ORACLE.json").read_text(encoding="utf-8"))
    input_rows = json.loads((run / "CF1_DEV_MODEL_INPUT_ONLY.json").read_text(encoding="utf-8"))["records"]
    scores = data["scores"]
    if len(scores) != 36 or len(input_rows) != 36 or len(oracle["pairs"]) != 36:
        raise RuntimeError("RESULT_COUNT_MISMATCH")
    summary = {"pairs": 36, "both_correct": 0, "by_family": {}, "ties": 0,
               "source_exact_git_blobs": SOURCES, "checkpoint_sha256": EXPECTED_SHA256["checkpoint"],
               "model_input_sha256": EXPECTED_SHA256["dev"], "bpe_manifest_sha256": EXPECTED_SHA256["manifest"],
               "gpu_calls": 0, "optimizer_updates": 0, "final_opened": False,
               "original_TEST_Q1Q2_read": False, "science_claim": "EXPLORATORY_PUBLIC_DEV_ONLY"}
    for row, gold, sc in zip(input_rows, oracle["pairs"], scores):
        if any(row[k] != gold[k] for k in ("context_a", "context_b", "completion_x", "completion_y")):
            raise RuntimeError("ORACLE_ORDER_OR_TEXT_MISMATCH")
        ma, mb = sc["margin_a"], sc["margin_b"]
        right_a = ma > 0 if gold["gold_a"] == "x" else ma < 0
        right_b = mb > 0 if gold["gold_b"] == "y" else mb < 0
        both = bool(right_a and right_b)
        family = gold["family"]
        item = summary["by_family"].setdefault(family, {"total": 0, "both_correct": 0})
        item["total"] += 1
        item["both_correct"] += int(both)
        summary["both_correct"] += int(both)
        summary["ties"] += int(ma == 0 or mb == 0)
    summary["accuracy"] = summary["both_correct"] / summary["pairs"]
    summary["scores_sha256"] = sha256(output.read_bytes())
    summary["status"] = "DEV_ONLY_DONE_NOT_FINAL_OR_ARCHITECTURE_CLAIM"
    write_new_json(run / "CF1_DEV36_OWNER_LOCAL_ADJUDICATION.json", summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
