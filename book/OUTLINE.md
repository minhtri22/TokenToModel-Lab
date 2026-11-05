# Phác thảo sách — Tự xây GPT-like từ Attention đến Paged Inference

1. Vì sao mô hình ngôn ngữ dự đoán token tiếp theo?
2. Tokenizer và dữ liệu huấn luyện — chất lượng, pháp lý, rò rỉ dữ liệu.
3. Toán học cần thiết: vector, ma trận, softmax, đạo hàm.
4. Scaled Dot-Product Attention và causal mask.
5. Viết Multi-Head Self-Attention bằng PyTorch.
6. Decoder-only Transformer và dự đoán next token.
7. Loss, backpropagation, optimizer, learning-rate schedule.
8. Viết vòng huấn luyện, checkpoint và tái lập kết quả.
9. Đánh giá mô hình: perplexity và ngoài perplexity.
10. Đọc/ghi KV cache liên tục.
11. Quản lý bộ nhớ phân trang: block pool, block table.
12. Viết/so sánh PagedAttention kernel.
13. Suy luận nhiều yêu cầu, cấp phát, prefix sharing, copy-on-write.
14. CPU/GPU, precision, throughput, latency và benchmark công bằng.
15. Từ mô hình đồ chơi tới mô hình được đánh giá độc lập.
16. License, bảo mật, triển khai và các điều kiện thương mại hóa.

**Cấu trúc mỗi chương:** trực giác → toán học → mã nguồn → bài kiểm thử → bảng cấu hình → đối chứng trước/sau → sai lầm thường gặp → bài tập và giải thích.

Chỉ đưa số liệu vào sách sau khi run receipts, QA và source hashes được xác thực; chú thích rõ tính chất toy/research/production.
