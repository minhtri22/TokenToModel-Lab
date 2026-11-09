param([ValidateSet('Preview','Smoke')][string]$Mode='Preview')
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$source=Join-Path $root '_tmp\TTM_T5_V5_IMPORTED_MODEL_INFERENCE_ONLY_20261109'
$dest=Join-Path $root '_tmp\ttm_t5_v5_imported_model_inference_only_v1'
$python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not [string]::Equals((Split-Path -Parent $MyInvocation.MyCommand.Path),$source,[System.StringComparison]::OrdinalIgnoreCase)) { throw 'SCRIPT_OUTSIDE_EXPECTED_PROJECT_PATH' }
if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) { throw 'INVALID_TTM_ROOT' }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'PINNED_PYTHON312_NOT_FOUND' }
$origin=& git -C $root remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) { throw 'GIT_ORIGIN_NOT_AVAILABLE' }
if (@('https://github.com/minhtri22/TokenToModel-Lab.git','https://github.com/minhtri22/TokenToModel-Lab','git@github.com:minhtri22/TokenToModel-Lab.git') -notcontains ([string]$origin).Trim()) { throw 'GIT_ORIGIN_NOT_TTM' }
$manifest=Join-Path $source 'SOURCE_SHA256_MANIFEST.json'
if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) { throw 'SOURCE_MANIFEST_MISSING' }
$m=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
if ($m.schema -cne 'ttm.t5.v5.inference_resume.source.manifest.v1') { throw 'INVALID_SOURCE_MANIFEST_SCHEMA' }
foreach($p in $m.source_sha256.PSObject.Properties) {
    if ($p.Name -notmatch '^[a-zA-Z0-9_.-]+$') { throw 'SOURCE_FILE_NAME_NOT_SAFE' }
    $f=Join-Path $source $p.Name
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { throw 'SOURCE_FILE_MISSING' }
    $got=(Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($got -cne [string]$p.Value) { throw "SOURCE_HASH_MISMATCH:$($p.Name)" }
}
if (Test-Path -LiteralPath $dest) { throw 'INFERENCE_RESUME_ALREADY_CONSUMED_NO_RERUN' }
$env:PYTHONDONTWRITEBYTECODE='1'
$runner=Join-Path $source 'ttm_t5_v5_imported_resume_inference.py'
$checker=Join-Path $source 'test_resume_inference_offline.py'
Write-Host 'T5_RESUME_SOURCE_SHA256=PASS'
& $python -B $runner --mode contract
if ($LASTEXITCODE -ne 0) { throw 'SOURCE_CONTRACT_FAILED' }
& $python -B $checker
if ($LASTEXITCODE -ne 0) { throw 'OFFLINE_QA_FAILED' }
Write-Host 'T5_RESUME_OFFLINE_QA=PASS_12_OF_12'
& $python -B $runner --mode preview
if ($LASTEXITCODE -ne 0) { throw 'INFERENCE_RESUME_PREFLIGHT_FAILED' }
if ($Mode -eq 'Preview') { Write-Host 'T5_RESUME_RUNTIME=NOT_EXECUTED'; exit 0 }
if (Test-Path -LiteralPath $dest) { throw 'RESUME_ONE_SHOT_ALREADY_CLAIMED' }
Write-Host 'T5_RESUME_INFERENCE_ONLY=AUTHORIZED_BY_EXPLICIT_SMOKE'
& $python -B $runner --mode execute
$rc=$LASTEXITCODE
Write-Host "T5_RESUME_WRAPPER_EXIT=$rc"
if (Test-Path -LiteralPath (Join-Path $dest 'RESULT.json')) {
    $obj=Get-Content -LiteralPath (Join-Path $dest 'RESULT.json') -Raw | ConvertFrom-Json
    Write-Host "T5_RESUME_FINAL_STATUS=$($obj.status)"
    Write-Host "T5_RESUME_RESULT_SHA256=$((Get-FileHash -LiteralPath (Join-Path $dest 'RESULT.json') -Algorithm SHA256).Hash.ToLowerInvariant())"
}
Write-Host 'T5_RESUME_NO_AUTOMATIC_RERUN=TRUE'
exit $rc
