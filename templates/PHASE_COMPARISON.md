# Biên bản so sánh giai đoạn (Phase Comparison) <PXX>

- Ứng viên (Candidate): <nhánh> / <commit> / <config_id> / <run_id>.
- Mốc đối chứng (Baseline): <main_sha> / <config_id> / <run_id>.
- Giả thuyết, lý do cần so sánh và điều kiện chấp nhận:
- Tải và dữ liệu tương đương (Workload Parity): đạt / không đạt / chưa chứng minh; giải thích:
- Môi trường, thiết bị, thư viện, dữ liệu và SHA-256:

| Phép đo (Metric) | Đơn vị | Đo điều gì? | Ngưỡng đạt | Giá trị đối chứng | Giá trị ứng viên | Sai khác (Delta) | Ý nghĩa và giới hạn |
|---|---|---|---:|---:|---:|---:|---|
| <tên phép đo> | | | | | | | |

- Số lượt lặp, biến thiên, khoảng bất định và sai số:
- Kiểm thử độc lập (Independent QA):
- Trường hợp lỗi (Negative Tests) và dữ liệu không đạt:
- Quyết định: giữ (KEEP) / loại bỏ (REJECT) / thử lại (RETEST).
- SHA-256, mã lượt chạy và vị trí bằng chứng:
- Quyền hợp nhất (Merge Authorization): có / không và lý do:
