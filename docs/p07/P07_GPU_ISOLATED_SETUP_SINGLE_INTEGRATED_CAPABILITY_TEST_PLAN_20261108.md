# TTM P07 — Kế hoạch tối thiểu môi trường GPU và một lần kiểm định tích hợp

Mã công việc: `TTM_P07_GPU_ENVIRONMENT_SETUP_AND_SINGLE_INTEGRATED_CAPABILITY_TEST_PLAN`. Ngày khóa: 2026-11-08. Trạng thái: **PLAN_LOCK_ONLY / NO_INSTALL / NO_GPU_DISPATCH**.

## 0. Quyết định ngắn

Không kiểm kê lại thiết bị, driver, OS, Python hiện có. G0 đã ghi nhận Intel Arc 140V (Core Ultra 7 258V), driver 32.0.101.8860, Windows 11 Home Single Language, ba PyTorch CPU-only và thiếu compiler SYCL trong PATH; RAM toàn hệ 32 GB. Những chứng cứ này đủ để **chọn hướng setup**.

Chọn trình tự tối thiểu: **một venv PyTorch XPU tách biệt → một GPU compute canary → nếu PASS, bổ sung chỉ compiler SYCL/Level Zero cần thiết → một canary truy cập page-table gián tiếp trực tiếp trên GPU**. Mỗi lần thực thi về sau chỉ tạo **một receipt tích hợp**, không tạo giấy phép riêng cho từng micro-check. Nếu một khâu FAIL thì stop; không tự đổi backend, driver, OS, hay chạy lại.

Đây là kế hoạch, **không có quyền cài đặt, tải, biên dịch hoặc thực thi GPU** ở commit này. Một quyết định chấp thuận phạm vi môi trường sẽ được yêu cầu trước lần thực thi thay đổi môi trường.

## 1. Mốc nguồn bất biến

- Repository `https://github.com/minhtri22/TokenToModel-Lab.git`; P06/main merge HEAD `4731f75cda6aa86b1dd2929b3f10d11fbbed0812`.
- P07 hiện trước commit kế hoạch `446824d823949043d4d4e6cf76d0a0884a49165f`. G0 inventory `artifacts/qa/p07/P07_G0_WINDOWS_READONLY_INVENTORY_AND_BACKEND_DISPOSITION_20261108.json`: `G0_INVENTORY=PASS`, `G0_BACKEND=BLOCKED_CAPABILITY_UNCONFIRMED`.
- P06 CPU paged oracle Git blob `4d52188adaf55674b6965513ea1beb38ec9a8e9b`, P05 dense `d835e5d7bb07fea447c5a869b13c70327ab05a53`, P02 `9762343e06cf800b50574c2871ae1ed58537fb18`.
- Local main theo G0 `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7` (cũ). **Không** đồng bộ trong G0/G0-enable; không fetch/pull/merge, không ghi đè local tracked/untracked changes. Khi cần code P07 mới, làm việc qua **owned temporary git worktree ở trong chính TTM project**, pin exact ref và không chạm checkout hiện hữu.

## 2. Phạm vi cài tối thiểu: hai thành phần theo điều kiện

### Nhánh A — PyTorch XPU (đi trước)

