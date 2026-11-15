# TTM VM V4 R8 G2 — Three SHA-matched Python runtime diagnosis

**Operation:** `TTM_VM_V4_R8_G2_OWNER_WINDOWS_PROTECTED_TRUST_BOUNDARY_INTEGRATED_PREEXEC_SINGLE_GATE`
**Date:** 2026-11-15 (Asia/Bangkok)
**Actor:** Implementation Agent, **not independent reviewer**
**Current decision:** `G2_HOLD · HOLD_INTEGRATED`
**Evidence level:** `OWNER_REPORTED_LOCAL_RESULT` and separately independently read GitHub source/hosted CI

## 1. Exact latest local evidence reported by owner

```text
EXISTING_G2_RECEIPT_SHA256=PASS_NO_MUTATION
HISTORICAL_RUNTIME_EXECUTABLE_SHA256_PIN=0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14
HISTORICAL_RUNTIME_SOURCE=G2_CLOSEOUT_COMMIT_3ca8d799
PYTHON_EXE_CANDIDATE_FILES_CHECKED=5
PYTHON_EXE_HASH_ERRORS=0
HISTORICAL_PYTHON_EXE=MULTIPLE_SAME_HASH_CANDIDATES_3
```

Three historical-executable byte matches were found in existing project locations:

- `P07_XPU`: `_runtime/p07/venv_xpu_cp312/Scripts/python.exe`
- `GEMMA2_A0D`: `_tmp/ttm_gemma2_a0d_isolated_offline_bfd60812929e47c884391da954057d8c/venv/Scripts/python.exe`
- `R8_G2_EXACT`: `_tmp/TTM_VM_R8_G2_EXACT_RUNTIME_20261115/venv/Scripts/python.exe`

All three returned `PINNED_EXE_PACKAGE_PROBE=HOLD_IMPORT_OR_METADATA_EXCEPTION` from the preceding diagnostic. Its script catches multiple distinct causes under one label; **this does not establish absent packages, invalid executable hashes or corrupted runtime**. `RUNTIME_ORIGINAL_MANIFEST_AND_MODULE_BYTE_READBACK=NOT_ATTESTED`; `REAL_HMAC_V2=NOT_EXECUTED`; `G3=NOT_EXECUTED`.

## 2. Inherited independent historical runtime pin

Prior [G2 runtime report at `3ca8d799`](https://github.com/minhtri22/TokenToModel-Lab/blob/3ca8d7993bc6921adc507cd4c9cf7d839e92141e/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_THREE_RESIDUAL_CONDITIONS_INTEGRATED_CLOSEOUT_20261115.md) records `RUNTIME_EXACT_PIN_ATTESTED` for a prior scoped Windows import check, using CPython 3.12.10, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, joblib 1.5.3 and threadpoolctl 3.6.0. The executable SHA matches all three venv binaries but does **not** bind the original venv directory, `pyvenv.cfg`, installed wheel RECORD or loaded module hashes. The exact historical runtime identity is therefore not automatically transferred to any current venv.

Original owner-local G2 receipt SHA `c0bf90955d09501b5dcdb7ab912635a666895b23c5c855494ddfb7381ce37795` was verified on the owner's host in earlier diagnostics; exact protected frozen source 5/5 also passed owner-reported SHA readback. The implementation agent did not fetch private receipt content.

## 3. Remediation implementation and QA

- [GitHub-pinned read-only script](https://github.com/minhtri22/TokenToModel-Lab/blob/2a9f538dc1aac0a5062e25053b22d5c981474e49/docs/research/vector-memory/r8/preexec/Diagnose-TTM-VM-R8-G2-Three-Pinned-Python-Environments-ReadOnly-PS51.ps1) pinned to commit `2a9f538dc1aac0a5062e25053b22d5c981474e49`.
- Git blob SHA-1 `3253ac72c10e645e126a1f6235b735b55a803c83`.
- Exact UTF-8 script SHA-256 `14bd9fa6a37cfdd9af74f5b61960478fc1521666c617fe7a58029db590c483db`.
- [Hosted Windows PS5.1 CI run 43734940848](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43734940848): completed/success. PowerShell 5.1 AST, nonmutating source command scan and embedded `python -I -B -c` metadata invocation PASS. **Owner private three-venv scan NOT_EXECUTED by hosted CI**.
- Script accesses only three already reported Python files, checks each executable SHA, presence of `pyvenv.cfg`, Python 3.12.10, the five metadata package versions, and binds `sys.prefix` to the venv directory. The embedded Python uses single quotes to avoid Windows PowerShell 5.1 native double-quote forwarding problems; stderr/traceback content is not disclosed. Missing package metadata is reported per named environment.
- Script does not install packages, create or alter venvs, read HMAC/private fold, create a new G_pre, modify existing receipts, call G3, run scientific models or write to GitHub.

## 4. Exit classification

Even if `R8_G2_EXACT` returns `PASS_SCOPED` for package versions and prefix, live module byte hashes, exact original runtime manifest, protected identity/ACL and genuine pre-G3 custody remain `NOT_ATTESTED`. No claimant may treat the three identical executable hashes as equivalent runtime pinning.

`FROZEN_SOURCE_5_OF_5=PASS_SCOPED_OWNER_REPORTED`
`HISTORICAL_RUNTIME_SHA_MATCH=THREE_CANDIDATES`
`CURRENT_RUNTIME_MANIFEST_AND_MODULE_BYTE_IDENTITY=NOT_ATTESTED`
`RETENTION_AMENDMENT_INDEPENDENT_ACCEPTANCE=HOLD`
`G2=HOLD_INTEGRATED`
`R8=NOT_GENERATED` · `G3=NOT_EXECUTED` · `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`

**Single continuation:** owner runs the exact GitHub-pinned read-only three-venv diagnostic, reports only sanitized status lines. Do not retry the original one-shot preexec or fabricate a replacement private receipt.
