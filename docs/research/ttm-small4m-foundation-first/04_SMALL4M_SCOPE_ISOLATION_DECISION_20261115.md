# TTM-Small-4M — Scope Isolation & Portfolio Decision

**Operation:** TTM_SMALL4M_FOUNDATION_FIRST_COMPONENT_SPEC_AND_ROOT_CAUSE_RESEARCH_REBASE_SINGLE_GATE  
**Ngày:** 2026-11-15 · **Nguồn quyết định phạm vi:** yêu cầu owner trong hội thoại hiện tại.  
**Git baseline:** `main=fbe4a1ed58eef66f896bbfe0471926b7cc45298e` sau PR #19 global append-only lineage.  
**Decision status:** `OWNER_REQUESTED_SCOPE_REALIGNMENT_DOCUMENTED`; không phải khoa học GO, không phải reviewer độc lập PASS. **F3/F4 NOT_OPENED.**

## 1. Tuyên bố phạm vi bất biến

**Đối tượng duy nhất của chương trình nghiên cứu lõi là TTM-Small-4M**: checkpoint baseline T4 step1024 và các bài toán giải thích NLL vs factual/prompt adherence. Phương pháp bắt buộc: **Foundation First → Root-Cause Localization → Discriminating Measurement → One-Component Optimization → Formal Adjudication (SM4M-F0..F4)**.

Hai dòng nghiên cứu **EmbeddingGemma 2** và **Vector Memory** là các chương trình **độc lập**, không phải hai module/candidate mặc định của Small-4M, và không phải giải pháp được đưa tự động vào F0–F4. Không dùng PASS/FAIL, seeds, checkpoints, datasets, donor semantics, retrieval NLL hoặc reviewer của chúng để tính điều kiện GO/STOP cho Small-4M.

Nghiên cứu độc lập có thể cùng tồn tại trong global lineage, nhưng chỉ là đường dẫn lịch sử. Dẫn nguồn bên ngoài để giải thích khái niệm không phải evidence về Small-4M.

## 2. Scope routing matrix (không thay lịch sử)

| Nhóm / branch family | Chế độ điều phối trong đợt này | Quyền sử dụng kết quả đối với Small-4M |
|---|---|---|
| **SM4M-F0/F1 source và evidence hiện hữu** | **ACTIVE — DESIGN/READ ONLY** | Được xem là bằng chứng trực tiếp khi same checkpoint/task và study scope rõ |
| **T4 baseline và tokenizer/checkpoint frozen** | **REFERENCE — READ ONLY** | Được tham chiếu với pinned SHA; không re-run hoặc sửa |
| **Small-4M FRESH12/FRESH16, CF1, D1 EXP32, A/C, H-DATA, FC01** | **HISTORICAL EVIDENCE — NO NEW EXECUTION** | Được dùng để phân loại fail/hypothesis; không trộn metrics giữa protocol |
| **D1 Bridge R1** | **CLOSED_FORMULATION_DESIGN_HOLD** theo main L0022 | Chỉ giữ negative design evidence, không tự mở benchmark redesign |
| **MD1 FAIL4** | **EXISTING DESIGN REFERENCE ONLY** | M0 được chọn làm ứng viên F2, không cho phép sinh data, scoring, forward |
| **EmbeddingGemma 2 / Gemini embedding experiments** | **INDEPENDENT — COORDINATION PAUSE** | KHÔNG đưa donor, adapter, OOD256 vào core; giữ PASS scoped và A0E HOLD riêng |
| **Vector Memory V1–V4** | **INDEPENDENT — COORDINATION PAUSE** | KHÔNG đưa Reader, retriever, R8 hay private gold vào core; giữ V3 PASS exploratory, R7 FAIL, R8 HOLD riêng |
| **TTM-SIX / cross-model representation transfer, R3/O1 side directions** | **PAUSED — OUTSIDE FOUNDATION TASK** | Không tự mở science hoặc dùng kết quả để khẳng định hạn chế core |
| **MoE, attention variants, scaling P09/P10** | **NOT_OPENED / PAUSED** | Chỉ có thể thành tối ưu F3 tương lai khi localization chứng minh lý do; không tự mở phase |
| **T5/T6 serving, Ollama, P07/P08 GPU kernel** | **ENGINEERING CLOSED/PAUSED AS-IS** | QA kỹ thuật, không dùng làm science fact-conditioning; T6 scoped closed, P07 HOLD, P08 NOT_OPENED |

