# TTM P01 — Chọn A, chuyển B khi GitHub CI không có khả năng kiểm thử: I0A-S

**Operation:** `TTM_P01_I0A_S_STATIC_SOURCE_ONE_SHOT_EXACT_PERMIT_REQUEST`  
**Ngày:** 2026-11-06. **Ghi nhận đồng ý trực tiếp của chủ dự án**: chọn phương án A (GitHub), nếu GitHub Actions/CI không hoạt động thì chuyển phương án B (một worktree Windows trong dự án). Người dùng chỉ định không tạo thêm thủ tục phê duyệt "giấy phép" ngoài mục đích kiểm soát phạm vi.  
**Repository:** `https://github.com/minhtri22/TokenToModel-Lab.git`.  
**Nhánh thiết kế:** `design/p01-tokenizer-data-prereg-20261105`.  
**GitHub main:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.  
**Design HEAD đã kiểm tra trước quyết định:** `a9cb8c2183d5c4a9e9a876ae3e88bf3f50b192e1`; PR #4 `OPEN/DRAFT/UNMERGED` và `behind_by=0`.

## 1. Giải thích "permit" và phạm vi phê duyệt đã nhận

"I0A permit" chỉ là **biên bản nội bộ giữ quyền thực hiện đúng phạm vi**, không phải giấy phép phần mềm, dịch vụ hay chấp thuận của bên thứ ba. Người dùng đã chấp thuận chiến lược A→B; không xin lại **quyết định chọn phương án**.

**Phân định quyết định:**
- `OWNER_ROUTE_APPROVAL=A_WITH_CONDITIONAL_B` — chấp thuận, không cần một vòng hỏi lại về A/B;
- `I0A_S_STATIC_AUTHORING_SCOPE=APPROVED_CONDITIONALLY` — chấp thuận phương hướng viết source-only, phải qua preflight thực tế trước khi tạo/ghi;
- `I0A_S_ADMISSION=HOLD_WINDOWS_OFFLINE` — chưa mở lượt triển khai, vì B chưa thể kiểm tra máy đích;
- `I0A_S_ACTUAL_WORKTREE_OR_SOURCE_WRITES=NONE` — hồ sơ này không tạo branch/worktree/source.

Đây không phải quyền tự động chạy mã. QA0/E0 vẫn chưa cấp.

## 2. GitHub Actions/CI kiểm tra trực tiếp

Từ GitHub connector ở nhánh thiết kế:
- API repository contents trả danh mục root và **không có** `.github`.
- Truy vấn `contents/.github?ref=design/p01-tokenizer-data-prereg-20261105` trả GitHub `404 NOT_FOUND`; do đó không có `.github/workflows` ở nhánh đã kiểm tra.
- GitHub Actions runs collection trên repository trả `total_count=0`.
- Tại exact design HEAD `a9cb8c2183d5c4a9e9a876ae3e88bf3f50b192e1`, số workflow-run theo commit = `0`, combined commit status checks = `0`.
- Endpoint liệt kê workflow registry không thuộc bề mặt `fetch` đã phê duyệt; **không suy diễn toàn bộ cấu hình GitHub Actions cấp tổ chức hoặc CI ngoài GitHub**.

**Kết luận:** `GITHUB_CI_CONFIGURED_ON_BRANCH=NO_WORKFLOW_FOUND`; `GITHUB_ACTIONS_RECENT_RUNS=0`; `CI_CAPABILITY_FOR_P01=NOT_ESTABLISHED`. Đây là **không có CI trong nhánh đang dùng**, **không phải bằng chứng** GitHub Actions bị outage/hết capacity. Theo quy tắc dự phòng của chủ dự án, **chọn B cho lượt I0A-S này**.

## 3. B — Phạm vi duy nhất đã chọn, còn chờ preflight

- Local repo: `D:\WORK\RESEARCH\TokenToModel-Lab`; origin exact như trên.
- Một worktree đề xuất, **chưa tạo**: `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105`.
- Nhánh triển khai ứng viên **chưa tạo**: `implementation/p01-i0a-s-f0-static-20261106`, xuất phát từ design HEAD exact được kiểm lại trước thời điểm thao tác; không merge PR #4.
- 12 tệp **ứng viên**, cần đọc tree/va chạm và pin lại trước khi ghi:
  1. `qa/p01/f0_fixture_generator.py`
  2. `qa/p01/independent_checker.py`
  3. `qa/p01/checker_contract_cases.py`
  4. `runtime/p01/windows_job_guard.py`
  5. `runtime/p01/write_quota_broker.py`
  6. `runtime/p01/source_scope_guard.py`
  7. `runtime/p01/evidence_manifest.py`
  8. `configs/p01_f0_static_i0a.json`
  9. `qa/p01/golden_vectors.json`
  10. `docs/qa/P01_I0A_STATIC_IMPLEMENTATION_REVIEW.md`
  11. `src/p01/byte_bpe.py`
  12. `src/p01/data_dedup_split.py`.
