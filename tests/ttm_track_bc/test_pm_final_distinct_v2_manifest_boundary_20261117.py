"""Third-actor PM fail-closed acceptance on exact B/C v2 F05/F06 amendment.

New independent tests. Standard-library-only; no Torch, GPU, checkpoint,
real corpus or optimizer. Deliberately separate from author B and contract C.
The original 3 PM tests remain unchanged in their existing repo path.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.ttm_track_b import bc_sft_bridge_v2 as b


class PMFinalDistinctBoundaryQA(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="ttm_pm_bc_v2_final_")
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.bundle = self.root / "bundle"
        b.write_bundle(self.bundle)
        self.manifest = self.bundle / "manifest.json"

    def manifest_data(self):
        return json.loads(self.manifest.read_bytes().decode("utf-8"))

    def set_manifest(self, data):
        self.manifest.write_bytes(b.canonical(data))

    def test_01_positive_canonical_bundle_and_seven_real_hashes(self):
        m = b.verify_bundle(self.bundle)
        self.assertEqual(m["bridge_schema"], b.BRIDGE_SCHEMA)
        self.assertEqual(m["schema"], b.SCHEMA)
        self.assertEqual(len(b.ARTIFACT_NAMES), 7)
        for field, filename in sorted(b.ARTIFACT_NAMES.items()):
            with self.subTest(field=field):
                raw = (self.bundle / filename).read_bytes()
                self.assertTrue(raw.endswith(b"\n"))
                self.assertNotIn(b"\r\n", raw)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), m[field])
                self.assertEqual(raw, b.canonical(json.loads(raw.decode("utf-8"))))

    def test_02_forged_missing_and_wrong_type_bridge_versions_rejected(self):
        variants = [
            ("unknown_alias", "ttm.bc.c_string_to_b_bytes.unapproved_alias"),
            ("old_version", "ttm.bc.c_string_to_b_bytes.v1"),
            ("null", None),
            ("number", 2),
            ("list", [b.BRIDGE_SCHEMA]),
        ]
        original = self.manifest_data()
        for label, variant in variants:
            with self.subTest(label=label):
                forged = dict(original)
                forged["bridge_schema"] = variant
                self.set_manifest(forged)
                with self.assertRaises(ValueError):
                    b.verify_bundle(self.bundle)
        missing = dict(original)
        del missing["bridge_schema"]
        self.set_manifest(missing)
        with self.assertRaises(ValueError):
            b.verify_bundle(self.bundle)

    def test_03_external_byte_identical_manifest_symlink_rejected(self):
        target = self.root / "external_manifest.json"
        target.write_bytes(self.manifest.read_bytes())
        self.manifest.unlink()
        try:
            self.manifest.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.fail("SYMLINK_TEST_NOT_EXECUTED: " + str(exc))
        self.assertTrue(self.manifest.is_symlink())
        with self.assertRaises(ValueError):
            b.verify_bundle(self.bundle)

    def test_04_manifest_directory_instead_of_file_rejected(self):
        self.manifest.unlink()
        self.manifest.mkdir()
        with self.assertRaises(ValueError):
            b.verify_bundle(self.bundle)

    def test_05_all_seven_artifact_symlinks_rejected(self):
        for field, filename in sorted(b.ARTIFACT_NAMES.items()):
            with self.subTest(field=field):
                src = self.bundle / filename
                outside = self.root / (field + ".external")
                src.rename(outside)
                try:
                    try:
                        src.symlink_to(outside)
                    except (OSError, NotImplementedError) as exc:
                        self.fail("ARTIFACT_SYMLINK_TEST_NOT_EXECUTED: " + str(exc))
                    self.assertTrue(src.is_symlink())
                    with self.assertRaises(ValueError):
                        b.verify_bundle(self.bundle)
                finally:
                    if src.is_symlink():
                        src.unlink()
                    outside.rename(src)

    def test_06_all_seven_artifact_byte_mutations_rejected(self):
        for field, filename in sorted(b.ARTIFACT_NAMES.items()):
            with self.subTest(field=field):
                src = self.bundle / filename
                raw = src.read_bytes()
                try:
                    src.write_bytes(raw + b"\n")
                    with self.assertRaises(ValueError):
                        b.verify_bundle(self.bundle)
                finally:
                    src.write_bytes(raw)

    def test_07_rehashed_semantically_wrong_target_rejected(self):
        p = self.bundle / b.ARTIFACT_NAMES["target_labels_sha256"]
        labels = json.loads(p.read_bytes().decode("utf-8"))
        y = labels["rows"][0]["y"]
        index = next(i for i, val in enumerate(y) if val != b.IGNORE)
        y[index] = (y[index] + 1) % b.VOCAB
        forged_raw = b.canonical(labels)
        p.write_bytes(forged_raw)
        forged_manifest = self.manifest_data()
        forged_manifest["target_labels_sha256"] = hashlib.sha256(forged_raw).hexdigest()
        self.set_manifest(forged_manifest)
        with self.assertRaises(ValueError):
            b.verify_bundle(self.bundle)

    def test_08_manifest_noncanonical_crlf_rejected(self):
        raw = self.manifest.read_bytes()
        self.assertIn(b"\n", raw)
        self.manifest.write_bytes(raw.replace(b"\n", b"\r\n"))
        with self.assertRaises(ValueError):
            b.verify_bundle(self.bundle)

    def test_09_legacy_pack_schema_rejected(self):
        forged = self.manifest_data()
        forged["schema"] = b.OLD_BC_SCHEMA
        self.set_manifest(forged)
        with self.assertRaises(ValueError):
            b.verify_bundle(self.bundle)


if __name__ == "__main__":
    unittest.main()
