# TTM T5 V5 — Phân xử nhập GGUF PASS, suy luận chưa chạy (2026-11-09)

## Kết quả thật từ lượt V5 đã tiêu thụ

- Bản vá wrapper schema `PASS_ONE_LITERAL_ONLY`; bộ kiểm định Windows `PASS_47_OF_47`.
- Ollama chạy trên tiến trình **PID 33992**, `127.0.0.1:12648`. Xác minh kép PID và HTTP trả `READY_DUAL_ATTESTED_STATE_ZERO_UNKNOWN`; không giả mạo `State=0` thành LISTEN.
- `ollama create` đã chạy và **trả mã 0**; server log `POST /api/create` trả **HTTP 200**. `create.stderr.log` xác nhận `parsing GGUF`, `writing manifest`, `success`.
- Kho V5 trong project có blob nguyên GGUF tại `blobs/sha256-5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, kích thước **15.061.376 byte**. Manifest thực tế nằm tại `manifests-v2/ollama.com/library/ttm-t5-f32-compat-only-v5final/latest`, là JSON có `schemaVersion=2`, `format=gguf`, `runner=llamacpp`, `layers[model].digest=sha256:5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`. Kho V5 lưu manifest 637 byte, SHA-256 `5966524c448e16c4de099f24c0dc334708ed63315322949fd8d684cc2aef8f14`.
- Guard V5 tìm đường dẫn có tiền tố **`manifests/`**; Ollama 0.40.14 ghi **`manifests-v2/`**, gây `CREATE_WITHOUT_PROJECT_LOCAL_MANIFEST_HOLD_NO_GENERATE` dù nhập mô hình thành công.
- **Không có** `/api/generate`, `GENERATION_RAW_RESPONSE.json`, hay token suy luận từ V5. Đã dừng đúng PID con, `shutdown.stop_status=STOPPED_OWNED_TREE`; kiểm tra cổng sau dừng `PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN`, chỉ còn ba dòng `PID=0/TIME_WAIT`.
- Kết luận hẹp: `OLLAMA_GGUF_IMPORT=PASS_OBSERVED`, `OLLAMA_INFERENCE=NOT_EXECUTED`. Không chứng minh mô hình sinh token, độ đúng của output hoặc parity. Kết quả `T5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED`.

## Quyết định kỹ thuật để tránh chuỗi thử lặp

Không sửa hay xóa kết quả V5, không mở lại `create`, không đổi `lineage.md` hoặc `main`.

Chuẩn bị một lượt suy luận **mang định danh mới, chỉ thực hiện generate** từ bản sao kho V5 nguyên vẹn. Gói trợ giúp `TTM_T5_V5_IMPORTED_MODEL_INFERENCE_ONLY_20261109.zip`, SHA256 `b07fc89d751710025d113a2e64249db260de7a351f18a75eb8a4a8c437f16379` (bàn giao qua cuộc trò chuyện; không lưu tệp ZIP nhị phân trên GitHub ở biên bản này). Kiểm định ngoại tuyến **12/12 PASS**, chưa gọi native Ollama.

Gói này:
- Kiểm tra đúng Git repo, Python 3.12, các SHA đã khóa và V5 `RESULT.json`; đối chiếu toàn bộ 5 tệp kho mô hình với `MODELS_AFTER_CREATE.json` và `RESULT.json`, trong đó có manifest-v2 cùng digest GGUF.
- Sao chép kho V5 sang `_tmp/ttm_t5_v5_imported_model_inference_only_v1/models`; không viết lại kho V5.
- Mở duy nhất tiến trình Ollama mới cổng `12649`, xác minh đúng PID, creation time, executable, loopback và HTTP 200/version.
- Kiểm tra tag qua `/api/tags`, rồi gọi đúng **một** `/api/generate`, `num_ctx=256`, `num_predict=32`, prompt tổng hợp; lưu `RESULT.json`, `GENERATION_RAW_RESPONSE.json`; dừng đúng tiến trình con.
- Mọi lỗi là FAIL/HOLD, không tự chạy lại và không ghi đè evidence.

**Bước thực hiện tiếp theo:** `TTM_T5_V5_IMPORTED_MODEL_INFERENCE_ONLY_ONE_SHOT_AND_RESULT_READBACK`. Chưa thực thi trên Windows; kết quả nhập mô hình PASS đã đủ, chỉ còn kiểm chứng suy luận.