- Chỉ author source và review SHA/diff; không chạy/import code, `pytest`, mô hình, Job Object, tạo file fixture/snapshot/merges, đọc corpus, cài dependency mạng, huấn luyện BPE/GPT hoặc thay P00.
- Git worktree/cleanups **chỉ bên trong root dự án**. Không dùng một RemoteMCP managed worktree nằm dưới sibling `D:\WORK\RESEARCH\.remotemcp` vì nằm ngoài project; nếu cần tạo worktree B phải dùng tuyến Windows PowerShell do chủ sở hữu chạy hoặc cơ chế đã được kiểm duyệt đảm bảo đúng root. Không auto `git worktree add` khi chưa kiểm tra preflight.
- Việc tạo worktree bởi Git sẽ thay metadata trong `.git` của **cùng repository dự án**, không thể coi là "không ghi .git" tuyệt đối; cần cho phép chính xác mutation Git metadata trong phạm vi dự án, cấm P00 tracked-content changes, cleanup, reset và prune.

## 4. Vì sao chưa tạo worktree/code ngay bây giờ?

Công cụ RemoteMCP `device_status` cho `DESKTOP-4PSD0G2` trả `OFFLINE` và `heartbeat_fresh=false` tại thời điểm kiểm tra. Lần `task_list_dir` trực tiếp cũng trả `device is offline`. Không có Git status/ACL/reparse/đĩa/RAM mới trên Windows. Biên bản cũ 2026-11-05 không thể thay thế kiểm tra ngay trước thao tác ghi.

**Điều kiện kỹ thuật cần hoàn thành khi máy có thể truy cập** (không phải vòng xin giấy phép mới):
- Root/origin/main/branch HEAD, trạng thái `git status` và P00 sạch, `git worktree list --porcelain` chỉ main + P00.
- `P01_CANDIDATE_EXISTS=False`, các đường parent không phải reparse; target nằm trong project; không xung đột tên/file, không được sửa ACL chung để cố vượt kiểm tra.
- Xác minh branch mới từ exact design HEAD và đúng danh mục, không tạo file ngoài danh sách; source hash readback trước/sau; định rõ số lượt và không tự rerun.
- Nếu Windows vẫn offline hoặc preflight không xác quyết: **HOLD_TECHNICAL**, không tự quay lại A bỏ qua lựa chọn B; không dùng branch GitHub để né yêu cầu kiểm tra máy Windows.

## 5. Kết quả và bước kế tiếp

`I0A_OWNER_ROUTE_APPROVAL=A_THEN_B_IF_CI_UNAVAILABLE`  
`I0A_A_CI_OBSERVATION=NO_GITHUB_WORKFLOW_ON_DESIGN_BRANCH_0_RUNS`  
`I0A_EFFECTIVE_MODE=B_ONE_IN_PROJECT_WINDOWS_WORKTREE`  
`I0A_B_PREFLIGHT=HOLD_DEVICE_OFFLINE`  
`I0A_S_IMPLEMENTATION_ADMISSION=HOLD_TECHNICAL_NOT_OWNER_APPROVAL`  
`I0A_S_SOURCE_AUTHORING_NOW=false`  
`I0A_S_WORKTREE_CREATION_NOW=false`  
`I0A_QA0_RUNTIME_EXECUTION=NOT_GRANTED`  
`I0A_E0_SCIENCE=NOT_GRANTED`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`.

**Bước thực hiện tiếp theo:** `TTM_P01_I0A_S_B_WINDOWS_EXACT_PREWRITE_PREFLIGHT_AND_ONE_SHOT_STATIC_AUTHORING`. Khi Windows online hoặc chủ sở hữu chạy PowerShell preflight, xác minh các cổng kỹ thuật rồi triển khai **chỉ source tĩnh đúng một worktree và 12 đường dẫn**. Không hỏi lại sự lựa chọn A/B; dừng nếu thay đổi phạm vi hoặc mốc Git khoa học.
