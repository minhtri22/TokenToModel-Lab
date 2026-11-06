#requires -Version 5.1
# TTM P01 L1 — ONE-SHOT resume from an already verified Windows executable.
# Creates only named TTM account/service/ACL; never runs W01-W12 or grouped QA.
[CmdletBinding()]
param([switch]$Apply)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $repo 'worktrees\p01-f0-static-i0a-20261105'
$stage = Join-Path $repo 'worktrees\_ttm_p01_l1_service_provision_20261106'
$binDir = Join-Path $stage 'broker_service'
$ev = Join-Path $stage 'evidence'
$exe = Join-Path $binDir 'TTMP01Broker.fixed.exe'
$fixed = Join-Path $binDir 'BrokerAttestationService.fixed.cs'
$head = 'f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$expectedExe = '56a780db6aa61fdd556540da340a3be223df2e41e1a7295bb33d05628dbf87ef'
$expectedSource = '8916fe262bf27d9176a648dd625b5fbb602f87a2cf69967fe9339def6d3561e4'
$branch = 'audit/p01-l1-native-security-critical-fix-20261106'
$svcName = 'TTMP01Broker'
$accountName = 'TTMP01Worker'
$run = 'L1_PROVISION_RESUME_' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ') + '_' + [guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir = Join-Path $repo ('worktrees\_ttm_p01_l1_qa_receipts\' + $run)
$report = [ordered]@{schema='ttm.p01.l1.provision_resume.v1';run_id=$run;original_head=$head;branch=$branch;
  mode=$(if($Apply){'APPLY_ONCE'}else{'PREFLIGHT_ONLY'});checks=[ordered]@{};
  result='BLOCK';service_stopped='NOT_STARTED';W01_W12='NOT_EXECUTED';
  L1_grouped_QA='NOT_AUTHORIZED';F0_rerun=$false;errors=@()}
