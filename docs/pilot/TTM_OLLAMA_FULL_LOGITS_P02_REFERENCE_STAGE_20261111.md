# TTM Ollama full logits — P02 F32 reference stage (2026-11-11)

Phép kiểm source-only trên Windows do chủ dự án báo cáo: `git apply --check=PASS`; `test_independent_full_logits_audit.py=PASS 5/5`. Đây là bằng chứng do chủ dự án cung cấp trong hội thoại; **không phải independent remote readback hoặc bằng chứng Ollama full logits**.

## Phạm vi giai đoạn

Tạo **đúng bốn** reference P02 PyTorch F32 từ checkpoint step1024 (SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`), source P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, prereg Git blob `fdcb81064a6c55b3dca5f71e18defff0895c0568`.

- `FL01=[97,98,99]`, `FL02=[257,304,111]`, `FL03=[97,10,98]`, `FL04=[88,267,628,195,160,111]`. Một vector `logits[-1,:]` có 2048 phần tử/chương trình; không softmax hay chọn top-K. Tổng 8192 giá trị.
- `produce_fl01_fl04_p02_reference.py` chỉ nạp checkpoint và mã P02 đã pin, chạy `eval()`, `torch.inference_mode()`, `cpu`, `float32`, kiểm biến thể `GELU=erf`. Chỉ ghi file mới bên trong TTM; không truy cập TEST/Q1Q2, huấn luyện hoặc Ollama.
- `verify_fl01_fl04_p02_reference.py` là kiểm toán độc lập **về cấu trúc và provenance công bố**, không nạp model, không xác minh số học bằng lần inference thứ hai. Có 7 kiểm thử âm/dương offline, kiểm exact 4×2048, số hữu hạn, token IDs, nguồn/checkpoint.
- Ghi `REFERENCE_P02_F32_FL01_FL04.jsonl` và `REFERENCE_INDEPENDENT_SEAL.json` trong `_tmp/ttm_ollama_full_logits_reference_fl01_fl04_20261111`, khóa SHA ngay trong lần chạy. Không đẩy logits thô hoặc checkpoint lên GitHub công khai.
- Script PowerShell: `tools/ollama_full_logits_v1/Invoke-TTM-Ollama-FullLogits-P02-Reference-PS51.ps1 -CheckpointPath <exact local .pt path in TTM>`. Khi checkpoint chưa có, dừng trước tạo reference.
- Không chạy lại nếu đã có thư mục stage; giữ nguyên bằng chứng lỗi để xét recovery. Không thay v5 hoặc `lineage.md`.

**Bước tiếp theo sau khi thấy owner receipt:** xác nhận original reference SHA + independent seal, khóa thành technical evidence trên nhánh; sau đó riêng biệt build runner Ollama có opt-in pre-sampler raw tensor hook, bảo đảm child-process provenance và so sánh đủ 8192 logits. Không gọi chỉ numeric pass là Ollama full-logit pass.
