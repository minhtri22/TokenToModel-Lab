[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][ValidatePattern('^[a-f0-9]{40}$')]
  [string] $ExpectedCommit,
  [string] $ProjectRoot='D:\WORK\RESEARCH\TokenToModel-Lab',
  [string] $Python312='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest

# Source-only recovery of pre-native syntax failure. No old file overwrite.
if ($PSVersionTable.PSVersion.Major -ne 5) { throw 'PS51_REQUIRED' }
$ProjectRoot=(Resolve-Path -LiteralPath $ProjectRoot -ErrorAction Stop).Path
if ($ProjectRoot.TrimEnd('\') -ine 'D:\WORK\RESEARCH\TokenToModel-Lab') { throw 'PROJECT_ROOT_NOT_EXACT_TTM' }
if (-not (Test-Path -LiteralPath $Python312 -PathType Leaf)) { throw 'PYTHON312_NOT_FOUND' }
$git=(Get-Command git.exe -CommandType Application -ErrorAction Stop).Source
$oldDir=Join-Path $ProjectRoot '_tmp\ttm_t5_c01c04_source_lock_20261110'
$newDir=Join-Path $ProjectRoot '_tmp\ttm_t5_c01c04_source_lock_syntaxfix_v2_20261110'
$stage=Join-Path $ProjectRoot '_tmp\ttm_t5_c01c04_gelu_erf_confirmatory_one_shot_20261110'
$ref=Join-Path $ProjectRoot '_tmp\TTM_T5_C01_C04_P02_FP32_FROZEN_REFERENCE_20261110.zip'
if (Test-Path -LiteralPath $stage) { throw 'CONFIRMATORY_STAGE_ALREADY_EXISTS_DO_NOT_RERUN' }
if (Test-Path -LiteralPath $newDir) { throw 'SOURCE_RECOVERY_V2_ALREADY_STAGED_NO_OVERWRITE' }
if (-not (Test-Path -LiteralPath $oldDir -PathType Container)) { throw 'ORIGINAL_SOURCE_LOCK_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $ref -PathType Leaf)) { throw 'REFERENCE_ZIP_NOT_FOUND' }
if ((Get-FileHash -LiteralPath $ref -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'e5d522bd5234c46af77dbb85990779bd09e25d35be587538cec577ee486c5996') { throw 'REFERENCE_ZIP_SHA_MISMATCH' }
& $Python312 -c 'import sys; assert sys.version_info[:2] == (3, 12)'
if ($LASTEXITCODE -ne 0) { throw 'PYTHON312_VERSION_MISMATCH' }

function Assert-TTM-GitBlob {
  param([string]$Path,[string]$ExpectedBlob)
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "SOURCE_NOT_FOUND:$Path" }
  $actual=(& $git -C $ProjectRoot hash-object $Path).Trim()
  if ($LASTEXITCODE -ne 0 -or $actual -ne $ExpectedBlob) { throw "SOURCE_GIT_BLOB_MISMATCH:$Path" }
}
$original=@{
  'ttm_t5_c01c04_gelu_erf_confirmatory_probe.cpp'='f14f4e8eaecba273a5fe314d04e8498c40c76655'
  'CMakeLists.txt'='9e829fbdc0415582a81e9d64c2b3da689cfd6b12'
  'independent_strict_c01c04_checker.py'='b38c09278588c3e8bf40208cbbacf8448bfdd97e'
  'test_confirmatory_static_and_negative_cases.py'='afad6dde4cbebddb469c71b3e7de45c2f08ef0e7'
  'run_c01c04_gelu_erf_confirmatory_once.py'='f92acb80692ca365aafbb67a059dd5c531fa5fa0'
}
foreach ($name in $original.Keys) {
  Assert-TTM-GitBlob -Path (Join-Path $oldDir $name) -ExpectedBlob $original[$name]
}
Write-Host 'ORIGINAL_5_SOURCE_BLOBS=PASS_PRESERVED_NO_OVERWRITE'

New-Item -ItemType Directory -Path $newDir -ErrorAction Stop | Out-Null
foreach ($name in @('ttm_t5_c01c04_gelu_erf_confirmatory_probe.cpp','CMakeLists.txt','test_confirmatory_static_and_negative_cases.py')) {
  $from=Join-Path $oldDir $name
  $dest=Join-Path $newDir $name
  if (Test-Path -LiteralPath $dest) { throw "NO_SOURCE_OVERWRITE:$name" }
  Copy-Item -LiteralPath $from -Destination $dest -ErrorAction Stop
  Assert-TTM-GitBlob -Path $dest -ExpectedBlob $original[$name]
}
$prefix='tools/pilot_t5/exact_root_v1/confirmatory_v1/'
$fixes=@(
  @{Name='independent_strict_c01c04_checker.py';Blob='cef0e214bb178f7e5059c5ada0200e75b3970936'},
  @{Name='run_c01c04_gelu_erf_confirmatory_once.py';Blob='aca05ce2791385a69fcd7d933fd5079e4088358b'}
)
foreach ($fix in $fixes) {
  $dest=Join-Path $newDir $fix.Name
  $url="https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/$ExpectedCommit/$prefix$($fix.Name)"
  if (Test-Path -LiteralPath $dest) { throw "FIXED_SOURCE_ALREADY_EXISTS:$dest" }
  Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $dest -ErrorAction Stop
  Assert-TTM-GitBlob -Path $dest -ExpectedBlob $fix.Blob
}
Write-Host 'RECOVERED_5_SOURCE_BLOBS=PASS'
$checker=Join-Path $newDir 'independent_strict_c01c04_checker.py'
$test=Join-Path $newDir 'test_confirmatory_static_and_negative_cases.py'
$runner=Join-Path $newDir 'run_c01c04_gelu_erf_confirmatory_once.py'
$env:PYTHONDONTWRITEBYTECODE='1'
& $Python312 -m py_compile $checker $test $runner
if ($LASTEXITCODE -ne 0) { throw 'PYTHON_SYNTAX_FAILED_NO_NATIVE' }
Write-Host 'PYTHON_ALL_SOURCES_PARSE=PASS'
& $Python312 -B $test
if ($LASTEXITCODE -ne 0) { throw 'NEGATIVE_QA_FAILED_NO_NATIVE' }
Write-Host 'INDEPENDENT_NEGATIVE_QA_12_OF_12=PASS'
Write-Host 'ORIGINAL_SOURCE_LOCK=UNCHANGED'
Write-Host 'CONFIRMATORY_STAGE=NOT_YET_STARTED'
& $Python312 -B $runner --project-root $ProjectRoot --source-dir $newDir --reference-zip $ref --approve-exact-once 'I_APPROVE_ONE_TTM_T5_C01_C04_GELU_ERF_STRICT_CONFIRMATORY'
if ($LASTEXITCODE -ne 0) {
  Write-Warning 'CONFIRMATORY_HOLD_PRESERVE_EVIDENCE_NO_RETRY'
  exit 2
}
Write-Host 'CONFIRMATORY_ONE_SHOT_RUNNER_EXIT=0'
