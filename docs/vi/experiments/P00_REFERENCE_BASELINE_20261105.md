# P00 — Báo cáo thiết lập mốc đối chứng kỹ thuật (Engineering Baseline) và sự khác biệt môi trường

> Bản tiếng Việt của [báo cáo gốc](../../../experiments/comparisons/P00_REFERENCE_BASELINE_20261105.md); số đo và phán quyết nguyên bản được giữ nguyên.

- **Mã phép so sánh (Comparison ID):** `TTM_P00_REFERENCE_BASELINE_COMPARISON_20261105`.
- **Kết luận:** `NO PERFORMANCE COMPARISON / BASELINE ESTABLISHMENT ONLY` — **chỉ thiết lập mốc đối chứng, không có so sánh hiệu năng hợp lệ**.
- **SHA-256 cấu hình (Configuration):** `ffcd83863fb9c2a8959fbaaa52ccdb7bf2977d68ea6aa869880015dc0daebcbd`.
- **SHA-256 mô hình trên Windows:** `821e60a6c97536bf3a251602b31dcc6b55f1c81836cffa5223ec2f063ae578ea`.

| Thuộc tính | Môi trường Linux tham chiếu (Reference) | QA cục bộ Windows | QA độc lập Windows |
|---|---|---|---|
| Biên bản nguồn | `TTM_P00_CONTAINER_REFERENCE_20261105_01` | `TTM_P00_WINDOWS_LOCAL_QA_20261105T043050Z` | `TTM_P00_INDEPENDENT_QA_20261105T051340397776Z` |
| Môi trường | Linux CPU | Windows 11 CPU | Windows 11 CPU |
| Python | 3.13.5 | Miniforge3 3.13.12 | 3.13.12 |
| PyTorch | `2.10.0+cpu` | Không ghi trong biên bản QA cục bộ | `2.12.0+cpu` |
| Bộ kiểm thử | 5 phép thử mô hình + 3 kiểm thử sổ đăng ký (Registry) | 5 mô hình + 8 sổ đăng ký/PowerShell 5.1 | 6 phép kiểm độc lập |
| Kết quả | **8/8 PASS** | **13/13 PASS** | **6/6 PASS** |
| Mục đích | Kiểm tra nhanh tham chiếu (Reference Smoke) | QA trên máy đích | Bổ sung xác minh độc lập |
| So sánh trực tiếp tốc độ | Không hợp lệ | Không hợp lệ | Không hợp lệ |

**Các phép đo QA độc lập:** sai lệch lớn nhất của điểm dự đoán (Logit Parity) `2.384185791015625e-07`; sai lệch tiền tố nhân quả (Causal Prefix) tối đa `0`; hàm mất mát gradient dự đoán token tiếp theo (Next-token Gradient Loss) `5.489449977874756`.

Không có đối chứng thực nghiệm tiền nhiệm về chất lượng, độ trễ (Latency), thông lượng (Throughput), độ phân mảnh bộ nhớ (Memory Fragmentation) hoặc huấn luyện (Training). Trạng thái `BASELINE_NO_PREDECESSOR` nghĩa là **chưa có mốc tiền nhiệm để so cải thiện**, do đó không tính phần trăm tăng tốc. Các phép đo P05–P08 chỉ có thể so sánh khi tải công việc (Workload), trọng số mô hình (Model Weights), thiết bị và kiểu số (Dtype) ngang bằng theo `docs/COMPARISON_PROTOCOL.md`.

**Quyết định (Decision):** giữ mốc đúng chức năng (Correctness Reference); tốc độ cải thiện (Speedup), chất lượng ngôn ngữ sau huấn luyện, mức sẵn sàng GPU và khả năng thương mại hóa đều **chưa được chứng minh (NOT_ESTABLISHED)**.
