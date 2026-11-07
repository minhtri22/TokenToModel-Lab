# P06 — Thẩm định QA CPU Windows và cổng đóng giai đoạn

Ngày 07/11/2026. Nhánh `feature/p06-paged-kv-manager-20261107`; mã đã chạy chính xác ở HEAD `af8f339e4e2de0a2ef5a9e25712874bbc461fffa`; nền `e35a9d179e9ee3584bf2bc3f34cbfe1b6c3d88ec`. [PR #10](https://github.com/minhtri22/TokenToModel-Lab/pull/10).

## Phán quyết

**`P06_TECHNICAL_EXIT_PASS_SCOPED_CPU_READY_FOR_EXACT_HEAD_MERGE`.** Bộ quản lý Paged KV hoạt động đúng trong các bài CPU synthetic đã khóa: logits tương đương P05 Dense KV và P02 không cache; phép Attention PyTorch độc lập; cấp/thu hồi block, page table, cách ly request, xóa dữ liệu khi tái sử dụng và các âm tính chống ghi sai. Đây là QA tính đúng kỹ thuật, không phải kết luận tăng tốc hay chất lượng khoa học.

## Bằng chứng Windows chính xác

- Biên bản `TTM_P06_WINDOWS_CPU_QA_20261107T163950Z_P10520.json`, SHA-256 `d19a72394df586a290a33394fd3b342a7d9f4d3fc44dcee7288c1b3016bdb5a3`. Phiên bản lưu GitHub khớp byte gốc (Git blob `2f8cf8f0e0e28ae119938ac53542a04c977ed9cd`); không sửa verdict nguồn.
- Python 3.12.10 và PyTorch 2.11.0+cpu. 8/8 unittest PASS, `EXIT=0`, `Ran 8 tests in 0.139s / OK`; log gốc vẫn ở `evidence/p06/TTM_P06_WINDOWS_CPU_QA_20261107T163950Z_P10520.unittest.log`, SHA do runner báo `8fe777493e009b93993302bb56c24ea3f7adcf868ab11385ed019a9b01482d5e`.
- 5/5 independent checker PASS, `EXIT=0`, JSON `status=PASS`, tất cả 5 kiểm tra `true`; log `...independent.log`, SHA do runner báo `8d4a5a59b2bc43b18116bf13e6a2c9d0de6cf5ea0be608dcaad3028983472c19`.
- Đã đọc trực tiếp nội dung hai log từ máy và kiểm tra cả 8 tên unittest, 5 tên independent, status, phạm vi, thống kê KV và tính hợp lệ các phép đo. **Không tính lại SHA nhị phân của hai log**, vì vậy SHA log là bằng chứng do runner ghi chứ không phải một lượt tái băm độc lập.
- Đối chiếu 6 Git blob P06/P05/P02/P00 từ biên bản với chính HEAD GitHub: **6/6 exact**. Không thay đổi `lineage.md`.
- Trên Windows, local HEAD trước/sau là `92facee15...`, không bị script thay đổi; cleanup worktree riêng `PASS_EXACT_OWNED_GIT_WORKTREE`. Local main còn cũ, việc cập nhật phải qua một bước fast-forward an toàn nếu người dùng cần, không phải công việc của kiểm định P06.

## Đo bộ nhớ và thời gian (không có tuyên bố tăng tốc)

- Load: 7 token, block size 3, 2 lần đo CPU float32.
- `paged_allocated_bytes=67584`; `dense_allocated_bytes=65536`; `used_logical_bytes=7168`; `fragmented_bytes=2048`.
- `paged_ms=[7.9678, 4.7428]`; `dense_ms=[18.5259, 10.5768]`; `recompute_ms=[3.1508, 15.1481]` (ms, phép đo tham khảo). Không so sánh hiệu năng một cách suy diễn từ 2 lần lặp; không công bố lợi thế P06.

## Ranh giới và bước tiếp theo

- Chỉ `SYNTHETIC_TOKEN_IDS_ONLY`. Không đọc dữ liệu Wikipedia F1, không truy cập TEST thật, không chạy lại E0/P03, không dùng GPU.
- `P04_REAL_HELDOUT=NOT_EXECUTED`; chưa có checkpoint GPT thực tế để đánh giá ngôn ngữ. Không ghi kết quả QA hạ tầng vào `lineage.md` khoa học.
- CI GitHub chưa có run cho HEAD này; Windows QA do chủ dự án chạy thay thế theo quy trình thực tế và được đối chiếu độc lập nội dung.
- Khi PR #10 sạch, đúng HEAD và được merge, đóng P06 theo phạm vi kỹ thuật CPU rồi **mới mở P07 design** từ main merge commit. P07 GPU Kernel là quyết định và QA riêng; không tự triển khai/chạy GPU trong phán quyết P06.

**Bước tiếp theo:** `TTM_P06_PR10_EXACT_HEAD_REVIEW_MERGE_AND_P07_DESIGN_OPEN`.
