# HANDOFF A — TTM-Small-4M Diagnosis · M0–M2

**Operation:** `TTM_TRACK_A_SMALL4M_VALIDITY_TO_FAILURE_LOCALIZATION_INTEGRATED`  
**Date / time zone:** 2026-11-16 · Asia/Bangkok  
**Owner:** người dùng, chủ repository · **PM:** ChatGPT (review theo phiên được yêu cầu, không chạy nền) · **Executor:** Agent A (chưa được gán tài khoản/phiên)  
**Research branch:** `research/ttm-track-a-small4m-diagnosis-20261116`  
**Initial base (PR #28 exact HEAD):** `ebdc54575eed1ff60c402eecf60289f408bb38ca`  
**Historical main / Question baseline:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`  
**Related:** [PR #28](https://github.com/minhtri22/TokenToModel-Lab/pull/28) (DRAFT, DO NOT MERGE), [Issue #29](https://github.com/minhtri22/TokenToModel-Lab/issues/29), [PM roadmap PR #30](https://github.com/minhtri22/TokenToModel-Lab/pull/30) (read-only), [5-step in-context-probe design](https://github.com/minhtri22/TokenToModel-Lab/tree/research/ttm-small4m-incontext-probe-roadmap-design-20261116).

> **Status at handoff:** `A_M0_OPEN · Q001_I1=HOLD_SCORER_LABEL_LEAKAGE · I2=NOT_EXECUTED · MODEL_FORWARD=FALSE · OPTIMIZER_STEPS=0 · NO_NEW_SCIENCE`. This handoff authorizes planning and code/source QA only. Existing owner conditional GO is **not** equivalent to I1 PASS on a materially amended protocol.

## 0. Non-negotiable boundaries / trách nhiệm

1. Work only in the Track A branch and scoped workspace `D:\WORK\RESEARCH\TokenToModel-Lab`. Never push directly to `main`, `lineage.md`, PR #28's source branch, Track B/C branches, or rewrite historical receipts. Proposal from A may be reviewed as a **stacked PR targeting PR #28's branch**, not automatically main.
2. Treat PR #28 as technical input, not a PASS. Confirm exact branch HEAD at start and stop if it diverged materially from the base; record the comparison. Do **not** replay historical TEST64, FRESH16, FINAL24, EXP32 or other consumed scientific evaluation as a fresh test.
3. No model forward, checkpoint loading beyond already-scoped read-only custody, training or I2 while I1 HOLD. One integrated amendment, one source/native negative QA round, one independent technical adjudication; **no micro-permits** or arbitrary new owner signatures. Scope of internal noncommercial owner use is declared, not a legal opinion about upstream data redistribution.
4. Keep native Windows QA/custody already PASS (16/16 Windows, 12-GiB committed-memory Job Object + separately sampled tree RSS; original step1024 checkpoint/tokenizer matched SHA) intact. Rerun only affected tests if the relevant source changes.
5. Use Python 3.12, PowerShell 5.1. Fail closed on hash, source, path, leak, unsafe memory, invalid rubric. GitHub commits + SHA-256 receipts are source of truth; private checkpoint/data/long raw logits remain private.

## 1. Exact evidence pin — no guesswork

- I1 verdict: `artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_I1_20261116.json`, at commit `ebdc54575eed1ff60c402eecf60289f408bb38ca`: `HOLD_I1_RESTRICTED_SCORER_LABEL_LEAKAGE`.
- Independent review: `artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_NATIVE_20261116/distinct-technical-review.md`; native receipt adjacent. Reviewed source candidate `6dc04c0545b28d4a0cad21ad8be8b70461c57790`.
- Code: `tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/ttm_sm4m_diag_q001.py`. In `put(...)`, `opts=[gold]` followed by sorted low-ID distractors; restricted top-1 uses first-listed argmax. This is label-derived candidate construction.
- Negative control recorded: constant logits score **80/80** restricted; blind ID-based, prompt-free scorer scores **15/16 recombined, 16/16 novel IDs, 16/16 counterfactual**, yet 0/16 full-vocabulary in those three. One of 16 recombined cases reuses the exact queried TRAIN key-value pair; six reuse any TRAIN binding.
- Frozen Q001 contract **as historical baseline only**: 24 TRAIN + 56 probe = 80; seed 20261116; max 256 CPU optimizer steps; 900 seconds; 12 GiB cap; 1 GiB output; T4 step1024 checkpoint SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; tokenizer source SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Frozen fixture SHA256 `5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a` represents the **old, invalid-for-Q1-scorer** interpretation. Keep immutable, do not silently replace; new protocol requires a new ID/version/hash.
- T4 source packs per `tools/pilot_t4/integrated/t4_data_pack.py`: `ids = bpe.encode(text) + [EOS_ID]`. Therefore the proposed induction prompt `[EOS][S][S]` in the design branch **does not follow this construction without a separate explicit control**.
- Historical VAL vs bigram NLL improvement 11.88%, TEST ~12.33%, but FRESH16 H1 0/16. None establishes a root cause.

## 2. M0 — Measurement-validity remediation (highest priority, week 1)

**Goal:** A source-level defensible measurement. Do not optimize the model to pass an invalid ruler.

1. Reproduce the unrestricted vs four-choice artifact entirely on **mock logits**, with exact old fixture, without opening checkpoint. Write reproducible negative tests: (a) constant equal logits; (b) blind fixed token-ID ranking; (c) permute candidate order; (d) mutate gold while holding context fixed; (e) swap queried bindings; (f) draw random candidate sets / unseen token IDs; (g) compare full-vocab versus candidate-only.
2. Introduce **gold-independent** candidate generation from prompt/context or a predeclared deterministic public fixture rule, with no hidden gold/label access. Restrict negative controls to the same visible information as the scorer. Tie-breaking must not depend on gold or first-choice placement. Avoid interpreting chance=25% unless choice balancing and label distribution justify it.
3. Audit group independence at **queried key-value binding**, parent, context and tokenizer-ID levels, not just exact-context hash. The old frozen fixture is preserved as failed evidence; create a **new versioned fixture** if repair changes items/splits. Record case-level SHA, group-level SHA, and old/new relationship. Do not keep old thresholds by default.
4. Propose **one amendment** declaring revised endpoint hierarchy: primary teacher-forced gold token NLL, rank, full-vocab top-1; context-conditioned contrast or log-odds as complementary endpoint; candidate-only performance strictly secondary and valid only after anti-shortcut controls. Predeclare positive/negative controls, success/fail/inconclusive regions, power/sample limits and one-shot budget **before observing model outputs**.
5. Independent QA must read a source pin distinct from the author, reproduce negative-control outcomes and check label invisibility. `I1_PASS` requires validated scorer+fixture+runner together, not a count of native QA passes. If any critical flaw remains `HOLD_I1` with one explicit blocker and minimal repair path.

**M0 artifacts:** `docs/research/ttm-abc/track-a/Q001_MEASUREMENT_AMENDMENT.md`, tests and fixture generator under current scoped Q001 tools, versioned manifest JSON, `artifacts/ttm-abc/track-a/M0_<run-id>_SOURCE_QA.json`, `.../M0_<run-id>_INDEPENDENT_REVIEW.md`.

## 3. M1 — Forward-only, teacher-forced capability diagnosis (week 1–3; separate prospective experiment)

**Not an automatic extension of Q001 GO.** Design and independent review now; execute only under the appropriate scoped owner decision after admission.

- Probe A: duplicated random-token strings, per-position teacher-forced `NLL(first S)-NLL(second S)` excluding first token of repeat. Controls: shuffled S, mismatched S', random init, EOS placement `BPE(text)+EOS` vs explicit `EOS+S+S`, length and position matched; verify actual prompt tokens and no train overlap.
- Probe B: paired entity/object swaps with **same bag of words**, balanced query-first/query-last, varied neutral gap length. Primary paired log-odds difference and sign; report `P(o1)+P(o2)` and candidate rank to detect low-mass artifacts. Validate that candidate strings encode to exactly intended token IDs or score full multi-token strings by summed logprob; never silently treat a multi-token object as one token.
- Controls: step1024 checkpoint vs at least three random-init seeds; optional M1280 only if its exact SHA `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`, provenance, optimizer/schedule and rights are checked. M1280 is a continuation, not an independent seed. Do not claim that change is caused by 256 extra steps unless data/schedule are equal.
- Design status: 5-step branch authored externally is `DESIGN_PROPOSAL_NOT_AUTHORIZED` and unreviewed. Challenge proposed 7,680/400 item counts and 0.3/2.0 nats thresholds with time/resource feasibility and pilot-independent power arguments; do not adopt as frozen facts.

**M1 outputs:** pre-registered question, fixture SHA, checked scorer, CPU resource preflight, arm/seed/position table, effect size + interval, validity verdict (`A_COPY`, `B_BINDING`, `RECENCY_ONLY`, `INCONCLUSIVE`, `INVALID_PROBE`) without inference beyond measured scope.

## 4. M2 — One Q001 I2 / failure localization (week 2–4)

**Conditional:** only if M0 I1 passes for a protocol and owner conditional GO is explicitly applicable to that exact amended scope. No automatic reassignment of old permits or reused one-shot nonce.

- Preserve original model, 24 TRAIN, 56 probe, seed, max 256 steps unless amendment explicitly versioned and approved **before execution**.
- One guarded CPU run with strict checkpoint/schema, step0 baseline, shifted labels, gradient finiteness, update delta, training NLL, held-out full-vocab gold NLL/rank/top-1, counterfactual paired effects, and output integrity. Do not collapse into a four-way accuracy headline.
- Adjudicate **implementation vs memorization vs in-context copy vs binding vs decoding/rater**; evidence may be insufficient for causal root cause, then record `ROOT_CAUSE_NOT_IDENTIFIED`.
- No historical TEST/FINAL24 reuse, no silent rerun, no tuning after reading results.

## 5. Acceptance / deliverables / PM review

| Gate | Definition of complete | Evidence |
|---|---|---|
| A0 (source) | Exact input HEAD, negative repro, candidate branch hygiene | Source pins and diff |
| A1 (measurement) | Gold-independent scorer + fixture + negative controls PASS | Mock test report + independent adversarial QA |
| A2 (runtime) | Changes covered by Windows 3.12/PS 5.1 safety QA; old untouched QA inherited only with file diff | Native report + hash/readback |
| A3 (prospective design) | Copy/binding probe endpoints, valid positive/negative controls, budget and one scoped question | Review + pre-registration |
| A4 (science conditional) | Only authorized guarded I2/probe run with receipt; otherwise `NOT_EXECUTED` | Run-ID and hash artifacts |
| A5 (adjudication) | Evidence-anchored `PASS/HOLD/FAIL/INCONCLUSIVE` per capability, not global claim | Independent review; PM acceptance |

**Agent A handback format:** exact HEAD, base SHA, changed files, source/fixture SHA256, QA rows (author vs independent), scientific scope, blocker, decision and **one** next action. Open a draft stacked PR A → PR #28 source branch for proposed code; do not merge. PM checks scope, adversarial controls, protocol amendment and dependencies before authorizing follow-on work.

**Interface to B:** hand off validated full-vocab scorer/teacher-forced evaluation contract; B must not depend on completing Q001 science.  
**Interface to C:** hand off valid capability endpoints, contamination exclusions, dataset hypotheses; C design may proceed but new science waits for validity.  
**Excluded:** architecture rewrites, SFT, scale experiments, T5/T6 parity, P07/P08, publish weights.

**Bước thực hiện tiếp theo — duy nhất:** `A_M0_GOLD_BLIND_SCORER_FIX_SPLIT_LEAK_NEGATIVES_AND_SINGLE_I1_REVIEW`.