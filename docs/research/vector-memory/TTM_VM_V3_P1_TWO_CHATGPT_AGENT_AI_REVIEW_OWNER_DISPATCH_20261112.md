# OWNER DISPATCH — V3 P1 two independent ChatGPT AI blind reviews

**Operation:** `TTM_VM_V3_P1_INDEPENDENT_CHATGPT_BLIND_SEMANTIC_REVIEW_EXPLORATORY`  
**Status:** `AI_RATER_HANDOFFS_READY`; `P1_HUMAN_REVIEW=HOLD_0_OF_2`; `CPU_SCIENCE=HOLD`.

Owner Windows source QA=99/99 PASS, private fixture 256 SHA256 `d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543` native PASS, V3 science not executed. Two blinded templates exist under:

`D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory\TTM_VM_V3_P1_BLIND_HUMAN_REVIEWS_20261112`

## Separate dispatch

1. Start independent conversations with **two genuinely separate ChatGPT agent sessions**; do not give either agent GitHub/source access, full fixture, owner's private case-level gold, the other agent's messages or cross-chat memory of this evaluation.
2. **A gets only** `TTM_VM_V3_P1_CHATGPT_AGENT_A_BLIND_HANDOFF_20261112.md` + `P1_REVIEW_A_TEMPLATE.json`.
3. **B gets only** `TTM_VM_V3_P1_CHATGPT_AGENT_B_BLIND_HANDOFF_20261112.md` + `P1_REVIEW_B_TEMPLATE.json`.
4. Ask for full valid JSON files `P1_REVIEW_A_AI_UNVERIFIED.json` and `P1_REVIEW_B_AI_UNVERIFIED.json`. Verify 32 rows, selected keys within same case, reason≥8, confidence 0..3, no original fields altered, independence disclosure. Keep outputs separate and private. **Never rename them to HUMAN_SIGNED**.
5. The frozen human validator expects *two actual human reviews*. Since these are AI agents, retain `attest_no_gold_or_other_review_access=false` and `attest_independent_semantic_mapping=false` in their JSON outputs, disclose AI identity and assess them as **`EXPLORATORY_SCOPED_AI_REVIEW` only**. Do **not** run the human-validator as an authority to release science; its code does not cryptographically establish human identity.
6. If owner wants AI evidence to replace human evidence, require a prospective, explicit preregistration amendment and report the changed evaluation class before any science run. No automatic GO. Existing V3 `P1_HUMAN_REVIEW=HOLD`, `CPU_SCIENCE=HOLD`, `TEST=SEALED`, `LINEAGE=L0022_UNCHANGED`.

**No changes** to frozen generator, Retriever, Reader, dataset SHA, TEST, main, or lineage are authorized by this dispatch.
