# G1-P0 — Thử nhanh chuyển giao biểu diễn trên hai Qwen thật

**Ngày:** 2026-11-10  
**Loại:** `EXPLORATORY_POC_ONLY`, không phải G1 confirmatory/science; không dùng TEST riêng tư.  
**Nhiệm vụ:** trả lời nhanh liệu đường tính toán source hidden → target hidden → target functional response có chạy và cho tín hiệu định hướng được hay không.  
**Dừng quản trị:** Không xây service broker/witness/ACL/GPU production mới chỉ để làm PoC. Các gate G1 gốc vẫn HOLD và phải thẩm định trước G1 science thực sự.

## Phạm vi đúng một lượt

- Hai mô hình **thực**: Qwen3-0.6B `c1899de289a04d12100db370d81485cdf75e47ca` và Qwen3-1.7B `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`, `hidden_states[28]`, 8 cặp probe đúng chuỗi trong hợp đồng G1.
- 24 câu **tự viết trong mã nguồn**, 16 fit / 8 eval, cố định trước khi chạy; **không** lấy TinyStories, T1, hay G1 private TRAIN/DEV/TEST; không chạm original TTM VAL/TEST.
- Ridge đa đầu ra `alpha=100` cố định (không chọn trên 8 eval), so sánh `aligned`, `direct`, `target_oracle`, `shuffled`, `train_mean` bằng MSE và normalized gain. Không ước lượng p-value, CI, power hay claim SIX ưu việt.
- Frozen Qwen inference trên Colab Free T4 (không train hay tạo checkpoint). Giải phóng 0.6B trước khi nạp 1.7B. Demo best-effort guard 2100 giây / peak reserved 12 GiB; **không phải GPU watchdog production**.
- Chỉ xuất 1 JSON metric receipt, nguồn SHA/commit, phiên bản Qwen và hashed prompts; không lưu hidden tensors. Kết quả này **không** được ghi `lineage.md` như scientific PASS/FAIL.

## Nguồn đã ghim

- Script: `scripts/research/six_ttm/poc/g1_real_qwen_tiny_poc.py`.
- Immutable source commit: `ea774dda50c67c6244908d166d356342b36747fd`.
- Exact Git blob SHA-1: `cefc05f482dd6b488a1b7889275e6104d0a44684`.
- Local author sanity check trên bản phát triển tương đương: PASS_SELFTEST_SYNTHETIC_ONLY; **bản nguồn GitHub không được xem như đã chạy T4**. Trước run, cell bên dưới tự gọi selftest trên đúng bytes ghim.
- G1 research chính giữ nguyên: `d5d0c5346a595557a76349f900d09be50bce289c`. Original private TEST and production gates HOLD.

## Chạy trong **một cell Google Colab** (chọn GPU Tesla T4)

```python
import sys, subprocess, hashlib, pathlib
from urllib.request import urlretrieve

subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                       "transformers>=4.55,<6", "accelerate>=1.0", "safetensors>=0.4"])

url = "https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/ea774dda50c67c6244908d166d356342b36747fd/scripts/research/six_ttm/poc/g1_real_qwen_tiny_poc.py"
script = pathlib.Path("/content/g1_real_qwen_tiny_poc.py")
urlretrieve(url, script)
blob = script.read_bytes()
blob_sha1 = hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\\0" + blob).hexdigest()
assert blob_sha1 == "cefc05f482dd6b488a1b7889275e6104d0a44684", "SOURCE_SHA_MISMATCH"

subprocess.check_call([sys.executable, str(script), "--mode", "selftest"])
subprocess.check_call([sys.executable, str(script), "--mode", "run",
                       "--output", "/content/g1_p0_real_qwen_receipt.json"])
```

**Lưu ý:** Python literal `b"\\0"` trong mã trên cần biểu diễn đúng một byte NUL. Nếu copy markdown mà phát sinh lỗi escape, dùng `bytes([0])` thay thế. Không dùng mã động từ branch `main`. Có thể tải JSON bằng Colab Files hoặc tự sao chép lên Drive; không lưu private test.

## Phán quyết ngay sau receipt

- Nếu đủ vector shape, 8 teacher functional responses, MSE cho năm phương án: `PIPELINE_REAL_QWEN_FEASIBLE`, dù aligned MSE có thể kém baseline.
- Nếu `aligned` tốt hơn `train_mean` và `shuffled`: ghi `EXPLORATORY_DIRECTIONAL_SIGNAL`, không `G1_SCIENCE_PASS`. So với `direct` để xem tầng biểu diễn target có đem lại lợi ích không.
- Nếu aligned kém: pipeline có thể chạy nhưng tín hiệu không được chứng minh. Owner quyết định **không đầu tư thêm** hoặc điều chỉnh thí nghiệm sau, không cần mở TEST.
- Nếu STOP do download/OOM/time: `TECHNICAL_STOP`, không phải khoa học FAIL.

**Không có owner science permit; không chạy G1 original.**

## Bước thực hiện tiếp theo

`TTM_SIX_G1_P0_REAL_QWEN_COLAB_ONE_SHOT_EXPLORATORY_FEASIBILITY`: chạy đúng một cell Colab T4, cung cấp `G1_P0_RESULT` hoặc traceback và receipt JSON. Trả một quyết định `CONTINUE_G1_ORIGINAL / STOP_OR_REDESIGN / TECHNICAL_STOP` dựa trên tín hiệu thật, rồi mới cân nhắc đóng một lô gate cho G1 original nếu còn đáng nghiên cứu.
