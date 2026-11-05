# P01 D1 — C09/G04-06: Hợp đồng giới hạn tài nguyên Windows (chỉ thiết kế)

**Mã:** `TTM_P01_C09_WINDOWS_JOB_OBJECT_GUARD_V1_DESIGN`.  
**Môi trường đích:** Windows 11, PowerShell 5.1, dự án `D:\WORK\RESEARCH\TokenToModel-Lab`.  
**Trạng thái:** `DESIGN_CONTRACT_PROPOSED_NOT_IMPLEMENTED_NOT_TESTED`. Không tạo hoặc chạy chương trình, Job Object, child process hay bộ thử tải RAM ở bước này.

## 1. Chọn duy nhất bộ đếm bộ nhớ và giải thích ngưỡng

**Đại lượng dùng để cưỡng chế:** **tổng bộ nhớ ảo đã cam kết của toàn bộ tiến trình trong cùng Windows Job Object (Job-wide Committed Memory)**, không phải RSS/Working Set. Giới hạn chính xác `4 * 1024^3 = 4294967296 bytes` (4 GiB), dự kiến bằng `JOBOBJECT_EXTENDED_LIMIT_INFORMATION.JobMemoryLimit` với `JOB_OBJECT_LIMIT_JOB_MEMORY` trong `BasicLimitInformation.LimitFlags`.

- **Đại lượng hard-limit:** bộ nhớ cam kết toàn job, Windows từ chối cấp phát làm vượt trần. **Không được** gọi nó là RSS. RAM vật lý sử dụng/Working Set, `PrivateBytes` theo từng process và RAM khả dụng máy chỉ là chỉ số quan sát, không thay thế trần job commit.
- **Đo đỉnh:** `JOBOBJECT_EXTENDED_LIMIT_INFORMATION.PeakJobMemoryUsed` qua `QueryInformationJobObject` (đỉnh bộ nhớ của job); đọc cùng limit đã cấu hình trước khi kết luận.
- **Đính chính hợp đồng cũ:** trường `max_peak_rss_bytes=4294967296` ở H05 là một *tên ứng viên chưa khóa và không cùng ngữ nghĩa*. **Không tự đổi tên trong hồ sơ lịch sử**. Với C09 đề xuất trường chuẩn `max_job_commit_bytes=4294967296`; `peak_working_set_bytes` là thông tin phụ, không có quyền thay thế phép đo job commit. Trước khóa khoa học D1 phải phê duyệt thay đổi tên/ý nghĩa bằng quyết định riêng.
- Tài liệu Microsoft mô tả `JOB_OBJECT_LIMIT_JOB_MEMORY` là giới hạn tổng committed memory cho **các tiến trình trong job**; một yêu cầu commit vượt giới hạn sẽ thất bại. **Không** giả định Windows tự động kết thúc toàn job ngay tại sự kiện vượt trần.

Nguồn nền tảng:
- https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information
- https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information
- https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects

## 2. Thứ tự khởi tạo bắt buộc để tránh khoảng trống kiểm soát

Đây là **hợp đồng thao tác API tương lai**, không phải lệnh cho phép thực hiện:

