# G1 — Integrated remediation after distinct Codex review (HOLD)

**Date:** 2026-11-09  
**Action:** `TTM_SIX_XMODEL_G1_CODEX_HOLD_REMEDIATION_INTEGRATED_REDESIGN_AND_NEGATIVE_QA`  
**Current scientific gate:** `HOLD`. No training, G1 TEST access, Qwen technical rerun, science authorization, or raw/derived scientific data publication.

## 0. Immutable independent-review evidence

Exact reviewer report: `docs/research/six-ttm/G1_CODEX_DISTINCT_PREEXECUTION_REVIEW_HOLD_20261109.md`.

- Original upload SHA256: `4e7d3b331783e7eb1ca82acb8b8e0d24b29a8edad3fa40616c9248eae6ef1f56`.
- Byte-exact Git blob: `5f478a0a801c31e9c119b9691440fc17252b3846` (original CRLF preserved).
- Review sources: research HEAD `dcac15b31eaf9cab90e17945cd2021a163e8ce3f`, main `b57b44e7287f842e81050c1faee337f636333dd0`.
- Reviewer report identity: `codex-distinct-01a1bfbf-baf4-75e3-bbf5-e32d64325f9e`; subagent names Bohr and Poincare. Identity provenance originates from the submitted report, not a separately authenticated credential.
- Distinct-review verdict: **`HOLD`**. Positive source/algorithm QA is preserved. Inferred repairs in this file are **engineering proposals**, not findings executed by Codex.

Do **not** rewrite, supersede, or mark the existing CodeX review PASS retrospectively. New source revisions get **new** Git blobs and a new reviewer verdict.

## 1. Issue-to-fix and required negative QA matrix

| Severity / reviewer § | Required repair | Mandatory failure-mode QA before science |
|---|---|---|
| BLOCKER §4.2: TRAIN/DEV reconstruction parses G1 TEST bytes inside original TinyStories TRAIN source | Split-aware private materializer/data broker: after one verified original source admission, seal distinct TRAIN, DEV, and TEST prefix sources; only expose TRAIN/DEV before `FIT_FROZEN`; TEST bytes inaccessible until release. Do not re-scan full original raw source during TRAIN/DEV extraction. Source admission and private raw prefix materialization need separate owner approval | Trap/hook all file reads; assert `TEST_BYTE_ACCESS_BEFORE_FIT_FROZEN=DENIED`; test wrong row/hash, missing/duplicate and cross-split prefix; no real TEST read |
| BLOCKER §4.3: owner approved only local metadata/hash sealing | Single explicit owner scope amendment covering original-source staging/location (Windows/Colab), numeric hidden/teacher-score NPZ, private receipts, access controls and retention, exact `run_id` and one-shot authorization; no silent extension of earlier approval | Attempt science under old metadata-only scope must STOP; no file or GPU side effects |
| MAJOR §4.4: model auxiliary files not all byte-pinned | Compare SHA256 of tokenizer.json, tokenizer_config.json, vocab, merges, config, index, LICENSE and generation_config against frozen receipts, plus weights and revision. Cross-check tokenizer used in science against manifest-seal token-ID pin, not only token count | One-byte change in config/tokenizer/index/license must STOP before load; equal token count with different token IDs rejected |
| MINOR §4.5: diagnostic scope ambiguous | v1b prereg amendment explicitly says whether source-only response, layer 14, and F orthogonal neutrality diagnostic are implemented, omitted, or exploration-only; no unrecorded post-hoc changes | Static protocol-vs-code table; verify all 8 primary continuations exactly |
| MAJOR §4.1 & §4.7: correlated/near-duplicate prefixes and exchangeability | Explicit null and CKA hypotheses with assumptions and restricted feasibility claim; assess near-duplicate/group dependency in private pre-TEST QA, or hold if separation invalid. Do not change frozen 128/64/64 silently | Adversarial near-duplicate fixture, paired-correlation false-positive detection, zero TEST-guided dedup |
| MAJOR §4.6: A→P versus B-direct different information budget | Keep `A`, `B` and oracle reported together; state `A→P` is linear in source; no claim of distinct SIX causal mechanism. Fairness limits documented; if stronger superiority claim is desired, design separate equal-information comparison before TEST | Controlled fixture in which B-direct equals/outperforms A and final verdict never claims mechanism superiority |
| MAJOR §4.8: degenerate TEST/bootstrap/CKA terminal behavior | Lock v1b bootstrap estimand avoiding zero random-sample SST, e.g. paired per-story squared-error differences divided by frozen full-TEST SST (candidate, reviewer must approve); terminal `INCONCLUSIVE` rather than generic exception for degenerate full TEST; define CKA zero variance and DEV zero SST | 63/64 TRAIN-mean + 1 deviating TEST story, every bootstrap resample; zero-variance CKA; never rerun consumed TEST |
| BLOCKER §4.9a: self-declared JSON permit | Authenticated owner/reviewer-scoped permit, independently verifiable trust root; bind exact HEAD, both source Git blobs, amendment, manifest hash, `run_id`, stage, workspace, owner/reviewer identity and one-shot policy. Absence of `code_author_id` must fail | Forged JSON, self-review, missing code author, wrong phase/run/HEAD/blob/workspace, expired/altered permit all STOP before data/model |
| BLOCKER §4.9b: empty DEV freeze, pack/marker race, replay | Durable state machine with atomic receipts: `ADMITTED → TRAIN_PACK_COMMITTED → DEV_PACK_COMMITTED → FIT_DEV_FROZEN → TEST_EXTRACTION_CONSUMED → TEST_PACK_COMMITTED → TEST_READ_CONSUMED → TERMINAL`. Verify full frozen JSON schema + SHA, bind commits/pack identities; atomic stage + fsync where available; recovery is terminal STOP, never silently rollback one-shot. No marker-only proof of successful pack commit | Empty/stale freeze, partial pack, concurrent runs, marker deletion, interrupted write, duplicate run and replay after STOP rejected |
| BLOCKER §4.9c: substituted/TOCTOU NPZ, paths/logs | Authenticate every pack by content digest and trusted stage receipt; hash **same opened bytes** parsed; validate decompressed array count/dtypes/shapes before allocation; reject symlink/reparse/redirect; enforce private path/ACL, sanitized error codes with no data payload | Same IDs with changed tensor values, hash mismatch, zip bombs/oversized member, symlink swap, log leakage, concurrent replace rejected |
| MAJOR §4.10: per-split GPU clock resets | Aggregate 60-min/model and 120-min total one-shot budget over all splits; watchdog for load, hidden/16 continuation forward, cleanup, GPU peak and Colab T4/free-only pin. Record consumption of elapsed time across stages. No unbounded operation | Fake monotonic-clock and peak-VRAM fixtures trigger STOP at every boundary; bounded throughput projection; no re-run consumed Qwen technical smokes |

