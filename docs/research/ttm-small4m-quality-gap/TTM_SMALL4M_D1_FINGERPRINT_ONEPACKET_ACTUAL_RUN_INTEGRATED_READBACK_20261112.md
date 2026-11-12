# TTM-Small-4M D1 — Biên nhận thực chạy fingerprint toàn bộ DEV + neutral prior

**Ngày:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_GENERATE_NEW_CANONICAL_FINGERPRINTS_OWNER_LOCAL_ONE_SHOT_AND_ADOPT`  
**Đối chiếu:** Đọc lại `D1_PUBLIC_SAFE_SUMMARY.json` thực tế từ máy Windows; người dùng cung cấp output của trình chạy PowerShell 5.1 và SHA-256 độc lập trên máy.

## 1. Kết quả thực thi

`D1_FINGERPRINT_ONEPACKET=PASS_SCOPED`  
`TTM_D1_FINGERPRINT_READBACK=PASS_SCOPED`  
`D1_PRIVATE_INDEX_SHA256=66a987550fdeb5b6ff3711d49ab673578be68418a1978b33126f6127deed763c`  
`D1_SAFE_SUMMARY_SHA256=7f27c8f9226ff333b61e1fd08dc140424c76aef2ea5ab1f0baaf9a751739ada7`

Một lượt tạo fingerprint mới đã **chạy xong thực tế**, sau khi sửa lỗi PowerShell 5.1. Chỉ mục private được lưu tại `_tmp/TTM_D1_ONEPACKET_FINGERPRINT_20261112/D1_PRIVATE_FINGERPRINT_INDEX.json`, **không đưa lên GitHub**. Biên nhận an toàn đã sao chép từ máy vào `artifacts/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_FINGERPRINT_ONEPACKET_OWNER_SAFE_RECEIPT_20261112.json` trên nhánh nghiên cứu.

| Hạng mục | Số bản ghi |
| --- | ---: |
| D1 DEV V2 | 128 |
| D1 neutral prior | 64 |
| FRESH16 S1 đã tiêu thụ | 16 |
| CF1 DEV36, cả hai ngữ cảnh mỗi cặp | 72 |
| Q1 + FRESH12 công khai được phép | 28 |
| AC FINAL24 | 24 |
| AC DEV12 | 12 |
| **Tổng chỉ mục** | **344** |

Tất cả 192 bản ghi D1 khác nhau sau chuẩn hóa. Toàn bộ 192 được so sánh với từng nhóm 152 prompt lịch sử, thành **29.184 phép đối chiếu**.

| Nhóm nguồn | Phép so sánh | Trùng sau chuẩn hóa | Trùng 5 từ liên tiếp | Jaccard cao nhất |
| --- | ---: | ---: | ---: | ---: |
| FRESH16 | 3.072 | 0 | 0 | 0,090909 |
| CF1 | 13.824 | 0 | 0 | 0,076923 |
| Q1/FRESH12 công khai | 5.376 | 0 | 0 | 0,137931 |
| AC FINAL24 | 4.608 | 0 | 0 | 0,088235 |
| AC DEV12 | 2.304 | 0 | 0 | 0,064516 |
| **Tổng** | **29.184** | **0** | **0** | **0,137931** |

`private_flag_count=0`. Không cặp nào đạt ngưỡng sàng lọc từ vựng exploratory `Jaccard ≥ 0,18`. **0 cảnh báo không đồng nghĩa có bằng chứng chứng minh không trùng ngữ nghĩa tuyệt đối.**

## 2. Điều được sửa về quản trị bằng chứng

Trước đó D1 bị `CLOSED_PREEXEC_UNCERTIFIABLE_WITHOUT_SEALED_ACCESS` do chưa có index đủ. **Đây không còn là mô tả đúng đối với nguồn DEV và các nguồn lịch sử đã được phép đọc**: chỉ mục mới đã được tạo và được đối chiếu đầy đủ 128 DEV + 64 prior với 152 prompt nguồn. Không cần đòi chỉ mục đã được tạo từ trước hay chạy thêm các vòng tạo dấu vân tay cho chính các nguồn này.

Tuy nhiên, TEST và phần Q1Q2 ngoài tập công khai không được đưa vào bộ nguồn; chúng **vẫn giữ niêm phong**, không thể dùng các hash output hay TRAIN/VAL thay cho chứng chỉ của những prompt này. Vì vậy:

- `SCOPED_CANONICAL_FINGERPRINTS=PASS`
- `KNOWN_ALLOWED_SOURCE_EXACT_LEXICAL_OVERLAP_SCREEN=PASS_SCOPED`
- `FULL_SEALED_NONOVERLAP=NOT_CERTIFIED`
- `SCIENCE_RELEASE=HOLD_PENDING_FROZEN_PREREG_NONOVERLAP_GOVERNANCE`

Khẳng định không trùng chỉ được giới hạn trong tập nguồn được cung cấp. Không mở TEST/Q1Q2, không lấy seed/mapping từ manifest và không công khai chỉ mục private; không train hay inference.

## 3. Quyết định và lộ trình

**Kết luận được chấp nhận:** source indexing và đối chiếu D1 đã hoàn thành có chứng cứ mới, `PASS_SCOPED`. Tình trạng HOLD science không xuất phát từ lỗi fingerprint hay thiếu công cụ băm; chỉ là giới hạn phần TEST/Q1Q2 vẫn niêm phong theo hợp đồng hiện có và điều kiện quyền/độc lập rater. Không được gọi `NO_FLAGS` thành `FULL_NONOVERLAP_PASS`.

**Không cần một vòng kiểm toán fingerprint mới.** Nếu chủ dự án muốn có kết quả mô hình nhanh, lựa chọn phù hợp là **thí nghiệm DEV mang nhãn exploratory riêng**, dùng gói đã khóa và không trộn kết quả với một nghiên cứu confirmatory yêu cầu bảo đảm nonoverlap trên toàn bộ sealed sources. Việc mở một đợt khoa học mới cần ghi rõ phạm vi và quyết định GO riêng, không âm thầm thay đổi hợp đồng D1 đã khóa.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_D1_POST_FINGERPRINT_ONE_OWNER_EXPLORATORY_DEV_RUN_DECISION` — một quyết định scope GO/HOLD rõ ràng, không lặp lại các micro-gate fingerprint. Nếu giữ đúng khoa học D1 confirmatory hiện tại: tiếp tục `SCIENCE=HOLD`.

**GitHub chỉ lưu nguồn runner và biên nhận an toàn; `lineage.md` chỉ được append sau khi có kết quả khoa học thực tế đã phân xử, không ghi cho lượt QA này.**
