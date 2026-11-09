# TTM T5 — Tiếp tục suy luận từ mô hình đã nhập ở V5

**Không chạy lại V5; không gọi `ollama create`; không dùng service Ollama thường ở 11434.** V5 đã nhập GGUF thành công (`ollama create` mã thoát 0, manifest-v2 khớp GGUF), sau đó bị chặn bởi điều kiện tìm sai đường dẫn manifest. Việc còn thiếu là gọi `/api/generate` và xác minh 1–32 token sinh ra.

Bản này là một *lượt suy luận mới* có định danh `ttm_t5_v5_imported_model_inference_only_v1` và cổng `12649`, dùng bản **sao chép nguyên vẹn** của kho mô hình V5 trong `_tmp`. V5 và các bằng chứng V1–V4 không được sửa/xóa. Không thay `main` hay `lineage.md`.

## Cổng kỹ thuật cần thiết

- Đúng Git repository, Python 3.12, GGUF và Ollama 0.40.14 đúng SHA-256, nguồn V5 đã được ghim.
- Kiểm tra kết quả V5 cho thấy `create_return_code=0`, manifest V2 `format=gguf`, lớp mô hình có digest SHA-256 khớp tệp GGUF và nguồn V5 đã dừng bình thường.
- So sánh SHA của toàn bộ kho mô hình V5 với `MODELS_AFTER_CREATE.json` và `RESULT.json`; sao chép sang thư mục mới rồi kiểm tra SHA lại.
- Máy chủ Ollama con riêng `127.0.0.1:12649`, PID/path/creation time đúng và HTTP 200 version 0.40.14, nguồn Windows IP Helper theo V5, không giả danh `state=0` thành LISTEN.
- API `/api/tags` phải nhìn thấy model chính xác trước khi gọi `/api/generate`; `num_ctx=256`, `num_predict=32`, chỉ prompt tổng hợp.
- Không chạy lại cùng ID nếu `CLAIM.json` tồn tại; không thay hoặc xóa dữ liệu cũ; kết quả STRICT LOGITS FAIL 7/8 vẫn giữ nguyên.

## Chạy

Giải nén ZIP dưới `_tmp/TTM_T5_V5_IMPORTED_MODEL_INFERENCE_ONLY_20261109`. Chạy đúng một lần với `-Mode Smoke`, **chỉ khi SHA của ZIP được xác nhận**. `-Mode Preview` không khởi động Ollama hoặc tạo bằng chứng.

Dùng `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <script> -Mode Smoke` với script `Invoke-TTM-T5-Imported-Model-Inference-Only.ps1`. Chương trình tự chạy 12 kiểm thử ngoại tuyến và tiền kiểm trước khi claim lượt suy luận. Kết quả nằm ở `_tmp/ttm_t5_v5_imported_model_inference_only_v1/RESULT.json`. Không đưa `serve.log` hoặc thư mục `home/.ollama` chứa khóa lên GitHub.

**Trạng thái:** `V5_CREATE=SUCCESS`, `V5_INFERENCE=NOT_EXECUTED`, `RESUME_OFFLINE_QA=12/12`, `RESUME_NATIVE=NOT_EXECUTED`.
