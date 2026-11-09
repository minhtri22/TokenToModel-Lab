# TTM-Small-4M × EmbeddingGemma 2 — QA tương đương số học mô hình nguyên bản trên CPU

**Ngày:** 09/11/2026. **Công việc:** `TTM_SMALL4M_EMBEDDINGGEMMA2_ORIGINAL_RUNNER_CPU_SYNTHETIC_NUMERIC_PARITY_QA`.

## Kết luận

**`PASS_ORIGINAL_RUNNER_CPU_SYNTHETIC_LOGIT_PARITY`**: bốn checkpoint A/B/C/D bước 2.048 được nạp nghiêm ngặt vào **mô hình được dựng bằng mã nguồn gốc** và vào **mô hình CPU độc lập**; trên 5 chuỗi token giả lập cho mỗi arm, cả **20/20 cặp logits PASS**, độ lệch tuyệt đối lớn nhất bằng **0,0**.

Đây là **QA kỹ thuật** về tái tạo logits trên CPU, không chứng minh parity bitwise với các nhân CUDA/T4, không đo NLL, không thử nghiệm khoa học mới, không tác động `lineage.md`.

## Chuỗi nguồn được xác minh

1. Đọc ZIP nguồn gốc đã lưu trong Drive `TTM_GEMMA2_DIRECTSWAP_GPU1024_SOURCE_20261109.zip`, file ID `1WYhjTWLio4pv4RdqPSQABn21A4kD75yF`, SHA-256 `e544c645635a28fe140802421d03a7928a7f0446d2df33bbfe4ec129e3a6ea27`, 16.932 byte.
2. Ba thành phần bên trong xác thực: `p02_exact.py` SHA-256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`; `ttm_embeddinggemma2_swap.py` SHA `d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39`; nguồn GPU1024 `ttm_directswap1024_gpu_once.py` SHA `00416c0ff5b2afdcca2780a20315dd2da0af93554cd2b32b6c94efb630dc5d3b`.
3. Áp dụng **đúng các sửa đổi của bộ dựng đã version hóa** `tools/embeddinggemma2_swap/ttm_build_directswap2048_from_locked1024.py`. Mã gốc GPU2048 tái tạo ra SHA-256 `0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e`. Không sửa logic `build_model`, `P02` hay `MappedGemmaInput`.
4. Import module GPU2048 trên **CPU** và chỉ gọi `core.build_model()`; tuyệt đối không gọi `preclaim()`, `execute()`, `train_one_step()`, `val_story_sums()` hoặc đọc các dữ liệu TRAIN/VAL/TEST. Mô hình độc lập là `IndependentP02` có source SHA-256 `016c2fdc8df2cab642b52f1c7111a5a6694944c8fd06e2cfd4d373d42a2dc438` từ công việc trước.

**Chi tiết quan trọng:** hàm dựng model gốc cần `ckpt` và `donor` đầu vào để dựng module, nhưng thí nghiệm chỉ kiểm tra *forward từ checkpoint 2048 đã hoàn tất*. Bộ QA dùng trọng số A/C 2048 làm dữ liệu khởi tạo surrogate cho `build_model`, sau đó **nạp strict 100% state_dict và buffer thực tế của từng arm**, bảo đảm những khởi tạo surrogate bị ghi đè hoàn toàn trước mỗi phép forward. Không dùng checkpoint T4 hoặc donor gốc để khởi tạo nghiên cứu mới, không tính ridge rồi lưu thành candidate. Đây là phép chấm lại **forward topology từ mã gốc trên trọng số đã khóa**, không phải tái diễn quá trình tạo checkpoint ban đầu.

## Kiểm định và ngưỡng

- Môi trường: Python 3.13.5, PyTorch 2.10.0+cpu, 2 CPU threads, CUDA disabled.
- Bộ token kiểm thử cố định trước chấm: chuỗi 8 token có EOS và biên vocab; 2 chuỗi song song 8 token; batch 2 × 32 token ngẫu nhiên xác định; 1 × 64; 1 × 256 token ở giới hạn context.
- Điều kiện: `|L_original − L_independent| ≤ 1e−5 + 1e−5 × |L_independent|` cho **toàn bộ tọa độ logits**, sau khi xác minh shape và tính hữu hạn. Ở đây ký hiệu `L` là **logits**, không phải loss.
- A/B/C/D đều `state_dict(strict=True)=PASS`; cả 5 trường hợp mỗi arm đều PASS; **max |Δlogit|=0,0**; max tỷ lệ sai số trên dung sai = 0,0.
- Đối chứng âm: sửa có chủ đích một logit `+10^−3` bị từ chối, shape sai bị từ chối, NaN bị từ chối; đối chứng dương tensor bằng nhau được chấp nhận. **4/4 PASS**.
- Tập 320 truyện vừa niêm phong: **không truy cập**. Không đọc văn bản TEST lịch sử, không chạy GPU, không có training step hoặc NLL khoa học.
- Không có dữ liệu riêng tư, ID truyện, tensor logits, trọng số hay checkpoint trong commit.

## Tài liệu tái tạo và bằng chứng

- Bộ runner QA: `ttm_gemma2_original_runner_cpu_numeric_parity_qa.py`, SHA-256 `9d22bef56e0f15d9f3c256c4b10225b15744f3fd79de415311bf5fecf80f3487` (đã chạy; cung cấp dưới dạng tệp tải trực tiếp trong cuộc hội thoại này, không ghi vào repo ở commit hiện tại).
- Biên bản đầy đủ JSON 20 ca: `TTM_GEMMA2_ORIGINAL_RUNNER_CPU_SYNTHETIC_NUMERIC_PARITY_QA_20261109.json`, SHA-256 `7aed7de19d8ba9d9a8190fa89bd3f7d301cf64b1e57e910411f1a68d9c249cbd` (tệp tải trong cuộc hội thoại).
- Bảng tóm tắt dạng máy đọc không nhạy cảm được lưu ở `artifacts/qa/ttm-embeddinggemma2/TTM_ORIGINAL_RUNNER_CPU_SYNTHETIC_NUMERIC_PARITY_QA_20261109.json`, gồm từng ca, SHA nguồn và checkpoint.

## Phán quyết đi tiếp

**`ORIGINAL_CPU_NUMERIC_PARITY_GATE=PASS`** cho bốn checkpoint đã đóng băng. Không dùng kết quả kỹ thuật này để tuyên bố mô hình C hiệu quả hoặc việc donor chuyển giao có lợi; giả thuyết khoa học chỉ được kiểm định qua one-shot new-holdout trong một bước riêng.

**Bước kế tiếp:** `TTM_SMALL4M_EMBEDDINGGEMMA2_CONFIRMATORY_EVALUATION_PREEXECUTION_INTEGRATED_QA_AND_ONE_SHOT_GATE`: đóng gói/kiểm tra chính xác quy tắc cửa sổ token, mask `-100`, tổng hợp theo 320 truyện, cổng nguồn/quyền và định nghĩa phép thử A−C/B−C/D−C đã tiền đăng ký. Có thể quyết định cấp phép khoa học one-shot trong gói này, nhưng **chưa được chấm tập mới** khi chưa có quyết định rõ ràng. Không cập nhật `lineage.md` trước khi có kết quả khoa học thẩm định.
