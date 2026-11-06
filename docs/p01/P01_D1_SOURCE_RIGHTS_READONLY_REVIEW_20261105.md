# P01 D1 — Rà soát nguồn văn bản và quyền sử dụng (Source Rights Read-only Review)

**Ngày thẩm định:** 05/11/2026  
**Mã kiểm tra:** `TTM_P01_D1_SOURCE_RIGHTS_READONLY_REVIEW`  
**Phạm vi:** chỉ đọc hồ sơ GitHub và danh sách thư mục gốc trên Windows; tra cứu điều khoản chính thức của một nguồn văn bản công khai để chuẩn bị phương án, **không tải văn bản hoặc tiếp nhận corpus**.

## 1. Bằng chứng tìm thấy trong dự án

- PR #4 đang ở trạng thái nháp (Draft), chưa hợp nhất; nhánh `design/p01-tokenizer-data-prereg-20261105`.
- Tệp `P01_D1_H02_H05_SOURCE_RESOURCE_GATE.md` chỉ đặc tả trường danh mục nguồn (`source_id`, `license_id`, `license_evidence_uri`, `permitted_uses`, `source_sha256`, `pii_status`, `admission_decision`), **chưa có danh mục nguồn với quyết định ALLOW**.
- Danh sách thư mục gốc `D:\WORK\RESEARCH\TokenToModel-Lab` từ RemoteMCP có `docs/`, `evidence/`, `artifacts/`, `configs/`, `reference/`... nhưng **không hiện thư mục `datasets/`**. Không suy ra không có dữ liệu hợp pháp ở mọi nơi khác trên thiết bị.
- Không có `source_snapshot_id`, byte nguồn, số tài liệu, quyền huấn luyện tokenizer, hoặc SHA-256 corpus đã được xác minh. **Không được gán ALLOW**.

**Kết luận đối với nguồn P01 hiện hành:** `H02_SOURCE_ADMISSION=HOLD_NO_VERIFIED_F1_OR_F2`.

## 2. Nguồn tiềm năng được kiểm tra điều khoản, chưa chấp thuận

**Ứng viên tham khảo:** văn bản Wikipedia tiếng Việt do Wikimedia cung cấp, **chưa được chọn làm nguồn P01**.

- Điều khoản Wikimedia Foundation cho biết văn bản đóng góp thường được cấp theo giấy phép Creative Commons Ghi công–Chia sẻ tương tự 4.0 (CC BY-SA 4.0), với khả năng có ngoại lệ và nội dung nhập từ nguồn khác.
- Hướng dẫn tái sử dụng của MediaWiki yêu cầu kiểm tra giấy phép tại nội dung cụ thể, ghi công tác giả/nguồn và chỉ rõ thay đổi nếu có. Trường hợp phân phối lại nội dung dẫn xuất còn có điều kiện chia sẻ tương tự.
- Vì chưa xác định **ảnh chụp dữ liệu cụ thể (Snapshot)**, danh sách trang, lịch sử nhập nguồn, điều kiện sử dụng khi huấn luyện tokenizer, phạm vi quyền riêng tư và nghĩa vụ công bố bộ từ vựng/dẫn xuất, nên chưa thể tuyên bố corpus đã đủ quyền dùng vào mục đích P01.

**Tài liệu chính thức chỉ phục vụ rà soát pháp lý, không phải giấy phép cấp riêng cho dự án:**

- Wikimedia Foundation, Điều khoản sử dụng: https://foundation.wikimedia.org/wiki/Terms_of_Use
- MediaWiki, Hướng dẫn tái sử dụng nội dung: https://www.mediawiki.org/wiki/Wikimedia_APIs/Content_reuse
- Wikimedia Attribution Framework, quy tắc thông tin giấy phép: https://attribution.wikimedia.org/attribution-signals/license.html

**Trạng thái ứng viên:** `CANDIDATE_ONLY_NOT_DOWNLOADED_NOT_ADMITTED`. Đây không phải kết luận pháp lý về tính hợp lệ của một bộ dữ liệu chưa xác định.

## 3. Bộ hồ sơ cần có trước quyết định ALLOW

| Trường bắt buộc | Đã có bằng chứng? |
|---|---|
| `source_id`, tên/tổ chức sở hữu và vị trí nguồn chính thức | Chưa có ứng viên được chọn |
| `license_id` và bản điều khoản áp dụng cho đúng corpus | Chưa |
| `permitted_uses`: học bộ tách token, tạo và phát hành từ vựng/quy tắc ghép, thương mại nếu cần | Chưa |
| `source_snapshot_id`, mã SHA-256, số byte, số tài liệu | Chưa, và không được tải trong bước này |
| Kết quả rà soát dữ liệu cá nhân (PII) và ngoại lệ bản quyền | Chưa |
| Quy tắc ghi công, chia sẻ tương tự, giới hạn lưu trữ và xóa | Chưa |
| Quyết định tiếp nhận của người có thẩm quyền (`admission_decision=ALLOW`) | Không có |

Quyền truy cập web hoặc quyền đọc tài liệu công khai **không** thay thế bằng chứng quyền sử dụng.

## 4. Quyết định và hướng không cần dữ liệu thật

- `F0_SYNTHETIC_DESIGN_REVIEW=PERMITTED`: chỉ mô tả/phân tích byte giả lập và bộ kiểm tra độc lập ở mức tài liệu.
- `F1_OR_F2_TRAINING_CORPUS=NOT_ADMITTED`: không có nguồn nào được duyệt.
- `SOURCE_DOWNLOAD_AUTHORIZED=false`.
- `BPE_TRAINING_AUTHORIZED=false`.
- `D1_SCIENTIFIC_PREREG_LOCK=HOLD_SOURCE_RIGHTS`.

Nếu trong một quyết định khoa học riêng chuyển P01 sang **F0-only**, phạm vi chỉ là kiểm tra chức năng trên dữ liệu giả lập; không được tuyên bố tỷ lệ nén, chất lượng hoặc khả năng khái quát trên văn bản thật.
