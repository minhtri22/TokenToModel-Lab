# P00 — Báo cáo đối chứng baseline và khác biệt môi trường

- Comparison ID: `TTM_P00_REFERENCE_BASELINE_COMPARISON_20261105`.
- Kết luận: **NO PERFORMANCE COMPARISON / BASELINE ESTABLISHMENT ONLY**.
- Config SHA-256 chung: `ffcd83863fb9c2a8959fbaaa52ccdb7bf2977d68ea6aa869880015dc0daebcbd`.
- Model SHA-256 Windows: `821e60a6c97536bf3a251602b31dcc6b55f1c81836cffa5223ec2f063ae578ea`.

| Thuộc tính | Reference Linux (trước) | Local QA Windows | Independent QA Windows |
|---|---|---|---|
| Nguồn | `TTM_P00_CONTAINER_REFERENCE_20261105_01` | `TTM_P00_WINDOWS_LOCAL_QA_20261105T043050Z` | `TTM_P00_INDEPENDENT_QA_20261105T051340397776Z` |
| Môi trường | Linux CPU | Windows 11 CPU | Windows 11 CPU |
| Python | 3.13.5 | Miniforge3 3.13.12 | 3.13.12 |
| PyTorch | 2.10.0+cpu | không ghi trong local QA receipt | 2.12.0+cpu |
| Bộ thử | 5 model + 3 registry | 5 model + 8 registry/PS51 | 6 independent |
| Kết quả | 8/8 PASS | 13/13 PASS | 6/6 PASS |
| Mục đích | Reference smoke | QA trên máy đích | Bổ sung kiểm chứng độc lập |
| So sánh trực tiếp tốc độ | Không hợp lệ | Không hợp lệ | Không hợp lệ |

**Các phép đo của independent QA:** logit parity max abs `2.384185791015625e-07`, causal prefix max abs `0`, next-token gradient loss `5.489449977874756`.

Không có baseline thực nghiệm tiền nhiệm về chất lượng, latency, throughput, fragment memory hay training. Đây là **BASELINE_NO_PREDECESSOR**, nên không tính phần trăm cải thiện. Các kết quả benchmark trong P05–P08 phải có workload, model weights, thiết bị và dtype so sánh ngang bằng theo `docs/COMPARISON_PROTOCOL.md`.

**Decision:** KEEP correctness reference; NOT_ESTABLISHED for speedup, trained language quality, GPU readiness or commercialization.
