# TTM — Quy trình thu gọn nhánh GitHub không làm mất lịch sử

Ngày 2026-11-08. Chỉ dọn **remote refs**, không xóa local Git branch/worktree hoặc file. Mốc main `4731f75cda6aa86b1dd2929b3f10d11fbbed0812`.

## Chốt hiện trạng và phân nhóm

- Trước dọn: 31 nhánh, 10 PR; 9 PR đã merge; PR #4 draft mở. Đối chiếu GitHub `compare main...branch` cho 9 nhánh merged `ahead=0`. Kiểm tra ancestry 17 nhánh P01 lịch sử với `adjudication/p01-f1-wp30-e0-closure-and-p02-handoff-20261107`: kết quả `behind=0`, tức là mọi commit của chúng nằm trong archive lineage mới. Hai side branches phân kỳ phải giữ archive riêng.
- Đã tạo 3 archive refs tại **đúng SHA** nguồn. Snapshot chi tiết xem manifest JSON. Tất cả original refs vẫn còn; chưa chạy xóa.
- Khi xóa: dừng nếu `main` không còn ở `4731f75cda6aa86b1dd2929b3f10d11fbbed0812` hoặc archive/P07 thay SHA, remote URL khác `https://github.com/minhtri22/TokenToModel-Lab.git`, branch mới xuất hiện cùng tên, PR #4 chưa đóng, hay thiếu xác minh nguồn.
- Không sử dụng `git branch -D` trên local, `git push --mirror`, `git push --prune`, `git fetch --prune`, `git push --force` hoặc `git remote update`; **không** xóa unmerged lịch sử khi chưa có anchor.
- Cơ chế mong muốn: `git push --porcelain --force-with-lease=refs/heads/<SOURCE>:<EXACT_OLD_SHA> origin :refs/heads/<SOURCE>` dưới `D:\WORK\RESEARCH\TokenToModel-Lab`, tuyệt đối chỉ tác động remote ref đã ghim; không cần checkout/fetch. Nếu fail một ref thì dừng toàn bộ, xuất biên bản đã thực hiện, không retry tự động.
- Phương án rollback ref (nếu đích vẫn vắng): tạo lại ref đúng SHA cũ từ archive theo manifest; chỉ thực hiện khi có quyết định riêng. Archive refs **không được xóa** trong cleanup này.
- Tài liệu quy tắc đề xuất `ADR-0001_TRAIN_FIRST_COLAB_AND_BRANCH_CLEANUP_20261108.md`; scripts bổ sung phải tự kiểm tra SHA, chế độ DryRun mặc định và ghi biên bản có chống ghi đè.

## Điều kiện đóng cleanup

`CLEANUP=PASS` khi remote còn `main`, `feature/p07-...`, 3 `archive/...`, branch governance nếu PR chưa merge; cả 29 tên nguồn thuộc manifest đã biến mất; chỉ còn PR quản trị đang mở (PR #4 đã đóng), không merge các nhánh legacy. `lineage.md` và local repo không đổi.

Nếu người dùng dừng trước xóa, kết luận là `CLEANUP_PREPARED_NOT_EXECUTED`, không tự tuyên bố PASS.
