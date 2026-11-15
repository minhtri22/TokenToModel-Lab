# TTM P0-A — Q2 Framework, Alternatives & Minimum Discriminating Evidence

**Operation:** `TTM_P0A_MEAS_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_SINGLE_GATE`  
**QuestionID:** `TTM-P0A-MEAS-Q001` · `MEASUREMENT` · **Date:** 2026-11-15.  
**Exact source `main`:** [f31754c21b4e26f7d7a15e53096090f2fa9b5d87](https://github.com/minhtri22/TokenToModel-Lab/commit/f31754c21b4e26f7d7a15e53096090f2fa9b5d87).  
**Status:** `Q2_AUTHOR_SOURCE_ONLY_PACKET_PREPARED · DISTINCT_Q2_QA_PENDING · OWNER_Q2_ACCEPTANCE_PENDING`.  
**No science:** no dataset, gold, scorer, rater packet, source access, model run, GPU or implementation branch.

## 1. Fixed inputs, source scope and problem

**Registered [Q1 Question Gate](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md)** Git blob `6b29c962b48c4134c925935409433d4ae2804110`. **[Active gate](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/ACTIVE_RESEARCH_GATE.md)** blob `288d4cd2c84315705e7ea06e45c246b6f3d67496`. **[Question-First policy](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md)** blob `af1a879a2552f100c6669cb9ab6dc98c930d2e19`. **[Independent Q1 source/design review](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/ttm-post-q001/TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_20261115.md)** blob `38d009fa3cdc36db847565520307a8ff05d4c8c3`, `PASS_Q1_DESIGN_SCOPE` at `a8fd21f35d56a87f869df673b318d437ed0c8b31`; reviewer human independence `NOT_EXTERNALLY_ATTESTED`. **[lineage.md](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/lineage.md)** Git blob `3409e036241deb1da6674619a2abc834bea8a2d6` — historical scientific results not rewritten.

**Scope** is exactly one atomic `LOCATED_AT(entity_id,location_id,reference_time_id)` assertion family. Truth labels `TRUE/FALSE/UNKNOWN` apply only to `ELIGIBLE` items, while `INVALID`, rights failure, ambiguous reference, missing witness, conflicting authority and missing model/rater parity are separate `REJECT` statuses. `UNKNOWN_VALID` requires a declared bounded, complete effective evidence domain and neither entailment nor refutation; missing record/truncation cannot be silently turned into UNKNOWN. False/contradictory location requires explicit visible negation or an explicit applicable functional/exclusive-location axiom. This is a **paper contract**, not a validated benchmark.

**Why this question:** historic T4 VAL/TEST NLL vs bigram PASS and FRESH16/FC01 scope negatives are distinct endpoints. They do not establish that H-DATA, H-OBJECTIVE, capacity or the rater caused failure. Measurement is prerequisite. This Q2 cannot rewrite Q001, reopen TEST/FINAL or recruit VM/EmbeddingGemma/Long-CoT as direct evidence.

## 2. Chosen frameworks and key limitations

- **5W1H:** WHO sees which source packet, WHAT is the typed fact, WHEN reference_time and truncation, WHY a label is justified, WHERE full material fact set is preserved, HOW independent adjudicator derives label. A diagram of access is **not** proof of actual byte parity.
- **Construct validity and falsification:** every mechanism has a falsifying observation; one observed outcome may be explained by several mechanisms, therefore no single-root-cause assertion.
- **Failure-mode / hard-veto review:** rights and information parity are noncompensatory; missing threshold cannot be offset by a high QA score.
- **Qualitative decision tree instead of MCDA/RPN:** no prospective data, weights, sample size or resource budget; any numerical ranking would be arbitrary. Do not use 5 Whys as a causal proof.

## 3. Five competing mechanisms — falsifiers and confounds

| Mechanism | Hypothesis / potential failure | Minimum future differentiating observation | Independent falsification challenge | Present evidence |
|---|---|---|---|---|
| `M0_VISIBLE_CONSTRUCT` | From the lawful bounded model-effective and rater-effective visible information, every eligible LOCATED_AT assertion has an operationally decidable TRUE/FALSE/UNKNOWN label and witness/proof of bounded source completeness. | A blinded adjudicator can reproduce a supported TRUE or FALSE, or justify UNKNOWN_VALID based on a bounded complete permitted domain, using no hidden E_core, with full material-fact parity of both views. | One purported ELIGIBLE item cannot justify a label from both effective views; rater-only defeating fact; or completeness cannot be established. | `DESIGN_CONTRACT_ONLY_NOT_EMPIRICALLY_VALIDATED` |
| `M1_HIDDEN_ONLY` | Gold is derived from E_core/answer key/hidden facts absent in one or both effective permitted views. | Prospective provenance trace from any prelabel/gold claim to exact model-effective and rater-visible spans, including post-tokenizer/post-truncation view and full material-fact set; compare with separately access-controlled oracle provenance without revealing hidden answer to rater. | All admitted gold claims have complete independently sufficient effective public witness on both views; no reliance on hidden-only metadata. | `UNVERIFIED_NOT_DEMONSTRATED_CAUSAL` |
| `M2_AMBIGUITY` | Assertion referent/time/location or source closure is not sufficiently defined for a unique operational label. | Predeclared single triple, explicit time and entity/location IDs, ontology authority and source completeness; independent derivation of mutually compatible truth outcomes. | A defined qualified domain yields unique reproducible label without hidden disambiguation; alternate locations alone do NOT imply exclusivity. | `ONTOLOGY_DESIGN_ONLY_NO_ITEM_VALIDATION` |
| `M3_SHORTCUT` | Lexical templates, order, length or style predict adjudication instead of the causal fact relation. | Separately permitted prospective group-disjoint, matched-information semantic contrast keeping nuisance cues fixed plus a cue-only negative control, with rubrics and thresholds frozen before data authoring. | Under predeclared changes of fact alone vs cue alone, measured decision reliably follows source-visible facts rather than cue position/format; label-change parity verified. | `NOT_TESTED_WITH_NEW_PROSPECTIVE_DATA` |
| `M4_RATER` | The adjudicator's rules/competence/position effects yield scores not determined by the same visible source facts. | Blinded independent qualified raters, exactly same task/visible evidence/rubric, calibrated on rights-cleared scope with explicit abstention, disagreement adjudication and format sensitivity checks. | Prospective independent raters agree under precommitted metric/threshold on admissible evidence, and source-based negative controls show no positional bias. | `NOT_CALIBRATED` |

**Mechanism overlap:** M0 is a validity prerequisite, not proof model works. M1 hidden gold and M2 ambiguity can coexist; M3 shortcut and M4 rater bias can coexist; source truncation can mimic M1. Do **not** force exclusive assignment, treat one symptom as cause, or infer a probability rank. Only a prospective owner-authorized, rights-cleared protocol could empirically separate them. This Q2 creates no fixtures, labels, calibration or new test sets.

## 4. Five alternatives — necessary evidence to change decision

| Alternative | Minimum differentiated evidence | Consequence if supported | Current status |
|---|---|---|---|
| `KEEP` | Only when a later owner-authorized prospective protocol verifies lawful source, eligible items, entire material-fact effective parity, independent item gold/rater, shortcut controls and frozen metric/threshold; no contradictory veto. | Retain the single LOCATED_AT relation and present rater protocol. | `NOT_JUSTIFIED_NO_ACTUAL_EVIDENCE` |
| `SIMPLIFY` | Before outcome exposure prove a LOCALIZABLE ontology failure and a narrower fixed subfamily retaining rights/source visibility/material parity and ability to falsify. | Restrict a prereg-declared subfamily (e.g. explicit time/referent), NOT rewrite gold after scoring. | `NOT_JUSTIFIED_NO_LOCALIZED_EVIDENCE` |
| `PIVOT` | Prove source/ontology of LOCATED_AT fundamentally infeasible and identify a SPECIFIC lawful alternate oracle/task with equal permitted information and independent validation. | Propose a NEW Question Gate only after original Q closure and owner decision. | `NOT_JUSTIFIED_NO_ALTERNATIVE_PROOF` |
| `STOP` | Document irreversible legal/construct/identifiability impossibility and absence of any feasible lawful alternative; lack of rights proof alone is not proof of impossibility. | Close this line without a falsified model verdict. | `NOT_JUSTIFIED_NO_PERMANENT_BARRIER_PROVEN` |
| `HOLD_EVIDENCE_INSUFFICIENT` | Any unmet hard veto or missing rights, item/witness proof, full parity, calibrated independent raters, threshold, checkpoint/runner consent, or independent review required at current phase. | Retain candidate and lineage; block source access, gold authoring, scoring and science until prospective conditions are admitted. | `CURRENT_DEFAULT_FOR_EMPIRICAL_ADMISSION_NOT_A_Q4_OWNER_DECISION` |

**Present recommendation:** `HOLD_EVIDENCE_INSUFFICIENT` for **any actual benchmark authoring, scoring, or science**; that is not a scientific failure and not a Q4 closure. A source/design Q2 comparison can be complete while runtime/rights/gold admissions remain HOLD. KEEP is not warranted now; STOP is not warranted without proof of irrevocable infeasibility; SIMPLIFY/PIVOT require their own distinguishing evidence. P0-B/P1/P2/P3/P4 remain unopened.

**Trade-offs:** KEEP protects comparability but incurs unverified rights/custody/calibration; SIMPLIFY is cheaper conceptually but narrows generalization and risks post-outcome selection; PIVOT may require a new lawful oracle and new Question Gate; STOP prevents unsound evaluation but needs strong evidence; HOLD preserves scientific integrity at the cost of deferred execution. No numeric cost or duration was sourced, and none is invented.

## 5. Minimum discriminating evidence — a specification, NOT production

| Evidence | Minimal required provenance / control | Can address | Current status |
|---|---|---|---|
| `E0_RIGHTS` | Document lawful access/use/transformation/third-party rater rights and PII handling before reading any source | ADMISSION_VETO | `NOT_VERIFIED` |
| `E1_CONSTRUCT` | Single atomic triple with explicit entity,location,time, visible ontology, domain completeness and allowed TRUE/FALSE/UNKNOWN vs REJECT; authorization/source proof | M0_VISIBLE_CONSTRUCT, M2_AMBIGUITY | `NOT_AUTHORED_OR_VERIFIED` |
| `E2_EFFECTIVE_VIEWS` | Exact source/builder/tokenizer/window and model-effective/rater-effective receipts with full label-changing fact set, not only common witness W; compare hidden oracle only under separate custody | M0_VISIBLE_CONSTRUCT, M1_HIDDEN_ONLY, M2_AMBIGUITY | `NOT_CAPTURED` |
| `E3_SHORTCUT_CONTRAST` | Preregged group-disjoint negative semantic contrast holding lexical/length/order nuisance fixed; separate cue-only perturbation if permitted | M3_SHORTCUT | `NOT_EXECUTED` |
| `E4_RATER_AGREEMENT` | Independent qualified same-task blind rater calibration, same permitted packet+rubric, explicit abstention and disagreement adjudication | M4_RATER, M2_AMBIGUITY | `NOT_EXECUTED` |
| `E5_PREREG` | Predeclare primary endpoint/denominator/threshold/STOP, source sample eligibility, cost/time/resources, reviewer and budget | ADMISSION_VETO | `NOT_FROZEN` |

**Minimality rule:** Start with lawful source/right status, grammar and source completeness, then a fully traced *model-effective vs rater-effective material fact set* and one prospective discriminating structure per hypothesis family **only after independent review/owner authorization**. Avoid additional arms or multi-Q experiments. Do not use previous FRESH16/FINAL24/TEST64 as “new” independent samples. The word “minimum” refers to the **types of evidence**, not an invented sample count.

**Evidence packets if later authorized:** source rights/custody and SHA; typed assertion with explicit time; evidence witness plus every material label-changing refutation/exclusivity; prompt builder/renderer/tokenizer/window/truncation policy and effective model-visible prefix hash/span; rater payload+rubric hash/spans, hidden gold exclusion; source completeness bound; negative controls and blind independent same-task adjudication. These are *required fields for future receipts*, NOT evidence presently produced.

## 6. Admission stages, rights and resource HOLD

| Stage | Hard conditions before transition | Today |
|---|---|---|
| `DESIGN_SOURCE_ONLY_Q2` | `registered_Q1_exact_main_and_policy`, `one_atomic_LOCATED_AT_grammar`, `M0_to_M4_falsifiers_and_overlap`, `five_alternatives_with_hard_veto`, `future_minimum_evidence_spec_and_unknown_costs` | `AUTHOR_DESIGN_REVIEW_DRAFT` |
| `BEFORE_SOURCE_ACCESS_OR_PRODUCTION_AUTHORING` | `AD-01R_rights_PII_copyright_and_third_party_rater_permission`, `AD-02_typed_reference_time_and_source_completeness`, `AD-03_source_visible_witness_feasibility`, `AD-05_shortcut_and_leakage_protocol`, `X14_visible_exclusivity_axiom_for_FALSE_or_conflict`, `AD-06_IF_PAIRED_CAUSAL_CONTRAST`, `owner_new_scope_authority` | `NOT_ADMITTED` |
| `BEFORE_FIXTURE_FREEZE` | `AD-01T_tokenizer_and_split_exact_if_sensitive`, `exact_builder_wrapper_tokenizer_context_truncation_pins`, `MODEL_EFFECTIVE_PREFIX_AND_RATER_EFFECTIVE_PAYLOAD_BYTES`, `X13_PARITY_OF_ALL_LABEL_CHANGING_MATERIAL_FACTS`, `X15_GATE_HOLD_AND_ITEM_REJECT_PRECEDENCE`, `source_complete_domain_proof_FOR_UNKNOWN`, `negative_pairs_AND_GROUP_SPLITS_IF_CAUSAL`, `AD-07_metric_sample_threshold_rater_roles_locked` | `NOT_ADMITTED` |
| `BEFORE_MODEL_EXECUTION` | `AD-00_exact_source_runner_pins`, `AD-01C_rights_and_checkpoint_byte_custody`, `owner_GO_SCOPED_IMPLEMENT_after_Q4`, `separate_owner_science_permission`, `budget_resource_authorization`, `sealed_TEST_FINAL_nonreplay` | `NOT_ADMITTED` |
| `BEFORE_SCORING` | `AD-04_same_task_independent_blind_gold_rater_calibration`, `verified_rater_visible_material_facts`, `AD-03_05_06_rechecks`, `prereg_metric_threshold_STOP_LOCK`, `no_hidden_gold_to_rater` | `NOT_ADMITTED` |

**Rights:** AD-01R missing: no evidence of permission to inspect, transform or pass candidate source/PII to third-party rater. Source access remains **NOT_AUTHORIZED**; a public GitHub document does not prove dataset rights. AD-01T exact tokenization/source splits unverified for future token-sensitive freeze. AD-01C checkpoint bytes/rights remain unverified before any model execution. **No private data access has been performed in this Q2.**

**Gold and AI-rater:** no actual item-level witness, independent human or same-task gold, rater packet/calibration, sample count, metric threshold, CI/power or consent to API use. `NOT_VALIDATED / NOT_CALIBRATED / NOT_FROZEN`, not FAIL and not 0 measured. Source feasibility for this restricted LOCATED_AT family is also **NOT_VERIFIED**. Approximate time/resources for potential future study cannot be grounded without a lawful source feasibility budget; `EXPECTED_COST=UNKNOWN`, `RESOURCE_CEILING=NOT_AUTHORIZED`.

**X13**: match **full label-changing material fact sets**, including any rater-only contradiction; one positive W shared in both views is insufficient. **X14**: do not assume distinct locations are contradictory without visible exclusivity. **X15**: when decisive witness drops out after truncation, issue **gate-level HOLD**, **item-level REJECT**, and preserve reason precedence (still unimplemented). **X16**: source/design PASS coexists with all actual admissions HOLD. Each condition retains its original prereg timing; Q2 author review cannot mark any dynamic gate PASS.

## 7. Adversarial source-only contract matrix (specification, not execution)

| ID | Logic challenge | Expected response |
|---|---|---|
| N01 | model-effective loses decisive witness after truncation while rater retains it | `GATE_HOLD_PARITY_LOST_AFTER_TRUNCATION_AND_ITEM_REJECT_PARITY` |
| N02 | model sees decisive W but rater not | `GATE_HOLD_EVIDENCE_PARITY_AND_ITEM_REJECT_PARITY` |
| N03 | prelabel TRUE/FALSE lacks decisive effective witness | `ITEM_REJECT_MISSING_WITNESS_NOT_UNKNOWN` |
| N04 | bounded source proven complete and well formed, no entailment or refutation | `UNKNOWN_VALID_ONLY_IF_ADMITTED` |
| N05 | explicit reference time missing or unresolved entity/location | `INVALID_ITEM_REJECT_SCHEMA` |
| N06 | two locations same time without visible exclusivity axiom | `DO_NOT_INFER_FALSE_OR_CONFLICT_BY_DEFAULT` |
| N07 | two authoritative facts conflict with visible incompatibility rule | `ITEM_REJECT_CONFLICTING_AUTHORITY` |
| N08 | causal pair changes both time and place | `HOLD_AD06_IF_CONTRAST` |
| N09 | rights unverified | `HOLD_RIGHTS_NO_SOURCE_ACCESS` |
| N10 | same task independent rater disagreement unresolved | `HOLD_RATER_COMPETENCE_NO_SCORING` |
| N11 | science requested at Q2 without Q4 owner GO/permit | `NO_MODEL_RUN` |
| N12 | oracle only hidden E_core | `HOLD_HIDDEN_ONLY_GOLD_NO_IMPUTATION` |
| X13 | rater has additional contradiction absent from model but both share positive W | `HOLD_FULL_MATERIAL_FACT_SET_PARITY_NOT_JUST_W` |
| X14 | no visible exclusivity between two locations | `NO_FALSE_NO_CONFLICT_UNLESS_OTHER_EXPLICIT_EVIDENCE` |
| X15 | post-truncation model missing W, rater retains W | `GATE_HOLD_AND_ITEM_REJECT_WITH_DETERMINISTIC_PRECEDENCE_PENDING_IMPLEMENTATION` |
| X16 | Q1 design PASS but rights/gold/rater threshold unresolved | `SOURCE_DESIGN_PASS_MAY_COEXIST_WITH_EMPIRICAL_HOLD` |

**Additional cross-case challenge:** when material parity fails *and* the item contains ontology ambiguity, preserve both reasons and select a prospective deterministic primary item reject code before fixture freeze. Likewise `UNKNOWN_VALID` is not a fail-closed fallback for absent source completeness proof. These are design requirements, not executed tests.

## 8. Q2 author disposition, independent acceptance and governance

**Author result:** `Q2_FRAMEWORK_AND_ALTERNATIVES_AUTHOR_REVIEW_COMPLETE_SOURCE_ONLY`. Q2 independent adjudication for this new registered question is **NOT_EXECUTED**; owner Q2 acceptance/closure is **NOT_DECIDED**. The earlier `PASS_Q1_DESIGN_SCOPE` certifies registration-ready question design only, **not Q2 answer or gold**. Q3/Q4 of `TTM-P0A-MEAS-Q001` still `NOT_EXECUTED/NOT_DECIDED`.

**HOLD gates:** source rights, source-visible feasibility, complete effective parity, independent rater, pre-registered metric/threshold, sample size, model/checkpoint byte custody and runner permissions. No science, gold, source item, code, training, inference, research branch or append to `lineage.md`. For governance `main` updates, first conduct distinct source-only Q2 review and obtain owner acceptance/merge decision; an author Draft PR alone is **not** a registered Q2 PASS.

**Evidence handoff:** [machine-readable Q2 matrix](../../../artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_MECHANISM_DISCRIMINATION_AND_ADMISSION_MATRIX_20261115.json). One integrated packet; do not create micro-permits.

## Bước thực hiện tiếp theo — duy nhất

`TTM_P0A_MEAS_Q2_EXACT_SOURCE_DISTINCT_REVIEW_AND_OWNER_ADMISSION_SINGLE_GATE`

A distinct reviewer must audit exact Q2 source HEAD, independently challenge M0–M4, the alternatives and rights/parity/veto timing; owner then decides accept Q2 design scope for progression or HOLD with one integrated remediation. **No automatic Q3, dataset, gold/scorer, model run, merge or science permission.**
