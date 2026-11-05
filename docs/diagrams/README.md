# P00 — Hướng dẫn đọc các sơ đồ kỹ thuật

Bộ sơ đồ mô tả **mã tham chiếu P00 đã được kiểm thử trên CPU**, không phải kết quả đánh giá hiệu năng mô hình đã huấn luyện.

| Tệp | Nội dung và cách đọc |
|---|---|
| `01_gpt_like_architecture.svg` / `.png` | Kiến trúc: token đầu vào, vector biểu diễn (Embedding), 2 khối Transformer, cơ chế chú ý có mặt nạ nhân quả (Causal Attention) và điểm dự đoán (logits) đầu ra |
| `02_executed_inference_flow.svg` / `.png` | Luồng suy luận: tính lại toàn chuỗi (dense), dùng KV phân trang (paged), đối chiếu kết quả số học và sinh token tiếp theo (autoregressive decoding) |
| `03_kv_cache_mechanics.svg` / `.png` | Ánh xạ trang logic sang trang vật lý qua bảng khối (block table), cấp phát/ghi/đọc/giải phóng bộ nhớ KV |

Bản SVG là sơ đồ gốc có thể chỉnh sửa; PNG là bản xuất ảnh để xem thuận tiện. Sơ đồ không thay cho biên bản thử nghiệm hoặc nhật ký chạy.

**Giới hạn quan trọng:** P00 chưa có nhân GPU đọc trực tiếp bộ nhớ phân trang (PagedAttention GPU kernel) và chưa đo tốc độ so với bộ nhớ KV liên tục. Khi đưa hình vào sách, phải đối chiếu với `reference/phase0/` và chú thích các thành phần **chưa triển khai**.

Số liệu định lượng và phạm vi kết luận đã được lưu trong `docs/qa/P00_FORMAL_ADJUDICATION_20261105.md` và được giải thích bằng tiếng Việt tại `docs/qa/P00_POST_MERGE_AUDIT_20261105.md`.