$serviceStarted = $false
function Add-Check([string]$name,[string]$status,[string]$detail) {
 $report.checks[$name]=[ordered]@{status=$status;detail=$detail}
 Write-Host ('TTM_RESUME_'+$name+'='+$status)
}
function Stop-Gate([string]$reason) {throw [InvalidOperationException]::new($reason)}
function Git-Read([string[]]$arguments) {
 $out=@(& git.exe -C $wt @arguments 2>&1)
 if($LASTEXITCODE -ne 0){Stop-Gate 'GIT_READ_FAILED'}
 return (($out -join [Environment]::NewLine).Trim())
}
function Assert-NoReparse([string]$path) {
 $p=$path
 while($p -and (Test-Path -LiteralPath $p)) {
  if(((Get-Item -LiteralPath $p -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Stop-Gate 'REPARSE_BOUNDARY'}
  $parent=Split-Path -Parent $p
  if($parent -eq $p){break}
  $p=$parent
 }
}
function Sha([string]$path) {
 return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Set-ExactDirectoryAcl([string]$path,[string]$serviceSid,[string]$workerSid,[bool]$workerRead) {
 $acl=New-Object System.Security.AccessControl.DirectorySecurity
 $acl.SetAccessRuleProtection($true,$false)
 $flags=[Security.AccessControl.InheritanceFlags]'ContainerInherit, ObjectInherit'
 $prop=[Security.AccessControl.PropagationFlags]::None
 $allow=[Security.AccessControl.AccessControlType]::Allow
 foreach($sidText in @('S-1-5-18','S-1-5-32-544',$serviceSid)) {
  $sid=New-Object Security.Principal.SecurityIdentifier($sidText)
  $rule=[Security.AccessControl.FileSystemAccessRule]::new($sid,[Security.AccessControl.FileSystemRights]::FullControl,$flags,$prop,$allow)
  $acl.AddAccessRule($rule)
 }
 if($workerRead) {
  $sid=New-Object Security.Principal.SecurityIdentifier($workerSid)
  $rule=[Security.AccessControl.FileSystemAccessRule]::new($sid,[Security.AccessControl.FileSystemRights]::ReadAndExecute,$flags,$prop,$allow)
  $acl.AddAccessRule($rule)
 }
 Set-Acl -LiteralPath $path -AclObject $acl
}
function Set-ExactFileAcl([string]$path,[string]$serviceSid) {
 $acl=New-Object Security.AccessControl.FileSecurity
 $acl.SetAccessRuleProtection($true,$false)
 foreach($sidText in @('S-1-5-18','S-1-5-32-544',$serviceSid)) {
  $sid=New-Object Security.Principal.SecurityIdentifier($sidText)
  $rule=[Security.AccessControl.FileSystemAccessRule]::new($sid,[Security.AccessControl.FileSystemRights]::FullControl,[Security.AccessControl.AccessControlType]::Allow)
  $acl.AddAccessRule($rule)
 }
 Set-Acl -LiteralPath $path -AclObject $acl
}
function Read-GH-Source([string]$path,[string]$ref,[string]$blob) {
 $uri='repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$ref
 $txt=@(& gh api $uri 2>&1)
 if($LASTEXITCODE -ne 0){Stop-Gate 'GITHUB_PINNED_SOURCE_UNAVAILABLE'}
 $obj=($txt -join [Environment]::NewLine)|ConvertFrom-Json
 if($obj.sha -cne $blob){Stop-Gate 'GITHUB_SOURCE_BLOB_MISMATCH'}
 return [Convert]::FromBase64String(($obj.content -replace '\s',''))
}
try {
 if(-not(Test-Path -LiteralPath $wt -PathType Container)){Stop-Gate 'PINNED_WORKTREE_ABSENT'}
 foreach($p in @($wt,$stage,$binDir,$fixed,$exe)){Assert-NoReparse $p}
 if((Git-Read @('rev-parse','HEAD')) -cne $head){Stop-Gate 'ORIGINAL_HEAD_MISMATCH'}
 if((Git-Read @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Stop-Gate 'ORIGINAL_BRANCH_MISMATCH'}
 if((Git-Read @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Stop-Gate 'ORIGIN_MISMATCH'}
 Add-Check 'PINNED_ORIGINAL' 'PASS' 'Read-only git identity; no checkout/commit on original'
 if(-not(Test-Path -LiteralPath $fixed -PathType Leaf) -or -not(Test-Path -LiteralPath $exe -PathType Leaf)){Stop-Gate 'COMPILE_RECOVERY_FILES_MISSING'}
 if((Sha $fixed) -cne $expectedSource -or (Sha $exe) -cne $expectedExe){Stop-Gate 'VERIFIED_EXE_SOURCE_SHA_MISMATCH'}
 Add-Check 'EXACT_VERIFIED_BINARY' 'PASS' $expectedExe
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Stop-Gate 'GH_CLI_MISSING'}
 & gh auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Stop-Gate 'GH_AUTH_MISSING'}
 Add-Check 'GITHUB_AUTH' 'PASS' 'Authenticated GitHub CLI'
 $existingService=Get-Service -Name $svcName -ErrorAction SilentlyContinue
 $existingAccount=Get-LocalUser -Name $accountName -ErrorAction SilentlyContinue
 if($existingService -or $existingAccount -or (Test-Path -LiteralPath (Join-Path $binDir 'broker_sids.txt'))){
  Stop-Gate 'PARTIAL_PROVISION_ALREADY_EXISTS_NO_AUTOMATIC_REUSE'
 }
 if(Test-Path -LiteralPath (Join-Path $binDir 'worker_credential.dpapi.xml')){Stop-Gate 'WORKER_SECRET_EXISTS'}
 if(Test-Path -LiteralPath (Join-Path $ev 'broker_ledger.sqlite3')){Stop-Gate 'LEDGER_EXISTS'}
 Add-Check 'ABSENT_SERVICE_AND_ACCOUNT' 'PASS' 'No existing service, account or credential to overwrite'
 $sidText=@(& sc.exe showsid $svcName 2>&1) -join [Environment]::NewLine
 $sidMatch=[regex]::Match($sidText,'S-1-5-80-(?:[0-9]+-){4}[0-9]+')
 if(-not $sidMatch.Success){Stop-Gate 'SC_SHOWSID_FAILED'}
 $serviceSid=$sidMatch.Value
 $report['broker_service_sid']=$serviceSid
 if(-not $Apply) {
  Add-Check 'APPLY' 'NOT_EXECUTED' 'Elevation and explicit -Apply required'
  $report.result='PREFLIGHT_PASS_ONLY'
 } else {
  $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  if(-not $admin){Stop-Gate 'ADMIN_REQUIRED'}
  # Preserve preexisting evidence directory; only its ACL is changed, never contents.
  if(-not(Test-Path -LiteralPath $ev -PathType Container)){Stop-Gate 'PREEXISTING_EVIDENCE_DIRECTORY_MISSING'}
  Assert-NoReparse $ev
  # Create non-admin worker. Password is never printed or sent to GitHub.
  $random=New-Object byte[] 32
  $rng=[Security.Cryptography.RandomNumberGenerator]::Create()
  try{$rng.GetBytes($random)}finally{$rng.Dispose()}
  $plain='TtM!'+[Convert]::ToBase64String($random).TrimEnd('=')+'9aA!'
  $secure=ConvertTo-SecureString -String $plain -AsPlainText -Force
  New-LocalUser -Name $accountName -Password $secure -AccountNeverExpires -UserMayNotChangePassword -Description 'TTM P01 L1 QA-only nonadministrator worker'|Out-Null
  $workerSid=(Get-LocalUser -Name $accountName).SID.Value
  $report['worker_sid']=$workerSid
  if(-not $workerSid.StartsWith('S-1-5-21-')){Stop-Gate 'WORKER_SID_INVALID'}
  Add-Check 'WORKER_ACCOUNT_CREATED' 'PASS_PROVISIONED' 'Dedicated nonadministrator SID'
  # Protect broker binary, secret and root by service SID; worker only read/traverse evidence.
  Set-ExactDirectoryAcl $stage $serviceSid $workerSid $false
  Set-ExactDirectoryAcl $binDir $serviceSid $workerSid $false
  Set-ExactDirectoryAcl $ev $serviceSid $workerSid $true
  Add-Check 'DIRECTORY_ACL_SET' 'PASS_CONFIGURED_ONLY' 'Independent denied-open probe required'
  $configFile=Join-Path $binDir 'broker_sids.txt'
  if(Test-Path -LiteralPath $configFile){Stop-Gate 'SID_CONFIG_COLLISION'}
  $config='service='+$serviceSid+[Environment]::NewLine+'worker='+$workerSid+[Environment]::NewLine
  [IO.File]::WriteAllText($configFile,$config,(New-Object Text.UTF8Encoding $false))
  $credFile=Join-Path $binDir 'worker_credential.dpapi.xml'
  $cred=[Management.Automation.PSCredential]::new(($env:COMPUTERNAME+'\'+$accountName),$secure)
  $cred | Export-Clixml -LiteralPath $credFile
  Set-ExactFileAcl $credFile $serviceSid
  $ledger=Join-Path $ev 'broker_ledger.sqlite3'
  $stream=[IO.File]::Open($ledger,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  $stream.Dispose()
  Set-ExactFileAcl $ledger $serviceSid
  Add-Check 'DPAPI_AND_LEDGER_ACL' 'PASS_CONFIGURED_ONLY' 'Secret local only; no secret in receipt or GitHub'
  $out=@(& sc.exe create $svcName ('binPath= "'+$exe+'"') 'start= demand' 'obj= NT AUTHORITY\LocalService' 'type= own' 2>&1)
  if($LASTEXITCODE -ne 0){Stop-Gate 'SC_CREATE_FAILED'}
  $out=@(& sc.exe sidtype $svcName unrestricted 2>&1)
  if($LASTEXITCODE -ne 0){Stop-Gate 'SC_SIDTYPE_FAILED'}
  $qc=@(& sc.exe qc $svcName 2>&1) -join [Environment]::NewLine
  if($LASTEXITCODE -ne 0 -or $qc -notmatch 'LocalService' -or $qc -notlike ('*'+$exe+'*')){Stop-Gate 'SCM_SERVICE_CONFIGURATION_MISMATCH'}
  Add-Check 'SERVICE_REGISTERED' 'PASS_CONFIGURED_ONLY' 'Manual-start LocalService; expected executable and service SID'
  try {
   Start-Service -Name $svcName -ErrorAction Stop
   Start-Sleep -Milliseconds 800
   if((Get-Service -Name $svcName).Status -ne 'Running'){Stop-Gate 'SCM_SERVICE_NOT_RUNNING'}
   $serviceStarted=$true
   Add-Check 'SERVICE_RUNNING' 'PASS_SCM_ONLY' 'Process token and pipe require separate native verification'
   $report['service_binary_sha256']=Sha $exe
  } catch {
   Add-Check 'SERVICE_RUNNING' 'BLOCK' $_.Exception.GetType().Name
  }
  if($serviceStarted) {
   try {
    # Independent worker-token impersonation + denied existing-dir write + peer SID handshake.
    $probeBytes=Read-GH-Source 'qa/p01/windows/TTMWorkerNativeProbe.cs' '92b5a5c3d7d18d46e10aecb74e8d4c6ccd33c9cd' '7fec3d8366c274f932db144648ad6b889e986c49'
    $probe=[Text.Encoding]::UTF8.GetString($probeBytes)
    Add-Type -TypeDefinition $probe -ReferencedAssemblies @('System.dll','System.Core.dll') -ErrorAction Stop
    $res=[TTMWorkerNativeProbe]::Run($accountName,$env:COMPUTERNAME,$plain,$ev,'TTM_P01_L1_BROKER_V1')
    if($res -eq 'PASS_WORKER_DENIED_WRITE_AND_PEER_AUTH_NO_WRITE'){
     Add-Check 'WORKER_DENIED_WRITE_AND_PEER' 'PASS_PROBE_SCOPE_ONLY' 'Single folder; authenticated peer response; not W01-W12'
    } else {
     Add-Check 'WORKER_DENIED_WRITE_AND_PEER' 'BLOCK' $res
    }
   } catch {
    Add-Check 'WORKER_DENIED_WRITE_AND_PEER' 'BLOCK' $_.Exception.GetType().Name
   }
   try {
    # Native readback of pipe DACL; no default-ACL fallback.
    $inspectorBytes=Read-GH-Source 'qa/p01/inspect_pipe_dacl_win32_v1.py' '674408484e3310c9f6ba0802730783ead0eb8c97' 'f871fed9f0bcd5a35ed3663a91a0756c13464980'
    $inspectorPath=Join-Path $binDir 'inspect_pipe_dacl_win32_v1.py'
    if(Test-Path -LiteralPath $inspectorPath){Stop-Gate 'INSPECTOR_COLLISION'}
    [IO.File]::WriteAllBytes($inspectorPath,$inspectorBytes)
    $python=Join-Path $env:USERPROFILE 'miniforge3\python.exe'
    if(-not(Test-Path -LiteralPath $python)){Stop-Gate 'PINNED_PYTHON_ABSENT'}
    $ret=@(& $python -B $inspectorPath --pipe '\\.\pipe\TTM_P01_L1_BROKER_V1' --service-sid $serviceSid --worker-sid $workerSid 2>&1)
    $status=$LASTEXITCODE
    if($status -eq 0){
     $obj=($ret -join [Environment]::NewLine)|ConvertFrom-Json
     if($obj.verdict -ne 'PASS_DACL_READBACK_ONLY'){Stop-Gate 'DACL_READBACK_UNEXPECTED'}
     Add-Check 'PIPE_DACL_READBACK' 'PASS_READBACK_ONLY' $obj.sddl_sha256
    }else {Add-Check 'PIPE_DACL_READBACK' 'BLOCK' ('Native inspector exit code '+$status)}
   } catch {
    Add-Check 'PIPE_DACL_READBACK' 'BLOCK' $_.Exception.GetType().Name
   }
  }
  $report.result='PARTIAL_PROVISIONED_NATIVE_REAUDIT_REQUIRED'
 }
} catch {
 $report.errors+= $_.Exception.Message
 $report.result='BLOCK_OR_PARTIAL_FAILURE'
 Write-Host ('TTM_RESUME_BLOCK='+$_.Exception.Message)
} finally {
 # Stop only a service started in this invocation, never delete service/account or evidence.
 if($serviceStarted) {
  try {
   Stop-Service -Name $svcName -ErrorAction Stop
   Add-Check 'SERVICE_STOP' 'PASS' 'Controlled service stopped'
   $report.service_stopped='PASS'
  } catch {
   Add-Check 'SERVICE_STOP' 'BLOCK' 'Manual service stop required'
   $report.service_stopped='UNVERIFIED'
   $report.result='STOP_UNVERIFIED'
  }
 }
 try {
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $report['utc']=[DateTime]::UtcNow.ToString('o')
  $report['executable_sha256']=$expectedExe
  $report['source_sha256']=$expectedSource
  $file=Join-Path $receiptDir ($run+'.json')
  [IO.File]::WriteAllText($file,($report|ConvertTo-Json -Depth 12),(New-Object Text.UTF8Encoding $false))
  $sha=Sha $file
  Write-Host ('TTM_RESUME_EVIDENCE_LOCAL='+$file)
  Write-Host ('TTM_RESUME_EVIDENCE_SHA256='+$sha)
  $dest='artifacts/qa/p01/'+$run+'.json'
  $post=Join-Path $receiptDir 'github_create.json'
  $request=@{branch=$branch;message=('evidence(p01): native provision resume '+$run);
     content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($post,$request,(New-Object Text.UTF8Encoding $false))
  $up=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$dest) --input $post 2>&1)
  if($LASTEXITCODE -ne 0){Stop-Gate 'GITHUB_UPLOAD_FAILED'}
  $obj=($up -join [Environment]::NewLine)|ConvertFrom-Json
  $back=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$dest+'?ref='+$obj.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Stop-Gate 'GITHUB_READBACK_FAILED'}
  $read=($back -join [Environment]::NewLine)|ConvertFrom-Json
  $h=[Security.Cryptography.SHA256]::Create()
  try {$got=([BitConverter]::ToString($h.ComputeHash([Convert]::FromBase64String(($read.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally {$h.Dispose()}
  if($got -cne $sha){Stop-Gate 'GITHUB_READBACK_SHA_MISMATCH'}
  Write-Host ('TTM_RESUME_GITHUB_COMMIT='+$obj.commit.sha)
  Write-Host 'TTM_RESUME_GITHUB_READBACK=PASS'
  $exit=3
 } catch {
  Write-Host ('TTM_RESUME_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exit=5
 }
}
Write-Host 'TTM_W01_W12_NATIVE=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exit
