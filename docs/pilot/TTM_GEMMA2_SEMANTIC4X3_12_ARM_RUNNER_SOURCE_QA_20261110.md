# TTM-Small-4M × EmbeddingGemma 2 — SEMANTIC4X3: triển khai runner và kiểm thử nguồn tích hợp

**Ngày:** 10/11/2026. **Operation:** `TTM_GEMMA2_SEMANTIC4X3_12_ARM_INTEGRATED_RUNNER_SOURCE_QA_AND_COLAB_FREE_T4_PREFLIGHT`.

**Quyết định hiện tại:** `SOURCE_IMPLEMENTED` · `CPU_QA_PASS_SCOPED` · `GPU_PREFLIGHT_NOT_EXECUTED` · `SCIENCE_NOT_AUTHORIZED`. Đây là bước triển khai mã nguồn theo hợp đồng tiền đăng ký V2, **không phải lượt huấn luyện**, không có kết quả science để ghi `lineage.md`.

## 1. Ràng buộc gốc, không thay đổi

- Nguồn TTM bước 1.024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; donor candidate SHA256 `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`; H768 mới `H768_SEALED_NOT_SCORED`, **768 truyện / 1.000 cửa sổ / 186.655 nhãn**, public seal SHA256 `9725b1254cde81b77e23b85ab479a08cafc14af0a7a536c7722ca87c7f2a5aa0`.
- Dùng đúng phép null giữ hình học projector (dual-matched null), source QA SHA256 `0d71f38da356056be50a18d36f589774190178fd321e6d2e3970413d96238a2d`. Không thay đổi Ridge ban đầu fit trên 1.917 token thật. Bốn nhánh PT-REAL, PT-PERM, NULL-REAL, NULL-PERM, **ba seed cố định S1/S2/S3** như contract V2, không đổi hyperparameter/seed sau khi quan sát kết quả.
- Mỗi nhánh 2.048 optimizer updates × 4.096 nhãn, tổng 100.663.296 lượt nhãn. 4 nhánh một seed dùng **cùng packet schedule**; 3 seed có lịch khác được SHA riêng. FP32, AdamW lr 1e-4, betas (0.9,0.95), eps 1e-8, wd 0.1, clip 1.0, micro-window ≤8, tokenizer/hardware P02 gốc, 131 fallback row bảo toàn E0.
- Ba RunID con S1/S2/S3 nằm trong cùng study root. Tạo một `STUDY_CLAIM.json` bất biến trước training, mỗi seed có `CLAIM.json` và `SCHEDULE_PRIVATE.json`. Mỗi arm có đủ tám READY model+optimizer+sampler/RNG tại 256/512/.../2048, khoá SHA và dấu START/DONE chống chạy lại chunk chưa phân xử.
- Chỉ khi có **12 final READY** và không tồn tại `SCORING_START.json` mới được mở chấm H768 một lần; trong **preflight**, chỉ hash và đọc metadata H768, **không giải mã H768_WINDOWS_PRIVATE.npz và không dùng nhãn holdout trong model.forward**. Đầu ra khoa học lưu per-story losses private, RESULT công khai chỉ có NLL và bootstrap.

## 2. Mã triển khai, kiểu thao tác

- `ttm_semantic4x3_runner.py`: `--mode fixture` (CPU tổng hợp); `--mode cpu-source-qa` (CPU nguồn thật và H768 metadata private); `--mode preflight` (Colab Free Tesla T4 + nguồn + quota + smoke tổng hợp, **chưa CLAIM**); `--mode execute` (**bị chặn nếu không có `--owner-science-approved`**); `--mode resume` (**chặn nếu không có manual adjudication**).
- `ttm_semantic4x3_independent_readback.py`: `--mode fixture` (CPU tổng hợp); `--mode readback` kiểm CLAIM/result/per-story, 96 metadata READY, SHA binary của **12 final checkpoint** và tính lại độc lập bootstrap chung 768 truyện × ba seed. Không import model hoặc chạy inference.
- `test_semantic4x3_offline_qa.py`: 11 unit tests, gồm consistency thống kê/negative QA, 3 seed schedules, không CLAIM khi chưa phê duyệt, không ghi đè CLAIM, không mở H768 khi thiếu READY, không replay chunk dang dở, không bỏ qua sửa đổi CI, phân tách H768 metadata và dữ liệu chấm.
- `ttm_semantic4x3_balanced_null_cpu_qa.py`: **tái sử dụng đúng mã frozen** đã có trong repo; không tự tái viết một thuật toán null khác.

