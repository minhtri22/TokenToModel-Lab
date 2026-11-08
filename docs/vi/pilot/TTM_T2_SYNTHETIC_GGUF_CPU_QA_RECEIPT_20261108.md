# TTM T2 — Biên bản triển khai xuất GGUF và kiểm thử tích hợp CPU bằng dữ liệu tổng hợp (08/11/2026)

> **Bản dịch hồ sơ kỹ thuật tại thời điểm lập biên bản:** không thay đổi kết luận lúc đó. Những kiểm tra native F32 và dữ liệu thật đã đạt sau đó được ghi trong [biên bản đóng T1–T3](../../pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md). [Bản gốc](../../pilot/TTM_T2_SYNTHETIC_GGUF_CPU_QA_RECEIPT_20261108.md) được bảo toàn.

**Yêu cầu hợp nhất (Pull Request):** PR #12, bản nháp (Draft). **Mốc gốc:** `main@1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.  
**Mã đối tượng Git nguồn P02 (Source Git Blob):** `9762343e06cf800b50574c2871ae1ed58537fb18`.  
**Chương trình đích đã khóa:** `ggml-org/llama.cpp@372dc5ca157276beb6c67b2e92477e8d662e964a`.  
**Gói triển khai T2:** `TTM_SMALL4M_T2_GGUF_CPU_QA_V1_20261108.zip`, lúc đó **chưa đưa lên GitHub**. SHA-256 ZIP: `F63123689CCD3D25A02A288CFC82D887615ECBBAC98424895CC9B7D0BF912D00`.

## Phạm vi thực thi (Execution Scope)

Đã chạy trong vùng chứa CPU tạm (Ephemeral CPU Container), với `torch 2.10.0+cpu` và Python 3.13, dùng **mã nguồn P02 giống hệt từng byte** với đối tượng Git gốc (`sha1('blob <size>\\0'+source)` = `9762343e...`). Đây chỉ là bản phản chiếu nguồn (Source Mirror) cho kiểm thử có thể tái lập, **không** chỉnh sửa GitHub hay thư mục Windows của người dùng. Không sử dụng TinyStories, không huấn luyện, không dùng Colab/GPU, không công bố mã, không mở tập TEST khoa học.

Gói gồm `t2_gguf_cpu.py`, `t2_llama_parity.py`, `llama_logits_probe.cpp` (bộ thăm dò C++ native), `CMakeLists.txt`, `test_t2_gguf_cpu.py`, bộ chạy PowerShell 5.1 và `T2_QA_REPORT_20261108.json`. **Bộ PowerShell lúc đó chưa kiểm tra động trên Windows của người dùng.**

## Kết quả kiểm thử đã đo (Measured QA)

| Phép kiểm | Kết quả được xác minh lúc đó |
|---|---|
| Cấu hình mô hình | Từ vựng **2.048**, ngữ cảnh **256**, **4 lớp**, **4 đầu chú ý**, chiều nhúng (Embedding Dimension) **256** |
| Số tham số không trùng | **3.749.376**, dùng chung trọng số đầu ra (Tied Output Head) |
| Ánh xạ tensor GGUF | Đọc lại được tên, hình dạng và kiểu của **52/52 tensor** |
| GGUF F32 | **PASS** cấu trúc và đọc lại trọng số; **15.051.712 byte**, sai lệch lớn nhất **0,0** |
| GGUF F16 | **PASS** kiểm tra cấu trúc/đọc lại trọng số; **7.552.960 byte**, sai lệch lớn nhất **3.0517578125e-5** |
| SHA-256 F32 | `b1b22687b60c65da2d585da5f8b553398cb537b3caa3f465532edd0092102bd8` |
| SHA-256 F16 | `a2b90ec458b592ce38bae4588a8db60660ab92add08491f80662d5d0a7d937cd` |
| Hợp đồng BPE tổng hợp | **256** mã byte + EOS=256 + **1.791** phép hợp nhất cặp được tạo tất định |
| Kiểm thử Python trên CPU (pytest) | **9/9 PASS**, kể cả từ chối ghi đè, tiêu đề hỏng, tệp cắt cụt và nguồn bị sửa |
| Nạp bằng tệp chạy `llama.cpp` đã khóa | **NOT_EXECUTED**, chương trình nhị phân chưa được cài trong vùng chạy CPU cô lập |
| Đối chiếu logits giữa PyTorch và `llama.cpp` | **NOT_EXECUTED** |
| Đối chiếu tokenizer của `llama.cpp` với BPE đại diện TTM | **NOT_EXECUTED** |
| Phán quyết tích hợp T2 tại thời điểm đó | **HOLD_LLAMA_CPU_BACKEND_AND_TOKENIZER** |

