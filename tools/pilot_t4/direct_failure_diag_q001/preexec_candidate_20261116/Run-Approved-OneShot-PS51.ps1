# Guarded I2 CPU launcher; requires three authenticated external signatures.
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
  [string]$RunnerPath=''
)
$ErrorActionPreference='Stop'
$Python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not $RunnerPath) {$RunnerPath=Join-Path $PSScriptRoot 'ttm_sm4m_diag_q001.py'}
if ($ExpectedRunnerSHA256 -cnotmatch '^[0-9a-f]{64}
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {throw 'HOLD_PY312_NOT_FOUND'}
$root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')+'\'
foreach($path in @($RunnerPath,$PermitPath,$CheckpointPath,$TokenInventoryPath,$TokenizerSourcePath,$FixtureDir,$OutputDir)) {
  if (-not [IO.Path]::GetFullPath($path).StartsWith($root,[StringComparison]::OrdinalIgnoreCase)) {throw 'HOLD_OUTSIDE_PROJECT'}
}
if (-not (Test-Path -LiteralPath $RunnerPath -PathType Leaf)) {throw 'HOLD_RUNNER_MISSING'}
if ((Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedRunnerSHA256) {throw 'HOLD_RUNNER_SHA'}
if (Test-Path -LiteralPath $OutputDir) {throw 'HOLD_OUTPUT_NOT_FRESH'}
& $Python -c 'import sys; assert sys.version_info[:2]==(3,12)'
if ($LASTEXITCODE -ne 0) {throw 'HOLD_PYTHON_VERSION'}
# Authenticate signatures and tokenizer rights BEFORE checking private checkpoint.
& $Python $RunnerPath release-preflight --root $ProjectRoot --permit $PermitPath --token-inventory $TokenInventoryPath --tokenizer-source $TokenizerSourcePath --fixture-dir $FixtureDir
if ($LASTEXITCODE -ne 0) {throw 'HOLD_AUTHENTICATED_RELEASE_PREFLIGHT'}
if (-not (Test-Path -LiteralPath $CheckpointPath -PathType Leaf)) {throw 'HOLD_CHECKPOINT_NOT_FOUND'}
if (-not (Test-Path -LiteralPath $FixtureDir -PathType Container)) {throw 'HOLD_FROZEN_FIXTURE_NOT_FOUND'}
$logRoot=Join-Path $ProjectRoot '_tmp\ttm_sm4m_diag_q001_one_shot_logs'
if (-not (Test-Path -LiteralPath $logRoot)) {New-Item -ItemType Directory -Path $logRoot | Out-Null}
$logOut=Join-Path $logRoot 'RUN_stdout.txt'
$logErr=Join-Path $logRoot 'RUN_stderr.txt'
if ((Test-Path -LiteralPath $logOut) -or (Test-Path -LiteralPath $logErr)) {throw 'HOLD_ONESHOT_ALREADY_CONSUMED'}
$argv=@($RunnerPath,'run','--root',$ProjectRoot,'--permit',$PermitPath,'--checkpoint',$CheckpointPath,
        '--token-inventory',$TokenInventoryPath,'--tokenizer-source',$TokenizerSourcePath,
        '--fixture-dir',$FixtureDir,'--out',$OutputDir)
$proc=Start-Process -FilePath $Python -ArgumentList $argv -WorkingDirectory $ProjectRoot -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
# Independent resource enforcement module: samples parent+descendant RSS,
# total stdout+stderr+recursively saved output, including after normal exit.
# If a child remains after parent exit the complete run is HOLD and killed.
$observation=Invoke-TTMDiagProcessWatch -Process $proc -StdOutPath $logOut -StdErrPath $logErr `
    -OutputDir $OutputDir -WallSeconds 900 -MaxTreeRssBytes 12884901888 `
    -MaxTotalOutputBytes 1073741824 -PollMilliseconds 250
Write-Output ('PASS_ONESHOT_EXIT_ZERO sampled_tree_peak_RSS_bytes='+$observation.PeakTreeRssBytesSampled+' final_output_bytes='+$observation.FinalTotalOutputBytes)
