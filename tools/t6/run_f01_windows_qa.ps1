# TTM T6 F-01 author-only Windows security QA. PowerShell 5.1; no benchmark rerun.
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
$PinnedHead = $PinnedHead.ToLowerInvariant()
$branch = 'feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109'
$wt = Join-Path $RepoRoot '.worktrees\ttm-t6-f01-security-qa-20261109'
$qaDirRel = 'artifacts/qa/t6/f01_windows_qa'
$utf8 = New-Object System.Text.UTF8Encoding($false)

function GitOne([string[]]$GitArguments, [string]$WorkDir, [string]$Tag) {
    $r = @(& git -C $WorkDir @GitArguments)
    if ($LASTEXITCODE -ne 0 -or $r.Count -ne 1) { throw ($Tag+'_GIT_FAILURE') }
    return ([string]$r[0]).Trim()
}
function HashFile([string]$path) {
    return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Assert-NoReparse([string]$path) {
    if (Test-Path -LiteralPath $path) {
        $item = Get-Item -LiteralPath $path -Force
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw ('REPARSE_DIRECTORY_DENIED:'+ $path)
        }
    }
}

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) { throw 'TTM_ROOT_MISSING' }
if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) { throw 'PYTHON312_MISSING' }
$projectReal = (Resolve-Path -LiteralPath $RepoRoot).Path.TrimEnd('\')
$gitRoot = GitOne @('rev-parse','--show-toplevel') $RepoRoot 'GIT_ROOT'
if ([IO.Path]::GetFullPath($gitRoot).TrimEnd('\') -ine [IO.Path]::GetFullPath($projectReal).TrimEnd('\')) {
    throw 'WRONG_PROJECT_ROOT'
}
$origin = GitOne @('remote','get-url','origin') $RepoRoot 'ORIGIN'
if ($origin -notmatch '^(https://github\.com/|git@github\.com:|ssh://git@github\.com/)minhtri22/TokenToModel-Lab(\.git)?$') {
    throw 'WRONG_GITHUB_REPOSITORY'
}
$line = GitOne @('ls-remote','origin',('refs/heads/'+$branch)) $RepoRoot 'REMOTE_BRANCH'
if (($line -split '\s+')[0].ToLowerInvariant() -ne $PinnedHead) { throw 'PINNED_HEAD_DRIFT' }

& git -C $RepoRoot fetch --no-tags origin ('refs/heads/'+$branch)
if ($LASTEXITCODE -ne 0) { throw 'FETCH_FAILED' }
if ((GitOne @('rev-parse','FETCH_HEAD') $RepoRoot 'FETCH_HEAD').ToLowerInvariant() -ne $PinnedHead) {
    throw 'FETCH_HEAD_MISMATCH'
}

$parent = Split-Path -Parent $wt
Assert-NoReparse $parent
if (Test-Path -LiteralPath $wt) { throw 'F01_QA_WORKTREE_ALREADY_EXISTS_NO_RERUN' }
if (-not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}
& git -C $RepoRoot worktree add --detach $wt $PinnedHead
if ($LASTEXITCODE -ne 0) { throw 'F01_QA_WORKTREE_CREATE_FAILED' }
if ((GitOne @('rev-parse','HEAD') $wt 'QA_HEAD').ToLowerInvariant() -ne $PinnedHead) {
    throw 'F01_QA_WORKTREE_SHA_MISMATCH'
}

$qaDir = Join-Path $wt $qaDirRel
foreach ($r in @('artifacts','artifacts/qa','artifacts/qa/t6')) {
    Assert-NoReparse (Join-Path $wt $r)
}
if (Test-Path -LiteralPath $qaDir) { throw 'F01_QA_EVIDENCE_EXISTS_NO_OVERWRITE' }
New-Item -ItemType Directory -Path $qaDir | Out-Null

function RunSuite([string]$pattern, [int]$expected, [string]$prefix) {
    $stdout = Join-Path $qaDir ($prefix + '.stdout.tmp')
    $stderr = Join-Path $qaDir ($prefix + '.stderr.tmp')
    $log = Join-Path $qaDir ($prefix + '.log')
    foreach ($p in @($stdout,$stderr,$log)) {
        if (Test-Path -LiteralPath $p) { throw ('QA_OUTPUT_EXISTS:'+ $p) }
    }
    $proc = Start-Process -FilePath $PythonExe -WorkingDirectory $wt `
        -ArgumentList @('-B','-m','unittest','discover','-s','tests/t6','-p',$pattern,'-v') `
        -Wait -PassThru -NoNewWindow -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    $outText = (Get-Content -LiteralPath $stdout -Raw) + (Get-Content -LiteralPath $stderr -Raw)
    [IO.File]::WriteAllText($log,$outText,$utf8)
    Write-Host $outText
    if ($proc.ExitCode -ne 0) { throw ($prefix + '_FAILED_EXIT_'+$proc.ExitCode) }
    if ($outText -notmatch ('Ran ' + $expected + ' tests in [\d.]+s\s+OK\s*$')) {
        throw ($prefix + '_EXPECTED_'+$expected+'_TESTS_PASS')
    }
    if ($prefix -eq 'F01_SECURITY' -and $outText -match '\bskipped=') {
        throw 'F01_REAL_JUNCTION_PROBE_SKIPPED_HOLD'
    }
    Remove-Item -LiteralPath $stdout,$stderr -Force
    return $log
}

$oldDontWrite = $env:PYTHONDONTWRITEBYTECODE
$env:PYTHONDONTWRITEBYTECODE = '1'
try {
    & $PythonExe -B -c 'import sys; assert sys.version_info[:2] == (3,12); import torch'
    if ($LASTEXITCODE -ne 0) { throw 'PYTHON312_OR_TORCH_IMPORT_FAILED' }
    $oldLog = RunSuite 'test_cache_ab_fixture.py' 16 'T6_LEGACY_16'
    $f01Log = RunSuite 'test_f01_path_containment.py' 9 'F01_SECURITY'

    $receipt = [ordered]@{
        schema = 'ttm.t6.f01.windows.author_negative_qa.v1'
        type = 'AUTHOR_QA_ONLY_NOT_CODEX_DISTINCT_REVIEW'
        source_head = $PinnedHead
        original_windows_benchmark = 'PRESERVED_NOT_RERUN'
        legacy_unittest = 'PASS_16_OF_16'
        f01_security_unittest = 'PASS_9_OF_9_REAL_WINDOWS_JUNCTION'
        source_scope = 'No TRAIN/TEST/Q1Q2/GPU/P07/P08'
        hashes_sha256 = [ordered]@{
            legacy_log = HashFile $oldLog
            security_log = HashFile $f01Log
        }
    }
    $receiptPath = Join-Path $qaDir 'TTM_T6_F01_WINDOWS_AUTHOR_QA_RECEIPT.json'
    [IO.File]::WriteAllText($receiptPath,(($receipt | ConvertTo-Json -Depth 5) + "`n"),$utf8)
    Write-Host ('T6_F01_QA_RECEIPT_SHA256=' + (HashFile $receiptPath))
    Write-Host ('T6_F01_QA_DIR=' + $qaDir)
    Write-Host 'T6_F01_WINDOWS_AUTHOR_QA=PASS_16_PLUS_9'
}
finally {
    $env:PYTHONDONTWRITEBYTECODE = $oldDontWrite
}
