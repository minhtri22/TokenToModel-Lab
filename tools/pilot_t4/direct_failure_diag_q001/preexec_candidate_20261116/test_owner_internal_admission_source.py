"""Windows Python 3.12 SOURCE-ONLY owner policy negative QA. No model files.

Run under Codex-controlled scoped project worktree; result is not independent
organisational signoff. The test uses a fake tokenizer digest for validator
schema QA only, and NEVER calls the actual runner/private data.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import platform
import sys
import tempfile
import unittest
from unittest import mock

import owner_internal_admission as owner

ROOT = Path(owner.ROOT)

def permit_payload(phase="run") -> dict:
    payload = {
        "question_id": owner.QUESTION_ID,
        "question_gate_main_sha": owner.Q1_MAIN,
        "project_root": owner.ROOT,
        "hostname": owner.HOST,
        "owner_decision": owner.OWNER_GO,
        "owner_research_scope": "LOCAL_INTERNAL_NONCOMMERCIAL_NO_REDISTRIBUTION",
        "owner_scope_document_git_blob": owner.OWNER_RECORD_BLOB,
        "owner_declaration_status": "OWNER_DECLARED_INTERNAL_SCOPE",
        "phase": phase,
        "checkpoint_sha256": owner.EXPECTED_CHECKPOINT_SHA256,
        "runner_sha256": "a"*64,
        "token_inventory_sha256": "b"*64,
        "underlying_inventory_sha256": "c"*64,
        "train_count": 24,
        "nontrain_count": 56,
        "seed": 20261116,
        "max_steps": 256,
        "expires_utc": (datetime.now(timezone.utc)+timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if phase == "run":
        payload["one_shot_nonce"] = "d"*64
        payload["frozen_fixture_sha256"] = "e"*64
    return payload

class OwnerInternalSourceQa(unittest.TestCase):
    def setUp(self):
        self.assertTrue(ROOT.is_dir(), "Only run within declared Windows project root")
        temp = ROOT / "_tmp"
        temp.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=str(temp), prefix="sm4m_owner_policy_test_")
        self.path = Path(self.tmp.name) / "fake_source_only_permit.json"
        self.doc_probe = owner._verify_owner_scope_record()
        self.kwargs = dict(phase="run",runner_sha256="a"*64,
            tokenizer_sha256="b"*64,underlying_sha256="c"*64,
            frozen_fixture_sha256="e"*64,project_root=ROOT)

    def tearDown(self):
        self.tmp.cleanup()

    def send(self, *, patch=None, package_patch=None):
        payload = permit_payload()
        if patch:
            payload.update(patch)
        package = {"mode":owner.MODE,"owner_scope_record":owner.OWNER_ISSUE_RECORD,"payload":payload}
        if package_patch:
            package.update(package_patch)
        self.path.write_text(json.dumps(package), encoding="utf-8")
        return owner.authenticate_owner_internal(self.path, **self.kwargs)

    def test_01_valid_scoped_schema_only(self):
        # Valid source-only schema: no checkpoint or tokenizer bytes accessed.
        result=self.send()
        self.assertEqual(result["owner_declaration_status"],"OWNER_DECLARED_INTERNAL_SCOPE")

    def test_02_wrong_question_denied(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(patch={"question_id":"OTHER"})

    def test_03_wrong_seed_denied(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(patch={"seed":20261117})

    def test_04_wrong_model_sha_denied(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(patch={"checkpoint_sha256":"0"*64})

    def test_05_wrong_runner_sha_denied(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(patch={"runner_sha256":"0"*64})

    def test_06_wrong_owner_record_denied(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(package_patch={"owner_scope_record":"local JSON permission"})

    def test_07_wrong_mode_denied(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(package_patch={"mode":"LEGACY_FAKE"})

    def test_08_extra_signature_field_denied(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(package_patch={"signatures":{"fake":"key"}})

    def test_09_bad_nonce_denied(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(patch={"one_shot_nonce":"NOT_A_HASH"})

    def test_10_false_fixture_hash_denied(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(patch={"frozen_fixture_sha256":"0"*64})

    def test_11_expired_denied(self):
        then=(datetime.now(timezone.utc)-timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self.assertRaises(owner.OwnerInternalHold):self.send(patch={"expires_utc":then})

    def test_12_owner_noncommercial_scope_denied_if_changed(self):
        with self.assertRaises(owner.OwnerInternalHold):self.send(patch={"owner_research_scope":"PUBLIC_RELEASE"})

    def test_13_absent_record_denied(self):
        with mock.patch.object(owner,"OWNER_RECORD_BLOB","0"*40):
            with self.assertRaises(owner.OwnerInternalHold):self.send()

    def test_14_foreign_host_denied(self):
        with mock.patch.object(platform,"node",return_value="OTHER"):
            with self.assertRaises(Exception):self.send()

if __name__=="__main__":
    if sys.version_info[:2]!=(3,12):
        raise SystemExit("HOLD_EXACT_PYTHON312")
    unittest.main(verbosity=2)