## 3. QA đã chạy thật — phạm vi rõ ràng

**CPU Python 3.13, torch CPU**: chạy `runner --mode fixture` PASS, reviewer `--mode fixture` PASS, `pytest -q` **11/11 PASS**; không có claim và không gọi CUDA.

Đối chiếu tệp dữ liệu **gốc thật** trong container (tệp checkpoint và donor lấy từ Drive connector, CAUSAL6 input ZIP private hiện có): đủ **7/7 SHA nguồn**, tải model đúng shape, parity **C2048 exact state và synthetic logits**, T4 TRAIN/VAL packet counts/values PASS, dựng thành công **12 lần khởi tạo model** cùng mask trainable 3.880.448 parameters/arm, null real tensor S1/S2/S3 và 2.048 TRAIN packets/seed cùng 4.096 nhãn từng packet. Khoảng cách lớn nhất giữa `X_real @ P.T` và `X_null @ P.T` ở FP32 (theo seed): S1 **1,0431e-7**; S2 **1,1176e-7**; S3 **1,1921e-7**. Relative covariance error ~2,05e-15. Các test không dùng H768, không dùng TEST/H320/H512, không train model, không gọi scientific forward trên dữ liệu thật (chỉ parity synthetic ngắn).

**Chưa thực hiện:** real H768 private NPZ được xác minh riêng bằng runner trong runtime Colab (mã nguồn hash đã khóa qua owner local H768 seal); actual T4 CUDA/peak memory; quota Drive live; toàn bộ 24.576 training update; READY thật; independent readback thật. Không ghi `PASS` các cổng chưa làm. Không có kết quả khoa học mới. Chưa bảo đảm Colab Free đủ thời lượng thực tế để hoàn thành 12 arms; nếu rớt giữa chunk, fail-closed, không tự replay.

## 4. Cổng tài nguyên trong cùng phiên Colab, không yêu cầu micro-permit

**Quota**: callback `drive.about(storageQuota)` trong preflight (cần phiên Colab đã xác thực), yêu cầu dung lượng trống hiện tại ≥ max(6 GiB, 96 × 52.947.341 byte + 1 GiB). Dung lượng owner ước khoảng 10 GB là xác nhận ban đầu, **không phải phép đo API**. Khi resume có phân xử, kiểm dung lượng cho số READY còn thiếu, không so quota động vào `env` checkpoint bất biến.

**GPU**: đúng Tesla T4 đơn, VRAM báo >=14 GiB, PyTorch CUDA healthy, reproducibility FP32 + `CUBLAS_WORKSPACE_CONFIG=:4096:8`, synthetic 8×256 cross entropy + backward, `max_memory_allocated` < 12 GiB. Kiểm tra chỉ được chạy trong phiên Colab của người dùng; CPU QA ở đây **không được gọi PASS_GPU**.

**Quản trị:** trước khi runner `--mode execute` được dùng phải có quyết định chủ dự án cho science. Notebook chuẩn bị chỉ có nạp nguồn, QA fixture và preflight; **không có cell execute**. Sau `STUDY_CLAIM` không `Run all`, không chạy lại `execute`, không tạo RunID mới; resume bắt buộc phân xử manual theo nhật ký exact READY trước.

## 5. Tệp nguồn, private package và bước kế tiếp

Tái sử dụng ZIP `TTM_GEMMA2_CAUSAL6_INPUT_PRIVATE_V1_20261109.zip` trên Drive, SHA256 `2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a` chỉ để đọc 7 nguồn đã pin, **bỏ qua toàn bộ H512 cũ**. Script PowerShell `PACK_TTM_SEMANTIC4X3_H768_PRIVATE_V1.ps1` đóng gói 3 file H768 đã niêm phong, không tạo lại H768. Chỉ đưa ZIP H768 riêng tư lên Drive; không commit ZIP, story IDs, token windows hay optimizer weights lên GitHub.

**Next operation:** `TTM_SEMANTIC4X3_COLAB_FREE_T4_PRECLAIM_REAL_SOURCE_QA_OWNER_DECISION`, xử lý một lượt nhập ZIP H768 vào Drive và chạy notebook preflight theo source SHA được ghim. Nếu PASS và owner quyết định riêng thì mới xem xét khoa học one-shot. Giữ `L0019` và `main` nguyên trạng, không GGUF/application.
