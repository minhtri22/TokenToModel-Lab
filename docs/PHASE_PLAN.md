# Lộ trình phát triển có cổng kiểm định (Phase Plan)

Mỗi giai đoạn (Phase) có thể gồm nhiều nhánh nhỏ, nhưng **mỗi thay đổi phải đi qua nhánh riêng, kiểm thử riêng và xem xét hợp nhất riêng**. Mỗi kết luận phải có cấu hình, mã nguồn, dữ liệu và nhật ký có thể truy xuất.

| Giai đoạn | Nhánh dự kiến | Mục đích | Điều kiện đóng giai đoạn |
|---|---|---|---|
| P00 | `feature/p00-source-docs-diagrams-20261105` | Thiết lập mã tham chiếu CPU và bộ nhớ KV phân trang | 13/13 QA cục bộ, 6/6 QA độc lập, thẩm định phạm vi; đã merge PR #1 |
| P01 | `feature/p01-tokenizer-data` | Bộ tách token (Tokenizer), dữ liệu, nguồn và giấy phép | Đối chiếu mã hóa–giải mã (Round-trip), kiểm tra rò rỉ dữ liệu (Leakage), SHA-256 và QA |
| P02 | `feature/p02-transformer-core` | Embedding, chuẩn hóa (LayerNorm/RMSNorm), chú ý có mặt nạ, mạng truyền thẳng (MLP) | Kiểm tra kích thước, gradient, nhân quả và đối chiếu mã tham chiếu |
| P03 | `feature/p03-train-loop` | Vòng huấn luyện (Training Loop), hàm mất mát, tối ưu hóa (Optimizer), lịch học (Scheduler) | Học khớp bộ dữ liệu rất nhỏ (Micro-batch Overfit), gradient hữu hạn, QA |
| P04 | `feature/p04-eval-checkpoints` | Điểm lưu mô hình (Checkpoint), sinh mẫu (Sampling), đánh giá độc lập | Tái lập được, kiểm tra dữ liệu giữ riêng (Held-out), QA |
| P05 | `feature/p05-dense-kv-cache` | Bộ nhớ KV liên tục (Dense KV Cache) | Đối chiếu logits với đường không cache; đo thời gian/bộ nhớ |
| P06 | `feature/p06-paged-kv-manager` | Kho khối (Block Pool), bảng trang (Block Table), cách ly yêu cầu | Đối chiếu P05, đo phân mảnh và nhiều yêu cầu |
| P07 | `feature/p07-paged-kernel` | Nhân tính toán đọc trang KV trực tiếp trên GPU (PagedAttention Kernel) | Đối chiếu số học và đo hiệu năng với tải giống nhau |
| P08 | `feature/p08-batching-gpu` | Lập lịch nhiều yêu cầu (Batching Scheduler), xử lý tiền tố/sinh token (Prefill/Decode), GPU | Thời gian token đầu (TTFT), thời gian token tiếp (TPOT), thông lượng và bộ nhớ |
| P09 | `feature/p09-model-scale` | Huấn luyện mô hình lớn hơn (Scaling) | Đường học, nhiều seed, đánh giá dữ liệu giữ riêng và chi phí |
| P10 | `feature/p10-post-training` | Tinh chỉnh sau huấn luyện (Post-training), làm theo hướng dẫn (Instruction Following) | Nguồn dữ liệu, an toàn, chất lượng và hồi quy |
| P11 | `feature/p11-serving-eval` | Giao diện phục vụ (Serving API), thẻ mô hình (Model Card), vận hành | Kiểm thử tải, độ ổn định, quyền riêng tư, bảo mật |
| P12 | `feature/p12-release-docs` | Đóng gói tái lập (Reproducibility Package), tài liệu và sách | Tái dựng độc lập, rà soát giấy phép và phát hành |

**Các cổng phụ thuộc:** P05 phải đo với đường không cache, P06 phải đo với P05, P07 với P06, P08 với P07 trên điều kiện ngang bằng. P09/P10 so sánh chất lượng trên dữ liệu kiểm định giữ riêng (Held-out Dataset), không dựa duy nhất vào độ giảm mất mát huấn luyện.

**Tình trạng sau đồng bộ:** P00 có mốc GitHub đã hợp nhất và local `main` đã đồng bộ tới đúng commit P00, theo biên bản `docs/qa/P00_LOCAL_FAST_FORWARD_ADJUDICATION_20261105.md`. Công việc rà soát tài liệu PR #2 là quyết định riêng; chưa mở P01 cho đến khi kiểm toán sau hợp nhất tài liệu và cổng P01 được chấp thuận. Cấu hình P00 làm đối chứng kỹ thuật theo mã băm (hash), không phải khóa thí nghiệm khoa học.
