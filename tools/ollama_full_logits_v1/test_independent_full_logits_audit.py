#!/usr/bin/env python3
"""No model, disk write or network; deterministic negative tests for numeric checker."""
import unittest
from independent_full_logits_audit import FIXTURES, N, LIMIT, compare

class NumericalQATest(unittest.TestCase):
    def setUp(self):
        self.ref = {k: [0.0]*N for k in FIXTURES}
        self.candidate = {k: [0.0]*N for k in FIXTURES}
        for v in self.ref.values(): v[123] = 2.0
        for v in self.candidate.values(): v[123] = 2.0

    def test_identical(self):
        self.assertEqual(sum(x["strict_pass"] for x in compare(self.ref,self.candidate)),4)
    def test_threshold_equal_pass(self):
        self.candidate["FL01"][2]=LIMIT
        self.assertTrue(compare(self.ref,self.candidate)[0]["strict_pass"])
    def test_threshold_exceeded_fail(self):
        self.candidate["FL01"][2]=LIMIT+1e-5
        self.assertFalse(compare(self.ref,self.candidate)[0]["strict_pass"])
    def test_top1_mismatch_fail(self):
        self.candidate["FL04"][124]=3.0
        self.assertFalse(compare(self.ref,self.candidate)[3]["top1_equal"])
    def test_signed_difference(self):
        self.candidate["FL02"][2]=-0.0004
        r=compare(self.ref,self.candidate)[1]
        self.assertEqual(r["peak_index"],2)
        self.assertAlmostEqual(r["signed_peak_ollama_minus_p02"],-0.0004)

if __name__=="__main__":
    unittest.main(verbosity=2)
