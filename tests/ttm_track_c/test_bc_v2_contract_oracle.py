"""Agent C standalone v2 draft contract QA; does not import B implementation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from bc_v2_contract_oracle import (
    ARTIFACT_NAMES, PACK_SCHEMA, RESUME_METADATA_SCHEMA, CANON_SCHEMA,
    SPECIAL, MAX_LEN, canonical_v2, sha256_bytes, strict_typed_bridge,
    strict_b_bytes_to_text, validate_new_schema, freeze_seven_artifacts,
    verify_seven_artifacts, LEGACY_SCHEMAS,
)


def sample():
    return [{"role": "system", "content": "s"},
            {"role": "user", "content": "\x00[ASSIST] e\u0301 🐈"},
            {"role": "assistant", "content": "a"}]


def specimens():
    return {
        "tokenizer_sha256": {"schema": "ttm.bc.synthetic.byte_chat_codec.v2",
                            "bytes": [0, 255], "special": SPECIAL},
        "chat_template_sha256": {"schema": "ttm.bc.synthetic.role_bound_template.v2",
                                 "shift": 1, "ignore": -100, "stop": ["EOT", "EOS"]},
        "serialized_inputs_sha256": {"schema": "ttm.bc.synthetic.inputs.v2",
                                     "ids": [258,260,0,65,262,261,66,262,256]},
        "target_masks_sha256": {"schema": "ttm.bc.synthetic.masks.v2",
                                "assistant_flags": [0,0,0,0,0,0,1,1,1]},
        "target_labels_sha256": {"schema": "ttm.bc.synthetic.targets.v2",
                                 "y": [-100,-100,-100,-100,-100,66,262,256]},
        "config_sha256": {"schema": "ttm.bc.synthetic.config.v2",
                          "context":32, "vocab_size":2048},
        "checkpoint_schema_sha256": {"schema": RESUME_METADATA_SCHEMA,
                                     "checkpoint_weights": "NOT_CREATED"},
    }


class ContractV2SourceQA(unittest.TestCase):
    def test_01_special_byte_ids_distinct(self):
        self.assertEqual(set(SPECIAL.values()), set(range(256,263)))

    def test_02_utf8_exact_roundtrip_with_nul_literal_and_unicode(self):
        x = sample()
        transformed = strict_typed_bridge(x, max_len=MAX_LEN)
        self.assertEqual(strict_b_bytes_to_text(transformed), x)
        self.assertIn(0, transformed[1]["content"])
        self.assertEqual(transformed[1]["content"],
                         list(x[1]["content"].encode("utf-8")))
        self.assertNotIn(SPECIAL["ASSIST"], transformed[1]["content"])

    def test_03_identity_normalization_nfc_not_nfd(self):
        a = [{"role":"user","content":"e\u0301"},
             {"role":"assistant","content":"ok"}]
        b = [{"role":"user","content":"\u00e9"},
             {"role":"assistant","content":"ok"}]
        self.assertNotEqual(strict_typed_bridge(a)[0]["content"],
                            strict_typed_bridge(b)[0]["content"])

    def test_04_reject_unpaired_surrogate_and_wrong_types(self):
        for wrong in ("\ud800", "\udc00", ["not a str"], b"bytes", ""):
            m = [{"role":"user","content":wrong},
                 {"role":"assistant","content":"ok"}]
            with self.subTest(wrong=repr(wrong)), self.assertRaises(
                 (ValueError, UnicodeError)):
                strict_typed_bridge(m)

    def test_05_no_byte_only_record_disguised_as_text(self):
        with self.assertRaises(ValueError):
            strict_typed_bridge([{"role":"user","content":[255]},
                                 {"role":"assistant","content":"ok"}])
        with self.assertRaises(UnicodeDecodeError):
            strict_b_bytes_to_text([{"role":"user","content":[255]}])
        self.assertEqual(strict_b_bytes_to_text(
            [{"role":"user","content":[0,1,2,3,4,5,6]}])[0]["content"],
            "\x00\x01\x02\x03\x04\x05\x06")

    def test_06_bad_role_structures(self):
        for m in ([], [{"role":"assistant","content":"no"}],
                  [{"role":"user","content":"q"}],
                  [{"role":"user","content":"q"},{"role":"system","content":"bad"},
                   {"role":"assistant","content":"a"}],
                  [{"role":"user","content":"q","other":1},
                   {"role":"assistant","content":"a"}]):
            with self.subTest(m=m), self.assertRaises(ValueError):
                strict_typed_bridge(m)

    def test_07_no_silent_oversize_and_max_len_limit(self):
        m = [{"role":"user","content":"u"*30},
             {"role":"assistant","content":"a"*30}]
        with self.assertRaisesRegex(ValueError,"NO_SILENT_TRUNCATION"):
            strict_typed_bridge(m, max_len=33)
        with self.assertRaises(ValueError):
            strict_typed_bridge(sample(),max_len=34)
        with self.assertRaises(ValueError):
            strict_typed_bridge(sample(),max_len=True)

    def test_08_schema_v2_pack_is_not_resume_metadata(self):
        validate_new_schema(PACK_SCHEMA,role="pack")
        validate_new_schema(RESUME_METADATA_SCHEMA,role="resume_metadata")
        with self.assertRaises(ValueError):
            validate_new_schema(PACK_SCHEMA,role="resume_metadata")
        with self.assertRaises(ValueError):
            validate_new_schema(RESUME_METADATA_SCHEMA,role="pack")
        for legacy in LEGACY_SCHEMAS:
            with self.subTest(schema=legacy),self.assertRaises(ValueError):
                validate_new_schema(legacy,role="pack")

    def test_09_exact_terminal_lf_bytes_and_distinct_old_digest(self):
        o={"é": "café", "a": [0,256]}
        b=canonical_v2(o)
        self.assertTrue(b.endswith(b"\n") and not b.endswith(b"\r\n"))
        self.assertEqual(b, '{"a":[0,256],"é":"café"}\n'.encode("utf-8"))
        self.assertNotEqual(sha256_bytes(b),sha256_bytes(b[:-1]))
        self.assertEqual(json.loads(b),o)

    def test_10_refuse_nan_and_surrogate_json(self):
        with self.assertRaises(ValueError):
            canonical_v2({"invalid":float("nan")})
        with self.assertRaises(UnicodeError):
            canonical_v2({"invalid":"\ud800"})

    def test_11_seven_actual_files_saved_verified_and_distinct(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            report=freeze_seven_artifacts(root,specimens())
            self.assertEqual(set(report["artifacts"]),set(ARTIFACT_NAMES))
            self.assertEqual(report["canonical_schema"],CANON_SCHEMA)
            self.assertTrue(verify_seven_artifacts(root,report))
            for key,name in ARTIFACT_NAMES.items():
                raw=(root/name).read_bytes()
                self.assertEqual(report["artifacts"][key]["sha256"],sha256_bytes(raw))
                self.assertEqual(report["artifacts"][key]["size"],len(raw))
                self.assertEqual(raw,canonical_v2(specimens()[key]))

    def test_12_all_seven_artifacts_mutation_fail(self):
        for key,name in ARTIFACT_NAMES.items():
            with self.subTest(key=key),tempfile.TemporaryDirectory() as td:
                root=Path(td)
                report=freeze_seven_artifacts(root,specimens())
                (root/name).write_bytes((root/name).read_bytes()+b" ")
                with self.assertRaises(ValueError):
                    verify_seven_artifacts(root,report)

    def test_13_crlf_mutation_rejected_and_old_no_lf_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            report=freeze_seven_artifacts(root,specimens())
            path=root/ARTIFACT_NAMES["config_sha256"]
            src=path.read_bytes()
            path.write_bytes(src.replace(b"\n",b"\r\n"))
            with self.assertRaises(ValueError):
                verify_seven_artifacts(root,report)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            report=freeze_seven_artifacts(root,specimens())
            path=root/ARTIFACT_NAMES["config_sha256"]
            path.write_bytes(path.read_bytes()[:-1])
            with self.assertRaises(ValueError):
                verify_seven_artifacts(root,report)

    def test_14_no_overwrite_partial_records_remain(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            report=freeze_seven_artifacts(root,specimens())
            with self.assertRaises(FileExistsError):
                freeze_seven_artifacts(root,specimens())
            self.assertTrue(verify_seven_artifacts(root,report))

    def test_15_alias_and_fake_digest_rejected_for_each_field(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            report=freeze_seven_artifacts(root,specimens())
            for key in ARTIFACT_NAMES:
                forged=copy.deepcopy(report)
                forged["artifacts"][key]["sha256"]="0"*64
                with self.subTest(key=key),self.assertRaises(ValueError):
                    verify_seven_artifacts(root,forged)
            bad=copy.deepcopy(report)
            bad["artifacts"]["tokenizer_sha256"]["file"]="../tokenizer.json"
            with self.assertRaises(ValueError):
                verify_seven_artifacts(root,bad)

    def test_16_missing_extra_fields_and_invalid_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            report=freeze_seven_artifacts(root,specimens())
            for key in ARTIFACT_NAMES:
                forged=copy.deepcopy(report);forged["artifacts"].pop(key)
                with self.subTest(key=key),self.assertRaises(ValueError):
                    verify_seven_artifacts(root,forged)
            forged=copy.deepcopy(report);forged["pack_schema"]="ttm.bc.synthetic.sft.pack.v1"
            with self.assertRaises(ValueError):
                verify_seven_artifacts(root,forged)
            forged=copy.deepcopy(report);forged["resume_metadata_schema"]="ttm.bc.synthetic.sft_checkpoint.v1"
            with self.assertRaises(ValueError):
                verify_seven_artifacts(root,forged)

    def test_17_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            report=freeze_seven_artifacts(root,specimens())
            path=root/ARTIFACT_NAMES["tokenizer_sha256"]
            original=root/"source.json"
            path.rename(original)
            try:
                path.symlink_to(original)
            except (OSError,NotImplementedError):
                self.skipTest("system does not permit symlinks")
            with self.assertRaisesRegex(ValueError,"SYMLINK"):
                verify_seven_artifacts(root,report)

    def test_18_raw_bytes_and_computed_hash_not_name_only(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            obj=specimens()
            report=freeze_seven_artifacts(root,obj)
            for key,entry in report["artifacts"].items():
                self.assertNotEqual(entry["sha256"],sha256_bytes(key.encode()))
                self.assertEqual(entry["sha256"],sha256_bytes(
                    (root/entry["file"]).read_bytes()))

if __name__=="__main__":
    unittest.main()
