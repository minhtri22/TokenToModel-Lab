# TTM-Small-4M — hậu kiểm chấm mù 32 cặp & quyết định dữ liệu
Ngày 2026-11-09. Nhánh PR #13. Phạm vi: `TTM_SMALL4M_POSTHOC_ABLATION_SEMANTIC_REVIEW_AND_NEXT_DATA_DECISION`.

## Thiết kế và dấu thời điểm
- 32 cặp gốc/bỏ dấu cách (8 prompt × checkpoints 1024,1280 × decoders greedy,sampled); 64 đầu ra đã sinh từ lượt trước. **Không sinh thêm**, không TRAIN/TEST/Q1Q2.
- Một lượt chấm **AI đơn lẻ**, ba chiều 0–3: bám prompt (prompt adherence), mạch lạc (coherence), nhất quán (consistency).
- Trước giải mù, SHA-256 phiếu `AI_BLIND_SCORES_FROZEN.csv`: `748acd55fa064f70c68af1f08fdda78b2e1c370969a8549b9da9eaf0f752037a`; rubric SHA `61705dac08df2c4458eb37e1fd9530d75a2efa11bec0a85f7f63640a5aaabad3`. Đã ghi dấu trên GitHub tại commit `2424f4d91365db142e9665a9c686978387e2dbc4` trước khi đọc key.
- Dữ liệu sinh cũ SHA `8c9cb99dcfd6e0f6eb507552c9bbcf6b0acfbf2d98d798a99c1e6358ea62cd2e`; mới SHA `eaa98bb4b1da6079513d96a73a23ea33a30fe43df0e736806a9294fa47530021`; 32/32 cặp được đối chiếu lại với văn bản nguồn.
- Lưu ý: rubric đã khóa trước **giải mù**, nhưng không phải giao thức khoa học đăng ký trước khi thấy dữ liệu đầu ra; đây là đánh giá hậu nghiệm (post-hoc).

## Điểm AI (mô tả, không phải kiểm chứng độc lập)

| Tiêu chí (0–3) | Gốc có dấu cách | Bỏ dấu cách | Δ |
|---|---:|---:|---:|
| Bám prompt | 0.000 | 0.094 | +0.094 |
| Mạch lạc | 0.281 | 0.656 | +0.375 |
| Nhất quán | 0.188 | 0.438 | +0.250 |
| **Tổng (0–9)** | **0.469** | **1.188** | **+0.719** |

Bỏ dấu cách thắng **17/32**, thua **7/32**, hòa **8/32**. Δ tổng: checkpoint 1024 **+1.000**, checkpoint 1280 **+0.438**; greedy **+0.750**, sampled **+0.688**. Tái lấy mẫu theo 8 cụm prompt (10.000 lần), CI95 mô tả cho Δ tổng **[+0.313, +1.188]**. Không diễn giải đây là CI cho tổng thể hoặc độ tin cậy của một người chấm.

## Rủi ro phương pháp phát hiện sau giải mù

**Kiểm toán vật liệu và số học: PASS 16/16; kiểm toán thiết kế mù: KHÔNG ĐẠT CÂN BẰNG.**
- Trong **24/32 cặp**, bản bỏ dấu cách ở cột A; chỉ **8/32** cặp đặt bản gốc ở A. Điểm trung bình cột A = **1.125/9** trong khi B = **0.531/9**. Nguy cơ **thiên lệch vị trí (position bias)** không thể loại trừ.
- Δ tổng khi bản bỏ dấu cách ở A = **+0.875**; khi bản gốc ở A chỉ **+0.250**. Không tự ý chấm lại sau giải mù.
- Downstream semantic rating **không thực sự mù hoàn toàn** vì newline đầu gốc có thể bộc lộ điều kiện. Một số văn bản đã được thảo luận ở lượt trước; chỉ có **một AI chấm**, không có giám khảo độc lập hay đồng thuận liên đánh giá.
- Các đoạn được cải thiện về mạch lạc cục bộ vẫn **không tiếp nối đúng nhân vật, vật thể và nhiệm vụ**; bám prompt đạt 0.094/3 điểm sau sửa. 6/32 đầu ra mới dừng sớm bằng EOS, gây nhiễu về độ dài. 8 prompt đều đã từng được xem xét.
- Sensitivity loại P02/P05: 24 cặp, Δ tổng +0.958, nhưng vẫn không sửa được lỗi thiên lệch A/B hoặc việc dùng prompt cũ.

**Phán quyết:** `SEMANTIC_GAIN_INDICATIVE_NOT_CONFIRMED`. Bằng chứng ủng hộ lợi ích định dạng ở mức ban đầu, nhưng **không đủ để chấp nhận cải thiện bám prompt về ngữ nghĩa** hoặc kết luận bước 1280 hơn 1024.

## Quyết định dữ liệu / mô hình

1. **Không tiếp tục huấn luyện lúc này**, không bổ sung epoch trên tập 2.048 truyện TRAIN đã lặp lại nhiều lần, không thay tokenizer hay kiến trúc P02 và không sửa các checkpoint khóa.
2. **Chấp nhận chuẩn hóa dấu cách cuối** như một biện pháp xử lý đầu vào cho các phép đánh giá *mới*, không hồi tố chấm lại Q1/Q2 đã tiêu thụ.
3. Mở một giao thức mới với **12 prompt hoàn toàn chưa dùng**, mỗi prompt thử gốc/trimmed ở cả checkpoint 1024/1280, greedy thống nhất (48 phần tiếp nối), **24 cặp A/B cân bằng 12/12**; giấu các dấu hiệu định dạng đầu khi chấm nội dung và mời người chấm độc lập. Không tự nhận confirmatory science PASS nếu thiếu người chấm độc lập.
4. Chỉ nếu vẫn thiếu khả năng bám prompt trên bộ mới mới xem xét nghiên cứu can thiệp dữ liệu TRAIN, thay đổi nhiệm vụ/học tiếp nối hoặc mở rộng ngân sách; phải có đối chứng mới và phê duyệt phù hợp. Đây là đề xuất chưa thực thi.

## Custody / QA
- Báo cáo đầy đủ và toàn bộ phiếu chấm/khóa riêng tư cùng 32+32 đoạn gốc nằm trong ZIP lưu riêng, **không đưa văn bản sinh thô hoặc key lên GitHub công khai**.
- ZIP SHA-256 `b7ddd93ee8c02adffb9db4d7b63ecfdc3d76298050dfbfa64617520627934c7c` (42.323 bytes), manifest SHA-256 `5fac5f3d9f97050def0980346b3e401c41ab5b183adb8104bf17d23d3ef77416`.
- Markdown đầy đủ SHA-256 `8b887fdc11fe632b72bcd12a84f86a20704f1f6449e622dd3e7e15ace0895e5b`, material QA 16/16 PASS, `RANDOMIZATION_BALANCE=FAIL_24_A_TRIMMED_VS_8_A_ORIGINAL`.
- `NO_NEW_TRAINING` · `NO_NEW_GENERATION` · `TEST=UNTOUCHED` · `Q1Q2=UNTOUCHED` · `MAIN=UNCHANGED` · `PR13=HOLD` · `LINEAGE=L0017_UNCHANGED`.

## Bước thực hiện tiếp theo
`TTM_SMALL4M_FRESH_12_PROMPT_BALANCED_BLIND_INFERENCE_PREREG_AND_REVIEW_READINESS`: soạn và đóng băng prompt mới/rubric và khóa reviewer độc lập; chưa huấn luyện, chưa sinh mẫu mới khi thiết kế chưa được khóa.
