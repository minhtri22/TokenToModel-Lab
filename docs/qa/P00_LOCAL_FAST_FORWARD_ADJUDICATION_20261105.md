# P00 — Thẩm định đồng bộ tiến nhanh (Fast-forward) local Windows

## Danh tính và nguồn chứng cứ

- Mã quyết định: `TTM_P00_LOCAL_FAST_FORWARD_RESULT_ADJUDICATION`.
- Ngày: 05/11/2026.
- Workspace: `D:\WORK\RESEARCH\TokenToModel-Lab`.
- Kho Git: `https://github.com/minhtri22/TokenToModel-Lab.git`.
- Biên bản gốc (Run Receipt): `D:\WORK\RESEARCH\TokenToModel-Lab\evidence\p00\TTM_P00_MAIN_FAST_FORWARD_20261105T075432222Z.json`.
- SHA-256 biên bản: `f452b99c531bb8bdba26249b4ef07172044c582471ab87c48285954490fbb4ab`.
- Bản biên bản người dùng cung cấp và tệp trên máy Windows đọc lại qua RemoteMCP có cùng SHA-256.

## Các bước xác minh

| Kiểm tra | Kết quả | Ý nghĩa |
|---|---|---|
| Trạng thái nguồn trước cập nhật | `f2ed098b033431924a3cbabdc9af89d7bbd7b378` | Đúng commit khởi tạo đã khóa |
| Local `main` sau cập nhật | `8df22f5f29e645b2becff936daccbd32ac780661` | Khớp GitHub `main` |
| Local `origin/main` | Cùng commit | Tham chiếu từ xa đã cập nhật |
| Cơ chế cập nhật | `EXACT_PIN_FAST_FORWARD_ONLY` | Chỉ tiến nhanh đúng commit, không cưỡng bức, không tạo merge mới |
| Worktree P00 | `382da2c52d0fb4efe1cd9de5c92e68de79a52a20` | Giữ nguyên nguồn đã kiểm thử |
| Bảo vệ tệp | `11` tệp, mã SHA-256 trước/sau trong biên bản | Không xóa/ghi đè tệp bảo vệ |
| Kiểm tra đọc lại bốn tệp quan trọng | SHA-256 đúng | Hai biên bản QA, script đồng bộ và script kiểm thử độc lập |
| Dọn dẹp (Cleanup) | `NONE` | Không dọn dữ liệu |
| Huấn luyện (Training) | `NOT_PERFORMED` | Không sinh kết quả học mới |
| PR #2 | Chưa hợp nhất tại thời điểm chạy | Đồng bộ mốc P00, chưa lấy tài liệu đang rà soát |

### Giải thích hai phép đo chính

- **So sánh commit (Commit Identity):** ba tham chiếu `main` trên GitHub, `main` tại local và `origin/main` tại local phải khớp **toàn bộ 40 ký tự SHA-1**. Đây là phép xác minh đồng nhất lịch sử mã nguồn, không phải đo tốc độ.
- **Mã băm SHA-256 của tệp (File Integrity):** các tệp cần bảo vệ phải có cùng SHA-256 trước và sau cập nhật. Giá trị không đổi nghĩa là nội dung byte không bị thay đổi; không chứng minh tính chính xác của nội dung khoa học.

## Kết luận

- `LOCAL_P00_FAST_FORWARD=PASS`.
- `LOCAL_MAIN_EQUALS_GITHUB_P00_MERGE=PASS`.
- `P00_WORKTREE_PRESERVED=PASS`.
- `PROTECTED_FILES_VERIFIED=11` theo biên bản gốc; bốn tệp được đối chiếu đọc lại độc lập trực tiếp.
- `NO_CLEANUP=PASS`.
- Không chạy lại QA mô hình P00 và không thay nội dung các bản QA cũ.
- Sau quyết định này, **không tiếp tục ghi local `main` chưa đồng bộ với P00** như một trạng thái hiện hành. Các tài liệu kiểm toán được viết trước thời điểm đồng bộ vẫn là ảnh chụp lịch sử có thời điểm.
- Chưa kiểm tra độc lập lại toàn bộ trạng thái Git sau các thao tác ngoài biên bản. Nếu muốn đồng bộ thay đổi PR #2 sau này, phải khóa commit mới và tiền kiểm lại.

**Quyết định:** `TTM_P00_LOCAL_FAST_FORWARD_RESULT_ADJUDICATION=PASS` trong phạm vi mốc P00 đã hợp nhất. Chưa cấp quyền mở P01 chỉ từ việc đồng bộ mã.
