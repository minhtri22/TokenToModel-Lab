# R3 — GitHub Source of Truth (2026-11-11)

**Trạng thái:** `OWNER_SCOPED_ADJUDICATION=DESIGN_R3_BEFORE_O1` · `R3=DESIGN_ONLY` · `O0=PRESERVE_HOLD` · `O1=DEFER` · `GPU/TRAINING=NOT_EXECUTED`.

**Nguồn nhánh:** `research/ttm-r3-structural-state-tracing-design-20261111`, từ exact Codex review commit `dbf2c5389358e3989c1cb4a691bb981c32ecaf45`. Không tự động hợp nhất `main`.

## Hiện vật trực tiếp trên GitHub

- [Biên bản phân xử 7 phát hiện Codex và bảo toàn PASS/FAIL](../../../docs/research/TTM_R2A_CODEX_INDEPENDENT_INTERNAL_REVIEW_OWNER_ADJUDICATION_20261111.md).
- [Thiết kế R3: ngữ nghĩa quan hệ, ontology, counterfactual 4 ô, graph split, 6 đối chứng A–F](../../../docs/research/TTM_R3_STRUCTURAL_STATE_TRACING_PHILOSOPHY_FORMAL_SCIENCE_DESIGN_20261111.md).
- [Hợp đồng máy ứng viên R3](TTM_R3_STATE_TRACING_STRUCTURAL_GRAPH_DESIGN_CANDIDATE_20261111.json).
- [Biên nhận QA 20/20 phía tác giả](TTM_R3_OWNER_ADJUDICATION_AND_AUTHOR_DESIGN_QA_20261111.json).
- [Báo cáo phản biện Codex gốc, bất biến trong lịch sử nhánh](../../../docs/research/TTM_R2A_CODEX_SCOPED_ADVERSARIAL_REVIEW_20261110.md).
- [Codex QA receipt gốc](../codex-review-20261111/TTM_R2A_CODEX_ADVERSARIAL_QA_RECEIPT_20261111.json).
- [Mã adversarial QA của Codex](../../../tools/research/semantic_state_r2/r2a_codex_adversarial_qa_20261111.py).
- [Dữ liệu oracle R2A nguyên byte](../r2a/R2A_ORACLE_DATASET.json) và [384 model-input R2A nguyên byte](../r2a/R2A_MODEL_INPUT_ONLY.json) trong lịch sử nhánh.

**Chỉ kết quả R2A là dữ liệu đã thực thi.** Dataset R3 96×4 và validator R3 **chưa được tạo/chạy**; số này là ngân sách thiết kế. QA 20/20 kiểm nguồn và logic bản thiết kế, không đánh đồng với kiểm thử R3 runtime, neural, science.

**Phát hiện quan trọng:** 11 mutation Codex = **4 ACCEPT sai (bypass)** + **7 REJECT đúng**. Giữ `R2A_INPUT_SCHEMA=FAIL_SCOPED`. Không rewrite file hoặc receipt gốc để khiến lỗi biến mất.

**Bước thực hiện tiếp theo:** `TTM_R3_STRICT_INPUT_VALIDATOR_AND_STRUCTURAL_GRAPH_TOY_IMPLEMENTATION_SINGLE_CPU_QA`. Triển khai R3 parser/generator trên dữ liệu toy, chống lộ nhãn, đủ 4 ô, rồi chạy một lượt QA CPU; chỉ sau đó cân nhắc khoa học GPU bằng một quyết định owner, không từng micro-permit.

## R3 thực thi CPU — đã hoàn tất 2026-11-11

**[Mở toàn bộ mã, dữ liệu toy 384 bản ghi, checker, 70 test và kết quả SHA trực tiếp trên GitHub](runtime/README.md).** Đây là kết quả kế nhiệm của thiết kế bên dưới, không ghi đè tài liệu design.

- `R3_RUNTIME_CPU=PASS_SCOPED_70/70` · `NEGATIVE_VALIDATION=PASS_42/42`
- `R3_ORACLE_FULL=GITHUB_COMMITTED` · `R3_MODEL_INPUT_ONLY_FULL=GITHUB_COMMITTED`
- `SHALLOW_DIRECT_64/384` · `VISIBLE_TEXT_ORACLE_384/384` · `NEURAL=NOT_TESTED`
- `O0=HOLD_PRESERVE` · `O1=DEFER` · `R2A_VALIDATOR_FAIL=HISTORICALLY_PRESERVED`
- [Biên bản CPU và phán quyết](../../../docs/research/TTM_R3_STRICT_INPUT_GRAPH_TOY_INTEGRATED_CPU_QA_AND_OWNER_ADJUDICATION_20261111.md)
