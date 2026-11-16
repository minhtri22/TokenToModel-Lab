#!/usr/bin/env python3
"""Versioned M0 v3 guarded-runner source integration; no checkpoint or I2."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import importlib._bootstrap_external
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]  # tools/pilot_t4/direct_failure_diag_q001 -> repo? resolved below
LEGACY = HERE.parent / "preexec_candidate_20261116"
sys.path.insert(0, str(LEGACY))
import ttm_sm4m_diag_q001 as diag
from q001_m0_goldblind import make_fixture, score_logits


class IntegratedM0SourceQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids = list(range(300, 500))
        cls.rows = diag.fixture_generator(cls.ids)

    def test_source_hash_pinned(self):
        src = HERE / "q001_m0_goldblind.py"
        self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),
                         diag.TRACK_A_V3_SOURCE_SHA256)
        self.assertTrue(diag.track_a_v3().SCHEMA.endswith(".mock"))

    def test_old_model_source_no_checkpoint(self):
        self.assertNotIn("torch", sys.modules)
        self.assertEqual(len(self.rows), 80)
        self.assertEqual(self.rows, make_fixture(self.ids))
        self.assertEqual(diag.SEED, 20261116)

    def test_runner_uses_v3_case_and_group_hashes(self):
        mf = diag.case_and_group_manifest(self.rows)
        self.assertEqual(mf["protocol_schema"], diag.TRACK_A_V3_PROTOCOL)
        self.assertEqual(mf["scorer_sha256"], diag.TRACK_A_V3_SOURCE_SHA256)
        self.assertEqual(len(mf["case_sha256"]), 80)
        self.assertEqual(len(mf["group_sha256"]), 5)

    def test_readback_immutable_and_tamper_denials(self):
        # Test files are transient and confined to repository checkout.
        repo = HERE.parents[3]
        with tempfile.TemporaryDirectory(prefix="_q001_m0_v3_", dir=repo) as temp:
            target = Path(temp)
            records = target / "FIXTURE_RECORDS.json"
            man = target / "FIXTURE_MANIFEST.json"
            records.write_bytes(diag.json_bytes(self.rows))
            mf = diag.case_and_group_manifest(self.rows)
            man.write_bytes(diag.json_bytes(mf))
            self.assertEqual(
                diag.read_frozen_fixture(target,mf["fixture_sha256"],
                                         allowed=self.ids),self.rows)
            original = records.read_bytes()
            records.write_bytes(original + b" ")
            with self.assertRaises(RuntimeError):
                diag.read_frozen_fixture(target, mf["fixture_sha256"], allowed=self.ids)
            records.write_bytes(original)
            broken = copy.deepcopy(mf)
            broken["case_sha256"][self.rows[0]["id"]] = "0" * 64
            man.write_bytes(diag.json_bytes(broken))
            with self.assertRaises(RuntimeError):
                diag.read_frozen_fixture(target,mf["fixture_sha256"],
                                         allowed=self.ids)

    def test_goldblind_live_eval_adapter_equal_logits(self):
        z = [0.0] * 2048
        for row in self.rows:
            score = diag.evaluate_goldblind_logits(z,row)
            self.assertFalse(score["candidate_correct"])
            self.assertFalse(score["greedy_correct"])
            self.assertTrue(score["candidate_tie_abstained"])
            self.assertTrue(score["full_vocab_tie_abstained"])

    def test_live_adapter_matches_frozen_module(self):
        values = [float(-i) for i in range(2048)]
        for row in self.rows:
            out = diag.evaluate_goldblind_logits(values,row)
            ref = score_logits(values,row)
            self.assertEqual(out["gold_nll"],ref["full_vocab_gold_nll"])
            self.assertEqual(out["gold_rank"],ref["full_vocab_gold_rank"])
            self.assertEqual(out["candidate_correct"],
                             ref["candidate_only_top1_correct_secondary"])

    def test_full_vocab_competition_not_candidate_success(self):
        row = next(x for x in self.rows if x["group"] == "TRAIN" and
                   x["gold"] != x["no_answer"])
        z = [-1.0] * 2048
        z[row["gold"]] = 5.0
        z[0] = 10.0
        out = diag.evaluate_goldblind_logits(z,row)
        self.assertTrue(out["candidate_correct"])
        self.assertFalse(out["greedy_correct"])
        self.assertEqual(out["gold_rank"],2)

    def test_tampered_scorer_pin_stops(self):
        with patch.object(diag, "TRACK_A_V3_SOURCE_SHA256", "0"*64), \
                patch.object(diag, "TRACK_A_V3_CRLF_SHA256", "0"*64):
            with self.assertRaisesRegex(RuntimeError, "TRACK_A_V3_SOURCE_SHA_MISMATCH"):
                diag.track_a_v3()

    def test_stale_mtime_size_pyc_is_never_executed(self):
        # Genuine reproduction of review F02: forge valid timestamp-based pyc
        # while the reviewed source bytes/mtime/size stay completely unchanged.
        with tempfile.TemporaryDirectory(prefix="_q001_v3_pyc_", dir=HERE.parents[3]) as d:
            root = Path(d)
            runner_dir = root / "preexec_candidate_20261116"
            score_dir = root / "track_a_m0_v3"
            runner_dir.mkdir()
            score_dir.mkdir()
            source = score_dir / "q001_m0_goldblind.py"
            source.write_bytes((HERE / source.name).read_bytes())
            st = source.stat()
            malicious = compile("PYC_SENTINEL_EXECUTED = True\n",
                                str(source), "exec")
            cache = Path(importlib.util.cache_from_source(str(source)))
            cache.parent.mkdir(exist_ok=True)
            cache.write_bytes(importlib._bootstrap_external._code_to_timestamp_pyc(
                malicious, int(st.st_mtime), st.st_size))
            # Positive control: the formerly used loader DOES execute the forged cache.
            spec = importlib.util.spec_from_file_location("old_loader_positive", source)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.assertTrue(getattr(mod, "PYC_SENTINEL_EXECUTED", False))
            self.assertEqual(source.read_bytes(), (HERE / source.name).read_bytes())
            self.assertEqual(source.stat().st_size, st.st_size)
            with patch.object(diag, "__file__", str(runner_dir / "ttm_sm4m_diag_q001.py")):
                secure = diag.track_a_v3()
            self.assertFalse(hasattr(secure, "PYC_SENTINEL_EXECUTED"))
            self.assertEqual(secure.VOCAB, 2048)

    def test_preserve_pre_remediation_private_manifest_by_exact_pins_only(self):
        # Use MOCK bytes to reach the compatibility branch without private I1.
        with tempfile.TemporaryDirectory(prefix="_q001_v3_oldmf_", dir=HERE.parents[3]) as d:
            directory = Path(d)
            records = directory / "FIXTURE_RECORDS.json"
            manifest = directory / "FIXTURE_MANIFEST.json"
            records.write_bytes(diag.json_bytes(self.rows))
            new_mf = diag.case_and_group_manifest(self.rows)
            old_mf = dict(new_mf,
                scorer_sha256=diag.TRACK_A_V3_PRE_REPAIR_SCORER_SHA256)
            manifest.write_bytes(diag.json_bytes(old_mf))
            digest = diag.sha256_file(records)
            with patch.object(diag, "TRACK_A_V3_FROZEN_RECORDS_SHA256", digest), \
                 patch.object(diag, "TRACK_A_V3_FROZEN_MANIFEST_SHA256", diag.sha256_file(manifest)):
                self.assertEqual(
                    diag.read_frozen_fixture(directory, digest, allowed=self.ids),
                    self.rows)
                manifest.write_bytes(manifest.read_bytes() + b" ")
                with self.assertRaises(RuntimeError):
                    diag.read_frozen_fixture(directory, digest, allowed=self.ids)


    def test_mutated_fixture_gold_rejected(self):
        broken = copy.deepcopy(self.rows)
        broken[0]["gold"] = 999
        absent = next(r["gold"] for r in self.rows if r["group"] == "HELDOUT_ABSENT")
        with self.assertRaises(RuntimeError):
            diag.validate_fixture(broken, absent)

    def test_old_v3_nonce_not_granted_and_no_i2_entry(self):
        child = subprocess.run([sys.executable, str(LEGACY/"ttm_sm4m_diag_q001.py"),
            "run"],text=True,capture_output=True,timeout=15)
        self.assertEqual(child.returncode,2)
        self.assertIn("HOLD_",child.stderr)

    def test_mock_source_qa_legacy_entry_uses_v3(self):
        res = diag.mock_source_qa()
        self.assertEqual(res["total"],res["passed"])
        self.assertFalse(res["model_run"])
        self.assertFalse(res["checkpoint_access"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
