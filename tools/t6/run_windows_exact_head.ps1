# TTM T6 Windows exact-head runner. PowerShell 5.1. Never updates local main or overwrites evidence.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[0-9a-fA-F]{40}$')]
    [string]$PinnedHead,
    [string]$RepoRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$PythonExe = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$branch = 'feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109'
$PinnedHead = $PinnedHead.ToLowerInvariant()
$worktree = Join-Path $RepoRoot '.worktrees\ttm-t6-pr15-20261109'
$qaDir = Join-Path $worktree 'artifacts\qa\t6'
$unitRel = 'artifacts/qa/t6/TTM_T6_WINDOWS_UNITTEST_OWNER_20261109.log'
$benchRel = 'artifacts/qa/t6/TTM_T6_WINDOWS_CPU_AB_OWNER_RUN.json'
$qaRel = 'artifacts/qa/t6/TTM_T6_WINDOWS_INDEPENDENT_QA_OWNER_20261109.json'
$receiptRel = 'artifacts/qa/t6/TTM_T6_WINDOWS_OWNER_RECEIPT_20261109.json'
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Assert-ExitCode([string]$name) {
    if ($LASTEXITCODE -ne 0) { throw ($name + '_EXIT_' + $LASTEXITCODE) }
}
function FullPath([string]$p) {
    return [System.IO.Path]::GetFullPath($p).TrimEnd('\').ToLowerInvariant()
}
function SHA([string]$p) {
    return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()
}

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) { throw 'PROJECT_ROOT_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) { throw 'PYTHON312_NOT_FOUND' }
$rootResolved = (Resolve-Path -LiteralPath $RepoRoot).Path
$gitTop = (& git -C $RepoRoot rev-parse --show-toplevel | Select-Object -First 1)
Assert-ExitCode 'GIT_ROOT'
if ((FullPath $gitTop.Replace('/', '\')) -ne (FullPath $rootResolved)) { throw 'WRONG_PROJECT_ROOT' }
$remote = (& git -C $RepoRoot remote get-url origin | Select-Object -First 1).Trim()
Assert-ExitCode 'ORIGIN'
if ($remote -notmatch '^(https://github\.com/|git@github\.com:|ssh://git@github\.com/)minhtri22/TokenToModel-Lab(\.git)?$') {
    throw 'ORIGIN_REPOSITORY_MISMATCH'
}
$remoteLine = (& git -C $RepoRoot ls-remote origin ('refs/heads/' + $branch) | Select-Object -First 1)
Assert-ExitCode 'GIT_REMOTE_HEAD'
if ([string]::IsNullOrWhiteSpace($remoteLine)) { throw 'REMOTE_T6_BRANCH_NOT_FOUND' }
$remoteHead = ($remoteLine -split '\s+')[0].ToLowerInvariant()
if ($remoteHead -ne $PinnedHead) { throw ('T6_HEAD_DRIFT expected=' + $PinnedHead + ' actual=' + $remoteHead) }

$parent = Split-Path -Parent $worktree
if (Test-Path -LiteralPath $parent) {
    $attr = (Get-Item -LiteralPath $parent -Force).Attributes
    if (($attr -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'WORKTREE_PARENT_IS_LINK' }
}
& git -C $RepoRoot fetch --no-tags origin ('refs/heads/' + $branch)
Assert-ExitCode 'FETCH_EXACT_HEAD'
$got = (& git -C $RepoRoot rev-parse FETCH_HEAD | Select-Object -First 1).Trim().ToLowerInvariant()
Assert-ExitCode 'FETCH_HEAD'
if ($got -ne $PinnedHead) { throw 'FETCH_HEAD_CHANGED' }

if (Test-Path -LiteralPath $worktree) {
    $wtAttr = (Get-Item -LiteralPath $worktree -Force).Attributes
    if (($wtAttr -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'WORKTREE_PATH_IS_LINK' }
    $wtTop = (& git -C $worktree rev-parse --show-toplevel | Select-Object -First 1)
    Assert-ExitCode 'EXISTING_WORKTREE'
    if ((FullPath $wtTop.Replace('/', '\')) -ne (FullPath $worktree)) { throw 'EXISTING_PATH_NOT_WORKTREE' }
} else {
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    & git -C $RepoRoot worktree add --detach $worktree $PinnedHead
    Assert-ExitCode 'CREATE_WORKTREE'
}
$wtHead = (& git -C $worktree rev-parse HEAD | Select-Object -First 1).Trim().ToLowerInvariant()
Assert-ExitCode 'WORKTREE_HEAD'
if ($wtHead -ne $PinnedHead) { throw 'WORKTREE_HEAD_MISMATCH' }
if ((& git -C $worktree status --porcelain)) { throw 'WORKTREE_NOT_CLEAN_BEFORE_RUN' }

foreach ($rel in @($unitRel, $benchRel, $qaRel, $receiptRel)) {
    if (Test-Path -LiteralPath (Join-Path $worktree $rel)) { throw ('ONE_SHOT_OUTPUT_ALREADY_EXISTS:' + $rel) }
}
if (-not (Test-Path -LiteralPath (Join-Path $worktree 'tests\t6\test_cache_ab_fixture.py'))) {
    throw 'T6_TEST_FILE_MISSING_AT_PINNED_HEAD'
}

foreach ($sub in @('artifacts','artifacts/qa','artifacts/qa/t6')) {
    $subPath = Join-Path $worktree $sub
    if (Test-Path -LiteralPath $subPath) {
        $subAttr = (Get-Item -LiteralPath $subPath -Force).Attributes
        if (($subAttr -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw ('EVIDENCE_PATH_IS_LINK:' + $sub) }
    }
}
New-Item -ItemType Directory -Path $qaDir -Force | Out-Null
$stdoutTmp = Join-Path $qaDir 'TTM_T6_WINDOWS_UNIT_STDOUT_TEMP.txt'
$stderrTmp = Join-Path $qaDir 'TTM_T6_WINDOWS_UNIT_STDERR_TEMP.txt'
if ((Test-Path -LiteralPath $stdoutTmp) -or (Test-Path -LiteralPath $stderrTmp)) { throw 'UNIT_LOG_TEMP_EXISTS' }
$oldDontWrite = $env:PYTHONDONTWRITEBYTECODE
$env:PYTHONDONTWRITEBYTECODE = '1'
Push-Location -LiteralPath $worktree
try {
    & $PythonExe -B -c 'import sys,torch; assert sys.version_info[:2]==(3,12); print("PYTHON",sys.version.split()[0],"TORCH",torch.__version__)'
    Assert-ExitCode 'PYTHON_TORCH_CHECK'

    # Capture unittest stderr without letting PowerShell 5.1 treat native stderr as a terminating error.
    $test = Start-Process -FilePath $PythonExe -WorkingDirectory $worktree -ArgumentList @(
        '-B','-m','unittest','discover','-s','tests/t6','-p','test_*.py','-v'
    ) -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdoutTmp -RedirectStandardError $stderrTmp
    $unitText = (Get-Content -LiteralPath $stdoutTmp -Raw) + (Get-Content -LiteralPath $stderrTmp -Raw)
    [System.IO.File]::WriteAllText((Join-Path $worktree $unitRel), $unitText, $utf8)
    Remove-Item -LiteralPath $stdoutTmp, $stderrTmp -Force
    Write-Host $unitText
    if ($test.ExitCode -ne 0) { throw ('T6_UNITTEST_FAILED_EXIT_'+$test.ExitCode) }
    if ($unitText -notmatch 'Ran 16 tests in [\d.]+s\s+OK\s*$') { throw 'UNITTEST_16_16_LOG_CONTRACT_FAIL' }
    Write-Host 'T6_WINDOWS_UNITTEST=PASS_16_OF_16'

    & $PythonExe -B tools/t6/cache_ab_benchmark_fixture.py --warmups 2 --repeats 5 --block-size 4 --output $benchRel
    Assert-ExitCode 'BENCHMARK'
    Write-Host 'T6_WINDOWS_BENCHMARK=COMPLETED'

    & $PythonExe -B tools/t6/independent_scoped_qa.py --report $benchRel --unittest-log $unitRel --output $qaRel
    Assert-ExitCode 'INDEPENDENT_QA'
    $check = Get-Content -LiteralPath $qaRel -Raw | ConvertFrom-Json
    if ($check.status -ne 'PASS_33_OF_33_SCOPED_MATERIAL_AND_ARITHMETIC') { throw ('INDEPENDENT_QA_HOLD:' + $check.status) }
    Write-Host 'T6_WINDOWS_INDEPENDENT_QA=PASS_33_OF_33'

    $report = Get-Content -LiteralPath $benchRel -Raw | ConvertFrom-Json
    if ($report.hardware.platform -notmatch 'Windows') { throw 'REPORT_IS_NOT_WINDOWS_PLATFORM' }
    if ($report.measurement_contract.device -notmatch 'Windows') { throw 'BENCHMARK_DEVICE_LABEL_STALE' }

    $receipt = [ordered]@{
        schema = 'ttm.t6.windows.owner_cpu_replay_receipt.v1'
        branch = $branch
        source_head = $PinnedHead
        scope = 'synthetic CPU only; no training, TEST, Q1/Q2, P07 or P08'
        platform = $report.hardware.platform
        python = $report.hardware.python
        torch = $report.hardware.torch
        unittest_status = 'PASS_16_OF_16'
        independent_qa_status = $check.status
        hashes_sha256 = [ordered]@{
            unittest_log = SHA (Join-Path $worktree $unitRel)
            benchmark_json = SHA (Join-Path $worktree $benchRel)
            independent_qa_json = SHA (Join-Path $worktree $qaRel)
        }
    }
    [System.IO.File]::WriteAllText(
        (Join-Path $worktree $receiptRel), (($receipt | ConvertTo-Json -Depth 7) + "`n"), $utf8
    )
    Write-Host ('T6_WINDOWS_OWNER_RECEIPT_SHA256=' + (SHA (Join-Path $worktree $receiptRel)))
    Write-Host ('T6_WINDOWS_EVIDENCE_PATH=' + $qaDir)
    Write-Host 'T6_WINDOWS_SCOPED_REPLAY=PASS'
}
finally {
    Pop-Location
    $env:PYTHONDONTWRITEBYTECODE = $oldDontWrite
}
