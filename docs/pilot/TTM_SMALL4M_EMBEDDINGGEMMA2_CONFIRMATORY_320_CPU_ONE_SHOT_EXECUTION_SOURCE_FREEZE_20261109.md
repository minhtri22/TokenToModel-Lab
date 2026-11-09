# TTM-Small-4M × EmbeddingGemma 2 — Hợp đồng một lượt chấm CPU 320 truyện, mã nguồn đã ghim

**Ngày:** 2026-11-09. **Nguồn dữ liệu GO:** commit `78c2d4483a0b3c592a06b3fdb35de00b3e013c25`, manifest riêng tư SHA-256 `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`, biên bản kiểm toán 320×256 SHA-256 `aa03c08b58aee49b46b049bceee8d735731235e19e3fed3a9725622b5d5dfdc8`.

## Khóa trước thực nghiệm

Bốn checkpoint A/B/C/D bước 2.048 đã kiểm SHA, mã gốc GPU2048 SHA-256 `0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e`, mã chấm độc lập SHA `de6ab9652bb690a6e967e752b9367f5755674a23a6c4b2fcb45941274612dfe1`, lớp tiền kiểm SHA `c92f827f7b462d42c53302b157038f0110d735ac41c4e4c2690f47356559e584`.

**Mã Python thực thi:** `ttm_gemma2_cpu_320_oneshot.py` SHA-256 `081115658713ef6823b5f0a2b68959235f86b2beac780f90dd451bcae6e959a5`. **Mã QA đọc lại độc lập** SHA `1f6fc134e7bc2a590f61b2c2c0409de701b65476bb8065ad9ad5425fc197532c`. **Gói chứa mã và checkpoint riêng tư** `TTM_GEMMA2_CPU320_ONESHOT_BUNDLE_20261109.zip`, SHA-256 `128f932b7e43882be1dcaac5bdca37118a78054b3c490ad3877e3838f5d6f3d3` và dung lượng 181.759.689 byte. **Gói ZIP không upload lên GitHub** vì chứa trọng số checkpoint. GitHub ghi dấu SHA bảo toàn nguồn.

Chấm chính xác 320 truyện, 405 cửa sổ, 75.798 nhãn token. Mỗi checkpoint chạy một lần trong chế độ CPU FP32 `eval()` / `inference_mode()`. Bốn tập NLL token-weighted được so sánh bằng **A−C, B−C, D−C**, bootstrap ghép cặp **theo truyện** 2.000 mẫu, NumPy `default_rng(2026110901)`, CI phân vị hai phía 95%. **PASS** chỉ nếu cả ba cận dưới CI95 >0, ngược lại **FAIL** khoa học nếu dữ liệu/chấm hợp lệ.

## One-shot và bằng chứng

Toàn bộ dữ liệu/cửa sổ/checkpoint phải đúng mã băm **trước** lần `forward()` đầu tiên. Sau tiền kiểm, ghi `CLAIM.json` bền vững và mới tính toán. Lưu `RESULT.json` công khai không ID/loss theo truyện; `PER_STORY_PRIVATE.json` chỉ ở máy chủ dự án, QA độc lập tính lại bootstrap mà không chạy model lần hai. Nếu CLAIM có rồi, kể cả gián đoạn, **không tự chạy lại**.

**Trạng thái khi đóng băng:** mã/ZIP đã được tạo và nguồn/checkpoint đã được nạp strict trên CPU với token giả lập, nhưng lượt chấm 320 truyện chưa chạy. RemoteMCP nhận tác vụ nhưng chặn lệnh ngay ở bước preflight bởi chính sách admission; chưa ghi CLAIM. Đường chạy Windows PowerShell trực tiếp là phương án fallback, không mở thêm cổng QA.

**Giới hạn khoa học:** TEST 64 truyện lịch sử đã được chấm ở L0012 nhưng không mở lại hoặc so gần trùng trong lần này. Không chứng minh donor EmbeddingGemma 2 không từng học TinyStories. Đây là xác nhận dự đoán cho một bộ checkpoint cố định, không phải huấn luyện lặp seed hay chứng minh chuyển giao nhân quả.

**Quản trị:** không thay main, checkpoint gốc, dữ liệu, và `lineage.md`; sau khi kết quả được xác minh độc lập mới append PASS/FAIL khoa học.
