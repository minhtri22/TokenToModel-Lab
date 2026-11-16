# TTM-SM4M-DIAG-Q001: native SOURCE-ONLY QA on managed Windows task.
# Absolutely no checkpoint, private token inventory, real fixture or model run.
# Must be run from exact candidate checkout and commit SHA readback on GitHub.
param(
  [string]$ProjectRoot='D:\WORK\RESEARCH\TokenToModel-Lab',
  [Parameter(Mandatory=$true)][string]$ExpectedRunnerSHA256,
  [Parameter(Mandatory=$true)][string]$ExpectedLauncherSHA256,
  [Parameter(Mandatory=$true)][string]$ExpectedWatchdogSHA256,
  [Parameter(Mandatory=$true)][string]$ExpectedNegativeQaSHA256,
  [Parameter(Mandatory=$true)][string]$ExpectedNativeWatchQaSHA256
)
$ErrorActionPreference='Stop'
$Error.Clear()
$files=[ordered]@{
  runner=(Join-Path $PSScriptRoot 'ttm_sm4m_diag_q001.py')
  launcher=(Join-Path $PSScriptRoot 'Run-Approved-OneShot-PS51.ps1')
  watchdog=(Join-Path $PSScriptRoot 'Watch-TTM-SM4M-ProcessTree-PS51.ps1')
  negative=(Join-Path $PSScriptRoot 'independent_negative_qa_v3.py')
  native_watch=(Join-Path $PSScriptRoot 'Invoke-DIAG-Q001-Watchdog-NativeNegativeQA-PS51.ps1')
}
$expected=[ordered]@{
  runner=$ExpectedRunnerSHA256
  launcher=$ExpectedLauncherSHA256
  watchdog=$ExpectedWatchdogSHA256
  negative=$ExpectedNegativeQaSHA256
  native_watch=$ExpectedNativeWatchQaSHA256
}
$receipt=[ordered]@{
  schema='ttm.sm4m.diag.q001.native.source_only_onepack.v1'
  operation='TTM_SM4M_DIAG_Q001_V3_LAUNCHER_BLOCKER_REMEDIATION_MANAGED_NATIVE_NEGATIVE_QA_AND_RIGHTS_CUSTODY_ONEPACK'
  model_executed=$false
  checkpoint_read=$false
  private_tokenizer_read=$false
  real_fixture_created=$false
  owner_conditional_go='PRESERVED'
  independent_reviewer_signoff='NOT_INCLUDED_IN_NATIVE_AUTHOR_QA'
  rights='NOT_VERIFIED'
  status='HOLD_NOT_EXECUTED'
  tests=[ordered]@{}
  error=$null
}
$project=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')+'\'
$qaDir=Join-Path $project ('_tmp\ttm_sm4m_diag_q001_managed_native_qa_'+$PID)
New-Item -ItemType Directory -Path $qaDir -ErrorAction Stop | Out-Null
$receiptPath=Join-Path $qaDir 'I1_NATIVE_SOURCE_QA_RECEIPT.json'
try {
  if ($PSVersionTable.PSVersion.Major -ne 5) {throw 'HOLD_NATIVE_PS51_REQUIRED'}
  $receipt.tests.PS51=$true
  if (-not ([IO.Path]::GetFullPath($PSScriptRoot).StartsWith($project,[StringComparison]::OrdinalIgnoreCase))) {
    throw 'HOLD_CANDIDATE_OUTSIDE_PROJECT_ROOT'
  }
  $receipt.tests.CANDIDATE_INSIDE_PROJECT=$true
  $python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
  if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {throw 'HOLD_PY312_EXE_MISSING'}
  & $python -c 'import sys; assert sys.version_info[:2] == (3,12)'
  if ($LASTEXITCODE -ne 0) {throw 'HOLD_PYTHON_3_12_REQUIRED'}
  $receipt.tests.PYTHON_312=$true

  foreach($name in $files.Keys) {
    $file=$files[$name]
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
      throw ('HOLD_SOURCE_MISSING_'+$name)
    }
    if ($expected[$name] -cnotmatch '^[0-9a-f]{64}$') {
      throw ('HOLD_BAD_EXPECTED_SHA_'+$name)
    }
    $actual=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -cne $expected[$name]) {
      throw ('HOLD_SOURCE_SHA_MISMATCH_'+$name)
    }
    $receipt.tests['SHA_'+$name]=$true
  }

  $psPaths=@($files.launcher,$files.watchdog,$files.native_watch,
    (Join-Path $PSScriptRoot 'Run-SourceQA-PS51.ps1'),$MyInvocation.MyCommand.Path)
  foreach($psFile in $psPaths) {
    $tokens=$null
    $errors=$null
    $ast=[System.Management.Automation.Language.Parser]::ParseFile(
      $psFile,[ref]$tokens,[ref]$errors)
    if ($null -eq $ast -or @($errors).Count -ne 0) {
      $details=(@($errors) | ForEach-Object {$_.Message}) -join ';'
      throw ('HOLD_PS_PARSE_'+[IO.Path]::GetFileName($psFile)+':'+$details)
    }
    $receipt.tests['PARSE_'+[IO.Path]::GetFileName($psFile)]=$true
  }

  $launcherText=[IO.File]::ReadAllText($files.launcher)
  $needles=@(
    "if (\$ExpectedRunnerSHA256 -cnotmatch '^[0-9a-f]{64}\$')",
    "if (\$ExpectedWatchdogSHA256 -cnotmatch '^[0-9a-f]{64}\$')",
    "Get-FileHash -LiteralPath \$WatchdogModule -Algorithm SHA256",
    "if (\$ActualWatchdogSHA256 -cne \$ExpectedWatchdogSHA256)",
    '. $WatchdogModule',
    'Get-Command Invoke-TTMDiagProcessWatch',
    '$proc=Start-Process'
  )
  $pos=-1
  foreach($needle in $needles) {
    $i=$launcherText.IndexOf($needle,[StringComparison]::Ordinal)
    if ($i -le $pos) {throw ('HOLD_LAUNCHER_BINDING_ORDER_'+$needle)}
    $pos=$i
  }
  $receipt.tests.WATCHDOG_PIN_LOAD_BEFORE_SPAWN=$true

  # No user private inputs or real model are passed to either test program.
  $probe=(& $python $files.runner source-qa | Out-String)
  if ($LASTEXITCODE -ne 0) {throw 'HOLD_PY_SOURCE_QA'}
  $mock=$probe | ConvertFrom-Json
  if ($mock.passed -ne $mock.total -or $mock.model_run) {throw 'HOLD_PY_SOURCE_QA_RECEIPT'}
  $receipt.tests.PY_MOCK_ORACLE=$true
  $receipt.mock_oracle_count=($mock.passed.ToString()+'/'+$mock.total.ToString())

  $negativeOutput=(& $python $files.negative | Out-String)
  if ($LASTEXITCODE -ne 0) {throw 'HOLD_PY_V3_NEGATIVE_QA'}
  $negative=$negativeOutput | ConvertFrom-Json
  if ($negative.passed -ne $negative.total -or $negative.model_execution) {
    throw 'HOLD_PY_V3_NEGATIVE_QA_RECEIPT'
  }
  $receipt.tests.PY_V3_MOCK_NEGATIVE=$true
  $receipt.v3_negative_count=($negative.passed.ToString()+'/'+$negative.total.ToString())

  $watchOut=(& powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass
    -File $files.native_watch -ProjectRoot $ProjectRoot
    -ExpectedWatchdogSHA256 $ExpectedWatchdogSHA256 | Out-String)
  if ($LASTEXITCODE -ne 0 -or $watchOut -notmatch 'NATIVE_WATCHDOG_NEGATIVE_QA=5/5') {
    throw ('HOLD_NATIVE_ADVERSARIAL_WATCHDOG:'+($watchOut.Trim()))
  }
  $receipt.tests.PS51_LIVE_WATCHDOG_NEGATIVE_5_5=$true
  $receipt.watchdog_report=$watchOut.Trim()
  $receipt.status='PASS_NATIVE_SOURCE_ONLY_NOT_I1'
} catch {
  $receipt.status='HOLD_NATIVE_SOURCE_QA'
  $receipt.error=$_.Exception.Message
} finally {
  $receipt.ts_utc=[DateTime]::UtcNow.ToString('o')
  $receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
  Write-Output ('I1_NATIVE_SOURCE_QA='+$receipt.status+'; RECEIPT='+$receiptPath)
  if ($null -ne $receipt.error) {Write-Output ('FIRST_FAIL='+$receipt.error)}
}
if ($receipt.status -ne 'PASS_NATIVE_SOURCE_ONLY_NOT_I1') {exit 2}
