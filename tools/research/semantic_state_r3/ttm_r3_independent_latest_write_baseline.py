#!/usr/bin/env python3
"""Independent read-only adversarial baseline for pinned TTM-R3 public toy.

No import of r3_generator or r3_independent_checker. Prediction reads only
story and question. Oracle answers are used AFTER prediction for scoring.
It does not validate whether the story's transition preconditions hold.
"""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

EXPECTED_MODEL_SHA256 = "4fa0ad45acdfecb2143a984127e6ad0c50126c203996148d60843eb1214cd50a"
EXPECTED_ORACLE_SHA256 = "bd9fb15d3f3850823e083269a61df90eaddaea3e61b8b73e9f40b4ec74c7ce47"
HOLDER_Q = re.compile(r"^Who holds ([a-z]+)\?$")
GOAL_Q = re.compile(r"^What is ([A-Za-z]+) goal\?$")
PASS = re.compile(r"^([A-Za-z]+) passes ([a-z]+) to ([A-Za-z]+)\.$")
INIT = re.compile(r"^([a-z]+) starts with ([A-Za-z]+)\.$")
CHANGE = re.compile(r"^([A-Za-z]+) changes goal from ([a-z]+) to ([a-z]+)\.$")
SET = re.compile(r"^([A-Za-z]+) begins goal ([a-z]+)\.$")
def predict(row):
    lines = row["story"].split("\n")
    match = HOLDER_Q.fullmatch(row["question"])
    if match:
        item = match.group(1)
        for line in reversed(lines):
            m = PASS.fullmatch(line)
            if m and m.group(2) == item:
                return m.group(3), "last_handoff"
            m = INIT.fullmatch(line)
            if m and m.group(1) == item:
                return m.group(2), "initial_holder"
        return None, "missing_holder"
    match = GOAL_Q.fullmatch(row["question"])
    if match:
        person = match.group(1)
        for line in reversed(lines):
            m = CHANGE.fullmatch(line)
            if m and m.group(1) == person:
                return m.group(3), "last_goal_change"
            m = SET.fullmatch(line)
            if m and m.group(1) == person:
                return m.group(2), "initial_goal"
        return None, "missing_goal"
    return None, "unknown_question"

def checked_json(path, expected_sha):
    raw = Path(path).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha:
        raise SystemExit(f"SOURCE_PIN_FAIL: {path}: {actual}")
    return json.loads(raw)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model-input", required=True, type=Path)
    p.add_argument("--oracle", required=True, type=Path)
    args = p.parse_args()
    model = checked_json(args.model_input, EXPECTED_MODEL_SHA256)
    oracle = checked_json(args.oracle, EXPECTED_ORACLE_SHA256)
    if len(model["records"]) != 384 or len(oracle["groups"]) != 96:
        raise SystemExit("UNEXPECTED_CORPUS_SIZE")
    totals = defaultdict(lambda: {"correct": 0, "total": 0})
    types = defaultdict(int)
    misses = []
    for i, row in enumerate(model["records"]):
        group = oracle["groups"][i // 4]
        cell = group["cells"][i % 4]
        # Check visible projection is aligned without ever using labels to predict.
        if (row["story"], row["question"]) != (cell["story"], cell["question"]):
            raise SystemExit(f"MODEL_ORACLE_PROJECTION_MISMATCH_AT_{i}")
        prediction, kind = predict(row)
        key = f"{group['family']}_{group['split']}"
        totals[key]["total"] += 1
        types[kind] += 1
        if prediction == cell["answer"]:
            totals[key]["correct"] += 1
        else:
            misses.append({"index": i, "group_id": group["group_id"],
                           "cell": cell["cell"], "predicted": prediction,
                           "expected": cell["answer"]})
    summary = {"status": "HEURISTIC_100_PERCENT" if not misses else "PARTIAL",
               "correct": 384 - len(misses), "total": 384,
               "method": "backward latest direct assignment, no alias/delegate/cancel/state replay",
               "by_family_split": dict(sorted(totals.items())),
               "source_of_prediction": dict(sorted(types.items())),
               "errors": misses[:10]}
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if misses:
        raise SystemExit(1)

if __name__ == "__main__":
    main()