## 2. Scientific statistical contract for next amendment (candidate only)

- Preserve 8 probes, TRAIN128/DEV64/TEST64, alpha `{1,10,100}`, seeds, TRAIN-only scaling, 1,000 shuffled TRAIN fits with DEV selection, 1,000 CKA permutations, 2,000 paired bootstrap.
- Keep target-oracle positive control, B-direct and TRAIN mean. Distinguish hypothesis of predictive transfer under this probe bank from CKA paired geometry; both can reflect surface-level shared features.
- Full TEST `SST<1e-8` → recorded `INCONCLUSIVE_DEGENERATE_TEST` after one-shot; no changing probes/splits or replay. Reject unqualified oracle without declaring absence of transfer.
- Bootstrap denominator candidate: freeze original whole-TEST denominator and compute resampled paired MSE difference per story; this avoids random zero denominators but **changes the estimand**, so require amendment + independent review before any TEST access.
- n=64 only `SCOPED_FEASIBILITY`, no 80% power or causal SIX-specific mechanism claims.

## 3. Integrated QA and decision, not micro-permission cycles

One engineering batch may fix every row, with new versioned sources and synthetic/negative QA evidence under the research branch only. QA must run exact Git blob-pinned sources, including split-isolation fixture, unauthenticated permit rejection, package-input SHA sabotage, missing freeze, NPZ tensor substitution, interleaved concurrent writes, crash/replay, degeneracy 63+1, near-duplicates, fake GPU clock and log sanitization. No real weights, dataset TEST or science GPU run.

Once engineering QA passes, the **same distinct reviewer or another genuinely separate reviewer** must read changed bytes and v1b protocol and issue a fresh PASS/HOLD/FAIL. Only then present **one** integrated owner decision for private source/feature storage and science one-shot. Reviewer PASS alone is not a science permit.

## 4. Immutable boundaries

- Historical T1 original SHA256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`.
- G1 manifest SHA256 `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6`, 128/64/64: do not rewrite or re-seal.
- Qwen3-0.6B and 1.7B technical one-shots: consumed, no re-run.
- `main`, PR #12, `lineage.md`, TTM-Small-4M checkpoints and other research repos remain untouched.
- No science TRAIN/DEV/TEST feature extraction, no use of unapproved Colab raw-source staging, no TEST opening.
- **Admission decision after this review: `HOLD_G1_SCIENCE`**; next task is one integrated **remediation + synthetic QA + distinct re-review**, not running science.
