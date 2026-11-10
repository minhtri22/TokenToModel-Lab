#!/usr/bin/env python3
"""No-model negative and static QA for frozen GELU_ERF C01-C04 protocol."""
from pathlib import Path
import ast,importlib.util,json,unittest

ROOT=Path(__file__).resolve().parent
FILE=ROOT/"independent_strict_c01c04_checker.py"
spec=importlib.util.spec_from_file_location("TTM_C01C04_Checker",FILE)
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def samples(origin):
    return [{"fixture_id":fid,"token_ids":list(ids),
             "logits":[float(j%13)/13 for j in range(2048)],
             **({"arm_id":"S1_F32_NO_FLASH","kv_type":"F32",
                 "flash":"DISABLED","flash_nodes_observed":0} if origin=="native"
                else {"source":"P02_F32_STEP1024_GELU_ERF"})}
            for fid,ids in c.FIX.items()]

class FrozenConfirmatory12(unittest.TestCase):
    def test_01_four_unique_heldout_fixtures(self):
        self.assertEqual(list(c.FIX),["C01","C02","C03","C04"])
        self.assertEqual([len(v) for v in c.FIX.values()],[2,4,11,17])
    def test_02_strict_threshold_unmodified(self):
        self.assertEqual(c.LIMIT,0.001)
    def test_03_native_exact_schema_accepts(self):
        self.assertEqual(set(c.checked(samples("native"),"native")),set(c.FIX))
    def test_04_reference_exact_schema_accepts(self):
        self.assertEqual(set(c.checked(samples("reference"),"reference")),set(c.FIX))
    def test_05_wrong_arm_rejected(self):
        rows=samples("native");rows[0]["kv_type"]="F16"
        with self.assertRaisesRegex(ValueError,"NATIVE_CONTEXT_NOT_F32_FLASH_OFF"):
            c.checked(rows,"native")
    def test_06_reused_fixture_rejected(self):
        rows=samples("native");rows[1]["fixture_id"]="C01"
        with self.assertRaisesRegex(ValueError,"FIXTURE_ID_TOKEN_OR_DUPLICATE"):
            c.checked(rows,"native")
    def test_07_wrong_token_rejected(self):
        rows=samples("native");rows[0]["token_ids"]=[1281]
        with self.assertRaisesRegex(ValueError,"FIXTURE_ID_TOKEN_OR_DUPLICATE"):
            c.checked(rows,"native")
    def test_08_missing_logit_rejected(self):
        rows=samples("native");rows[0]["logits"].pop()
        with self.assertRaisesRegex(ValueError,"LOGITS_NONFINITE_OR_WRONG_LENGTH"):
            c.checked(rows,"native")
    def test_09_invalid_number_rejected(self):
        rows=samples("native");rows[0]["logits"][2]=float("nan")
        with self.assertRaisesRegex(ValueError,"LOGITS_NONFINITE_OR_WRONG_LENGTH"):
            c.checked(rows,"native")
    def test_10_exact_four_lines(self):
        rows=samples("reference")
        raw=("\n".join(json.dumps(x) for x in rows)+"\n").encode()
        self.assertEqual(len(c.parse4(raw)),4)
        with self.assertRaisesRegex(ValueError,"EXACT_FOUR_JSONL"):
            c.parse4(raw[:-1])
    def test_11_candidate_source_cpp_limits(self):
        s=(ROOT/"ttm_t5_c01c04_gelu_erf_confirmatory_probe.cpp").read_text("utf-8")
        self.assertIn("rows!=4",s)
        self.assertIn("T5_GELU_ERF_CONFIRMATORY_COMPLETE_ROWS_4",s)
        self.assertIn("ffn_gelu_erf-0",s)
        self.assertNotIn('{"D01"',s)
        self.assertNotIn('{"SYN01"',s)
    def test_12_runner_does_not_replay_or_retrain(self):
        s=(ROOT/"run_c01c04_gelu_erf_confirmatory_once.py").read_text("utf-8")
        self.assertIn("CONFIRMATORY_ALREADY_STARTED_NO_REPEAT",s)
        self.assertNotIn("optimizer.step()",s)
        self.assertNotIn("llama_decode(",s)
        self.assertIn("GELU_ERF_DISCOVERY_GATE_NOT_MET",s)
        for p in ROOT.glob("*.py"):ast.parse(p.read_text("utf-8"),filename=str(p))

if __name__=="__main__":unittest.main(verbosity=2)
