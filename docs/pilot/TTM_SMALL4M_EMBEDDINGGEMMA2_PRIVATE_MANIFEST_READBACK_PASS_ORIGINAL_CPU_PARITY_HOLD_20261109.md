# TTM-Small-4M × EmbeddingGemma 2 — Niêm phong private membership PASS có giới hạn

**Ngày:** 09/11/2026. **Nhánh:** `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`.

## Bằng chứng mới từ Windows

Chủ dự án chạy mã `TTM_ttm_gemma2_holdout_independent_readback.py`, SHA-256 `bb49af35a9b1ff04c58125ddc004538ad2067aef00701c0e09356fd03f692a40`, trực tiếp trên Windows bằng Python 3.12, trong workspace `D:\WORK\RESEARCH\TokenToModel-Lab`. Đã xác minh SHA-256 của script trước khi chạy. Hai phép chạy:

1. `--mode fixture-qa`: **8/8 PASS** (chọn thứ tự băm, nguồn sai, trùng ID, rò nhóm cũ, bucket TEST cũ, trạng thái TEST đã chấm, đếm nhãn).
2. `--mode readback --repo <workspace>`: **`PASS_SCOPED_MANIFEST_INDEPENDENT_READBACK`**, băm độc lập byte của manifest riêng tư và khớp SHA-256 niêm phong `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`; kiểm tra đúng **320 truyện**, **75.798 nhãn**, **0 trùng ID** với nhóm TRAIN/VAL/TEST T1, **0** thuộc bucket TEST cũ. Báo cáo gốc ghi **2.119.489** truyện TRAIN đã quét; kiểm toán lần này đối chiếu con số đã ghi, không quét lại toàn bộ TRAIN.

**Phán quyết:** `PASS_SCOPED_MANIFEST_INDEPENDENT_READBACK`. Đây là kiểm tra danh sách và tính toàn vẹn nguồn đã khóa, **không chấm mô hình**, **không chứng minh không có dữ liệu nhiễm bẩn**, **không mở TEST cũ** và **không cập nhật kết quả khoa học trong `lineage.md`**.

## Nguồn công khai để tái tạo kỹ thuật

- `tools/embeddinggemma2_swap/ttm_gemma2_independent_membership_readback_20261109.py`, SHA-256 `bb49af35a9b1ff04c58125ddc004538ad2067aef00701c0e09356fd03f692a40`.
- `tools/embeddinggemma2_swap/ttm_gemma2_independent_cpu_checkpoint_binding_qa_20261109.py`, SHA-256 `016c2fdc8df2cab642b52f1c7111a5a6694944c8fd06e2cfd4d373d42a2dc438`. Đây là bộ dựng CPU độc lập dùng cho QA cấu trúc đã PASS trước đó, **không phải source mô hình GPU gốc**, do đó chưa đạt parity.
- `artifacts/qa/ttm-embeddinggemma2/TTM_NEW_HOLDOUT_WINDOWS_PRIVATE_MANIFEST_READBACK_20261109.json` là biên bản **không chứa 320 ID**, không có raw text, checkpoint hay logits.

## Giới hạn và bước tiếp theo

Bộ chấm CPU độc lập trước đó đã nạp A/B/C/D và kiểm tra token tổng hợp. Tuy nhiên không có chứng cứ từ lần này về kiểm tra số học giữa mô hình CPU dựng lại và **chính phiên bản GPU runner gốc** `ttm_directswap2048_gpu_once.py`, SHA-256 `0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e`. Nguồn gốc được lưu trong bộ ZIP nguồn frozen và được phép **trích xuất + hash + import** ở lần QA kỹ thuật kế tiếp; không được suy diễn PASS từ `strict_state_dict_load` hoặc `causal_prefix=0`.

Các giới hạn khoa học còn mở: không quét gần trùng độc lập lần hai với toàn TRAIN, không đối chiếu gần trùng văn bản với VAL/TEST lịch sử (giữ nguyên lệnh cấm đọc TEST), chưa xác minh donor EmbeddingGemma 2 có nhìn thấy nội dung này trong tiền huấn luyện hay không. Vì thế phát biểu xác nhận sau này chỉ được giới hạn trên **bộ checkpoint cố định và tập holdout đã khóa**, không suy diễn thành chứng minh nhân quả hoặc lặp training độc lập.

**Tiếp theo:** `TTM_SMALL4M_EMBEDDINGGEMMA2_ORIGINAL_RUNNER_CPU_SYNTHETIC_NUMERIC_PARITY_QA`. Chỉ trích xuất nguồn đã ghim và chạy một tập token giả lập trong CPU trên các checkpoint đã khóa; kiểm toán logits với tolerance định trước, đưa nguồn và biên bản lên repo nếu PASS. Không sử dụng 320 truyện mới, không chấm VAL/TEST, không chạy GPU, không huấn luyện, không mở/gộp nhánh khác, không sửa `lineage.md`.
