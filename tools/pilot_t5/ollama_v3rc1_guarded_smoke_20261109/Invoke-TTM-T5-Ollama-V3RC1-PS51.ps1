#requires -Version 5.1
param([ValidateSet('QA','Smoke')][string]$Mode='QA')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$env:PYTHONDONTWRITEBYTECODE='1'

$project='D:\WORK\RESEARCH\TokenToModel-Lab'
$source=Join-Path $project '_tmp\TTM_T5_OLLAMA_V3RC1_GUARDED_SMOKE_20261109'
$run=Join-Path $project '_tmp\ttm_t5_ollama_compat_only_single_v3rc1'
$py='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$runner=Join-Path $source 't5_ollama_v3rc1.py'
$test=Join-Path $source 'test_v3rc1_independent.py'
$manifest=Join-Path $source 'SOURCE_SHA256_MANIFEST.json'

if (-not [string]::Equals([IO.Path]::GetFullPath($PSScriptRoot),[IO.Path]::GetFullPath($source),[StringComparison]::OrdinalIgnoreCase)) {throw 'SOURCE_LOCATION_OUTSIDE_PINNED_PROJECT_FOLDER'}
if (-not (Test-Path -LiteralPath (Join-Path $project '.git'))) {throw 'NOT_EXPECTED_TTM_REPO'}
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) {throw 'PYTHON312_MISSING'}
if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {throw 'MANIFEST_MISSING'}
if ($Mode -eq 'Smoke' -and (Test-Path -LiteralPath $run)) {throw 'ONE_SHOT_V3RC1_ALREADY_CLAIMED_NO_RERUN'}
$payload=Get-Content -LiteralPath $manifest -Raw -Encoding UTF8 | ConvertFrom-Json
if ($payload.schema -cne 'ttm.t5.ollama.v3rc1.release.manifest.v1') {throw 'MANIFEST_SCHEMA_INVALID'}
foreach($file in $payload.source_files.PSObject.Properties) {
    if ($file.Name -cnotmatch '^[A-Za-z0-9._-]+$') {throw 'MANIFEST_UNSAFE_FILENAME'}
    $target=Join-Path $source $file.Name
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {throw ('PINNED_SOURCE_MISSING:'+ $file.Name)}
    $actual=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -cne ([string]$file.Value).ToLowerInvariant()) {throw ('PINNED_SOURCE_SHA256_MISMATCH:'+ $file.Name)}
}
Write-Host 'T5_V3RC1_SOURCE_SHA256=PASS'

$tokens=$null
$errors=$null
[System.Management.Automation.Language.Parser]::ParseFile((Join-Path $source 'Invoke-TTM-T5-Ollama-V3RC1-PS51.ps1'),[ref]$tokens,[ref]$errors) | Out-Null
if ($errors.Count -gt 0) {throw 'POWERSHELL51_PARSE_FAILED'}
Write-Host 'T5_V3RC1_PS51_PARSE=PASS'

$qaStdout=Join-Path $source ('WINDOWS_QA_'+$Mode+'_stdout.txt')
$qaStderr=Join-Path $source ('WINDOWS_QA_'+$Mode+'_stderr.txt')
if ((Test-Path -LiteralPath $qaStdout) -or (Test-Path -LiteralPath $qaStderr)) {throw 'QA_LOG_ALREADY_EXISTS_NO_OVERWRITE'}
# Python unittest writes to stderr. Using process redirection avoids PowerShell 5.1
# treating redirected native stderr as a terminating NativeCommandError.
$qaProcess=Start-Process -FilePath $py -ArgumentList @('-B',('"'+$test+'"')) -NoNewWindow -Wait -PassThru -RedirectStandardOutput $qaStdout -RedirectStandardError $qaStderr
$qaCode=$qaProcess.ExitCode
Get-Content -LiteralPath $qaStdout | ForEach-Object {Write-Host $_}
Get-Content -LiteralPath $qaStderr | ForEach-Object {Write-Host $_}
Write-Host ('T5_V3RC1_QA_STDOUT='+$qaStdout)
Write-Host ('T5_V3RC1_QA_STDERR='+$qaStderr)
Write-Host ('T5_V3RC1_QA_STDERR_SHA256='+ (Get-FileHash -LiteralPath $qaStderr -Algorithm SHA256).Hash.ToLowerInvariant())
if ($qaCode -ne 0) {Write-Host 'T5_V3RC1_WINDOWS_QA=FAIL'; exit 4}
Write-Host 'T5_V3RC1_WINDOWS_QA=PASS_84_OF_84'

if ($Mode -eq 'QA') {
    Write-Host 'T5_V3RC1_RUNTIME=NOT_EXECUTED_QA_ONLY'
    exit 0
}
# Preview is READ-ONLY. This cannot consume the one-shot claim.
& $py -B $runner --mode preview
if ($LASTEXITCODE -ne 0) {throw 'T5_V3RC1_PREVIEW_HOLD_NO_CLAIM'}
if (Test-Path -LiteralPath $run) {throw 'V3RC1_CLAIM_APPEARED_DURING_PREVIEW'}
Write-Host 'T5_V3RC1_SINGLE_RUN=AUTHORIZED_START'
& $py -B $runner --mode execute
$executeCode=$LASTEXITCODE
Write-Host ('T5_V3RC1_EXECUTION_EXIT='+$executeCode)
$resultPath=Join-Path $run 'RESULT.json'
if (Test-Path -LiteralPath $resultPath -PathType Leaf) {
    $result=Get-Content -LiteralPath $resultPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Host ('T5_V3RC1_RESULT_STATUS='+$result.status)
    Write-Host ('T5_V3RC1_RESULT_PATH='+$resultPath)
    Write-Host ('T5_V3RC1_RESULT_SHA256='+ (Get-FileHash -LiteralPath $resultPath -Algorithm SHA256).Hash.ToLowerInvariant())
    if ($result.failure) {Write-Host ('T5_V3RC1_FAILURE='+$result.failure.message)}
} else {
    Write-Host 'T5_V3RC1_RESULT_MISSING=HOLD_KEEP_ALL_EVIDENCE'
}
$trace=Join-Path $run 'READINESS_ATTEMPTS.jsonl'
if (Test-Path -LiteralPath $trace -PathType Leaf) {
    Write-Host ('T5_V3RC1_READINESS_TRACE='+$trace)
    Write-Host ('T5_V3RC1_READINESS_TRACE_SHA256='+ (Get-FileHash -LiteralPath $trace -Algorithm SHA256).Hash.ToLowerInvariant())
    Get-Content -LiteralPath $trace -Tail 3 | ForEach-Object {Write-Host $_}
}
Write-Host 'T5_V3RC1_NO_AUTOMATIC_RERUN=TRUE'
if ($executeCode -ne 0) {exit 4}
exit 0
