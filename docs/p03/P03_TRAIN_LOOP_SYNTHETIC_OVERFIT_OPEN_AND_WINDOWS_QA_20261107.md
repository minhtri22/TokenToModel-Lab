# TTM — P03: mở vòng huấn luyện và bài kiểm tra overfit tập rất nhỏ

Ngày: 07/11/2026. Base chính xác sau PR #6: `dd8e83658535daad02d008d1b6a959628336cf31`.

## Mục tiêu phạm vi P03 gốc

- Vòng huấn luyện (Training Loop) dự đoán token tiếp theo, AdamW optimizer, warmup/cosine LR scheduler, gradient accumulation, gradient clipping, kiểm tra NaN/Inf và mô hình thật cập nhật trọng số.
- Kiểm định micro-batch overfit trên **token ID tổng hợp**; chưa nạp nguồn Wikipedia, không chạm tập TEST, không làm checkpoint (P04).
- Đầu vào bắt buộc tensor `int64 [batch,time]` với ID `0..2047` đúng model P02; từ chối sai kích thước, ID và cấu hình.

## Đã triển khai

`src/p03/train_loop.py`, `tests/p03/test_train_loop.py`, `tools/p03/independent_p03_qa.py`, pin git blob/SHA ở biên bản `artifacts/qa/p03/P03_SYNTHETIC_TRAIN_LOOP_OFFHOST_QA_20261107.json`.

Bộ QA trên CPU ngoài máy người dùng, Python 3.13.5, PyTorch 2.10.0: **6/6 unit PASS**, **7/7 independent checker PASS**. Các lỗi khởi tạo fixture và đường import checker ở lượt phát triển sơ bộ được ghi nhận ở biên bản QA, đã sửa và chạy lại tại tầng kỹ thuật; không phải lỗi khoa học.

Lượt thực sự cập nhật trọng số trên tập tổng hợp 2 mẫu × 6 token, 90 bước, `initial_loss=7.674461841583252` → `final_loss=0.01513530034571886`. Đây là **khả năng ghi nhớ fixture**, chưa phải kết quả học trên Wikipedia hay tổng quát hóa.

## Ranh giới bản quyền/khoa học

F1 WP30 chỉ được cấp cho `BPE_E0_ONLY` trong nguồn khóa P01, do đó **không nạp văn bản WP30 sang P03**. Nếu chủ dự án muốn huấn luyện GPT trên WP30, cần quyết định riêng về phạm vi sử dụng và ghi nguồn/quyền. Giữ dữ liệu TEST niêm phong đến P04 và chỉ mở P04 sau P03 đủ chứng cứ. `lineage.md` không bổ sung trong bước QA kỹ thuật này.

## QA Windows gộp một lượt

Chạy từ nhánh exact-head trong worktree riêng thuộc `D:\WORK\RESEARCH\TokenToModel-Lab`, Python 3.12.10 với PyTorch 2.11.0 CPU đã tồn tại, không cần Docker hoặc download:
- `python -B -m unittest discover -s tests/p03 -p test_*.py -v`: 6/6
- `python -B tools/p03/independent_p03_qa.py`: 7/7, giá trị loss và cập nhật trọng số.

Ghi SHA nguồn, HEAD, runtime, stdout/stderr và trả biên bản PASS/FAIL. Không tự động thay đổi main, xóa worktree ngoài phần do bộ chạy tạo, hoặc chạy lại P01 E0.

**Trạng thái**: `P02=CLOSED_SCOPED_CPU`, `P03=OPEN_CANDIDATE_OFFHOST_QA_PASS`, `P03_WINDOWS=NOT_EXECUTED`, `P04=NOT_OPENED`.

**Bước tiếp theo**: `TTM_P03_WINDOWS_CPU_SYNTHETIC_MICROBATCH_OVERFIT_INTEGRATED_QA` và thẩm định độc lập/merge nếu đạt.
