# TTM-Small-4M — T4 Tích hợp: khóa thiết kế, đo năng lực, mã huấn luyện

**Ngày:** 2026-11-08  
**Repo:** `minhtri22/TokenToModel-Lab`, PR #12 *draft*  
**Trạng thái:** `T1–T3=PASS_TECHNICAL` · `T4_CODE_STATIC_AND_SYNTHETIC_CPU_QA=PASS` · `T4_GPU_CAPACITY=NOT_EXECUTED` · `T4_SCIENCE_LOCK=HOLD` · `T4_SCIENCE=NOT_EXECUTED`.

## Một lượt tổng hợp, không lặp T1–T3

1. Quyết định phạm vi **pilot có giới hạn**: 2048 truyện TRAIN, 256 VAL, 64 TEST niêm phong; BPE2048 học từ 768 TRAIN. Bộ tách đã được kiểm định độc lập trong phạm vi tập này, nhưng không có kết luận loại trùng gần trên *toàn bộ* truyện TRAIN bị loại. Nguồn và license CDLA-Sharing-1.0 có nghĩa vụ; không công khai dữ liệu truyện hay tập tokenized.
2. H1 chính: cùng tokenizer, mô hình có **VAL NLL thấp hơn ≥5%** so với bigram Add-0.1 từ TRAIN; bootstrap theo truyện 1000 lượt seed 20261109, cận dưới 95% của độ chênh NLL tuyệt đối phải >0. Uniform, unigram là đối chứng phụ. **Checkpoint cuối bước 1024** là kết quả chính; chỉ sử dụng TEST một lượt sau khi khóa kết quả VAL.
3. 1024 bước tối đa, **đúng 4096 nhãn mục tiêu (không tính PAD) / bước**, tổng 4.194.304 lần nhãn; AdamW 0.9/0.95, weight decay 0.1, LR 3e-4, warmup32, cosine to3e-5; VAL mỗi128 bước, checkpoints READY-last tại 256/512/768/1024; GPU thời gian khoa học tối đa90phút. Chọn microbatch/FP16-FP32/accum **sau** phép đo tổng hợp, trước TRAIN, không chọn từ VAL/TEST.
4. T2 GGUF F32 vẫn PASS (chỉ mô hình chưa train), T3 Colab Tesla T4 và Drive resume PASS; F16 GGUF vẫn BLOCKED và tùy chọn. Kết quả mô hình sau train/GGUF/Ollama phải đo ở T5.

## Nội dung bundle

