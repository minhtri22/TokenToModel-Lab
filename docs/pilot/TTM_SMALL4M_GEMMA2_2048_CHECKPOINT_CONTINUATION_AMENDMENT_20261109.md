# AMENDMENT — TTM-Small-4M × EmbeddingGemma 2: GPU 2.048 via verified step1024 checkpoint bridge

**Ngày:** 2026-11-09. **Chủ dự án xác nhận:** sau khi phát hiện tiền tố TRAIN 1.024 bước giống nhau, **không chạy lại 1.024 bước đã tiêu thụ**; sử dụng đúng bốn checkpoint cuối A/B/C/D từ GPU1024 như tiền tố và thực thi **thêm 1.024 bước mỗi arm** để đạt 2.048 bước tổng thích nghi. **TRẠNG THÁI TẠI AMENDMENT:** `NOT_EXECUTED`, không có CLAIM mới hoặc VALIDATION mới. Đây là sửa đổi hợp đồng **trước khi bắt đầu GPU2048**, không được viết lại hợp đồng hay kết quả 1.024 đã có.

**Mã định danh thí nghiệm đích giữ nguyên**: `ttm_small4m_gemma2_directswap_2048x4096_t4_gpu_20261109_v1`, chỉ tạo khi đã kiểm mọi điều kiện bridge. **Thí nghiệm nguồn đã đóng**: `ttm_small4m_gemma2_directswap_1024x4096_t4_gpu_20261109_v1`. Không sử dụng tính năng `--resume` của thí nghiệm nguồn để tạo kết quả khác; không sửa các tệp gốc.

## 1. Thay đổi so với tiền đăng ký trước đó

[Tiền đăng ký phiên bản 1](TTM_SMALL4M_GEMMA2_DIRECTSWAP_2048_GPU_EQUAL_EXPOSURE_ONE_SHOT_PREREG_20261109.md), commit `d942c32ed3da053a57e8ff22b1bc00d412a88ea7`, đã dự kiến chạy một lượt mới từ checkpoint TTM T4 step1024 cho toàn bộ 2.048 steps. **Phương án đó được SUPERSEDED BEFORE CLAIM** bởi amendment này; không sửa hoặc xóa lịch sử. Bộ chạy/notebook GPU2048 v1 là **DO_NOT_RUN**; cần sử dụng notebook bridge riêng ghim nguồn và hash.

**Lý do**: đúng 1.024 bước tiền tố cùng lịch TRAIN; checkpoint nguồn có đầy đủ model, optimizer, CUDA/CPU RNG và 1.024 loss. Để không lãng phí GPU, giữ nguyên prefix thực tế đó thay vì tính lại. **Giới hạn nhận thức**: kế thừa trạng thái thực là chính xác cho thao tác `continue from checkpoint`, nhưng không chứng minh nó *bitwise* bằng một lần tái khởi chạy 2.048 steps trong mọi môi trường. Đây là **một mở rộng có điều kiện dựa vào kết quả VAL cũ đã xem**, không phải replication độc lập. Không được dùng `DIRECT_SWAP_2048` như bằng chứng xác nhận ngoài mẫu.

## 2. Parent checkpoint exact pin

