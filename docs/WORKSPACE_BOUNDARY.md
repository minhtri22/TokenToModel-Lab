# TTM — Ranh giới nơi làm việc và quy tắc thao tác an toàn

## Danh tính cố định

- Kho GitHub chính thức: `https://github.com/minhtri22/TokenToModel-Lab.git`.
- Thư mục gốc được phép trên Windows: `D:\WORK\RESEARCH\TokenToModel-Lab`.
- Cây làm việc chính (main working tree) là chính thư mục gốc. Cây làm việc phụ (Git worktree) P00 chỉ được tồn tại bên trong `worktrees/` của thư mục gốc.
- Với công việc do RemoteMCP quản lý, chỉ dùng đường dẫn cây làm việc được trả về từ `project_status.worktrees_root_rel`, sau khi chứng minh đường dẫn vật lý vẫn nằm trong thư mục gốc. Không tự tạo đường dẫn bên ngoài.

## Quy tắc bất biến

1. Trước mọi thao tác Git phải kiểm tra kho nguồn (`origin`), commit hiện tại, thư mục gốc và chủ sở hữu của cây làm việc.
2. Từ chối đường dẫn trỏ sang kho khác, liên kết tượng trưng (symbolic link), điểm nối (junction) hoặc điểm phân tích lại (reparse point) có thể đưa thao tác ra ngoài phạm vi.
3. **Cấm tạo, di chuyển, xóa hoặc dọn cây làm việc Git bên ngoài thư mục gốc trên.**
4. Mọi thao tác dọn dẹp cần một quyết định riêng, nêu đúng đường dẫn và được người dùng chấp thuận rõ ràng. Cấm `git clean -fdx`, `git reset --hard`, `git worktree prune`, `git worktree remove --force`, xóa đệ quy, `Remove-Item -Recurse` và xóa theo ký tự đại diện.
5. Dữ liệu chạy, thư mục tạm, dữ liệu huấn luyện, điểm lưu mô hình (checkpoint), bộ nhớ đệm (cache) và nhật ký phải được chuyển hướng vào thư mục gốc trước khi thực thi. Không thay đổi thông tin đăng nhập Git hay biến môi trường toàn máy.
6. `lineage.md` chỉ ghi bổ sung (append-only); giữ các kết quả đạt, không đạt và chưa đủ bằng chứng.

## Ranh giới khoa học của P00

- P00 chỉ kiểm tra tính đúng chức năng (correctness) trên bộ xử lý trung tâm (CPU).
- Bộ nhớ Key/Value phân trang (Paged KV Cache) hiện vẫn gom dữ liệu K/V thành mảng liên tục để tính cơ chế chú ý (Attention); **chưa phải** nhân GPU đọc trang trực tiếp (direct-paged kernel).
- Không suy diễn tăng tốc, chất lượng mô hình đã huấn luyện hay khả năng thương mại hóa từ kết quả P00.

## Trạng thái sau hợp nhất P00

- Commit hợp nhất trên GitHub: `8df22f5f29e645b2becff936daccbd32ac780661`.
- Khi kiểm tra sau hợp nhất ngày 05/11/2026, tham chiếu local `main` và `origin/main` còn ở `f2ed098b033431924a3cbabdc9af89d7bbd7b378`. Không tự kết luận local đã đồng bộ.
- Worktree P00 được giữ nguyên, không xóa/dọn; đồng bộ local và kiểm tra trạng thái sạch là cổng riêng.
- Xem `docs/qa/P00_POST_MERGE_AUDIT_20261105.md` để biết kết luận và phần còn thiếu.
