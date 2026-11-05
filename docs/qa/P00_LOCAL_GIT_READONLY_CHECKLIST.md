# P00 — Kiểm tra Git local sau hợp nhất, chỉ đọc

Mục đích: xác minh trạng thái thật của `main` trên máy Windows trước khi **xem xét** đồng bộ với GitHub. Những lệnh bên dưới chỉ đọc Git và tệp; **không** tạo cây làm việc mới, không tải mã, không đổi nhánh, không xóa và không hợp nhất.

**Phạm vi duy nhất:** `D:\WORK\RESEARCH\TokenToModel-Lab`.

## Lệnh chạy trên PowerShell 5.1

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$expectedOrigin = 'https://github.com/minhtri22/TokenToModel-Lab.git'
$expectedMainBeforeSync = 'f2ed098b033431924a3cbabdc9af89d7bbd7b378'
$expectedGitHubP00Merge = '8df22f5f29e645b2becff936daccbd32ac780661'

if (-not (Test-Path -LiteralPath $root -PathType Container)) {
    throw 'TTM_ROOT_NOT_FOUND'
}
$rootItem = Get-Item -LiteralPath $root -Force
if (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'TTM_ROOT_REPARSE_POINT_REJECTED'
}

$git = Get-Command git.exe -CommandType Application -ErrorAction Stop
$top = (& $git.Source -C $root rev-parse --show-toplevel).Trim().Replace('/', '\')
if ($LASTEXITCODE -ne 0 -or $top.TrimEnd('\') -ine $root.TrimEnd('\')) {
    throw 'TTM_WRONG_REPOSITORY'
}
$origin = (& $git.Source -C $root remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0 -or $origin -cne $expectedOrigin) {
    throw 'TTM_WRONG_ORIGIN'
}

$localMain = (& $git.Source -C $root rev-parse refs/heads/main).Trim()
$localHead = (& $git.Source -C $root rev-parse HEAD).Trim()
$branch = (& $git.Source -C $root branch --show-current).Trim()
$trackedChanges = @(& $git.Source -C $root status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0) { throw 'TTM_LOCAL_STATUS_FAILED' }

$trees = @(& $git.Source -C $root worktree list --porcelain)
if ($LASTEXITCODE -ne 0) { throw 'TTM_WORKTREE_LIST_FAILED' }
$canonicalRoot = [IO.Path]::GetFullPath($root).TrimEnd('\')
foreach ($line in $trees) {
    if ($line.StartsWith('worktree ')) {
        $worktreePath = [IO.Path]::GetFullPath($line.Substring(9)).TrimEnd('\')
        $isChild = $worktreePath.StartsWith($canonicalRoot + '\',
                      [StringComparison]::OrdinalIgnoreCase)
        if ($worktreePath -ine $canonicalRoot -and -not $isChild) {
            throw "TTM_WORKTREE_OUTSIDE_SCOPE: $worktreePath"
        }
    }
}

Write-Host "TTM_LOCAL_MAIN=$localMain"
Write-Host "TTM_LOCAL_HEAD=$localHead"
Write-Host "TTM_LOCAL_BRANCH=$branch"
Write-Host "TTM_GITHUB_P00_MERGE_EXPECTED=$expectedGitHubP00Merge"
Write-Host "TTM_LOCAL_MAIN_AT_ORIGINAL_PIN=$($localMain -eq $expectedMainBeforeSync)"
Write-Host "TTM_TRACKED_OR_UNTRACKED_STATUS_COUNT=$($trackedChanges.Count)"
Write-Host 'TTM_STATUS_BEGIN'
$trackedChanges
Write-Host 'TTM_STATUS_END'
Write-Host 'TTM_WORKTREE_LIST_BEGIN'
$trees
Write-Host 'TTM_WORKTREE_LIST_END'
Write-Host 'TTM_CHECK=READ_ONLY_NO_SYNC_NO_CLEANUP'
```

## Cách xử lý kết quả

- Nếu `origin` hoặc thư mục gốc không đúng, **dừng**; không tự sửa.
- Nếu có thay đổi chưa commit, phải phân loại và bảo toàn trước khi đồng bộ; không dùng `reset --hard` hoặc `clean`.
- Nếu có worktree bên ngoài phạm vi, **dừng**; không dọn hoặc di chuyển tự động.
- Nếu local `main` còn cũ nhưng sạch, chỉ sau quyết định riêng mới xem xét tải ref mới và tiến nhanh (Fast-forward), không dùng hợp nhất cưỡng bức.
- Worktree P00 được giữ nguyên ngay cả khi GitHub đã hợp nhất nhánh; việc dọn worktree cần quyết định riêng.
- Không mở P01 cho đến khi đối chiếu đúng `main`, quyền sở hữu worktree, trạng thái sạch và quyết định mốc đối chứng.
