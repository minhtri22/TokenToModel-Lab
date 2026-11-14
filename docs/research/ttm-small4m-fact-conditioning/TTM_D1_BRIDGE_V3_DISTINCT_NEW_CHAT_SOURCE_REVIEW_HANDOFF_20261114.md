# HANDOFF — D1 Bridge V3 distinct independent source/preregistration review

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V3_DISTINCT_NEW_CHAT_PREREG_SOURCE_REVIEW_SINGLE_GO_HOLD_NO_GPU`  
**Date:** 2026-11-14  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Scientific source input (frozen HEAD):** `8f0714b29c98ca9be7c7444f964267faea4efb76`  
**Review role:** Independent AI Scientific Protocol Reviewer, new isolated chat (not human, independence self-attested unless explicitly verified).  
**Mode:** `READ_ONLY / DESIGN_ONLY / NO_GPU / NO_TRAIN / NO_INFERENCE / NO_PRIVATE_EVAL_GOLD / NO_TEST_Q1Q2`.

## 1. Mandatory read at frozen commit

Read all **7/7 documents** before a full verdict. Verify every Git blob SHA-1 returned by GitHub at exactly `8f0714b29c98ca9be7c7444f964267faea4efb76` (not dynamic branch HEAD).

| Source | Expected Git blob SHA-1 |
|---|---|
| [V3 MD](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_PREREG_DESIGN_AND_OWNER_HOLD_20261114.md) | `50556c367844e9f9c8aa3bf1a97e394fd74c37f1` |
| [V3 JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_D1V2_01_11_DESIGN_HOLD_20261114.json) | `927e7931ee044c70db4354db43330ae93f11331d` |
| [V3 QA JS](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/tools/pilot_t4/fc01/ttm_d1_bridge_v3_source_only_contract_qa_20261114.js) | `0d5ffa42e57344692e48ffcb2e134e921a9d8f95` |
| [V3 QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_SINGLE_PACKET_SOURCE_ONLY_QA_AND_OWNER_HOLD_20261114.json) | `d6dd1cd2c8e78677c81ba01b26851d933d5f82a5` |
| [V2 distinct review MD](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_DISTINCT_AI_SOURCE_REVIEW_20261114.md) | `3191c5427354b7239602fcb66b92202554084c30` |
| [V2 distinct review JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_DISTINCT_AI_REVIEW_RECEIPT_20261114.json) | `7b7074ad0166b43f20ca8e10d9bf8ac4e96001fd` |
| [lineage L0018](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/lineage.md) | `ddff96dbf8f52ab8f13ce169d9e264a1a05dd3bc` |

These are **Git blob SHA-1 hashes**, not SHA-256. V2 review originated from an independent new-chat AI:
- V2 review markdown SHA-256: `f482d9855b16bed2bc764e63c2d986259b8f94bd9bb1f65e30b145f5e5e23cae`
- V2 review receipt SHA-256: `52168ae7c523d1999388e9a2de211e10a940050b15b935a856c383c62c12c04f`

The owner checked original upload SHA-256 and verified exact original Git blob SHA after archiving. **Review at source metadata level** must not pretend to independently rehash raw bytes unless done.

V3 is **a source-contract proposal**, not an implemented/tested AST checker, parser or custody setup. V3 same-author assertions 57/57 and mutation negatives 13/13 do **not** establish scientific validity. Do not accept self-authored PASS as independent PASS.

## 2. Task: independent adversarial R1–R6 design review

Review each AM and all 11 D1V2 issue IDs; give `PASS/HOLD/FAIL`, issue ID, severity, exact frozen source pointer and must-fix. Deliberately search for new critical issues beyond the 11 previously listed.

**R1 / AM01 (D1V2-01/02):** Challenge reachable-state trace semantics, finite initial-state coverage, strong bisimulation, allowed alpha-renaming, observability of priority/temporal/causal events. Is an externally distinct trace automatically a meaningful task-structure OOD? Could the strong trace criterion create *false OOD novelty* from irrelevant internal event labels? Could an alpha-renamed case evade a naïve checker? If checker unavailable, `AST_REAL_CHECKER=NOT_IMPLEMENTED`, `NONOVERLAP=NOT_EXECUTED`.

**R2 / AM02 (D1V2-03/04):** Challenge whether narrow EBNF/parser grammar (agent+verb+target+optional qualifier) measures prompt-following versus mere formatted phrase completion. Examine natural paraphrases, false negatives, negation, quotes, multiple clauses, condition-witness inferred from prompt without oracle leaking into model inputs, unique gold A≠B, EOS/real T1 token budget 224+32. Require a specific deterministic grammar and independent synthetic fixture evaluation before any experimental data.

**R3 / AM03 (D1V2-05/06):** Verify signed integer `D_s = sum_f(success_C-success_B)`, `D_s=0` nonpositive and `k≥10/12` one-sided exact binomial sign-test p=79/4096 at k=10. Check what the *randomness population* actually is with a shared parent/corpus/test set and 12 labelled seed streams. Could seed effects be correlated despite domain separation? Evaluate conditional-on-fixed-skeleton hypothesis, sample power q=.7/.8/.9, magnitude guard +10pp **not inferential**, bootstrap crossed design descriptive only. Test tie & one missing seed as fail-closed.

**R4 / AM04 (D1V2-07):** Verify all integer gates `Σ_s D_s≥308`; category C−B ≥0 in 4/4, category Δcount≥39 in ≥3/4; C absolute≥192 in 4/4. Check precedence INVALID first, no category cherry-picking, 4 skeleton/category heterogeneity and lexical cue shortcuts. Would extreme contribution of one skeleton allow a misleading "uniform" label? Require explicit interpretation (descriptive safeguards not 4 tests).

**R5 / AM05 (D1V2-08/09):** Challenge whether the proposed isolated auditor can read **AST-only** exports from TRAIN/VAL and sealed EVAL without exposing gold, labels or answer-determining structure to trainer. Who controls keys/ACL, audit logs, signer identity and counterexample storage? Could AST projections themselves encode gold or reveal mapping? Is source-only overlap check possible without real data? Separate verified access from text role descriptions. No request to access private data.

**R6 / AM06 (D1V2-10/11):** Verify exact parent/T1 inherited source pins vs missing *new* runner/dataset/negative sampler SHA; RNG/negative exposure determinism; post-nonzero-AdamW interruption equivalence, optimizer moments and full state, fail-closed bad checkpoint; compute B/C same data and updates but C higher FLOPs; viability of **36 T4 Free arm-runs**, 9216 steps, 18432 generations, $0 paid budget and no resource measurement. Do **not** infer Free T4 feasible from earlier short FC01.

## 3. One single design verdict

Choose exactly one: `GO_DESIGN_ONLY`, `HOLD_REVISE_BEFORE_PREREG`, `FAIL_INVALID_DESIGN`, `HOLD_SOURCE_UNAVAILABLE`.

- `GO_DESIGN_ONLY` means the **specification** is suitable to advance to a separately authorized implementation + source QA gate, **NOT** science GO. Actual AST checker/parser, ACL and runner still NOT_EXECUTED.
- `HOLD_REVISE_BEFORE_PREREG` means a V4 amendment is required **before V3 is accepted**; avoid micro-permits.
- `FAIL_INVALID_DESIGN` means unresolvable foundational invalidity with redesign necessary.
- `HOLD_SOURCE_UNAVAILABLE` means files or expected Git blobs missing/unverifiable.

All verdicts **preserve** `D1_BRIDGE_SCIENCE=HOLD`, `D1_EXISTING=HOLD_UNMODIFIED`, `TEST_Q1Q2=SEALED`, `FC01_EXPLORATORY=CLOSED_PASS_SCOPED`, `FC02=NOT_OPENED`, `GPU=NO`, `TRAINING=NO`, `MAIN=UNCHANGED`. Do not change V1/V2/V3 or their recorded historical outcomes.

## 4. Reviewer deliverables

Return exactly two complete files:
1. `TTM_D1_BRIDGE_V3_DISTINCT_INDEPENDENT_PREREG_SOURCE_REVIEW_20261114.md` (source custody, six axis matrix, issue IDs, status, risk, must-fix, statistical checks, single verdict).
2. `TTM_D1_BRIDGE_V3_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json` (7 source pins, exact verdict, every axis, exceptions/limitations, rights/gold access flags, reviewer independence class, science HOLD and next operation).

If the agent has owner-authorized write access to a separate **review-only evidence branch**, it may commit those two files there without changing frozen source; otherwise return them as attachments for owner archiving. Don't invent SHA or claim bytes uploaded when not. Report a single **Bước thực hiện tiếp theo**.

**Start read-only review immediately**. No new owner approval is needed to review public pinned source. No training, inference, gold creation, new TEST accesses, or GPU are authorized.
