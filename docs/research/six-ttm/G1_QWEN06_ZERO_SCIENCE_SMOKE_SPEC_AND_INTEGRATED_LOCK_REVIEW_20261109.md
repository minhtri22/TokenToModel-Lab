# G1 — Đặc tả kiểm thử trạng thái ẩn Qwen3-0.6B và thẩm định khóa tích hợp

**Ngày:** 2026-11-09  
**Nhánh nghiên cứu duy nhất:** `research/ttm-six-cross-model-representation-transfer-20261109`  
**Trạng thái:** `DESIGN_AND_GATED_RUNNER_PREPARED / RUNTIME_SMOKE_NOT_EXECUTED / G1_SCIENCE_LOCK_HOLD`  
**Nguồn TTM main:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a` tại thời điểm đọc lại; không cập nhật, không merge.  
**PR #12:** tuyến pilot TTM-Small-4M độc lập, vẫn OPEN/DRAFT tại thời điểm G1; HEAD có thể tiếp tục đổi do tuyến chính.

## 1. Mục tiêu của đúng một kiểm thử tổng hợp

Đánh giá kỹ thuật liệu `Qwen3-0.6B` được tải từ **revision và SHA-256 cố định** có thể xuất các trạng thái ẩn trên hai tiền tố tổng hợp mà không train, không dùng dữ liệu nghiên cứu, không lộ TEST, không gọi API bên ngoài để inference. Kiểm tra đúng số lớp, shape, dtype, mask, hữu hạn (finite), tính lặp trên cùng runtime, GPU peak, checksum. Thử nghiệm này **không** đo chuyển giao biểu diễn SIX, không đánh giá tính đúng ngữ nghĩa và không cấp quyền khoa học G1.

Mã duy nhất: `scripts/research/six_ttm/g1_qwen06_zero_science_smoke.py`, tệp được khóa sơ bộ tại commit `a7191d5611d959cd90ea345ecb055f5816a7be1c`; Git blob `dde9267b5a2d631365ce555e59fed403d0921657`.

## 2. Nguồn và môi trường ứng viên (khóa trước smoke)

| Thành phần | Pin và lý do | Cổng |
|---|---|---|
| Model ID | `Qwen/Qwen3-0.6B` | Exact |
| Revision | `c1899de289a04d12100db370d81485cdf75e47ca` | Exact, không lấy `main` |
| Weights | `model.safetensors`; SHA-256 công khai `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b` | **Tính lại SHA-256 bytes đã tải rồi mới load** |
| LICENSE | `Apache-2.0` ở cùng revision | Giữ nội dung giấy phép và nguồn |
| Tensor expected | `num_hidden_layers=28`, `hidden_size=1024`, `vocab_size=151936` | Kiểm `config.json` trước load; `hidden_states` 29 tensors |
| Python | `3.12.10` | Pin lấy từ env Colab T3 đã đọc trước; lệch phải HOLD |
| PyTorch | `2.14.1+cu130` | Pin ứng viên dựa trên Colab T3; khác phiên bản → HOLD, không tự cài |
| Transformers | `4.57.6` | Pin tương thích Qwen3 |
| Hugging Face Hub | `0.36.0` | Pin phụ thuộc |
| Tokenizers | `0.22.1` | Pin phụ thuộc |
| Safetensors | `0.6.2` | Pin phụ thuộc |
| GPU | **Tesla T4 CUDA CC 7.5**, GPU >= 12 GiB tổng và >= 8 GiB rảnh | FP16, không BF16 trên T4 |
| Local Colab disk | >= 6 GiB rảnh trước tải | Không ghi vào Windows / không ghi Drive |
| Peak CUDA reserved | <= 6 GiB, nếu vượt thì FAIL kỹ thuật | Không sửa ngưỡng sau chạy |

Tệp trọng số được HF công bố ~1,5 GB; FP16 lý thuyết ~1,50 GB cho 751,6M tham số, **chưa tính overhead**. Với batch=2, sequence <=64, hình dạng mỗi hidden tensor `[2,seq_len,1024]`. Tổng 29 trạng thái ở seq=64, FP16 khoảng **7,25 MiB** chưa tính logits (~37,1 MiB), trạng thái trung gian hay bản copy. Đây chỉ là tính toán ước lượng, không phải số đo GPU.

Nguồn công khai ghim:
- https://huggingface.co/Qwen/Qwen3-0.6B/tree/c1899de289a04d12100db370d81485cdf75e47ca
- https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors
- https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/config.json
- https://huggingface.co/docs/transformers/v5.6.0/en/model_doc/qwen3
- https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html

**Giới hạn:** SHA-256 trọng số trên là giá trị **do nhà cung cấp công bố**, chưa được tính lại từ bytes tải trên Colab. Hash mọi tệp tokenizer, config, LICENSE sẽ ghi từ bytes đã tải và trong receipt; phiên bản môi trường T3 là ứng viên, **không** khẳng định runtime Colab hiện tại giống T3. Bất kỳ chênh lệch nào yêu cầu sửa kế hoạch trước khi chạy; không phá tính tái lập bằng `pip install -U` tự động.

## 3. Lượt kiểm thử kỹ thuật hữu hạn, không chạy khoa học

Bộ chạy chỉ hỗ trợ hai pha; không có lệnh train hay API sản sinh embedding từ dữ liệu người dùng:

1. `--phase preflight`: thực thi tại **Google Colab** trong môi trường đã cài đúng các dependency; kiểm Python/Torch/libraries/GPU/VRAM/disk; không tải model.
2. `--phase smoke` (chỉ sau preflight PASS và quyết định sử dụng cùng runtime): tải đúng các tệp tại revision qua HF Hub, SHA-256 từng tệp, đối chiếu weight SHA **trước khi load**, kiểm config, nạp bằng FP16 GPU, chạy **hai input tổng hợp** và lặp forward hai lần trong `torch.inference_mode()`, `use_cache=False`, `output_hidden_states=True`.

Hai fixture cố định: `x0 x1 ... x7` và `a0 a1 ... a15`; tokenize độc lập, batch padding phải tồn tại, dài từ 8 đến 64 token. Mọi trạng thái ẩn phải có shape `[2,L,1024]`, giá trị finite; logits `[2,L,151936]` finite; chọn các layer index `0,7,14,21,28`; chỉ hash vector của token cuối hợp lệ sau chuyển FP32, **không xuất tensor thô**. Hai forward trên cùng runtime phải cho cùng SHA-256; khác → `REPEATABILITY_MISMATCH` và dừng. GPU max reserved <=6 GiB.

Bộ chạy ghi receipt:
- `/content/ttm_six_g1/G1_PREFLIGHT_RECEIPT.json`
- `/content/ttm_six_g1/G1_SMOKE_RECEIPT.json`

**Đây là đường trong Colab, không phải đường Windows.** Không tạo Google Drive, không sửa checkpoint, không đụng repo SIX, không viết `lineage.md`. Không tự động tải lại khi FAIL. Nếu thất bại, gửi receipt/console ra ngoài để phân tích và giữ nguyên lịch sử fail.

## 4. Hướng dẫn vận hành bằng Colab — chỉ khi chủ sở hữu quyết định chạy

Trong **một runtime Colab GPU miễn phí** đã có PyTorch `2.14.1+cu130` và Python `3.12.10`. Kiểm tra từ `--phase preflight` phải báo PASS trước khi bắt đầu download.

Clone đúng nhánh, kiểm origin/ref SHA và tệp:
```bash
git clone --single-branch --branch research/ttm-six-cross-model-representation-transfer-20261109 \
  https://github.com/minhtri22/TokenToModel-Lab.git /content/ttm_six_g1_checkout
