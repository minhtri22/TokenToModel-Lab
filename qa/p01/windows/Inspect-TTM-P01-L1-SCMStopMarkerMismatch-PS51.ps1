#requires -Version 5.1
# TTM P01 L1: forensic readback ONLY after SCM stop recovery marker mismatch.
# Writes: new TTM QA receipt and corresponding GitHub evidence; never touches markers or service.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$marker=Join-Path $stage 'L1_BROKER_V2_SCM_STOP_RECOVERY_ATTEMPT_20261106.lock'
$forceMarker=Join-Path $stage 'L1_BROKER_V2_EXACT_PROCESS_TERMINATE_ATTEMPT_20261106.lock'
$oldRun='L1_BROKER_V2_SCM_STOP_RECOVERY_20261106T163818549Z_8b9033ff'
$oldSha='f1ca3d0899fe6637a512e44dd073b449d4805ca8f8a8afa1e8a3989599143502'
$base='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$id='L1_STOP_MARKER_MISMATCH_READONLY_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $root ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$rec=[ordered]@{
 schema='ttm.p01.l1.stop_marker_mismatch_readonly.v1'
 run_id=$id
 reported_failure_commit='441bec040d9d186bc2088d0747efe04d71a62f74'
 original_receipt_commit='8a3666c655edba86bef2a841a31246fe19e0e870'
 marker_expected_sha256=$oldSha
 checks=[ordered]@{}
 marker=[ordered]@{}
 scm=[ordered]@{}
 force_marker_state='NOT_CHECKED'
 verdict='BLOCK_READONLY_DIAGNOSTIC'
 errors=@()
 service_changed=$false
 marker_changed=$false
 process_terminated=$false
 W01_W12='NOT_EXECUTED'
 grouped_L1='NOT_AUTHORIZED'
}
function Gate([string]$key,[string]$value,[string]$detail){
 $rec.checks[$key]=[ordered]@{status=$value;detail=$detail}
 Write-Host ('TTM_MARKER_DIAG_'+$key+'='+$value)
}
function Halt([string]$why){throw [InvalidOperationException]::new($why)}
function HashBytes([byte[]]$bytes){
 $hash=[Security.Cryptography.SHA256]::Create()
 try{return ([BitConverter]::ToString($hash.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()}
 finally{$hash.Dispose()}
}
function HashFile([string]$file){return (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()}
function GitRead([string[]]$GitArguments){
 $out=@(& git.exe -C $wt @GitArguments 2>&1)
 if($LASTEXITCODE -ne 0){Halt 'LOCAL_GIT_READ_FAILED'}
 return (($out -join [Environment]::NewLine).Trim())
}
function NoReparse([string]$p){
 $current=$p
 while($current -and (Test-Path -LiteralPath $current)){
  $item=Get-Item -LiteralPath $current -Force -ErrorAction Stop
  if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Halt 'REPARSE_BOUNDARY'}
  $parent=Split-Path -Parent $current
  if($parent -eq $current){break}
  $current=$parent
 }
}
try{
 $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin){Halt 'ADMIN_REQUIRED'}
 Gate 'ADMIN' 'PASS' 'Elevated token'
 $svc=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $svc){Halt 'SERVICE_ABSENT'}
 $rec.scm=[ordered]@{state=$svc.State;pid=[int]$svc.ProcessId;account=$svc.StartName;mode=$svc.StartMode;image=$svc.PathName}
 Gate 'SCM' 'PASS_READONLY' ('State='+$svc.State+';Pid='+$svc.ProcessId)
 foreach($p in @($wt,$stage,$marker,$forceMarker,$receiptDir)){NoReparse $p}
 if((GitRead -GitArguments @('rev-parse','HEAD')) -cne $base){Halt 'HEAD_MISMATCH'}
 if((GitRead -GitArguments @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Halt 'BRANCH_MISMATCH'}
 if((GitRead -GitArguments @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Halt 'ORIGIN_MISMATCH'}
 Gate 'ORIGINAL' 'PASS' 'HEAD branch origin read-only'
 $expectedLines=@(('run_id='+$oldRun),'service=TTMP01Broker','process_creation_unix_ms=1793982282113','')
 $expectedText=$expectedLines -join [Environment]::NewLine
 $expectedBytes=[Text.Encoding]::UTF8.GetBytes($expectedText)
 $derived=HashBytes $expectedBytes
 if($derived -cne $oldSha){Halt 'RECONSTRUCTED_MARKER_HASH_NOT_MATCH_ORIGINAL'}
 Gate 'ORIGINAL_MARKER_RECONSTRUCTION' 'PASS_EXACT' $derived
 $item=Get-Item -LiteralPath $marker -Force -ErrorAction Stop
 if($item.PSIsContainer){Halt 'STOP_MARKER_NOT_FILE'}
 $contents=[IO.File]::ReadAllBytes($marker)
 $observed=HashBytes $contents
 $first=-1
 $bound=[Math]::Min($contents.Length,$expectedBytes.Length)
 for($i=0;$i -lt $bound;$i++){
  if($contents[$i] -ne $expectedBytes[$i]){$first=$i;break}
 }
 if($first -lt 0 -and $contents.Length -ne $expectedBytes.Length){$first=$bound}
 $rec.marker=[ordered]@{
  path=$marker
  expected_sha256=$oldSha
  actual_sha256=$observed
  expected_length=$expectedBytes.Length
  actual_length=$contents.Length
  first_different_byte=$(if($first -ge 0){$first}else{$null})
  created_utc=$item.CreationTimeUtc.ToString('o')
  modified_utc=$item.LastWriteTimeUtc.ToString('o')
  attributes=$item.Attributes.ToString()
  bytes_published=$false
 }
 Gate 'STOP_MARKER' $(if($observed -ceq $oldSha){'PASS_EXACT'}else{'BLOCK_HASH_DRIFT'}) 'SHA256/length/times only; content not published'
 try{
  $force=Get-Item -LiteralPath $forceMarker -Force -ErrorAction Stop
  $rec.force_marker_state=$(if(($force.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){'BLOCK_REPARSE'}else{'PRESENT'})
 }catch{
  $rec.force_marker_state='NOT_CONFIRMED_PRESENT'
 }
 Gate 'FORCE_MARKER' $rec.force_marker_state 'No changes and no inference of guaranteed absence'
 if($observed -ceq $oldSha){$rec.verdict='MARKER_NOW_EXACT_REASSESS_REQUIRED'}
 else{$rec.verdict='BLOCK_MARKER_DRIFT_CONFIRMED_NO_ACTION'}
}catch{
 $rec.errors+= $_.Exception.Message
 $rec.verdict='BLOCK_FORENSIC_READONLY_EXCEPTION'
 Write-Host ('TTM_MARKER_DIAG_BLOCK='+$_.Exception.Message)
}finally{
 try{
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $rec['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($file,($rec|ConvertTo-Json -Depth 14),(New-Object Text.UTF8Encoding $false))
  $sha=HashFile $file
  Write-Host ('TTM_MARKER_DIAG_RECEIPT='+$file)
  Write-Host ('TTM_MARKER_DIAG_SHA256='+$sha)
  $path='artifacts/qa/p01/'+$id+'.json'
  $request=Join-Path $receiptDir 'github_create.json'
  $payload=@{branch=$branch;message=('evidence(p01): SCM stop marker SHA forensic '+$id);
   content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$payload,(New-Object Text.UTF8Encoding $false))
  $saved=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$path) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_UPLOAD_FAILED'}
  $obj=($saved -join [Environment]::NewLine)|ConvertFrom-Json
  $read=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$obj.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_READBACK_FAILED'}
  $back=($read -join [Environment]::NewLine)|ConvertFrom-Json
  $got=HashBytes ([Convert]::FromBase64String(($back.content -replace '\s','')))
  if($got -cne $sha){Halt 'GITHUB_SHA256_READBACK_MISMATCH'}
  Write-Host ('TTM_MARKER_DIAG_GITHUB_COMMIT='+$obj.commit.sha)
  Write-Host 'TTM_MARKER_DIAG_GITHUB_READBACK=PASS'
  $code=if($rec.verdict -eq 'MARKER_NOW_EXACT_REASSESS_REQUIRED'){0}else{3}
 }catch{
  Write-Host ('TTM_MARKER_DIAG_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $code=5
 }
}
Write-Host 'TTM_MARKER_DIAG_PROCESS_ACTION=NONE'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $code
