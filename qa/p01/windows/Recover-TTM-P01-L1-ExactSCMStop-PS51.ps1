#requires -Version 5.1
# TTM P01 L1 -- ONE controlled SCM STOP recovery, never force-kill.
# Refuses to affect any non-matching process, service, path or source hash.
[CmdletBinding()]param([switch]$Apply)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$worktree=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$exe=Join-Path $stage 'broker_service\TTMP01Broker.attestationV2.exe'
$serviceName='TTMP01Broker'
$expectedHead='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$expectedExeHash='a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a'
$expectedNativeMarkerHash='f0d895e68c30b8c3845336ea8aee40d2e1ca84f96816906a952ae70ad81587c7'
$expectedSwitchMarkerHash='29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1'
$expectedPid=26200
$expectedCreationUnixMs=[int64]1793982282113
$nativeMarker=Join-Path $stage 'L1_BROKER_V2_WORKER_V3_NATIVE_SECURITY_ATTEMPT_20261106.lock'
$switchMarker=Join-Path $stage 'L1_SCM_V2_SWITCH_ATTEMPT_20261106.lock'
$recoveryMarker=Join-Path $stage 'L1_BROKER_V2_SCM_STOP_RECOVERY_ATTEMPT_20261106.lock'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$id='L1_BROKER_V2_SCM_STOP_RECOVERY_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $root ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$rec=[ordered]@{
 schema='ttm.p01.l1.exact_scm_stop_recovery.v1';run_id=$id;
 original_head=$expectedHead
 incident_commit='45f74877a43a66e6559f2a61d6f765ffd0c7da98'
 live_snapshot_commit='bcbc91328045d691819faaf81fdbb5f085e8ba2f'
 mode=$(if($Apply){'APPLY_ONCE'}else{'READONLY'})
 checks=[ordered]@{};SCM_before=[ordered]@{};SCM_after=[ordered]@{}
 sc_stop_exit=$null;sc_stop_output=@();recovery_marker_sha256=$null
 service_stop_requested=$false;forced_termination=$false;service_started=$false
 account_changed=$false;ACL_changed=$false;SCM_configuration_changed=$false
 verdict='BLOCK';errors=@();W01_W12='NOT_EXECUTED';L1_grouped_QA='NOT_AUTHORIZED'
}
function Gate([string]$name,[string]$status,[string]$detail){
 $rec.checks[$name]=[ordered]@{status=$status;detail=$detail}
 Write-Host ('TTM_RECOVER_'+$name+'='+$status)
}
function Block([string]$why){throw [InvalidOperationException]::new($why)}
function Sha([string]$p){return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function ReadGit([string[]]$GitArguments){
 $out=@(& git.exe -C $worktree @GitArguments 2>&1)
 if($LASTEXITCODE -ne 0){Block 'ORIGINAL_GIT_COMMAND_FAILED'}
 return (($out -join [Environment]::NewLine).Trim())
}
function CheckNoReparse([string]$path){
 $p=$path
 while($p -and (Test-Path -LiteralPath $p)){
  if(((Get-Item -LiteralPath $p -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Block 'REPARSE_BOUNDARY'}
  $parent=Split-Path -Parent $p
  if($parent -eq $p){break}
  $p=$parent
 }
}
function Get-ServiceSnapshot {
 $svc=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $svc){Block 'SCM_SERVICE_MISSING'}
 return $svc
}
function Snapshot([string]$key,$svc){
 $rec[$key]=[ordered]@{
  name=$svc.Name;state=$svc.State;start_mode=$svc.StartMode
  start_name=$svc.StartName;path_name=$svc.PathName
  pid=[int]$svc.ProcessId;exit_code=$svc.ExitCode
 }
}
try {
 $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin){Block 'ADMIN_REQUIRED'}
 Gate 'ADMIN' 'PASS' 'Elevated Windows Administrator token'
 foreach($p in @($worktree,$stage,$exe,$nativeMarker,$switchMarker,$recoveryMarker,$receiptDir)){CheckNoReparse $p}
 if((ReadGit -GitArguments @('rev-parse','HEAD')) -cne $expectedHead){Block 'ORIGINAL_HEAD_CHANGED'}
 if((ReadGit -GitArguments @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Block 'ORIGINAL_BRANCH_CHANGED'}
 if((ReadGit -GitArguments @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Block 'ORIGINAL_ORIGIN_CHANGED'}
 Gate 'ORIGINAL_HEAD' 'PASS' 'Original repository checked read-only'
 foreach($item in @(
  @{name='V2_EXE';path=$exe;hash=$expectedExeHash},
  @{name='NATIVE_MARKER';path=$nativeMarker;hash=$expectedNativeMarkerHash},
  @{name='SWITCH_MARKER';path=$switchMarker;hash=$expectedSwitchMarkerHash}
  )){
  if(-not(Test-Path -LiteralPath $item.path -PathType Leaf)){Block ('MISSING_'+$item.name)}
  if((Sha $item.path) -cne $item.hash){Block ('HASH_MISMATCH_'+$item.name)}
  Gate $item.name 'PASS_EXACT' $item.hash
 }
 $svc=Get-ServiceSnapshot
 Snapshot 'SCM_before' $svc
 if($svc.StartName -ine 'NT AUTHORITY\LocalService' -or $svc.StartMode -ne 'Manual' -or
    $svc.PathName.Trim().Trim([char]34).Trim() -ine $exe){Block 'SCM_CONFIGURATION_CHANGED'}
 Gate 'SCM_CONFIG' 'PASS' 'Manual, LocalService, exact pinned broker V2'
 if($svc.State -eq 'Stopped' -and [int]$svc.ProcessId -eq 0){
  Gate 'SERVICE' 'PASS_ALREADY_STOPPED' 'Service stopped before any action'
  $rec.verdict='PASS_CURRENTLY_STOPPED_NO_ACTION_PREVIOUS_STOP_BLOCK_RETAINED'
 }elseif($svc.State -ne 'Running'){
  Block ('SCM_NOT_RUNNING_STATE_'+$svc.State)
 }elseif([int]$svc.ProcessId -ne $expectedPid){
  Block 'SCM_PID_DIFFERENT_FROM_FROZEN_INCIDENT'
 }else{
  $process=Get-CimInstance Win32_Process -Filter ('ProcessId='+$expectedPid) -ErrorAction Stop
  if($null -eq $process -or $process.ExecutablePath -ine $exe){Block 'SCM_PROCESS_IMAGE_OR_PID_MISMATCH'}
  $createdUtc=([datetime]$process.CreationDate).ToUniversalTime()
  $createdMs=([DateTimeOffset]::new($createdUtc)).ToUnixTimeMilliseconds()
  $rec['process_identity']=[ordered]@{pid=$expectedPid;creation_unix_ms=$createdMs;image_path=$process.ExecutablePath}
  if([Math]::Abs($createdMs-$expectedCreationUnixMs) -gt 1000){Block 'SCM_PROCESS_CREATION_TIMESTAMP_MISMATCH'}
  Gate 'EXACT_LIVE_PROCESS' 'PASS' 'PID + image path + creation-time identity pinned to incident'
  # One-shot marker: test absence using Win32, distinguish access denied.
  Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TtmP01StopMarker {
 [DllImport("kernel32.dll",EntryPoint="GetFileAttributesW",CharSet=CharSet.Unicode,ExactSpelling=true,SetLastError=true)]
 public static extern uint GetAttributes(string path);
}
'@ -ErrorAction Stop
  $attributes=[TtmP01StopMarker]::GetAttributes($recoveryMarker)
  if($attributes -ne [uint32]::MaxValue){Block 'STOP_RECOVERY_ALREADY_ATTEMPTED_NO_REPLAY'}
  $markerError=[Runtime.InteropServices.Marshal]::GetLastWin32Error()
  if($markerError -ne 2){Block ('STOP_RECOVERY_MARKER_UNRESOLVED_'+$markerError)}
  Gate 'RECOVERY_MARKER_ABSENT' 'PASS_WIN32_2' 'Marker proven not to exist by Win32'
  if(-not $Apply){
   $rec.verdict='PREFLIGHT_PASS_STOP_NOT_REQUESTED'
   Gate 'SCM_STOP_COMMAND' 'NOT_EXECUTED' 'Explicit -Apply required'
  }else{
   # Durable marker created before the only SCM STOP control request.
   $bytes=[Text.Encoding]::UTF8.GetBytes(('run_id='+$id+[Environment]::NewLine+'service='+$serviceName+
    [Environment]::NewLine+'process_creation_unix_ms='+$createdMs+[Environment]::NewLine))
   $stream=[IO.File]::Open($recoveryMarker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
   try{$stream.Write($bytes,0,$bytes.Length);$stream.Flush()}
   finally{$stream.Dispose()}
   $rec.recovery_marker_sha256=Sha $recoveryMarker
   Gate 'RECOVERY_MARKER' 'PASS_CREATED' 'No replay, do not delete marker'
   $rec.service_stop_requested=$true
   $result=@(& sc.exe stop $serviceName 2>&1)
   $rec.sc_stop_exit=$LASTEXITCODE
   $rec.sc_stop_output=@($result|ForEach-Object {"$_"})
   Gate 'SCM_STOP_COMMAND' $(if($LASTEXITCODE -eq 0){'ACCEPTED'}else{'RETURNED_ERROR'}) ('Exit='+$LASTEXITCODE)
   # Bounded observation; no repeated stop and no forced termination.
   $deadline=[DateTime]::UtcNow.AddSeconds(15)
   do{
    Start-Sleep -Milliseconds 750
    $after=Get-ServiceSnapshot
    if($after.State -eq 'Stopped' -and [int]$after.ProcessId -eq 0){break}
   }while([DateTime]::UtcNow -lt $deadline)
   Snapshot 'SCM_after' $after
   if($after.State -eq 'Stopped' -and [int]$after.ProcessId -eq 0){
    Gate 'SERVICE_FINAL_STATE' 'PASS_STOPPED_PID_0' 'Independent readback after one SCM stop request'
    $rec.verdict=if($rec.sc_stop_exit -eq 0){'PASS_CONTROLLED_SCM_STOP_RECOVERED'}else{'RECOVERED_STATE_WITH_SCM_CONTROL_ERROR'}
   }else{
    Gate 'SERVICE_FINAL_STATE' 'BLOCK_RUNNING_OR_PENDING_NO_FORCE' ('State='+$after.State+';PID='+$after.ProcessId)
    $rec.verdict='BLOCK_STOP_RECOVERY_UNRESOLVED_NO_FORCE'
   }
  }
 }
}catch{
 $rec.errors+= $_.Exception.Message
 $rec.verdict='BLOCK_STOP_RECOVERY_EXCEPTION'
 Write-Host ('TTM_RECOVER_BLOCK='+$_.Exception.Message)
}finally{
 # Snapshot in all modes; never stop again, kill, delete, or alter the SCM.
 try{
  if($rec.SCM_after.Count -eq 0){
   try{
    $last=Get-ServiceSnapshot
    Snapshot 'SCM_after' $last
    Write-Host ('TTM_RECOVER_SCM_FINAL_STATE='+$last.State+';PID='+$last.ProcessId)
   }catch{
    $rec.errors+=('FINAL_SCM_SNAPSHOT_'+$_.Exception.GetType().Name)
   }
  }
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $rec['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($file,($rec|ConvertTo-Json -Depth 16),(New-Object Text.UTF8Encoding $false))
  $sha=Sha $file
  Write-Host ('TTM_RECOVER_RECEIPT='+$file)
  Write-Host ('TTM_RECOVER_SHA256='+$sha)
  $target='artifacts/qa/p01/'+$id+'.json'
  $request=Join-Path $receiptDir 'github_create.json'
  $payload=@{branch=$branch;message=('evidence(p01): exact SCM service-stop recovery '+$id);
   content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$payload,(New-Object Text.UTF8Encoding $false))
  $up=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$target) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_UPLOAD_FAILED'}
  $saved=($up -join [Environment]::NewLine)|ConvertFrom-Json
  $raw=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$target+'?ref='+$saved.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_READBACK_FAILED'}
  $back=($raw -join [Environment]::NewLine)|ConvertFrom-Json
  $sha256=[Security.Cryptography.SHA256]::Create()
  try{$backHash=([BitConverter]::ToString($sha256.ComputeHash([Convert]::FromBase64String(($back.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally{$sha256.Dispose()}
  if($backHash -cne $sha){Block 'GITHUB_SHA256_MISMATCH'}
  Write-Host ('TTM_RECOVER_GITHUB_COMMIT='+$saved.commit.sha)
  Write-Host 'TTM_RECOVER_GITHUB_READBACK=PASS'
  $exitCode=if($rec.verdict -in @('PASS_CONTROLLED_SCM_STOP_RECOVERED','PASS_CURRENTLY_STOPPED_NO_ACTION_PREVIOUS_STOP_BLOCK_RETAINED')){0}else{3}
 }catch{
  Write-Host ('TTM_RECOVER_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exitCode=5
 }
}
Write-Host 'TTM_RECOVER_FORCED_TERMINATION=NOT_EXECUTED'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exitCode
