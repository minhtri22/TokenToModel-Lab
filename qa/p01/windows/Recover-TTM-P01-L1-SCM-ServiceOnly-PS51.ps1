#requires -Version 5.1
# TTM P01 L1 — one-shot RECOVER MISSING SERVICE ONLY after observed SCM error 1060.
# No worker account/ACL/ledger/credential creation, no W01-W12, no F0.
[CmdletBinding()] param([switch]$Apply)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $repo 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $repo 'worktrees\_ttm_p01_l1_service_provision_20261106'
$exe=Join-Path $stage 'broker_service\TTMP01Broker.fixed.exe'
$config=Join-Path $stage 'broker_service\broker_sids.txt'
$cred=Join-Path $stage 'broker_service\worker_credential.dpapi.xml'
$ledger=Join-Path $stage 'evidence\broker_ledger.sqlite3'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$head='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$expectedExe='56a780db6aa61fdd556540da340a3be223df2e41e1a7295bb33d05628dbf87ef'
$expectedServiceSid='S-1-5-80-3250491234-3884958938-4011397885-464722667-3405458206'
$expectedWorkerSid='S-1-5-21-2910051730-1322758338-3406810807-1009'
$svc='TTMP01Broker'
$run='L1_SC_CREATE_SERVICE_ONLY_RECOVERY_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $repo ('worktrees\_ttm_p01_l1_qa_receipts\'+$run)
$receipt=[ordered]@{schema='ttm.p01.l1.service_only_recovery.v1';run_id=$run;mode=$(if($Apply){'APPLY_ONCE'}else{'PREFLIGHT_ONLY'});
 original_head=$head;source_receipt_commit='a56692b0029296042279218e33924008edd2e64b';checks=[ordered]@{};sc_create_exit=$null;sc_create_output=@();
 sc_sidtype_exit=$null;sc_sidtype_output=@();verdict='BLOCK';errors=@();W01_W12='NOT_EXECUTED';grouped_L1='NOT_AUTHORIZED';account_created=$false;ACL_modified=$false;service_started=$false}
