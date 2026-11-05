# Lộ trình phát triển có cổng (Phase Plan)

| Phase | Nhánh dự kiến | Phạm vi và chứng cứ | Điều kiện đóng phase |
|---|---|---|---|
| P00 | `feature/p00-baseline-qa` | Khóa nguồn tham chiếu, môi trường, smoke test, test hiện có | Static + CPU baseline QA PASS, receipt và quyết định phạm vi |
| P01 | `feature/p01-tokenizer-data` | Tokenizer, corpus pipeline, dedup, train/val/test, provenance | Round-trip, leakage, hash tập dữ liệu, QA PASS |
| P02 | `feature/p02-transformer-core` | Embedding, LayerNorm/RMSNorm, masked attention, MLP, residual | Shape, gradcheck/gradient, causal invariance, parity với reference |
| P03 | `feature/p03-train-loop` | Loss, optimizer, scheduler, mixed precision theo điều kiện | Overfit micro-batch, loss finite, resume parity, QA |
| P04 | `feature/p04-eval-checkpoints` | Checkpoint, sampling, perplexity, đánh giá held-out | Tái hiện kết quả, khóa tập đánh giá, QA |
| P05 | `feature/p05-dense-kv-cache` | Suy luận từng token với cache liên tục | So sánh logits với không cache, đo tốc độ/bộ nhớ |
| P06 | `feature/p06-paged-kv-manager` | Block pool, table, free, isolation, OOM, no-leak | Parity dense KV, phân mảnh, tests multi-request |
| P07 | `feature/p07-paged-kernel` | Kernel đọc block table trực tiếp, không gather toàn cache | Parity số học, microbenchmark cùng workload, QA |
| P08 | `feature/p08-batching-gpu` | Multi-request scheduler, prefill/decode, backend GPU | TTFT/TPOT/tokens/s, p50/p95, memory, lỗi biên |
| P09 | `feature/p09-model-scale` | Huấn luyện corpus lớn hơn, scaling/model variants | Đường học, benchmark held-out, seeds, chi phí, QA |
| P10 | `feature/p10-post-training` | Tinh chỉnh có giám sát nếu phù hợp, instruction following | Data provenance, baseline quality, regression/safety, QA |
| P11 | `feature/p11-serving-eval` | API, model card, behavior/safety/security | Tests tải, độ ổn định, privacy, model card, QA |
| P12 | `feature/p12-release-docs` | Tài liệu, reproducibility package, sách, release checklist | Rebuild clean-room, độc lập tái hiện, duyệt license |

**Quy tắc:** Mỗi phase có thể có nhiều nhánh nhỏ; mỗi phát triển/thay đổi là một nhánh. Có thể thiết kế phase trước nhưng không tuyên bố phase đã PASS khi chưa có QA và dữ liệu thật.

**Mốc đối chứng:** P05 so với suy luận không cache; P06 so với P05; P07 so với P06; P08 so với P07. P09/P10 so sánh chất lượng trên cùng bộ held-out trước/sau cùng giao thức.

**Ưu tiên thời gian đầu:** P00 → P01 → P02 → P03 → P04 → P05 → P06. Không vội xây kernel GPU trước khi parity đúng.
