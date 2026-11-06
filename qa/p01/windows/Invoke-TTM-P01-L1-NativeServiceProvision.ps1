#requires -Version 5.1
[CmdletBinding()]
param([switch]$Apply)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$repo='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $repo 'worktrees\p01-f0-static-i0a-20261105'
$head='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$service='TTMP01Broker'
$user='TTMP01Worker'
$sourceCommit='3954551912794bc0886b898b3900c87201450f72'
$blobSha='ac3d4f88974930f67549445f8e37c9809ce61516'
$id='L1_SERVICE_PROVISION_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$workspace=Join-Path $repo 'worktrees\_ttm_p01_l1_service_provision_20261106'
$receiptDir=Join-Path $repo ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$r=[ordered]@{schema='ttm.p01.l1.windows_service_provision.v1';run_id=$id;original_head=$head;branch=$branch;source_commit=$sourceCommit;apply=[bool]$Apply;checks=[ordered]@{};verdict='BLOCK';W01_W12='NOT_EXECUTED';L1_permit='NOT_GRANTED';errors=@()}
function Record([string]$key,[string]$value,[string]$note) {
 $r.checks[$key]=[ordered]@{status=$value;detail=$note}
 Write-Host ('TTM_SERVICE_GATE_'+$key+'='+$value)
}
function Block([string]$why) {throw [InvalidOperationException]::new($why)}
function G([string[]]$arglist) {
 $out=@(& git.exe -C $wt @arglist 2>&1)
 if($LASTEXITCODE -ne 0){Block 'GIT_READ_ERROR'}
 return (($out -join [Environment]::NewLine).Trim())
}
function SafePath([string]$p) {
 while($p -and (Test-Path -LiteralPath $p)) {
  if(((Get-Item -LiteralPath $p -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Block 'REPARSE_DENIED'}
  $q=Split-Path -Parent $p
  if($q -eq $p){break}
  $p=$q
 }
}
function ApplyDirectoryAcl([string]$path,[string]$sid,[string]$workerSid,[bool]$allowRead) {
 $acl=New-Object Security.AccessControl.DirectorySecurity
 $acl.SetAccessRuleProtection($true,$false)
 $aclRuleType=[Security.AccessControl.FileSystemAccessRule]
 $inherit=[Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit'
 $prop=[Security.AccessControl.PropagationFlags]::None
 $allow=[Security.AccessControl.AccessControlType]::Allow
 foreach($principal in @('S-1-5-18','S-1-5-32-544',$sid)) {
  $identity=New-Object Security.Principal.SecurityIdentifier($principal)
  $rule=New-Object Security.AccessControl.FileSystemAccessRule($identity,[Security.AccessControl.FileSystemRights]::FullControl,$inherit,$prop,$allow)
  $acl.AddAccessRule($rule)
 }
 if($allowRead) {
  $identity=New-Object Security.Principal.SecurityIdentifier($workerSid)
  $rule=New-Object Security.AccessControl.FileSystemAccessRule($identity,[Security.AccessControl.FileSystemRights]::ReadAndExecute,$inherit,$prop,$allow)
  $acl.AddAccessRule($rule)
 }
 Set-Acl -LiteralPath $path -AclObject $acl
}
$started=$false
try {
 if(-not(Test-Path -LiteralPath $wt)){Block 'PINNED_WORKTREE_ABSENT'}
 SafePath $wt
 if((G @('rev-parse','HEAD')) -cne $head){Block 'HEAD_CHANGED'}
 if((G @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Block 'BRANCH_CHANGED'}
 if((G @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Block 'WRONG_ORIGIN'}
 Record 'PINNED_WORKTREE' 'PASS' 'No checkout/fetch/pull/commit on local original'
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Block 'GH_CLI_REQUIRED'}
 & gh auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Block 'GH_NOT_AUTHENTICATED'}
 Record 'GH_AUTH' 'PASS' 'GitHub CLI can write evidence'
 if(-not $Apply) {
  Record 'PROVISION' 'NOT_EXECUTED' 'Run elevated PowerShell with -Apply to provision once'
  $r.verdict='PREFLIGHT_ONLY'
 } else {
  $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  if(-not $admin){Block 'ADMIN_REQUIRED'}
  if(Test-Path -LiteralPath $workspace){Block 'WORKSPACE_EXISTS_NO_OVERWRITE'}
  if(Get-Service -Name $service -ErrorAction SilentlyContinue){Block 'SERVICE_EXISTS_NO_OVERWRITE'}
  if(Get-LocalUser -Name $user -ErrorAction SilentlyContinue){Block 'USER_EXISTS_NO_OVERWRITE'}
  $csc=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
  if(-not(Test-Path -LiteralPath $csc)){Block 'CSHARP_COMPILER_NOT_FOUND'}
  $endpoint='repos/minhtri22/TokenToModel-Lab/contents/runtime/p01/windows/BrokerAttestationService.cs?ref='+$sourceCommit
  $raw=@(& gh api $endpoint 2>&1)
  if($LASTEXITCODE -ne 0){Block 'EXACT_SOURCE_DOWNLOAD_FAILED'}
  $obj=($raw -join [Environment]::NewLine)|ConvertFrom-Json
  if($obj.sha -cne $blobSha){Block 'EXACT_SOURCE_BLOB_MISMATCH'}
  $sourceBytes=[Convert]::FromBase64String(($obj.content -replace '\s',''))
  $bin=Join-Path $workspace 'broker_service'
  $ev=Join-Path $workspace 'evidence'
  New-Item -ItemType Directory -Path $bin,$ev -Force|Out-Null
  $src=Join-Path $bin 'BrokerAttestationService.cs'
  [IO.File]::WriteAllBytes($src,$sourceBytes)
  $exe=Join-Path $bin 'TTMP01Broker.exe'
  & $csc '/nologo' '/target:exe' ('/out:'+$exe) '/reference:System.dll' '/reference:System.Core.dll' '/reference:System.ServiceProcess.dll' $src
  if($LASTEXITCODE -ne 0 -or -not(Test-Path $exe)){Block 'SERVICE_BINARY_COMPILE_FAILED'}
  Record 'SERVICE_BINARY' 'PASS_SOURCE_BUILT' ((Get-FileHash $exe -Algorithm SHA256).Hash.ToLowerInvariant())
  $sidOutput=@(& sc.exe showsid $service 2>&1) -join [Environment]::NewLine
  $sidMatch=[regex]::Match($sidOutput,'S-1-5-80-(?:[0-9]+-){4}[0-9]+')
  if(-not $sidMatch.Success){Block 'SERVICE_SID_NOT_RESOLVED'}
  $sid=$sidMatch.Value
  $random=New-Object byte[] 32
  $rng=[Security.Cryptography.RandomNumberGenerator]::Create()
  try{$rng.GetBytes($random)}finally{$rng.Dispose()}
  $secret='TtM!'+[Convert]::ToBase64String($random).TrimEnd('=')+'9aA!'
  $secure=ConvertTo-SecureString $secret -AsPlainText -Force
  New-LocalUser -Name $user -Password $secure -AccountNeverExpires -Description 'TTM P01 QA worker - nonadministrator'|Out-Null
  $workerSid=(Get-LocalUser -Name $user).SID.Value
  if(-not $workerSid.StartsWith('S-1-5-21-')){Block 'WORKER_SID_INVALID'}
  Record 'WORKER_ACCOUNT' 'PASS_CREATED' $workerSid

  $created=@(& sc.exe create $service ('binPath= "'+$exe+'"') 'start= demand' 'obj= NT AUTHORITY\LocalService' 'type= own' 2>&1)
  if($LASTEXITCODE -ne 0){Block 'SERVICE_CREATE_FAILED'}
  $typed=@(& sc.exe sidtype $service unrestricted 2>&1)
  if($LASTEXITCODE -ne 0){Block 'SERVICE_SIDTYPE_FAILED'}
  $qc=@(& sc.exe qc $service 2>&1) -join [Environment]::NewLine
  if($qc -notmatch 'LocalService'){Block 'SERVICE_NOT_LOCAL_SERVICE'}
  Record 'SERVICE_IDENTITY' 'PASS_PROVISIONED_NOT_ATTESTED' $sid
  ApplyDirectoryAcl $bin $sid $workerSid $false
  # DPAPI-encrypted credential for later native QA; never print or upload.
  $credentialFile=Join-Path $bin 'worker_credential.dpapi.xml'
  $credential=New-Object System.Management.Automation.PSCredential(($env:COMPUTERNAME+'\'+$user),$secure)
  $credential | Export-Clixml -LiteralPath $credentialFile
  $credential=$null
  Record 'WORKER_CREDENTIAL_DPAPI' 'PASS_LOCAL_ONLY' 'Encrypted using current admin-user DPAPI; excluded from evidence uploads'
  ApplyDirectoryAcl $ev $sid $workerSid $true
  $cfg=Join-Path $bin 'broker_sids.txt'
  $config='service='+$sid+[Environment]::NewLine+'worker='+$workerSid+[Environment]::NewLine
  [IO.File]::WriteAllText($cfg,$config,(New-Object Text.UTF8Encoding $false))
  $ledger=Join-Path $ev 'broker_ledger.sqlite3'
  $stream=[IO.File]::Open($ledger,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  $stream.Dispose()
  $fileAcl=New-Object Security.AccessControl.FileSecurity
  $fileAcl.SetAccessRuleProtection($true,$false)
  foreach($principal in @('S-1-5-18','S-1-5-32-544',$sid)) {
   $identity=New-Object Security.Principal.SecurityIdentifier($principal)
   $rule=New-Object Security.AccessControl.FileSystemAccessRule($identity,[Security.AccessControl.FileSystemRights]::FullControl,[Security.AccessControl.AccessControlType]::Allow)
   $fileAcl.AddAccessRule($rule)
  }
  Set-Acl -LiteralPath $ledger -AclObject $fileAcl
  Set-Acl -LiteralPath $credentialFile -AclObject $fileAcl
  Record 'ROOT_AND_LEDGER_ACL' 'PASS_CONFIGURED_ONLY' 'ACL applied; effective worker-token negative proof still required'
  try {
   Start-Service -Name $service -ErrorAction Stop
   Start-Sleep -Milliseconds 800
   if((Get-Service $service).Status -eq 'Running') {
    $started=$true
    Record 'BROKER_PROCESS' 'PASS_SCM_RUNNING' 'SCM attestation only; IPC peer/DACL not yet qualified'
   } else {Record 'BROKER_PROCESS' 'BLOCK' 'Service exited before SCM RUNNING'}
  } catch {Record 'BROKER_PROCESS' 'BLOCK' $_.Exception.GetType().Name}
  Record 'PIPE_DACL_NATIVE' 'NOT_EXECUTED' 'Requires readback and real worker peer SID probe'
  Record 'WORKER_TOKEN_DENIED_OPEN' 'NOT_EXECUTED' 'Requires native identity impersonation negative test'
  $r.verdict='PARTIAL_PROVISIONED_NATIVE_REAUDIT_REQUIRED'
 }
} catch {
 $r.errors+= $_.Exception.Message
 $r.verdict='BLOCK_OR_PARTIAL_FAILURE'
 Write-Host ('TTM_SERVICE_PROVISION_BLOCK='+$_.Exception.Message)
} finally {
 if($started) {
  try {Stop-Service -Name $service -ErrorAction Stop;Record 'BROKER_STOPPED' 'PASS' 'Manual-start service stopped'}
  catch {Record 'BROKER_STOPPED' 'BLOCK' 'Manual stop verification required';$r.verdict='STOP_UNVERIFIED'}
 }
 try {
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $r['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($file,($r|ConvertTo-Json -Depth 10),(New-Object Text.UTF8Encoding $false))
  $sha=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
  Write-Host ('TTM_SERVICE_EVIDENCE_LOCAL='+$file)
  Write-Host ('TTM_SERVICE_EVIDENCE_SHA256='+$sha)
  $path='artifacts/qa/p01/'+$id+'.json'
  $request=Join-Path $receiptDir 'gh_request.json'
  $body=@{message=('evidence(p01): native service provisioning '+$id);branch=$branch;content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$body,(New-Object Text.UTF8Encoding $false))
  $response=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$path) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_EVIDENCE_CREATE_FAILED'}
  $created=($response -join [Environment]::NewLine)|ConvertFrom-Json
  $readback=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$created.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_EVIDENCE_READBACK_FAILED'}
  $got=($readback -join [Environment]::NewLine)|ConvertFrom-Json
  $decoded=[Convert]::FromBase64String(($got.content -replace '\s',''))
  $alg=[Security.Cryptography.SHA256]::Create()
  try {$observed=([BitConverter]::ToString($alg.ComputeHash($decoded))).Replace('-','').ToLowerInvariant()}
  finally {$alg.Dispose()}
  if($observed -cne $sha){Block 'GITHUB_EVIDENCE_SHA256_MISMATCH'}
  Write-Host ('TTM_SERVICE_EVIDENCE_GITHUB_COMMIT='+$created.commit.sha)
  Write-Host 'TTM_SERVICE_EVIDENCE_GITHUB_READBACK=PASS'
  $exitCode=3
 } catch {
  Write-Host ('TTM_SERVICE_EVIDENCE_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exitCode=5
 }
}
Write-Host 'TTM_W01_W12_NATIVE=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exitCode
