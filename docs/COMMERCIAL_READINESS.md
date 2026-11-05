# Đánh giá điều kiện thương mại hóa (Commercial Readiness)

Một mô hình tự viết và vượt kiểm thử kỹ thuật **không mặc nhiên** đủ chất lượng, đủ quyền sử dụng hoặc đủ an toàn để kinh doanh.

| Hạng mục | Bằng chứng cần có | Trạng thái sau P00 |
|---|---|---|
| Giấy phép mã nguồn (Source License) | Danh mục thành phần phần mềm (SBOM), rà soát giấy phép | Chưa đánh giá |
| Quyền sử dụng dữ liệu (Data Rights) | Nguồn dữ liệu, giấy phép, chấp thuận khi cần | Chưa đánh giá |
| Quyền phát hành trọng số (Weight License) | Nguồn trọng số, ràng buộc phụ thuộc và phân phối | Chưa đánh giá |
| Chất lượng theo mục đích (Use-case Quality) | Đối chứng trên tập dữ liệu giữ riêng (Held-out Benchmark), tiêu chí chấp nhận | Chưa đánh giá |
| Bảo mật hệ thống (Security) | Xác thực (Authentication), giới hạn tốc độ (Rate Limiting), kiểm tra rủi ro câu lệnh (Prompt Risks) | Chưa đánh giá |
| Quyền riêng tư (Privacy) | Quy trình xử lý thông tin cá nhân (PII), lưu giữ và xóa dữ liệu | Chưa đánh giá |
| Hiệu năng và chi phí (Performance/Cost) | Thời gian token đầu (TTFT), mỗi token tiếp theo (TPOT), nhiều yêu cầu đồng thời, chi phí | Chưa đánh giá |
| Vận hành (Operations) | Khả năng tái dựng (Reproducible Build), quay lui (Rollback), giám sát (Monitoring) | Chưa đánh giá |
| Tuân thủ thị trường (Compliance) | Rà soát quy định phù hợp sản phẩm và khu vực triển khai | Chưa đánh giá |

P00 chỉ đã kiểm định **tính đúng chức năng tham chiếu CPU**. Không đánh dấu mục nào trong bảng là đạt nhờ kết quả 19/19 bài QA. Bảng này là danh mục điều kiện cần khảo sát ở các giai đoạn sau, không phải chứng nhận thương mại.
