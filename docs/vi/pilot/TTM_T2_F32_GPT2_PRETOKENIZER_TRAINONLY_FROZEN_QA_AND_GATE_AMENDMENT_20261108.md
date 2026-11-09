# TTM-Small-4M T2 F32 — Tiền phân đoạn GPT-2 (Pretokenizer), chỉ dùng TRAIN và kiểm thử native đã khóa

**Ngày:** 08/11/2026. **Mốc đối chứng (Baseline):** PR #12 ở trạng thái bản nháp (Draft), từ `main@1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`; mã Git blob nguồn P02 `9762343e06cf800b50574c2871ae1ed58537fb18`; mã `llama.cpp` `372dc5ca157276beb6c67b2e92477e8d662e964a`. Không thay đổi P00–P12, P07 hoặc `lineage.md`.

> Đây là bản tiếng Việt của [tài liệu kỹ thuật T2 F32 gốc](../../pilot/TTM_T2_F32_GPT2_PRETOKENIZER_TRAINONLY_FROZEN_QA_AND_GATE_AMENDMENT_20261108.md). Các trạng thái trước khi chạy Windows được giữ nguyên để bảo toàn lịch sử; hãy xem kết luận sau đó trong [hồ sơ đóng kỹ thuật T1–T3](../../pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md).

## 1. Phạm vi thiết kế đã triển khai

- Gói mã CPU `TTM_SMALL4M_T2_F32_GPT2_TRAIN_ONLY_INTEGRATED_QA_20261108.zip`, SHA-256 `d6fd9d09a031c4c19e099f0d66d7d5fcccc0e8543ea602d7268ec6cb415dbcb9`, gồm chương trình học BPE bằng Python (BPE Fitter), bộ xuất GGUF F32 và bộ chuyển đổi suy luận (Inference Adapter), bộ chạy dòng lệnh PowerShell 5.1, kiểm thử hồi quy (Regression Tests), dữ liệu kiểm thử (Fixtures), README và bản kê mã băm từng tệp (Hash Manifest). **Lúc lập hồ sơ, gói mới là tệp đính kèm, chưa commit mã lên PR**; chỉ sau khi Windows native PASS mới đưa đúng byte đã khóa lên GitHub.
- SHA-256 bộ chạy PowerShell: `62f0246ddbebe01aa8603e781226ea5cc8436141442b71e4dc3e595f5bd0be73`. Bộ chạy kiểm tra SHA tất cả thành phần, đúng `llama.cpp`, chương trình thăm dò (Native Probe), thư viện động (DLL), nguồn P02 và thư mục kết quả mới, không ghi đè (No-overwrite).
- BPE: các mã byte `0..255`; mã kết thúc truyện (EOS) `256`; **1.791** phép hợp nhất tất định (Deterministic Merges) ở ID `257..2047`, metadata `tokenizer.ggml.pre=gpt-2`. Biểu thức chính quy (Regex) đúng bản GPT-2 đã ghim; bảo toàn mọi ký tự không khớp regex (CRLF, tab, newline). Chỉ gộp trong từng đoạn tiền tách (Pretokenized Segment), không gộp qua ranh giới truyện hoặc tập dữ liệu.
- Quy tắc `train_only` chỉ chấp nhận đối tượng `Story(split=TRAIN)` từ nguồn đã cho phép. T2 học quy tắc hợp nhất từ **720 truyện TRAIN tổng hợp**, chưa dùng TinyStories hoặc học khoa học. Khi có TRAIN thật, phải khóa revision/SHA, quy tắc phân đoạn truyện, chống trùng (Deduplication), bản kê (Manifest) và quyền. Không dùng VAL/TEST để học BPE.
- Hợp đồng xuất F32: giữ nguyên **52 tensor** P02, đọc lại trọng số F32 với sai lệch lớn nhất **0**, đưa đủ metadata token và thứ tự hợp nhất; mô hình **3.749.376 tham số**. Không thay đổi kiến trúc, không thử F16 trong lượt QA tích hợp này.

## 2. Bộ tình huống kiểm thử đã khóa trước khi chạy native (Frozen Fixtures)

`TTM_T2_F32_NEW_FIXTURES_FROZEN_20261108.json`, SHA-256 `5a4ba58db3ad7c1ad0a7c6a790c08184d43c1e3a081ad2dcaf2d4c3b9dbeb9f2`, có **20** chuỗi thử tokenizer và **10** chuỗi mã ID cho kiểm tra số học độc lập. Bộ này không trùng các ca V5B; bao phủ khoảng trắng, tab, CRLF, Unicode, dấu câu, xuống dòng, lời nhắc (Prompt) và EOS. Mọi tình huống được khóa **trước** khi kiểm thử Windows native.

