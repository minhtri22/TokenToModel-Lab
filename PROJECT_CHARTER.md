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

## Phụ lục quản trị có hiệu lực từ 15/11/2026 — Question First và main chuẩn

Chủ sở hữu đã yêu cầu khóa [quy chế nghiên cứu ưu tiên câu hỏi](docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md) trên `main` **trước mọi gate nghiên cứu tiếp theo**. Đây là **bổ sung ưu tiên về sau** cho các mục "Mỗi phát triển hoặc sửa đổi phải có nhánh riêng" và "chỉ merge sau QA": trước khi mở nhánh nghiên cứu/đổi kiến trúc phải đăng ký **một Question Gate**, chọn framework (5W1H/5 Whys/SWOT/FMEA/MCDA/khả năng bác bỏ) có lý do, trả lời và đóng gate với quyết định owner. Mỗi lần chỉ **một** câu hỏi nghiên cứu chủ động và tối đa một nhánh nghiên cứu/implement đang hoạt động. Không sinh nhánh con cho mỗi finding.

`lineage.md` tiếp tục append-only; **chỉ các kết quả khoa học PASS/FAIL có phạm vi, exact implement HEAD và nguồn phân xử** mới được thêm từ thời điểm hiệu lực. Entry kỹ thuật và governance lịch sử giữ nguyên byte nhưng không mở rộng tiền lệ cho entry mới. QA/HOLD/design/metadata nằm trong [active research gate](docs/governance/ACTIVE_RESEARCH_GATE.md) và receipt riêng. Sau mỗi nghiên cứu phải có quyết định **MERGE_APPROVED / EVIDENCE_ONLY_NO_MERGE / NO_MERGE_NEEDED / HOLD_MERGE_REVIEW**. `main` là trạng thái quyết định/lineage khoa học mới nhất được chứng nhận, không là nơi gom code FAIL/HOLD.

**Ngoại lệ quản trị ban đầu có owner phê duyệt:** commit tài liệu-only ban hành chính sách trực tiếp vào `main` sau author QA, không có science, không đổi `lineage.md`, không merge nhánh implement hoặc trao quyền thực thi. Những thay đổi về sau theo quy trình PR/QA/owner thông thường. Không tự xóa nhánh cũ hay worktree.
