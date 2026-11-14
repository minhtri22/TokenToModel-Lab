#!/usr/bin/env python3
"""Read-only checks of the R8 V4 DESIGN contract; never loads/generates R8 data.

This checker does NOT implement O1-O8 inference. G0 independent static QA,
G1 source rights, G2 validator/custody and G3 generation remain unopened.
Compatible with Python 3.12 standard library.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_ORACLES = {f"O{i}" for i in range(1, 9)}
PRIMARY = ["O2", "O3", "O4", "O5", "O6"]
IDS = ("A", "B", "C", "D")


def check_contract(raw: bytes) -> dict:
    d = json.loads(raw.decode("utf-8"))
    reasons: list[str] = []

    def assert_true(condition: bool, message: str) -> None:
        if not condition:
            reasons.append(message)

    assert_true(d.get("design_only") is True, "design_only must be true")
    assert_true(d.get("owner_adopted") is False, "owner cannot be pre-attested")
    assert_true(d.get("r8_generated") is False, "R8 must not be generated")
    c = d["case_design"]
    assert_true((c["families"], c["pairs_per_family"], c["cases_per_pair"], c["cards_per_case"]) == (8,4,2,32), "8x4 pairs, two cases and 32 cards expected")
    assert_true((c["select_cases"], c["abstain_cases"]) == (32,32), "32/32 action balance expected")
    assert_true(set(d["oracles"]) == EXPECTED_ORACLES, "must register O1 through O8")
    assert_true(d["statistics"]["primary_families"] == PRIMARY, "O5 must be a primary testing family")
    assert_true(d["statistics"]["multiple_testing"] == "Holm", "Holm must be predeclared")
    assert_true(abs(d["statistics"]["familywise_alpha"] - 0.05) < 1e-12, "alpha 0.05 expected")
    assert_true(abs(d["statistics"]["first_rank_cutoff"] - 0.01) < 1e-12, "5 tests first Holm cutoff .01")
    assert_true(abs(d["statistics"]["key_null_select"] - 1/32) < 1e-12, "key null 1/32")
    o5 = d["oracles"]["O5"]
    assert_true(abs(o5["select_train_case_positive_weight"] + 31*o5["select_train_case_each_negative_weight"]-1) < 1e-12, "O5 case weights must sum to 1")
    r = d["raters"]
    assert_true(r["owner_decision"] == "PENDING", "rater option not owner-adopted")
    totals = {x: [0,0] for x in IDS}
    s, a = r["select_twin_raters_by_pair_slot"], r["abstain_twin_raters_by_pair_slot"]
    assert_true(len(s) == len(a) == 4, "4 pair slots required")
    if len(s) == len(a) == 4:
        for i, (ss, aa) in enumerate(zip(s,a)):
            assert_true(len(ss) == len(aa) == 2 and set(ss+aa) == set(IDS), f"pair {i} must use 4 raters without twin overlap")
            for x in ss:
                if x in totals: totals[x][0] += 1
            for x in aa:
                if x in totals: totals[x][1] += 1
    assert_true(all(v == [2,2] for v in totals.values()), "each rater 2 SELECT and 2 ABSTAIN per family")
    assert_true(r["evaluations_total"] == 128 and r["per_rater_cases"] == 32, "128 evaluations; 32 per rater")
    assert_true(d["folds"]["crossfold_post_edge"] == "FOLD_LEAK_CV_INVALID_NO_REPARTITION", "post-generation cross-fold edges must invalidate CV")
    assert_true(d["gates"]["G3"] == "NOT_AUTHORIZED", "G3 must remain blocked")
    return {
        "schema": "ttm.vm.v4.r8.v4.design_static_check.v1",
        "contract_sha256": hashlib.sha256(raw).hexdigest(),
        "design_checks": "PASS_SCOPED" if not reasons else "FAIL",
        "reasons": reasons,
        "tested_source": "DESIGN_CONTRACT_ONLY",
        "not_executed": ["R8_GENERATION","O1_O8_MODEL_RUNS","INDEPENDENT_QA","OWNER_RIGHTS","PRIVATE_CUSTODY"]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract", type=Path)
    ns = parser.parse_args()
    result = check_contract(ns.contract.read_bytes())
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["design_checks"] != "PASS_SCOPED":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
