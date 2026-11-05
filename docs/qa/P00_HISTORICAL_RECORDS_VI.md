# P00 — Chú giải tiếng Việt cho hồ sơ kỹ thuật lịch sử

Tài liệu này là **bản hướng dẫn bổ sung**, không thay thế hoặc chỉnh sửa các bản gốc đã dùng để ra quyết định QA. Những chuỗi trạng thái tiếng Anh trong tệp gốc là **mã định danh** được giữ nguyên để đối chiếu.

## Các hồ sơ cần đọc

| Hồ sơ nguyên gốc | Nội dung đã ghi nhận |
|---|---|
| `docs/qa/P00_PS51_CALLDEPTH_RECOVERY_20261105.md` | Lỗi PowerShell 5.1 bị tràn độ sâu gọi hàm (CallDepthOverflow) do trùng tên hàm `Git`, đã được sửa trước khi chạy QA thành công |
| `docs/qa/P00_FORMAL_ADJUDICATION_20261105.md` | Thẩm định 13 bài QA Windows và 6 bài QA bổ sung, chấp thuận trong phạm vi tính đúng của mô hình CPU |
| `experiments/comparisons/P00_REFERENCE_BASELINE_20261105.md` | P00 là mốc đầu tiên, chưa có phiên bản tiền nhiệm để tính cải thiện tốc độ hoặc chất lượng |
| `lineage.md` | Dòng lịch sử có cả lỗi hạ tầng, kết quả PASS và quyết định; **chỉ ghi bổ sung (append-only)** |
| `experiments/registry.jsonl` và `artifacts/qa/p00/` | Mã lần chạy, biên bản gốc, mã SHA-256 và log |

## Cách diễn giải các trạng thái

- `PASS_SCOPED_CORRECTNESS`: đạt các bài kiểm tra tính đúng trong phạm vi CPU nhỏ, không phải chứng minh huấn luyện thành công.
- `PROPOSED_NOT_FROZEN`: cấu hình chưa được khóa thành hợp đồng thí nghiệm khoa học.
- `NOT_PERFORMED`: việc huấn luyện hay phép thử đó chưa diễn ra.
- `NOT_ESTABLISHED`: chưa có bằng chứng đủ để kết luận.
- `INDEPENDENT_QA_PASS_6_OF_6`: sáu bài thử bổ sung có fixture độc lập với các bài thử phát triển; không khẳng định có bên thứ ba kiểm định.
- `MERGE=NOT_AUTHORIZED` trong biên bản thời điểm trước hợp nhất: là trạng thái **tại thời điểm tệp được tạo**, không phải trạng thái hiện tại của GitHub.

## Nguyên tắc bảo toàn

Tuyệt đối không viết lại biên bản gốc để cập nhật trạng thái hiện tại. Thêm tài liệu kiểm toán mới hoặc entry mới trong `lineage.md` để diễn đạt những thay đổi xảy ra **sau** khi tệp gốc được khóa. Xem `docs/qa/P00_POST_MERGE_AUDIT_20261105.md` để biết trạng thái mới nhất trong phạm vi kiểm toán.
