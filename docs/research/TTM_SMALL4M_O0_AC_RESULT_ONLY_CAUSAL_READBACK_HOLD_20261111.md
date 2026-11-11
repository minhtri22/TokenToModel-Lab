# TTM-Small-4M O0 — Đọc lại kết quả A/C: HOLD khi chưa có phân xử khoa học

**Ngày:** 2026-11-11  
**Công việc:** `TTM_SMALL4M_ORIGINAL_O0_OBJECTIVE_SIGNAL_AC_RESULT_ONLY_CAUSAL_DECISION_READBACK`  
**Nhánh ghi nhận duy nhất:** `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111`  
**Phạm vi:** `DESIGN_AND_SOURCE_READBACK_ONLY`. Không thực thi, không chấm lại, không tạo cổng mới.

## 1. Thực tế nguồn GitHub đã kiểm

- HEAD nhánh hậu CF1 trước khi ghi nhận: `9ff667662f2dd25cb15d9094414c259acca156d8`.
- HEAD nhánh agent AC: `837289fda82b41653a61b74e476f76a0b4c4137c`, **không đổi** so với lần rà soát trước.
- Đã xem danh mục đầy đủ của cây tệp AC tại đúng HEAD này (`truncated=false`). Không thấy tệp kết quả huấn luyện A/C thực hoặc biên bản phân xử khoa học về `C−A`; không đồng nhất các QA tổng hợp/kết quả mô phỏng với kết quả thực tế.
- Biên nhận AC có thẩm quyền tại `artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_SMALL4M_AC_FINAL_PREEXEC_SINGLE_DECISION_AND_SOURCE_READBACK_20261111.json`, Git blob `0c83b23c13c588a7787dd64a6c3d9ed5da22c5ce`: `status=NO_GO_PREEXEC_EXTERNAL_AND_NATIVE_GATES_OPEN`, `decision=NO_GO_NO_EXECUTION`.
- Các kiểm nguồn **đã PASS phạm vi**: static QA 23/23, synthetic CPU resume 6/6, quyền theo văn bản license, escrow ciphertext và cân bằng 12/12. Đây không phải bằng chứng A/C đã được train.
- Các điều kiện chưa đóng trong biên nhận: quyền dùng private pack do owner chứng thực, lưu riêng khóa giải mù, người chấm độc lập, native Python 3.12 V2, zero-step T4 FP16, khôi phục thực tế Small4M, khóa owner cho science.

**Giới hạn xác minh:** kết luận `NOT_FOUND_AT_PINNED_AC_GITHUB_HEAD` chỉ áp dụng nguồn GitHub của nhánh AC đã xem, không chứng minh tuyệt đối rằng không tồn tại kết quả chưa đẩy lên GitHub hoặc ở nguồn riêng. Không đọc Windows, Drive hay khóa riêng trong lượt này.

## 2. Phân xử điều kiện nhân quả O0

| Chỉ số | Trạng thái |
|---|---|
| Arm A huấn luyện đủ 128 bước, checkpoint/receipt | `NOT_EVIDENCED` |
| Arm C huấn luyện đủ 128 bước, checkpoint/receipt | `NOT_EVIDENCED` |
| Điểm FINAL24 theo chấm mù và SHA khóa | `NOT_EVIDENCED` |
| `Δ = score_C − score_A` | **`NOT_ESTIMABLE`** |
| Điều kiện VAL NLL và coherence/consistency | `NOT_EVALUABLE` |
| Kết luận nhân quả về suffix-weighted CE | **`UNDETERMINED`** |
| Đánh giá nguyên nhân dữ liệu/cửa sổ | **`UNPROVEN_UNCHANGED`** |

Không được ghi `C−A=0`, `C−A=FAIL`, hoặc `H_OBJECTIVE_FALSIFIED`: thiếu dữ liệu khác với kết quả âm tính khoa học. Cũng không được suy rằng dữ liệu là nguyên nhân chỉ vì AC chưa có kết quả. Đối chứng hiện hữu chỉ phân biệt **trọng số loss theo vị trí** và không phân biệt corpus diversity, semantic goal supervision, khả năng mô hình 3,75M hoặc ranh giới context 256.

## 3. Một quyết định và điều kiện đóng

**`O0_OBJECTIVE_CAUSAL_DECISION=HOLD_AC_NO_ADJUDICATED_RESULT`**.

Giữ phương hướng thiết kế `O0_SAME_ARCH_OBJECTIVE_SIGNAL_ALLOCATION_AS_AC_C_MINUS_A` như một giả thuyết ưu tiên để kiểm chứng, **không biến thành ưu tiên bắt buộc huấn luyện hoặc quyền chạy**. Tiếp tục bảo toàn `T4_VAL_H1=PASS`, `DATA_WINDOW_CAUSE=UNPROVEN`, `CAPACITY_CEILING=UNPROVEN`, `B/D=DEFER`, `O1=DEFER`.

Chỉ tiếp nhận **sau này** khi đúng agent AC công bố một biên bản khoa học hoàn tất có nguồn checkpoint hai arm, khóa chấm FINAL24 và kết quả chênh lệch cùng kiểm tra an toàn VAL. Nếu agent AC ra quyết định HOLD cuối mà không huấn luyện, ghi đúng HOLD, không tự tạo toy, mở đào tạo mới hoặc hỏi micro-permit.

**Không viết** nhánh AC, FRESH16, `main`, `lineage.md`, PR#13; không mở TEST/Q1Q2; không sửa/tạo science prereg. Tài liệu này không phải kết quả PASS/FAIL khoa học để append `lineage.md`.

## Bước thực hiện tiếp theo

`TTM_SMALL4M_ORIGINAL_O0_WAIT_FOR_AC_ADJUDICATED_RESULT_OR_FINAL_HOLD_READBACK_ONLY`

Không thực hiện nghiên cứu mới từ nhánh hậu CF1 khi thiếu dữ liệu AC. Khi nguồn AC thật sự đổi, chỉ đọc biên bản quyết định cuối và áp dụng phép phân biệt C−A đã khóa để phân xử giả thuyết mục tiêu học theo đúng phạm vi.

**Trạng thái cuối:** `O0_SOURCE=PINNED` · `T4_VAL_H1=PASS` · `AC=NO_GO_PREEXEC` · `C_MINUS_A=NOT_ESTIMABLE` · `H_OBJECTIVE=UNDETERMINED` · `DATA_WINDOW_CAUSE=UNPROVEN` · `CAPACITY_LIMIT=UNPROVEN` · `B/D=DEFER` · `O1=DEFER` · `NEW_TRAINING=NO` · `GPU=NO` · `TEST_Q1Q2=UNTOUCHED` · `MAIN/LINEAGE=UNMODIFIED`.
