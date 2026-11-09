param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{40}$')][string]$ExpectedHead,
    [ValidateSet('Preview','QA')][string]$Mode='Preview',
    [switch]$CleanupIfPublished
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$remote='https://github.com/minhtri22/TokenToModel-Lab.git'
$branch='research/ttm-small-4m-colab-pilot-prereg-20261108'
$pythonRel='tools/qa/ttm_pr12_github_single_integrated_qa.py'
$sourceBlob='95696be90c8255631535c29e25c698cf5ae44946'

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
$tmp=Join-Path $root ('_tmp\TTM_PR12_BOOTSTRAP_'+$ExpectedHead.Substring(0,12))
if (Test-Path -LiteralPath $tmp) {throw 'TTM_PR12_BOOTSTRAP_ALREADY_EXISTS_NO_OVERWRITE'}
[System.IO.Directory]::CreateDirectory($tmp) | Out-Null
$download=Join-Path $tmp 'ttm_pr12_github_single_integrated_qa.py'
$url="https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/$ExpectedHead/$pythonRel"
Invoke-WebRequest -Uri $url -UseBasicParsing -OutFile $download -TimeoutSec 60
if (-not (Test-Path -LiteralPath $download -PathType Leaf)) {throw 'QA_SOURCE_DOWNLOAD_MISSING'}
$blob=(& git hash-object -t blob --no-filters -- $download 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $blob -cne $sourceBlob) {throw 'QA_SOURCE_EXACT_GIT_BLOB_MISMATCH'}
$expectedSha256='5d16f2c881e37867a3c76a70835b221553d53b600feeb5de7786cfae03460275'
$actualSha256=(Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualSha256 -cne $expectedSha256) {throw 'QA_SOURCE_SHA256_MISMATCH'}
Write-Host 'TTM_PR12_QA_SOURCE_GITHUB_BLOB=PASS'
Write-Host 'TTM_PR12_QA_SOURCE_SHA256=PASS'
$python=(Get-Command python.exe -ErrorAction Stop).Source
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
