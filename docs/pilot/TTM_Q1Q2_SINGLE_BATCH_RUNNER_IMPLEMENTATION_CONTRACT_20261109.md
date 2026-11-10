# TTM Small4M — Q1/Q2 one-batch runner: hợp đồng triển khai hữu hạn

Ngày: 2026-11-09 · Base GitHub main `b57b44e7287f842e81050c1faee337f636333dd0` · PR #13, một nhánh duy nhất. **Đây là tài liệu thiết kế bộ chạy, không phải chứng nhận runtime và chưa thực thi Q1/Q2.**

## 1. Tái sử dụng nguồn đã có, không nhập lại mô hình

- Dùng đúng nguồn thuộc main: `tools/pilot_t5/v5_native_source_20261109/t5_final_minimal_smoke_v5.py` và `t5_native_tcp.py`. **Không** gọi hàm execute/create V5, chỉ tái sử dụng helper quan sát sở hữu tiến trình, phân loại TCP, xác minh socket, API và dừng cây tiến trình được sở hữu. Đối chiếu SHA-256 nguồn với manifest V5; từ chối nếu khác.
- GGUF F32 tại `_tmp/ttm_t5_trained_f32_v1/TTM-Small4M-T4-step1024-F32.gguf`: SHA-256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, kích thước 15.061.376 byte. Dùng kho mô hình đã import từ `_tmp/ttm_t5_ollama_compat_only_single_v5final/models`, xác minh `RESULT.json`, manifest-v2 và `MODELS_AFTER_CREATE.json`, rồi **sao chép** vào output mới; nguyên bản V5 và inference-only giữ nguyên.
- Ollama đã chứng minh 0.40.14; executable SHA-256 `14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981`. Port mới cố định **12650**, chỉ loopback; không đụng cổng 11434/12648/12649, không `ollama create`, không huấn luyện, không tái sử dụng RunID đã tiêu thụ.
- Tại project root `D:\WORK\RESEARCH\TokenToModel-Lab`: output một lần `_tmp/ttm_q1q2_ollama_once_v1`, source bootstrap tải từ **commit SHA của PR #13** sau khi mã/manifest được lưu GitHub. Không checkout nhánh vào local root, tránh đụng 17.635 tệp untracked.

## 2. Đầu vào cố định và thống kê hợp lệ

`tools/pilot_q1q2/frozen_inputs_20261109/` trên base main đã có:
- `Q1_ORIGINAL_PROMPTS.json` (16 lời dẫn tự viết, 8 everyday/4 cause_effect/4 consistency).
- `Q1_FROZEN_48_RUN_MATRIX.json` (16 greedy nhiệt độ 0 và 32 sampled nhiệt độ 0.8, top-p 0.9, seed 101/102); tối đa 48×64 = **3.072** token.
- `Q2_FROZEN_24_MEASUREMENT_MATRIX.json` (2 mức `num_ctx` 128/256, 4 prompt × 3 lần đo, 32 token mỗi lần) + 2 lượt warm-up, tổng **768+64** token. 
- Tổng ngân sách một batch **3.904** token output tối đa, chưa tính tokens đầu vào; HTTP `stream=false`, `raw=true`; mỗi lần phải lưu `run_id`, prompt ID, seed và options chính xác, raw response, `done_reason` và toàn bộ trường đo thời gian. Khi thiếu dữ liệu response, ghi `HOLD` không tự chạy lại.
- Chỉ số `distinct-2/3`, `repeat-3gram` trên chuỗi token BPE2048 được encode lại từ **generated text**, ghi rõ đó không phải native sampled token IDs. Đọc đúng `_tmp/ttm_t1_real_source_v1/T1_BPE2048_REAL_TRAIN_MANIFEST.json` SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, nạp `BPE2048` từ mã trên main; không đọc raw TRAIN/VAL/TEST. Nếu BPE manifest thiếu/sai hash thì `HOLD_PRECLAIM` thay vì giả dùng word count.
- Q2: `tokens_per_sec=eval_count/(eval_duration_ns/1e9)` khi `eval_count>0` và duration dương, tính median/range theo num_ctx, lưu `load_duration`, `prompt_eval_duration`, `eval_duration`, `total_duration`; **không** suy ra TTFT từ non-streaming và không gọi thay context là architecture ablation.
- Bốn chiều rubric 0–3 theo nguồn khóa; người chấm thủ công một người, không tự điền điểm hay tuyên bố độc lập. Tiêu chí GO/REVISE/STOP là *exploratory threshold* đã khóa trước, không coi là thử nghiệm xác nhận hay thương mại.

