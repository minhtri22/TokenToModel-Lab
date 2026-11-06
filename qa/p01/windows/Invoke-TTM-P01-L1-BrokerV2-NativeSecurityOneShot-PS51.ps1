#requires -Version 5.1
# TTM P01 L1: DESIGN-ONLY candidate. Native dispatch is blocked until V3 client probe lock.
# No SCM config, account, ACL, ledger writes, F0, W01-W12, or grouped QA.
[CmdletBinding()] param([switch]$Execute)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo='D:\WORK\RESEARCH\TokenToModel-Lab'
$worktree=Join-Path $repo 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $repo 'worktrees\_ttm_p01_l1_service_provision_20261106'
$bin=Join-Path $stage 'broker_service'
$exe=Join-Path $bin 'TTMP01Broker.attestationV2.exe'
$probeDll=Join-Path $bin 'TTMWorkerNativeProbeV2.dll'
$credentialFile=Join-Path $bin 'worker_credential.dpapi.xml'
$ledgerFile=Join-Path $stage 'evidence\broker_ledger.sqlite3'
$cfgFile=Join-Path $bin 'broker_sids.txt'
$serviceName='TTMP01Broker'
$workerName='TTMP01Worker'
$pipe='\\.\pipe\TTM_P01_L1_BROKER_V1'
$serviceSid='S-1-5-80-3250491234-3884958938-4011397885-464722667-3405458206'
$workerSid='S-1-5-21-2910051730-1322758338-3406810807-1009'
$base='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$exeSha='a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a'
$probeSha='ea44cc5fca81e7f1e692726502dea0ad97ab543bc86f2abef52a25e1ffa96eb6'
$inspectorBlob='f871fed9f0bcd5a35ed3663a91a0756c13464980'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$marker=Join-Path $stage 'L1_BROKER_V2_NATIVE_SECURITY_ATTEMPT_20261106.lock'
$id='L1_BROKER_V2_NATIVE_SECURITY_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $repo ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$receipt=[ordered]@{
 schema='ttm.p01.l1.broker_v2_native_security_one_shot.v1'
 run_id=$id
 original_head=$base
 switch_receipt_commit='98f96dfd002fde146b0922501510b3229ad63bc9'
 mode=$(if($Execute){'EXECUTE_ONCE'}else{'READONLY_PREFLIGHT'})
 checks=[ordered]@{}
 process_id=$null
 broker_exe_sha256=$exeSha
 worker_probe_dll_sha256=$probeSha
 service_started=$false
 service_final_state='NOT_STARTED'
 native_dacl_inspector=@{}
 worker_probe_result='NOT_EXECUTED'
 verdict='BLOCK'
 errors=@()
 W01_W12='NOT_EXECUTED'
 L1_grouped_QA='NOT_AUTHORIZED'
}
$startAttempted=$false
$startedByThisRun=$false
function Gate([string]$name,[string]$value,[string]$detail){
 $receipt.checks[$name]=[ordered]@{status=$value;detail=$detail}
 Write-Host ('TTM_NATIVE_V2_'+$name+'='+$value)
}
function Block([string]$reason){throw [InvalidOperationException]::new($reason)}
function Sha256([string]$path){return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function ReadGit([string[]]$GitArguments){
 $out=@(& git.exe -C $worktree @GitArguments 2>&1)
 if($LASTEXITCODE -ne 0){Block 'LOCAL_GIT_COMMAND_FAILED'}
 return (($out -join [Environment]::NewLine).Trim())
}
function NoReparse([string]$path){
 $p=$path
 while($p -and (Test-Path -LiteralPath $p)){
  $item=Get-Item -LiteralPath $p -Force
  if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Block 'REPARSE_BOUNDARY'}
  $parent=Split-Path -Parent $p
  if($parent -eq $p){break}
  $p=$parent
 }
}
function NormalizeImage([string]$path){return $path.Trim().Trim([char]34).Trim()}
function FetchExactSource([string]$path,[string]$ref,[string]$blob){
 $uri='repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$ref
 $out=@(& gh api $uri 2>&1)
 if($LASTEXITCODE -ne 0){Block 'SOURCE_FETCH_ERROR'}
 $obj=($out -join [Environment]::NewLine)|ConvertFrom-Json
 if($obj.sha -cne $blob){Block 'INSPECTOR_SOURCE_GIT_BLOB_MISMATCH'}
 return ,([Convert]::FromBase64String(($obj.content -replace '\s','')))
}
try{
 $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin){Block 'ADMIN_REQUIRED_BEFORE_STAGE_ACCESS'}
 Gate 'ADMIN_ELEVATED' 'PASS' 'Elevated Windows Administrator token'
 foreach($p in @($worktree,$stage,$bin,$exe,$probeDll,$credentialFile,$cfgFile,$ledgerFile,$marker)){NoReparse $p}
 if((ReadGit -GitArguments @('rev-parse','HEAD')) -cne $base){Block 'ORIGINAL_HEAD_CHANGED'}
 if((ReadGit -GitArguments @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Block 'ORIGINAL_BRANCH_CHANGED'}
 if((ReadGit -GitArguments @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Block 'ORIGIN_CHANGED'}
 Gate 'PINNED_ORIGINAL' 'PASS' 'No original worktree mutation'
 if((Sha256 $exe) -cne $exeSha -or (Sha256 $probeDll) -cne $probeSha){Block 'V2_BINARY_SHA256_MISMATCH'}
 Gate 'BINARY_PINS' 'PASS' 'V2 EXE and worker DLL verified'
 $user=Get-LocalUser -Name $workerName -ErrorAction Stop
 if($null -eq $user -or $user.SID.Value -cne $workerSid -or -not $user.Enabled){Block 'WORKER_SID_OR_STATUS_MISMATCH'}
 $sidLines=@([IO.File]::ReadAllLines($cfgFile))
 if($sidLines.Length -ne 2 -or $sidLines[0] -cne ('service='+$serviceSid) -or $sidLines[1] -cne ('worker='+$workerSid)){Block 'SID_CONFIG_MISMATCH'}
 foreach($path in @($credentialFile,$ledgerFile)){
  if(-not(Test-Path -LiteralPath $path -PathType Leaf)){Block 'CREDENTIAL_OR_LEDGER_MISSING'}
 }
 Gate 'WORKER_AND_CONFIG' 'PASS_PRESENCE_ONLY' 'Pinned worker SID and config, credential/ledger present'
 $svc=Get-Service -Name $serviceName -ErrorAction Stop
 if($svc.Status -ne 'Stopped'){Block 'SERVICE_MUST_BE_STOPPED_BEFORE_ONE_SHOT'}
 $cim=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $cim -or (NormalizeImage $cim.PathName) -ine $exe -or
    $cim.StartName -ine 'NT AUTHORITY\LocalService' -or $cim.StartMode -ne 'Manual' -or $cim.State -ne 'Stopped'){
   Block 'SCM_V2_IDENTITY_OR_STATE_MISMATCH'
 }
 $sType=@(& sc.exe qsidtype $serviceName 2>&1) -join [Environment]::NewLine
 if($LASTEXITCODE -ne 0 -or $sType -notmatch 'UNRESTRICTED'){Block 'SERVICE_SIDTYPE_MISMATCH'}
 $sSid=@(& sc.exe showsid $serviceName 2>&1) -join [Environment]::NewLine
 if($LASTEXITCODE -ne 0 -or -not $sSid.Contains($serviceSid)){Block 'SERVICE_SID_DERIVATION_MISMATCH'}
 Gate 'SCM_V2_STOPPED' 'PASS' 'V2 exact binPath, LocalService, manual, unrestricted SID'
 # Explicit no-replay status. Existence query alone is insufficient if ACL denies.
 Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TtmP01NativeMarkerRead {
 [DllImport("kernel32.dll",CharSet=CharSet.Unicode,EntryPoint="GetFileAttributesW",ExactSpelling=true,SetLastError=true)]
 public static extern UInt32 ReadAttributes(string filename);
}
'@ -ErrorAction Stop
 $attr=[TtmP01NativeMarkerRead]::ReadAttributes($marker)
 if($attr -ne [UInt32]::MaxValue){Block 'NATIVE_SECURITY_ALREADY_ATTEMPTED_NO_REPLAY'}
 $err=[Runtime.InteropServices.Marshal]::GetLastWin32Error()
 if($err -ne 2){Block ('NATIVE_MARKER_ABSENCE_NOT_PROVEN_WIN32_'+$err)}
 Gate 'ONE_SHOT_MARKER_ABSENT' 'PASS_WIN32_2' 'Exact marker absent; no write done'
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Block 'GH_CLI_REQUIRED'}
 & gh auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Block 'GH_AUTH_REQUIRED'}
 Gate 'GITHUB_AUTH' 'PASS' 'Ready for receipt upload and readback'
 $python=Join-Path $env:USERPROFILE 'miniforge3\python.exe'
 if(-not(Test-Path -LiteralPath $python -PathType Leaf)){Block 'MINIFORGE_PYTHON_MISSING'}
 if($Execute){Block 'V3_EXPLICIT_PIPE_RIGHTS_CLIENT_PROBE_REQUIRED_BEFORE_NATIVE_DISPATCH'}
 if(-not $Execute){
  Gate 'NATIVE_EXECUTION' 'NOT_EXECUTED' 'Pass -Execute only in separately authorized one-shot'
  $receipt.verdict='PREFLIGHT_PASS_NO_SERVICE_START'
 } else {
  # Source fetched and pinned BEFORE service launch.
  $inspectorBytes=FetchExactSource 'qa/p01/inspect_pipe_dacl_win32_v1.py' '674408484e3310c9f6ba0802730783ead0eb8c97' $inspectorBlob
  New-Item -ItemType Directory -Path $receiptDir -Force | Out-Null
  $inspectorFile=Join-Path $receiptDir 'inspect_pipe_dacl_win32_v1.py'
  if(Test-Path -LiteralPath $inspectorFile){Block 'INSPECTOR_PATH_COLLISION'}
  [IO.File]::WriteAllBytes($inspectorFile,$inspectorBytes)
  # This credential is read only by the same user-scoped DPAPI context that created it.
  $cred=Import-Clixml -LiteralPath $credentialFile
  if($null -eq $cred -or $cred -isnot [System.Management.Automation.PSCredential]){Block 'DPAPI_CREDENTIAL_IMPORT_FAILED'}
  if($cred.UserName -ine ($env:COMPUTERNAME+'\'+$workerName)){Block 'DPAPI_CREDENTIAL_WORKER_IDENTITY_MISMATCH'}
  Gate 'DPAPI_CREDENTIAL' 'PASS_LOCAL_ONLY' 'Identity verified; password never logged or uploaded'
  # Compile in-memory token inspection helper; no service config change.
  Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Security.Principal;
public static class TtmP01ServiceTokenRead {
 [DllImport("kernel32.dll",SetLastError=true)] static extern IntPtr OpenProcess(uint desiredAccess,bool inherit,int processId);
 [DllImport("advapi32.dll",SetLastError=true)] static extern bool OpenProcessToken(IntPtr process,uint desiredAccess,out IntPtr token);
 [DllImport("kernel32.dll",SetLastError=true)] static extern bool CloseHandle(IntPtr handle);
 public static string Inspect(int pid,string sid){
  IntPtr process=OpenProcess(0x1000u,false,pid);
  if(process==IntPtr.Zero)return "BLOCK_PROCESS_OPEN_"+Marshal.GetLastWin32Error().ToString();
  try{
   IntPtr token=IntPtr.Zero;
   if(!OpenProcessToken(process,0x8u,out token))return "BLOCK_TOKEN_OPEN_"+Marshal.GetLastWin32Error().ToString();
   try{
    using(var identity=new WindowsIdentity(token)){
     if(identity.User==null || identity.User.Value!="S-1-5-19")return "BLOCK_NOT_LOCAL_SERVICE";
     bool matched=false;
     foreach(IdentityReference group in identity.Groups){
      if(group.Translate(typeof(SecurityIdentifier)).Value==sid){matched=true;break;}
     }
     return matched?"PASS_LOCALSERVICE_AND_SERVICE_SID_GROUP":"BLOCK_SERVICE_SID_NOT_IN_TOKEN_GROUPS";
    }
   }finally{CloseHandle(token);}
  }finally{CloseHandle(process);}
 }
}
'@ -ErrorAction Stop
  # Durable one-shot marker before service start; never delete or reset after any outcome.
  $mark=([Text.Encoding]::UTF8).GetBytes(('run='+$id+[Environment]::NewLine+'exe_sha256='+$exeSha+[Environment]::NewLine))
  $fs=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  try{$fs.Write($mark,0,$mark.Length);$fs.Flush()}
  finally{$fs.Dispose()}
  $receipt['native_attempt_marker_sha256']=Sha256 $marker
  Gate 'ONE_SHOT_MARKER' 'PASS_CREATED' 'Durable one-time marker; future attempts blocked'
  $startAttempted=$true
  try{
   Start-Service -Name $serviceName -ErrorAction Stop
   $startedByThisRun=$true
  }catch{
   Gate 'SERVICE_START' 'BLOCK' $_.Exception.GetType().Name
   Block 'SERVICE_START_FAILED'
  }
  Start-Sleep -Milliseconds 1000
  $live=Get-Service -Name $serviceName -ErrorAction Stop
  $liveCim=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
  if($live.Status -ne 'Running' -or $liveCim.State -ne 'Running' -or $liveCim.ProcessId -le 0){Block 'SERVICE_DID_NOT_STAY_RUNNING'}
  $receipt.process_id=[int]$liveCim.ProcessId
  $receipt.service_started=$true
  Gate 'SERVICE_START' 'PASS_SCM_RUNNING' 'Service running under SCM; SID token independently checked next'
  $tokenState=[TtmP01ServiceTokenRead]::Inspect([int]$liveCim.ProcessId,$serviceSid)
  if($tokenState -ne 'PASS_LOCALSERVICE_AND_SERVICE_SID_GROUP'){Gate 'SERVICE_TOKEN' 'BLOCK' $tokenState;Block 'SERVICE_TOKEN_ATTESTATION_FAILED'}
  Gate 'SERVICE_TOKEN' 'PASS' 'Actual process token has LocalService user SID and service SID group'
  # Pipe DACL readback is independent of worker communication and must pass first.
  $inspectorOut=@(& $python -B $inspectorFile --pipe $pipe --service-sid $serviceSid --worker-sid $workerSid 2>&1)
  $inspectorExit=$LASTEXITCODE
  $inspectorObj=$null
  try{$inspectorObj=($inspectorOut -join [Environment]::NewLine)|ConvertFrom-Json}catch{}
  if($null -eq $inspectorObj){Gate 'PIPE_DACL_NATIVE' 'BLOCK' ('JSON_UNREADABLE_EXIT_'+$inspectorExit);Block 'PIPE_DACL_INSPECTOR_UNREADABLE'}
  $inspectorSddlHash=$null
  $inspectorWinError=$null
  if($null -ne $inspectorObj.PSObject.Properties['sddl_sha256']) {
    $inspectorSddlHash=[string]$inspectorObj.sddl_sha256
  }
  if($null -ne $inspectorObj.PSObject.Properties['winerror']) {
    $inspectorWinError=$inspectorObj.winerror
  }
  $receipt.native_dacl_inspector=[ordered]@{
    verdict=$inspectorObj.verdict
    reason=$inspectorObj.reason
    sddl_sha256=$inspectorSddlHash
    winerror=$inspectorWinError
  }
  if($inspectorExit -ne 0 -or $inspectorObj.verdict -ne 'PASS_DACL_READBACK_ONLY'){
   Gate 'PIPE_DACL_NATIVE' 'BLOCK' ([string]$inspectorObj.reason)
   Block 'PIPE_DACL_INSPECTOR_FAILED'
  }
  Gate 'PIPE_DACL_NATIVE' 'PASS_READBACK_ONLY' 'Explicit expected service and worker SIDs; no broad allow ACEs'
  # Native worker probe impersonates its logon token and requests prohibited rights
  # independently. It never writes to evidence/ledger; no payload operation is supported.
  [Reflection.Assembly]::LoadFrom($probeDll)|Out-Null
  $secret=$cred.GetNetworkCredential().Password
  try{
   $probeResult=[TTMWorkerNativeProbe]::Run($workerName,$env:COMPUTERNAME,$secret,(Join-Path $stage 'evidence'),'TTM_P01_L1_BROKER_V1')
  }finally{$secret=$null;$cred=$null}
  $receipt.worker_probe_result=$probeResult
  if($probeResult -ne 'PASS_WORKER_SEPARATE_RIGHTS_LEDGER_DENIED_AND_PEER_AUTH_NO_WRITE'){
   Gate 'WORKER_TOKEN_AND_PEER' 'BLOCK' $probeResult
   Block 'WORKER_TOKEN_AND_PEER_PROBE_FAILED'
  }
  Gate 'WORKER_TOKEN_AND_PEER' 'PASS_NARROW_NATIVE_SCOPE' 'Denied opens for separate rights/ledger and successful worker SID pipe handshake'
  $receipt.verdict='PASS_NATIVE_V2_ATTESTATION_SCOPE_ONLY_W01_W12_NOT_AUTHORIZED'
 }
}catch{
 $receipt.errors+= $_.Exception.Message
 $receipt.verdict='BLOCK_OR_PARTIAL_NATIVE_V2_TEST'
 Write-Host ('TTM_NATIVE_V2_BLOCK='+$_.Exception.Message)
}finally{
 # Stop only if start was attempted. Do not stop a pre-existing service.
 if($startAttempted){
  try{
   $state=Get-Service -Name $serviceName -ErrorAction Stop
   if($state.Status -ne 'Stopped'){
    Stop-Service -Name $serviceName -ErrorAction Stop
    $state.WaitForStatus([System.ServiceProcess.ServiceControllerStatus]::Stopped,[TimeSpan]::FromSeconds(12))
   }
   $finalState=(Get-Service -Name $serviceName -ErrorAction Stop).Status.ToString()
   $receipt.service_final_state=$finalState
   if($finalState -ne 'Stopped'){Block 'SERVICE_STOP_NOT_VERIFIED'}
   Gate 'SERVICE_STOP' 'PASS' 'SCM service stopped after this native one-shot'
  }catch{
   Gate 'SERVICE_STOP' 'BLOCK' $_.Exception.GetType().Name
   $receipt.service_final_state='UNVERIFIED'
   $receipt.verdict='STOP_UNVERIFIED_MANUAL_INTERVENTION_REQUIRED'
  }
 }
 try{
  New-Item -ItemType Directory -Path $receiptDir -Force |Out-Null
  $receipt['utc']=[DateTime]::UtcNow.ToString('o')
  $json=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($json,($receipt|ConvertTo-Json -Depth 15),(New-Object Text.UTF8Encoding $false))
  $sha=Sha256 $json
  Write-Host ('TTM_NATIVE_V2_RECEIPT='+$json)
  Write-Host ('TTM_NATIVE_V2_SHA256='+$sha)
  $ghPath='artifacts/qa/p01/'+$id+'.json'
  $req=Join-Path $receiptDir 'github_create.json'
  $body=@{branch=$branch;message=('evidence(p01): V2 native service and access QA '+$id);content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($json))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($req,$body,(New-Object Text.UTF8Encoding $false))
  $up=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$ghPath) --input $req 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_CREATE_EVIDENCE_FAILED'}
  $created=($up -join [Environment]::NewLine)|ConvertFrom-Json
  $read=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$ghPath+'?ref='+$created.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_EVIDENCE_READBACK_FAILED'}
  $obj=($read -join [Environment]::NewLine)|ConvertFrom-Json
  $hash=[Security.Cryptography.SHA256]::Create()
  try{$compare=([BitConverter]::ToString($hash.ComputeHash([Convert]::FromBase64String(($obj.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally{$hash.Dispose()}
  if($compare -cne $sha){Block 'GITHUB_EVIDENCE_SHA256_MISMATCH'}
  Write-Host ('TTM_NATIVE_V2_GITHUB_COMMIT='+$created.commit.sha)
  Write-Host 'TTM_NATIVE_V2_GITHUB_READBACK=PASS'
  $exitCode=if($receipt.verdict -eq 'PASS_NATIVE_V2_ATTESTATION_SCOPE_ONLY_W01_W12_NOT_AUTHORIZED'){0}else{3}
 }catch{
  Write-Host ('TTM_NATIVE_V2_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exitCode=5
 }
}
Write-Host 'TTM_W01_W12_NATIVE=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exitCode
