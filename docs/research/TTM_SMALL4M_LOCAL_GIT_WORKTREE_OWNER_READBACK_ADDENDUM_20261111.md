# TTM-Small-4M — Bổ sung biên bản đọc lại Git local do chủ dự án cung cấp

**Ngày:** 2026-11-11  
**Phạm vi:** bổ sung chứng cứ về trạng thái local cho nghiên cứu hậu CF1, chỉ đọc, không chạy khoa học.  
**Nguồn:** kết quả PowerShell 5.1 do chủ dự án cung cấp trực tiếp trong cuộc trò chuyện, và GitHub compare lịch sử. Các quan sát từ console **không phải** kiểm toán Git filesystem độc lập lần thứ hai.

## 1. Trạng thái repository gốc

- Root: `D:\WORK\RESEARCH\TokenToModel-Lab`.
- `git rev-parse HEAD`: `b57b44e7287f842e81050c1faee337f636333dd0`.
- `git status --porcelain=v1 --untracked-files=normal`: không có tệp đã được Git theo dõi bị sửa, xóa hoặc staged; tồn tại **tám mục chưa được Git theo dõi**.
- Các mục chưa theo dõi: `.worktrees/`, `TTM_FRESH12_OWNER_PRIVATE_KEY_BACKUP_DO_NOT_GITHUB.zip`, `_evidence/`, `_runtime/`, `artifacts/qa/r2/`, `artifacts/qa/ttm-embeddinggemma2/`, `demos/`, `experiments/p01/`.
- Tệp ZIP khóa riêng tư không được Git theo dõi; tuyệt đối không công bố hoặc đưa vào commit công khai. Sự tồn tại của ZIP không khẳng định nội dung, tính xác thực hay tình trạng ACL.
- `refs/remotes/origin/main` local: `d4ec548727ba85625d1bf2684d85ec9e6867572b`.
- GitHub `main` tại thời điểm rà soát: `5d52e32f20021e36f08f284ef9864d3ba36dbead`.
- GitHub compare: `b57b44e..d4ec548 = ahead 139, behind 0`; `d4ec548..5d52e32 = ahead 7, behind 0`. Tổng GitHub main mới hơn local main 146 commit. Đây là quan hệ tổ tiên/hậu duệ của commit, **không** chứng minh fast-forward update có thể thao tác ngay mà không đụng đường dẫn untracked.

## 2. Worktree

Console `git worktree list --porcelain` liệt kê **13 worktree**, trong đó:
- Root TTM `main`.
- Hai RemoteMCP worktree ngoài phạm vi project root: `D:/WORK/RESEARCH/.remotemcp/w/prj_1544c3e94ebd4b2947bc84e9/tsk_4fb1b1663e6de4c303138660` và `.../tsk_a219c435c867be41ddc5c4fc`.
- Các worktree trong root TTM: CF1 evidence, T6 detached, P00, P01, FRESH16, Ollama logits, R2A Codex review, SIX G1 v1c review, SIX G1 Windows review, vector memory external detached.

Hai RemoteMCP worktree nằm ngoài phạm vi đã được điều lệ TTM chấp thuận cho worktree. Đánh dấu `EXTERNAL_LEGACY_WORKTREE_REGISTRATION_REQUIRES_SEPARATE_BOUNDARY_REVIEW` nhưng **không** xóa, di chuyển, prune hay tạo worktree mới. Trạng thái sạch/bẩn **của các worktree phụ** không được xác minh bằng lần chạy `git status` trên root. Trạng thái `UNTRACKED_PRESERVE` được áp dụng cho cả tám mục.

## 3. Các nhánh khoa học hiện hữu

- CF1 local evidence `cf6a37e5e9709ab0613918dc03ee70efa79f893f` là one-shot đã tiêu thụ: không tái chạy hoặc đánh giá TEST.
- FRESH16 local `6c4ba3946d6ddd3d0b4dcdc8348f7f734289d2e2`; GitHub nghiên cứu FRESH16 quan sát `23dd0f73656a2882c54f8d27a0280511f06fd2ce`. Không mặc định local chứa audit F01/F02 hoặc phụ lục rubric chưa duyệt.
- P01 local `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0` là worktree lịch sử bảo toàn.
- Mã A/C và điều kiện khoa học không thay đổi chỉ từ kết quả `git status`; `NO_GO_PREEXEC` vẫn hiệu lực.
- RemoteDesktop đọc thư mục `_tmp` thành công, nhưng **không thấy** `TTM_AC_NATIVE_PREEXEC_STDERR_FIX_V2_6628401b08ea`; thao tác truy cập trực tiếp thư mục dự kiến trả `WinError 3`. Không khẳng định script QA V2 đã chạy hoặc 6/6 native tests PASS.

## 4. Quyết định kiểm kê

- `ROOT_TRACKED_STATUS=CLEAN_BY_OWNER_CONSOLE`
- `UNTRACKED_COUNT=8`; `UNTRACKED_PRESERVE=YES`
- `WORKTREE_COUNT=13`; `NON_PROJECT_WORKTREE_COUNT=2`
- `CHILD_WORKTREE_DIRTY_STATUS=UNKNOWN`
- `LOCAL_MAIN_ANCESTOR_OF_GITHUB_MAIN=YES_146_COMMITS`
- `SYNCHRONIZE_GIT=NOT_AUTHORIZED_NOT_EXECUTED`
- `AC_NATIVE_V2=NOT_VERIFIED`
- `FRESH16=HOLD`, `AC=HOLD`, `NEW_TRAINING=0`, `NEW_INFERENCE=0`.
- Không thay `main`, `lineage.md`, PR #13, hay các kết quả khoa học đã khóa.

## 5. Bước thực hiện tiếp theo

`TTM_SMALL4M_ORIGINAL_FRESH16_PROTOCOL_OWNER_RATER_AND_AC_NATIVE_V2_SINGLE_READBACK_DECISION_NO_SCIENCE`

Chỉ sau kiểm kê không ghi dữ liệu từng worktree và xác nhận người chấm/diễn giải rubric, đóng gói một lượt phân xử FRESH16 và AC về GO/HOLD. Git sync và cleanup là nhánh quản trị độc lập, không phải điều kiện để tạo thêm toy hay cấp phép khoa học. Giữ trạng thái HOLD nếu thiếu bằng chứng.
