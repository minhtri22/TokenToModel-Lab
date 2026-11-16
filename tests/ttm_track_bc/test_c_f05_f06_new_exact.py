"""Agent C exact B v2 F05/F06 independent-of-B-author negative contract suite.

Synthetic-only. No model training, no GPU, no protected TEST.
Source must be committed on a review branch parented to the *new B tested
implementation*, not the 2026-11-16 pre-remediation candidate.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from src.ttm_track_b import bc_sft_bridge_v2 as B

B_EXACT_CODE = "a83e1526bce842761f3051dad28b90a55395a6aa"
BRIDGE_EXACT = "ttm.bc.c_string_to_b_bytes.v2"


class CExactF05F06NegativeQA(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="c_f05_f06_new_")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bundle = self.root / "bundle"
        self.manifest = B.write_bundle(self.bundle)
        self.manifest_path = self.bundle / "manifest.json"

    def _rewrite_manifest(self, modify):
        candidate = json.loads(self.manifest_path.read_bytes().decode("utf-8"))
        modify(candidate)
        self.manifest_path.write_bytes(B.canonical(candidate))

    def test_01_actual_positive_bundle_is_valid(self):
        verified = B.verify_bundle(self.bundle)
        self.assertEqual(verified, self.manifest)
        self.assertEqual(verified["bridge_schema"], B.BRIDGE_SCHEMA)
        self.assertEqual(verified["bridge_schema"], BRIDGE_EXACT)
        self.assertEqual(set(B.ARTIFACT_NAMES), set(B.REQUIRED))

    def test_02_f05_forged_exact_length_alias_is_rejected(self):
        self._rewrite_manifest(lambda m: m.__setitem__(
            "bridge_schema", "ttm.bc.c_string_to_b_bytes.unapproved_alias"))
        with self.assertRaisesRegex(ValueError, "BRIDGE_SCHEMA_VERSION_MISMATCH"):
            B.verify_bundle(self.bundle)

    def test_03_f05_missing_bridge_schema_is_rejected(self):
        self._rewrite_manifest(lambda m: m.pop("bridge_schema"))
        with self.assertRaisesRegex(ValueError, "BRIDGE_SCHEMA_VERSION_MISMATCH"):
            B.verify_bundle(self.bundle)

    def test_04_f05_wrong_types_and_obsolete_versions_are_rejected(self):
        old_bytes = self.manifest_path.read_bytes()
        for forged in (None, False, True, {}, [], 0, 14, "", "ttm.bc.c_string_to_b_bytes.v1"):
            with self.subTest(forged=repr(forged)):
                self.manifest_path.write_bytes(old_bytes)
                self._rewrite_manifest(lambda m: m.__setitem__("bridge_schema", forged))
                with self.assertRaisesRegex(ValueError, "BRIDGE_SCHEMA_VERSION_MISMATCH"):
                    B.verify_bundle(self.bundle)
        self.manifest_path.write_bytes(old_bytes)
        self.assertEqual(B.verify_bundle(self.bundle), self.manifest)

    def test_05_f06_external_same_byte_manifest_symlink_is_rejected(self):
        external = self.root / "valid_external_manifest.json"
        original = self.manifest_path.read_bytes()
        external.write_bytes(original)
        self.assertEqual(external.read_bytes(), original)
        self.manifest_path.unlink()
        # Deliberately NO skip. A platform without symlink rights is NOT_EXECUTED.
        self.manifest_path.symlink_to(external)
        self.assertTrue(self.manifest_path.is_symlink())
        with self.assertRaisesRegex(ValueError, "SYMLINK_OR_MISSING_MANIFEST"):
            B.verify_bundle(self.bundle)

    def test_06_f06_missing_or_directory_manifest_is_rejected(self):
        self.manifest_path.unlink()
        # An absent basename fails at the prior exact-file-set gate. That is
        # fail-closed too; F06's separate symlink test checks the pre-read guard.
        with self.assertRaisesRegex(ValueError, "BUNDLE_FILE_SET_MISMATCH"):
            B.verify_bundle(self.bundle)
        self.manifest_path.mkdir()
        with self.assertRaisesRegex(ValueError, "SYMLINK_OR_MISSING_MANIFEST"):
            B.verify_bundle(self.bundle)

    def test_07_seven_real_artifact_bytes_readback_and_sha_match(self):
        for key, name in B.ARTIFACT_NAMES.items():
            with self.subTest(name=name):
                data = (self.bundle / name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), self.manifest[key])
                self.assertEqual(data[-1:], b"\n")
                self.assertNotIn(b"\r\n", data)
                self.assertEqual(data, B.canonical(json.loads(data.decode("utf-8"))))

    def test_08_seven_independent_artifact_byte_mutations_rejected(self):
        for key, name in B.ARTIFACT_NAMES.items():
            with self.subTest(name=name):
                path = self.bundle / name
                saved = path.read_bytes()
                path.write_bytes(saved + b" ")
                try:
                    with self.assertRaises(ValueError):
                        B.verify_bundle(self.bundle)
                finally:
                    path.write_bytes(saved)
                self.assertEqual(B.verify_bundle(self.bundle), self.manifest)

    def test_09_seven_forged_manifest_hex_sha_rejected(self):
        saved = self.manifest_path.read_bytes()
        for key in B.ARTIFACT_NAMES:
            with self.subTest(key=key):
                self.manifest_path.write_bytes(saved)
                self._rewrite_manifest(lambda m: m.__setitem__(key, "0"*64))
                with self.assertRaisesRegex(ValueError, "ARTIFACT_SHA_READBACK_MISMATCH"):
                    B.verify_bundle(self.bundle)
        self.manifest_path.write_bytes(saved)
        self.assertEqual(B.verify_bundle(self.bundle), self.manifest)

    def test_10_seven_rehashed_forgeries_with_changed_semantics_rejected(self):
        saved_m = self.manifest_path.read_bytes()
        for key, name in B.ARTIFACT_NAMES.items():
            with self.subTest(key=key):
                p = self.bundle / name
                original = p.read_bytes()
                document = json.loads(original.decode("utf-8"))
                document["__forged_semantic_change__"] = True
                forged = B.canonical(document)
                try:
                    p.write_bytes(forged)
                    m = json.loads(saved_m.decode("utf-8"))
                    m[key] = hashlib.sha256(forged).hexdigest()
                    self.manifest_path.write_bytes(B.canonical(m))
                    with self.assertRaises(ValueError):
                        B.verify_bundle(self.bundle)
                finally:
                    p.write_bytes(original)
                    self.manifest_path.write_bytes(saved_m)
                self.assertEqual(B.verify_bundle(self.bundle), self.manifest)

    def test_11_checkpoint_and_legacy_schema_alias_rejected(self):
        old = self.manifest_path.read_bytes()
        cases = [
            ("schema", "ttm.bc.synthetic.sft.pack.v1"),
            ("schema", "ttm.bc.synthetic.sft_pack.v1"),
            ("schema", "ttm.track_b.synthetic.byte_windows.v1"),
            ("checkpoint_schema", "ttm.bc.synthetic.sft_checkpoint.v1"),
            ("checkpoint_schema", "ttm.t4.science.checkpoint.v1"),
            ("canonical_schema", "ttm.bc.canonical_json_utf8_lf.v1")
        ]
        for field,value in cases:
            with self.subTest(field=field,value=value):
                self.manifest_path.write_bytes(old)
                self._rewrite_manifest(lambda m: m.__setitem__(field,value))
                with self.assertRaises(ValueError):
                    B.verify_bundle(self.bundle)

    def test_12_manifest_LF_CRLF_and_untrusted_extra_file_rejected(self):
        orig = self.manifest_path.read_bytes()
        for modified in [orig[:-1], orig.replace(b"\n", b"\r\n")]:
            self.manifest_path.write_bytes(modified)
            with self.assertRaises(ValueError):
                B.verify_bundle(self.bundle)
        self.manifest_path.write_bytes(orig)
        (self.bundle / "EXTRA_FORGED_MANIFEST.json").write_text("{}", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "BUNDLE_FILE_SET_MISMATCH"):
            B.verify_bundle(self.bundle)

    def test_13_role_mask_target_semantics_match_independent_known_answer(self):
        messages = [{"role": "system", "content": "P"},
                    {"role": "user", "content": "\x00é"},
                    {"role": "assistant", "content": "ạ"}]
        ids,flags = B.serialize(messages,33)
        self.assertEqual(flags, B.derive_mask(ids))
        x,y = B.build(messages,33)
        self.assertEqual(x[:len(ids)-1], ids[:-1])
        self.assertEqual(y[:len(ids)-1],
            [ids[i] if flags[i] else -100 for i in range(1,len(ids))])
        self.assertEqual([v for v in y if v >= 0][-2:],
                         [B.SPECIAL["EOT"],B.SPECIAL["EOS"]])
        self.assertNotIn(B.SPECIAL["PAD"],y)
        for index in range(len(flags)):
            tampered = flags.copy();tampered[index] ^= 1
            with self.subTest(index=index),self.assertRaises(ValueError):
                B.targets(ids,tampered,33)
        self.assertEqual(B.from_byte_messages(B.to_byte_messages(messages)),messages)

    def test_14_checkpoint_metadata_not_real_weights(self):
        checkpoint = json.loads((self.bundle/"checkpoint_schema.json").read_bytes())
        self.assertEqual(checkpoint["scope"], "METADATA_ONLY_NO_ACTUAL_CHECKPOINT")
        self.assertIs(checkpoint["resume_enabled"], False)
        self.assertEqual(checkpoint["weights"],"NOT_CREATED")
        self.assertEqual(checkpoint["optimizer_state"],"NOT_CREATED")


    def test_15_exact_B_source_and_C_reference_git_blob_pins(self):
        root = Path(__file__).resolve().parents[2]
        def git_blob_sha(path):
            data = path.read_bytes().replace(b"\r\n", b"\n")
            return hashlib.sha1(
                b"blob " + str(len(data)).encode("ascii") + b"\0" + data
            ).hexdigest()
        self.assertEqual(git_blob_sha(root/"src/ttm_track_b/bc_sft_bridge_v2.py"),
                         "c56d98b520fef387fab43bac87b7a9247287b17c")
        self.assertEqual(git_blob_sha(Path(__file__).with_name("c_part_b_c_v2_reference.py")),
                         "9ae5e8b189b361a496bc7bfd9ec0342bc24a7e72")


if __name__ == "__main__":
    unittest.main()
