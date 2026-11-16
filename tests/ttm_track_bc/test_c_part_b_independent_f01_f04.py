"""Agent-C-authored cross-track tests on exact B v2 review branch.

This is NOT the B-author suite and NOT distinct third-party QA. CPU-only
synthetic engineering; source C oracle is copied by exact Git blob.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import tempfile
import unittest

from src.ttm_track_b import bc_sft_bridge_v2 as B
from src.ttm_track_b import bc_sft_interface as B_V1
from src.ttm_track_b.scaffold import cross_entropy_valid

_ORACLE = Path(__file__).with_name("c_part_b_c_v2_reference.py")
_SPEC = importlib.util.spec_from_file_location("c_part_b_independent_oracle", _ORACLE)
C = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(C)

EXACT_B_REVIEW_HEAD = "724f62a025b8ecc7c452b9ee16c926adfd2b8c7e"
EXACT_C_HEAD = "66c9b92a30cd403aa909528008ffaa6d83286285"
C_ORACLE_GIT_BLOB = "9ae5e8b189b361a496bc7bfd9ec0342bc24a7e72"


def short_messages():
    return [{"role":"system","content":"P"},
            {"role":"user","content":"\x00[ASSIST]é"},
            {"role":"assistant","content":"ạ"}]


def manual_role_wire(msgs):
    payload = C.strict_typed_bridge(msgs, max_len=33)
    ids, mask = [B.SPECIAL["BOS"]], [0]
    for message in payload:
        role = message["role"]
        marker = B.SPECIAL[{"system":"SYS","user":"USER","assistant":"ASSIST"}[role]]
        is_assistant = int(role == "assistant")
        raw = message["content"]
        ids.extend([marker, *raw, B.SPECIAL["EOT"]])
        mask.extend([0] + [is_assistant]*len(raw) + [is_assistant])
    ids.append(B.SPECIAL["EOS"])
    mask.append(1)
    return ids, mask


def independent_artifact_report(root: Path, manifest: dict):
    return {
        "wire_schema": C.WIRE_SCHEMA,
        "pack_schema": C.PACK_SCHEMA,
        "resume_metadata_schema": C.RESUME_METADATA_SCHEMA,
        "canonical_schema": C.CANON_SCHEMA,
        "artifacts": {
            key: {"file": name, "size":len((root/name).read_bytes()),
                  "sha256":manifest[key]}
            for key,name in C.ARTIFACT_NAMES.items()
        }
    }


class CPartBExactCandidateQA(unittest.TestCase):
    def test_01_c_schema_identity_byte_policy_matches_b(self):
        self.assertEqual(B.SCHEMA, C.PACK_SCHEMA)
        self.assertEqual(B.CHECKPOINT_SCHEMA, C.RESUME_METADATA_SCHEMA)
        self.assertEqual(B.BRIDGE_SCHEMA, C.WIRE_SCHEMA)
        self.assertEqual(B.CANONICAL_SCHEMA, C.CANON_SCHEMA)
        self.assertEqual(B.CHAT_TEMPLATE_SCHEMA, C.TEMPLATE_SCHEMA)
        self.assertEqual(B.SPECIAL, C.SPECIAL)
        self.assertEqual(B.MAX_MODEL_CONTEXT, C.MAX_LEN-1)

    def test_02_preserve_v1_immutable_codec_and_names(self):
        self.assertEqual(B_V1.PACK_SCHEMA, "ttm.bc.synthetic.sft.pack.v1")
        self.assertEqual(B_V1.RESUME_SCHEMA, "ttm.bc.synthetic.sft.resume.v1")
        self.assertEqual(B_V1.CANONICAL_SCHEMA if hasattr(B_V1,"CANONICAL_SCHEMA") else "V1_NO_LF",
                         "V1_NO_LF")
        self.assertNotEqual(B_V1.PACK_SCHEMA,B.SCHEMA)
        self.assertNotEqual(B_V1.canonical({"x":1}),B.canonical({"x":1}))

    def test_03_c_to_b_exact_utf8_roundtrip_including_nul_role_literal(self):
        m=short_messages()
        self.assertEqual(B.to_byte_messages(m),C.strict_typed_bridge(m))
        self.assertEqual(B.from_byte_messages(B.to_byte_messages(m)),m)
        self.assertEqual(B.to_byte_messages(m)[1]["content"],list(m[1]["content"].encode("utf-8")))
        self.assertIn(0,B.to_byte_messages(m)[1]["content"])
        self.assertTrue(all(v <= 255 for v in B.to_byte_messages(m)[1]["content"]))

    def test_04_independent_role_wire_and_plus_one_mask(self):
        msgs=short_messages()
        expected_ids, expected_mask=manual_role_wire(msgs)
        ids, flags=B.serialize(msgs,33)
        self.assertEqual((ids,flags),(expected_ids,expected_mask))
        x,y=B.build(msgs,33)
        self.assertEqual(x[:len(ids)-1],ids[:-1])
        self.assertEqual(y[:len(ids)-1],
                         [ids[i] if expected_mask[i] else -100 for i in range(1,len(ids))])
        self.assertEqual([v for v in y if v>=0][-2:],[B.SPECIAL["EOT"],B.SPECIAL["EOS"]])
        self.assertEqual(y.count(B.SPECIAL["USER"]),0)
        self.assertEqual(y.count(B.SPECIAL["PAD"]),0)

    def test_05_every_flag_mutation_rejected_against_role_reference(self):
        ids,flags=B.serialize(short_messages(),33)
        for i in range(len(flags)):
            wrong=flags.copy()
            wrong[i]^=1
            with self.subTest(i=i),self.assertRaises(ValueError):
                B.targets(ids,wrong,33)

    def test_06_injected_specials_and_double_eos_rejected(self):
        ids,flags=B.serialize(short_messages(),33)
        index=ids.index(B.SPECIAL["USER"])+1
        for s in B.SPECIAL.values():
            altered=ids.copy();altered[index]=s
            with self.subTest(s=s),self.assertRaises(ValueError):
                B.targets(altered,flags,33)
        with self.assertRaises(ValueError):
            B.targets(ids+[B.SPECIAL["EOS"]],flags+[1],33)

    def test_07_nfc_nfd_byte_identity_not_normalized(self):
        def m(x):
            return [{"role":"user","content":x},{"role":"assistant","content":"a"}]
        self.assertNotEqual(B.to_byte_messages(m("é")),B.to_byte_messages(m("e\u0301")))
        self.assertNotEqual(B.canonical({"v":"é"}),B.canonical({"v":"e\u0301"}))

    def test_08_reject_invalid_surrogate_or_byte_as_c_text(self):
        for text in ("\ud800","\udfff"):
            with self.subTest(text=repr(text)),self.assertRaises(UnicodeEncodeError):
                B.to_byte_messages([{"role":"user","content":text},
                                    {"role":"assistant","content":"a"}])
        with self.assertRaises(ValueError):
            B.to_byte_messages([{"role":"user","content":[65]},
                                {"role":"assistant","content":"a"}])
        with self.assertRaises(UnicodeDecodeError):
            B.from_byte_messages([{"role":"user","content":[255]}])

    def test_09_new_canonical_bytes_exact_c_reference(self):
        o={"z":"🇻🇳","a":[0,256],"é":"e\u0301"}
        self.assertEqual(B.canonical(o),C.canonical_v2(o))
        self.assertEqual(B.canonical(o)[-1:],b"\n")
        self.assertNotEqual(B.sha(B.canonical(o)), B.sha(B_V1.canonical(o)))
        with self.assertRaises(UnicodeEncodeError):
            B.canonical({"bad":"\ud800"})

    def test_10_new_schema_rejects_old_and_alias_names(self):
        C.validate_new_schema(B.SCHEMA,role="pack")
        C.validate_new_schema(B.CHECKPOINT_SCHEMA,role="resume_metadata")
        for value in [B.OLD_B_SCHEMA,B.OLD_BC_SCHEMA,B.C_V1_SCHEMA,
                      "ttm.bc.synthetic.sft.pack.v2",
                      "ttm.bc.synthetic.sft.resume_metadata.v2",
                      "ttm.t4.science.checkpoint.v1"]:
            with self.subTest(schema=value),self.assertRaises(ValueError):
                B.verify_legacy_rejected({"schema":value})
            with self.subTest(c=value),self.assertRaises(ValueError):
                C.validate_new_schema(value,role="pack")

    def test_11_B_actual_artifacts_readable_by_independent_C_verifier(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"bundle"
            actual=B.write_bundle(root)
            independent=independent_artifact_report(root,actual)
            self.assertTrue(C.verify_seven_artifacts(root,independent))
            self.assertEqual(B.verify_bundle(root),actual)
            for key,name in C.ARTIFACT_NAMES.items():
                self.assertEqual(actual[key],hashlib.sha256((root/name).read_bytes()).hexdigest())

    def test_12_all_seven_file_content_mutations_rejected_by_C_and_B(self):
        for key,name in C.ARTIFACT_NAMES.items():
            with self.subTest(key=key),tempfile.TemporaryDirectory() as d:
                root=Path(d)/"bundle"
                manifest=B.write_bundle(root)
                c_report=independent_artifact_report(root,manifest)
                p=root/name
                p.write_bytes(p.read_bytes()+b" ")
                with self.assertRaises(ValueError):
                    B.verify_bundle(root)
                with self.assertRaises(ValueError):
                    C.verify_seven_artifacts(root,c_report)

    def test_13_all_seven_hash_fields_manifest_forgery_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"bundle"
            original=B.write_bundle(root)
            f=root/"manifest.json"
            raw=f.read_bytes()
            for key in C.ARTIFACT_NAMES:
                forged=copy.deepcopy(original);forged[key]="0"*64
                try:
                    f.write_bytes(B.canonical(forged))
                    with self.subTest(key=key),self.assertRaises(ValueError):
                        B.verify_bundle(root)
                finally:
                    f.write_bytes(raw)

    def test_14_signed_but_wrong_labels_detected_by_source_oracle(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"bundle"
            manifest=B.write_bundle(root)
            target=root/C.ARTIFACT_NAMES["target_labels_sha256"]
            document=json.loads(target.read_bytes())
            document["rows"][0]["y"][0]=42
            tampered=B.canonical(document)
            target.write_bytes(tampered)
            manifest["target_labels_sha256"]=hashlib.sha256(tampered).hexdigest()
            (root/"manifest.json").write_bytes(B.canonical(manifest))
            with self.assertRaises(ValueError):
                B.verify_bundle(root)

    def test_15_lf_and_crlf_mutations_rejected_by_B_and_C(self):
        for mutate in (lambda x:x[:-1],lambda x:x.replace(b"\n",b"\r\n")):
            with tempfile.TemporaryDirectory() as d:
                root=Path(d)/"bundle"
                manifest=B.write_bundle(root)
                c_report=independent_artifact_report(root,manifest)
                target=root/C.ARTIFACT_NAMES["config_sha256"]
                target.write_bytes(mutate(target.read_bytes()))
                with self.assertRaises(ValueError):B.verify_bundle(root)
                with self.assertRaises(ValueError):C.verify_seven_artifacts(root,c_report)

    def test_16_metadata_not_checkpoint_and_no_legacy_weights(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"bundle"
            B.write_bundle(root)
            record=json.loads((root/C.ARTIFACT_NAMES["checkpoint_schema_sha256"]).read_bytes())
            self.assertEqual(record["scope"],"METADATA_ONLY_NO_ACTUAL_CHECKPOINT")
            self.assertIs(record["resume_enabled"],False)
            self.assertEqual(record["weights"],"NOT_CREATED")
            self.assertEqual(record["optimizer_state"],"NOT_CREATED")

    def test_17_32_model_context_exact_and_no_truncation_in_pack(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"bundle"
            B.write_bundle(root)
            records=json.loads((root/C.ARTIFACT_NAMES["serialized_inputs_sha256"]).read_bytes())
            self.assertTrue(all(len(row["x"])==32 for row in records["rows"]))
        big=[{"role":"user","content":"U"*40},{"role":"assistant","content":"A"}]
        with self.assertRaises(ValueError):
            B.build(big,33)

    def test_18_b_native_model_scoped_p02_probe_no_optimizer(self):
        r=B.synthetic_cpu_probe_v2()
        self.assertEqual(r["optimizer_steps"],0)
        self.assertFalse(r["science_executed"])
        self.assertTrue(r["direct_prompt_target_ce_zero"])
        self.assertTrue(r["causal_isolated"])
        self.assertTrue(r["padding_isolated"])
        self.assertGreater(r["prompt_context_grad_l1"],0)

    def test_19_byte_identity_for_seeded_short_dialogues(self):
        rng=random.Random(20261117)
        for i in range(200):
            msgs=[{"role":"user","content":chr(65+rng.randrange(25))},
                  {"role":"assistant","content":chr(97+rng.randrange(25))}]
            if rng.randrange(2):
                msgs.insert(0,{"role":"system","content":"P"})
            ids,flags=manual_role_wire(msgs)
            self.assertEqual(B.serialize(msgs,33),(ids,flags))
            x,y=B.build(msgs,33)
            self.assertEqual(y[:len(ids)-1],
                             [ids[k] if flags[k] else -100 for k in range(1,len(ids))])

if __name__=="__main__":
    unittest.main()
