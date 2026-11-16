# HANDOFF — TTM-SM4M-DIAG-Q001: một lượt phân xử trước thực thi và quyết định owner

**Operation:** `TTM_SM4M_DIAG_Q001_SINGLE_DISTINCT_PREEXEC_REVIEW_AND_OWNER_GO_HOLD_ONEPACK`  
**Date:** 2026-11-16 · **Repository:** `minhtri22/TokenToModel-Lab` · **Base source main before registration:** `434a2592dc94a038d1dc33026eb5fb12b68c8af1` · **QuestionID:** `TTM-SM4M-DIAG-Q001`.  
**Q1 registration becomes effective on main only after governance PR merged/readback. Exact registration merge HEAD:** `READ_PROVIDER_POSTMERGE`.  
**Q1:** registration requested explicitly by owner for a **different ENGINEERING diagnostic**. **Q2/Q3:** one authored source-only packet, **not independently accepted**, **Q4:** owner execution choice **PENDING**, **I1/I2/I3/I4:** `NOT_EXECUTED`. This handoff is **not** a science permit.

## Context that cannot be lost
L0011 T4 actual trained step1024 VAL NLL PASS scoped, L0012 sealed TEST descriptive PASS consumed, L0015 FRESH16 V2 adherence scoped FAIL 0/16 and 0/8. We do not know cause. Exact P02 `9762343e06cf800b50574c2871ae1ed58537fb18`, actual model config 4 blocks ×256 emb, 4 heads, seq256, vocab2048, 3,749,376 parameters; checkpoint step1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` (45,074,891 bytes, private). P02 default 2-layer/64-dim is wrong for this checkpoint. GGUF backend is excluded from the direct diagnosis because numerical parity is not universal.

## Reviewer exact source/design QA — ONE packet

Read the [Q1 technical question and integrated design](TTM_SM4M_DIAG_Q001_REGISTERED_QUESTION_AND_ONEPACK_20261116.md), [machine-readable frozen protocol](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_FROZEN_ONEPACK_PREEXEC_CONTRACT_20261116.json), and [author QA receipt](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_AUTHOR_SOURCE_QA_RECEIPT_20261116.json) at the exact new governance HEAD; compare all source blobs to pinned original main. No input data or checkpoint retrieval without owner grant. Reviewer must be distinct from author, and must report one exact source verdict `PASS_DIAG_Q001_SINGLE_PREEXEC_SOURCE_SCOPED` or `HOLD_DIAG_Q001_PREEXEC` with actual gaps; not a science result or human/organization guarantee.

**Eight challenges (not micro-permits):**
1. **Distinctness:** The question is ability to perform abstract synthetic token-ID binding under frozen P02/fine-tune and one-step greedy, NOT re-registering `LOCATED_AT` ontology/gold, nor T5/GGUF strict parity.
2. **Checkpoint config:** P02 exact blob, T4 step1024 SHA and 3,749,376 params; `torch.load(weights_only=True)`, strict load, no hidden default seq64/emb64/layer2 or replay of sealed TEST/FINAL.
3. **Target shift:** last-token logits of exactly nine input token IDs predict the **tenth** answer; no target inside input, no loss over all prompt positions. Confirm model forward shape, gradient path and oracle/negative controls.
4. **Leakage/fairness:** all 24 train vs 56 nontrain fixture roles locked, 16 recombined, 16 novel-ID relative only to **probe TRAIN**, 16 *paired* counterfactual (not independent heldout), 8 heldout absent. No chosen easy samples; no gradients/early-stop from 56 probes, no evaluation tuning. Ensure reserved/tag/key/value IDs non-colliding and query first/second balanced.
5. **Probability and generation:** compare four-option candidate-restricted top-1 with **full-vocabulary** greedy top-1. A restricted-correct/greedy-wrong pair is logit competition, **not** proof of sampler/GGUF bug; single-answer-target avoids parser ambiguity. No posthoc candidate list.
6. **Predefined thresholds:** `TRAIN=24/24` full-vocab greedy and `mean answer CE <=0.10 nat` at **step256**, small heldout operational bands only, no multi-seed tuning, no false CI/real-language claim. Stops are hard at 256 steps, 900 CPU seconds, 12 GiB RSS, 1 GiB outputs; incomplete run is resource HOLD, not learning FAIL.
7. **Rights and execution custody:** Private T4 checkpoint rights `AD-01C/AD-00/E6=NOT_VERIFIED` and host executable/torch SHA NOT_PINNED; synthetic generation is only a protocol. Preexec independent audit of actual runner and fixture source must happen during **I1 before I2**, not falsely declared PASS now. Do not generate fixtures, train or inspect private data at Q2/Q3.
8. **Governance:** Q1 registered on `main` before any implementation branch; Q2/Q3 paper review independent; Q4 owner `GO_SCOPED_IMPLEMENT` or HOLD occurs **before** I1. Future I2 requires explicit conditional owner run permit, which can be the same one-packet decision but must STOP on failed I1 custody/QA. No scientific lineage update from paper.

## Exactly one later owner decision

If distinct Q2/Q3 source review is scoped PASS and practical checkout/rights are legitimately attestable, show owner **one binary choice**:

- `GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL` — owner Q4 may authorize exactly **one** I1 implementation branch (from then-current main) for a frozen diagnostic runner + negative QA and, **only after I1 independently passes and exact checkpoint rights/byte custody are verified**, one I2 CPU batch with no retries/seed changes or science branch expansion. If any precondition fails, `HOLD_RUN` without execution; do not auto-extend. This single conditional GO is distinct from the owner's present consent to register Q1.
- `HOLD_SMALL4M_DIAG_EXECUTION` — keep source-only plan, no code or runs; disclose which unavoidable evidence is missing (not a dozen new paper gates).

**If rights/checkpoint cannot be verified:** reviewer must say `HOLD_RUNTIME_ADMISSION` even if paper design is sound. Do NOT infer that lack of rights proves a model defect. If user chooses GO but condition is not met, execution is not authorized.

**Deliverable after actual authorized one-shot run:** a finite triage record showing earliest failing layer among `CUSTODY/ORACLE/GRADIENT/OPTIMIZATION/TINY_OVERFIT/TRANSFER/OUTPUT_COMPETITION`, all 80 case groups exact counts and receipt SHA; independent readback; decision whether to fix trainer, data/objective, decoder format, or seek an actual rights-valid semantic benchmark. A run producing only new governance QA without numeric observations is NOT a successful engineering result.

**No micro-permits:** One Q1–Q3 author design, one distinct review/Q4 owner decision, one guarded I1/I2/I3/I4 run+adjudication. P0A Q001 remains CLOSED_HOLD, P0B withdrawn, no access to old TEST/FINAL24.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_SM4M_DIAG_Q001_SINGLE_DISTINCT_PREEXEC_REVIEW_AND_OWNER_GO_HOLD_ONEPACK`.
