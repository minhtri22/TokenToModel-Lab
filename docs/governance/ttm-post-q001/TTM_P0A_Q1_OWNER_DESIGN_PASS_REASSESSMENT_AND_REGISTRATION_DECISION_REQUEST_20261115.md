# TTM P0-A — Owner reassessment of design PASS and Q1 registration GO/HOLD

**Operation:** `TTM_P0A_Q1_OWNER_DESIGN_PASS_REASSESSMENT_AND_REGISTRATION_DECISION_SINGLE_GATE`  
**Date:** 2026-11-15. **Repository:** [minhtri22/TokenToModel-Lab](https://github.com/minhtri22/TokenToModel-Lab).  
**Draft PR:** [#22](https://github.com/minhtri22/TokenToModel-Lab/pull/22) (not merged at the time of evidence reception).  
**Exact independently reviewed source/design HEAD:** `a8fd21f35d56a87f869df673b318d437ed0c8b31`.  
**Exact baseline `main`:** `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7`.  
**Original reviewed HOLD HEAD:** `f3225f4f2cbc48ef15cdbc92cf5c050c78f4fa1a`.  
**Decision owner:** `OWNER_GO_HOLD_NOT_YET_DECIDED`. The ChatGPT user transmitted the review results and uploaded the two exact artifacts, **not** an explicit `GO_REGISTER_Q1_SCOPED` declaration.

## 1. Exact independent-review evidence — archived verbatim

**Original user-uploaded review bytes were checked; these archive paths retain the same raw bytes.**

| File | Git blob SHA-1 of raw byte-exact content | Raw SHA-256 |
|---|---|---|
| [Independent reviewer Markdown](TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_20261115.md) | `38d009fa3cdc36db847565520307a8ff05d4c8c3` | `755efd1b49385a996ae03d2d264897576c91df3dbbe8d890046fb0765dea01a4` |
| [Independent reviewer JSON receipt](../../../artifacts/governance/ttm-post-q001/TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_RECEIPT_20261115.json) | `203c4b0f84536e96921edc42bd30717357201535` | `8a94ace8f0bc74d8c07944afbf1b2bd0099b792c7d7ea9776dafe40440fdf886` |

The reviewer JSON's `review_markdown_raw_sha256` matches the actual archived Markdown. The ten Git blob SHA-1 pins in its source manifest were read back on the **exact reviewed HEAD** and match 10/10 GitHub file blobs. The raw SHA-256 entries in the ten-file source manifest are **reviewer-attested**; this archive operation did not recompute each GitHub source file's SHA-256 independently. The original pre-remediation review report/receipt remain unarchived byte-exact on GitHub; do not retroactively claim otherwise.

**Independent verdict:** `PASS_Q1_DESIGN_SCOPE` on `a8fd21f35d56a87f869df673b318d437ed0c8b31`. All 3 original design blockers are reported `PASS_DESIGN_REMEDIATED`:
- `F-CONSTRUCT` — one `LOCATED_AT(entity_id,location_id,reference_time_id)` family, item admissibility distinct from `TRUE/FALSE/UNKNOWN`; `UNKNOWN_VALID` does not absorb missing witness or invalid item.
- `F-PARITY` — require evidence visible **after** model prompt generation/tokenization/truncation, and comparison against actual rater-visible facts, not only archive packet.
- `F-DECISION` — distinguish prospective `KEEP/SIMPLIFY/PIVOT/STOP/HOLD_EVIDENCE_INSUFFICIENT`; HOLD remains default while evidence is incomplete.

**Review depth:** 12/12 logical negative contracts N01–N12, plus reviewer-initiated X13–X16. Neither author 85/85 QA nor symbolic review is a real sample, rater or scorer run.

## 2. Reviewer residual checks — preserve as hard veto for future prospective admission

- **X13 (`BEFORE_FIXTURE_FREEZE`):** Witness W common to model and rater is **insufficient** if one view sees any *additional label-changing/refuting information*. Enforce parity on the **whole material fact set and information budget**, not just one positive witness span. Stop on mismatched decisive evidence.
- **X14 (`BEFORE_PRODUCTION_AUTHORING`):** Two distinct locations for an entity at one time are **not inherently contradictory** without a source-visible functional/exclusive-location axiom (or actually incompatible authoritative facts). Do not infer `FALSE`, conflict or closed-world negative by lexical difference alone.
- **X15 (`BEFORE_FIXTURE_FREEZE`):** If the model-effective prefix loses a required fact (truncation) while rater retains it, record **gate-level HOLD** `HOLD_PARITY_LOST_AFTER_TRUNCATION` and a deterministic **item-level REJECT_PARITY or REJECT_MISSING_WITNESS** with explicit precedence. Never emit `UNKNOWN` as a fallback. Runtime precedence remains `NOT_IMPLEMENTED`.
- **X16:** A source/design Q1 PASS **may** coexist with unresolved data rights, actual gold/rater calibration, checkpoint bytes, threshold and source feasibility. These do not become PASS just because the abstract question is coherent.

The above are **admission conditions** for any future authoring/fixture freeze, **not** actual implementation or test receipts. If the question-registration policy demands any item to be further specified before registering Q1, remain `HOLD_Q1_REGISTRATION` until it is written prospectively and independently read back; do not fabricate proof.

## 3. Owner decision matrix — one choice only

### `GO_REGISTER_Q1_SCOPED`

Approve **registration of exactly one P0-A MEASUREMENT Question Gate** under the [Question-First policy](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md) and [Question Gate template](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/templates/TTM_RESEARCH_QUESTION_GATE.md). Registration must be captured on `main` with assigned QuestionID, exact source/head/manifest, a falsifiable single question and discriminating minimum evidence, five decisions and hard-veto conditions, the phase-specific cost/budget/threshold/rights status, and X13–X15 at the correct time. `ACTIVE_RESEARCH_GATE.md` must be updated **with** the registration, under the relevant owner-approved governance PR and independent readback.

**GO_REGISTER_Q1_SCOPED authorizes only the Question Gate entry.** It does not approve merging PR #22 in its entirety, creating gold/dataset/scorer, accessing private sources, training or inference, GPU, modifying T4 architecture, opening F0–F2, or setting aside old sealed TEST/FINAL. If any mandatory Q1 registration field cannot be specified lawfully/prospectively, record `HOLD_Q1_REGISTRATION` instead of creating an incomplete Q1 on `main`. Q1 registration alone does not supply the later Q2/Q3/Q4 or `GO_SCOPED_IMPLEMENT`.

### `HOLD_Q1_REGISTRATION`

Do not register Q1; preserve the independently scoped `PASS_Q1_DESIGN_SCOPE` and archive evidence. Keep PR #22 Draft, `main` unchanged and all science rights denied. List what exact future Q1-registration fields or independent-human attestation are required and gather them in **one integrated governance packet**; no micro-permits.

## 4. Current gate statuses — no implicit elevation

| Gate / asset | Status |
|---|---|
| `P0-A_source/design` | `PASS_Q1_DESIGN_SCOPE` at exact reviewed `a8fd21f35d56a87f869df673b318d437ed0c8b31` |
| `reviewer_independence` | `AI_DISTINCT_SOURCE_REVIEW · HUMAN_ORGANIZATIONAL_INDEPENDENCE_NOT_EXTERNALLY_ATTESTED` |
| `original_prior_review_raw_sha256` | `NOT_VERIFIED_LOCAL_ONLY` |
| `benchmark_gold` | `NOT_VALIDATED` |
| `source_rights` | `NOT_VERIFIED` |
| `visible_source_feasibility` | `NOT_VERIFIED` |
| `item_level_witness/actual_effective_prefix` | `NOT_VERIFIED/NOT_CAPTURED` |
| `independent_same_task_rater` | `NOT_CALIBRATED` |
| `threshold/sample_size` | `NOT_FROZEN` |
| `checkpoint_custody` | `NOT_VERIFIED` |
| `Q1_registered_on_main` | `NO` |
| `owner_registration_decision` | `PENDING_GO_OR_HOLD` |
| `science/new_gold/new_scorer/model_run` | `NOT_AUTHORIZED` |
| `F0_F2` | `PAUSED` |
| `PR22_merge` | `NOT_AUTHORIZED` |
| `lineage.md` | `UNCHANGED; NOT_FOR_DESIGN_QA` |

**One owner decision next:** `GO_REGISTER_Q1_SCOPED` or `HOLD_Q1_REGISTRATION`, under `TTM_P0A_Q1_OWNER_DESIGN_PASS_REASSESSMENT_AND_REGISTRATION_DECISION_SINGLE_GATE`. No other execution.
