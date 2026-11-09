# TTM T5 — Kết luận Ollama GGUF import + 32-token inference (2026-11-09)

## Đã xác nhận từ Windows thật

**KẾT LUẬN: `PASS_COMPATIBILITY_IMPORT_REUSED_AND_INFERENCE_CONFIRMED`.**

Bộ chạy suy luận kế nhiệm đã tái sử dụng đúng kho mô hình nhập thành công ở lượt V5, sao chép 5 tệp giữ nguyên SHA, không gọi `ollama create`, mở Ollama riêng ở `127.0.0.1:12649` (PID `21972`), xác minh HTTP 200/version và tag rồi gọi `/api/generate` **một lần**.

- `RESULT.json` do người dùng tải lên và console thống nhất SHA-256: `2af9d32aabfc03e6240a499162ee901fae9b8afeb854f437c7ae10d623bd105d` (1.343 byte).
- `GENERATION_RAW_RESPONSE.json` được đọc chỉ-đọc từ máy: model `ttm-t5-f32-compat-only-v5final:latest`; `done=true`, `done_reason=length`; `prompt_eval_count=10`, `eval_count=32`.
- **Generated text:** ` was a big, a big tree. The bird was very happy to the tree. The bird was very happy.\nOne day, the bird saw a big`. Output ngắn, lặp; không kết luận chất lượng ngôn ngữ/suy luận.
- `IMPORTED_STORE_COPY_VERIFIED.json`: `file_count=5`, `same_sha256_tree=true`. Kho V5 gốc được giữ nguyên.
- `READINESS_ATTEMPTS.jsonl`: kiểm tra lần 2 `READY_DUAL_ATTESTED_STATE_ZERO_UNKNOWN`, HTTP 200, vẫn không tuyên bố `TCP LISTEN=2` khi Windows trả state=0.
- Sau chạy: `shutdown.stop_status=STOPPED_OWNED_TREE`, `shutdown_port_adjudication.decision=PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN`; chỉ còn `TIME_WAIT` là vô hại.

## Phân xử ranh giới

| Câu hỏi | Kết luận |
|---|---|
| Ollama 0.40.14 có chấp nhận GGUF F32 TTM-Small-4M? | **PASS** (lượt V5: `ollama create` mã thoát 0, manifest-v2 đúng GGUF SHA) |
| Ollama có nạp lại model và sinh token? | **PASS** (lượt inference-only: 32 token thực tế) |
| Chất lượng ngôn ngữ/suy luận có tốt không? | **CHƯA KIỂM CHỨNG** (đoạn mẫu có lặp) |
| Logits từ llama.cpp có tương đương checkpoint chuẩn? | **FAIL 7/8 GIỮ NGUYÊN**; không chứng minh parity PASS |

**Đóng mục tiêu kiểm định tương thích Ollama T5**; không tự động đóng tất cả phase nghiên cứu hay tuyên bố mô hình có chất lượng cao. Không tạo model mới, không sử dụng lại one-shot, không thay `lineage.md` vì đây là bằng chứng tương thích kỹ thuật; không merge PR #12 hoặc sửa `main`.

## Bước thực hiện tiếp theo

`TTM_SMALL_POST_COMPATIBILITY_QUALITY_AND_ABLATION_EVALUATION_PLAN`: đánh giá nhỏ, có tiêu chí về độ lặp, câu trả lời cơ bản, độ trễ và bật/tắt các cấu hình đã khóa; xác định ranh giới chất lượng và nút thắt parity trước quyết định huấn luyện tiếp. Không cần kiểm tra TCP/Ollama hạ tầng thêm.
