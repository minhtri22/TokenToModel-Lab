# PowerShell 5.1, execute from project-local extracted private bundle only.
# Source SHA and private checkpoint SHA are validated before any CLAIM.
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$source = $PSScriptRoot
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$out = Join-Path $root '_tmp\ttm_small4m_gemma2_zero_gate_residual_32_cpu_probe_20261109_v1'
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'PYTHON312_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'PROJECT_ROOT_NOT_FOUND' }
if (Test-Path -LiteralPath $out) { throw 'ONE_SHOT_OUTPUT_EXISTS_NO_RETRY' }
if ((Split-Path -Parent $source).ToLowerInvariant() -ne (Join-Path $root '_tmp').ToLowerInvariant()) {
    throw 'SOURCE_NOT_WITHIN_PROJECT_TMP'
}
$hashPins = @{
  'ttm_gemma2_gate32_cpu_once.py' = '235816631eedbe212f7f431700024f1e4ae8e470fd5b0cabcdabd78421c815bf';
  'ttm_gemma2_gate32_independent_readback.py' = 'd25296daa0ff3185dc078195d0b239b655c0d305a031a3d0129d9b5a5d05cbca';
  'checkpoint.pt' = 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b';
  'candidate_initialization.pt' = 'c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3';
  'src\p02_exact.py' = 'e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07';
  'src\ttm_embeddinggemma2_swap.py' = 'd11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39'
}
foreach ($key in $hashPins.Keys) {
    $item = Join-Path $source $key
    if (-not (Test-Path -LiteralPath $item -PathType Leaf)) { throw "MISSING_SOURCE=$key" }
    $actual = (Get-FileHash -LiteralPath $item -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $hashPins[$key]) { throw "SOURCE_SHA256_MISMATCH=$key" }
}
$env:CUDA_VISIBLE_DEVICES = '-1'
$env:PYTHONDONTWRITEBYTECODE = '1'
& $py -B -c 'import sys,torch,numpy; assert sys.version_info[:2]==(3,12); print(sys.version.split()[0],torch.__version__)'
if ($LASTEXITCODE -ne 0) { throw 'CPU_RUNTIME_CHECK_FAIL_NO_CLAIM' }
# The runner checks PACK sha256, all sources, and zero-gate logits BEFORE atomic CLAIM.
& $py -B (Join-Path $source 'ttm_gemma2_gate32_cpu_once.py') --mode execute --repo $root --source $source
if ($LASTEXITCODE -ne 0) { throw 'GATED32_ONE_SHOT_FAILED_OR_INTERRUPTED_DO_NOT_RERUN' }
& $py -B (Join-Path $source 'ttm_gemma2_gate32_independent_readback.py') --repo $root
if ($LASTEXITCODE -ne 0) { throw 'GATED32_READBACK_HOLD_NO_RESCORING' }
Write-Host 'TTM_GATED32_SCIENCE_EXECUTED_ONCE=PASS_SCORED_UNADJUDICATED'
Write-Host '=== RESULT.json (PUBLIC) ==='
Get-Content -LiteralPath (Join-Path $out 'RESULT.json') -Raw
Write-Host '=== INDEPENDENT_READBACK_PUBLIC.json ==='
Get-Content -LiteralPath (Join-Path $out 'INDEPENDENT_READBACK_PUBLIC.json') -Raw
Write-Host "GATED32_RESULT_SHA256=$((Get-FileHash -LiteralPath (Join-Path $out 'RESULT.json') -Algorithm SHA256).Hash)"