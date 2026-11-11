#!/usr/bin/env python3
"""Offline design QA, no private BPE load or model forward."""
import importlib.util,json,tempfile,unittest,ast
from pathlib import Path
HERE=Path(__file__).resolve().parent
SCRIPT=HERE/"ttm_fresh16_integrated_offline_review.py"
SOURCE=SCRIPT.read_text("utf-8")
SP=importlib.util.spec_from_file_location("ttm_fresh16_qa",SCRIPT)
M=importlib.util.module_from_spec(SP);SP.loader.exec_module(M)
ROOT=HERE.parents[2]
PROMPTS=json.loads((ROOT/M.PROMPTS).read_text("utf-8"))
HISTORY=json.loads((ROOT/M.HISTORY).read_text("utf-8"))
RUBRIC=json.loads((ROOT/M.RUBRIC).read_text("utf-8"))
class StaticReviewQA(unittest.TestCase):
    def test_syntax(self):ast.parse(SOURCE)
    def test_counts_and_sources(self):
        r=M.assess_public(PROMPTS,HISTORY,RUBRIC)
        self.assertEqual((r["prompt_count"],r["historical_count"],r["exact_collisions"]),(16,28,0))
    def test_historical_header_uses_name_not_source(self):
        self.assertEqual({item["name"]:item["git_blob_sha"] for item in HISTORY["sources"]},
                         M.EXPECTED_HIST_BLOBS)
        self.assertTrue(all("source" not in item for item in HISTORY["sources"]))
        self.assertEqual(M.assess_public(PROMPTS,HISTORY,RUBRIC)["status"],
                         "PASS_PUBLIC_FROZEN_SOURCE")
    def test_historical_source_name_tamper_detected(self):
        altered=json.loads(json.dumps(HISTORY))
        altered["sources"][0]["name"]="UNEXPECTED_PUBLIC_SOURCE"
        with self.assertRaisesRegex(ValueError,"HIST_SOURCE_PIN_CHANGED"):
            M.assess_public(PROMPTS,altered,RUBRIC)
    def test_near_duplicate_boundary(self):
        a=M.gramset("red cat sleeps on the mat",3)
        self.assertEqual(M.jaccard(a,a),1.)
    def test_change_required_by_both_pairs(self):
        x=json.loads(json.dumps(PROMPTS));x["new_prompts"][1]["prompt_text"]=x["new_prompts"][0]["prompt_text"]
        with self.assertRaisesRegex(ValueError,"PROMPT_TEXT_DUPLICATE"):
            M.assess_public(x,HISTORY,RUBRIC)
    def test_negative_trailing_space(self):
        x=json.loads(json.dumps(PROMPTS));x["new_prompts"][0]["prompt_text"]+=" "
        with self.assertRaisesRegex(ValueError,"PROMPT_SERIALIZATION_CHANGED"):
            M.assess_public(x,HISTORY,RUBRIC)
    def test_threshold_tampering_rejected(self):
        x=json.loads(json.dumps(RUBRIC));x["fixture_contract"]["primary"]["H2"]["required_min"]=1
        with self.assertRaisesRegex(ValueError,"H1_H2_PREREG_CHANGED"):
            M.assess_public(PROMPTS,HISTORY,x)
    def test_repeated_intervention_word_uses_last_occurrence(self):
        pair=next(x for x in PROMPTS["new_prompts"] if x["id"]=="CP05-A")
        self.assertEqual(pair["prompt_text"].lower().count("red"),2)
        self.assertEqual(M.assess_public(PROMPTS,HISTORY,RUBRIC)["status"],
                         "PASS_PUBLIC_FROZEN_SOURCE")
    def test_checkpoint_missing_holds(self):
        self.assertEqual(M.check_ckpt(Path("/tmp"),None,"1024")["status"],
                         "HOLD_CHECKPOINT_NOT_SUPPLIED")
    def test_no_runner_or_test_data_access(self):
        self.assertNotIn("import torch",SOURCE)
        self.assertNotIn("shutil.rmtree",SOURCE)
        self.assertNotIn("HTTPConnection",SOURCE)
        self.assertNotIn("TEST_64",SOURCE)
        self.assertIn('reviewer_custody',SOURCE)
if __name__=="__main__":unittest.main(verbosity=2)
