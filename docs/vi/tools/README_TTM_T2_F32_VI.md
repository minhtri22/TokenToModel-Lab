# TTM-Small-4M — T2 F32: bước tiền phân đoạn GPT-2 (Pretokenizer) và BPE 2.048 mã (2026-11-08)

> **Bản tiếng Việt chuẩn hóa của hướng dẫn T2 tại thời điểm tạo gói.** Mọi SHA, đường dẫn và trạng thái từ trước khi chạy native được giữ nguyên. Không chạy lại bài thử đã tiêu thụ. Xem [hồ sơ gốc](../../../tools/pilot_t1t3/source_t2/README_TTM_T2_F32_VI.md) và [kết luận kỹ thuật T1–T3](../pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md).

**Mục tiêu:** kiểm tra tuyến tích hợp **bộ tách token (Tokenizer) 2.048 mã học chỉ từ TRAIN tổng hợp (Synthetic TRAIN-only) → GGUF F32 → chạy `llama.cpp` trên CPU → so mã token (Token IDs) và điểm dự đoán trước chuẩn hóa (Logits)**. Đây là QA kỹ thuật, không phải khoa học; không dùng TinyStories, TEST, Colab hoặc GPU.

## Tình trạng

- mã đối tượng Git P02 chính xác (Exact Git Blob) `9762343e06cf800b50574c2871ae1ed58537fb18`.
- Bộ thực thi (Backend) `ggml-org/llama.cpp@372dc5ca157276beb6c67b2e92477e8d662e964a` đã biên dịch ở lượt V5B; sử dụng lại **chính** `ttm_t2_v5_probe.exe`, không biên dịch lại.
- Trước V6 T2: phép đo số học (Numeric) F32 8/8 PASS, BPE toàn chuỗi (Whole-string) FAIL 2/9 (dấu cách và xuống dòng (Whitespace/Newline)), F16 hỗn hợp (Mixed F16) dừng STOP; tất cả bằng chứng (Evidence) cũ giữ nguyên.
- BPE mới: 256 mã byte cơ sở (Base-byte IDs) `0..255`, EOS `256`, 1.791 phép hợp nhất (Merges) học theo tần suất **trong từng đoạn tiền tách GPT-2** với quy tắc phá hòa (Tie-break) ổn định, IDs `257..2047`, mã hóa/giải mã UTF-8 nghiêm ngặt.
- điều kiện chỉ đọc TRAIN (TRAIN-only Guard): chỉ `Story(split='TRAIN')`, nguồn `SYNTHETIC_TRAIN_FIXTURE` trong lượt kỹ thuật; các tập con (Split) VAL/TEST bị từ chối. Với dữ liệu thật, phải khóa bản quyền/SHA byte nguồn (Source Bytes), ranh giới truyện (Story Boundary)/chống trùng (Deduplication) và bản kê (Manifest) trước khi học (Fit). Kết quả tổng hợp **không được dùng làm tokenizer khoa học**.
- Các fixtures độc lập mới đã niêm phong trước phép chạy native; SHA256 `5a4ba58db3ad7c1ad0a7c6a790c08184d43c1e3a081ad2dcaf2d4c3b9dbeb9f2`, 20 ca văn bản và 10 ca mã token (Token IDs), không trùng toàn bộ ca V5B.

## QA chỉ với CPU trong môi trường tạo gói

**11/11 phép kiểm Python (pytest) đạt:** `11/11 pytest PASS` dùng Python `3.13`, torch `2.10.0+cpu`, `regex 2026.5.9`, NumPy `2.3.4` trên môi trường riêng, bao gồm exact P02 F32 GGUF 52 tensor, sai lệch đọc lại trọng số (Weight Readback Error) bằng 0, từ chối bản kê đã bị chỉnh sửa (Manifest Tamper Rejection) và các cổng TRAIN-only. Chưa chạy được chương trình nhị phân gốc Windows (Native Binary) tại môi trường tạo gói; không tự nhận `T2_FULL_PASS`.

## Đường dẫn sử dụng trên máy Windows

Giải nén gói ZIP vào **`C:\Users\minht\Downloads\TTM_T2_F32_TRAINONLY`** (các tệp ở ngay thư mục gốc (Root) của thư mục này). Bộ chạy dùng:

- TTM cục bộ (Local) `D:\WORK\RESEARCH\TokenToModel-Lab`, nhánh `main` nguyên trạng ở `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.
- Môi trường Python CPU đã tạo từ V3: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\py313_cpu_venv\Scripts\python.exe`.
- Mã cũ đã ghim `C:\Users\minht\Downloads\TTM_T2_V3\t2_gguf_cpu.py`.
- Bộ thăm dò C++ (Probe) biên dịch V5B: `_tmp\ttm_t2\v5b_technical\build\Release\ttm_t2_v5_probe.exe`.
- Các thư viện động (DLL) cũ nguyên trạng: `_tmp\ttm_t2\build\bin\Release`.
- Đầu ra (Output) **mới duy nhất**: `_tmp\ttm_t2\f32_pretok_trainonly_v1\`. Nếu thư mục đã tồn tại, cả kiểm tra trước (Preview)/thực thi (Execute) sẽ từ chối; **không chạy lại Execute**.

### Hai lệnh bên trong gói

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File Run-TTM-T2-F32-TrainOnly-Integrated-PS51.ps1 -Mode Preview`

**Chỉ khi Preview PASS**, chạy một lần:

`powershell.exe -NoProfile -ExecutionPolicy Bypass -File Run-TTM-T2-F32-TrainOnly-Integrated-PS51.ps1 -Mode Execute`

Bộ chạy sẽ xác minh SHA của toàn bộ tệp, repo/origin/HEAD, Git blob P02, V3 helper, V5B receipt+binary, DLL và manifest fixtures. Nếu thiếu `regex==2026.5.9`, nó chỉ tải **một** wheel này vào venv CPU dự án trong `Execute` (không cài vào Conda `cfcr-gpu-311`), không dùng GPU. `Preview` không tải và không ghi.

## Tiêu chí phán quyết

**PASS kỹ thuật F32 tích hợp** chỉ khi **20/20 tokenizer IDs khớp**, **10/10 logits vectors 2048 chiều sai số tuyệt đối lớn nhất ≤0,001**, **0 top-1 mismatch**, no-overwrite/manifest/nguồn TRAIN-only nguyên vẹn. Báo cáo JSON ghi cả FAIL/mismatch và các SHA. Dù kỹ thuật PASS, `SCIENCE_LOCK=HOLD` cho đến khi quyền TinyStories, train/val/test, tokenizer thực và Colab checkpoint-resume được kiểm định.

**F16**: Dừng ở backend pinned với `unsupported types f32/f16` (V5B). Đề xuất chuyển F16/quantization sang đường tối ưu tùy chọn trong một ADR bổ sung; chỉ mở pilot F32 sau khi thẩm định và chấp nhận sửa tiền đăng ký. **Không xóa hoặc sửa các kết quả V3/V4/V5/V5B**.
