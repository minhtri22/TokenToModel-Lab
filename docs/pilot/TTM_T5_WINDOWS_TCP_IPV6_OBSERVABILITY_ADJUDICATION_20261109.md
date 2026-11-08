# TTM T5 — Tiếp nhận phép đo Windows 11434 và phân xử bộ lọc TCP/IPv6 (2026-11-09)

## 1. Nguồn và kết quả
Người dùng thực thi đoạn PowerShell chỉ đọc; kết quả báo lại:
- `netstat.exe -ano -p TCP` + lọc cổng 11434: **0 dòng**.
- `Get-NetTCPConnection -LocalPort 11434`: **1 dòng**, `LocalAddress=::`, `LocalPort=11434`, `OwningProcess=14464`; cột `State` trống trong phần console gửi đến nên **chưa xác minh chính xác trạng thái từ lệnh đó**.
- TCP connect tới `127.0.0.1:11434`: **PASS**.
- HTTP trực tiếp GET `http://127.0.0.1:11434/api/version`: **200**, `{"version":"0.40.14"}`.
- `TTM_T5_NETWORK_DIAGNOSTIC=READONLY_COMPLETED`. Chưa xác minh độc lập đường dẫn binary của PID 14464. Không nạp GGUF hay sinh token.

## 2. Đối chiếu giao thức Windows
Theo Microsoft Learn **netstat**, `-p tcp` và `-p tcpv6` là hai bộ lọc giao thức khác nhau. `Get-NetTCPConnection` hỗ trợ IPv4/IPv6 và lấy PID, trạng thái. Địa chỉ `::` biểu thị địa chỉ IPv6 không xác định (wildcard), **không** đồng nghĩa chỉ lắng nghe loopback.

Nguồn tài liệu:
- https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netstat
- https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection

Đây là bằng chứng rằng phép chỉ dùng `netstat -p TCP` **không đáng tin cậy như một kiểm tra tổng quát về cổng trên máy hiện tại**, vì đã bỏ sót ít nhất một dịch vụ HTTP đang hoạt động. Giả thuyết mạnh là dịch vụ này dùng TCP/IPv6; **chưa có output `netstat -p TCPv6` để chốt**.

## 3. Giới hạn suy luận với V2
Lỗi V2 trên **cổng 12644** là `READINESS_TIMEOUT_WAIT_PORT_PID_NOT_YET_OBSERVED`, với 40/40 mẫu netstat không thấy PID và 0 HTTP request. Log V2 từng ghi `Listening on 127.0.0.1:12644`. Phép đo mới tại **11434, địa chỉ `::`** chỉ là đối chứng; **không chứng minh V2 cũng là IPv6**. V2 PID đã dừng, không thể đo lại listener lịch sử bằng phép đo live.

Không thay cơ chế từ kiểm PID nghiêm ngặt sang chỉ kiểm HTTP, vì có thể gắn nhầm một dịch vụ khác. Không tự coi wildcard `::` an toàn cho máy chủ TTM cô lập.

## 4. Phán quyết
- `NETWORK_11434_TCP_CONNECT=PASS`; `NETWORK_11434_HTTP_VERSION=PASS_200_0.40.14`.
- `NETSTAT_TCP_ONLY_OBSERVABILITY=INCOMPLETE`.
- `TCPv6_HYPOTHESIS=PLAUSIBLE_NOT_YET_DIRECTLY_CHECKED`.
- `V2_12644_DEEP_ROOT_CAUSE=NOT_ESTABLISHED`.
- `V1_ONE_SHOT=CONSUMED_NO_RERUN`; `V2_ONE_SHOT=CONSUMED_NO_RERUN`.
- `OLLAMA_GGUF_COMPATIBILITY=NOT_TESTED`; `T5_FULL_LOGITS=FAIL_7_OF_8_PRESERVED`.
- Không thay checkpoint, GGUF, `main`, `lineage.md`, không TRAIN/TEST.

## 5. Bước tiếp theo
`TTM_T5_NETWORK_TCPV6_PORT_IDENTITY_READONLY_CONFIRMATION_NO_NEW_SMOKE`: trên **dịch vụ hiện có 11434**, gọi `netstat.exe -ano -p TCPv6` và `netstat.exe -ano` (không bộ lọc) để tìm đúng cổng, đối chiếu `Get-NetTCPConnection -State Listen`, PID và đường dẫn executable thật (read-only). Nếu TCPv6 xuất hiện với PID 14464 thì xác minh nguyên nhân bộ lọc riêng đối với 11434; nếu không, cần chẩn đoán cách liệt kê socket. Sau đó mới thiết kế lại cơ chế PID+HTTP cho lần smoke tiếp theo; **chưa cấp quyền V3**.
