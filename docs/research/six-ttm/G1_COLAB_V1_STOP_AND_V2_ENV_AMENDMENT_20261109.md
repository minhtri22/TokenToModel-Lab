# G1 — Thẩm định STOP Colab v1 và sửa hợp đồng môi trường v2

**Ngày:** 2026-11-09  
**Trạng thái:** `V1_PREFLIGHT_STOP_EXPECTED / V2_SOURCE_AND_NOTEBOOK_QA_PASS_SCOPED / V2_COLAB_NOT_EXECUTED / G1_SCIENCE_LOCK_HOLD`  
**Phạm vi:** TTM × SIX G1; chỉ sửa trên `research/ttm-six-cross-model-representation-transfer-20261109`; không sửa `main`, corpus, TTM train/checkpoints, `lineage.md` hoặc repo SIX.

## 1. Bằng chứng do chủ sở hữu gửi từ Colab (lượt v1 đã tiêu thụ)

- `G1_NOTEBOOK_MODE=ZERO_SCIENCE_PREFLIGHT_ONLY`.
- `G1_SOURCE_BLOB_SHA=24318de7d0196944a0a9a6d6be9851099f18b85b`: **khớp** script gốc.
- Python **3.13.16**, PyTorch **2.14.1+cu130**, Transformers **5.22.1**, huggingface-hub **1.33.0**, tokenizers **0.23.3**, safetensors **0.8.0**.
- `CUDA_AVAILABLE=True`, `GPU_NAME=Tesla T4`, `GPU_CC=(7,5)`.
- GPU free **15,527,116,800 bytes** (~14.46 GiB), GPU total **15,637,086,208 bytes**, disk free **120,839,077,888 bytes** (~112.54 GiB).
- `G1_PREFLIGHT_EXIT_CODE=1`; `G1_PREFLIGHT_RECEIPT.status=STOP_FAIL_CLOSED`; `error=PYTHON_3_12_10_REQUIRED`; `science_executed=false`.
- Chẩn đoán: script v1 dừng ở kiểm tra Python trước khi kiểm package/GPU và trước tải trọng số. Nguồn mã đúng, GPU phù hợp theo inventory; **không** diễn giải là preflight PASS tổng thể hoặc model runtime FAIL.

**Không ghi đè receipt STOP và không sửa script v1**. Người dùng đã cung cấp nội dung receipt và console, chưa có tệp receipt bytes độc lập để tính SHA-256. Trạng thái provenance `OWNER_CONSOLE_READBACK_NOT_FILE_SHA_VERIFIED`.

## 2. Sửa đổi có giới hạn v2, không tự cài thư viện

Nguồn script v2 mới: `scripts/research/six_ttm/g1_qwen06_zero_science_smoke_colab_env_20261109_v2.py`.
- Git blob script v2: `c98811e167696f86e94e3da9d01f3b9f020c3cc6`.
- Commit tạo script v2: `66cbc40ee65072c375bccdc3eebfceb76236174e`.
- Python mới khóa **3.13.16**; Torch **2.14.1+cu130** giữ nguyên.
- Package mới khóa chính xác: `transformers=5.22.1`, `huggingface-hub=1.33.0`, `tokenizers=0.23.3`, `safetensors=0.8.0`.
- Đổi `from_pretrained(..., torch_dtype=torch.float16)` sang `from_pretrained(..., dtype=torch.float16)` theo API Transformers 5.x, vẫn FP16 trên Tesla T4. Đây là thay đổi **khả thi về mặt API**, cần thực chứng bằng v2 smoke.
- Không thay model id `Qwen/Qwen3-0.6B`, model revision `c1899de289a04d12100db370d81485cdf75e47ca`, expected `model.safetensors` SHA-256 `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b`, guards về GPU/memory/disk, 29 hidden states, 28 lớp, hidden width 1024, 2 đầu vào synthetic, 2 lần forward, không train.
- Đã kiểm tra tree tại revision gốc: `config.json`, `generation_config.json`, `merges.txt`, `vocab.json`, `tokenizer.json`, `tokenizer_config.json`, `model.safetensors`, `LICENSE` đều hiện diện. Không tự tải model khi chưa qua preflight.

