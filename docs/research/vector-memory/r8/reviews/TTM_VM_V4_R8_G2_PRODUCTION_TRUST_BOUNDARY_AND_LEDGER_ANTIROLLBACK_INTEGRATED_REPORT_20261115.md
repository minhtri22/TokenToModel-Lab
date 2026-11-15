# TTM VM V4 R8 — G2 production trust boundary / remote anti-rollback implementation

**Operation:** `TTM_VM_V4_R8_G2_PRODUCTION_TRUST_BOUNDARY_AND_LEDGER_ANTIROLLBACK_INTEGRATED_IMPLEMENTATION_SINGLE_GATE`  
**Date:** 2026-11-15 (Asia/Bangkok)  
**Actor:** Implementation Agent, **not independent reviewer**  
**Code candidate commit:** `ab6d7e0c58acbae855e87b072c1dd6ac1905d38d`  
**Integrated disposition:** `G2_HOLD · HOLD_INTEGRATED` · `PRODUCTION_TRUST_BOUNDARY_NOT_ATTESTED`.

## Frozen references and unmodified evidence

- Exact frozen five scientific sources: `84d9d5c95e9962ccfe294852570e261b145fe403` (not edited).
- Prior independent source review: `94b377ce6c0d6aa9e1d08ae4ff628c215449be1f` (F01–F09).
- Prior remediation: `2c6aee6d9644bd2035c4624ab12f1b524a11e6e0` (35/35 local fixture tests); unchanged here.
- Owner accepts lack of off-device backup only for R8-D exploratory. `RECOVERY_NOT_VERIFIED`. Retention amendment `b1231faef1b2a4166016ee78a9de6617800efeff` is still **PROPOSED_NOT_EFFECTIVE**. No distinct reviewer acceptance recorded.
- No real R8 key, blueprint/gold, G_pre commitment, candidate, G3 or G4 created/executed.

## Source candidate and evidence on GitHub

