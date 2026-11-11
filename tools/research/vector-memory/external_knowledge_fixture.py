#!/usr/bin/env python3
"""TTM Vector Memory: synthetic external-fact story fixtures (DESIGN_ONLY).

Generates toy, counterfactual story-level examples. No checkpoint, tokenizer,
training, retrieval/inference, or scientific evaluation is performed here.

TEST must be generated privately with an independently escrowed secret, never
committed publicly. Public sample generation covers only TRAIN/DEV.
"""
from __future__ import annotations
import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path

SCHEMA = "ttm.vector_memory.external_knowledge.fixture.v1"
SPEC_ID = "TTM_VECTOR_MEMORY_EXTERNAL_KNOWLEDGE_EVALUATION_DESIGN"
SEED = "TTM_VM_EXTERNAL_FACTS_20261111_V1"
COUNTS = {"train": 256, "dev": 64, "test": 64}
LABELS = (
    "bivor", "caxen", "doral", "fekum", "gilen", "havor", "jekin", "kofur",
    "lamet", "mipor", "navek", "pizol", "raqum", "sivel", "tobak", "wexil",
)
QUESTION_TEMPLATES = (
    "For archive object {entity}, what is its assigned access tag? Answer:",
    "Which access tag belongs to archive object {entity}? Answer:",
)
FACT_TEMPLATE = "Archive object {entity} has access tag {value}."
ALIAS_ALPHABET = "bcdfghjklmnpqrstvwxz"


def digest(payload: str, split: str, secret: str | None) -> bytes:
    # TEST depends on private, independently committed entropy; no public seed
    # suffices to reconstruct its mappings or questions.
    if split == "test":
        if not secret or len(secret) < 24:
            raise ValueError("TEST_SECRET_REQUIRED_MIN_24_CHARS")
        return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
    return hashlib.sha256(f"{SEED}|{payload}".encode("utf-8")).digest()


def alias(split: str, index: int, slot: int, secret: str | None) -> str:
    raw = digest(f"alias|{split}|{index}|{slot}", split, secret)
    # Prefix fixes an intentionally fictitious namespace, not a real-world entity.
    return "obj" + "".join(ALIAS_ALPHABET[byte % len(ALIAS_ALPHABET)] for byte in raw[:12])


def make_case(split: str, index: int, test_secret: str | None = None) -> dict:
    if split not in COUNTS or not 0 <= index < COUNTS[split]:
        raise ValueError("INVALID_SPLIT_OR_INDEX")
    if split == "test" and (not test_secret or len(test_secret) < 24):
        raise ValueError("TEST_SECRET_REQUIRED_MIN_24_CHARS")
    # 16 labels exactly balanced in each split; independent of the question text.
    # 5 mod 16 is coprime, so wrong labels are also balanced.
    rotation = digest(f"rotation|{split}", split, test_secret)[0] % len(LABELS)
    correct_id = (index * 5 + rotation) % len(LABELS)
    target_slot = digest(f"targetslot|{split}|{index}", split, test_secret)[0] % 3
    labels = [LABELS[(correct_id + 3 + j * 4) % len(LABELS)] for j in range(3)]
    labels[target_slot] = LABELS[correct_id]
    # All three labels distinct and only one is gold.
    if len(set(labels)) != 3:
        raise AssertionError("DUPLICATE_LABEL_WITHIN_STORY")
    entities = [alias(split, index, j, test_secret) for j in range(3)]
    target_entity = entities[target_slot]
    answer = LABELS[correct_id]
    # Swap only the target value; keys, record count, and position stay fixed.
    # The foil cannot be the correct answer or any other existing card value.
    wrong_id = next((correct_id + shift) % len(LABELS) for shift in range(1, len(LABELS))
                    if LABELS[(correct_id + shift) % len(LABELS)] not in labels)
    wrong_label = LABELS[wrong_id]
    order = sorted(range(3), key=lambda j: digest(f"cardorder|{split}|{index}|{j}", split, test_secret))

    def card(j: int, value: str) -> dict:
        return {"key": entities[j], "value": value, "text": FACT_TEMPLATE.format(entity=entities[j], value=value)}

    right = [card(j, labels[j]) for j in order]
    wrong = [card(j, wrong_label if j == target_slot else labels[j]) for j in order]
    template = QUESTION_TEMPLATES[digest(f"template|{split}|{index}", split, test_secret)[0] % len(QUESTION_TEMPLATES)]
    question = template.format(entity=target_entity)
    case = {
        "schema": SCHEMA,
        "case_id": f"vm-{split}-{index:04d}",
        "split": split,
        "question": question,
        "answer": answer,
        "target_key": target_entity,
        "correct_memory": right,
        "wrong_memory": wrong,
        "none_memory": [],
        "no_memory_mask_all": True,
        "answer_only_scoring": True,
        "question_excludes_answer": True,
        "target_record_rank": next(i for i, j in enumerate(order) if j == target_slot),
        "source_type": "synthetic_fictitious_fact_after_frozen_checkpoint",
    }
    validate_case(case)
    return case


