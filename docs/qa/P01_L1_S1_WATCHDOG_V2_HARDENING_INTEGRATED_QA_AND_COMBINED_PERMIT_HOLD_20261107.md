# TTM P01 L1 S1 — Khóa tăng cường watchdog V2 và quyết định giấy phép chung

**Ngày:** 2026-11-07  
**Nhánh:** `audit/p01-l1-native-security-critical-fix-20261106`  
**Trạng thái:** `SOURCE_STATIC_PASS` nhưng `NATIVE_PERMIT=HOLD_NOT_ISSUED`.

## 1. Kết quả tiếp nhận

Tiền kiểm Windows PowerShell 5.1 do người dùng thực hiện có mã thoát 0 và `TTM_S1_WATCHDOG_VERDICT=PASS_READONLY_DESIGN_PREFLIGHT_NO_NATIVE`. SCM đã được đọc hai lần và báo `Stopped/PID0`; HEAD gốc, ba marker QA V1–V3, hai binary Broker V3/Worker V4 và nguồn harness S1 khớp. Không chạy lại Python QA V3; biên bản trước xác nhận `41/41`, `16/16`, exit 0, trong khi verdict launcher V3 vẫn giữ `BLOCK`.

**Đầu vào bất biến:** P00, mười kết quả F0, HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, `lineage.md` chỉ nối thêm kết quả khoa học khi được adjudicate, marker đã tiêu thụ, lộ trình P00–P12.

## 2. Nguồn watchdog V2 đã triển khai

| Tệp | Giá trị khóa |
|---|---|
| Nguồn C# | `qa/p01/windows/S1/TTMS1IsolatedJobWatchdogEngineV2.cs` |
| Commit nguồn | `91a0f7b96d6c05321e7f0bd4cafef744b459e4c2` |
| Git blob | `5763ca10025bb928f161a0f33fa493d436107375` |
| SHA-256 | `f8c07f486a4e373810e75ec1cf99d79414f66d7e74c65851d0ff268b949640c3` |
| Kích thước | 21.811 byte UTF-8 |
| QA độc lập (JavaScript, nguồn thuần túy) | **68/68 điều kiện và 24/24 biến thể âm** |
| Biên bản QA | `artifacts/qa/p01/S1_WATCHDOG_V2_INTEGRATED_INDEPENDENT_SOURCE_QA_20261107.json` |
| Biên dịch / thực thi C# | **NOT_EXECUTED** |

Nguồn V2 vẫn cố ý không có hàm `Main()`, không có quyền tự cấp phép, không tạo marker thực thi, không biên dịch/khởi chạy native, không đụng SCM.

### Những thay đổi so với watchdog V1