Parent folder read-only: [Drive GPU1024](https://drive.google.com/drive/folders/1JeRva6DWqT8b0ltC9R3SIz7ZhXEyuNe4).

- `CLAIM.json` original SHA256 `d7e99b831dcb69688e4a1483732f174125f8e1a10d5e73cea5c4ef9efcfb3011`; `RESULT.json` original SHA256 `46a93c888063c27711541c067d168ded31bbf22f6c46ba6efe45051cdc9c0bec` with all four arms complete.
- Parent schedule `train_schedule_sha256=19ddc05128c188b86bda2f02de6389946944fe287c26abbf7d24cc5f9681e8f2` (1.024 × 4.096 labels). New full schedule is `81e4834f991607e8c3143bb67ed4a9ade93faa5f9526f630dc79e85bb0e51a52` (2.048 × 4.096); **hash of first 1.024 steps of new schedule must equal parent schedule SHA**.
- Original GPU1024 runner SHA256 `00416c0ff5b2afdcca2780a20315dd2da0af93554cd2b32b6c94efb630dc5d3b`.
- Four parent `checkpoints/<ARM>/step_1024_attempt_00/{checkpoint.pt,READY.json}`:

| Arm | SHA256 original checkpoint.pt | Bytes |
|---|---|---:|
| A | `95bb69de752bf051958f0d8e19a388528d2cc102f02258c88d756526a9406aa2` | 45,100,187 |
| B | `8ecca1e181726965d4f6e76c8e725b612706d5242accd408a9386964939191d1` | 51,393,267 |
| C | `cb77a5c2e435dd8cf1f61259f560a22964bc8c8c06889b0494cb961ed76bc9ac` | 52,969,605 |
| D | `81003fa2fe194a7e22b30d1b3e330fc65ec0ae486a08511d17c367ec5c25f69f` | 52,969,605 |

Bridge must check exact SHA256, size, READY metadata (`arm,step,run_id,source,schedule`), payload schema, `input_sha256`, optimizer group hyperparameters, **every trainable AdamW param has step=1024**, 1.024 finite losses, single Tesla T4 CUDA RNG; plus original CLAIM environment `torch=2.14.1+cu130`, `cuda=13.0`, T4, `CUDA_FP32_NO_TF32`, microbatch8. **If environment differs, STOP without creating a new science CLAIM**. CPU QA can inspect all but cannot assert future GPU determinism.

## 3. New execution after the bridge

- A/B/C/D remain the original 4 model variants, same trainability, exact original checkpoint and donor candidate source, optimizer already at step1024, no reset.
- Shared fixed TRAIN schedule SHA256 `81e4834f991607e8c3143bb67ed4a9ade93faa5f9526f630dc79e85bb0e51a52`. **Only indices 1024...2047** (training steps 1025...2048) may be executed for each arm. 1.024 added steps × 4.096 = **4,194,304 additional TRAIN labels per arm**, 16,777,216 added over A/B/C/D; combined 2.048-step history = **8,388,608 labels per arm** and 33,554,432 overall including already-consumed prefix.
- AdamW state continues unchanged, LR 1e-4, no scheduler, gradient clip1, FP32, no TF32. New **incremental** GPU budget cap 5.400 seconds, count only added compute, record separately the parent original cumulative ~287.82035 seconds. Save new RUN_ID checkpoint READY-last after steps **1.280, 1.536, 1.792, 2.048** (4 per arm), to reduce preemption loss, with old 1.024 losses retained as prefix.
- **Source-to-new-run bridge receipt** under new Drive namespace pins original parent checkpoint SHA, original RUN_ID/source/schedule, imported step=1024, environment and verifier SHA. A per-arm start marker is written before the first new optimizer step: if interruption occurs before first new READY, fail closed; do not silently restart consumed steps. For interrupted run beyond new READY use exactly the same `RUN_ID`, `CLAIM`, source and schedule, with verified new READY checkpoint; no auto reset.
- At completion: **one** NLL VAL scoring pass for all arms, same 328 windows/256 stories/61.122 labels and 1,000 paired story bootstrap seed20261109. All three lower 95% CI bounds `A−C>0`, `B−C>0`, `D−C>0` required for `DIRECT_SWAP_2048_POSITIVE_EXPLORATORY`; otherwise `DIRECT_SWAP_2048_BENEFIT_NOT_ESTABLISHED`. This retained endpoint was already chosen after observing old VAL and thus is exploratory. **Never read TEST.**
- After one-shot execution, independent QA verifies source/parent hashes, imported optimizer/RNG/step, 4 complete step2048 new checkpoint files and readback, 256 story loss sums and CI, no duplicate/replayed steps. Only then append `lineage.md`. Existing L0015 negative GPU1024 outcome remains unchanged.
- `TTM_SMALL4M_EMBEDDINGGEMMA2_RESIDUAL_GATED_ARCHITECTURE_DESIGN_AND_MINIMAL_PROOF` remains `DEFERRED` until owner reviews the new GPU2048 adjudication. No additional training automatically authorized.

**Hard limits:** no edits to old GPU1024, original T4, 64-step evidence or main/PR#12; no deletion, no TRAIN/VAL arrays, checkpoint binaries or per-story private data committed to public GitHub. Do not start GPU merely because this document exists; bridge runner and negative QA must pass first.
