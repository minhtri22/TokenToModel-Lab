# TTM VM V4 R8 G2 — Exact-venv RECORD read-only audit and owner one-shot continuation

**Operation:** `TTM_VM_V4_R8_G2_OWNER_WINDOWS_PROTECTED_TRUST_BOUNDARY_INTEGRATED_PREEXEC_SINGLE_GATE`  
**Date:** 2026-11-15 (Asia/Bangkok)  
**Role:** Implementation Agent, **not independent QA**  
**Decision:** `G2_HOLD · HOLD_INTEGRATED`

## Input pin and correction

Owner's latest read-only diagnostic found three `python.exe` files with historical SHA-256
`0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14`.
Only the designated R8 G2 venv has Python 3.12.10, correct `sys.prefix` and the five exact package versions (NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, joblib 1.5.3, threadpoolctl 3.6.0).

Owner-approved environment **candidate**, not final production attestation:

```text
D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_VM_R8_G2_EXACT_RUNTIME_20261115\venv\Scripts\python.exe
```

P07 XPU lacks required metadata packages and GEMMA2 A0D has wrong NumPy/SciPy versions; neither is an alternative R8 runtime. No package installation, replacement, repair or new Python environment is warranted.

[Owner-reported readback evidence](https://github.com/minhtri22/TokenToModel-Lab/blob/7ec58312f498143949486563897abe82bcabc43a/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_THREE_ENV_OWNER_READBACK_AND_RUNTIME_RECONCILIATION_20261115.md).

## New source-only preexec diagnostic

- [Exact read-only PowerShell 5.1 script at Git commit `dd64cdab`](https://github.com/minhtri22/TokenToModel-Lab/blob/dd64cdab328cf0fd4c6d996a09dd8ce6e3367e2f/docs/research/vector-memory/r8/preexec/Verify-TTM-VM-R8-G2-Exact-Venv-Record-ReadOnly-PS51.ps1)
- Git blob SHA-1: `57a95a202f07a118f4d6c3b0c07a7d23fec51ec7`
- Script UTF-8 SHA-256: `db2c61d0bb3f75def571064396f69b14d2cea8eb522dce181959f95b59369a6f`
- [Windows PowerShell 5.1 hosted CI run 43736072447](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43736072447): `completed/success`; `EXACT_VENV_PS51_PARSE=PASS`, `EXACT_VENV_READONLY_AST=PASS`, `EMBEDDED_PYTHON_HOSTED_WINDOWS_STD_LIB=PASS_SCOPED`.
- The hosted CI did **not** inspect owner-local packages, receipt or protected source; hosted smoke cannot be used to claim full custody runtime attestation.

This script performs one bounded **read-only** audit:

1. Rehash original G2 one-shot private receipt against previously reported SHA-256 and check it again after the scan. It does not display private receipt contents.
2. Rehash frozen protected source 5/5 and the designated G2 Python executable against the exact historical pins.
3. Run only that executable with `-I -B` to inspect Python 3.12.10, exact venv `sys.prefix` and the five dependency metadata versions.
4. For those five packages, enumerate installed wheel `RECORD` members and verify on-disk SHA-256 digests, count missing/mismatched/outside-prefix/symlink/unsupported entries, and count valid native `.pyd` bytes. This deliberately does not import R8 scientific modules or read private key/fold/blueprint.
5. Compare the number of valid hashed entries against the *historical observed count of 3,636* and report `PASS_SCOPED_COUNT_3636` only if the current count exactly matches and no RECORD mismatch exists.

The script never upgrades any G2 outcome, even when RECORD is clean. Original runtime manifest and loaded native module byte hashes are still `NOT_ATTESTED` without original independent manifest/receipt cross-check, and production mandatory G3 dispatch and antirollback are still unverified.

## Gate and admission status

| Requirement | Status |
| --- | --- |
| Existing original receipt | `PASS_SHA256_PRESERVED_OWNER_REPORTED` |
| Frozen source 5/5 | `PASS_SCOPED_OWNER_REPORTED` |
| Exact G2 Python executable and metadata package versions | `PASS_SCOPED_OWNER_REPORTED` |
| Installed exact-venv RECORD hashes on owner Windows today | `NOT_EXECUTED`, pending owner one read-only audit |
| Original runtime manifest and loaded module exact bytes | `NOT_ATTESTED` |
| Real G_pre HMAC DPAPI custody / release / signed admission | `NOT_EXECUTED` / `HOLD` |
| Mandatory production G3 launcher / remote antirollback | `NOT_ATTESTED` |
| Distinct retention amendment acceptance | `HOLD` |
| G2 integrated | **`HOLD_INTEGRATED`** |

Do not rerun the original one-shot preexec; do not create, replace or delete a private receipt; no science execution, R8 generation, real HMAC key, G_pre/G3, GPU, GitHub merge or owner permit change.

**Single continuation:** the owner runs the exact pinned read-only RECORD checker once and returns **only status lines**. The Implementation Agent reconciles that with historical runtime/manifest evidence and commits a scoped conclusion to GitHub before determining whether independent QA is admissible.