1. **Job Object gán ngay khi tạo tiến trình:** sử dụng `PROC_THREAD_ATTRIBUTE_JOB_LIST=0x0002000D` cùng `STARTUPINFOEX` và `CREATE_SUSPENDED`. Kiểm tra `IsProcessInJob` trước khi `ResumeThread`. Không còn bước `CreateProcess` rồi mới `AssignProcessToJobObject`. Kết quả này là **kiểm tra nguồn**, không phải bằng chứng tình huống crash đã được kiểm chứng trên Windows. Tài liệu Windows: https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute
2. **Giới hạn tài nguyên:** `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, tối đa 1 tiến trình hoạt động và 256 MiB job committed memory; tối đa 15.000 ms cho S1 và 3.000 ms xác nhận dừng. Nếu vượt hạn hoặc không xác minh được kết thúc: BLOCK.
3. **Giới hạn đầu ra bằng RAM:** stdout/stderr dùng anonymous pipes; chỉ giữ tối đa 8 KiB trong mỗi bộ đệm, phần dư bị loại bỏ và đánh cờ tràn. Không để S1 ghi trực tiếp file stdout/stderr; chỉ nhận đúng ba dòng PASS, exit code 0 và stderr trống.
4. **Thu hẹp khoảng thay đổi EXE sau SHA-256:** mở EXE với `FileShare.Read`, giữ handle đến sau khi tiến trình kết thúc, chặn ghi/xóa theo chia sẻ file Windows trong thời gian bảo vệ. Không tuyên bố bảo vệ trước tác tử đặc quyền ngoài phạm vi.
5. **Kiểm tra cấu trúc P/Invoke:** có fail-closed `Marshal.SizeOf` cho `STARTUPINFOEX`, `PROCESS_INFORMATION`, `JOBOBJECT_*` v.v. trên x64. Chưa được xác nhận bằng biên dịch và thực thi thật.

## 3. Kiểm định tích hợp độc lập

Bộ kiểm định thứ hai dựa trên đúng nội dung GitHub, kiểm tra 68 điều kiện mã nguồn và 24 biến thể âm (bao gồm đổi xử lý thời gian, tắt giám sát đầu ra, bỏ JOB_LIST, bỏ kiểm tra SHA-256, cho phép ghi file EXE, cho phép PID khác, xóa trạng thái BLOCK khi không xác minh được kết thúc). Kết quả: `PASS_WATCHDOG_V2_STRUCTURAL_SOURCE_ONLY_68_68_NEGATIVE_24_24`.

**Giới hạn quan trọng:** Chỉ có bảo đảm rằng các cấu trúc/điều kiện nguồn được hiện diện và biến thể nguy hiểm bị phát hiện ở cấp kiểm tra văn bản. Chưa có thực thi compiler, C# runtime, Windows P/Invoke, lỗi khởi tạo Job Object hoặc negative timeout thật. Không được tự suy ra kết quả PASS runtime từ kết quả kiểm định nguồn.

## 4. Quyết định về một giấy phép native chung

**`HOLD_NOT_ISSUED`** vì hai bằng chứng vẫn chưa có:

- **Bộ điều phối một lượt (one-shot host/runner):** cần nguồn khóa chính xác, xác thực permit và binary/compiler pins, từ chối marker tồn tại, tạo marker nguyên tử (`CreateNew`), biên dịch harness S1 + watchdog host, giới hạn đúng một lần thực thi, giữ receipt PASS/FAIL, readback GitHub bằng SHA-256 và không dọn/xóa ngoài dự án.
- **Kiểm chứng C#5/x64/Win32 trên Windows:** kết quả biên dịch và layout ABI trong nhánh permit tương lai, cùng bằng chứng negative cho timeout/kết thúc/Job Object. Không được coi P/Invoke source assertions là kiểm định thực tế.

Khi hai điều kiện này qua QA nguồn, chỉ **một quyết định cấp phép chung** được xem xét: `exact-source S1 compile + exact-source watchdog host compile + exactly-one isolated S1 native smoke`. Không tách thành giấy phép riêng cho mỗi kiểm tra kỹ thuật nhỏ. Nếu compiler FAIL hoặc các điều kiện fail-closed: dừng luôn, giữ marker và receipt, không chạy lại tự động.

**Không nằm trong permit S1:** biên dịch lại Broker V3/Worker V4, chuyển/khởi động/dừng SCM, các W01–W12, khoa học F0 hoặc mở P02. S1 PASS tương lai cũng không tương đương `NORMAL_STOP=QUALIFIED` hoặc `NATIVE_SECURITY=QUALIFIED`.

## 5. Bước thực hiện tiếp theo duy nhất

`TTM_P01_L1_V3V4_S1_EXACT_SOURCE_ONE_SHOT_NATIVE_HOST_AND_PERMIT_RUNNER_IMPLEMENTATION_STATIC_QA`

Triển khai đúng phần thiếu và kiểm định tích hợp có giới hạn; tái sử dụng Python QA V3, preflight Windows và nguồn V2 đã khóa. Sau đó mới quyết định permit chung, không tạo thêm chuỗi các cổng cấp phép nhỏ.

**Hiện trạng:** `WINDOWS_READONLY_PREFLIGHT=PASS`, `WATCHDOG_SOURCE_V2_STATIC=PASS`, `S1_NATIVE=NOT_EXECUTED`, `SCM_ACTION=NONE`, `P01=OPEN`, `P02=NOT_OPENED`, `NORMAL_STOP=NOT_REQUALIFIED`, `NATIVE_SECURITY=NOT_QUALIFIED`.
