# TTM VM V4 R8 G2 — Owner Windows three-venv readback and runtime reconciliation

**Operation:** `TTM_VM_V4_R8_G2_OWNER_WINDOWS_PROTECTED_TRUST_BOUNDARY_INTEGRATED_PREEXEC_SINGLE_GATE`  
**Date:** 2026-11-15 (Asia/Bangkok)  
**Role:** Implementation Agent · `OWNER_REPORTED_LOCAL_OUTPUT` (not independent QA)  
**Decision:** **`G2_HOLD · HOLD_INTEGRATED`**.

## 1. Owner-reported exact local readback

The owner supplied an exit-code-successful read-only diagnostic run of pinned script commit `d57ddbf6e2bcb939d0642f290be4433a8bc5f110`, after verifying original G2 receipt SHA-256. No original receipt private content was provided to the implementation agent.

```text
ORIGINAL_G2_RECEIPT=PASS_SHA256_PRESERVED
CANDIDATE=P07_XPU
CANDIDATE_EXE_SHA_P07_XPU=PASS_HISTORICAL_HASH
PYVENV_CFG_P07_XPU=PRESENT
PROBE_STATE_P07_XPU=PASS_JSON
PYTHON_VERSION_P07_XPU=3.12.10
VENV_PREFIX_BOUND_P07_XPU=PASS
PACKAGE_P07_XPU_numpy=NOT_INSTALLED
PACKAGE_P07_XPU_scipy=NOT_INSTALLED
PACKAGE_P07_XPU_scikit-learn=NOT_INSTALLED
PACKAGE_P07_XPU_joblib=NOT_INSTALLED
PACKAGE_P07_XPU_threadpoolctl=NOT_INSTALLED
VERSION_METADATA_P07_XPU=HOLD_MISMATCH
CANDIDATE=GEMMA2_A0D
CANDIDATE_EXE_SHA_GEMMA2_A0D=PASS_HISTORICAL_HASH
PYVENV_CFG_GEMMA2_A0D=PRESENT
PROBE_STATE_GEMMA2_A0D=PASS_JSON
PYTHON_VERSION_GEMMA2_A0D=3.12.10
VENV_PREFIX_BOUND_GEMMA2_A0D=PASS
PACKAGE_GEMMA2_A0D_numpy=2.4.4
PACKAGE_GEMMA2_A0D_scipy=1.17.1
PACKAGE_GEMMA2_A0D_scikit-learn=1.8.0
PACKAGE_GEMMA2_A0D_joblib=1.5.3
PACKAGE_GEMMA2_A0D_threadpoolctl=3.6.0
VERSION_METADATA_GEMMA2_A0D=HOLD_MISMATCH
CANDIDATE=R8_G2_EXACT
CANDIDATE_EXE_SHA_R8_G2_EXACT=PASS_HISTORICAL_HASH
PYVENV_CFG_R8_G2_EXACT=PRESENT
PROBE_STATE_R8_G2_EXACT=PASS_JSON
PYTHON_VERSION_R8_G2_EXACT=3.12.10
VENV_PREFIX_BOUND_R8_G2_EXACT=PASS
PACKAGE_R8_G2_EXACT_numpy=2.3.5
PACKAGE_R8_G2_EXACT_scipy=1.17.0
PACKAGE_R8_G2_EXACT_scikit-learn=1.8.0
PACKAGE_R8_G2_EXACT_joblib=1.5.3
PACKAGE_R8_G2_EXACT_threadpoolctl=3.6.0
VERSION_METADATA_R8_G2_EXACT=PASS_SCOPED
R8_G2_EXECUTABLE_MATCH=PASS_SHA_ONLY
R8_G2_VERSION_METADATA=PASS_SCOPED
RUNTIME_ORIGINAL_MANIFEST_AND_LOADED_MODULE_SHA=NOT_ATTESTED
PRODUCTION_CUSTODY_HMAC_V2=NOT_EXECUTED
R8=NOT_GENERATED
G3=NOT_EXECUTED
G2=HOLD_INTEGRATED
```

## 2. Interpretation

| Exact venv candidate | SHA of python.exe | Python/prefix | Package metadata contract | Scoped decision |
| --- | --- | --- | --- | --- |
| `_runtime/p07/venv_xpu_cp312` | same historical exact SHA | 3.12.10 / prefix match | five required dependencies absent in that environment | `HOLD_NOT_R8_RUNTIME` |
| `_tmp/ttm_gemma2_a0d_isolated_offline_bfd60812929e47c884391da954057d8c/venv` | same historical exact SHA | 3.12.10 / prefix match | NumPy 2.4.4, SciPy 1.17.1 are **different** from frozen R8 pins | `HOLD_RUNTIME_VERSION_MISMATCH` |
| `_tmp/TTM_VM_R8_G2_EXACT_RUNTIME_20261115/venv` | same historical exact SHA | 3.12.10 / prefix match | NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, joblib 1.5.3, threadpoolctl 3.6.0 | `PASS_SCOPED_EXE_PREFIX_AND_METADATA_ONLY` |

The [G2 residual closeout from 3ca8d799](https://github.com/minhtri22/TokenToModel-Lab/blob/3ca8d7993bc6921adc507cd4c9cf7d839e92141e/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_THREE_RESIDUAL_CONDITIONS_INTEGRATED_CLOSEOUT_20261115.md) reported a prior isolated runtime with wheel RECORD integrity, native imports, verified loaded module bytes and a local runtime receipt. The **current** output establishes a plausible path for that environment, not a new verification of those hashes or access control. Identical `python.exe` SHA values do not imply identical virtual environments.

## 3. Preservation and unresolved

- Existing one-shot receipt SHA-256 `c0bf90955d09501b5dcdb7ab912635a666895b23c5c855494ddfb7381ce37795`: preserved according to owner's earlier and current read-only output; private file contents not published.
- Protected source 5/5: inherited `PASS_SCOPED_OWNER_REPORTED` from current owner's prior readback. No new scientific source modifications.
- Exact original runtime manifest, wheel/RECORD readback and imported native modules on today's system: **`NOT_ATTESTED`**.
- Actual DPAPI HMAC key, G_pre commitment, production mandatory launcher and G3: **`NOT_EXECUTED` / `NOT_ATTESTED`**.
- Retention amendment independent acceptance: **`HOLD`**.
- Recovery: **`NOT_VERIFIED`**; owner backup waiver is only for R8-D exploratory.
- `G0=PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW`, `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `GPU=NO`, `READER=0`, `PROBE256=SEALED`.

**Adjudication:** `RUNTIME_EXE_AND_VERSIONS=PASS_SCOPED_R8_G2_EXACT` · `RUNTIME_FULL_BYTE_MANIFEST=NOT_ATTESTED` · **`G2_HOLD_INTEGRATED`**. No merge, G3 authorization, new key, or R8 authoring.
