# TTM-SM4M-DIAG-Q001 — source-only, no private checkpoint/model invocation.
param(
  [string]$ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab',
  [Parameter(Mandatory=$true)][string]$ExpectedRunnerSHA256,
  [string]$CandidatePath = ''
)
$ErrorActionPreference='Stop'
$Python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
# Script is checked out in exact-reviewed GitHub source directory; never _tmp.
if (-not $CandidatePath) { $CandidatePath=Join-Path $PSScriptRoot 'ttm_sm4m_diag_q001.py' }
$root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')+'\'
$source=[IO.Path]::GetFullPath($CandidatePath)
if (-not $source.StartsWith($root,[StringComparison]::OrdinalIgnoreCase)) {throw 'HOLD_RUNNER_OUTSIDE_PROJECT'}
if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {throw 'HOLD_RUNNER_MISSING'}
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {throw 'HOLD_PYTHON312_NOT_FOUND'}
if ($ExpectedRunnerSHA256 -cnotmatch '^[0-9a-f]{64}$') {throw 'HOLD_RUNNER_PIN_64HEX_REQUIRED'}
$actual=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -cne $ExpectedRunnerSHA256) {throw 'HOLD_SOURCE_SHA_MISMATCH'}
& $Python -c 'import sys; assert sys.version_info[:2]==(3,12)'
if ($LASTEXITCODE -ne 0) {throw 'HOLD_PY312_VERSION'}
& $Python $source source-qa
if ($LASTEXITCODE -ne 0) {throw 'HOLD_SOURCE_QA_FAILED'}
Write-Output 'PASS_SOURCE_QA_ONLY_NO_FIXTURES_NO_MODEL'
