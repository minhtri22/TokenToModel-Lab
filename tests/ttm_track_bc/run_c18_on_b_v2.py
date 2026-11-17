"""Run the *unchanged exact C 18 tests* with their imported API routed to B v2.

All 18 test bodies are byte-for-byte from C HEAD 56c18e2a...;
the B compatibility module is explicitly present in this folder.
The metadata-only C test is NOT real seven-file custody, which is separate.
"""
from __future__ import annotations
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest
# Direct script invocation sets sys.path[0] to tests/ttm_track_bc, not repo root.
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import b_v2_c_oracle_compat as compat

ROOT=Path(__file__).resolve().parent
PINNED_TEST=ROOT/"test_c_part_a_wire_oracle_pinned.py"
PINNED_SOURCE=ROOT/"c_part_a_wire_oracle_pinned.py"
EXPECTED_TEST_SHA256="1237f530b0d97288d8cad003813eec400e6e9178f766fd3c3a67748ca434bcf7"
EXPECTED_SOURCE_SHA256="bbd72ecb890d74188b20ae808dd518dbbc70c3ae945b03a710b9a7bc3ba603b0"

def canonical_git_sha(path):
    # Windows checkout may CRLF-convert working tree; Git's canonical blob is LF.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n")).hexdigest()

if __name__=="__main__":
    if canonical_git_sha(PINNED_SOURCE)!=EXPECTED_SOURCE_SHA256:
        raise RuntimeError("C_ORACLE_SOURCE_PIN_MISMATCH")
    if canonical_git_sha(PINNED_TEST)!=EXPECTED_TEST_SHA256:
        raise RuntimeError("C_ORACLE_TEST_PIN_MISMATCH")
    sys.modules["bc_sft_wire_oracle"]=compat
    spec=importlib.util.spec_from_file_location("c_part_a_exact_tests_routed_to_b_v2",PINNED_TEST)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite=unittest.defaultTestLoader.loadTestsFromModule(module)
    runner=unittest.TextTestRunner(verbosity=2)
    result=runner.run(suite)
    if result.testsRun!=18 or result.failures or result.errors:
        raise SystemExit("C_PART_A_18_ON_B_V2_NOT_PASS")
    print("C_PART_A_EXACT_18_TESTS_B_V2_ROUTED_PASS=18/18")
