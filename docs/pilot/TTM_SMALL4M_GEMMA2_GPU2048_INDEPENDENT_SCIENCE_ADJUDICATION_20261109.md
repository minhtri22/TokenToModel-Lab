# TTM-Small-4M × EmbeddingGemma 2 — Thẩm định khoa học sau 2.048 bước

**Ngày:** 09/11/2026. **Nhánh nghiên cứu:** `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`. **Lượt chạy:** `ttm_small4m_gemma2_directswap_2048x4096_t4_gpu_20261109_v1`.

## Kết luận

**`PASS_EXPLORATORY_VAL_SIGNAL_ONLY`**: trên tập kiểm định (validation), cấu hình C có hao hụt log-likelihood âm (negative log-likelihood, NLL) thấp hơn A, B và D sau 2.048 bước; cả ba khoảng tin cậy 95% của chênh lệch A−C, B−C, D−C có cận dưới dương. **`CONFIRMATORY_NOT_ESTABLISHED`**: chưa chứng minh tính tổng quát hóa hay lợi ích nhân quả của embedding.

Đây là thí nghiệm **mở rộng phụ thuộc kết quả** từ 1.024 bước, không phải lặp huấn luyện độc lập. Phán quyết âm L0015 ở 1.024 bước giữ nguyên.

## Đối chiếu nguồn gốc và checkpoint

- Nguồn trên GitHub: commit bridge `24492886922c7ac92c30ffa7d74f2d41b606a916`, mã băm SHA-256 `1f3e01c6e1baf5fcab5d22e41b3c49d309b5dc5f8d2a4cf0fcf5c2fc45728ae6`. Bộ chạy lõi SHA-256 `0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e`; kiểm tra CPU trước GPU 20/20 PASS.
- Tệp `CLAIM` và `RESULT` của lượt nguồn 1.024 bước được tải và băm lại, lần lượt `d7e99b831dcb69688e4a1483732f174125f8e1a10d5e73cea5c4ef9efcfb3011` và `46a93c888063c27711541c067d168ded31bbf22f6c46ba6efe45051cdc9c0bec`; đều khớp mã băm đã khóa.
- 1.024 mục đầu tiên của lịch TRAIN mới trùng hoàn toàn lịch cũ; SHA-256 tiền tố `19ddc05128c188b86bda2f02de6389946944fe287c26abbf7d24cc5f9681e8f2` và toàn lịch `81e4834f991607e8c3143bb67ed4a9ade93faa5f9526f630dc79e85bb0e51a52`; đủ 4.096 nhãn tại mỗi bước.
- Đã đọc bốn biên bản kế thừa `IMPORT_A/B/C/D`, xác nhận nhận AdamW ở bước 1.024 và trạng thái ngẫu nhiên (RNG) CPU/CUDA.
- Đã tải bốn checkpoint bước 2.048 thực từ Drive, băm SHA-256 độc lập, nạp bằng PyTorch CPU với `weights_only=True`, đọc dấu `READY`; tất cả có đúng 2.048 loss, bộ đếm AdamW ở 2.048 và RNG CPU/CUDA.

| Cấu hình | Kích thước (byte) | SHA-256 bước 2.048 |
|---|---:|---|
| A | 45.109.595 | `ed7419f6421f4d82590c11ed8003b7df45aca9e86678ac2e1bdbeb62d8cd0081` |
| B | 51.402.611 | `a4bb239a4952f2670966e6aacf89b10374ecce9ac2f4b8ba22003ed1589c024c` |
| C | 52.978.949 | `ba04731f3d9f90a61e5d0819ca6f22a86775ff9784a94fe128128d205b7ca44d` |
| D | 52.978.949 | `db5bebe2182d4f479028b260e0f70497d67d6f6dfac845d95708cb9c9f78f41e` |

Nguồn vật chất: [thư mục Drive](https://drive.google.com/drive/folders/1zadSQtNsCm5jG5pMtZPaWeCgsprNS6eg). Kết quả [RESULT.json](https://drive.google.com/file/d/1ZS-RTj2nFMrVmAHnbFGCdGEhmj9HJYgD/view), SHA-256 `f0cf6edd8481197b87c1c9906a9f48664376ee5055d8994fd864126e4dcedf65`. Tệp riêng tư theo 256 truyện SHA-256 `8c64d166c45f03eb114400dddca7f5cf35d90bd336b8b5cc5c90708095f526c7`.

## Phép đo độc lập

Tái tính từ tổng loss của 256 truyện, 328 cửa sổ, 61.122 nhãn VALIDATION; bootstrap ghép cặp theo truyện (paired story bootstrap) 1.000 lượt với `numpy.random.default_rng(20261109)`. Tất cả NLL và khoảng tin cậy 95% khớp báo cáo GPU.

| Cấu hình | NLL bước 1.024 | NLL bước 2.048 |
|---|---:|---:|
| A | 3,350122 | 3,313238 |
| B | 3,313222 | 3,328059 |
| C | 3,360402 | 3,270317 |
| D | 3,475417 | 3,392096 |

| So sánh | Chênh lệch NLL | Khoảng tin cậy 95% |
|---|---:|---|
| A−C | +0,042921 | [+0,032714; +0,052938] |
| B−C | +0,057742 | [+0,046504; +0,069384] |
| D−C | +0,121779 | [+0,110578; +0,134014] |

## Giới hạn và quyết định

Thẩm định độc lập này kiểm chứng **vật chất checkpoint và thống kê từ dữ liệu từng truyện**, không phải chạy lại suy luận từng token bằng bộ đánh giá thứ hai. Không đọc TEST, không tái huấn luyện GPU. Một seed, tập VALIDATION đã được tham khảo trước đó, ngân sách bước/nhãn bằng nhau nhưng phép tính dấu phẩy động (FLOPs) khác nhau. Không kết luận EmbeddingGemma 2 tạo ưu thế ngữ nghĩa đã được xác nhận.

**Quyết định:** ghi nhận tín hiệu dương thăm dò, giữ nguyên phán quyết âm L0015, chưa cấp quyền huấn luyện mới. Thiết kế cổng dư (residual/gated) vẫn chờ quyết định riêng. Giữ nguyên `main`, PR #12, các checkpoint nguồn và tập TEST.

Biên bản kiểm toán tổng hợp: `artifacts/qa/ttm-embeddinggemma2/TTM_GPU2048_INDEPENDENT_MATERIAL_STATISTICS_QA_20261109.json`. Dữ liệu theo truyện, lịch TRAIN và trọng số không công bố trên GitHub.
