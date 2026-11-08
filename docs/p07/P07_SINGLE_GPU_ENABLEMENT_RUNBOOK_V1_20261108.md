# TTM P07 — Một runner môi trường GPU riêng biệt (PowerShell 5.1), không tự thực thi

**Mục tiêu:** đúng một lượt kích hoạt môi trường Intel Arc 140V trên Windows, không kiểm kê lại phần cứng. Khối A: PyTorch XPU trong venv riêng → GPU FP32 canary. Chỉ khi A PASS, khối B: Intel DPC++/SYCL 2026.2.0 qua gói Conda trong môi trường riêng → một canary đọc page-table trực tiếp bằng GPU Level Zero. Cả hai ghi một receipt JSON và các log trong workplace TTM.

## Trạng thái ủy quyền

`PLAN_AND_RUNNER_PREPARED_ONLY` — người dùng **chưa cấp quyền thực thi cài/tải/dispatch**. Script mặc định `-Mode Preview` chỉ đọc. `-Mode Execute` bắt buộc truyền cả chuỗi chấp thuận `TTM_P07_APPROVE_ISOLATED_INSTALL_AND_GPU_CANARY_V1` và `-ExpectedP07Head <40 hex>` đúng GitHub ở lúc thực thi. Một lock có chế độ *CreateNew* ngăn tự chạy lần thứ hai.

## Thư mục và không gian

Tất cả runtime tạo mới nằm bên trong `D:\WORK\RESEARCH\TokenToModel-Lab\_runtime\p07\`:

- `venv_xpu_cp312`: venv Python 3.12.10, không sửa seed Python.
- `wheels`: wheelhouse pip, SHA-256 cho tất cả bánh xe trước cài offline.
- `sycl_conda` / `conda_pkgs`: môi trường Conda compiler và cache Intel 2026.2.0, `--download-only` rồi SHA-256 trước `--offline`.
- `tmp`: build/temp/chỉ xóa khi PASS và có sentinel đúng; khi FAIL giữ nguyên để điều tra.
- `evidence\p07\gpu_enablement`: lock, manifest, log, receipt (không xóa khi cleanup).

D: phải còn ít nhất 24 GiB khi bắt đầu và tối thiểu 12 GiB sau thiết lập; tổng phát sinh mục tiêu không quá 18 GiB, trong đó PyTorch XPU tối đa 6 GiB, phần compiler thêm tối đa 12 GiB. RAM còn tối thiểu 8 GiB lúc bắt đầu. Nếu tài nguyên không đủ thì dừng, không tự dọn tài liệu hoặc những repo khác.

## Quy trình thực hiện khi được phê duyệt

1. **Tải ZIP từ ChatGPT**, kiểm tra SHA-256 của ZIP/PS1 theo bảng SHA, giải nén vào Downloads mới.
2. **Preview trước (chỉ đọc)**: chạy Parser PowerShell 5.1, kiểm tra script SHA; sau đó gọi `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ... -Mode Preview`. Chỉ đối chiếu Git remote refs và dung lượng trống D; không kiểm kê GPU lần nữa.
3. **Đợi chấp thuận rõ ràng** trước khi gọi `-Mode Execute`. Phải đặt `-ExpectedP07Head` theo SHA GitHub trong biên bản đã pin. Nếu remote branch/main dịch chuyển, script dừng.
4. **Execute** dùng duy nhất venv, conda prefix, wheelhouse dưới TTM. Ghi manifest SHA từng gói trước khi offline install; không cài vào Python seed, Miniforge base, driver hay PATH toàn hệ.
5. Nếu XPU không tạo được tensor GPU hoặc parity FP32 sai, dừng **trước compiler**. Nếu đã PASS, thử SYCL Level Zero với bảng trang và hai request xen kẽ. C++ canary chỉ kiểm tra **direct physical-page lookup**, chưa phải PagedAttention đầy đủ.
6. Gửi `TTM_P07_GPU_ENABLEMENT_FINAL`, `RECEIPT`, `RECEIPT_SHA256` và JSON cùng log cho phán quyết; mọi FAIL giữ nguyên, không auto-rerun.

## Phạm vi, giới hạn

- PyTorch đã xác minh có wheel `torch-2.12.1+xpu-cp312-cp312-win_amd64.whl` trên index chính thức. Gói Intel `dpcpp_win-64=2026.2.0` và `intel-sycl-rt=2026.2.0` có qua Conda. Ở bước Execute, resolver tải dependencies; thực tế có thể FAIL nếu phụ thuộc thay đổi. Khi đó giữ FAIL, không tự đổi version. Hash ghi lại **sau tải, trước cài**; đó là bằng chứng toàn vẹn *trong lượt này*, không phải chứng chỉ độc lập của publisher.
- Windows 11 **Home Single Language** trên máy không nằm trong ma trận Pro/Enterprise được Intel chứng nhận cho GPU client. Cho phép thử kỹ thuật không đồng nghĩa có hỗ trợ chính thức. Không nâng cấp OS/driver để “sửa” lỗi.
- Conda có thể tạo metadata dưới profile user hoặc Windows có thể ghi file tạm/telemetry ngoài D do phần mềm; script hạn chế prefix và cache vào D nhưng **không cam kết tuyệt đối không ghi byte ngoài D**. Không chạy installer exe toàn hệ thống.
- GPU Arc 140V là tích hợp, 16GB hiển thị trong tên thiết bị không được xem là 16 GiB VRAM riêng.
- Trước khi chạy, cần đảm bảo không có tiến trình nghiên cứu khác phụ thuộc đến môi trường C/Miniforge đang sử dụng; script không nâng thư viện nào trong các môi trường đó.
- `main`/`lineage.md`, P01–P06, E0, F1/TEST giữ nguyên. P08 chưa mở. Không tạo worktree, không fetch/checkout/pull Git; chỉ `ls-remote` và `rev-parse` trong repo.
- **Đây chỉ là capability canary**. Để đóng P07 vẫn phải triển khai custom PagedAttention kernel, đối chiếu logits/Attention/negative QA và đo benchmark GPU cùng tải G1/G2. Không suy diễn GPU speedup từ canary này.

## Nguồn tài liệu

- PyTorch XPU index: https://download.pytorch.org/whl/xpu/torch/
- Intel DPC++ package modes: https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler-download.html
- Intel oneAPI 2026 compiler/system requirements: https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-dpcpp/2026.html
- Anaconda conda-forge `dpcpp_win-64`: https://anaconda.org/channels/conda-forge/packages/dpcpp_win-64/overview

**Bước thực hiện tiếp theo:** `TTM_P07_USER_APPROVAL_THEN_SINGLE_GPU_ENABLEMENT_ONE_SHOT` — có phạm vi chấp thuận rồi mới chạy một lượt; không kiểm kê phần cứng lại.
