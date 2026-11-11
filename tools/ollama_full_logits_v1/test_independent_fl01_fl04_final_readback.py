#!/usr/bin/env python3
"""Unit QA for read-only independent full-logits numeric/provenance adjudicator."""
import ast,importlib.util,json,tempfile,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parent
PATH=BASE/"independent_fl01_fl04_final_readback.py"
SOURCE=PATH.read_text("utf-8")
spec=importlib.util.spec_from_file_location("ttm_end_to_end_verifier",PATH)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ScienceVerifierQA(unittest.TestCase):
    def test_ast(self):ast.parse(SOURCE)
    def test_frozen_tokens(self):
        self.assertEqual([len(x) for x in m.FIXTURES.values()],[3,3,3,6])
    def test_frozen_result_sha(self):
        self.assertEqual(m.RUN_SHA,"18f2fea2d986449eda098a949103e9614ab3c8a1a2368a3647c0c7729dbda269")
    def test_comparison_identical(self):
        a=[{"fixture_id":fid,"logits":[0.0]*2048} for fid in m.FIXTURES]
        rows=m.comparison(a,a)
        self.assertTrue(all(x["strict_pass"] and x["max_abs"]==0 for x in rows))
    def test_comparison_detects_fail(self):
        a=[{"fixture_id":fid,"logits":[0.0]*2048} for fid in m.FIXTURES]
        b=[{"fixture_id":fid,"logits":[0.0]*2048} for fid in m.FIXTURES]
        b[1]["logits"][34]=0.005
        self.assertFalse(m.comparison(a,b)[1]["strict_pass"])
    def test_invalid_token_vector(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"fake"
            row={"fixture_id":"FL01","token_ids":[1],"source":"P02_F32_STEP1024_GELU_ERF","logits":[0.0]*2048}
            path.write_text(json.dumps(row)+"\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"EXACT_FOUR"):
                m.read_vectors(path,"reference")
    def test_no_inference_import(self):
        self.assertNotIn("import torch",SOURCE)
        self.assertNotIn("HTTPConnection",SOURCE)
        self.assertNotIn("Popen(",SOURCE)
        self.assertNotIn("rmtree(",SOURCE)
    def test_output_exclusive_and_no_lineage_write(self):
        self.assertIn('destination.open("x"',SOURCE)
        self.assertIn('"lineage_write":False',SOURCE)
if __name__=="__main__":unittest.main(verbosity=2)
