#!/usr/bin/env python3
"""Second, separately coded mock checker. NOT an independent human reviewer."""
import hashlib
import json
import sys

from q001_m0_goldblind import make_fixture, score_logits

GROUP_COUNTS = dict(TRAIN=24, HELDOUT_RECOMBINED=16,
                    HELDOUT_NOVEL_IDS=16, PAIRED_COUNTERFACTUAL=16,
                    HELDOUT_ABSENT=8)


def h(obj):
    b = (json.dumps(obj, sort_keys=True, ensure_ascii=False,
                    separators=(",", ":")) + "\n").encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def independent_choices(row):
    ctx = row["context"]
    n = row["no_answer"]
    base = [ctx[2], ctx[5], n]
    possible = sorted(set(row["value_pool"]) - set(base))
    assert len(set(base)) == 3 and possible
    extra = min(possible, key=lambda t: (h(["filler", ctx, t]), t))
    base.append(extra)
    return sorted(base, key=lambda t: (h(["order", ctx, t]), t))


def check():
    rows = make_fixture(list(range(300, 500)))
    failures = []
    observed = {g: [] for g in GROUP_COUNTS}
    train = [r for r in rows if r["group"] == "TRAIN"]
    train_bindings = {(r["context"][j], r["context"][j + 1])
                      for r in train for j in (1, 4)}
    train_ids = {x for r in train for x in r["context"]}
    by_id = {r["id"]: r for r in train}
    constant = [0.0] * 2048
    blind = [float(-i) for i in range(2048)]
    negative = {}
    for row in rows:
        c, group = row["context"], row["group"]
        observed[group].append(row)
        expected = (c[2] if c[7] == c[1] else c[5] if c[7] == c[4]
                    else row["no_answer"])
        if row["gold"] != expected:
            failures.append("oracle:" + row["id"])
        if row["choices"] != independent_choices(row):
            failures.append("gold_blind_candidate:" + row["id"])
        if group in ("HELDOUT_RECOMBINED", "HELDOUT_ABSENT"):
            if any((c[j], c[j + 1]) in train_bindings for j in (1, 4)):
                failures.append("train_binding_leak:" + row["id"])
        if group == "HELDOUT_NOVEL_IDS":
            if any(c[j] in train_ids for j in (1, 2, 4, 5, 7)):
                failures.append("token_id_leak:" + row["id"])
        if group == "PAIRED_COUNTERFACTUAL":
            p = by_id.get(row["parent"])
            if not p or c[2] != p["context"][5] or c[5] != p["context"][2]:
                failures.append("counterfactual_parent:" + row["id"])
        s = score_logits(constant, row)
        if not (s["candidate_tie_abstained"] and s["full_vocab_tie_abstained"]):
            failures.append("tie_shortcut:" + row["id"])
    for group, want in GROUP_COUNTS.items():
        if len(observed[group]) != want:
            failures.append("count:" + group)
        negative[group] = sum(score_logits(blind, r)[
            "candidate_only_top1_correct_secondary"] for r in observed[group])
    # Candidate-only blind scores are diagnostics, not claims of chance=25%.
    return {"schema": "ttm.sm4m.track_a.m0.independent_logic_mock.v1",
            "input_fixture_sha256": h(rows),
            "groups": {k: len(v) for k, v in observed.items()},
            "blind_fixed_id_candidate_secondary": negative,
            "negative_equal_logits_pass": "tie_shortcut" not in
                " ".join(failures),
            "failure_count": len(failures), "failures": failures,
            "status": "PASS_MOCK_LOGIC" if not failures else "HOLD_MOCK_LOGIC",
            "author_identity_independent": False,
            "external_distinct_reviewer": "NOT_EXECUTED",
            "python312_windows_verified": "NOT_EXECUTED_IN_THIS_SCRIPT",
            "model_forward": False, "I2": "NOT_EXECUTED"}


if __name__ == "__main__":
    report = check()
    print(json.dumps(report, sort_keys=True))
    sys.exit(0 if not report["failures"] else 2)
