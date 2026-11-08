# Mục lục tài liệu tiếng Việt của TokenToModel-Lab (TTM)

**Ngày rà soát:** 08/11/2026. **Nhánh nguồn:** `research/ttm-small-4m-colab-pilot-prereg-20261108`. **Phạm vi:** toàn bộ **55 tệp Markdown mô tả/hướng dẫn/biên bản** được kiểm kê trên `main` và PR #12; không sửa mã nguồn, hình ảnh, dữ liệu, tệp JSON/máy hoặc tệp khoa học `lineage.md`.

## Nguyên tắc đọc

- **Tiếng Việt trước, thuật ngữ tiếng Anh trong ngoặc đơn:** ví dụ *điểm lưu mô hình (Checkpoint)*, *bộ tách token (Tokenizer)*, *độ tương đương số học (Numerical Parity)*.
- **Giữ nguyên định danh máy:** tên tệp, trường JSON, đường dẫn, lệnh, mã trạng thái như `PASS_INDEPENDENT`, commit, SHA-256 và tên công cụ như `llama.cpp`. Chúng không phải câu diễn giải cần dịch.
- **Không chỉnh sửa bằng chứng lịch sử đã khóa:** 13 tài liệu cần Việt hóa sâu được lưu **bản tiếng Việt riêng** và liên kết với nguyên bản. Các dòng `NOT_EXECUTED` trong hồ sơ lịch sử **không phải trạng thái hiện hành**, tham khảo biên bản đóng T1–T3.
- **Không ghi đè lịch sử khoa học:** `lineage.md` giữ nguyên và chỉ ghi bổ sung (Append-only). Nhật ký máy, tệp JSON, code Python/PowerShell, checkpoint và ảnh SVG/PNG không được sửa chỉ để Việt hóa.

## Tình trạng tổng hợp

| Loại | Số lượng | Cách truy cập |
|---|---:|---|
| Tài liệu vốn có phần diễn giải chính bằng tiếng Việt | **42** | Đọc trực tiếp bản gốc (mã định danh kỹ thuật giữ nguyên) |
| Hồ sơ cũ cần bản diễn giải tiếng Việt riêng | **2** | `docs/vi/qa/`, `docs/vi/experiments/` |
| Hồ sơ pilot T1–T3/T4 có nội dung tiếng Anh hoặc thuật ngữ chưa đồng nhất | **11** | `docs/vi/pilot/` |
| **Tổng Markdown đã kiểm kê** | **55** | Mục lục bên dưới |
| Hồ sơ kỹ thuật/máy (JSON, log, Python, PS, ipynb, SVG/PNG) | Ngoài tập Markdown | Giữ nguyên vì mã và bằng chứng cần đối chiếu |

## A. Bản tiếng Việt riêng cho 13 hồ sơ

