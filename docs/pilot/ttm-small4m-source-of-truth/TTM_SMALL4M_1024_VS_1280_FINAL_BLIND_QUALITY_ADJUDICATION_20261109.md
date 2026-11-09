# TTM-Small-4M T4 gốc — đánh giá A/B chấm mù bước 1.024 và 1.280

**Ngày:** 2026-11-09 · **Phạm vi:** Thăm dò mô tả (exploratory), 8 prompt, 2 decoder, 16 cặp, 32 bản sinh đã tồn tại. **Không huấn luyện, không sinh thêm, không TEST, không tái sử dụng Q1/Q2.**

## 1. Quy tắc và trình tự

1. Chỉ đọc `blinded_review.csv` trong ZIP gốc, không mở khóa `blinding_key_private.json`. Khóa `RUBRIC_AND_DECISION_FREEZE.json` SHA-256 `d894795e09bf88a64a08839425ad9ef721c912ae7315e0d1387991cb292ac969`.
2. Chấm đủ 96 ô điểm nguyên trên ba trục: **bám prompt (adherence)**, **mạch lạc (coherence)**, **nhất quán (consistency)**, thang 0–3. Mỗi A/B được chấm riêng, không lấy NLL làm tiêu chí chất lượng. Không trừ điểm cơ học chỉ vì câu cuối bị cắt bởi hạn mức 64 token BPE.
3. Đóng băng phiếu A/B trước giải mù: `FROZEN_BLIND_SCORES.csv`, SHA-256 **`cafffd62bddf441c301e3058d7941c09e6e4d96bf144ab40009971bfc882c24c`**; biên bản đóng băng SHA-256 `84bfb357fe577c439aee08a82d32ea17c0f660661d0353527114b5e2739cbdaa`. **Chỉ sau đó** mở khóa A/B từ ZIP, đối chiếu 32 đoạn nguyên văn với `raw.json`, tính chênh lệch và đánh giá ngưỡng.
4. QA lập trình tách khỏi hàm chấm điểm đạt **PASS_25_OF_25_SCOPED_MATERIAL_AND_ARITHMETIC**. QA chứng minh hash/mapping/tính toán/phạm vi, **không chứng minh sự đúng đắn của nhận xét chủ quan**. Ngưỡng quyết định đã được khóa **trước khi đọc mapping**, nhưng **sau khi nhìn thấy văn bản A/B**, vì vậy không phải một prereg xác nhận bên ngoài.

**Rubric:**
- 0: không đạt/đổi chủ đề/đứt mạch hoặc mâu thuẫn nặng; 1: nối tiếp rất yếu, chỉ còn đại từ hoặc mảnh nghĩa; 2: có diễn biến/chi tiết cốt lõi tương đối ổn; 3: phát triển liên quan, rõ ràng, nhất quán. Mô tả riêng từng trục ở `RUBRIC_AND_DECISION_FREEZE.json`.

**Ngưỡng cải thiện thăm dò được khóa trước khi giải mù:** tổng trung bình tăng ít nhất **+1,5/9**; bước 1.280 thắng ít nhất **10/16 cặp**; cận dưới bootstrap cụm theo prompt trên 0; cả Greedy và Sampling có chênh lệch không âm. Bắt buộc đủ bốn tiêu chí mới gọi `IMPROVED_EXPLORATORY`.

## 2. Kết quả

| Tiêu chí (0–3) | 1.024 | 1.280 | Δ 1.280−1.024 |
|---|---:|---:|---:|
| Bám prompt | 0.375 | 0.375 | +0.000 |
| Mạch lạc | 0.500 | 0.938 | +0.438 |
| Nhất quán | 0.500 | 0.750 | +0.250 |
| **Tổng (0–9)** | **1.375** | **2.062** | **+0.688** |

**Thắng/Hòa/Thua theo tổng điểm từng cặp:** checkpoint 1.280 thắng **6**, checkpoint 1.024 thắng **2**, **8** cặp hòa. Greedy Δ **+0,500/9**, Sampling Δ **+0,875/9**. Không cải thiện bám prompt (Δ = 0).

Bootstrap mô tả phân cụm theo 8 prompt (giữ nguyên cặp 2 decoder; 10.000 lần, seed 20261109): **[+0.0625, +1.3125]** điểm tổng. Đây **không** phải khoảng tin cậy hiệu chuẩn cho chất lượng ngoài tập 8 prompt hoặc độ tin cậy giữa người chấm.

## 3. Bảng chấm đầy đủ theo 16 cặp

Mỗi ô dưới đây ghi **(bám prompt, mạch lạc, nhất quán)**; bảng CSV đính kèm chứa nhận xét định tính riêng từng cặp và dấu A/B khi giải mù.