def validate_case(c: dict) -> None:
    assert c["schema"] == SCHEMA and c["split"] in COUNTS
    assert c["answer"] in LABELS and c["answer"] not in c["question"]
    assert c["target_key"] in c["question"]
    assert c["none_memory"] == [] and c["no_memory_mask_all"] is True
    yes, no = c["correct_memory"], c["wrong_memory"]
    assert len(yes) == len(no) == 3
    assert [x["key"] for x in yes] == [x["key"] for x in no]
    assert len({x["key"] for x in yes}) == 3
    assert [x["key"] for x in yes].count(c["target_key"]) == 1
    y_target = next(x for x in yes if x["key"] == c["target_key"])
    n_target = next(x for x in no if x["key"] == c["target_key"])
    assert y_target["value"] == c["answer"] and n_target["value"] != c["answer"]
    assert all(x["value"] != c["answer"] for x in no)
    assert all(a["value"] == b["value"] for a, b in zip(yes, no) if a["key"] != c["target_key"])
    assert all(x["text"] == FACT_TEMPLATE.format(entity=x["key"], value=x["value"]) for x in yes + no)
    assert all(x["key"] not in x["value"] for x in yes + no)


def build(split: str, secret: str | None = None) -> list[dict]:
    cases = [make_case(split, i, secret) for i in range(COUNTS[split])]
    ids = [c["target_key"] for c in cases]
    # Per-story independent key namespace, never use TRAIN/DEV answer labels to
    # construct TEST mappings. A separate cross-split check is in static QA.
    assert len(set(ids)) == len(ids)
    expected = COUNTS[split] // len(LABELS)
    assert all(sum(c["answer"] == label for c in cases) == expected for label in LABELS)
    return cases


def stable_json(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--split", choices=tuple(COUNTS), required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--repo-root", type=Path, required=True,
                   help="Approved project root. All generated outputs must stay within it.")
    args = p.parse_args()
    root = args.repo_root.resolve(strict=True)
    destination = args.output.resolve()
    if not destination.is_relative_to(root):
        raise SystemExit("PROJECT_BOUNDARY_DENIED")
    if destination.exists():
        raise SystemExit("NO_OVERWRITE_EXISTING_DATASET")
    if args.split == "test" and "/_private/" not in destination.as_posix().lower():
        raise SystemExit("TEST_OUTPUT_MUST_BE_UNDER_PROJECT__PRIVATE")
    secret = os.environ.get("TTM_VM_TEST_SECRET") if args.split == "test" else None
    cases = build(args.split, secret)
    destination.parent.mkdir(parents=True, exist_ok=True)
    raw = stable_json({"schema": SCHEMA, "split": args.split, "cases": cases})
    destination.write_bytes(raw)
    digest_sha = hashlib.sha256(raw).hexdigest()
    print(json.dumps({"status": "DESIGN_FIXTURE_GENERATED_NOT_SCIENCE", "split": args.split,
                      "cases": len(cases), "sha256": digest_sha,
                      "output_inside_project": True}, sort_keys=True))


if __name__ == "__main__":
    main()
