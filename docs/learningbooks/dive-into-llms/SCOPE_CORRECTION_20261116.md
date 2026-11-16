# Sửa phạm vi học tập — 2026-11-16

**Loại:** `DOCS_CORRECTION` (không phải science QA, không phải science FAIL hoặc PASS).

## Sai lệch ban đầu

Yêu cầu của người dùng là clone và học/chuyển ngữ bộ giáo trình [dive-into-llms](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0), trong khi bản nháp trước đó lại đặt 11 chương dưới góc nhìn “ứng dụng với TTM/CLDP/Agent Orchestrator”. Điều này gây cảm giác đang biên soạn sách về năng lực của TTM/CLDP trước khi có chứng cứ khoa học. Đây là lỗi phạm vi và diễn đạt.

## Điều chỉnh

1. Giữ nguyên bản Git upstream đã khóa; ghi rõ 11 tệp chỉ là **study notes**.
2. Bỏ toàn bộ phần “Ứng dụng/Liên hệ TTM/CLDP/dự án” khỏi 11 ghi chú và loại phân loại độ liên quan dự án trên từng trang.
3. Bỏ tài liệu `RESEARCH_DIRECTION_MATRIX.md` khỏi cây học tập hiện hành để không làm tài liệu đào tạo lẫn với các đề xuất nghiên cứu. Lịch sử Git trước đó vẫn truy xuất được, không sửa `main` hoặc `lineage.md`.
4. Báo `FULL_TRANSLATION=0/34`; không chấp nhận chỉ số “chưa dịch = 0” cho toàn bộ upstream.
5. Không tuyên bố đã kiểm định khả năng của TTM hoặc CLDP. Không thay Question Gate hay owner science decision.

## QA còn mở

- [ ] Review độc lập độ chính xác nội dung.
- [ ] Rà theo từng nguồn nếu cần bản dịch thực sự.
- [ ] Quyết định owner đối với việc giữ/loại các ghi chú tự biên soạn.
- [ ] Merge PR nếu QA và owner chấp nhận.

**Kết luận:** `CORRECTION_SCOPE_AUTHOR_APPLIED`; `NO_SCIENCE_EXECUTION`; `NO_INDEPENDENT_QA_YET`. 
