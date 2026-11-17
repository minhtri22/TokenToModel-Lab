"""Source-only negative tests for lost-original-T4-session recovery.

No actual Colab GPU runs, private TinyStories or historical TEST.
Q4 decision is immutable; "recovery" must be a genuinely new TECH40 event.
"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

ROOT=Path(__file__).resolve().parents[2]
RECOVERY=ROOT/"src/ttm_new_gpt_baseline/tech40_fresh_recovery.py"
BRIDGE=ROOT/"src/ttm_new_gpt_baseline/tech40_continuation.py"
Q4=ROOT/"docs/architecture/TTM_PM_MISSING_TECH40_RECOVERY_Q4_DECISION_20261117.json"
spec=importlib.util.spec_from_file_location("lost_original_tech40_recovery_QA",RECOVERY)
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
specb=importlib.util.spec_from_file_location("lost_original_bridge_QA",BRIDGE)
b=importlib.util.module_from_spec(specb)
specb.loader.exec_module(b)

class RecoverySourceQA(unittest.TestCase):
    def test_exact_q4_source_git_blob_and_scoped_decision(self):
        sha=r.read_q4(Q4,b)
        self.assertEqual(len(sha),64)
        self.assertEqual(r.git_blob(Q4.read_bytes().replace(b"\r\n",b"\n")),r.Q4_BLOB)
        self.assertEqual(json.loads(Q4.read_text("utf8"))["decision"],r.EXPECTED_DECISION)

    def test_fake_q4_rejected_before_gpu(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"GO.json";p.write_text('{"decision":"GO"}')
            with self.assertRaisesRegex(ValueError,"EXACT_RECOVERY_Q4_GIT_BLOB_REQUIRED"):
                r.read_q4(p,b)

    def test_empty_ephemeral_parent_is_recovery_eligible(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)/"drive";base.mkdir()
            checked=r.guard_not_original_available(str(Path(d)/"missing_original"),str(base))
            self.assertEqual(checked,1)

    def test_existing_original_receipt_blocks_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            original=Path(d)/"TTM_MATCHED_4M_SESSIONS"
            receipt=original/"TTM_40_1024__example123"/"TECHNICAL_SYNTHETIC_40.json"
            receipt.parent.mkdir(parents=True)
            receipt.write_text('{"genuine":true}')
            drive=Path(d)/"drive";drive.mkdir()
            with self.assertRaisesRegex(ValueError,"USE_ORIGINAL_TECH40_BRIDGE_INSTEAD"):
                r.guard_not_original_available(original,drive)

    def test_drive_original_receipt_backup_blocks_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            drive=Path(d)/"owner";drive.mkdir()
            p=drive/"archive"/"TECHNICAL_SYNTHETIC_40.json"
            p.parent.mkdir();p.write_text("{}")
            with self.assertRaisesRegex(ValueError,"POSSIBLE_ORIGINAL_RECEIPT_BACKUP_USE_BRIDGE"):
                r.guard_not_original_available(Path(d)/"no_session",drive)

    def test_existing_fresh_recovery_does_not_block_resume(self):
        with tempfile.TemporaryDirectory() as d:
            drive=Path(d)/"owner";drive.mkdir()
            p=drive/"TTM_FRESH40_RECOVERY__newrun"/"TECHNICAL_SYNTHETIC_40.json"
            p.parent.mkdir();p.write_text("{}")
            self.assertGreaterEqual(
                r.guard_not_original_available(Path(d)/"absent",drive),1)

    def test_missing_owner_drive_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"OWNER_GOOGLE_DRIVE_ROOT_NOT_MOUNTED"):
                r.guard_not_original_available(Path(d)/"absent",Path(d)/"drive_missing")

    def test_run_id_validation(self):
        self.assertFalse(__import__("re").fullmatch(r.VALID_RUN_ID,"short"))
        self.assertTrue(__import__("re").fullmatch(r.VALID_RUN_ID,"ttm_recovery_20261117_01"))
        self.assertFalse(__import__("re").fullmatch(r.VALID_RUN_ID,"spaces in runid"))

    def test_tech40_is_explicitly_fresh_and_ordered_before_science(self):
        s=RECOVERY.read_text("utf-8")
        self.assertIn('"fresh_tech40":True',s)
        self.assertIn('"old_tech40_receipt_reused":False',s)
        self.assertIn("RECOVERY_SYNTHETIC40_FRESH_RUN_NOT_REUSE",s)
        self.assertLess(s.index("old.synthetic_40("),s.index("old.train("))
        self.assertLess(s.index("old.train("),s.index("old.compare("))

    def test_qa_from_historical_log_cannot_replace_actual_receipt(self):
        s=RECOVERY.read_text("utf8")
        self.assertNotIn("1a273db7f175578cdc9cf6a976d4679835a42d86a1c0c1604a6ea4e64596a1d9",s)
        self.assertIn('old.require_capacity(receipt,"replica_1024")',s)

    def test_once_only_lock_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"RECOVERY_Q4_LOCK.json"
            r.write_once(p,{"first":True})
            with self.assertRaises(FileExistsError):
                r.write_once(p,{"first":False})
            self.assertEqual(r.read_json(p),{"first":True})

    def test_immutable_p02_and_data_and_test_seal(self):
        decision=json.loads(Q4.read_text("utf8"))
        self.assertEqual(decision["original_main"],b.SOURCE_MAIN)
        self.assertEqual(decision["private_train_val_sha256"],b.DATA_SHA)
        self.assertEqual(decision["historical_left_1024_checkpoint_sha256"],b.HISTORICAL_CHECKPOINT_SHA)
        self.assertEqual(decision["recipe_sha256"],b.RECIPE_SHA)
        self.assertEqual(decision["test"],"SEALED_NO_ACCESS")

    def test_no_training_when_source_custody_preflight_fails(self):
        args=SimpleNamespace(old_runner="OLD",bridge="BRIDGE",new_runner="NEW",
                             q4="BAD",sources="SRC",data="NO_DATA",
                             manifest="NO_MANIFEST",historical_checkpoint="CP",
                             durable_parent="DRIVE",original_parent="NONE",
                             run_id="recovery_test_one",mode="onepack")
        with mock.patch.object(r,"load_bridge",side_effect=ValueError("BRIDGE_MISSING")):
            with self.assertRaisesRegex(ValueError,"BRIDGE_MISSING"):
                r.preflight(args)

    def test_runtime_mode_names_are_scoped(self):
        s=RECOVERY.read_text("utf8")
        self.assertIn('choices=["preflight","onepack","resume"]',s)
        self.assertIn('test_accessed":False',s)
        self.assertIn('RECOVERY_RESUME_EXPLICIT_READY_STEP_REQUIRED',s)

if __name__=="__main__":
    unittest.main()
