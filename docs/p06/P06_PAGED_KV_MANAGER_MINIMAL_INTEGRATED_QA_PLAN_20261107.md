# TTM P06 — Mở nhánh Paged KV Manager, kế hoạch tích hợp tối thiểu

Ngày 2026-11-07.

## Phạm vi và mốc nguồn

- P05 đã được hợp nhất bằng PR #9 ở đúng `main` commit `e35a9d179e9ee3584bf2bc3f34cbfe1b6c3d88ec`. P05 có kết quả kiểm định Windows CPU synthetic với 6 unittest và 4 independent Python PASS, nhưng runner PS5.1 V1 ghi **FAIL_OR_INCONCLUSIVE** do lỗi diễn giải số thuộc tính. Phán quyết đối chiếu chính thức `PASS_SCOPED_CPU_WITH_RUNNER_V1_FALSE_NEGATIVE`; không sửa biên bản FAIL.
- P05 oracle: `src/p05/dense_kv_cache.py`, Git blob `d835e5d7bb07fea447c5a869b13c70327ab05a53`.
- P00 reference paged implementation: `reference/phase0/paged_kv.py`, Git blob `ead322ff7559686cd8989264506cee6dd54c7441`. P00 là tham chiếu kiểm tra chức năng; không được gọi là PagedAttention GPU tối ưu.
- Bắt đầu P06 theo `docs/PHASE_PLAN.md`: Block Pool (kho khối), Block Table (bảng trang), cách ly nhiều yêu cầu, đối chiếu P05, đo phân mảnh và nhiều yêu cầu.
- Chưa triển khai code P06, chưa tạo PR hoặc cấp kết luận P06 PASS trong commit mở nhánh này.

## Hợp đồng tối thiểu cho P06

1. **Nguồn dữ liệu:** chỉ token ID tổng hợp `[0, 2047]`, CPU float32; không đọc 30 bài Wikipedia F1, không đọc TEST thật, không chạy P03/huấn luyện.
2. **Bộ quản lý trang:** pool vật lý theo block, page-table riêng từng `request_id`, `allocate`/`write`/`read`/`release`, không dùng GPU kernels.
3. **Kiểm tra số học:** với các chuỗi đủ độ dài để vượt ranh giới block, logits decode từng bước của P06 đối chiếu **P05 Dense KV** và decoder P02 không cache, cùng cấu hình/weights. Không làm thay đổi source P05.
4. **Cách ly và vòng đời:** hai yêu cầu xen kẽ, phân trang độc lập, không đọc chéo KV; release/reuse phải xóa dữ liệu cũ; negative QA cho request trùng, context quá dài, hết block, vị trí chưa cấp phát và lỗi layer/shape.
5. **Bộ nhớ/phân mảnh:** ghi tổng block, free/used, số token, số byte cấp phát và tổn phí phân mảnh nội bộ `allocated_slots - live_tokens`. Phân biệt overhead quản lý với tăng tốc. Kiểm tra không có block leak sau release.
6. **Tải nhiều yêu cầu:** ít nhất hai tình huống phân bổ/tái sử dụng xen kẽ; không suy diễn thông lượng đa GPU từ các thử nghiệm này.
7. **Thời gian:** đo P05 Dense và P06 Paged cùng tải và cùng máy, số lần chạy/bản PyTorch ghim vào receipt. Không tuyên bố `speedup` nếu không có kiểm định và đối chứng hợp lệ.
8. **QA độc lập:** một bộ unit và một checker độc lập với phép tính `torch.nn.functional.scaled_dot_product_attention` cho chuỗi decode ngắn; ngừng nếu logits hoặc cách ly FAIL.

## Quy trình gọn

- Một commit nguồn P06 + unit + independent checker + config.
- Một lượt QA tích hợp ngoại tuyến trên dữ liệu tổng hợp; khi PASS, một gói Windows PowerShell 5.1 ghim SHA/git blob và chỉ làm việc trong TTM workplace.
- Bằng chứng Windows gồm file JSON, stdout/stderr, thông số RAM/CPU, hash nguồn, kết luận QA; cleanup đúng worktree tạm được tạo, giữ FAIL/PASS.
- Một quyết định phán quyết gộp cho toàn P06; không mở giấy phép riêng cho từng kiểm thử kỹ thuật nhỏ.
- P07 kernel GPU chỉ được mở sau khi P06 được rà soát và hợp nhất. Không động `lineage.md` trừ khi phát sinh kết quả khoa học cần phán quyết, không ghi lỗi công cụ vào lineage.

## Trạng thái

`P01=FROZEN` · `P02=FROZEN` · `P03=CLOSED_SCOPED_CPU` · `P04=CLOSED_SCOPED_CPU` · `P05=CLOSED_SCOPED_CPU_WITH_RUNNER_FALSE_NEGATIVE` · `P06=OPEN_DESIGN_ONLY` · `P07=NOT_OPENED`.

**Bước thực hiện tiếp theo:** `TTM_P06_PAGED_KV_MANAGER_IMPLEMENTATION_AND_SYNTHETIC_CPU_QA`: triển khai bộ quản lý trang có đầy đủ âm tính; đối chiếu P05; không dùng corpus hoặc GPU.
