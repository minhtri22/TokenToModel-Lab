# TTM-Small-4M D1 Bridge V6 R1/R3 — Custody, source review and 32-skeleton admission

**Operation:** `TTM_SMALL4M_D1_V6_R1R3_INTEGRATED_EVIDENCE_CUSTODY_AND_INDEPENDENT_32_SKELETON_SOURCE_QA_SINGLE_GO_HOLD`  
**Date:** 2026-11-14  
**Repo:** `minhtri22/TokenToModel-Lab`  
**Frozen science HEAD:** `dd52804685d186c17e600221ffb16ce78aea12ea`  
**Candidate source commit:** `b5dd5890b73a29744530ed3a1ffbc0dc7ae5195a`  
**Method:** read-only Windows RemoteMCP bytes/text + independent source-level structured comparison; same chat AI reviewer, **not an externally independent rater**. No GPU, training, inference, private gold or TEST Q1/Q2.

## 1. Evidence custody — byte-identical inputs

| Native artifact | Independently recomputed SHA-256 of UTF-8 bytes read from Windows | Git blob SHA-1 (staged) |
|---|---|---|
| `TTM_D1_BRIDGE_V6_R1_R3_PROSPECTIVE_CANDIDATE.json` | `e05774d9f0a155e19f70574260be839f1f0634bdfce2399ab2a67622dbc214a5` | `ed05456e5da0a9b162968a9c043f3628f143d8f8` |
| `TTM_D1_BRIDGE_V6_R1_R3_INTEGRATED_QA_RECEIPT.json` | `85f93961dba4b847da460ed61f4acb4f8b2d327867707dd4c5b58f51405c0dff` | `28e5afcca99a122b214ab1ec4882793889173ab2` |

The native receipt SHA-256 equals the value independently reported by owner PowerShell `Get-FileHash`. Candidate SHA-256 matches the expected digest inside that same receipt. RemoteMCP gateway-local `read_file` returned the original text in bounded line ranges; concatenated UTF-8 bytes plus terminating LF were independently SHA-256 hashed; both matched. Do not conflate public artifact custody with private gold/key custody.

## 2. Independent R1–R6 source reconciliation

| Criterion | Finding | Evidence |
|---|---|---|
| R1 AM01 | **HOLD** | `RETAIN` now `set_max`; `CARRY` now `forall_set` held-item locations; five other-than-WAIT actions explicitly guard `time=current_time`; WAIT specifies atomic advance and scheduled events; four synthetic complete CAT fixtures. **But 32 actual skeletons, unique oracle and independent reachable checker absent.** |
| R2 AM02 | PASS_SCOPED inherited | Candidate vs V6 deep structural JSON identical |
| R3 AM03 | **PASS_SOURCE_SCOPED** | Candidate seed array exactly equals all 12 V5 frozen seed values; final `20261201`, correcting V6 `20261131`; source-only, not RNG runtime |
| R4 AM04 | PASS_SCOPED inherited | Candidate vs V6 deep structural JSON identical |
| R5 AM05 | PASS_SCOPED_DESIGN inherited | Candidate vs V6 deep structural JSON identical; trusted-custodian protocol only, no production keys/security proof |
| R6 AM06 | PASS_SCOPED inherited | Candidate vs V6 deep structural JSON identical |

**Totals for candidate:** 5/6 scoped source passes, 1/6 R1 HOLD, 0 FAIL. This is **not** 5/6 scientific gates passed. A raw JSON string comparison falsely flags reordered keys after canonical serialization; independent recursive structural comparison found **zero changed fields** for R2/R4/R5/R6.

**Native QA (not rerun):** 13/13 synthetic positive, 12/12 synthetic negative, 128 finite transitions. These are inherited observed results, not independent full-world proofs.

## 3. Complete 32-position admission matrix

The frozen design requires all four categories, each with **4 TRAIN and 4 structurally OOD** skeletons, totaling **16 TRAIN + 16 OOD = 32**. Candidate source has `actual_4x4_skeletons = NOT_GENERATED`, `actual_reachable_checker = NOT_IMPLEMENTED_FOR_RESEARCH_DATASET_SYNTHETIC_QA_ONLY`, and `actual_AST_source = NOT_IMPLEMENTED`.

| Category | TRAIN expected / available | OOD expected / available | Admission |
|---|---:|---:|---|
| entity_location | 4 / 0 | 4 / 0 | NOT_EXECUTED |
| causal_reasoning | 4 / 0 | 4 / 0 | NOT_EXECUTED |
| rule_constraint | 4 / 0 | 4 / 0 | NOT_EXECUTED |
| goal_persistence | 4 / 0 | 4 / 0 | NOT_EXECUTED |
| **TOTAL** | **16 / 0** | **16 / 0** | **HOLD** |

All **32 individual required slots** are enumerated in the accompanying machine-readable JSON matrix. Each is marked `NOT_PROVIDED_NOT_EXECUTED`, **not FAIL**. This explicitly inspects the entire required admission surface while acknowledging that the actual 32 skeleton AST bytes and oracle witnesses cannot be inspected because they have not been produced. CAT01–CAT04 are only synthetic schematics and count **0** toward the 32. No EVAL gold, data, or TEST was created by this review.

**Each future actual skeleton requires:** complete typed initial A/B states and intervention; reachable unique canonical next-action oracle with `gold_A ≠ gold_B`; type-preserving relevant causal graph nonisomorphism (not aliases or inert changes); independently checked TRAIN/VAL/EVAL nonoverlap; immutable pins, rights and independent review. No `HOLD` category may be silently dropped or replaced by 3/4.

## 4. Design adjudication — one verdict

**`HOLD_REVISE_BEFORE_PREREG`.** R3 seed drift is source-corrected; R1 time/holder/protection source fixes are provisionally satisfactory under scoped synthetic coverage. Actual 32 typed skeletons, independent reachable/unique oracle and structural nonoverlap are unavailable. An AI check in the same conversation cannot substitute for a truly distinct independent reviewer.

**Preserved:** `D1_BRIDGE_SCIENCE=HOLD`, `D1_EXISTING=HOLD_UNMODIFIED`, `TEST_Q1Q2=SEALED`, `FC02=NOT_OPENED`, `GPU=0`, `TRAINING=0`, `INFERENCE=0`, `MAIN=UNCHANGED`, `lineage.md=UNCHANGED`.

## 5. Bước thực hiện tiếp theo — duy nhất

Continue the **same integrated R1 32-skeleton admission gate**, rather than reopening micro-permits: produce and pin four genuine TRAIN plus four OOD typed skeleton ASTs in each of four categories; independently validate reachability, oracle uniqueness, nonisomorphism, rights and sealed custody; then obtain one distinct source-only GO/HOLD review. No rerun of already unchanged 13/13 or 12/12 QA, no scientific execution until separately authorized.
