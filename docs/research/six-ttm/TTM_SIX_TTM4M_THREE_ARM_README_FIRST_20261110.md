# TTM × SIX — ba nhánh TTM-Small-4M, bộ runner chuẩn bị chạy

**Trạng thái:** `SOURCE_IMPLEMENTED` / `CPU_QA_PASS` / `PARENT_CKPT_SHA_PENDING` / `OWNER_PILOT_EXECUTION_PERMIT=NOT_ISSUED` / `GPU_NOT_RUN`.

## Thành phần

- `ttm_six_ttm4m_three_arm_v1.py`: một runner cho cả A (CE), B (CE + direct response MSE), C (CE + template-residual response MSE).
- `test_ttm_six_ttm4m_three_arm_v1.py`: 20 bài QA độc lập trên CPU; mô hình giả rất nhỏ, không dùng dữ liệu G1 TEST.
- `TTM_SIX_TTM4M_THREE_ARM_T4_PRECLAIM_V1_20261110.ipynb`: notebook Colab chứa nguyên vẹn mã runner **đã nén**, giải nén và kiểm SHA256 trước khi dùng, các ô preflight và training gate.
- `WRITE_OWNER_PILOT_APPROVAL_LATER.json`: **chỉ là bản nháp không có hiệu lực** (`owner_approved=false`).
- `TTM_SIX_TTM4M_THREE_ARM_INTEGRATED_OFFLINE_QA_20261110.json`: QA source + notebook + frozen Qwen.

## Nguồn đã kiểm soát

- Parent original TTM step1280 `checkpoint.pt` SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; READY SHA256 `eb89d0a797451187ed20956d1f0097e9a8b9539da8eeaa92960e2a8508c9095f`. **Chưa băm lại byte từ Drive trong lượt này.**
- Frozen TTM TRAIN-only BPE manifest SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; có thể nằm ở `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json` trên máy Windows. Phải đọc & kiểm SHA, không tái huấn luyện tokenizer.
- Authored fictional Qwen ZIP SHA256 `6f98560117219cf3cecc37fb87ff562a784fe82238d9b2d831cbda7634488d9f`, nguồn mã Qwen SHA256 `9688deb1d1157c93fb7090e5b1c12ea4bc56ed0dedadb0597d84ceb4e68e82eb`.
- P02 Python Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; BPE Python Git blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`; notebook tải từ immutable Git commit `f69d4eb0b566344b19e9795de59ee6eec87ef47f` rồi kiểm blob.

## Thao tác người dùng sau khi nhận riêng pilot approval

1. Chỉ mở notebook trên **Colab Free** và chọn **T4 GPU** nếu được cấp. Không chạy lại Qwen model.
2. Chạy cell 1–4 để xác minh SHA và preflight **chỉ đọc**: mount Drive để đọc đúng checkpoint gốc; upload **hai tệp** `TTM_SIX_G1_EXPLORE_REAL_QWEN_DEV_RESULTS.zip` và `T1_BPE2048_REAL_TRAIN_MANIFEST.json`. Không đọc G1 TEST hoặc TTM VAL/TEST.
3. Nếu preflight PASS, **dừng lại** và trình receipt để chủ sở hữu cấp quyền chạy **pilot mới** riêng. Không sử dụng approval G1 cũ.
4. Chỉ sau approval mới, đặt JSON đã phê duyệt ở `/content/TTM_SIX_TTM4M_NEW_OWNER_PILOT_APPROVAL.json`, bật `AUTHORIZED_NEW_PILOT=True` và chạy cell cuối. Notebook sẽ kiểm file approval, checkpoint/tokenizer lại trước khi train; giới hạn 72 optimizer updates ×3, tổng 1200s best effort, VRAM reserved <12GiB.
5. Lưu output 3 arm weights và `READY.json` chỉ ở `MyDrive/TTM/ttm-six-functional-pilot-v1/ttm_six_ttm4m_functional_transfer_public48_dev16_v1/`. Không ghi đè nếu output đã tồn tại. Chia A/B/C tạo nhánh trọng số riêng, không phải bước 1281 của original TTM.

## Ý nghĩa thống kê

DEV 16 mẫu / 4 nhóm đã từng được quan sát trong Qwen pilot: **không phải held-out confirmatory**. Quy tắc `EXPLORATORY_FUNCTIONAL_GAIN_CANDIDATE` là sàng lọc trước, không phải p-value hoặc G1 PASS. Một đối chứng template-only dự báo teacher responses DEV MAE=0.052022961, phải vượt qua để có tín hiệu C; nếu không, `EXPLORATORY_NO_CLEAR_GAIN`. Nếu thiếu bất kỳ nguồn nào, `TECHNICAL_STOP`.

**Không thực hiện:** chạy GPU, đọc TEST, sửa `main`, `lineage.md`, checkpoint TTM gốc, huấn luyện Qwen, cung cấp science permit gốc.
