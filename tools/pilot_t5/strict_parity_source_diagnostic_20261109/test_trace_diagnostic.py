#!/usr/bin/env python3
"""Synthetic-only offline unit tests, not a rerun of the native parity experiment."""
import unittest
from diagnose_existing_trace import diagnose, TraceError, CHECKPOINT, GGUF, LLAMA, LIMIT, SENSITIVITY

NAMES = ["inpL","attn_norm-0","wqkv_b-0","ffn_inp-0"] + [f"stage-{i:02d}" for i in range(30)] + ["result_output"]
assert len(NAMES) == 35

def mock_frozen_trace():
    rows=[]
    for i in range(8):
        vals=[0.0,1e-8,1e-7,0.00008]+[0.0001]*30+[0.0008 if i==0 else 0.0011+i*0.0001]
        rows.append({"fixture_index":i,"n_ids":i+1,
          "stages":[{"stage":n,"max_abs":v} for n,v in zip(NAMES,vals)],
          "final_max_abs":vals[-1],
          "first_over_1e5":"ffn_inp-0",
          "first_over_0_001":None if i==0 else "result_output"})
    return {"schema":"ttm.t5.f32.numeric.localization.single.v1",
      "checkpoint_sha256":CHECKPOINT,"gguf_sha256":GGUF,
      "llama_source_commit":LLAMA,"fixed_absolute_logit_threshold":LIMIT,
      "non_acceptance_local_sensitivity":SENSITIVITY,
      "test_read":False,"train_steps":0,"rows":rows}

class TraceTests(unittest.TestCase):
    def test_positive(self):
        r=diagnose(mock_frozen_trace())
        self.assertEqual(r["strict_failures"],7)
        self.assertTrue(r["historical_7_of_8_fail_preserved"])
    def test_threshold_tamper(self):
        r=mock_frozen_trace();r["fixed_absolute_logit_threshold"]=0.01
        with self.assertRaises(TraceError):diagnose(r)
    def test_wrong_backend(self):
        r=mock_frozen_trace();r["llama_source_commit"]="0"*40
        with self.assertRaises(TraceError):diagnose(r)
    def test_missing_stage(self):
        r=mock_frozen_trace();r["rows"][1]["stages"].pop(5)
        with self.assertRaises(TraceError):diagnose(r)
    def test_changed_fixture_count(self):
        r=mock_frozen_trace();r["rows"].pop()
        with self.assertRaises(TraceError):diagnose(r)
    def test_changed_fixture_order(self):
        r=mock_frozen_trace();r["rows"][3]["fixture_index"]=5
        with self.assertRaises(TraceError):diagnose(r)
    def test_stage_crossing_corruption(self):
        r=mock_frozen_trace();r["rows"][0]["stages"][1]["max_abs"]=0.0005
        with self.assertRaises(TraceError):diagnose(r)
    def test_outcome_tamper(self):
        r=mock_frozen_trace();r["rows"][1]["stages"][-1]["max_abs"]=0.0009
        r["rows"][1]["final_max_abs"]=0.0009
        r["rows"][1]["first_over_0_001"]=None
        with self.assertRaises(TraceError):diagnose(r)
    def test_test_access_flag(self):
        r=mock_frozen_trace();r["test_read"]=True
        with self.assertRaises(TraceError):diagnose(r)

if __name__=="__main__":
    unittest.main()
