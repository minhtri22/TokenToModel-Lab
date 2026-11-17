"""No-model regression probes for owner-internal I1 admission on Windows."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import owner_internal_admission as owner
import release_auth_v2
import ttm_sm4m_diag_q001 as runner


class OwnerInternalQA(unittest.TestCase):
    root = Path(release_auth_v2.TRUSTED_PROJECT_ROOT)

    def setUp(self):
        self.runtime = {"runner": "a" * 64}
        self.digest = "b" * 64
        self.verdict = {
            "I1": "I1_PASS_SCOPED_INTERNAL_RESEARCH",
            "scope": deepcopy(owner.SCOPE),
            "runtime_sha256": dict(self.runtime),
            "expires_utc": (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "fixture_sha256": self.digest,
        }

    def test_reviewed_verdict_schema(self):
        self.assertEqual(owner.validate_verdict(self.verdict, runtime_sha256=self.runtime), self.digest)

    def test_scope_mutations(self):
        for field in ("question_gate_main_sha", "question_id", "project_root", "hostname",
                      "seed", "steps", "owner_decision", "owner_scope_record",
                      "owner_scope_document_git_blob", "tokenizer_source_sha256",
                      "checkpoint_sha256", "train_count", "nontrain_count"):
            with self.subTest(field=field):
                tampered = deepcopy(self.verdict)
                tampered["scope"][field] = None
                with self.assertRaisesRegex(owner.OwnerInternalHold, "I1_SCOPE"):
                    owner.validate_verdict(tampered, runtime_sha256=self.runtime)

    def test_verdict_mutations(self):
        for field, value in {"I1": "HOLD_I1", "runtime_sha256": {}, "fixture_sha256": "bad",
                             "expires_utc": "2020-01-01T00:00:00Z"}.items():
            with self.subTest(field=field):
                with self.assertRaises(owner.OwnerInternalHold):
                    owner.validate_verdict(dict(self.verdict, **{field: value}), runtime_sha256=self.runtime)

    def test_live_scope_and_foreign_identity(self):
        owner.require_scope(self.root)
        with self.assertRaisesRegex(release_auth_v2.AdmissionHold, "PROJECT_ROOT"):
            owner.require_scope(self.root / "_fake")
        with patch.object(release_auth_v2.platform, "node", return_value="foreign-host"):
            with self.assertRaisesRegex(release_auth_v2.AdmissionHold, "HOSTNAME"):
                owner.require_scope(self.root)

    def test_tampered_owner_document(self):
        with patch.object(owner, "OWNER_RECORD_BLOB", "0" * 40):
            with self.assertRaisesRegex(owner.OwnerInternalHold, "SCOPE_DOCUMENT"):
                owner.require_scope(self.root)

    def test_tampered_owner_module(self):
        args = SimpleNamespace(permit="", token_inventory="", tokenizer_source="dummy")
        with patch.object(runner, "OWNER_INTERNAL_GUARD_GIT_BLOB", "0" * 40):
            with self.assertRaisesRegex(RuntimeError, "ADMISSION_SOURCE_NOT_PINNED"):
                runner.owner_admission(args, self.root, run=False)

    def test_forged_local_owner_packet(self):
        args = SimpleNamespace(permit="fake.json", token_inventory="", tokenizer_source="dummy")
        with self.assertRaisesRegex(RuntimeError, "LOCAL_OWNER_PACKET_DENIED"):
            runner.owner_admission(args, self.root, run=True)

    def test_missing_github_verdict_denied_before_tokenizer(self):
        args = SimpleNamespace(permit="", token_inventory="", tokenizer_source="dummy")
        with patch("urllib.request.OpenerDirector.open", side_effect=OSError("offline")):
            with self.assertRaisesRegex(owner.OwnerInternalHold, "GITHUB_READBACK"):
                runner.owner_admission(args, self.root, run=True)

    def test_wrong_original_source(self):
        with self.assertRaisesRegex(owner.OwnerInternalHold, "ORIGINAL_BPE_SHA256"):
            owner.original_token_ids(b'{"tokens":[],"eos_id":256}')

    def test_fixture_tamper(self):
        meta, raw = runner.mock_token_inventory()
        rows = runner.fixture_generator(runner.permitted_ids(meta, raw))
        fixture = runner.json_bytes(rows)
        digest = hashlib.sha256(fixture).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / "FIXTURE_MANIFEST.json").write_bytes(runner.json_bytes(runner.case_and_group_manifest(rows)))
            records = target / "FIXTURE_RECORDS.json"
            records.write_bytes(fixture)
            self.assertEqual(runner.read_frozen_fixture(target, digest, meta, raw), rows)
            records.write_bytes(fixture + b"\n")
            with self.assertRaisesRegex(RuntimeError, "FIXTURE_BYTES_CHANGED"):
                runner.read_frozen_fixture(target, digest, meta, raw)

    def test_legacy_still_denies_missing_trust_anchors(self):
        with self.assertRaisesRegex(release_auth_v2.AdmissionHold, "TRUST_ANCHORS"):
            release_auth_v2.authenticate_release(Path("dummy"), phase="run", runner_sha256="x",
                tokenizer_sha256="x", underlying_sha256="x", project_root=self.root)


if __name__ == "__main__":
    unittest.main()
