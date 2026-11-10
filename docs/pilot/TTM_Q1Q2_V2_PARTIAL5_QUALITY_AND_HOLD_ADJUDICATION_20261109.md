# TTM-Small-4M — Q1/Q2 V2: 5 đầu ra thật, đánh giá thăm dò và giữ HOLD

Ngày 2026-11-09. Nguồn dữ liệu: GitHub commit [`0ff76409919903cd1e7b7035890b012300984eef`](https://github.com/minhtri22/TokenToModel-Lab/commit/0ff76409919903cd1e7b7035890b012300984eef), không sử dụng TEST đã niêm phong. Biên bản này **chỉ phân tích kết quả đã sinh**; không chạy thêm Ollama hoặc chấm rubric thay người đánh giá.

## 1. Phân xử kỹ thuật

- 17/17 kiểm thử offline PASS, native preview PASS; V2 đã tạo CLAIM tại `_tmp/ttm_q1q2_ollama_once_v2` và sinh **5/74** yêu cầu, **283** token từ 2 prompts (E01 3 outputs; E02 2 outputs); Q2: **0/24**, warmups 0/2.
- `failure.message=OWNERSHIP_RECHECK_HOLD_UNTRUSTED_PID` trước request thứ sáu, tại `v5.assert_owned_listener()`. Không nên suy ra tiến trình lạ thực sự chiếm cổng: nguồn phân loại từ chối bất kỳ row PID khác PID kỳ vọng, ngoại lệ duy nhất là `PID=0, state=11, TIME_WAIT` có hình dạng chuẩn. **Không có TCP snapshot đúng thời điểm failure được lưu trong RESULT.**
- `shutdown.stop_status=STOPPED_OWNED_TREE` với taskkill exit 0; nhưng `shutdown_port.decision=HOLD_UNSAFE_PORT_ROW_AFTER_SHUTDOWN`. Chưa chứng nhận cổng đã sạch hoặc tiến trình lạ là vô hại. **Không nới lỏng/loại bỏ owner gate**.
- V1 `HOLD` 0 requests và V2 `HOLD` 5 requests đều đã tiêu thụ; giữ nguyên thư mục, log, raw, checkpoint, model store; không tự chạy lại/khởi động V3. GitHub đã ghi commit và readback 8/8 file V2.

## 2. Số liệu Q1 trên mẫu có thật

| Run | Điều kiện | Token native | Distinct-3 (BPE re-encode) | Repeat-3gram | Done |
|---|---|---:|---:|---:|---|
| `Q1-E01-G0` | GREEDY | 64 | 0.7903 | 0.2097 | `length` |
| `Q1-E01-S101` | SAMPLED | 64 | 0.9677 | 0.0323 | `length` |
| `Q1-E01-S102` | SAMPLED | 64 | 1.0000 | 0.0000 | `length` |
| `Q1-E02-G0` | GREEDY | 27 | 0.9167 | 0.0833 | `stop` |
| `Q1-E02-S101` | SAMPLED | 64 | 0.9839 | 0.0161 | `length` |

Trung bình `distinct-3`: greedy **0.8535** (n=2) vs sampled **0.9839** (n=3). `repeat-3gram`: greedy **0.1465**, sampled **0.0161**. Đây chỉ là mô tả nhóm rất nhỏ, **không phải kết luận hiệu quả sampling hay kiểm định thống kê**, không phải token ID native. Có 4 output bị giới hạn 64 token và 1 output dừng bằng EOS sau 27 token.

## 3. Sàng lọc chất lượng bằng quan sát, không chấm rubric khoa học

- E01 hỏi tiếp câu chuyện **Mara, chiếc cốc đỏ, tiếng gõ cửa sổ**. Greedy lặp `big tree` và đưa nhân vật Lily không có trong prompt; sampling chuyển sang `park/garden`, câu sai ngữ pháp, mất mục tiêu sự kiện.
- E02 hỏi **Leo có một chiếc tất khô, cần giữ ấm hai chân**. Greedy/sampled chuyển sang công viên, gấu, cây cối, không giải quyết vấn đề chiếc tất.
- Kết luận chỉ đạt `PARTIAL_OBSERVATION_WEAK_PROMPT_ADHERENCE`: có mẫu cấu trúc truyện ngắn, nhưng liên kết thực thể, mục tiêu và sự kiện rất yếu; sampling làm đa dạng từ vựng nhưng không cứu mạch lạc trong 5 mẫu.
- Chưa có 16 greedy, 4 nhân quả, 4 nhất quán và đánh giá 0–3 của người chấm. Vì vậy **không được chấm GO/STOP cuối cùng**, không ghi `PASS`/ `FAIL` science vào `lineage.md`.

## 4. Quyết định hữu hạn, không vòng lặp hạ tầng

`Q1Q2_EXECUTION=HOLD_INCOMPLETE`; `QUALITY=NOT_ADJUDICATED`; `REVISE=CANDIDATE`; `Q2=NOT_EXECUTED`; `MERGE=HOLD`.

**Đề xuất:** không khởi động V3 chỉ để đủ 74 lần sinh. Rà soát khoa học TTM-Small-4M trước: vì T4 checkpoint step1024 đã tốt hơn bigram trên VAL nhưng 5 đầu ra hiện bám prompt yếu, cần xác định rõ hướng cải thiện tiếp theo (budget train, dữ liệu, context, tokenizer/causal format) và một phép thử thăm dò nhỏ, độc lập trước khi tiếp tục full Q1/Q2. Bất kỳ thay đổi nào cũng phải đăng ký trước và **không đổi điều kiện Q1/Q2 đã khóa** nếu muốn giữ phép so sánh gốc.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_PARTIAL5_QUALITY_REVISE_DECISION_AND_NO_THIRD_RUN`. Chỉ sau khi quyết định khoa học mới xem xét successor inference phù hợp; yêu cầu kiểm tra owner port với bằng chứng TCP đầy đủ chứ không bỏ gate.
