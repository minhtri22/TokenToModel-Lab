# TTM T5 — Phân xử lượt chạy V3 RC1: trạng thái TCP rỗng (2026-11-09)

## Bằng chứng đã đối chiếu
- Người dùng cung cấp `RESULT(20261108-182223).json` 3.020 byte, SHA-256 `eafbd3383af348cbedd3505f78b19f4c1ea063bac975eef4eada8e52606ed4b2`. Bản này đã kiểm tra khớp SHA với console.
- `Pasted text(20261108-182302).txt` ghi `T5_V3RC1_SOURCE_SHA256=PASS`, `T5_V3RC1_PS51_PARSE=PASS`, 84/84 mock unittest trên Windows, và `PREFLIGHT=PASS_READONLY_NO_CLAIM`. Các `PRECLAIM_HOLD` trước đoạn unittest là các negative test có chủ đích, **không phải các lượt chạy Ollama thật**.
- Lượt thực tế `START_EXACT_ONCE` tại `127.0.0.1:12645`, `server_pid=32976`, `RESULT.status=FAIL_OR_HOLD_COMPATIBILITY_ONLY_NO_RERUN`. **V3 RC1 đã tiêu thụ**, không chạy lại.
- `READINESS_ATTEMPTS.jsonl`: **1 mẫu duy nhất** `HOLD_TCP_ROW_INVALID_OR_MISSING_STATE`; socket có `local_address="127.0.0.1"`, `local_port=12645`, `pid=32976`, `state=""`; `processes=[]`, `http.attempted=false`. Đã kiểm tra SHA-256 dấu vết đúng `b1ea5d9e9192801f32b2a5efec57062abde9b3a1fca4b29be77c8819bc72ec03`.
- Nhật ký `serve.log` của tiến trình con ghi `Listening on 127.0.0.1:12645 (version 0.40.14)` ngày 2026-11-09 01:21:58.794 +07:00. Log không chứng minh HTTP đã được kiểm thử. Không đưa SSH key phát sinh trong log lên GitHub.
- `PATH_DLL_RISK.json`: thư mục chứa `ggml-base.dll` có mặt trong `PATH` của tiến trình cha nhưng **đã lọc khỏi PATH tiến trình con**, không thay đổi PATH toàn hệ thống; cảnh báo DLL không xuất hiện trong serve.log mới. Không quy cho DLL là nguyên nhân của lỗi State.
- `models_after_run={}`; stage chỉ `server_started`; không tới `ollama create`/generate. Dừng PID 32976 bằng `STOPPED_OWNED_TREE`, mã taskkill=0; TCP table sau dừng không có dòng.
- GGUF SHA-256 trước/sau `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, executable Ollama `14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981`, hai FAIL receipts cũ đều giữ nguyên.

## Phân tích mã nguồn
Nguồn RC1 sử dụng `Get-NetTCPConnection -ErrorAction Stop | Where-Object LocalPort | ForEach-Object { state=[string]$_.State }`. Bản ghi thực nhận `state=""`, và `$listenPids` chỉ lấy các dòng `state -eq 'Listen'`, nên không có tiến trình nào được xác thực qua CIM, không gọi HTTP và fail-closed ngay mẫu đầu.

Điều này chỉ xác nhận **giá trị State được chuyển sang JSON là rỗng**, không phân biệt được thuộc tính CIM thực sự null, PowerShell chuyển kiểu sai, hay nhà cung cấp dữ liệu khác biệt. Ở lần đọc trước trên 11434, cột State cũng để trống; đây là dấu hiệu lặp lại nhưng **chưa phải chẩn đoán nhân quả độc lập**.

Theo Microsoft Learn, `Get-NetTCPConnection` hỗ trợ bộ lọc `-State Listen` cũng như `-LocalPort`: https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection. Không thể tự gán `Listen` cho chuỗi rỗng hoặc chỉ dùng HTTP thay cho kiểm PID.

## Phán quyết
- `V1_ONE_SHOT=CONSUMED`; `V2_ONE_SHOT=CONSUMED`; `V3RC1_ONE_SHOT=CONSUMED_NO_RERUN`.
- `WINDOWS_RC1_QA=PASS_84_OF_84_STATIC_MOCK`; `READINESS=HOLD_TCP_STATE_EMPTY`.
- `PROJECT_LOCAL_MODEL_IMPORT=NOT_EXECUTED`; `INFERENCE=NOT_EXECUTED`; `GGUF_COMPATIBILITY=NOT_ESTABLISHED_NOT_PROVEN_FAIL`.
- `SCIENCE_TRAIN_TEST=NOT_ACCESSED`; `T5_FULL_LOGITS=FAIL_7_OF_8_PRESERVED`.
- Không thay GGUF/checkpoint, `main`, `lineage.md` hoặc các bằng chứng FAIL lịch sử.

## Bước thực hiện tiếp theo
`TTM_T5_NATIVE_TCP_STATE_READONLY_DIAGNOSTIC_BEFORE_ANY_NEW_RC`: kiểm tra **chỉ đọc** trên dịch vụ 11434 vốn đang chạy, đối chiếu `Get-NetTCPConnection -LocalPort 11434`, `Get-NetTCPConnection -LocalPort 11434 -State Listen`, `CimInstanceProperties['State'].Value` và kiểu giá trị; ghi rõ các bản ghi và lỗi. Không khởi động Ollama, không nhập GGUF, không mở V4 vội. Sau khi có kết quả, gộp bản sửa adapter và QA vào đúng một quyết định chạy tiếp theo.
