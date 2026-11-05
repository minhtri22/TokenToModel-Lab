# P01 D1 — Tiền thẩm định bộ kiểm tra độc lập, chỉ đọc

**Mã:** `TTM_P01_D1_INDEPENDENT_QA_PREAUTH_READONLY`  
**Ngày:** 05/11/2026  
**Trạng thái:** `SPEC_ORACLE_CHECK_PASS_CHECKER_RUNTIME_NOT_AUTHORIZED`.

## 1. Nguồn được kiểm tra

- Đặc tả byte F0: `docs/p01/P01_D1_H04_FIXTURES_AND_INDEPENDENT_QA_SPEC.md`.
- Thuật toán BPE: `docs/p01/P01_D1_H01_DETERMINISTIC_BPE_SPEC.md`.
- Trùng và gần trùng: `docs/p01/P01_D1_H03_DEDUP_SPLIT_SPEC.md`.
- Tiêu chí D1: `docs/p01/P01_D1_METHOD_REVIEW_AND_LOCK_GATE_20261105.md`.

Chỉ dùng dữ liệu byte giả lập **đã viết trong tài liệu**, không tải corpus, không chạy phần mềm tokenizer P01 và không dùng TRAIN/VALIDATION/TEST thật.

## 2. Kiểm tra lại giá trị oracle (Expected Results)

| Mã | Phép kiểm tra | Kết quả | Giới hạn |
|---|---|---|---|
| Q01 | Tính SHA-256 từ chuỗi byte hex F00–F08 và F11 | 10/10 trùng bản đặc tả | Chỉ chứng minh bảng mã băm đúng với byte mô tả |
| Q02 | Tính SHA-256 từ byte `41` lặp 64 lần và 65 lần (F09–F10) | 2/2 trùng | Không có mô hình GPT nào đã chạy |
| Q03 | Chuỗi F02 (`e1baaf`) và F03 (`61cc86cc81`) sau Unicode NFC | Cùng thành `e1baaf`, giữ raw hash khác nhau | Khẳng định quy tắc khóa phụ; chưa chạy Dedup P01 |
| Q04 | Giải mã UTF-8 nghiêm ngặt cho F06, F07 và F08 | 3/3 trường hợp bị từ chối | Chỉ kiểm tra oracle thư viện chuẩn, không kiểm thử sản phẩm |

**Kết luận về byte oracle:** `F0_ORACLE_BYTES_SHA=PASS_12_OF_12`; `F0_UNICODE_REFERENCE_CHECK=PASS_SCOPED`. Kết quả này không làm H04 từ `PENDING` chuyển thành `DYNAMIC_QA_PASS`.

## 3. Độc lập cần được chứng minh như thế nào?

Bộ kiểm tra (Checker) không được chỉ gọi lại cùng hàm của chương trình thực thi mà tuyên bố đã kiểm tra độc lập. Hợp đồng chuẩn bị như sau:

| Lớp | Nguồn sự thật độc lập | Trường hợp sai phải phát hiện |
|---|---|---|
| Bộ mã hóa byte B0 | Hex đầu vào F00–F11 và SHA-256 kỳ vọng trong đặc tả đã khóa | Thay Unicode, cắt chuỗi, ép kiểu, ID vượt 255 |
| BPE B1 | Quy tắc TIE01, OVERLAP01, BOUNDARY01 và SHA của tệp `merges.ttmbpe` | Thay luật phá hòa, ghép chồng lấn, ghép xuyên tài liệu, định dạng bị thay |
| Phân nhóm gần trùng | So sánh F02/F03, nhóm A–B–C, kiểm tra ranh giới tỷ lệ | Nhóm bị tách, đổi byte gốc, đổi seed, đổi ngưỡng |
| Chia tập | Danh sách nhóm được khóa và công thức SHA seed 20261105 | Một nhóm hoặc nội dung trùng đi vào hai tập; TEST đi vào TRAIN |
| Quyền dữ liệu | Danh mục nguồn có quyền `ALLOW` | Tài liệu thiếu phép vẫn lọt vào TRAIN |
| Tài nguyên | Số đo RAM/đĩa và cơ chế giám sát dừng an toàn | Vượt ngưỡng, vẫn tiếp tục hoặc tự thử lại |

Bộ kiểm tra có thể dùng thư viện băm tiêu chuẩn để xác minh byte nhưng **không** được đọc mã thuật toán BPE của ứng viên để tính oracle theo cùng một đường. Mọi oracle cố định phải được ghim SHA trước thực thi và được thử bằng cả trường hợp âm tính (Negative Control).

## 4. Các cổng còn thiếu

1. **Checker chưa có mã nguồn được duyệt:** chưa có commit, SHA-256, kiểm tra tĩnh hoặc biên bản âm tính trên Windows. Chưa được viết mới trong phạm vi chỉ đọc này.
2. **Chưa có bộ dữ liệu F0 được lưu bằng byte riêng:** chỉ có bảng Markdown; phải phê duyệt quy tắc tạo byte từ hex sau I0 và kiểm tra tệp/giá trị kỳ vọng trước lần chạy.
3. **Nguồn TRAIN chưa được phê duyệt:** không có cách chứng minh tệp merges từ dữ liệu thực khi không có dữ liệu hợp lệ.
4. **Bộ giới hạn tài nguyên (Resource Guard) chưa có QA:** không thể dùng điều kiện RAM/đĩa dự kiến để tuyên bố an toàn thực thi.
5. **Chưa có người/bộ kiểm định tách biệt với nhóm triển khai:** một lượt đọc lại nội dung bởi trợ lý không phải kiểm định bên thứ ba.

## 5. Kết luận tiền thẩm định

- `H04_STATIC_ORACLE_INTEGRITY=PASS_SCOPED`.
- `H04_CHECKER_IMPLEMENTATION=NOT_PRESENT`.
- `H04_INDEPENDENT_NEGATIVE_QA=NOT_EXECUTED`.
- `H04_WINDOWS_RUNTIME_QA=NOT_EXECUTED`.
- `H04_INDEPENDENT_QA_PREAUTH=HOLD_CHECKER_AND_NEGATIVE_CONTROLS`.
- `P01_D1_SCIENTIFIC_PREREG_LOCK=HOLD`.

**Không** tạo worktree P01, không tạo checker thực thi, không huấn luyện, không tải corpus và không chỉnh sửa các SHA mẫu sau khi đã nhìn thấy kết quả tương lai.
