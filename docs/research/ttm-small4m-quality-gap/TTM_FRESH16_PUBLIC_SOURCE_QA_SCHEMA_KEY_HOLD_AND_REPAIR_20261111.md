# TTM FRESH16 — HOLD kỹ thuật và sửa lỗi metadata danh mục lịch sử

**Ngày:** 2026-11-11  
**Trạng thái trước sửa:** `HOLD_TECHNICAL_OFFLINE_UNIT_QA_7_PASS_2_ERROR`  
**Trạng thái sau sửa nguồn:** `PATCHED_NOT_YET_EXECUTED_ON_WINDOWS`

Chủ dự án đã chạy PowerShell 5.1 ở nhánh FRESH16; SHA checkpoint cục bộ bước 1.024 và 1.280 đều `PASS`. Trong **9 bài kiểm thử nguồn**, 7 bài PASS; `test_counts_and_sources` và `test_repeated_intervention_word_uses_last_occurrence` đều dừng với `KeyError: 'source'` tại hàm `assess_public()`.

**Nguyên nhân đã xác định:** danh mục lịch sử `TTM_FRESH16_ALLOWED_PUBLIC_HISTORICAL_PROMPTS_20261111.json` có `sources[].name`, `sources[].git_blob_sha`; mã nguồn cũ lại yêu cầu `sources[].source`. Đây là sai lệch khóa schema do bộ kiểm định, không phải lỗi trong prompt, dữ liệu BPE, checkpoint hoặc kết quả khoa học.

**Sửa nguồn tối thiểu:** chỉ đổi `x["source"]` thành `x["name"]` tại vòng lặp tạo `hdict`. Bổ sung kiểm thử schema dương tính và kiểm thử từ chối tên nguồn bị sửa. Các khóa Git blob của Q1/FRESH12, 16 prompt, thang điểm, H1 ≥12/16, H2 ≥6/8 và các checkpoint SHA giữ nguyên.

**Giới hạn quan sát:** bộ QA tích hợp BPE + checkpoint **chưa chạy** vì unittest đã dừng trước khi gọi. Không có `_tmp/ttm_fresh16_integrated_offline_review_20261111` được tạo bởi lượt chạy lỗi; nếu thư mục tồn tại sau đó phải kiểm tra và giữ nguyên, không ghi đè. Bộ thử nghiệm sau sửa cần chạy offline trên Windows trước khi được gán `PASS`. Đây là sự cố kỹ thuật, **không ghi FAIL khoa học vào `lineage.md`**.

**Bước thực hiện tiếp theo:** fast-forward nhánh FRESH16 đúng commit sửa, giữ worktree sạch, chạy lại **duy nhất** QA offline tích hợp; không training/inference, không TEST; reviewer custody vẫn HOLD tới khi có xác nhận độc lập.
