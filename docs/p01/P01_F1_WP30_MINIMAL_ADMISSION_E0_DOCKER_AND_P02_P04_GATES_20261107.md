# TTM P01 — Chốt sử dụng F1 Wikipedia tinh gọn và bộ E0 Docker tích hợp

Ngày 07/11/2026. Quyết định theo chỉ đạo chủ dự án: **tránh 30 thủ tục giấy phép theo trang khi chưa có dấu hiệu rủi ro cụ thể**; duy trì đúng hợp đồng khoa học cho tokenizer/đánh giá.

## F1 — Phạm vi chấp thuận tối thiểu

Chỉ 30 bài Wikipedia tiếng Việt theo bản ghi đính kèm, có revision, SHA-256, link ghi công và 30 nhóm độc lập. Metadata quyền chung là CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/ ; Wikimedia Terms, https://foundation.wikimedia.org/wiki/Terms_of_Use . Chấp thuận **chỉ cho BPE E0 nội bộ chưa phân phối**, không tự tuyên bố quyền đối với mọi đoạn nhập từ bên thứ ba, không công bố source bytes và không chuyển quyền này sang phát hành mô hình thương mại. 0 cờ PII/bản quyền của bộ quét không phải bảo đảm pháp lý tuyệt đối. Khi phát hiện ngoại lệ cụ thể cần cách ly đúng tài liệu, không âm thầm bỏ qua.

Giữ 10 Wikisource và CQG-J3 ngoài E0. Không sửa kết quả cũ hoặc hồ sơ HOLD lịch sử; phán quyết kế nhiệm này là `ALLOW_WP30_SCOPED_INTERNAL_BPE_E0_CONDITIONAL_CC_BY_SA` cho **đúng mục đích**.

## Triển khai và kiểm tra tĩnh đã hoàn thành

Bộ chạy đính kèm hội thoại `TTM_P01_F1_WP30_E0_DOCKER_INTEGRATED_BUNDLE_20261107.zip` SHA `9263487c4efaa475016deaec016b75c886434b99d0586d41368e3caf470f3723`.

- Một PowerShell: `TTM_P01_F1_WP30_BPE_E0_DOCKER_ONE_SHOT_PS51_20261107.ps1`, SHA `ae5c875f2b8aaa3b493b0bfdcdd24c862f9a3913df2e41cceaff233d11fc2072`.
- Engine Python SHA `2f1b85c52b198046ffb472f284488b6d0ce17bcff7697062f6767e6f0ae6a53d`; independent checker SHA `ae07e11942e09cd910231e48f86d0e8d2d541ca80f8abbb6fbdcf2476ccb67c1`.
- Preflight chặn nếu sai Git origin, sai SHA biên bản/corpus, thiếu 30 nhóm H03, thiếu quyền ghi công, có cờ PII chưa xử lý, RAM trống dưới 8 GiB, D: trống dưới 16 GiB hoặc Docker Linux image không sẵn. Image Python có thể tải trước marker bằng tùy chọn rõ ràng.
- Chia bằng H03 seed `20261105`: 24 TRAIN / 3 VALIDATION / 3 TEST. Stage chỉ copy TRAIN cho hai container; TEST **không** được mount vào Docker hoặc dùng để chọn BPE.
- B0 byte 256; B1 deterministic byte BPE mục tiêu vocab 2048, tie lexicographic, ghép không chồng lấn; hai Docker fresh `--network none`, 4 GiB RAM, 4 CPU, 600 giây/lượt, yêu cầu cùng bảng ghép SHA. Independent checker đọc lại source/split và round-trip TRAIN/VALIDATION.
- Thí nghiệm dùng marker CreateNew, không tự rerun; không sửa F0-only source guard hay S1. Chỉ dọn temp mới tạo bên trong `D:\WORK\RESEARCH\TokenToModel-Lab`, không xóa worktree.
- Kiểm thử tổng hợp trên máy biên soạn: **8/8 PASS**, đối chiếu thuật toán BPE chậm/nhanh và âm tính, checker độc lập, hai worker xuất cùng SHA. **Chưa chạy native PS5.1, chưa chạy Docker Windows, chưa có E0 thật.**

## Trình tự P01 → P04, không vượt pha

Khi user chạy E0 một lần, đọc receipt `evidence/p01/TTM_P01_F1_WP30_E0_DOCKER_20261107.json` và `experiments/p01/TTM_P01_F1_WP30_E0_DOCKER_20261107/independent_qa.json`. Chỉ sau khi **E0 PASS + independent QA và phán quyết đóng P01** mới mở P02 core Transformer, tiếp đó P03 loop training và P04 checkpoints/held-out evaluation. Với máy 32 GB/Arc 140V, P02 và micro-batch P03 CPU chạy local; dài hơn dùng Colab có pin môi trường, giữ dữ liệu riêng và checkpoint; không thay đổi tiêu chí thực nghiệm.

`F1_WP30_INTERNAL=SCOPED_ALLOW` · `E0=NOT_EXECUTED` · `P01=OPEN` · `P02/P03/P04=NOT_OPENED` · `lineage.md=UNCHANGED`.


**Bổ sung QA trước marker:** chạy container Python chỉ để xác minh Docker Linux, giới hạn RAM/CPU/PID, read-only, network=none và bind mount; không truy cập F1 hoặc sinh dữ liệu khoa học.
