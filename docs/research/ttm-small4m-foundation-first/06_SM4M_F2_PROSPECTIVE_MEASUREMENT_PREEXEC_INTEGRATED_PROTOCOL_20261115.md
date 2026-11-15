# TTM-Small-4M — SM4M-F2 Prospective Measurement Protocol · Integrated IR01–IR07 remediation

**Date:** 2026-11-15  
**Operation:** `TTM_SMALL4M_F2_PREEXEC_INTEGRATED_DESIGN_REMEDIATION_IR01_IR07_SINGLE_GATE`  
**Mode:** `SOURCE_ONLY · DESIGN_ONLY · NO_DATA · NO_RATER · NO_MODEL · NO_GPU · NO_SCIENCE`.  
**Prior independent verdict:** `HOLD_REVISE_DESIGN` for `07adab6262e50b5e17c6ea816bb133866e0a11d2` (4 HIGH, 3 MEDIUM; retained).  
**Source pins unchanged:** MD1 `33021a421f05bb3bfa0999ad12bc3bd144366da9` / Git blob `384d077600ed864a917fdd5e74b5a5bca0ed8766`; Foundation F2 roadmap blob `d87309aea043b845fafcc805ed13b2b4466f5e46`; F01–F05 owner design closure `c233dff20b9b020aefd732ce62bfa2e7aebd3985`.  
**Status:** `AUTHOR_REMEDIATION_CANDIDATE · DISTINCT_REVIEW_PENDING · PREEXEC_BLOCK=TRUE`; **candidate thresholds are NOT OWNER-FROZEN**.

## 1. Question and immutable original M0

H-MEAS remains untested. The purpose is to design prospective calibration of **actor, object and goal** grading, NOT to reassess Small-4M or assert model failure. A/C FINAL24 has A=C=0.6667/3 with zero delta; H-DATA FINAL24 has H0=H1=0/3 on 48 continuations (144 primary axis scores), a different protocol. Do not pool or rerun any previous scores/TEST.

`M0-ORIGINAL` as MD1: 32 new cores (4 strata×8), 64 continuations (32 gold `111` +32 `000`), 2 independent blind raters on the **same** 64 IDs. Each rater/axis: `TP+FN=32`, `TN+FP=32`; sensitivity≥`28/32`, specificity≥`28/32`, inter-rater agreement≥`0.85`. Proposed raw exact agreement `matches≥55/64` must be owner-frozen prospectively, not attributed to the MD1 text. M0 PASS can only certify **clear-polarity grading**, not independent per-axis validity.

`M0X-AXIS` and `M0U-UNKNOWN` below are prospective extensions *within* F2, not edits to MD1 or new science phases. No prompts, gold, judgments, item SHA, rights attestation or scorer exist from this design operation.

## 2. IR-01 HIGH: non-circular integrated authorization and release state machine

Only one **future** owner authorization is contemplated, with explicit conditional scope; the current owner F01–F05 design GO is NOT that permit. `GO_DESIGN_SCOPED` from an AI reviewer is never `GO_EXECUTION`. The future owner may give `GO_SCOPED_CONDITIONAL` (or HOLD/STOP), specifying private item authoring limits plus exact **conditional** pre-score release predicates in one decision. No owner decision currently grants this.

| Stage | Entry guard / verifier | Permitted after guard | Forbidden |
|---|---|---|---|
| `S0_DESIGN_DRAFT` (**current**) | Current exact source and seven IR findings | Edit documentation; static/adversarial author QA | Any data, rater, model |
| `S1_DESIGN_FROZEN_FOR_OWNER` | Distinct design QA; exact source, sample plan, rubric, thresholds, proxy catalogue, checker-interface, stop rules frozen by cryptographic pin for owner review | Submit one integrated owner GO/HOLD/STOP | No private items yet |
| `S2_PRIVATE_AUTHORING_ALLOWED` (NOT AUTHORIZED) | `G12A` owner conditional GO; `G01P` rights policy; `G03` MD1 untouched; `G06P` prespecified negative controls; `G07P` frozen thresholds; `G08P` blinding plan; `G09P` checker contract; named custodian | Author planned private items and provisional gold; execute ONLY preregistered, owner-scoped nuisance-only proxy QA and frozen checker implementation/synthetic negative QA to obtain G06E/G09E | No blinded rater scores, Small-4M model inference, GPU, training or unplanned proxies |
| `S3_PRE_SCORE_EVIDENCE` | Per-item rights `G01E`; nonoverlap `G02E`; independent gold/12-edge proof `G04E/G05E`; nuisance QA `G06E`; sealed packets `G08E`; independent frozen checker QA `G09E`; immutable manifests `G10E` | Custodian seals signed admission readback; separate independent reviewer checks | No self-release, no adaptive replacement |
| `S4_PRE_SCORE_RELEASED` (NOT AUTHORIZED) | Independent QA verifies every S3 receipt; immutable release event references **previously granted** owner conditional scope `G12B`. If initial owner GO lacked conditional scoring, a substantive owner decision is required, not an implied permit | Only then blinded M0→M0X→M0U scoring with prereg stop rules | No extra TEST/FINAL/model/scaling |
| `S5_TERMINAL_CLOSURE` | Score freeze, checker readback and owner final science adjudication | Archive PASS/FAIL/HOLD with provenance | No retrospective edits/re-runs |

