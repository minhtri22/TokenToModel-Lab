# G1 v1c — Codex second-HOLD repair and integrated re-review packet

Date: 2026-11-09. Scientific authorization: **HOLD**. No real TinyStories/Qwen/TEST/science was executed.

## Scope and historical evidence

GitHub: https://github.com/minhtri22/TokenToModel-Lab

Research branch: research/ttm-six-cross-model-representation-transfer-20261109

Windows project root: D:\WORK\RESEARCH\TokenToModel-Lab

Previous reviewed candidate at cd6998b2459039a35fcca390958687ddb0b15340, prior source candidate d42ebb741d95338d64ae420dd86f3ab10ed591ad. Previous distinct reviewer returned HOLD (71 cases, 54 controls, 17 reproduced defects/shortfalls). Original reviewer report, test harness and log are archived in this branch as three *new* files; the local original and its SHA256 receipt have not been changed. This is not a claim that a new Codex review has run.

T1 manifest SHA256: 9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9.

Private G1 manifest SHA256: 6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6. TRAIN128/DEV64/TEST64. Do not re-seal or read the real TEST.

## Exact v1c source pins (verified after GitHub commit)

| Repo-relative file under scripts/research/six_ttm | Git blob |
|---|---|
| g1_science_guard_v1c.py | 4554a3e12911cbf0606a8be053660cad0c38f374 |
| g1_science_core_v1c.py | f591bd617feb007c20023a313ebc5f429471d8b2 |
| g1_science_private_feature_extractor_v1c.py | 9bb28fe39999fba0bab5474e2644b11f7940c06a |
| test_g1_v1c_critical_qa.py | 01030f2aba4a7356d093664c628973a73b458475 |
| test_g1_v1c_hard_gate_negative_qa.py | 9d824034124f210d9dd58c23954d4da66ba119c2 |

Original v1b source blobs remain unchanged. The source above matches bytes independently tested on isolated Linux CPU Python 3.13.5 / NumPy 2.3.5 / cryptography 46.0.4.

## The two Codex CRITICAL defects fixed in v1c candidate

**Freeze replay schema:** v1b prepare emitted a frozen DEV schema v1, while the committed prepare and validator used v1b. v1c prepare now emits the exact v1b schema. Tests create TRAIN/DEV-only synthetic features, construct the freeze with complete lineage, validate signed-content SHA and schema, then recompute prepare and compare every frozen selection field. PASS. No real TEST byte was opened.

**False-significant CKA:** v1b used numerically different observed and permutation computations. v1c centers once and reuses the same Gram matrices, denominator and reduction function for observed and all nulls. It counts rounding-equivalent values conservatively as ties at tolerance 64 * float64 machine-epsilon * max(1, abs(observed)). On a 64-story permutation-invariant centered Gram, the corrected p-value is **1.0** instead of false-significant 1/1001; on a strongly coupled fixture it is 1/1001. The tolerance is a prospective statistical amendment requiring external scientific review.

## Additional HIGH-risk coding hardening

- Signed owner admission requires run/phase/workspace, owner and distinct reviewer, exact source HEAD and guard/core/extractor/amendment blob pin formats, explicit private T1 TRAIN-only and Free T4 no-training data scope and expiry. Production authority key is STILL None and non-bypassably denies science.
- DEV freeze validation now requires complete keys, exact seed numbers, valid hex digests, fully numeric nonboolean 1000 shuffled alpha choices, finite DEV scores and exact run/pack/manifest linkage.
- File read checks same opened file-handle identity as checked path (device+inode); commit checks the private root itself for redirection BEFORE writing. These reduce local corruption hazards but do not replace OS ACL/trusted writer and fail under a malicious actor with control of parent dirs.
- Cumulative GPU budget no longer treats a missing, partial or nonfinite previous ledger as zero. This is not an OS kill watchdog or trusted external budget.

## QA evidence (AUTHOR-OWNED, not independent reviewer)

- test_g1_v1c_critical_qa.py: **PASS 7 cases**, including DEV freeze replay, null-invariant CKA p=1, informative CKA p=0.000999, zero-variance CKA INCONCLUSIVE, and full synthetic 1000 shuffled fits / 1000 CKA nulls / 2000 bootstrap paths.
- test_g1_v1c_hard_gate_negative_qa.py: **PASS 22 checks**, including test-only Ed25519 signatures, no production key, missing HEAD/guard/scope/amendment, boolean alpha, malformed digest, missing seed/DEV score, incomplete GPU ledger, redirected root and mocked file-handle substitution.
- guard_v1c selftest reports production key unprovisioned and science false; core_v1c synthetic 6 tests PASS; extractor_v1c synthetic 8 probes PASS.
- Prior v1b author QA 38/38 and original Codex 71 cases/17 defects remain independent historical records; do not combine counts as if they were one reviewer suite.

## Single hard-gate admission package, still HOLD

| Hard gate | Decision today | Missing distinct independent evidence |
|---|---|---|
| OWNER AUTHORITY | HOLD | Production owner-controlled public trust key, immutable launcher and signed exact code/source/run/rights admission. Test-only signing keys are not owner credentials. |
| SPLIT BROKER | HOLD | Owner-authorized trusted split materializer, TEST inaccessible before freeze even through Windows hardlinks, byte isolation/ACL QA; no unapproved Colab source staging. |
| PACK LEDGER | HOLD | External authenticated writer and atomic pack+receipt+freeze transaction, trusted source lineage and crash-recovery adjudication; local file hash alone does not authenticate origin. |
| ONE-SHOT | HOLD | External monotonic ledger that survives deletion/rollback of the private workspace, logs every TEST consumption and terminal STOP. |
| GPU WATCHDOG | HOLD | OS kill-capable supervised worker, persisted cumulative 60-minute/model and 120-minute/run limits, T4 resource/endurance QA. |
| METHODS | HOLD | Distinct adjudication of v1a mapping/dedup, v1b fixed TEST SST bootstrap, new v1c CKA tie rule, null exchangeability and limited 64-story feasibility. |

Do NOT split these into six independent owner permits. Integrate and review them as one pre-science admission package. Reviewer should rerun both v1c tests and design new adversarial fixtures; choose exactly one distinct PASS/HOLD/FAIL conclusion. Reviewer PASS, if achieved, does not itself authorize science or raw-source staging.

## Explicit boundaries

Never rerun consumed Qwen technical one-shots, regenerate T1/G1 manifests, open real TEST, download models, load private TinyStories source, create real G1 feature packs, write private data to GitHub, or alter main, PR#12, lineage.md, TTM-Small-4M checkpoints or unrelated worktrees.

**Current verdict: VERSIONED_V1C_SOURCE_PINNED, AUTHOR_QA_29_CASES_PASS, DISTINCT_REVIEW_PENDING, SCIENCE_LOCK=HOLD.**
