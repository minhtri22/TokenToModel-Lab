# TTM P01 — Thay thế lựa chọn F1: F1-VI-GENERAL-01, không dùng CQG-J3

Ngày: 07/11/2026. Mã quyết định: `TTM_P01_F1_RESELECT_VI_GENERAL_EXCLUDE_CQG_J3`. Đây là **quyết định chọn nguồn ứng viên**, không phải tiếp nhận corpus hay giấy phép chạy E0.

## 1. Chỉ thị chủ dự án

Chủ dự án yêu cầu **loại CQG-J3 khỏi phase P01 F1** và lựa chọn nguồn phù hợp hơn. Từ thời điểm này:

- `F1-CQG-J3` được đánh dấu `SUPERSEDED_NOT_APPLICABLE` trong công việc F1 hiện hành.
- Không chạy `TTM_P01_F1_CQG_J3_READONLY_CENSUS_PS51_V1.ps1` cho F1 của phase P01; không nhập nghiên cứu CQG, SIX, ARN, IRIS hay các repository nghiên cứu nội bộ vào corpus mới.
- Không xóa các quyết định đã ghi, SHA, bằng chứng PASS/FAIL, source code hoặc tài liệu của dự án khác. Các hồ sơ quyết định trước đây được giữ **bất biến để truy vết**; văn bản này là quyết định kế nhiệm.

## 2. Nguồn thay thế

**Mã ứng viên mới:** `F1-VI-GENERAL-01`.

| Nguồn | Mục tiêu tài liệu | Văn phong | Điều kiện tiếp nhận |
|---|---:|---|---|
| Wikipedia tiếng Việt — https://vi.wikipedia.org | 70 | tiếng Việt hiện đại, nhiều chủ đề | lưu page ID, revision ID, URL, đóng góp tác giả/ghi công, giấy phép và ngoại lệ từng trang; không lấy ảnh, hộp thông tin, bảng mã |
| Wikisource tiếng Việt — https://vi.wikisource.org | 20 | văn xuôi và văn chương | kiểm tra tình trạng bản quyền tác phẩm **và** bản dịch/bản in; không lấy nhiều chương cùng tác phẩm làm nhóm độc lập |
| CSDL quốc gia về pháp luật — https://vbpl.vn | 10 | văn bản chính thức hành chính/pháp lý | chỉ văn bản quy phạm/pháp luật chính thức, không lấy bài diễn giải hay bình luận; tránh bản hợp nhất gần trùng |
| **Tổng** | **100** | | **Mục tiêu chưa materialize, không phải bộ được duyệt** |

Chính sách lựa chọn nguồn là nghiên cứu ứng dụng BPE trên tiếng Việt tổng quát, **không** là tập đại diện công bằng của tiếng Việt đời thường và không là corpus P03 GPT.

## 3. Bằng chứng điều kiện sử dụng

- Wikimedia cung cấp văn bản thường theo Creative Commons Attribution-ShareAlike, có ghi công và điều kiện chia sẻ tương tự; phải kiểm tra từng revision, tác giả, ngoại lệ bản quyền và trách nhiệm nếu phát hành lại. https://foundation.wikimedia.org/wiki/Terms_of_Use ; https://www.mediawiki.org/wiki/Wikimedia_APIs/Content_reuse
- Chính sách Wikisource tiếng Việt yêu cầu thẩm định công cộng/giấy phép từng tác phẩm và cả bản dịch nếu có. https://vi.wikisource.org/wiki/Wikisource:Quy_%C4%91%E1%BB%8Bnh_b%E1%BA%A3n_quy%E1%BB%81n
- Điều 15 Luật Sở hữu trí tuệ loại trừ văn bản quy phạm pháp luật, hành chính, tư pháp và bản dịch chính thức khỏi bảo hộ quyền tác giả. Chỉ áp dụng ở phạm vi đó; không mặc định mọi trang thuộc `vbpl.vn` được phép sao chép và phân phối theo mọi cách. https://ipvietnam.gov.vn/bo-luat-luat
- Chưa có kết luận pháp lý rằng tệp `merges` hay mô hình huấn luyện trên dữ liệu CC BY-SA tự động thuộc hoặc không thuộc giấy phép chia sẻ tương tự. Khi cần phân phối/ứng dụng thương mại phải rà soát ở giai đoạn liên quan.

## 4. Quy trình tối thiểu để xác nhận F1

1. Chọn trước đúng 100 URL/tác phẩm ứng viên theo 7 nhóm chủ đề Wikipedia (10 mục mỗi nhóm), 20 tác phẩm Wikisource độc lập, 10 văn bản pháp luật chính thức. Khóa nguyên tắc chọn không dựa trên nhãn TEST hoặc kết quả BPE.
2. Lập `source manifest` với ít nhất `source_id`, `original_location`, `owner_or_author`, `license_id`, `license_evidence_uri`, `permitted_uses`, `source_revision`, `source_sha256`, `byte_count`, `document_count`, `encoding`, `pii_status`, `copyright_status`, `rights_reviewed_at`, `reviewer`, `source_snapshot_id`, `admission_decision`.
3. Chỉ nhận nội dung đủ quyền, UTF-8 hợp lệ, không chứa thông tin PII chưa xử lý; bảo toàn byte nguồn và tệp dẫn xuất khác nhau cùng mã SHA-256. Chặn F1 nếu thiếu bất kỳ chứng cứ quyền dùng bắt buộc nào.
4. Theo H03 đã định, nhóm near-duplicate bằng connected components; >=30 nhóm độc lập. Seed `20261105`, chia theo nhóm 80/10/10, không giao cắt raw/canonical/group. Một tác phẩm nhiều chương phải ở cùng nhóm nguồn dù H03 không phát hiện trùng từ vựng.
5. Giữ `<=64 MiB`, `<=2.000 tài liệu`. Lưu corpus chỉ trong `D:\WORK\RESEARCH\TokenToModel-Lab\datasets\approved_sources\`, **không commit văn bản gốc lên GitHub**.

## 5. Tuyến E0 và trạng thái

Tuyến ứng viên: Docker Linux trên CPU của Windows, container không mạng khi TRAIN, nguồn chỉ đọc, không gắn TEST, giới hạn RAM/job memory, đĩa, thời gian và kiểm thử từ chối trước chạy. Tuyến này **chưa đạt cổng QA**; không được dùng như cách bỏ qua các bảo vệ đã duyệt. S1 Windows native FAIL/consumed được giữ nguyên và không tái thực thi.

`K1=PASS_SCOPED_WINDOWS`; `K2=PASS_SCOPED_WINDOWS`; `K3=HOLD_SOURCE_ADMISSION`; `K4=ROUTE_SELECTED_NOT_QUALIFIED`; `E0=NOT_EXECUTED`; `P01=OPEN`; `P02=NOT_OPENED`.

## 6. Bước kế tiếp

`TTM_P01_F1_VI_GENERAL_01_EXACT_100_URL_SELECTION_AND_RIGHTS_SNAPSHOT_PREFLIGHT` — lập danh sách URL/revision có provenance và giấy phép, kiểm tra giới hạn và PII, rồi mới xét quyền tải/tạo snapshot, split và E0. Không thêm một vòng QA L1/K1/K2, không sửa `lineage.md`, không merge P01.