## 3. Một lượt với các cổng kỹ thuật gộp

1. **Offline static QA** mã nguồn và fixture: 16/48/24+2, SHA manifest, các trường hợp từ chối port bận/mô hình sai, chống ghi đè, không đọc TEST, không có path escape; xác nhận chính xác source GH SHA và tokenizer, lưu QA receipt trên PR #13.
2. **Preclaim read-only**: Python 3.12, đúng Windows/repo/origin/main SHA, nguồn V5+T1+Q1Q2/GGUF hash, PID/port không hoạt động, disk free ≥1 GiB, giới hạn thời gian một batch 45 phút, tài nguyên CPU xác minh. Không tự cài Python/Ollama, không thay hệ thống, không tạo CLAIM nếu thiếu điều kiện.
3. **One-shot**: tạo độc quyền một thư mục mới/CLAIM; copy model store kèm so hash từng tệp; khởi động đúng Ollama exe vào isolated HOME/TMP/MODELS, xác minh PID + executable + HTTP. Chạy **Q1 48 → Q2 warm-up 2 → Q2 measured 24**, mỗi request kiểm server ownership, timeout 180 giây; ghi raw từng request bất biến ngay sau khi nhận, không tự lặp job lỗi.
4. **Đóng và đọc lại**: dừng đúng tiến trình con, đánh giá cổng active socket, raw output + hash tree, tạo RESULT_PASS/HOLD/FAIL phân biệt rõ complete vs partial và nguồn. Nếu runtime hỏng thì vẫn cố lưu receipt và giữ dữ liệu ở project.
5. **Đẩy bằng chứng**: sàng lọc private/PII, GitHub fast-forward commit qua PR #13, tải lại mọi biên bản đã publish và so SHA trước bất kỳ cleanup nào. **Không xóa kho V5, checkpoint, tokenizer manifest riêng, worktree hay 17.635 tệp untracked.** Không dọn run dir khi còn thiếu bằng chứng cần phục hồi.

## 4. Điều kiện đóng và merge

- `Q1Q2_RUNNER_SOURCE=PASS`: nguồn + negative QA đã ghi vào PR và đọc lại được. Không tương đương native PASS.
- `Q1Q2_BATCH=PASS_EXECUTED_SCOPED`: 48 + 2 + 24 raw completed đúng ID/model/hash và có receipt; metrics độc lập kiểm lại. Mọi thiếu/timeout là HOLD/FAIL tương ứng, không chạy lại consumed run.
- `QUALITY_GO` chỉ sau khi rater thủ công hoàn tất và so đúng tiêu chí exploratory; nếu chưa chấm thì `QUALITY=NOT_ADJUDICATED`, dù inference PASS.
- `MERGE_READY` đòi nguồn thực thi, test/QA, bảng chất lượng + raw, quyền công bố và lineage khoa học đúng; người dùng review, merge bằng PR, kiểm main, sau đó xem xét nghỉ hưu nhánh. **Không tạo nhánh Q1/Q2 thứ hai.**

**Bước kế tiếp:** `TTM_Q1Q2_SINGLE_BATCH_RUNNER_IMPLEMENTATION_AND_OFFLINE_QA`. Chỉ triển khai code và test từ nguồn GitHub trên PR #13 trước khi cho phép một lượt native.