| Prompt | Decoder | 1.024 | 1.280 | Tổng Δ | Thắng |
|---|---|---|---|---:|---|
| P01 | greedy | (1, 1, 0) | (1, 1, 0) | +0 | tie |
| P01 | sampled | (1, 0, 0) | (1, 1, 0) | +1 | 1280 |
| P02 | greedy | (0, 0, 0) | (0, 2, 2) | +4 | 1280 |
| P02 | sampled | (0, 0, 0) | (0, 0, 0) | +0 | tie |
| P03 | greedy | (0, 0, 1) | (0, 1, 0) | +0 | tie |
| P03 | sampled | (0, 1, 1) | (0, 1, 0) | -1 | 1024 |
| P04 | greedy | (1, 1, 1) | (1, 1, 1) | +0 | tie |
| P04 | sampled | (1, 0, 0) | (1, 1, 1) | +2 | 1280 |
| P05 | greedy | (0, 1, 1) | (0, 1, 2) | +1 | 1280 |
| P05 | sampled | (0, 1, 1) | (0, 1, 1) | +0 | tie |
| P06 | greedy | (0, 1, 1) | (0, 1, 1) | +0 | tie |
| P06 | sampled | (0, 0, 0) | (1, 1, 2) | +4 | 1280 |
| P07 | greedy | (0, 1, 1) | (0, 0, 1) | -1 | 1024 |
| P07 | sampled | (1, 0, 0) | (0, 1, 0) | +0 | tie |
| P08 | greedy | (1, 1, 1) | (1, 1, 1) | +0 | tie |
| P08 | sampled | (0, 0, 0) | (0, 1, 0) | +1 | 1280 |

## 4. Phân tích nhạy cảm và giới hạn

- **Hai ví dụ P02/greedy và P05/greedy** từng bị gắn nhãn checkpoint trong một trả lời trước. Dù lần này chỉ mở mapping sau khi khóa phiếu, reviewer ChatGPT có thể nhớ những ví dụ đó. Vì vậy **không thể gọi lượt chấm này là đánh giá hoàn toàn mù**. Khi loại hai cặp, chỉ còn 14 cặp: bước 1.280 thắng 4, bước 1.024 thắng 2, hòa 8; Δ trung bình **+0,429/9**.
- Chỉ **một AI reviewer**, không phải người đánh giá độc lập hoặc hội đồng nhiều người; không có thước đo đồng thuận giữa các giám khảo (inter-rater agreement). Do đó kết luận không đủ cơ sở xác nhận lợi ích người dùng.
- Các đoạn dài tối đa 64 BPE tokens, có thể kết thúc khi chưa trọn câu; 8 prompt không đại diện cho nhiệm vụ chung. Một draw/seed cho sampling; không thể suy ra độ bền vững giữa các seed.
- Bộ chạy phát sinh 32 đoạn bằng triển khai forward PyTorch độc lập theo P02, nhưng **chưa xác minh parity số học bit-exact** với bộ P02 chuẩn. QA ban đầu mô tả một smoke forward sai công thức và loại bỏ nó; đầu ra hiện tại là lượt sửa sau đó. Nếu cần xác nhận suy luận hệ thống, đây là một cổng kỹ thuật còn mở.
- Kết quả huấn luyện VAL NLL bước 1.024→1.280 **3,522339→3,498089** vẫn hợp lệ trong phạm vi trước đó. Phép chấm này không phủ định việc giảm NLL; chỉ bác bỏ suy diễn rằng NLL giảm đã chứng minh khả năng sinh tốt rõ rệt.

## 5. Phân xử

**`QUALITY_VERDICT=NO_DEMONSTRATED_GAIN_SCOPED`**: bước 1.280 có điểm mạch lạc và nhất quán nhỉnh hơn, nhưng tổng điểm chỉ tăng **+0,688/9**, chưa qua ngưỡng khóa **+1,5/9**, và chỉ có **6/16** thắng, dưới ngưỡng **10/16**. Bám prompt không tăng. Kết luận là **chưa chứng minh mức cải thiện đủ mạnh**, không khẳng định 1.280 tệ hơn hay huấn luyện vô ích.

**Mức độ phân xử:** quyết định mô tả thăm dò dựa trên một người chấm AI, có phơi nhiễm nhãn một phần; **`INDEPENDENT_HUMAN_REVIEW=NOT_PERFORMED`**. Không ghi `SCIENCE_PASS`/`SCIENCE_FAIL` mới vào `lineage.md` từ phép chấm này.

**Quản trị:** `GPU_NEW_TRAIN=NO` · `GENERATION_NEW=NO` · `TEST=SEALED` · `Q1Q2=CONSUMED_UNCHANGED` · `PR13=HOLD` · `MAIN=UNCHANGED` · `LINEAGE=L0017_UNCHANGED`.

## 6. Bước thực hiện tiếp theo

`TTM_SMALL4M_PROMPT_ADHERENCE_ROOT_CAUSE_READONLY_DIAGNOSTIC` — rà soát read-only hợp đồng tokenization/forward parity của mẫu sinh, phân bố cấu trúc mẫu TRAIN (dạng đầu vào và đích next-token), mức độ instruction/prompt-conditioning, và lỗi rời chủ đề. Chưa đổi dữ liệu hoặc cấp GPU thêm cho đến khi có nguyên nhân khả kiểm.

## Bằng chứng

- ZIP sinh gốc: https://drive.google.com/file/d/1k0HwoT5ZCmVgGodpGAC0sri3F9fO3pD-/view
- `FROZEN_BLIND_SCORES.csv`, `BLIND_SCORES_FROZEN_RECEIPT.json`, `RUBRIC_AND_DECISION_FREEZE.json`, `UNBLINDED_SCORES_PER_PAIR.csv`, `SCOPED_FINAL_QUALITY_ADJUDICATION.json`, `POST_UNBLIND_MATERIAL_QA.json`, cùng mã kiểm toán và nguồn ZIP gốc được đóng gói kèm.
