#!/usr/bin/env python3
"""Offline structural QA for the frozen FL01..FL04 reference producer."""
from __future__ import annotations
import ast
import json
import sys
from pathlib import Path
import unittest
from verify_fl01_fl04_p02_reference import FIX, P02, PREREG, CKPT, checked_rows

class FrozenReferenceTests(unittest.TestCase):
    def setUp(self):
        self.rows = []
        for fid, ids in FIX.items():
            self.rows.append({
                "fixture_id": fid, "token_ids": list(ids),
                "source": "P02_F32_STEP1024_GELU_ERF",
                "checkpoint_sha256": CKPT,
                "p02_git_blob": P02,
                "prereg_git_blob": PREREG,
                "logits": [0.0]*2048,
            })
    def raw(self):
        return "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in self.rows)
    def test_valid_four_2048(self):
        self.assertEqual(len(checked_rows(self.raw())),4)
    def test_missing_final_newline(self):
        with self.assertRaisesRegex(ValueError,"EXACT_4"):checked_rows(self.raw().rstrip("\n"))
    def test_wrong_fixture(self):
        self.rows[0]["token_ids"][0] = -1
        with self.assertRaisesRegex(ValueError,"MISMATCH"):checked_rows(self.raw())
    def test_bad_reference_source(self):
        self.rows[1]["source"] = "synthetic"
        with self.assertRaisesRegex(ValueError,"MISMATCH"):checked_rows(self.raw())
    def test_nonfinite(self):
        self.rows[2]["logits"][2] = float("nan")
        with self.assertRaisesRegex(ValueError,"NONFINITE"):checked_rows(self.raw())
    def test_2047_rejected(self):
        self.rows[3]["logits"].pop()
        with self.assertRaisesRegex(ValueError,"NONFINITE"):checked_rows(self.raw())
    def test_ast_all_python_files(self):
        for f in Path(__file__).parent.glob("*.py"):
            ast.parse(f.read_text("utf-8"), filename=str(f))

if __name__ == "__main__":
    unittest.main(verbosity=2)