| Nội dung | Bản tiếng Việt | Hồ sơ nguyên bản |
|---|---|---|
| P00 — Phục hồi lỗi PowerShell tràn độ sâu gọi | [Đọc bản tiếng Việt](qa/P00_PS51_CALLDEPTH_RECOVERY_20261105.md) | [Nguồn](../qa/P00_PS51_CALLDEPTH_RECOVERY_20261105.md) |
| P00 — So sánh mốc kỹ thuật CPU | [Đọc bản tiếng Việt](experiments/P00_REFERENCE_BASELINE_20261105.md) | [Nguồn](../../experiments/comparisons/P00_REFERENCE_BASELINE_20261105.md) |
| T1/T2 — Nguồn, giấy phép, BPE và kiểm chứng GGUF | [Đọc bản tiếng Việt](pilot/TTM_SMALL4M_T1_T2_INTEGRATED_SOURCE_TOKENIZER_EXPORT_REVIEW_20261108.md) | [Nguồn](../pilot/TTM_SMALL4M_T1_T2_INTEGRATED_SOURCE_TOKENIZER_EXPORT_REVIEW_20261108.md) |
| T1 — Đóng kiểm toán độc lập, bàn giao T3 | [Đọc bản tiếng Việt](pilot/TTM_T1_INDEPENDENT_QA_CLOSURE_AND_T3_COLAB_HANDOFF_20261108.md) | [Nguồn](../pilot/TTM_T1_INDEPENDENT_QA_CLOSURE_AND_T3_COLAB_HANDOFF_20261108.md) |
| T1–T3 — Đóng kiểm thử kỹ thuật và các điều kiện khoa học T4 | [Đọc bản tiếng Việt](pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md) | [Nguồn](../pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md) |
| T1/T3 — Tiền kiểm nguồn và phục hồi Colab/Drive | [Đọc bản tiếng Việt](pilot/TTM_T1_T3_INTEGRATED_SOURCE_AND_RESUME_PREFLIGHT_20261108.md) | [Nguồn](../pilot/TTM_T1_T3_INTEGRATED_SOURCE_AND_RESUME_PREFLIGHT_20261108.md) |
| T2 — BPE GPT-2, F32 và bộ kiểm thử khóa | [Đọc bản tiếng Việt](pilot/TTM_T2_F32_GPT2_PRETOKENIZER_TRAINONLY_FROZEN_QA_AND_GATE_AMENDMENT_20261108.md) | [Nguồn](../pilot/TTM_T2_F32_GPT2_PRETOKENIZER_TRAINONLY_FROZEN_QA_AND_GATE_AMENDMENT_20261108.md) |
| T2 — Đóng kiểm thử native F32, điều chỉnh F16 | [Đọc bản tiếng Việt](pilot/TTM_T2_F32_NATIVE_CLOSURE_AND_F16_GATE_AMENDMENT_20261108.md) | [Nguồn](../pilot/TTM_T2_F32_NATIVE_CLOSURE_AND_F16_GATE_AMENDMENT_20261108.md) |
| T2 — Biên bản GGUF CPU tổng hợp | [Đọc bản tiếng Việt](pilot/TTM_T2_SYNTHETIC_GGUF_CPU_QA_RECEIPT_20261108.md) | [Nguồn](../pilot/TTM_T2_SYNTHETIC_GGUF_CPU_QA_RECEIPT_20261108.md) |
| T2 V4 — Phán quyết lỗi và phạm vi V5 | [Đọc bản tiếng Việt](pilot/TTM_T2_V4_ADJUDICATION_AND_V5_SCOPE_20261108.md) | [Nguồn](../pilot/TTM_T2_V4_ADJUDICATION_AND_V5_SCOPE_20261108.md) |
| T2 V5B — Phân xử tương đương F32, lỗi F16 | [Đọc bản tiếng Việt](pilot/TTM_T2_V5B_PARITY_ADJUDICATION_AND_F32_FIRST_ADAPTER_DECISION_20261108.md) | [Nguồn](../pilot/TTM_T2_V5B_PARITY_ADJUDICATION_AND_F32_FIRST_ADAPTER_DECISION_20261108.md) |
| T2 V5 — Lỗi biên dịch C1083 và phục hồi V5B | [Đọc bản tiếng Việt](pilot/TTM_T2_V5_CMAKE_C1083_AND_V5B_RECOVERY_20261108.md) | [Nguồn](../pilot/TTM_T2_V5_CMAKE_C1083_AND_V5B_RECOVERY_20261108.md) |
| T1–T7 — Tiền đăng ký thử nghiệm mô hình nhỏ | [Đọc bản tiếng Việt](pilot/TTM_TRAIN_FIRST_END_TO_END_PILOT_PREREG_DRAFT_20261108.md) | [Nguồn](../pilot/TTM_TRAIN_FIRST_END_TO_END_PILOT_PREREG_DRAFT_20261108.md) |

## B. 42 tài liệu đã trình bày chính bằng tiếng Việt

