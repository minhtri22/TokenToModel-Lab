# TTM P01 E0 — Sửa lỗi tham số phiên bản Python 3.12 (V3)

Ngày 07/11/2026. Phạm vi một sửa lỗi kỹ thuật **trước** marker E0.

## Bằng chứng lỗi Windows

Miniforge base `C:\Users\minht\miniforge3\python.exe` xác nhận đang là `3.13.12`; bộ chạy đã chọn Python 3.12 riêng `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe`. Sau `TTM_P01_F1_E0_DOCKER_PRECHECK=START`, câu lệnh `-c` bị PowerShell 5.1 xử lý dấu nháy sai, tạo thành biểu thức `...major)+.+str(...)` và Python ném SyntaxError. Kết luận `HOST_PYTHON_VERSION_CHECK_FAILED_NO_MARKER`, `E0=NOT_EXECUTED`. Đọc lại máy không có marker hoặc biên bản E0; thư mục `experiments/p01` chưa tồn tại.

## Sửa tối thiểu

Đổi đúng một đoạn tiền kiểm:
- Từ `& $py -B -c 'import sys;print(str(sys.version_info.major)+"."+str(sys.version_info.minor)+"."+str(sys.version_info.micro))'`.
- Thành `& $py --version`; kiểm biểu thức `^Python 3\.12\.[0-9]+(?:\s|$)`. Không chuyển bất kỳ literal Python nào qua PowerShell nữa.

Không sửa engine/checker, SHA nguồn, chia H03, giới hạn Docker hay tên marker/receipt. Python 3.12 tiếp tục sử dụng đường độc lập, không hạ cấp môi trường Miniforge 3.13 đang chia sẻ với dự án khác.

- Script V3: `TTM_P01_F1_WP30_BPE_E0_DOCKER_PY312_VERSION_PROBE_RECOVERY_V3_PS51_20261107.ps1`; SHA-256 `6afe3ca0bdf9ef18f6c37a360b59f97634dd985d1ae59125bb8eb280d12c0c09`.
- Bộ nén V3 SHA-256 `395553b7b9d41bbb865afbcd3ef93bedd29a185b480978cb81eb6bd94dadb3b8`.
- Mã nguồn engine SHA-256 `2f1b85c52b198046ffb472f284488b6d0ce17bcff7697062f6767e6f0ae6a53d`.
- Independent checker SHA-256 `ae07e11942e09cd910231e48f86d0e8d2d541ca80f8abbb6fbdcf2476ccb67c1`.

Đối chiếu byte nhúng, khác biệt code phạm vi một block, bộ tự kiểm thử BPE ngoại tuyến PASS. **Chưa có PS51 parser hoặc E0 Windows PASS**. Tệp chạy chỉ đính kèm hội thoại, không commit source qua GitHub.

## Công việc tiếp theo

Xác minh phiên bản Python 3.12 ngoài Miniforge, SHA-256 script V3, PS51 parser, marker pristine; chạy đúng **original E0 single-shot marker** qua bộ khôi phục V3. Nếu FAIL sau marker, giữ nguyên chứng cứ và không chạy lại. Sau khi E0 và QA độc lập PASS mới xét đóng P01 và chuyển P02/P03/P04.

Không sửa P00-P12, K1/K2, S1, `main` hoặc `lineage.md`.
