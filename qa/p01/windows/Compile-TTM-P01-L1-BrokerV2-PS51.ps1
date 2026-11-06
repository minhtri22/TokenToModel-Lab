#requires -Version 5.1
# TTM P01 L1: compile V2 service/probe, no SCM/account/ACL/token mutation.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106\broker_service'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$head='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$oldExeHash='56a780db6aa61fdd556540da340a3be223df2e41e1a7295bb33d05628dbf87ef'
$oldSrcHash='8916fe262bf27d9176a648dd625b5fbb602f87a2cf69967fe9339def6d3561e4'
$serverCommit='37ec4d70f89161a7202298bbdc92117e075ea5be'
$serverBlob='49b2aa5e7ce36657bfd001bfffc9019988588538'
$probeCommit='b784f5b0c6d68cb7599e2adad6551af0e73782b1'
$probeBlob='0e089a5a52c1c36f5ffa4813d30c55617ad379aa'
$run='L1_BROKER_V2_COMPILE_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$evidenceDir=Join-Path $root ('worktrees\_ttm_p01_l1_qa_receipts\'+$run)
$serverFile=Join-Path $stage 'BrokerAttestationServiceV2.cs'
$serverExe=Join-Path $stage 'TTMP01Broker.attestationV2.exe'
$probeFile=Join-Path $stage 'TTMWorkerNativeProbeV2.cs'
$probeDll=Join-Path $stage 'TTMWorkerNativeProbeV2.dll'
$rec=[ordered]@{schema='ttm.p01.l1.broker_v2_compile_gate.v1';run_id=$run;
 original_head=$head;source_refs=[ordered]@{server=$serverCommit;probe=$probeCommit};
 checks=[ordered]@{};compiler=[ordered]@{};verdict='BLOCK';
 SCM_service_changed=$false;worker_account_changed=$false;ACL_changed=$false;
 W01_W12='NOT_EXECUTED';L1_grouped_QA='NOT_AUTHORIZED';errors=@()}