- `T4_PREREG_INTEGRATED_CANDIDATE_20261108.json` — khóa nghiên cứu đề xuất, còn năng lực/phê duyệt.
- `p02_source_exact.py` — mã P02 nguyên bản, Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`.
- `t4_capacity_smoke.py` — đo 4096 token mục tiêu tổng hợp trên Tesla T4, các ứng viên fp32/mb2, fp16/mb2, mb4, mb8. Mỗi cấu hình 2 warmup + 4 timed steps; tính thời gian worst và 25% dự phòng, VRAM <=80%.
- `TTM_T4_Synthetic_Capacity_20261108_v1.ipynb` — **notebook nên chạy tiếp theo**. Chỉ dữ liệu tổng hợp, một RUN_ID, lưu báo cáo/env/pip freeze/READY lên Google Drive; không có TinyStories trong notebook.
- `t4_data_pack.py` + nguồn T1/BPE pinned — **chỉ khi cần đóng gói dữ liệu riêng tư** từ 2 tệp raw Windows đã PASS, tạo `TRAIN/VAL` token windows dưới `_tmp`, tuyệt đối không đưa TEST vào npz/public GitHub.
- `Run-TTM-T4-Data-Pack-PS51.ps1` — Preview và Execute riêng, ghim repo/origin/main và SHA; một lượt không ghi đè.
- `t4_capacity_accept.py` — xét riêng năng lực theo thống kê *số target hợp lệ/cửa sổ* của dữ liệu TRAIN thực; còn hệ số bảo thủ 10% ngoài dự phòng 25%. Chỉ đề xuất ứng viên, không cấp science.
- `t4_eval.py` — TRAIN-only uniform/unigram/Add-α bigram và NLL theo truyện VAL/bootstrapping.
- `t4_train_science.py` + `TTM_T4_Science_FailClosed_20261108_v1.ipynb` — **chưa được chạy**. Khóa science thiếu thì dừng trước mọi TRAIN. Sau science lock sẽ nạp NPZ vào SSD Colab, dùng sampler Train-only, đúng 4096 nhãn/bước, state model/optimizer/scheduler/sampler/Python/NumPy/CPU/CUDA RNG và GradScaler, READY-last Drive.
- `tests/test_t4_integrated.py` — bộ kiểm thử CPU không khoa học.

## Chạy ngay: đo năng lực T4 *synthetic*

Mở notebook `TTM_T4_Synthetic_Capacity_20261108_v1.ipynb` trên Colab. Chọn T4 nếu được cấp, chạy tuần tự các ô. Cấp quyền gắn Drive ở ô 2. Không bấm Run All lại khi thư mục output đã được tạo. **Ô cuối đồng bộ Drive phải chạy kể cả khi phép đo bị chặn.**

Đích duy nhất: `MyDrive/TTM/ttm-small-pilot/t4_capacity_synthetic_20261108_v1/`.

Điều kiện máy: PyTorch hỗ trợ CUDA và free VRAM đủ; mức GPU có thể thay đổi, không được giả sử đã có T4. Đo phân biệt các ứng viên, không chọn hyperparameter theo chất lượng mô hình. `CAPACITY_PASS_PROVISIONAL` chỉ là **bằng chứng hạ tầng**, chưa là quyền huấn luyện.

## Tiếp theo, sau Capacity report readback (không làm ngay bây giờ)

**Windows** (không cài lại PyTorch, không tải lại TinyStories): giải nén bundle vào `Downloads\TTM_T4_INTEGRATED_V1`, so SHA256 ZIP và PowerShell; chạy:

```powershell
$script="$env:USERPROFILE\Downloads\TTM_T4_INTEGRATED_V1\Run-TTM-T4-Data-Pack-PS51.ps1"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -Mode Preview
if ($LASTEXITCODE -ne 0) { throw 'T4_PACK_PREVIEW_BLOCKED' }
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -Mode Execute
if ($LASTEXITCODE -ne 0) { throw 'T4_PACK_EXECUTE_STOP_KEEP_EVIDENCE' }
```

Chỉ xuất `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t4_data_pack_v1\T4_PRIVATE_TRAIN_VAL_WINDOWS.npz` và manifest. Không commit file này: nó mang token có thể giải ngược ra truyện gốc. Chuyển bản riêng tư vào `MyDrive/TTM/ttm-small-pilot/t4_private_pack_20261108_v1/`, kiểm SHA trong Drive; **không tạo tập TEST token**.

Sau đó chạy `t4_capacity_accept.py` trên CPU với hai manifest, lưu đánh giá `T4_CAPACITY_PRIVATE_PACK_REVIEW.json` (không ghi đè), đối chiếu độc lập. Nếu 1024 bước 4096 token không thể đạt ngân sách90phút, ghi HOLD và sửa tiền đăng ký *trước khoa học*, không tự giảm số bước hoặc tăng quỹ GPU.

## Kết luận hiện có, cổng khoa học

Dù bộ mã Python đã đạt **13/13 unit tests CPU** và notebook AST PASS, Tesla T4 **chưa đo** khối lượng T4 thật, dữ liệu token TRAIN/VAL riêng tư **chưa đóng gói**, evaluator và trainer **chưa qua kiểm thử tích hợp full GPU/Drive bằng dữ liệu không khoa học**. Science lock phải tiếp tục `HOLD`; không tự cấp `T4_SCIENCE_LOCK.json`, không chạy notebook science. Sau khi khóa khoa học và năng lực PASS, có thể thẩm định *một* lượt T4, không cần tạo permit cho các phép kiểm nhỏ.

Lịch sử lỗi T3 cũ được bảo toàn; `lineage.md` append-only chỉ ghi thực nghiệm khoa học, không ghi QA kỹ thuật. Không sửa P00–P12, không mở P07.

**Bước thực hiện tiếp theo:** `TTM_T4_SYNTHETIC_4096_TARGET_GPU_CAPACITY_AND_DRIVE_READBACK` — chạy notebook capacity, gửi báo cáo từ Google Drive, tôi sẽ thẩm định ứng viên và cửa thời gian, không chạy science.
