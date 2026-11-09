# TTM-Small-4M × EmbeddingGemma 2 — Causal6 nguồn tích hợp v1

**Trạng thái:** Mã được dựng và kiểm tra tổng hợp trên CPU; **chưa chạy đối chiếu thật với checkpoint C2048, chưa niêm phong H512, chưa xác minh Tesla T4 của Colab, chưa tạo CLAIM khoa học**.

## Phạm vi đã khóa

- Sáu nhánh `RR-F`, `RP-F`, `RR-A`, `RP-A`, `OR-F`, `OP-F` trên TTM 256 chiều; 2.048 optimizer steps × 4.096 nhãn mỗi nhánh, tổng 50.331.648 nhãn huấn luyện.
- Một phép chiếu Ridge (ridge projection) chung cho cặp RR/RP, một phép chiếu Procrustes trực giao (orthogonal Procrustes) chung cho OR/OP; với đối chứng hoán vị (permutation), hoán vị vector **sau** khi fit projection, không refit theo hoán vị.
- Đối chứng chính (primary contrast): NLL(RP-F) − NLL(RR-F), khoảng tin cậy 95% bootstrap ghép theo truyện (paired-story bootstrap) 2.000 lần; hai phép tương tác còn lại chỉ mang tính thăm dò.
- Tập H512 chọn theo SHA-256 trên TinyStories-valid đã ghim, loại trừ TRAIN/VAL/TEST lịch sử và 320 truyện L0017 bằng SHA chính xác, rà trùng gần 5-word Jaccard ≥0,85 trong H512 và với TRAIN2048/VAL256. Không mở lại nội dung TEST cũ hoặc 320 truyện để chấm.
- Mọi code, checkpoint, donor và lịch lấy mẫu phải khớp checksum trước CLAIM; CPU kiểm tra parity model C2048 nguyên bản trên cùng chuỗi token tổng hợp, không dùng real holdout.
- Chỉ chạy huấn luyện trên **Google Colab Free Tesla T4**, FP32. Không có quyền điều khiển hoặc xác minh runtime Free T4 từ phiên chat hiện tại. GPU/Drive là cổng còn chưa xác minh.

## Tệp bàn giao

- `ttm_causal6_h512_seal.py`: niêm phong 512 truyện trên **máy Windows**; ghi private H512 ID/token-window pack chỉ trong thư mục `_tmp` của dự án; không chấm mô hình.
- `ttm_causal6_colab_free_t4_one_shot.py`: kiểm tra nguồn và C2048 parity trên CPU (`cpu-source-qa`); kiểm tra Colab T4 trước CLAIM (`preflight`); chạy một lần (`execute`) hoặc khôi phục có kiểm tra READY (`resume`) ở cùng RunID.
- `ttm_causal6_independent_readback.py`: chỉ tái tính thống kê từ dữ liệu tổng loss theo truyện, kiểm checkpoint hashes và các mốc READY; không chạy model forward.
- `RUN_WINDOWS_H512_SEAL_AND_STAGE.ps1` (**tải riêng, không nằm trong ZIP nguồn**): xác minh các input cũ trên máy, chạy niêm phong H512, kiểm source parity rồi tạo private ZIP chỉ dành cho Drive của chủ dự án.
- `TTM_CAUSAL6_FREE_T4_ONE_SHOT_COLAB_20261109.ipynb`: notebook Colab; người dùng phải điền ZIP SHA256 từ Windows và xác nhận dung lượng Drive, trước khi chạy preflight và execute. Notebook không khởi động science khi chưa có đầu vào.

**Trình tự một gói:** tải source ZIP + stage PS → stage/niêm phong H512 trên Windows (không GPU) → tải ZIP riêng tư lên `MyDrive/TTM/ttm-small-pilot/` → mở notebook Free T4 → source/env/T4 preflight → CLAIM duy nhất → sáu nhánh với READY mỗi 256 bước → đánh giá H512 đúng một lần → independent readback → phân xử khoa học. Không tự chạy lại sau CLAIM nếu interrupted.

**Giới hạn:** H512 chưa loại được mọi near-duplicate với TEST64/holdout320 lịch sử vì chỉ dùng SHA exclusion; donor pretraining overlap chưa biết; một seed huấn luyện không chứng minh ngữ nghĩa donor là nguyên nhân duy nhất. Không GGUF, không Ollama, không sửa lineage khi mới chuẩn bị kỹ thuật.
