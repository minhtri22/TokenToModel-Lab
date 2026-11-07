# TTM P05 — Khóa phạm vi tối thiểu Dense KV Cache (CPU)

Ngày 07/11/2026. Cơ sở: GitHub main merge P04 `88bde037705607730cfc24e36875aa865d3a380c`. P04 đã PASS trong phạm vi synthetic CPU; đánh giá ngôn ngữ thật vẫn chưa thực hiện.

## Mục tiêu theo `docs/PHASE_PLAN.md`

P05 phát triển bộ nhớ Key/Value liên tục (Dense KV Cache) cho đường suy luận từng token, sau đó:
1. Đối chiếu logits **từng vị trí** với đường P02 không cache (no-cache full causal forward).
2. Kiểm thử xen kẽ nhiều request, chống lẫn KV, giới hạn độ dài và dung lượng, release/reuse.
3. Đo thời gian giải mã tuần tự trên **cùng workload**, bytes KV cấp phát và bytes logic sử dụng. Không kết luận tăng tốc khi chưa có đo lặp lại và kiểm soát cấu hình.
4. QA riêng trên Windows CPU và bộ kiểm định độc lập trước khi xét đóng P05.

Không thay kiến trúc P00–P12; P06 mới dùng bộ nhớ phân trang (Paged KV); P07 mới tính GPU kernel, P08 batching.

## Mẫu mã ứng viên đã kiểm thử ngoài máy Windows (NOT YET COMMITTED)

Ba tệp mẫu nằm trong gói đính kèm hội thoại `TTM_P05_DENSE_KV_SYNTHETIC_CANDIDATE_20261107.zip`:
- `src/p05/dense_kv_cache.py`: SHA-256 `45e3b2e153a4d37578a5dfacc86a313a5026c89eba13fcff41b59a0143b50412`; Git blob khi commit chính xác dự kiến `d835e5d7bb07fea447c5a869b13c70327ab05a53`.
- `tests/p05/test_dense_kv_cache.py`: SHA-256 `616638f65de58008245c059ffcae4114898f7985296b505cb5209b6b8f84598f`; Git blob dự kiến `2fa25a579a600b3c80c28ac7ef07b253805e3490`.
- `tools/p05/independent_dense_kv_qa.py`: SHA-256 `3da42c253daebf6cde229ebeaf305263c370fbdf23133582e9271b480b300d97`; Git blob dự kiến `2e318b38b0a4e5a33a407515908d31d0c7d32e6d`.

ZIP SHA-256 `d508405b693bfb386f8dd16130c293cd8c4e984480984ae9db546b7e04c2304a`.

**QA ứng viên ngoại tuyến**: 6/6 unit PASS và 4/4 kiểm tra độc lập PASS, PyTorch 2.10.0+cpu. Các phép thử dùng **token ID tổng hợp** kể cả 256/1024/2047; không đọc WP30, TRAIN, TEST hoặc checkpoint. Đối chiếu SDPA tham chiếu, full forward no-cache, can thiệp request, byte accounting. Đã đo 2 lần trên chuỗi sáu token; kết quả chỉ minh họa khả năng thu thập số đo, không phải baseline hiệu năng Windows.

## Ranh giới và trạng thái

`P05=OPEN_DESIGN_AND_OFFHOST_CANDIDATE`, `P05_WINDOWS_QA=NOT_EXECUTED`, `P05_FORMAL_ADJUDICATION=PENDING`. Gói source hiện chỉ tồn tại dưới dạng artifact đính kèm hội thoại, **chưa được commit vào GitHub**. Tệp này là hồ sơ thiết kế, không được diễn giải thành kết quả kiểm định source HEAD.

`P01_E0=UNCHANGED_NO_RERUN` · `P02/P03/P04=MERGED` · `P06=NOT_OPENED` · `lineage.md=UNCHANGED`.

**Bước thực hiện tiếp theo:** `TTM_P05_EXACT_SOURCE_IMPORT_TO_BRANCH_AND_WINDOWS_CPU_INTEGRATED_QA` — nhập chính xác ba tệp mã ứng viên vào nhánh P05, đối chiếu SHA, chạy gói QA Windows CPU rồi độc lập adjudication. Không mở thêm giấy phép cho từng phép kiểm tra nhỏ.
