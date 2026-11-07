# TTM P06 — CPU Paged KV Manager và QA tổng hợp ngoại tuyến

Ngày: 2026-11-07. Nhánh kế thừa P05 merge `e35a9d179e9ee3584bf2bc3f34cbfe1b6c3d88ec`. Mã và kiểm thử P06 được tạo trên nhánh hiện có `feature/p06-paged-kv-manager-20261107` mà không sửa P00–P05.

## Triển khai

`src/p06/paged_kv_manager.py` cung cấp `PagedKVCache` CPU float32: vật lý `[layers, K/V, blocks, block_size, heads, head_dim]`, page table riêng cho mỗi `request_id`, allocate/write/read/release, xóa khối trước tái sử dụng, thống kê allocated/reserved/logical/fragmentation. Bộ decode `paged_forward_tokens` dùng đúng mô hình P02, kiểm tra thiếu trang và giới hạn ngữ cảnh **trước khi thêm một lượt token**; không sửa P05 hoặc P02.

Không có prefix sharing, GPU kernel, PagedAttention CUDA/Vulkan hoặc runtime production.

## QA chính và độc lập

- `tests/p06/test_paged_kv_manager.py`: **8/8 PASS** ở CPU, gồm logits so P05/P02 (LayerNorm/RMSNorm), trang xen kẽ/giải phóng/không rò KV, phân mảnh, hết block không đột biến trạng thái, dữ liệu/dtype sai bị từ chối, page-table read-only, append theo nhóm tương đương từng token, đo thời gian và số byte.
- `tools/p06/independent_paged_kv_qa.py`: **5/5 PASS**, dùng tính `torch.nn.functional.scaled_dot_product_attention` cho tham chiếu toán học độc lập; P00 paged reference được khóa Git blob `ead322ff7559686cd8989264506cee6dd54c7441`. Các phép thử thêm xác minh cách ly, phân mảnh, từ chối OOM và CPU benchmark.
- Python 3.13.5, PyTorch 2.10.0+cpu. Raw log SHA: unit `e97b79238d6da06fb86683a67d12521f3ac4ab6e34d54a4e5af91df0b1c0767f`, independent `0f8e85ed746a4f7efec010c7c4122a674d278501090aa5778fc541052cb876cc`.
- Ban đầu bộ checker ngoại tuyến **FAIL ở chính oracle thử nghiệm** (sai reshape QKV và tham chiếu P00 tạm là stub); đã sửa checker và khôi phục P00 theo exact Git blob rồi chạy lại PASS. Không sửa mã P06, không tiêu thụ lượt khoa học.

## Phạm vi và benchmark

- Bộ đo trên tải 7 token, hai lượt, block size 3: Dense pool 65.536 byte, Paged pool 67.584 byte, logical KV 7.168 byte, phân mảnh 2.048 byte. Thời gian CPU thu thập trong JSON evidence, **không xác nhận P06 nhanh hơn P05**.
- TEST thật không được đọc, corpus F1 không được dùng, E0 không chạy lại; P07 kernel GPU chưa mở.
- Kết quả chỉ **`OFFHOST_SYNTHETIC_QA_PASS_13_OF_13`**; `P06_WINDOWS_QA=NOT_EXECUTED`, `P06_TECHNICAL_CLOSURE=PENDING`.
- `lineage.md` bất biến (QA kỹ thuật chứ không phải kết quả khoa học về tổng quát).

## Tiếp theo

Một lượt QA tích hợp Windows từ exact Git HEAD, kiểm SHA Python/P00/P02/P05, chạy 8 unittest + 5 independent, ghi raw stdout/stderr + SHA vào `evidence/p06`, cleanup đúng worktree đã tạo. Chỉ sau khi QA Windows và phán quyết độc lập PASS mới xét PR merge và mở P07. Không đặt giấy phép riêng cho từng kiểm thử nhỏ.