**Phát hiện về ánh xạ trọng số (Tensor Mapping):** `nn.Linear` của TTM/PyTorch lưu tensor dưới dạng `[out,in]`, nên ghi trực tiếp theo thứ tự hàng (Row-major) trong GGUF là đúng. Bộ chuyển đổi GPT-2 của Hugging Face phải chuyển vị (Transpose) vì `Conv1D` của HF lưu `[in,out]`. Chuyển vị thêm lần nữa cho TTM là lỗi. Việc xuất được tệp, nạp bộ chuyển đổi hoặc tự đọc lại trọng số **không chứng minh** tương đương logits của chương trình suy luận gốc.

**Rủi ro bộ tách token (Tokenizer):** BPE đại diện ban đầu thao tác trên toàn chuỗi ở mức byte, còn GPT-2 có quy tắc tiền phân đoạn bằng biểu thức chính quy (Pretokenization Regex). Chuỗi chứa dấu cách, xuống dòng hoặc Unicode cần đối chiếu bằng `llama_tokenize` thực. Nếu sai, đó là lỗi thật của T2 và phải sửa cách tương thích tokenizer; không được âm thầm đổi kiến trúc hay tiêu chí khoa học.

## Phép kiểm CPU Windows đã được quy định nhưng lúc đó chưa chạy

- Xác minh đúng kho Git, mã nguồn đã khóa; chạy `-Mode Preview` (chỉ đọc) rồi `-Mode Execute` một lượt từ ZIP. Chỉ `-AcquirePinnedLlamaCpp` mới được phép tải **mã nguồn `llama.cpp`**, không tải TinyStories; hoặc dùng nguồn có sẵn qua `-LlamaSource`.
- Bộ thăm dò C++ native ở commit ghim phải trả về vector logits đủ **2.048 chiều**, chấp nhận mã token đầu vào rõ ràng và **9** trường hợp kiểm thử tokenizer. Ngưỡng sai lệch logits F32 `<=1e-3`, F16 `<=2e-2`; cần **8** trường hợp số học và **9** trường hợp tách token, cùng lựa chọn đứng đầu (Top-1). Nếu FAIL phải giữ nguyên FAIL.
- Lưu nhật ký console, biên bản cuối và SHA. Rà soát từng tệp nguồn có SHA trước khi đưa vào PR #12. **Không** chạy huấn luyện Colab dài khi chưa chứng minh tương đương tokenizer và chương trình suy luận.

## Quản trị (Governance) và trạng thái lịch sử

`TTM_T2_STRUCTURAL=PASS` · `T2_WEIGHT_READBACK=PASS` · `T2_PYTHON_9_OF_9=PASS` · `T2_LLAMA_CPP_CPU=NOT_EXECUTED` · `T2_FULL=HOLD` · `SCIENCE_LOCK=HOLD` · `COLAB_T4_GPU=NOT_USED`.

Không sửa `lineage.md`; đây chỉ là biên bản QA kỹ thuật, **không phải kết quả khoa học PASS**.

**Bước tiếp theo trong biên bản gốc:** chạy kiểm tra native CPU trên Windows với nguồn ghim; sau khi có biên bản, hoặc cho phép bước T1/T3 hoặc phân loại sai lệch T2 và sửa riêng bộ chuyển đổi (Adapter). Không chạy lại khoa học.
