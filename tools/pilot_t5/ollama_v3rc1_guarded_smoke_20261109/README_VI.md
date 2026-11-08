# TTM T5 — Ollama 0.40.14 · V3 RC1 guarded single-smoke

**Mục tiêu duy nhất:** xác nhận checkpoint TTM-Small4M-T4 step 1024 (GGUF F32, 15.061.376 byte) có thực sự **nhập được** và **sinh 1–32 token** bằng Ollama 0.40.14 trên Windows. Đây là QA tương thích (compatibility-only); **không** tái phán xử logits strict parity (vẫn FAIL 7/8).

## Phạm vi và bảo toàn

- Bản này là **RC1 kế nhiệm V3**, không chỉnh sửa V3 source-only gốc đã khóa. Trên Windows dùng Python 3.12 + PowerShell 5.1; không tải thêm mô hình/gói Python.
- Khu lưu nguồn sau giải nén: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_T5_OLLAMA_V3RC1_GUARDED_SMOKE_20261109`.
- Thư mục claim và tất cả bằng chứng: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_compat_only_single_v3rc1`.
- Ollama con lắng nghe duy nhất trên `127.0.0.1:12645`, tag `ttm-t5-f32-compat-only-v3rc1:latest`, `num_ctx=256`, `num_predict=32`. Không dùng/cấu hình lại Ollama hiện có ở 11434, không gọi cloud.
- `OLLAMA_MODELS`, `OLLAMA_TMPDIR`, `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, `TEMP`, `TMP`, `XDG_CACHE_HOME` trỏ vào root riêng trong dự án; từ chối junction/symlink và địa chỉ lắng nghe khác loopback. Riêng `PATH` của Ollama con được lọc bỏ thư mục đã bị cảnh báo `ttm_t2\build\bin\Release` (chứa GGML DLL); không đổi PATH của Windows hoặc phiên PowerShell của người dùng.
- Tiền kiểm SHA của GGUF: `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`. Phải khớp SHA Ollama.exe, nguồn, hai biên bản FAIL cũ, còn cổng trống và dung lượng >=1 GiB. V1 và V2 phải còn nguyên `CLAIM.json`, `RESULT.json`.
- Phải kiểm tra PID + trạng thái `Listen` + địa chỉ + danh tính exe/CreationDate bằng Windows TCP table trước HTTP version, kiểm lại sau HTTP, sau `create` và sau `generate`. Mọi quyết định có trace append/flush/fsync.
- Ngay khi tạo thư mục V3RC1 `CLAIM.json`, lượt được coi là **CONSUMED** kể cả FAIL/HOLD. Không xóa, đổi tên, ghi đè thư mục claim để chạy lại. Nếu bị chặn **trước claim**, không tiêu thụ.
- Báo cáo `RESULT.json`, `READINESS_ATTEMPTS.jsonl`, `serve.log`, `MODELS_AFTER_CREATE.json`, log create và `GENERATION_RAW_RESPONSE.json` nếu đến bước tương ứng. Ngừng đúng PID cây tiến trình do RC1 tạo. Giữ log FAIL; không đưa nguyên văn khóa riêng Ollama `.ollama/id_ed25519` hoặc home/serve.log lên GitHub.

## Thực hiện tích hợp một lượt

1. Tải ZIP, kiểm SHA-256 được công bố bên ngoài ZIP, giải nén một lần vào thư mục nguồn trên. Không giải nén ngoài project root.
2. Chạy `powershell.exe -NoProfile -ExecutionPolicy Bypass -File '<source>\Invoke-TTM-T5-Ollama-V3RC1-PS51.ps1' -Mode Smoke` (hướng dẫn launcher đầy đủ có trong phản hồi của ChatGPT). Wrapper sẽ xác minh manifest SHA và cú pháp PowerShell, chạy **84 unit tests giả lập**, rồi kiểm nguồn/phiên bản/cổng bằng `--mode preview` **chỉ đọc**. Nếu PASS thì tự gọi đúng **một** `--mode execute`.
3. Nếu kết quả không đạt, **không chạy lại**. Gửi `RESULT.json` và 3 dòng cuối `READINESS_ATTEMPTS.jsonl` cho ChatGPT. Không thay đổi `lineage.md`.

Có thể chạy `-Mode QA` riêng để thực hiện kiểm định tĩnh trước, nhưng **không bắt buộc** và sẽ **không** chạy Ollama. Không bao giờ gọi `--mode execute` trực tiếp bỏ qua wrapper.

## Trạng thái khoa học

- T4 checkpoint gốc, SHA các tệp, bằng chứng FAIL T5 logits gốc và V5B giữ nguyên.
- Chỉ kết luận `PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE` khi nhập thành công, xác nhận manifest trong kho dự án, API thấy model tag và nhận `done=true` với `1 <= eval_count <= 32`.
- Nếu FAIL trước nhập, **không** kết luận mô hình không tương thích. Nếu `ollama create` FAIL, phân loại khả năng nạp GGUF thất bại theo log; nếu generate FAIL, phân loại riêng.

**Bước thực hiện tiếp theo:** `TTM_T5_V3RC1_SINGLE_SMOKE_RESULT_READBACK_ADJUDICATION` sau đúng một lượt Windows.
