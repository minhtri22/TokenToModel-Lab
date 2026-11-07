# TTM P07 — Phán quyết G0 Windows Arc 140V: kiểm kê PASS, khả năng GPU bị chặn

Ngày thẩm định: **08/11/2026 (Việt Nam)**. Nguồn là JSON console do chủ dự án cung cấp, thu lúc **2026-11-07T17:34:26.8672025Z**. Đây là bản ghi công khai đã **chuẩn hóa, lược bỏ đường dẫn chứa tên tài khoản người dùng**; tệp gốc chỉ in ra console, do đó **không có tệp receipt gốc để xác minh SHA-256 từng byte**. Script dò đã pin SHA-256 `d4bfc3ea86ac1ffde0836a8df7321447ee0fb6b22f5f4e38dc6cc0d666ac17ec`.

## Quyết định chính thức

- **`G0_READONLY_INVENTORY=PASS`**: script hoàn thành không lỗi, thiết bị/driver, ba môi trường PyTorch, công cụ và Git được kiểm kê. Chưa dispatch GPU.
- **`G0_BACKEND_RUNTIME=BLOCKED_CAPABILITY_UNCONFIRMED`**: không có PyTorch XPU khả dụng trong những môi trường được dò; chưa tìm thấy trình biên dịch SYCL, không có kiểm định Level Zero dispatch.
- **`P07=DESIGN_ONLY_BLOCKED_GPU_RUNTIME`**; `G1=NOT_IMPLEMENTED`, `G2=NOT_EXECUTED`, `P08=NOT_OPENED`. **Không cấp quyền cài đặt, biên dịch hay chạy kernel từ phán quyết G0**.
- Chỉ giữ **SYCL + Level Zero** là *kiến trúc ứng viên có điều kiện* (đọc trực tiếp page table), không phải backend khả thi đã xác minh. **PyTorch XPU** là ứng viên tích hợp và GPU-oracle, không thay thế yêu cầu kernel đọc KV qua bảng trang.

## Thiết bị và khả năng môi trường đã quan sát

| Hạng mục | Quan sát |
|---|---|
| CPU | Intel Core Ultra 7 258V |
| GPU | Intel Arc 140V (tích hợp), PnP `VEN_8086&DEV_64A0` |
| Driver | `32.0.101.8860` — ngày 25/06/2026 — trạng thái `OK` |
| Windows | **Windows 11 Home Single Language**, version `10.0.26300` |
| RAM trống / D: trống | `13.668 GiB` / `34.563 GiB` tại thời điểm dò |
| Python 3.12.10 | PyTorch `2.11.0+cpu`; XPU unavailable; count 0 |
| Miniforge 3.13.12 | PyTorch `2.12.0+cpu`; XPU unavailable; count 0 |
| Conda cfcr-gpu-311, Python 3.11.15 | PyTorch `2.4.1+cpu`; `torch-directml` metadata `0.2.5.dev240914`, **chưa thử tính toán GPU** |
| Toolchain có sẵn | MSVC `cl.exe` 14.44.35207, CMake, Ninja |
| Toolchain chưa tìm thấy | `icx`, `icpx`, `dpcpp`, `sycl-ls`, `llvm-spirv`; thư mục oneAPI chuẩn không tồn tại |

Tên hiển thị GPU có chuỗi “16GB” nhưng **không được xem là 16 GiB VRAM chuyên dụng**: không có phép đo dedicated/shared memory để kết luận. “Không có trên PATH” không được viết thành “hoàn toàn không cài đặt”.

## Đối chiếu nhà cung cấp (kiểm tra ngày 08/11/2026)

