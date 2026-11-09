# TTM T5 — Phán quyết State=0 của Windows CIM; kiểm chứng tiếp bằng IP Helper (2026-11-09)

## Tiếp nhận bằng chứng chỉ đọc

Người dùng kiểm tra **dịch vụ Ollama sẵn có** ở cổng 11434, không mở lượt smoke mới:
- `TCP_ROWS=1`, địa chỉ `::`, PID `14464` (tiến trình `ollama.exe` đã xác nhận trong lần đọc trước);
- `TCP_STATE_DIRECT=[]`, `TCP_STATE_CIM=[0]`, kiểu `System.Byte`;
- `Get-NetTCPConnection -LocalPort 11434 -State Listen` trả **No matching MSFT_NetTCPConnection objects**, tức truy vấn trạng thái TCP=2 không có kết quả;
- phép đo trước đó cùng dịch vụ có TCP connect tới `127.0.0.1:11434` thành công và HTTP `GET /api/version` trả 200/0.40.14.

Đối chiếu Microsoft SDK: `MIB_TCP_STATE_LISTEN=2`; **0 không được suy diễn thành Listen**. Bảng CIM trên máy đã thể hiện giá trị trạng thái không nhất quán với phép đo khả dụng mạng. Nguyên nhân sâu hơn **chưa xác minh**, không tự khẳng định là lỗi PowerShell hay Windows kernel.

## Phán quyết giữ nguyên

- `CIM_STATE=0_NOT_TRUSTED_FOR_STRICT_TCP_LISTEN_GATE`; `CIM_LISTEN_FILTER=NO_MATCH`.
- `V1_ONE_SHOT=CONSUMED`, `V2_ONE_SHOT=CONSUMED`, `V3RC1_ONE_SHOT=CONSUMED`, **NO_RERUN**.
- `OLLAMA_CREATE=NOT_EXECUTED`, `OLLAMA_INFERENCE=NOT_EXECUTED`, `GGUF_COMPATIBILITY=NOT_ESTABLISHED`.
- `T5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED`, GGUF và checksum khoa học giữ nguyên.
- Không sửa `main`, `lineage.md`, checkpoint, các biên bản PASS/FAIL đã khóa.

## Gói kiểm chứng IP Helper nguồn riêng

Đã chuẩn bị gói **chỉ đọc** `TTM_T5_IPHELPER_TCP_NATIVE_READONLY_20261109.zip`, SHA256 `a684caf1417a6c50931ebeef6e0b3d1b6334d115e4db63514b3df9ad795ab202` (6 tệp).

- `ttm_t5_iphelper_readonly.py`: `GetExtendedTcpTable` qua `ctypes` với `TCP_TABLE_OWNER_PID_ALL` trên AF_INET/AF_INET6, chỉ đọc PID/state/IP/port của **11434**; hạn chế kích thước bảng, kiểm cấu trúc, không gán State 0 thành LISTEN.
- `test_iphelper_readonly.py`: 22 kiểm định giả lập; `PASS_22_OF_22` trên container của assistant; **Windows native API chưa chạy**.
- Wrapper PowerShell 5.1 ghim SHA manifest, chạy QA và native probe; không mở hoặc dừng Ollama, không tạo claim, không đụng V1/V2/RC1.
- Mã nguồn và ZIP hiện được bàn giao dưới dạng tệp đính kèm trong cuộc trò chuyện; **không khẳng định mã nguồn ZIP đã commit lên GitHub**. Biên bản này và dữ liệu readback được commit, chưa có bằng chứng native của gói.

Tài liệu Microsoft: https://learn.microsoft.com/en-us/windows/win32/api/iphlpapi/nf-iphlpapi-getextendedtcptable ; https://learn.microsoft.com/en-us/windows/win32/api/tcpmib/ns-tcpmib-mib_tcprow_owner_pid ; https://learn.microsoft.com/en-us/windows/win32/api/tcpmib/ns-tcpmib-mib_tcp6row_owner_pid .

## Quyết định bước tiếp theo

`TTM_T5_IPHELPER_NATIVE_TCP_READONLY_REFERENCE_11434_AND_INTEGRATED_GUARD_DECISION`: thực hiện **một** phép đo IP Helper chỉ đọc trên dịch vụ Ollama hiện có; nếu API vẫn báo 0 hoặc không có bản ghi, dừng và rà soát phương pháp an toàn khác. Chỉ nếu API trả chính xác State=2 và đúng PID mới sửa guard nguồn và kiểm định độc lập; **không tự cấp quyền thử Ollama mới**.
