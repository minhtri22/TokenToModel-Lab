# TTM T5 — TCP table ownership guard V3 · mã nguồn chỉ đọc (source-only)

**Không chạy Ollama, không import GGUF, không tạo hoặc tái sử dụng lượt thực nghiệm trong bước này.**

## Mục tiêu

Sửa bộ kiểm tra sẵn sàng của ứng viên chạy Ollama kế nhiệm T5 sau khi V1 và V2 dừng vì `netstat -p TCP` không quan sát thấy listener. Trên dịch vụ Ollama hiện có, người dùng thấy `netstat -p TCP` và `-p TCPv6` đều không trả dòng, nhưng `Get-NetTCPConnection` xác nhận PID 14464 và `/api/version` trả HTTP 200.

## Thiết kế đã thực hiện

- Lấy toàn bộ trạng thái TCP bằng `Get-NetTCPConnection -ErrorAction Stop`, lọc cổng chuyên dụng trong PowerShell 5.1, trích xuất `LocalAddress`, `LocalPort`, `State`, `OwningProcess` và xác minh danh tính bằng `Get-CimInstance Win32_Process`.
- Bắt buộc có `State=Listen`, đúng PID tiến trình riêng; đường dẫn executable phải đúng đường dẫn Ollama đã ghim, tên `ollama.exe` và thời điểm tạo tiến trình phải còn ổn định.
- Chỉ chấp nhận `127.0.0.1` hoặc `::1`, từ chối `::` (IPv6 wildcard), `0.0.0.0`, IPv4-mapped và các địa chỉ không đúng loopback.
- Nếu PID sai, nhiều PID, thiếu trạng thái, thiếu danh tính, tên executable sai hoặc backend TCP lỗi, dừng (`HOLD`), **không gửi HTTP**. Chỉ gửi GET `/api/version` trực tiếp (không proxy) sau kiểm tra PID, yêu cầu HTTP 200 và phiên bản chính xác. Đọc lại TCP table sau HTTP để phát hiện PID/địa chỉ/thời điểm tạo tiến trình thay đổi.
- Từng quyết định được ghi trong JSONL, mở mới độc quyền (`x`) và `fsync()` trước bước tiếp. Giữ kiểm tra PID ở các giai đoạn sau import/generate trong mã nguồn kế nhiệm.
- Không dùng `netstat` để chấp nhận/từ chối trạng thái cổng. Không sửa `PATH`; cảnh báo `ggml-base.dll` vẫn là giả thuyết môi trường, không phải kết luận nguyên nhân.

## Bất biến an toàn

- Ứng viên V3 được đặt tên riêng: `_tmp/ttm_t5_ollama_compat_only_single_v3`, cổng 12645, model `ttm-t5-f32-compat-only-v3:latest`; chỉ là **dự thảo**, chưa được cấp quyền chạy.
- `t5_ollama_smoke_v3_candidate.py` có khóa cứng `V3_SOURCE_ONLY_EXECUTION_LOCK_NO_RUNTIME_PERMIT`. Cổng CLI chỉ cho phép `--mode contract`; **không có `--mode execute` được chấp nhận**. Không chỉnh khóa này để chạy mô hình.
- GGUF gốc SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, số token 32, ngữ cảnh 256, yêu cầu lưu trong project, kết quả strict parity FAIL 7/8 và V1/V2 đã tiêu thụ đều được giữ nguyên.

## Kiểm định độc lập

Bộ `test_independent_tcp_owner_guard_v3.py` có **60 trường hợp giả lập** gồm PID đúng/sai, hai họ IP, `::` wildcard, IPv4-mapped, `Bound/Established`, thiếu `State`, CIM path sai, thời điểm tạo tiến trình đổi, HTTP 503/JSON sai/version sai, TCP snapshot thay đổi sau HTTP, trace độc quyền và khóa execution. Không dùng Ollama, không chạy PowerShell, không mở socket thật. Ở Windows, mọi file tạm do QA tạo được giới hạn trong `_tmp` của TTM và tự dọn thư mục QA đó.

## Chạy QA tĩnh trên Windows (không cần chạy ở bước này nếu chưa muốn)

1. Giải nén ZIP thành thư mục mới bên trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp` (không đè bản cũ).
2. Chạy `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <duong_dan>\Check-TTM-T5-TCP-Guard-V3-PS51.ps1`.
3. Chỉ `T5_V3_WINDOWS_STATIC_QA=PASS_60_OF_60` mới là QA tĩnh; không đồng nghĩa đã xác minh PowerShell TCP table thật trên Windows, và **không** phải model compatibility PASS.

## Giới hạn còn lại

- Kiểm thử mock độc lập không thay thế thử native trên Windows. `Get-NetTCPConnection` / CIM chưa được chạy bởi gói này. Cần kiểm tra cú pháp PowerShell 5.1 native và nhận dữ liệu TCP table **chỉ đọc** trước khi cân nhắc lượt Ollama V3.
- Chưa xác định nguyên nhân của việc `netstat` không thấy cổng 11434/12644; không suy luận nguồn lỗi thuộc GGUF hoặc Ollama.
- Tuyệt đối không sửa/xóa thư mục V1/V2, `main`, `lineage.md`, checkpoint hoặc GGUF.

**Bước thực hiện tiếp theo:** `TTM_T5_TCP_OWNER_GUARD_V3_WINDOWS_STATIC_QA_AND_TCP_TABLE_READONLY_READBACK`. Sau đó mới có quyết định riêng về một lượt smoke mới, không cấp quyền mặc định.
