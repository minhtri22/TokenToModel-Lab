# TTM Vector Memory V3 — Owner AI-review substitution amendment

**Operation:** `TTM_VM_V3_P1_HUMAN_GATE_OR_PROSPECTIVE_AI_AMENDMENT_AND_PINNED_SCORER_OWNER_GO_HOLD`  
**Date:** 2026-11-12 (Asia/Bangkok)  
**Approval:** Owner explicitly authorized use of two ChatGPT AI raters instead of two human raters for this solo, internal exploratory study.  
**Classification:** `AI_ASSISTED_EXPLORATORY_SCOPED`.  
**Status:** `AMENDMENT_ACCEPTED_PROSPECTIVE_TO_V3_CPU_SCIENCE` — not a claim of the original human condition having passed.

## Authority, chronology, scope

This amendment was decided **after** the blinded AI A/B reviews and after the aggregate AI-vs-gold QA were visible, but **before** any V3 256-case Reader inference or retriever scoring. It is prospective **only to the forthcoming V3 science execution**, not preregistered before seeing the AI outputs. This departure from the original human-review requirement must remain visible in any published interpretation and is a potential source of selection/confirmation bias.

Replace the V3 P1 approval gate `TWO_DISTINCT_BLIND_HUMAN_ATTESTATIONS` with `TWO_DISTINCT_CHATGPT_AI_BLIND_REVIEWS_SHA_PINNED_AND_GOLD_CHECKED`. The old human gate remains `NOT_SATISFIED_0_OF_2`. No AI file may be renamed to `SIGNED`, and no human attestation field may be set to true.

## Exact review custody

| Source | Raw UTF-8 SHA-256 | Cases | Agreement with frozen private P1 gold |
|---|---|---:|---:|
| Agent A, `P1_REVIEW_A_AI_UNVERIFIED.json` | `46c9fad4b77065cf086213c64ee04145704efa8d6dd3cfbad56d80c9e1d68ed6` | 32 | 32/32 |
| Agent B, `P1_REVIEW_B_AI_UNVERIFIED.json` | `fd719ada13d2e44a72d29af04d18bb5d839547b288046ce410cfa9e5b7e49cdf` | 32 | 32/32 |

AI inter-rater agreement 32/32, reasons/keys/schema valid, `human attestation=false` both. The reviewer independence was **self-reported**; this is not human certification and does not cryptographically establish session separation. Public receipt `artifacts/research/vector-memory/TTM_VM_V3_P1_TWO_AI_BLIND_RATER_AGREEMENT_AND_GOLD_QA_20261112.json` documented 24/24 checks **before this amendment**.

Frozen private V3 fixture SHA-256 `d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543`. Source generator Git blob `5f51b8b464e54a370f3a3fa99d91307118f52f46`, V3 retriever Git blob `68bfeaaf1d0acf0cf446e4d734e34368fbf8f702`. No source, fixture, seed, Reader, optimizer, or thresholds are amended.

## Invariants and release gates

1. Keep the **same 256 PROBE**, 8 × 32 cards/cases, **96 primary positives** and **128 primary negatives**, P1 seen by two AI raters only as public index.
2. Keep all prespecified primary thresholds: positive correct select ≥72/96, P1 ≥20/32, negative correct abstain ≥122/128, NLL(A)−NLL(B1) and NLL(C1)−NLL(B1) ≥0.05, paired 95% bootstrap CI lower >0, Oracle(A−O1) ≥0.05, bootstrap 2,000 draws seeds 20261120/20261121; frozen L0020 Reader SHA `c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f`.
3. New reviewer custody must read **actual** GitHub-pinned AI JSON raw bytes, verify both SHA-256, distinct AI IDs, 32 unchanged public rows, no human claims, 32/32 consensus and private P1 gold match; do this before one-shot marker. Gold is never passed into retriever.
4. Independent source/mock scorer QA and native Windows source/fixture/Reader/backbone/T1 SHA preflight must PASS; source worktree clean and exact commit detached; no `-ExecuteOnce` by default; if once marker exists, no retry or cleanup.
5. No TEST, no GPU, no retraining, no rerun of V2 or earlier V3 scoring; `lineage.md` remains at L0022 until *actual* V3 science has been independently adjudicated.
6. Explain that V3 P1 proposed phrases are already in the V3 retriever source dictionary; passing does **not** demonstrate unconstrained unseen semantic generalization. Negative cases use action-only scoring and do not have Reader NLL.

## Owner release decision

**`GO_SCOPED_V3_CPU_ONESHOT_CONDITIONAL_ON_NATIVE_PREEXEC`** is an **authorization to attempt a single native Windows preflight and then one CPU inference** only after all pinned checks succeed. It is **not** a claim of native QA PASS or science execution. If any input SHA, AI custody or mock/native QA gate fails, the *effective execution decision* is `HOLD_FAIL_CLOSED`.

Owner must explicitly invoke `-ExecuteOnce` after reviewing the preflight. The research branch may receive this amendment and source/release artifacts; **main and append-only lineage remain unchanged**.