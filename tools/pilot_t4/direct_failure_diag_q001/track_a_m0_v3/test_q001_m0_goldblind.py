#!/usr/bin/env python3
"""Adversarial stdlib mock tests for Track A M0 v3 (never model science)."""
import copy
import math
import unittest

from q001_m0_goldblind import (
    VOCAB, GROUPS, SEED, candidates_from_visible, digest, inventory,
    make_fixture, manifest, oracle, score_logits, split_audit,
    unique_top1, validate_fixture,
)


class M0AdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids = list(range(300, 500))
        cls.rows = make_fixture(cls.ids)

    def test_01_counts_unique_and_seed(self):
        self.assertEqual(len(self.rows), 80)
        self.assertEqual({g: sum(r["group"] == g for r in self.rows)
                          for g in GROUPS}, GROUPS)
        self.assertEqual(digest(self.rows), digest(make_fixture(self.ids)))
        self.assertNotEqual(digest(self.rows), digest(make_fixture(self.ids, SEED + 1)))

    def test_02_gold_never_used_for_candidate_construction(self):
        for r in self.rows:
            original = candidates_from_visible(
                r["context"], r["no_answer"], r["value_pool"])
            mutated = dict(r, gold=987)
            self.assertEqual(original, candidates_from_visible(
                mutated["context"], mutated["no_answer"], mutated["value_pool"]))
            self.assertEqual(original, r["choices"])
            self.assertIn(r["gold"], original)

    def test_03_constant_logits_must_abstain(self):
        z = [0.0] * VOCAB
        for r in self.rows:
            s = score_logits(z, r)
            self.assertTrue(s["candidate_tie_abstained"])
            self.assertTrue(s["full_vocab_tie_abstained"])
            self.assertFalse(s["candidate_only_top1_correct_secondary"])
            self.assertFalse(s["full_vocab_top1_correct"])
            self.assertAlmostEqual(s["full_vocab_gold_nll"], math.log(VOCAB))

    def test_04_candidate_order_permutation_invariance(self):
        for r in self.rows:
            options = r["choices"]
            scores = [(x, float(x)) for x in options]
            self.assertEqual(unique_top1(scores), unique_top1(scores[::-1]))
            self.assertIsNone(unique_top1([(x, 0.0) for x in options]))

    def test_05_gold_mutation_changes_metric_not_choices(self):
        r = self.rows[0]
        replacement = next(x for x in r["choices"] if x != r["gold"])
        logits = [-1.0] * VOCAB
        logits[r["gold"]] = 5.0
        altered = dict(r, gold=replacement)
        self.assertEqual(r["choices"], altered["choices"])
        self.assertTrue(score_logits(logits, r)["full_vocab_top1_correct"])
        self.assertFalse(score_logits(logits, altered)["full_vocab_top1_correct"])
        self.assertLess(score_logits(logits, r)["full_vocab_gold_nll"],
                        score_logits(logits, altered)["full_vocab_gold_nll"])

    def test_06_query_swap_reverses_oracle(self):
        r = next(r for r in self.rows if r["group"] == "TRAIN"
                 and r["gold"] != r["no_answer"])
        c = r["context"][:]
        c[7] = c[4] if c[7] == c[1] else c[1]
        self.assertNotEqual(r["gold"], oracle(c, r["no_answer"]))
        opts = candidates_from_visible(c, r["no_answer"], r["value_pool"])
        self.assertIn(oracle(c, r["no_answer"]), opts)

    def test_07_strict_holdout_binding_exclusion(self):
        rep = split_audit(self.rows)
        self.assertEqual(rep["train_binding_leaks_in_independent_holdouts"], [])
        self.assertEqual(rep["novel_role_id_collisions"], [])
        self.assertFalse(rep["counterfactual_independent_of_train"])
        self.assertEqual(rep["counterfactual_parent_linked_cases"], 16)

    def test_08_parent_linked_not_independent(self):
        parents = {r["id"]: r for r in self.rows if r["group"] == "TRAIN"}
        for r in self.rows:
            if r["group"] != "PAIRED_COUNTERFACTUAL":
                continue
            p = parents[r["parent"]]
            self.assertEqual(r["context"][7], p["context"][7])
            self.assertEqual(r["context"][2], p["context"][5])
            self.assertEqual(r["context"][5], p["context"][2])
            self.assertNotEqual(r["gold"], p["gold"])

    def test_09_forged_gold_rejected(self):
        changed = copy.deepcopy(self.rows)
        changed[0]["gold"] = 777
        with self.assertRaisesRegex(ValueError, "BAD_GOLD"):
            validate_fixture(changed)

    def test_10_forged_choices_rejected(self):
        changed = copy.deepcopy(self.rows)
        changed[0]["choices"] = changed[0]["choices"][::-1]
        with self.assertRaisesRegex(ValueError, "LABEL_LEAK_OR_CHOICES"):
            validate_fixture(changed)

    def test_11_binding_leak_rejected(self):
        changed = copy.deepcopy(self.rows)
        train = next(r for r in changed if r["group"] == "TRAIN")
        held = next(r for r in changed if r["group"] == "HELDOUT_RECOMBINED")
        held["context"][1:3] = train["context"][1:3]
        held["gold"] = oracle(held["context"], held["no_answer"])
        held["choices"] = candidates_from_visible(
            held["context"], held["no_answer"], held["value_pool"])
        with self.assertRaises(ValueError):
            validate_fixture(changed)

    def test_12_invalid_inventory_and_logits(self):
        with self.assertRaises(ValueError):
            inventory(list(range(100, 179)))  # only 79 IDs
        with self.assertRaises(ValueError):
            inventory(list(range(200, 300)))  # contains EOS 256
        with self.assertRaises(ValueError):
            score_logits([0.0] * (VOCAB - 1), self.rows[0])
        with self.assertRaises(ValueError):
            score_logits([math.nan] * VOCAB, self.rows[0])

    def test_13_versioned_mock_manifest(self):
        m = manifest(self.rows)
        self.assertTrue(m["mock_only"])
        self.assertFalse(m["model_forward"])
        self.assertEqual(m["I2"], "NOT_EXECUTED")
        self.assertEqual(len(m["case_sha256"]), 80)
        self.assertEqual(len(m["group_sha256"]), 5)
        self.assertEqual(m["fixture_sha256"], digest(self.rows))

    def test_14_blind_fixed_logits_are_not_evidence_of_binding(self):
        blind = [float(-x) for x in range(VOCAB)]
        counts = {g: sum(score_logits(blind, r)[
            "candidate_only_top1_correct_secondary"] for r in self.rows
            if r["group"] == g) for g in GROUPS}
        self.assertEqual(sum(counts.values()), sum(
            score_logits(blind, r)["candidate_only_top1_correct_secondary"]
            for r in self.rows))
        self.assertEqual(sum(score_logits(blind, r)[
            "full_vocab_top1_correct"] for r in self.rows), 0)


    def test_15_candidate_only_cannot_replace_full_vocab(self):
        r = next(r for r in self.rows if r["group"] == "TRAIN"
                 and r["gold"] != r["no_answer"])
        logits = [0.0] * VOCAB
        logits[r["gold"]] = 4.0
        logits[0] = 9.0  # outside the public MOCK allowed-ID pool
        s = score_logits(logits, r)
        self.assertTrue(s["candidate_only_top1_correct_secondary"])
        self.assertFalse(s["full_vocab_top1_correct"])
        self.assertEqual(s["full_vocab_gold_rank"], 2)

    def test_16_unseen_random_candidate_pool_does_not_inject_gold(self):
        for r in self.rows:
            varied = copy.deepcopy(r)
            varied["value_pool"] = list(range(900, 940))
            varied["choices"] = candidates_from_visible(
                varied["context"], varied["no_answer"], varied["value_pool"])
            self.assertEqual(len(set(varied["choices"])), 4)
            self.assertIn(r["gold"], varied["choices"])
            self.assertEqual(varied["choices"], candidates_from_visible(
                varied["context"], varied["no_answer"], varied["value_pool"]))
            self.assertTrue(score_logits([0.0] * VOCAB, varied)[
                "candidate_tie_abstained"])


    def test_17_large_uniform_logits_stable_nll(self):
        # A reviewer found the former m + log_sum - gold collapsed to zero.
        for value in (0.0, 1e20, -1e20, 1e100, -1e100):
            z = [value] * VOCAB
            for row in self.rows:
                s = score_logits(z, row)
                self.assertAlmostEqual(s["full_vocab_gold_nll"],
                                       math.log(VOCAB), places=10)
                self.assertTrue(s["full_vocab_tie_abstained"])
                self.assertTrue(s["candidate_tie_abstained"])

    def test_18_large_shift_does_not_change_nll(self):
        row = self.rows[0]
        # Choose differences larger than the ULP near 1e20.
        base = [float(-65536*i) for i in range(VOCAB)]
        shifted = [1e20 + x for x in base]
        a = score_logits(base, row)
        b = score_logits(shifted, row)
        self.assertAlmostEqual(a["full_vocab_gold_nll"],
                               b["full_vocab_gold_nll"], delta=65536)
        # Exact flat logit-shift invariance is tested separately above.



if __name__ == "__main__":
    unittest.main(verbosity=2)
