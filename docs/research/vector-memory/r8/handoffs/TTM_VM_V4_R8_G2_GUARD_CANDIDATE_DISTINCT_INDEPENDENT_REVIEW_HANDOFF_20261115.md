# HANDOFF — TTM VM V4 R8 G2: Distinct Independent Review

**Operation:** TTM_VM_V4_R8_G2_GUARD_CANDIDATE_INDEPENDENT_REVIEW_AND_TRUST_BOUNDARY_ADMISSION_SINGLE_GATE
**Date:** 2026-11-15 (Asia/Bangkok)
**Repository:** minhtri22/TokenToModel-Lab
**Recipient:** Distinct Independent AI Scientific, Security & Source Reviewer — NOT the implementation agent.
**Mode:** READ_ONLY_INDEPENDENT_REVIEW · EXACT_GIT_PINS · NO_SCIENCE · NO_NEW_PERMIT
**Initial verdict:** G2_HOLD · HOLD_INTEGRATED; authoring NOT_AUTHORIZED.

## 1. Scope and exact source pins

- Frozen scientific source: 84d9d5c95e9962ccfe294852570e261b145fe403 (do not change).
- Independent G0 source verdict: 12d66bcff86a6cf435998a98a14afd254924fa5d (preserve PASS_SCOPED).
- Owner scoped risk acceptance and PROPOSED retention amendment: b1231faef1b2a4166016ee78a9de6617800efeff.
- Implementation/source-QA candidate: 9d210f1392e81a17f1c35cea12230bf7ff74fb02.
- GitHub source-QA ZIP: commit 63e45126625cd99064f9d476affe39c5d347e21d, file under docs/research/vector-memory/r8/reviews/artifacts/.
- ZIP SHA-256: d1bf1b43f2cd9d482c989173ab1736594eb4593d5931094df285f8c95c174b77; size 30727 bytes; 3 files.
- GitHub ZIP URL: https://github.com/minhtri22/TokenToModel-Lab/blob/63e45126625cd99064f9d476affe39c5d347e21d/docs/research/vector-memory/r8/reviews/artifacts/TTM_VM_V4_R8_G2_PRE_G3_GUARD_SOURCE_QA_20261115.zip
- Exact source URLs:
  - https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py
  - https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/test_pre_g3_admission_guard.py
  - https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_PRE_G3_ADMISSION_GUARD_IMPLEMENTATION_AND_SOURCE_QA_20261115.md
- Amendment URL: https://github.com/minhtri22/TokenToModel-Lab/blob/b1231faef1b2a4166016ee78a9de6617800efeff/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_OWNER_RISK_ACCEPTANCE_AND_SCOPED_FINAL_ADJUDICATION_20261115.md

## 2. Independent review duties

**A — Evidence chain and integrity.** Fetch exact commits, ZIP and manifest directly from GitHub. Verify SHA-256, Git blob IDs, archive member byte identity, and changed-file scope relative to b1231fa (two added Python files + one report; frozen scientific source unchanged). Do NOT accept implementation-agent self-reported 22/22 as independent QA.

**B — Retention amendment.** Independently decide whether proposed R8-D-only use of GitHub immutable release plus signed timestamp and fail-closed invalidation preserves prospective G_pre evidence integrity. The owner waived an *off-device backup requirement*, NOT the need for authentic pre-G3 commitment. Recovery remains NOT_VERIFIED. Immutable GitHub releases lock assets/tag while extant; deletion by sufficiently privileged actors remains a risk. Confirm no retroactive change to pre-registration and no inappropriate extrapolation to R8-C/production. Issue a distinct PASS_SCOPED_AMENDMENT / HOLD with scientific rationale, exact protocol limits, and evidence-loss invalidation rules.

