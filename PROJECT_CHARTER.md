# Điều lệ dự án (Project Charter)

## Danh tính và mục tiêu

- Tên: **TokenToModel Lab (TTM)** — từ token đến mô hình.
- Mã nguồn: `https://github.com/minhtri22/TokenToModel-Lab`.
- Phạm vi kỹ thuật: xây Transformer chỉ có bộ giải mã (Decoder-only Transformer), huấn luyện từ đầu đến cuối (End-to-end Training), đánh giá, tối ưu suy luận và quản lý bộ nhớ phân trang.
- Phạm vi nghiên cứu: cơ chế chú ý (Attention), sai số số học, quản trị bộ nhớ KV (KV Cache), hiệu năng, quy mô mô hình và các biến thể kiến trúc.
- Phạm vi giáo dục: tài liệu tiếng Việt, bài thực hành có bằng chứng và biên soạn sách.
- Thương mại hóa là mục tiêu dài hạn có điều kiện: phải kiểm tra nguồn dữ liệu, quyền dùng mã/trọng số, an toàn, hiệu năng, chất lượng và vận hành; không suy ra từ một bản demo.

## Nguyên tắc quản trị

1. Mỗi phát triển hoặc sửa đổi phải có nhánh riêng từ commit `main` được xác minh; không ghi đè kết quả cũ.
2. Mỗi cấu hình và lần chạy có mã định danh, commit, nguồn dữ liệu, hạt giống ngẫu nhiên (seed), môi trường, mã SHA-256 và biên bản thử nghiệm.
3. Cần xác lập giả thuyết, tiêu chí và đối chứng (Baseline) trước khi coi một phép đo là cải thiện.
4. Giữ cả PASS, FAIL và kết quả chưa kết luận (Inconclusive). Sổ `lineage.md` chỉ ghi bổ sung (append-only).
5. Kiểm thử chức năng (QA PASS), kết quả khoa học và mức sẵn sàng thương mại là ba quyết định khác nhau.
6. Chỉ hợp nhất (merge) nhánh vào `main` sau kiểm thử độc lập trong phạm vi đã công bố và quyết định chấp thuận.
7. Mọi Git worktree và thao tác dọn dẹp phải nằm trong `D:\WORK\RESEARCH\TokenToModel-Lab`; không xóa hay tác động thư mục của dự án khác.
8. Tài liệu do dự án viết dùng tiếng Việt; thuật ngữ chuyên ngành tiếng Anh đặt trong ngoặc sau phần tiếng Việt. Giữ nguyên tên mã, đường dẫn, lệnh, chỉ số và nguyên văn của bằng chứng đã khóa.

## Mốc đầu tiên

P00 đã đạt kiểm thử mô hình CPU và được hợp nhất trên GitHub qua PR #1. Đây là mốc kỹ thuật cho các giai đoạn tiếp theo, **không** chứng minh huấn luyện thành công hoặc tăng tốc PagedAttention.
