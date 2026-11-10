# TTM EmbeddingGemma 2 SEMANTIC4X3 — Kết quả khoa học ứng viên, độc lập số học và 12 checkpoint SHA PASS

**Ngày:** 10/11/2026 · **StudyID:** `ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2` · **Nguồn runner:** `a3182549739cda848ce0f7f449b1f1455e06419d72295dcee96f0e8a7822f676`.

**Trạng thái:** `SCIENCE_COMPLETED_PENDING_INDEPENDENT_ADJUDICATION`. Kết quả khoa học **ứng viên** `PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE`, **chưa ghi L0020** cho đến khi frozen checker xác minh toàn bộ 96 READY.

## Dữ liệu và kết quả

12 arms × 2048 bước, 4096 labels/update, một Tesla T4, H768 mới 768 truyện / 1000 windows / 186655 labels. `STUDY_CLAIM` `5c76c4da3d1d1c0532f04a7ff557fd0f8e46279e7e1590dd34cf7801368b47a2`, `RESULT` `d60f8e206b20b30a5b83f324427fa0b206a9d00174661419abf2185401022610`, private per-story `e51f9b840cd6d9b324257efdda56b781663d488cf47cfc92ced4101de93ebcf2`. Số liệu NLL và hai đối chứng được giữ nguyên byte trong public RESULT JSON cùng commit.

| Seed | tau_residual (nats/token) | gamma_real (nats/token) |
|---|---:|---:|
| S1 | 0.0175553509 | 0.0044749603 |
| S2 | 0.0154038430 | 0.0076739716 |
| S3 | 0.0000483432 | 0.0016843330 |

- **tau_residual (co-primary):** mean `0.011002512359983604`, paired story bootstrap 2000 draws CI95 `[0.008006140400569671, 0.014223537326267178]`.
- **gamma_real (co-primary):** mean `0.004611088298351975`, CI95 `[0.0026581794515664957, 0.006716623930602704]`.
- Cả ba seed đều dương đối với cả hai đối chứng. **S3** có `tau_residual=0.00004834318450962886` gần bằng không; kết quả có thể nhạy với training seed.

## Thẩm định thực tế đã làm, không huấn luyện hay model.forward lại

1. Đọc trực tiếp từ Google Drive ba file `STUDY_CLAIM.json`, `RESULT.json`, `PER_STORY_PRIVATE.json`, tự tính SHA toàn tệp **khớp chính xác**. Dữ liệu per-story giữ private, không commit.
2. Tự tính từ loss-sum của 768 truyện: **12 NLL và 12 contrasts** theo seed; cả hai trung bình và **2000** bootstrap draws (seed 2026111199) cho ra CI95 đúng chính xác trong `RESULT`.
3. Đã tải và băm SHA256 độc lập **cả 12 checkpoint cuối** `step_2048/checkpoint.pt` (~53MB/tệp) so với 12 READY tương ứng: **PASS 12/12**. Hash công khai trong file JSON biên bản.
4. Mỗi nhánh có đúng 8 thư mục `step_0256`... `step_2048`, và 8 marker `CHUNK_START` / `CHUNK_DONE`, tổng **96** mốc. Đã xác minh đủ 12 metadata READY cuối khớp RunID, source, schedule, env và step.
5. **Còn thiếu:** kiểm nội dung `READY.json` và SHA gắn trong `CHUNK_DONE` của toàn bộ 96 mốc bằng source frozen `ttm_semantic4x3_independent_readback.py` (SHA256 `51732bd62cfd13bf8956f11ee862b939d0dc78a62c58cd3d655dc05b566764e2`). Khi checker tạo `INDEPENDENT_READBACK_PUBLIC.json`, sẽ đọc lại receipt và phân xử chính thức PASS/FAIL. Không sửa gate, không mở science mới.

**Giới hạn kết luận:** H768 same-domain TinyStories-valid; donor pretraining overlap chưa xác minh; effect là phần cấu trúc ngoài Ridge khởi tạo, không phải pure pretrained semantics; CI story bootstrap conditional on 3 fixed adaptation seeds; không có multi-donor independent replication.

**Bước thực hiện tiếp theo:** `TTM_SEMANTIC4X3_FROZEN_INDEPENDENT_96_READY_READBACK_THEN_L0020_ADJUDICATION` (read-only đối với model/science; chỉ reviewer tạo 1 receipt mới, không gọi GPU).
