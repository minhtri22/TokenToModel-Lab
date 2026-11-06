#requires -Version 5.1
# TTM P01 L1 — read-only diagnosis of pre-gate Access is denied.
# Changes only new QA receipt files and GitHub evidence, never SCM/account/ACL.
[CmdletBinding()] param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo='D:\WORK\RESEARCH\TokenToModel-Lab'
$worktree=Join-Path $repo 'worktrees\p01-f0-static-i0a-20261105'
$staging=Join-Path $repo 'worktrees\_ttm_p01_l1_service_provision_20261106'
$broker=Join-Path $staging 'broker_service'
$evidence=Join-Path $staging 'evidence'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$expectedHead='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$run='L1_SCM_SWITCH_EARLY_DENIED_DIAG_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$evidenceDir=Join-Path $repo ('worktrees\_ttm_p01_l1_qa_receipts\'+$run)
$report=[ordered]@{
 schema='ttm.p01.l1.scm_switch_early_access_diagnostic.v1';run_id=$run;
 original_head_expected=$expectedHead;prior_failure_commit='14b51937f861f26f05d53b38f0808522e462e5d9';
 admin_elevated=$false;checks=[ordered]@{};errors=@();
 verdict='BLOCK_READONLY_DIAGNOSTIC';
 scm_changed_by_diagnostic=$false;account_changed_by_diagnostic=$false;
 acl_changed_by_diagnostic=$false;worker_started=$false;
 W01_W12='NOT_EXECUTED';L1_grouped_QA='NOT_AUTHORIZED';
}
function Record-Check([string]$key,[string]$status,[string]$detail){
 $report.checks[$key]=[ordered]@{status=$status;detail=$detail}
 Write-Host ('TTM_ACCESS_DIAG_'+$key+'='+$status)
}
function Record-Path([string]$label,[string]$target) {
 # Mirror the ORIGINAL NoReparse traversal; never open file contents.
 $cursor=$target
 $result='READABLE_METADATA_ONLY'
 $stoppedAt=''
 $exType=''
 $errorId=''
 while($cursor) {
  try {
   $exists=Test-Path -LiteralPath $cursor -ErrorAction Stop
   if(-not $exists){
    $result='ABSENT'
    $stoppedAt=$cursor
    break
   }
   $item=Get-Item -LiteralPath $cursor -Force -ErrorAction Stop
   if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){
    $result='REPARSE_POINT_BLOCK'
    $stoppedAt=$cursor
    break
   }
  } catch {
   $result='ACCESS_ERROR'
   $stoppedAt=$cursor
   $exType=$_.Exception.GetType().FullName
   $errorId=$_.FullyQualifiedErrorId
   break
  }
  $parent=Split-Path -Parent $cursor
  if([string]::IsNullOrEmpty($parent) -or $parent -eq $cursor){break}
  $cursor=$parent
 }
 $report.checks['PATH_'+$label]=[ordered]@{
  status=$result;stopped_at=$stoppedAt;exception_type=$exType;error_id=$errorId
 }
 Write-Host ('TTM_ACCESS_DIAG_PATH_'+$label+'='+$result)
 if($result -eq 'ACCESS_ERROR'){
  Write-Host ('TTM_ACCESS_DIAG_FIRST_ERROR_PATH='+$stoppedAt)
  Write-Host ('TTM_ACCESS_DIAG_FIRST_ERROR_TYPE='+$exType)
 }
}
function SHA256([string]$path){
 return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}
