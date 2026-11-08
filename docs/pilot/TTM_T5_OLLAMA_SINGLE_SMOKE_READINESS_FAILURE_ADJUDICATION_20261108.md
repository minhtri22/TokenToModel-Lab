# TTM T5 — Phân xử lỗi cổng sẵn sàng Ollama cô lập (2026-11-08)

**Phạm vi:** QA kỹ thuật (engineering QA) chỉ đọc bằng chứng đã tạo, không chạy lại Ollama, không nhập GGUF, không suy luận, không TRAIN/TEST, không sửa nguồn hay tiêu chí T5.

## 1. Xuất xứ bằng chứng

- Tệp do người dùng cung cấp: RESULT(20261108-162027).json; SHA-256 theo byte: 128af713e90cf838a487129f14520fb30bbbd37c34daf12bac9b94e8d2fc6773 (2.755 byte).
- Tệp nguồn nguyên vẹn đã commit tại evidence/pilot/t5-trained/TTM_T5_OLLAMA_PROJECT_LOCAL_SINGLE_SMOKE_RESULT_20261108.json; đọc lại GitHub và so sánh đúng nội dung nguyên bản.
- Thư mục hiện hữu Windows: D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_compat_only_single_v1. Đã đọc CLAIM.json, RESULT.json, ENV_SCOPE.json, MODELS_BEFORE.json, Modelfile, serve.log và mã Python gốc qua kết nối chỉ đọc.
- CLAIM.json xác nhận ONE_SHOT_CLAIMED. Không xóa, không tái sử dụng lần chạy đã tiêu thụ.

## 2. Dấu thời gian và kết quả thực tế

- RESULT: FAIL_OR_HOLD_COMPATIBILITY_ONLY_NO_RERUN; failure=ISOLATED_OLLAMA_SERVER_NOT_READY_20S, kết thúc 2026-11-08 16:20:09.124322 UTC.
- serve.log xác nhận Listening on 127.0.0.1:12643 (version 0.40.14) lúc 2026-11-08 23:19:46.892 +07:00, gần như ngay sau mốc bắt đầu 23:19:46.815805 +07:00.
- Báo cáo chỉ ghi nhận server_started, chưa có owned_server_ready, create_completed, generate_completed. Vì vậy ollama create và suy luận chưa diễn ra.
- MODELS_BEFORE.json={} và models_after_run={} cho thấy không có mô hình nào được ghi vào kho mô hình cô lập.
- ENV_SCOPE.json ghi OLLAMA_MODELS nằm dưới TTM; OLLAMA_NO_CLOUD=1, HOME/USERPROFILE/APPDATA/LOCALAPPDATA nằm dưới thư mục dự án. Đây là xác nhận cấu hình dự kiến, không phải audit toàn bộ mọi thao tác I/O hệ điều hành.
- shutdown: PID 672, STOPPED_OWNED_TREE, taskkill_exit_code=0 và shutdown_port_owners=[].
- SHA trước và sau không đổi: GGUF 5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5; Ollama executable 14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981; FAIL nguyên bản c61f73216764b8582a5c996e85c59feb55b13496ec0117deb713d9b1843ec8e8; V5B ac699d4e750037f88bbab776bb42a38079cd82b0a1c2f72385127ac5a36d9375.
- serve.log cảnh báo ggml-base.dll từ PATH ở _tmp/ttm_t2/build/bin/Release và cho thấy chọn CPU, không chọn GPU tích hợp. Không đủ căn cứ quy nguyên nhân lỗi readiness cho cảnh báo này.
- Ollama có tạo khóa SSH tại vùng HOME riêng của lượt chạy; nội dung khóa không được công bố lên GitHub.

## 3. Phân tích mã nguồn

Vòng lặp readiness kiểm tra đồng thời hai điều kiện:

1. Tập PID listening mà netstat_listening_owners(12643) phát hiện phải đúng bằng {proc.pid}.
2. GET trực tiếp tới http://127.0.0.1:12643/api/version phải trả version 0.40.14.

Vòng lặp tối đa 40 lần, nghỉ 0,5 giây/lượt, nhưng không lưu PID tìm được, HTTP response hoặc exception mỗi lần (ngoại lệ API được bỏ qua). Vì vậy, log Listening chứng minh service đã mở listener, song không đủ dữ liệu để phân biệt lỗi netstat/PID với lỗi API hoặc phiên bản. Không tuyên bố đã cô lập chính xác nguyên nhân.

Việc chưa vượt cổng readiness nghĩa là chưa gọi ollama create hoặc /api/generate. Báo cáo này KHÔNG phải bằng chứng Ollama không hỗ trợ mô hình.

## 4. Phán quyết

- ONE_SHOT=CONSUMED_STOP_NO_RERUN.
- OLLAMA_DEDICATED_LISTENER=OBSERVED_IN_SERVE_LOG.
- OWNED_SERVER_READINESS_GATE=FAIL_TIMEOUT_SUBCONDITION_UNKNOWN.
- STORAGE_GUARD=SCOPED_ENV_OBSERVED; IMPORT_NOT_REACHED.
- OLLAMA_IMPORT=NOT_EXECUTED; OLLAMA_GENERATION=NOT_EXECUTED.
- OLLAMA_GGUF_COMPATIBILITY=NOT_ESTABLISHED.
- ORIGINAL_GGUF_AND_FAILURE_SHA256=UNCHANGED.
- SERVER_SHUTDOWN=PASS_OBSERVED.
- T5_STRICT_F32_LOGITS=FAIL_7_OF_8_PRESERVED.
- TRAIN_TEST=NOT_ACCESSED.
- MAIN_AND_LINEAGE=UNCHANGED.

## 5. Bước tiếp theo

TTM_T5_OLLAMA_READINESS_GATE_SOURCE_ONLY_REPAIR_DESIGN_AND_INDEPENDENT_STATIC_QA

Chỉ sửa thiết kế và QA tĩnh của bộ chạy mới để ghi lại từng vòng: tập PID listening, PID tiến trình, kết quả kết nối, HTTP status/version và lỗi rõ ràng; không bỏ qua lỗi mà không ghi log. Phải giữ bảo vệ cổng chống nhập nhầm dịch vụ khác, giữ kho mô hình bên trong TTM, và không tự động chạy lại. Một lượt thực thi mới có ID khác chỉ được xem xét sau QA độc lập và quyết định cấp quyền rõ ràng; không tái sử dụng claim đã tiêu thụ.
