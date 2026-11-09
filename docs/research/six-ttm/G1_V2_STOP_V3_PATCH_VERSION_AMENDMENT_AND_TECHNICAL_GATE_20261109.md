# G1 — Giữ STOP v2 và sửa cổng Python theo nhánh 3.13 (v3)

Ngày 2026-11-09. Trạng thái: `V2_STOP_PRESERVED / V3_STATIC_STRUCTURE_PASS_SCOPED / V3_RUNTIME_NOT_EXECUTED / G1_SCIENCE_LOCK_HOLD`.

## 1. Biên bản do chủ sở hữu cung cấp — v2 (bất biến)

- `G1_V2_SCRIPT_BLOB=c98811e167696f86e94e3da9d01f3b9f020c3cc6`: trùng blob v2 đã công bố.
- `G1_V2_STATIC_COMPILE=PASS`: **trong phiên Colab đó**, script v2 đã biên dịch.
- `G1_V2_PREFLIGHT_EXIT=1`; `G1_V2_PREFLIGHT_RECEIPT.status=STOP_FAIL_CLOSED`; `error=PYTHON_3_13_16_REQUIRED`; `science_executed=false`.
- Ô 2 dừng `STOP_PREFLIGHT_NOT_PASS_FOR_V2` trước khi đánh dấu one-shot hoặc tải trọng số. Đây là **hành vi chặn đúng thiết kế**; không phải kết quả tensor hay khoa học.
- **Không có trường Python thực tế trong receipt v2 khi dừng sớm**; chỉ biết giá trị `platform.python_version()` không bằng `3.13.16` tại thời điểm v2. Inventory v1 trước đó từng báo `3.13.16`, không suy diễn rằng v2 cũng vậy. Nguyên nhân chi tiết vẫn `UNKNOWN_ACTUAL_INTERPRETER_VERSION`. Không định nghĩa đây là lỗi PyTorch/Qwen.
- Biên bản console do chủ sở hữu gửi đã được ghi lại dưới dạng diễn giải; chưa xác minh SHA-256 một tệp receipt gốc.

## 2. Sửa v3: chỉ nới patch Python, giữ cổng thực chất

Script v2 **không sửa**: `scripts/research/six_ttm/g1_qwen06_zero_science_smoke_colab_env_20261109_v2.py` / Git blob `c98811e167696f86e94e3da9d01f3b9f020c3cc6`.

Script v3 mới: `scripts/research/six_ttm/g1_qwen06_zero_science_smoke_colab_env_20261109_v3.py`, Git blob `f394293a7c43d8c726d88a1a9b9f63ab49fe3d4a`.

- Chấp nhận chính xác Python **3.13.x bản ổn định**, không chấp nhận `3.12`, `3.14` hoặc `alpha/beta/rc`. Đây là cổng **technical preflight**; ghi full patch version và `sys.executable` vào receipt để đối chiếu, không tự nhận là version science-lock cố định.
- Các gói vẫn phải khớp **exact** với inventory v1: `torch=2.14.1+cu130`, `transformers=5.22.1`, `huggingface-hub=1.33.0`, `tokenizers=0.23.3`, `safetensors=0.8.0`; GPU `Tesla T4, CC7.5`, memory/disk guards giữ nguyên.
- Teacher ID/revision `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca`; expected model weight SHA-256 `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b`. Vẫn SHA before load; không training; hai synthetic fixtures; 29 tensors; FP16.
- Tách đường receipt v3 vào `/content/ttm_six_g1_v3` tránh ghi đè các receipt v1/v2.

Notebook v3: `notebooks/six_ttm/TTM_SIX_G1_V3_COLAB_PY313_PATCH_FLEX_PREFLIGHT_ONESHOT_SMOKE_20261109.ipynb`, Git blob `f00554c0ceda46f8c4b7f6a8b54cc7a88cb0ddfa`.

- **Ô 1**: ghi full Python và đường dẫn thực thi; tải script nhỏ theo commit bất biến, đối chiếu Git blob, `ast.parse`, `py_compile` và `--phase preflight`; không tải trọng số Qwen.
- **Ô 2**: **chỉ sau ô 1 PASS**; kiểm lại source blob, receipt v3, phiên bản Python và đường dẫn thực thi giống ô 1, Torch, các gói exact, GPU T4. Marker với `open("x")` được tạo trước download, ngăn lặp lại trong cùng runtime. `--phase smoke` mới tải ~1,5 GB teacher và chạy no-grad. Không tự reset marker khi FAIL; mọi dữ liệu trong thư mục v3.
- Nếu Python thực tế không phải 3.13.x, hoặc thư viện bị đổi, ghi STOP và đưa inventory vào một lần rà soát; **không tự sửa thêm phiên bản hoặc cài hạ cấp**.

## 3. QA và quyết định

- Đọc lại trên GitHub: script v3 đúng Git blob `f394293a7c43d8c726d88a1a9b9f63ab49fe3d4a`, notebook đúng blob `f00554c0ceda46f8c4b7f6a8b54cc7a88cb0ddfa`.
- `14/14` kiểm tra cấu trúc mã và notebook PASS trong phạm vi: bảo toàn v2, kiểm Python 3.13 stable, giữ exact library/GPU/model/weight, SHA trước load, cô lập root, ghi interpreter, gate ô 2, one-shot marker và không tự train.
- **Đây không phải biên dịch hay chạy v3 trong Colab.** `V3_AST/PY_COMPILE=NOT_EXECUTED`, `V3_COLAB_PREFLIGHT=NOT_EXECUTED`, `V3_MODEL_DOWNLOAD=NOT_EXECUTED`, `V3_SMOKE=NOT_EXECUTED`, `G1_SCIENCE_LOCK=HOLD`.
- Không cập nhật `main`, không mở/đóng PR #12, không sửa repo SIX hoặc `lineage.md`, không chạy train. PR #12 đã được merged bởi tuyến khác; G1 không gây hoặc sửa sự kiện đó.

## 4. Bước thực hiện tiếp theo

`TTM_SIX_XMODEL_G1_V3_COLAB_PREFLIGHT_READBACK_THEN_SINGLE_SMOKE`.

Mở notebook v3 theo commit được liên kết trong báo cáo; **chạy ô 1 trước và đọc `G1_V3_NOTEBOOK_PYTHON`, `G1_V3_STATIC_COMPILE`, `G1_V3_PREFLIGHT_RECEIPT`**. Nếu `PASS_PREFLIGHT_ONLY`, chủ sở hữu có thể chạy ô 2 **đúng một lần**; nếu STOP không chạy ô 2. Gửi console hoặc receipt để thẩm định. Không yêu cầu thay đổi TTM-Small-4M hay tải mô hình ở bước tiền kiểm.