cd /content/ttm_six_g1_checkout
git remote get-url origin
git rev-parse HEAD
git cat-file -p dde9267b5a2d631365ce555e59fed403d0921657 >/dev/null
```

Chọn đúng phiên bản các thư viện ở trên và đối chiếu với receipt; **không dùng lệnh nâng cấp toàn bộ PyTorch**. Khi môi trường tương thích:
```bash
python /content/ttm_six_g1_checkout/scripts/research/six_ttm/g1_qwen06_zero_science_smoke.py --phase preflight
# Chỉ sau khi PRECHECK PASS:
python /content/ttm_six_g1_checkout/scripts/research/six_ttm/g1_qwen06_zero_science_smoke.py --phase smoke
```

Trước khi chạy, có thể xác minh chính xác tệp script so với commit cũ:
```bash
cd /content/ttm_six_g1_checkout
git rev-parse HEAD:scripts/research/six_ttm/g1_qwen06_zero_science_smoke.py
# Phải trả về dde9267b5a2d631365ce555e59fed403d0921657.
```

**Quan trọng:** `git cat-file` ở trên kiểm tra *sự tồn tại* blob; `git rev-parse HEAD:path` mới kiểm chứng blob đang được dùng. `preflight` không tự cài thư viện. Bản mẫu này chưa chạy và chưa xác minh runtime thực tế. Nếu không có đúng phiên bản môi trường đã khóa, trả `HOLD_ENV` thay vì tự ép cài lại môi trường TTM-Small-4M.

## 5. Thẩm định tích hợp: đủ tiêu chí G1 science lock chưa?

| Điều kiện | Trạng thái sau thiết kế | Có được mở science? |
|---|---|---|
| Mốc SIX / provenance | G0 đã audit PASS có phạm vi | Không tự cấp phép |
| Qwen weights SHA nguồn công bố | PINNED_EXPECTED | Không thay hash bytes Colab |
| Script/nhánh/shape và negative path | CODE_COMMITTED, STATIC_REVIEW_PENDING | Chưa |
| Runtime phiên bản/Colab T4 | CANDIDATE_PINNED_NOT_RECHECKED | Chưa |
| Actual bytes SHA + hidden states | NOT_EXECUTED | Chưa |
| Dữ liệu/rights/probe bank/G1 primary thresholds | PREREG_DRAFT_HOLD | Chưa |
| Baseline TTM-Small-4M đã trained | G3_DEPENDENCY_NOT_READY | Không chặn G1 teacher |

**Adjudication:** `G1_ZERO_SCIENCE_RUNNER_READY_FOR_STATIC_QA`, `G1_TECHNICAL_SMOKE_NOT_EXECUTED`, `G1_SCIENCE_LOCK=HOLD`. Không đánh đồng thiết kế, mã được commit với test PASS. Sau một lượt static QA và một smoke Colab đạt, thẩm định một lần hợp đồng khoa học G1, không phát sinh chuỗi cấp phép nhỏ riêng.

**Bước thực hiện tiếp theo:** `TTM_SIX_XMODEL_G1_STATIC_QA_AND_COLAB_TECHNICAL_PREFLIGHT_EXECUTION` — chạy static QA độc lập và một preflight trên Colab; nếu PASS rồi mới quyết định tải model/chạy smoke; không train và không can thiệp PR #12.