1. Giám sát viên (Supervisor) ở **ngoài job bị kiểm soát** thực hiện kiểm tra workspace/origin/commit và năng lực sử dụng Job Object. Nếu đang bị ràng buộc bởi job cha và không thể tạo hệ thống job lồng hợp lệ, phải **từ chối trước khi chạy**; không dùng đường fallback thiếu giới hạn.
2. `CreateJobObject`; thiết lập `JOB_OBJECT_LIMIT_JOB_MEMORY` và `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, `JobMemoryLimit=4294967296` bằng `SetInformationJobObject` **trước khi tạo worker**. Không bật `JOB_OBJECT_LIMIT_BREAKAWAY_OK` hoặc `JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK`.
3. Dùng `CreateProcessW` với `CREATE_SUSPENDED`, executable và command line đã ghim; **không** dùng `CREATE_BREAKAWAY_FROM_JOB`. Không cho con thừa hưởng job handle hoặc các quyền điều khiển giám sát viên (handle inheritance off, hạn chế duplicate). Process chưa được phép chạy tác vụ khi chưa vào job.
4. `AssignProcessToJobObject` cho tiến trình còn suspended. Kiểm tra kết quả bằng `IsProcessInJob`; xác minh cấu hình giới hạn đã áp dụng và không có hành vi breakaway. Nếu assignment thất bại, tiêu hủy worker suspended và ghi lỗi — **tuyệt đối không ResumeThread**.
5. Chỉ `ResumeThread` sau khi đã ghim job, giới hạn, môi trường `TEMP/TMP` trong workplace, quyền ghi giới hạn và danh tính worker. Mọi tiến trình con phải được kế thừa job hoặc được xác minh gắn job trước khi làm việc.
6. Giám sát viên giữ job handle không kế thừa; khi hết hạn hoặc lỗi, `TerminateJobObject`, đợi `ActiveProcesses=0`, băm/ghi biên bản ở **ngoài** job. `KILL_ON_JOB_CLOSE` là cơ chế hậu thuẫn khi handle cuối được đóng, không là lý do bỏ qua logic chờ/đọc lại.

**Điều kiện thất bại đóng:** worker khởi chạy trước khi được gắn job; tiến trình con ngoài job; một handle Job Object thoát quyền quản lý; job lồng không hợp lệ; không gọi được Win32 API hoặc không chứng minh `IsProcessInJob` cho worker ⇒ `GUARD_NOT_ESTABLISHED`, không cấp phép chạy tiếp.

**Giới hạn thừa kế:** theo Microsoft, tiến trình con tạo bằng `CreateProcess` thường kế thừa job; **không** coi mọi cơ chế tạo tiến trình từ xa (ví dụ WMI `Win32_Process.Create`) tự động được quản lý. Cấm các cơ chế tạo child không có bằng chứng nằm trong job. Nested jobs cần điều kiện riêng.

Nguồn:
- https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs
- https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw
- https://learn.microsoft.com/en-us/windows/win32/procthread/suspending-thread-execution

## 3. Phân loại giới hạn thời gian

- Thời gian cho một lượt chạy là **1.800 giây thời gian thực (Wall-clock Elapsed Time)**, đo bởi giám sát viên ngoài job qua đồng hồ đơn điệu (Monotonic Clock, ví dụ `GetTickCount64` với xử lý hợp lệ). Bắt đầu đếm **trước** khi ResumeThread; khi đạt hạn phải dừng job.
- `JOB_OBJECT_LIMIT_JOB_TIME` là **thời gian thực thi user-mode CPU** của job, không thay thế wall-clock; không dùng để chứng minh 1.800 giây thời gian thực.
- Theo hợp đồng, giám sát viên cũng cần có watchdog/thiết kế giám sát tiến trình cha; nếu timer hoặc supervisor chết mà handle vẫn còn, không thể ghi `WALL_CLOCK_GUARD_PASS`. `KILL_ON_JOB_CLOSE` chỉ hỗ trợ khi handle cuối thật sự được đóng.
- Không có kiểm thử thực tế timeout tại D1. Quyết định I0 cần bằng chứng negative QA để xác minh sai số, thứ tự dừng và không còn tiến trình.

Nguồn về job CPU time: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information

## 4. Giới hạn đĩa là cổng riêng, **không do JobMemoryLimit cưỡng chế**

**Giới hạn ứng viên:** corpus đầu vào ≤64 MiB; số tài liệu ≤2.000; tổng tệp tạm + evidence ≤2 GiB; D: trống trước chạy ≥16 GiB và sau dự phòng ≥12 GiB. Những con số chỉ là đề xuất thiết kế được tiền kiểm trên một ảnh chụp tài nguyên Windows trước đây.

- Windows Job Object **không** tự áp dụng giới hạn số byte ghi tệp 2 GiB. Phải có đường ghi được kiểm soát (Write Broker / File Quota Controller) với tổng byte đã nhận, hạn mức cho từng file, kiểm tra giới hạn **trước mỗi lần ghi**, và từ chối vượt. Không coi việc kiểm tra kích thước tệp sau khi ghi là hard quota.
- Worker phải có quyền hệ thống tệp tối thiểu, chỉ đọc nguồn đã duyệt; các tệp P01 được phép tạo chỉ trong workplace. Cần giải pháp token hạn chế (Restricted Token) / ACL hoặc cơ chế cách ly tương đương đủ để worker **không thể** ghi ngoài broker. Nếu không kiểm chứng được cơ chế cách ly đó trên Windows đích, **I0 vẫn HOLD**, không dùng môi trường `TEMP` làm bằng chứng duy nhất.
- Nếu đường ghi trực tiếp, symlink/junction, file path đi ra ngoài workspace, hoặc tiến trình con/worker có thể bỏ qua broker, cổng bị coi `DISK_GUARD_NOT_ESTABLISHED`.
- Biên bản không được lưu trữ dữ liệu nhạy cảm hay corpus trên GitHub. Giám sát viên chỉ được ghi nhật ký/số đo theo chính sách, không tự dọn worktree P00.

## 5. Oracle kiểm thử âm tính C09 trước khi cấp quyền I0

| ID | Trường hợp giả lập tương lai | Kết quả kỳ vọng và bằng chứng cần có |
|---|---|---|
| W01 | Yêu cầu memory commit tổng job vượt 4 GiB | Hệ điều hành từ chối commit vượt trần; supervisor phân loại `JOB_COMMIT_LIMIT_REACHED` hoặc `INCONCLUSIVE` nếu không xác định nguyên nhân. Không PASS vì không có thông báo bất đồng bộ. |
| W02 | Hai worker trong cùng job, mỗi worker dưới 4 GiB nhưng tổng vượt | Trần job-wide phải chặn; không dùng trần từng process để kết luận. |
| W03 | Child qua `CreateProcess` cố mở rộng bộ nhớ | Child phải nằm trong job và tính vào tổng commit; không xác minh được thì FAIL/HOLD. |
| W04 | Worker thử breakaway / tạo child ngoài job | Phải bị ngăn; nếu child ngoài phạm vi, `GUARD_ESCAPED=FAIL`. |
| W05 | `AssignProcessToJobObject` thất bại ở worker suspended | Không `ResumeThread`, không có tác vụ khoa học, ghi lỗi. |
| W06 | Job ở môi trường đã có job cha không tương thích | `NESTED_JOB_UNSUPPORTED=HOLD`; không chạy fallback. |
| W07 | Thời gian thực chạm 1.800 giây trong lúc worker ngủ | Supervisor dừng job dù CPU time thấp; `ActiveProcesses=0` sau dừng. |
| W08 | Job handle cuối đóng bất thường | `KILL_ON_JOB_CLOSE` phải kết thúc các process thuộc job; không giả định thông báo bảo đảm được chuyển. |
| W09 | Worker cố ghi vượt 2 GiB hoặc bypass broker | Broker từ chối ghi **trước** khi vượt; nếu bypass được, FAIL. |
| W10 | Đường ghi `..`, junction/symlink, UNC hoặc ngoài root | Truy cập/ghi phải bị chặn; không tạo tệp ra ngoài workplace. |
| W11 | RAM/D: trước lượt chạy không đủ, hoặc dữ liệu chưa có quyền | Không khởi chạy worker; giữ `PREAUTH_HOLD`. |
| W12 | Receipt bị thiếu, mất dòng cuối, ghi đè hoặc hash sai | `INCONCLUSIVE_EVIDENCE_FAILURE` hoặc FAIL; không tự đổi ID/lặp lần chạy. |

Giám sát viên phải ghi `job_id`, worker PIDs, API return codes, `GetLastError` khi có, limit flags, `JobMemoryLimit`, `PeakJobMemoryUsed`, wall-clock elapsed, `ActiveProcesses`, nguồn/cấu hình SHA, trạng thái dừng và danh mục file. Chỉ nhận `PASS` nếu tất cả điều kiện liên quan có bằng chứng độc lập và mọi đường ghi nằm trong workspace.

**Lưu ý:** Giới hạn commit có thể làm thao tác cấp phát thất bại trong khi worker tiếp tục chạy. Vì vậy không ghi `RESOURCE_LIMIT_STOP` chỉ dựa trên một sự kiện bất đồng bộ; supervisor phải kiểm chứng trạng thái dừng thực tế, không còn tiến trình, và phân loại `INCONCLUSIVE` nếu không xác định được nguồn lỗi.

## 6. Quyết định C09 ở mức đặc tả

`C09_JOB_WIDE_MEMORY_METRIC=JOB_COMMITTED_BYTES` (ứng viên chuẩn cho phép thẩm định), `MAX_JOB_COMMIT_BYTES=4294967296`, `WALL_CLOCK_LIMIT_SECONDS=1800`.  
`C09_RESOURCE_GUARD_CONTRACT=SPECIFIED_DESIGN_ONLY`.  
`C09_GUARD_IMPLEMENTED=false`, `C09_WINDOWS_NEGATIVE_QA=NOT_EXECUTED`, `C09_I0_PERMIT=NOT_GRANTED`.

Hồ sơ H05 cũ dùng tên `max_peak_rss_bytes` vẫn là lịch sử; hợp đồng tương lai **phải** áp dụng tên mới và phê duyệt nhất quán trong I0, không tráo đổi metric. Không được tự chạy thử tải RAM/đĩa chỉ vì văn bản thiết kế đã đủ.
