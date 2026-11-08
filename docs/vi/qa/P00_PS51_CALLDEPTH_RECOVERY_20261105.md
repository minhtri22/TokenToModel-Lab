# P00 — Phục hồi lỗi tràn độ sâu gọi hàm (CallDepthOverflow) trong QA Windows PowerShell 5.1 — 05/11/2026

> **Bản dịch tiếng Việt của hồ sơ lịch sử.** Giữ nguyên [tài liệu gốc](../../qa/P00_PS51_CALLDEPTH_RECOVERY_20261105.md) và toàn bộ phán quyết, mã băm, mã commit. Bản dịch không thay thế biên bản chạy Windows.

## Phân loại (Classification)

- **Loại lỗi:** lỗi hạ tầng/bộ chạy kiểm thử (Infrastructure / QA Harness Failure), **không phải** kết quả nghiên cứu khoa học mô hình.
- **Nguồn:** nhật ký cửa sổ lệnh (Console) Windows PowerShell 5.1 do người dùng cung cấp.
- **Bộ chạy trước:** `scripts/TTM_P00_WINDOWS_QA.ps1` tại commit `24223818af8b05e5546462eb759c591a083ab202`.
- **SHA-256 trước đó:** `60be1d43a857a643d39388533f870ec967b7b84dff456b0a51e83a4dadf68548`.
- **Ngoại lệ quan sát được:** `CallDepthOverflow,TTM_P00_WINDOWS_QA.ps1`.
- **Chưa có kết quả QA Windows hợp lệ** từ lượt lỗi này; không được hợp nhất mã (Merge).

## Chẩn đoán (Diagnosis)

PowerShell tìm và phân giải tên lệnh **không phân biệt chữ hoa/chữ thường**. Khi chương trình khai báo `function Git(...)`, tên hàm này che khuất lệnh ngoài `git` trong cùng script. Lệnh gọi `& git ...` vì vậy lại gọi chính hàm `Git`, dẫn đến **đệ quy vô hạn (Infinite Recursion)** và tràn độ sâu gọi.

Lỗi thứ hai: khi truyền mảng đối số vào hàm PowerShell, mã cũ dùng cách bung mảng theo vị trí (Positional Array Splatting), thay vì gắn rõ vào tham số mảng `[string[]]` của hàm.

## Cách khắc phục (Repair)

- Đổi tên hàm thành `Invoke-TtmGit` và `Invoke-TtmGitWorktree`.
- Xác định `git.exe` là chương trình bên ngoài (External Application) bằng `Get-Command -CommandType Application`.
- Gọi **đúng đường dẫn chương trình thực thi** thay vì tên `git` có thể bị nhầm.
- Gắn mọi mảng đối số của hàm phụ bằng tham số `-GitArgs @( ... )`.
- Giữ nguyên không gian làm việc chuẩn (Canonical Workspace), nhánh, nguồn lịch sử, quy tắc không dọn dẹp và không hợp nhất.
- Bổ sung kiểm thử hồi quy tĩnh độc lập (Independent Static Regression Checks) trong `tests/test_windows_bootstrap_static.py`.

## Bằng chứng và điều kiện còn mở (Evidence and Remaining Gate)

Kiểm tra tĩnh mã nguồn (Static Source Checks) và kiểm thử hồi quy Python cục bộ đã PASS trong môi trường biên soạn. Những kết quả đó **không thay thế** việc chạy trực tiếp Windows PowerShell 5.1 hoặc QA Windows độc lập.

Sau khi lấy bộ chạy đã sửa từ commit được ghim và đối chiếu SHA-256, chỉ tiếp tục **đúng mục đích kiểm tra P00 ban đầu**. Không xóa, dọn nhánh (Prune) hoặc tạo lại bất kỳ cây làm việc Git (Git Worktree) nào đã tồn tại. Nếu cây làm việc đúng đường dẫn đã có, phải dừng để thẩm định trạng thái độc lập, không dùng thao tác cưỡng bức (Force).
