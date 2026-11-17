"""Distinct PM source-only QA for the *combined* exact B34->BC36->B37 + C35 tree.

Only Python stdlib; no model import/load, no real data, no GPU, no training,
no network I/O, no mutation outside unittest fixtures. Scope: design/engineering
contracts, not science or owner release authority.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
C_REF = "4efe93ce0a3910c449972b3f7e9911a004fe2b3c"
C_BLOB = "364a15d305b71e0c236a27409430f1e27e14aa70"
A_REQ_BLOB = "3de320f1e734c7610fb750477803b082fefff753"
B_REF = "ff4304e04f44de69a07cd767b2a7f400d6e95e88"

C_REG = Path("artifacts/ttm-abc/track-c/C_SCIENCE_REQUIREMENTS_AND_A_C_COMPATIBILITY_20261117.json")
B_REG = Path("artifacts/ttm-abc/track-b/B_ABC_CCR01_EXACT_C_37_26_14_REMAP_20261117.json")
MANIFEST = Path("artifacts/ttm-abc/bc-sft/v2/MANIFEST_CANONICAL_LF.json")
ART_ROOT = Path("artifacts/ttm-abc/bc-sft/v2/actual_bytes")


def read(path: Path) -> bytes:
    return (ROOT / path).read_bytes()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class PMCombinedSourceOnlyQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.c_raw = read(C_REG)
        cls.c = json.loads(cls.c_raw)
        cls.b = json.loads(read(B_REG))

    def test_01_exact_independent_git_blob_pins(self) -> None:
        pins = {
            C_REG: C_BLOB,
            B_REG: "c2d4a050f35218de2c023d3a5c50fb3454404c23",
            Path("src/ttm_track_b/bc_sft_bridge_v2.py"):
                "c56d98b520fef387fab43bac87b7a9247287b17c",
            Path("src/ttm_track_b/bc_sft_interface.py"):
                "636a7d695e49802e3d8d80ab0ef06f25ef7d8322",
            Path("tests/ttm_track_c/bc_v2_contract_oracle.py"):
                "9ae5e8b189b361a496bc7bfd9ec0342bc24a7e72",
            Path("tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py"):
                "fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6",
        }
        for path, expected in pins.items():
            with self.subTest(path=str(path)):
                self.assertEqual(git_blob(read(path)), expected)
        self.assertEqual(hashlib.sha256(self.c_raw).hexdigest(),
                         "6db387c75e3f2f0ae8b05af65f66cfddf025ad2ba06d562e8645a16f9f0aab1d")
        self.assertEqual(self.c["sources"]["a_requirements_git_blob"], A_REQ_BLOB)
        self.assertEqual(self.b["input_pins"]["A_requirement_blob"], A_REQ_BLOB)
        self.assertEqual(self.b["input_pins"]["C_registry_blob"], C_BLOB)
        self.assertEqual(self.b["input_pins"]["C_packet"], C_REF)

    def test_02_37_26_14_exact_names_types_units_masks_domains(self) -> None:
        b, c = self.b, self.c
        aa, cc, bb = b["A37"], b["C26"], b["B14"]
        a_ref = c["original_A_37_field_crosswalk"]
        c_ref = c["C_B_additional_logical_requirements"]
        b_ref = c["ASSUMPTIONS_REQUIRING_B"]
        self.assertEqual([len(aa), len(cc), len(bb)], [37, 26, 14])
        self.assertEqual(len({x["field"] for x in aa + cc}), 63)
        self.assertTrue({x["field"] for x in bb}.issubset({x["field"] for x in cc}))
        comparisons = 0
        a_map = {
            "field": "field", "owner": "owner", "expected_type": "type",
            "unit": "unit", "byte_domain": "byte_domain",
            "validation": "validation", "negative_case": "C_negative_case",
            "hold": "hold", "C_disposition": "C_disposition",
        }
        c_map = {
            "field": "field", "owner": "owner", "expected_type": "type",
            "unit": "unit", "byte_domain": "byte_domain",
            "validation": "validation", "negative_case": "negative_case",
            "hold": "hold", "source_requirement_blob": None,
        }
        for i, (row, src) in enumerate(zip(aa, a_ref, strict=True)):
            for dest, original in a_map.items():
                with self.subTest(group="A37", i=i, field=dest):
                    self.assertEqual(row[dest], src[original])
                comparisons += 1
            self.assertEqual(row["source_requirement_blob"], A_REQ_BLOB)
        for i, (row, src) in enumerate(zip(cc, c_ref, strict=True)):
            for dest in ("field", "owner", "expected_type", "unit",
                         "byte_domain", "validation", "negative_case", "hold"):
                original = "type" if dest == "expected_type" else dest
                with self.subTest(group="C26", i=i, field=dest):
                    self.assertEqual(row[dest], src[original])
                comparisons += 1
            self.assertEqual(row["source_requirement_commit"], C_REF)
            self.assertEqual(row["source_requirement_blob"], C_BLOB)
        for i, (row, src) in enumerate(zip(bb, b_ref, strict=True)):
            for dest in ("field", "expected_type", "unit", "byte_domain", "negative_case"):
                with self.subTest(group="B14", i=i, field=dest):
                    self.assertEqual(row[dest], src[dest])
                comparisons += 1
            self.assertEqual(row["source_requirement_blob"], C_BLOB)
        self.assertEqual(comparisons, 37*9 + 26*8 + 14*5)
        self.assertEqual(comparisons, 611)
        # Previous PM 637 comparison counted a ninth C property elsewhere; here
        # exact 611 nonredundant matched fields + source pin checks above.

    def test_03_existing_B_statuses_not_promoted(self) -> None:
        self.assertEqual(Counter(r["status"] for r in self.b["A37"]),
                         {"EXACT_MATCH": 10, "ADAPTER_DESIGN_REQUIRED": 12,
                          "NOT_PROVEN": 14, "INCOMPATIBLE": 1})
        self.assertEqual(Counter(r["status"] for r in self.b["C26"]),
                         {"ADAPTER_DESIGN_REQUIRED": 9, "NOT_PROVEN": 17})
        self.assertEqual(Counter(r["status"] for r in self.b["B14"]),
                         {"ADAPTER_DESIGN_REQUIRED": 7, "NOT_PROVEN": 7})
        self.assertTrue(self.c["real_sft"] != "GO")

    def test_04_existed_seven_artifact_files_exact_sha256(self) -> None:
        m = json.loads(read(MANIFEST))
        self.assertEqual(m["bridge_schema"], "ttm.bc.c_string_to_b_bytes.v2")
        self.assertEqual(len(m["artifact_filenames"]), 7)
        self.assertTrue(m["no_science"] and m["synthetic_only"])
        for key, filename in m["artifact_filenames"].items():
            with self.subTest(key=key):
                blob = read(ART_ROOT / filename)
                self.assertEqual(hashlib.sha256(blob).hexdigest(), m[key])
                self.assertTrue(blob.endswith(b"\n"))
                self.assertFalse(blob.endswith(b"\n\n"))
                self.assertNotIn(b"\r\n", blob)

    def test_05_direct_T4_BC_token_alias_remains_incompatible(self) -> None:
        # The two existing source byte streams are pinned in test_01.
        bpe = read(Path("tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py")).decode("utf-8")
        bc = read(Path("src/ttm_track_b/bc_sft_interface.py")).decode("utf-8")
        self.assertIn("EOS_ID = 256", bpe)
        self.assertIn("N_MERGES = 1791", bpe)
        self.assertIn("new_id=257+rank", bpe)
        self.assertIn("PAD, BOS, SYS, USER, ASSIST, EOT, EOS = 257, 258, 259, 260, 261, 262, 256", bc)
        self.assertIn("T4_NATIVE_BPE_EXTERNAL_ROLE_BYTE_SPAN_DESIGN_ONLY",
                      read(Path("docs/coordination/ttm-abc/track-c/C_ABC_F01_F02_F03_INTEGRATED_ALIGNMENT_AMENDMENT_V2_20261117.md")).decode("utf-8"))
        # No attempt to load real T4 weights or claim sidecar has been implemented.


if __name__ == "__main__":
    unittest.main()
