# TTM-Small-4M — Chấm mù thăm dò 32 cặp bản gốc/bỏ dấu cách và quyết định dữ liệu

**Ngày:** 2026-11-09 · **Task:** `TTM_SMALL4M_POSTHOC_ABLATION_SEMANTIC_REVIEW_AND_NEXT_DATA_DECISION` · **Kết luận:** `SEMANTIC_GAIN_INDICATIVE_NOT_CONFIRMED` · **Chốt dữ liệu:** `NO_DATA_REWRITE_OR_NEW_TRAINING_NOW`.

## 1. Nguồn và khóa điểm trước khi giải mù

- Dữ liệu gốc 32 đầu ra: SHA-256 `8c9cb99dcfd6e0f6eb507552c9bbcf6b0acfbf2d98d798a99c1e6358ea62cd2e`.
- Dữ liệu bỏ đúng 1 dấu cách cuối: 32 đầu ra, SHA-256 `eaa98bb4b1da6079513d96a73a23ea33a30fe43df0e736806a9294fa47530021`.
- 8 prompt × 2 checkpoint gốc (1024,1280) × 2 decoder (greedy, sampled): 32 cặp A/B, **64 đoạn văn và 192 điểm thành phần**. Không dùng TEST hay Q1/Q2.
- Mã nguồn P02 và BPE, checkpoint nguồn đã pin ở báo cáo phép thử trước. Không huấn luyện hoặc sinh thêm token trong bước đánh giá này.
- Phiếu chấm AI được khóa **trước khi đọc bảng giải mù**: `AI_BLIND_SCORES_FROZEN.csv` SHA256 `748acd55fa064f70c68af1f08fdda78b2e1c370969a8549b9da9eaf0f752037a`; rubric SHA256 `61705dac08df2c4458eb37e1fd9530d75a2efa11bec0a85f7f63640a5aaabad3`; ảnh danh mục chấm A/B SHA256 `fec7427b75fcf52eeb82e563f9571a31d463724e299d7119c6c33f3087a2827d`. Dấu khóa được commit trên GitHub PR#13 trước khi giải mù: xem biên bản `TTM_SMALL4M_POSTHOC_SEMANTIC_REVIEW_PRE_UNBLIND_SCORE_LOCK_20261109.json`.
- Mỗi điều kiện/đoạn được chấm 0–3 ở **bám prompt (prompt adherence), mạch lạc (coherence), nhất quán (consistency)**, tổng 0–9. Điểm được đánh giá theo phần tiếp nối, không cộng điểm chỉ vì bớt xuống dòng đầu.

## 2. Kết quả sau giải mù

| Tiêu chí | Gốc có dấu cách | Bỏ dấu cách | Chênh lệch |
|---|---:|---:|---:|
| Bám prompt (0–3) | 0,000 | 0,094 | +0,094 |
| Mạch lạc (0–3) | 0,281 | 0,656 | +0,375 |
| Nhất quán (0–3) | 0,188 | 0,438 | +0,250 |
| **Tổng (0–9)** | **0,469** | **1,188** | **+0,719** |

Bỏ dấu cách thắng **17/32**, thua **7/32**, hòa **8/32**.

| Nhóm | Số cặp | Điểm tổng gốc | Điểm tổng bỏ dấu cách | Δ |
|---|---:|---:|---:|---:|
| Checkpoint 1024 | 16 | 0,250 | 1,250 | +1,000 |
| Checkpoint 1280 | 16 | 0,688 | 1,125 | +0,438 |
| Decoder greedy | 16 | 0,625 | 1,375 | +0,750 |
| Decoder sampled | 16 | 0,312 | 1,000 | +0,688 |

Tái lấy mẫu theo cụm 8 prompt, 10.000 lượt (mô tả, không phải khoảng tin cậy độc lập theo người chấm): chênh điểm tổng CI95 [0,312; 1,188]. Giữ nguyên trường hợp P02/P05 từng xuất hiện nhãn trong hội thoại; phân tích độ nhạy loại toàn bộ hai nhóm chỉ để minh họa, còn **24 cặp**, Δ tổng 0,958.

## 3. Phân xử hạn chế phương pháp — quan trọng

