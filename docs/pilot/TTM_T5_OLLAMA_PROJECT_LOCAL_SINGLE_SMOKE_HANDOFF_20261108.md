# TTM T5 — Ollama GGUF F32 compatibility-only single smoke (Windows)

**Mục tiêu:** Kiểm tra khả năng Ollama 0.40.14 nhập GGUF gốc và sinh tối đa 32 token từ prompt tổng hợp trong ngữ cảnh 256. Đây là QA kỹ thuật, **không** phải T5 F32 strict parity PASS, không đọc TRAIN/TEST.

## Quy tắc

- Python 3.12 stdlib, PowerShell 5.1, **không tải mạng** / không cài thêm package.
- Chỉ đọc GGUF và hai bản ghi FAIL tại `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_trained_f32_v1` và tệp `ollama.exe` đã được phát hiện trên máy. Dừng nếu SHA không khớp hoặc phiên bản Ollama khác 0.40.14.
- **Không dùng Ollama hiện tại ở `127.0.0.1:11434`**. Mở tiến trình `ollama serve` riêng trên `127.0.0.1:12643`; kiểm tra cổng trống trước và PID sở hữu cổng sau. Nếu sai cổng/PID, dừng.
- Đặt biến môi trường riêng cho tiến trình con `OLLAMA_MODELS`, `OLLAMA_TMPDIR`, `TMP`, `TEMP`, `HOME`, `USERPROFILE`, `APPDATA`, `LOCALAPPDATA`, v.v. trỏ vào thư mục TTM. Dùng `OLLAMA_NO_CLOUD=1`. Không sửa biến môi trường người dùng/hệ thống, không khởi động lại tray/daemon đang chạy. Lưu ý giới hạn: đây là giới hạn đường dẫn **do quy trình và Ollama công bố**, không phải sandbox chặn tuyệt đối mọi hoạt động ghi của một binary bên ngoài.
- Thư mục chạy một lần: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_compat_only_single_v1`. `CLAIM.json` đánh dấu một lần; nếu thư mục đã tồn tại thì dừng, không xóa và không chạy lại.
- `Modelfile` nhập từ GGUF nguyên bản; sau `ollama create`, **phải có manifest trong kho models của riêng lượt chạy và tag thấy được qua đúng API trên port 12643** mới được gọi `/api/generate`.
- API generate: `stream=false`, `raw=true`, `keep_alive=0`, `num_ctx=256`, `num_predict=32`, `seed=20261108`, `temperature=0`; giữ phản hồi gốc. PASS chỉ khi có `done=true`, `eval_count` trong `[1,32]`, đúng tên model, cổng được sở hữu đúng, checksum gốc trước/sau không đổi và server riêng đã dừng/port đóng.
- Khi FAIL/HOLD: giữ toàn bộ `CLAIM.json`, `RESULT.json`, `serve.log`, `create.stdout.log`, `create.stderr.log`, `GENERATION_RAW_RESPONSE.json` (nếu có), snapshot SHA, thư mục local model store; **không tự động retry**.

## Cách thực hiện

1. Tải ZIP vào `Downloads`, kiểm tra SHA-256 theo hướng dẫn kèm ở chat rồi giải nén **vào chính xác** `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_single_smoke_source_v1` (không ghi đè thư mục có sẵn).
2. Có thể đọc trước với `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_single_smoke_source_v1\Run-TTM-T5-Ollama-Compatibility-Single-PS51.ps1" -Mode Preview`.
3. Thực hiện **đúng một lần** `-Mode Execute`; bộ chạy tự thực hiện preflight đầy đủ rồi tiếp tục import/generate. Nếu xuất hiện lỗi, không xóa `CLAIM.json`, không chạy lại.
4. Gửi `RESULT.json` và dòng console cuối để phân xử. Các tệp và log còn nguyên trong dự án.

## Phán quyết

- `PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE`: có thể chạy Ollama ở phạm vi smoke.
- `FAIL_OR_HOLD_COMPATIBILITY_ONLY_NO_RERUN` hoặc `HOLD_*`: giữ bằng chứng và điều tra, không cấp thêm lượt tùy tiện.
- Luôn giữ `T5_STRICT_PARITY=FAIL_7_OF_8_PRESERVED`, không mở P02/P03/T4 train hoặc TEST, không sửa `main` và `lineage.md`.

Nguồn chuẩn Ollama: https://docs.ollama.com/import ; https://docs.ollama.com/api/generate ; https://github.com/ollama/ollama/blob/main/docs/windows.mdx
