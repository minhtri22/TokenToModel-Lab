# TTM VM V4 R8 G2 — Postreceipt source readback and historical Python pin reconciliation

**Operation:** `TTM_VM_V4_R8_G2_OWNER_WINDOWS_PROTECTED_TRUST_BOUNDARY_INTEGRATED_PREEXEC_SINGLE_GATE`  
**Date:** 2026-11-15 (Asia/Bangkok)  
**Role:** Implementation Agent · **Evidence grade:** `OWNER_REPORTED_OUTPUT` plus separately fetched public GitHub report; **not independent QA**.  
**Decision:** `G2_HOLD · HOLD_INTEGRATED`. Nothing authorizes R8-D/G3.

## New owner-reported Windows output (no local file access by this agent)

```text
EXISTING_G2_RECEIPT_SHA256=PASS
EXISTING_G2_RECEIPT_PRESERVED=TRUE
FROZEN_SOURCE_5_OF_5=PASS_READONLY_BYTE_MATCH
PROTECTED_SOURCE_ROOT_CANDIDATE=D:\WORK\RESEARCH\TokenToModel-Lab\_private\r8_custody\source
RUNTIME_MATCHING_VERSION_CANDIDATE=NONE_IN_BOUNDED_DISCOVERY
RUNTIME_EXACT_PIN=NOT_ATTESTED_WITHOUT_ORIGINAL_MANIFEST
REAL_HMAC_V2=NOT_EXECUTED
G3=NOT_EXECUTED
G2=HOLD_INTEGRATED
```

The user also supplied a no-error PowerShell exit-code check. These lines establish a successful **read-only hash probe**, not a new G2 approval. The existing private one-shot receipt hash, previously reported, is `c0bf90955d09501b5dcdb7ab912635a666895b23c5c855494ddfb7381ce37795`. This agent did not read the original private receipt or its bytes and does not claim independent verification.

## Exact historical runtime evidence reconciled

The prior [G2 original integrated residual report](https://github.com/minhtri22/TokenToModel-Lab/blob/3ca8d7993bc6921adc507cd4c9cf7d839e92141e/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_THREE_RESIDUAL_CONDITIONS_INTEGRATED_CLOSEOUT_20261115.md) records scoped readback and `RUNTIME_EXACT_PIN_ATTESTED` in its prior environment. Historical executable SHA-256:

```text
0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14
```

Previously observed versions: CPython 3.12.10, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, joblib 1.5.3, threadpoolctl 3.6.0. The report documents a project-local isolated runtime, wheel/RECORD integrity checks and an original private runtime receipt containing executable and loaded module paths and hashes.

**Reconciliation:** The recent `NONE_IN_BOUNDED_DISCOVERY` is not evidence that the historically verified project-local isolated runtime is gone. The prior command inspected only `PATH` Python executables and a conventional Python312 install location. Neither search proves completeness for project-local venvs, and matching a version alone is not an exact pin.

## Non-destructive follow-up implementation

- Exact [read-only script](https://github.com/minhtri22/TokenToModel-Lab/blob/2f80ebf56bd25bbaff5796f1a14313b9a9febb90/docs/research/vector-memory/r8/preexec/Find-TTM-VM-R8-G2-Historical-Python-Pin-ReadOnly-PS51.ps1)
- Script exact Git blob `604bad00f582414d747565896045e4fa7f944af2`.
- Script SHA-256 `f3bada02ac672f65acbbd9dff7755179ebd93b2915476d61d1527e47ccfe7a99`.
- Static Windows PowerShell 5.1 QA: [GitHub Actions run 43729299638](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43729299638) `completed/success`. `HISTORICAL_PYTHON_PS51_PARSE=PASS` and `HISTORICAL_PYTHON_READONLY_AST_SCOPE=PASS`; **the private runtime search was NOT executed by hosted CI**.
- Read-only probe hashes only project-root `python.exe` candidates, compares against the historical executable SHA-256, and inspects version metadata **only after exact executable SHA match**. No installation, package upgrade, receipt edit, private HMAC read, G_pre, G3 or science.
- The probe reports `RUNTIME_ORIGINAL_MANIFEST_AND_MODULE_BYTE_READBACK=NOT_ATTESTED` even if an executable hash matches. Full runtime admission also requires original manifest/loaded module pins, identity and rights.

## Preserved gate and interpretation

| Condition | State |
| --- | --- |
| Existing owner-local one-shot receipt and frozen source 5/5 | `PASS_SCOPED_OWNER_REPORTED` |
| Historical G2 exact runtime pin | `PASS_SCOPED_HISTORICAL` (inherited, not reproduced today) |
| Exact runtime executable located today | `NOT_VERIFIED` pending project-local scan |
| Current runtime manifest, module bytes, token readback | `NOT_ATTESTED` |
| Real DPAPI key/HMAC V2 and actual G_pre | `NOT_EXECUTED` |
| Production mandatory launcher, retention independent acceptance | `NOT_ATTESTED` / `HOLD` |
| Integrated G2 | **`HOLD_INTEGRATED`** |

**One continuation:** run only the committed read-only historical runtime SHA locator; preserve all old receipts and exact source pins. If the executable is missing, report `NOT_FOUND` and do not silently install a replacement or assume a historical PASS transfers to another interpreter.
