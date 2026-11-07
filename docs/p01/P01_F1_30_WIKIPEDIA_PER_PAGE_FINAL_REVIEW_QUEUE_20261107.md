# TTM P01 — F1-VI-GENERAL-01: chốt kỹ thuật, chưa chốt quyền từng trang

Ngày 07/11/2026. Biên bản nguồn chính xác: `TTM_P01_F1_V3_INDEPENDENT_RIGHTS_PII_AUDIT_UTF8_RECOVERY_V2_20261107.json` (SHA-256 `6e373ffe6e6340c633b52a45035abbe41836ba8a341afa1dd279ba1fd5d68cf3`, Git blob `8f52e67d4b4dc86570c467bed9b67bb2cee0afe3`).

## Kết luận có căn cứ

- 40/40 cặp nguồn/văn bản được checker độc lập xác minh SHA; 40 group H03 ứng viên không trùng; 0 regex PII và 0 copyright cue trên dữ liệu đã quét.
- 30 bài Wikipedia đều có revision ID và URL lịch sử ghi công; chúng tạo đúng 30 nhóm H03 độc lập, tổng 1422683 byte văn bản; 10 Wikisource dự phòng với 176376 byte.
- Đây **không phải F1=ALLOW**. Kiểm tra ngoại lệ trích dẫn/nhập ngoài giấy phép và PII trên đúng revision từng trang vẫn là cổng bắt buộc; kiểm toán regex không thay việc này.
- Đề nghị chỉ xét 30 Wikipedia làm F1 chính. Wikisource giữ HOLD vì bản quyền tác phẩm/bản dịch/biên tập, không đưa vào TRAIN.

## Điều kiện per-page cần ghi trên hồ sơ

Với từng revision gốc: (1) giấy phép văn bản chính CC BY-SA 4.0/ngoại lệ, (2) nội dung bên thứ ba/trích dẫn được cấp phép hoặc được loại, (3) xem xét PII thực chất, (4) URL lịch sử + yêu cầu ghi công và share-alike theo phạm vi áp dụng. Nếu trang không đạt, ghi FAIL/HOLD cho trang đó; không tuyên bố còn 30 nhóm nếu loại bất kỳ trang Wikipedia và không nhận thêm Wikisource đủ quyền.

Tham chiếu: https://foundation.wikimedia.org/wiki/Terms_of_Use ; https://creativecommons.org/licenses/by-sa/4.0/ .

## 30 Wikipedia có SHA cố định — per-page review pending

