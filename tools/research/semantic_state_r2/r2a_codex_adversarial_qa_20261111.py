#!/usr/bin/env python3
"""Independent, CPU-only adversarial review of the public R2A fixture.

The visible-text interpreter does not import the generator or its event metadata.
The original checker is imported only to test deliberately corrupted inputs.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess


REVIEWED_HEAD = "c85b2ab504953bd667f09909f3495c4772fd1b2e"
ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "artifacts" / "qa" / "ttm-r2-semantic-toy" / "r2a"
SOURCE = ROOT / "tools" / "research" / "semantic_state_r2"

EVENT_PATTERNS = (
    (re.compile(r"The ([a-z]+) belongs to ([A-Z][a-z]+)\."), False),
    (re.compile(r"([A-Z][a-z]+) has the ([a-z]+) now\."), True),
    (re.compile(r"([A-Z][a-z]+) plans to ([a-z ]+)\."), False),
    (re.compile(r"([A-Z][a-z]+) intends to ([a-z ]+)\."), False),
)
QUESTION_PATTERNS = (
    re.compile(r"Who owns the ([a-z]+)\?"),
    re.compile(r"Who has the ([a-z]+) now\?"),
    re.compile(r"What does ([A-Z][a-z]+) plan to do\?"),
    re.compile(r"Which goal does ([A-Z][a-z]+) intend to pursue\?"),
)


def check(condition: bool, description: str) -> None:
    if not condition:
        raise AssertionError(description)


def read_json(path: Path) -> dict:
    return json.loads(path.read_bytes())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path)], cwd=ROOT, text=True
    ).strip()


def parse_event(sentence: str) -> tuple[str, str]:
    for pattern, reverse in EVENT_PATTERNS:
        match = pattern.fullmatch(sentence)
        if match is not None:
            left, right = match.groups()
            return (right, left) if reverse else (left, right)
    raise AssertionError(f"Unexpected R2A visible event: {sentence!r}")


def parse_query(question: str) -> str:
    for pattern in QUESTION_PATTERNS:
        match = pattern.fullmatch(question)
        if match is not None:
            return match.group(1)
    raise AssertionError(f"Unexpected R2A visible question: {question!r}")


def predict_visible(row: dict) -> dict:
    events = [parse_event(sentence) for sentence in row["story"].split("\n")]
    key = parse_query(row["question"])
    relevant = [(index, value) for index, (event_key, value) in enumerate(events)
                if event_key == key]
    check(len(events) == 4 and len(relevant) == 2, "Unexpected event counts")
    return {
        "latest_relevant": relevant[-1][1],
        "first_relevant": relevant[0][1],
        "last_story": events[-1][1],
        "third_story": events[2][1],
        "query_positions": [index for index, _ in relevant],
    }


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "reviewed_r2a_checker", SOURCE / "r2a_independent_checker.py"
    )
    check(spec is not None and spec.loader is not None, "Checker import unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mutation(checker, oracle: dict, model: dict, name: str, mutate, should_accept: bool):
    changed_oracle = deepcopy(oracle)
    changed_model = deepcopy(model)
    mutate(changed_oracle, changed_model)
    try:
        checker.check(changed_oracle, changed_model)
        accepted = True
        error = None
    except Exception as exc:
        accepted = False
        error = type(exc).__name__ + ": " + str(exc)
    check(accepted == should_accept, f"Unexpected checker behavior for {name}: {error}")
    return {"case": name, "accepted_by_original_checker": accepted,
            "expected_acceptance_observed": True, "rejection": error}


def review() -> dict:
    checkout_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    check(subprocess.run(
        ["git", "merge-base", "--is-ancestor", REVIEWED_HEAD, checkout_head],
        cwd=ROOT, check=False
    ).returncode == 0, "Review checkout is not descended from the pinned source")

    manifest_path = EVIDENCE / "R2A_COMPLETE_GITHUB_CUSTODY_MANIFEST_20261110.json"
    pinned_manifest = subprocess.check_output(
        ["git", "show", f"{REVIEWED_HEAD}:{manifest_path.relative_to(ROOT).as_posix()}"],
        cwd=ROOT,
    )
    check(manifest_path.read_bytes() == pinned_manifest,
          "Local manifest differs from pinned GitHub source")
    manifest = read_json(manifest_path)
    custody = []
    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        check(path.is_file(), "Manifest path missing")
        observed = {"path": entry["path"], "sha256": sha256(path),
                    "git_blob": git_blob(path), "bytes": path.stat().st_size}
        check(observed["sha256"] == entry["sha256"], f"SHA256 mismatch: {path}")
        check(observed["git_blob"] == entry["git_blob"], f"Git blob mismatch: {path}")
        check(observed["bytes"] == entry["size_bytes"], f"Size mismatch: {path}")
        custody.append(observed)
    check(len(custody) == 10, "Unexpected manifest count")

    oracle_path = EVIDENCE / "R2A_ORACLE_DATASET.json"
    model_path = EVIDENCE / "R2A_MODEL_INPUT_ONLY.json"
    oracle = read_json(oracle_path)
    model = read_json(model_path)
    pairs, probes = oracle["pairs"], oracle["probes"]
    records = pairs + probes
    check((len(pairs), len(probes), len(model["records"])) == (256, 128, 384),
          "Fixture counts wrong")
    check(model["records"] == [
        {"story": row["story"], "question": row["question"]} for row in records
    ], "Projection not equal to public oracle ordering")
    check(all(set(row) == {"story", "question"} for row in model["records"]),
          "Canonical record carries additional fields")

    predictions = [predict_visible(row) for row in records]
    answer_scores = {
        method: sum(pred[method] == row["answer"]
                    for pred, row in zip(predictions, records))
        for method in ("latest_relevant", "first_relevant", "last_story", "third_story")
    }
    check(answer_scores["latest_relevant"] == 384, "Key-recency rule is not exact")

    pair_lookup = defaultdict(dict)
    for pair in pairs:
        pair_lookup[pair["pair_id"]][pair["variant"]] = pair
    probe_lookup = {probe["pair_id"]: probe for probe in probes}
    check(len(pair_lookup) == len(probe_lookup) == 128, "Expected 128 groups")
    position_counts = Counter()
    families_splits = Counter()
    for ident, pair in pair_lookup.items():
        check(set(pair) == {"A", "B"}, f"A/B variant missing for {ident}")
        a, b, q = pair["A"], pair["B"], probe_lookup[ident]
        bag = lambda s: Counter(re.findall(r"[a-z]+", s.lower()))
        check(bag(a["story"]) == bag(b["story"]), "Word multiset differs")
        check(a["question"] == b["question"] and a["answer"] != b["answer"],
              "Pair is not answer-flipping")
        check(q["story"] == a["story"] and q["question"] != a["question"]
              and q["answer"] != a["answer"], "Query swap is not A-bound")
        positions = tuple(predict_visible(a)["query_positions"])
        position_counts[(a["family"], a["split"], positions)] += 1
        families_splits[(a["family"], a["split"])] += 1
    check(all(count == 32 for count in families_splits.values())
          and len(families_splits) == 4, "Family/split size imbalance")
    check(all(sum(1 for fam, split, pos in position_counts
                  if fam == f and split == s) == 6
              for f, s in families_splits), "Incomplete position counterbalance")

    story_counts = Counter(row["story"] for row in records)
    duplicate_stories = sum(count == 2 for count in story_counts.values())
    check(duplicate_stories == 128 and max(story_counts.values()) == 2,
          "Unexpected A/query-swap duplication")
    check(all(pairs[2 * i]["variant"] == "A"
              and pairs[2 * i + 1]["variant"] == "B"
              and pairs[2 * i]["pair_id"] == pairs[2 * i + 1]["pair_id"]
              for i in range(128)), "Pair adjacency changed")
    check(all(p["story"] == pair_lookup[p["pair_id"]]["A"]["story"]
              for p in probes), "Probe-A story reuse changed")

    checker = load_checker()
    check(checker.check(oracle, model)["result"] == "PASS_SCOPED_TOY_FIXTURE_ONLY",
          "Original checker rejects canonical fixture")
    mutations = [
        ("MODEL_ROOT_ANSWER_VECTOR", lambda d, m: m.update(answer_vector=[r["answer"] for r in records]), True),
        ("MODEL_ROOT_ORACLE", lambda d, m: m.update(oracle=d), True),
        ("MODEL_ROOT_SPLIT_METADATA", lambda d, m: m.update(split=[r["split"] for r in records]), True),
        ("ORACLE_DECLARATION_FALSE_SEALED", lambda d, m: d.update(declaration="Sealed FINAL TEST with hidden labels"), True),
        ("MODEL_RECORD_ANSWER", lambda d, m: m["records"][0].update(answer="Lan"), False),
        ("MODEL_RECORD_SPLIT", lambda d, m: m["records"][0].update(split="DEV"), False),
        ("ORACLE_ROOT_UNEXPECTED_FIELD", lambda d, m: d.update(unexpected="metadata"), False),
        ("PAIR_WRONG_ANSWER", lambda d, m: d["pairs"][0].update(answer="INVALID"), False),
        ("SOURCE_EVENTS_TAMPERED", lambda d, m: d["pairs"][0]["source_events"][0].update(value="INVALID"), False),
        ("WRONG_DECLARED_COUNTS", lambda d, m: d["counts"].update(pairs=999), False),
        ("MODEL_PROJECTION_REORDER", lambda d, m: m["records"].reverse(), False),
    ]
    mutation_results = [
        test_mutation(checker, oracle, model, name, mutate, should_accept)
        for name, mutate, should_accept in mutations
    ]
    bypasses = [result["case"] for result in mutation_results
                if result["accepted_by_original_checker"] and
                result["case"] in {"MODEL_ROOT_ANSWER_VECTOR", "MODEL_ROOT_ORACLE",
                                   "MODEL_ROOT_SPLIT_METADATA", "ORACLE_DECLARATION_FALSE_SEALED"}]
    check(len(bypasses) == 4, "Expected known source validator bypasses changed")

    return {
        "schema": "ttm.r2a.codex_ai_internal_adversarial_review.v1",
        "pinned_head": REVIEWED_HEAD,
        "reviewer": "CODEX_AI_INTERNAL",
        "scope": "PUBLIC_R2A_CPU_ONLY_NO_NEURAL_NO_GPU",
        "independent_review_script_sha256": sha256(Path(__file__)),
        "integrity": {"files_verified": len(custody), "files": custody,
                      "oracle_sha256": sha256(oracle_path),
                      "model_input_sha256": sha256(model_path)},
        "independent_visible_text": {
            "rows": len(records), "prediction_scores_of_384": answer_scores,
            "paired_bag_of_words_max_correct_of_256": 128,
            "counterfactual_groups": len(pair_lookup),
            "query_swap_probes": len(probe_lookup),
            "A_B_adjacent_pairs": 128,
            "A_Q_duplicate_stories": duplicate_stories,
            "query_swap_uses_only_A": 128,
            "six_query_position_patterns_per_family_split": True,
            "public_answer_labels": True,
            "blind_science_final": False,
        },
        "validator_mutations": mutation_results,
        "validator_mutations_expected_results": len(mutation_results),
        "validator_bypasses": bypasses,
        "adjudication": {
            "R2A_VALID_SCOPED": "PASS_WITH_VALIDATOR_HARDENING_REQUIRED",
            "R2A_INPUT_SCHEMA": "FAIL_SCOPED",
            "FAIR_SUPERVISION": "HOLD_DESIGN_ONLY",
            "NEURAL_GAIN": "NOT_TESTED",
            "recommended_owner_decision": "DESIGN_R3_BEFORE_O1",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = review()
    output = args.output.resolve()
    check(not output.exists(), "Refuse to overwrite QA receipt")
    check(output.is_relative_to(ROOT), "QA receipt must remain inside the repository")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8", newline="\n")
    print(f"R2A_CODEX_QA=PASS_SCOPED rows={result['independent_visible_text']['rows']}")
    print(f"R2A_MODEL_ROOT_VALIDATOR=FAIL_SCOPED bypasses={len(result['validator_bypasses'])}")
    print("R2A_NEURAL_GAIN=NOT_TESTED")
    print(f"R2A_RECEIPT_SHA256={sha256(output)}")


if __name__ == "__main__":
    main()
