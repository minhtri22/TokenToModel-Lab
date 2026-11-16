# TTM-SM4M-DIAG-Q001: future single-run guarded launcher ONLY AFTER external
# distinct review, rights/custody, owner Q4, and frozen I1 fixture are verified.
# Do not invoke this script merely because it was supplied in chat.
param(
  [string]$ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab',
  [Parameter(Mandatory=$true)][string]$PermitPath,
  [Parameter(Mandatory=$true)][string]$CheckpointPath,
  [Parameter(Mandatory=$true)][string]$TokenInventoryPath,
  [Parameter(Mandatory=$true)][string]$OutputDir,
  [Parameter(Mandatory=$true)][string]$ExpectedRunnerSHA256,
  [string]$RunnerPath = ''
)
$ErrorActionPreference = 'Stop'
$Python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not $RunnerPath) { $RunnerPath = Join-Path $ProjectRoot '_tmp\ttm_sm4m_diag_q001_candidate\ttm_sm4m_diag_q001.py' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'HOLD_PYTHON312_MISSING' }
$root = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\') + '\'
foreach($p in @($PermitPath,$CheckpointPath,$TokenInventoryPath,$OutputDir,$RunnerPath)) {
  if (-not ([IO.Path]::GetFullPath($p)).StartsWith($root,[StringComparison]::OrdinalIgnoreCase)) {
    throw 'HOLD_PATH_OUTSIDE_PROJECT_ROOT'
  }
}
if (-not (Test-Path -LiteralPath $RunnerPath -PathType Leaf)) { throw 'HOLD_RUNNER_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $PermitPath -PathType Leaf)) { throw 'HOLD_PERMIT_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $TokenInventoryPath -PathType Leaf)) { throw 'HOLD_TOKENIZER_INVENTORY_NOT_FOUND' }
if (Test-Path -LiteralPath $OutputDir) { throw 'HOLD_OUTPUT_NOT_FRESH' }
if ($ExpectedRunnerSHA256 -notmatch '^[0-9a-fA-F]{64}$') { throw 'HOLD_RUNNER_SHA_SYNTAX' }
$sha = (Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sha -ne $ExpectedRunnerSHA256.ToLowerInvariant()) { throw 'HOLD_RUNNER_SHA_MISMATCH' }
# Check owner/independent/rights declaration before touching checkpoint *metadata*.
$p = Get-Content -LiteralPath $PermitPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($p.owner_decision -ne 'GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL' -or
    $p.distinct_q2_q3_review -ne 'PASS_DIAG_Q001_SINGLE_PREEXEC_SOURCE_SCOPED' -or
    $p.q4_owner_scoped_implementation -ne 'GO_SCOPED_IMPLEMENT' -or
    $p.owner_model_execution_permit -ne 'GO_SINGLE_ONE_SHOT_CPU' -or
    $p.ad00_ad01c_e6_rights -ne 'VERIFIED_SCOPED' -or
    $p.checkpoint_byte_custody -ne 'VERIFIED_EXACT_SHA256' -or
    $p.runner_independent_negative_qa -ne 'PASS') { throw 'HOLD_PREEXEC_OWNER_RIGHTS_REVIEW' }
if (-not (Test-Path -LiteralPath $CheckpointPath -PathType Leaf)) { throw 'HOLD_PRIVATE_CHECKPOINT_MISSING' }
& $Python -c 'import sys; assert sys.version_info[:2] == (3,12), sys.version'
if ($LASTEXITCODE -ne 0) { throw 'HOLD_PYTHON_VERSION' }
# stdout/stderr stay in project root. Actual diagnostic output is created by Python
# only after verifying ALL source/weight/fixture evidence.
$logRoot = Join-Path $ProjectRoot '_tmp\ttm_sm4m_diag_q001_one_shot_logs'
if (-not (Test-Path -LiteralPath $logRoot)) { New-Item -ItemType Directory -Path $logRoot -Force | Out-Null }
$logOut = Join-Path $logRoot 'RUN_stdout.txt'
$logErr = Join-Path $logRoot 'RUN_stderr.txt'
if ((Test-Path $logOut) -or (Test-Path $logErr)) { throw 'HOLD_ONE_SHOT_LOGS_ALREADY_EXIST' }
$args = @($RunnerPath,'run','--root',$ProjectRoot,'--permit',$PermitPath,
          '--checkpoint',$CheckpointPath,'--token-inventory',$TokenInventoryPath,'--out',$OutputDir)
$proc = Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $ProjectRoot `
    -PassThru -RedirectStandardOutput $logOut -RedirectStandardError $logErr
if (-not $proc.WaitForExit(900000)) {
  & taskkill.exe /PID $proc.Id /T /F | Out-Null
  throw 'HOLD_900_SECOND_WALL_STOP_ONE_SHOT_NO_RETRY'
}
if ($proc.ExitCode -ne 0) {
  throw ('HOLD_RUN_EXIT_CODE_' + $proc.ExitCode + ' see ' + $logErr)
}
Write-Output ('ONE_SHOT_TERMINATED_EXIT_ZERO; STDOUT=' + $logOut)
Write-Output ('RECEIPT=' + (Join-Path $OutputDir 'RUN_RECEIPT.json'))
