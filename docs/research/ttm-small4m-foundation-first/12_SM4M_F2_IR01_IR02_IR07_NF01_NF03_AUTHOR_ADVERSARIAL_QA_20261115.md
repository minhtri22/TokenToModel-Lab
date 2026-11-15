# SM4M-F2 — Integrated Author Adversarial Source/Contract QA, IR01/IR02/IR07 + NF01–NF03

**Date:** 2026-11-15  
**Operation:** `TTM_SMALL4M_F2_IR01_IR02_IR07_AND_NF01_NF03_INTEGRATED_CONTRACT_REMEDIATION_SINGLE_GATE`  
**Role:** SAME-AUTHOR SOURCE QA, not independent scientific QA.  
**Prior independent exact candidate:** `cf0f459b54d0e91a7923e7a08b621d374e712e51`, verdict `HOLD_REVISE_DESIGN`; original `07adab...` HOLD remains unchanged. Four original findings (`IR03/IR04/IR05/IR06`) remain `CLOSED_DESIGN` scoped.  
**Remediated source Git blob pins:** 06 `6b924e6e12a9bdf1e43e59ed4fd5bfae20f1f632`; 07 `d83c713b1b9b94a9dff948e8a24d03aec82f5e70`; 11 strict JSON Schema `3540ef5904c303e72431e1bdbafe181f046b74fe`.

## 1. What changed substantively

| Finding | New prospective source-level contract | Still unverified at runtime |
|---|---|---|
| IR01 HIGH + NF02 HIGH | G04P **symbolic-only**, permitted in S0/S1 with abstract variables and per-stratum dependency matrix; G04E **actual eight rater-visible story variants plus 12 edges/core** only after explicit owner G12A in S2; evidence G04E independently QA before owner-conditional G12B release | Owner G12A, text and gold, actual G04E, G12B |
| IR02 HIGH + NF01 HIGH | Fully versioned rater-visible request must include source-bearing story prefix, exactly one candidate continuation, fixed actor/object/goal questions and canonical rubric. Independent gold raters **first view exactly the same evidence** as the blinded rater and cite visible UTF-8 source spans; hidden E_core cannot be exclusive fact source. Any insufficient visible evidence => HOLD_EVIDENCE_PARITY | Real natural-language semantic feasibility, item-level witness parity |
| IR07 MEDIUM + NF03 MEDIUM | Strict Draft2020-12 per-record machine schema with 10 record types, closed extra fields, exact ID/digest/score types, stage-dependent event requirements. Document 07 locks FK, graph counts, visible packet SHA, span offsets, canonical RFC8785 bytes, 16-rank total first-error priority and C01–C12 compound negative oracles | Reference meta-schema validation, implemented scorer, authorized full negative fixture execution, private integrity hashes |

**Preserved without reopening:** IR03 NC1–NC6 anti-shortcut; IR04 0/1/UNKNOWN with always-abstain failure; IR05 screening only with 16 M0X core clusters and eight UNKNOWN cases/axis; IR06 isolated rater and exposure HOLD. M0 MD1 32 cores/64 items and 28/32, 0.85 unchanged; no new labels/items have been created.

## 2. Self-QA done BEFORE handoff

**Stage A — typed schema synthetic tests: 42/42 PASS, 0 FAIL**. Generated **structural placeholder records only**, no narratives/items/gold. Tested ten strict record types; missing/extra keys, wrong type, invalid score strings/bool/UNKNOWN in binary, missing visible prefix, leakage of core/gold fields into rater request, conditional S2/S4 stage records, early S1 without future S4 receipts, graph 8-pattern/12-edge arithmetic. Author QA fixture generator initially produced duplicated IDs in its **synthetic sample**; fixed the generator and reran the entire batch. This was a test-harness issue, not proof that full schema is valid for every real artifact.

**Stage B — cross-source contract regression: 40/40 PASS, 0 FAIL**. Read exact source blobs 06/07/11; checked G04P vs G04E, G12A vs G12B, evidence parity, protection of MD1/F01–F05 and IR03–IR06, all thirteen G00–G12, N01–N28 and C01–C12 present; parsed exactly sixteen distinct ranked first-error codes; verified all 12 specified compound-error expected outcomes using symbolic priority logic. C11 accepts a valid early state event without future proof; other runtime permission failures remain HOLD.

**Total author-only checks: 82/82 PASS; independent QA on revised candidate: NOT_EXECUTED.** QA receipts:
- `artifacts/research/ttm-small4m-foundation-first/TTM_SMALL4M_F2_IR01_IR02_IR07_NF01_NF03_AUTHOR_SCHEMA_QA_RECEIPT_20261115.json`, blob `7b56b7f005059cdb3e2bbc2f02fafb466dc422ee`
- `artifacts/research/ttm-small4m-foundation-first/TTM_SMALL4M_F2_IR01_IR02_IR07_NF01_NF03_AUTHOR_INTEGRATED_QA_RECEIPT_20261115.json`, blob `399cb258731c0570bf6836908909ef1e788d7cbe`

**Detected and fixed during self QA:** (a) in typed stage-event schema, early S1 could not require G12B receipt that cannot yet exist; requirements are now conditional on transition stage; (b) gold-adjudication witness list requires a distinct actor/object/goal witness as normative cross-record check; (c) outdated N01–N27 shorthand was changed to N01–N28 + C01–C12; (d) explicit multi-fault error priority prevents conflicting rejection outcomes.

## 3. What this DOES NOT verify

1. No actual source/story texts, 8-pattern natural-language proof, independent gold, visible-span parity, rights, privacy or nonoverlap have been generated or reviewed. Source-only symbolic satisfiability **cannot** certify empirical semantic independence.
2. No actual nuisance classifier/model, provider/human rater, session isolation, score checker implementation, scorer negative fixtures or replay performed. JSON Schema was checked by **author lightweight structural validator**, not a separately certified reference Draft2020-12 interpreter.
3. No owner conditional data-authoring GO or score-release GO. New thresholds remain proposals. No Small-4M model inference, training, GPU or TEST/FINAL re-use.
4. The source-only QA and a machine-readable schema are necessary input to independent review, **not sufficient scientific evidence**.

## 4. Author gate outcome

`PASS_AUTHOR_SOURCE_AND_SYNTHETIC_CONTRACT_QA_82_OF_82_ONLY`.

Old independent `HOLD_REVISE_DESIGN` applies to the prior exact candidate and is not overwritten. No design-closure / science GO is issued here. All runtime admission E gates remain NOT_CREATED/NOT_VERIFIED, `PREEXEC_BLOCK=TRUE`, `F3/F4=NOT_OPENED`, `MERGE=NOT_AUTHORIZED`.

**Bước thực hiện tiếp theo — duy nhất:** distinct independent source/design review at the **exact new remediation commit** (reviewing both corrected 06/07 plus strict schema 11 and author QA) returns one `GO_DESIGN_SCOPED` / `HOLD_REVISE_DESIGN`. Do not rerun historical tests or start science.
