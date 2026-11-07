#requires -Version 5.1
# TTM P01 L1 S1: V3 successor; V1 and V2 failed QA receipts remain immutable.
# V3 logs Python output even when checker exits nonzero; source-only, no native C#.
# Never compiles/executes the C# harness, touches SCM, or mutates Broker V3/Worker V4.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$original=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$receiptRoot=Join-Path $root 'worktrees\_ttm_p01_l1_qa_receipts'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$sourceCommit='3add36f538c6fe39658ea72d91034b8c8a5f666a'
$originalHead='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$oldServiceExe=Join-Path $stage 'broker_service\TTMP01Broker.attestationV2.exe'
$marker=Join-Path $stage 'L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_V3_ATTEMPT_20261107.lock'
$prior2Marker=Join-Path $stage 'L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_V2_ATTEMPT_20261107.lock'
$prior2MarkerSha='506425d4fcd9e82fc0aa2d6c0056e0dda69f03a7ebbf270e43c97d3ddb2215d0'
$prior2Run='L1_S1_WINDOWS_INDEPENDENT_SOURCE_QA_V2_20261107T022147072Z_cd5dc8ba'
$prior2Receipt=Join-Path $receiptRoot ($prior2Run+'\'+$prior2Run+'.json')
$prior2ReceiptSha='fa955c9ebc23de8daddbd44e9af90171e53a65075aa8e7e3cf6dd17945ed5bad'
$prior2ReceiptBlob='3923ade3082a1c8d9530a5482a98eeee7a7f3339'
$prior2ReceiptCommit='57b9511770d2d5407475e621cc5f296606003750'
$priorMarker=Join-Path $stage 'L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_ATTEMPT_20261107.lock'
$priorMarkerSha='d39f4cd82c48c0401d48089c961f353663955671135c1e76ede06334b0b0f877'
$priorRun='L1_S1_WINDOWS_INDEPENDENT_SOURCE_QA_20261107T021034614Z_ec579411'
$priorReceipt=Join-Path $receiptRoot ($priorRun+'\'+$priorRun+'.json')
$priorReceiptSha='53fdf29600117f39eb5fd3c68a6d6276eaaa73b0238859fd6a79725260b95b41'
$priorReceiptBlob='7ea7ca44e9aa1ce6032218b0189d06f791bc43d9'
$priorReceiptCommit='f99a5ed372fde9787cc050b1f492021e9d4842e3'
$python=Join-Path $env:USERPROFILE 'miniforge3\python.exe'
$files=@(
  @{key='HARNESS';path='qa/p01/windows/S1/TTMS1IsolatedCancellationHarness.cs';file='TTMS1IsolatedCancellationHarness.cs';
    blob='872c67174c6fbbcea9941fe3bfa0acee3cddfb7c';sha='fd179c74fa1a136d791a5f9f6394ea657c58e7a46d1983c0eafa81051e99d6a9'},
  @{key='INDEPENDENT_QA';path='qa/p01/windows/S1/Independent-QA-S1-IsolatedCancellation-Static-V3.py';file='Independent-QA-S1-IsolatedCancellation-Static-V3.py';
    blob='8b65cb027b8ec7f7950036ca7cc6cc45eed3e603';sha='488bf941a872391ac55d6c3ce2fb5684846f756e4d87899844513bb5157850a2'}
)
$id='L1_S1_WINDOWS_INDEPENDENT_SOURCE_QA_V3_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$dir=Join-Path $receiptRoot $id
$receiptPath=Join-Path $dir ($id+'.json')
$canWrite=$false
$githubOK=$false
$exitCode=3
$receipt=[ordered]@{
 schema='ttm.p01.l1.s1.windows_independent_source_static_qa.v3'
 run_id=$id;source_commit=$sourceCommit;original_head=$originalHead
 mode='SOURCE_ONLY_NO_NATIVE'
 checks=[ordered]@{};source_files=@();python_checker=$null
 marker_sha256=$null;scm_before=$null;scm_after=$null
 predecessor=[ordered]@{run_id=$priorRun;receipt_commit=$priorReceiptCommit;receipt_sha256=$priorReceiptSha;marker_sha256=$priorMarkerSha;status='PENDING_PIN_RECHECK'}
 predecessor_v2=[ordered]@{run_id=$prior2Run;receipt_commit=$prior2ReceiptCommit;receipt_sha256=$prior2ReceiptSha;marker_sha256=$prior2MarkerSha;status='PENDING_PIN_RECHECK'}
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
 foreach($p in @($root,$original,$stage,$receiptRoot,$dir,$marker,$priorMarker,$priorReceipt,$prior2Marker,$prior2Receipt,$python)){RejectReparse $p}
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
 # Preserve and independently bind the original failed one-shot QA receipt.
 if(-not(Test-Path -LiteralPath $priorMarker -PathType Leaf) -or
    (ShaFile $priorMarker) -cne $priorMarkerSha){StopGate 'V1_FAILED_MARKER_MISMATCH'}
 if(-not(Test-Path -LiteralPath $priorReceipt -PathType Leaf) -or
    (ShaFile $priorReceipt) -cne $priorReceiptSha){StopGate 'V1_FAILED_RECEIPT_MISMATCH'}
 $v1=([IO.File]::ReadAllText($priorReceipt) | ConvertFrom-Json)
 if($v1.verdict -cne 'BLOCK_WINDOWS_S1_SOURCE_QA' -or
    $v1.python_checker.exit_code -ne 1 -or
    $v1.python_checker.error -notlike '*ValueError: substring not found*' -or
    $v1.compiler_execution -cne 'NOT_EXECUTED' -or
    $v1.s1_native_execution -cne 'NOT_EXECUTED' -or
    $v1.service_action -cne 'NONE'){StopGate 'V1_FAILED_RECEIPT_CONTRACT_MISMATCH'}
 $priorUrl='repos/minhtri22/TokenToModel-Lab/contents/artifacts/qa/p01/'+$priorRun+'.json?ref='+$priorReceiptCommit
 $priorGH=ReadNative 'gh.exe' @('api',$priorUrl)
 if($priorGH.code -ne 0){StopGate 'V1_FAILURE_GITHUB_READ_FAILED'}
 $priorObj=$priorGH.text | ConvertFrom-Json
 if($priorObj.sha -cne $priorReceiptBlob -or
    (ShaBytes ([Convert]::FromBase64String(($priorObj.content -replace '\s','')))) -cne $priorReceiptSha){StopGate 'V1_FAILURE_GITHUB_READBACK_MISMATCH'}
 $receipt.predecessor.status='PASS_PINNED_FAIL_PRESERVED'
 Gate 'V1_FAILED_RECEIPT_AND_MARKER' 'PASS_EXACT_FAIL_PRESERVED' $priorReceiptSha
 # Exact V2 failed execution is immutable and must also be preserved.
 if(-not(Test-Path -LiteralPath $prior2Marker -PathType Leaf) -or
    (ShaFile $prior2Marker) -cne $prior2MarkerSha){StopGate 'V2_FAILED_MARKER_MISMATCH'}
 if(-not(Test-Path -LiteralPath $prior2Receipt -PathType Leaf) -or
    (ShaFile $prior2Receipt) -cne $prior2ReceiptSha){StopGate 'V2_FAILED_RECEIPT_MISMATCH'}
 $v2=([IO.File]::ReadAllText($prior2Receipt) | ConvertFrom-Json)
 if($v2.verdict -cne 'BLOCK_WINDOWS_S1_SOURCE_QA' -or
    $null -ne $v2.python_checker -or
    $v2.marker_sha256 -cne $prior2MarkerSha -or
    $v2.source_commit -cne '5a5389ae7d98bfd3140296f43476c99859862979' -or
    $v2.compiler_execution -cne 'NOT_EXECUTED' -or
    $v2.s1_native_execution -cne 'NOT_EXECUTED' -or
    $v2.service_action -cne 'NONE'){StopGate 'V2_FAILED_RECEIPT_CONTRACT_MISMATCH'}
 $v2Url='repos/minhtri22/TokenToModel-Lab/contents/artifacts/qa/p01/'+$prior2Run+'.json?ref='+$prior2ReceiptCommit
 $v2GH=ReadNative 'gh.exe' @('api',$v2Url)
 if($v2GH.code -ne 0){StopGate 'V2_FAILED_RECEIPT_GITHUB_READ_FAILED'}
 $v2Obj=$v2GH.text | ConvertFrom-Json
 if($v2Obj.sha -cne $prior2ReceiptBlob -or
    (ShaBytes ([Convert]::FromBase64String(($v2Obj.content -replace '\s','')))) -cne $prior2ReceiptSha){StopGate 'V2_FAILED_RECEIPT_GITHUB_MISMATCH'}
 $receipt.predecessor_v2.status='PASS_PINNED_FAIL_PRESERVED'
 Gate 'V2_FAILED_RECEIPT_AND_MARKER' 'PASS_EXACT_FAIL_PRESERVED' $prior2ReceiptSha
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
 # Preserve the checker output BEFORE evaluating exit status; no swallowed FAIL JSON.
 $outText=[string]$run.text
 $receipt.python_checker=[ordered]@{
  exit_code=$run.code;stdout_sha256=(ShaBytes ([Text.Encoding]::UTF8.GetBytes($outText)))
  stdout_preview=$outText.Substring(0,[Math]::Min(12000,$outText.Length))
  parsed_json=$false
 }
 $parsed=$null
 try {
  if(-not [string]::IsNullOrWhiteSpace($outText)){$parsed=$outText | ConvertFrom-Json -ErrorAction Stop}
 }catch{
  $receipt.python_checker['parse_error']=$_.Exception.Message
 }
 if($null -ne $parsed){
  $receipt.python_checker['parsed_json']=$true
  $receipt.python_checker['schema']=$parsed.schema
  $receipt.python_checker['verdict']=$parsed.verdict
  $receipt.python_checker['positive_passed']=$parsed.positive_passed
  $receipt.python_checker['positive_total']=$parsed.positive_total
  $receipt.python_checker['negative_rejected']=$parsed.negative_rejected
  $receipt.python_checker['negative_total']=$parsed.negative_total
  $receipt.python_checker['positive_failed']=@($parsed.positive_failed)
  $receipt.python_checker['negative_failed']=@($parsed.negative_failed)
  $receipt.python_checker['negative_inspection_errors']=$parsed.negative_inspection_errors
  $receipt.python_checker['negative_fail_checks']=$parsed.negative_fail_checks
  $receipt.python_checker['source_sha256']=$parsed.source_sha256
  $receipt.python_checker['sha256_pinned']=$parsed.sha256_pinned
  $receipt.python_checker['compiler_status']=$parsed.native_csharp_compile
  $receipt.python_checker['native_status']=$parsed.native_harness_run
 }
 if($null -eq $parsed -or $run.code -ne 0){StopGate 'S1_INDEPENDENT_PYTHON_QA_FAILED_OUTPUT_PRESERVED'}
 if($parsed.schema -cne 'ttm.p01.l1.s1.isolated_cancel_independent_static.v3' -or
    $null -eq $parsed.negative_inspection_errors -or
    $parsed.negative_inspection_errors.PSObject.Properties.Count -ne 0 -or
    $null -eq $parsed.negative_fail_checks -or
    $parsed.negative_fail_checks.PSObject.Properties.Count -ne 16 -or
    $parsed.verdict -cne 'PASS_SOURCE_STATIC_NO_NATIVE' -or
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
 $receipt.verdict='PASS_WINDOWS_S1_V3_PYTHON_SOURCE_QA_NO_NATIVE'
}catch{
 $receipt.errors+= $_.Exception.Message
 $receipt.verdict='BLOCK_WINDOWS_S1_SOURCE_QA'
 Write-Host ('TTM_S1_QA_BLOCK='+$_.Exception.Message)
}finally{
 # Always snapshot the service after a failed checker, too.
 if($null -ne $receipt.scm_before -and $null -eq $receipt.scm_after){
  try{
   $receipt.scm_after=SnapshotSCM
   if(($receipt.scm_before | ConvertTo-Json -Compress) -cne
      ($receipt.scm_after | ConvertTo-Json -Compress)){
    $receipt.errors+='SCM_SNAPSHOT_CHANGED_AFTER_CHECKER_FAILURE'
    $receipt.verdict='BLOCK_SCM_SNAPSHOT_CHANGED'
   }else{Gate 'SCM_AFTER' 'PASS_STOPPED_PID0' 'Read-only including checker failure'}
  }catch{
   $receipt.errors+=('SCM_AFTER_READ_FAILED_'+$_.Exception.Message)
   $receipt.verdict='BLOCK_SCM_AFTER_READ_FAILURE'
  }
 }
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
if($githubOK -and $receipt.verdict -eq 'PASS_WINDOWS_S1_V3_PYTHON_SOURCE_QA_NO_NATIVE'){$exitCode=0}
exit $exitCode
