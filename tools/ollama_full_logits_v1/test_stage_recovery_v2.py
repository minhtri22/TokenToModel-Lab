#!/usr/bin/env python3
"""Source-only QA: V2 path & C++ symbol correction, no native inference."""
import ast
from pathlib import Path
import unittest
BASE=Path(__file__).resolve().parent
PY=(BASE/"stage_and_build_ollama_full_logits_v2.py").read_text("utf-8")
PATCH=(BASE/"ttm_ollama_full_logits_b11963_hook_v2.patch").read_text("utf-8")
class V2OfflineTest(unittest.TestCase):
    def test_python_syntax(self):
        ast.parse(PY)
    def test_new_stage_under_tmp(self):
        self.assertIn('V2_STAGE = "_tmp/fl2"',PY)
        self.assertNotIn('stage=contained(root,root/"_tmp/ttm_ollama_full_logits_candidate_build_20261111"',PY)
    def test_failed_v1_preserved(self):
        self.assertIn("FROZEN_FAILED_V1_RECEIPT_SHA_CHANGED",PY)
        self.assertIn("V1_PARTIAL_LLAMA_DIR_EXISTS_DO_NOT_CLEAN",PY)
        self.assertNotIn("shutil.rmtree(",PY)
    def test_git_longpaths_scoped(self):
        self.assertIn('"core.longpaths=true"',PY)
    def test_cpp_vocab_symbol(self):
        self.assertIn("llama_model_get_vocab(llama_get_model(slot.ctx_tgt))",PATCH)
        self.assertNotIn("llama_vocab_n_tokens(vocab)",PATCH)
        self.assertIn("llama_get_logits_ith(slot.ctx_tgt, tok_idx)",PATCH)
    def test_no_inference(self):
        self.assertNotIn("ollama run",PY)
        self.assertNotIn("llama_decode(",PY)
        self.assertIn("OLLAMA_FULL_LOGITS_INFERENCE=NOT_EXECUTED",PY)
if __name__=="__main__":
    unittest.main(verbosity=2)