**Dependency proof:** `G12A` does **not** require G02E/G04E/G05E/G06E/G10E, which logically require privately authored bytes; these come *after* S2, including only expressly authorized nuisance proxy checks and checker negative QA (not AI rater scoring or Small-4M model use). `G12B` requires them all but authorizes **scoring**, not authoring. The aggregate `PREEXEC_BLOCK` applies to scoring until S4; design QA alone never opens it. The checker cannot release itself and the author cannot verify their own gold. If any S2/S3 invariant fails → `HOLD_PRE_SCORE` with immutable negative receipt, no scoring. If one created core is invalid, **entire packet HOLD**; there is no reserve pool or replacement in this design. Any future reserve and finite replacement plan must be independently frozen before first item; never adapt after scores. One staged conditional decision avoids a series of micro-permits without skipping genuine future evidence.

## 3. IR-02 HIGH: per-axis semantic construct and exact 12-edge obligations

**Fact ledger schema per core:** fixed `E_core` identifies three bounded propositions and independent **witnesses**, not just a gold bit vector:
- `P_A`: actor identity/role for a *fixed* event.
- `P_O`: object identity/custody for a *separately fixed* fact.
- `P_G`: goal or progress evaluated using a *separate observable outcome/rule witness*; cannot merely restate actor or object.
- Each reference frame, event/time, entity and source witness is specified **before writing continuations**. If actor↔object or object↔goal semantic entailment cannot be separated, that core/stratum is **not feasible** for an orthogonal 2³ cube. Label `0` means an explicit contradictory claim against stable external facts, NOT omission; `UNKNOWN` means insufficient evidence, not false. Do not infer truth from inconsistent `E_core ∧ C` (classical explosion).

**Gold determination:** Two independent blinded gold adjudicators receive `E_core` and candidate continuation *without its intended bit vector*. Each provides actor/object/goal truth value plus exact evidence witness; discrepancies or coupling require `HOLD_SEMANTIC_COUPLING`, not a compromise after seeing scores. Human attestation must really be human; AI-only adjudication stays `EXPLORATORY_AI_GOLD`.

**All 8 patterns for each core:** `000,001,010,011,100,101,110,111`, all with unambiguous evidence. For every Hamming-distance-1 edge, adjudicator checks:
1. The changed axis flips gold truth; the **other two** remain equal.
2. Both unchanged axes retain **the same underlying reference and evidence witness**, not merely identical 0/1.
3. No newly created actor/object/goal dependency, time change, referent ambiguity or lexical leak has altered meaning.
4. All eight variants share the same stable `E_core` and are valid standalone texts.
Exactly **12 undirected edges/core = four actor, four object, four goal**. All 12 require source-grounded individual decisions. Independent reviewers must demonstrate `2³` feasibility for each planned stratum (`object_custody`, `social_relation`, `causal_obstacle`, `temporal_rule`) before owner authoring GO; **not** by assuming equal bit counts imply semantic independence. If a stratum cannot instantiate all eight valid conditions, `HOLD_REVISE_CONSTRUCT`, no stealth stratum substitution.

**M0X count proposal:** 16 independent cores (4 strata×4), eight items/core =128, 16 per pattern, 64 positive and 64 negative per axis, 64 matched edges per axis (4/core). Independent inference unit=**16 cores**, not 128 item rows. Invalid gold/edge detected pre-score ⇒ `HOLD_GOLD_QA` whole cohort; post-score ⇒ terminal `HOLD_INVALID_GOLD_AFTER_SCORE` without denominator edits.

## 4. IR-03 HIGH: all prespecified anti-shortcut controls mandatory

Prior wording “one or more weak proxies fail” is replaced by this **complete compulsory catalogue**, subject to exact version/feature/fit budget/source freeze before data authoring:

