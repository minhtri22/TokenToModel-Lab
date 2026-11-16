# Guarded I2 CPU launcher; exact owner-internal policy OR legacy authenticated signatures.
# NO execution merely because owner selected conditional GO. No auto-retries.
param(
  [string]$ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab',
  [Parameter(Mandatory=$true)][string]$PermitPath,
  [Parameter(Mandatory=$true)][string]$CheckpointPath,
  [Parameter(Mandatory=$true)][string]$TokenInventoryPath,
  [Parameter(Mandatory=$true)][string]$TokenizerSourcePath,
  [Parameter(Mandatory=$true)][string]$FixtureDir,
  [Parameter(Mandatory=$true)][string]$OutputDir,
  [Parameter(Mandatory=$true)][string]$ExpectedRunnerSHA256,
  [Parameter(Mandatory=$true)][string]$ExpectedWatchdogSHA256,
  [Parameter(Mandatory=$true)][string]$ExpectedJobGuardSHA256,
  [string]$RunnerPath=''
)
$ErrorActionPreference='Stop'
$Python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$PinnedRunner=Join-Path $PSScriptRoot 'ttm_sm4m_diag_q001.py'
if (-not $RunnerPath) {$RunnerPath=$PinnedRunner}
if ([IO.Path]::GetFullPath($RunnerPath) -ine $PinnedRunner) {throw 'HOLD_RUNNER_PATH_NOT_PINNED'}
if ($ExpectedRunnerSHA256 -cnotmatch '^[0-9a-f]{64}$') {throw 'HOLD_RUNNER_PIN_FORMAT'}
if ($ExpectedWatchdogSHA256 -cnotmatch '^[0-9a-f]{64}$') {throw 'HOLD_WATCHDOG_PIN_FORMAT'}
if ($ExpectedJobGuardSHA256 -cnotmatch '^[0-9a-f]{64}$') {throw 'HOLD_JOB_GUARD_PIN_FORMAT'}
if ($ExpectedRunnerSHA256 -cne '8f2606f075738dcb85a15a9f1a506aafbbb3a255f0ec2f1f1615b2f8930bd693') {throw 'HOLD_RUNNER_PIN_NOT_REVIEWED'}
if ($ExpectedWatchdogSHA256 -cne 'd80f46e6d023fa165b097fb449a3844a47a3020416a7b22240fa4c4a2cdbce4c') {throw 'HOLD_WATCHDOG_PIN_NOT_REVIEWED'}
if ($ExpectedJobGuardSHA256 -cne 'e00c9e3b0bffecc68956f42d1aa9b76119fd5d4bd1c52647711ea398459b585b') {throw 'HOLD_JOB_GUARD_PIN_NOT_REVIEWED'}
$JobGuard=Join-Path $PSScriptRoot 'windows_job_memory_limit.py'
if (-not (Test-Path -LiteralPath $JobGuard -PathType Leaf)) {throw 'HOLD_JOB_GUARD_MISSING'}
if ((Get-FileHash -LiteralPath $JobGuard -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedJobGuardSHA256) {
    throw 'HOLD_JOB_GUARD_ACTUAL_SHA'
}
$WatchdogModule=Join-Path $PSScriptRoot 'Watch-TTM-SM4M-ProcessTree-PS51.ps1'
if (-not (Test-Path -LiteralPath $WatchdogModule -PathType Leaf)) {throw 'HOLD_WATCHDOG_MODULE_MISSING'}
$WatchdogBytes=[IO.File]::ReadAllBytes($WatchdogModule)
$hasher=[Security.Cryptography.SHA256]::Create()
try {
    $ActualWatchdogSHA256=[BitConverter]::ToString($hasher.ComputeHash($WatchdogBytes)).Replace('-','').ToLowerInvariant()
} finally {
    $hasher.Dispose()
}
if ($ActualWatchdogSHA256 -cne $ExpectedWatchdogSHA256) {throw 'HOLD_WATCHDOG_SOURCE_SHA'}
# Execute the exact verified buffer, without reopening a mutable module path.
. ([scriptblock]::Create([Text.Encoding]::UTF8.GetString($WatchdogBytes)))
if (-not (Get-Command Invoke-TTMDiagProcessWatch -CommandType Function -ErrorAction SilentlyContinue)) {
    throw 'HOLD_WATCHDOG_FUNCTION_NOT_LOADED'
}
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {throw 'HOLD_PY312_NOT_FOUND'}
$root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')+'\'
foreach($path in @($RunnerPath,$PermitPath,$CheckpointPath,$TokenInventoryPath,$TokenizerSourcePath,$FixtureDir,$OutputDir)) {
  if (-not [IO.Path]::GetFullPath($path).StartsWith($root,[StringComparison]::OrdinalIgnoreCase)) {throw 'HOLD_OUTSIDE_PROJECT'}
}
if (-not (Test-Path -LiteralPath $RunnerPath -PathType Leaf)) {throw 'HOLD_RUNNER_MISSING'}
if ((Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedRunnerSHA256) {throw 'HOLD_RUNNER_SHA'}
$guard=Join-Path $PSScriptRoot 'release_auth_v2.py'
if ((Get-FileHash -LiteralPath $guard -Algorithm SHA256).Hash.ToLowerInvariant() -cne 'cd0d2ff8496186146f605d1c07f24ba7a87a6d92343bc23b4c9b4ba10564ec09') {throw 'HOLD_RELEASE_GUARD_SHA'}
if (Test-Path -LiteralPath $OutputDir) {throw 'HOLD_OUTPUT_NOT_FRESH'}
& $Python -c 'import sys; assert sys.version_info[:2]==(3,12)'
if ($LASTEXITCODE -ne 0) {throw 'HOLD_PYTHON_VERSION'}
# Authenticate exact reviewed owner scope or legacy signatures BEFORE private checkpoint reads.
& $Python $RunnerPath release-preflight --root $ProjectRoot --permit $PermitPath --token-inventory $TokenInventoryPath --tokenizer-source $TokenizerSourcePath --fixture-dir $FixtureDir
if ($LASTEXITCODE -ne 0) {throw 'HOLD_AUTHENTICATED_RELEASE_PREFLIGHT'}
if (-not (Test-Path -LiteralPath $CheckpointPath -PathType Leaf)) {throw 'HOLD_CHECKPOINT_NOT_FOUND'}
if (-not (Test-Path -LiteralPath $FixtureDir -PathType Container)) {throw 'HOLD_FROZEN_FIXTURE_NOT_FOUND'}
$logRoot=Join-Path $ProjectRoot '_tmp\ttm_sm4m_diag_q001_one_shot_logs'
if (-not (Test-Path -LiteralPath $logRoot)) {New-Item -ItemType Directory -Path $logRoot | Out-Null}
$logOut=Join-Path $logRoot 'RUN_stdout.txt'
$logErr=Join-Path $logRoot 'RUN_stderr.txt'
if ((Test-Path -LiteralPath $logOut) -or (Test-Path -LiteralPath $logErr)) {throw 'HOLD_ONESHOT_ALREADY_CONSUMED'}
# OS job-wide hard COMMITTED memory cap is applied before child resumes.
# Separate watchdog continues sampling tree RSS, wall time and total output.
$runnerArgs=@($RunnerPath,'run','--root',$ProjectRoot,'--permit',$PermitPath,'--checkpoint',$CheckpointPath,
        '--token-inventory',$TokenInventoryPath,'--tokenizer-source',$TokenizerSourcePath,
        '--fixture-dir',$FixtureDir,'--out',$OutputDir)
$argv=@($JobGuard,'--guard','--cwd',$ProjectRoot,'--max-job-commit-bytes','12884901888',
        '--wall-seconds','900','--',$Python)+$runnerArgs
# Start-Process joins ArgumentList. Quote each argument and normalize paths
# beforehand so a leading/nonterminal space stays part of its argument.
$quotedArgs=@($argv | ForEach-Object {'"' + $_.TrimEnd('\') + '"'})
$proc=Start-Process -FilePath $Python -ArgumentList $quotedArgs -WorkingDirectory $ProjectRoot -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
# Nonzero exit from OS job wrapper is HOLD, never a model-science FAIL.
# Independent resource enforcement module: samples parent+descendant RSS,
# total stdout+stderr+recursively saved output, including after normal exit.
# If a child remains after parent exit the complete run is HOLD and killed.
$observation=Invoke-TTMDiagProcessWatch -Process $proc -StdOutPath $logOut -StdErrPath $logErr `
    -OutputDir $OutputDir -WallSeconds 900 -MaxTreeRssBytes 12884901888 `
    -MaxTotalOutputBytes 1073741824 -PollMilliseconds 250
Write-Output ('PASS_ONESHOT_EXIT_ZERO sampled_tree_peak_RSS_bytes='+$observation.PeakTreeRssBytesSampled+' final_output_bytes='+$observation.FinalTotalOutputBytes)
