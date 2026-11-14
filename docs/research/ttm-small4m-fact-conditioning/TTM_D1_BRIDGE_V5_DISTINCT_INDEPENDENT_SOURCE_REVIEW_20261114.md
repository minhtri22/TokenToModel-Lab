# Independent AI Source Review — TTM D1 Bridge V5 (2026-11-14)

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V5_DISTINCT_NEW_CHAT_INDEPENDENT_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU`  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Frozen input HEAD:** `0b7205093e70cc6473244a23d2a20ead568452c1`  
**Role:** AI scientific-protocol reviewer in a distinct chat; *self-attested only*, not a human reviewer and not an externally validated independence/custody attestation.  
**Scope:** GitHub read-only, source/design only; no GPU, training, model inference, private EVAL AST/gold, TEST/Q1Q2, git write, permit or scientific release.

## One integrated design verdict

**`HOLD_REVISE_BEFORE_PREREG` — 4/6 PASS source-scoped, 2/6 HOLD, 0 FAIL.**

V5 improves V4 substantively: aliases are separated from action IDs, raw low-entropy EVAL hashes are replaced by a hidden HMAC, an anti-replay audit procedure is specified, and exact contrastive parameters trace to the original FC01 prereg. Nonetheless **two genuine source-protocol ambiguities** prevent design release: (1) the proposed six-action ontology has no frozen coverage/typed transition mapping for all four task categories; (2) the trusted custodian/auditor key split and minimal public signed receipt do not yet establish a verifiable binding to the exact one-shot TRAIN/VAL–EVAL audit ledger. Neither gap can be solved merely by interpreting a 45/45 same-author field check as independent security/semantics QA.

**This verdict is not an owner decision and does not modify frozen science HOLD.** No `GO_DESIGN_ONLY` and no science GO are granted.

## S1–S8 — source custody at frozen HEAD

All eight files were read through the GitHub connector at the exact immutable commit. Expected vs observed **Git blob SHA-1 metadata matched 8/8**. This is **not** an independent SHA-256 rehash of original GitHub bytes; the two historic V4 SHA-256 values are recorded source claims, not independently recomputed here.

| ID | Source at frozen commit | Git blob SHA-1, expected = observed | Status |
|---|---|---|---|
| S1 | [V5 design MD](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V5_SINGLE_PACKET_SEMANTIC_ALIAS_HIDING_AUDIT_COMMITMENT_CONTRAST_PARAMS_PREREG_DESIGN_HOLD_20261114.md) | `f72c0f8381f2a81364b2411630ae709f93d5c1a1` | MATCH |
| S2 | [V5 contract JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V5_SINGLE_PACKET_SEMANTIC_ALIAS_HIDING_COMMITMENT_CONTRAST_PARAMS_SOURCE_CONTRACT_20261114.json) | `f4103f571ea80f909d59b1d9fe5f426702f53fa4` | MATCH |
| S3 | [V5 same-author QA JS](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/tools/pilot_t4/fc01/ttm_d1_bridge_v5_source_only_contract_qa_20261114.js) | `26a03f04d2ee744d368adf7aa8da6c3ed2f03683` | MATCH |
| S4 | [V5 QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V5_SOURCE_ONLY_INTEGRATED_QA_AND_SINGLE_OWNER_HOLD_20261114.json) | `03426c516ca18553aed87db86906e1d614f49606` | MATCH |
| S5 | [V4 reviewer MD](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_DISTINCT_INDEPENDENT_SOURCE_REVIEW_20261114.md) | `f1c8dc3e987b811f0d08d4784831bbf154bf1462` | MATCH |
| S6 | [V4 reviewer JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json) | `dcad6a0cf8d684b0dcadfe0b99e2ae3aa78af09c` | MATCH |
| S7 | [lineage.md L0020](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/lineage.md) | `7b2595cf0794e11a3393f543abf20e0bcbcb3804` | MATCH |
| S8 | [FC01 original prereg](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/docs/research/ttm-small4m-fact-conditioning/TTM_SMALL4M_FC01_DATA_OBJECTIVE_CAPACITY_SINGLE_PREREG_DESIGN_20261112.md) | `af80eddfb2175b58a90c2a9761f0ed339e03678a` | MATCH |

Historic uploaded V4 report SHA-256 (as recorded in S5/S6/S7): `8fd3ff6469403c9abb4cdc7672f9206c29329adf29388e8ca78fbb0df0eec47f`; V4 receipt SHA-256: `2bdb82bb4e585c158c291c7b48838985249a7063a588af71b8e32f333dcedd94`. These were not independently rehashed from downloaded GitHub raw bytes in this review.

## R1–R6 adversarial examination

| Axis | Status | Severity | Principal finding |
|---|---|---|---|
| R1/AM01 | **HOLD** | HIGH | Alias disjointness and reachable-counterexample rule are specified and resolve the V4 lexical-label conflation in principle |
| R2/AM02 | **PASS** | MEDIUM | TIME must be emitted by the model; it cannot be filled from gold |
| R3/AM03 | **PASS** | HIGH | Twelve fixed unique seeds 20261120 |
| R4/AM04 | **PASS** | MEDIUM | Integer gates are internally consistent: sum D>=308/3072; >=3 of 4 category deltas >=39/768, all 4 nonnegative; C correct >=192/768 each category |
| R5/AM05 | **HOLD** | CRITICAL | V5 materially fixes raw-hash dictionary leakage with a private keyed HMAC, per-batch random ID, one-shot ledger and Ed25519 policy |
| R6/AM06 | **PASS** | HIGH | Independent source #8 directly contains AdamW lr=1e-4, betas  |

### R1 / AM01 — HOLD · HIGH

**What passed:** Six distinct canonical IDs (`RELOCATE`, `CARRY`, `TRANSFER`, `RETAIN`, `WAIT`, `ACTIVATE`) with disjoint literal aliases; `move↔relocate` and `give↔hand over` rejected as lexical OOD; `move↔carry` must have reachable holder/state effect; no inert-log or unreachable-state OOD; ambiguities must HOLD. This directly addresses the core of `D1V4-N01`.

**Design blocker `D1V5-N01`:** `canonical_verbs[].effect` consists of English effect strings, while preconditions, permissible world-states, task goal/time/priority/guard evaluation, and the correspondence of destination/recipient/trigger to `target_id`/`qualifier_id` are not frozen. More importantly, no four-category × action/slot coverage table is present among the eight sources. `RETAIN` requires an interval, `WAIT` a trigger, `CARRY` a destination and `TRANSFER` a recipient, but the shared five-field scoring tuple does not define how all of these remain distinguishable. A counterexample oracle cannot be independently adjudicated from this source contract alone. A six-verb ontology might make a legitimate category unrepresentable; ID mismatch alone must never count as OOD.

**Must-fix in one prospective amendment:** typed domain schema, explicit pre-/postconditions and invariants for each canonical action, common admissible state and temporal/priority semantics, mapping of all four categories to the action/target/qualifier slots, plus finite positive/negative fixtures with concrete reachable and unreachable witnesses. Unrepresentable categories must be explicitly excluded/HOLD *before data creation*, not repaired after outcomes. Do not invent EVAL witnesses.

**Exact pointers:** `S2.AM01_semantic_action_alias.canonical_verbs`, `.action_novelty`, `.fixtures`; `S1 §2`; `S5 R1`.

### R2 / AM02 — PASS, design-scoped · MEDIUM

The primary output is *canonical action constrained generation*, not natural-language reasoning. Generated output must include TIME explicitly; gold must not supply time or other missing fields. Multiword aliases `hand over` and `turn on` are specified for typed lexing, though grammar `ACTION ::= AGENT SP VERB SP TARGET SP TIME (SP QUALIFIER)? TERMINAL?` is not executable by itself. **Future mandatory gate**, not a source-design PASS for the actual parser: freeze phrase boundaries, longest-match ambiguity rule, explicit NONE-TIME surface form, qualifier/recipient/trigger disambiguation, prompt-echo/quote/negation/truncation tests, >=64/64 legal positives and zero false accepts over >=64 adversarial negatives. Actual parser QA: `NOT_EXECUTED`.

**Exact pointers:** `S2.AM02_parser.grammar`, `.time`, `.quality_future`; `S1 §3`; `S5 R2`.

### R3 / AM03 — PASS, design-scoped · HIGH (inference qualification)

Verified source arithmetic: 12 consecutive unique eight-digit seeds `20261120` through `20261201`; each `D_s` is **signed integer** over 256 paired families, a positive seed requires `D_s>0`, tie is nonpositive. Under a binomial independent-seed idealization, one-sided `k>=10` of 12 has `p=(66+12+1)/4096=79/4096≈0.019287109375`, below α=.05. SHA256 namespace/seed-message derivation is prospectively specified, not executed. No claim that deterministic seed labels prove i.i.d.; valid scope is only the positive-seed probability conditional on *16 fixed OOD skeletons*, not an OOD universe or inferential mean gain >=10 percentage points. **Future gate:** real stochastic nondegeneracy and same-seed reproducibility; if absent, no inferential p-value.

**Exact pointers:** `S2.AM03_stats.seed_values`, `.D_s`, `.positive`, `.tie`, `.p_k10`; `S2.AM06_contrast_package.exact_PRNG_derivation`; `S5 R3`.

### R4 / AM04 — PASS, design-scoped · MEDIUM

Checked integer gates: global gain `ceil(12×256×0.10)=308`; category delta 5pp `ceil(12×64×0.05)=39` in >=3/4 categories; all four categories nonnegative; C must achieve >=`12×64×0.25=192` family-correct across seeds per category. No hidden all-skeleton-win requirement or significance claim for the 10pp magnitude. Require complete per-skeleton heterogeneity and failures in predeclared reporting; no post hoc gate.

**Exact pointers:** `S2.AM04_category.*`, `S1 §3`, `S5 R4`.

### R5 / AM05 — HOLD · CRITICAL

**What passed conceptually:** V5 recognizes low-entropy EVAL AST as gold-adjacent, avoids public raw SHA-256/AST, proposes secret 32-byte CSPRNG HMAC-SHA256, 16 random bytes for batch `audit_id`, JCS RFC8785+NFC canonicalization, domain separation, one shot and an Ed25519 signed public receipt. A dictionary attacker cannot test guessed ASTs against the keyed digest without the secret (conditional on secrecy and correct implementation). This is *not* zero knowledge. One-shot/no adaptive queries is a sensible response to V4 `N02/N03`.

**Design blocker `D1V5-N02`:** The pre-read append-only ledger is supposed to bind `audit_id`, protocol, `TRAIN_VAL_AST_commit`, `EVAL_AST_HMAC` and checker SHA. But the V5 signed public receipt's complete allowed field list omits the pre-read ledger digest and `TRAIN_VAL_AST_commit`/equivalent authenticated binding. A verifier cannot check that the claimed PASS corresponds to precisely the frozen TRAIN/VAL–EVAL one-shot audit solely from the minimal signed object. The custodian alone holds the HMAC key while the auditor is separately trusted to inspect the private AST; a verification flow for *same AST committed = AST audited* is not defined. “On crash: signed UNKNOWN” is not implementable if signing capability is unavailable; lack of receipt must map deterministically to HOLD. The handoff/MD and JSON describe a domain suffix and `audit_id` length with slightly different notation (16 raw bytes vs UTF-8 hex string); the intended byte encoding must be unambiguous in frozen fixtures.

**Must-fix in one prospective amendment:** a precommitted immutable ledger ID/digest authenticated by the signed receipt (and a safely disclosed or privately independently verifiable TRAIN/VAL binding), an explicit private key/AST verification path not exposing gold or HMAC key to trainer/owner, exact byte-level HMAC/JCS/Ed25519 vectors (`DOMAIN || 0x00`, UTF-8 hex ID length = 32 bytes if 16 raw bytes become 32 hex digits), signer pin and no-reuse policy, one-shot state transitions and `ABSENT/INVALID/UNKNOWN/FAIL => HOLD`. Preserve denial of per-family witnesses and adaptive query channels.

**Exact pointers:** `S2.AM05_hidden_commitment.trusted_roles`, `.hiding.message`, `.one_shot_audit.batch_lock`, `.signed_receipt.allowed_public`; `S1 §4`, `S5 R5`.

### R6 / AM06 — PASS, design-scoped · HIGH (pre-exec safeguards)

**Direct independent crosscheck with eighth source FC01**: S8 §4–§5 specifies `AdamW` (`lr=1e-4`, `betas=(.9,.95)`, `weight_decay=.1`, `grad_clip=1`), warmup 16 → cosine `1e-5` by step256, batch `16×256`, microbatch `4` and accumulation `4`, `12` core + `4` synthetic, FP32, `λ=.2`, `τ=1`, `K=4`. All agree with `S2.AM06_contrast_package.exact_candidate_training_params`. FC01 used a different exploratory design and 1 TRAIN_SEED; this proves **preexisting provenance of the candidate** values, *not* suitability/optimality for D1 structural-OOD or outcome-independent transport of performance. V5's new 12 seeds/hashed stream namespaces are prospective choices, not values copied from FC01.

Negative policy is one opposite-condition continuation from the **same TRAIN family per positive**; it must be checked *actually wrong under the positive condition* by typed semantics, not merely labeled opposite. B/C share primary LM bytes, episode order, CE token slots and optimizer updates; C has **1,024 extra negatives per seed** and more supervision/FLOPs. The only interpretable C−B estimand is a full *contrastive training package*, never a loss-only or equal-FLOPs effect. Future gate requires gradient/label validity, RNG byte SHA reproducibility, nonzero-AdamW-moment interrupted/resume equivalence, exact model/tokenizer manifest, independent rights and data-split QA. `12×3=36` runs, `36×256=9,216` optimizer steps and `36×256×2=18,432` generated outputs are **plan only**; Free T4 and paid USD 0 remain unverified. No fourth arm and no post-outcome tuning.

**Exact pointers:** `S8 §4–§5`, `S2.AM06_contrast_package.parameter_provenance`, `.exact_candidate_training_params`, `.exact_PRNG_derivation`; `S1 §5`, `S5 R6`.

## Prior issue lineage and new issues

V4 received 17 earlier issue IDs (`D1V2-01..11` and `D1V3-N01..N06`) and added four (`D1V4-N01..N04`), all traceable to the reviewed six axes; **design-scope progress is not runtime closure**. Axis allocation: R1 `D1V2-01,02`, `D1V3-N01`, `D1V4-N01`; R2 `D1V2-03,04`, `D1V3-N02`; R3 `D1V2-05,06`; R4 `D1V2-07`; R5 `D1V2-08,09`, `D1V3-N03`, `D1V4-N02,N03`; R6 `D1V2-10,11`, `D1V3-N04,N05,N06`, `D1V4-N04`. New V5 findings: **`D1V5-N01` (HIGH, R1) ontology/category/slot coverage** and **`D1V5-N02` (CRITICAL, R5) authenticated ledger–receipt/independent custodian binding**. These two are DESIGN blockers. The parser, security runtime, rights, stochastic testing and resource limits remain future implementation gates, not fresh design-failure IDs.

## What the same-author QA establishes — and does not

S3 checks 45 literal contract/cross-reference properties and mutates 15 JSON fields; S4 *reports* 45/45 and 15/15 detections, executed in same-author in-memory V8 checks rather than an independent separate CLI re-run. This supports **presence/consistency of text fields** only. It cannot attest reachable causal counterexamples, parser grammar ambiguity, real HMAC/JCS/Ed25519 vectors, signing/ACL isolation, rights, seed independence, gradient/resume or T4 affordability. This review inspected S3/S4; it did not execute their CLI, generate model outputs or access any private evidence.

## Single integrated Bước thực hiện tiếp theo

**One prospective V6 source amendment, not six micro-permits:** freeze (i) R1 category-to-typed-action/goal/time/slot coverage and concrete reachable witness fixtures, and (ii) R5 immutable pre-read audit-ledger binding to signed receipt, custodian–auditor HMAC-verification path and exact failure/encoding state machine. Then request **one distinct, read-only design GO/HOLD** based on that complete packet. Preserve V1–V5 unchanged. Only an eventual design GO can authorize *consideration* of a separate implementation QA; it does not release training, inference, GPU or D1 science.

**Unchanged controls:** `D1_BRIDGE_SCIENCE=HOLD`; `D1_EXISTING=HOLD_UNMODIFIED`; `TEST_Q1Q2=SEALED`; `FC01_EXPLORATORY=CLOSED_PASS_SCOPED`; `FC02=NOT_OPENED`; `GPU=NO`; `TRAINING=NO`; `INFERENCE=NO`; `MAIN=UNCHANGED`.
