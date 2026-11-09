# TTM-Small T2 V5B — Phân xử độc lập tương đương số học (Parity), phương án ưu tiên F32 và sửa bộ tách token

**Ngày:** 08/11/2026. **Yêu cầu hợp nhất (Pull Request):** PR #12, bản nháp (Draft). **Nguồn:** nhật ký Windows, JSON người dùng đính kèm, JSON đọc lại độc lập qua RemoteDesktop và phép tính SHA bằng Python.

> Đây là bản diễn giải tiếng Việt của [hồ sơ V5B đã khóa](../../pilot/TTM_T2_V5B_PARITY_ADJUDICATION_AND_F32_FIRST_ADAPTER_DECISION_20261108.md). Giữ nguyên các lỗi tại V5B; kết quả F32 ở các lượt sau không được dùng để viết lại biên bản này.

## 1. Khóa bằng chứng (Evidence Lock)

- Đường dẫn báo cáo V5B: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\v5b_technical\TTM_T2_V5B_UTF8_AND_F16_MIXED_DIAGNOSTIC.json`.
- **SHA-256 byte gốc đã tính lại từ tệp người dùng:** `1c2e9e67340ba30c00396af2db707a81cb5bbe8e487ebf5d5dfec91fe05c95bb`, trùng bản đọc trực tiếp trên Windows.
- Mã Git blob nguồn P02: `9762343e06cf800b50574c2871ae1ed58537fb18`. Phiên bản `llama.cpp` được ghim (Pinned): `372dc5ca157276beb6c67b2e92477e8d662e964a`.
- SHA-256 biên bản V4: `b1f064e5626db5b4034b9bf17e424257db767616bc2eae4a420f2be88dca7a34`; V5: `59763e6a153c9f917bb494247ba207b1394fc4c775932b5aba036d09cd6cb147`.
- Ứng viên mô hình F16 có tensor vị trí F32: SHA-256 `8c228098be580e7b224fd0a7b40411402ae796fb9d754f7fcef110ac5edf85d4`; dung lượng **7.684.032 byte**, **52 tensor**, sai lệch lớn nhất khi đọc lại trọng số `3.0517578125e-5`.

## 2. Phân xử kỹ thuật trong đúng phạm vi (Scoped Adjudication)

| Mệnh đề kiểm tra | Trạng thái | Bằng chứng |
|---|---|---|
| Biên dịch và chạy bộ thăm dò gốc (Native Probe) V5B | PASS | Đã tạo và thực thi bộ thăm dò V5B |
| Logits GGUF F32 tương đương | **PASS_SCOPED_8_OF_8** | Sai lệch tuyệt đối lớn nhất `0.0008662939176055651` ≤ ngưỡng `0.001`; **0** sai lựa chọn đứng đầu (Top-1) |
| Byte UTF-8 của đầu vào bộ tách token F32 | PASS_SCOPED_UTF8 | `café` và `Xin chào` không còn sai sau khi chuyển tham số qua mã thập lục phân ASCII (ASCII-hex) |
| Bộ tách token F32 tổng hợp | **FAIL_2_OF_9** | `a b`: TTM `[289,98]`, llama `[97,32,98]`; `a\nb`: TTM `[267,98]`, llama `[97,10,98]` |
| Nạp/chạy tensor F16 trộn tensor vị trí F32 | **STOP_RUNTIME** | `ggml-cpu/binary-ops.cpp:136` đã ghim báo `unsupported types: dst: f32, src0: f32, src1: f16`; **0** logits hợp lệ |
| Phán quyết T2 đầy đủ tại V5B | **NOT_PASS** | Bộ tách token chưa tương đương; kiểu F16 chưa được chương trình gốc thử nghiệm hỗ trợ |
| Thực nghiệm khoa học / TinyStories / Colab | NOT_EXECUTED | `science_executed=false`, `gpu_used=false` |

**Giới hạn kết luận F16:** lỗi của chương trình gốc CPU tại một đồ thị tính toán (Computation Graph) và cách trộn tensor cụ thể; không chứng minh mọi checkpoint F16 hoặc mọi phiên bản backend đều không chạy. Không sửa hoặc cho phép chạy lại V5B. `lineage.md` chỉ ghi khoa học, không ghi thêm lỗi kỹ thuật này.

## 3. Chẩn đoán nguyên nhân bộ tách token và phép thử đối chứng hậu kiểm (Posthoc Diagnostic)

Mã tham chiếu tổng hợp V3 áp dụng BPE lên **toàn chuỗi đầu vào (Whole-string Input)**; trong khi GGUF ghi `tokenizer.ggml.pre=gpt-2`, và `llama.cpp` ghim dùng bộ phân đoạn chính quy (Regular-expression Pretokenizer) từ `src/llama-vocab.cpp` trước BPE. Bộ BPE nguyên gốc có thể gộp qua dấu cách/xuống dòng, còn tokenizer của `llama.cpp` không thể gộp qua ranh giới các đoạn đã tách.

Để kiểm định giả thuyết, đã viết **bộ chuyển đổi đối chứng hậu kiểm (Posthoc Reference Adapter)** bằng Python CPU riêng: áp dụng regex GPT-2 cho từng đoạn, sau đó giữ **đúng** bảng **2.048** mã ID BPE và **1.791** phép hợp nhất tổng hợp, đồng thời kiểm rằng ghép các đoạn trả về đúng văn bản và byte UTF-8.

- Mã `TTM_T2_PRETOKENIZER_GPT2_COMPAT_REFERENCE_20261108.py` có SHA-256 `cc89cfc2c9087b6cfbc4671267e92cb8bfce18683d198cc164bb5ff821d7fb83`.
- Biên bản `TTM_T2_PRETOKENIZER_GPT2_COMPAT_POSTHOC_QA_20261108.json` có SHA-256 `e0cc2bed604c20aa6f3234e1902da27c75930fc3c66c8e2227ebec350b16c007`.
- Mã công cụ tổng hợp gốc có SHA-256 `577a063bd75ec5fe1dea4ad57e0826dffa8a2a99d7ca7327bffd2fee01d5ff1d`.
- **9/9 ca hậu kiểm** khớp mã token native đã thấy ở V5B; bộ tham chiếu toàn chuỗi gốc sai **2/9**. Kết quả này xác nhận giả thuyết **trên bộ tình huống đã biết**, không phải kiểm thử trên tập giữ riêng (Held-out QA) hoặc một lượt chạy `llama.cpp` mới. **Không được đổi FAIL V5B thành PASS T2.**

## 4. Phương án thiết kế — chờ khóa khoa học

**Giữ nguyên các điều kiện bất biến (Invariants):** lõi mô hình P02, quy mô khoảng **3,75 triệu** tham số, từ vựng **2.048 ID** (byte gốc `0..255`, EOS `256`, hợp nhất `257..2047`), tokenizer chỉ học từ TRAIN, phiên bản và cách chia TinyStories, kiểm tra rò rỉ dữ liệu (Leakage), một lượt thực nghiệm khoa học (One-shot), `lineage.md` chỉ bổ sung.

**Sửa đúng điểm trước khi thực nghiệm:** dùng bước tiền phân đoạn tương thích GPT-2 (GPT-2-compatible Pretokenization), đúng regex và ánh xạ byte–Unicode của `llama.cpp` đã ghim; áp dụng ở cả giai đoạn **học quy tắc BPE trên TRAIN** và **mã hóa/giải mã (Encode/Decode)**. Chỉ cho phép gộp trong cùng một đoạn tiền tách, không qua ranh giới dấu cách/xuống dòng. Bản kê (Manifest) phải ghim phiên bản và SHA regex, từ vựng, thứ tự hợp nhất, các mức ưu tiên (Ordered Ranks), EOS, cách mã hóa và chuẩn hóa. Không sửa kết quả đã khóa; thay đổi này phải được đăng ký trước khi chạy khoa học.

**Ưu tiên F32 thay vì tiếp tục các biến thể F16:** mô hình 3,75M chỉ cần GGUF F32 khoảng **15 MB**, phù hợp pilot. Bắt buộc kiểm tra **100% mã token** và logits F32 trên **bộ kiểm thử mới được khóa trước khi chạy**, với tokenizer chỉ dùng TRAIN. F16/lượng tử hóa (Quantization) là tuyến tối ưu độc lập; giữ `F16_PINNED_BACKEND_BLOCKED`, không tuyên bố F16 triển khai được. Chỉ sau bổ sung quyết định kiến trúc (ADR) hoặc tiền đăng ký được duyệt mới chuyển F16 thành tùy chọn; hiện tại `SCIENCE_LOCK=HOLD`.

**Không sửa để tìm PASS:** nếu tokenizer F32 cuối vẫn sai, dừng kỹ thuật (STOP), sửa adapter đã ghim phiên bản, không đổi kiến trúc/cách chia/ngân sách/tập kiểm tra. Không huấn luyện Colab khi chưa có quyết định và bằng chứng thật.

## 5. Bước triển khai tích hợp tối thiểu

`TTM_T2_F32_GPT2_PRETOKENIZER_TRAIN_ONLY_CONTRACT_AND_INTEGRATED_QA`: cập nhật hợp đồng tokenizer TRAIN-only với regex GPT-2; khóa trước bộ tình huống mới gồm khoảng trắng, dấu câu, EOS, xuống dòng/CRLF, Unicode và ranh giới truyện; chạy đúng một lượt GGUF F32 CPU và kiểm tra 2.048 chiều logits trên native, ghim bản kê/SHA, lưu đầy đủ kết quả PASS/FAIL. Lỗi F16 giữ ở hồ sơ kỹ thuật riêng, không chạy lại F16 cho đến khi có giải pháp backend được chứng minh.

**Trạng thái cuối của biên bản gốc:** mở một lượt thẩm định tiền đăng ký tổng hợp T1/T2/T3, không chạy GPU Colab T4 cho tới khi các cổng khoa học và quyền nguồn bắt buộc đạt. PR #12 giữ bản nháp, chưa hợp nhất.

**Tham khảo mã gốc (Upstream):** https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-vocab.cpp và https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/ggml/src/ggml-cpu/binary-ops.cpp
