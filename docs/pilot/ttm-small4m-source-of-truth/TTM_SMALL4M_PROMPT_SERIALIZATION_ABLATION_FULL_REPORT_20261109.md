# TTM-Small-4M — Ablation bỏ dấu cách cuối prompt (thăm dò hậu nghiệm)

**Ngày:** 2026-11-09  ·  **Nhiệm vụ:** `TTM_SMALL4M_PROMPT_SERIALIZATION_CONTROLLED_ABLATION_PREREG_AND_ONE_SMALL_INFERENCE_BATCH`  ·  **Quyết định:** `ABALATION_POSITIVE_LEXICAL_ONLY / SEMANTIC_ADHERENCE_NOT_ESTABLISHED`.

## Thứ tự và khóa thực thi

- Tiền đăng ký (preregistration) đã **commit lên PR #13 trước khi sinh bất cứ mẫu mới nào**, Git commit `fb5699857e435efb85c20e1be6baa7a206bb835e`. Bản JSON local SHA-256 `b32e8f322e1a067271690fe181aed7ba1ec4bc9735d527209db9174bdadc719a`.
- Bằng chứng đối chứng bất biến: 32 mẫu cũ `raw.json` SHA-256 `8c9cb99dcfd6e0f6eb507552c9bbcf6b0acfbf2d98d798a99c1e6358ea62cd2e` (không tái sinh); 32 mẫu mới sau khi chỉ bỏ đúng một ASCII space có SHA-256 `eaa98bb4b1da6079513d96a73a23ea33a30fe43df0e736806a9294fa47530021`. Claim one-shot được tạo trước khi sinh và không cho tự chạy lại.
- Checkpoint gốc 1024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; 1280 SHA-256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; BPE-2048 gốc merge SHA-256 `aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af`; mã P02 đúng blob `9762343e06cf800b50574c2871ae1ed58537fb18`.
- 8 prompt gốc P01–P08, hai checkpoint, hai bộ giải mã: greedy và sampled (temperature 0,8; top-k 40, top-p 0,9), seed `20261109 + số prompt`, tối đa 64 BPE token; **32 mới** không cần GPU và **32 cũ** làm đối chứng. Không train, không dùng TEST, Q1/Q2, TRAIN, VAL và không tạo prompt mới.

## Chỉ số đã đóng băng trước khi sinh

Tiêu chí chính: *bất kỳ từ khóa đặc trưng nào trong phần tiếp nối* theo chính danh sách 8 nhóm từ đã dùng trong `analyzed.json` trước đó; tìm từ không phân biệt hoa thường và có ranh giới từ. Đây chỉ là proxy lexical, **không phải điểm đánh giá ngữ nghĩa**.

| Checkpoint | Decoder | Anchor hit trước /8 | Anchor hit sau /8 | Xuống dòng token đầu trước → sau | EOS sớm trước → sau | Lặp 3-gram trước → sau |
|---:|---|---:|---:|---:|---:|---:|
| 1024 | greedy | 0/8 | 1/8 | 8/8 → 0/8 | 0/8 → 2/8 | 35.89% → 29.84% |
| 1024 | sampled | 0/8 | 1/8 | 7/8 → 0/8 | 0/8 → 1/8 | 4.64% → 3.23% |
| 1280 | greedy | 0/8 | 0/8 | 8/8 → 0/8 | 0/8 → 2/8 | 32.46% → 39.00% |
| 1280 | sampled | 0/8 | 1/8 | 6/8 → 0/8 | 0/8 → 1/8 | 3.83% → 1.81% |

**Tổng số cặp:** 0/32 → 3/32 đoạn nhắc lại ít nhất một chi tiết; token đầu là newline 29/32 → 0/32; EOS sớm 0/32 → 6/32. Riêng checkpoint 1024 có 2/16 lexical hits sau sửa, checkpoint 1280 có 1/16. Sáu mẫu EOS sớm làm độ dài mẫu không đồng đều: so sánh độ lặp cần diễn giải cẩn thận, và không nên coi giảm lặp là tăng chất lượng.

