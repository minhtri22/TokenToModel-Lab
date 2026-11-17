"""Separate numerical oracle QA for the paired VAL bootstrap.
No TinyStories bytes, checkpoints, TEST or model inference. Requires NumPy.
Author-implemented checker; organizational independent QA not claimed.
"""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "src/ttm_new_gpt_baseline/runner.py"
spec = importlib.util.spec_from_file_location("ttm_matched_paired_qa", p)
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)

class PairedStoryQA(unittest.TestCase):
    def test_equal_losses_zero_gain(self):
        obj = r.paired_bootstrap([2.0]*256, [2.0]*256, [2]*256)
        self.assertEqual(obj["left_minus_right_nll"], 0.)
        self.assertEqual(obj["paired_95pct_ci"], [0., 0.])
        self.assertEqual(obj["target_count"], 512)
    def test_uniform_gain(self):
        obj = r.paired_bootstrap([3.0]*256, [1.0]*256, [2]*256)
        self.assertEqual(obj["left_minus_right_nll"], 1.)
        self.assertEqual(obj["paired_95pct_ci"], [1., 1.])
        self.assertEqual(obj["left_nll"], 1.5)
        self.assertEqual(obj["right_nll"], .5)
    def test_reverse_sign(self):
        obj = r.paired_bootstrap([1.0]*256, [3.0]*256, [2]*256)
        self.assertEqual(obj["left_minus_right_nll"], -1.)
    def test_refuse_wrong_story_number(self):
        with self.assertRaisesRegex(ValueError, "PAIRED_STORY_INPUT_INVALID"):
            r.paired_bootstrap([1.]*255, [1.]*255, [2]*255)
    def test_refuse_zero_counts(self):
        with self.assertRaises(ValueError):
            r.paired_bootstrap([1.]*256, [1.]*256, [0]*256)
    def test_refuse_nans(self):
        with self.assertRaises(ValueError):
            r.paired_bootstrap([float("nan")]*256, [1.]*256, [2]*256)
    def test_deterministic_bootstrap(self):
        a = [1.0 + i*.001 for i in range(256)]
        b = [1.0 - i*.001 for i in range(256)]
        self.assertEqual(r.paired_bootstrap(a,b,[2]*256,seed=17,reps=100),
                         r.paired_bootstrap(a,b,[2]*256,seed=17,reps=100))
    def test_no_2048_vs_1024_fairness(self):
        self.assertEqual(r.plan_of("replica_1024")["steps"], 1024)
        self.assertEqual(r.plan_of("replica_2048")["steps"], 2048)
        self.assertNotEqual(r.recipe_hash("replica_1024"),r.recipe_hash("replica_2048"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
