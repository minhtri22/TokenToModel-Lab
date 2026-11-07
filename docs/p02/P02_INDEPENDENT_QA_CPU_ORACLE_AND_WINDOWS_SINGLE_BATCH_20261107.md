# P02 — Kiểm tra độc lập CPU bổ sung (không có dữ liệu khoa học)

Ngày: 07/11/2026. Nhánh P02 giữ nguyên kiến trúc và config BPE 2048 token.

Thêm `tools/p02/independent_p02_qa.py` kiểm tra theo tuyến **khác** 6 bài unittest của tác giả:
- Attention theo PyTorch `scaled_dot_product_attention(is_causal=True)` đối chiếu q/k/v của lớp P02;
- Logits/loss/gradient của P02 đối chiếu mô hình tham chiếu P00 (cùng cấu hình);
- Đảo các token tương lai ở hai batch để thử cô lập tiền tố;
- Kiểm lại shape, weight tying, số tham số 235264 và từ chối ID âm/2048, chuỗi vượt context.

Bộ này chỉ dùng token ID tổng hợp, **không đọc** Wikipedia/TRAIN/VALIDATION/TEST, không optimizer.step, không checkpoint, không P03/P04. Kiểm tra tĩnh Python compile PASS; **chưa thực thi kiểm định này trên Windows**, kết quả phải do máy Windows báo qua QA runner có khóa SHA.

Mã tệp kiểm định SHA-256: `c0ce4bd4db66e31984c1ee01431552dfe8a7219dfd212af957d8647e4734e252`; Git blob: `7f7038da478f23c3f5c260ef332ed70628bd4142`.

Không tạo phase/cấp phép riêng vì đây là phần của gói tích hợp P02. Giữ P02 ở `OPEN`, PR #6 vẫn nháp, P03/P04 chưa mở. Các bản ghi E0, one-shot marker và `lineage.md` bất biến.

Bước kế tiếp: một lượt QA Windows CPU gồm 6 bài unittest + 4 bài độc lập trên đúng HEAD mới, đọc log/biên bản và thẩm định PASS/FAIL, rồi xét hợp nhất P02.