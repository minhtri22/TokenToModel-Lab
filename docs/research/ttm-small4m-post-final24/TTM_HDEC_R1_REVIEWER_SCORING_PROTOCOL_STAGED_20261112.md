# H-DEC-R1 — Quy trình người chấm mù kế nhiệm (STAGED, chưa tiếp nhận)

**Operation:** `TTM_SMALL4M_H_DEC_R1_INDEPENDENT_BLIND_RATER_ACCEPTANCE_PENDING`  
**Run:** `TTM_SMALL4M_POST_FINAL24_DECODING_REPETITION_DIAGNOSTIC_V1`  
**Status:** `REVIEWER_NOT_ASSIGNED_OR_ACCEPTED` · `NO_MODEL_OUTPUTS` · `SCORING_NOT_STARTED`.

## Phạm vi

- 24 prompt riêng tư mới `NF01–NF24`, 48 đoạn văn sinh trên cùng checkpoint A bước 1152 bằng hai decoder D0/D1.
- Mỗi prompt có một cặp `R01–R24`, hai đoạn `LEFT/RIGHT` xếp theo escrow AES-256-GCM đã khóa 12/12, cân bằng 3/3 ở từng stratum. Người chấm KHÔNG nhận danh tính D0/D1 hay mapping.
- Chấm mỗi đoạn ba trục 0–3: **prompt adherence**, **coherence**, **consistency** (sử dụng rubric FINAL24 cũ chỉ ở mức tiêu chí, không sử dụng văn bản hoặc điểm cũ). Tổng cộng **144 điểm nguyên**, 24 ghi chú theo từng cặp, trung lập cả hai thứ tự; được phép cho điểm bằng nhau.
- Người chấm không dùng lịch sử ChatGPT của owner, không truy cập file owner, không hỏi khóa, không tra GitHub để suy đoán nhãn. Khai báo chính xác là AI hay con người, không tự nhận xác minh độc lập tổ chức.

## Chấm và khóa

Chỉ khi nhận packet sau một lần inference hợp lệ và đúng SHA, tạo score file, SHA-256 của JSON điểm nguyên byte và SHA mảng score canonical; biên nhận gồm reviewer identity, session reference thực tế nếu được cung cấp, UTC, SHA đầu vào, đếm 144 số và 24 note, `UNBLIND=NOT_EXECUTED`. Owner xác minh điểm đã khóa rồi mới giải mù ở phiên riêng.

**Chưa thực hiện:** giao packet, chấm, tạo score, nhận xác nhận reviewer. Tệp này không phải chữ ký chấp nhận hoặc sự kiện reviewer đã nhận công việc.

## Sau freeze — tính lại kết quả

Metric đo lặp tự động trên 48 raw outputs, khác đánh giá ngữ nghĩa bằng người chấm. Dùng chuẩn từ `re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower())`; `repeat_fraction=1-unique_word_trigrams/total_word_trigrams` hoặc 0 nếu dưới 3 từ. Chấm mù guardrail bắt buộc trên 3 trục riêng. Tính CIs bằng NumPy `2.3.5`, `default_rng(20261112)`, 20.000 resamples trên 24 cặp, `quantile(..., method='linear')`. Không dùng lại FINAL24 cũ để chọn penalty hoặc ngưỡng.
