# P01 D1 — Tiền kiểm Git/Windows và tài nguyên chỉ đọc cho I0A

**Mã:** `TTM_P01_I0A_READONLY_WINDOWS_EVIDENCE_V1`  
**Ngày:** 05/11/2026. **Trạng thái:** `PARTIAL_READONLY_EVIDENCE_PENDING_LOCAL_GIT_STATUS_AND_FRESH_RAM_DISK`.  
**Chế độ:** đọc Git metadata, node telemetry; không tạo worktree, không chạy QA, không tải dữ liệu, không ghi/xóa/cleanup.

## 1. Bằng chứng đã quan sát trực tiếp

| Thành phần | Giá trị và nguồn | Đánh giá |
|---|---|---|
| GitHub `main` | `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7` (connector GitHub, phiên kiểm tra này) | `PASS_EXACT_REF` |
| GitHub PR #4 | `open/draft/merged=false`, từ đúng base trên, `behind_by=0` | `PASS_READONLY_BRANCH_SCOPE` |
| Windows `.git/refs/heads/main` | `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7` (RemoteMCP đọc file) | `PASS_EXACT_REF` |
| Windows `.git/refs/remotes/origin/main` | `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7` | `PASS_EXACT_REF` |
| Windows `.git/config` | `origin=https://github.com/minhtri22/TokenToModel-Lab.git` | `PASS_EXPECTED_ORIGIN` |
| Nhánh P00 `.git/refs/heads/feature/p00-source-docs-diagrams-20261105` | `382da2c52d0fb4efe1cd9de5c92e68de79a52a20` | `PASS_REF_ONLY` |
| Link P00 `worktrees/.../.git` + `.git/worktrees/.../HEAD` | trỏ tới `.git/worktrees/p00-source-docs-diagrams-20261105` và branch P00 đã ghim | `PASS_LINK_METADATA` |
| Danh mục `.git/worktrees` | Chỉ có mục P00 đã biết ở thời điểm đọc | `PASS_METADATA_ONLY` |
| Biên bản fast-forward cũ | `TTM_P01_BASELINE_FAST_FORWARD_20261105T083903147Z.json`, SHA-256 `ee69f32a993d011b35173074a5ea221bdffc3feb70c780b532f045e9beb58b7f` | `PASS_PRIOR_RECEIPT` |
| RemoteMCP node `DESKTOP-4PSD0G2` | Online; signed heartbeat báo 0 active node jobs, dữ liệu quan sát có tuổi nhỏ | `PASS_NODE_OBSERVATION_ONLY` |

**Không suy diễn:** đọc `.git/refs` và metadata không thay thế `git status`, kiểm tra dirty/untracked, xác minh HEAD bằng Git CLI, quyền hệ thống tệp, hay kiểm tra junction/reparse. Số 0 tác vụ của RemoteMCP không chứng minh RAM/đĩa đang đủ.

## 2. RAM/đĩa và cổng QA động

Bằng chứng Windows gần nhất do người dùng chạy vào `2026-11-05T11:01:18.0864528Z` (18:01 tại Việt Nam): RAM khả dụng **10.959 GiB**, D: trống **34.869 GiB**, D: sau dự phòng **32.807 GiB**. Đạt ngưỡng ứng viên ở thời điểm đó. Đây **không** phải phép đo mới tại thời điểm quyết định I0A và không chứng minh có Job Object, quota disk hoặc watchdog thực sự chạy.

`I0A-07=HOLD_RECHECK`; `RESOURCE_GUARD_DYNAMIC_QA=NOT_EXECUTED`.

## 3. Chương trình tiền kiểm chỉ đọc đã chuẩn bị, chưa thực hiện ở Windows

**Tên:** `TTM_P01_I0A_READONLY_WINDOWS_PREFLIGHT.ps1`.  
**SHA-256 nguồn trong môi trường chuẩn bị:** `deb82ad16380dfd53c7def559cb9a7ec392321a84d6bc2cb79ee0ac2123e0012`.  
**Vị trí nếu người dùng quyết định lưu:** `D:\WORK\RESEARCH\TokenToModel-Lab\tmp\TTM_P01_I0A_READONLY_WINDOWS_PREFLIGHT.ps1`.  
**Loại:** chương trình kiểm tra hành chính chỉ đọc, **không** phải checker hoặc guard P01, không tạo fixture và không huấn luyện.

Hợp đồng chương trình: từ chối sai root/origin, kiểm tra reparse trên các thành phần chính, đọc Git bằng `--no-optional-locks` và tắt fsmonitor/untracked cache; in `git status --porcelain` dưới dạng **số lượng**, worktree list, Git HEAD P00 và repo, đo RAM/đĩa bằng CIM. **Không chạy git fetch, reset, clean, worktree add/remove, create/delete file hoặc gọi Job Object**. Console được dùng để phân xử, chương trình không ghi tệp receipt trên Windows.

**Giới hạn cần khai báo:** việc đọc bằng Git và CIM không phải một hệ thống kiểm soát bất biến/hệ điều hành có thể chứng minh tuyệt đối không có thay đổi do tiến trình khác. Một bộ kiểm tra chỉ đọc ở mức lệnh không thay thế QA/audit hệ thống. Không thể coi chương trình đã thực thi hoặc đạt QA Windows chỉ vì nó đã qua rà soát tĩnh.

### Cách kiểm tra trước khi chạy (nếu cần quan sát thêm)

```powershell
$script = 'D:\WORK\RESEARCH\TokenToModel-Lab\tmp\TTM_P01_I0A_READONLY_WINDOWS_PREFLIGHT.ps1'
$expected = 'deb82ad16380dfd53c7def559cb9a7ec392321a84d6bc2cb79ee0ac2123e0012'
if (-not (Test-Path -LiteralPath $script -PathType Leaf)) { throw 'TTM_P01_PREFLIGHT_SCRIPT_MISSING' }
if ((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash -ine $expected) { throw 'TTM_P01_PREFLIGHT_SHA256_MISMATCH' }
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script
```

Nếu console không đủ điều kiện, giữ nguyên cổng HOLD; không tự chạy script khác, sửa ref, gọi Git cleanup hoặc tạo worktree để khắc phục.

## 4. Trạng thái chính xác I0A-01/02/07

- `I0A-01_GIT_REFS_AND_ORIGIN=PASS_SCOPED_READONLY`; `I0A-01_GIT_STATUS_AND_REPARSE=HOLD_NOT_OBSERVED`.
- `I0A-02_PATH_ALLOWLIST=DEFINED_DESIGN_ONLY`; `I0A-02_CANDIDATE_COLLISION_AND_ACL=HOLD_NOT_OBSERVED`.
- `I0A-07_PRIOR_RAM_DISK_SNAPSHOT=PASS_HISTORICAL`; `I0A-07_FRESH_CAPACITY=HOLD_NOT_MEASURED`.
- `I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`; `P01_WORKTREE_CREATION_AUTHORIZED=false`; `P00_CLEANUP_AUTHORIZED=false`.

**Bước tiếp theo:** đọc console read-only nếu người dùng thực thi, đối chiếu SHA/đúng root và thời điểm; sau đó thẩm định I0A-01/02/07 và xin quyết định permit riêng. Không cấp I0A trong tài liệu này.
