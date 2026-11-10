# Handoff Codex AI — Adversarial R3A source, shortcut, O0-only decision

**As of 2026-11-11** · **Task:** `TTM_R3A_CODEX_ADVERSARIAL_HEURISTICS_REVIEW_THEN_O0_ONLY_SMALL_NEURAL_FEASIBILITY_SINGLE_OWNER_DECISION` · **Review role:** Codex AI nội bộ, không đại diện bên ngoài. **Không** chạy GPU, huấn luyện TTM, mở TEST/Q1Q2 hoặc thay main/lineage.

## Đọc từ GitHub, không sử dụng ZIP của ChatGPT

- [Phân xử R3 và sửa R3A](TTM_R3_ADVERSARIAL_REVIEW_OWNER_ADJUDICATION_AND_R3A_MINIMAL_ANTISHORTCUT_CPU_QA_20261111.md).
- [Manifest SHA/git blob](../../artifacts/qa/ttm-r3-structural-design/r3a/R3A_SOURCE_OF_TRUTH_SHA256_AND_OWNER_SCOPED_DECISION_20261111.json).
- [R3A generator](../../tools/research/semantic_state_r3/r3a_generator.py), [checker](../../tools/research/semantic_state_r3/r3a_independent_checker.py), [44 tests](../../tools/research/semantic_state_r3/r3a_integrated_cpu_qa.py).
- [R3A public oracle](../../artifacts/qa/ttm-r3-structural-design/r3a/R3A_PUBLIC_ORACLE.json), [384 input-only rows](../../artifacts/qa/ttm-r3-structural-design/r3a/R3A_MODEL_INPUT_ONLY.json).
- [R3A baseline 208/384](../../artifacts/qa/ttm-r3-structural-design/r3a/R3A_LATEST_WRITE_BASELINE.json), [R3 gốc exact Python 384/384](../../artifacts/qa/ttm-r3-structural-design/r3a/R3_ORIGINAL_CODEX_BASELINE_EXACT_PYTHON_FULL_REPLAY.json).
- [Review R3 đã khóa](TTM_R3_ADVERSARIAL_REVIEW_20261111.md) và [original reviewer Python](../../tools/research/semantic_state_r3/ttm_r3_independent_latest_write_baseline.py) inherited unchanged from commit `d641e1577eaef4d3adffa526a13c3392a519b3bb`.

## Phản biện cần thực hiện thực sự, không chấm hình thức

1. **Kiểm SHA và tái lập.** Kiểm Git blob tất cả hiện vật; gọi đúng checker độc lập với hai JSON (384/384) và chạy 44 tests. Nếu chưa chạy, ghi `NOT_EXECUTED`.
2. **Đối chứng heuristic mới:** A) alias substitution/reverse lookup (không cập nhật state), B) last relevant delegation/cancel, C) shallow regex/transducer, D) positional/row-index bias. Đo trên từng family+split và **không dùng oracle để dự đoán**. Nếu một shallow rule đạt 384/384, giữ `SCIENCE_DISCRIMINATION=HOLD` cùng source code/chứng cứ.
3. **Phản thực semantic:** A/B target và distractor; kiểm tiền điều kiện, alias binding, goal `NONE`; bắt lỗi nếu statement giống hệt gây lộ đáp án theo vị trí, hoặc group/cell ID lọt qua model-input.
4. **Structural split:** query-conditioned event-role signature hiện tại vẫn có thể quá yếu; thử canonical dependency graph theo cạnh và ràng buộc query thay vì chỉ event sequence; kiểm overlap và adjacency pattern across DEV/CHALLENGE.
5. **Fairness và claim:** R3A là public toy; không gọi FINAL. Đối chứng `C-F` khác objective, không kết luận pure architecture. Không dùng R3A để chọn/huấn luyện O1.
6. **Kết luận lựa chọn:** `KEEP_O0_ONLY_SMALL_NEURAL_FEASIBILITY_DESIGN` / `AMEND_TOY_AGAIN` / `ARCHIVE_R3_UNINFORMATIVE`. Không có GO T4 trong chính review này.

**Cách ghi bằng chứng:** báo cáo phản biện .md, baseline độc lập .py, kết quả replay JSON/stdout và QA/negative receipt .json trên **nhánh review riêng**, ghim exact SHA R3A. Bất kỳ review source nào chưa được chạy đầy đủ phải ghi `SOURCE_READ_ONLY` thay vì `PASS_REPLAY`. Không sửa các tệp gốc trong nhánh này, không merge và không claim scientific PASS.

**Bước thực hiện tiếp theo sau review:** một quyết định owner duy nhất cho `O0_ONLY_SMALL_NEURAL_FEASIBILITY` hoặc HOLD/ARCHIVE. O1 vẫn DEFER.
