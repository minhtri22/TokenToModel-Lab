#requires -Version 5.1
# TTM P01 L1 S1: one-shot Windows independent PYTHON SOURCE QA only.
# Never compiles/executes the C# harness, touches SCM, or mutates Broker V3/Worker V4.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$original=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$receiptRoot=Join-Path $root 'worktrees\_ttm_p01_l1_qa_receipts'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$sourceCommit='ec62ed6c07fece40a06e44aa6fada778d9c8c8ce'
$originalHead='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$oldServiceExe=Join-Path $stage 'broker_service\TTMP01Broker.attestationV2.exe'
$marker=Join-Path $stage 'L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_ATTEMPT_20261107.lock'
$python=Join-Path $env:USERPROFILE 'miniforge3\python.exe'
$files=@(
  @{key='HARNESS';path='qa/p01/windows/S1/TTMS1IsolatedCancellationHarness.cs';file='TTMS1IsolatedCancellationHarness.cs';
    blob='872c67174c6fbbcea9941fe3bfa0acee3cddfb7c';sha='fd179c74fa1a136d791a5f9f6394ea657c58e7a46d1983c0eafa81051e99d6a9'},
  @{key='INDEPENDENT_QA';path='qa/p01/windows/S1/Independent-QA-S1-IsolatedCancellation-Static.py';file='Independent-QA-S1-IsolatedCancellation-Static.py';
    blob='81d78f60a2c92e29e2d4818dfdf15953487768b8';sha='78d873cba4f0078187c9126ceb4a20ecade78c40ca74ca163e02e554384c3227'}
)
$id='L1_S1_WINDOWS_INDEPENDENT_SOURCE_QA_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$dir=Join-Path $receiptRoot $id
$receiptPath=Join-Path $dir ($id+'.json')
$canWrite=$false
$githubOK=$false
$exitCode=3
$receipt=[ordered]@{
 schema='ttm.p01.l1.s1.windows_independent_source_static_qa.v1'
 run_id=$id;source_commit=$sourceCommit;original_head=$originalHead
 mode='SOURCE_ONLY_NO_NATIVE'
 checks=[ordered]@{};source_files=@();python_checker=$null
 marker_sha256=$null;scm_before=$null;scm_after=$null
 errors=@();verdict='BLOCK'
 compiler_execution='NOT_EXECUTED';s1_native_execution='NOT_EXECUTED'
 service_action='NONE';scm_mutation=$false;science_jobs='NOT_EXECUTED'
 W01_W12='NOT_EXECUTED';L1_grouped_QA='NOT_AUTHORIZED';P01='OPEN';P02='NOT_OPENED'
}
function StopGate([string]$why){throw [InvalidOperationException]::new($why)}
function Gate([string]$name,[string]$status,[string]$detail){
 $receipt.checks[$name]=[ordered]@{status=$status;detail=$detail}
 Write-Host ('TTM_S1_QA_'+$name+'='+$status)
}
function ShaBytes([byte[]]$bytes){
 $sha=[Security.Cryptography.SHA256]::Create()
 try{return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()}
 finally{$sha.Dispose()}
}
function ShaFile([string]$path){return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function RejectReparse([string]$path){
 $p=$path
 while($p){
  if(Test-Path -LiteralPath $p){
   $item=Get-Item -LiteralPath $p -Force
   if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){StopGate ('REPARSE_BOUNDARY_'+$p)}
  }
  $parent=Split-Path -Parent $p
  if([string]::IsNullOrEmpty($parent) -or $parent -eq $p){break}
  $p=$parent
 }
}
function ReadNative([string]$exe,[string[]]$argv){
 $previous=$ErrorActionPreference
 $ErrorActionPreference='Continue'
 try{
  $messages=@(& $exe @argv 2>&1)
  $nativeExit=$LASTEXITCODE
 }finally{$ErrorActionPreference=$previous}
 return [ordered]@{
  code=$nativeExit
  text=(($messages | ForEach-Object {$_.ToString()}) -join [Environment]::NewLine)
 }
}
function SnapshotSCM{
 $service=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $service){StopGate 'BROKER_SERVICE_MISSING'}
 $path=$service.PathName.Trim().Trim([char]34).Trim()
 if($service.State -ne 'Stopped' -or [int]$service.ProcessId -ne 0 -or
    $service.StartMode -ne 'Manual' -or $service.StartName -ine 'NT AUTHORITY\LocalService' -or
    $path -ine $oldServiceExe){StopGate 'BROKER_SCM_NOT_FROZEN_STOPPED_PID0'}
 return [ordered]@{name=$service.Name;state=$service.State;pid=[int]$service.ProcessId;
   start_mode=$service.StartMode;start_name=$service.StartName;image_path=$path}
}
try{
 if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){StopGate 'WINDOWS_REQUIRED'}
 $ident=[Security.Principal.WindowsIdentity]::GetCurrent()
 $admin=([Security.Principal.WindowsPrincipal]::new($ident)).IsInRole(
  [Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin){StopGate 'ADMIN_REQUIRED'}
 foreach($p in @($root,$original,$stage,$receiptRoot,$dir,$marker,$python)){RejectReparse $p}
 if(-not(Test-Path -LiteralPath $root -PathType Container) -or
    -not(Test-Path -LiteralPath $receiptRoot -PathType Container) -or
    -not(Test-Path -LiteralPath $stage -PathType Container)){StopGate 'TTM_PROJECT_WORKSPACE_MISSING'}
 $canWrite=$true
 Gate 'PROJECT_BOUNDARY' 'PASS_EXACT' $root
 $g=ReadNative 'git.exe' @('-C',$original,'rev-parse','HEAD')
 if($g.code -ne 0 -or $g.text.Trim() -cne $originalHead){StopGate 'ORIGINAL_HEAD_MISMATCH'}
 $g=ReadNative 'git.exe' @('-C',$original,'branch','--show-current')
 if($g.code -ne 0 -or $g.text.Trim() -cne 'implementation/p01-i0a-s-f0-static-20261106'){StopGate 'ORIGINAL_BRANCH_MISMATCH'}
 $g=ReadNative 'git.exe' @('-C',$original,'remote','get-url','origin')
 if($g.code -ne 0 -or $g.text.Trim() -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){StopGate 'ORIGINAL_ORIGIN_MISMATCH'}
 Gate 'FROZEN_ORIGINAL' 'PASS_EXACT' $originalHead
 $receipt.scm_before=SnapshotSCM
 Gate 'SCM_READONLY' 'PASS_STOPPED_PID0' 'Manual LocalService V2 image'
 if(-not(Test-Path -LiteralPath $python -PathType Leaf)){StopGate 'MINIFORGE_PYTHON_MISSING'}
 $pyCheck=ReadNative $python @('-B','-c','import sys;print(sys.version_info.major,sys.version_info.minor,sys.maxsize.bit_length()+1,sep=chr(124))')
 if($pyCheck.code -ne 0 -or $pyCheck.text -notmatch '^3\|1[0-9]\|64$'){StopGate 'PYTHON_64BIT_IDENTITY_MISMATCH'}
 Gate 'PYTHON_X64' 'PASS' $pyCheck.text
 $auth=ReadNative 'gh.exe' @('auth','status')
 if($auth.code -ne 0){StopGate 'GITHUB_AUTH_REQUIRED'}
 Gate 'GITHUB_AUTH' 'PASS' 'GitHub CLI authenticated'
 if(Test-Path -LiteralPath $marker){StopGate 'S1_STATIC_QA_ALREADY_ATTEMPTED_NO_REPLAY'}
 if(Test-Path -LiteralPath $dir){StopGate 'EVIDENCE_DIRECTORY_ALREADY_EXISTS'}
 New-Item -ItemType Directory -Path $dir -ErrorAction Stop | Out-Null
 foreach($item in $files){
  $uri='repos/minhtri22/TokenToModel-Lab/contents/'+$item.path+'?ref='+$sourceCommit
  $response=ReadNative 'gh.exe' @('api',$uri)
  if($response.code -ne 0){StopGate ('GITHUB_SOURCE_FETCH_FAILED_'+$item.key)}
  $entry=$response.text | ConvertFrom-Json
  if($entry.sha -cne $item.blob){StopGate ('GITHUB_SOURCE_BLOB_MISMATCH_'+$item.key)}
  $bytes=[Convert]::FromBase64String(($entry.content -replace '\s',''))
  if((ShaBytes $bytes) -cne $item.sha){StopGate ('GITHUB_SOURCE_SHA256_MISMATCH_'+$item.key)}
  $local=Join-Path $dir $item.file
  RejectReparse $local
  [IO.File]::WriteAllBytes($local,$bytes)
  if((ShaFile $local) -cne $item.sha){StopGate ('LOCAL_SOURCE_SHA256_MISMATCH_'+$item.key)}
  $receipt.source_files+=@([ordered]@{name=$item.key;git_blob=$item.blob;sha256=$item.sha;path=$local})
  Gate ('SOURCE_'+$item.key) 'PASS_EXACT_GIT_BLOB_SHA256' $item.sha
 }
 $markerBytes=[Text.Encoding]::UTF8.GetBytes(('run_id='+$id+[Environment]::NewLine+'source_commit='+$sourceCommit+[Environment]::NewLine))
 $fs=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try{$fs.Write($markerBytes,0,$markerBytes.Length);$fs.Flush()}finally{$fs.Dispose()}
 $receipt.marker_sha256=ShaFile $marker
 Gate 'ONE_SHOT_QA_MARKER' 'PASS_CREATED' 'No replay, no cleanup'
 $harness=Join-Path $dir $files[0].file
 $checker=Join-Path $dir $files[1].file
 $run=ReadNative $python @('-B',$checker,'--source',$harness,'--expected-sha256',$files[0].sha)
 $parsed=$null
 try{$parsed=$run.text | ConvertFrom-Json}catch{
  $receipt.python_checker=[ordered]@{exit_code=$run.code;error=$run.text.Substring(0,[Math]::Min(4096,$run.text.Length))}
 }
 if($null -eq $parsed -or $run.code -ne 0){StopGate 'S1_INDEPENDENT_PYTHON_QA_FAILED'}
 $receipt.python_checker=[ordered]@{
  exit_code=$run.code;verdict=$parsed.verdict
  positive_passed=$parsed.positive_passed;positive_total=$parsed.positive_total
  negative_rejected=$parsed.negative_rejected;negative_total=$parsed.negative_total
  positive_failed=@($parsed.positive_failed);negative_failed=@($parsed.negative_failed)
  source_sha256=$parsed.source_sha256;sha256_pinned=$parsed.sha256_pinned
  compiler_status=$parsed.native_csharp_compile;native_status=$parsed.native_harness_run
 }
 if($parsed.verdict -cne 'PASS_SOURCE_STATIC_NO_NATIVE' -or
    $parsed.positive_total -ne 41 -or $parsed.positive_passed -ne 41 -or
    $parsed.negative_total -ne 16 -or $parsed.negative_rejected -ne 16 -or
    $parsed.sha256_pinned -ne $true -or
    $parsed.source_sha256 -cne $files[0].sha -or
    $parsed.native_csharp_compile -cne 'NOT_EXECUTED' -or
    $parsed.native_harness_run -cne 'NOT_EXECUTED' -or
    $parsed.SCM_action -cne 'NONE'){StopGate 'S1_PYTHON_STATIC_QA_CONTRACT_BLOCK'}
 Gate 'INDEPENDENT_PYTHON_STATIC_QA' 'PASS_41_41_NEGATIVE_16_16' 'Source-only'
 $receipt.scm_after=SnapshotSCM
 if(($receipt.scm_before | ConvertTo-Json -Compress) -cne
    ($receipt.scm_after | ConvertTo-Json -Compress)){StopGate 'SCM_SNAPSHOT_CHANGED'}
 Gate 'SCM_AFTER' 'PASS_STOPPED_PID0' 'Read-only; no configuration change'
 $receipt.verdict='PASS_WINDOWS_S1_PYTHON_SOURCE_QA_NO_NATIVE'
}catch{
 $receipt.errors+= $_.Exception.Message
 $receipt.verdict='BLOCK_WINDOWS_S1_SOURCE_QA'
 Write-Host ('TTM_S1_QA_BLOCK='+$_.Exception.Message)
}finally{
 if($canWrite){
  try{
   if(-not(Test-Path -LiteralPath $dir)){New-Item -ItemType Directory -Path $dir -ErrorAction Stop | Out-Null}
   $receipt['utc']=[DateTime]::UtcNow.ToString('o')
   [IO.File]::WriteAllText($receiptPath,($receipt | ConvertTo-Json -Depth 16),(New-Object Text.UTF8Encoding $false))
   $localHash=ShaFile $receiptPath
   Write-Host ('TTM_S1_QA_RECEIPT='+$receiptPath)
   Write-Host ('TTM_S1_QA_SHA256='+$localHash)
   $bodyPath=Join-Path $dir 'github_create.json'
   $target='artifacts/qa/p01/'+$id+'.json'
   $body=@{branch=$branch;message=('evidence(p01): S1 Windows independent source QA '+$id);
     content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($receiptPath))} | ConvertTo-Json -Compress
   [IO.File]::WriteAllText($bodyPath,$body,(New-Object Text.UTF8Encoding $false))
   $upload=ReadNative 'gh.exe' @('api','-X','PUT',('repos/minhtri22/TokenToModel-Lab/contents/'+$target),'--input',$bodyPath)
   if($upload.code -ne 0){StopGate 'GITHUB_RECEIPT_UPLOAD_FAILED'}
   $newCommit=($upload.text | ConvertFrom-Json).commit.sha
   if($newCommit -notmatch '^[0-9a-f]{40}$'){StopGate 'GITHUB_COMMIT_NOT_READABLE'}
   $readback=ReadNative 'gh.exe' @('api',('repos/minhtri22/TokenToModel-Lab/contents/'+$target+'?ref='+$newCommit))
   if($readback.code -ne 0){StopGate 'GITHUB_RECEIPT_READBACK_FAILED'}
   $remote=$readback.text | ConvertFrom-Json
   $remoteBytes=[Convert]::FromBase64String(($remote.content -replace '\s',''))
   if((ShaBytes $remoteBytes) -cne $localHash){StopGate 'GITHUB_RECEIPT_SHA256_MISMATCH'}
   $githubOK=$true
   Write-Host ('TTM_S1_QA_GITHUB_COMMIT='+$newCommit)
   Write-Host 'TTM_S1_QA_GITHUB_READBACK=PASS'
  }catch{
   $receipt.verdict='BLOCK_GITHUB_RECEIPT_NOT_QUALIFIED'
   Write-Host ('TTM_S1_QA_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  }
 }
}
Write-Host ('TTM_S1_QA_VERDICT='+$receipt.verdict)
Write-Host 'TTM_S1_QA_CSC_EXECUTION=NOT_EXECUTED'
Write-Host 'TTM_S1_QA_NATIVE_EXECUTION=NOT_EXECUTED'
Write-Host 'TTM_S1_QA_SCM_ACTION=NONE'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
if($githubOK -and $receipt.verdict -eq 'PASS_WINDOWS_S1_PYTHON_SOURCE_QA_NO_NATIVE'){$exitCode=0}
exit $exitCode
