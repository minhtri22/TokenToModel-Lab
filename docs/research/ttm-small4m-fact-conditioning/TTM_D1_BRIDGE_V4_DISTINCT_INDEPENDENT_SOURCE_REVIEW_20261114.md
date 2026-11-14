# Independent AI Source Review — TTM D1 Bridge V4 (2026-11-14)

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V4_DISTINCT_NEW_CHAT_TASK_RELEVANT_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU`
**Repository:** `minhtri22/TokenToModel-Lab`
**Frozen scientific/source input HEAD:** `1c923c0dc1a064411190392612e9d2475486bd2c`
**Independence:** `INDEPENDENT_NEW_CHAT_AI_SELF_ATTESTED` (not human, not externally identity/custody verified).
**Review mode:** `READ_ONLY / DESIGN_ONLY / SOURCE_ONLY / NO_GPU / NO_TRAIN / NO_INFERENCE / NO_PRIVATE_GOLD / NO_TEST_Q1Q2`.

## Decision

**Single design verdict: `HOLD_REVISE_BEFORE_PREREG`** — 3/6 PASS scoped design, 3/6 HOLD, 0 FAIL. This is a review finding, not a new owner authorization or a science outcome.

V4 materially improves V3, especially mandatory TIME in generated text, sign-test arithmetic, disclosure of gold-adjacent AST risk and relabeling the C-v-B contrast as a package effect. Remaining *design-level* blockers are: lexical-alias versus semantic-action equivalence, confidentiality/lifecycle of the AST audit commitment, and frozen contrastive training parameters. Real-world tests remain future gates, not false source-level PASS.

## S1–S7: frozen GitHub source custody

Verified through GitHub connector at exact commit; expected SHA-1 matched `fetch_file.result.sha` for all 7. This is Git blob metadata/content from one connector channel, **not independent SHA-256 hashing of fetched raw bytes**. V3 report SHA-256 values are claims recorded in its handoff/lineage, not rehashed here.

| ID | Source | Git blob SHA-1 (expected = observed) | Status |
|---|---|---|---|
| S1 | [V4 design Markdown](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_SINGLE_PACKET_TASK_RELEVANT_OOD_PARSER_AUDITOR_CONTRAST_PREREG_DESIGN_HOLD_20261114.md) | `39f89d8fa111b3b15d34f47b4a776c61bc6e42a2` | PASS_METADATA |
| S2 | [V4 machine-readable JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_SINGLE_PACKET_TASK_RELEVANT_OOD_PARSER_AUDITOR_CONTRAST_PREREG_DESIGN_HOLD_20261114.json) | `e89284318ce49c2cb0373dc37660216eb532904d` | PASS_METADATA |
| S3 | [V4 same-author QA JS](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/tools/pilot_t4/fc01/ttm_d1_bridge_v4_source_only_contract_qa_20261114.js) | `d459882694651d5e8e8455c30abc0a90dba8e444` | PASS_METADATA |
| S4 | [V4 source-only QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_SINGLE_PACKET_SOURCE_ONLY_QA_AND_OWNER_HOLD_20261114.json) | `09eb5882c68e7cb45e82d4e4d85891ae0bdb31e4` | PASS_METADATA |
| S5 | [V3 independent review Markdown](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_DISTINCT_INDEPENDENT_PREREG_SOURCE_REVIEW_20261114.md) | `0ef0a578262daa6379a2b3af25d3a3c2e9b05fb8` | PASS_METADATA |
| S6 | [V3 independent review JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json) | `425260e35a3c2d798058ea35d8007144072bcbd3` | PASS_METADATA |
| S7 | [lineage.md (L0019)](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/lineage.md) | `c7eb0cfd417876b456ce3f5b4616c2d989a1f076` | PASS_METADATA |

## R1–R6: adversarial review

### R1 / AM01 — HOLD (HIGH)
**Finding:** Reachable task-policy counterexample and inert-trace rejection substantially improve V3. But action-word literal swap fixture is ambiguous: a surface alias for the same canonical verb must be separated from a different canonical verb/action. No final task-ontology equivalence contract explicitly resolves this.
**Action/gate:** Freeze typed canonical verb/action IDs, an explicit surface-alias equivalence relation, and paired fixtures: same action alias => equivalent; different task-relevant canonical verb/action => distinct only when genuine reachable causal policy counterexample exists. Preserve goal and time semantics; no lexicon shortcut.
**Exact source pointers:** `S2.AM01_task_relevant_OOD.task_semantics.canonicalization`; `S2.AM01_task_relevant_OOD.task_semantics.causal_difference_proof`; `S2.AM01_task_relevant_OOD.synthetic_preexec_fixtures[action_word_literal_swap_only]`.
**Issue coverage:** `D1V2-01`, `D1V2-02`, `D1V3-N01`.

### R2 / AM02 — PASS (HIGH_FUTURE_GATE)
**Finding:** TIME is explicit and mandatory, including NONE via a spoken/frozen phrase; tuple includes time. Generated text, not gold, supplies scored fields. Primary claim correctly restricted to bounded canonical-action generation; 64 positive and >=64 negative independent synthetic tests are prospective, not achieved.
**Action/gate:** Before science, SHA-pin disjoint lexicon/tokenization, phrase boundaries, ambiguity rejection, no-gold completion; test multiword TIME, NONE, agent/target/condition errors, paraphrase false negatives, truncation, prompt echo, quote-only, negation and 64/64 positives with zero false accepts on >=64 negatives.
**Exact source pointers:** `S2.AM02_parser_oracle.grammar.ebnf`; `S2.AM02_parser_oracle.measurement_validity.independent_preexec_fixture_contract`.
**Issue coverage:** `D1V2-03`, `D1V2-04`, `D1V3-N02`.

### R3 / AM03 — PASS (HIGH_FUTURE_GATE)
**Finding:** Exactly 12 frozen unique seeds, signed integer D_s over 256 paired families, D_s>0 positive, zero negative/nonpositive; exact one-sided binomial threshold k>=10 of 12 and conditional fixed-skeleton scope mathematically consistent. Stream independence is not demonstrated.
**Action/gate:** Freeze actual PRNG derivation and prove same-seed digest reproducibility, different seed stochastic nondegeneracy, no missing/selectively rerun seeds. No mean>=10pp inferential claim.
**Exact source pointers:** `S2.AM03_statistics.seed_values`; `S2.AM03_statistics.exact_sign_test`; `S2.AM03_statistics.independence`.
**Issue coverage:** `D1V2-05`, `D1V2-06`.

### R4 / AM04 — PASS (MEDIUM_FUTURE_GATE)
**Finding:** Integer thresholds 308/39/192 are correct and category checks scoped to 12 seeds × 64 families. Mandatory per-skeleton heterogeneity disclosures avoid hidden 'all 16 skeletons benefit' claims.
**Action/gate:** Report all skeleton-level gains and cue-shortcut probes without post-hoc decision thresholds. Keep aggregate >=10pp as descriptive gate, not p-value about magnitude.
**Exact source pointers:** `S2.AM04_category.integer_gates`; `S2.AM04_category.skeleton_diagnostics_no_new_hidden_threshold`.
**Issue coverage:** `D1V2-07`.

### R5 / AM05 — HOLD (CRITICAL)
**Finding:** V4 appropriately treats EVAL_AST as answer-determining and designates a trusted isolated auditor. However EVAL_AST_commitment in an externally visible receipt is not specified as hiding for potentially enumerable/low-entropy synthetic ASTs; a raw unsalted hash is not confidentiality. A 'one sealed batch' statement also lacks unique protocol/batch identity, no-repeat/replay-resistance enforcement, versioned failure behavior and disclosure/access policy for commitments. Actual ACL/key/signer proofs are pending.
**Action/gate:** Predefine hiding commitment (secret per-batch nonce/HMAC under custodian key or equivalent) with threat analysis; define visibility, key/nonce custody, canonical byte encoding, signature fields and verification, immutable audit identity, no adaptive retries or queries, and signed fail-closed UNKNOWN. Require a distinct auditor/custodian policy plus denied-read/log tests before science.
**Exact source pointers:** `S2.AM05_custody_rights.authenticated_receipt.fields`; `S2.AM05_custody_rights.sealed_workflow`; `S2.AM05_custody_rights.threat_model.adaptive_oracle_risk`.
**Issue coverage:** `D1V2-08`, `D1V2-09`, `D1V3-N03`.

### R6 / AM06 — HOLD (HIGH)
**Finding:** Attribution is now correctly limited to C negative supervision + contrastive loss + extra compute package versus B. But exact negative ratios/coefficient, LR/schedule and RNG derivation remain undecided; preserving them for post-design implementation without an immutable pre-outcome selection rule leaves experiment-defining choices open. Real implementation/resource claims still unverified.
**Action/gate:** In integrated V5, lock exact ratios, coefficients, negative-label construction, LR/schedule, RNG algorithm/namespaces, exposures/FLOPs accounting and complete fail-closed resource/resume plan prospectively before any outcomes. Do not add fourth arm or claim objective-only.
**Exact source pointers:** `S2.research_question.primary_estimand`; `S2.AM06_contrast_control_resource.frozen_negs_spec_required.ratio_coefficient`; `S2.AM06_contrast_control_resource.randomness_non_degenerate.root`; `S2.AM06_contrast_control_resource.AdamW_resume_required`; `S2.AM06_contrast_control_resource.Free_T4_resource_gate`.
**Issue coverage:** `D1V2-10`, `D1V2-11`, `D1V3-N04`, `D1V3-N05`, `D1V3-N06`.

## Complete 17/17 inherited issue coverage

`ADDRESSED_DESIGN_SCOPED` does not mean implemented or independently executed. `OPEN_DESIGN_BLOCKER` participates in this HOLD. `PROSPECTIVE_RUNTIME_GATE` is not a V4 source-level FAIL.

| Issue | Axis | Current status | Reason | Source pointer |
|---|---|---|---|---|
| `D1V2-01` | R1 | `OPEN_DESIGN_BLOCKER` | Semantic action ontology and OOD witness alignment | `S2.AM01_task_relevant_OOD.task_semantics.canonicalization` |
| `D1V2-02` | R1 | `OPEN_DESIGN_BLOCKER` | Task-relevant novelty vs lexical shortcut | `S2.AM01_task_relevant_OOD.task_semantics.canonicalization` |
| `D1V2-03` | R2 | `ADDRESSED_DESIGN_SCOPED` | TIME explicit; parser/runtime pending | `S2.AM02_parser_oracle.grammar.ebnf` |
| `D1V2-04` | R2 | `ADDRESSED_DESIGN_SCOPED` | Unique gold A/B and synthetic QA criteria prospective | `S2.AM02_parser_oracle.grammar.ebnf` |
| `D1V2-05` | R3 | `ADDRESSED_DESIGN_SCOPED` | Strict signed integer, zero nonpositive | `S2.AM03_statistics.seed_values` |
| `D1V2-06` | R3 | `ADDRESSED_DESIGN_SCOPED` | Conditional seed inference only; iid pending | `S2.AM03_statistics.seed_values` |
| `D1V2-07` | R4 | `ADDRESSED_DESIGN_SCOPED` | Correct integer categories and heterogeneity disclosures | `S2.AM04_category.integer_gates` |
| `D1V2-08` | R5 | `OPEN_DESIGN_BLOCKER` | Gold-adjacent auditor model needs hidden commitment | `S2.AM05_custody_rights.authenticated_receipt.fields` |
| `D1V2-09` | R5 | `OPEN_DESIGN_BLOCKER` | Receipt lifecycle, ACL/rights and signer policy | `S2.AM05_custody_rights.authenticated_receipt.fields` |
| `D1V2-10` | R6 | `OPEN_DESIGN_BLOCKER` | Exact intervention parameters pending | `S2.research_question.primary_estimand` |
| `D1V2-11` | R6 | `PROSPECTIVE_RUNTIME_GATE` | Free T4 feasibility and restart unverified | `S2.research_question.primary_estimand` |
| `D1V3-N01` | R1 | `OPEN_DESIGN_BLOCKER` | Action-alias vs semantic-verb swap distinction | `S2.AM01_task_relevant_OOD.task_semantics.canonicalization` |
| `D1V3-N02` | R2 | `ADDRESSED_DESIGN_SCOPED` | TIME grammar synchronized | `S2.AM02_parser_oracle.grammar.ebnf` |
| `D1V3-N03` | R5 | `OPEN_DESIGN_BLOCKER` | AST gold-adjacent correctly stated; receipt confidentiality unresolved | `S2.AM05_custody_rights.authenticated_receipt.fields` |
| `D1V3-N04` | R6 | `ADDRESSED_DESIGN_SCOPED` | Package, not loss-only, estimand | `S2.research_question.primary_estimand` |
| `D1V3-N05` | R6 | `PROSPECTIVE_RUNTIME_GATE` | Actual stochastic root/stream QA pending | `S2.research_question.primary_estimand` |
| `D1V3-N06` | R6 | `ADDRESSED_DESIGN_SCOPED` | 44/44 +15/15 same-author contract checks not semantic QA | `S2.research_question.primary_estimand` |

## New V4 findings

| ID | Severity | Finding | Source |
|---|---|---|---|
| `D1V4-N01` | HIGH | Action lexical aliases and semantic verbs not sharply disjoint | `S2.AM01_task_relevant_OOD.synthetic_preexec_fixtures[action_word_literal_swap_only]` |
| `D1V4-N02` | CRITICAL | EVAL_AST_commitment confidentiality is not defined for enumerable AST | `S2.AM05_custody_rights.authenticated_receipt.fields` |
| `D1V4-N03` | HIGH | Single-audit replay/no-retry identity protocol underspecified | `S2.AM05_custody_rights.sealed_workflow` |
| `D1V4-N04` | HIGH | Treatment-defining contrastive ratios/loss/LR/RNG details still floating | `S2.AM06_contrast_control_resource.frozen_negs_spec_required.ratio_coefficient` |

## Independent source arithmetic audit

- Unit of `success`: family correct on **both** A and B. `D_s = sum_{f=1}^{256}(success_C - success_B)` is a signed integer; positive iff `D_s > 0`, tie zero is nonpositive.
- Exact one-sided binomial sign-test for iid idealization, n=12: `p(k=9)=299/4096=0.072998046875`; `p(k=10)=79/4096=0.019287109375`; `p(k=11)=13/4096=0.003173828125`; `p(k=12)=1/4096=0.000244140625`. At alpha=.05, k>=10 passes the sign component.
- Hypothetical sign-only power under iid Bernoulli P(seed positive)=.7/.8/.9: `0.252815347855 / 0.558345748480 / 0.889130022255`; *not empirical power*. Combined gates cannot have greater power than sign component.
- Aggregate gain count: `ceil(12 × 256 × 0.10)=308`. Category gain: `ceil(12 × 64 × 0.05)=39`. Per-category C absolute correct >=25%: `12 × 64 × 0.25=192`.
- Budget plan: `12 × 3 = 36` arm-runs; `12 × 3 × 256 = 9216` updates; `12 × 3 × 256 × 2 = 18432` generation outputs.
- Sign test only concerns P_training_seed(D_s>0) conditional on **fixed 16 skeletons** and assumed independent stochastic streams; it cannot establish population-level OOD, loss-only effect, mean effect >=10pp or equal-FLOPs.

## QA and implementation boundary

- S3 checks 44 assertions about JSON/MD fields; 15 deliberately mutated JSON variants are caught. S4 reports `PASS_SCOPED_44_OF_44_AND_NEGATIVE_15_OF_15`. The reviewer inspected source and receipt but **did not execute** Node CLI; no claim of independent rerun.
- The QA function validates literal presence/cross-field assertions, not operational correctness, parser sensitivity/specificity, AST nonoverlap, custody security, rights, seed iid, AdamW resume, or Free T4 throughput.
- Prospective preexec must prove AST/checker/generator semantics with positive and negative fixtures, parser 64/64 legal positives and zero false accepts over >=64 adversarial negatives, all A/B gold uniqueness under a sealed custodian, ACL/signer/audit receipt validation, rights/PII/copyright, duplicate/leakage negative sampler, independent seed digests, nonzero-moment AdamW interrupted/resumed equivalence, corrupt checkpoint failure, and measured $0 T4 runtime/resources. No actual proof has been supplied.

## Single integrated V5 recommendation

Create one prospective **V5 prereg source-contract amendment** (not editing V1–V4) that simultaneously:

1. Defines canonical action verb IDs versus lexical aliases and updates the OOD fixtures, ensuring a genuine reachable causal witness is necessary and label-only shortcuts cannot count.
2. Specifies a hiding commitment for private EVAL_AST, the visibility/key/nonce and signature policy, unique immutable audit ID, one permitted batch, replay/no-retry behavior, and any failure as HOLD.
3. Freezes exact contrastive negative construction and ratios, coefficient, LR/schedule, RNG derivation/namespaces, B/C intervention accounting and fail-closed one-packet future implementation criteria.

This is **one integrated amendment and one subsequent independent design review**, not micro-permits or authorization for science. Do not use D1 outcomes to choose missing values.

## Preserved states and reviewer attestation

`D1_BRIDGE_SCIENCE=HOLD`; `D1_EXISTING=HOLD_UNMODIFIED`; `TEST_Q1Q2=SEALED`; `FC01_EXPLORATORY=CLOSED_PASS_SCOPED`; `FC02=NOT_OPENED`; `GPU=NO`; `TRAIN=NO`; `INFERENCE=NO`; `MAIN=UNCHANGED`; `V1/V2/V3/V4=IMMUTABLE`.

Reviewer used GitHub connector read-only. No private data, gold, test, Python science, GPU, training or inference. Local creation of this review report and machine receipt is **not** a mutation to the GitHub repository, a human signoff, or external independence proof.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_D1_BRIDGE_V5_SINGLE_PACKET_SEMANTIC_ALIAS_HIDING_AUDIT_COMMITMENT_CONTRAST_PARAMS_PREREG_SOURCE_AMENDMENT_NO_GPU`.
