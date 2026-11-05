# Hợp đồng so sánh cấu hình (Comparison Protocol)

## Ghi nhận mỗi cấu hình

`config_id`, `config_sha256`, `git_sha`, `dataset_sha256`, `tokenizer_sha256`, `split_id`, `seed`, `dtype`, `device`, `backend`, `torch_version`, `n_layers`, `n_heads`, `n_kv_heads`, `d_model`, `context_length`, `block_size`, `batching`, `optimizer`, `lr_schedule`, `train_tokens`, `checkpoint_sha256`.

Không phải mọi trường đều có mặt ở phase P00, nhưng những trường ảnh hưởng đến đối chứng phải được ghi hoặc ghi `not_applicable`.

## So sánh công bằng

- Chất lượng: cùng dữ liệu held-out và tiêu chí; nếu số train tokens/compute khác, báo cáo thêm chi phí/khối lượng học.
- Tốc độ: cùng model weights, số input/output tokens, batch/concurrency, dtype, thiết bị, driver, chế độ warmup, profiler và số lần đo.
- Sai số: ghi cả absolute error và relative error; quy định tolerance trước khi chạy.
- Tài nguyên: CPU/RAM/GPU memory peak, fragment slack, OOM, thời gian, điện năng nếu đo được.
- Không so sánh hai run khác workload bằng % cải thiện như thể cùng điều kiện.

## Chỉ tiêu

| Nhóm | Metrics | Ý nghĩa |
|---|---|---|
| Toán và correctness | max_abs_logit_error, grad_norm, causal_leak_count | Đúng chức năng |
| Learning | train_loss, val_loss, perplexity, tokens_seen | Học được gì |
| Suy luận | TTFT_ms, TPOT_ms, tokens_per_sec, p50_ms, p95_ms | Hiệu suất |
| Bộ nhớ | peak_RSS_MiB, peak_GPU_MiB, fragmentation_ratio | Hiệu suất cấp phát |
| An toàn vận hành | OOM_count, isolation_failures, crash_count | Tính bền vững |
| Chi phí | wall_time_s, train_kWh nếu đo trực tiếp, cost_per_1M_tokens | Khả năng mở rộng |

## Báo cáo bắt buộc sau phase

- Thay đổi + giả thuyết + baseline.
- Bảng cấu hình trước/sau.
- Bảng metric trước/sau với chênh lệch tuyệt đối và tương đối (nếu có ý nghĩa).
- QA verdict, mẫu và độ bất định, bằng chứng.
- Quyết định: KEEP / REJECT / RETEST và nguyên nhân.

Sử dụng `templates/PHASE_COMPARISON.md` và `scripts/compare_runs.py` để khởi tạo biên bản. Chênh lệch không tự suy ra nhân quả nếu các điều kiện không bằng nhau.
