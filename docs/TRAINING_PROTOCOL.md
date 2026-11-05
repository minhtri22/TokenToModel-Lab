# Quy trình huấn luyện end-to-end

## T0 — Smoke & overfit

- Dữ liệu đồ chơi (toy) ngắn, sinh hoặc có nguồn rõ ràng; tokenizer byte-level để kiểm thử.
- Phải overfit một mini-batch có chủ đích; kiểm tra loss và gradient hữu hạn.
- Seed + config + commit cố định. Mục tiêu là đúng đường học, không phải chất lượng ngôn ngữ.

## T1 — Corpus & tokenizer

- Thu thập hợp pháp, ghi nguồn/giấy phép, chuẩn hóa unicode, loại trùng, kiểm tra chất lượng và PII.
- Split train/validation/test độc lập; kiểm tra leakage/dedup xuyên các split.
- Huấn luyện tokenizer, khóa vocabulary, normalizer và special tokens, hash artifact.

## T2 — Baseline training

- Định nghĩa config (layer, dimension, heads, context, precision, optimizer, LR schedule, batch, grad accumulation, tokens budget).
- Gradient clipping, checkpoint, log loss/grad norms, validation định kỳ.
- Atomic checkpoint và resume parity; nếu thay đổi batch/resume cần phân loại thay đổi chế độ thí nghiệm.

## T3 — Scaling & ablations

- Thử kích thước mô hình, context, attention variant, RoPE, GQA ở từng nhánh riêng.
- Thực hiện A/B trên cùng dữ liệu và ngân sách so sánh được; ghi throughput và tổng chi phí.
- Đánh giá chất lượng, không chỉ training loss.

## T4 — Post-training

- Nếu mục tiêu là trợ lý hội thoại: instruction tuning/SFT hoặc alignment theo mục tiêu sử dụng.
- Cần dữ liệu phù hợp, kiểm thử hành vi, safety/security và kiểm tra regressions.

## T5 — Model release

- Model card, dataset card, weight license, inference test, evaluation report, reproducibility recipe.
- Chỉ sử dụng tên "commercial-ready" sau khi qua kiểm tra license/privacy/security và chất lượng trên dữ liệu phù hợp mục đích.

**Cổng tuyệt đối:** không dùng TEST để điều chỉnh hyperparameter; không tái dùng seed "một lần" nếu đã khóa theo giao thức; giữ cả thất bại.