## Kiểm tra ngữ nghĩa bằng ví dụ (mô tả hậu nghiệm)

- P03, 1024/sampled: có nhắc `Sam` nhưng bỏ mất ba quả lê và người bà, chuyển sang món đồ chơi/xe; không xem đây là giữ được sự kiện lõi.
- P05, 1024/greedy: nhắc `garden` nhưng bỏ robot Pip, hoa hướng dương và mục tiêu trồng hoa; lặp `garden` và chuyển sang cây/công viên.
- P05, 1280/sampled: nhắc `garden` nhưng chủ thể đổi thành `She` và câu chuyện chuyển sang rừng/ông bà, không thực hiện tiếp tình huống của Pip.
- P02, 1280/greedy sau sửa vẫn chuyển từ Lumo/cáo/cầu thành `He ... friends` rồi Tom/Lily và lời xin lỗi lặp. Không có cải thiện semantic adherence rõ ràng trên ví dụ này.

## Kết luận và giới hạn

**Đã xác nhận:** thay đổi đúng một dấu cách cuối làm đảo mạnh token đầu; toàn bộ 32 mẫu mới không còn bắt đầu bằng newline. Chỉ số lexical có **tín hiệu tăng nhỏ 3/32**, đạt điều kiện `ABALATION_POSITIVE_LEXICAL` đã khóa trước thực thi.

**Chưa chứng minh:** khả năng giữ nhân vật, vật thể và trình tự nhân quả tốt hơn; chất lượng checkpoint 1280 hơn 1024 sau sửa; ý nghĩa thống kê/khái quát hóa ngoài tám prompt. Các từ khóa đơn lẻ có thể trùng ngẫu nhiên trong câu chuyện khác, và các prompt đã được dùng trong thí nghiệm cũ nên **không được xem là kiểm định xác nhận độc lập**. Không có đánh giá mù đa reviewer đối với 32 đoạn mới.

**Quan sát phụ:** 6/32 EOS sớm sau sửa (0/32 trước sửa), do đó chuẩn hóa prompt cũng có thể ảnh hưởng đến chiều dài và tính trọn vẹn; cần đo và không che giấu. Các điều kiện không khác biệt về checkpoint/decoder/seed/max tokens nhưng trạng thái RNG qua những token khác nhau làm tiếp nối khác nhau, không có ghép cặp token từng bước.

## QA, bảo quản bằng chứng và ranh giới

- Kiểm toán độc lập trên mã nguồn khác runner: **PASS_42_OF_42_SOURCE_MATERIAL_AND_ARITHMETIC**, gồm SHA-256, khóa prereg, claim, nguyên bản 32 mẫu, đủ 32 đầu ra mới, seed, token hợp lệ, chỉnh đúng 1 dấu cách, tính lại metric, cả negative test của regular expression. **QA kỹ thuật, không phải QA chấm chất lượng bởi con người.**
- Dữ liệu riêng tư giữ nguyên: không công bố hai checkpoint, các bảng hợp nhất BPE riêng tư, gói TRAIN/VAL hoặc TEST. Đầu ra 32 mới và khóa so sánh chỉ nằm trong ZIP bằng chứng của người sở hữu, không commit lên GitHub.
- GitHub PR #13 giữ DRAFT / HOLD. `main` và `lineage.md` (L0017) không bị thay đổi. Chưa có scientific PASS/FAIL mới đủ điều kiện ghi vào lineage.

### Bước thực hiện tiếp theo

`TTM_SMALL4M_POSTHOC_ABLATION_SEMANTIC_REVIEW_AND_NEXT_DATA_DECISION` — chỉ đọc và đánh giá mù 16 cặp cũ/mới theo cùng rubric 0–3, chú ý chủ thể, sự kiện và quan hệ nhân quả. Nếu muốn tuyên bố cải thiện ngoài mẫu, xây dựng bộ prompt mới chưa đánh giá với reviewer độc lập; không huấn luyện thêm trước quyết định này.
