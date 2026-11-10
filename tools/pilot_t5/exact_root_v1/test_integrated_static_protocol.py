#!/usr/bin/env python3
"""Read-only source/prereg/static QA; never loads a model or calls C++."""
import ast
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[3]
S=ROOT/"tools/pilot_t5/exact_root_v1"
P=ROOT/"artifacts/qa/ttm-t5-parity/TTM_T5_EXACT_FIRST_OP_NEW_FIXTURES_INTEGRATED_PREREG_20261110.json"
EXPECTED_PREREG="82fdd9fe716579181db648caa69170fb63d115a6"
FILENAMES=[
"p02_firstop_discovery_reference.py",
"prepare_isolated_llama_trace_gelu_sources.py",
"independent_firstop_signed_tensor_audit.py",
"run_owner_discovery_two_variants_once.py"
]

def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

class TestExactRootContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads(P.read_text("utf-8"))
        cls.src={name:(S/name).read_text("utf-8") for name in FILENAMES}
        cls.cpp=(S/"ttm_t5_firstop_trace_probe.cpp").read_text("utf-8")
        cls.cmake=(S/"CMakeLists.txt").read_text("utf-8")

    def test_01_prereg_exact_blob(self):
        self.assertEqual(blob(P),EXPECTED_PREREG)

    def test_02_exact_partition_counts(self):
        self.assertEqual([(x["fixture_id"],x["partition"],len(x["token_ids"]))
            for x in self.plan["fixtures"]],
            [("D01","discovery",1),("D02","discovery",5),
             ("C01","confirmatory",2),("C02","confirmatory",4),
             ("C03","confirmatory",11),("C04","confirmatory",17)])

    def test_03_unique_new_sequences(self):
        cases=self.plan["fixtures"]
        self.assertEqual(len({tuple(x["token_ids"]) for x in cases}),6)
        self.assertTrue(all(all(257<=t<2048 for t in x["token_ids"]) for x in cases))

    def test_04_no_previous_fixture_names_in_cpp(self):
        self.assertNotIn("SYN01",self.cpp)
        self.assertIn('{"D01", {1281}}',self.cpp)
        self.assertIn('{"D02", {1406, 971, 566, 1092, 1587}}',self.cpp)

    def test_05_only_f32_no_flash_arm(self):
        self.assertEqual(self.cpp.count('{"S1_F32_NO_FLASH", GGML_TYPE_F32, LLAMA_FLASH_ATTN_TYPE_DISABLED, false}'),1)
        self.assertNotIn('{"S0"',self.cpp)

    def test_06_mandatory_pre_gelu_tensors(self):
        for name in ("Qcur-0","Kcur-0","Vcur-0","kqv-0","kqv_out-0",
                     "attn_wo_mm-0","attn_wo_out-0","ffn_inp-0",
                     "ffn_gelu-0","result_output"):
            self.assertIn(name,self.cpp)

    def test_07_no_uncontrolled_cpp_many_rows(self):
        self.assertIn("rows!=2",self.cpp)
        self.assertIn("llama_get_logits_ith(ctx,-1)",self.cpp)
        self.assertNotIn("rows!=32",self.cpp)
        self.assertIn("TRACE_FLUSH_FAILED",self.cpp)

    def test_08_source_patches_isolated(self):
        p=self.src["prepare_isolated_llama_trace_gelu_sources.py"]
        self.assertIn('("trace_only",False),("trace_gelu_erf",True)',p)
        self.assertIn('"worktree","add","--detach"',p)
        self.assertIn('LLM_FFN_GELU_ERF, LLM_FFN_SEQ, il);',p)
        self.assertIn('cb(cur, "attn_wo_mm", il)',p)
        self.assertNotIn("git reset",p)

    def test_09_P02_pins(self):
        p=self.src["p02_firstop_discovery_reference.py"]
        self.assertIn("cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b",p)
        self.assertIn("82fdd9fe716579181db648caa69170fb63d115a6",p)
        self.assertIn("PASS_TWO_REAL_CPU_DISCOVERY_REFERENCES",p)
        self.assertIn("MANUAL_P02_FORWARD_NOT_BITWISE_IDENTICAL",p)

    def test_10_P02_does_not_run_confirmatory(self):
        p=self.src["p02_firstop_discovery_reference.py"]
        self.assertIn('x["partition"]=="discovery"',p)
        self.assertNotIn('x["partition"]=="confirmatory"',p)

    def test_11_audit_fixed_metric_and_signed_peak(self):
        p=self.src["independent_firstop_signed_tensor_audit.py"]
        self.assertIn("STRICT_LIMIT=0.001",p)
        self.assertIn('"signed_peak":diff[worst]',p)
        self.assertIn("NATIVE_FIXTURE_OR_ARM_MISMATCH",p)
        self.assertIn("PADDED_KQ_SHAPE_NOT_RECONCILED",p)

    def test_12_runner_preserves_science(self):
        p=self.src["run_owner_discovery_two_variants_once.py"]
        self.assertIn("DISCOVERY_OR_ISOLATION_ALREADY_EXISTS_NO_RETRY",p)
        self.assertIn("CONFIRMATORY_HOLD",p)
        self.assertIn("NATIVE_32_REPLAY=NO",p)
        self.assertIn("--ff-only",p)
        self.assertEqual(p.count('T5_NATIVE_ONE_SHOT='),1)
        self.assertNotIn('"training":True',p)

    def test_13_MSCV_native_compile_required(self):
        self.assertIn("if(NOT MSVC",self.cmake)
        self.assertIn("ttm_t5_firstop_trace_probe",self.cmake)
        self.assertIn("LLAMA_SOURCE_ROOT",self.cmake)
        self.assertIn("LLAMA_BUILD_ROOT",self.cmake)

    def test_14_all_python_sources_parse(self):
        for name,src in self.src.items():
            with self.subTest(name=name):
                ast.parse(src,filename=name)

    def test_15_diagnostic_not_acceptance_threshold(self):
        self.assertEqual(self.plan["baseline"]["first_stage_sensitivity"],"1e-5_DIAGNOSTIC_ONLY_NOT_PASS_THRESHOLD")
        self.assertEqual(self.plan["source_pins"]["previously_approved_strict_threshold"],0.001)

    def test_16_confirmatory_requires_frozen_patch(self):
        self.assertTrue(self.plan["governance"]["confirmatory_requires_frozen_patch_and_independent_checker"])
        self.assertEqual(self.plan["execution_status"]["confirmatory"],"NOT_EXECUTED")

if __name__=="__main__":unittest.main(verbosity=2)