function Gate([string]$name,[string]$status,[string]$detail){
 $rec.checks[$name]=[ordered]@{status=$status;detail=$detail}
 Write-Host ('TTM_V2_'+$name+'='+$status)
}
function Halt([string]$why){throw [InvalidOperationException]::new($why)}
function Digest([string]$path){return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function GitRead([string[]]$GitArguments){
 $lines=@(& git.exe -C $wt @GitArguments 2>&1)
 if($LASTEXITCODE -ne 0){Halt 'GIT_IDENTITY_COMMAND_FAILED'}
 return (($lines -join [Environment]::NewLine).Trim())
}
function AssertPath([string]$path){
 $p=$path
 while($p -and (Test-Path -LiteralPath $p)){
  if(((Get-Item -LiteralPath $p -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Halt 'REPARSE_BOUNDARY'}
  $parent=Split-Path -Parent $p
  if($parent -eq $p){break}
  $p=$parent
 }
}
function PinnedBytes([string]$path,[string]$commit,[string]$blob){
 $api='repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$commit
 $lines=@(& gh api $api 2>&1)
 if($LASTEXITCODE -ne 0){Halt 'GITHUB_SOURCE_FETCH_FAILED'}
 $obj=($lines -join [Environment]::NewLine)|ConvertFrom-Json
 if($obj.sha -cne $blob){Halt 'PINNED_GIT_BLOB_MISMATCH'}
 return ,([Convert]::FromBase64String(($obj.content -replace '\s','')))
}
try {
 if(-not(Test-Path -LiteralPath $stage -PathType Container)){Halt 'PREEXISTING_STAGE_ABSENT'}
 foreach($p in @($wt,$stage,$serverFile,$serverExe,$probeFile,$probeDll)){AssertPath $p}
 if((GitRead -GitArguments @('rev-parse','HEAD')) -cne $head){Halt 'HEAD_MISMATCH'}
 if((GitRead -GitArguments @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Halt 'BRANCH_MISMATCH'}
 if((GitRead -GitArguments @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Halt 'ORIGIN_MISMATCH'}
 Gate 'ORIGINAL_HEAD' 'PASS' 'Original local worktree read-only'
 if((Digest (Join-Path $stage 'TTMP01Broker.fixed.exe')) -cne $oldExeHash){Halt 'ORIGINAL_BINARY_CHANGED'}
 if((Digest (Join-Path $stage 'BrokerAttestationService.fixed.cs')) -cne $oldSrcHash){Halt 'ORIGINAL_CSHARP_CHANGED'}
 Gate 'ORIGINAL_V1_PINS' 'PASS' 'No original service source or binary change'
 $service=Get-Service -Name 'TTMP01Broker' -ErrorAction SilentlyContinue
 if($null -eq $service){Halt 'INSTALLED_SERVICE_ABSENT'}
 if($service.Status -ne 'Stopped'){Halt 'SERVICE_MUST_BE_STOPPED'}
 $cfg=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $cfg -or $cfg.StartName -ine 'NT AUTHORITY\LocalService' -or
    $cfg.StartMode -ne 'Manual' -or $cfg.PathName -notlike '*TTMP01Broker.fixed.exe*'){
  Halt 'SERVICE_CONFIG_UNEXPECTED'
 }
 Gate 'INSTALLED_SERVICE_STOPPED' 'PASS' 'SCM configuration remains pointing to V1; not modified'
 $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin){Halt 'ADMIN_REQUIRED_FOR_PROTECTED_STAGE_FILES'}
 $csc=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
 if(-not(Test-Path -LiteralPath $csc -PathType Leaf)){Halt 'CSC_MISSING'}
 foreach($f in @($serverFile,$serverExe,$probeFile,$probeDll)){if(Test-Path -LiteralPath $f){Halt 'V2_FILE_ALREADY_EXISTS_NO_OVERWRITE'}}
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Halt 'GH_REQUIRED'}
 & gh auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Halt 'GH_AUTH_FAILED'}
 $serverBytes=PinnedBytes 'runtime/p01/windows/BrokerAttestationServiceV2.cs' $serverCommit $serverBlob
 $probeBytes=PinnedBytes 'qa/p01/windows/TTMWorkerNativeProbeV2.cs' $probeCommit $probeBlob
 $serverText=[Text.Encoding]::UTF8.GetString($serverBytes)
 $probeText=[Text.Encoding]::UTF8.GetString($probeBytes)
 if($serverText.IndexOf('int n = pipe.Read(') -lt 0 -or $serverText.IndexOf('pipe.RunAsClient(') -lt $serverText.IndexOf('int n = pipe.Read(')){Halt 'BROKER_V2_READ_BEFORE_IMPERSONATION_NOT_PROVEN'}
 if($probeText.IndexOf('foreach(uint right in forbiddenRights)') -lt 0 -or $probeText.IndexOf('BLOCK_WORKER_CAN_WRITE_LEDGER') -lt 0){Halt 'WORKER_PROBE_V2_NEGATIVE_RIGHTS_NOT_PROVEN'}
 Gate 'V2_SOURCE_PINS' 'PASS' 'Exact GitHub blobs, read-before-impersonate and separate rights checks'
 [IO.File]::WriteAllBytes($serverFile,$serverBytes)
 [IO.File]::WriteAllBytes($probeFile,$probeBytes)
 $out=@(& $csc '/nologo' '/target:exe' ('/out:'+$serverExe) '/reference:System.dll' '/reference:System.Core.dll' '/reference:System.ServiceProcess.dll' $serverFile 2>&1)
 $code=$LASTEXITCODE
 $rec.compiler['server']=[ordered]@{exit=$code;output=@($out|ForEach-Object {"$_"})}
 if($code -ne 0 -or -not(Test-Path -LiteralPath $serverExe -PathType Leaf)){Gate 'BROKER_V2_WINDOWS_CSC' 'FAIL' ('exit='+$code);Halt 'BROKER_V2_COMPILE_FAILED'}
 Gate 'BROKER_V2_WINDOWS_CSC' 'PASS' 'Exact V2 source compiled on Windows'
 $out=@(& $csc '/nologo' '/target:library' ('/out:'+$probeDll) '/reference:System.dll' '/reference:System.Core.dll' $probeFile 2>&1)
 $code=$LASTEXITCODE
 $rec.compiler['probe']=[ordered]@{exit=$code;output=@($out|ForEach-Object {"$_"})}
 if($code -ne 0 -or -not(Test-Path -LiteralPath $probeDll -PathType Leaf)){Gate 'WORKER_PROBE_V2_WINDOWS_CSC' 'FAIL' ('exit='+$code);Halt 'WORKER_PROBE_V2_COMPILE_FAILED'}
 Gate 'WORKER_PROBE_V2_WINDOWS_CSC' 'PASS' 'Exact V2 probe source compiled on Windows'
 $rec.artifact_sha256=[ordered]@{server_source=Digest $serverFile;server_exe=Digest $serverExe;probe_source=Digest $probeFile;probe_dll=Digest $probeDll}
 $rec.verdict='PASS_COMPILE_ONLY_V2_NOT_ACTIVATED'
} catch {
 $rec.errors+= $_.Exception.Message
 $rec.verdict='BLOCK_OR_COMPILE_FAIL'
 Write-Host ('TTM_V2_BLOCK='+$_.Exception.Message)
} finally {
 try {
  New-Item -ItemType Directory -Path $evidenceDir -Force|Out-Null
  $rec['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $evidenceDir ($run+'.json')
  [IO.File]::WriteAllText($file,($rec|ConvertTo-Json -Depth 15),(New-Object Text.UTF8Encoding $false))
  $sha=Digest $file
  Write-Host ('TTM_V2_EVIDENCE_LOCAL='+$file)
  Write-Host ('TTM_V2_EVIDENCE_SHA256='+$sha)
  $path='artifacts/qa/p01/'+$run+'.json'
  $request=Join-Path $evidenceDir 'github_request.json'
  $body=@{branch=$branch;message=('evidence(p01): broker V2 compile '+$run);content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$body,(New-Object Text.UTF8Encoding $false))
  $upload=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$path) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_EVIDENCE_UPLOAD_FAILED'}
  $obj=($upload -join [Environment]::NewLine)|ConvertFrom-Json
  $fetch=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$obj.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_EVIDENCE_READBACK_FAILED'}
  $read=($fetch -join [Environment]::NewLine)|ConvertFrom-Json
  $h=[Security.Cryptography.SHA256]::Create()
  try{$got=([BitConverter]::ToString($h.ComputeHash([Convert]::FromBase64String(($read.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally{$h.Dispose()}
  if($got -cne $sha){Halt 'GITHUB_EVIDENCE_SHA256_MISMATCH'}
  Write-Host ('TTM_V2_GITHUB_COMMIT='+$obj.commit.sha)
  Write-Host 'TTM_V2_GITHUB_READBACK=PASS'
  $exit=if($rec.verdict -eq 'PASS_COMPILE_ONLY_V2_NOT_ACTIVATED'){0}else{3}
 } catch {
  Write-Host ('TTM_V2_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exit=5
 }
}
Write-Host 'TTM_V2_SERVICE_SWITCH=NOT_EXECUTED'
Write-Host 'TTM_W01_W12_NATIVE=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exit