**Ngưỡng chấp nhận:** **20/20** mã token từ `llama.cpp` phải đúng tuyệt đối với bộ tham chiếu BPE byte (Byte-BPE Oracle); **10/10** vector logits **2.048 chiều** F32 có sai lệch lớn nhất (Maximum Absolute Error) ≤ `0.001`, không sai Top-1. Các khóa P02/Git blob/chương trình thăm dò/DLL/bản kê/chống ghi đè phải PASS. Không coi kết quả hậu kiểm (Posthoc) **9/9** từ V5B là kiểm thử giữ riêng (Held-out Evidence).

## 3. Kết quả đã có và các cổng còn thiếu lúc lập hồ sơ

| Hạng mục | Trạng thái tại thời điểm ghi |
|---|---|
| BPE tổng hợp đúng 2.048 mã, 1.791 hợp nhất, từ chối nguồn ngoài TRAIN | `PASS_CPU_UNIT` |
| Mã hóa–giải mã vòng tròn (Round-trip) UTF-8/CRLF/dấu câu, từ chối bản kê bị sửa | `PASS_CPU_UNIT` |
| Bộ tình huống mới có SHA và không trùng V5B | `PASS_CPU_UNIT` |
| GGUF F32 từ P02 có 52 tensor, đọc trọng số sai lệch 0 | `PASS_CPU_UNIT` |
| Kiểm thử `pytest` của Python | **11/11 PASS** trong Linux CPU/Python 3.13/`torch 2.10.0+cpu`/`regex 2026.5.9` cô lập |
| Toàn vẹn ZIP, CRC, SHA cả bảy tệp | `PASS_PACKAGE_STATIC` |
| Phân tích cú pháp PowerShell 5.1 trên Windows người dùng | `NOT_EXECUTED` |
| `llama.cpp` native F32 trên 20 ca tokenizer + 10 ca số học | **`NOT_EXECUTED`** |
| Học tokenizer từ TinyStories TRAIN thật; kiểm nguồn, chia tập, chống trùng và Colab resume | `NOT_EXECUTED / SCIENCE_LOCK_HOLD` |

## 4. Đề xuất điều chỉnh cổng T2 — ưu tiên F32 (F32-first)

**Khuyến nghị thẩm định (Review Recommendation):** với mô hình khoảng 3,75 triệu tham số, trước khi huấn luyện dài phải chứng minh suy luận GGUF F32 thực, mã token chính xác và logits tương đương. Đây là điều kiện **bắt buộc** của bước khả thi xuất mô hình trước huấn luyện. F16 và lượng tử hóa (Quantization) chuyển sang tuyến tối ưu hiệu năng độc lập, không dùng làm bằng chứng học được của mô hình.

Đề xuất giữ kiến trúc và trình tự P00–P12, giảm các cổng kỹ thuật nhỏ lặp lại. Lỗi V5B khi trộn `f16+position_f32` vẫn giữ STOP với thông báo `unsupported types: dst: f32, src0: f32, src1: f16`; đề xuất không hồi tố thành PASS.

**Trạng thái lịch sử:** `F32_FIRST_GATE_AMENDMENT=PROPOSED_PENDING_REVIEW` · `T2_F32_NEW_FROZEN_QA=READY_FOR_WINDOWS` · `T2_FULL=HOLD` · `SCIENCE_LOCK=NOT_GRANTED`. Tài liệu này chưa cấp quyền dùng GPU Colab hoặc huấn luyện.

## 5. Bước tích hợp tiếp theo duy nhất tại thời điểm đó

Dùng đúng mã PowerShell đã đóng gói trên Windows trong thư mục Downloads mới: xác minh SHA và cú pháp PS5.1 → `-Mode Preview` chỉ đọc → `-Mode Execute` đúng một lượt ở `_tmp/ttm_t2/f32_pretok_trainonly_v1`. Chỉ cài thêm thư viện bánh xe (Wheel) đã ghim `regex==2026.5.9` vào môi trường Python CPU cô lập của TTM nếu thiếu. Các hiện vật V3/V4/V5/V5B vẫn chỉ đọc; không tải nguồn hoặc biên dịch C++.

Sau đó đọc JSON độc lập, phân loại FAIL thật hay PASS. Nếu PASS, lưu mã/bản kê đúng SHA vào PR #12 và mở tiền kiểm nguồn T1/T3/Colab chỉ **sau** khi điều chỉnh quản trị được chấp thuận. Chưa dùng seed khoa học, TEST hoặc GPU huấn luyện T4 trước khóa tiền đăng ký cuối.