Notebook mới: `notebooks/six_ttm/TTM_SIX_G1_COLAB_ENV_V2_PREFLIGHT_AND_ONESHOT_SMOKE_20261109.ipynb`.
- Git blob notebook v2: `8430ec9a2616a73fe08e495be6ff71b5296125fe`.
- Commit notebook: `862239833f1ba970d4ad9ae6cbde934ca024b52e`.
- **Ô 1:** fetch script nhỏ theo exact commit và kiểm Git blob SHA, `ast.parse` và `py_compile` **trong chính Colab**, gọi `--phase preflight` (không tải trọng số).
- **Ô 2:** chủ sở hữu chọn chạy riêng; chỉ qua khi receipt ô 1 = `PASS_PREFLIGHT_ONLY`, `environment_amendment` đúng `COLAB_RUNTIME_20261109_V2`, phiên bản Python/Torch/T4 đúng; tạo `G1_SMOKE_ATTEMPTED_V2.marker` bằng open `x` **trước** download; gọi `--phase smoke` một lần, đọc `G1_SMOKE_RECEIPT.json`. Không tự chạy lại khi fail. Phạm vi dữ liệu `/content/ttm_six_g1`, không Drive.
- Ngân sách file tải teacher: ~1.5 GB, chỉ xuất hiện nếu chủ sở hữu chạy riêng ô 2.

## 3. Thẩm định mã mới

Đã đọc lại file qua GitHub connector và kiểm 15/15 điều kiện tĩnh có phạm vi: script nguồn cũ không đổi; exact blob v2 và notebook; không tự cài package; source hash check; AST/compile **được đưa vào ô Colab**; không tải trọng số ở ô 1; ô 2 yêu cầu preflight pass; marker một lần; pin Python/Torch/package; model revision và SHA nguồn; SHA trước load; không optimizer/backward; trạng thái `science_executed=False`; notebook cells chưa thực thi.

**Phân biệt rõ:** `V2_STATIC_SOURCE_STRUCTURE=PASS_SCOPED`; `V2_COLAB_AST_PY_COMPILE=NOT_EXECUTED`; `V2_COLAB_PREFLIGHT=NOT_EXECUTED`; `V2_SMOKE=NOT_EXECUTED`. Không được gọi v2 runtime PASS trước khi có receipt.

## 4. Quyết định và ranh giới nghiên cứu

- `V1_EXPECTED_STOP_PRESERVED=YES`.
- `V2_ENV_AMENDMENT_ACCEPTED_FOR_TECHNICAL_READINESS=YES` dựa trên inventory chủ sở hữu, nhưng chỉ trong branch SIX × TTM.
- `QWEN_WEIGHT_BYTES_SHA256=NOT_CHECKED`, `QWEN_HIDDEN_STATES_RUNTIME=NOT_CHECKED`, `G1_SCIENCE_LOCK=HOLD`.
- Nếu v2 preflight FAIL, giữ STOP, không chạy ô 2; phân tích trong một lượt thẩm định kỹ thuật. Nếu PASS, có thể chạy đúng một smoke technical zero-science; dù PASS cũng chưa mở thí nghiệm G1 dựa trên corpus/probe bank nếu chưa chốt tiền đăng ký khoa học.
- Lộ trình TTM-Small-4M độc lập. Không có quyền tự thay đổi local repo hoặc merge nhánh mới; `main` và PR #12 có thể đã đổi do tác nhân khác trong quá trình G1, phải đọc lại chứ không tự đồng bộ.

## Bước thực hiện tiếp theo

`TTM_SIX_XMODEL_G1_V2_COLAB_PREFLIGHT_AND_SINGLE_ZERO_SCIENCE_SMOKE_READBACK`:

Mở notebook v2 tại chính SHA của nhánh; chạy ô 1, chỉ khi `PASS_PREFLIGHT_ONLY` mới chủ động chạy ô 2. Gửi `G1_PREFLIGHT_RECEIPT.json` và (nếu có) `G1_SMOKE_RECEIPT.json` hoặc toàn bộ console. Phân biệt STOP kỹ thuật với kết luận khoa học, giữ mọi bằng chứng FAIL.
