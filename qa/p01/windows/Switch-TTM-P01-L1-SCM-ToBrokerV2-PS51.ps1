#requires -Version 5.1
# TTM P01 L1 — one-shot SCM binPath switch ONLY after Windows V2 native compile.
# No service start, token probe, ACL mutation, worker changes, W01-W12 or L1 grouped QA.
[CmdletBinding()] param([switch]$Apply)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $repo 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $repo 'worktrees\_ttm_p01_l1_service_provision_20261106'
$bin=Join-Path $stage 'broker_service'
$oldExe=Join-Path $bin 'TTMP01Broker.fixed.exe'
$newExe=Join-Path $bin 'TTMP01Broker.attestationV2.exe'
$newSource=Join-Path $bin 'BrokerAttestationServiceV2.cs'
$probeDll=Join-Path $bin 'TTMWorkerNativeProbeV2.dll'
$cfgFile=Join-Path $bin 'broker_sids.txt'
$credFile=Join-Path $bin 'worker_credential.dpapi.xml'
$ledgerFile=Join-Path $stage 'evidence\broker_ledger.sqlite3'
$svc='TTMP01Broker'
$worker='TTMP01Worker'
$oneShotMarker=Join-Path $stage 'L1_SCM_V2_SWITCH_ATTEMPT_20261106.lock'
$head='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$oldSha='56a780db6aa61fdd556540da340a3be223df2e41e1a7295bb33d05628dbf87ef'
$newSha='a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a'
$sourceSha='42ef0c0046d9b90ec0584211010341e7a04b93ea9541cb36ada66fdc2d830fae'
$probeSha='ea44cc5fca81e7f1e692726502dea0ad97ab543bc86f2abef52a25e1ffa96eb6'
$serviceSid='S-1-5-80-3250491234-3884958938-4011397885-464722667-3405458206'
$workerSid='S-1-5-21-2910051730-1322758338-3406810807-1009'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$id='L1_BROKER_V2_SCM_SWITCH_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $repo ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$receipt=[ordered]@{
 schema='ttm.p01.l1.broker_v2_scm_binary_switch.v1';run_id=$id;
 compile_receipt_commit='82ad048e899c33bfff576d12eda706d3b00aa8a4';
 original_head=$head;mode=$(if($Apply){'APPLY_ONCE'}else{'PREFLIGHT_ONLY'});
 checks=[ordered]@{};sc_config_exit=$null;sc_config_output=@();
 sc_qc_before=@();sc_qc_after=@();verdict='BLOCK';errors=@();
 scm_binpath_changed=$false;service_started=$false;
 worker_account_changed=$false;ACL_changed=$false;
 W01_W12='NOT_EXECUTED';grouped_L1='NOT_AUTHORIZED';
}
function Gate([string]$key,[string]$status,[string]$detail) {
 $receipt.checks[$key]=[ordered]@{status=$status;detail=$detail}
 Write-Host ('TTM_SWITCH_'+$key+'='+$status)
}
function Block([string]$why) {throw [InvalidOperationException]::new($why)}
function HashOf([string]$path) {
 return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function ReadGit([string[]]$GitArguments) {
 $out=@(& git.exe -C $wt @GitArguments 2>&1)
 if($LASTEXITCODE -ne 0){Block 'LOCAL_GIT_READ_FAILED'}
 return (($out -join [Environment]::NewLine).Trim())
}
function NoReparse([string]$path) {
 $p=$path
 while($p -and (Test-Path -LiteralPath $p)) {
  if(((Get-Item -LiteralPath $p -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Block 'REPARSE_BOUNDARY'}
  $parent=Split-Path -Parent $p
  if($parent -eq $p){break}
  $p=$parent
 }
}
function NormalizeBinPath([string]$path) {
 return $path.Trim().Trim([char]34).Trim()
}
try {
 if(-not(Test-Path -LiteralPath $wt -PathType Container)){Block 'WORKTREE_ABSENT'}
 foreach($p in @($wt,$stage,$bin,$oldExe,$newExe,$newSource,$probeDll,$cfgFile,$credFile,$ledgerFile,$oneShotMarker)) {NoReparse $p}
 if((ReadGit -GitArguments @('rev-parse','HEAD')) -cne $head){Block 'ORIGINAL_HEAD_CHANGED'}
 if((ReadGit -GitArguments @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Block 'ORIGINAL_BRANCH_CHANGED'}
 if((ReadGit -GitArguments @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Block 'ORIGIN_CHANGED'}
 Gate 'PINNED_ORIGINAL' 'PASS' 'Original worktree checked read-only'
 foreach($entry in @(
  @{Path=$oldExe;Expected=$oldSha},
  @{Path=$newExe;Expected=$newSha},
  @{Path=$newSource;Expected=$sourceSha},
  @{Path=$probeDll;Expected=$probeSha}
 )) {
  $path=[string]$entry.Path;$expected=[string]$entry.Expected
  if(-not(Test-Path -LiteralPath $path -PathType Leaf)){Block 'MISSING_PINNED_BINARY_OR_SOURCE'}
  if((HashOf $path) -cne $expected){Block 'BINARY_OR_SOURCE_SHA256_MISMATCH'}
 }
 Gate 'EXACT_V1_V2_SHA256' 'PASS' 'V1 EXE, V2 EXE, V2 C# source, V2 probe DLL'
 $actualWorker=Get-LocalUser -Name $worker -ErrorAction SilentlyContinue
 if($null -eq $actualWorker -or $actualWorker.SID.Value -cne $workerSid -or -not $actualWorker.Enabled){Block 'WORKER_ACCOUNT_SID_MISMATCH'}
 Gate 'WORKER_IDENTITY' 'PASS_PRESENT_NOT_TOKEN_QUALIFIED' 'No account mutation'
 foreach($path in @($cfgFile,$credFile,$ledgerFile)) {
  if(-not(Test-Path -LiteralPath $path -PathType Leaf)){Block 'EXISTING_PROVISION_FILE_MISSING'}
 }
 $sidLines=@([IO.File]::ReadAllLines($cfgFile))
 if($sidLines.Length -ne 2 -or $sidLines[0] -cne ('service='+$serviceSid) -or $sidLines[1] -cne ('worker='+$workerSid)){Block 'PINNED_SID_CONFIG_MISMATCH'}
 foreach($path in @($stage,$bin,(Join-Path $stage 'evidence'))) {
  $acl=Get-Acl -LiteralPath $path
  if(-not $acl.AreAccessRulesProtected){Block 'UNPROTECTED_STAGE_DACL'}
  $found=$false
  foreach($ace in @($acl.Access)) {
   try{$s=$ace.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value}catch{Block 'STAGE_ACE_TRANSLATION_FAILED'}
   if($s -eq $serviceSid -and $ace.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow){$found=$true}
  }
  if(-not $found){Block 'SERVICE_SID_MISSING_STAGE_DACL'}
 }
 Gate 'STAGING_SID_DACL' 'PASS_READBACK_ONLY' 'Protected ACL and service SID; no effective token claim'
 $current=Get-Service -Name $svc -ErrorAction SilentlyContinue
 if($null -eq $current){Block 'SERVICE_MISSING'}
 if($current.Status -ne 'Stopped'){Block 'SERVICE_NOT_STOPPED'}
 $wmi=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $wmi -or $wmi.Name -cne $svc){Block 'SERVICE_IDENTITY_UNEXPECTED'}
 if($wmi.StartName -ine 'NT AUTHORITY\LocalService' -or $wmi.StartMode -ne 'Manual' -or $wmi.State -ne 'Stopped'){Block 'SERVICE_ACCOUNT_STARTMODE_STATE_MISMATCH'}
 if((NormalizeBinPath $wmi.PathName) -ine $oldExe){Block 'SCM_BINPATH_NOT_EXPECTED_V1'}
 $qc=@(& sc.exe qc $svc 2>&1)
 if($LASTEXITCODE -ne 0){Block 'SC_QC_BEFORE_FAILED'}
 $receipt.sc_qc_before=@($qc|ForEach-Object {"$_"})
 $sidOutput=@(& sc.exe showsid $svc 2>&1) -join [Environment]::NewLine
 if($LASTEXITCODE -ne 0 -or -not $sidOutput.Contains($serviceSid)){Block 'SCM_DERIVED_SERVICE_SID_MISMATCH'}
 $sidType=@(& sc.exe qsidtype $svc 2>&1) -join [Environment]::NewLine
 if($LASTEXITCODE -ne 0 -or $sidType -notmatch 'UNRESTRICTED'){Block 'SCM_SERVICE_SIDTYPE_NOT_UNRESTRICTED'}
 Gate 'SCM_V1_STOPPED' 'PASS' 'Expected V1 binPath, Manual LocalService, unrestricted service SID'
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Block 'GH_CLI_MISSING'}
 & gh auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Block 'GH_AUTH_MISSING'}
 if(Test-Path -LiteralPath $oneShotMarker -PathType Leaf){Block 'SCM_V2_SWITCH_ALREADY_ATTEMPTED_NO_REPLAY'}
 if(-not $Apply) {
  Gate 'SCM_BINARY_SWITCH' 'NOT_EXECUTED' 'Explicit elevated -Apply is required'
  $receipt.verdict='READONLY_PREFLIGHT_PASS'
 } else {
  $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
  if(-not $admin){Block 'ADMIN_REQUIRED'}
  # Durable one-shot marker is created inside TTM, before the first SCM mutation.
  # A partial Windows failure must never be replayed without a separate adjudication.
  $markBytes=[Text.Encoding]::UTF8.GetBytes(('run_id='+$id+[Environment]::NewLine+
     'old_sha256='+$oldSha+[Environment]::NewLine+'new_sha256='+$newSha+[Environment]::NewLine))
  $markStream=[IO.File]::Open($oneShotMarker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  try{$markStream.Write($markBytes,0,$markBytes.Length);$markStream.Flush()}
  finally{$markStream.Dispose()}
  $receipt['one_shot_marker_sha256']=HashOf $oneShotMarker
  Gate 'ONE_SHOT_MARKER' 'PASS_CREATED' 'Non-secret marker retained on success/failure; never remove automatically'
  # Only change existing service's binPath, not StartName, StartMode, SID, ACL or account.
  $argv=@('config',$svc,'binPath=',('"'+$newExe+'"'))
  $sc=@(& sc.exe @argv 2>&1)
  $receipt.sc_config_exit=$LASTEXITCODE
  $receipt.sc_config_output=@($sc|ForEach-Object {"$_"})
  if($LASTEXITCODE -ne 0){Block ('SC_CONFIG_BINPATH_FAILED_'+$LASTEXITCODE)}
  $receipt.scm_binpath_changed=$true
  Gate 'SCM_CONFIG_COMMAND' 'PASS' 'sc config returned exit 0; independent readback required'
  $qc2=@(& sc.exe qc $svc 2>&1)
  $code=$LASTEXITCODE
  $receipt.sc_qc_after=@($qc2|ForEach-Object {"$_"})
  if($code -ne 0){Block 'SC_QC_AFTER_FAILED'}
  $after=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
  if($null -eq $after -or (NormalizeBinPath $after.PathName) -ine $newExe -or
    $after.StartName -ine 'NT AUTHORITY\LocalService' -or $after.StartMode -ne 'Manual' -or
    $after.State -ne 'Stopped'){
   Block 'SCM_V2_READBACK_MISMATCH_NO_AUTO_ROLLBACK'
  }
  if((HashOf $newExe) -cne $newSha){Block 'V2_BINARY_CHANGED_AFTER_SCM_UPDATE'}
  Gate 'SCM_V2_READBACK' 'PASS_CONFIG_ONLY' 'SCM pinned V2 executable; still STOPPED and manual'
  $receipt.verdict='PASS_SCM_SWITCH_V2_NOT_STARTED_SECURITY_NOT_QUALIFIED'
 }
} catch {
 $receipt.errors+= $_.Exception.Message
 $receipt.verdict='BLOCK_OR_PARTIAL_SCM_SWITCH'
 Write-Host ('TTM_SWITCH_BLOCK='+$_.Exception.Message)
} finally {
 try {
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $receipt['utc']=[DateTime]::UtcNow.ToString('o')
  $receipt['V2_exe_sha256']=$newSha
  $receipt['V2_probe_dll_sha256']=$probeSha
  $file=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($file,($receipt|ConvertTo-Json -Depth 15),(New-Object Text.UTF8Encoding $false))
  $sha=HashOf $file
  Write-Host ('TTM_SWITCH_RECEIPT='+$file)
  Write-Host ('TTM_SWITCH_SHA256='+$sha)
  $request=Join-Path $receiptDir 'github_create.json'
  $githubPath='artifacts/qa/p01/'+$id+'.json'
  $body=@{branch=$branch;message=('evidence(p01): V2 SCM binPath one-shot '+$id);
      content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$body,(New-Object Text.UTF8Encoding $false))
  $post=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$githubPath) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_CREATE_EVIDENCE_FAILED'}
  $saved=($post -join [Environment]::NewLine)|ConvertFrom-Json
  $reread=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$githubPath+'?ref='+$saved.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_EVIDENCE_READBACK_FAILED'}
  $download=($reread -join [Environment]::NewLine)|ConvertFrom-Json
  $h=[Security.Cryptography.SHA256]::Create()
  try{$observed=([BitConverter]::ToString($h.ComputeHash([Convert]::FromBase64String(($download.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally{$h.Dispose()}
  if($observed -cne $sha){Block 'GITHUB_EVIDENCE_SHA256_MISMATCH'}
  Write-Host ('TTM_SWITCH_GITHUB_COMMIT='+$saved.commit.sha)
  Write-Host 'TTM_SWITCH_GITHUB_READBACK=PASS'
  $exitCode=if($receipt.verdict -eq 'PASS_SCM_SWITCH_V2_NOT_STARTED_SECURITY_NOT_QUALIFIED'){0}else{3}
 } catch {
  Write-Host ('TTM_SWITCH_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exitCode=5
 }
}
Write-Host 'TTM_V2_SERVICE_START=NOT_EXECUTED'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exitCode
