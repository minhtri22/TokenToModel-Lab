# TTM VM V4 R8 — Pre-G3 admission guard implementation & source QA

- **Operation:** `TTM_VM_V4_R8_G2_PRE_G3_ADMISSION_GUARD_IMPLEMENTATION_AND_SOURCE_QA_SINGLE_GATE`
- **Date:** 2026-11-15 (Asia/Bangkok)
- **Role:** implementation agent (not an independent reviewer)
- **Disposition:** `PASS_SCOPED_SOURCE_FIXTURE_QA_19_OF_19`; `PRODUCTION_ADMISSION_NOT_ATTESTED`; `G2_HOLD · HOLD_INTEGRATED`

## Frozen baseline and inherited evidence

- Scientific implementation remains frozen at [`84d9d5c95e9962ccfe294852570e261b145fe403`](https://github.com/minhtri22/TokenToModel-Lab/commit/84d9d5c95e9962ccfe294852570e261b145fe403). Its `r8_production_caller.py` exposes `precommit_before_G3` and `verify_after_G3_before_CV` but does **not** register a generator or authenticate a remote timestamped admission receipt before invoking a generator.
- [Independent G0 source review at `12d66bcf`](https://github.com/minhtri22/TokenToModel-Lab/blob/12d66bcff86a6cf435998a98a14afd254924fa5d/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_GPRE_V2_FINAL_INDEPENDENT_G0_G2_ADJUDICATION.md) remains `PASS_SCOPED`.
- [Local custody/5-of-5 protected SHA report at `45dc302c`](https://github.com/minhtri22/TokenToModel-Lab/blob/45dc302c67a96e7af2c1bfa6fb2b4944e6c81915/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_MINIMAL_LOCAL_WINDOWS_CUSTODY_AND_SOURCE_LOCK_20261115.md) and [exact runtime at `3ca8d799`](https://github.com/minhtri22/TokenToModel-Lab/blob/3ca8d7993bc6921adc507cd4c9cf7d839e92141e/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_THREE_RESIDUAL_CONDITIONS_INTEGRATED_CLOSEOUT_20261115.md) are preserved, not rerun.
- [Owner risk-acceptance and prospective retention proposal at `b1231fa`](https://github.com/minhtri22/TokenToModel-Lab/blob/b1231faef1b2a4166016ee78a9de6617800efeff/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_OWNER_RISK_ACCEPTANCE_AND_SCOPED_FINAL_ADJUDICATION_20261115.md): backup-independent recovery is `NON_BLOCKING` for R8-D exploratory, while `RECOVERY_NOT_VERIFIED`; retention amendment is **proposed, not effective**.
- [GitHub immutable release sentinel](https://github.com/minhtri22/TokenToModel-Lab/releases/tag/ttm-vm-v4-r8-g2-commitment-sentinel-20261115) stays evidence for the harmless sentinel **only**, not a real G_pre receipt.

## New source candidate (separate implementation branch)

- `docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py`
  - SHA-256: `6bf5150b65718ad594dec4fc66f42a9dc6e29cf004828f265752af1d9e603a31`
  - Git blob SHA-1: `b35da231742d5bcf01f8d4ab48069afbfad37eea`
- `docs/research/vector-memory/r8/integrated_closure/test_pre_g3_admission_guard.py`
  - SHA-256: `65279926056b0e64a118c62a1d5e12f1a87213c7e6d1b9c9f1ed762c51b50e7c`
  - Git blob SHA-1: `4b5ebfcd7316fe9267ccbf5254670c370412826a`

Both Git blobs were read back from GitHub and matched locally generated Git blob hashes. New code is additive; no modification to the frozen scientific modules.

## Implemented fixture guard behavior

1. Reject noncanonical/duplicate-field private envelope, wrong schema/algorithm, source commit mismatch, malformed session, nonce, blueprint or lock byte digest.
2. Bind private digest `SHA256(nonce || exact_envelope_bytes)` to an `AnchorProof` with exact session, source/runtime manifest, release tag, algorithm and asset proof fields.
3. Reject missing/mismatched signature/immutability flags, invalid UTC timestamp ordering, absent/mismatched independently accepted receipt and acceptance timestamp not subsequent to signed timestamp.
4. Persistently reserve a session and commitment digest via SQLite `BEGIN IMMEDIATE`, uniqueness and `synchronous=FULL`, **before** invoking the supplied fixture callback. A failed callback still consumes the one-shot permission.
5. **Production default denies before callback** (`PRODUCTION_VERIFIER_AND_AMENDMENT_NOT_ADMITTED`). `fixture_mode=True` is restricted to source QA and must not be used for a real G3 executor.

### QA actually executed

Command: `PYTHONWARNINGS=error::ResourceWarning python -m unittest -v test_pre_g3_admission_guard.py`.

- **19/19 unittest methods PASS**. Coverage includes valid fixture once, production-default deny, absent anchor, unsigned/mutable release, wrong anchor/session/manifest/version/tag, timestamp order, absent/incorrect acceptance, tampered private bytes, nonce, duplicate JSON, callback failure consumption, missing ledger directory, persistent replay and eight concurrent calls with **one** accepted callback.
- The tests ran in this agent's isolated Linux Python **3.13.5**, not on owner's Windows Python 3.12.10. They do not substitute for the previously attested Windows runtime or for future Windows native execution QA.
- No real private key, real G_pre commitment, R8 gold, case text, G3 generator, research GPU or model execution was created or invoked.

## Explicit unclosed gaps; no production PASS

- `INDEPENDENT_RETENTION_AMENDMENT_ACCEPTANCE=NOT_EXECUTED`: prior amendment `b1231fa` is still proposed; this implementation does not decide whether risk of release deletion is acceptable.
- `TRUSTED_GITHUB_ATTESTATION_VERIFIER=NOT_IMPLEMENTED`: test `Proofs` provides fixture-only outputs. A `signature_verified=True` attribute by itself is **not** cryptographic signature verification; a separately reviewed verifier must validate actual remote asset bytes, signed bundle, server-side timestamp, approved identity and deletion/invalidation policy.
- `TRUSTED_INDEPENDENT_ACCEPTANCE_RECEIPT_VERIFIER=NOT_IMPLEMENTED`: test fixture uses a synthetic reviewer commit (`aaaa...`) and does not assert a real reviewer decision.
- `PRIVATE_HMAC_V2_CRYPTOGRAPHIC_RECOMPUTATION=NOT_INTEGRATED`: this guard verifies exact-byte lock binding and V2 field shapes; a real trusted custody adapter must separately validate HMAC lock against original blueprint and the custodian-held key via frozen `folds_raters.preassign_r8` before authoring.
- `G3_PRODUCTION_GENERATOR_REGISTERED=NO`: no production generator was present at frozen pin, and frozen `r8_production_caller.py` was not patched. The new guarded dispatcher demonstrates fail-closed fixture behavior **only**. It cannot claim to prevent execution via every future unregistered entrypoint.
- `EXACT_WINDOWS_3_12_GUARD_QA=NOT_EXECUTED`, `CROSS_PROCESS_WINDOWS_RACE_QA=NOT_EXECUTED`, `REAL_CUSTODY_LEDGER_ACL_AND_DURABILITY=NOT_VERIFIED`.
- Additional production hardening needed: trusted verifier construction, approved retention/invalidation decision, trusted HMAC proof, secure ledger path/permissions, robust handling of transient errors and independent verification of source-to-generator call graph. None is silently waived.

## Adjudication and next review

**Implementation and fixture QA:** `PASS_SCOPED_SOURCE_FIXTURE_QA_19_OF_19`.

**Independent QA:** `NOT_EXECUTED`; self-testing is not an independent review.

**G2 integrated:** `G2_HOLD · HOLD_INTEGRATED`.

A distinct reviewer should assess the **exact** implementation candidate and retention amendment; require a genuinely trusted production verifier and source-level admission path to be proven before any authorization. The narrow next gate is **independent review of this pinned candidate and its explicit production gaps**, not another repeat of G0, Windows custody, source hashes or Python package installation.

`G0=PASS_SCOPED` · `G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` · `R7=FROZEN_FAIL` · `R8=NOT_GENERATED` · `G3/G4=NOT_EXECUTED` · `G5/G6=SEALED` · `READER=0` · `GPU=NO` · `PROBE256=SEALED` · `ACTUAL_HMAC_KEY_GENERATED=FALSE` · `ACTUAL_G_PRE_COMMITMENT_CREATED=FALSE` · `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.