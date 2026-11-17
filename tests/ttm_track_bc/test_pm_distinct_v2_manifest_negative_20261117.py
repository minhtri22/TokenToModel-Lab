"""PM-authored exact-candidate negative probes for BC v2 manifest verification.

This is a NEW independent review test; it was not part of B's 24 or C's 19
previously executed tests. Run only against exact B implementation source
724f62a025b8ecc7c452b9ee16c926adfd2b8c7e; no model/Torch/GPU/science.

The two negative cases below are EXPECTED TO FAIL on the existing B v2 source:
their purpose is to prove missing fail-closed checks, not to assert QA PASS.
No execution status is claimed until the tests are actually run.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.ttm_track_b import bc_sft_bridge_v2 as b


class DistinctManifestBoundaryReview(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ttm_bc_pm_v2_")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bundle = self.root / "bundle"
        b.write_bundle(self.bundle)
        self.manifest = self.bundle / "manifest.json"

    def test_01_valid_fixture_is_accepted(self):
        result = b.verify_bundle(self.bundle)
        self.assertEqual(result["bridge_schema"], b.BRIDGE_SCHEMA)
        self.assertEqual(result["schema"], b.SCHEMA)

    def test_02_forged_bridge_schema_must_fail_closed(self):
        data = json.loads(self.manifest.read_bytes().decode("utf-8"))
        self.assertEqual(data["bridge_schema"], b.BRIDGE_SCHEMA)
        data["bridge_schema"] = "ttm.bc.c_string_to_b_bytes.unapproved_alias"
        # Preserve all seven actual artifact bytes and SHAs. Recanonicalize
        # only the manifest: no accidental CRLF or digest-field corruption.
        self.manifest.write_bytes(b.canonical(data))
        with self.assertRaises(ValueError, msg="BC-QA-F05: forged bridge alias accepted"):
            b.verify_bundle(self.bundle)

    def test_03_manifest_symlink_must_fail_closed(self):
        external_manifest = self.root / "external_manifest.json"
        external_manifest.write_bytes(self.manifest.read_bytes())
        self.manifest.unlink()
        try:
            self.manifest.symlink_to(external_manifest)
        except (OSError, NotImplementedError) as exc:
            self.skipTest("platform cannot create symlink: " + str(exc))
        self.assertTrue(self.manifest.is_symlink())
        with self.assertRaises(ValueError, msg="BC-QA-F06: manifest symlink accepted"):
            b.verify_bundle(self.bundle)


if __name__ == "__main__":
    unittest.main()
