# TTM T5 — Phán quyết Windows TCP ownership sau kiểm tra TCPv6 (2026-11-09)

## Phạm vi và nguồn
Người dùng thực hiện một phép kiểm tra PowerShell **chỉ đọc** trên Ollama hiện có (cổng 11434), không khởi động/dừng dịch vụ. Bằng chứng được đối chiếu với kết quả kiểm tra TCP/HTTP và biên bản V1/V2 đã khóa. Đây là QA hạ tầng, **không** phải kiểm thử mô hình hoặc dữ liệu TRAIN/TEST.

## Quan sát trực tiếp
| Phương thức | Kết quả |
|---|---|
| `netstat.exe -ano -p TCP`, lọc cổng 11434 | 0 dòng |
| `netstat.exe -ano -p TCPv6`, lọc cổng 11434 | 0 dòng |
| `Get-NetTCPConnection -LocalPort 11434` | PID `14464`, địa chỉ `::` |
| `Get-CimInstance Win32_Process` | `ollama.exe` từ `C:\Users\minht\AppData\Local\Programs\Ollama\ollama.exe` |
| Kiểm tra trước đó TCP `127.0.0.1:11434` | PASS |
| Kiểm tra trước đó `/api/version` | HTTP 200, Ollama 0.40.14 |

**Chú ý về giới hạn:** cột `State` xuất hiện trống trong bản ghi console; vì vậy không được gán `Listen` cho dòng `Get-NetTCPConnection` này. Không chứng minh nguyên nhân thiếu dòng netstat là IPv6; **cả TCPv6 đều trả 0**. Dữ liệu cổng 11434 không chứng minh phép đo lịch sử trên cổng V2 12644 có cùng nguyên nhân.

## Phán quyết
- `NETWORK_REFERENCE_11434=TCP_AND_HTTP_REACHABLE_IN_PRIOR_READBACK`.
- `NETSTAT_TCP=ZERO_MATCHES`; `NETSTAT_TCPV6=ZERO_MATCHES`.
- `GET_NETTCPCONNECTION_OWNER=PID_14464_OLLAMA_EXE`; `TCP_STATE=UNVERIFIED_CONSOLE_OUTPUT`.
- `TCPV6_ONLY_EXPLANATION=REJECTED`; `EXACT_NETSTAT_MISS_CAUSE=UNKNOWN`.
- `V1_ONE_SHOT=CONSUMED_NO_RERUN`; `V2_ONE_SHOT=CONSUMED_NO_RERUN`.
- `T5_OLLAMA_GGUF_COMPATIBILITY=NOT_ESTABLISHED`; `T5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED`.

## Yêu cầu kỹ thuật đóng gói cho bộ đọc cổng kế nhiệm
Sửa **một lần trên nguồn**, không mở thêm thử nghiệm cho mỗi lỗi chẩn đoán.

1. **Lấy danh sách socket từ Windows TCP table**, qua `Get-NetTCPConnection -LocalPort <pin> -ErrorAction Stop` và **lọc `State=Listen` theo thuộc tính**, không dựa vào bảng đã format. Nếu truy vấn lỗi, trả về `HOLD_TCP_TABLE_UNAVAILABLE`, không diễn giải là không có listener.
2. Chỉ chấp nhận các socket cổng riêng do **đúng PID tiến trình con** sở hữu và chỉ `127.0.0.1` hoặc `::1`. Từ chối `::`, `0.0.0.0`, địa chỉ không phải loopback, nhiều PID, PID khác, socket thiếu `State`. `::` không đồng nghĩa loopback `::1`.
3. Đối chiếu tiến trình còn sống, executable path và hash PIN, nếu có khả năng race PID thì phải xử lý đóng lỗi (fail closed). Không lấy thành công HTTP làm bằng chứng PID duy nhất.
4. **Sau khi** PID/scope PASS, gọi HTTP trực tiếp tới `127.0.0.1:<port>/api/version`, bỏ proxy; bắt buộc 200 và phiên bản chính xác. Lưu từng lần kiểm tra trạng thái TCP/PID và HTTP cùng mã lỗi vào JSONL trước quyết định.
5. Kiểm định ngoại tuyến tình huống: TCP table rỗng, `State` trống, `Bound`, IPv4 loopback đúng PID, IPv6 `::1` đúng PID, `::` wildcard, `0.0.0.0`, PID lạ, nhiều PID, trạng thái đổi giữa hai lần đọc, HTTP lỗi và sai version; giữ nguyên scope read-only cho kiểm thử.
6. Không thao tác kho mô hình, không sửa `PATH`, không gọi `ollama create` hay `generate` trong bước sửa nguồn. Kiểm định tĩnh độc lập hoàn tất rồi mới quyết định **một lượt smoke mới riêng**, không tái sử dụng V1/V2.

Nguồn đối chiếu API Windows:
- https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection
- https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat

**Bước thực hiện tiếp theo:** `TTM_T5_GET_NETTCPCONNECTION_GUARD_INTEGRATED_SOURCE_ONLY_REPAIR_AND_QA`. **Chưa cấp phép V3**.
