# TTM P01 D1 — Kế hoạch kiểm tra ACL/đường dẫn chỉ đọc

**Mã:** `TTM_P01_D1_I0A_PATH_ACL_READONLY_COMPLETION_AND_SEPARATE_PERMIT_DECISION`  
**Ngày:** 2026-11-05. **Phạm vi:** thiết kế và quan sát chỉ đọc.  
**Đường GitHub:** `minhtri22/TokenToModel-Lab` / `design/p01-tokenizer-data-prereg-20261105` / PR #4 Draft.  
**Gốc Git:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.

## 1. Bằng chứng đã có

- GitHub `main` giữ nguyên mốc trên; PR #4 vẫn Draft/unmerged, behind=0 khi kiểm tra.
- Qua RemoteMCP `task_list_dir` trên project `TokenToModel-Lab`: `worktrees` chỉ có `p00-source-docs-diagrams-20261105`; `.git/worktrees` chỉ có mục tương ứng P00; `cache` trống, `evidence` có `p00`. Đây là **quan sát danh mục**, không phải ACL hoặc chứng chỉ đường dẫn thực.
- Console do người dùng cung cấp tại `2026-11-05T14:21:38.5319680Z`: main/origin, P00, trạng thái Git sạch, P01 chưa tồn tại và RAM/D: đạt ngưỡng tại thời điểm đo; đã lưu tại `artifacts/qa/p01/TTM_P01_I0A_WINDOWS_READONLY_USER_CONSOLE_20261105T142138Z.txt`.
- **Chưa** đọc được DACL/ACL của `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees`, `.git/worktrees`, `tmp`, `cache`, `evidence` hoặc quyền người thực thi tương lai.

## 2. Giới hạn của phép đọc ACL

`Get-Acl -LiteralPath` lấy security descriptor và DACL của đối tượng có thật; nó **không** tự chứng minh `Effective Access` của tài khoản/nhóm/token bị hạn chế sẽ dùng cho worker I0A, không chứng minh đường dẫn không bị thay đổi sau thời điểm kiểm tra (TOCTOU) và không thể đọc ACL của worktree P01 **chưa được tạo**. Các thư mục hiện hữu có thể mang `ReparsePoint` (junction/symlink). Nếu phát hiện phải HOLD thay vì đi theo để sửa hoặc xóa.

