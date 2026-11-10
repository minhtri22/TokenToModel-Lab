[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][ValidatePattern('^[a-f0-9]{40}$')][string]$ExpectedCommit,
  [string]$ProjectRoot='D:\WORK\RESEARCH\TokenToModel-Lab',
  [string]$Python312='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
if($PSVersionTable.PSVersion.Major -ne 5){throw 'POWERSHELL51_REQUIRED'}
$ProjectRoot=(Resolve-Path -LiteralPath $ProjectRoot).Path
if($ProjectRoot.TrimEnd('\') -ine 'D:\WORK\RESEARCH\TokenToModel-Lab'){throw 'EXACT_PROJECT_ROOT_REQUIRED'}
if(-not (Test-Path -LiteralPath $Python312 -PathType Leaf)){throw 'PYTHON312_NOT_FOUND'}
$git=(Get-Command git.exe -CommandType Application -ErrorAction Stop).Source
$ref=Join-Path $ProjectRoot '_tmp\TTM_T5_C01_C04_P02_FP32_FROZEN_REFERENCE_20261110.zip'
$stage=Join-Path $ProjectRoot '_tmp\ttm_t5_c01c04_gelu_erf_confirmatory_one_shot_20261110'
$src=Join-Path $ProjectRoot '_tmp\ttm_t5_c01c04_source_lock_20261110'
if(-not (Test-Path -LiteralPath $ref -PathType Leaf)){throw 'FROZEN_TRUE_P02_REFERENCE_ZIP_REQUIRED'}
$refHash=(Get-FileHash -LiteralPath $ref -Algorithm SHA256).Hash.ToLowerInvariant()
if($refHash -ne 'e5d522bd5234c46af77dbb85990779bd09e25d35be587538cec577ee486c5996'){
  throw 'FROZEN_TRUE_P02_REFERENCE_ZIP_SHA_MISMATCH'
}
if((Test-Path -LiteralPath $stage) -or (Test-Path -LiteralPath $src)){
  throw 'CONFIRMATORY_ALREADY_STARTED_OR_PARTIAL_NO_RETRY'
}
& $Python312 -c 'import sys; assert sys.version_info[:2] == (3,12)'
if($LASTEXITCODE -ne 0){throw 'PYTHON312_VERSION_MISMATCH'}
New-Item -ItemType Directory -Path $src -ErrorAction Stop | Out-Null
function Get-TTMSource {
  param([string]$Relative,[string]$Target,[string]$Blob)
  if(Test-Path -LiteralPath $Target){throw "SOURCE_EXISTS_NO_OVERWRITE:$Relative"}
  $url="https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/$ExpectedCommit/$Relative"
  Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $Target -ErrorAction Stop
  $actual=(& $git -C $ProjectRoot hash-object $Target).Trim()
  if($LASTEXITCODE -ne 0 -or $actual -ne $Blob){throw "SOURCE_GIT_BLOB_MISMATCH:$Relative"}
  Write-Host "SOURCE_PIN_PASS=$Relative"
}
$prefix='tools/pilot_t5/exact_root_v1/confirmatory_v1'
$cpp=Join-Path $src 'ttm_t5_c01c04_gelu_erf_confirmatory_probe.cpp'
$cmake=Join-Path $src 'CMakeLists.txt'
$checker=Join-Path $src 'independent_strict_c01c04_checker.py'
$tests=Join-Path $src 'test_confirmatory_static_and_negative_cases.py'
$runner=Join-Path $src 'run_c01c04_gelu_erf_confirmatory_once.py'
Get-TTMSource -Relative "$prefix/ttm_t5_c01c04_gelu_erf_confirmatory_probe.cpp" -Target $cpp -Blob 'f14f4e8eaecba273a5fe314d04e8498c40c76655'
Get-TTMSource -Relative "$prefix/CMakeLists.txt" -Target $cmake -Blob '9e829fbdc0415582a81e9d64c2b3da689cfd6b12'
Get-TTMSource -Relative "$prefix/independent_strict_c01c04_checker.py" -Target $checker -Blob 'b38c09278588c3e8bf40208cbbacf8448bfdd97e'
Get-TTMSource -Relative "$prefix/test_confirmatory_static_and_negative_cases.py" -Target $tests -Blob 'afad6dde4cbebddb469c71b3e7de45c2f08ef0e7'
Get-TTMSource -Relative "$prefix/run_c01c04_gelu_erf_confirmatory_once.py" -Target $runner -Blob 'f92acb80692ca365aafbb67a059dd5c531fa5fa0'
$env:PYTHONDONTWRITEBYTECODE='1'
& $Python312 -m py_compile $checker $tests $runner
if($LASTEXITCODE -ne 0){throw 'PYTHON_CONFIRMATORY_PARSE_FAILED_C_NO_NATIVE'}
Write-Host 'TRUE_P02_C01_C04_REFERENCE_SHA=PASS'
Write-Host 'CONFIRMATORY_SOURCE_GIT_BLOB_5_OF_5=PASS'
Write-Host 'CONFIRMATORY_OWNER_SCOPE=EXACT_ONE_FOUR_C01_C04_NATIVE'
Write-Host 'HISTORICAL_AND_DISCOVERY_RERUN=NO'
Write-Host 'PR16=HOLD_UNTIL_INDEPENDENT_ADJUDICATION'
& $Python312 -B $runner --project-root $ProjectRoot --source-dir $src --reference-zip $ref --approve-exact-once 'I_APPROVE_ONE_TTM_T5_C01_C04_GELU_ERF_STRICT_CONFIRMATORY'
if($LASTEXITCODE -ne 0){
  Write-Warning 'CONFIRMATORY_HOLD: DO NOT RETRY. Preserve original and new evidence.'
}
