# TTM-Small-4M gốc — 1024→1280: runner kế nhiệm và kiểm thử CPU

Ngày 2026-11-09 · PR #13 trên repo `minhtri22/TokenToModel-Lab`. **Không chạy GPU, không tạo CLAIM, không viết lại T4 gốc; chỉ source+QA.**

## 1. Ranh giới khoa học

- Đối tượng duy nhất: T4 P02 3.749.376 tham số với embedding **gốc**, BPE2048, context256, checkpoint step1024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- Nhánh EmbeddingGemma2 chỉ dùng A làm **bằng chứng tham khảo**: A có optimizer mới, FP32 và LR 1e-4, **không** phải tiếp nối optimizer T4 gốc. B/C/D không tham gia.
- Mục tiêu `ttm_small4m_step1024_to1280_exploratory_v1`: khôi phục 1.024 → 256 bước mới × 4.096 nhãn = **1.048.576 exposures**; AdamW/LambdaLR/sampler, Python/NumPy/torch CPU+CUDA RNG và GradScaler nguyên trạng; FP16 microbatch8; LR sàn 3e-5. Không sửa trainer `t4_train_science_a2.py` hay khóa khoa học cũ.

## 2. Mã và cổng bảo vệ

- Runner [`tools/pilot_t4/original_1024to1280_20261109/ttm_t4_original_1024_to1280.py`](../..//tools/pilot_t4/original_1024to1280_20261109/ttm_t4_original_1024_to1280.py), SHA-256 `55cf8f9f686d911411ed3284ba6baf00b7a4ed1d7cc255e3f4fed1b9a2f5365c`, Git blob `1f539aedd04d7097f2cb26b0220b14bd106c8b65`.
- Kiểm thử độc lập [`tools/pilot_t4/original_1024to1280_20261109/test_ttm_t4_original_1024_to1280_offline.py`](../..//tools/pilot_t4/original_1024to1280_20261109/test_ttm_t4_original_1024_to1280_offline.py), SHA-256 `fad6d4860493209a285276dc12f1fd26d47ceb694b4aa8e1e64edbde456f7e28`, Git blob `e10ce2f0ce78d1d9aa0a7a7170735fefe79a825c`.
- Chế độ `inspect` **read-only CPU**: đối chiếu đúng Git blob P02/trainer/capacity/evaluator; manifest; file READY, log 1.024 bước, checkpoint 45.074.891 bytes và SHA, `torch.load(weights_only=True)`, optimizer step, scheduler, GradScaler/RNG. Không đọc TEST; không nhập donor.
- Chế độ `execute` yêu cầu `--lock` và `--lock-sha` mới chứa quyền `OWNER_APPROVED_ONESHOT_EXPLORATORY`, nguồn runner SHA, checkpoint parent, policy Colab Free, budget, không TEST. **Chưa tạo khóa này.** Đồng thời đòi một Tesla T4 và môi trường `torch=2.14.1+cu130`, CUDA13.0, để tránh tiếp nối sai môi trường.
- Bộ chạy reuse hàm TRAIN và đánh giá **từ bản mã A2 gốc đã pin** qua module import, nhưng không gọi `main()` T4 gốc, không thay đếm bước/lock gốc. Khóa mới được ghi vào checkpoint kế nhiệm riêng.
- `--resume-ready` chỉ từ đúng READY step1152, cùng RunID/lock, kiểm SHA checkpoint+progress+baseline, AdamW 1152 và scheduler1152; không tự restart từ step1024.
- Lưu thêm checkpoint/READY-last ở bước **1152** và **1280** trong namespace Drive mới; VAL step1152 diagnostic, step1280 primary. Bootstrap ghép cặp 256 truyện / 61.122 targets, 1.000 lượt seed20261109. PASS về VAL **không** tự đồng nghĩa truyện tốt.
- Không tự tải checkpoint lại, không công bố riêng tư: `checkpoint.pt`, TRAIN/VAL NPZ, per-story loss, raw TEST. Nhận parent từ Drive theo đúng SHA.

## 3. Kiểm thử offline đã thực thi

- Python **3.13.5**, PyTorch **2.10.0+cpu**: `py_compile=PASS_2_FILES`, unittest **22/22 PASS**, bao gồm negative QA SHA/READY, AdamW step/moments, thiếu NumPy RNG, thiếu GradScaler, scheduler drift, data pack pin, missing lock, source blob, refuse overwrite, paired bootstrap, CPU fixture restore deep equality.
- **Đọc checkpoint thật trên CPU:** từ [Drive step1024](https://drive.google.com/drive/folders/1pLmIEB595x_cEkez0299C7mI_mV4bMfO), `READY` SHA256 `b720f32da8efe2b39ebfa0aa94f0833ec3845a62c21b9407d8a04558f681d685`, `progress` SHA256 `5517cc69...606ec`, checkpoint SHA256 `cb985751...cb271b`; 52 tham số AdamW có trạng thái, optimizer step 1024, scheduler last_epoch1024, lr 3e-5, scaler và CUDA RNG hiện diện. CPU `checked_parent=PASS` **không tương đương** CUDA model restore/one-step success.
- QA JSON: `artifacts/qa/ttm-original1280/TTM_T4_ORIGINAL_1024_TO1280_SOURCE_CPU_QA_20261109.json`. Chưa chạy source từ HEAD GitHub này trên Windows; Git blob readback chỉ xác minh byte nguồn.

## 4. Đóng/Mở thực nghiệm

`SOURCE_QA=PASS_SCOPED` · `REAL_PARENT_CPU_INSPECT=PASS` · `GPU=NOT_EXECUTED` · `NEW_LOCK=NOT_ISSUED` · `CLAIM=NOT_CREATED` · `QUALITY=NOT_ADJUDICATED`. Để chạy, cần phê duyệt lock science mới trên một review gộp, notebook Colab với source SHA/Drive/Free T4, CPU/GPU preclaim và lưu bằng chứng độc lập; không cấp phép chỉ vì source PASS. `MERGE_DECISION=HOLD` cho PR #13. `lineage.md` append-only và không thay đổi trong lượt QA.

**Bước thực hiện tiếp theo:** `TTM_T4_ORIGINAL_1280_COLAB_PINNED_BOOTSTRAP_AND_OWNER_SCIENCE_LOCK_REVIEW` — phát hành notebook bootstrap chỉ kiểm tra, rồi quyết định cấp quyền 256 bước, không thay mô hình.
