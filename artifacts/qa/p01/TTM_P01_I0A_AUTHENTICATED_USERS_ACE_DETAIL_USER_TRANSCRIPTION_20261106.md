# TTM P01 — Bằng chứng ACE chi tiết do người dùng gửi (bản tổng hợp có nguồn gốc)
 
**Nguồn:** người dùng dán các dòng console PowerShell `PATH_*_ACE_*` trong hội thoại, không đính kèm tệp gốc. **Không phải** biên bản Windows đã ký, không có SHA-256 của toàn bộ console gốc và không được coi là kiểm chứng quyền worker runtime.  
**Thời gian của lần đọc này:** không có dòng `OBSERVED_AT_UTC` trong đoạn console mới, không suy ra thời điểm đọc từ thời điểm nhắn tin.  
**Nhánh lưu hồ sơ:** `design/p01-tokenizer-data-prereg-20261105` / PR #4 (Draft); tuyệt đối không dùng để cấp quyền I0A.

| Mục | Reparse | ACL protected | ACE của S-1-5-11 | ACE 1 | ACE 2 |
|---|---|---|---:|---|---|
| D_WORK | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |
| RESEARCH | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |
| ROOT | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |
| WORKTREES | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |
| P00 | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |
| GIT | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |
| GIT_WORKTREES | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |
| TMP | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |
| EVIDENCE | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |
| CACHE | False | False | 2 | Modify, Synchronize (`1245631`), inherited, effective on current object | `-536805376` (`0xE0010000`), inherited, CI+OI, InheritOnly |

**Thuộc tính chung của 10 mục (từ console):**
- Mỗi mục `PATH_*_AUTHENTICATED_USERS_ACE_COUNT=2`; cả hai `TYPE=Allow`, `INHERITED=True`.
- ACE 1: `INHERITANCE=None`, `PROPAGATION=None`. `Modify, Synchronize` áp dụng trên đối tượng đang đọc; script in `RIGHTS_INT=1245631`.
- ACE 2: `INHERITANCE=ContainerInherit, ObjectInherit`, `PROPAGATION=InheritOnly`, `RIGHTS_INT=-536805376`. Khi diễn giải như số 32-bit không dấu: `0xE0010000`, các cờ tổng quát `GENERIC_READ`, `GENERIC_WRITE`, `GENERIC_EXECUTE`, `DELETE`. ACE 2 không có hiệu lực trực tiếp trên đối tượng hiện tại, nhưng định hướng thừa kế xuống file/subfolder.
- `EFFECTIVE_ACCESS_OF_FUTURE_WORKER=NOT_TESTED`, `I0A_PERMISSION=NOT_GRANTED`, `ACL_MUTATION=NONE`, `WORKTREE_MUTATION=NONE`.
- Đoạn console có `TTM_P01_I0A_ACE_DETAIL_END`; dòng bắt đầu `TTM_P01_I0A_ACE_DETAIL_BEGIN` và `OBSERVED_AT_UTC` **không được cung cấp** trong tin nhắn này.

**Chống suy diễn sai:** một trường `Allow` không đủ để chứng minh một chủ thể riêng có quyền truy cập hiệu lực; cần xét token, DACL đầy đủ, quyền share, ngữ cảnh UAC/restricted token và path resolution. Tuy nhiên `Modify` **không phải** chỉ `WriteAttributes`, mà bao gồm read/write/delete theo .NET `FileSystemRights`; vì vậy đây là bằng chứng quyền rộng đáng kể tại cả P00 và `.git`.

**Nguồn Windows chính thức:**
- https://learn.microsoft.com/en-us/dotnet/api/system.security.accesscontrol.filesystemrights
- https://learn.microsoft.com/en-us/windows/win32/secauthz/ace-inheritance-rules
- https://learn.microsoft.com/en-us/windows/win32/secauthz/dacls-and-aces

Không có thay đổi ACL, không tạo worktree, không chạy checker/guard/corpus/training.
