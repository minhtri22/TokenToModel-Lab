# TTM P01 E0 — Khôi phục tiền kiểm ảnh Docker / Python 3.12 (V2)

Ngày 07/11/2026. Chỉ sửa **lỗi tiền kiểm** trước marker, không chạy lại F0/K1/K2/S1 hoặc nới cổng khoa học.

## Console thực tế
E0 offline fixture PASS; 30 Wikipedia/30 nhóm H03 và chia 24 TRAIN/3 VALIDATION/3 TEST đều PASS tại tiền kiểm. RAM 11.48 GiB và Docker Linux đã PASS ở lượt mới. Sau đó `docker image inspect python:3.13-slim` gặp ảnh chưa có và PowerShell 5.1 với `$ErrorActionPreference='Stop'` ném `NativeCommandError`, **không chạy tới `-AllowImagePull`**. Ba lệnh kiểm tra tên container theo mẫu `container inspect` cũng tiềm ẩn cùng lỗi. Đọc lại máy không có marker/receipt E0 và chưa có experiments/p01, temp E0 đã dọn. `E0=NOT_EXECUTED`.

## Sửa kỹ thuật sau lỗi (V2)

Để đáp ứng đề nghị Python 3.12 của chủ dự án:
- Mặc định host path `C:\Users\minht\miniforge3\python.exe`. **Bắt buộc xác minh runtime chính là 3.12**; không tự thay đổi Miniforge base. Nếu đó là 3.13, cung cấp `-HostPythonPath` cho một bản Python 3.12 khác đã cài.
- Docker image chuyển trước lượt khoa học đầu tiên từ `python:3.13-slim` sang `python:3.12-slim`, pin actual image ID trong lượt, container `--pull=never`, mạng tắt.
- Docker image/container existence probes chuyển sang .NET ProcessStartInfo đọc exit code, không dùng native STDERR dưới `ErrorActionPreference=Stop`.
- Docker image pull có thể kích hoạt với `-AllowImagePull`, chỉ trước marker, tiến trình có giới hạn; cùng một capability smoke giới hạn RAM/CPU/PIDs trước marker, xác minh Python 3.12.

**Mã Python engine/checker nhúng bất biến SHA**:
- Engine: `2f1b85c52b198046ffb472f284488b6d0ce17bcff7697062f6767e6f0ae6a53d`
- Checker: `ae07e11942e09cd910231e48f86d0e8d2d541ca80f8abbb6fbdcf2476ccb67c1`

PowerShell V2: `TTM_P01_F1_WP30_BPE_E0_DOCKER_PY312_ARGV_RECOVERY_V2_PS51_20261107.ps1`; SHA-256 `6070e42420b16a599c5a304b8b4e157b8b5c28396acdb278966a63161439f74a`.

ZIP đính kèm: `TTM_P01_E0_PY312_DOCKER_PREFLIGHT_RECOVERY_V2_20261107.zip`; SHA-256 `588f5fb8eb0cd4c00561e4df32d8cf17255c923d446f015ffdfaaf939252ee58`.

Đã xác minh byte mã nhúng, phân tích cú pháp Python theo grammar 3.12, 8 synthetic integration tests PASS. **Chưa kiểm tra native parser PS5.1, chưa chạy trên máy Windows/ Docker của chủ dự án; không tuyên bố E0 PASS.**

V2 giữ nguyên tên marker, receipt và kết quả E0 để tránh tạo một lượt E0 mới. Trong trường hợp lỗi sau marker phải giữ FAIL, tuyệt đối không chạy lại.

## Bước tiếp theo

Kiểm tra phiên bản Python host tại Miniforge và (nếu cần) đường Python 3.12 độc lập; xác minh SHA script và cú pháp PS51; chạy đúng một lượt V2 khi tài nguyên/Docker sẵn sàng; đọc kết quả E0 và independent QA để quyết định P01 closure, rồi mới mở P02→P03→P04. Giữ `main` và `lineage.md` bất biến.
