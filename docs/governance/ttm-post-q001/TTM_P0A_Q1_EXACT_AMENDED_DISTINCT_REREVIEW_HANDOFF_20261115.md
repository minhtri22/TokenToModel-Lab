# HANDOFF — P0-A exact amended distinct Q1 source/design re-review

**Operation:** `TTM_P0A_MEASUREMENT_GOLD_INTEGRATED_REMEDIATION_EXACT_CANDIDATE_DISTINCT_REREVIEW_SINGLE_GATE`  
**Repo:** https://github.com/minhtri22/TokenToModel-Lab  
**Draft PR (same existing branch, not new research branch):** https://github.com/minhtri22/TokenToModel-Lab/pull/22  
**Original independent reviewed candidate:** `f3225f4f2cbc48ef15cdbc92cf5c050c78f4fa1a`.  
**Main reference:** `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7` · lineage Git blob `3409e036241deb1da6674619a2abc834bea8a2d6`.  
**New amended candidate HEAD:** MUST be resolved and pinned as complete 40-character SHA **from PR #22 after the single remediation commit**. An authored handoff cannot self-embed its own future commit SHA; verify a direct first-parent child of the frozen original candidate and record exact HEAD in reviewer deliverables.  
**Reviewer:** distinct from original P0-A candidate/remediation author; original reviewer may review again if organizationally independent.  
**Mode:** `READ_ONLY · SOURCE/DESIGN_ONLY · NO_SCIENCE`.

## 1. Why the exact re-review is needed

Owner reported independent `HOLD_Q1_SOURCE_DESIGN` on original candidate. Three HIGH blockers:
- `F-CONSTRUCT`: legitimate UNKNOWN when evidence genuinely insufficient versus an author-declared fact losing its required witness;
- `F-PARITY`: source stored packet != effective model-visible prefix after prompt rendering/tokenization/context truncation; rater might see witness model never saw;
- `F-DECISION`: too-wide assertion family and no deterministic minimum evidence supporting KEEP/SIMPLIFY/PIVOT/STOP/HOLD.

**Original reviewer Markdown/JSON remain at owner-local Windows paths; no raw reviewer report SHA-256 or original receipt SHA-256 independently fetched from GitHub in this remedial authoring round.** Original independent HOLD is *reported by owner*; do not treat author restatement as reviewer receipt. Reviewer can request the original files if byte-exact archive is needed. No claim of Q1 PASS or benchmark validated.

## 2. Read these exact paths at new amended HEAD

1. [P0-A revised question candidate](../ttm-post-q001/TTM_P0A_MEASUREMENT_GOLD_PROSPECTIVE_QUESTION_CANDIDATE_20261115.md) — original blob at old HEAD `fa45faadad78899cab3b48062c5befd3a141a53e`.
2. [P0-A revised machine-readable design contract](../../../artifacts/governance/ttm-post-q001/TTM_P0A_OWNER_SELECTION_AND_SOURCE_ONLY_DESIGN_CONTRACT_20261115.json) — original blob `3fd84c44e0aa56c6dfab55326bfe6addbb18f580`.
3. [One integrated construct/parity/decision remediation source contract](TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_SOURCE_CONTRACT_20261115.md).
4. [Author source-only QA receipt (85/85)](../../../artifacts/governance/ttm-post-q001/TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_AUTHOR_QA_RECEIPT_20261115.json) — **not independent review**.
5. [Owner priority selection unchanged](TTM_POST_Q001_P0A_OWNER_SELECTION_AND_PRIORITY_DEPENDENCY_LOCK_20261115.md).
6. [Original post-Q001 priority matrix](TTM_POST_Q001_RESEARCH_DIRECTION_PRIORITY_MATRIX_20261115.md), [machine matrix](../../../artifacts/governance/ttm-post-q001/TTM_POST_Q001_RESEARCH_DIRECTION_PRIORITY_MATRIX_20261115.json), original author QA remains frozen.