| ID | Control and information permitted | Acceptance/reject rule |
|---|---|---|
| `NC1_GLOBAL_VALENCE` | Always `000`, always `111`, and majority-bit global valence, evaluated on full 2³ pattern graph | These MUST fail M0X actor/object/goal and full-edge acceptance; if an obvious polarity shortcut passes ⇒ `HOLD_SHORTCUT` |
| `NC2_LENGTH_FORMAT` | Non-semantic char/token lengths, punctuation, casing, whitespace, paragraph structure, EOS/format | Core-heldout score under nuisance threshold |
| `NC3_STYLE_LEXICAL_CUES` | Preregistered hedges, negations, templates, role-name positions, stylistic marker combinations; **no fact ledger or gold bit** | Any cue representing a true semantic predicate requires construct review; no hidden exclusion |
| `NC4_METADATA_ORDER` | Rater-visible ordering, index, surface template, author/stratum markers; hidden labels/core IDs MUST NOT leak | Immediate `HOLD_LEAKAGE` if identifiers/label correlates are visible |
| `NC5_STRONG_NUISANCE_ENSEMBLE` | Preregistered combination NC2–NC4 with fixed classifier family, tuning budget and input schema | Every specified model/feature variant evaluated; do not report selectively |
| `NC6_GOLD_COUPLING` | Independent ground-truth source inspection of 8 patterns and **all 12 edges per core** | Any semantic coupling ⇒ `HOLD_GOLD_QA` |

**Evaluation split for learned NC2–NC5:** four predetermined folds, one *whole core from each stratum* held out per fold; all eight variants/core remain in same fold. Author/template IDs also disjoint when claiming those generalizations. If 16 cores lack independent author/template groups to implement an intended check, `HOLD_INADEQUATE_GROUP_DISJOINTNESS`, not an item-level leakage-prone split. Fixed feature vocabulary, proxy list, fit/tune budgets, fold mapping and random seed committed before authoring.

**Candidate nuisance failure ceiling (NOT frozen):** For **every** registered learned nuisance model and **every** axis, heldout balanced accuracy must be ≤`0.625` and no model may meet simultaneous M0X sensitivity, specificity and edge requirements. Any score >0.625, acceptance success, leakage or missing proxy receipt ⇒ `HOLD_SHORTCUT`; there is no “one proxy failed so QA PASS”. This is an exploratory risk screen under n=16 cores, **not a proof of no possible shortcut**. Reviewer must assess threshold operating characteristics before owner freezes it. All NC gates require actual independent post-authoring evidence before S4.

## 5. IR-04 HIGH: operational UNKNOWN, 3×3 scoring and always-abstain negative

**Normative epistemic rule for a fixed proposition P and source E:**
- Gold `1`: unambiguous evidence of P.
- Gold `0`: explicit evidence refuting P, including exclusive alternative justified by a predeclared rule. Mere lack of evidence is NOT 0.
- Gold `UNKNOWN`: neither P nor its explicit negation supported, but source coherent and referenced entities/time unambiguous; includes missing information or unresolved alternatives.
- `INVALID_SOURCE` (unscored and HOLD): contradictory evidence, unresolved referent/time, missing core facts/ambiguous question. Source invalid ≠ epistemic UNKNOWN. Missing rater answer ≠ epistemic UNKNOWN.
- Gold independently adjudicated with exact source spans; both non-target axes in M0U must be provably decidable.

**M0U proposal:** 24 new independent cores, 4 strata×6, one item/core, 8 target-UNKNOWN for each actor/object/goal (2 per stratum). For each target axis, all four combinations `00,01,10,11` of the **two decidable axes** appear twice over its eight target-UNKNOWN items. Thus for each measured axis: **8 gold UNKNOWN, 8 gold 1, 8 gold 0** across 24 items; two raters score all IDs in isolated contexts.

**Candidate gates PER RATER/PER AXIS (NOT frozen):** on 8 true UNKNOWN, predict UNKNOWN ≥`7/8` (false certainty≤1/8); on 16 decidable items, binary correct ≥`14/16`, erroneous UNKNOWN≤`1/16`, and with 8 true positive/8 true negative, sensitivity and specificity each ≥`7/8`. **Full 3×3 confusion** matrix rows gold {0,1,UNKNOWN} each sum8; columns predicted {0,1,UNKNOWN}; overall 24. Report target recall, false certainty, false-UNKNOWN, non-target accuracy, coverage and stratum/core. Rater that **always answers UNKNOWN** scores 8/8 targeted recall but 0/16 decidable binary correct and false-UNKNOWN16/16 ⇒ FAIL. No pooling into M0 or M0X.

## 6. IR-05 MEDIUM: thresholds, dependence and modest claims

Planned, **none created**: M0 32 cores/64 items; M0X 16/128; M0U 24/24; total **72 cores, 216 items**, two raters =432 item-rater assignments and **1296 axis decisions**, **not** 1296 independent cases.

