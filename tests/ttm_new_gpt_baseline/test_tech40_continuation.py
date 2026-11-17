"""Distinct negative QA for TECH40 byte-custody -> Q4 -> TinyStories1024.

No Torch, GPU, Drive secret, training or historical TEST. Original runner
source is read from an immutable public GitHub commit and SHA-1 verified.
Tests authored in same workflow, not independent human/organizational QA.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "src/ttm_new_gpt_baseline/tech40_continuation.py"
RUNNER = ROOT / "src/ttm_new_gpt_baseline/runner.py"
Q4 = ROOT / "docs/architecture/TTM_PM_Q4_TECH40_REUSE_1024_VAL_ONLY_DECISION_20261117.json"
spec = importlib.util.spec_from_file_location("tech40_bridge_test_under_review", SCRIPT)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class DistinctTech40BridgeQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        url = ("https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/"
               "2b8a3613dea0daa5babf6f85fc7ea4ec093d4135/"
               "src/ttm_new_gpt_baseline/runner.py")
        with urllib.request.urlopen(url, timeout=35) as res:
            cls.old_bytes = res.read(170000)
        if b.git_blob(cls.old_bytes) != b.OLD_RUNNER_BLOB:
            raise AssertionError("ORIGINAL_PUBLIC_COMMIT_BLOB_DRIFT")

    def test_q4_exact_source_blob_and_conditional_go(self):
        a = b.q4_readback(Q4)
        self.assertEqual(a["q4_git_blob"], b.Q4_DECISION_BLOB)
        self.assertEqual(a["decision"], b.GO_DECISION)
        self.assertEqual(len(a["q4_sha256"]), 64)

    def test_current_runner_exact_source_blob(self):
        self.assertEqual(b.git_blob(RUNNER.read_bytes().replace(b"\r\n", b"\n")), b.NEW_RUNNER_BLOB)

    def test_source_critical_functions_identical_old_new(self):
        with tempfile.TemporaryDirectory() as folder:
            previous = Path(folder) / "old_runner.py"
            previous.write_bytes(self.old_bytes)
            out = b.source_equivalence(previous, RUNNER)
            self.assertEqual(out["old_runner_blob"], b.OLD_RUNNER_BLOB)
            self.assertEqual(out["new_runner_blob"], b.NEW_RUNNER_BLOB)
            self.assertIn("train", out["science_functions_identical_exact_bytes"])
            self.assertIn("compare", out["science_functions_identical_exact_bytes"])
            self.assertIn("synthetic_40", out["science_functions_identical_exact_bytes"])

    def test_mutated_old_runner_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            previous = Path(folder) / "old_runner.py"
            previous.write_bytes(self.old_bytes + b"\n#unauthorized")
            with self.assertRaisesRegex(ValueError, "EXACT_GIT_BLOB_MISMATCH"):
                b.source_equivalence(previous, RUNNER)

    def test_mutated_new_runner_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            old = Path(folder)/"old.py"
            new = Path(folder)/"new.py"
            old.write_bytes(self.old_bytes)
            new.write_bytes(RUNNER.read_bytes()+b"\n#unreviewed")
            with self.assertRaisesRegex(ValueError, "EXACT_GIT_BLOB_MISMATCH"):
                b.source_equivalence(old, new)

    def test_unknown_q4_file_content_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/"go.json"
            p.write_text('{"decision":"GO"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Q4_GITHUB_GIT_BLOB_DRIFT"):
                b.q4_readback(p)

    def test_no_recovered_receipt_from_console_only(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)/"TTM_40_1024__from_console"
            root.mkdir()
            (root/"TECHNICAL_SYNTHETIC_40.json").write_text(
                '{"status":"PASS_FULL_P02_SYNTHETIC_40_SCOPED"}')
            with self.assertRaisesRegex(ValueError, "MISSING_OR_SYMLINK_FILE"):
                b.original_receipt_readback(root, None)

    def test_fake_old_session_cannot_claim_exact_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)/"TTM_40_1024__fake_stage40"
            root.mkdir()
            for s in ("TECHNICAL_SYNTHETIC_40.json", "SESSION_LOCK.json", "SESSION_STATUS.json"):
                (root/s).write_text("{}")
            with self.assertRaisesRegex(ValueError,"HOLD_RECEIPT_RAW_BYTES_NOT_EQUAL"):
                b.original_receipt_readback(root, None)

    def test_stage40_multiple_candidates_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            for i in (1,2):
                d=Path(folder)/("TTM_40_1024__candidate%d"%i)
                d.mkdir()
                (d/"TECHNICAL_SYNTHETIC_40.json").write_text("{}")
            with self.assertRaisesRegex(ValueError,"NOT_UNIQUE"):
                b.find_original(folder)

    def test_stage40_missing_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,"NOT_UNIQUE_OR_MISSING"):
                b.find_original(folder)

    def test_claim_write_once_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"PM_TECH40_CONTINUATION_ONCE_CLAIM.json"
            b.write_once(p,{"mode":"Q4"})
            with self.assertRaisesRegex(FileExistsError,"ONE_SHOT_OUTPUT_EXISTS"):
                b.write_once(p,{"mode":"Q4_OVERRIDE"})
            self.assertEqual(json.loads(p.read_bytes()),{"mode":"Q4"})

    def test_bridge_never_runs_synthetic_40(self):
        s=SCRIPT.read_text("utf-8")
        self.assertNotIn(".synthetic_40(",s)
        self.assertNotIn("mode == \"synthetic-40\"",s)
        self.assertIn('old.train(trainargs, verified_integrated=authorized)',s)
        self.assertIn('old.compare(compareargs, verified_integrated=authorized)',s)
        self.assertIn('if not (target / "FINAL.json").exists():',s)

    def test_target_separate_from_origin_and_reproducibility_only(self):
        s=SCRIPT.read_text("utf-8")
        self.assertIn('"adopt_" + original_run_id',s)
        self.assertIn('"DURABLE_OUTPUT_MUST_BE_IN_OWNER_MOUNTED_TTM_DRIVE"',s)
        self.assertIn('"REPLICATION_VAL_ONLY_NO_NEW_MODEL_CLAIM"',s)
        self.assertIn('HISTORICAL_CHECKPOINT_SHA',s)

    def test_sha_from_console_is_candidate_not_byte_verified(self):
        self.assertEqual(
            b.TECH40_SHA_FROM_USER_STDOUT,
            "1a273db7f175578cdc9cf6a976d4679835a42d86a1c0c1604a6ea4e64596a1d9")
        q4 = json.loads(Q4.read_text("utf-8"))
        self.assertIn("NOT_YET_RAW_FILE_VERIFIED",q4["receipt_sha_evidence_level"])

if __name__ == "__main__":
    unittest.main()
