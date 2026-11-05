#!/usr/bin/env python3
"""Register an existing result receipt; never generate experiment results."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "experiments" / "runs"
REGISTRY = ROOT / "experiments" / "registry.jsonl"
REQUIRED = {"run_id", "phase", "kind", "status", "git_sha", "branch", "config_path", "config_sha256", "dataset_id", "seed", "environment", "workload_id", "metrics", "qa_evidence"}
STATUSES = {"PASS", "FAIL", "INCONCLUSIVE"}
KINDS = {"QA", "TRAIN", "EVAL", "BENCH"}

def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(data, root=ROOT):
    missing = REQUIRED - set(data)
    if missing:
        raise ValueError("Missing fields: " + ", ".join(sorted(missing)))
    runid = data["run_id"]
    if not isinstance(runid, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{4,100}", runid):
        raise ValueError("Invalid run_id")
    if data["status"] not in STATUSES or data["kind"] not in KINDS:
        raise ValueError("Invalid status or kind")
    if not isinstance(data["metrics"], dict) or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in data["metrics"].values()):
        raise ValueError("Metrics must map names to numeric values")
    config_rel = Path(data["config_path"])
    if config_rel.is_absolute() or ".." in config_rel.parts:
        raise ValueError("config_path must be repository-relative")
    config = (root / config_rel).resolve()
    if not config.is_relative_to(root.resolve()) or not config.is_file():
        raise ValueError("Config not found under project root")
    actual = hash_file(config)
    if actual.lower() != data["config_sha256"].lower():
        raise ValueError("Config SHA256 mismatch: " + actual)
    return runid

def register(receipt_path, root=ROOT):
    root = Path(root)
    data = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    rid = validate(data, root)
    dest = root / "experiments" / "runs" / (rid + ".json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    # Create-only mode: prevents accidental overwrite of a prior run.
    with dest.open("xb") as f:
        f.write(raw)
        f.flush(); os.fsync(f.fileno())
    entry = {"run_id": rid, "phase": data["phase"], "kind": data["kind"], "status": data["status"], "receipt_sha256": hashlib.sha256(raw).hexdigest(), "path": str(dest.relative_to(root)).replace("\\", "/")}
    with (root / "experiments" / "registry.jsonl").open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
        f.flush(); os.fsync(f.fileno())
    return dest, entry

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("receipt", help="Pre-existing, completed JSON receipt")
    args = ap.parse_args()
    try:
        path, entry = register(args.receipt)
        print("RUN_REGISTERED=" + entry["run_id"])
        print("RECEIPT_SHA256=" + entry["receipt_sha256"])
        print("RECEIPT_PATH=" + str(path))
    except Exception as ex:
        print("RUN_REJECTED=" + str(ex), file=sys.stderr)
        return 1
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
