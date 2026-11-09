# TTM-T6 — Windows 11 CPU A/B replay: No-cache / Dense KV / Paged KV

**Ngày:** 2026-11-09 · **Trạng thái:** `WINDOWS_SCOPED_SYNTHETIC_CPU=PASS`, `QA_UNIT=16/16`, `QA_MATERIAL=33/33`, `CROSS_FILE_AUDIT=17/17`, `PERFORMANCE_SPEEDUP=NOT_CLAIMED`.

**Đây là bản đọc lại trực tiếp bốn hiện vật người sở hữu vừa chạy, không phải lượt benchmark mới của trợ lý.**

## 1. Xuất xứ và bất biến

- Repository: `minhtri22/TokenToModel-Lab`, branch PR #15 `feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109`.
- Worktree Windows: `D:\WORK\RESEARCH\TokenToModel-Lab\.worktrees\ttm-t6-pr15-20261109`.
- Commit **thực thi** (không nhầm với HEAD sau khi lưu bằng chứng): `ff4d30ea294f148d5d060f1331cfbf6f4f6d44aa`.
- Windows `Windows-11-10.0.26300-SP0`; Python **3.12.10**; PyTorch **2.11.0+cpu**; CPU float32; 8 logical CPUs, PyTorch 2 threads.
- P02/P05/P06 gốc **không thay đổi**: Git blobs `9762343e06cf800b50574c2871ae1ed58537fb18`, `d835e5d7bb07fea447c5a869b13c70327ab05a53`, `4d52188adaf55674b6965513ea1beb38ec9a8e9b`.
- Synthetic P02, vocabulary 2048, embedding 64, 2 layers, 4 heads, context 32, 6 tokens mới, no checkpoint T4, no TRAIN/VAL/TEST/Q1Q2/GPU.
- Warmups **2**, repeats **5** per mode. TTFT bao gồm request start và prefill đến token đầu, **không bao gồm** tạo pool cache; TPOT đo riêng các token 2–6.

## 2. Kiểm tra tính đúng

- 16 unit tests PASS, thời gian **2,216 giây**.
- 33/33 kiểm toán số học/vật liệu PASS; một chương trình đối chiếu chéo độc lập khác đọc lại 4 tệp và kiểm tra **17/17** bất biến gồm source pins, head, QA, thuật toán, lượt đo, logits, memory math và nguồn byte.
- Cả ba chế độ sinh ra **cùng 6 token** trong từng tải; độ lệch logits Dense/Paged vs No-cache lớn nhất trên Windows là **`2.980232238769531e-7`**, thấp hơn tolerance `atol=rtol=2e-5`. Dense và Paged có logits **trùng tuyệt đối trong fixture**.
- Kiểm thử âm tính: token sai, vượt context, OOM không cập nhật nửa chừng, cách ly hai request, scrub KV sau release và phát hiện cố tình làm sai logits/token.

## 3. TTFT/TPOT Windows (median ms)

| Tải | Prompt tokens | No-cache TTFT | Dense TTFT | Paged TTFT | No-cache TPOT | Dense TPOT | Paged TPOT |
|---|---:|---:|---:|---:|---:|---:|---:|
| Short | 4 | 0.5018 | 1.5850 | 2.0770 | 0.47996 | 0.73490 | 0.59212 |
| Medium | 11 | 0.6266 | 4.1852 | 4.6819 | 0.43744 | 0.56074 | 0.52578 |
| Cross-pages | 16 | 0.6344 | 6.0103 | 7.4051 | 0.57438 | 0.55288 | 0.51000 |

**Phán quyết:** No-cache có TTFT thấp nhất ở cả ba tải ngắn CPU. Paged TPOT nhỏ hơn Dense ở 2/3 tải, nhưng không đủ bằng chứng để tuyên bố tăng tốc tổng quát. So sánh Linux/Windows không đồng nhất môi trường hoặc clock; không kết luận GPU serving speedup.

## 4. Bộ nhớ KV (hai request 13+5 token)

| Hạng mục | Dense | Paged |
|---|---:|---:|
| Pool vật lý đã cấp | 65,536 bytes | 65,536 bytes |
| Dung lượng dành riêng cho request | 65,536 bytes | 24,576 bytes |
| KV logic đang sử dụng | 18,432 bytes | 18,432 bytes |
| Phân mảnh bên trong phần dành riêng | 47,104 bytes | 6,144 bytes |

Đây là **dung lượng tensor KV đúng byte**, không phải peak RSS. Mẫu `rss_sampled_after_decode_bytes` đều `null`; do đó **không được** tuyên bố giảm tổng RAM hoặc tính năng mới P07/P08.

## 5. Bảo quản nguyên byte trên GitHub

Đã đối chiếu SHA-256 gốc độc lập từ văn bản đọc máy Windows, dựng lại chính xác CRLF/LF của tệp, rồi commit và **đọc lại GitHub đúng byte 4/4**. Các SHA-256 ở đây là của tệp owner ban đầu, không phải tệp trình bày chuyển đổi:

| Tệp | SHA-256 của hiện vật owner |
|---|---|
| [Unit test log](../artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_UNITTEST_OWNER_20261109.log) | `2f063493c448723ae9fcfd2d2ca364bb0374dcdf1369558c9302669924c93590` |
| [Benchmark JSON](../artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_CPU_AB_OWNER_RUN.json) | `39275324dc56c2bbfb075e73991cf4383f48bdc38acdaf182c66178b42e113b0` |
| [QA JSON](../artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_INDEPENDENT_QA_OWNER_20261109.json) | `2525b423dac500c19810e4c66a301939bf0e4083ceeeb0a779509c41783b6591` |
| [Owner receipt](../artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_OWNER_RECEIPT_20261109.json) | `742247aaa64701d6e09964db8a0724c2980bccaf9ffe533402703dd8e7b327c6` |

[Biên bản nguồn, SHA và QA](../artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_OWNER_INDEPENDENT_READBACK_AND_ADJUDICATION_20261109.json) ghim các Git blob và chi tiết giới hạn. Trong trường hợp GitHub web tự trình bày thay đổi xuống dòng, dùng Git raw/blobs hoặc Git SHA để đối chiếu.

## 6. Quyết định phạm vi và bước tiếp theo

**`PASS_SCOPED_WINDOWS_CPU_TECHNICAL`** với 16/16 unittest, 33/33 material QA, 17/17 độc lập tái tính xuyên tệp và 4/4 raw evidence SHA GitHub. Không phải xác nhận khoa học mở rộng hay đánh giá người phản biện bên ngoài.

Giữ `PR15=DRAFT_HOLD` cho đến khi có người review khác xác nhận ranh giới, chất lượng code, CI Windows và quyết định merge. **Không cần chạy lại** batch benchmark này chỉ để sửa báo cáo. Không thêm `lineage.md`, không sửa P02/P05/P06, không mở P07/P08, không sửa `main`.

**Bước thực hiện tiếp theo:** `TTM_T6_PR15_DISTINCT_REVIEW_AND_MERGE_DECISION` — kiểm tra riêng code/test và 4 hiện vật Windows đã khóa, sau đó mới phán quyết merge hoặc HOLD.
