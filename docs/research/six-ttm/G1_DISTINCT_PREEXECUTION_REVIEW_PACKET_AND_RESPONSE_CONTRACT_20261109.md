# G1 — Independent pre-execution reviewer packet

**Status:** `PENDING_TRULY_DISTINCT_SCIENTIFIC_REVIEW`. **No reviewer verdict is attached.**  
**Prepared:** 2026-11-09. **Scientific TEST and Qwen feature extraction:** NOT RUN.

## Reviewer mandate — single integrated decision

An author-distinct scientist/agent should review **source code, exact blob pins and methodological v1a amendment**, not merely the author's synthetic PASS output. Reviewer returns one complete `PASS_DISTINCT_REVIEWER`, `HOLD`, or `FAIL` verdict with identity, independent affiliation/agent run ID, date, exact source/blob hashes, inspected tests, unresolved findings and required changes. The result must be committed to the research branch as a **new** append-only review, not overwriting this request. The code author and the assistant who generated the packet must **not self-sign**.

### Stable material identifiers

| Material | Git blob SHA |
|---|---|
| Original prereg candidate JSON | `de049ba00331d90f3c7ae72ab3daf943c766ec82` |
| Original methods & thresholds | `9dcbf31b2835e07922b2aaf66e5895c7d2f8b03b` |
| Source mapper and private G1 metadata producer | `aee230060f8202907953e0eeab0ae5b1099a584e` |
| Private G1 29-gate metadata QA | `7dfc6bea2cee1773c20fee655691fc366a6a9ecd` |
| Science core `g1_science_core_v1.py` | `b3ea8c890c45e3e2d248ad850977b53f5782552e` |
| Feature extractor `g1_science_private_feature_extractor_v1.py` | `f1557470ff66857e35ced71641b542685f6b3083` |
| Adversarial QA `g1_science_adversarial_qa_v1.py` | `e6a93ac8248665de78d970ef9d237de5a45d9d8c` |
| Integrated QA `g1_science_preexecution_integrated_qa_v1.py` | `c022de4bdc2eae88b61d1ea2d578302c25c12445` |
| T1 split 2368 IDs (SHA256) | `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9` |
| G1 private prefix manifest SHA256 | `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6` |
| Qwen0.6B weight SHA256 | `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b` |
| Qwen1.7B shard1 SHA256 | `169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5` |
| Qwen1.7B shard2 SHA256 | `912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9` |

See separate v1a amendment `G1_V1A_DATA_MAPPING_DEDUP_FUNCTIONAL_ALIGNMENT_AMENDMENT_REVIEW_CANDIDATE_20261109.md`. **Original prereg is unchanged**.

## Synthetic QA claimed by code author — MUST NOT count as independent peer review

Exact tested files source-pinned; CPU environment Python 3.13.5 / NumPy 2.3.5:

```text
PASS_SYNTHETIC_ONLY_NO_SCIENCE, tests=6
PASS_ADVERSARIAL_SYNTHETIC_QA_NO_SCIENCE, checks=14
PASS_EXTRACTOR_SYNTHETIC_ONLY_NO_FILES_OR_GPU, probes=8
PASS_INTEGRATED_SYNTHETIC_QA_SOURCE_PINS, source_blobs_verified=3
PASS_FULL_LOOP_SYNTHETIC_1000_PERM_1000_CKA_2000_BOOT
```

The 1000/1000/2000 test used *small synthetic feature dimensions*, not actual 1024/2048 Qwen data. It confirms code paths, not timing or GPU science. No real G1 response computed, no science verdict, no TEST source reopened.

Reviewer should independently run **fresh tests** (not just script outputs), including: linear ridge dual vs closed-form, A→P composition equivalence, relative-alpha fairness for each shuffled fit, train-only scaling, DEV-only selection, 8-probe continuation score indexing under separate tokenization, first-occurrence mapping reproducibility, prefix de-dup across G1 splits, 29-gate manifest proof, and TEST marker before *any* TEST feature read. Check that negative control corruption is detected, that test exhaustion prevents reuse and that a missing reviewer/owner authority blocks science. The current QA does **not** establish independent agreement on all these contracts.

