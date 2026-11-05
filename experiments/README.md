# Nhật ký thí nghiệm và phép đo (Experiment Log)

Mỗi lần chạy có một mã riêng (Run ID) và một biên bản bất biến (Run Receipt) ở `runs/<run_id>.json`.

- Đăng ký biên bản bằng `python scripts/record_run.py <receipt.json>`; chương trình kiểm tra SHA-256 cấu hình và từ chối ghi đè mã lượt chạy.
- `registry.jsonl` là sổ đăng ký chỉ ghi bổ sung (Append-only Registry). Bằng chứng chính là biên bản và nhật ký thô có mã băm, không chỉ là dòng mục lục.
- Báo cáo so sánh được tạo từ `python scripts/compare_runs.py <base_id> <candidate_id>`.
- Chỉ diễn giải cải thiện nếu hai lượt chạy có tải ngang bằng (Workload Parity), cùng nguồn dữ liệu và tiêu chí phù hợp.
- Nhật ký lớn, tập dữ liệu và điểm lưu mô hình (Checkpoint) ở ngoài Git nhưng **bên trong** workplace dự án, có đường dẫn cùng SHA-256.
- Giữ kết quả đạt (PASS), không đạt (FAIL) và chưa đủ kết luận (Inconclusive); không đổi dữ liệu lịch sử.

**Lưu ý P00:** các lần chạy ban đầu chỉ chứng minh tính đúng của bộ mã trên CPU. Không có phép so sánh tốc độ phù hợp hoặc kết quả huấn luyện khoa học. Xem `experiments/comparisons/P00_REFERENCE_BASELINE_20261105.md` và `docs/COMPARISON_PROTOCOL.md`.