| Chủ đề | Tài liệu |
|---|---|
| Tổng quan dự án | [README.md](../../README.md) |
| Điều lệ dự án | [PROJECT_CHARTER.md](../../PROJECT_CHARTER.md) |
| Kiến trúc hệ thống | [docs/ARCHITECTURE.md](../ARCHITECTURE.md) |
| Đánh giá điều kiện thương mại hóa | [docs/COMMERCIAL_READINESS.md](../COMMERCIAL_READINESS.md) |
| Giao thức so sánh cấu hình | [docs/COMPARISON_PROTOCOL.md](../COMPARISON_PROTOCOL.md) |
| Quy trình quản trị và hợp nhất | [docs/GOVERNANCE.md](../GOVERNANCE.md) |
| Lộ trình P00–P12 | [docs/PHASE_PLAN.md](../PHASE_PLAN.md) |
| Quy chuẩn thuật ngữ tiếng Việt | [docs/TERMINOLOGY_VI.md](../TERMINOLOGY_VI.md) |
| Giao thức huấn luyện | [docs/TRAINING_PROTOCOL.md](../TRAINING_PROTOCOL.md) |
| Ranh giới workspace | [docs/WORKSPACE_BOUNDARY.md](../WORKSPACE_BOUNDARY.md) |
| Quyết định đổi ưu tiên sang huấn luyện trước (ADR-0001) | [docs/decisions/ADR-0001_TRAIN_FIRST_COLAB_AND_BRANCH_CLEANUP_20261108.md](../decisions/ADR-0001_TRAIN_FIRST_COLAB_AND_BRANCH_CLEANUP_20261108.md) |
| Quy trình thu gọn nhánh Git | [docs/decisions/TTM_BRANCH_CONSOLIDATION_RUNBOOK_20261108.md](../decisions/TTM_BRANCH_CONSOLIDATION_RUNBOOK_20261108.md) |
| Chú giải sơ đồ P00 | [docs/diagrams/README.md](../diagrams/README.md) |
| Thẩm định P01 và cổng P02 | [docs/p01/P01_F1_WP30_E0_FORMAL_ADJUDICATION_AND_P02_OPEN_GATE_20261107.md](../p01/P01_F1_WP30_E0_FORMAL_ADJUDICATION_AND_P02_OPEN_GATE_20261107.md) |
| P02 — Kiểm thử CPU độc lập | [docs/p02/P02_INDEPENDENT_QA_CPU_ORACLE_AND_WINDOWS_SINGLE_BATCH_20261107.md](../p02/P02_INDEPENDENT_QA_CPU_ORACLE_AND_WINDOWS_SINGLE_BATCH_20261107.md) |
| P02 — Mở lõi Transformer | [docs/p02/P02_TRANSFORMER_CORE_BPE2048_OPEN_AND_QA_PLAN_20261107.md](../p02/P02_TRANSFORMER_CORE_BPE2048_OPEN_AND_QA_PLAN_20261107.md) |
| P02 — Phán quyết QA trên Windows | [docs/p02/P02_WINDOWS_CPU_FORMAL_ADJUDICATION_AND_P03_GATE_20261107.md](../p02/P02_WINDOWS_CPU_FORMAL_ADJUDICATION_AND_P03_GATE_20261107.md) |
| P03 — Huấn luyện tổng hợp, học khớp tập nhỏ | [docs/p03/P03_TRAIN_LOOP_SYNTHETIC_OVERFIT_OPEN_AND_WINDOWS_QA_20261107.md](../p03/P03_TRAIN_LOOP_SYNTHETIC_OVERFIT_OPEN_AND_WINDOWS_QA_20261107.md) |
| P03 — Phán quyết chuyển P04 | [docs/p03/P03_WINDOWS_SYNTHETIC_FORMAL_ADJUDICATION_AND_P04_GATE_20261107.md](../p03/P03_WINDOWS_SYNTHETIC_FORMAL_ADJUDICATION_AND_P04_GATE_20261107.md) |
| P04 — Lưu checkpoint và đánh giá mô phỏng | [docs/p04/P04_CHECKPOINT_SAMPLING_SYNTHETIC_EVAL_OPEN_AND_QA_20261107.md](../p04/P04_CHECKPOINT_SAMPLING_SYNTHETIC_EVAL_OPEN_AND_QA_20261107.md) |
| P04 — Phán quyết QA trên Windows | [docs/p04/P04_WINDOWS_CPU_FORMAL_ADJUDICATION_AND_P05_GATE_20261107.md](../p04/P04_WINDOWS_CPU_FORMAL_ADJUDICATION_AND_P05_GATE_20261107.md) |
| P05 — Bộ nhớ đệm KV liên tục trên CPU | [docs/p05/P05_DENSE_KV_CPU_SOURCE_IMPORT_AND_QA_PLAN_20261107.md](../p05/P05_DENSE_KV_CPU_SOURCE_IMPORT_AND_QA_PLAN_20261107.md) |
| P05 — Phân xử lỗi báo sai và chuyển P06 | [docs/p05/P05_WINDOWS_CPU_V1_FALSE_NEGATIVE_ADJUDICATION_AND_P06_GATE_20261107.md](../p05/P05_WINDOWS_CPU_V1_FALSE_NEGATIVE_ADJUDICATION_AND_P06_GATE_20261107.md) |
| P06 — Bộ quản lý KV phân trang | [docs/p06/P06_PAGED_KV_IMPLEMENTATION_AND_OFFHOST_QA_20261107.md](../p06/P06_PAGED_KV_IMPLEMENTATION_AND_OFFHOST_QA_20261107.md) |
| P06 — Kế hoạch QA tích hợp | [docs/p06/P06_PAGED_KV_MANAGER_MINIMAL_INTEGRATED_QA_PLAN_20261107.md](../p06/P06_PAGED_KV_MANAGER_MINIMAL_INTEGRATED_QA_PLAN_20261107.md) |
| P06 — Phán quyết và cổng P07 | [docs/p06/P06_WINDOWS_CPU_FORMAL_ADJUDICATION_AND_P07_GATE_20261107.md](../p06/P06_WINDOWS_CPU_FORMAL_ADJUDICATION_AND_P07_GATE_20261107.md) |
| P00 — Đồng bộ và đóng mốc PR #2 | [docs/qa/P00_DOC_PR2_LOCAL_SYNC_AND_BASELINE_CLOSURE_20261105.md](../qa/P00_DOC_PR2_LOCAL_SYNC_AND_BASELINE_CLOSURE_20261105.md) |
| P00 — Kiểm tra tĩnh đồng bộ PR #2 | [docs/qa/P00_DOC_PR2_SYNC_AUDIT_STATIC_QA_20261105.md](../qa/P00_DOC_PR2_SYNC_AUDIT_STATIC_QA_20261105.md) |
| P00 — Rà soát độc lập tài liệu | [docs/qa/P00_DOCUMENTATION_INDEPENDENT_REVIEW_20261105.md](../qa/P00_DOCUMENTATION_INDEPENDENT_REVIEW_20261105.md) |
| P00 — Kiểm tra tĩnh tài liệu | [docs/qa/P00_DOCUMENTATION_STATIC_QA_20261105.md](../qa/P00_DOCUMENTATION_STATIC_QA_20261105.md) |
| P00 — Phán quyết QA chính thức | [docs/qa/P00_FORMAL_ADJUDICATION_20261105.md](../qa/P00_FORMAL_ADJUDICATION_20261105.md) |
| P00 — Chú giải hồ sơ lịch sử | [docs/qa/P00_HISTORICAL_RECORDS_VI.md](../qa/P00_HISTORICAL_RECORDS_VI.md) |
| P00 — Thẩm định đồng bộ tiến nhanh | [docs/qa/P00_LOCAL_FAST_FORWARD_ADJUDICATION_20261105.md](../qa/P00_LOCAL_FAST_FORWARD_ADJUDICATION_20261105.md) |
| P00 — Danh mục kiểm tra Git chỉ đọc | [docs/qa/P00_LOCAL_GIT_READONLY_CHECKLIST.md](../qa/P00_LOCAL_GIT_READONLY_CHECKLIST.md) |
| P00 — Kiểm toán sau hợp nhất | [docs/qa/P00_POST_MERGE_AUDIT_20261105.md](../qa/P00_POST_MERGE_AUDIT_20261105.md) |
| Phác thảo sách TTM | [book/OUTLINE.md](../../book/OUTLINE.md) |
| Nguồn gốc mã tham chiếu P00 | [reference/PROVENANCE.md](../../reference/PROVENANCE.md) |
| Hướng dẫn chạy mã tham chiếu P00 | [reference/phase0/README.md](../../reference/phase0/README.md) |
| Mẫu ghi kết quả vào lịch sử khoa học | [templates/LINEAGE_ENTRY.md](../../templates/LINEAGE_ENTRY.md) |
| Mẫu so sánh giai đoạn | [templates/PHASE_COMPARISON.md](../../templates/PHASE_COMPARISON.md) |
| Mẫu kiểm tra yêu cầu hợp nhất | [templates/PR_CHECKLIST.md](../../templates/PR_CHECKLIST.md) |
| Quản lý nhật ký thực nghiệm | [experiments/README.md](../../experiments/README.md) |

## C. Cách đọc kết luận kỹ thuật hiện tại

- **T1:** nguồn TinyStories gốc, chia tập 2.048 TRAIN / 256 VAL / 64 TEST và BPE 2.048 mã từ 768 truyện TRAIN đã qua kiểm toán độc lập trong phạm vi tập thử giới hạn (Bounded Pilot).
- **T2:** xuất GGUF F32 và đối chiếu `llama.cpp` đạt 20/20 mã token, 10/10 trường hợp logits; F16 vẫn bị chặn (Blocked) ở tuyến tùy chọn.
- **T3:** lưu và phục hồi checkpoint trên Colab Tesla T4 + Google Drive đã đạt kiểm tra độc lập 20 bước liên tục so với 10+10, trên dữ liệu tổng hợp. Lượt lỗi RNG ban đầu vẫn được giữ STOP.
- **T4:** chưa thực hiện khoa học; khóa khoa học `SCIENCE_LOCK=HOLD`. Phải khóa quyền dữ liệu, đối chứng NLL, ngân sách, năng lực GPU và bộ huấn luyện T4 trước khi xin phép đúng một lượt.
- [Biên bản quyết định mới nhất — tiếng Việt](pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md). Không tự suy ra mô hình đã được huấn luyện tốt hoặc sẵn sàng thương mại.

