# P01 D1 — Phân xử console ACL Windows và cổng cấp quyền I0A

**Operation:** `TTM_P01_D1_I0A_PATH_ACL_WINDOWS_CONSOLE_ADJUDICATION`  
**Ngày quan sát:** 2026-11-05T15:01:59.4488197Z (22:01:59 ICT).  
**Nhánh:** `design/p01-tokenizer-data-prereg-20261105`; PR #4 draft.  
**Phạm vi:** đọc console Windows do người dùng cung cấp và rà soát chính sách; không chạy test/mutate local; chưa cấp permit.  
**Nguồn chứng cứ:** `artifacts/qa/p01/TTM_P01_I0A_PATH_ACL_READONLY_USER_CONSOLE_20261105T150159Z.txt`, transcript chép từ hội thoại; **không** có signed node receipt hoặc SHA-256 toàn bộ console gốc.

## 1. Những điều đã kiểm tra thành công

- `GIT_ORIGIN_MATCH=True`, `GIT_MAIN_MATCH=True`, `GIT_REMOTE_MAIN_MATCH=True`, `P00_HEAD_MATCH=True`.
- `ROOT_DIRTY_COUNT=0`, `P00_DIRTY_COUNT=0`, `WORKTREE_COUNT=2`.
- Toàn bộ 10 đường dẫn có thật được script đọc ACL thành công: `D_WORK, RESEARCH, ROOT, WORKTREES, P00, GIT, GIT_WORKTREES, TMP, EVIDENCE, CACHE`.
- Trên 10 đường dẫn ấy: `REPARSE=False`, `ACL_PROTECTED=False`, `ACL_ACE_COUNT=8`, `ACL_DENY_COUNT=0`, `ACL_WRITE_ALLOW_COUNT=4`, `ACL_BROAD_WRITE_COUNT=2`.
- `P01_CANDIDATE_EXISTS=False`; chưa có ACL của P01 ứng viên vì chưa có thư mục. Thông báo `WORKTREE_MUTATION=NONE`, `CLEANUP=NONE`, `WRITES_BY_SCRIPT=NONE`.

## 2. Phản biện bảo mật độc lập

**Rủi ro chung:** cả 10 thư mục đều có 2 ACE `Allow` mang SID `S-1-5-11` (Windows `Authenticated Users`) mà bộ lọc script coi là quyền liên quan đến ghi. 10 cảnh báo không phải 10 lỗ hổng đã được xác nhận; đây có thể là các ACE kế thừa từ cấp trên, nên **không được xóa hay chỉnh sửa ACL của D:\WORK, RESEARCH, P00 hoặc các dự án khác**. `ACL_PROTECTED=False` chỉ cho biết DACL cho phép kế thừa, chưa chứng minh mỗi ACE này thực sự kế thừa.

**Giới hạn của phép kiểm tra:** bộ lọc `writeMask` trong V2 gồm `WriteAttributes`, `WriteExtendedAttributes`, `WriteData`, `AppendData`, `Delete`, `DeleteSubdirectoriesAndFiles`, `ChangePermissions`, `TakeOwnership`. Chỉ số `BROAD_WRITE_COUNT=2` **không nói** mỗi ACE cấp `WriteData` hay `CreateFiles`; phải xem chính xác `FileSystemRights`, `IsInherited`, `InheritanceFlags`, `PropagationFlags`, `AccessControlType` và danh tính token của worker trong tương lai. Việc `DENY_COUNT=0` cũng không tự chứng minh một user sẽ được phép ghi, vì quyền thực tế phụ thuộc token và toàn bộ DACL.

**Tài liệu Microsoft**:
- https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/81d92bba-d22b-4a8c-908a-554ab29148ab
- https://learn.microsoft.com/en-us/windows/win32/secauthz/dacls-and-aces
- https://learn.microsoft.com/en-us/windows/win32/secauthz/how-dacls-control-access-to-an-object
- https://learn.microsoft.com/en-us/windows/win32/ad/access-control-inheritance

**Rủi ro không thể đóng chỉ bằng Get-Acl:** P01 chưa tồn tại, worker trong tương lai chưa có token hạn chế, chưa có bằng chứng rằng worker không thể ghi ngoài thư mục được phép; chưa chứng minh chống TOCTOU hoặc bypass write broker. Do đó không gọi `EFFECTIVE_ACCESS_PASS`.

## 3. Bảng PASS/HOLD/FAIL

| Cổng | Bằng chứng | Phán quyết |
|---|---|---|
| Git origin/HEAD/P00 | Trùng pin, sạch, 2 worktrees | `PASS_OBSERVATION_ONLY` |
| ACL inventory 10 paths | Đọc đủ 10/10, không báo reparse | `PASS_INVENTORY_ONLY` |
| ACL broad-write risk | 10/10 path có SID `S-1-5-11` x2 Allow theo bộ lọc writeMask | **`HOLD_SECURITY_REVIEW`** |
| Path P01 candidate | Không tồn tại | `PASS_NOT_MATERIALIZED`, không có ACL tương lai |
| Actual restricted-worker effective access | Chưa kiểm | **`HOLD_NOT_TESTED`** |
| Tác động ngoài phạm vi | Script báo không ghi/cleanup; không có ký số hệ thống | `PASS_USER_REPORTED_SCOPE` |
| Permit I0A riêng | Chưa được cấp | **`NOT_GRANTED`** |

**Lưu ý:** `PATH_ACL_INVENTORY=HOLD_REVIEW` và `HOLD_REASON_COUNT=10` là kết quả đúng, không phải FAIL của script và không thể tự đổi thành PASS để mở I0A.

## 4. Quyết định cổng I0A

`TTM_P01_D1_I0A_ACL_CONSOLE_ADJUDICATION=COMPLETED_WITH_HOLD`  
`I0A_01_GIT_OBSERVATION=PASS_SCOPED`  
`I0A_02_PATH_ACL=HOLD_AUTHENTICATED_USERS_ALLOW_ACE_REVIEW`  
`I0A_07_CAPACITY=PASS_PRIOR_TIMESTAMPED_SNAPSHOT_RECHECK_BEFORE_PERMIT`  
`I0A_WORKER_EFFECTIVE_ACCESS=NOT_TESTED`  
`I0A_PREAUTH_ADMISSION=HOLD`  
`I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`QA0_EXECUTION_PERMIT=NOT_GRANTED`  
`E0_SCIENTIFIC_PERMIT=NOT_GRANTED`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_DATA_DOWNLOAD_AUTHORIZED=false`  
`P01_TRAINING_AUTHORIZED=false`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`

## 5. Tiếp theo

`TTM_P01_D1_I0A_AUTHENTICATED_USERS_ACE_RIGHTS_READONLY_QUALIFICATION` — đọc chính xác 2 ACE `S-1-5-11` tại mỗi thư mục liên quan, quyền `FileSystemRights`, `IsInherited` và cờ kế thừa; kiểm chứng đường dẫn/thuộc tính vẫn đúng. **Không thay đổi ACL**. Sau đó đề xuất phương án cô lập **bên trong root dự án** cho worker P01 trong một quyết định triển khai riêng, thay vì sửa quyền các thư mục chung.

Không ghi mục khoa học mới vào `lineage.md` cho lỗi/cảnh báo hạ tầng này.
