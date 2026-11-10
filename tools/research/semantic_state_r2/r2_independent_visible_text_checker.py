#!/usr/bin/env python3
"""Independent R2 visible-text verifier (does not import or call the generator).

A deterministic grammar interpreter is an oracle, NOT a learned neural model.
Inspect rendered story/question, never use source_events to infer an answer.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "ttm.r2.ordered_state_goal.counterfactual_pairs.v1"
PEOPLE = frozenset(("Lan", "Minh", "An", "Binh", "Hoa", "Mai", "Nam", "Duy"))
OBJECTS = frozenset(("key", "book", "ball", "cup", "map", "note"))
GOALS = frozenset(("open the gate", "read the book", "visit the garden", "help a friend",
                   "rest at home", "draw a map", "find the ball", "write a note"))
RE_OWNER = re.compile(r"^The ([a-z]+) belongs to ([A-Z][a-z]+)\.$")
RE_PLAN = re.compile(r"^([A-Z][a-z]+) plans to (.+)\.$")
RE_WHO = re.compile(r"^Who owns the ([a-z]+)\?$")
RE_GOAL = re.compile(r"^What does ([A-Z][a-z]+) plan to do\?$")


class ValidationError(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise ValidationError(reason)


def fingerprint(s):
    return Counter(re.findall(r"[a-z]+", s.lower()))


def interpret_visible(story, question):
    """Independently recover all state transitions from exact visible lines."""
    require(isinstance(story, str) and isinstance(question, str), "BAD_STORY_TYPE")
    lines = story.split("\n")
    require(len(lines) == 4 and all(line and len(line) < 140 for line in lines),
            "MALFORMED_EVENT_SEQUENCE")
    owners, goals, parsed = {}, {}, []
    for line in lines:
        m = RE_OWNER.fullmatch(line)
        if m:
            obj, person = m.groups()
            require(obj in OBJECTS and person in PEOPLE, "INVALID_OWNERSHIP_TERM")
            owners[obj] = person
            parsed.append(("owner", obj, person))
            continue
        m = RE_PLAN.fullmatch(line)
        if m:
            person, goal = m.groups()
            require(person in PEOPLE and goal in GOALS, "INVALID_GOAL_TERM")
            goals[person] = goal
            parsed.append(("goal", person, goal))
            continue
        raise ValidationError("UNRECOGNIZED_EVENT")

    wm = RE_WHO.fullmatch(question)
    gm = RE_GOAL.fullmatch(question)
    require((wm is None) != (gm is None), "MALFORMED_QUESTION")
    if wm:
        query_key = wm.group(1)
        require(query_key in OBJECTS and query_key in owners, "UNKNOWN_OWNER_QUERY")
        family, answer = "ownership", owners[query_key]
        candidates = tuple(sorted({v for k, target, v in parsed
                                   if k == "owner" and target == query_key}))
    else:
        query_key = gm.group(1)
        require(query_key in PEOPLE and query_key in goals, "UNKNOWN_GOAL_QUERY")
        family, answer = "goal", goals[query_key]
        candidates = tuple(sorted({v for k, target, v in parsed
                                   if k == "goal" and target == query_key}))
    require(len(candidates) == 2, "MISSING_CONFLICTING_UPDATES")
    require(all(x[0] == ("owner" if wm else "goal") for x in parsed),
            "MIXED_EVENT_FAMILIES")
    require(parsed[0][1] == query_key and parsed[2][1] == query_key and
            parsed[1][1] != query_key and parsed[3][1] != query_key,
            "QUERY_VS_DISTRACTOR_POSITIONS")
    return family, answer, candidates, parsed


def verify(data):
    require(isinstance(data, dict) and data.get("schema") == SCHEMA,
            "SCHEMA_MISMATCH")
    require(data.get("seed") == 20261110 and data.get("n_per_family") == 64,
            "FROZEN_DESIGN_MISMATCH")
    records = data.get("records")
    require(isinstance(records, list) and len(records) == 256, "INCORRECT_RECORD_COUNT")
    pairs = defaultdict(list)
    unique_ids, unique_stories = set(), set()
    accurate, bag_correct, composition = 0, 0, Counter()
    for row in records:
        require(isinstance(row, dict), "BAD_RECORD")
        rid = row.get("id")
        require(isinstance(rid, str) and rid not in unique_ids, "DUPLICATE_RECORD_ID")
        unique_ids.add(rid)
        family, answer, candidates, parsed = interpret_visible(row.get("story"), row.get("question"))
        require(row.get("family") == family, "FAMILY_LABEL_MISMATCH")
        require(row.get("answer") == answer, "ORACLE_ANSWER_MISMATCH")
        split = row.get("split")
        require(split in ("DEV", "CHALLENGE"), "BAD_SPLIT")
        pid = row.get("pair_id")
        require(isinstance(pid, str) and re.fullmatch(r"[OG]\d{3}", pid),
                "MALFORMED_PAIR_ID")
        require(pid.startswith("O" if family == "ownership" else "G"), "PAIR_FAMILY_MISMATCH")
        idx = int(pid[1:])
        require(1 <= idx <= 64, "PAIR_ID_OUT_OF_RANGE")
        require(split == ("DEV" if idx <= 32 else "CHALLENGE"), "SPLIT_LEAKAGE")
        variant = row.get("variant")
        require(type(variant) is int and variant in (0, 1) and
                rid == pid + ("A" if variant == 0 else "B"), "BAD_VARIANT")
        pair_fingerprint = (row["story"], row["question"])
        require(pair_fingerprint not in unique_stories, "DUPLICATE_STORY")
        unique_stories.add(pair_fingerprint)
        pairs[pid].append(row)
        composition[(family, split)] += 1
        accurate += int(row["answer"] == answer)
        # Order-invariant lexical rule: select alphabetic first possible value.
        # It CANNOT see order; it is not GPT-2 or a trained baseline.
        bag_correct += int(row["answer"] == candidates[0])
    require(len(pairs) == 128, "WRONG_PAIR_TOTAL")
    for (family, split), count in composition.items():
        require(count == 64, "BAD_FAMILY_SPLIT_COUNT")
    require(len(composition) == 4, "MISSING_FAMILY_SPLIT")
    for pid, rows in pairs.items():
        require(len(rows) == 2, "INCOMPLETE_PAIR")
        a, b = sorted(rows, key=lambda z: z["variant"])
        require(a["variant"] == 0 and b["variant"] == 1 and
                a["family"] == b["family"] and a["split"] == b["split"] and
                a["question"] == b["question"], "PAIR_STRUCTURE_INVALID")
        aa, bb = a["story"].split("\n"), b["story"].split("\n")
        require(aa[0] == bb[2] and aa[2] == bb[0] and aa[1] == bb[1] and
                aa[3] == bb[3], "NOT_SINGLE_REORDERED_UPDATE_PAIR")
        require(fingerprint(a["story"]) == fingerprint(b["story"]),
                "LEXICAL_BAG_NOT_MATCHED")
        require(a["answer"] != b["answer"], "COUNTERFACTUAL_ANSWER_NOT_CHANGED")
    require(accurate == 256 and bag_correct == 128, "EXPECTED_TOY_PROPERTIES_FAILED")
    return {
        "verdict": "PASS_DETERMINISTIC_TOY_SPEC_ONLY",
        "records": len(records),
        "pairs": len(pairs),
        "family_split_counts": {f"{k[0]}_{k[1]}": v for k, v in sorted(composition.items())},
        "independent_visible_text_oracle_correct": accurate,
        "order_invariant_lexical_control_correct": bag_correct,
        "bag_control_accuracy": bag_correct / len(records),
        "toy_rule_interpreter_accuracy": accurate / len(records),
        "counterfactual_pairs_exact_word_bag_matched": 128,
        "original_ttm_inference": 0,
        "original_ttm_training_steps": 0,
        "interpretation": [
            "All 256 toy answers follow directly from the public synthetic update rules.",
            "Swapping conflicting update order reverses the answer despite identical word multiset.",
            "A bag-of-words-only predictor cannot exceed 50% accuracy on balanced paired contradictions.",
            "A trivial last-relevant-update rule solves the toy; this is not evidence for new architecture.",
            "GPT-2/TTM causal attention does preserve order; no neural weakness is demonstrated."
        ]
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    output = Path(args.output).resolve()
    if output.exists():
        raise SystemExit("REFUSE_OVERWRITE")
    original = Path(args.input).read_bytes()
    dataset = json.loads(original.decode("utf-8"))
    result = verify(dataset)
    result["input_dataset_sha256"] = hashlib.sha256(original).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
