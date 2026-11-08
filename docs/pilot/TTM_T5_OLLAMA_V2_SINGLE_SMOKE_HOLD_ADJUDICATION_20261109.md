# TTM T5 — Phân xử lượt thử Ollama V2: cổng PID không quan sát được (2026-11-09)

## Phạm vi
Đây là phân xử QA kỹ thuật chỉ đọc, không thực hiện lệnh mới trên Ollama, không đào tạo/TEST, không sửa mô hình, ngưỡng logits hoặc kết quả khoa học. V1 và V2 đã nhận một lần và không được chạy lại. Dữ liệu gốc được đọc từ máy Windows qua kênh tệp chỉ đọc; chưa có phép đo SHA256 native độc lập cho chính tệp RESULT/TRACE khi đọc này.

## Kết quả quan sát
- Nguồn Windows: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_compat_only_single_v2`.
- `RESULT.json`: `FAIL_OR_HOLD_COMPATIBILITY_ONLY_NO_RERUN`, lỗi `READINESS_TIMEOUT_WAIT_PORT_PID_NOT_YET_OBSERVED`, PID con `20028`, host `127.0.0.1:12644`; stage chỉ có `server_started`.
- `READINESS_ATTEMPTS.jsonl`: đúng **40/40** attempt từ 2026-11-09 00:03:34.289 +07:00 đến 00:03:56.077 +07:00; `netstat.owners=[]`, `netstat.rows=[]`; **0/40 HTTP probe attempted**, không thể kết luận endpoint `/api/version` hoạt động hay không.
- `serve.log` riêng Ollama 0.40.14 ghi `Listening on 127.0.0.1:12644 (version 0.40.14)` tại 2026-11-09 00:03:34.352 +07:00. Có mâu thuẫn giữa trạng thái ghi trong log và quan sát bằng `netstat` của runner; chưa chứng minh kết nối HTTP thực sự khả dụng tại thời điểm đó.
- `PATH_DLL_RISK.json`: tìm thấy thư mục `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\build\bin\Release` chứa `ggml-base.dll` trong `PATH`; log cảnh báo `potentially incompatible library detected in PATH`. Đó là rủi ro, **không phải bằng chứng nhân quả** cho lỗi readiness. Log cũng cho biết CPU được chọn và iGPU Intel bị bỏ qua.
- Máy chủ đã bị dừng theo `STOPPED_OWNED_TREE`, `taskkill_exit_code=0`; `shutdown_port_owners=[]` theo cùng cơ chế netstat — kiểm chứng riêng PID dừng là tốt hơn bằng chứng netstat đơn lẻ.
- Trước/sau cùng SHA: GGUF `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`; Ollama executable `14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981`; lỗi gốc `c61f73216764b8582a5c996e85c59feb55b13496ec0117deb713d9b1843ec8e8`; V5B `ac699d4e750037f88bbab776bb42a38079cd82b0a1c2f72385127ac5a36d9375`.
- Thư mục model rỗng sau lượt chạy. Chưa đến `ollama create`, chưa đến generate và không có TRAIN/TEST.

## Đối chiếu source V2
Mã V2 trong `readiness_sample` kiểm tra netstat trước. Khi PID không nằm trong `owners`, nó trả `WAIT_PORT_PID_NOT_YET_OBSERVED` ngay lập tức, đặt `http.attempted=false`. Vì vậy thử kiểm tra API bị **chặn về mặt điều khiển**, không phải API đã được kiểm thử và trả lỗi. Kiểm định tĩnh 23/23 trước đó không phát hiện được tình huống thực tế vì dùng netstat mock.

## Quyết định
- `V1_ONE_SHOT=CONSUMED_NO_RERUN`; `V2_ONE_SHOT=CONSUMED_NO_RERUN`.
- `OLLAMA_V2_READINESS=HOLD_NETSTAT_PID_NOT_OBSERVED_40_OF_40`.
- `OLLAMA_LOG_LISTENER=OBSERVED`; `ACTUAL_SOCKET_CONNECTIVITY=NOT_PROVEN`.
- `HTTP_READINESS=NOT_ATTEMPTED`; `OLLAMA_CREATE=NOT_EXECUTED`; `OLLAMA_GENERATION=NOT_EXECUTED`.
- `MODEL_COMPATIBILITY=NOT_ESTABLISHED_NOT_PROVEN_FAIL`.
- `ORIGINAL_GGUF_AND_FAILURE_REPORT_HASHES=UNCHANGED`.
- `T5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED`; `lineage.md=UNCHANGED`.

## Bước tiếp theo — không mở thêm lượt Ollama
`TTM_T5_WINDOWS_NETWORK_OBSERVATION_READONLY_TRIANGULATION`: kiểm tra thụ động trên dịch vụ **đang tồn tại** bằng cách so sánh `netstat.exe -ano -p TCP`, `Get-NetTCPConnection`, `Test-NetConnection`/TCP handshake và `GET /api/version` trên cùng host/port, với kết quả thô và mã lỗi. Không khởi động/đóng Ollama, không gọi create/generate, không đụng dữ liệu train/TEST. Nếu không có dịch vụ sẵn, kết luận `NO_ACTIVE_REFERENCE_LISTENER` và dừng. Sau khi biết chính xác độ tin cậy của phép đo trên Windows, thiết kế một preflight mới kiểm chứng bằng mô phỏng và quyết định có cần một lượt smoke mới hay không — **không tự động cấp phép V3**.
