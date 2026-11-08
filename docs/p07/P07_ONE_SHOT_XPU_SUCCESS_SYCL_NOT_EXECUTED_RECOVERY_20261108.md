# TTM P07 — Phán quyết lượt GPU đã tiêu thụ: XPU PASS, giới hạn dung lượng chặn SYCL

Ngày 08/11/2026. Lượt `P07_GPU_ENABLEMENT_20261108T024525Z_P28364` trên Windows. Đường dẫn biên bản gốc: `evidence/p07/gpu_enablement/P07_GPU_ENABLEMENT_20261108T024525Z_P28364.json`. SHA-256 được runner báo: `9A619F41412A6BE87FCD7A307477A148AE80C6BD8801206CFC5791FB7AF3B647`; **chưa tái băm byte gốc** qua connector đọc văn bản. Đã đọc lại receipt, tệp lock và log GPU/pip trực tiếp từ Windows.

## Kết quả

- Giữ nguyên `FAIL_OR_INCONCLUSIVE_NO_AUTORERUN` và nguyên nhân `PYTORCH_XPU_DISK_BUDGET_6_GIB_EXCEEDED`. Đây là **giới hạn riêng của bước cài XPU**, không phải tổng ổ D quá thấp, cũng không phải kiểm định GPU FAIL.
- `wheel_download=PASS_HASHED` (manifest gốc 30 wheel), `xpu_install=PASS_OFFLINE_PINNED_WHEELS`, `xpu_compute=PASS_REAL_GPU_COMPUTE`. Torch thực sự `2.12.1+xpu`, `torch.xpu.is_available()=true`, `device_count=1`, Intel Arc 140V. FP32 canary chênh lệch tối đa `3.725290298461914e-09`. Log pip check: “No broken requirements found.” Log cũng có cảnh báo NumPy chưa có nhưng **không làm hỏng kết quả GPU tính toán**.
- D: từ `34.561` còn `28.524 GiB`, tăng sử dụng `6.037 GiB` = **vượt ngưỡng con 6 GiB đúng 0.037 GiB (~38 MiB)**. Tổng giới hạn 18 GiB vẫn chưa vượt, mức dự trữ 12 GiB còn nguyên. **Không tự nâng giới hạn hoặc xóa dữ liệu để làm pass.**
- `compiler_download=NOT_EXECUTED`, `compiler_install=NOT_EXECUTED`, `sycl_direct_page_index=NOT_EXECUTED`. P07 custom GPU paged-attention kernel và P08 chưa mở.
- `P07_GPU_ENABLEMENT_V1_ONE_SHOT.lock` đã tồn tại và chứa cùng run ID cùng HEAD `4024941b96358828804ea77481e860550c5547a0`: **lượt đã tiêu thụ; tuyệt đối không chạy lại V1**. Hiện trạng môi trường và các tệp wheel được `PRESERVED_FOR_DIAGNOSIS_NO_DELETION`. Không sửa `main`, P01–P06 hay `lineage.md`.

## Phán quyết kỹ thuật

`XPU_CAPABILITY=PASS_REAL_GPU` · `ONE_SHOT=CONSUMED` · `RUN_V1=FAIL_OR_INCONCLUSIVE_PRESERVED` · `SYCL_CAPABILITY=NOT_TESTED` · `P07=DESIGN_ONLY`.

Điều này **loại bỏ giả thuyết môi trường XPU không thể sử dụng Arc 140V trong phép canary đã thử**, nhưng **chưa chứng minh bất kỳ kernel SYCL đọc page table hoặc cải thiện hiệu năng P07**.

## Tiếp tục hợp lý, chưa cho phép thực thi

`TTM_P07_SYCL_STAGE_ONLY_PRESERVED_XPU_ENV_CONTINUATION_PLAN`:

1. **Không chạy lại** V1; không xóa khóa, venv XPU, wheelhouse hay log. Không cài lại torch, không chạy lại canary XPU.
2. Nếu thực thi một lượt tiếp tục riêng sau khi chấp thuận: giữ đầu nguồn test và các wheel hash, nhận **venv XPU đã PASS**, kiểm tra đúng receipt/lock, SHA wheel và driver read-only. Không lấy lại ngân sách 6 GiB từ đầu.
3. Tính ngân sách còn lại từ snapshot gốc: `18 - 6.037 = 11.963 GiB`. D free phải duy trì ít nhất 12 GiB. Nếu compiler cần lớn hơn phần còn lại thì **dừng trước tải/cài**.
4. Chỉ triển khai **compiler SYCL và phép thử đọc bảng trang trên GPU** trong lượt kế tiếp; một receipt PASS/FAIL riêng, append-only evidence. Không thay Windows/driver/Python seed, không mở P08.
5. Môi trường `_runtime/p07` chỉ là đối tượng thuộc dự án; việc dọn dẹp tạm hay rollback phải được xác nhận đúng phạm vi, không xóa bằng chứng/hệ thống.

Đây là kế hoạch phục hồi chính xác từ trạng thái đã có, không mở thêm một vòng kiểm kê GPU. Không có quyền chạy successor từ tài liệu này.
