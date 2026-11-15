# TTM VM V4 R8 G2 — Owner-reported local Windows preexec receipt

**Operation:** `TTM_VM_V4_R8_G2_OWNER_WINDOWS_PROTECTED_TRUST_BOUNDARY_INTEGRATED_PREEXEC_SINGLE_GATE`  
**Date:** 2026-11-15 (Asia/Bangkok)  
**Evidence level:** `OWNER_REPORTED_LOCAL_OUTPUT_NOT_INDEPENDENTLY_READ`  
**Disposition:** `G2_HOLD · HOLD_INTEGRATED`  
**No execution performed by this GitHub evidence record.**

## Exact source and output custody

- Fixed PowerShell 5.1 source commit: `3bf15b8f3fde05f49d10b382906602d14ba5e14b`.
- Script SHA-256: `f69a9cd4595172e901686d0e6395e0b5a071c3815f761ea025dc1e340ba7978d`.
- Existing protected owner-local receipt path (do not publish content or overwrite): `D:\WORK\RESEARCH\TokenToModel-Lab\_private\r8_custody\receipts\g2-owner-windows-protected-trust-boundary-preexec-20261115.json`.
- **Owner-reported receipt SHA-256:** `c0bf90955d09501b5dcdb7ab912635a666895b23c5c855494ddfb7381ce37795`. The agent did **not** access this private file; hash verification against the original bytes remains `NOT_INDEPENDENTLY_VERIFIED`.
- The owner's first shell invocation failed at PowerShell argument binding (empty positional string for `-ProtectedSourceRoot`) **before script execution**; a corrected invocation omitting empty named arguments subsequently produced the output below.

## Owner-supplied actual local output

```text
FROZEN_SOURCE_5_OF_5=NOT_EXECUTED_SOURCE_ROOT_NOT_PINNED
RUNTIME_EXACT_PIN=NOT_EXECUTED_PYTHON_EXE_NOT_PINNED
WINDOWS_DPAPI_CURRENTUSER_SENTINEL=PASS_SCOPED_SAME_PROFILE_ONLY
GITHUB_CLI_TRUSTED_EXECUTABLE=NOT_ATTESTED_PREAPPROVED_HASH_ABSENT_OR_MISMATCH
GITHUB_REAL_SENTINEL_ATTESTATION=PASS_SCOPED_GITHUB_SIGNED_PUBLIC_SENTINEL
PREEXEC_RECEIPT_SHA256=c0bf90955d09501b5dcdb7ab912635a666895b23c5c855494ddfb7381ce37795
G2_INTEGRATED=HOLD_INTEGRATED
R8=NOT_GENERATED
G3=NOT_EXECUTED
```

The owner reported a successful shell exit-code check after the output, but successful script termination means **receipt recording**, not G2 admission. The one-shot receipt file now exists and must not be overwritten or regenerated using the same path.

## Reconciled matrix

| Item | Decision |
| --- | --- |
| Owner DPAPI ephemeral sentinel same profile | `PASS_SCOPED_OWNER_REPORTED` |
| GitHub public signed sentinel verification | `PASS_SCOPED_OWNER_REPORTED` (also separate hosted-Windows smoke PASS) |
| Protected source 5/5 on owner device this run | `NOT_EXECUTED_SOURCE_ROOT_NOT_PINNED` |
| Exact owner Python executable + runtime this run | `NOT_EXECUTED_PYTHON_EXE_NOT_PINNED` |
| SHA pin for owner-local GitHub CLI executable | `NOT_ATTESTED_PREAPPROVED_HASH_ABSENT_OR_MISMATCH` |
| Real protected key/HMAC V2, G_pre commitment | `NOT_EXECUTED` |
| Accepted amendment, mandatory production G3 path | `HOLD` / `NOT_ATTESTED` |
| R8, G3, G4 | `NOT_GENERATED` / `NOT_EXECUTED` |
| G2 | **`HOLD_INTEGRATED`** |

## Non-destructive continuation

1. Keep the original receipt immutable. Validate its bytes locally against the owner-reported SHA-256 without printing private receipt content.
2. Read *previously authorized custody evidence* and identify exact protected frozen-source directory and Python 3.12 isolated runtime executable. Do not guess or regenerate source/key. If local source selection is ambiguous, leave `NOT_VERIFIED`.
3. Perform only a bounded, read-only follow-up check; any additional receipt must use a **new distinct filename and cross-reference the original receipt SHA-256**, never overwrite the one-shot receipt or invent prior evidence.
4. Treat GitHub CLI hash as `NOT_ATTESTED` until a preapproved executable digest is independently known; comparing the file to its own fresh hash would not establish trusted provenance.
5. Do not re-run R8, create real private HMAC key/G_pre, authorize G3, change GitHub release retention, or merge this implementation branch. A separate independent reviewer remains required for retention amendment and production admission.

**Current single gate:** `G2_HOLD · HOLD_INTEGRATED`; no `GO_R8_D_CANDIDATE_AUTHORING_ONLY`.
