#!/usr/bin/env python3
"""Independent synthetic-only negative and positive contract tests.

Never reads checkpoint, GGUF, TEST, original eight native fixtures or invokes
llama.cpp. Tests audit_new_native_results.evaluate against mock values.
"""
import copy
import json
from pathlib import Path
import unittest

from audit_new_native_results import evaluate, EXPECTED_ARMS

ROOT=Path(__file__).resolve().parents[3]
PLAN=ROOT/"artifacts/qa/ttm-t5-parity/TTM_T5_KV_FLASH_2X2_FRESH_SYNTHETIC_PREREG_20261109.json"
OLD_FROZEN=[
    [97],[97,98,99],[1,2,3,4,5],[256,97,98,99],
    [100,200,300,400,500,600,700,800],
    list(range(1,17)),[48,49,10,65,32,66,256],list(range(1,33))
]

def synthetic_material(plan):
    reference=[]
    native=[]
    for f in plan["control_design"]["new_fixtures"]:
        fid=f["fixture_id"]
        ids=f["ids"]
        values=[0.0001*i for i in range(2048)]
        reference.append({"fixture_id":fid,"token_ids":ids,"logits":values})
        for arm,(kv,flash) in EXPECTED_ARMS.items():
            native.append({"fixture_id":fid,"arm_id":arm,"token_ids":ids,
                           "kv_type":kv,"flash":flash,
                           "flash_nodes_observed":4 if flash=="ENABLED" else 0,
                           "logits":values.copy()})
    return reference,native

class ContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads(PLAN.read_text(encoding="utf-8"))
    def setUp(self):
        self.reference,self.native=synthetic_material(self.plan)
    def test_frozen_2x2_design(self):
        self.assertEqual(len(self.plan["control_design"]["new_fixtures"]),8)
        self.assertEqual(len(self.plan["control_design"]["arms"]),4)
        self.assertEqual(self.plan["original_pins"]["final_logits_acceptance_max_abs"],0.001)
        self.assertEqual(self.plan["control_design"]["expected_runs"],32)
    def test_new_fixtures_disjoint_from_old_exact_arrays(self):
        v=[x["ids"] for x in self.plan["control_design"]["new_fixtures"]]
        self.assertEqual(len(v),len({tuple(z) for z in v}))
        for ids in v:
            self.assertNotIn(ids,OLD_FROZEN)
            self.assertTrue(all(257<=z<2048 for z in ids))
    def test_32_positive(self):
        out=evaluate(self.plan,self.reference,self.native)
        self.assertEqual(len(out["rows"]),32)
        self.assertEqual(out["arm_strict_pass_counts"],{k:8 for k in EXPECTED_ARMS})
        self.assertEqual(out["frozen_historical_strict_failures"],7)
    def test_missing_arm(self):
        with self.assertRaises(ValueError):
            evaluate(self.plan,self.reference,self.native[:-1])
    def test_duplicate_arm(self):
        rows=self.native.copy();rows[0]=rows[1]
        with self.assertRaises(ValueError):
            evaluate(self.plan,self.reference,rows)
    def test_changed_KV_type(self):
        rows=copy.deepcopy(self.native);rows[0]["kv_type"]="F32"
        with self.assertRaises(ValueError):
            evaluate(self.plan,self.reference,rows)
    def test_flash_path_forged(self):
        rows=copy.deepcopy(self.native);rows[0]["flash_nodes_observed"]=0
        with self.assertRaises(ValueError):
            evaluate(self.plan,self.reference,rows)
    def test_wrong_fixture_ids(self):
        rows=copy.deepcopy(self.native);rows[0]["token_ids"]=[999]
        with self.assertRaises(ValueError):
            evaluate(self.plan,self.reference,rows)
    def test_reference_mismatch(self):
        rows=copy.deepcopy(self.reference);rows[0]["fixture_id"]="SYN02"
        with self.assertRaises(ValueError):
            evaluate(self.plan,rows,self.native)
    def test_nonfinite(self):
        rows=copy.deepcopy(self.native);rows[0]["logits"][0]=float("nan")
        with self.assertRaises(ValueError):
            evaluate(self.plan,self.reference,rows)
    def test_wrong_vocab(self):
        rows=copy.deepcopy(self.native);rows[0]["logits"]=rows[0]["logits"][:-1]
        with self.assertRaises(ValueError):
            evaluate(self.plan,self.reference,rows)
    def test_threshold_not_relaxed(self):
        p=copy.deepcopy(self.plan);p["original_pins"]["final_logits_acceptance_max_abs"]=0.01
        with self.assertRaises(ValueError):
            evaluate(p,self.reference,self.native)
    def test_no_old_test_in_plan(self):
        self.assertTrue(self.plan["governance"]["old_eight_immutable"])
        self.assertFalse(self.plan["governance"]["new_native_execution"])
        self.assertFalse(self.plan["governance"]["new_training"])
        self.assertTrue(self.plan["governance"]["test_untouched"])

if __name__=="__main__":
    unittest.main(verbosity=2)
