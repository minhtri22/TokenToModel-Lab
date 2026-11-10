# TTM SEMANTIC4X3 V2 — Hướng dẫn Colab tiền kiểm (không huấn luyện)

**Ngày:** 10/11/2026. **Trạng thái:** `RUNNER_SOURCE=IMPLEMENTED_QA_PASS_SCOPED` · `COLAB_GPU_PREFLIGHT=NOT_EXECUTED` · `OWNER_SCIENCE_AUTHORIZATION=NOT_GRANTED`.

## Thành phần đã khóa

- Mã chạy 4 arms × 3 seed: `tools/embeddinggemma2_swap/semantic4x3_v2/ttm_semantic4x3_runner.py`, SHA256 `9a824e453195cafc530e2289d3b8a87e354faf8905ca73b2f29b79144d657a8d`.
- Bộ kiểm độc lập: `ttm_semantic4x3_independent_readback.py`, SHA256 `51732bd62cfd13bf8956f11ee862b939d0dc78a62c58cd3d655dc05b566764e2`.
- Mã tạo null frozen: `ttm_semantic4x3_balanced_null_cpu_qa.py`, SHA256 `0d71f38da356056be50a18d36f589774190178fd321e6d2e3970413d96238a2d`.
- CAUSAL6 input ZIP **đang có** trên Drive `MyDrive/TTM/ttm-small-pilot/TTM_GEMMA2_CAUSAL6_INPUT_PRIVATE_V1_20261109.zip`, SHA256 `2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a`, notebook chỉ giải nén **bảy tệp nguồn** cần thiết, bỏ qua H512 cũ.
- H768 private nguồn bất biến đã niêm phong trên máy Windows: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_semantic4x3_h768_seal_v1_20261110\`. Public seal SHA256 `9725b1254cde81b77e23b85ab479a08cafc14af0a7a536c7722ca87c7f2a5aa0`.

## Cách chuẩn bị một lần

1. Tải `PACK_TTM_SEMANTIC4X3_H768_PRIVATE_V1.ps1` từ **commit phát hành đã khóa**, kiểm SHA source và chạy bằng PowerShell 5.1 trên Windows. Script chỉ **sao chép**, không tạo lại H768, không đổi private gốc, ghi ZIP trong `_tmp` của chính dự án. Kết quả: `TTM_SEMANTIC4X3_H768_PRIVATE_V1_20261110.zip`, chứa đúng `h768/H768_PUBLIC_SEAL.json`, `h768/H768_MEMBERSHIP_PRIVATE.json`, `h768/H768_WINDOWS_PRIVATE.npz`.
2. Upload ZIP duy nhất này vào Google Drive `MyDrive/TTM/ttm-small-pilot/` bằng giao diện Drive hoặc đồng bộ Drive; **không** tải lên GitHub. Không cần upload lại CAUSAL6 source ZIP.
3. Mở notebook `TTM_SEMANTIC4X3_FREE_T4_PRECLAIM_ONLY_20261110.ipynb` từ GitHub hoặc tải bản `.ipynb`. Chọn môi trường **Google Colab Free Tesla T4**. Chỉ chạy 3 ô Python theo thứ tự: (1) mount Drive + kiểm 7 SHA cũ và 3 SHA H768; (2) tải runner/reviewer/helper từ commit đã pin, fixture QA; (3) xác thực Drive **ngay trong preflight**, kiểm quota API, GPU T4 và synthetic smoke. Nếu gói hoặc quota bị HOLD, **không** bật huấn luyện.

**Notebook không chứa ô science execute**. `OWNER_VERIFIED_FREE_GIB=9.0` chỉ là attestation bảo thủ của owner (~10 GB thập phân), preflight vẫn bắt buộc hỏi `drive.about(storageQuota)` để xác thực free bytes ngay trước CLAIM. Nếu API chưa cấp quyền, `HOLD_DRIVE_QUOTA_UNAVAILABLE`, không giả PASS. Điều kiện frozen: khoảng trống >=6 GiB và >= 96 checkpoint × 52,947,341 bytes + 1 GiB reserve.

## Điều kiện PASS_PRECLAIM và ranh giới khoa học

- `TTM_SEMANTIC4X3_SOURCE_BUNDLE=PASS_SOURCE_SHA7_H768_SHA3`.
- `TTM_SEMANTIC4X3_SYNTHETIC_FIXTURES=PASS_NO_CLAIM`.
- `PREFLIGHT_EXIT_CODE=0` và `TTM_SEMANTIC4X3_PRECLAIM=PASS_NO_SCIENCE_CONSUMED`.

Cổng GPU kiểm một Tesla T4 với >=14 GiB VRAM reported, CUDA khỏe, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, forward–scalar-loss–backward trên synthetic 8×256 và peak allocated <12GiB. 4×3 khởi tạo nguồn và null đều kiểm CPU trước GPU smoke, 3 schedules riêng SHA; H768 chỉ đọc metadata/seal/hash, không giải mã nhãn cho scorer trước khi đủ 12 final READY.

Sau PASS, quyết định riêng của chủ dự án mới có thể mở `--mode execute --owner-science-approved` theo cùng RunID đã khóa. Không tự thêm cell execute, không chạy `Run all` sau khi đã CLAIM; nếu ngắt sau CLAIM, giữ nguyên marker để phân xử, không tạo run mới hoặc auto resume. Nếu đủ 12 READY và kết quả hoàn tất, dùng bộ readback độc lập để tính lại NLL/bootstrap mà **không huấn luyện và không gọi model.forward**, rồi mới phân xử PASS/FAIL và ghi lineage append-only.

**Giới hạn:** Free T4 không đảm bảo thời lượng liên tục cho 24.576 bước. Bộ chạy là mã nguồn thực, đã kiểm CPU, nhưng **chưa** kiểm GPU T4 mới, chưa huấn luyện và chưa xác thực đầy đủ H768 private NPZ trong Colab. `main`, L0017, L0018, L0019 không thay đổi, GGUF/application deferred.