function Set-Gate([string]$name,[string]$state,[string]$details) {
 $receipt.checks[$name]=[ordered]@{status=$state;detail=$details}
 Write-Host ('TTM_SERVICE_ONLY_'+$name+'='+$state)
}
function Halt([string]$reason) {throw [InvalidOperationException]::new($reason)}
function Sha256([string]$path) {return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function Assert-NoReparse([string]$path) {
 $p=$path
 while($p -and (Test-Path -LiteralPath $p)){
  $item=Get-Item -LiteralPath $p -Force
  if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Halt 'REPARSE_BOUNDARY'}
  $parent=Split-Path -Parent $p
  if($parent -eq $p){break}
  $p=$parent
 }
}
function Read-Git([string[]]$GitArguments) {
 $lines=@(& git.exe -C $wt @GitArguments 2>&1)
 if($LASTEXITCODE -ne 0){Halt 'LOCAL_GIT_IDENTITY_FAILED'}
 return (($lines -join [Environment]::NewLine).Trim())
}
try {
 foreach($p in @($wt,$stage,$exe,$config,$cred,$ledger)){Assert-NoReparse $p}
 if((Read-Git -GitArguments @('rev-parse','HEAD')) -cne $head){Halt 'LOCAL_HEAD_CHANGED'}
 if((Read-Git -GitArguments @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Halt 'LOCAL_BRANCH_CHANGED'}
 if((Read-Git -GitArguments @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Halt 'LOCAL_ORIGIN_MISMATCH'}
 Set-Gate 'PINNED_WORKTREE' 'PASS' 'Read-only original worktree'
 if(-not(Test-Path -LiteralPath $exe -PathType Leaf) -or (Sha256 $exe) -cne $expectedExe){Halt 'EXACT_BINARY_SHA256_MISMATCH'}
 Set-Gate 'EXACT_BINARY' 'PASS' $expectedExe
 $u=Get-LocalUser -Name TTMP01Worker -ErrorAction SilentlyContinue
 if($null -eq $u -or $u.SID.Value -cne $expectedWorkerSid -or -not $u.Enabled){Halt 'EXACT_WORKER_ACCOUNT_MISMATCH'}
 Set-Gate 'WORKER_IDENTITY' 'PASS_PRESENT_NOT_TOKEN_QUALIFIED' 'Existing worker SID and enabled state; no account mutation'
 foreach($p in @($config,$cred,$ledger)){if(-not(Test-Path -LiteralPath $p -PathType Leaf)){Halt 'PINNED_PROVISION_FILE_ABSENT'}}
 # SID configuration is public identity metadata, not a credential.
 $sidLines=@([IO.File]::ReadAllLines($config))
 if($sidLines.Length -ne 2 -or $sidLines[0] -cne ('service='+$expectedServiceSid) -or $sidLines[1] -cne ('worker='+$expectedWorkerSid)){Halt 'PINNED_SID_CONFIGURATION_MISMATCH'}
 Set-Gate 'EXISTING_CONFIG_AND_SECRET' 'PASS_PRESENCE_ONLY' 'Exactly pinned SID metadata; DPAPI/ledger bytes not read or changed'
 $adminGroupSid=New-Object Security.Principal.SecurityIdentifier('S-1-5-32-544')
 $adminGroup=Get-LocalGroupMember -SID $adminGroupSid -ErrorAction Stop
 if(@($adminGroup | Where-Object {$_.SID.Value -eq $expectedWorkerSid}).Count -gt 0){Halt 'WORKER_IS_LOCAL_ADMIN'}
 Set-Gate 'WORKER_NONADMIN' 'PASS' 'Exact worker SID is not a direct local Administrators member'
 foreach($p in @($stage,(Join-Path $stage 'broker_service'),(Join-Path $stage 'evidence'))){
  $acl=Get-Acl -LiteralPath $p
  if(-not $acl.AreAccessRulesProtected){Halt 'UNPROTECTED_DIRECTORY_DACL'}
  $allowed=@($acl.Access|Where-Object {$_.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow}|ForEach-Object {$_.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value})
  if($allowed -notcontains $expectedServiceSid){Halt 'SERVICE_SID_MISSING_IN_DACL'}
  foreach($ace in @($acl.Access)){
   try {$aceSid=$ace.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value}
   catch {Halt 'DACL_SID_TRANSLATION_FAILED'}
   if($aceSid -eq $expectedWorkerSid -and $ace.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow){
    $forbidden=[Security.AccessControl.FileSystemRights]::Write -bor [Security.AccessControl.FileSystemRights]::Delete -bor [Security.AccessControl.FileSystemRights]::DeleteSubdirectoriesAndFiles -bor [Security.AccessControl.FileSystemRights]::ChangePermissions -bor [Security.AccessControl.FileSystemRights]::TakeOwnership
    if(($ace.FileSystemRights -band $forbidden) -ne 0){Halt 'WORKER_HAS_WRITE_ON_STAGE_OR_EVIDENCE'}
   }
  }
 }
 Set-Gate 'DIRECTORY_DACL_STATIC' 'PASS_READBACK_ONLY' 'Protected DACL with service SID; worker denied-open not attested'
 if($null -ne (Get-Service -Name $svc -ErrorAction SilentlyContinue)){Halt 'SCM_SERVICE_EXISTS_NO_RECREATE'}
 $query=@(& sc.exe query $svc 2>&1)
 $receipt['sc_query_exit']=$LASTEXITCODE
 if($LASTEXITCODE -ne 1060){Halt 'SCM_NOT_EXPECTED_ABSENT_1060'}
 Set-Gate 'SCM_ABSENT_1060' 'PASS' 'Service currently absent'
 $sidText=@(& sc.exe showsid $svc 2>&1) -join [Environment]::NewLine
 if($LASTEXITCODE -ne 0 -or -not $sidText.Contains($expectedServiceSid)){Halt 'SC_SHOWSID_MISMATCH'}
 Set-Gate 'DERIVED_SERVICE_SID' 'PASS' 'SCM service SID matches existing protected DACL'
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Halt 'GH_CLI_NOT_AVAILABLE'}
 & gh auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Halt 'GH_AUTH_REQUIRED'}
 if(-not $Apply){
  Set-Gate 'EXECUTION' 'NOT_EXECUTED' 'Use elevated -Apply once, after source review'
  $receipt.verdict='PREFLIGHT_ONLY'
 }else {
  $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  if(-not $admin){Halt 'ADMIN_REQUIRED'}
  # MUST pass option name and value as distinct argv elements to sc.exe.
  $arguments=@('create',$svc,'binPath=',('"'+$exe+'"'),'start=','demand','obj=','NT AUTHORITY\LocalService','type=','own')
  $out=@(& sc.exe @arguments 2>&1)
  $receipt.sc_create_exit=$LASTEXITCODE
  $receipt.sc_create_output=@($out|ForEach-Object {"$_"})
  if($LASTEXITCODE -ne 0){Halt ('SC_CREATE_FAILED_EXIT_'+$LASTEXITCODE)}
  Set-Gate 'SC_CREATE' 'PASS_CREATED' 'Corrected argv separation; independent SCM verification pending'
  $out=@(& sc.exe sidtype $svc unrestricted 2>&1)
  $receipt.sc_sidtype_exit=$LASTEXITCODE
  $receipt.sc_sidtype_output=@($out|ForEach-Object {"$_"})
  if($LASTEXITCODE -ne 0){Halt ('SC_SIDTYPE_FAILED_EXIT_'+$LASTEXITCODE)}
  Set-Gate 'SC_SIDTYPE' 'PASS_CONFIGURED' 'Unrestricted service SID enabled'
  $qc=@(& sc.exe qc $svc 2>&1)
  $receipt['sc_qc_exit']=$LASTEXITCODE
  $receipt['sc_qc_output']=@($qc|ForEach-Object {"$_"})
  if($LASTEXITCODE -ne 0){Halt 'SCM_CONFIG_READBACK_FAILED'}
  $svcState=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
  if($null -eq $svcState -or $svcState.StartName -ine 'NT AUTHORITY\LocalService' -or $svcState.StartMode -ne 'Manual' -or $svcState.PathName -notlike ('*'+$exe+'*')){
   Halt 'SCM_BINPATH_ACCOUNT_STARTMODE_MISMATCH'
  }
  Set-Gate 'SCM_CONFIG_READBACK' 'PASS_CONFIG_ONLY' 'Exact executable, LocalService and manual start; no process launched'
  $receipt.verdict='PASS_SERVICE_CREATED_NOT_STARTED_NOT_SECURITY_QUALIFIED'
 }
}catch{
 $receipt.errors+= $_.Exception.Message
 $receipt.verdict='BLOCK_OR_PARTIAL_SERVICE_RECOVERY'
 Write-Host ('TTM_SERVICE_ONLY_BLOCK='+$_.Exception.Message)
}finally{
 try {
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $receipt['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $receiptDir ($run+'.json')
  [IO.File]::WriteAllText($file,($receipt|ConvertTo-Json -Depth 15),(New-Object Text.UTF8Encoding $false))
  $sha=Sha256 $file
  Write-Host ('TTM_SERVICE_ONLY_RECEIPT='+$file)
  Write-Host ('TTM_SERVICE_ONLY_SHA256='+$sha)
  $request=Join-Path $receiptDir 'github_create.json'
  $path='artifacts/qa/p01/'+$run+'.json'
  $body=@{branch=$branch;message=('evidence(p01): one-shot SC service recovery '+$run);
    content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$body,(New-Object Text.UTF8Encoding $false))
  $upload=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$path) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_EVIDENCE_UPLOAD_FAILED'}
  $created=($upload -join [Environment]::NewLine)|ConvertFrom-Json
  $response=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$created.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_EVIDENCE_READBACK_FAILED'}
  $read=($response -join [Environment]::NewLine)|ConvertFrom-Json
  $hasher=[Security.Cryptography.SHA256]::Create()
  try{$backSha=([BitConverter]::ToString($hasher.ComputeHash([Convert]::FromBase64String(($read.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally{$hasher.Dispose()}
  if($backSha -cne $sha){Halt 'GITHUB_EVIDENCE_SHA256_MISMATCH'}
  Write-Host ('TTM_SERVICE_ONLY_GITHUB_COMMIT='+$created.commit.sha)
  Write-Host 'TTM_SERVICE_ONLY_GITHUB_READBACK=PASS'
  $exitCode=if($receipt.verdict -eq 'PASS_SERVICE_CREATED_NOT_STARTED_NOT_SECURITY_QUALIFIED'){0}else{3}
 } catch {
  Write-Host ('TTM_SERVICE_ONLY_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exitCode=5
 }
}
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exitCode
