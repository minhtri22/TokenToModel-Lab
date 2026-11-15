# HANDOFF — Q001 independent Q3 one-shot readback/re-review of remediation

**Operation:** `SM4M_Q001_Q3_EXACT_AMENDED_CANDIDATE_DISTINCT_READBACK_AND_REREVIEW_SINGLE_GATE`  
**Repo:** `minhtri22/TokenToModel-Lab` · **Draft PR:** [#21](https://github.com/minhtri22/TokenToModel-Lab/pull/21)  
**Frozen original Q3 candidate:** `3c53d062c7c6ff4218d80177253dd1c061ac6362`  
**Frozen main baseline:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`  
**Amended candidate HEAD:** the exact commit on PR #21 after the single amendment push; **read and pin its full 40-character SHA before review**, and check that it descends directly from original Q3 HEAD. The implementation handoff cannot safely self-embed its own future commit SHA; owner message must supply and reviewer must verify it.  
**Independence:** reviewer not the Q2 author and not the Q3 remediation author.  
**Mode:** `READ_ONLY · EXACT_SOURCE_ONLY · NO_MODEL_RUN · NO_SCIENCE`.

## 1. Reason for re-review

Original independent Q3 [report](SM4M_Q001_Q3_DISTINCT_INDEPENDENT_REVIEW_20261115.md), SHA-256 `e619ea9460abd112ab32016e7644c273a6cce2d20044fe8bd0e129d18d820680`, verdict **`HOLD_Q3_REMEDIATION`**:
- `Q3-F01 HIGH`: AD-03 and AD-06 were late in the machine-readable `conditions_before_scoring` (first admission should be before production authoring/freeze).
- `Q3-F02 HIGH`: contradictory active Q2/Q3 status and multiple next steps.
- `Q3-F03 MEDIUM`: AD-01 over-bundled data rights, tokenizer and checkpoint custody.
- `Q3-F04 LOW`: Holtzman term should be “maximization-based decoding”.

**Owner accepted Q2 evidence scope, not Q3 PASS, gold/admission, science authorization or Q4 closure.** Q3 original has not been overwritten. The original JSON receipt is SHA-256 `529490652a7f140153292ec090496c1b5deec8ca36f54b25aa5b63c98cbd08ba` inside uploaded ZIP SHA-256 `816938d1d08479947c21206b6eeacc41da43c07abc29ac42dc31b0a844ae089d`. The ZIP is **not** byte-exact archived in GitHub; [derived intake metadata](../../../artifacts/governance/sm4m-q001/SM4M_Q001_Q3_EXTERNAL_REVIEW_INTAKE_VERIFICATION_20261115.json) is not the original receipt.

## 2. Immutable originals versus v2 amendments

**Read in full**:
1. [Original 7 Q2 input SHA table](SM4M_Q001_OWNER_SCOPED_Q2_ACCEPTANCE_20261115.md) — verify each source blob still exact at the amended HEAD.
2. [Original Q3 independent report](SM4M_Q001_Q3_DISTINCT_INDEPENDENT_REVIEW_20261115.md) and ask owner for original zipped receipt if independent receipt-byte reacquisition is required.
3. [One integrated amendment / design phase contract](SM4M_Q001_Q3_INTEGRATED_REMEDIATION_AND_PHASE_CONTRACT_20261115.md).
4. [Versioned machine-readable matrix v2](../../../artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json).
5. [Versioned literature correction v2](SM4M_Q001_Q2_LITERATURE_TRIAGE_Q3_REMEDIATION_V2_20261115.md).
6. [Canonical active research gate](../ACTIVE_RESEARCH_GATE.md).
7. [Author remediation QA receipt](../../../artifacts/governance/sm4m-q001/SM4M_Q001_Q3_INTEGRATED_REMEDIATION_AUTHOR_QA_RECEIPT_20261115.json) — **not independent**.

The old machine matrix `SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_20261115.json` and original literature remain immutable original-scoped **historical** evidence. The v2 files supersede only admission timing/terminology for Q3 rerun. This is **not** a re-execution of 10 studies, and Q2 author QA 38/64/59 cannot be treated as Q3 PASS.

## 3. Required adversarial checks

**F01:** Parse v2 JSON, assert `AD-03` and `AD-06` are present in `conditions_before_authoring` and `conditions_before_freeze`; the scoring phase includes only **rechecks**, not first admission. Find a negative fixture with hidden-gold-only or no one-variable pair and demonstrate it is refused *before authoring/freeze*. Confirm a separate exact programmatic oracle, if considered, would require preregistered contract and equal information budget. **Do not author an actual dataset**.

**F02:** Read full `ACTIVE_RESEARCH_GATE.md`: one current Q001 row, exactly one next step, no old `Q2_NOT_COMPLETED` or `Q3_NOT_REVIEWED`, no Q4 GO, and separate `main` actual HEAD from proposed PR state. Verify Q3 still HOLD pending re-review. Do not merge automatically.

**F03:** Check that `AD-01R` rights blocks unauthorized content access, `AD-01T` tokenizer/split identity blocks token-sensitive fixture freeze, `AD-01C` checkpoint byte custody blocks model execution but **not pure read-only design**. None should be misrepresented as PASS. Check that this is one AD-01 staged contract, not three new gates/micro-permits.

**F04:** Versioned literature P05 says “Maximization-based decoding”; original Q2 document is not silently rewritten. Scientific interpretation (decoder-only evidence weakened on D1 EXP32) unchanged.

**Regression checks:** 10 original study outcomes, 7 hypotheses and all AD-00…AD-08 original statuses preserved; no source/model/architecture/science, rater, gold, TEST/FINAL replay, branch proliferation, Q4, or `lineage.md` mutation. Original 7 Git blob SHA-1 identical. The original Q3 reviewer affirmations remain `KEEP_HISTORICAL_REFERENCE_ONLY`, `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`, and `ROOT_CAUSE_NOT_IDENTIFIED`.

## 4. Output contract

Produce **one** `SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_REVIEW_20261115.md` and **one** `SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_RECEIPT_20261115.json`, including:
- reviewed exact new HEAD, old HEAD, Git diff path list, reviewer independence declaration, SHA integrity 7/7 Q2 and changed/amended file hashes;
- F01..F04 status with supporting exact paths/lines and negative source-only contract checks;
- AD-00..AD-08 remain NOT ADMITTED / status preserved; caveats for AD-01R/T/C, AD-03, AD-06;
- one verdict `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED` or `HOLD_Q3_REMEDIATION`, scientific root cause identified `false`, execution flags `false`, and one next step.

A PASS approves **source/design admission-contract consistency only**, not actual admission or model inference. After PASS, owner Q4/merge decision is separate. A HOLD should give **one integrated remedy within PR #21**, not a new research branch.

## 5. Hard boundaries

`NO_CODE_PATCH · NO_NEW_RESEARCH_BRANCH · NO_MODEL_INFERENCE · NO_GPU · NO_TRAINING · NO_GOLD · NO_SCORER · NO_TEST_FINAL_REPLAY · NO_LINEAGE_CHANGE · NO_OWNER_Q4 · NO_MERGE`.

**Next single step:** `SM4M_Q001_Q3_EXACT_AMENDED_CANDIDATE_DISTINCT_READBACK_AND_REREVIEW_SINGLE_GATE`.
