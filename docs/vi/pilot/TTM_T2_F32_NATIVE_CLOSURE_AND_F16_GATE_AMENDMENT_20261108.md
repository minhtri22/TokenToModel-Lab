# TTM-Small-4M — Đóng kiểm thử native T2 F32 và điều chỉnh cổng F16

**Ngày:** 08/11/2026. **Phạm vi (Scope):** PR #12 ở trạng thái nháp (Draft); chứng minh khả thi khi xuất GGUF bằng dữ liệu tổng hợp, **không** chứng minh mô hình đã học. **Mốc `main` chính xác:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.

> Bản diễn giải tiếng Việt của [hồ sơ lịch sử đã khóa](../../pilot/TTM_T2_F32_NATIVE_CLOSURE_AND_F16_GATE_AMENDMENT_20261108.md). Trạng thái `NOT_EXECUTED` phía dưới được giữ đúng **thời điểm ghi hồ sơ**; không phải kết luận mới nhất sau T1–T3.

## 1. Đọc lại độc lập và nguồn gốc (Independent Readback and Provenance)

Biên bản CPU được đối chiếu giữa JSON người dùng cung cấp và bản được đọc độc lập trực tiếp trên Windows:

- **Đường dẫn gốc:** `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\f32_pretok_trainonly_v1\TTM_T2_F32_GPT2_PRETOKENIZER_INTEGRATED_QA.json`.
- **SHA-256 byte chính xác:** `21fbaa01e2b9e57f500884c6f4d77c25203d1d4ee89944abf91028c1770348ef`. Tệp được lưu nguyên byte ở `evidence/pilot/t2-f32/TTM_T2_F32_GPT2_PRETOKENIZER_INTEGRATED_QA.json`, mã đối tượng Git (Git Blob) `d156c0699c5b1ecafcafbd832796a06f3d24b433`.
- **SHA-256 của bộ tình huống kiểm thử đã khóa (Frozen Fixtures):** `5a4ba58db3ad7c1ad0a7c6a790c08184d43c1e3a081ad2dcaf2d4c3b9dbeb9f2`, gồm 20 ca tokenizer và 10 ca logits. Bản Git ở `evidence/pilot/t2-f32/TTM_T2_F32_NEW_FIXTURES_FROZEN_20261108.json` có mã `2b187347a89531202cebf9e6062a2b737e079714`.
- **Nguồn mô hình P02:** mã đối tượng Git `9762343e06cf800b50574c2871ae1ed58537fb18`. **Chương trình suy luận `llama.cpp` đã ghim:** `372dc5ca157276beb6c67b2e92477e8d662e964a`. **SHA-256 bộ thăm dò native V5B:** `080c096d52448f665df43ebc962d7a62b17a0781326bc6358e8535d25f37c963`.
- **SHA-256 gói mã ZIP:** `d6fd9d09a031c4c19e099f0d66d7d5fcccc0e8543ea602d7268ec6cb415dbcb9`; danh sách SHA từng tệp được lưu ở `evidence/pilot/t2-f32/BUNDLE_SHA256_MANIFEST.json`, Git blob `63ab6fcd98fd9f15695d35f2dfaac652efc6a671`. **Tại thời điểm biên bản gốc được lập**, ZIP và mã giải nén chỉ hiện diện trong tệp đính kèm cuộc trò chuyện, chưa được commit lên GitHub. Bản kê được tạo **trước** khi chạy Windows nên trường `native_windows=NOT_EXECUTED` phải giữ nguyên, không sửa hồi tố.
- **SHA-256 GGUF F32:** `474bc1dcb472cca429ce07747bdaf6ecbe8a7e9b66ce4d5e8658ad919e5e191e`; **15.052.128 byte**, **52 tensor**, sai lệch tuyệt đối tối đa khi đọc lại trọng số bằng **0**.
- **Bộ tách token BPE:** **2.048** ID = **256 byte** + mã kết thúc EOS ID **256** + **1.791** phép hợp nhất (Merges) trên các đoạn đã tiền tách theo GPT-2, chỉ dùng TRAIN. SHA cam kết nguồn BPE tổng hợp `e85028842955334cad014d6f1365f95d79ec953f7cab3a0a2f75ded83bcb1a08`; SHA bản kê đầu ra `652d74488646d8d329792a37cef3ba1bfcd221d7ec7ee57dc6700208a3ca1fca`. Bản kê đầy đủ vẫn ở thư mục chạy một lần trên Windows; bản đọc từ xa bị cắt đoạn khoảng 20.000 ký tự nên **không** đưa một phiên bản thiếu vào GitHub.
- **Đối chiếu native trên CPU:** **20/20** mã token chính xác; **10/10** vectơ logits có **2.048 chiều**, sai lệch tuyệt đối lớn nhất `0.0008438229900207261` ≤ ngưỡng tiền đăng ký `0.001`, không sai lựa chọn đứng đầu (Top-1).
- **Phép thử từ chối (Negative Controls):** `reject_VAL`, `reject_TEST`, `reject_wrong_source`, `reject_unknown_token_id`, `reject_EOS_decode` đều đúng (True).
- **Ranh giới:** `train_data=SYNTHETIC_TRAIN_FIXTURE_ONLY_NOT_TINYSTORIES`, `gpu_used=false`, `science_executed=false`. **Lúc đó chưa tải nguồn TinyStories thật.**