try {
 $wp=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
 $report.admin_elevated=$wp.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 Record-Check 'ADMIN_ELEVATED' $(if($report.admin_elevated){'PASS'}else{'BLOCK_NOT_ADMIN'}) 'Windows admin membership of the current elevated token'
 $pathSet=[ordered]@{
 WORKTREE=$worktree
 STAGE=$staging
 BROKER_DIR=$broker
 V1_EXE=(Join-Path $broker 'TTMP01Broker.fixed.exe')
 V2_EXE=(Join-Path $broker 'TTMP01Broker.attestationV2.exe')
 V2_SOURCE=(Join-Path $broker 'BrokerAttestationServiceV2.cs')
 V2_PROBE_DLL=(Join-Path $broker 'TTMWorkerNativeProbeV2.dll')
 SID_CONFIG=(Join-Path $broker 'broker_sids.txt')
 CREDENTIAL_METADATA=(Join-Path $broker 'worker_credential.dpapi.xml')
 LEDGER_METADATA=(Join-Path $evidence 'broker_ledger.sqlite3')
 SWITCH_MARKER=(Join-Path $staging 'L1_SCM_V2_SWITCH_ATTEMPT_20261106.lock')
 }
 foreach($key in $pathSet.Keys){Record-Path $key $pathSet[$key]}
 # Read SCM only; do not start, stop, configure, or delete the service.
 try{
  $scm=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
  if($null -eq $scm){
   Record-Check 'SCM_PRESENT' 'BLOCK_ABSENT' 'Expected service absent, no modification attempted'
  } else {
   $report['scm_snapshot']=[ordered]@{
    state=$scm.State;start_mode=$scm.StartMode;start_name=$scm.StartName;path_name=$scm.PathName
   }
   Record-Check 'SCM_PRESENT' 'PASS_READBACK_ONLY' ('State='+$scm.State+';Mode='+$scm.StartMode)
  }
 }catch{
  Record-Check 'SCM_READ' 'ACCESS_ERROR' $_.Exception.GetType().FullName
 }
 # Git only through read-only commands. Include errors without altering HEAD.
 foreach($command in @(
  @{name='HEAD';args=@('rev-parse','HEAD')},
  @{name='BRANCH';args=@('branch','--show-current')},
  @{name='ORIGIN';args=@('remote','get-url','origin')}
  )){
  try{
   $out=@(& git.exe -C $worktree @($command.args) 2>&1)
   $code=$LASTEXITCODE
   if($code -ne 0){Record-Check ('GIT_'+$command.name) 'BLOCK' ('Exit='+$code)}
   else{
    $value=($out -join [Environment]::NewLine).Trim()
    $valid=switch($command.name){
     'HEAD' {$value -ceq $expectedHead}
     'BRANCH' {$value -ceq 'implementation/p01-i0a-s-f0-static-20261106'}
     'ORIGIN' {$value -ieq 'https://github.com/minhtri22/TokenToModel-Lab.git'}
    }
    Record-Check ('GIT_'+$command.name) $(if($valid){'PASS'}else{'BLOCK_MISMATCH'}) 'Read-only identity comparison'
   }
  }catch{
   Record-Check ('GIT_'+$command.name) 'ACCESS_ERROR' $_.Exception.GetType().FullName
  }
 }
 $marker=$report.checks['PATH_SWITCH_MARKER'].status
 if($marker -eq 'READABLE_METADATA_ONLY'){
  Record-Check 'ONE_SHOT_REPLAY' 'BLOCK_MARKER_PRESENT' 'Do not run any SCM config; marker was already created'
 } elseif($marker -eq 'ABSENT') {
  Record-Check 'ONE_SHOT_REPLAY' 'NOT_ATTEMPTED_BY_PREVIOUS_RECEIPT' 'Marker absent; independent SCM state readback still needed'
 } else {
  Record-Check 'ONE_SHOT_REPLAY' 'BLOCK_UNRESOLVED' 'Marker path inspection not conclusive'
 }
 $report.verdict='READONLY_DIAGNOSTIC_COMPLETED_NOT_SCM_PERMIT'
} catch {
 $report.errors+= $_.Exception.GetType().FullName
 $report.verdict='BLOCK_READONLY_DIAGNOSTIC_EXCEPTION'
 Write-Host ('TTM_ACCESS_DIAG_BLOCK='+$_.Exception.GetType().Name)
} finally {
 try {
  New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
  $report['utc']=[DateTime]::UtcNow.ToString('o')
  $json=Join-Path $evidenceDir ($run+'.json')
  [IO.File]::WriteAllText($json,($report|ConvertTo-Json -Depth 16),(New-Object Text.UTF8Encoding $false))
  $sha=SHA256 $json
  Write-Host ('TTM_ACCESS_DIAG_RECEIPT='+$json)
  Write-Host ('TTM_ACCESS_DIAG_SHA256='+$sha)
  $apiPath='artifacts/qa/p01/'+$run+'.json'
  $request=Join-Path $evidenceDir 'github_request.json'
  $payload=@{branch=$branch;message=('evidence(p01): early SCM switch denied path diagnosis '+$run);content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($json))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$payload,(New-Object Text.UTF8Encoding $false))
  $response=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$apiPath) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){throw 'GITHUB_EVIDENCE_CREATE_FAILED'}
  $result=($response -join [Environment]::NewLine)|ConvertFrom-Json
  $back=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$apiPath+'?ref='+$result.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){throw 'GITHUB_EVIDENCE_READBACK_FAILED'}
  $retrieved=($back -join [Environment]::NewLine)|ConvertFrom-Json
  $h=[Security.Cryptography.SHA256]::Create()
  try{
   $got=([BitConverter]::ToString($h.ComputeHash([Convert]::FromBase64String(($retrieved.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()
  }finally{$h.Dispose()}
  if($got -cne $sha){throw 'GITHUB_EVIDENCE_SHA256_MISMATCH'}
  Write-Host ('TTM_ACCESS_DIAG_GITHUB_COMMIT='+$result.commit.sha)
  Write-Host 'TTM_ACCESS_DIAG_GITHUB_READBACK=PASS'
  $exitCode=if($report.verdict -eq 'READONLY_DIAGNOSTIC_COMPLETED_NOT_SCM_PERMIT'){0}else{3}
 } catch {
  Write-Host ('TTM_ACCESS_DIAG_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exitCode=5
 }
}
Write-Host 'TTM_SCM_SWITCH=NOT_EXECUTED'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exitCode
