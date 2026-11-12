# HANDOFF — TTM VM V3 P1 Independent ChatGPT Blind Rater B

**Operation:** `TTM_VM_V3_P1_INDEPENDENT_CHATGPT_BLIND_SEMANTIC_REVIEW_EXPLORATORY`  
**Role:** independent AI blind evaluator, **NOT A HUMAN REVIEWER**.  
**Evidence class:** `EXPLORATORY_SCOPED_AI_REVIEW_NOT_HUMAN_ATTESTATION`.  
**Slot:** `B`. **Status:** `SCORING_NOT_STARTED`. **Scope:** 32 P1 cases × 32 public records.  
**Owner-pinned V3 fixture SHA256:** `d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543`.

## Only permitted input

Owner supplies `P1_REVIEW_B_TEMPLATE.json` **and this handoff only**. Read only each `question` and its `public_index` cards (`key`, `source_id`, `retrieval_text`). DO NOT access the other slot, full private V3 fixture, source/generator/retriever/rater validator, `answer`, `target_key`, `gold_action`, `truth_constraints`, prior reviews, GitHub source, web search, or connected files. Do not use background knowledge of source truth. Report `BLINDNESS_COMPROMISED` and stop if any excluded data has been exposed.

## Work

Judge **all 32 case rows independently**. Decide whether exactly one card is semantically supported by question and its public attributes/source. Select it if clear; otherwise abstain. Never force selection from position, ID format, guessed generator pattern or a hidden synonym table. On each row, modify **only**:
- `selected_key`: exact `public_index[].key` for that same case, or JSON `null` for ambiguity/insufficient grounds;
- `reason`: independent short explanation (at least 8 characters), or explanation of abstention;
- `confidence`: integer 0=undetermined, 1=low, 2=medium, 3=high.

Preserve all 32 case IDs, original ordering, question text, public index contents, slot, fixture SHA, and original template schema. No extra fields or altered case contents.

## Output

Return one **complete, valid JSON file** named `P1_REVIEW_B_AI_UNVERIFIED.json`, derived from the original template. Use `rater_id = "CHATGPT_AI_RATER_B"` (or another honest distinct AI ID), and actual `reviewed_at_iso8601` with timezone. Do not invent a timestamp. Existing schema name `ttm.vm.v3.p1.blinded_independent_human_review.v1` is a *template identifier*, not an assertion of human status. **Leave both** `attest_no_gold_or_other_review_access=false` and `attest_independent_semantic_mapping=false` in this AI-only artifact so the human attestation gate is never inadvertently passed. Independently describe your actual blindness and independence **outside** the JSON.

Never output `P1_REVIEW_B_SIGNED.json`, invoke human validator, claim `PASS_TWO_DISTINCT_BLIND_HUMAN_ATTESTATIONS`, infer private gold, or execute Reader/science/TEST/GPU. Deliver the JSON only to owner, not to other agent.

## Final checks and report

Confirm exactly 32 unique case IDs and 32 nonempty reasons ≥8 characters; each non-null selected key belongs to that case's index; each confidence is integer 0..3; template fields and public input are unchanged; no prohibited inputs were consulted. Report alongside file: `AI_RATER_SLOT=B`, `CASES_SCORED=32`, `SELECT_COUNT`, `ABSTAIN_COUNT`, `BLINDNESS=SELF_REPORTED_CLEAN` or `BLINDNESS_COMPROMISED`, `HUMAN_ATTESTATION=NOT_CLAIMED`, `SCIENCE_EXECUTION=NO`. Do not declare scientific PASS.

**Governance:** Two distinct ChatGPT agents are still **zero human reviewers** under the frozen preregistration. AI agreement on 32/32 cannot close `P1_HUMAN_REVIEW` or authorize CPU science. Replacing human review requires a prospective owner amendment and reclassification, never retrospective assertion. `TEST=SEALED`, `LINEAGE=L0022_UNCHANGED`, `READER=FROZEN`.