## 2. Phán quyết kỹ thuật tích hợp (Integrated Technical Decision)

`T2_F32_EXPORT_FEASIBILITY=PASS_TECHNICAL_SCOPED`.

Mô hình P02 được khởi tạo trọng số ngẫu nhiên, kết hợp BPE 2.048 ID chỉ học từ tập TRAIN mô phỏng; sau đó xuất GGUF F32 và dùng `llama.cpp` CPU thực để kiểm tra **20/20 ca tokenizer mới** và **10/10 ca logits mới**. Bằng chứng này đủ để đóng câu hỏi **khả thi xuất F32 tổng hợp**, **không chứng minh** việc chuyển checkpoint sau huấn luyện, chạy Ollama, chất lượng dữ liệu hoặc giả thuyết H1.

**Thay đổi tuyến bắt buộc với F16 (Critical-path Change):** đối với mô hình khoảng 3,75 triệu tham số, độ đúng khi suy luận F32 phải đạt trước khi huấn luyện dài. F16 và lượng tử hóa (Quantization) Q8/Q4 được chuyển sang tuyến tối ưu/triển khai A/B tùy chọn. Các lỗi V4/V5B vẫn được bảo lưu `F16_BACKEND_BLOCKED`, không được đổi thành PASS. Đây là điều chỉnh tiêu chí ra khỏi giai đoạn T2 ở phạm vi pilot nháp, **không** thay đổi kiến trúc P00–P12, lịch sử kiểm thử, P07 hoặc phân biệt QA kỹ thuật với lịch sử khoa học. Muốn coi là khóa quản trị toàn dự án vẫn cần rà soát và hợp nhất.

## 3. Các điều kiện còn bắt buộc theo ảnh chụp lịch sử (Remaining Gates)

- **T1:** rà soát phiên bản/quyền TinyStories; kiểm SHA của byte nguồn thật, phân đoạn truyện, chống trùng chính xác và trùng gần, bản kê TRAIN/VAL/TEST, không rò rỉ TEST; học BPE 2.048 ID từ **TRAIN thật** và kiểm tra lại mã token gốc của chính bộ mã đã khóa.
- **T3:** đo năng lực tổng hợp (Synthetic Capacity Smoke) trên GPU T4 do Colab cấp, khóa thư viện/môi trường; đọc lại checkpoint theo cơ chế ghi READY cuối cùng (READY-last), đối chiếu 20 bước liên tục với 10 → lưu → khôi phục → 10, gồm bộ tối ưu, lịch học, RNG và con trỏ.
- **Trước T4:** thẩm định tiền đăng ký khoa học tổng hợp (Integrated Scientific Preregistration); không xin giấy phép riêng cho mỗi kiểm tra kỹ thuật nhỏ.
- **T5:** đối chiếu số học và chất lượng sinh của checkpoint **đã học** khi xuất GGUF qua Windows/`llama.cpp`/Ollama; không suy ra từ T2 tổng hợp.
- **Nhật ký khoa học:** không đưa QA kỹ thuật vào tệp `lineage.md` chỉ ghi bổ sung (Append-only).

| Cổng | Phán quyết tại thời điểm ghi |
|---|---|
| `T2_F32_NEW_FROZEN_TOKENIZER_NATIVE` | **PASS 20/20** |
| `T2_F32_NEW_FROZEN_LOGITS_NATIVE` | **PASS 10/10, sai lệch lớn nhất 0.00084382299** |
| `T2_F32_SYNTHETIC_EXPORT` | **PASS / TECHNICALLY CLOSED** |
| `T2_F16_CPU` | **BLOCKED**, giữ kết quả cũ |
| `T1_REAL_DATA_AND_TRAINONLY_BPE` | NOT_EXECUTED |
| `T3_COLAB_DRIVE_RESUME` | NOT_EXECUTED |
| `T5_TRAINED_CHECKPOINT_EXPORT` | NOT_EXECUTED |
| `SCIENCE_LOCK` | **HOLD** |
| `COLAB_T4` | **NOT_STARTED** |

**Bước thực hiện tiếp theo theo tài liệu gốc:** `TTM_SMALL4M_T1_T3_TINYSTORIES_SOURCE_SPLIT_AND_COLAB_DRIVE_RESUME_INTEGRATED_PREFLIGHT`. Giữ nguyên QA kỹ thuật đã tiêu thụ, đưa ZIP mã đã khóa và mã thành phần lên PR #12 trước hợp nhất, không tạo lượt T2 mới; không mở TinyStories TRAIN hoặc GPU T4 khoa học trước khi cổng nguồn thật và phục hồi đạt.
