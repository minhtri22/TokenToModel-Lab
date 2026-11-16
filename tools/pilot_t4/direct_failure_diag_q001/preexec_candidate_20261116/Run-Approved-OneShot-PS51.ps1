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
  [string]$RunnerPath=''
)
$ErrorActionPreference='Stop'
$Python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not $RunnerPath) {$RunnerPath=Join-Path $PSScriptRoot 'ttm_sm4m_diag_q001.py'}
if ($ExpectedRunnerSHA256 -cnotmatch '^[0-9a-f]{64}$') {throw 'HOLD_RUNNER_PIN_FORMAT'}
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
$watch=[Diagnostics.Stopwatch]::StartNew()
$peakRss=0L
try {
  while (-not $proc.WaitForExit(1000)) {
    if ($watch.Elapsed.TotalSeconds -ge 900) {throw 'HOLD_WALL_900_SECONDS'}
    $native=Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if ($native) {$peakRss=[Math]::Max($peakRss,[Int64]$native.WorkingSet64)}
    if ($peakRss -gt 12GB) {throw 'HOLD_EXTERNAL_RSS_12GIB'}
    $size=0L
    foreach($f in @($logOut,$logErr)) {if (Test-Path -LiteralPath $f) {$size+=(Get-Item -LiteralPath $f).Length}}
    if ($size -ge 1GB) {throw 'HOLD_LOG_OUTPUT_1GIB'}
    if (Test-Path -LiteralPath $OutputDir) {
      $files=Get-ChildItem -LiteralPath $OutputDir -Recurse -File -ErrorAction SilentlyContinue
      if ($files) {$size+=($files | Measure-Object -Property Length -Sum).Sum}
      if ($size -ge 1GB) {throw 'HOLD_TOTAL_OUTPUT_1GIB'}
    }
  }
  if ($proc.ExitCode -ne 0) {throw ('HOLD_RUN_EXIT_'+$proc.ExitCode)}
  Write-Output ('PASS_ONESHOT_EXIT_ZERO peak_RSS_bytes_sampled='+$peakRss)
} finally {
  if (-not $proc.HasExited) {
    & taskkill.exe /PID $proc.Id /T /F 2>$null | Out-Null
  }
}
