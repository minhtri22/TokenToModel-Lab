# TTM T5 — Ollama chạy bình thường, IP Helper trả trạng thái TCP=0 (2026-11-09)

## 1. Nhận bằng chứng
- Ảnh ứng dụng Ollama do người dùng cung cấp cho thấy giao diện trả lời câu `hi`: `Hello! How can I help you today?`. Không thấy model ID trong ảnh; không chứng minh TTM-Small-4M đã được nhập hay sử dụng.
- Phép đo đã xác minh trước đó trên dịch vụ 11434: GET `/api/version` HTTP 200, Ollama 0.40.14, tiến trình PID 14464 có executable path `C:\Users\minht\AppData\Local\Programs\Ollama\ollama.exe`.
- Gói IP Helper ZIP SHA256 `a684caf1417a6c50931ebeef6e0b3d1b6334d115e4db63514b3df9ad795ab202`, mã nguồn SHA PASS theo console. Bài thử ngoại tuyến Windows `22/22 PASS`.
- Chẩn đoán IP Helper native `GetExtendedTcpTable` (cả IPv4/IPv6, cổng 11434) `API_SUCCESS`. IPv4: một dòng `0.0.0.0:11434`, PID 14464, `state_code=0`. IPv6: một dòng `[::]:11434`, PID 14464, `state_code=0`. Cả hai `state_verified_listen=false`, không phải loopback-only.
- `TTM_T5_IPHELPER_STATUS=HOLD_NO_VALIDATED_LISTEN_ROW`, `T5_IPHELPER_NATIVE_PROBE_EXIT=4`, dù `T5_IPHELPER_WRAPPER_EXIT=0`. **Exit=0 của wrapper chỉ biểu thị wrapper kết thúc; không được làm sai lệch status HOLD của probe.**
- Không khởi động hoặc dừng Ollama, không tạo model, không đọc/sửa TRAIN/TEST, checkpoint, GGUF hoặc evidence V1/V2/RC1.

## 2. Giới hạn khoa học và nhận định
- Ollama desktop được quan sát hoạt động với một mô hình **không xác định**. TTM-Small-4M **chưa** đến được `ollama create` hoặc `/api/generate` trong 3 lần chạy cô lập trước đây.
- Theo Microsoft Learn, `MIB_TCP_STATE_LISTEN=2`; state `0` không được coi là LISTEN. Mã nguồn không được tự đổi `0→2`.
- Microsoft Q&A ghi nhận báo cáo cộng đồng về Windows 11 26H2 mà native API, CIM và `netstat` đồng thời có triệu chứng này, trong khi kết nối HTTP vẫn thành công. Chưa đối chiếu build/KB/driver máy người dùng nên **không kết luận cùng nguyên nhân**, không cài/xóa bản cập nhật Windows hoặc can thiệp driver.
- Địa chỉ `0.0.0.0`/`::` trên **dịch vụ 11434 đang hoạt động** không được sao chép sang máy chủ thử nghiệm cô lập. Bản successor bắt buộc `127.0.0.1`/`::1`, đúng PID/process identity và cổng riêng.
- `V1/V2/V3RC1=CONSUMED_NO_RERUN`, `GGUF_COMPATIBILITY=NOT_ESTABLISHED`, `T5_STRICT_FULL_LOGITS=FAIL_7_OF_8_PRESERVED`.

## 3. Quyết định thực dụng — dừng chuỗi thăm dò TCP nhỏ
Không mở lượt smoke mới chỉ để thử một biến thể TCP API. Bộ thử thực tế kế tiếp cần **song chứng nhận quyền sở hữu và hoạt động HTTP** trên cùng socket loopback, có guard fail-closed:
1. Cổng riêng mới chưa được claim, precheck không có kết nối và PID khác; nguồn/Ollama/checkpoint/executable/FAIL receipt đúng hash; thư mục model store riêng trong TTM; hoàn toàn không sửa dịch vụ 11434.
2. Sinh một tiến trình Ollama con và lưu `pid`, path thực và creation time; dùng bảng TCP native để xác minh **đúng PID và loopback**, từ chối PID lạ, wildcard hoặc nhiều owner. Nếu `state=0`, ghi `UNKNOWN`, không gọi là LISTEN; chỉ chấp nhận riêng trường hợp kiểm thử compatibility khi đồng thời có **HTTP 200/version exact** qua `127.0.0.1:<new-port>`, bảng TCP và danh tính tiến trình **khớp trước và sau** HTTP, không có dấu hiệu PID replacement hoặc thêm owner. Bất kỳ lỗi/khác biệt nào = HOLD.
3. Sau tạo model, xác minh manifest nằm trong kho dự án, tag vừa tạo và nguồn gốc GGUF; tối đa 32 token, num_ctx 256, prompt tổng hợp. Ghi RESULT/TRACE và SHA, cleanup chỉ thuộc PID con; one-shot không được lặp lại.
4. Kiểm định độc lập các ca negative và một mock end-to-end; chỉ khi QA PASS mới quyết định lượt thử một lần **mang danh tính mới**. Đây là giới hạn thay thế, không sửa đổi/hợp thức hóa V3RC1 đã thất bại.
5. Chưa cấp phép chạy mới trong biên bản này. Không merge PR #12, không chỉnh `main`, `lineage.md`.

Nguồn:
- Microsoft Learn: https://learn.microsoft.com/en-us/windows/win32/api/tcpmib/ns-tcpmib-mib_tcprow_owner_pid
- Microsoft Q&A (community evidence, not official bug determination): https://learn.microsoft.com/en-us/answers/questions/6057787/getextendedtcptable-returns-dwstate-0-for-listenin
- Ollama documentation: https://github.com/ollama/ollama/blob/main/docs/import.mdx

**Bước thực hiện tiếp theo:** `TTM_T5_FROZEN_REPLAY_SAFE_OWNER_HTTP_DUAL_ATTESTATION_RELEASE_DESIGN_AND_OFFLINE_QA`, không cần thêm lệnh chẩn đoán Windows lẻ tẻ.
