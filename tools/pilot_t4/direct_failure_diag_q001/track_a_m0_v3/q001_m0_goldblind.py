#!/usr/bin/env python3
"""Track A Q001 M0 v3: gold-blind MOCK fixture and scoring contract.

DESIGN/SOURCE QA ONLY. This module does not load checkpoints or run I2.
This is a NEW protocol; it does not validate or replace the historical fixture.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
import random
import sys

SCHEMA = "ttm.sm4m.q001.track_a.measurement.v3.mock"
SEED = 20261116
GROUPS = {
    "TRAIN": 24, "HELDOUT_RECOMBINED": 16, "HELDOUT_NOVEL_IDS": 16,
    "PAIRED_COUNTERFACTUAL": 16, "HELDOUT_ABSENT": 8,
}
VOCAB = 2048


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def require(condition, why):
    if not condition:
        raise ValueError("HOLD_M0_" + why)


def inventory(allowed):
    require(len(allowed) >= 80 and len(set(allowed)) == len(allowed),
            "ALLOWED_IDS")
    require(all(type(x) is int and 0 <= x < VOCAB and x != 256
                for x in allowed), "INVALID_IDS")
    return sorted(allowed)


def roles_for(allowed, seed=SEED):
    ids = inventory(allowed)
    rng = random.Random(seed)
    rng.shuffle(ids)
    return (rng, ids[:4], ids[4:20], ids[20:36],
            ids[36:52], ids[52:68])


def candidates_from_visible(context, no_answer, value_pool):
    """Gold- and label-free; consumes only 9 visible IDs and declared roles/pool."""
    require(len(context) == 9 and context[2] != context[5],
            "BAD_VISIBLE_CONTEXT")
    values = [context[2], context[5], no_answer]
    require(len(set(values)) == 3, "VISIBLE_VALUE_COLLISION")
    eligible = sorted(set(value_pool) - set(values))
    require(bool(eligible), "NO_FOURTH_CANDIDATE")
    token = min(eligible, key=lambda t: (digest(["filler", context, t]), t))
    values.append(token)
    # Choice display order is a function of visible input ONLY.
    values.sort(key=lambda t: (digest(["order", context, t]), t))
    return values


def oracle(context, no_answer):
    return (context[2] if context[7] == context[1]
            else context[5] if context[7] == context[4] else no_answer)


def make_fixture(allowed, seed=SEED):
    rng, roles, ks, vs, kn, vn = roles_for(allowed, seed)
    bind, query, answer, no_answer = roles
    pool = vs + vn
    rows, contexts = [], set()

    def put(group, k1, v1, k2, v2, kq, parent=None):
        require(k1 != k2 and v1 != v2, "BAD_BINDINGS")
        ctx = [bind, k1, v1, bind, k2, v2, query, kq, answer]
        if tuple(ctx) in contexts:
            return False
        row = {"id": f"{group}_{sum(r['group'] == group for r in rows):02d}",
               "group": group, "context": ctx, "gold": oracle(ctx, no_answer),
               "no_answer": no_answer, "value_pool": pool,
               "parent": parent}
        row["choices"] = candidates_from_visible(ctx, no_answer, pool)
        contexts.add(tuple(ctx))
        rows.append(row)
        return True

    for i in range(16):
        k1, k2 = ks[i], ks[(i + 5) % 16]
        v1, v2 = vs[i], vs[(i + 7) % 16]
        require(put("TRAIN", k1, v1, k2, v2, k1 if i % 2 == 0 else k2),
                "TRAIN_COLLISION")
    for i in range(8):
        require(put("TRAIN", ks[i], vs[i], ks[(i + 3) % 16],
                    vs[(i + 4) % 16], ks[(i + 8) % 16]), "TRAIN_ABSENT")

    train_pairs = {(r["context"][i], r["context"][i+1])
                   for r in rows for i in (1, 4)}
    attempts = 0
    while sum(r["group"] == "HELDOUT_RECOMBINED" for r in rows) < 16:
        attempts += 1
        require(attempts <= 20000, "RECOMBINED_GENERATION")
        k1, k2 = rng.sample(ks, 2)
        v1, v2 = rng.sample(vs, 2)
        if (k1, v1) in train_pairs or (k2, v2) in train_pairs:
            continue
        put("HELDOUT_RECOMBINED", k1, v1, k2, v2,
            k1 if attempts % 2 else k2)

    for i in range(16):
        require(put("HELDOUT_NOVEL_IDS", kn[i], vn[i],
                    kn[(i + 1) % 16], vn[(i + 5) % 16],
                    kn[i] if i % 2 == 0 else kn[(i + 1) % 16]),
                "NOVEL_COLLISION")

    for p in rows[:16]:
        c = p["context"]
        require(put("PAIRED_COUNTERFACTUAL", c[1], c[5], c[4], c[2],
                    c[7], parent=p["id"]), "PARENT_COLLISION")

    attempts = 0
    while sum(r["group"] == "HELDOUT_ABSENT" for r in rows) < 8:
        attempts += 1
        require(attempts <= 20000, "ABSENT_GENERATION")
        k1, k2, kq = rng.sample(ks, 3)
        v1, v2 = rng.sample(vs, 2)
        if (k1, v1) in train_pairs or (k2, v2) in train_pairs:
            continue
        put("HELDOUT_ABSENT", k1, v1, k2, v2, kq)

    validate_fixture(rows)
    return rows


def split_audit(rows):
    train = [r for r in rows if r["group"] == "TRAIN"]
    pairs = {(r["context"][i], r["context"][i + 1])
             for r in train for i in (1, 4)}
    clean = [r for r in rows
             if r["group"] in ("HELDOUT_RECOMBINED", "HELDOUT_ABSENT")]
    leaked = [r["id"] for r in clean
              if any((r["context"][i], r["context"][i + 1]) in pairs
                     for i in (1, 4))]
    novel = [r for r in rows if r["group"] == "HELDOUT_NOVEL_IDS"]
    train_ids = {x for r in train for x in r["context"]}
    novel_overlap = [r["id"] for r in novel
                     if any(r["context"][i] in train_ids
                            for i in (1, 2, 4, 5, 7))]
    parent_count = sum(r["group"] == "PAIRED_COUNTERFACTUAL"
                       and r["parent"] is not None for r in rows)
    return {"train_binding_leaks_in_independent_holdouts": leaked,
            "novel_role_id_collisions": novel_overlap,
            "counterfactual_parent_linked_cases": parent_count,
            "counterfactual_independent_of_train": False}


def validate_fixture(rows):
    require(Counter(r["group"] for r in rows) == Counter(GROUPS),
            "GROUP_COUNTS")
    require(len({r["id"] for r in rows}) == 80 and
            len({tuple(r["context"]) for r in rows}) == 80,
            "DUPLICATE_ROWS")
    for row in rows:
        c = row["context"]
        require(len(c) == 9 and c[1] != c[4] and c[2] != c[5],
                "CASE_GRAMMAR")
        require(row["gold"] == oracle(c, row["no_answer"]), "BAD_GOLD")
        require(row["choices"] == candidates_from_visible(
            c, row["no_answer"], row["value_pool"]), "LABEL_LEAK_OR_CHOICES")
        require(row["gold"] in row["choices"], "GOLD_NOT_VISIBLE")
    report = split_audit(rows)
    require(not report["train_binding_leaks_in_independent_holdouts"]
            and not report["novel_role_id_collisions"]
            and report["counterfactual_parent_linked_cases"] == 16,
            "SPLIT_LEAK_OR_PARENT")
    parents = {r["id"]: r for r in rows if r["group"] == "TRAIN"}
    for r in rows:
        if r["group"] != "PAIRED_COUNTERFACTUAL":
            require(r["parent"] is None, "UNEXPECTED_PARENT")
            continue
        p = parents.get(r["parent"])
        require(p is not None, "PARENT_MISSING")
        a, b = p["context"], r["context"]
        require(a[1] == b[1] and a[4] == b[4] and a[7] == b[7]
                and a[2] == b[5] and a[5] == b[2]
                and p["gold"] != r["gold"], "COUNTERFACTUAL_BAD_SWAP")
    return report


def unique_top1(pairs):
    """Order-independent argmax. Ambiguous ties abstain; never first-choice."""
    m = max(v for _, v in pairs)
    winners = [i for i, v in pairs if v == m]
    return winners[0] if len(winners) == 1 else None


def score_logits(logits, row):
    """Gold used ONLY for endpoints, NEVER for constructing choices."""
    require(len(logits) == VOCAB and all(
        isinstance(v, (float, int)) and math.isfinite(v) for v in logits),
        "LOGIT_SHAPE_OR_FINITE")
    c = row["context"]
    opts = candidates_from_visible(c, row["no_answer"], row["value_pool"])
    require(opts == row["choices"], "CHOICE_INTEGRITY")
    gold = row["gold"]
    require(type(gold) is int and 0 <= gold < VOCAB, "INVALID_GOLD")
    top = unique_top1(enumerate(logits))
    restricted = unique_top1((x, logits[x]) for x in opts)
    m = max(logits)
    nll = m + math.log(sum(math.exp(x-m) for x in logits)) - logits[gold]
    competitors = [logits[x] for x in opts if x != gold]
    return {"full_vocab_gold_nll": nll,
            "full_vocab_gold_rank": 1 + sum(x > logits[gold] for x in logits),
            "full_vocab_top1_correct": top == gold,
            "full_vocab_tie_abstained": top is None,
            "context_contrast_logit_margin": logits[gold] - max(competitors),
            "candidate_only_top1_correct_secondary": restricted == gold,
            "candidate_tie_abstained": restricted is None}


def manifest(rows):
    return {"schema": SCHEMA, "seed": SEED, "counts": GROUPS,
            "fixture_sha256": digest(rows),
            "case_sha256": {r["id"]: digest(r) for r in rows},
            "group_sha256": {g: digest([r for r in rows if r["group"] == g])
                             for g in GROUPS},
            "split_audit": split_audit(rows),
            "mock_only": True, "model_forward": False,
            "I2": "NOT_EXECUTED", "I1": "NOT_ADJUDICATED"}


def mock_source_qa():
    rows = make_fixture(list(range(300, 500)))
    constant = [0.0] * VOCAB
    equal_scores = [score_logits(constant, row) for row in rows]
    # These two controls never read context/gold in constructing logits.
    blind = [float(-i) for i in range(VOCAB)]
    blind_scores = [score_logits(blind, row) for row in rows]
    second = make_fixture(list(range(300, 500)))
    train = [r for r in rows if r["group"] == "TRAIN"]
    bound = sum(r["gold"] != r["no_answer"] for r in train)
    checks = {
        "determinism": digest(rows) == digest(second),
        "seed_changes_fixture": digest(rows) != digest(
            make_fixture(list(range(300, 500)), seed=SEED+1)),
        "correct_counts": len(rows) == 80 and bound == 16,
        "zero_binding_leak": not split_audit(rows)[
            "train_binding_leaks_in_independent_holdouts"],
        "linked_counterfactual_declared": split_audit(rows)[
            "counterfactual_parent_linked_cases"] == 16,
        "equal_logits_candidate_abstains": all(
            s["candidate_tie_abstained"] and
            not s["candidate_only_top1_correct_secondary"] for s in equal_scores),
        "equal_logits_full_vocab_abstains": all(
            s["full_vocab_tie_abstained"] and
            not s["full_vocab_top1_correct"] for s in equal_scores),
        "gold_mutation_keeps_choices": all(
            candidates_from_visible(r["context"], r["no_answer"],
                                    r["value_pool"]) == r["choices"] for r in rows),
        "blind_logit_vector_constant_across_contexts": blind[0] == 0.0,
        "mock_no_forward": True,
    }
    return {"mode": "MOCK_SOURCE_ONLY", "checks": checks,
            "passed": sum(checks.values()), "total": len(checks),
            "blind_restricted_by_group": {
                g: sum(s["candidate_only_top1_correct_secondary"]
                       for s, r in zip(blind_scores, rows) if r["group"] == g)
                for g in GROUPS},
            "fixture_sha256": digest(rows), "model_forward": False,
            "native_windows_qa": "NOT_EXECUTED",
            "independent_human_review": "NOT_EXECUTED"}


if __name__ == "__main__":
    if sys.argv[1:] == ["mock-qa"]:
        print(json.dumps(mock_source_qa(), sort_keys=True))
    elif sys.argv[1:] == ["mock-manifest"]:
        print(json.dumps(manifest(make_fixture(list(range(300, 500)))),
                         sort_keys=True, indent=2))
    else:
        raise SystemExit("SOURCE_ONLY: choose mock-qa or mock-manifest")
