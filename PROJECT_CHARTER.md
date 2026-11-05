# Điều lệ dự án (Project Charter)

- **Tên chính thức:** TokenToModel Lab (TTM) — From Token to Model.
- **Sản phẩm cuối:** mô hình ngôn ngữ decoder-only có huấn luyện end-to-end, trình phục vụ suy luận, hệ đo và tài liệu có thể tái lập.
- **Nghiên cứu:** cơ chế attention, quản lý KV, sai số số học, hiệu suất, mở rộng và các biến thể.
- **Giáo dục:** sổ tay kỹ thuật, thí nghiệm và dàn ý chuyển hóa thành sách.
- **Thương mại:** là mục tiêu dài hạn có điều kiện; không đồng nhất việc tự viết mô hình với quyền sử dụng dữ liệu/weights hoặc mức độ an toàn để thương mại.

## Quy tắc quyết định

1. Đặc tả và đối chứng trước phát triển; mọi thay đổi làm biến đổi kết quả phải có lý do và cấu hình được ghim.
2. Tất cả nhánh triển khai xuất phát từ main HEAD mới nhất; nhánh độc lập, không ghi đè kết quả cũ.
3. QA PASS mới merge; trạng thái thực nghiệm được tuyên bố riêng (VALIDATED/INCONCLUSIVE/FAIL).
4. Mỗi kết luận dẫn đến run ID, cấu hình, seed, bộ dữ liệu, commit SHA, môi trường, log và hash bằng chứng.
5. Mọi kết quả PASS, FAIL, NO_RESULT đều được bảo lưu. `lineage.md` append-only, không xóa hay sửa mốc cũ; đính chính bằng entry mới.
6. Chỉ huấn luyện thật khi dữ liệu, giấy phép, tài nguyên và phép thử đã được xác định rõ; không gán tên "GPT thương mại" cho thử nghiệm toy.
