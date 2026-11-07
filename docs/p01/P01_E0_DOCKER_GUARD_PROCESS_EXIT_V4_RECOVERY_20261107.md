# TTM P01 E0 — V3 Docker Guard báo EXIT rỗng, xử lý V4 giữ nguyên thí nghiệm

Ngày 07/11/2026.

## Bằng chứng

`python:3.12-slim` đã tải thành công, Docker image ID `sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54`; Python host 3.12.10, 30 văn bản F1 và chia H03 24/3/3 đều PASS tiền kiểm. Bản V3 thất bại tại `Check-DockerGuardCapability`: `DOCKER_GUARD_CAPABILITY_FAILED_PRE_MARKER_EXIT_:` nhưng không có số exit code hoặc stderr. Đọc lại workspace không có marker/receipt E0 hay experiments/p01.

**Không được suy ra từ log rằng Docker đã không hỗ trợ giới hạn RAM/PID/mount; cũng không được tự tuyên bố Docker Guard PASS.** Lỗi V3 có thể ở cách thu mã thoát `Start-Process -PassThru` hoặc lỗi thật của Docker. V4 phải hiển thị nguyên nhân.

## V4 — Sửa duy nhất đường gọi Docker

Script đính kèm cuộc hội thoại: `TTM_P01_F1_WP30_BPE_E0_DOCKER_PY312_PROCESS_EXIT_RECOVERY_V4_PS51_20261107.ps1`, SHA-256 `7b36c6657957367908d26190b600e5e0b39c93007e455c0e20345ef48b29f2af`.

- Thay ba vị trí `Start-Process -PassThru` của **pull, guard capability và worker** bằng `System.Diagnostics.Process` với capture `StdOut`/`StdErr` bất đồng bộ, timeout và `ExitCode` xác thực.
- Không thay các cờ Docker: `--network=none`, `--memory=4g`, `--memory-swap=4g`, `--pids-limit=96`, `--cpus=4`, `--read-only`, `--cap-drop=ALL`, `no-new-privileges`, file size limit, readonly bind.
- Giữ marker một lượt `TTM_P01_F1_WP30_E0_DOCKER_20261107.once`, cùng output và input F1.
- SHA-256 engine Python `2f1b85c52b198046ffb472f284488b6d0ce17bcff7697062f6767e6f0ae6a53d`, checker `ae07e11942e09cd910231e48f86d0e8d2d541ca80f8abbb6fbdcf2476ccb67c1` giữ nguyên.
- Bộ kiểm thử BPE offline và kiểm SHA nhúng PASS. **Chưa xác nhận parser PS5.1 hoặc guard Docker trên máy Windows bằng V4.**

ZIP đính kèm `TTM_P01_E0_DOCKER_GUARD_PROCESS_EXIT_V4_RECOVERY_BUNDLE_20261107.zip`, SHA-256 `df3e01a93d6ad9308b48cf4157d0a1d6607779ea9c7dcaa711ec89d923d40c15`.

## Bước tiếp theo

Người dùng kiểm SHA script V4, PS51 parser, marker/receipt pristine và chạy một lượt V4 **không cần pull ảnh nữa**. Nếu guard Docker vẫn không đạt, giữ nguyên lỗi có số exit code + stderr và **dừng trước marker**; không tự đổi cờ bảo vệ. Nếu guard PASS và E0 chạy, marker một lượt là đã tiêu thụ: lỗi sau marker không được rerun.

Không sửa `main`, `lineage.md`, K1/K2, S1, dữ liệu 30 bài, các seed hoặc lộ trình P00–P12. `E0=NOT_EXECUTED`, `P01=OPEN`, `P02=NOT_OPENED` ở thời điểm lập hồ sơ.
