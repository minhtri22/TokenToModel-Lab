# TTM-Small-4M × EmbeddingGemma 2 — Đóng gói kiểm toán VALIDATION-only 320×256, phán quyết GO

**Ngày:** 09/11/2026. **Nhánh:** `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`. **Mã công việc:** `TTM_SMALL4M_EMBEDDINGGEMMA2_VALIDATION_ONLY_NEAR_DUPLICATE_AUDIT_AND_FINAL_GO_DECISION`.

## Bằng chứng chạy thật trên Windows

Chủ dự án chạy bộ kiểm toán Python 3.12, mã SHA-256 `80361cdfa16dd6c37ced6809adbbbd2ea778f9ef9ba7ebc578a7a9d9f7ed1f85` (source ZIP SHA-256 `25a420162996de36588d2bf0b77c5d20205e05e746364cd4fd989464cb062677`). Trước khi kiểm toán, 24/24 phép thử giả lập PASS. Biên bản đầu ra là `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_gemma2_validation_only_near_audit_20261109\VALIDATION_ONLY_NEAR_AUDIT_PUBLIC_RECEIPT.json`. Owner kiểm tra SHA-256 của chính biên bản trên Windows: `aa03c08b58aee49b46b049bceee8d735731235e19e3fed3a9725622b5d5dfdc8`.

Một lượt đọc lại từ xa tệp receipt công khai này cho kết quả khớp số liệu owner:
- **320** truyện mới với **75.798** nhãn mục tiêu, **405** cửa sổ; kiểm tra liên kết nội dung và cửa sổ trả `PASS_REAL_DATA_TOKEN_AND_WINDOW_BINDING`.
- **256** truyện VALIDATION lịch sử, `320 × 256 = 81.920` cặp đã đối chiếu theo Jaccard tập 5-word shingle với ngưỡng **0,85**.
- **0** cặp đạt ngưỡng gần trùng, **0** truyện mới bị ảnh hưởng, **0** VALIDATION cũ bị ảnh hưởng; độ tương đồng lớn nhất **0,078947368421**.
- Niêm phong manifest private SHA-256 `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`; BPE SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Không dùng GPU, không huấn luyện, không nạp checkpoint, không gọi `model.forward`, không tính NLL và không chấm 320 truyện trong thao tác kiểm toán.

## Đóng cổng chuẩn bị

**`GO_SCOPED_CPU_ONE_SHOT_READY_SEPARATE_EXECUTION`**, theo chính quyết định trong biên bản chạy thật. Đóng chuỗi QA chuẩn bị; không phát sinh thêm một cổng kỹ thuật để cho phép kiểm định mô hình.

**Phạm vi giới hạn đã công khai:** L0012 đã từng chấm 64 truyện TEST lịch sử một lần bằng mô hình gốc. Trong lượt kiểm toán này không mở hoặc giải mã văn bản TEST, nên **không chứng minh hết trùng gần đúng** với 64 truyện đó. Chưa xác minh lịch tiền huấn luyện của donor EmbeddingGemma 2. Phép thử xác nhận chỉ dành cho bốn checkpoint A/B/C/D bước 2.048 **đã chọn cố định**, không phải huấn luyện lại seed khác hoặc kiểm định cơ chế nhân quả của donor.

## Thử nghiệm khoa học sắp tới — tác vụ tách biệt

Một lượt CPU one-shot duy nhất chấm **đúng 320 truyện và 75.798 nhãn** cho A/B/C/D, trên 405 cửa sổ đã khóa. Trước **lần gọi forward đầu tiên** đối chiếu đầy đủ manifest, dữ liệu, tokenizer, ranh giới/cửa sổ, checkpoint và mã scorer đã ghim. Chỉ dùng read-only checkpoints, `eval()`, `inference_mode()`, không optimizer, không GPU, không đổi nguồn, không chọn lại checkpoint. Có `CLAIM` bền vững ghi **trước bất kỳ phép chấm nào**, không phát lại cùng one-shot nếu bị ngắt, và biên bản `RESULT` + QA độc lập trước khi cập nhật `lineage.md` append-only.

Chỉ số chính: NLL token-weighted; đối chứng **A−C, B−C, D−C**; bootstrap ghép theo truyện **2.000 lượt**, seed **2026110901**, CI phân vị hai phía 95%; PASS khoa học chỉ nếu **cả ba cận dưới đều >0**, FAIL khoa học khi tiền kiểm hợp lệ nhưng có ít nhất một cận dưới không dương. Kết quả khoa học này **chưa được thực thi** ở thời điểm biên bản.

**Quản trị:** không sửa `main`, TEST cũ hay `lineage.md`, không công bố ID riêng tư, văn bản truyện, token arrays, per-story loss, checkpoint hoặc logits. Source Python được phân phối bằng ZIP đã băm cho chủ dự án; commit này ghi chứng cứ và phán quyết, không giả nhận mã nguồn Python nằm trong GitHub.