Normative baseline:
- [Question-First policy at exact main](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md)
- [Question Gate template](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/templates/TTM_RESEARCH_QUESTION_GATE.md)
- [Q3-reviewed Q001 admission version v2](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json)

## 3. Adversarial checks REQUIRED — one integrated review, no micro-permits

**Construct:** Verify `LOCATED_AT(entity_id,location_id,reference_time_id)` is a single, falsifiable atomic family; time and referents visible and unambiguous; out-of-scope relations excluded. Demonstrate that ITEM_ADMISSION_STATUS is separate from FACT_LABEL; `TRUE` requires positive visible evidence, `FALSE` explicit refutation or visible exclusivity axiom, `UNKNOWN_VALID` bounded complete evidence domain with neither entailment nor refutation; `INVALID` is a rejection, not a fact label. Challenge conflict, ambiguous referents and missing authorization. **Counterexample:** assigned TRUE but witness truncated must be REJECT, never UNKNOWN.

**Effective evidence parity:** Trace declared source → prompt builder/wrappers → exact tokenizer/context/truncation → effective model prefix, versus actual rater-visible evidence. An archived source witness alone is insufficient. Check planned receipt fields include effective prefix hash, witness token spans after truncation, rater packet hash, rights and absence of hidden gold. **Counterexample:** 256-token window drops W, rater still sees W ⇒ `HOLD_PARITY_LOST_AFTER_TRUNCATION` before fixture freeze. No demand to access private checkpoints for abstract source review.

**Decision tree:** KEEP only after lawful prospective item-level validation with independent gold/rater and frozen endpoints; SIMPLIFY only pre-outcome localized issue; PIVOT requires demonstrated scope infeasibility plus lawful equal-information alternate oracle and separate Question Gate; STOP requires proven permanent impossibility (not merely missing rights); HOLD default on missing evidence. Check five branches actually predict distinct outcomes, hard veto precedence and the difference between Q1 design readiness versus actual gold/benchmark validation.

**Negative contracts:** Independently reconstruct and try to falsify 12 authored symbolic scenarios rather than accepting 85/85 QA. In particular challenge: unknown vs missing witness; source-bounded completeness; false vs absent exclusive axiom; contradictory authorities; both directions of parity mismatch; AD-06 only if causal contrast; no Q1 registration/science authority.

**Governance regression:** Confirm original seven PR #22 docs/evidence files unmodified except two precise revised P0-A paths; exactly one new remediation contract + author QA receipt + this handoff; owner P0-A priority, data/objective tie, P0-B dependence and P4 reference-only unchanged. No `ACTIVE_RESEARCH_GATE.md` or `lineage.md` changes, no Q1 registration, no science, no PR merge, no new branch. Private `TEST64/FINAL24/FINAL72` sealed.

## 4. Review outputs (new files, no repo writes)

1. `TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_20261115.md`
2. `TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_RECEIPT_20261115.json`

Each must record exact reviewed new HEAD, original HEAD, full file SHA-1 plus raw SHA-256 verification status, reviewer independence, three finding dispositions, specific negative controls (not merely author QA repetition), source/path/line for defects, remaining NOT_VERIFIED rights/gold/threshold/custody, and **one** overall verdict:
- `PASS_Q1_DESIGN_SCOPE` only when source/design admission question now coherent, with separate `BENCHMARK_GOLD=NOT_VALIDATED`. This does **not** authorize Q1 registration, source access, production authoring, model science or merge.
- `HOLD_Q1_SOURCE_DESIGN` if any registration-blocking defect remains; one integrated remediation suggestion on the same PR #22, no fresh research branch.

**Next single step:** `TTM_P0A_MEASUREMENT_GOLD_INTEGRATED_REMEDIATION_EXACT_CANDIDATE_DISTINCT_REREVIEW_SINGLE_GATE`.

**Hard stop:** `NO_Q1_REGISTER · NO_SCIENCE · NO_DATA_GOLD_SCORER · NO_MODEL_RUN · NO_PR22_MERGE · NO_LINEAGE_EDIT · NO_MICRO_PERMITS`.