**M0X candidate** unchanged: per rater/axis sensitivity≥`56/64`, specificity≥`56/64`, edge correctness≥`56/64` and two-rater exact agreement≥`109/128` on shared items. A **full-correct edge** requires both endpoints’ **entire three-axis vector** equal gold, not just target bit; no partial credit. Add per-stratum floor ≥`12/16` correct edges per axis, per rater, plus per-core and pattern table. Each edge shares endpoints and scores with other edges; statistical unit=16 story cores (4/stratum).

**Rationale:** The 87.5% rates mimic original M0 calibration difficulty as a *candidate screening target*, not statistically proven transfer. Two completely bad cores can still consume 8 of 64 edge errors while meeting global threshold; per-stratum floors and all-core gold feasibility expose concentrated failures but cannot make this confirmatory. For M0U, even a naive independent-binomial Wilson 95% interval for 7/8 spans about **0.529–0.978**, and 14/16 about **0.640–0.965**; true uncertainty across texts/cores may be greater. No power-confirmatory claim, no T4 natural-output generalization. Future descriptive score readback must report core/stratum-specific failures and core-cluster uncertainty with a preregistered algorithm; no item-iid bootstrap and no post-hoc tuning.

**Endpoint hierarchy:** pre-score gold/rights/anti-shortcut gates → M0 polarity → M0X per-axis/edge/stratum/proxy → M0U unknown/false-abstain. FAIL/HOLD stops all downstream in one frozen state machine. All NEW cutoffs (NC2–NC5 0.625, stratum12/16, M0X 56/64 and109/128, M0U 7/8,14/16,1/16) are only **candidate proposals**, requiring independent QA and owner freeze BEFORE any calibration item creation. This document does not freeze them.

## 7. IR-06 MEDIUM: isolated rater contexts and variant leakage

Each blinded item is evaluated **one at a time in a fresh isolated no-recall session**, with no full packet, no visibility of variants/core IDs/patterns/strata/gold or other scores. Custodian holds mapping and sends each rater exactly the **same underlying item set** under opaque IDs. Fixed concealed permutation interleaves cores and strata and prohibits adjacent same-core variants; no cross-session history or side-by-side access. For AI raters, independently verify disabled/shared memory/log retrieval and freeze provider/model/version/prompt settings. For humans, isolate display and disallow cross-item export; log independent identity and session. A second rater must not inherit first rater context.

If cross-session recollection, core-variant comparisons, leaked label metadata, or exposure compromise is detected or cannot be ruled out under the declared provider, `HOLD_RATER_EXPOSURE`; freeze negative evidence, no replacement rater based on observed scores. Agreement alone does not prove rater validity.

## 8. IR-07 MEDIUM: canonical checker semantics, negative QA and fail closed

The source-only checker schema, rejection order, 12-edge graph validation, 3×3 M0U report, stage gates, exhaustive negative fixture table and reason codes are specified in document 07. Implementation and any checker execution are **NOT AUTHORIZED in this gate**. Prospective validation order: `PARSE→SCHEMA→COUNT/ID→GOLD_GRAPH/EVIDENCE→RIGHTS/NONOVERLAP/NUISANCE→FREEZE→BLIND_SCORE→IMMUTABLE_SCORE→CUSTODIAN_UNBLIND→SCORER→ADJUDICATION`. Any violation yields deterministic `HOLD`/`FAIL` and an append-only negative receipt without dropping items/retuning. M0/M0X require exact integers 0/1; M0U permits 0/1 or exact `UNKNOWN`, never silently coercing null, missing, NaN, out-of-range or string score values.

## 9. Limits and next gate

The original independent F2 `HOLD_REVISE_DESIGN` persists at `07adab...`. This remediation is **author design only** until separate QA. Neither semantic witnesses nor 72 cores, 216 items, independent gold, licensed source, custody SHA or blinded scoring exist yet. Existing Foundation First F01–F05 owner `GO_DESIGN_SCOPED` remains scoped and unaffected; F3/F4 remain unopened.

`PREEXEC_BLOCK=TRUE · OWNER_DATA_AUTHORING_GO=FALSE · OWNER_SCORE_GO=FALSE · GOLD_NOT_AUTHORED · SOURCE_RIGHTS_NOT_ATTESTED · SCORER_NOT_IMPLEMENTED · NO_MODEL · NO_GPU · NO_TRAIN · NO_MERGE`.

**Bước thực hiện tiếp theo — duy nhất:** after one integrated author adversarial/self-QA gate, distinct independent source/design review of the exact amended candidate with one `GO_DESIGN_SCOPED` or `HOLD_REVISE_DESIGN`. No automatic owner execution permit.
