# P01 D1 — Danh mục nơi làm việc và tệp I0A dự kiến (Allowlist), chưa cấp quyền tạo

**Mã:** `TTM_P01_I0A_F0_STATIC_WORKPLACE_ALLOWLIST_V1_DESIGN`  
**Thời điểm:** 05/11/2026. **Trạng thái:** `PROPOSED_ONLY_NOT_MATERIALIZED`.  
**Repository:** `https://github.com/minhtri22/TokenToModel-Lab.git`.  
**Local root chính xác:** `D:\WORK\RESEARCH\TokenToModel-Lab`.

## 1. Ranh giới bắt buộc

Mọi thư mục Git worktree, mô-đun được cấp phép tương lai, fixture, cache, temp và receipt phải nằm **bên trong** local root của dự án; tuyệt đối không có thao tác chỉnh sửa, xóa hoặc cleanup ngoài root. Tại D1, **không có đường dẫn nào trong bảng bên dưới được tạo**.

| Hạng mục | Đường dẫn hoặc phạm vi | Tình trạng hiện tại |
|---|---|---|
| Main hiện hữu | `D:\WORK\RESEARCH\TokenToModel-Lab` | Chỉ đọc, không chạm source/config P00 |
| Worktree P00 hiện hữu | `worktrees\p00-source-docs-diagrams-20261105` | Bảo vệ, không xóa hoặc cập nhật HEAD |
| **Worktree P01 ứng viên** | `worktrees\p01-f0-static-i0a-20261105` | `CANDIDATE_ONLY` — **cấm tạo khi chưa có permit riêng** |
| Dữ liệu gốc P00, evidence P00 | `evidence\p00\`, worktree P00 | Đọc đúng tài liệu/biên bản, không sửa/ghi đè |
| Evidence P01 ứng viên | `evidence\p01\` | Chỉ được phép ghi trong giai đoạn có permit riêng, với tên create-new |
| Temp/cache P01 ứng viên | `tmp\p01\`, `cache\p01\` | Chưa tạo, không cleanup |
| Corpus F1/F2 | Mọi đường dẫn `datasets\approved_sources\` hoặc bên ngoài | `DENIED` cho I0A F0-only; không tải hoặc đọc |

**Nghiêm cấm:** `git worktree add/remove/prune`, `git clean`, `reset --hard`, force push, xóa/move/ghi đè P00, tải corpus, huấn luyện, thay cấu hình P00, dùng Docker/WSL ghi ngoài root, thao tác vào workspace nghiên cứu khác.

## 2. Danh mục tệp được cân nhắc cho một permit I0A tương lai

Các tệp dưới đây là **đích dự kiến trong worktree P01 ứng viên**, không phải tệp đã tồn tại hoặc quyền được cấp:

| Đường dẫn tương đối bên dưới worktree ứng viên | Trách nhiệm | Phạm vi trong I0A nếu được cấp |
|---|---|---|
| `qa/p01/f0_fixture_generator.py` | Sinh đúng fixture từ hex/SHA đã ghim; không tải hoặc đọc nguồn ngoài | Viết mã và static QA |
| `qa/p01/independent_checker.py` | Checker độc lập, kiểm oracle byte/BPE/split/merges | Viết mã riêng, không gọi hàm của generator làm oracle |
| `qa/p01/checker_contract_cases.py` | Danh sách C01–C10, A/M/K, lỗi và ca âm tính | Chỉ xác minh cấu trúc/static |
| `runtime/p01/windows_job_guard.py` | Giao diện supervisor Windows Job Object, chặn trước ResumeThread | Viết mã, **không chạy Job Object trong I0A** |
| `runtime/p01/write_quota_broker.py` | Thiết kế quyền ghi tối thiểu và quota 2 GiB | Chỉ tệp mã, không tạo file lớn |
| `runtime/p01/source_scope_guard.py` | Từ chối F1/F2, TEST khoa học, path ngoài root | Không mở đọc nguồn |
| `runtime/p01/evidence_manifest.py` | JCS manifest, create-new, SHA đọc lại | Chưa tạo receipt chạy thật |
| `configs/p01_f0_static_i0a.json` | Cấu hình ứng viên: `max_job_commit_bytes=4294967296`, wall 1800s, source F0-only | Không sửa `configs/phase0_reference.json` |
| `qa/p01/golden_vectors.json` | Chứa các vector nguyên bản đã được duyệt, không có corpus | Chỉ nguồn static test (nếu permit) |
| `docs/qa/P01_I0A_STATIC_IMPLEMENTATION_REVIEW.md` | Hồ sơ QA tĩnh ở nhánh kế nhiệm | Chỉ sau khi có mã và biên bản đủ điều kiện |

**Deny-by-default:** bất kỳ file nào khác, đặc biệt `src/model/**`, `tokenizer_train*.py`, `trainer/**`, `datasets/**`, `models/**`, `checkpoints/**`, `.git/hooks/**`, `lineage.md` bị sửa thay vì append, đều nằm ngoài phạm vi I0A F0. Danh mục mới chỉ là **ứng viên**; trước permit phải rà soát va chạm với cây nguồn thực tế và ghim SHA của hợp đồng.

Không được sửa/ghi file trong root main để “tiện” cho việc triển khai; chỉ cân nhắc worktree ứng viên sau khi được chủ sở hữu cấp quyền rõ ràng. Không tạo worktree chỉ để kiểm tra sự tồn tại.

## 3. Kiểm tra đường dẫn từ chối thoát root

Trước khi cấp quyền I0A, phải đọc và chặn:
- đường dẫn có `..`, UNC, ổ đĩa khác hoặc đường dẫn tuyệt đối ngoài `D:\WORK\RESEARCH\TokenToModel-Lab`;
- junction/symlink/reparse-point ở root, `worktrees`, đường dẫn worktree ứng viên và các thành phần tổ tiên;
- đường dẫn trùng nhau sau chuẩn hóa chữ hoa/thường của NTFS, ký tự phân cách, tên bị cấm, tên cùng tồn tại và file đã tồn tại bị ghi đè;
- `git worktree list --porcelain` báo worktree không thuộc root, hoặc số lượng/tham chiếu không khớp biên bản đã ghim;
- tình trạng `git status` bẩn/tracked modifications hoặc untracked **xung đột** với tệp sẽ tạo; không được dùng `git clean` để làm sạch.

Nếu môi trường không đủ khả năng chứng minh đường dẫn an toàn hoặc thiếu permission ⇒ `I0A_PATH_SCOPE_HOLD`, không thực thi, không thử ở vị trí ngoài root.

## 4. Ranh giới quyền mạng và nguồn

Trong I0A F0-only, mọi đường tải corpus và gói Python, mô hình, cache từ mạng đều **không mặc định được cấp**; pin dependency và môi trường nguồn trước permit. Git chỉ được thao tác theo quy trình chính xác có kiểm tra SHA, không force push hoặc fetch nhằm mở rộng phạm vi. Nguồn F0 là đặc tả, không phải dữ liệu để học BPE hoặc đánh giá chất lượng tiếng Việt.

## 5. Trạng thái

`I0A_PROPOSED_WORKTREE_PATH=worktrees/p01-f0-static-i0a-20261105`  
`I0A_FILES_ALLOWLIST=SPECIFIED_DESIGN_ONLY`  
`I0A_PATH_EXISTENCE_COLLISION_CHECK=NOT_COMPLETED_ON_WINDOWS`  
`I0A_REPARSE_AND_GIT_STATUS_CHECK=NOT_COMPLETED_ON_WINDOWS`  
`I0A_FILESYSTEM_MUTATION_AUTHORIZED=false`  
`I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`I0A_WORKTREE_CREATION_AUTHORIZED=false`  
`I0A_CLEANUP_AUTHORIZED=false`

**Bước tiếp theo:** đọc trạng thái Windows bằng preflight chỉ đọc, thẩm định va chạm và chốt exact permit ở quyết định **riêng**, không tự cấp quyền trong D1.