## D. Kiểm soát chất lượng bản dịch

- Mã SHA-256/commit, mã trạng thái và liên kết URL được đối chiếu giữa bản gốc và bản dịch cho cả 13 hồ sơ; **không thiếu chuỗi SHA/URL** trong các bản dịch.
- Liên kết giữa các tài liệu và đường dẫn từ mục lục dùng đường dẫn tương đối (Relative Paths); không đổi tên tệp nguyên bản.
- Ngôn ngữ chỉ là lớp trình bày; không đổi hợp đồng khoa học, tiêu chí PASS/FAIL, ngân sách hay số đo. Bản gốc tiếp tục là nguồn chứng cứ có thẩm quyền (Authoritative Source).
- **Giới hạn:** phần chính của 42 tài liệu trước đây đã là tiếng Việt, nhưng tên lệnh, mã thử nghiệm và một số nhãn kỹ thuật tiếng Anh vẫn giữ nguyên để nhận dạng và truy xuất đúng. Mục lục cùng [từ điển thuật ngữ](../TERMINOLOGY_VI.md) giải thích những nhãn này.

**Bước thực hiện tiếp theo:** hoàn thiện tiền đăng ký khoa học T4 trong **một lượt rà soát tích hợp**, thử nhanh năng lực GPU với dữ liệu tổng hợp và thẩm định độc lập; không chạy lại T1–T3.
