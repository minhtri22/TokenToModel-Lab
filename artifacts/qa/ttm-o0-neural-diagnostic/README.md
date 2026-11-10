# TTM O0-only — New Diagnostic Neural Feasibility (DESIGN ONLY, 2026-11-11)

**GitHub Source of Truth:** branch `research/ttm-o0-only-neural-feasibility-diagnostic-design-20261111`; based on exact R3A adjudication `815541c6f8ed2e275d12ae67780b9a95228e490f`. **`T4=HOLD`** · `GPU/TRAIN/INFERENCE=NOT_EXECUTED` · `TEST_Q1Q2=UNTOUCHED`.

- [Báo cáo thiết kế corpus mới, thí nghiệm frozen-vs-adapted O0, đánh giá và một quyết định GO/HOLD](../../../docs/research/TTM_O0_ONLY_NEW_DIAGNOSTIC_NEURAL_FEASIBILITY_SOURCE_EVAL_BUDGET_AND_SINGLE_GO_NO_GO_20261111.md)
- [Machine-readable candidate: bốn họ dữ liệu, 1.280 quartet / 5.120 rows, một arm 128×4.096 target](TTM_O0_ONLY_NEW_DIAGNOSTIC_CORPUS_AND_SINGLE_RUN_DESIGN_CANDIDATE_20261111.json)
- [Biên nhận kiểm tra nguồn/thiết kế phía tác giả 27/27 và quyết định HOLD T4](TTM_O0_ONLY_NEW_DIAGNOSTIC_AUTHOR_DESIGN_SOURCE_QA_AND_SINGLE_DECISION_20261111.json)
- [R3A science adjudication kế thừa: heuristic Python 384/384, R3A demo-only](../../../docs/research/TTM_R3A_PYTHON_FULL_REPLAY_AND_OWNER_SCOPED_ADJUDICATION_20261111.md)

**Chưa có** dữ liệu corpus mới, generator, strict checker, runner science, checkpoint sau học hoặc FINAL ciphertext trên nhánh này. Các số 1.280/5.120/524.288 là *budget ứng viên*, **không phải số lượng mẫu/huấn luyện đã chạy**. Không dùng public R3A làm FINAL.

**Một bước tích hợp tiếp theo:** `TTM_O0_NEW_DIAGNOSTIC_CORPUS_GENERATOR_STRICT_CHECKER_SHORTCUT_AUDIT_AND_ONE_CPU_PREFLIGHT_SINGLE_OWNER_DECISION`. Chỉ sau kết quả CPU + private FINAL escrow + T4 capacity/restore, owner mới có thể ra quyết định GO/HOLD mới. Không biến từng kiểm tra thành micro-permit.

Không ghi `lineage.md` cho thiết kế; chỉ tiếp tục sau khoa học có phán quyết đúng quy trình.