**C — Adversarial guard source audit.** Inspect all entrypoints, exact payload canonicalization, nonce/digest binding, lock HMAC authenticity, source/runtime pin verification, trusted anchor signature provenance, signed/published/acceptance time order, one-shot atomic ledger, replay and concurrent callers. Mandatory questions:
  1. Is fixture_mode=True an externally selectable bypass? Production defaults deny, but is there any real protected generator call path?
  2. Are AnchorProof and AcceptedReceipt merely user-constructible data classes, with no real trusted GitHub/attestation verifier?
  3. Is amendment_review_commit only regex-checked rather than independently authenticated?
  4. Does the guard authenticate the *actual HMAC V2* under private custody, or only check schema and 64-hex fields?
  5. Are source/runtime manifests verified by actual file/byte readback at admission, or only strings compared within a claimed proof?
  6. Is ledger path protected against symlink/hardlink, directory replacement, tampering, rollback and inappropriate permissions? Is consumption persisted and one-shot across processes?
  7. Can any unguarded path call the actual case generator, or is the generator as yet unregistered? Does the original r8_production_caller.py enforce admission?
  8. Could a remote release be deleted/replaced, or trust state become stale between verification and dispatch? How is invalidation enforced?
  9. Are negative-test fixtures representative enough, and are error paths consistently fail-closed BEFORE callback invocation?

**D — Independent QA.** Independently re-run or independently inspect source-only tests from exact GitHub bytes in an isolated environment if permitted. Preserve no-science and no-real-key constraints. Include malformed/duplicate JSON, nonce, lock, digest, version, source/runtime pin, missing/forged receipt, timestamp order, replay, two threads and two spawned processes. Do not represent tests on non-Windows Python as a Windows 3.12 production admission certificate. Treat implementation 22/22 as historical source-fixture claim.

**E — Distinguish three separate verdicts.** (1) amendment acceptance; (2) fixture guard source QA; (3) production trust-boundary readiness. Independent PASS on (1) or (2) does not imply (3). G2 remains HOLD unless all contractual gate requirements have independent supporting evidence.

## 3. Protected boundaries; prohibited operations

- Do not modify implementation files or frozen scientific source in this review.
- Do not generate R8 candidate/cases/gold/fold mapping; no real HMAC key or G_pre commitment.
- Do not call real G3, G4, model training or GPU; keep G5/G6/PROBE256 sealed.
- Do not modify Windows custody ACL, reset user profile, provision backup, or request repeated owner GO.
- Do not auto-approve retention or silently weaken required timestamp-before-G3 and invalidation semantics.
- No merge to main, no promotion to production, no scientific release.
- Keep any private path, key, fold map, blueprint, SID and custody details out of public GitHub evidence.

## 4. Required deliverables (one integrated independent review)

Prepare:

1. docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_GUARD_CANDIDATE_DISTINCT_INDEPENDENT_REVIEW_20261115.md
2. docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_GUARD_CANDIDATE_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261115.json

Both must record reviewed exact SHA/ZIP SHA-256, distinct reviewer identity, method, all findings with severity/file/line/repro, independent test evidence where actually executed, amendment decision, fixture source decision, production readiness, and one integrated PASS/HOLD adjudication. Use statuses NOT_EXECUTED / NOT_VERIFIED when appropriate. Prefer a separate review evidence branch from exact candidate/packaging commit; commit/push ONLY public-safe review artifacts, and read back GitHub blobs. If write permissions are blocked, return full report inline with NOT_COMMITTED_POLICY_BLOCKED and never fabricate a commit.

**Hard stops:** The original G0 PASS is unchanged; owner backup waiver applies only to R8-D exploratory; no GO_R8_D_CANDIDATE_AUTHORING_ONLY or G3 permit is granted by this review instruction. Do not call independent QA on the implementation agent's own evidence.

## 5. Exit classification

- AMENDMENT=PASS_SCOPED or HOLD with explicit retention/invalidation reasoning.
- SOURCE_FIXTURE_GUARD=PASS_SCOPED / HOLD / FAIL (independent evidence only).
- PRODUCTION_ADMISSION=NOT_ATTESTED or PASS only with a genuinely verified production trust boundary and independent evidence (not currently provided).
- G2=HOLD_INTEGRATED unless every prerequisite for scoped R8-D admission is demonstrably satisfied.

**Next step:** one distinct independent reviewer adjudicates the exact GitHub candidate; the implementation agent handles any remediation only after that review. No micro-permits.
