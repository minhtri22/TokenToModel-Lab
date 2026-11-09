param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{40}$')][string]$ExpectedHead,
    [ValidateSet('Preview','QA')][string]$Mode='Preview',
    [switch]$CleanupIfPublished,
    [string]$PythonExe = ""
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$remote='https://github.com/minhtri22/TokenToModel-Lab.git'
$branch='research/ttm-small-4m-colab-pilot-prereg-20261108'
$pythonRel='tools/qa/ttm_pr12_github_single_integrated_qa.py'
$sourceBlob='fc886061863f5d5eb63b3f4e0e63cd6f726f8efb'

if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) {throw 'TTM_REPO_NOT_FOUND'}
$origin=(& git -C $root remote get-url origin 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or @($remote,$remote.Substring(0,$remote.Length-4),'git@github.com:minhtri22/TokenToModel-Lab.git') -notcontains $origin) {throw 'TTM_ORIGIN_MISMATCH'}
$current=(& git -C $root ls-remote origin "refs/heads/$branch" 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or -not $current.StartsWith("$ExpectedHead" + [char]9)) {throw 'TTM_PR12_REMOTE_HEAD_MISMATCH'}
if ($Mode -eq 'Preview') {
    Write-Host 'TTM_PR12_GITHUB_SOURCE_OF_TRUTH=PASS_EXACT_HEAD'
    Write-Host 'TTM_PR12_PREVIEW=PASS_NO_DOWNLOAD_NO_QA'
    exit 0
}
$python=$null
$candidates=New-Object System.Collections.Generic.List[string]
if (-not [string]::IsNullOrWhiteSpace($PythonExe)) {
    $candidates.Add($PythonExe)
} else {
    if (-not [string]::IsNullOrWhiteSpace($env:CONDA_PREFIX)) {
        $candidates.Add((Join-Path $env:CONDA_PREFIX 'python.exe'))
    }
    $candidates.Add((Join-Path $env:USERPROFILE 'miniforge3\envs\cfcr-gpu-311\python.exe'))
    $candidates.Add((Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'))
    $candidates.Add((Join-Path $env:USERPROFILE 'miniforge3\python.exe'))
}
foreach ($candidate in $candidates) {
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
    $ok=$false
    try {
        & $candidate -I -c 'import sys; assert sys.version_info >= (3, 11); import pytest, numpy, torch, regex' 2>&1 | Out-Null
        $ok=($LASTEXITCODE -eq 0)
    } catch { $ok=$false }
    if ($ok) { $python=$candidate; break }
}
if ([string]::IsNullOrWhiteSpace($python)) {
    throw 'NO_PYTHON_WITH_PYTEST_NUMPY_TORCH_REGEX_BEFORE_QA_CLAIM'
}
Write-Host ('TTM_PR12_QA_SELECTED_PYTHON=' + $python)
Write-Host 'TTM_PR12_QA_DEPENDENCY_PREFLIGHT=PASS_NO_INSTALL'
$tmp=Join-Path $root ('_tmp\TTM_PR12_BOOTSTRAP_'+$ExpectedHead.Substring(0,12))
if (Test-Path -LiteralPath $tmp) {throw 'TTM_PR12_BOOTSTRAP_ALREADY_EXISTS_NO_OVERWRITE'}
[System.IO.Directory]::CreateDirectory($tmp) | Out-Null
$download=Join-Path $tmp 'ttm_pr12_github_single_integrated_qa.py'
$url="https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/$ExpectedHead/$pythonRel"
Invoke-WebRequest -Uri $url -UseBasicParsing -OutFile $download -TimeoutSec 60
if (-not (Test-Path -LiteralPath $download -PathType Leaf)) {throw 'QA_SOURCE_DOWNLOAD_MISSING'}
$blob=(& git hash-object -t blob --no-filters -- $download 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $blob -cne $sourceBlob) {throw 'QA_SOURCE_EXACT_GIT_BLOB_MISMATCH'}
$expectedSha256='ad26e6303f27178637a767735efd3b3c6e072ec31211326bbc794c79b27c300e'
$actualSha256=(Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualSha256 -cne $expectedSha256) {throw 'QA_SOURCE_SHA256_MISMATCH'}
Write-Host 'TTM_PR12_QA_SOURCE_GITHUB_BLOB=PASS'
Write-Host 'TTM_PR12_QA_SOURCE_SHA256=PASS'
$argv=@('-B',$download,'--head',$ExpectedHead,'--mode','qa')
if ($CleanupIfPublished) {$argv+=@('--cleanup-if-published')}
& $python @argv
$rc=$LASTEXITCODE
Write-Host "TTM_PR12_WINDOWS_QA_EXIT=$rc"
if ($rc -eq 0 -and $CleanupIfPublished) {
    $resolved=[System.IO.Path]::GetFullPath($tmp)
    $expectedParent=[System.IO.Path]::GetFullPath((Join-Path $root '_tmp'))
    if ([System.IO.Path]::GetDirectoryName($resolved) -cne $expectedParent) {throw 'BOOTSTRAP_CLEANUP_SCOPE_INVALID'}
    $item=Get-Item -LiteralPath $tmp -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {throw 'BOOTSTRAP_REPARSE_POINT'}
    Remove-Item -LiteralPath $tmp -Recurse -Force
    Write-Host 'TTM_PR12_BOOTSTRAP_CLEANUP=PASS_SCOPED_AFTER_GITHUB_READBACK'
}
exit $rc
