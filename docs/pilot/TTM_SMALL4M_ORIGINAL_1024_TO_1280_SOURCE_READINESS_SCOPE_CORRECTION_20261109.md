# TTM-Small-4M T4 gốc — nguồn sẵn sàng cho thiết kế 1.024 → 1.280; kế thừa đúng giới hạn từ nhánh A

Ngày 2026-11-09 · PR #13 · Scope: **mô hình gốc T4, không tích hợp EmbeddingGemma 2** · **DESIGN / SOURCE-ONLY QA**.

## 1. Điều chỉnh phạm vi theo quyết định của chủ dự án

Giữ đúng công việc `TTM_SMALL4M_1024_TO_1280_EXPLORATORY_CONTINUATION_PREREG_SOURCE_READY_REVIEW`. Nhánh `TTM_SMALL4M_EMBEDDINGGEMMA2` là **nghiên cứu độc lập**. Chỉ kế thừa quan sát của nhánh **A (original tied TTM)**; không chuyển sang C, không đưa bảng embedding donor/ridge, untied head hoặc vector hoán vị vào chương trình T4.

Tại [lượt A/B/C/D 2.048 bước](https://github.com/minhtri22/TokenToModel-Lab/blob/02d5385732f13e0df265d87e09b8127add0292d3/docs/pilot/TTM_SMALL4M_GEMMA2_GPU2048_INDEPENDENT_SCIENCE_ADJUDICATION_20261109.md), A được khởi tạo từ **trọng số** checkpoint T4 step1024 rồi huấn luyện 1.024+1.024 bước thích nghi; VAL NLL của A ở mốc thích nghi 1.024: **3.3501216608**, ở 2.048: **3.3132380124** (giảm **0.0368836484**). Đây là **tín hiệu phụ** gợi ý optimizer có thể tiếp tục học. **Không** coi A là checkpoint kế nhiệm của T4 gốc, vì optimizer của A được khởi tạo mới, FP32, LR hằng `1e-4`, còn T4 gốc FP16 và AdamW với warmup/cosine. Số bước của A là *bước thích nghi bổ sung sau khi nạp trọng số T4*, không phải "T4 original step2048". Đối tượng so sánh bắt buộc vẫn là checkpoint T4 gốc step1024 → successor step1280.

## 2. Bằng chứng nguồn T4 gốc

- `t4_science_4m_1024_a2_20261108_v1`; checkpoint `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; progress `5517cc691fc803eaa69db4078f1f3b3ed78f99fa3c012cb17fd8655123c606ec`.
- Bằng chứng H1 VAL NLL **3.5223388517**, bigram **3.9972314170** (**PASS_H1_CONFIRMATORY_VAL_SCOPE**, không sửa); TEST 64 đã tiêu thụ, **không đọc lại**.
- Model P02 **3.749.376 params**, BPE 2.048, ctx256; TRAIN 2.048 stories, VAL 256; pack SHA `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; 4.096 target/bước; FP16 microbatch8 seed `20261108`.
- Nguồn trainer `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py` Git blob `76c4d0155cd0736919f41682f240b47ad3d7c428`, SHA256 `c6298f3381efd4b54e4b3e7aeb8143354f36bb1ed9fd87d08900cee18f7f90e6`. Lock khoa học đã tiêu thụ SHA `fd183ade2a696d40313aae19b63429d4ef3edd8abf25c899c8cc496836d36817`.
- Chỉ kiểm tra mã nguồn và biên bản hiện có. **Không khẳng định vừa băm lại checkpoint, pack trên Drive hoặc hồi phục runtime.**

## 3. Kết quả source audit 18 điều kiện

`PASS_STATIC_SOURCE_CONTRACT_18_OF_18`: xác nhận nguồn có snapshot full model+AdamW+LambdaLR+sampler+RNG Python/NumPy/torch CPU/CUDA+GradScaler; có hàm kiểm SHA READY-last và có hàm phục hồi toàn bộ state; kiến trúc 3.749.376 params; gradient clip 1.0; scheduler lambda `0.1` tại 1.024/1.025/1.152/1.280 tương ứng LR lý thuyết **3e-5** nếu giữ nguyên LR cơ sở `3e-4`.

**Hai cổng chặn không được lách:**
1. `t4_train_science_a2.py` chủ động từ chối `start>=TOTAL_STEPS` tại step1024, và khoa học gốc yêu cầu đúng 1024 steps; **không** sửa/yêu cầu chạy lại trainer gốc hoặc truyền lock khoa học cũ sang batch mới.
2. `checkpoint_load()` gốc yêu cầu `science_lock_sha256` cũ phải khớp payload. Runner kế nhiệm phải thực hiện **import có xác minh lock gốc** và tách một **new science lock + new RunID + new READY namespace**. Không tuyên bố scheduler/optimizer khôi phục đúng cho tới khi có kiểm thử thực tế (CPU fixture và Colab preclaim).

Source audit tĩnh không phải `SOURCE_READY_TO_EXECUTE`: runner kế nhiệm chưa có, nên status hiện là `DESIGN_CONTRACT_READY` / `RUNNER_NOT_IMPLEMENTED`.

## 4. Tiền đăng ký cho successor (chưa cấp phép thực thi)

- Tên duy nhất `ttm_small4m_step1024_to1280_exploratory_v1`, checkpoint cha duy nhất **T4 gốc step1024**; **256 bước mới** từ 1.025 đến 1.280, đúng **1.048.576** target exposures (4.096/bước).
- Khôi phục nguyên trạng **weights, AdamW, LambdaLR, sampler, CPU/CUDA RNG, Python/NumPy RNG, GradScaler**; không reset seed, optimizer, scheduler. Same tokenizer/train/val/context/architecture, microbatch8 FP16, clip1.0. LR tiếp nối ở floor `3e-5` sau khi kiểm scheduler/optimizer state tại import.
- 1.152 **diagnostic only**; 1.280 **primary VAL endpoint** (chọn trước). So `DeltaVAL=NLL(original1024)-NLL(successor1280)` trên cùng 256 truyện VAL, số nhãn/masks như gốc. Nếu cần baseline theo truyện, re-score checkpoint gốc **read-only** đúng một lượt; pair-bootstrap theo **truyện** 1.000 lượt seed20261109. Đánh giá chỉ thăm dò, không tái xác nhận H1; TEST 64 tuyệt đối không truy cập.
- `TRAINING_HELPFUL_SIGNAL` nếu DeltaVAL>0 và paired bootstrap95% lower>0, **không** có lỗi nguồn/QA. `TRAINING_NOT_CLEARED` nếu DeltaVAL≤0 hoặc CI không chứng minh dương. `HOLD` nếu thiếu độ toàn vẹn nguồn, runtime hoặc kết quả. Ngay cả VAL cải thiện cũng **không** khẳng định sinh truyện bám prompt tốt hơn.
- Một batch Colab Free T4 **chỉ sau owner approval, runner nguồn mới + negative/offline QA, exact SHA, new lock và preclaim**. Lưu checkpoint/READY mới, receipt, không sửa dữ liệu và RunID gốc. Không mở Q1/Q2 V3 vì V1/V2 đã tiêu thụ. Không đụng nhánh EmbeddingGemma2.
- Không tăng model size hoặc thay dataset trong thử nghiệm này; đó là giả thuyết độc lập khi chưa có đủ bằng chứng.

## 5. Quyết định

`ORIGINAL_T4=PRIMARY_SCOPE` · `CROSS_BRANCH_A=REFERENCE_ONLY` · `SOURCE_STATIC_QA=PASS_18/18` · `SUCCESSOR_IMPLEMENTATION=PENDING` · `SCIENCE_LOCK=NOT_ISSUED` · `GPU=NOT_USED` · `Q1Q2_V3=NOT_OPENED` · `PR13=HOLD` · `MAIN=UNCHANGED`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_1024_TO_1280_ORIGINAL_CONTINUATION_RUNNER_AND_INDEPENDENT_OFFLINE_QA` — triển khai runner successor nhỏ, kiểm thử chống reset optimizer/RNG, kiểm SHA checkpoint cha và ghim mã GitHub; không mở GPU trước khi có kết quả QA và quyết định khoa học.
