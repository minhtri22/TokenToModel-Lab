# TTM-Small-4M / EmbeddingGemma 2 SEMANTIC4X3 — H768 niêm phong nguồn thực, kiểm kê tài nguyên trước CLAIM
**Ngày:** 2026-11-10. **Thao tác:** `TTM_SMALL4M_EMBEDDINGGEMMA2_SEMANTIC4X3_H768_REAL_SEAL_AND_RESOURCE_PREFLIGHT_SINGLE_BATCH`.

## Kết quả xác minh

- H768 được owner niêm phong bằng script frozen `ttm_semantic4x3_h768_one_shot_source_seal.py` tại Git blob `ac11b9c7cb7403d5dc222dbfcda866d43f705e29`, SHA256 `40197872225dde9cc17b0c098ade1918017b3e25d79d159ec92918a0c7de3ce6`.
- Fixture CPU `PASS_4_CHECKS`, source selector executed once in Windows project root; không chạy GPU, inference, training hoặc tạo CLAIM.
- **Real H768: `H768_SEALED_NOT_SCORED`**; 768 truyện, 1000 cửa sổ, 186655 target labels. `excluded_exact_source_count=1159` trong stream valid (không phải tổng số tập được exclusion); near-duplicate counts: 0 pair với 2048 T1 TRAIN, 0 pair với 256 T1 VAL, 0 pair nội bộ.
- Không mở/giải mã nội dung historical TEST64, L0017 H320, L0019 H512. Các tập cũ này chỉ được loại trùng exact SHA; near-dup với chúng và donor-pretraining contamination **chưa được loại trừ**. H768 vẫn TinyStories-valid cùng miền.
- **Public seal SHA256:** `9725b1254cde81b77e23b85ab479a08cafc14af0a7a536c7722ca87c7f2a5aa0` (đã tính lại độc lập từ cấu trúc JSON canonical). **Private H768 membership:** `0ab671ae59ff4300d8257f2689261d6328afd7563c0aa66b363bc22348c1628f`. **Private H768 windows pack:** `1eb5b54b4bb7744e23fffd0fd755d5c91853a773dcc0d2219f777b47ba6a53df`. Các SHA private chỉ là receipt do selector tạo; chưa tải và hash lại riêng hai binary private.
- Đã đọc lại `H768_PUBLIC_SEAL.json` trực tiếp từ Windows bằng kết nối RemoteDesktop (readonly), đối chiếu payload với log owner và source frozen; file tương đương canonical compact UTF-8 JSON + newline, Git blob `3597bce6ad5330cef1e3aaf67fd87d8d01c0c578`.
- Files private bất biến trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_semantic4x3_h768_seal_v1_20261110\`: `H768_MEMBERSHIP_PRIVATE.json` và `H768_WINDOWS_PRIVATE.npz`. **Không** đưa story SHA IDs, plaintext, per-story labels/loss, weights hay input private lên GitHub.
- Đây là kết quả khóa **dữ liệu nguồn**, không phải kết quả khoa học PASS/FAIL. Không thêm mục vào `lineage.md`; L0017/L0018/L0019 không thay đổi.

## Trạng thái thực thi SEMANTIC4X3

- Frozen protocol V2 `docs/pilot/TTM_GEMMA2_SEMANTIC4X3_INTEGRATED_PREREG_SOURCE_RESOURCE_DECISION_20261110.md` giữ nguyên. Bốn arms × ba seed, checkpoint base1024 và donor cũ, 2048 updates × 4096 target labels mỗi arm; `tau_residual` và `gamma_real` co-primary; H768 mới vẫn được niêm phong chính xác một lần. **Chưa có quyền train**.
- Các nguồn hiện trên GitHub là **QA donor null** và **selector H768**, chưa có runner science 12-arm đầy đủ, chưa có GPU preflight mới và chưa tạo one-shot CLAIM hoặc train scientific.
- Hợp đồng lưu đầy đủ 8 checkpoint READY/arm, 12 arms. Theo kích cỡ checkpoint CAUSAL6 F **52947341 bytes**, dự toán bắt buộc 5082944736 bytes (~4.73 GiB), **chưa** gồm H768 private, nguồn ZIP, log và margin 1 GiB.
- Cổng frozen yêu cầu **>=6 GiB trống thật trên Google Drive ngay trước CLAIM**, và free quota thực phải vượt mandatory writes + 1 GiB margin. Lúc báo cáo, **chưa xác minh được quota hiện thời** bằng kết nối; số 6 GiB owner từng khai báo trước CAUSAL6 không được phép dùng thay số đo hôm nay. GPU Colab Free Tesla T4 **chưa được kiểm trên phiên thực thi mới**.
- **Resource verdict `HOLD_UNVERIFIED_CURRENT_DRIVE_FREE_AND_T4`**. Không tự giảm budget, không tái sử dụng H512 để tránh tạo H768 mới, không xóa checkpoint cũ để ép quota. Không làm thêm một chuỗi micro-permit; tiếp theo triển khai runner tích hợp duy nhất và preflight toàn bộ điều kiện trước CLAIM.

## Kết luận và bước thực hiện tiếp theo

`H768_SOURCE=SEALED_PASS` · `PUBLIC_SHA256=PASS` · `PREREG_V2=FROZEN` · `RESOURCE=HOLD` · `RUNNER_4X3=NOT_IMPLEMENTED` · `SCIENCE_CLAIM=NOT_CREATED` · `L0019=PRESERVED`.

**Next:** `TTM_GEMMA2_SEMANTIC4X3_12_ARM_INTEGRATED_RUNNER_SOURCE_QA_AND_COLAB_FREE_T4_RESOURCE_PREFLIGHT`. Trước CLAIM phải lấy chỉ số Drive StorageQuota hiện tại, pin/check toàn bộ H768 private, 3 TRAIN schedules / 12 arm initializations, source/checkpoint, independent reviewer và kiểm CUDA GPU. Chưa chạy science hay cho phép tự chạy ô one-shot.
