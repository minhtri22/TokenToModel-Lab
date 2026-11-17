# Track A · Q001 M0 — Measurement amendment v3 (prospective; not released)

**Operation:** `A_M0_GOLD_BLIND_SCORER_FIX_SPLIT_LEAK_NEGATIVES_AND_SINGLE_I1_REVIEW`  
**Date:** 2026-11-16 · **Status:** `SOURCE_ONLY_PROPOSAL` · **I1:** `HOLD` until end-to-end admission  
**Research branch:** `research/ttm-track-a-small4m-diagnosis-20261116`

## 1. Why a new protocol is mandatory

The historical Q001 I1 result is **HOLD_I1_RESTRICTED_SCORER_LABEL_LEAKAGE**, not a model failure or success. In source commit `6dc04c0545b28d4a0cad21ad8be8b70461c57790`, `put()` creates `opts=[gold]` and fills it with low-ID distractors. Python's first-match restricted argmax converts equal logits into **80/80** apparent accuracy. A fixed, context-blind ID-ranking vector also yields 15/16 recombined, 16/16 novel-ID and 16/16 counterfactual restricted, despite 0/16 full-vocabulary for all three. Old ≥12/16 restricted thresholds therefore **cannot** be carried over.

The frozen historical fixture SHA-256 `5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a` remains immutable and invalid for the former restricted-Q1 interpretation. Do not overwrite or silently reinterpret it. Original I1 decision, original checkpoint custody, older 16/16 native QA and one-shot nonce are preserved.

## 2. Scope of v3 implementation

The separate `tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/q001_m0_goldblind.py` is a *new* stdlib-only, mock-token scientific measurement proposal. It does not import a checkpoint, call torch, claim an I2 nonce, modify the legacy runner or authorize model science. Its mock inventory is synthesized as IDs 300–499 and is **not** proof of private tokenizer custody.

The proposed four candidates use only (a) the visible nine-token context, (b) declared `NO_ANSWER` role, and (c) a predeclared candidate value pool. They are never computed from `gold`. A fourth value is deterministically chosen using the context hash, and candidate order is deterministically keyed to the visible context. Gold is only consumed by **metric computation**, not candidate selection. A unique maximum is required; ties abstain independently of order. No claim of 25% chance is made without evaluating actual choice distribution, class frequencies and a predeclared null.

The 24 TRAIN / 56 probe split and group names remain as **design counts**, not a replay of consumed historical science. Recombined and absent holdouts must contain **zero** TRAIN key–value bindings across either of their two context positions. Novel ID cases must exclude TRAIN key/value token IDs. Counterfactuals deliberately reuse TRAIN keys and parent bindings and are **parent-linked paired cases**, not independent held-out observations. All records and groups have versioned, deterministic SHA-256, with a separate fixture digest. Context uniqueness alone is insufficient.

## 3. Measurement hierarchy and validity

| Priority | Endpoint | Interpretation |
|---|---|---|
| Primary 1 | Teacher-forced gold next-token **full-vocabulary NLL** | Numeric proper scoring rule at the ninth-token context position |
| Primary 2 | Full-vocabulary gold rank + full-vocabulary greedy top-1 | Whether target survives 2,048-way competition; tie explicitly abstains |
| Complementary | Context-conditioned paired log-odds / contrast margins | Matched parent/swap comparisons; require sign and context dependence, report low candidate mass |
| Secondary only | Gold-blind four-candidate accuracy | Descriptive with null controls; **not** a stand-alone capability claim |

A context-free fixed-ID scorer, uniform logits, value-only scorer, constant `NO_ANSWER`, choice permutations, swapped gold labels, swapped queries, random candidate fourth values, novel IDs and parent-leak checks are **negative controls**. An explicit oracle and exactly matched query-context change are **positive controls** for fixture validity, not model performance. For eventual copy/binding, random-init controls and EOS-placement controls are prospective experiments and *not* part of M0 execution.

## 4. Single prospective analysis, sample limits, conditional decisions

A valid I1 requires (i) complete implementation+fixture+one-shot runner wired to the **same** amended protocol, (ii) deterministic source/real-tokenizer inventory/fixture hashes and strict parent/binding overlap report, (iii) passing adversarial negatives and Python 3.12 / PowerShell 5.1 native safety readback for affected paths, and (iv) a genuinely **distinct reviewer** inspecting exact amended bytes and signing a decision. Passing mock tests alone does not constitute I1 PASS.

**Regions:** `I1_PASS` only when all validity conditions are verified. `HOLD_I1` for a missing runtime integration, reviewer, hash, split or a shortcut. `INVALID_PROBE` if a negative control satisfies the proposed criterion using label-free scores or a case is contaminated. `INCONCLUSIVE` for insufficient statistical precision. For prospective model outputs, report raw paired effects, per-group counts, confidence intervals/uncertainty and exact denominator. No new numeric ability thresholds or p-value cutoff is authorized by this source-only amendment. With n=8 or n=16 and parent-linked counterfactuals, estimates are low-power and not 56 independent observations.

**Budget:** M0 uses only deterministic in-memory synthetic fixtures, zero optimizer steps, zero model forwards, and no checkpoint opens. This is not an I2 run. Eventual I2 is a separate **single** 256-step max, 900-second/12-GiB guarded CPU experiment only after this amended protocol has I1 release and the owner conditional GO is demonstrably applicable to that exact new Question/fixture/source; no old nonce or historical TEST/FRESH16/FINAL24/EXP32 is consumed or replayed.

## 5. Exact lineage and scope limits

Historical source: `6dc04c0545b28d4a0cad21ad8be8b70461c57790` · I1 receipt: `artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_I1_20261116.json` at `ebdc54575eed1ff60c402eecf60289f408bb38ca`. Original checkpoint SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, tokenizer source SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; these are inherited custody claims, **not** newly read private bytes.

Track A v3 mock manifest is a new artifact, **not the original 80-record fixture**, despite equal count and seed. No old threshold, model result or release signature transfers by implication. PR #33 remains DRAFT stacked onto PR #28, not main. Main, `lineage.md`, Track B/C, the PR #28 branch, original receipts and private data are untouched.

**For B:** a proposed full-vocabulary teacher-forced evaluator contract, contingent on implementation review. **For C:** strict split/parent leakage taxonomy and negative-control rules, not science performance.

**Next action:** independent, exact-HEAD end-to-end integration and native reviewer admission for this amended v3 protocol as one integrated gate; **do not run I2** while HOLD.
