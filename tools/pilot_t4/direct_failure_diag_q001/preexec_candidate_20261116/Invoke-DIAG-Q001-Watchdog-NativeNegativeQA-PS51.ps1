# Only adversarial Windows PowerShell 5.1 / Python 3.12 SOURCE-ONLY tests.
# Never imports model, opens checkpoint, freezes real fixture or grants rights.
param(
  [string]$ProjectRoot='D:\WORK\RESEARCH\TokenToModel-Lab',
  [Parameter(Mandatory=$true)][string]$ExpectedWatchdogSHA256
)
$ErrorActionPreference='Stop'
if ($PSVersionTable.PSVersion.Major -ne 5) {throw 'HOLD_EXPECTED_WINDOWS_PS51'}
$python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {throw 'HOLD_PY312_MISSING'}
& $python -c 'import sys; assert sys.version_info[:2]==(3,12)'
if ($LASTEXITCODE -ne 0) {throw 'HOLD_PY312_WRONG_VERSION'}
$source=Join-Path $PSScriptRoot 'Watch-TTM-SM4M-ProcessTree-PS51.ps1'
if ($ExpectedWatchdogSHA256 -cnotmatch '^[0-9a-f]{64}$') {throw 'HOLD_WATCH_SOURCE_SHA_FORMAT'}
if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedWatchdogSHA256) {throw 'HOLD_WATCH_SOURCE_SHA_MISMATCH'}
. $source
$root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')+'\'
if (-not [IO.Path]::GetFullPath($PSScriptRoot).StartsWith($root,[StringComparison]::OrdinalIgnoreCase)) {throw 'HOLD_QA_SOURCE_OUTSIDE_PROJECT'}
$qa=Join-Path $ProjectRoot ('_tmp\ttm_sm4m_diag_q001_native_watchdog_qa_'+$PID)
New-Item -ItemType Directory -Path $qa -ErrorAction Stop | Out-Null
$fixture=Join-Path $qa 'synthetic_process_only.py'
@'
import os,subprocess,sys,time
mode=sys.argv[1]
if mode=="normal": print("OK",flush=True)
elif mode=="exit_big":
 sys.stdout.buffer.write(b"X"*65536); sys.stdout.buffer.flush()
elif mode=="stall": time.sleep(8)
elif mode=="child":
 data=bytearray(90*1024*1024)
 with open(sys.argv[2],"w") as f: f.write(str(os.getpid()))
 time.sleep(8)
elif mode in ("parent_child","parent_exit_child"):
 child=subprocess.Popen([sys.executable,__file__,"child",sys.argv[2]])
 time.sleep(.8 if mode=="parent_exit_child" else 8)
else: sys.exit(13)
'@ | Set-Content -LiteralPath $fixture -Encoding ASCII
$checks=[ordered]@{}
function Test-MockCase([string]$mode,[string]$expect,[int]$seconds,[Int64]$rss,[Int64]$size) {
  $out=Join-Path $qa ($mode+'.stdout.txt');$err=Join-Path $qa ($mode+'.stderr.txt')
  $folder=Join-Path $qa ('artifacts_'+$mode)
  New-Item -ItemType Directory -Path $folder | Out-Null
  $childfile=Join-Path $qa ($mode+'.child.pid')
  $args=@('-u',$fixture,$mode,$childfile)
  $p=Start-Process -FilePath $python -ArgumentList $args -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
  try {
    $s=Invoke-TTMDiagProcessWatch -Process $p -StdOutPath $out -StdErrPath $err -OutputDir $folder -WallSeconds $seconds -MaxTreeRssBytes $rss -MaxTotalOutputBytes $size -PollMilliseconds 100
    return ($expect -eq 'PASS' -and $s.ExitCode -eq 0)
  } catch {
    return ($_.Exception.Message -like ($expect+'*'))
  } finally {
    $p.Refresh()
    if (-not $p.HasExited) { & taskkill.exe /PID $p.Id /T /F 2>$null | Out-Null }
    if (Test-Path -LiteralPath $childfile -PathType Leaf) {
      $cpid=[int](Get-Content -LiteralPath $childfile -Raw)
      $still=Get-Process -Id $cpid -ErrorAction SilentlyContinue
      if ($still) {try{$still.Kill()}catch{}}
    }
  }
}
$checks['normal_exit_pass']=Test-MockCase 'normal' 'PASS' 8 1073741824 1073741824
$checks['postexit_total_output_rejected']=Test-MockCase 'exit_big' 'HOLD_WATCHDOG_TOTAL_LOG_AND_OUTPUT_BYTES' 8 1073741824 4096
$checks['wall_time_kill']=Test-MockCase 'stall' 'HOLD_WATCHDOG_WALL_TIME' 1 1073741824 1073741824
$checks['child_memory_in_aggregate']=Test-MockCase 'parent_child' 'HOLD_WATCHDOG_AGGREGATE_PROCESS_TREE_RSS' 8 50331648 1073741824
$checks['orphan_child_after_parent_exit']=Test-MockCase 'parent_exit_child' 'HOLD_WATCHDOG_ORPHAN_DESCENDANT_AFTER_PARENT_EXIT' 8 1073741824 1073741824
$pass=(@($checks.Values | Where-Object {$_ -eq $true})).Count
$receipt=[ordered]@{schema='ttm.sm4m.diag.q001.native_watchdog_negative_qa.v1';scope='WINDOWS_POWERSHELL_5_1_PYTHON_3_12_SOURCE_ONLY';checks=$checks;pass=$pass;total=$checks.Count;model_execution=$false;checkpoint_read=$false;rights_verified=$false}
$record=Join-Path $qa 'NATIVE_WATCHDOG_QA_RECEIPT.json'
$receipt|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $record -Encoding UTF8
Write-Output ('NATIVE_WATCHDOG_NEGATIVE_QA='+$pass+'/'+$checks.Count+' RECEIPT='+$record)
if ($pass -ne $checks.Count) {throw 'HOLD_NATIVE_WATCHDOG_NEGATIVE_QA'}
