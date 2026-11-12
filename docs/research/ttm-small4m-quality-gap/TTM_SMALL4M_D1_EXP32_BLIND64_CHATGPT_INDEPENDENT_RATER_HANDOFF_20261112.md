# HANDOFF — TTM-Small-4M D1 Exploratory DEV32 / BLIND64

**Vai trò:** Independent ChatGPT blind rater, scoring only (chấm mù, không tạo văn bản).  
**Loại:** `EXPLORATORY_SCOPED_AI_REVIEW`, riêng khỏi D1 confirmatory 512 outputs.  
**Trạng thái sau thực thi owner:** `BLIND64_ACTUAL_OUTPUTS_FROZEN_OWNER_LOCAL` · `RATER_SCORING_NOT_STARTED`.

**SHA-256 tệp BLIND64 thực tế:** `4288c311f22147a85a414fd436fbeba1287464bb60d745ca64e5ce07839158f1`. Chỉ chấm khi SHA-256 tệp đính kèm trùng chính xác. Nếu tệp bị thay đổi, trả `RATER_BLOCKED_INPUT_SHA_MISMATCH`; không dùng dữ liệu thay thế.

## Lệnh thực hiện

Khi chủ dự án chuyển handoff kèm **tệp `D1_EXP32_BLIND64_PRIVATE.json`** vào một ChatGPT chat mới, thực hiện ngay trong phạm vi được giao. **Không ký nhận hay xin phép chấm**. Không xem mã sinh, nhánh khoa học, seed, decoder, labels, mapping, private owner raw, kết quả prior studies, hoặc câu trả lời dự kiến. Chỉ xem `opaque_id`, `prompt_text`, `generated_text_only`.

1. Xác nhận SHA-256 byte của tệp đính kèm đúng với giá trị đã khóa bên trên, schema `ttm.d1.exploratory_dev32.blind64.v1`, 64 records, opaque_id duy nhất. Nếu thiếu tệp, SHA không trùng hoặc chưa có `generated_text_only` thực tế, trả `RATER_BLOCKED_NO_AUTHORIZED_TEXT_OR_SHA_MISMATCH` thay vì bịa điểm.
2. Chấm đủ **64/64** văn bản theo cùng rubric D1: `adherence_0_to_3` nguyên từ 0 tới 3.
   - **0:** không có sự kiện/hành động đủ điều kiện chấm.
   - **1:** có sự kiện nhưng sai hoặc không gắn với dữ kiện câu hỏi.
   - **2:** hành động đầu phù hợp fact, nhân vật và đối tượng.
   - **3:** hành động phù hợp fact và giữ mục tiêu ở diễn tiến tiếp.
3. Mỗi record ghi thêm `first_event_fact_match` (true/false/null), `goal_retention` (true/false/null), `serious_contradiction` (true/false/null), `notes` ngắn và nêu `unscorable_reason` nếu null. Không suy diễn từ text không đủ thông tin.
4. Trả một tệp **private** `D1_EXP32_RATER_BLIND64_SCORES.json` chứa record theo opaque_id và receipt `D1_EXP32_RATER_BLIND64_SCORE_FREEZE_RECEIPT.json` gồm `model_used`, `input_sha256`, `count=64`, `scored_count`, `unscorable_count`, `scores_sha256`, `blindness_integrity`, `actual_execution_status`. **Khóa điểm và SHA-256 trước khi giải mù**.
5. Không công khai generated_text hay per-record score lên GitHub; không sửa khoa học, không mở TEST/Q1Q2 và không tạo outputs mới.

**Giới hạn:** Đây là chấm khám phá DEV, không phải đánh giá xác nhận (confirmatory). Người chấm không được nhận thông tin phương pháp giải mã, seed hoặc điều kiện của từng record; điều này chỉ được nối lại phía owner **sau khi khóa điểm**. Không tuyên bố cải thiện decoder bền vững chỉ từ phép chấm này.

**Bước thực hiện tiếp theo:** Chủ dự án đính kèm tệp `D1_EXP32_BLIND64_PRIVATE.json` từ `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_D1_EXPLORATORY_DEV32_ONE_SHOT_20261112` vào một phiên ChatGPT mới không có ngữ cảnh nghiên cứu, đồng thời chuyển rubric trong handoff này. Tệp private chỉ để chấm trong phiên đó, không công khai trên GitHub. Handoff tự khởi động công việc khi dữ liệu được giao, không tự khởi chạy agent từ commit GitHub.
