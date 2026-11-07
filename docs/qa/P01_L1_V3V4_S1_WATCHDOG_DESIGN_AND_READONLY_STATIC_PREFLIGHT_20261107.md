# TTM P01 L1 — S1 Native Smoke: thiết kế watchdog và tiền kiểm nguồn (SOURCE ONLY)

**Ngày khóa thiết kế:** 2026-11-07  
**Nhánh QA:** `audit/p01-l1-native-security-critical-fix-20261106`  
**Phạm vi:** Chỉ thiết kế, nguồn tiền kiểm chỉ đọc và kiểm tra tĩnh độc lập. **Không có giấy phép biên dịch S1, không chạy native, không thay đổi SCM, không chạy khoa học.**

## I. Trạng thái đầu vào đã được xác minh

| Điều kiện | Bằng chứng / trạng thái |
|---|---|
| P00 và 10 F0 | Đã khóa, không thay đổi |
| HEAD gốc | `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0` |
| Broker V3 EXE | Biên dịch và SHA-256 readback PASS, không chạy |
| Worker V4 DLL | Biên dịch và SHA-256 readback PASS, không chạy; giữ cảnh báo CS0162 |
| Harness S1 C# | Blob `872c67174c6fbbcea9941fe3bfa0acee3cddfb7c`, SHA-256 `fd179c74fa1a136d791a5f9f6394ea657c58e7a46d1983c0eafa81051e99d6a9` |
| Python QA S1 V3 trên Windows | `PASS_SOURCE_STATIC_NO_NATIVE`, 41/41 positive + 16/16 negatives, exit 0 |
| PowerShell launcher V3 | `BLOCK_WINDOWS_S1_SOURCE_QA`, lỗi `.PSObject.Properties.Count` sau khi Python PASS; không thay đổi thành PASS |
| Receipt Python V3 | Commit `f61af1431ff41c3588657b57828d7928a30c2832`, blob `673d12839b3821820732361b43540ccc5c748ffc`, SHA-256 `52f5f8c896a5306b3f5e3fd4b85b3763a97a193273c49dbe809e5a065efe5c33` |
| Marker V1/V2/V3 | Đã tiêu thụ; preserve, no replay |
| S1 binary | Chưa tạo; không được tạo trong bước này |
| SCM | `TTMP01Broker`: `Stopped` / PID 0 / Manual / LocalService / V2 binary trong receipt V3 |
| P01/P02 | `OPEN` / `NOT_OPENED` |

Không chạy lại Python V3; sử dụng kết quả đã ghi trong receipt.

## II. Bộ tiền kiểm (source-only, read-only)

Nguồn: `qa/p01/windows/S1/Invoke-TTM-P01-L1-S1-Watchdog-ReadOnlyDesignPreflight-PS51.ps1`.

Chỉ hỗ trợ `ReadOnlyPreflight`. **Không có** tham số `ExecuteOnce`, lệnh gọi binary hoặc trình biên dịch. Kiểm tra:

1. Windows PowerShell 5.1, dự án đúng `D:\WORK\RESEARCH\TokenToModel-Lab`, đường dẫn không phải reparse point.
2. HEAD, nhánh và origin của frozen original.
3. SCM phải còn `Stopped/PID0`, chế độ Manual, tài khoản LocalService, đường dẫn binary V2. Quan sát SCM **hai lần**, không tác động.
4. Ba marker QA S1 V1/V2/V3 phải còn nguyên SHA-256.
5. Hash hai binary Broker V3/Worker V4 chỉ đọc; **không kiểm định lại chức năng và không biên dịch lại**.
6. Nguồn S1 C# qua GitHub tại commit bất biến: Git blob + SHA-256 khớp.
7. Biên bản V3: giữ nguyên verdict launcher `BLOCK_WINDOWS_S1_SOURCE_QA`, đọc lại Python `exit 0`, `41/41`, `16/16`, chưa native.
8. Binary S1 chưa tồn tại (đúng trạng thái trước khi quyết định cấp phép), RAM trống >=2 GiB, ổ đĩa đích >=1 GiB.
9. Nếu tất cả PASS, chỉ in `PASS_READONLY_DESIGN_PREFLIGHT_NO_NATIVE` và `EXECUTION=NOT_AUTHORIZED`.

**Giới hạn xác minh:** kiểm tra tĩnh của nguồn PowerShell không thay thế `Parser.ParseFile` trên Windows PowerShell 5.1; trạng thái SCM và RAM/đĩa không thể được khẳng định cho thời điểm khác nếu không có log Windows mới.

## III. Watchdog runtime đích — hợp đồng thiết kế, CHƯA TRIỂN KHAI

S1 chỉ được thực thi trong tiến trình thử nghiệm độc lập, không phải Broker đang cài đặt. Để ngăn tiến trình con thoát khỏi giám sát nếu watchdog chết, phương án ưu tiên là Windows **Job Object**:

