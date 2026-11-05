# Quy trình quản trị nhánh, QA, nhật ký và merge

## Vòng đời thay đổi

PROPOSED → BRANCHED → IMPLEMENTED → QA_PENDING → QA_PASS hoặc QA_FAIL → (nếu PASS) REVIEWED → MERGED → BASELINE_LOCKED.

- QA FAIL: không merge; sửa trên nhánh, phát sinh receipt QA mới; FAIL cũ không bị xóa.
- Chưa xác minh: INCONCLUSIVE, không gán PASS.
- Mọi nhánh phát triển từ `main` đã được `fetch` và xác nhận commit HEAD; không được dùng PR cũ làm nguồn lẫn lộn.

## Cổng merge

1. Kiểm tra nguồn gốc: repo path, origin, base/main SHA, branch name, tree status.
2. Cấu hình khóa: config file, hash, model/dataset/tokenizer IDs, Python+Torch+backend, device, seed, commit.
3. Kiểm thử: unit, integration, negative/error, regression, numerical parity theo phạm vi.
4. Báo cáo so sánh: baseline run, candidate run, workload parity; nếu không so được, phải ghi rõ lý do.
5. QA độc lập: bộ kiểm thử tách khỏi mã phát triển; có receipt QA, hash, người/quy trình xác minh.
6. Ghi nhật ký: run receipts bất biến, bảng so sánh, record lineage; thất bại cũng lưu.
7. Merge: qua PR (ưu tiên), kiểm tra branch protection/required review; tạo git tag hoặc release marker cho baseline. Không dùng `--force` hay `rebase` để sửa các bản ghi đã xuất bản.

## Phân loại kết luận

- `QA_PASS`: mã đáp ứng bộ kiểm thử đã định; không đại diện cho hiệu năng hoặc giá trị sản phẩm.
- `EXPERIMENT_PASS`: đạt tiêu chí đo đã định và có baseline tương thích.
- `EXPERIMENT_FAIL`: không đạt; giữ dữ liệu.
- `INCONCLUSIVE`: không đủ bằng chứng hoặc phép đo không tương thích.
- `COMMERCIAL_READY`: chỉ khi có đánh giá độc lập chất lượng, bảo mật, license, dữ liệu, vận hành và tuân thủ liên quan.

## Nhật ký

- `lineage.md`: append-only, mốc quyết định/chuyển trạng thái; gồm kỹ thuật, huấn luyện, QA và nghiên cứu, khác các repo nghiên cứu khác.
- `experiments/runs/<run-id>.json`: receipt bất biến, một run/một file; cấm overwrite.
- `experiments/registry.jsonl`: phụ lục index theo run ID, append-only, gồm hash file receipt.
- `experiments/comparisons/`: biên bản so sánh có điều kiện ngang bằng.
- `artifacts/qa/`: các receipt QA nhỏ được commit; logs nặng/checkpoints/dataset không mặc định commit.

## Quy tắc bằng chứng

File raw nặng lưu kho riêng có kiểm soát, cùng URI/path và SHA256. Không commit API keys, secrets, dataset không được cấp phép, hoặc thông tin người dùng. Đính chính bằng entry mới đề cập entry cũ, không sửa ngầm số đo.

## TTM workspace isolation (P00)

- Canonical root: `D:\WORK\RESEARCH\TokenToModel-Lab` only.
- Worktrees only inside root. Managed RemoteMCP worktrees use the authoritative project-specific path returned by `project_status`, not manually selected paths.
- No deletion/cleanup outside root; no symlink/junction traversal; no `git clean -fdx`, force worktree remove, broad/glob deletion.
- Candidate P00 must remain on its feature branch until Windows QA and independent sign-off; a PASS in a different environment is not transferable.
- A one-file metadata bootstrap on `main` is an exception for establishing the very first ref on an empty GitHub repository. It must not be reported as P00 QA PASS.
