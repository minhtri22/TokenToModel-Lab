# P01 C09 — Rà soát triển khai Windows Job Object / Write Broker và QA âm tính độc lập

**Mã công việc:** `TTM_P01_QA0_WINDOWS_SECURITY_GUARD_IMPLEMENTATION_AND_INDEPENDENT_NEGATIVE_QA_DESIGN`  
**Ngày:** 2026-11-06. **Repo:** `https://github.com/minhtri22/TokenToModel-Lab`.  
**Nhánh triển khai:** `implementation/p01-i0a-s-f0-static-20261106`. **HEAD sau hoàn thiện tĩnh:** `b793191932d794e53d88e275a45bad571750a9c3`; **base trước khi viết:** `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.  
**Nhánh thiết kế:** `design/p01-tokenizer-data-prereg-20261105` trên PR #4 Draft.  
**Quyết định:** `C09_SOURCE_REVIEW=PASS_SCOPED_WITH_OPEN_NATIVE_GAPS`; `WINDOWS_C09_RUNTIME_QUALIFICATION=HOLD`.

## 1. Đối chiếu nguồn và bằng chứng

Đặc tả chuẩn gốc: `docs/p01/P01_D1_C09_G04_06_WINDOWS_JOB_OBJECT_GUARD_DESIGN_20261105.md`. Giới hạn **job-wide committed memory**, không phải RSS, là **4 GiB = 4294967296 bytes**; tường minh `JOB_OBJECT_LIMIT_JOB_MEMORY` và `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`; không cho phép breakaway; chỉ ResumeThread sau khi tạo suspended, gắn Job Object, kiểm tra thành viên và quyền filesystem. 2 GiB quota ghi tệp là cổng riêng; không thể do Job Object cưỡng chế.

Rà soát độc lập qua GitHub ở `b7931919...`:
- So với `f2e333df...`: **2 commit tăng, 0 commit sau nhánh gốc**, đúng **4 đường dẫn** P01 (2 sửa, 2 thêm). Không ghi đè P00/main/config P00, `lineage.md`.
- Source guard `runtime/p01/windows_job_guard.py` đã có cấu trúc `ctypes` của Win32 `JOBOBJECT_EXTENDED_LIMIT_INFORMATION`, `CreateJobObjectW`, `SetInformationJobObject`, `QueryInformationJobObject`, `AssignProcessToJobObject`, `IsProcessInJob`, `TerminateJobObject`, `TerminateProcess`, `WaitForSingleObject`, kiểm tra flags/memory readback và lỗi gắn process. Khi lỗi attach/query/membership, mã yêu cầu hủy tiến trình và đợi kết thúc; nếu timeout không được coi là thành công. Tất cả là **source chưa kiểm thử API Windows**.
- Source broker `runtime/p01/write_quota_broker.py` có kiểm tra đầu vào, đường dẫn Win32, reserved device name, ADS, UNC, `..`, collision case-insensitive và trần 2 GiB **trước ghi**. Hiện chỉ là `QuotaLedger` **dry-run**, không mở tệp.
- Bộ QA `qa/p01/independent_windows_guard_policy_negative.py` chứa đúng **12 test methods**: 9 trường hợp chính sách và 3 bộ giả lập kernel lỗi assignment, membership, thời gian chờ kết thúc. Đây là bộ kiểm tra **chính sách**, KHÔNG phải 12 kiểm thử Windows `W01..W12` của đặc tả C09; không được gộp tên hay khẳng định W01..W12 PASS.
- `start_worker()` luôn `GuardNotEstablished`; `write_file()` luôn `BrokerUnavailable`. Không có tiến trình worker, không ghi tệp, không mở corpus theo mã mới.

**Kết quả kiểm tra bằng cấu trúc/đọc lại GitHub:** `SOURCE_SCOPE_READBACK=12/12 PASS` (bao gồm HEAD, base, đúng 4 path, cờ limit, API biểu thị trong source, 12 test và các đường từ chối). Đây là kiểm toán **tĩnh**, không phải Python AST/dynamic QA PASS.

## 2. Ranh giới bảo mật chưa đạt

1. Chưa có tuyến `CreateProcessW(CREATE_SUSPENDED)` với restricted-token/AppContainer đáng tin cậy, kiểm chứng parent/nested job và thủ tục ResumeThread an toàn. Hàm `attach_suspended(..., suspended=True)` hiện nhận khẳng định của caller, **không tự chứng minh thread suspended**; phải được bọc bởi một supervisor đã chứng thực.
2. Chưa có một broker OS-level độc lập với worker, directory-handle-based `CREATE_NEW`, chống symlink/reparse TOCTOU, quota nguyên tử khi nhiều worker ghi và giới hạn quyền filesystem thực. Việc nhận đường dẫn hợp cú pháp không chứng minh containment. ACL `Authenticated Users: Modify` ở vùng dự án không tự mất hiệu lực.
3. Chưa có watchdog thời gian thực đơn điệu, `ActiveProcesses=0`, lifecycle process tree, kill-on-close và receipt JCS được đo/chứng minh ở runtime.
4. Chưa chạy Windows API thực tế hoặc 12 trường hợp W01..W12; không có bằng chứng kernel readback/LastError/active-child trên máy đích.
5. Chưa đồng bộ worktree Windows P01 với hai commit C09 mới; **cấm reset/clean/force**. Việc RemoteMCP Core đang có project TTM dạng `NON_GIT` không được dùng để lách thao tác worktree ngoài managed route.

## 3. Kế hoạch QA nguồn an toàn (không phải QA0 bảo mật)

Đã chuẩn bị script PowerShell 5.1 `TTM_P01_C09_SAFE_SYNC_AND_NEGATIVE_POLICY_QA_20261106.ps1`, SHA-256 `0e1f0cd70bb0897bcab89497c48a9489852dfe04e1f8607bbca0e91a8b8764d9`, giao cho người dùng chạy khi cần. Script chặn sai máy/origin/SHA, P00/root/P01 bẩn, worktree khác 3, reparse tổ tiên. Chỉ từ `f2e333df...` tiến nhanh đến `b7931919...` sau khi xác thực đúng 2 commit/4 path; không dọn. Sau đó AST bằng Python `-I -S -B -`. Mặc định không import/execute P01; nếu chủ dự án **tự bật** `-RunPurePolicyQA`, script chạy đúng 12 test mô phỏng và chính sách, không đụng API Job Object/ghi đĩa. Nhật ký in console, chưa tự upload lên GitHub; chủ sở hữu phải cung cấp console làm bằng chứng. Không chạy lại smoke F0 đã PASS.

**Giới hạn về an toàn:** chế độ `-RunPurePolicyQA` có nhập code Python P01 để kiểm tra thuần chính sách, nên chỉ dùng sau tiền kiểm exact SHA; không thay thế môi trường Windows cô lập cho QA0/W01–W12.

## 4. Tiến độ W01–W12

Các tiêu chí độc lập còn yêu cầu: W01 job memory commit, W02 cộng dồn 2 worker, W03 child inheritance, W04 breakaway, W05 attach fail trước resume, W06 parent job không tương thích, W07 watchdog wall-clock, W08 close handle, W09 quota vượt/bypass, W10 junction/UNC/ADS/TOCTOU, W11 tài nguyên và quyền nguồn, W12 receipt thiếu/giả. Tất cả **`NOT_EXECUTED`**. Tuyệt đối không thử cấp phát 4 GiB RAM/đĩa trên notebook để mở cổng mà chưa có kế hoạch tài nguyên và quyền riêng.

## 5. Phán quyết

`P01_C09_SOURCE_GUARD_IMPL=PARTIAL_NATIVE_PRIMITIVES`  
`P01_C09_SOURCE_BROKER_IMPL=DRY_RUN_PREWRITE_POLICY`  
`P01_C09_INDEPENDENT_POLICY_QA=12_SOURCE_PREPARED_NOT_EXECUTED`  
`P01_C09_GITHUB_STATIC_REVIEW=PASS_12_OF_12`  
`P01_C09_LOCAL_WINDOWS_SYNC=PENDING`  
`P01_C09_WINDOWS_JOB_SECURITY=NOT_ESTABLISHED`  
`P01_C09_WINDOWS_FILE_WRITE_ISOLATION=NOT_ESTABLISHED`  
`P01_C09_W01_W12=NOT_EXECUTED`  
`P01_C09_WINDOWS_QA0_EXECUTION=HOLD`  
`P01_F0_FUNCTIONAL_OFFHOST=PASS_10_OF_10_UNCHANGED`  
`P01_MAIN_P00_LINEAGE=UNCHANGED`  
`P01_GIT_MERGE_OR_CLEANUP=NONE`.

**Bước thực hiện tiếp theo:** `TTM_P01_C09_WINDOWS_SAFE_SYNC_AND_INDEPENDENT_POLICY_QA` — chủ sở hữu chạy script chỉ đọc / fast-forward có guard; gửi console. Sau đó riêng biệt `TTM_P01_C09_RESTRICTED_WORKER_BROKER_NATIVE_COMPLETION_AND_W01_W12_PREFLIGHT`. Không tự kích hoạt QA0 Windows, không huấn luyện.
