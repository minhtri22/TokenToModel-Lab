# Quyền tài liệu và truy xuất nguồn — Dive into LLMs

**Kiểm tra 2026-11-16:** Đường dẫn [upstream](https://github.com/Lordog/dive-into-llms) · commit khóa [`f84c04268794ef94f8949808bbc14ab8636763a0`](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0).

## Kết quả

- Trong API listing thư mục gốc upstream tại thời điểm kiểm tra: có `.gitignore`, `README.md`, `documents/`, `pics/`; **không có `LICENSE`**.
- Tìm `LICENSE` tại root bằng GitHub Contents API trả `404 Not Found`. Chưa kiểm toán toàn bộ quyền tách rời của từng PDF, ảnh, notebook và tư liệu mượn từ bên thứ ba.
- README nêu mục tiêu phổ cập và cung cấp miễn phí; **không coi đây là giấy phép công bố bản dịch / redistribution**.
- **`RIGHTS_REUSE_AND_DERIVATIVE=NOT_VERIFIED`; `FULL_TRANSLATION_PUBLICATION=HOLD`.**

## Các hành động được phép trong phạm vi docs-only này

- Truy cập liên kết upstream, clone về máy để nghiên cứu và kiểm kê trong giới hạn điều khoản áp dụng; giữ tài liệu upstream tách khỏi Git repository TTM.
- Viết **phân tích học thuật độc lập, glossary do tác giả mới biên soạn, ma trận câu hỏi và liên kết nguồn**.
- Không commit lại README gốc, notebook, slide PDF, hình ảnh, bản dịch chương chi tiết, dù đã ghi công tác giả.
- Không tạo bản fork công khai chứa nội dung chuyển ngữ trước khi có giấy phép rõ.

## Yêu cầu cấp quyền cần giải quyết

Đề nghị người giữ bản quyền xác nhận **bằng văn bản** ít nhất: (1) có cho phép dịch từ tiếng Trung sang tiếng Việt, (2) có được xuất bản công khai trên GitHub, (3) giấy phép của bản dịch, (4) yêu cầu attribution/chia sẻ tương tự, (5) có quyền dịch notebook, ảnh, slide PDF và tài liệu bên thứ ba hay không, (6) cách xử lý cập nhật upstream và yêu cầu gỡ bỏ. Nếu chỉ cấp quyền một phần, giới hạn manifest vào đúng file.

Gợi ý thông điệp ngắn xin quyền:

> We are preparing a Vietnamese study companion for research and education related to TokenToModel-Lab and CLDP. May we translate and publish selected text chapters of dive-into-llms on GitHub? Please clarify the permitted files, attribution, derivative licensing, and whether notebooks, figures, and slides are covered. We will not publish translated original content without permission.

**Không có bằng chứng đã gửi yêu cầu, đã nhận đồng ý, hoặc đã được cấp giấy phép.**

## Source manifest (phạm vi thực đọc)

| Tệp | Git blob SHA-1 (upstream) |
|---|---|
| `README.md` | `933f8fae9ba3cf9fd0a3d314793749451b5bd0b2` |
| `documents/chapter1/README.md` | `23aaae0187c2a72bc13f36caf33ddaa5789ecbf2` |
| `documents/chapter2/README.md` | `eeca2e40c8f8a6559c072840694232eafbb78692` |
| `documents/chapter3/README.md` | `758e3bb6cac9bf0f339df9619957503a395205ab` |
| `documents/chapter4/README.md` | `ded35cfaf1027f0aee8444997c1fd8fedd9a23bf` |
| `documents/chapter10/README.md` | `afbfb399680bedb1a423cbac6c843e87f2d1fb21` |
| `documents/chapter11/README.md` | `34296bf478910ac869a165cac751da53f4256b59` |

**Lưu ý:** SHA-1 Git blob là định danh Git, không thay thế SHA-256 của receipt. Các file Ch.5–9 chỉ kiểm kê theo mục lục root; chưa xác minh nội dung sâu. Không tuyên bố QA independent nếu chưa có reviewer riêng.
