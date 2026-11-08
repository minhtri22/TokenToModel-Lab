# TTM-Small T2 V5B — Độc lập phân xử PASS/FAIL và phương án sửa tokenizer F32-first

**Ngày:** 2026-11-08 · **PR:** #12 DRAFT · **Nguồn:** Windows log từ chủ dự án, JSON đính kèm, độc lập đọc lại JSON từ RemoteDesktop, Python local SHA kiểm tra.

## 1. Khóa bằng chứng

- V5B report file: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\v5b_technical\TTM_T2_V5B_UTF8_AND_F16_MIXED_DIAGNOSTIC.json`.
- **Raw SHA256 đã tính lại từ tệp đính kèm**: `1c2e9e67340ba30c00396af2db707a81cb5bbe8e487ebf5d5dfec91fe05c95bb`; nội dung cũng đọc trực tiếp trên Windows và trùng với báo cáo.
- Mã P02 Git blob: `9762343e06cf800b50574c2871ae1ed58537fb18`. llama.cpp pinned `372dc5ca157276beb6c67b2e92477e8d662e964a`.
- Receipt V4 SHA: `b1f064e5626db5b4034b9bf17e424257db767616bc2eae4a420f2be88dca7a34`, V5 SHA: `59763e6a153c9f917bb494247ba207b1394fc4c775932b5aba036d09cd6cb147`.
- Gói F16-position-F32 candidate: `8c228098be580e7b224fd0a7b40411402ae796fb9d754f7fcef110ac5edf85d4`, 7,684,032 bytes, 52 tensors, maximal readback weight error `3.0517578125e-5`.

## 2. Phân xử kỹ thuật có giới hạn

| Mệnh đề | Trạng thái | Bằng chứng |
|---|---|---|
| Build V5B native | PASS | đã tạo và thực thi probe V5B |
| F32 GGUF numerical parity | **PASS_SCOPED_8_OF_8** | max |Δlogit| `0.0008662939176055651` <= frozen threshold `0.001`, 0 top1 mismatch |
| F32 tokenizer text byte integrity | PASS_SCOPED_UTF8 | `café` và `Xin chào` không còn mismatch sau chuyển ASCII-hex |
| F32 tokenizer overall | **FAIL_2_OF_9** | `a b`: TTM `[289,98]`, llama `[97,32,98]`; `a\nb`: TTM `[267,98]`, llama `[97,10,98]` |
| F16 + F32 positional tensors load/run | **STOP_RUNTIME** | pinned `ggml-cpu/binary-ops.cpp:136`, `unsupported types: dst: f32, src0: f32, src1: f16`; 0 valid logits |
| T2 full | **NOT_PASS** | tokenizer incomplete; F16 unsupported on tested backend/configuration |
| Science / TinyStories / Colab | NOT_EXECUTED | `science_executed=false`, `gpu_used=false` |

**Chú ý:** F16 lỗi backend CPU tại một graph/mix tensor cụ thể; chưa đủ bằng chứng khẳng định mọi checkpoint F16 hoặc mọi backend/phiên bản đều lỗi. Không sửa hoặc cấp quyền chạy lại V5B. `lineage.md` chỉ chứa khoa học, không append lỗi QA kỹ thuật này.

## 3. Chẩn đoán nguyên nhân tokenizer và thử nghiệm đối chứng kỹ thuật không khoa học

V3 synthetic oracle thực hiện BPE trên **whole input string**, trong khi GGUF ghi `tokenizer.ggml.pre=gpt-2` và pinned llama.cpp `src/llama-vocab.cpp` tách regex trước BPE. Merge crossing a space/newline in oracle không thể xuất hiện qua các đoạn đã tách bởi llama.cpp.

Để kiểm chứng giả thuyết, đã tạo **reference adapter hậu kiểm (posthoc)** trên Python CPU trong môi trường riêng: thực hiện đúng regex GPT-2 trên từng segment, sau đó áp dụng **chính** bảng 2.048 synthetic IDs và 1.791 synthetic merges gốc, kiểm tra nối các segment trả lại đúng văn bản/UTF-8.

- Code: `TTM_T2_PRETOKENIZER_GPT2_COMPAT_REFERENCE_20261108.py`, SHA256 `cc89cfc2c9087b6cfbc4671267e92cb8bfce18683d198cc164bb5ff821d7fb83`.
- QA JSON: `TTM_T2_PRETOKENIZER_GPT2_COMPAT_POSTHOC_QA_20261108.json`, SHA256 `e0cc2bed604c20aa6f3234e1902da27c75930fc3c66c8e2227ebec350b16c007`.
- Pinned original synthetic helper SHA256 `577a063bd75ec5fe1dea4ad57e0826dffa8a2a99d7ca7327bffd2fee01d5ff1d`.
- **9/9 posthoc fixtures** trùng với các ID native đã quan sát ở V5B; original whole-string oracle sai 2/9. Điều này xác minh giả thuyết trên **chính** fixtures cũ, KHÔNG phải held-out tokenizer QA hoặc new llama.cpp runtime run. Không được thay chữ FAIL V5B thành T2 PASS.

## 4. Quyết định thiết kế đề xuất — chưa khóa khoa học

**Giữ các bất biến**: P02 core, mô hình ~3.75M, 2.048 vocab IDs (byte base 0..255, EOS 256, 1.791 merges 257..2047), tokenizer chỉ TRAIN, TinyStories version/source/split, kiểm thử leakage, one-shot science, `lineage.md` append-only.

**Sửa trước khi thực nghiệm**: pretokenization GPT-2-compatible (exact pinned llama.cpp regex & byte-to-Unicode mapping), **áp dụng tại cả bước học merges trên TRAIN và encode/decode**; BPE merges chỉ gộp trong mỗi pretokenized segment, không qua khoảng trắng/newline boundary. Lưu regex version/hash, vocab, merges, ordered ranks, EOS, encoding/normalization trong manifest. Không sửa các kết quả thử đã khóa. Đây là thay đổi **đề xuất vào tiền đăng ký chưa chốt**, phải được thẩm định nhất quán trước science.

**Đề xuất F32-first thay vì tiếp tục thử nhiều biến thể F16**: với model 3.75M, GGUF F32 ~15 MB là đủ nhỏ cho pilot; cần F32 token-ID parity 100% và logits PASS trên **fixtures mới xác định trước lần chạy** và tokenizer TRAIN-only sau khi freeze. F16/quantization là đường tối ưu hiệu năng riêng; ghi `F16_PINNED_BACKEND_BLOCKED` và không tuyên bố deploy F16. **Thay đổi cổng F16 thành tùy chọn chỉ được áp dụng sau khi phê duyệt bổ sung ADR/prereg**; hiện tại `SCIENCE_LOCK=HOLD`.

**Không sửa để tìm PASS:** nếu F32 final tokenizer còn sai, STOP kỹ thuật, sửa adapter đã version-pin, không đổi kiến trúc/split/budget/test. Không huấn luyện Colab khi chưa có quyết định cổng và kiểm thử thực tế.

## 5. Bước triển khai tối thiểu duy nhất (không tách permit nhỏ)

`TTM_T2_F32_GPT2_PRETOKENIZER_TRAIN_ONLY_CONTRACT_AND_INTEGRATED_QA`: cập nhật hợp đồng tokenizer TRAIN-only phù hợp GPT2 regex; thêm bộ test fixture mới gồm whitespace, punctuation, EOS, newline/CRLF, Unicode và story boundaries **niêm phong trước khi chạy**; một lượt CPU F32 GGUF/native tokenizer/2048 logits QA; ghim manifest/hashes và ghi cả PASS/FAIL. F16 STOP được giữ ở technical issue khác, không rerun thử F16 cho đến khi có giải pháp backend chứng minh được.

**Cuối bước:** một thẩm định tiền đăng ký tổng hợp T1/T2/T3, không mở GPU Colab T4 trước khi tất cả cổng khoa học và quyền nguồn bắt buộc đã đạt. PR #12 tiếp tục draft/unmerged.

**Tham chiếu mã upstream:** https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-vocab.cpp ; https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/ggml/src/ggml-cpu/binary-ops.cpp