- PyTorch tài liệu hỗ trợ Intel Core Ultra Series 2 **Lunar Lake** trên Windows 11 và có đường phân phối XPU độc lập; không đồng nghĩa những `+cpu` wheel hiện có sử dụng được Intel GPU. [Tài liệu PyTorch](https://docs.pytorch.org/docs/main/notes/get_start_xpu.html).
- Intel có DPC++/SYCL chạy Windows và GPU Intel Arc; tuy nhiên **yêu cầu hệ thống oneAPI DPC++/C++ 2026 liệt kê Windows 11 Pro/Enterprise cho client GPU**, trong khi máy thực tế là **Home Single Language**. Do đó support/qualification chính thức trên đúng OS này là **CHƯA ĐƯỢC CHỨNG MINH**. Không tự suy ra Home không thể chạy kỹ thuật. [Yêu cầu hệ thống Intel 2026](https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-dpcpp/2026.html).
- Intel Triton XPU trên Windows hiện có hướng dẫn **experimental, source build**, và danh sách card ví dụ không ghi Arc 140V; **không chọn làm backend chính**. [Intel Windows Triton](https://github.com/intel/intel-xpu-backend-for-triton/blob/main/.github/WINDOWS.md).
- DirectML chỉ xuất hiện qua metadata một package trong môi trường Python 3.11. Không có phép đo DirectML GPU thực chạy, và kể cả chạy được cũng không tự chứng minh yêu cầu P07 “direct paged-KV” custom kernel.
- CUDA không thuộc đường thực hiện GPU Intel này.

## Tính nhất quán Git

- Biên bản G0 pin `expected_remote_main=4731f75cda6aa86b1dd2929b3f10d11fbbed0812` và mốc **design-before-contract** `a1a5fde085bacce834656c0d5140e1cb5b433b51`, tương thích với lịch sử nhánh P07. HEAD hiện tại trước quyết định G0 là `6c55a220bb5931fc14f823a2e241b21ff8d5867b` do đã append hợp đồng kỹ thuật; **không phải sai nguồn G0**.
- Máy báo origin đúng `https://github.com/minhtri22/TokenToModel-Lab.git`, local `main` còn ở `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`, tracked changes `false`. Chưa fetch, checkout, merge hoặc cập nhật local; không tự động thay HEAD.
- Các nguồn P01–P06, hợp đồng P07 G1 và `lineage.md` bất biến. Không dùng F1/TEST, không chạy E0, không tạo P08.

## Hướng khắc phục gọn, chưa được cấp quyền thực thi

**`TTM_P07_G0_CAPABILITY_GAP_ISOLATED_ENABLEMENT_PLAN_NO_INSTALL`**:

1. **Đóng G0 ở phạm vi kiểm kê** và giữ duy nhất một capability gap cho runtime GPU. Không mở gate riêng cho những kiểm tra kỹ thuật nhỏ.
2. Trước mọi thay đổi môi trường, soạn phương án môi trường thử tách biệt trong đúng dự án: kiểm tra rủi ro Windows 11 Home vs Intel validation matrix, lựa chọn PyTorch XPU wheel cho GPU-oracle, và đường SYCL compiler/Level Zero cho direct-paged kernel. Không cài vào Python 3.12 gốc hay Miniforge base, không nâng driver khi chưa có bằng chứng cần thiết.
3. Trình chủ dự án **một quyết định xin phép riêng** nếu cần tạo môi trường/ tải wheel/ cài oneAPI. Báo cáo dung lượng dự kiến, chính xác đường dẫn D:, công cụ/phiên bản/SHA, rollback và ảnh hưởng tới môi trường hiện có. Chỉ khi được chấp thuận mới thực hiện một lượt capability qualification nhỏ theo đúng P07; nếu không, giữ `BLOCKED_CAPABILITY`.
4. Sau khi chứng minh XPU/SYCL thực sự có compute device và cách truy cập paged KV trực tiếp, mới xem xét G1 implementation/QA. G2 benchmark và P08 vẫn đóng. Nếu GPU runtime không đủ, báo FAIL hoặc BLOCK, không chuyển CPU mock thành bằng chứng GPU.

**Phán quyết cuối:** `G0_INVENTORY=PASS`; `G0_BACKEND=BLOCKED_CAPABILITY_UNCONFIRMED`; `P07=DESIGN_ONLY`; `P08=NOT_OPENED`.
