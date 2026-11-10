# TTM-Small-4M — tiền đăng ký phép thử định dạng prompt (post-hoc exploratory)

**Đóng băng trước khi sinh mẫu mới: 2026-11-09.** Mục tiêu: `TTM_SMALL4M_PROMPT_SERIALIZATION_CONTROLLED_ABLATION_PREREG_AND_ONE_SMALL_INFERENCE_BATCH`.

## Phạm vi đã cố định

Dùng đúng 8 prompt P01–P08 và 32 phần tiếp nối đã sinh trong phép kiểm tra chất lượng cũ; không dùng prompt mới, TEST, Q1/Q2, TRAIN, VAL; không train. Mỗi prompt cũ có **đúng một dấu cách ASCII ở cuối**; điều kiện mới **chỉ bỏ đúng dấu cách cuối đó**. So sánh 2 checkpoint gốc 1024/1280 với cùng BPE 2048, cùng giải mã greedy hoặc sampled (temperature=0.8, top-k=40, top-p=0.9), cùng seed `20261109+int(prompt_id[1:])`, tối đa 64 token mới. Tạo đúng **32** phần tiếp nối không có dấu cách; đối chiếu với **32** phần tiếp nối cũ, không tái sinh cũ.

## Tiêu chí đánh giá được khóa trước thực thi

**Chính (thăm dò):** Số phần tiếp nối có ít nhất một từ khóa đặc trưng trong prompt, so sánh `clean - original` qua 32 cặp, cũng như riêng từng checkpoint và decoder. Danh sách từ khóa từ `analyzed.json` cũ được giữ nguyên:

- P01: nora, bell, chair
- P02: lumo, fox, bridge
- P03: sam, pears, grandmother
- P04: eva, hat, river
- P05: pip, robot, sunflower, garden
- P06: max, june, clock, repair
- P07: lina, map, library, book
- P08: rabbit, lantern, cabin

So từ không phân biệt hoa/thường với ranh giới từ. Chỉ chấm phần sinh ra, không chấm lại prompt. **Phụ (mô tả):** token đầu là newline ID10, phân bố token đầu, lặp 3-gram trên BPE IDs, EOS sớm, lỗi UTF-8, ví dụ text; không dùng chỉ số phụ để định nghĩa thành công sau kết quả.

`ABALATION_POSITIVE_LEXICAL` nếu số phần có >=1 từ khóa **tăng** so với baseline, `NO_LEXICAL_ADHERENCE_GAIN` nếu không tăng, `HOLD` nếu thất bại bất kỳ QA hoặc không đủ 32 mẫu. Đây chỉ là kết luận **lexical** và hậu nghiệm, không phải chứng minh cải thiện ngữ nghĩa hoặc khả năng khái quát hóa. Kết quả thẩm định mù 1024/1280 trước đây vẫn là phép thử riêng.

## Các ghim bất biến

- Bản tiền đăng ký JSON gốc ở môi trường thực thi: SHA-256 **`b32e8f322e1a067271690fe181aed7ba1ec4bc9735d527209db9174bdadc719a`**, được tạo và kiểm SHA trước commit này.
- 32 mẫu cũ `raw.json`: `8c9cb99dcfd6e0f6eb507552c9bbcf6b0acfbf2d98d798a99c1e6358ea62cd2e`.
- Checkpoint 1024: `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- Checkpoint 1280: `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`.
- Tokenizer merge manifest SHA-256: `aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af`; source P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`.

Trạng thái tại freeze: **`NEW_INFERENCE=NOT_YET_EXECUTED`**. Không ghi science mới vào `lineage.md` trước phân xử; PR #13 vẫn HOLD và `main` không đổi.
