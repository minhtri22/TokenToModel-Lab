# P01 D1 — Cổng thẩm định thiết kế bộ kiểm tra độc lập (Independent Checker)

**Trạng thái:** `DESIGN_REVIEW_ONLY_NO_CHECKER_CODE`. Đây là bản phân công/phương pháp QA; chưa cho phép tạo mã, chạy lệnh Python, tạo dữ liệu F0 trên Windows hoặc huấn luyện.

## 1. Tính độc lập cần chứng minh

- Bộ kiểm tra (Checker) không được gọi lại hàm `encode/decode` của bộ tách token làm chính oracle của nó. Việc đối chiếu byte đầu ra cần thực hiện trực tiếp trên byte nguồn đã ghim và danh sách ID được giải mã độc lập.
- Với B0, các byte 0–255 và các trường hợp từ chối ngoài phạm vi phải có oracle thủ công trong tài liệu, không xuất phát từ kết quả phần mềm cần kiểm tra.
- Với B1, kiểm tra cấu trúc `merges.ttmbpe` bằng bộ đọc tệp riêng: magic 11 byte, số nguyên 32-bit thứ tự byte thấp trước (Little-endian), `actual_vocab_size=256+merge_count`, `new_id=256+rank`, không có ID trỏ trước quy tắc tạo ra nó và không có byte thừa/truncated.
- Các mẫu hòa tần suất, cặp chồng lấn và biên tài liệu có kết quả được ghi rõ trước thực thi, không cho phép đổi oracle sau khi thấy kết quả.
- Bộ kiểm tra dữ liệu phải đối chiếu quyền sử dụng và `group_id` độc lập với bộ chia tập; TEST không được đọc khi học quy tắc BPE.

## 2. Ma trận kiểm định dự kiến

| Cổng | Bộ mẫu / oracle | Điều kiện đạt khi được cấp quyền chạy | Tình huống phải FAIL |
|---|---|---|---|
| C01 — B0 toàn miền byte | 256 byte cơ bản | 256/256 mã đúng, trả lại byte nguyên vẹn | Ép kiểu hoặc đổi byte |
| C02 — F0 hoàn nguyên | F00–F11 | 12/12 đúng raw bytes; giữ nguyên NFC/NFD, CRLF | Bị thay dấu, thay newline |
| C03 — Lỗi Unicode | F06/F07/F08 và N04 | 100% lỗi đúng contract | Tự chèn ký tự thay thế |
| C04 — Từ chối ID | N01–N03, N06 | 100% từ chối trường hợp sai | `bool` được coi là int, ID âm bị chấp nhận |
| C05 — BPE ghép và phá hòa | TIE01, OVERLAP01, BOUNDARY01 | Quy tắc và ID khớp oracle, không ghép xuyên tài liệu | Đếm/ghép sai vị trí |
| C06 — Tính quyết định | ORDER01, REPRO01 | Hai tiến trình sạch tạo cùng byte và SHA-256 | Khác do thứ tự hashmap, thời gian |
| C07 — Chống rò rỉ | DUP01, TRANSITIVE01, SPLIT01, LEAK01 | Không có `group_id`/băm chung xuyên tập | TEST bị đọc để học BPE |
| C08 — Điều kiện từ chối nguồn | RIGHTS01, MIN01 | Từ chối nguồn thiếu quyền hoặc ít hơn 30 nhóm | Tự cấp quyền dữ liệu hoặc tự chia lại |
| C09 — Giới hạn tài nguyên | N08, ngân sách H05 | Quá ngưỡng phải dừng có biên bản, không chạy lại | Dừng không có log, vượt quá rồi vẫn PASS |
| C10 — Tính toàn vẹn bằng chứng | SHA-256 của mã, cấu hình, fixture và biên bản | Mã hash khớp, không ghi đè `run_id` | Chấp nhận tệp sai SHA hoặc đổi oracle |

Cột điều kiện đạt là **hợp đồng cho kiểm thử tương lai**, hiện chưa có bài nào trong số C01–C10 được chạy trên trình triển khai P01.

## 3. Tiền kiểm QA trước khi viết mã

1. Một người/quy trình kiểm định riêng phải đọc đặc tả H01, H03, H04 và chỉ ra các trường hợp ranh giới chưa có oracle; ghi PASS/HOLD/FAIL bằng văn bản trước khi cho phép I0.
2. Kiểm tra sự tương thích và mâu thuẫn giữa B0 256 ID và B1 2048 ID; không sửa P00 để vượt qua.
3. Chốt mối quan hệ giữa mỗi bộ mẫu F0 và từng chức năng `encode_bytes`, `decode_bytes`, `encode_text`, `decode_text`; phân biệt dữ liệu byte sai UTF-8 và Unicode đầu vào không hợp lệ.
4. Đưa bộ kiểm tra lên nhánh/mã nguồn riêng **chỉ khi I0 được cho phép**, cùng mã nguồn và SHA-256 riêng với generator/renderer.
5. Kiểm tra tĩnh, kiểm thử âm tính, kiểm thử độc lập và biên bản Windows thực tế là các quyết định sau; không suy diễn từ việc bản thiết kế đầy đủ.

## 4. Kết luận hiện tại

`H04_CHECKER_DESIGN_GATE=SPECIFIED`  
`H04_CHECKER_SOURCE=NOT_CREATED`  
`H04_INDEPENDENT_DYNAMIC_QA=NOT_EXECUTED`  
`H04_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`P01_D1_SCIENTIFIC_LOCK=HOLD`

**Bước tiếp theo:** thẩm định độc lập C01–C10 ở mức hồ sơ (đặc biệt oracle BPE và dữ liệu chia nhóm). Sau khi nguồn và cổng an toàn thực thi được chấp thuận mới xem xét I0, không mở tự động.
