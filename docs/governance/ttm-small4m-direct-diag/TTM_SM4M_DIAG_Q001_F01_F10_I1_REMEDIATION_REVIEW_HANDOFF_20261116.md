# HANDOFF — TTM-SM4M-DIAG-Q001 · F01–F10 I1 remediation and distinct release adjudication

**Operation:** `TTM_SM4M_DIAG_Q001_I1_INTEGRATED_REMEDIATION_NEGATIVE_QA_RIGHTS_AND_SINGLE_RELEASE_REASSESSMENT`  
**Date:** 2026-11-16 · **Repository:** `minhtri22/TokenToModel-Lab` · **Draft PR:** [#28](https://github.com/minhtri22/TokenToModel-Lab/pull/28).  
**Q1 main:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` · **original reviewed code:** `fb0bd357fbcc95adcc94d39e94c4bdb54c1714d5` · **original independent HOLD evidence:** `cbc27333e13b586a8da1c0b1a3741660a61faf25`.  
**New remediation candidate exact HEAD:** freeze **PR #28 HEAD at review time**, not the old code SHA; reviewer must return explicit HEAD + Git blob pins.  
**Current source verdict:** `AUTHOR_REMEDIATED_SOURCE_ONLY`. The earlier independent `HOLD_DIAG_Q001_CANDIDATE_SOURCE` is preserved unchanged and is NOT retroactively promoted. **I1 release: `HOLD_I1`; I2 CPU 256 steps: `NOT_EXECUTED`.**  
**Owner decision:** `GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL` already given; do NOT ask owner again or reinterpret as unconditional rights access or science GO.

## Exact evidence to inspect (no ZIP or local Downloads required)

- [Original distinct 10-finding HOLD](TTM_SM4M_DIAG_Q001_FB0_INDEPENDENT_SOURCE_REVIEW_HOLD_20261116.md) and [machine receipt](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_FB0_INDEPENDENT_REVIEW_RECEIPT_20261116.json).
- [New F01–F10 remediation Git blob/SHA256 manifest](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_F01_F10_REMEDIATION_SOURCE_MANIFEST_20261116.json).
- [Runner](../../../tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/ttm_sm4m_diag_q001.py) (exact repository source path). **Actual repo-root link:** https://github.com/minhtri22/TokenToModel-Lab/tree/review/ttm-sm4m-diag-q001-preexec-source-candidate-20261116/tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116
- `release_auth_v2.py`, `independent_negative_qa_v2.py`, both PowerShell launchers and README in that directory. `qa_crosscheck.py`, original ZIP SHA manifest and old source receipt remain historical, unchanged.

## Findings: implementation response and evidence boundary

| Finding | New source behavior | Still missing for I1 release |
|---|---|---|
| **F01 BLOCKER** | Ed25519 verification of **three distinct** role signatures over the same payload; one signed run nonce plus atomic consumed claim; runner requires hard-pinned SHA-256 of release guard. Local GO strings have no authority. | **Externally authenticated** owner/reviewer/rights signer public keys. Trust list deliberately empty; no forged GO succeeds. Native signed release and replay QA not certified. |
| **F02 BLOCKER** | Verify SHA-256 over actual underlying normalized full tokenizer inventory; enforce all 2,048 IDs categorized non-special/special/reserved, compare exact metadata ID lists, reject forged SHA/taxonomy. | Real tokenizer source bytes and custody attestation **NOT_VERIFIED**, no private access performed. |
| **F03 BLOCKER** | Admitted `fixture-freeze` writes exactly `FIXTURE_RECORDS.json` (80 complete cases), `FIXTURE_MANIFEST.json` (80 per-case/five group digests) and receipt; `run` verifies signed fixture hash, byte equality, oracle, all manifests. | Actual private I1 freeze **NOT_EXECUTED**; needs rights and authenticated upstream approval. |
| **F04 BLOCKER** | Both launchers choose the source beside `$PSScriptRoot`, enforce full lowercase 64-hex SHA-256 runner and scope paths to project root. | Windows PS 5.1 + Python 3.12 native execution **NOT_EXECUTED**. |
| **F05 BLOCKER** | New separate-path adversarial test contains forged local GO, changed inventory SHA, edited case/group hashes, bad oracle/target, replay nonce, source target-shift checks, and process guard-source checks; author ran **31/31 mock/source PASS**. | A genuinely independent reviewer must rerun and challenge actual Windows negative guards. Author self-test ≠ independent PASS. |
| **F06 BLOCKER** | Runner denies all release with empty hard-coded attested signer roots. It **cannot** infer legal rights from editable JSON. | Rights AD-00/AD-01C/E6, authorized checkpoint readback exact SHA, real tokenizer, external issuer signatures and Windows environment **NOT_VERIFIED**. Mandatory hard veto. |
| **F07 MAJOR** | Added finite positive weight-delta assertion, parameter SHA-256 and L2 norms before/after update, peak sampled RSS, Python/Torch versions, step0/256 group results. | Real model update never executed; cannot assert nonzero weight change empirically yet. |
| **F08 MAJOR** | External Windows process watchdog checks 900s, 12 GiB RSS, total log/output 1 GiB and uses process-tree kill; no retry. | Native Windows resource/timeout/child-process adversarial QA **NOT_EXECUTED**. |
| **F09 MINOR** | README corrects original `17/17` typo to historical `18/18`; old original receipt preserved. | Source readback only. |
| **F10 MINOR** | Explicit 4-choice caveat: gold at index zero, sorted distractors, not a calibrated benchmark, not proof of decoder bug. | No posthoc change to frozen Q1 candidate choices; future different hard-negative design needs separate owner amendment. |

## Independent QA request — one exact-head integrated packet

1. Pin new complete PR #28 HEAD; verify all Git blobs against the *new* remediation manifest. Check only files within the TTM Small4M Q1 source/governance/evidence scope changed, original independent HOLD unchanged, `lineage.md` and Q1 protocol unchanged.
2. Run `independent_negative_qa_v2.py` using **Python 3.12** from an exact project-root checkout in a clean Windows PowerShell 5.1 session. It must not touch checkpoint, real tokenizer, sealed TEST/FINAL or external paths. Independently mutate trusted keys/signatures/replay nonce, target shift, oracle, fixture hashes, wrong P02/checkpoint, and child-process time/RSS/output STOP. Confirm explicit HOLD on all injections, no I2 outputs.
3. Verify `release_auth_v2.py` rejects all local sign-off JSON under unconfigured trust anchors, and later requires authentically pinned distinct public keys. **Do not fabricate Ed25519 signatures/rights to get PASS.** No reader may access private checkpoint before role and AD evidence is valid.
4. Check normalized original tokenizer manifest against actual bytes *only after lawful rights admission*; no guessed reserved IDs. Independently confirm all 80 case records and SHA per case/group once authorized to freeze; no pre-I2 fixture generated now.
5. Return a single verdict `PASS_DIAG_Q001_REMEDIATED_SOURCE_SCOPED` or `HOLD_DIAG_Q001_REMEDIATED_SOURCE` and a **separate** `I1_PASS` or `HOLD_I1`. Source-only PASS does not imply I1 release.
6. I1 can become PASS **only** with external rights/signers, exact T4 checkpoint bytes, Windows 3.12/torch/psutil, native negative QA, and reviewed executable/fixture SHAs. Then, under the *already granted conditional owner GO*, exactly ONE I2 run (seed 20261116, 24 train/56 probes, 256 steps max, 900s/12GiB/1GiB) without retry. Report actual group metrics and root-cause triage.
7. If any gate is HOLD, produce a single evidence-based blocker ledger, not further governance micro-permits; no I2 model run. Original T4 science lineage and sealed TEST/FINAL remain untouched.

**Truth boundary:** Current 31/31 was author-run Linux Python 3.13 mock/source QA, not Windows 3.12, not independent organization, not a T4 inference/training experiment. No new experimental result about Small4M exists yet. The original reviewer `HOLD` survives.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_SM4M_DIAG_Q001_F01_F10_EXACT_REMEDIATED_CANDIDATE_DISTINCT_NEGATIVE_QA_RIGHTS_CUSTODY_AND_SINGLE_I1_ADJUDICATION`.