1. **Preflight + permit:** hard pin S1 EXE SHA-256, source SHA-256, watchdog binary/hash, GitHub receipt đã kiểm định, permit mới cho đúng một lần. Không đọc hoặc sửa các marker V1–V3. Kiểm tra SCM V2 Stopped/PID0.
2. **Pristine evidence:** output/marker S1 native chưa tồn tại. Tạo marker thực thi bằng `CreateNew` trong đúng workspace TTM trước khi cho chạy; không tự động chạy lại nếu đã tạo.
3. **Containment trước execution:** `CreateJobObject` với `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` và không cho breakaway; `CreateProcessW(...CREATE_SUSPENDED...)` cho **đúng S1 EXE** (đường dẫn tuyệt đối, hash đã khóa), `AssignProcessToJobObject`, chỉ sau đó `ResumeThread`. Nếu bất kỳ API nào lỗi: fail-closed, đóng/thu hồi handle của đúng tiến trình mới, giữ bằng chứng; không động tới service PID.
4. **Thời gian:** tối đa **15.000 ms** cho tiến trình S1, thêm tối đa **3.000 ms** để xác minh termination sau khi timeout; tổng ngân sách watchdog dự kiến <=20.000 ms cộng thời gian preflight/publish riêng. Không đánh đồng 4.000 ms trong harness với timeout giám sát ngoài.
5. **I/O và PASS:** chỉ stdout của tiến trình S1, cap log đề xuất 8 KiB; kiểm tra chính xác, mỗi dòng một lần:
   - `TTM_S1_IDLE_ACCEPT=PASS_COMPLETED_ABORTED`
   - `TTM_S1_SILENT_READ=PASS_COMPLETED_ABORTED`
   - `TTM_S1_VERDICT=PASS_ISOLATED_CANCELLATION_ONLY`
   - exit 0, không có sự kiện I/O bất ngờ hay stderr.
6. **Timeout:** `TerminateJobObject` chỉ trên **Job Object do watchdog tạo**; sau đó phải xác nhận mọi tiến trình thuộc job đã kết thúc. Không dùng `Stop-Process -Name`, không giết theo PID tìm kiếm, không gọi `sc.exe` hoặc `Stop-Service`. Nếu không chứng minh được termination, `BLOCK_TERMINATION_UNCONFIRMED`, không khởi chạy tiếp, không tự động dọn evidence.
7. **Kết thúc:** đóng handle, xác minh SCM V2 vẫn Stopped/PID0, ghi kết quả PASS/FAIL và timestamp, exit code, SHA-256 stdout/stderr, marker, PID/creation time cùng cấu trúc bằng chứng vào đúng dự án. Công bố và readback GitHub theo SHA-256; nếu thiếu bằng chứng hoặc readback thất bại thì không được nhận PASS.

Hợp đồng này **không** được coi là đã có watchdog runtime hoạt động. Bản hiện tại chỉ có tiền kiểm chỉ đọc; chưa có Job Object executable và chưa chạy thử termination paths. Một lỗi trong `AssignProcessToJobObject` hoặc khoảng cách giữa launch và assign phải là BLOCK. Vì vậy launch suspended-before-assign là điều kiện bắt buộc của thiết kế, không thay bằng `Process.Start` rồi mới assign.

Nguồn tham khảo:
- Windows Job Objects và kill-on-close: https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
- AssignProcessToJobObject: https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject
- CancelIoEx chỉ yêu cầu hủy: https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex

## IV. Phạm vi một lượt S1 khi tương lai được cấp phép

**Một** lượt gồm hai tình huống của cùng harness, không phải hai lượt riêng:

| Case | Kỳ vọng | FAIL / BLOCK |
|---|---|---|
| IDLE_ACCEPT | Hủy accept đang chờ, bắt completion và Win32 995 | Kết nối thành công bất ngờ, timeout, không hủy |
| SILENT_READ | Client cục bộ kết nối nhưng không gửi dữ liệu; hủy read, completion và Win32 995 | Có dữ liệu, timeout, sai trạng thái kết thúc |
| Watchdog | Tiến trình và job bounded; stdout exact; exit 0; SCM không đổi | Bất kỳ timeout, Job Object fail, output thiếu, child leak, SCM changed |

Đây là **toy isolated runtime smoke**; kể cả S1 PASS, vẫn không được coi là Broker V3 normal-stop PASS hoặc Worker V4 native-security PASS. S2–S5 cần cổng thực thi riêng theo kết quả thực tế.

## V. Quyết định hiện tại và hành động tiếp theo

- `S1_WATCHDOG_DESIGN=SPECIFIED`.
- `S1_WATCHDOG_READONLY_PREFLIGHT_SOURCE=IMPLEMENTED`.
- `S1_WATCHDOG_SOURCE_INDEPENDENT_STATIC_AUDIT=PASS_31_31_NEGATIVE_16_16` (thực hiện qua kiểm định văn bản/JS độc lập).
- `S1_WATCHDOG_WINDOWS_PS51_PARSE=NOT_EXECUTED`.
- `S1_WATCHDOG_TARGET_WINDOWS_PREFLIGHT=NOT_EXECUTED`.
- `S1_JOB_OBJECT_NATIVE_WATCHDOG=NOT_IMPLEMENTED`.
- `S1_EXECUTION_PERMIT=NOT_ISSUED`, `S1_CSC=NOT_EXECUTED`, `S1_NATIVE=NOT_EXECUTED`.
- `NORMAL_STOP=NOT_REQUALIFIED`, `NATIVE_SECURITY=NOT_QUALIFIED`, `P01=OPEN`, `P02=NOT_OPENED`.

**Bước thực hiện tiếp theo:** `TTM_P01_L1_V3V4_S1_WATCHDOG_WINDOWS_READONLY_PREFLIGHT_AND_JOB_OBJECT_EXECUTION_DESIGN_LOCK`. Kiểm tra cú pháp PowerShell 5.1 và chạy tiền kiểm **chỉ đọc** trên máy Windows; hoàn thiện nguồn watchdog Job Object trong cùng nhóm công việc kỹ thuật, kiểm định tĩnh, sau đó mới xét **một quyết định permit chung** cho biên dịch S1 và chạy một lượt native. Không đặt thêm permit riêng cho mỗi kiểm tra nhỏ.

Bảo toàn P00, 10 F0, HEAD, `lineage.md` append-only, tất cả biên bản FAIL/PASS, marker tiêu thụ và kiến trúc P00–P12.
