# Experiment log

- Mỗi run: một receipt JSON bất biến dưới `runs/<run_id>.json`.
- Dùng `python scripts/record_run.py <receipt.json>` để đăng ký; chương trình từ chối ghi đè run ID, kiểm SHA256 cấu hình.
- `registry.jsonl` là index append-only. Bằng chứng thực nghiệm là receipt và raw logs có hash, không phải chỉ là bản ghi index.
- Báo cáo đối chứng tạo bằng `python scripts/compare_runs.py <base_id> <candidate_id>`.
- Mọi chênh lệch chỉ có thể được diễn giải là lợi ích khi workload/parity thực sự phù hợp.
- Log nặng, datasets, checkpoint lưu ngoài Git với đường dẫn và SHA256.
