# TTM-Small-4M — FRESH12: tiền đăng ký và sẵn sàng phản biện

**Ngày khóa thiết kế:** 2026-11-09. **Phạm vi:** `TTM_SMALL4M_FRESH_12_PROMPT_BALANCED_BLIND_INFERENCE_PREREG_AND_REVIEW_READINESS`. **GitHub PR #13** là nguồn sự thật (source of truth) của protocol, metadata, source QA và kết quả; Drive/private chỉ giữ những dữ liệu cần bảo mật.

## 1. Dữ liệu thí nghiệm được đóng băng, nhưng CHƯA thực thi

- **12 prompt mới F01–F12** tự soạn để đánh giá tiếp nối truyện tiếng Anh. Chỉ kiểm tra khác **8 prompt P01–P08** đã dùng trước đây, không đọc lại Q1/Q2 V1/V2 hoặc TEST; chưa được chứng minh tuyệt đối chưa có trùng với mọi lịch sử TTM.
- 2 checkpoint gốc T4: **step1024** SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; **step1280** SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`.
- P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, tokenizer BPE 2048 merge SHA256 `aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af`.
- **Chỉ greedy/argmax**, không sampling; **64 token tối đa**, EOS=256, context=256. Seed ghi nhận theo `20261109 + int(Fxx[1:])` cho cả hai checkpoint/điều kiện, dù greedy là deterministic. Hai điều kiện: `BASELINE_FINAL_ASCII_SPACE` = văn bản clean + **đúng 1 dấu cách U+0020**; `TRIMMED` = clean text không dấu cách cuối. Không điều chỉnh dấu câu, từ ngữ hay model.
- Khi được mở, thực hiện **48** tiếp nối mới = 12 prompt × 2 checkpoint × 2 điều kiện, tạo **24 cặp đối chiếu**. Tất cả đều mới, không dùng lại 32 đoạn cũ để đánh giá chất lượng này.

**Tài liệu gốc chuẩn xác của 12 prompt, checksum từng prompt và lịch cặp công khai:** [JSON tiền đăng ký chính thức](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_PUBLIC_PREREG_GITHUB_CANONICAL_20261109.json).

## 2. Cân bằng A/B và bảo vệ giải mù

- A chứa điều kiện trimmed trong đúng **12/24** cặp; baseline chiếm A **12/24**.
- **Từng checkpoint** có **6/12** A=trimmed và **6/12** A=baseline.
- Với cùng prompt, A/B đảo vị trí giữa checkpoint 1024 và 1280, tránh nhầm hiệu ứng checkpoint với hiệu ứng vị trí.
- Hạt giống phân bổ do bộ tạo số ngẫu nhiên an toàn sinh ra; sắp hạng prompt bằng `HMAC_SHA256(seed, "BALANCE:"+id)`, chọn 6 ID đầu làm A=trimmed ở step1024, đảo ở step1280.
- SHA256 ánh xạ gốc riêng tư: `ed22d6fc6d2075a7d7aedb1512aba9ae4034b95dd39fbe9c5c4a5c86a4aad9ed`. [Bản escrow **mã hóa** trên GitHub](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_ENCRYPTED_BLIND_SEED_ESCROW_20261109.json) dùng AES-256-GCM và được giải mã **sau khi** người đánh giá nộp điểm, niêm phong SHA256. **Tuyệt đối không commit key giải mã hay A/B plaintext vào repository công khai.**

## 3. Người chấm độc lập (independent reviewer) — ĐIỀU KIỆN CÒN THIẾU

Tại thời điểm khóa thiết kế, **PR #13 không có review GitHub nào; chưa có người chấm độc lập được định danh/nhận trách nhiệm**. Do đó `REVIEWER_READINESS=HOLD`, `INFERENCE=NOT_EXECUTED`.

Người chấm cần đáp ứng:

1. Không phải người tạo 12 prompt, chọn checkpoint hoặc triển khai bộ sinh; không được xem key/map hoặc kết quả thô có nhãn trước khi hoàn tất đánh giá.
2. Đọc rubric **0–3** ba chiều cho **từng văn bản**: bám prompt (prompt adherence), mạch lạc (coherence), nhất quán (consistency). Chỉ chấm nội dung tiếp nối, không cộng/trừ điểm cho định dạng xuống dòng ban đầu. Dừng sớm EOS có thể làm mất phát triển truyện thì chấm theo thiếu hụt nội dung.
3. Chỉ nhận reviewer packet sau suy luận gồm prompt, text A/B đã **chuẩn hóa khoảng trắng ở đầu để giảm lộ điều kiện**, pair_id, không có checkpoint/condition labels; không có token IDs, NLL, seed giải mù, kết quả thử trước.
4. Nộp file CSV theo [mẫu khóa](../../../artifacts/qa/ttm-original1280/fresh12/REVIEWER_SCORE_TEMPLATE_20261109.csv), điền đủ 24 cặp × hai văn bản × ba tiêu chí = **144 điểm nguyên 0–3**, kèm biên bản xác nhận độc lập. SHA-256 CSV và ghi nhận nộp điểm lên GitHub **trước khi giải mù**.
5. Khi đã niêm phong điểm mới sử dụng key giải mã riêng để tính chênh lệch. Người chấm không phải ChatGPT trong hội thoại này. Nếu người chấm là một AI độc lập thay vì con người, phải ghi đúng danh tính mô hình và giới hạn của nó; không tự xưng phản biện bởi con người.

Đây là thí nghiệm trên prompt mới **trong phạm vi pilot**, không có thẩm quyền tái sử dụng TEST. Việc định dạng đầu có thể tự tiết lộ điều kiện dù đã normalize: chỉ gọi `BLINDED_TO_LABELS_WITH_RESIDUAL_CUE_RISK`, không tự nhận double-blind.

## 4. Rubric khóa

| Tiêu chí (0–3) | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Bám prompt | Bỏ các thành phần xác định | Giữ 1 chi tiết nhưng bỏ nhiệm vụ | Giữ vài thành phần, tiếp nối phần nào | Giữ nhân vật, vật, mục tiêu và diễn tiến phù hợp |
| Mạch lạc | Đoạn rời/rối | Vài câu hiểu được, khó liên kết | Sự kiện phần lớn nối nhau | Tiếp nối rõ và tiến triển |
| Nhất quán | Đổi chủ thể hoặc mâu thuẫn | Liên tục một phần, nhiều lỗi | Chủ thể/sự kiện khá ổn định | Ổn định nhân vật, cảnh và sự kiện |

Điểm mỗi trục chấm độc lập; không tự động quy đổi chỉ số từ khóa (lexical proxy) thành bám prompt ngữ nghĩa. Dùng **điểm trung bình chênh lệch bám prompt trimmed − baseline** làm mục tiêu chính. Ngưỡng dự kiến để ứng viên cải thiện: Δ trung bình ≥0,5/3; trimmed thắng rõ về adherence ≥16/24; Δ adherence từng checkpoint ≥0; Δ coherence và consistency mỗi trục ≥−0,25; bootstrap cụm 12 prompt CI95 thấp hơn phải >0; đồng thời có bản chấm độc lập hợp lệ. Ngưỡng và giới hạn này đã nằm trong JSON ghim **trước inference**.

## 5. Cổng kết thúc hữu hạn

- `PASS_AUTHOR_STATIC_READINESS`: 12 prompt độc nhất trong pilot, đúng BPE, clean/baseline khác đúng một dấu cách, 24 cặp cân bằng, source/checkpoint ghim.
- `HOLD_INDEPENDENT_REVIEWER_NOT_IDENTIFIED`: hiện chưa có người chấm và không có phiếu độc lập.
- `NEW_INFERENCE=0/48`, `NEW_TRAINING=0`, `TEST_READS=0`, `Q1Q2_READS=0`.
- Khi người chấm xác nhận phạm vi, thực thi **một** batch 48 continuation và niêm phong raw output; gửi packet đã ẩn nhãn; khóa 144 điểm; mở khóa mapping; kiểm toán/phán quyết.
- Không chuyển sang thay TRAIN/tokenizer/kiến trúc, cũng không tăng GPU budget khi chưa phân xử kết quả này.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_FRESH12_INDEPENDENT_REVIEWER_ATTESTATION_THEN_SINGLE_BATCH_INFERENCE`. Mọi thay đổi hợp đồng sau commit này đều phải thể hiện bằng amendment mới, không sửa lịch gốc.

`PR13=HOLD` · `MAIN=UNCHANGED` · `LINEAGE=L0017_UNCHANGED`.
