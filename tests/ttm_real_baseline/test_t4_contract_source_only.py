"""No-real-data, no-model, no-Torch source/contract QA for T4 vertical slice.

Run with python -S -B -m unittest discover ... Python 3.12.
All artifacts and token NLL values in this suite are synthetic declarations.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import unittest

from src.ttm_real_baseline.typed_admission import (
    BASE_MAIN_SHA, BPE_SCHEMA, CHECKPOINT_SCHEMA, EXACT_SOURCE_BLOBS,
    PACK_SCHEMA, READY_SCHEMA, SCHEMA, T4_CONFIG, ContractHold,
    inspect_declarations,
)
from src.ttm_real_baseline.byte_eval_contract import (
    ByteDomainHold, arithmetic_bpb,
)


ROOT = Path(__file__).resolve().parents[2]


def fake_sha(name: str) -> str:
    return hashlib.sha256(("TTM_FAKE_FIXTURE_NOT_REAL:" + name).encode()).hexdigest()


def synthetic_packet() -> dict:
    """Fake metadata, not an attestation or any real private source."""
    values = {n: fake_sha(n) for n in (
        "checkpoint", "pack", "bpe_file", "bpe_manifest", "bpe_merges",
        "raw_source", "split", "science_lock", "progress",
    )}
    return {
        "schema": SCHEMA,
        "source": {"main_commit": BASE_MAIN_SHA, "git_blobs": dict(EXACT_SOURCE_BLOBS)},
        "tokenizer": {
            "schema": BPE_SCHEMA,
            "file_sha256": values["bpe_file"],
            "manifest_sha256": values["bpe_manifest"],
            "token_merges_sha256": values["bpe_merges"],
            "vocab_size": 2048, "eos_id": 256, "merges": 1791, "trained_on": "TRAIN_ONLY",
        },
        "pack": {
            "schema": PACK_SCHEMA, "npz_sha256": values["pack"], "npz_bytes": 12000,
            "t1_bpe_file_sha256": values["bpe_file"],
            "t1_bpe_internal_sha256": values["bpe_manifest"],
            "source_sha256": values["raw_source"], "t1_split_sha256": values["split"],
            "contains_test": False, "contains_raw_text": False, "context": 256,
        },
        "checkpoint": {
            "file_sha256": values["checkpoint"],
            "ready": {
                "schema": READY_SCHEMA, "sha256": values["checkpoint"],
                "bytes": 100_000, "step": 512, "checkpoint": "checkpoint.pt",
                "train_pack_sha256": values["pack"],
                "science_lock_sha256": values["science_lock"],
                "progress_sha256": values["progress"],
            },
            "declared_header": {
                "schema": CHECKPOINT_SCHEMA, "step": 512,
                "p02_git_blob": EXACT_SOURCE_BLOBS["P02"], "config": dict(T4_CONFIG),
                "science_lock_sha256": values["science_lock"],
                "train_pack_sha256": values["pack"],
            },
        },
        "codec": {
            "kind": "T4_TRAIN_ONLY_BPE2048", "direct_bc_v2_alias": False,
            "external_role_byte_sidecar": "DESIGN_ONLY_NOT_IMPLEMENTED",
        },
        "evaluation": {
            "primary": "C_VALID_UTF8_BYTE_BPB", "a_i1": "PASS_SCOPED_MEASUREMENT_ONLY",
            "gold_source": "HOLD_REAL_EVIDENCE_MISSING",
            "fresh_val": "HOLD_REAL_EVIDENCE_MISSING",
            "byte_spans": "HOLD_REAL_EVIDENCE_MISSING",
        },
        "authority": {
            "q4": "HOLD", "i2": "HOLD",
            "checkpoint_read": False, "real_data_read": False,
            "gpu": False, "science": False, "new_test": False,
            "rights": "UNVERIFIED", "native_resource": "UNVERIFIED",
            "independent_real_qa": "UNVERIFIED",
        },
    }


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def git_source(path: str) -> bytes:
    result = subprocess.run(["git", "cat-file", "blob", "HEAD:" + path],
                            cwd=ROOT, capture_output=True, check=True)
    return result.stdout


class TestT4MetadataAdmission(unittest.TestCase):
    def test_01_only_declarative_pass_never_runtime_go(self):
        out = inspect_declarations(synthetic_packet())
        self.assertEqual(out["status"], "PASS_DECLARED_SOURCE_RELATIONSHIPS_ONLY")
        self.assertFalse(out["authorizes_q4"])
        self.assertFalse(out["authorizes_i2"])
        self.assertFalse(out["authorizes_checkpoint_or_data_read"])
        self.assertEqual(out["physical_byte_custody"], "UNVERIFIED")

    def test_02_source_git_pins_exact_main_object(self):
        paths = {
            "P02": "src/p02/transformer_core.py",
            "T4_CAPACITY": "tools/pilot_t4/integrated/t4_capacity_smoke.py",
            "T4_TRAIN": "tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py",
            "T4_PACK": "tools/pilot_t4/integrated/t4_data_pack.py",
            "T4_BPE": "tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py",
            "B_SYNTHETIC_LOADER": "src/ttm_track_b/scaffold.py",
            "C_REGISTRY": "artifacts/ttm-abc/track-c/C_SCIENCE_REQUIREMENTS_AND_A_C_COMPATIBILITY_20261117.json",
        }
        self.assertEqual(set(paths), set(EXACT_SOURCE_BLOBS))
        for k, p in paths.items():
            with self.subTest(role=k):
                self.assertEqual(git_blob_sha(git_source(p)), EXACT_SOURCE_BLOBS[k])

    def test_03_wrong_source_blob_rejected(self):
        pkt = synthetic_packet()
        pkt["source"]["git_blobs"]["T4_PACK"] = "0" * 40
        with self.assertRaisesRegex(ContractHold, "PINNED_GIT_SOURCE_MISMATCH"):
            inspect_declarations(pkt)

    def test_04_BPE_file_and_manifest_sha_are_distinct_typed_links(self):
        p = synthetic_packet()
        p["pack"]["t1_bpe_file_sha256"] = p["tokenizer"]["manifest_sha256"]
        with self.assertRaisesRegex(ContractHold, "BPE_FILE_SHA_DOMAIN_MISMATCH"):
            inspect_declarations(p)
        p = synthetic_packet()
        p["pack"]["t1_bpe_internal_sha256"] = p["tokenizer"]["file_sha256"]
        with self.assertRaisesRegex(ContractHold, "BPE_INTERNAL_MANIFEST_SHA_DOMAIN_MISMATCH"):
            inspect_declarations(p)

    def test_05_ready_train_pack_pin_not_tokenizer_sha(self):
        p = synthetic_packet()
        p["checkpoint"]["ready"]["train_pack_sha256"] = p["tokenizer"]["file_sha256"]
        with self.assertRaisesRegex(ContractHold, "READY_TRAIN_PACK_SHA_MISMATCH"):
            inspect_declarations(p)

    def test_06_payload_header_pack_pin_checked_independently(self):
        p = synthetic_packet()
        p["checkpoint"]["declared_header"]["train_pack_sha256"] = p["tokenizer"]["file_sha256"]
        with self.assertRaisesRegex(ContractHold, "T4_CHECKPOINT_TRAIN_PACK_SHA_MISMATCH"):
            inspect_declarations(p)

    def test_07_ready_checkpoint_file_pin_and_bytes(self):
        p = synthetic_packet()
        p["checkpoint"]["ready"]["sha256"] = fake_sha("other-file")
        with self.assertRaisesRegex(ContractHold, "READY_CHECKPOINT_FILE_SHA_MISMATCH"):
            inspect_declarations(p)
        p = synthetic_packet()
        p["checkpoint"]["ready"]["bytes"] = 0
        with self.assertRaisesRegex(ContractHold, "INVALID_POSITIVE_INTEGER"):
            inspect_declarations(p)

    def test_08_checkpoint_schema_config_and_step(self):
        for key, val, code in (
            ("schema", "ttm.p04.model_checkpoint.v1", "SCHEMA_MISMATCH"),
            ("step", 1024, "STEP_MISMATCH"),
        ):
            p = synthetic_packet()
            p["checkpoint"]["declared_header"][key] = val
            with self.subTest(key=key), self.assertRaisesRegex(ContractHold, code):
                inspect_declarations(p)
        p = synthetic_packet()
        p["checkpoint"]["declared_header"]["config"]["n_layer"] = 8
        with self.assertRaisesRegex(ContractHold, "T4_MODEL_CONFIG_MISMATCH"):
            inspect_declarations(p)

    def test_09_reject_P04_and_BC_checkpoint_as_real_T4(self):
        p = synthetic_packet()
        p["checkpoint"]["declared_header"]["schema"] = "ttm.bc.synthetic.sft_checkpoint.v2"
        with self.assertRaisesRegex(ContractHold, "T4_CHECKPOINT_SCHEMA_MISMATCH"):
            inspect_declarations(p)
        p = synthetic_packet()
        p["checkpoint"]["ready"]["schema"] = "ttm.track_b.checkpoint.ready.v1"
        with self.assertRaisesRegex(ContractHold, "T4_READY_SCHEMA_MISMATCH"):
            inspect_declarations(p)

    def test_10_no_direct_T4_to_BC_token_alias(self):
        p = synthetic_packet()
        p["codec"]["direct_bc_v2_alias"] = True
        with self.assertRaisesRegex(ContractHold, "IDS_257_TO_262_COLLIDE"):
            inspect_declarations(p)
        p = synthetic_packet()
        p["codec"]["external_role_byte_sidecar"] = "IMPLEMENTED"
        with self.assertRaisesRegex(ContractHold, "PROSPECTIVE_CODEC_UNVERIFIED"):
            inspect_declarations(p)

    def test_11_no_false_rights_or_Q4_grant(self):
        for key, val, code in (
            ("q4", "GO", "UNAUTHORIZED_Q4_GO"),
            ("i2", "GO", "UNAUTHORIZED_I2_GO"),
            ("checkpoint_read", True, "UNAUTHORIZED_EXECUTION"),
            ("real_data_read", True, "UNAUTHORIZED_EXECUTION"),
            ("science", True, "UNAUTHORIZED_EXECUTION"),
            ("rights", "ATTESTED", "FALSE_ATTESTATION"),
        ):
            p = synthetic_packet()
            p["authority"][key] = val
            with self.subTest(key=key), self.assertRaisesRegex(ContractHold, code):
                inspect_declarations(p)

    def test_12_no_TEST_or_raw_story_in_T4_pack(self):
        for key in ("contains_test", "contains_raw_text"):
            p = synthetic_packet()
            p["pack"][key] = True
            with self.subTest(key=key), self.assertRaisesRegex(ContractHold, "FORBIDDEN"):
                inspect_declarations(p)

    def test_13_reject_invalid_or_unknown_source_field(self):
        p = synthetic_packet()
        p["tokenizer"]["file_sha256"] = "UPPERCASE-NOT-HEX"
        with self.assertRaisesRegex(ContractHold, "INVALID_SHA_DOMAIN"):
            inspect_declarations(p)
        p = synthetic_packet()
        p["checkpoint"]["unsafe_pickle_allowed"] = True
        with self.assertRaisesRegex(ContractHold, "SCHEMA_KEYS_MISMATCH"):
            inspect_declarations(p)

    def test_14_historical_B_loader_contains_known_SHA_alias_bug(self):
        s = git_source("src/ttm_track_b/scaffold.py").decode()
        self.assertIn('if tokenizer_sha != cp["train_pack_sha256"]:', s)
        self.assertIn('cp["bpe_merges_sha256"] != tokenizer_sha', s)
        # This candidate does not call or patch that loader.
        self.assertEqual(inspect_declarations(synthetic_packet())["real_model_run"], False)

    def test_15_T4_source_fields_match_proposed_contract(self):
        trainer = git_source("tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py").decode()
        pack = git_source("tools/pilot_t4/integrated/t4_data_pack.py").decode()
        bpe = git_source("tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py").decode()
        for s in ('ttm.t4.science.checkpoint.v1', "'train_pack_sha256':pack_sha",
                  "'p02_git_blob':P02_BLOB", "'model':model.state_dict()"):
            self.assertIn(s, trainer)
        for s in ("'t1_bpe_file_sha256':BPE_FILE_SHA",
                  "'t1_bpe_internal_sha256':bpe_raw['manifest_sha256']",
                  "'npz_sha256':file_sha(dat)"):
            self.assertIn(s, pack)
        self.assertIn("MODEL_NAME = 'ttm.gpt2.pretokenized.byte-bpe.2048.v1'", bpe)
        self.assertIn("EOS_ID = 256", bpe)
        self.assertIn("N_MERGES = 1791", bpe)


class TestUTF8ByteDomain(unittest.TestCase):
    @staticmethod
    def rows():
        return [
            {"token_id": 262, "kind": "TEXT", "start": 0, "end": 1,
             "gold_nll_nats": 0.7},
            {"token_id": 300, "kind": "TEXT", "start": 1, "end": 3,
             "gold_nll_nats": 1.4},
            {"token_id": 256, "kind": "EOS", "start": None, "end": None,
             "gold_nll_nats": None},
        ]

    def test_16_multibyte_utf8_not_one_token_one_byte(self):
        r = arithmetic_bpb("aá".encode("utf8"), self.rows())
        self.assertEqual(r["valid_utf8_bytes"], 3)
        self.assertEqual(r["text_target_count"], 2)
        self.assertAlmostEqual(r["text_nll_sum_nats"], 2.1)
        self.assertAlmostEqual(r["text_val_bpb_arithmetic_only"], 2.1 / (3 * math.log(2)))
        self.assertFalse(r["authorized_for_real_science"])

    def test_17_T4_merge_id_262_is_valid_text_not_BC_EOT(self):
        r = arithmetic_bpb(b"x", [
            {"token_id": 262, "kind": "TEXT", "start": 0, "end": 1,
             "gold_nll_nats": 0.5}
        ])
        self.assertEqual(r["text_target_count"], 1)

    def test_18_EOS_excludes_stop_nll_and_bytes(self):
        result = arithmetic_bpb(b"X", [
            {"token_id": 88, "kind": "TEXT", "start": 0, "end": 1, "gold_nll_nats": 1.0},
            {"token_id": 256, "kind": "EOS", "start": None, "end": None, "gold_nll_nats": None},
        ])
        self.assertEqual(result["text_nll_sum_nats"], 1.0)
        self.assertEqual(result["valid_utf8_bytes"], 1)
        with self.assertRaisesRegex(ByteDomainHold, "EOS_MUST_HAVE_NO_RAW_BYTES_OR_NLL"):
            arithmetic_bpb(b"X", [
                {"token_id": 88, "kind": "TEXT", "start": 0, "end": 1, "gold_nll_nats": 1.0},
                {"token_id": 256, "kind": "EOS", "start": None, "end": None, "gold_nll_nats": 2.0},
            ])

    def test_19_T4_EOS_cannot_be_scored_text(self):
        row = {"token_id": 256, "kind": "TEXT", "start": 0, "end": 1, "gold_nll_nats": 0.2}
        with self.assertRaisesRegex(ByteDomainHold, "T4_TEXT_ROLE_OR_EOS_ALIAS"):
            arithmetic_bpb(b"x", [row])

    def test_20_invalid_UTF8_rejected(self):
        with self.assertRaisesRegex(ByteDomainHold, "INVALID_UTF8"):
            arithmetic_bpb(b"\xff", self.rows())

    def test_21_noncontiguous_overlap_and_uncovered_rejected(self):
        for first, second in ((0, 2), (1, 2)):
            rows = self.rows()
            rows[0]["start"] = first
            rows[1]["start"] = second
            with self.subTest(first=first, second=second):
                with self.assertRaises(ByteDomainHold):
                    arithmetic_bpb("aá".encode("utf8"), rows)
        rows = self.rows()[:1]
        with self.assertRaisesRegex(ByteDomainHold, "RAW_TEXT_NOT_COVERED"):
            arithmetic_bpb("aá".encode("utf8"), rows)

    def test_22_nonfinite_negative_NLL_rejected(self):
        for value in (float("nan"), float("inf"), -1.0, "0.1"):
            rows = self.rows()
            rows[0]["gold_nll_nats"] = value
            with self.subTest(value=str(value)), self.assertRaisesRegex(
                ByteDomainHold, "NONFINITE_OR_NEGATIVE_NLL"
            ):
                arithmetic_bpb("aá".encode("utf8"), rows)

    def test_23_no_after_EOS_text_or_forged_role(self):
        rows = self.rows()
        rows.append({"token_id": 262, "kind": "TEXT", "start": 3, "end": 4,
                     "gold_nll_nats": 0.5})
        with self.assertRaisesRegex(ByteDomainHold, "T4_TEXT_ROLE_OR_EOS_ALIAS"):
            arithmetic_bpb("aáb".encode("utf8"), rows)
        rows = self.rows()
        rows[0]["kind"] = "BC_EOT"
        with self.assertRaisesRegex(ByteDomainHold, "T4_TEXT_ROLE_OR_EOS_ALIAS"):
            arithmetic_bpb("aá".encode("utf8"), rows)

    def test_24_output_explicitly_denies_science_provenance(self):
        result = arithmetic_bpb("aá".encode("utf8"), self.rows())
        self.assertEqual(result["full_vocab_nll_provenance"],
                         "UNVERIFIED_EXTERNAL_A_SCORER_REQUIRED")
        self.assertEqual(result["raw_byte_span_authenticity"],
                         "UNVERIFIED_REAL_SOURCE_REQUIRED")
        self.assertFalse(result["authorized_for_real_science"])


    def test_25_integrated_Q4_ledger_is_not_a_release_token(self):
        p = "artifacts/ttm-real-baseline/TTM_PM_T4_ABC_R0_R8_ADMISSION_LEDGER_20261117.json"
        d = json.loads(git_source(p).decode("utf-8"))
        self.assertEqual(d["source_main_sha"], BASE_MAIN_SHA)
        self.assertEqual(d["source_pins"], EXACT_SOURCE_BLOBS)
        self.assertEqual([x["gate"] for x in d["gates"]],
                         ["R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"])
        self.assertTrue(all(x["status"].startswith("HOLD")
                            for x in d["gates"][1:]))
        self.assertEqual(d["owner_q4_decision"], "HOLD_REAL_VERTICAL_SLICE")
        self.assertEqual(d["gates"][0]["status"], "PASS_SOURCE_CONTRACT_SCOPED")
        self.assertEqual(d["source_contract_result"],
                         "PASS_SOURCE_CONTRACT_SCOPED_NOT_PHYSICAL_CUSTODY")
        report = git_source(
            "docs/architecture/"
            "TTM_PM_REAL_GPT_T4_VERTICAL_SLICE_ABC_ADAPTER_ADMISSION_ONEPACK_20261117.md"
        ).decode("utf-8")
        self.assertIn("**25/25** test mỗi hệ", report)
        self.assertIn("R0_PASS_SOURCE_CONTRACT_SCOPED", report)
        self.assertNotIn("**24/24** test mỗi hệ", report)
        self.assertNotIn("R0_CANDIDATE_PENDING_QA", report)
        self.assertFalse(d["model_checkpoint_access_authorized"])
        self.assertFalse(d["scientific_run_authorized"])
        self.assertFalse(d["gpu_execution_authorized"])
        self.assertFalse(d["private_dataset_access_authorized"])
        self.assertIn("NOT_GENERIC_E2E_SOURCE_MERGE_GATE", d["i2_scope"])


if __name__ == "__main__":
    unittest.main()
