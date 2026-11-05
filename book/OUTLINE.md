# Phác thảo sách — Xây dựng mô hình ngôn ngữ từ token đến suy luận phân trang

1. Vì sao mô hình ngôn ngữ dự đoán token tiếp theo?
2. Bộ tách token (Tokenizer) và dữ liệu huấn luyện: chất lượng, pháp lý, rò rỉ.
3. Toán học cần thiết: vector, ma trận, hàm chuẩn hóa xác suất (Softmax), đạo hàm.
4. Cơ chế chú ý tích vô hướng có tỷ lệ (Scaled Dot-Product Attention) và mặt nạ nhân quả (Causal Mask).
5. Tự viết cơ chế tự chú ý nhiều đầu (Multi-Head Self-Attention) bằng PyTorch.
6. Transformer chỉ có bộ giải mã (Decoder-only Transformer) và dự đoán token tiếp theo (Next-token Prediction).
7. Hàm mất mát (Loss), lan truyền ngược (Backpropagation), bộ tối ưu (Optimizer), lịch tốc độ học (Learning Rate Schedule).
8. Vòng huấn luyện (Training Loop), điểm lưu (Checkpoint) và tái lập kết quả.
9. Đánh giá mô hình: độ bối rối (Perplexity) và các phép đo khác.
10. Bộ nhớ Key/Value liên tục (Dense KV Cache).
11. Quản lý bộ nhớ phân trang: kho khối (Block Pool) và bảng khối (Block Table).
12. Viết và so sánh nhân tính toán chú ý phân trang (PagedAttention Kernel).
13. Suy luận nhiều yêu cầu, chia sẻ tiền tố (Prefix Sharing), sao chép khi ghi (Copy-on-write).
14. CPU/GPU, độ chính xác số (Precision), thông lượng (Throughput), độ trễ (Latency) và đo công bằng (Benchmarking).
15. Từ mô hình thử nhỏ đến mô hình được đánh giá độc lập.
16. Quyền sử dụng (Licensing), bảo mật (Security), triển khai (Deployment) và điều kiện thương mại hóa.

**Cấu trúc mỗi chương:** giải thích trực giác → toán học → mã nguồn → bài kiểm thử → bảng cấu hình → đối chứng trước/sau → lỗi đã gặp → bài tập và giải thích.

Chỉ đưa số liệu vào sách sau khi biên bản lần chạy (Run Receipt), kiểm thử độc lập và mã SHA-256 của nguồn được xác minh. Phải chú thích rõ thử nghiệm minh họa (Toy), nghiên cứu (Research) hay sản phẩm triển khai (Production).
