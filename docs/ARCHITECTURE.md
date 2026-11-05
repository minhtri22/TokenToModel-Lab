# Kiến trúc hệ thống TokenToModel-Lab

## Chu trình từ dữ liệu đến mô hình

```text
Văn bản có nguồn gốc và quyền sử dụng được kiểm tra
        ↓
Chuẩn bị tập dữ liệu (Dataset Preparation)
        ↓
Bộ tách token (Tokenizer) → Mã token (Token IDs)
        ↓
Transformer chỉ có bộ giải mã (Decoder-only Transformer)
  ├─ Biểu diễn token/vị trí (Embeddings)
  ├─ Cơ chế chú ý có mặt nạ nhân quả (Causal Attention)
  ├─ Mạng truyền thẳng (MLP)
  ├─ Chuẩn hóa (Normalization)
  └─ Đầu dự đoán token (Language Model Head)
        ↓
Huấn luyện / Kiểm định / Điểm lưu (Training / Validation / Checkpoint)
        ↓
Bộ máy suy luận (Inference Engine)
  ├─ Đường tham chiếu không dùng cache (No-cache Reference)
  ├─ Bộ nhớ KV liên tục (Dense KV Cache) — dự kiến P05
  └─ Bộ nhớ KV phân trang (Paged KV Cache)
       ├─ Kho trang (Block Pool)
       ├─ Bảng ánh xạ trang (Block Table)
       ├─ Cấp phát / Giải phóng (Allocation / Release)
       ├─ Chú ý có độ lệch vị trí (Offset-aware Attention) — sau P00
       └─ Nhân tính toán GPU theo trang (Paged GPU Kernel) — dự kiến P07
```

## Thành phần đã chạy tại P00

P00 cung cấp mô hình GPT-like nhỏ với 2 lớp Transformer, 4 đầu chú ý (Attention Heads), kích thước biểu diễn 64 chiều, bộ từ vựng theo byte 256 giá trị và trang KV chứa 4 token. Mã nguồn là `reference/phase0/model.py` và `reference/phase0/paged_kv.py`.

Bộ nhớ KV phân trang là cơ chế quản lý bộ nhớ **khi suy luận**, không thay thế phép toán Attention và không tự động biến quá trình huấn luyện thành huấn luyện phân trang. Đường P00 đọc/gom K/V vào tensor PyTorch liên tục trước khi tính chú ý.

## Bất biến và biên giới khẳng định

- Không xem trước token tương lai (causal isolation).
- Kết quả đường thường và đường phân trang gần bằng nhau (numerical parity).
- Không lẫn dữ liệu giữa các yêu cầu (request isolation).
- Cấp phát, giải phóng và hết chỗ lưu có hành vi xác định (allocation, release, OOM).

Các khẳng định này chỉ áp dụng cho phạm vi fixture CPU đã được kiểm thử. Chưa kết luận tăng tốc GPU, khả năng phục vụ đồng thời trong thực tế, hay chất lượng ngôn ngữ sau huấn luyện.

Đọc kết quả và giới hạn ở `docs/qa/P00_FORMAL_ADJUDICATION_20261105.md`, xem cách đo tại `docs/COMPARISON_PROTOCOL.md`.
