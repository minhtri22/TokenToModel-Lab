#!/usr/bin/env python3
"""R2 semantic state/goal toy: deterministic language-only counterfactual generator.

No model import, training, generation from TTM, private data, or GPU work.
This is an *oracle fixture*, not a demonstration of neural semantic learning.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import re

SCHEMA = "ttm.r2.ordered_state_goal.counterfactual_pairs.v1"
SEED = 20261110
PEOPLE = ("Lan", "Minh", "An", "Binh", "Hoa", "Mai", "Nam", "Duy")
OBJECTS = ("key", "book", "ball", "cup", "map", "note")
GOALS = ("open the gate", "read the book", "visit the garden", "help a friend",
         "rest at home", "draw a map", "find the ball", "write a note")
N_PER_FAMILY = 64
STORIES_PER_PAIR = 2


def canonical_bytes(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def update_state(events):
    """Generator-side structured transition oracle; checker must NOT call this."""
    state = {"owner": {}, "goal": {}}
    for event in events:
        if event["type"] == "assign":
            state["owner"][event["object"]] = event["person"]
        elif event["type"] == "plan":
            state["goal"][event["person"]] = event["goal"]
        else:
            raise ValueError("UNKNOWN_EVENT")
    return state


def render(events):
    rows = []
    for event in events:
        if event["type"] == "assign":
            rows.append(f'The {event["object"]} belongs to {event["person"]}.')
        else:
            rows.append(f'{event["person"]} plans to {event["goal"]}.')
    return "\n".join(rows)


def words(text):
    return Counter(re.findall(r"[a-z]+", text.lower()))


def build_pair(family, i, rng):
    people = rng.sample(PEOPLE, 4)
    a, b, c, d = people
    if family == "ownership":
        target, distract = rng.sample(OBJECTS, 2)
        e1 = {"type": "assign", "object": target, "person": a}
        e2 = {"type": "assign", "object": target, "person": b}
        noise1 = {"type": "assign", "object": distract, "person": c}
        noise2 = {"type": "assign", "object": distract, "person": d}
        question = f"Who owns the {target}?"
        target_key = target
        track = "owner"
    elif family == "goal":
        g1, g2, g3, g4 = rng.sample(GOALS, 4)
        e1 = {"type": "plan", "person": a, "goal": g1}
        e2 = {"type": "plan", "person": a, "goal": g2}
        noise1 = {"type": "plan", "person": b, "goal": g3}
        noise2 = {"type": "plan", "person": b, "goal": g4}
        question = f"What does {a} plan to do?"
        target_key = a
        track = "goal"
    else:
        raise ValueError("BAD_FAMILY")

    sequences = ([e1, noise1, e2, noise2], [e2, noise1, e1, noise2])
    pair_id = ("O" if family == "ownership" else "G") + f"{i+1:03d}"
    split = "DEV" if i < 32 else "CHALLENGE"
    records = []
    for variant, events in enumerate(sequences):
        answer = update_state(events)[track][target_key]
        records.append({
            "id": pair_id + ("A" if variant == 0 else "B"),
            "pair_id": pair_id,
            "family": family,
            "split": split,
            "variant": variant,
            "story": render(events),
            "question": question,
            "answer": answer,
            "source_events": events,
        })
    assert records[0]["answer"] != records[1]["answer"]
    assert words(records[0]["story"]) == words(records[1]["story"])
    assert records[0]["question"] == records[1]["question"]
    assert records[0]["split"] == records[1]["split"]
    return records


def build_dataset():
    rng = random.Random(SEED)
    records = []
    pair_seen = set()
    for family in ("ownership", "goal"):
        for i in range(N_PER_FAMILY):
            for retry in range(100):
                pair = build_pair(family, i, rng)
                fingerprint = tuple(sorted((x["story"], x["question"]) for x in pair))
                if fingerprint not in pair_seen:
                    pair_seen.add(fingerprint)
                    records.extend(pair)
                    break
            else:
                raise RuntimeError("FAILED_TO_CONSTRUCT_UNIQUE_PAIR")
    records.sort(key=lambda x: (x["family"], x["pair_id"], x["variant"]))
    counts = Counter((r["family"], r["split"]) for r in records)
    return {
        "schema": SCHEMA, "seed": SEED, "n_per_family": N_PER_FAMILY,
        "notes": [
            "Artificial English grammar; not a natural language understanding benchmark.",
            "DEV and CHALLENGE labels are both publicly exposed; CHALLENGE is NOT a sealed TEST.",
            "Two variants have identical word multisets, but opposing last-write-wins answers.",
            "The generated answer is computed from structured events; independent checker must parse the visible story.",
            "No model training, no inference, no TTM checkpoint, no private TinyStories, TEST or Q1Q2."
        ],
        "counts": {f"{k[0]}_{k[1]}": v for k, v in sorted(counts.items())},
        "records": records
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True, help="new UTF-8 JSON path; never overwrite")
    a = ap.parse_args()
    target = Path(a.output).expanduser().resolve()
    if target.exists():
        raise SystemExit("REFUSE_OVERWRITE_EXISTING_OUTPUT")
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_bytes(build_dataset())
    target.write_bytes(payload)
    print(json.dumps({"status": "GENERATED_SYNTHETIC_ONLY",
                      "dataset_sha256": sha256(payload),
                      "records": 256, "pairs": 128, "path": str(target)}, sort_keys=True))


if __name__ == "__main__":
    main()