| ID | Trang | Revision | SHA văn bản (đầu 12) | Nguồn lịch sử | Quyền / PII |
|---|---|---:|---|---|---|
| WP006 | Hội An | 75654046 | `827197ef4d3f` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Phố_cổ_Hội_An&action=history) | HOLD_PER_PAGE |
| WP008 | Đồng bằng sông Cửu Long | 75642271 | `8a0054a57b1f` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Đồng_bằng_sông_Cửu_Long&action=history) | HOLD_PER_PAGE |
| WP011 | Địa lý Việt Nam | 75108045 | `678dc21b195b` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Địa_lý_Việt_Nam&action=history) | HOLD_PER_PAGE |
| WP012 | Khí hậu Việt Nam | 75660280 | `6be7d4e14f4c` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Khí_hậu_Việt_Nam&action=history) | HOLD_PER_PAGE |
| WP016 | Phú Quốc | 75641049 | `6e1d5ccb1913` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Phú_Quốc&action=history) | HOLD_PER_PAGE |
| WP017 | Sa Pa | 75216552 | `1e0891069302` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Sa_Pa&action=history) | HOLD_PER_PAGE |
| WP021 | Lịch sử Việt Nam | 75667370 | `01f1ca7625ea` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Lịch_sử_Việt_Nam&action=history) | HOLD_PER_PAGE |
| WP022 | Nhà Trần | 75660286 | `75e91f34212d` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Nhà_Trần&action=history) | HOLD_PER_PAGE |
| WP023 | Nhà Lý | 75611474 | `87d284187a1b` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Nhà_Lý&action=history) | HOLD_PER_PAGE |
| WP025 | Văn Lang | 75578223 | `1dae07569783` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Văn_Lang&action=history) | HOLD_PER_PAGE |
| WP027 | Cách mạng tháng Tám | 75533120 | `1f03b7498a62` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Cách_mạng_Tháng_Tám&action=history) | HOLD_PER_PAGE |
| WP029 | Khởi nghĩa Lam Sơn | 75630810 | `3e5075dff7c4` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Khởi_nghĩa_Lam_Sơn&action=history) | HOLD_PER_PAGE |
| WP031 | Văn hóa Việt Nam | 75550832 | `271a96325d62` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Văn_hóa_Việt_Nam&action=history) | HOLD_PER_PAGE |
| WP032 | Ẩm thực Việt Nam | 75524867 | `0c5130fa1bbe` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Ẩm_thực_Việt_Nam&action=history) | HOLD_PER_PAGE |
| WP033 | Phở | 75647145 | `3c3b10b03336` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Phở&action=history) | HOLD_PER_PAGE |
| WP035 | Áo dài | 75565615 | `2576c735b685` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Áo_dài&action=history) | HOLD_PER_PAGE |
| WP036 | Tết Nguyên Đán | 75681026 | `ceb7ed12cfea` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Tết_Nguyên_Đán&action=history) | HOLD_PER_PAGE |
| WP037 | Quan họ | 75673678 | `d40a19f9eeeb` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Quan_họ&action=history) | HOLD_PER_PAGE |
| WP042 | Di truyền học | 75586128 | `0309dc5f1ba6` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Di_truyền_học&action=history) | HOLD_PER_PAGE |
| WP043 | Sinh thái học | 75472997 | `5cc006ad2998` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Sinh_thái_học&action=history) | HOLD_PER_PAGE |
| WP044 | Quang hợp | 75051386 | `4743bd394a72` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Quang_hợp&action=history) | HOLD_PER_PAGE |
| WP048 | Vi sinh vật học | 75079245 | `0fedf5e72d75` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Vi_sinh_vật_học&action=history) | HOLD_PER_PAGE |
| WP049 | Đa dạng sinh học | 75574422 | `e4b2c2826c89` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Đa_dạng_sinh_học&action=history) | HOLD_PER_PAGE |
| WP053 | Toán học | 75607277 | `064f872cfc97` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Toán_học&action=history) | HOLD_PER_PAGE |
| WP054 | Xác suất | 75665965 | `1ea77d6418d7` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Xác_suất&action=history) | HOLD_PER_PAGE |
| WP061 | Internet | 75348708 | `8f310661cdb0` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Internet&action=history) | HOLD_PER_PAGE |
| WP062 | Máy tính | 75614991 | `dce9434ce778` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Máy_tính&action=history) | HOLD_PER_PAGE |
| WP063 | Trí tuệ nhân tạo | 75515418 | `2ac87367fd00` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Trí_tuệ_nhân_tạo&action=history) | HOLD_PER_PAGE |
| WP068 | Giáo dục | 75352011 | `c2d1732b2511` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Giáo_dục&action=history) | HOLD_PER_PAGE |
| WP070 | Du lịch | 75296343 | `598bb060e87d` | [Ghi công](https://vi.wikipedia.org/w/index.php?title=Du_lịch&action=history) | HOLD_PER_PAGE |

## Wikisource dự phòng — chưa sử dụng

| ID | Tác phẩm | Cờ thẩm định |
|---|---|---|
| WS001 | Truyện Kiều | INCOMPLETE_WORK_REVIEW, WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |
| WS003 | Chiều hôm nhớ nhà | WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |
| WS008 | Sấm Trạng Trình | WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |
| WS009 | Nguyễn Trãi - Thị Lộ | AUTHOR_ATTRIBUTION_CONFLICT_REVIEW, WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |
| WS011 | Tự thán (Nguyễn Trãi) | WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |
| WS012 | Thơ vô đề của Nguyễn Bỉnh Khiêm | INCOMPLETE_WORK_REVIEW, WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |
| WS014 | Nam quốc sơn hà | TRANSLATION_RIGHTS_CONFIRMATION, WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |
| WS015 | Văn tế nghĩa sĩ Cần Giuộc | WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |
| WS018 | Bình Ngô đại cáo | WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |
| WS019 | Chiếu dời đô | WORK_EDITOR_TRANSLATOR_LICENSE_REVIEW |

## Quyết định đường găng

Không thêm nguồn hoặc QA K1/K2 và không chạy S1. Khi đúng ít nhất 30 nhóm đã qua thẩm định quyền/PII, khóa snapshot/split theo H03 seed `20261105`, niêm phong TEST, chạy một gói Docker bảo vệ tích hợp rồi mới xét E0 TRAIN-only hai tiến trình sạch cùng SHA. Không tự cấp E0 trong hồ sơ này.

`K1/K2=PASS_SCOPED_PRESERVED` · `F1_GROUPS=40_CANDIDATE` · `F1_ADMISSION=HOLD` · `E0=NOT_EXECUTED` · `P01=OPEN` · `P02=NOT_OPENED` · `lineage.md=UNCHANGED`.
