#requires -Version 5.1
# TTM P01 L1: clean V3 successor from parse-passed V1, exact 64-hex marker hash readback.
# -ReadOnly is default. -TerminateExactTTMProcess is explicit authorization.
# No generic kill by PID. No SCM reconfiguration or repeat science.
[CmdletBinding()]
param([switch]$TerminateExactTTMProcess)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$bin=Join-Path $stage 'broker_service'
$exe=Join-Path $bin 'TTMP01Broker.attestationV2.exe'
$exeSha='a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a'
$expectedHead='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$svc='TTMP01Broker'
$expectedPID=26200
$expectedCreatedMs=[int64]1793982282113
$markers=@(
 @{name='SCM_SWITCH';path=(Join-Path $stage 'L1_SCM_V2_SWITCH_ATTEMPT_20261106.lock');sha='29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1'},
 @{name='NATIVE_TEST';path=(Join-Path $stage 'L1_BROKER_V2_WORKER_V3_NATIVE_SECURITY_ATTEMPT_20261106.lock');sha='f0d895e68c30b8c3845336ea8aee40d2e1ca84f96816906a952ae70ad81587c7'},
 @{name='SCM_STOP_RECOVERY';path=(Join-Path $stage 'L1_BROKER_V2_SCM_STOP_RECOVERY_ATTEMPT_20261106.lock');sha='f1ca3d0899fe6637a512e44dd073b449d4805ca8f8a8afa1e8a3989599143502'}
)
$forceMarker=Join-Path $stage 'L1_BROKER_V2_EXACT_PROCESS_TERMINATE_ATTEMPT_20261106.lock'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$id='L1_BROKER_V2_EXACT_PROCESS_RECOVERY_V3_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $root ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$r=[ordered]@{
 schema='ttm.p01.l1.exact_process_recovery_after_scm_1061.v3'
 run_id=$id
 original_HEAD=$expectedHead
 source_failure_commit='8a3666c655edba86bef2a841a31246fe19e0e870'
  marker_integrity_receipt_commit='8f8dfde1fda2a8907a1bae04f6459f486f0f68ec'
  malformed_predecessor_receipt_commit='441bec040d9d186bc2088d0747efe04d71a62f74'
 mode=$(if($TerminateExactTTMProcess){'EXPLICIT_TERMINATE_EXACT_PROCESS_ONCE'}else{'READONLY_PREFLIGHT'})
 checks=[ordered]@{}
 before=[ordered]@{}
 after=[ordered]@{}
 process_identity=[ordered]@{}
 recovery_marker_sha256=$null
 native_handle_result='NOT_EXECUTED'
 termination_attempted=$false
 forced_termination=$false
 SCM_configuration_changed=$false
 worker_or_ACL_changed=$false
 prior_markers_changed=$false
 errors=@()
 verdict='BLOCK'
 W01_W12='NOT_EXECUTED'
 L1_grouped_QA='NOT_AUTHORIZED'
}
function Gate([string]$name,[string]$status,[string]$detail){
 $r.checks[$name]=[ordered]@{status=$status;detail=$detail}
 Write-Host ('TTM_FORCE_'+$name+'='+$status)
}
function Halt([string]$reason){throw [InvalidOperationException]::new($reason)}
function Sha([string]$p){return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function ReadGit([string[]]$GitArguments){
 $lines=@(& git.exe -C $wt @GitArguments 2>&1)
 if($LASTEXITCODE -ne 0){Halt 'GIT_IDENTITY_FAILED'}
 return (($lines -join [Environment]::NewLine).Trim())
}
function NoReparse([string]$path){
 $p=$path
 while($p -and (Test-Path -LiteralPath $p)){
  $item=Get-Item -LiteralPath $p -Force -ErrorAction Stop
  if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Halt 'TTM_REPARSE_PATH_REFUSED'}
  $parent=Split-Path -Parent $p
  if($p -eq $parent){break}
  $p=$parent
 }
}
function GetSCM{
 $result=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $result){Halt 'SCM_SERVICE_MISSING'}
 return $result
}
function RecordSCM([string]$key,$state){
 $r[$key]=[ordered]@{
  state=$state.State;service_name=$state.Name;process_id=[int]$state.ProcessId
  start_mode=$state.StartMode;service_account=$state.StartName
  image_path=$state.PathName;win32_exit=$state.ExitCode
 }
}
try {
 $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin){Halt 'ADMIN_REQUIRED'}
 Gate 'ADMIN' 'PASS' 'Elevated Windows administrator'
 # Snapshot SCM before touching protected project paths.
 $current=GetSCM
 RecordSCM 'before' $current
 Gate 'SCM_SNAPSHOT' 'PASS_READONLY' ('State='+$current.State+';PID='+$current.ProcessId)
 foreach($path in @($wt,$stage,$bin,$exe,$forceMarker,$receiptDir)){NoReparse $path}
 foreach($entry in $markers){NoReparse $entry.path}
 if((ReadGit -GitArguments @('rev-parse','HEAD')) -cne $expectedHead){Halt 'ORIGINAL_HEAD_CHANGED'}
 if((ReadGit -GitArguments @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Halt 'ORIGINAL_BRANCH_CHANGED'}
 if((ReadGit -GitArguments @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Halt 'ORIGINAL_ORIGIN_CHANGED'}
 Gate 'ORIGINAL_WORKTREE' 'PASS' 'Pinned worktree read-only'
 if((Sha $exe) -cne $exeSha){Halt 'BROKER_V2_BINARY_SHA256_MISMATCH'}
 Gate 'EXACT_EXE' 'PASS' $exeSha
 foreach($entry in $markers){
  if($entry.sha.Length -ne 64 -or $entry.sha -notmatch '^[0-9a-f]{64}$'){Halt ('INVALID_MARKER_PIN_FORMAT_'+$entry.name)}
  if(-not(Test-Path -LiteralPath $entry.path -PathType Leaf)){Halt ('MISSING_PRIOR_MARKER_'+$entry.name)}
  if((Sha $entry.path) -cne $entry.sha){Halt ('PRIOR_MARKER_SHA256_CHANGED_'+$entry.name)}
  Gate ('MARKER_'+$entry.name) 'PASS_EXACT' $entry.sha
 }
 if($current.StartMode -ne 'Manual' -or $current.StartName -ine 'NT AUTHORITY\LocalService' -or
    $current.PathName.Trim().Trim([char]34).Trim() -ine $exe){Halt 'SCM_SERVICE_CONFIGURATION_UNEXPECTED'}
 Gate 'SCM_CONFIG' 'PASS' 'Dedicated Manual LocalService V2 executable'
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Halt 'GITHUB_CLI_MISSING'}
 & gh auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Halt 'GITHUB_AUTH_FAILED'}
 Gate 'GITHUB_AUTH' 'PASS' 'Evidence publication available before possible termination'
 if($current.State -eq 'Stopped' -and [int]$current.ProcessId -eq 0){
  Gate 'SERVICE' 'PASS_ALREADY_STOPPED' 'No process termination needed'
  $r.verdict='PASS_SERVICE_ALREADY_STOPPED_NO_FORCE'
 } else {
  if($current.State -ne 'Running' -or [int]$current.ProcessId -ne $expectedPID){Halt 'SERVICE_NOT_EXACT_RUNNING_INCIDENT'}
  $proc=Get-CimInstance Win32_Process -Filter ('ProcessId='+$expectedPID) -ErrorAction Stop
  if($null -eq $proc -or $proc.ExecutablePath -ine $exe){Halt 'PROCESS_IMAGE_IDENTITY_MISMATCH'}
  $createdUtc=([datetime]$proc.CreationDate).ToUniversalTime()
  $createdMs=[DateTimeOffset]::new($createdUtc).ToUnixTimeMilliseconds()
  if([Math]::Abs($createdMs-$expectedCreatedMs) -gt 1000){Halt 'PROCESS_REPLACED_CREATION_MISMATCH'}
  $r.process_identity=[ordered]@{
   pid=$expectedPID;creation_unix_ms=$createdMs;image_path=$proc.ExecutablePath
  }
  Gate 'EXACT_PROCESS' 'PASS' 'SCM PID, V2 image and process creation time all pinned'
  # Win32 must prove recovery marker absent. Test-Path false is not sufficient.
  Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TtmP01ExactKillMarker {
 [DllImport("kernel32.dll",EntryPoint="GetFileAttributesW",CharSet=CharSet.Unicode,ExactSpelling=true,SetLastError=true)]
 public static extern UInt32 Query(string path);
}
'@ -ErrorAction Stop
  $attr=[TtmP01ExactKillMarker]::Query($forceMarker)
  if($attr -ne [uint32]::MaxValue){Halt 'EXACT_TERMINATION_ALREADY_ATTEMPTED_NO_REPLAY'}
  $lastError=[Runtime.InteropServices.Marshal]::GetLastWin32Error()
  if($lastError -ne 2){Halt ('TERMINATION_MARKER_ABSENCE_NOT_PROVEN_'+$lastError)}
  Gate 'TERMINATION_MARKER_ABSENCE' 'PASS_WIN32_2' 'One-shot force recovery marker not present'
  # Native helper binds the exact kernel process HANDLE to creation time and
  # image path immediately before termination; this prevents PID reuse harm.
  Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class TtmP01ExactProcessHandle {
 [StructLayout(LayoutKind.Sequential)]
 struct FILETIME {public uint low;public uint high;}
 [DllImport("kernel32.dll",SetLastError=true)]
 static extern IntPtr OpenProcess(uint rights,bool inherit,uint pid);
 [DllImport("kernel32.dll",SetLastError=true)]
 static extern bool CloseHandle(IntPtr handle);
 [DllImport("kernel32.dll",SetLastError=true)]
 static extern bool GetProcessTimes(IntPtr handle,out FILETIME created,out FILETIME exited,out FILETIME kernel,out FILETIME user);
 [DllImport("kernel32.dll",EntryPoint="QueryFullProcessImageNameW",CharSet=CharSet.Unicode,ExactSpelling=true,SetLastError=true)]
 static extern bool GetImage(IntPtr handle,uint flags,StringBuilder text,ref uint size);
 [DllImport("kernel32.dll",SetLastError=true)]
 static extern bool GetExitCodeProcess(IntPtr handle,out uint code);
 [DllImport("kernel32.dll",SetLastError=true)]
 static extern bool TerminateProcess(IntPtr handle,uint exitCode);
 [DllImport("kernel32.dll",SetLastError=true)]
 static extern uint WaitForSingleObject(IntPtr handle,uint millis);
 public static string Invoke(uint pid,long expectedCreated,string expectedImage,bool actuallyTerminate){
  // PROCESS_TERMINATE(1), QUERY_LIMITED_INFORMATION(0x1000), SYNCHRONIZE(0x100000)
  IntPtr handle=OpenProcess(0x101001u,false,pid);
  if(handle==IntPtr.Zero)return "BLOCK_OPEN_PROCESS_"+Marshal.GetLastWin32Error();
  try{
   FILETIME c,e,k,u;
   if(!GetProcessTimes(handle,out c,out e,out k,out u))
    return "BLOCK_QUERY_CREATION_"+Marshal.GetLastWin32Error();
   long time=((long)c.high<<32)|(long)c.low;
   long created=new DateTimeOffset(DateTime.FromFileTimeUtc(time)).ToUnixTimeMilliseconds();
   if(Math.Abs(created-expectedCreated)>1000)
    return "BLOCK_KERNEL_HANDLE_CREATION_MISMATCH";
   var image=new StringBuilder(32768);
   uint length=(uint)image.Capacity;
   if(!GetImage(handle,0,image,ref length))
    return "BLOCK_QUERY_IMAGE_"+Marshal.GetLastWin32Error();
   if(!string.Equals(image.ToString(),expectedImage,StringComparison.OrdinalIgnoreCase))
    return "BLOCK_KERNEL_HANDLE_IMAGE_MISMATCH";
   uint exitCode;
   if(!GetExitCodeProcess(handle,out exitCode))
    return "BLOCK_QUERY_RUNNING_"+Marshal.GetLastWin32Error();
   if(exitCode!=259u)return "BLOCK_KERNEL_HANDLE_ALREADY_EXITED";
   if(!actuallyTerminate)return "PASS_KERNEL_HANDLE_EXACT_NO_TERMINATE";
   if(!TerminateProcess(handle,1u))
    return "BLOCK_TERMINATE_PROCESS_"+Marshal.GetLastWin32Error();
   uint wait=WaitForSingleObject(handle,10000u);
   if(wait==0u)return "PASS_EXACT_HANDLE_EXIT_CONFIRMED";
   if(wait==258u)return "BLOCK_PROCESS_EXIT_WAIT_TIMEOUT";
   return "BLOCK_PROCESS_EXIT_WAIT_"+wait;
  }finally{CloseHandle(handle);}
 }
}
'@ -ErrorAction Stop
  # Safe no-mutation handle preflight before marking any attempt.
  $handlePreflight=[TtmP01ExactProcessHandle]::Invoke([uint32]$expectedPID,$expectedCreatedMs,$exe,$false)
  if($handlePreflight -cne 'PASS_KERNEL_HANDLE_EXACT_NO_TERMINATE'){Halt $handlePreflight}
  Gate 'KERNEL_PROCESS_HANDLE' 'PASS_EXACT_NO_TERMINATE' 'Kernel handle creation time, binary image and live exit code checked'
  if(-not $TerminateExactTTMProcess){
   Gate 'PROCESS_ACTION' 'NOT_EXECUTED' 'Read-only mode; exact termination requires explicit switch'
   $r.verdict='PREFLIGHT_PASS_TERMINATION_NOT_EXECUTED'
  }else{
   # Refresh SCM before one-shot marker. This also guards against a newly-owned
   # process or changed SCM configuration between the two preflight snapshots.
   $again=GetSCM
   if($again.State -ne 'Running' -or [int]$again.ProcessId -ne $expectedPID -or
      $again.StartName -ine 'NT AUTHORITY\LocalService' -or
      $again.PathName.Trim().Trim([char]34).Trim() -ine $exe){Halt 'SCM_CHANGED_BEFORE_PROCESS_ACTION'}
   Gate 'SCM_RECHECK' 'PASS' 'SCM still maps exact service and PID immediately before action'
   $bytes=[Text.Encoding]::UTF8.GetBytes(('run_id='+$id+[Environment]::NewLine+
    'expected_pid='+$expectedPID+[Environment]::NewLine+
    'expected_created_unix_ms='+$expectedCreatedMs+[Environment]::NewLine+
    'exe_sha256='+$exeSha+[Environment]::NewLine))
   $fs=[IO.File]::Open($forceMarker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
   try{$fs.Write($bytes,0,$bytes.Length);$fs.Flush()}
   finally{$fs.Dispose()}
   $r.recovery_marker_sha256=Sha $forceMarker
   Gate 'ONE_SHOT_MARKER' 'PASS_CREATED' 'New TTM-only marker; never automatically removed'
   $r.termination_attempted=$true
   $native=[TtmP01ExactProcessHandle]::Invoke([uint32]$expectedPID,$expectedCreatedMs,$exe,$true)
   $r.native_handle_result=$native
   if($native -ceq 'PASS_EXACT_HANDLE_EXIT_CONFIRMED'){
    $r.forced_termination=$true
    Gate 'EXACT_TERMINATION' 'PASS_PROCESS_HANDLE_EXITED' 'Only exact matched V2 service process handle terminated'
   }else{Gate 'EXACT_TERMINATION' 'BLOCK' $native}
   # At most 10 seconds SCM status observation; no Stop-Service, SCM control,
   # process termination retry or service start.
   $limit=[DateTime]::UtcNow.AddSeconds(10)
   do{
    $final=GetSCM
    if($final.State -eq 'Stopped' -and [int]$final.ProcessId -eq 0){break}
    Start-Sleep -Milliseconds 500
   }while([DateTime]::UtcNow -lt $limit)
   RecordSCM 'after' $final
   if($native -ceq 'PASS_EXACT_HANDLE_EXIT_CONFIRMED' -and
      $final.State -eq 'Stopped' -and [int]$final.ProcessId -eq 0){
    Gate 'SCM_FINAL_STATE' 'PASS_STOPPED_PID_0' 'Actual SCM state after handle-based termination'
    $r.verdict='PASS_EXACT_TTM_PROCESS_RECOVERED_WITH_FORCED_TERMINATION'
   }else{
    Gate 'SCM_FINAL_STATE' 'BLOCK_UNRESOLVED' ('State='+$final.State+';PID='+$final.ProcessId)
    $r.verdict='BLOCK_EXACT_PROCESS_RECOVERY_NOT_VERIFIED'
   }
  }
 }
}catch{
 $r.errors+= $_.Exception.Message
 $r.verdict='BLOCK_EXACT_PROCESS_RECOVERY_EXCEPTION'
 Write-Host ('TTM_FORCE_BLOCK='+$_.Exception.Message)
}finally{
 try{
  if($r.after.Count -eq 0){
   try{
    $last=GetSCM
    RecordSCM 'after' $last
    Write-Host ('TTM_FORCE_LAST_SCM='+$last.State+';PID='+$last.ProcessId)
   }catch{
    $r.errors+=('FINAL_SCM_SNAPSHOT_FAILED_'+$_.Exception.GetType().Name)
   }
  }
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $r['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($file,($r|ConvertTo-Json -Depth 18),(New-Object Text.UTF8Encoding $false))
  $sha=Sha $file
  Write-Host ('TTM_FORCE_RECEIPT='+$file)
  Write-Host ('TTM_FORCE_SHA256='+$sha)
  $target='artifacts/qa/p01/'+$id+'.json'
  $request=Join-Path $receiptDir 'github_create.json'
  $content=@{branch=$branch;message=('evidence(p01): exact TTM process recovery after SCM 1061 '+$id);
    content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$content,(New-Object Text.UTF8Encoding $false))
  $up=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$target) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_UPLOAD_FAILED'}
  $saved=($up -join [Environment]::NewLine)|ConvertFrom-Json
  $back=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$target+'?ref='+$saved.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_READBACK_FAILED'}
  $read=($back -join [Environment]::NewLine)|ConvertFrom-Json
  $h=[Security.Cryptography.SHA256]::Create()
  try{$got=([BitConverter]::ToString($h.ComputeHash([Convert]::FromBase64String(($read.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally{$h.Dispose()}
  if($got -cne $sha){Halt 'GITHUB_RECEIPT_SHA_MISMATCH'}
  Write-Host ('TTM_FORCE_GITHUB_COMMIT='+$saved.commit.sha)
  Write-Host 'TTM_FORCE_GITHUB_READBACK=PASS'
  $exitCode=if($r.verdict -in @('PASS_SERVICE_ALREADY_STOPPED_NO_FORCE','PASS_EXACT_TTM_PROCESS_RECOVERED_WITH_FORCED_TERMINATION')){0}else{3}
 }catch{
  Write-Host ('TTM_FORCE_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exitCode=5
 }
}
Write-Host 'TTM_W01_W12_NATIVE=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exitCode
