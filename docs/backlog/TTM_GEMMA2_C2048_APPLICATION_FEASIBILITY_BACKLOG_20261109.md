# Backlog — TTM-Small-4M EmbeddingGemma 2 C2048 ứng dụng thực tế (DEFERRED)

**Ghi nhận 09/11/2026 theo yêu cầu chủ dự án.** Trạng thái: `BACKLOG_ONLY_NOT_AUTHORIZED_TO_EXECUTE`. Không bắt đầu công việc khi nghiên cứu cơ chế B/G/R đang được ưu tiên.

Khi chủ dự án quyết định mở hướng ứng dụng, đánh giá bằng **checkpoint C sau 2.048 bước đã có** (kết quả L0017) theo các mục công việc:

1. Đánh giá mẫu sinh văn bản (text generation) trên prompt đã tiền đăng ký; đo chất lượng bằng rubric, so sánh với TTM nguyên bản và đối chứng, tách biệt dữ liệu đã dùng.
2. Đo RAM, thời gian khởi tạo, tốc độ token/s và độ trễ suy luận CPU trên cấu hình máy được xác minh; báo cáo peak working set, phiên bản torch và số luồng.
3. Xác minh cách chuyển/fold input token mapping và ridge projection nếu hợp lệ, và kiểm tra tính nhất quán logits trước/sau chuyển; không mặc định donor encoder cần tham gia runtime.
4. Kiểm tra chuyển đổi checkpoint C sang định dạng phục vụ suy luận, gồm GGUF và tương thích với `llama.cpp`/Ollama; **output head untied** là điều kiện kỹ thuật chưa được chứng minh tương thích.
5. Báo cáo trade-off hiệu quả/chi phí và giới hạn sản phẩm, **không biến chứng cứ NLL L0017 thành tuyên bố chất lượng sản phẩm**.

**Không tự mở:** GGUF conversion, Ollama smoke, benchmark RAM/CPU, sản phẩm hoặc deploy. Không thay đổi ưu tiên nghiên cứu cơ chế hiện tại, không chạy lại 320-story holdout.