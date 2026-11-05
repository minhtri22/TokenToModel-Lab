# TokenToModel Lab (TTM) — GPT-like từ token tới suy luận phân trang

Bộ mã P00 để đưa lên nhánh phát triển của repository `minhtri22/TokenToModel-Lab`. **Chưa có kết quả huấn luyện khoa học chính thức, chưa có phép đo tối ưu PagedAttention GPU.**

## Mục tiêu

Tự xây và hiểu trọn chu trình tokenizer → dữ liệu → decoder-only Transformer → huấn luyện → đánh giá → KV cache → paged attention → phục vụ mô hình → rà soát thương mại hóa.

Mỗi thay đổi đi qua nhánh Git riêng, mã hóa cấu hình, ghi nhật ký, QA và so sánh đối chứng. `main` chỉ nhận nhánh đã QA PASS. `lineage.md` chỉ ghi thêm, không sửa lịch sử. QA PASS không tự động đồng nghĩa đạt chất lượng khoa học hoặc sẵn sàng thương mại.

## Tình trạng ban đầu

- `reference/phase0/`: bản mã PyTorch minh họa từ gói tham chiếu đã tạo trong hội thoại; được lưu **nguyên trạng** để tiếp tục phát triển, không coi là phiên bản production.
- `docs/`: kiến trúc, lộ trình, quản trị, giao thức đo, huấn luyện, thương mại.
- `configs/`: cấu hình đề xuất, **chưa đóng băng thí nghiệm**.
- `experiments/`: nhật ký JSONL và cấu trúc đối chứng; hiện chưa chứa lượt chạy khoa học nào.
- `scripts/`: công cụ ghi receipt và tạo so sánh; chỉ kiểm tra/ghi bằng chứng, không tự chạy huấn luyện.
- `book/`: dàn ý sách phát triển từ các mốc đã được xác thực.

## Chạy bộ tham chiếu CPU

Cài PyTorch phù hợp theo tài liệu chính thức; có thể dùng Python 3.13 nếu có bản torch tương thích. Từ thư mục repository:

```powershell
python -m unittest discover -s reference/phase0 -p test_reference.py -v
python -m unittest discover -s tests -p test_*.py -v
python reference/phase0/demo.py
```

Các lệnh này dùng fixture nhỏ, không tải dữ liệu khoa học, không huấn luyện chính thức, không tác động Git.

## GitHub và ranh giới workspace

- Repository duy nhất: `https://github.com/minhtri22/TokenToModel-Lab`.
- Workplace duy nhất: `D:\WORK\RESEARCH\TokenToModel-Lab`.
- Git checkout `main` tại chính root này. Mọi worktree, chạy thử, dọn dẹp đều **chỉ trong root**; mọi cleanup cần quyền riêng và kiểm tra đường dẫn.
- Không thực hiện `git worktree prune`, `remove --force`, `git clean -fdx` hoặc xóa thư mục vượt ranh giới.
- `main` chỉ nhận thay đổi P00 sau kiểm thử và QA độc lập PASS; bootstrap main chỉ được phép là commit metadata không chứa nguồn P00.
- Xem `docs/WORKSPACE_BOUNDARY.md` và `TTM_P00_INSTALL_README.md` trong bundle.
- Không dùng Research Adapter. RemoteMCP managed worktrees (nếu có) phải theo đúng workspace do project_status trả về.

## Bước tiếp theo

P00: kiểm tra source / diagrams / hashes; chạy QA độc lập trên Windows mục tiêu và pin bằng chứng; chỉ merge sau khi QA độc lập PASS. Sau đó mở P01.
