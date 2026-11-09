# GATED32 — Sửa lỗi đối số Python trong launcher PowerShell 5.1 trước CLAIM

Ngày 09/11/2026. Đây là sửa lỗi kỹ thuật trước CLAIM, không thay đổi hợp đồng khoa học hay khởi chạy một phép thử mới.

## Nguyên nhân và thay đổi

PowerShell 5.1 bỏ các dấu ngoặc kép bên trong đối số python -c khi gọi chương trình native. Lệnh print("CPU_GATE32_RUNTIME",...) được Python nhận như print(CPU_GATE32_RUNTIME,...), gây NameError và CPU_RUNTIME_CHECK_FAIL_NO_CLAIM.

Thay đúng một câu lệnh print bằng print(sys.version.split()[0],torch.__version__) để không phụ thuộc lớp trích dẫn.

## Bằng chứng

- Đã đọc lại launcher trong D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_gemma2_gate32_source_20261109\RUN_GATED32_ONCE.ps1 trên Windows và xác minh lệnh sửa.
- Đã kiểm tra chỉ đọc thư mục _tmp\ttm_small4m_gemma2_zero_gate_residual_32_cpu_probe_20261109_v1 và CLAIM.json đều chưa tồn tại.
- Launcher gốc SHA256 trên ZIP LF: e27b7ba2419cf9dc1c7a0483abb68ff0f7ffcd53a9b585bdc8a59f3d1c407adc.
- Bản launcher sửa LF SHA256: b520bb489c7d8a3873811782b16e449a0786cb9b49b3dedb594b16b0b6c7abbf. SHA trên Windows có thể khác nếu thay newline.
- Runner khoa học SHA256 không đổi: 235816631eedbe212f7f431700024f1e4ae8e470fd5b0cabcdabd78421c815bf.
- Reviewer khoa học SHA256 không đổi: d25296daa0ff3185dc078195d0b239b655c0d305a031a3d0129d9b5a5d05cbca.

Không tải lại ZIP nguồn gốc, không thay checkpoint, candidate, T4 private TRAIN/VAL, optimizer, RunID, seed, quy tắc bootstrap hay L0017.

## Tiếp tục

Chỉ sau khi xác minh output và CLAIM vẫn chưa tồn tại, thực thi đúng launcher đã sửa một lần. Nếu CLAIM xuất hiện hoặc bị gián đoạn sau CLAIM, giữ nguyên bằng chứng và không khởi chạy lại.
