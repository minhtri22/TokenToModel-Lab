# TTM-P0A-MEAS-Q001 — Owner GO to register Question Gate on main

**Operation:** `TTM_P0A_Q1_OWNER_DESIGN_PASS_REASSESSMENT_AND_REGISTRATION_DECISION_SINGLE_GATE`.  
**Decision date:** 2026-11-15 · **Repository:** `minhtri22/TokenToModel-Lab`.  
**Owner's explicit declaration:** “Tôi quyết định GO_REGISTER_Q1_SCOPED cho TTM P0-A. Thực hiện một lượt đăng ký Question Gate trên main theo policy, giữ nguyên tất cả science/rights/gold/runner HOLD; kiểm tra điều kiện bắt buộc, không mở micro-permit và không tự cho phép merge implementation.”  
**Decision:** `GO_REGISTER_Q1_SCOPED` for **exactly one `MEASUREMENT` Question Gate**, ID `TTM-P0A-MEAS-Q001`.  
**Scope:** `Q1_REGISTRATION_GOVERNANCE_ONLY · NO_SCIENCE · NO_GOLD · NO_MODEL · NO_IMPLEMENTATION_MERGE`.  
**Pre-registration main:** `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7`. **Independently reviewed exact design:** `a8fd21f35d56a87f869df673b318d437ed0c8b31`. **Evidence archive PR #22 HEAD before decision commit:** `f128af5f6bbdcd6f7ab9c5e9c7026707d4df8552`.  

## 1. Basis for GO registration, NOT science GO

1. [Amended independent AI source/design report](TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_20261115.md), `PASS_Q1_DESIGN_SCOPE`, raw SHA-256 `755efd1b49385a996ae03d2d264897576c91df3dbbe8d890046fb0765dea01a4`; [receipt](../../../artifacts/governance/ttm-post-q001/TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_RECEIPT_20261115.json), raw SHA-256 `8a94ace8f0bc74d8c07944afbf1b2bd0099b792c7d7ea9776dafe40440fdf886`.
2. Reviewer confirmed original `F-CONSTRUCT`, `F-PARITY`, `F-DECISION` cured at source/design level; 12 symbolic negatives and X13–X16. Distinct ChatGPT review is **not** external human/organizational independence attestation.
3. Owner had already prioritized P0-A Measurement ahead of P0-B, data/objective P1, context/decoder P2, architecture P3; Long CoT/Mole-Syn remains P4 reference-only.
4. [Question-First policy](../TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md) requires Q1 question on `main` before research branch/data/model; owner now permits this single governance registration.
5. Complete [Question Gate Q1](TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md) supplies: one falsifiable `LOCATED_AT` question, new unique QuestionID, 5 decision alternatives and hard veto, OBSERVED/INFERRED/UNKNOWN, source HEAD/sha, prospective minimal evidence, staged AD gates, owner and independent reviewer, cost/threshold status, next single step.

## 2. Admission / HOLD still binding

| Component | Decision |
|---|---|
| `Q1_QUESTION_REGISTERED` | **GO** only after PR #22 governance-only merge and `main` readback |
| `Q2_FRAMEWORK/ALTERNATIVES` | `NOT_EXECUTED` for new Q |
| `Q3_ANSWER_REVIEW` | `NOT_EXECUTED` for new Q; old Q1 design review is prior eligibility evidence |
| `Q4_OWNER_CLOSURE` | `NOT_DECIDED` for new Q |
| `BENCHMARK/GOLD/SCORE/RUBRIC` | `NOT_VALIDATED · NOT_AUTHORIZED_TO_CREATE` |
| `DATA_RIGHTS/PII` | `NOT_VERIFIED · NO_PRIVATE_SOURCE_ACCESS` |
| `EFFECTIVE_MODEL_RATER_PARITY` | `NOT_CAPTURED`, X13/X15 hard veto before future fixture freeze |
| `EXCLUSIVITY/ONTOLOGY` | X14 hard veto before prospective authoring |
| `INDEPENDENT_RATER` | `NOT_CALIBRATED` |
| `METRIC/THRESHOLD/SAMPLE` | `NOT_FROZEN`, no science prereg |
| `CHECKPOINT/RUNNER/GPU` | `HOLD_NOT_VERIFIED · NOT_AUTHORIZED` |
| `F0–F2/P0-B/P1/P2/P3` | `PAUSED/NOT_OPENED` |
| `Long-CoT/Mole-Syn` | `REFERENCE_ONLY` |
| `ROOT_CAUSE` | `NOT_IDENTIFIED` |
| `LINEAGE` | `NO_ENTRY_FOR_Q1_DESIGN`; blob must be unchanged |
| `Implementation merge` | `NOT_AUTHORIZED` |

**Owner approval of this registration includes merging only the governance/document/evidence-only PR #22** as the vehicle to update `main`, after exact HEAD check, diff/rights scope QA, and GitHub readback. This does **not** authorize merging code, model/trainer, benchmark, dataset, test/fixture, checkpoint or implementation source. If a non-governance path appears, HOLD the merge and leave Q1 unregistered on main.

## 3. Provenance and registration readback

At authoring time GitHub Q1 registration commit SHA is unknown and **must be read from GitHub after merge**, never invented as a self-reference. Recheck PR #22 `merged=true`, `main` includes this decision, Question Gate file, machine receipt and revised `ACTIVE_RESEARCH_GATE.md`, with Git blob `lineage.md=3409e036241deb1da6674619a2abc834bea8a2d6`. Earlier request `TTM_P0A_Q1_OWNER_DESIGN_PASS_REASSESSMENT_AND_REGISTRATION_DECISION_REQUEST_20261115.md` remains a **historical pending-at-creation request**, not an up-to-date decision. This owner decision takes precedence.

**Current decision state upon valid main readback:** `GO_REGISTER_Q1_SCOPED · Q1_QUESTION_REGISTERED · NEW_SCIENCE_HOLD`.

## Bước thực hiện tiếp theo — duy nhất

`TTM_P0A_MEAS_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_SINGLE_GATE`

Design/source-only evaluation of M0–M4 and source-visible construct/rights/negative controls under the one already registered QuestionID. Do not open implementation, author data/gold or conduct model/rater experiments; no micro-permits.
