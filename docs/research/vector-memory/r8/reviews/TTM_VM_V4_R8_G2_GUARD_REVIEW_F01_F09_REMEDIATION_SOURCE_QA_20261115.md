# TTM VM V4 R8 — G2 guard remediation after distinct independent review

**Operation:** `TTM_VM_V4_R8_G2_GUARD_INDEPENDENT_F01_F09_REMEDIATION_SOURCE_QA_SINGLE_GATE`  
**Date:** 2026-11-15 (Asia/Bangkok)  
**Role:** Implementation Agent, **not independent reviewer**  
**Disposition:** `PASS_SCOPED_LOCAL_REGRESSION_35_OF_35` · `G2_HOLD` · `HOLD_INTEGRATED`.

## Exact inputs and inherited pins

- Exact distinct independent review: [`94b377ce6c0d6aa9e1d08ae4ff628c215449be1f`](https://github.com/minhtri22/TokenToModel-Lab/commit/94b377ce6c0d6aa9e1d08ae4ff628c215449be1f), with independent 22/22 Windows source fixture QA and 23 additional reviewer probes.
- Original implementation candidate: `9d210f1392e81a17f1c35cea12230bf7ff74fb02`.
- Exact frozen scientific implementation: `84d9d5c95e9962ccfe294852570e261b145fe403` — unchanged.
- Distinct reviewer findings F01–F09: [review report](https://github.com/minhtri22/TokenToModel-Lab/blob/94b377ce6c0d6aa9e1d08ae4ff628c215449be1f/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_GUARD_CANDIDATE_DISTINCT_INDEPENDENT_REVIEW_20261115.md).
- Owner backup waiver is limited to R8-D exploratory. `RECOVERY_NOT_VERIFIED`. Retention amendment `b1231fa...` remains `PROPOSED_NOT_EFFECTIVE` and needs a genuinely distinct reviewer.
- G0, protected source 5/5, and exact pinned Windows runtime PASS results are preserved, not rerun.

## Code changes — narrowly scoped

The remediation branch updates **only**:
1. `docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py`
2. `docs/research/vector-memory/r8/integrated_closure/test_pre_g3_admission_guard.py`

### Closed as scoped local regression, NOT as production trust attestation

- **F01/P14:** `fixture_mode="false"` no longer enables callback: only the literal Boolean `True` activates the synthetic fixture path. Production default is still hard denied.
- **F02/P14:** string truthy `"false"` for `immutable`, `signature_verified`, `accepted` is denied; all require identity with Boolean `True`. All-zero 40-hex amendment review commit is denied. This is **not** cryptographic reviewer authentication.
- **F05/P15/P16:** strict `published < signed < verified < accepted <= now` chronology in the mocked attestations; equal timestamp and receipt preceding verifier fail.
- **F05/P17:** second verification of the *same* anchor proof after acceptance; an anchor absent or changed at that point denies before callback. A release disappearing **after** that readback remains a trust-boundary/TOCTOU problem.
- **F06/P19/P21:** existing ledger schema must match expected constraints; non-standard trigger/view/index objects are rejected; files with more than one hardlink are denied. None of this is sufficient protection against root replacement, copied databases, malicious filesystem permissions or rollback.
- **F07/P22/P23:** NaN/Infinity and invalid Unicode/lone surrogates now produce typed `AdmissionDenied("PRIVATE_ENVELOPE_INVALID")`, not leaking `ValueError` or `UnicodeEncodeError`.
- **F08:** renamed the misleading "cross-session" test to "same-session replay through new guard instance"; no claim of replay defense across ledgers.

## Implementation QA

- Environment: local Linux sandbox, CPython 3.13.5; no R8 science, no Windows custody access.
- Command: `python -B -W error::ResourceWarning -m unittest -q test_pre_g3_admission_guard.py`.
- **35/35 PASS** (original 22 + 13 new regression methods); two spawned processes and eight threads with exactly one callback in *a single normal fixture ledger*.
- Python compile check: PASS.
- New tests explicitly cover string flags, strict chronology, anchor revocation/mutation after receipt, altered schema, hardlink, SQLite trigger, NaN, lone surrogate, and all-zero review placeholder.
- Windows Python 3.12 rerun on the amended candidate: **NOT_EXECUTED**; independent rerun: **NOT_EXECUTED**.
- Exact local source SHA-256:
  - Guard: `83dc3c1fa98ba07487d251465c88be65423085ba60ae62740db300918223f2e6`
  - Tests: `9b1725fd660c861b6fd82576bb825df592214622652a416281fddf08bccad73d`
- Git blobs:
  - Guard: `c2f4cd636ecb97b9bb2e11e737c371b469acf2e6`
  - Tests: `cba02fb7d3cf180318d015345428a2fff125dd56`

## Findings still BLOCKING admission — explicit residuals

- **F01:** `fixture_mode=True` remains externally selectable and accepts caller-injected verifier/callback. This is fixture-only proof of behavior, **never a production authorization**.
- **F02:** `AnchorProof` / `AcceptedReceipt` are caller-produced structures; no actual signed release/attestation trust root or independent reviewer signature validation exists.
- **F03:** production HMAC V2 is not recomputed using the custodian key and frozen blueprint/fold algorithm; 64-hex HMAC shape alone is insufficient.
- **F04:** source/runtime manifest hashes are not read back from current loaded artifacts and approved runtime at dispatch; string equality is insufficient.
- **F05:** remote timestamp/signed bundle provenance and immediate evidence-loss invalidation are not enforced by a trusted production verifier. The second mock check does not eliminate all TOCTOU.
- **F06:** alternate ledger file, rollback to pre-consume, hardlink/namespace races not covered by a trusted custodian root, and offline antirollback proof remain unavailable.
- **F09:** retention amendment needs independent acceptance by a reviewer different from the author and an enforceable evidence-loss invalidation path.

### Deliberate hard stop

The existing guarded dispatcher has **no approved production verifier and no registered G3 generator**. Default production mode denies all dispatch. No source change in this branch alters the frozen `r8_production_caller.py` entrypoint. There is **no evidence** that a future G3 path is necessarily mediated by this guard.

Passing 35 fixture tests must **never** be described as `G2_PASS`, `PRODUCTION_ADMISSION_PASS`, or `GO_R8_D_CANDIDATE_AUTHORING_ONLY`.

## Single adjudication

`IMPLEMENTATION_SOURCE_REGRESSION=PASS_SCOPED_LOCAL_35_OF_35`  
`PRODUCTION_TRUST_BOUNDARY=NOT_ATTESTED`  
`RETENTION_AMENDMENT_INDEPENDENT_ACCEPTANCE=HOLD`  
`GUARD_SOURCE_INDEPENDENT_REREVIEW=NOT_EXECUTED`  
**`G2=HOLD_INTEGRATED`**

**Immutable scientific state:** `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `READER=0`, `GPU=NO`, `PROBE256=SEALED`, `ACTUAL_HMAC_KEY_GENERATED=FALSE`, `ACTUAL_G_PRE_COMMITMENT_CREATED=FALSE`.

No scientific dispatch, new owner micro-permit, unseal, PR merge, or modification to frozen historical source was performed.