- Python seed: `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe` (Python 3.12.10) **chỉ làm trình tạo venv**; không pip install vào seed.
- Ứng viên đã xác nhận có wheel chính thức Windows x64/cp312: `torch==2.12.1+xpu`, từ `https://download.pytorch.org/whl/xpu`. Chỉ cần torch và dependencies thực sự được resolver yêu cầu; **không cài torchvision, torchaudio, Triton, IPEX, DirectML hoặc OpenVINO** trong thử này.
- Bước cài được phép về sau phải pin tất cả wheel name/version/size/SHA-256 vào wheel manifest **sau khi tải nhưng trước khi pip install**, cài offline từ chính wheelhouse; fail nếu resolver yêu cầu nguồn chưa pin hoặc phiên bản sai. Không fallback sang wheel CPU hay nightly.
- PyTorch XPU Windows supports Intel Core Ultra Series 2 Lunar Lake theo [PyTorch docs](https://docs.pytorch.org/docs/main/notes/get_start_xpu.html). Điều này không đảm bảo cặp driver/OS thực tế PASS.

### Nhánh B — compiler SYCL/Level Zero (chỉ khi A PASS)

- Phiên bản ứng viên: **Intel oneAPI DPC++/C++ Compiler 2026.2.0 standalone**, cùng các thư viện tối thiểu cần để compile/execute SYCL, không cài toàn bộ oneAPI Toolkit/Deep Learning Essentials nếu không bắt buộc.
- Nguồn chính thức: [Intel release notes](https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-dpcpp/2026.html) và [Standalone tools](https://www.intel.com/content/www/us/en/docs/oneapi-toolkit/installation-guide-windows/latest/install-standalone-tools.html).
- DPC++ 2026 ghi ~3 GB tối thiểu cho compiler+libraries và có thể cần thêm 6 GB tạm. Chỉ tải/install sau khi XPU GPU dispatch thực hoạt động.
- **Windows 11 Home Single Language** không nằm trong ma trận **Windows 11 Pro/Enterprise** cho client GPU của compiler 2026.2: đây là rủi ro unsupported validation, **không phải kết luận chắc chắn phần mềm không chạy**. Không nâng cấp OS. Nếu installer không chấp nhận OS hoặc không cho scope cài an toàn, dừng `BLOCKED_OS_OR_INSTALL_SCOPE` và báo bằng chứng.
- **Không có bằng chứng installer Intel 2026.2 có thể bảo đảm toàn bộ ghi tệp/registry chỉ nằm trong D**. Dùng đích cài D: nếu installer hỗ trợ. Trước khi thực thi cần xác nhận lựa chọn install scope thật sự và phần ghi ngoài D do hệ thống yêu cầu; nếu không chấp nhận được thì dừng **trước** khi cài. Không xóa thư mục hệ thống bằng PowerShell.

## 3. Phân vùng trong workplace và giới hạn tài nguyên

Project owner root: `D:\WORK\RESEARCH\TokenToModel-Lab`. Tất cả venv/wheelhouse/tmp/receipt cho lần enablement phải nằm dưới đây:

| Đối tượng | Đường dẫn trong project |
|---|---|
| Python isolated venv | `_runtime\p07\venv_xpu_cp312` |
| Wheelhouse/download | `_runtime\p07\wheels` |
| Temp/build/cache | `_runtime\p07\tmp` |
| Target Intel oneAPI (nếu vendor hỗ trợ) | `_runtime\p07\oneapi` |
| Evidence vĩnh viễn | `evidence\p07\gpu_enablement` |

Một số installer Windows có thể ghi metadata hệ thống, Registry hoặc cache ngoài D dù đích file ở D; phải ghi rõ trước khi thực thi, không hứa hoàn nguyên tuyệt đối bằng xóa thư mục.

- Snapshot G0: D free 34.563 GiB, RAM free 13.668 GiB; không dùng số này thay cho tiền kiểm dung lượng tại lúc tải.
- **Ngân sách kế hoạch** (không phải kích thước đo thực tế): tối đa 6 GiB cho nhánh A (venv + wheels + cache), tối đa 12 GiB bổ sung cho nhánh B (compiler + installer + temporary), tổng phát sinh không quá 18 GiB.
- Yêu cầu an toàn trước download: D free >= 24 GiB, RAM free >= 8 GiB; luôn để lại >= 12 GiB D free, nếu không thì STOP; không xóa dữ liệu khác để lấy chỗ.
- Chuyển tạm `TEMP`, `TMP`, `PIP_CACHE_DIR` sang `_runtime\p07\tmp` **chỉ trong process con**, dùng `pip --no-cache-dir` khi phù hợp; không sửa env vars người dùng, PATH toàn hệ, Python seed hoặc driver.
- Không build PyTorch hay Triton từ source; không thử CUDA. Nếu build/toolchain biến thành yêu cầu ngoài ngân sách, dừng và báo quyết định backend lại.

## 4. Một lượt kiểm định tích hợp duy nhất sau khi được chấp thuận

**Cùng một runner và một receipt, từng phần fail-closed:**

- **A1 — venv/wheel integrity:** validate Python 3.12, wheel list/hashes, `torch.__version__` thực sự có `+xpu`; tuyệt đối không import CPU torch từ môi trường gốc.
- **A2 — GPU compute canary:** `torch.xpu.is_available()==True`, `device_count>=1`, device name trỏ Intel, tạo tensor float32 nhỏ trên `xpu`, chạy cộng/nhân ma trận hoặc softmax, `torch.xpu.synchronize()`, tải kết quả về CPU, sai số `atol/rtol <= 1e-5` so với oracle CPU, tensor finite. Đây chỉ là GPU compute smoke, không phải P07 production kernel.
- **B1 — SYCL device/compiler:** khi A2 PASS, xác minh `icx/icpx`, `sycl-ls` cho thấy GPU Level Zero/Intel phù hợp. Nếu không xuất hiện thì fail có bằng chứng; không thay OS/driver.
- **B2 — one tiny direct-index canary:** compile/run một nguồn SYCL tổng hợp, có `page_table` và physical KV pool nhỏ, đọc `p=page_table[j/B], o=j%B` **trực tiếp qua bảng trang trên GPU**; không gather toàn bộ thành dense tensor trước. Đối chiếu giá trị lấy được với CPU oracle độc lập và dùng hai request xen kẽ để kiểm tra không cross-request. Không dùng P01–P06 datasets/checkpoints.
- **STOP/R1:** tổng hợp kết quả A1/A2/B1/B2 một lần dưới `evidence\p07\gpu_enablement`, ghi: Python, wheel SHA256, compiler/installer SHA256, OS caveat, device name, driver unchanged, exit codes, oracle delta, memory/disk before/after, cleanup status. `PASS_XPU_AND_SYCL_DIRECT_INDEX` cho phép **xét mở** G1 implementation theo hợp đồng đã khóa; mọi FAIL giữ `P07_DESIGN_ONLY`. Không tự rerun, không nhảy backend thay thế.

Chỉ kiểm định sự tồn tại của hai khả năng GPU compute/XPU và **direct physical page-table read**, chưa chứng minh P07 PagedAttention numerical parity đầy đủ hoặc speedup. G1 còn cần attention/logits parity, negative QA, độc lập; G2 còn yêu cầu benchmark cùng GPU/dtype/load.

## 5. Quy trình giữ nguyên quản trị

1. Bản kế hoạch này là **một** quyết định kỹ thuật cho capability-gap, không mở tiếp nhiều mini-permits.
2. Chỉ sau chấp thuận cài/tải/dispatch mới triển khai runner tương ứng. Có SHA pin cho nguồn và một receipt tích hợp; không sửa `lineage.md` cho QA cài đặt.
3. Trường hợp FAIL: giữ evidence, ngừng, chỉ dọn đúng `_runtime\p07\tmp` và owned worktree đã tạo, có path/sentinel và scope checks; không xóa wheelhouse/venv hoặc oneAPI trước quyết định rollback rõ ràng. Nếu installer có state ngoài project, dùng uninstaller do vendor hỗ trợ, không manual recursive deletion.
4. Không thay `main`, không đụng P01–P06/E0/F1 TEST. Không mở P08 trước khi P07 kernel QA, GPU matched-load benchmark, adjudication và merge.

**Phán quyết kế hoạch:** `PLAN=LOCKED`; `A/B_INSTALL=NOT_AUTHORIZED`; `XPU_CANARY=NOT_EXECUTED`; `SYCL_CANARY=NOT_EXECUTED`; `G1/G2=NOT_OPENED`; `P07=DESIGN_ONLY_CAPABILITY_GAP`; `P08=NOT_OPENED`.

**Bước thực hiện tiếp theo:** `TTM_P07_SINGLE_ISOLATED_GPU_ENABLEMENT_AUTHORIZATION_AND_RUNNER` — một quyết định cho đúng phạm vi setup+canary, rồi một lượt thực thi; không tái kiểm kê phần cứng.
