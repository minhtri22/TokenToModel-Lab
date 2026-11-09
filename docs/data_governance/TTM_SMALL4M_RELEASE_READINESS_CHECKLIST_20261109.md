# TTM-Small-4M — Checklist trước khi phát hành (Release Decision Template)

**Trạng thái hiện tại:** DRAFT_REVIEW / NO_RELEASE_PERMIT. Mẫu này không tự cấp phép công bố dữ liệu, mã nguồn hoặc mô hình.

## 1. Định nghĩa các quyết định riêng

| Phần phát hành | Owner signoff | Đánh giá quyền | Kiểm tra nhạy cảm | Kết quả tạm |
|---|---|---|---|---|
| Source code/T1–T5 | Chưa có | LICENSE root chưa có; third-party audit chờ | source-secret scan chờ | HOLD |
| Dataset card / Model card / QA sanitized | Phạm vi nhánh tài liệu | Có nguồn và trích dẫn | Không chứa raw data/secret | SCOPED_READY |
| Original TinyStories raw copy | Chưa có | CDLA-Sharing-1.0 obligations R1/R2 chờ | privacy/copyright chờ | HOLD |
| Derived TRAIN/VAL/TEST pack | Chưa có | CDLA Enhanced Data/Results classification chờ | sealed TEST & privacy chờ | HOLD |
| BPE merges tokenizer | Chưa có | quyền learned artifact chưa giải quyết | reconstructability chờ | HOLD |
| PyTorch model step1024/1280 | Chưa có | weights license chưa chọn | memorization extraction chờ | HOLD |
| GGUF F32 Ollama model | Chưa có | phụ thuộc weights/BPE/tooling | strict logits FAIL7/8 phải nêu | HOLD |
| Sampler/generation demo output | Chưa có | text similarity/copyright chờ | redact PII/unsafe content chờ | HOLD |

**Lưu ý:** giấy phép upstream CDLA-Sharing-1.0 cho phép use/publish data theo điều kiện, không đồng nghĩa mọi hoạt động publish đều bị cấm. Kết luận HOLD là thiếu chứng cứ/signoff, không phải ý kiến pháp lý khẳng định cấm.

## 2. Một gói chứng thực tối thiểu

- R1: upstream card/revision/hash và chủ thể cấp phép đã được đối chiếu.
- R2: CDLA-Sharing-1.0 attribution, notice sửa đổi, cách cấp lại Data/Enhanced Data được review.
- R3: từng gói weight/merge/GGUF/output được đánh giá khác biệt Data và Results.
- R4: PII/copyright/memorization và khả năng model trả lại truyện nguồn được kiểm tra bằng dữ liệu được phép, **không mở lại TEST đã tiêu thụ**.
- R5: owner lựa chọn source LICENSE/weight license, có SBOM/third-party notices cho các bản phân phối.
- R6: reproduce package có source SHA, tokenizer, RNG, checkpoint READY, environment, weights hash, đối chiếu SHA thực.
- R7: hồ sơ phát hành công bố cả PASS/FAIL/HOLD, tách kỹ thuật và khoa học; không sửa kết quả H1, TEST hoặc FAIL7/8.
- R8: chủ dự án phê duyệt chính xác các file/đường dẫn/phiên bản được phát hành, phạm vi, ngày, reviewer và giá trị SHA.

## 3. Phiếu ký chưa điền

- Release candidate identifier: **PENDING**
- Scope: source / dataset / BPE / weights / GGUF / examples — **PENDING**
- Owner signoff: **PENDING**
- Reviewer quyền dữ liệu: **PENDING**
- Reviewer PII/memorization: **PENDING**
- Binary SHA256 manifest: **PENDING**
- R1–R8 adjudication: **HOLD**
- Final decision: **HOLD_NO_RELEASE_AUTHORIZATION**

Sau khi quyết định, xuất một receipt riêng và dẫn tới manifest chính thức; không sửa bản nháp lịch sử để biến HOLD thành PASS. Không nhập bản ghi quản trị kỹ thuật vào khoa học append-only lineage.md.

**Bước thực hiện tiếp theo:** chủ dự án đánh giá gói quyền và cấp phạm vi phát hành cụ thể nếu đủ chứng cứ; nhánh docs hiện chỉ đề xuất card/release policy.