- **Chỉ có một người chấm AI**, không có giám khảo con người độc lập, không có liên đánh giá (inter-rater reliability). Kết quả **không** chứng minh chất lượng mô hình theo chuẩn xác nhận.
- Hoán vị A/B **không cân bằng: 24/32 cặp** đặt điều kiện bỏ dấu cách ở cột A và **8/32** đặt bản gốc ở cột A. Cột A đạt trung bình `1,125/9`, cột B `0,531/9`. Đây là **thiết kế có nguy cơ thiên lệch vị trí**, không được che giấu bằng QA số học.
- Trong nhóm điều kiện bỏ dấu cách nằm cột A, Δ tổng là +0,875. Trong nhóm điều kiện bản gốc nằm cột A, Δ còn +0,250. Không thể xem hai nhóm khác nhau là ước lượng nhân quả độc lập.
- Nhiều đầu ra gốc có newline đầu tiên, nên có thể nhận biết điều kiện thông qua hình thức; **mù chỉ là che nhãn, không mù hoàn toàn**.
- Điểm bám prompt sau chỉnh **0,094/3**, cho thấy không giữ được nhân vật/mục tiêu truyện. Ba từ khóa tìm thấy trong phép thử trước không thể hiện bám sát diễn biến ngữ nghĩa. Ngoài ra 6/32 mẫu bỏ dấu cách kết thúc sớm EOS (0/32 ở bản gốc), là yếu tố nhiễu về độ dài.
- Tất cả 8 prompt đã được dùng để phát hiện vấn đề ban đầu. Phân tích hậu nghiệm **không dùng để lựa chọn khoa học xác nhận**.

**Kiểm toán vật liệu/số học:** `PASS_SCOPED_MATERIAL_AND_ARITHMETIC`, **16/16** điều kiện. **Kiểm toán thiết kế:** `FAIL_UNBALANCED_24_VS_8`, không cấp quyền gọi là independent semantic PASS.

## 4. Quyết định hướng dữ liệu/huấn luyện

1. **Giữ nguyên checkpoint, TRAIN, tokenizer, kiến trúc P02 và hai kết quả NLL đã khóa. Không huấn luyện thêm hoặc thay dữ liệu trong bước này.** Việc tiếp tục 256 bước đã giảm NLL nhưng phép đo bám prompt tuyệt đối vẫn rất thấp.
2. **Chuẩn hóa định dạng prompt cho các thử nghiệm mới:** không đưa dấu cách ASCII rời ở cuối, vẫn phải đối chiếu đúng BPE/seed/cấu hình. Đây là điều kiện đánh giá, không phải sửa checkpoint.
3. **Trước khi cân nhắc thay đổi dữ liệu, cần kiểm tra ngoài mẫu mới (fresh prompts):** đề xuất 12 prompt mới chưa dùng trong Q1/Q2, TEST hoặc các lượt trước, dùng 2 checkpoint, greedy và cặp original/trimmed (48 đoạn nếu 12×2×2). Tiền đăng ký rubric và danh sách prompt trước thực thi, **A/B cân bằng 12/12**, chuẩn hóa hiển thị newline đầu để tránh lộ điều kiện, mời một người chấm độc lập thực sự. Đây là đề xuất, **chưa thực thi**.
4. Nếu vẫn bám prompt thấp, mở một thiết kế can thiệp dữ liệu riêng trên TRAIN mới hoặc cách tạo nhiệm vụ tiếp nối (instruction-style / entity-continuation), nhưng phải kiểm soát ngân sách, quyền nguồn, và thiết kế đối chứng; **không tự động thêm epoch trên 2.048 truyện đã lặp lại ~10,5×**.

**Phán quyết:** `SEMANTIC_GAIN_INDICATIVE_NOT_CONFIRMED` · `DATA_CHANGE=HOLD` · `TRAINING=NO` · `TEST=UNTOUCHED` · `Q1Q2=UNTOUCHED` · `PR13=HOLD` · `MAIN=UNCHANGED` · `LINEAGE=L0017_UNCHANGED`.

## Bước thực hiện tiếp theo

`TTM_SMALL4M_FRESH_12_PROMPT_BALANCED_BLIND_INFERENCE_PREREG_AND_REVIEW_READINESS` — chỉ lập và khóa hợp đồng kiểm định mới, không chạy huấn luyện; chuẩn bị chấm độc lập. Nếu không có giám khảo độc lập, đánh dấu HOLD chất lượng xác nhận thay vì tự khẳng định PASS.
