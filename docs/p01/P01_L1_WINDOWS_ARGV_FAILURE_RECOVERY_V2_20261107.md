# TTM P01 — Khôi phục lỗi truyền tham số Python trên Windows (V2)

Ngày 07/11/2026. Đây là hồ sơ QA kỹ thuật của nhánh kiểm toán, không phải thẩm định khoa học.

## Bằng chứng thất bại được giữ nguyên

Đã đọc lại từ Windows tệp `evidence/p01/TTM_P01_L1_WINDOWS_SINGLE_BATCH_20261107.json` và marker `TTM_P01_L1_WINDOWS_SINGLE_BATCH_20261107.once`. Biên bản trả về `verdict=FAIL_OR_INCONCLUSIVE`, `reason=EXACT_SOURCE_EXTRACTION_FAILED`, `source_pin=b481a90fa82abb194f5ae60945a5ad4408b5a425`. Marker cũ đã tiêu thụ, thư mục tạm đã được dọn theo console; không chạy 7 QA Windows, F0 hoặc E0.

## Nguyên nhân và sửa chữa

Mã Python truyền thẳng qua `PowerShell 5.1 → python -c <multiline>` làm mất dấu ngoặc kép ở tệp nguồn nhúng, dẫn tới `SyntaxError: invalid decimal literal` đối với chuỗi Git blob SHA.

Bản khôi phục V2 tạo một tệp Python UTF-8 trong đúng thư mục tạm do script sở hữu và gọi `python -B <path> <args>`, không truyền Python nguồn qua `-c`. Trước khi chạy, bắt buộc kiểm tra biên bản FAIL và marker nguyên bản rồi bảo toàn SHA của chúng. Sử dụng marker và receipt mới; tuyệt đối không xóa hoặc sửa marker cũ. Không fetch/checkout/merge/reset Git; dùng mã commit đã tải xuống từ lần chạy trước.

**Tên script:** `TTM_P01_L1_WINDOWS_ARGV_RECOVERY_V2_PS51.ps1` (tệp đính kèm chat, chưa commit vào repository). **SHA-256 byte BOM + UTF-8:** `33fce6fa4ce42c08662e0f04b62744a5092d086c9ce702ab809e91f88cfe2967`.

Kiểm tra tĩnh phần Python nhúng: `ast.parse=PASS`; 11 kiểm tra phạm vi sửa chữa: PASS. **Chưa thực thi parser PowerShell 5.1 hoặc QA trên Windows** ở bước ghi nhận này; không gọi đây là Windows PASS.

## Trạng thái cổng

`L1_WINDOWS=NOT_EXECUTED_RECOVERY_V2`; `F1=HOLD_SOURCE_RIGHTS`; `K4=HOLD_ROUTE_DECISION`; `E0=NOT_EXECUTED`; `P01=OPEN`; `P02=NOT_OPENED`.

Khi người dùng chạy script và nhận receipt V2, mới thẩm định độc lập và lưu lại bằng chứng Windows. Không chạy lại 10 F0; không sửa lineage.md, S1 receipt/marker hoặc P00.