## Required methodological findings to adjudicate

1. **v1a source mapper:** original 2368 T1 identities are content SHAs, source-row index first occurrence is a new convention; pre-TEST amendment versus original prereg. Duplicated raw content had 363 selected identity extra occurrences. Is this acceptable without selection bias?
2. **v1a dedup:** 23 duplicate prefixes removed before selecting 128/64/64; validate deterministic order and that no TEST labels were used.
3. **Orthogonal null:** a full-rank rotation in an isotropic-ridge normalized space preserves information; relabel F-random as *neutral basis diagnostic*, not negative evidence. Check geometry and CKA implementation.
4. **Linearity:** G1 A→P remains a linear source-hidden mapping; B-direct must receive fair equal-budget comparison and mechanism conclusion must be restrained.
5. **Score semantics:** `prefix_token_ids + continuation_token_ids` vs raw concatenation; check causal shift `prefix_len-1 + i`, UTF-8 byte scaling and all eight strings.
6. **Statistics and power:** 1,000 TRAIN-pair shuffles each DEV-select alpha, 2,000 paired story bootstrap, macro 8D R² vs TRAIN mean, CKA shuffle p, oracle threshold and degeneracy stops. TEST=64 is scoped feasibility, not verified 80% power.
7. **One-shot/test:** core PREP reads only TRAIN + DEV numeric packs; TEST extraction may happen only after DEV fit frozen; TEST pack is opened only after exclusive TEST-read marker. Review forced STOP cases, stale files, content IDs, symlinks and ability to corrupt or forge documentary review/permit JSON.
8. **Data rights:** owner's **earlier** approval was for local TinyStories TRAIN scan and hash-only G1 manifest. It did **not** authorize copying original corpus to Colab nor storing teacher numeric features. Future `private_source_staging_approved` and numeric feature handling must be explicitly included in **one combined science-owner decision**. No raw/derived teacher tensor may be published on GitHub.
9. **Practical workload:** sequential Qwen0.6 / Qwen1.7B loading, 16 continuation forward passes per prefix, T4 memory/CPU, max 60 minutes/model and 120 total. Synthetic QA is **not** a runtime GPU endurance check; independent reviewer must assess feasibility and fail-closed resource behavior.

## Distinct review output contract

Reviewer must provide one signed source-backed artifact including:

```text
review_schema=ttm.six.g1.distinct_preexec_science_review.v1
reviewer_id=<independently verified human or genuinely separate agent execution>
reviewer_is_code_author=false
reviewed_branch=<exact research branch>
reviewed_core_blob=b3ea8c890c45e3e2d248ad850977b53f5782552e
reviewed_extractor_blob=f1557470ff66857e35ced71641b542685f6b3083
reviewed_v1a_amendment=<exact reviewed blob>
independent_tests=<source, methods, receipts>
risks_and_open_findings=<specific evidence>
outcome=PASS_DISTINCT_REVIEWER | HOLD | FAIL
science_authorization=NOT_ISSUED_BY_REVIEW_ALONE
```

No self-signed review; `PASS` only with substantive independent analysis. Permit ownership and final science authorization remain separate from reviewer verdict, bundled as **one integrated admission decision**. No re-running Qwen technical one-shots, T1, Seal or metadata QA.

## Reviewer service discovery status

Available Notion Custom Agent search was attempted for `scientific code review`; provider returned `entitlement_required` (Business plan), **no agent executed**. Connected Codex Native tool needs an opaque current-turn token not supplied in this conversation; no claim of a distinct Codex review. Thus `DISTINCT_REVIEW=NOT_COMPLETED` and `SCIENCE_LOCK=HOLD`.

**Immediate gate:** obtain source-pinned distinct review and an owner-approved data-staging/numeric-feature scope in one review packet. Until then, existing code permits `--mode synthetic-qa` only; no real feature extraction or private TEST access.