New files at exact [commit `ab6d7e0c58acbae855e87b072c1dd6ac1905d38d`](https://github.com/minhtri22/TokenToModel-Lab/commit/ab6d7e0c58acbae855e87b072c1dd6ac1905d38d):

- [`r8_production_trust_boundary.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/ab6d7e0c58acbae855e87b072c1dd6ac1905d38d/docs/research/vector-memory/r8/integrated_closure/r8_production_trust_boundary.py) — SHA-256 `de085cba7ec671de2787ea78837ac18a54cc30cc38e53f36af17214ab4253763`; Git blob `f983d5493ba095a1b677bfe867e4c31570f0db23`.
- [`test_r8_production_trust_boundary.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/ab6d7e0c58acbae855e87b072c1dd6ac1905d38d/docs/research/vector-memory/r8/integrated_closure/test_r8_production_trust_boundary.py) — SHA-256 `15d43bdfec10659053116320a56f6a0b2b12771f62fbf8217837c126ae264c65`; Git blob `434919d726e1929d52307a2ce7c0d08c97bafff1`.
- [ZIP two new exact-byte Python files](https://github.com/minhtri22/TokenToModel-Lab/blob/ab6d7e0c58acbae855e87b072c1dd6ac1905d38d/docs/research/vector-memory/r8/reviews/artifacts/TTM_VM_V4_R8_G2_TRUST_BOUNDARY_NEW_CODE_20261115.zip): SHA-256 `e7637128d2e85b4e1da66b329cf6e31a8b421bf60085ac3740f7b40f6841b885`; Git blob `1f0cfe742f3fc437bd672c5825ce785f16faac01`.
- [ZIP hash manifest](https://github.com/minhtri22/TokenToModel-Lab/blob/ab6d7e0c58acbae855e87b072c1dd6ac1905d38d/docs/research/vector-memory/r8/reviews/artifacts/TTM_VM_V4_R8_G2_TRUST_BOUNDARY_NEW_CODE_20261115.sha256.txt).
- [Windows Python 3.12 source-only CI](https://github.com/minhtri22/TokenToModel-Lab/blob/ab6d7e0c58acbae855e87b072c1dd6ac1905d38d/.github/workflows/ttm-vm-r8-g2-production-trust-sourceqa.yml).

Diff against remediation commit is exactly five added files: two Python source/test, ZIP, manifest, workflow. No modifications to the frozen research files, P00/G0 baseline, or protected private storage.

## Implemented source mechanisms; scope of each

**Real GitHub verifier adapter (source candidate).** The `GitHubReleaseAuthority` uses a pinned GitHub CLI executable, fixed repository identity, exact release tag/asset name, GitHub REST `immutable=true`, remote asset download, SHA-256, and `gh release verify-asset` / `gh release verify` cryptographic verification. It demands signed timestamps from the **verificationResult.verifiedTimestamps** subtree; bare caller flags and predicate fields do not count. Errors or unfamiliar CLI JSON shapes must fail closed. **No actual command in this adapter was run against GitHub this turn**; only its source and synthetic negative tests ran. It must be tested with pinned GitHub CLI and a harmless release before production attestation. Official guidance: https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/secure-your-dependencies/verify-release-integrity .

**Protected key + HMAC V2 (source candidate).** `WindowsDPAPIKeyReader` reads a pre-existing DPAPI CurrentUser ciphertext from private custody, decrypts it under the current Windows profile, returns only key bytes in process memory; it does not generate any key. `authenticate_hmac_v2` checks the frozen `folds_raters.py` byte SHA, loads exact source without public-checkout import fallback, re-computes `preassign_r8` from the frozen V2 implementation and compares **full canonical lock bytes**, not HMAC-like strings. Fixture QA substitutes a synthetic 32-blueprint algorithm module with a locally pinned test digest — **not a real frozen V2 execution**. Real DPAPI/HMAC Windows custody test remains NOT_EXECUTED.

**Current source/runtime binding (source candidate).** `PinnedCustody.verify` reads all five frozen source files, compares exact SHA-256, verifies computed canonical source manifest SHA, checks Python 3.12 executable SHA, package versions (NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0), runtime manifest exact bytes and loaded module paths and hashes. This method needs actual protected Windows runtime/ACL token attestation; it was **not run against the user's machine**.

**One-shot remote consumption before callback (source candidate).** `RemoteOneShotLedger` derives a unique release tag from the prospective digest and calls `gh release create` for a public-safe consumed marker. It must verify the new immutable signed release and asset before any callback. A duplicate existing release/tag, missing signature, GitHub outage or mismatch refuses admission. Replacing or rolling back a *local* SQLite file cannot reset a remote consumed marker **while the remote release exists**. However sufficiently privileged deletion and later reissue remain possible, as does untrusted process modification. This is **not** an attested WORM, rollback-proof storage or accepted retention substitute.

**Source call graph (candidate).** `ProductionBoundaryCandidate.dispatch` obtains an internally registered generator callback, checks source/runtime/private HMAC, validates prospective G_pre and distinct GitHub reviewer approval release, rechecks the anchor, remotely consumes one-shot marker and only then calls the target. No approved G3 generator is registered in this tree: `_registered_generator=None` and `dispatch` rejects immediately with `NO_APPROVED_G3_GENERATOR_REGISTERED`. Synthetic tests temporarily register an inert callback. Python module/class globals are mutable in an untrusted interpreter; mandatory enforcement in the **authorized Windows launcher and OS process boundary remains UNVERIFIED**, including other hypothetical future generator entrypoints.

## QA: exact running result

- Local Linux CPython 3.13.5: `57/57 PASS` (35 inherited regression + 22 new boundary synthetic/negative methods).
- GitHub Actions [run #43714211130](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43714211130), exact head `ab6d7e0c58acbae855e87b072c1dd6ac1905d38d`: **completed/success**, hosted Windows CPython **3.12.10**, `Ran 57 tests ... OK`. See job `windows-source-only` and logs. No scientific data or real private HMAC key was used.
- New negative tests cover missing/revoked remote anchor, no independent approval, forged commit, reviewer not distinct, wrong commitment digest, wrong HMAC key and tampered lock (synthetic algorithm), alternate local instance with remote consumed marker, remote call failure, malformed JSON, CLI hash mismatch and production default denial.
- CI is **source/fixture** only: it did not run against the user's existing NTFS custody, Windows DPAPI key, real frozen HMAC with protected key, authenticated GH client, real G_pre or generator.

## Critical limitations that remain fail-closed

| Requirement | Disposition |
| --- | --- |
| F01 production launcher identity / no bypass across future entrypoints | `NOT_ATTESTED`; generator not registered |
| F02 real GitHub signed trust root and distinct acceptance | `SOURCE_CANDIDATE_ONLY`; no real acceptance release |
| F03 exact frozen HMAC V2 under authorized private custodian | `NOT_EXECUTED_REAL_KEY` |
| F04 protected Windows runtime/source byte readback at live dispatch | `NOT_EXECUTED_ON_OWNER_WINDOWS` |
| F05 signed-time/evidence-loss validation in actual GH adapter | `NOT_ATTESTED_REAL_GITHUB` |
| F06 antirollback across deleted remote releases / arbitrary process tampering | `NOT_PROVEN`; scope only while remote marker exists |
| F09 retention amendment by reviewer distinct from its author | `HOLD` |

**Warning:** A `57/57` QA result does not close F01–F06 or admit R8 candidate authoring. An actual production trust boundary requires verified Windows process isolation, authentic DPAPI key and source, GitHub attestation readback, reviewer identity/custody, remote consume policy, and an approved actual generator path. Do not label current `NOT_ATTESTED` as PASS.

## Integrated disposition and scientific invariants

`IMPLEMENTATION_SOURCE_FIXTURE_QA=PASS_SCOPED_WINDOWS_HOSTED_57_OF_57`  
`PRODUCTION_TRUST_BOUNDARY=NOT_ATTESTED`  
`PRODUCTION_ANTIROLLBACK=HOLD_RETENTION_AND_OS_BOUNDARY`  
`RETENTION_AMENDMENT_INDEPENDENT_ACCEPTANCE=HOLD`  
`DISTINCT_REVIEW_OF_NEW_CANDIDATE=NOT_EXECUTED`  
**`G2=HOLD_INTEGRATED`**

`G0=PASS_SCOPED` · `G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` · `R7=FROZEN_FAIL` · `R8=NOT_GENERATED` · `G3/G4=NOT_EXECUTED` · `G5/G6=SEALED` · `READER=0` · `GPU=NO` · `PROBE256=SEALED` · `ACTUAL_HMAC_KEY_GENERATED=FALSE` · `ACTUAL_G_PRE_COMMITMENT_CREATED=FALSE` · `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.

The original scientific source, owner risk acceptance, previous QA and independent findings are preserved. This candidate was implemented and tested by the same implementation agent, not independently approved. No production deployment, merge or science execution was authorized.
