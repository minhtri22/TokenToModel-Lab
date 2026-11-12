# HANDOFF — TTM-Small-4M D1 Exploratory DEV32 / BLIND64

**Vai trò:** Independent ChatGPT blind rater, scoring only (chấm mù, không tạo văn bản).  
**Loại:** `EXPLORATORY_SCOPED_AI_REVIEW`, riêng khỏi D1 confirmatory 512 outputs.  
**Trạng thái khi phát hành handoff:** `BLIND_INPUT_PENDING_ACTUAL_CPU_EXECUTION`.

## Lệnh thực hiện

Khi chủ dự án chuyển handoff kèm **tệp `D1_EXP32_BLIND64_PRIVATE.json`** vào một ChatGPT chat mới, thực hiện ngay trong phạm vi được giao. **Không ký nhận hay xin phép chấm**. Không xem mã sinh, nhánh khoa học, seed, decoder, labels, mapping, private owner raw, kết quả prior studies, hoặc câu trả lời dự kiến. Chỉ xem `opaque_id`, `prompt_text`, `generated_text_only`.

1. Xác nhận schema `ttm.d1.exploratory_dev32.blind64.v1`, 64 records, opaque_id duy nhất. Ghi SHA-256 của tệp gốc; nếu thiếu tệp hoặc chưa có `generated_text_only` là dữ liệu thật, trả `RATER_BLOCKED_NO_AUTHORIZED_TEXT` thay vì bịa điểm.
2. Chấm đủ **64/64** văn bản theo cùng rubric D1: `adherence_0_to_3` nguyên từ 0 tới 3.
   - **0:** không có sự kiện/hành động đủ điều kiện chấm.
   - **1:** có sự kiện nhưng sai hoặc không gắn với dữ kiện câu hỏi.
   - **2:** hành động đầu phù hợp fact, nhân vật và đối tượng.
   - **3:** hành động phù hợp fact và giữ mục tiêu ở diễn tiến tiếp.
3. Mỗi record ghi thêm `first_event_fact_match` (true/false/null), `goal_retention` (true/false/null), `serious_contradiction` (true/false/null), `notes` ngắn và nêu `unscorable_reason` nếu null. Không suy diễn từ text không đủ thông tin.
4. Trả một tệp **private** `D1_EXP32_RATER_BLIND64_SCORES.json` chứa record theo opaque_id và receipt `D1_EXP32_RATER_BLIND64_SCORE_FREEZE_RECEIPT.json` gồm `model_used`, `input_sha256`, `count=64`, `scored_count`, `unscorable_count`, `scores_sha256`, `blindness_integrity`, `actual_execution_status`. **Khóa điểm và SHA-256 trước khi giải mù**.
5. Không công khai generated_text hay per-record score lên GitHub; không sửa khoa học, không mở TEST/Q1Q2 và không tạo outputs mới.

**Cảnh báo:** Một seed nucleus được dùng cho 32 văn bản; kết quả chỉ có thể hỗ trợ phân tích khám phá, không chứng minh decoder rescue bền vững. Sau khi khóa điểm, giao receipt về owner để nối lại nhãn nội bộ và phân xử DEV32.

**Bước thực hiện tiếp theo:** Sau khi CPU owner tạo đủ BLIND64 và khóa SHA, giao chính tệp mù cùng handoff này cho ChatGPT phiên khác. Handoff tự khởi động công việc khi có dữ liệu, không tự khởi chạy một agent từ commit GitHub.
