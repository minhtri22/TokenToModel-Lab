# Kiểm tra mức sẵn sàng thương mại (Commercial Readiness)

Không mặc định một mô hình tự huấn luyện là có thể khai thác thương mại.

| Hạng mục | Bằng chứng tối thiểu | Trạng thái ban đầu |
|---|---|---|
| License mã nguồn/phụ thuộc | SBOM, license audit | NOT_ASSESSED |
| Quyền sử dụng dữ liệu | Provenance, license, consent khi cần | NOT_ASSESSED |
| Quyền phát hành trọng số | Nguồn weights, dependency restrictions | NOT_ASSESSED |
| Chất lượng theo use case | Held-out benchmark + acceptance | NOT_ASSESSED |
| Bảo mật hệ thống | Authentication, rate limiting, prompt risks, audit | NOT_ASSESSED |
| Quyền riêng tư | PII workflow, retention, deletion | NOT_ASSESSED |
| Hiệu năng và chi phí | TTFT, TPOT, concurrency, total cost | NOT_ASSESSED |
| Khả năng bảo trì | Reproducible build, rollback, monitoring | NOT_ASSESSED |
| Tuân thủ thị trường mục tiêu | Rà soát luật/tiêu chuẩn hiện hành theo sản phẩm | NOT_ASSESSED |

Mục đích của bảng này là xác định khoảng trống cần giải quyết, không tạo chứng nhận thương mại.
