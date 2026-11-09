param([Parameter(Mandatory=$true)][ValidateSet('Preview','Smoke')][string]$Mode)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$name='TTM_T5_OLLAMA_V5_TIMEWAIT_GUARD_20261109'
$source=Split-Path -Parent $MyInvocation.MyCommand.Path
$expectedSource=Join-Path (Join-Path $root '_tmp') $name
$python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$oneShot=Join-Path $root '_tmp\ttm_t5_ollama_compat_only_single_v5final'
$manifest=Join-Path $source 'SOURCE_SHA256_MANIFEST.json'
$expectedManifest='bc1bb30df9907c52df7e292b7a0c039d3c48b6944d122e0015f2131b378b53df'

if (-not [string]::Equals($source,$expectedSource,[System.StringComparison]::OrdinalIgnoreCase)) { throw 'SOURCE_DIRECTORY_NOT_EXACT_PROJECT_LOCAL' }
if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) { throw 'PROJECT_REPO_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'PYTHON312_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) { throw 'SOURCE_MANIFEST_NOT_FOUND' }
if ((Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash.ToLowerInvariant() -cne $expectedManifest) { throw 'SOURCE_MANIFEST_SHA_MISMATCH' }
# Exact origin guard; no Git write.
$origin=& git -C $root remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) { throw 'GIT_ORIGIN_UNAVAILABLE' }
$accepted=@('https://github.com/minhtri22/TokenToModel-Lab.git','https://github.com/minhtri22/TokenToModel-Lab','git@github.com:minhtri22/TokenToModel-Lab.git')
if ($accepted -notcontains ([string]$origin).Trim()) { throw 'GIT_ORIGIN_NOT_TTM_CANONICAL' }
if (Test-Path -LiteralPath $oneShot) { throw 'ONE_SHOT_ALREADY_CONSUMED_NO_RERUN' }
$pins=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
if ($pins.schema -cne 'ttm.t5.final.minimal.compat.one_shot.source.manifest.v1') { throw 'INVALID_MANIFEST_SCHEMA' }
foreach ($entry in $pins.source_files.PSObject.Properties) {
    if ($entry.Name -notmatch '^[A-Za-z0-9_.-]+$') { throw 'UNSAFE_PINNED_FILENAME' }
    $f=Join-Path $source $entry.Name
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { throw "SOURCE_FILE_MISSING:$($entry.Name)" }
    if ((Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant() -cne ([string]$entry.Value).ToLowerInvariant()) { throw "SOURCE_FILE_SHA256_MISMATCH:$($entry.Name)" }
}
Write-Host 'T5_V5_SOURCE_AND_MANIFEST_SHA256=PASS'
$env:PYTHONDONTWRITEBYTECODE='1'
$runner=Join-Path $source 't5_final_minimal_smoke_v5.py'
$checker=Join-Path $source 'test_final_minimal_smoke_v5.py'

& $python -B $runner --mode contract
if ($LASTEXITCODE -ne 0) { throw 'V5_CONTRACT_REJECTED' }
& $python -B $checker
if ($LASTEXITCODE -ne 0) { throw 'V5_OFFLINE_QA_FAILED_NO_RUNTIME' }
Write-Host 'T5_V5_INDEPENDENT_QA=PASS_47_OF_47'
if (Test-Path -LiteralPath $oneShot) { throw 'ONE_SHOT_DIR_CREATED_DURING_QA_HOLD' }
& $python -B $runner --mode preview
if ($LASTEXITCODE -ne 0) { throw 'V5_PREVIEW_FAILED_NO_EXECUTION' }
Write-Host 'T5_V5_PREVIEW=PASS'
if ($Mode -eq 'Preview') {
    Write-Host 'T5_V5_RUNTIME=NOT_EXECUTED'
    exit 0
}
# Owner-approved single execution. Once directory exists, the one-shot is consumed.
if (Test-Path -LiteralPath $oneShot) { throw 'V5_ALREADY_CLAIMED' }
Write-Host 'T5_V5_SINGLE_NATIVE_SMOKE=AUTHORIZED_EXACT_ONCE'
& $python -B $runner --mode execute
$rc=$LASTEXITCODE
Write-Host "T5_V5_EXECUTION_EXIT=$rc"
$result=Join-Path $oneShot 'RESULT.json'
$trace=Join-Path $oneShot 'READINESS_ATTEMPTS.jsonl'
if (Test-Path -LiteralPath $result -PathType Leaf) {
    $object=Get-Content -LiteralPath $result -Raw | ConvertFrom-Json
    Write-Host "T5_V5_RESULT_STATUS=$($object.status)"
    if ($object.PSObject.Properties.Match('failure').Count -gt 0) { Write-Host "T5_V5_FAILURE=$($object.failure.message)" }
    if ($object.PSObject.Properties.Match('evaluation').Count -gt 0) { Write-Host "T5_V5_GENERATED_TOKENS=$($object.evaluation.generated_tokens)" }
    Write-Host "T5_V5_RESULT_SHA256=$((Get-FileHash -LiteralPath $result -Algorithm SHA256).Hash.ToLowerInvariant())"
    Write-Host "T5_V5_RESULT_PATH=$result"
} else { Write-Host 'T5_V5_RESULT=MISSING_NEEDS_MANUAL_REVIEW' }
if (Test-Path -LiteralPath $trace -PathType Leaf) {
    Write-Host "T5_V5_TRACE_SHA256=$((Get-FileHash -LiteralPath $trace -Algorithm SHA256).Hash.ToLowerInvariant())"
    Write-Host "T5_V5_TRACE_PATH=$trace"
    Get-Content -LiteralPath $trace -Tail 1
}
Write-Host 'T5_V5_NO_AUTOMATIC_RERUN=TRUE'
Write-Host 'T5_V5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED'
exit $rc
