# SM4M-Q001 — Hồ sơ trình owner Q4 (CHƯA PHÊ DUYỆT)

**Operation:** `SM4M_Q001_Q3_EVIDENCE_PUBLISH_AND_Q4_OWNER_DECISION_PREPARATION_SINGLE_GATE`  
**Repository:** [minhtri22/TokenToModel-Lab](https://github.com/minhtri22/TokenToModel-Lab) · **Draft PR:** [#21](https://github.com/minhtri22/TokenToModel-Lab/pull/21)  
**Question:** `SM4M-Q001` · **Policy:** `TTM-GOV-QF-20261115-V1`.  
**Source-of-truth main at intake:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`.  
**Independent Q3 reviewed EXACT HEAD:** `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`.  
**Owner Q4 status:** `PENDING_OWNER_GO_HOLD`; this document **does not record an owner decision**.  
**Reviewer authority:** read-only source/design; no science permission, no merge permission.

## 1. Chứng cứ independent Q3 — byte exact

The independent reviewer evaluated the immutable `c37ac0b3901eb6fd9c658d818c02e85f66b7936e` commit, not the later receipt-publication commit. These files are **published afterwards** in the same governance PR without changing the reviewed design/source files:

| Record | Git blob SHA-1 | Raw SHA-256 |
|---|---|---|
| [Independent Q3 Markdown](../sm4m-q001/SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_REVIEW_20261115.md) | `480662b2c88a8758e7a7cae22eec53c3d494a6ff` | `4496860eabb794658d6f1a7c3f84eec8c0f32b03d9814bd5ee5ec66992a173a0` |
| [Independent Q3 JSON receipt](../../../artifacts/governance/sm4m-q001/SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_RECEIPT_20261115.json) | `555c3b476402e49cd12e77523d47fb08fc13fe67` | `7809d6ffb6f803d953eaa368b70241c43bc6ccfbce91a0f463bf4e06023a3e6f` |

Original Q3 review was `HOLD_Q3_REMEDIATION` on `3c53d062c7c6ff4218d80177253dd1c061ac6362`; amended Q3 reviewer verdict on `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`: `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED`. No independent reviewer has audited the *future publication commit* as a new scientific candidate; it contains only appended review receipts, this pending decision request and active metadata. The exact reviewed source/design SHA and Git blob paths must stay unchanged.

## 2. Q3 scoped acceptance evidence

- Q3-F01…F04 `PASS_REMEDIATED_SOURCE_ONLY`; independent symbolic source contract checks `18/18 PASS`.
- Original seven Q2 docs Git blob SHA-1 and raw SHA-256 `7/7` accepted in scope.
- Ten study results, seven causal hypotheses, 13 literature source records and original AD-00…AD-08 statuses preserved.
- No data/model inference/training, unblind, TEST/FINAL replay, architecture change, source patch or scientific run.
- Original Q3 ZIP receipt remains **not archived byte-exact** on GitHub; this caveat concerns the *earlier HOLD review receipt*, not the new Q3 PASS receipt stored with exact SHA here.
- Independence declaration: a distinct analysis session; personal/organizational identity not independently authenticated.

**Scientific conclusions unchanged:**
`KEEP_HISTORICAL_REFERENCE_ONLY`; `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`; `ROOT_CAUSE_NOT_IDENTIFIED`. Q3 PASS **does not** turn an AD gate PASS, scientific result PASS, or authorize a new study.

## 3. Quyết định owner Q4 bắt buộc — chưa chọn

Owner must explicitly decide **BOTH**: (a) question closure disposition and (b) governance PR #21 merge disposition.

**Recommended (not authorized):**
- `Q4_CLOSED_HOLD_NEW_SCIENCE`: Q001 question answered *as far as current source/design evidence permits*: no confirmed architecture source bug; historical T4 retained; scientific root cause not identified; new science admission HOLD.
- `MERGE_APPROVED_GOVERNANCE_DOCS_ONLY`: merge only documentation, Q2/Q3 receipts, revised admission policy, and active status (no implementation/checkpoint/private data). Actual merge only after owner explicit approval and PR reread HEAD/base.
- Keep F0–F2 paused; do not launch new Question Gate, research branch, science run, new dataset/gold/scorer or architecture patch as part of this Q4.

**Alternative owner choice:** `Q4_HOLD_OPEN` and/or `HOLD_MERGE_REVIEW` with a recorded reason and missing evidence. No merge if HOLD.

**Independent Q3 PASS does not approve the merge; the owner must provide a GO/HOLD decision.** Publishing this document into PR #21 does not preselect GO or grant a permit.

## 4. Consequences if owner approves docs-only merge later

Verify exact current PR HEAD and `main` baseline again, consider required GitHub branch protection/reviews; merge the approved governance-only diff, verify readback new main and archive PR closure. The active register on main must reflect the **actual** owner Q4 decision (not this pending request); preserve immutable Q2 and Q3 source pins and `lineage.md`. Do not merge while Q4 remains pending.

**Single next step:** `SM4M_Q001_Q4_OWNER_CLOSURE_AND_PR21_GOVERNANCE_ONLY_MERGE_GO_HOLD_SINGLE_GATE` — explicit owner decision GO/HOLD; assistant shall not guess.
