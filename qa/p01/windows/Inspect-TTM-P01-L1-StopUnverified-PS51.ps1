#requires -Version 5.1
# TTM P01 L1: stop-unverified incident, READ-ONLY machine-state snapshot.
# Only new project-local receipt JSON + GitHub QA commit may be written.
# No service start/stop, process termination, ACL, accounts, marker modification.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$worktree=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$bin=Join-Path $stage 'broker_service'
$expectedExe=Join-Path $bin 'TTMP01Broker.attestationV2.exe'
$expectedExeSha='a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a'
$expectedOriginal='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$marker=Join-Path $stage 'L1_BROKER_V2_WORKER_V3_NATIVE_SECURITY_ATTEMPT_20261106.lock'
$markerSha='f0d895e68c30b8c3845336ea8aee40d2e1ca84f96816906a952ae70ad81587c7'
$switchMarker=Join-Path $stage 'L1_SCM_V2_SWITCH_ATTEMPT_20261106.lock'
$switchMarkerSha='29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1'
$serviceName='TTMP01Broker'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$id='L1_V2_STOP_UNVERIFIED_READONLY_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $root ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$report=[ordered]@{
 schema='ttm.p01.l1.stop_unverified_readonly.v1'
 run_id=$id
 source_incident_commit='45f74877a43a66e6559f2a61d6f765ffd0c7da98'
 original_head_expected=$expectedOriginal
 checks=[ordered]@{}
 scm=[ordered]@{}
 process=[ordered]@{}
 queryex=[ordered]@{}
 marker=[ordered]@{}
 errors=@()
 verdict='INCOMPLETE_READONLY_DIAGNOSTIC'
 service_mutated=$false
 process_terminated=$false
 account_mutated=$false
 ACL_mutated=$false
 W01_W12='NOT_EXECUTED'
 L1_grouped_QA='NOT_AUTHORIZED'
}
function Gate([string]$name,[string]$status,[string]$detail){
 $report.checks[$name]=[ordered]@{status=$status;detail=$detail}
 Write-Host ('TTM_STOP_DIAG_'+$name+'='+$status)
}
function Sha([string]$path){return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function Block([string]$reason){throw [InvalidOperationException]::new($reason)}
function ReadGit([string[]]$GitArguments){
 $lines=@(& git.exe -C $worktree @GitArguments 2>&1)
 if($LASTEXITCODE -ne 0){Block 'GIT_READ_FAILED'}
 return (($lines -join [Environment]::NewLine).Trim())
}
function CheckMarker([string]$name,[string]$path,[string]$expected){
 try {
  $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
  if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Gate $name 'BLOCK_REPARSE' 'Do not follow';return}
  if($item.PSIsContainer){Gate $name 'BLOCK_NOT_FILE' 'Expected file marker';return}
  $observed=Sha $path
  if($observed -cne $expected){Gate $name 'BLOCK_HASH_MISMATCH' $observed;return}
  Gate $name 'PASS_PRESENT_EXACT' $observed
 }catch{
  Gate $name 'BLOCK_MISSING_OR_INACCESSIBLE' $_.Exception.GetType().Name
 }
}
try {
 $isAdmin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 Gate 'ELEVATED' $(if($isAdmin){'PASS'}else{'BLOCK_ADMIN_REQUIRED'}) 'Windows elevated token checked before protected path access'
 if(-not $isAdmin){Block 'ADMIN_REQUIRED'}
 # Observe real SCM state FIRST, before any potentially inaccessible TTM paths.
 $svc=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $svc){Block 'SERVICE_MISSING_UNEXPECTED'}
 $report.scm=[ordered]@{
  name=$svc.Name
  state=$svc.State
  status=$svc.Status
  start_mode=$svc.StartMode
  account=$svc.StartName
  binpath=$svc.PathName
  process_id=[int]$svc.ProcessId
  exit_code=$svc.ExitCode
  service_specific_exit=$svc.ServiceSpecificExitCode
 }
 Gate 'SCM_SNAPSHOT' 'PASS_READONLY' ('State='+$svc.State+';PID='+$svc.ProcessId)
 $q=@(& sc.exe queryex $serviceName 2>&1)
 $queryExit=$LASTEXITCODE
 $report.queryex=[ordered]@{exit_code=$queryExit;lines=@($q|ForEach-Object {"$_"})}
 if($queryExit -ne 0){Gate 'QUERYEX' 'BLOCK' ('Exit='+$queryExit)}
 else{Gate 'QUERYEX' 'PASS_READONLY' 'SCM queryex captured'}
 $qc=@(& sc.exe qc $serviceName 2>&1)
 $qcExit=$LASTEXITCODE
 $report['qc']=[ordered]@{exit_code=$qcExit;lines=@($qc|ForEach-Object {"$_"})}
 if($qcExit -ne 0){Gate 'SCM_CONFIG' 'BLOCK' ('Exit='+$qcExit)}
 elseif($svc.StartName -ine 'NT AUTHORITY\LocalService' -or $svc.StartMode -ne 'Manual' -or
         $svc.PathName.Trim().Trim([char]34).Trim() -ine $expectedExe){
  Gate 'SCM_CONFIG' 'BLOCK_UNEXPECTED_CONFIG' 'No changes allowed'
 }else{
  Gate 'SCM_CONFIG' 'PASS_READBACK_ONLY' 'Expected V2 binary, LocalService, demand start'
 }
 if($svc.ProcessId -gt 0){
  try{
   $pidNumber=[int]$svc.ProcessId
   $p=Get-CimInstance Win32_Process -Filter ("ProcessId="+$pidNumber) -ErrorAction Stop
   if($null -eq $p){Gate 'SCM_PID' 'BLOCK_PID_NOT_FOUND' 'Do not assume old process PID is current'}
   else{
    $report.process=[ordered]@{pid=$pidNumber;name=$p.Name;executable_path=$p.ExecutablePath;creation_date=$p.CreationDate}
    if($p.ExecutablePath -and ($p.ExecutablePath -ine $expectedExe)){
     Gate 'SCM_PID' 'BLOCK_PROCESS_IMAGE_MISMATCH' 'Do not terminate or reconfigure'
    }else{
     Gate 'SCM_PID' 'PASS_PROCESS_OBSERVED' 'SCM-linked PID and image metadata observed'
    }
   }
  }catch{
   Gate 'SCM_PID' 'BLOCK_PROCESS_QUERY' $_.Exception.GetType().Name
  }
 }else{
  Gate 'SCM_PID' 'NO_ACTIVE_SERVICE_PID' 'No process owned by SCM service at time of snapshot'
 }
 if(-not(Test-Path -LiteralPath $worktree -PathType Container)){Block 'ORIGINAL_WORKTREE_MISSING'}
 if((ReadGit -GitArguments @('rev-parse','HEAD')) -cne $expectedOriginal){Block 'ORIGINAL_HEAD_MISMATCH'}
 if((ReadGit -GitArguments @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Block 'ORIGINAL_BRANCH_MISMATCH'}
 if((ReadGit -GitArguments @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Block 'ORIGIN_MISMATCH'}
 Gate 'ORIGINAL_WORKTREE' 'PASS' 'Exact original HEAD/branch/origin read-only'
 if((Sha $expectedExe) -cne $expectedExeSha){Block 'V2_EXE_SHA256_MISMATCH'}
 Gate 'V2_EXE_PIN' 'PASS' $expectedExeSha
 CheckMarker 'SCM_SWITCH_MARKER' $switchMarker $switchMarkerSha
 CheckMarker 'NATIVE_TEST_MARKER' $marker $markerSha
 if($svc.State -eq 'Stopped' -and $svc.ProcessId -eq 0){
  $report.verdict='PASS_SERVICE_STOPPED_NOW_READONLY_DIAG_ONLY'
  Gate 'SERVICE_CURRENT_STATE' 'PASS_STOPPED_NOW' 'No running SCM PID at observation; previous stop failure retained'
 }else {
  $report.verdict='BLOCK_ACTIVE_OR_TRANSITIONING_SERVICE_NEEDS_SEPARATE_RECOVERY'
  Gate 'SERVICE_CURRENT_STATE' 'BLOCK_ACTIVE_OR_TRANSITION' ('State='+$svc.State+';Pid='+$svc.ProcessId)
 }
} catch {
 $report.errors+= $_.Exception.Message
 $report.verdict='BLOCK_READONLY_DIAGNOSTIC'
 Write-Host ('TTM_STOP_DIAG_BLOCK='+$_.Exception.Message)
} finally {
 # Only a new project-local QA evidence directory is created. No process action.
 try{
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $report['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($file,($report|ConvertTo-Json -Depth 16),(New-Object Text.UTF8Encoding $false))
  $sha=Sha $file
  Write-Host ('TTM_STOP_DIAG_RECEIPT='+$file)
  Write-Host ('TTM_STOP_DIAG_SHA256='+$sha)
  $target='artifacts/qa/p01/'+$id+'.json'
  $request=Join-Path $receiptDir 'github_create.json'
  $body=@{branch=$branch;message=('evidence(p01): STOP_UNVERIFIED native SCM snapshot '+$id);
    content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$body,(New-Object Text.UTF8Encoding $false))
  $up=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$target) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_UPLOAD_FAILED'}
  $created=($up -join [Environment]::NewLine)|ConvertFrom-Json
  $back=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$target+'?ref='+$created.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_READBACK_FAILED'}
  $read=($back -join [Environment]::NewLine)|ConvertFrom-Json
  $h=[Security.Cryptography.SHA256]::Create()
  try{
   $got=([BitConverter]::ToString($h.ComputeHash([Convert]::FromBase64String(($read.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()
  }finally{$h.Dispose()}
  if($got -cne $sha){Block 'GITHUB_SHA_READBACK_MISMATCH'}
  Write-Host ('TTM_STOP_DIAG_GITHUB_COMMIT='+$created.commit.sha)
  Write-Host 'TTM_STOP_DIAG_GITHUB_READBACK=PASS'
  $code=if($report.verdict -eq 'PASS_SERVICE_STOPPED_NOW_READONLY_DIAG_ONLY'){0}else{3}
 }catch{
  Write-Host ('TTM_STOP_DIAG_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $code=5
 }
}
Write-Host 'TTM_STOP_DIAG_SERVICE_ACTION=NONE'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $code
