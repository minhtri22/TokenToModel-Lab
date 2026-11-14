# HANDOFF — D1 Bridge V5 / distinct independent source-only protocol review

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V5_DISTINCT_NEW_CHAT_INDEPENDENT_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU`  
**Ngày:** 2026-11-14  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Frozen scientific/source input HEAD:** `0b7205093e70cc6473244a23d2a20ead568452c1`  
**Vai trò:** Independent AI Scientific Protocol Reviewer, new chat (self-attested independence, not verified human).  
**Mode:** `READ_ONLY / DESIGN_ONLY / NO_GPU / NO_TRAIN / NO_INFERENCE / NO_PRIVATE_EVAL_GOLD / NO_TEST_Q1Q2`.

## 1. Nguồn bắt buộc — 8/8

Đọc nguyên bản 8/8 nguồn đúng **frozen HEAD**, đối chiếu Git blob SHA-1 ở cùng commit (không lấy dynamic branch HEAD). Không tuyên bố đã tái băm SHA-256 byte gốc nếu chỉ có metadata GitHub.

| Nguồn | Git blob SHA-1 kỳ vọng |
|---|---|
| [V5 design MD](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V5_SINGLE_PACKET_SEMANTIC_ALIAS_HIDING_AUDIT_COMMITMENT_CONTRAST_PARAMS_PREREG_DESIGN_HOLD_20261114.md) | `f72c0f8381f2a81364b2411630ae709f93d5c1a1` |
| [V5 contract JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V5_SINGLE_PACKET_SEMANTIC_ALIAS_HIDING_COMMITMENT_CONTRAST_PARAMS_SOURCE_CONTRACT_20261114.json) | `f4103f571ea80f909d59b1d9fe5f426702f53fa4` |
| [V5 QA JS](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/tools/pilot_t4/fc01/ttm_d1_bridge_v5_source_only_contract_qa_20261114.js) | `26a03f04d2ee744d368adf7aa8da6c3ed2f03683` |
| [V5 QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V5_SOURCE_ONLY_INTEGRATED_QA_AND_SINGLE_OWNER_HOLD_20261114.json) | `03426c516ca18553aed87db86906e1d614f49606` |
| [V4 independent reviewer MD](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_DISTINCT_INDEPENDENT_SOURCE_REVIEW_20261114.md) | `f1c8dc3e987b811f0d08d4784831bbf154bf1462` |
| [V4 independent reviewer JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json) | `dcad6a0cf8d684b0dcadfe0b99e2ae3aa78af09c` |
| [lineage.md L0020](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/lineage.md) | `7b2595cf0794e11a3393f543abf20e0bcbcb3804` |
| [FC01 original prereg parameter origin](https://github.com/minhtri22/TokenToModel-Lab/blob/0b7205093e70cc6473244a23d2a20ead568452c1/docs/research/ttm-small4m-fact-conditioning/TTM_SMALL4M_FC01_DATA_OBJECTIVE_CAPACITY_SINGLE_PREREG_DESIGN_20261112.md) | `af80eddfb2175b58a90c2a9761f0ed339e03678a` |

Nguồn thứ 8 là **FC01 prereg gốc** để kiểm tra giá trị `lambda=.2`, `tau=1`, `K=4`, AdamW, warmup, cosine, batch; không được chỉ tin V5 author. Reviewer V4 kết luận `HOLD_REVISE_BEFORE_PREREG`, R1/R5/R6 HOLD và R2/R3/R4 PASS trong phạm vi thiết kế. V4 raw review originals đã băm SHA-256 trên bytes upload trước khi commit: MD `8fd3ff6469403c9abb4cdc7672f9206c29329adf29388e8ca78fbb0df0eec47f`, JSON `2bdb82bb4e585c158c291c7b48838985249a7063a588af71b8e32f333dcedd94`.

## 2. Phản biện độc lập sáu trục R1–R6

Mỗi trục phải có `PASS/HOLD/FAIL` và severity `CRITICAL/HIGH/MEDIUM/LOW`, source pointer exact, lý do và must-fix. Không xem `SOURCE_ONLY_QA=45/45 + 15/15` do cùng tác giả là independent science QA; đây chỉ là checking fields/cross-reference và in-memory mutation, **không** có actual AST/parser/HMAC runtime.

**R1 / AM01 — Semantic alias vs action semantics (V4 HOLD):** Kiểm bộ 6 canonical verbs (RELOCATE/CARRY/TRANSFER/RETAIN/WAIT/ACTIVATE), typed state-transition signatures, exact lexical aliases và điều kiện `reachable policy+goal/time counterexample`. Kiểm các ca `move↔relocate` alias, `move↔carry` khác holder nếu reachable, `give↔hand over` alias, log-only inert trace, unreachable actions, đa nghĩa từ. Có đảm bảo action ontology bao phủ 4 nhóm nhiệm vụ mà không ép câu trả lời vào ontology quá hẹp? Khi hai action ids khác mà không có counterexample, không được ghi OOD PASS. Chỉ có spec, `ACTUAL_ONTOLOGY_CHECKER=NOT_EXECUTED`.

**R2 / AM02 — TIME/parser (V4 PASS scoped):** Xem việc nối alias nhiều từ `hand over`, `turn on`, TIME phrase nhiều từ và qualifier có làm grammar mơ hồ không; parser có tự lấy time/condition từ gold không? Distinguish `CANONICAL_ACTION_CONSTRAINED_GENERATION` from natural-language reasoning. Future 64 positive/64 negative synthetic independent QA chỉ là gate chưa thực thi.

**R3 / AM03 — Statistics (V4 PASS scoped):** Xác minh 12 seed nguyên 20261120…20261201, `D_s` signed integer over 256 paired families, `D_s>0` strict, `D_s=0` nonpositive, k≥10, p(k10)=79/4096. Kiểm seed PRNG derivation V5 có khác source randomness thực hay chỉ khác label, và seed-level iid chưa thể khẳng định. Phép test chỉ suy ra xác suất seed dương trên 16 fixed OOD skeletons, không mean ≥10pp inferential hoặc OOD universe.

**R4 / AM04 — Category gates (V4 PASS scoped):** Kiểm các ngưỡng nguyên `ΣD≥308`, Δcategory≥39 ở ≥3/4, C correct≥192 mỗi category và 4/4 không âm; cần disclosure per-skeleton, không hidden posthoc gates.

**R5 / AM05 — Hiding audit commitment (V4 CRITICAL HOLD):** Challenge HMAC-SHA256 32-byte secret under low-entropy EVAL AST, RFC8785 canonical bytes, 128-bit audit_id, audit key confidentiality, key reuse policy, domain separation, public signed receipt fields, Ed25519 public key pin, one batch/no retry. Is raw SHA of training/eval AST inadvertently public? Can receipt be replayed or compared across batch/queries? What if crash before signed UNKNOWN? Check trusted auditor/custodian privilege separation and private witness; **all real keys, ACL, rights and signing tests are NOT_EXECUTED**. Demand threat-model evidence and exact encoding fixtures before any implementation pass.

**R6 / AM06 — Frozen contrastive training package (V4 HOLD):** Independently crosscheck **against source #8** FC01 prereg: `λ=.2, τ=1, K=4`, AdamW lr1e-4, betas .9/.95, weight decay .1, clip1, warmup 16, cosine1e-5, batch16×256, core12+task4, 256 updates. Negative from opposite condition of **same TRAIN family only**, one negative/task positive, C gets extra info and compute; B/C episode bytes and primary LM token-slots matched but NOT negative exposure/FLOPs. Assess whether prior FC01 values are a justified prospective control for new structural-OOD tasks, not validation-tuned. Test RNG SHA256 namespace message exactness, sampler reproducibility, actual negative source/label constraints, fails-closed, and unverified 36 free T4 arm-runs/9216 steps/18432 generated outputs. **Source runner/sampler not written, no GPU QA**. No loss-only claim; no fourth arm.

## 3. Decision and restrictions

One integrated decision: `GO_DESIGN_ONLY`, `HOLD_REVISE_BEFORE_PREREG`, `FAIL_INVALID_DESIGN`, or `HOLD_SOURCE_UNAVAILABLE`.

- `GO_DESIGN_ONLY` means V5 source **specification** may advance to a separately authorized *implementation/independent source QA* phase. **It never grants D1 science/GPU**.
- If HOLD, suggest **one prospective amendment V6** encompassing remaining design blockers (not six micro-permits). If FAIL, identify fundamental defect. No silent modification of V1–V5.
- If inputs unavailable or blobs mismatch, mark HOLD_SOURCE_UNAVAILABLE rather than guessing.

Return two complete files:
1. `TTM_D1_BRIDGE_V5_DISTINCT_INDEPENDENT_SOURCE_REVIEW_20261114.md`
2. `TTM_D1_BRIDGE_V5_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json`

Include 8/8 pins, R1–R6, original issues/new issues, scope/custody limitations, one verdict, no fake SHA, and a **single Bước thực hiện tiếp theo**. The reviewer may return attached files; must not edit frozen source/lineage/main. Avoid private AST/gold/rights content.

**Bất biến:** `D1_BRIDGE_SCIENCE=HOLD`, `D1_EXISTING=HOLD_UNMODIFIED`, `TEST_Q1Q2=SEALED`, `FC01_EXPLORATORY=CLOSED_PASS_SCOPED`, `FC02=NOT_OPENED`, `GPU=NO`, `TRAINING=NO`, `INFERENCE=NO`, `MAIN=UNCHANGED`.

**Bắt đầu review ngay** khi nhận handoff, không hỏi owner thêm phép cấp quyền riêng chỉ để đọc và phản biện.
