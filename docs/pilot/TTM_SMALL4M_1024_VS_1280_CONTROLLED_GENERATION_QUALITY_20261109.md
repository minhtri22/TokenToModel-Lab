# TTM-Small-4M T4 gốc — so sánh sinh kiểm soát bước 1.024 và 1.280

Ngày: 2026-11-09. Nhánh: PR #13. Phạm vi: **thăm dò (exploratory)**, không huấn luyện, không mở TEST, không tái sử dụng Q1/Q2 đã tiêu thụ. `main` bất biến.

## Thiết lập

- Checkpoint gốc bước 1.024 SHA-256: `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- Checkpoint kế nhiệm bước 1.280 SHA-256: `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`.
- Kiến trúc P02: 3.749.376 tham số, BPE 2.048, context 256, trọng số PyTorch nạp `strict=True`, suy luận CPU. Đây là bộ chạy đối chiếu tự triển khai theo phương trình forward của P02; chưa tuyên bố parity bit-exact với chương trình P02 đã pin.
- Tokenizer T1 TRAIN-only: 1.791 phép hợp nhất, SHA-256 của danh sách token và merge `aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af`. Tệp manifest tư nhân không được xuất bản.
- 8 prompt mới tiếng Anh, 2 decoder (greedy; sampling temperature=0.8, top-k=40, top-p=0.9), cùng prompt và seed cho từng cặp 1.024/1.280, tối đa 64 token. **32 đoạn sinh thật**, không tải TEST hay input Q1/Q2.
- Đối chứng tập trung *bám prompt, mạch lạc, nhất quán*; điểm chấm mù con người chưa thực hiện. Chỉ số tự động kiểm **tên/vật thể/địa điểm đặc trưng của prompt trong phần tiếp nối** và tỉ lệ lặp 3-gram trên ID BPE mới sinh. Các anchor được định nghĩa trong báo cáo hậu nghiệm, chỉ dùng mô tả, không phải endpoint được đăng ký từ trước.

## Kết quả mô tả (KHÔNG thay thế rubric con người)

| Điều kiện | Số prompt có >= 1 anchor /8 | Trung bình 3-gram token lặp |
|---|---:|---:|
| 1.024 / greedy | 0/8 | 35,89% |
| 1.280 / greedy | 0/8 | 32,46% |
| 1.024 / sampling | 0/8 | 4,64% |
| 1.280 / sampling | 0/8 | 3,83% |

Không có dấu hiệu cải thiện bám prompt theo proxy này (0/32 đầu ra có anchor). Việc giảm lặp nhỏ không chứng minh cải thiện mạch lạc. Một số đoạn từ cả hai checkpoint thay nhân vật, cảnh và mục tiêu của prompt thành chuyện chung về cô bé/công viên/cây lớn.

Ví dụ P02: `A young fox called Lumo was afraid to cross the narrow bridge.`
- 1.024 / greedy: `One day, Mama's mom's mom and said, "I'm sorry, I can't want to be a big and you."`
- 1.280 / greedy: `One day, Mama was playing in the park with her mom. She was very happy and she saw a big tree...`

Ví dụ P05: `Pip the little robot wanted to plant a sunflower in the garden.`
- 1.024 / greedy: `I'm sorry, you can't want to play with it. I have a big, but it is a big tree...`
- 1.280 / greedy: `The little girl was very happy and she had to play with her friends...`

## Vị trí bằng chứng và QA

- [ZIP bằng chứng đầy đủ lưu riêng trên Google Drive TTM](https://drive.google.com/file/d/1k0HwoT5ZCmVgGodpGAC0sri3F9fO3pD-/view): chứa `prereg.json`, `raw.json` (32 đoạn, token IDs, seed), `analyzed.json`, `blinded_review.csv`, `blinding_key_private.json`, `QA.json`, `REPORT.md`, `manifest.json`. Không có checkpoint, tokenizer manifest tư nhân, TRAIN/VAL/TEST.
- ZIP SHA-256: `db7e327fa4a9a2badc9f7d0b79f8276ae4925513cee3750b6bd04dde45fc535c` — 21.959 byte. Google Drive metadata được đọc lại có đúng tên và kích thước; chưa băm lại byte ZIP từ Drive.
- `QA.json` ghi **PASS_19_OF_19_SCOPED_ARTIFACT_CONTRACT**, chỉ về ràng buộc vật liệu/cấu hình. Không phải QA mù chất lượng hoặc xác nhận khoa học.
- Một lần smoke kỹ thuật ban đầu có lỗi công thức residual attention khi tự triển khai nên **toàn bộ output lần đó bị loại**; đã sửa về đúng công thức của P02 trước khi chạy bộ 32 mẫu này. Không coi smoke lỗi là dữ liệu khoa học.

## Phán quyết phạm vi

`GENERATION_EXECUTED=YES` · `QUALITY_GAIN=NOT_ESTABLISHED` · `BLIND_HUMAN_RUBRIC=PENDING` · `TRAINING=NOT_EXECUTED` · `TEST=UNTOUCHED` · `Q1Q2=UNTOUCHED` · `PR13=HOLD` · `MAIN=UNCHANGED`.

Giữ kết quả VAL NLL bước 1.280 đã có, nhưng **không suy ra** chất lượng truyện tốt hơn. Chưa ghi thêm `lineage.md` cho phép đo mới vì chưa đạt phân xử chất lượng độc lập.

**Bước thực hiện tiếp theo:** đánh giá mù 16 cặp A/B trên ba tiêu chí 0–3 (bám prompt, mạch lạc, nhất quán); tách khóa giải mù cho tới khi chấm xong, rồi adjudicate `IMPROVED` / `NO_DEMONSTRATED_GAIN` / `HOLD`. Không train thêm trước quyết định này.