Các đường dẫn cần đọc: `D:\WORK`, `D:\WORK\RESEARCH`, project root, `worktrees`, P00, `.git`, `.git/worktrees`, `tmp`, `evidence`, `cache`, và tên P01 ứng viên. Không dò hoặc sửa các dự án nghiên cứu khác, không thao tác vào root `C:\`.

Nguồn tham khảo:
- https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/get-acl?view=powershell-5.1
- https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-points-and-file-operations

## 3. Chương trình kiểm toán bổ sung (chỉ đọc)

**Tên:** `TTM_P01_I0A_PATH_ACL_READONLY.ps1`  
**SHA-256 trên đúng file chuẩn bị:** `6c21da3ae5da1786c3ac524c6fbb5af2dc6714e6ceec42b77d9ad7ab74a56742`.  
**Chạy:** sau khi xác minh SHA-256 nếu có file, hoặc dán toàn bộ mã đúng nguyên văn vào phiên PowerShell 5.1. **Chưa thực thi trên Windows**.

Hàm đọc Git chỉ gọi `rev-parse`, `remote get-url`, `status --porcelain`, `worktree list --porcelain`. Các phép Windows chỉ là `Get-Item`/`Get-Acl`/`Test-Path`. Không gọi `Set-Acl`, `icacls /grant`, `git clean`, `worktree add/remove`, `Remove-Item`, lệnh mạng hoặc tạo file.

Đầu ra dự kiến: `TTM_P01_I0A_PATH_ACL_READONLY_BEGIN/END`, số ACE/DENY/ALLOW ghi, ACE cho principals phổ biến nếu có, reparse theo từng đường dẫn, `P01_CANDIDATE_ACL=NOT_APPLICABLE_WHILE_ABSENT`, `EFFECTIVE_ACCESS_OF_FUTURE_RESTRICTED_WORKER=NOT_TESTED`, `HOLD_REASON_COUNT`.

**Quan trọng:** Broad write ACE là tín hiệu cần thẩm định, **không** khẳng định quyền ghi có hiệu lực sau khi cân nhắc ACE Deny, group token, inheritance, UAC, integrity level hoặc ACL đặc biệt. Ngay cả khi `PATH_ACL_INVENTORY=PASS_SCOPED_READONLY`, không được tự cấp I0A.

## 4. Tiêu chí phán quyết sau khi nhận console

| Mã | Bằng chứng bắt buộc | Kết luận nếu thiếu |
|---|---|---|
| PA-01 | Root/origin/main/P00 đúng pin, trạng thái Git sạch | HOLD |
| PA-02 | Worktree P01 chưa tồn tại, danh mục worktree đúng phạm vi dự án | HOLD |
| PA-03 | Không có Reparse Point bất thường tại tất cả tổ tiên và đích hiện hữu | HOLD |
| PA-04 | `Get-Acl` đọc được DACL của toàn bộ các thư mục hiện hữu được chỉ định | HOLD |
| PA-05 | ACE có thể cấp quyền ghi cho nhóm phổ biến được báo cáo và thẩm định, không che khỏi biên bản | HOLD nếu có rủi ro chưa thẩm định |
| PA-06 | Không coi ACL của parent là ACL/Effective Access đã được chứng minh của P01 tương lai | Phải giữ QA0 path isolation ở HOLD |
| PA-07 | Không có tác động ngoài workspace/không ghi hoặc dọn dẹp | Nếu có dấu hiệu thay đổi: FAIL_SCOPE |
| PA-08 | Quyết định I0A chính xác theo permit riêng do chủ sở hữu phê duyệt | NOT_GRANTED nếu chưa có |

**Trạng thái lúc soạn:** `PA-01/02=PASS_PRIOR_SCOPED`, `PA-03..05=HOLD_NO_NEW_ACL_CONSOLE`, `PA-06=KNOWN_LIMITATION`, `PA-07=NO_MUTATION_OBSERVED`, `PA-08=NOT_GRANTED`.

**Bước tiếp theo:** thẩm định kết quả ACL do Windows trả về trước khi xem xét phát hành permit I0A với exact HEAD/allowlist; chưa có quyền tạo worktree P01, viết mã, chạy QA, huấn luyện, hợp nhất PR #4 hoặc dọn P00.

## Sửa lỗi công cụ tiền kiểm — 05/11/2026 (chưa chạy lại)

Bản `TTM_P01_I0A_PATH_ACL_READONLY.ps1` với SHA-256 `6c21da3ae5da1786c3ac524c6fbb5af2dc6714e6ceec42b77d9ad7ab74a56742` gặp lỗi `GIT_READ_FAILED:` khi người dùng dán trực tiếp vào PowerShell. **Nguyên nhân trong mã nguồn**: hàm `Read-Git([string]$dir,[string[]]$args)` dùng tên `$args` trùng biến tự động PowerShell, có thể làm mất vector đối số Git; thông báo lỗi in rỗng. Không có bằng chứng cho thấy repository sai, Git bẩn hoặc ACL không hợp lệ.

Bản sửa **V2** đổi tên tham số và biến splat thành `$gitArgs` mà **không đổi các phép kiểm tra hay thêm thao tác ghi**:
- Tên: `TTM_P01_I0A_PATH_ACL_READONLY_FIXED_V2.ps1`.
- SHA-256 chuẩn V2: `be13fd964938c37becffcc548a3de7a442f25776f88991988e5c2d9aae9a5d0a`.
- Bản V1 không được dùng cho lần tiền kiểm tiếp; đây là bản sửa công cụ, **không phải kết quả khoa học**.
- V2 chưa được thực thi trên máy Windows đích, không có console ACL đã được thẩm định; `I0A-02=HOLD`, `I0A_PERMIT=NOT_GRANTED`, `QA0/E0=NOT_GRANTED`.
- Không tự động tạo worktree P01, tải nguồn, huấn luyện, hợp nhất PR #4 hoặc dọn P00.