**PAUSE không tương đương FAIL, CLOSED hoặc DELETE.** Lưu chính xác các trạng thái khoa học của từng nhánh, không chuyển kết quả âm tính thành PASS hay ngược lại. Không chặn độc lập về mặt kỹ thuật cho các dự án ngoài yêu cầu Small-4M; quyết định này chỉ khoanh phạm vi ưu tiên và ngăn cross-contamination khi điều phối.

## 3. Nguồn sự thật và quy tắc merge/lineage

Nguồn đã hợp nhất:
- [main lineage.md tại fbe4a1](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/lineage.md), bao gồm Small-4M L0011–L0012, FRESH16 L0015, FC01 L0016, D1 R1 L0022, EmbeddingGemma 2 L0024, Vector Memory L0023, H-DATA L0025, FINAL24/H-DEC L0026 và global L0028.
- [Global lineage merge audit và 64-branch matrix](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/governance/TTM_GLOBAL_LINEAGE_MERGE_AUDIT_AND_RESEARCH_DIRECTION_MATRIX_20261114.md) có nhãn UNVERIFIED_CURRENT_GATE cho các nhánh chưa xác minh. Không coi toàn bộ 64 nhánh đã được chứng nhận.
- [D1 R1 independent HOLD closure](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/research/ttm-small4m-fact-conditioning/TTM_D1_R1_INDEPENDENT_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_REVIEW_20261114.md) ghi admitted OOD=0 trong bounded constructive search, không phải bất khả thi tuyệt đối.

**Chính sách:** GitHub là source of truth về documents/code/evidence đã commit, nhưng private checkpoint/data/escrow nằm ở custodian hợp lệ; GitHub public SHA chỉ là commitment, không được giả làm byte QA. `lineage.md` append-only, bảo toàn định danh và kết quả đã khóa; nhánh FAIL chỉ ghi kết quả và evidence, không cần merge code FAIL. Những nhánh có QA đủ điều kiện mới được reviewer/owner xem xét merge; gate này **không merge**. Bốn tài liệu mới nằm trên nhánh tài liệu riêng, không thay `main`, `lineage.md`, model, source, checkpoint hay data.

## 4. Không được làm trong gate Foundation First

1. Không thêm phase hoặc workflow research khác ngoài SM4M-F0..F4; F2 chỉ được thiết kế, F3/F4 chưa mở.
2. Không GPU/CPU science, inference, tokenizer re-fit, dataset regeneration, training, evaluation, unlock TEST/Q1Q2/OOD/FINAL hay rescore lịch sử.
3. Không thay tokenizer weights, attention/FFN, optimizer, checkpoint, architecture, seed, prereg thresholds hay đóng lại các one-shot đã consumed.
4. Không tạo PR merge, không viết lịch sử vào `main`, không cấp owner permit thay owner. Không tự sinh micro-permit hoặc dispatch external reviewer/gold data.
5. Không đưa EmbeddingGemma 2 hoặc Vector Memory vào root-cause matrix như nguyên nhân/giải pháp đã chứng minh; không tái sử dụng rater/scorer hay private data của hai nghiên cứu này.

## 5. Trạng thái, custody và next single gate

**Đã thực hiện trong scope:** đọc source exact-P02, T4 trainer và evidence adjudications; đối chiếu global lineage main mới; viết bốn tài liệu **author source-only** F0, F1, F2..F4 roadmap và scope isolation trên nhánh nghiên cứu tách biệt.

**Chưa thực hiện:** independent QA bốn tài liệu, private checkpoint/data byte readback, source audit toàn bộ nhánh UNVERIFIED, new science, owner permit, GitHub merge vào main. Không tuyên bố closed scientific gate.

**Owner design decision đề nghị:** `KEEP_SMALL4M_FOUNDATION_ACTIVE / PAUSE_DISTRACTING_WORKSTREAMS / F2_M0_DESIGN_ONLY / HOLD_ALL_NEW_SCIENCE`.

**Bước thực hiện tiếp theo — duy nhất:** distinct independent **READ-ONLY SOURCE/SCIENTIFIC DESIGN REVIEW** của **đúng bốn tài liệu cùng gate** và pinned evidence; trả một `GO_DESIGN_SCOPED` hoặc `HOLD_REVISE_DESIGN` cho owner. Không mở thêm nghiên cứu, benchmark, GPU hoặc một chuỗi permit.
