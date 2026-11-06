#requires -Version 5.1
# TTM P01 L1 -- exact-source COMPILE-ONLY; DEFAULT IS READ-ONLY.
# DO NOT invoke -CompileOnce until separate operator authorization.
[CmdletBinding()]param([switch]$CompileOnce)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$bin=Join-Path $stage 'broker_service'
$qaRun='L1_V3_V4_WINDOWS_INDEPENDENT_STATIC_QA_V4_20261106T180725764Z_b9748149'
$qaDir=Join-Path $root ('worktrees\_ttm_p01_l1_qa_receipts\'+$qaRun)
$qaFile=Join-Path $qaDir ($qaRun+'.json')
$qaSha='619bd23aee3d901418a41e638597718929baed6caeb7e5db5e5078fd96cbed3c'
$qaCommit='3860d08601ee77402d44926776f69208da103157'
$qaBlob='c5d1ae4eb6a154161638710d8c4ec2b3f82c82d1'
$qaMarker=Join-Path $stage 'L1_V3_V4_INDEPENDENT_STATIC_QA_V4_ATTEMPT_20261107.lock'
$qaMarkerSha='515fc6c37370cb0080af05b87f837bff2e4f564f693cf49d7c1e5840d1f44e38'
$historicalMarkers=@(
 @{name='SWITCH';file='L1_SCM_V2_SWITCH_ATTEMPT_20261106.lock';sha='29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1'},
 @{name='NATIVE';file='L1_BROKER_V2_WORKER_V3_NATIVE_SECURITY_ATTEMPT_20261106.lock';sha='f0d895e68c30b8c3845336ea8aee40d2e1ca84f96816906a952ae70ad81587c7'},
 @{name='SCM_STOP';file='L1_BROKER_V2_SCM_STOP_RECOVERY_ATTEMPT_20261106.lock';sha='f1ca3d0899fe6637a512e44dd073b449d4805ca8f8a8afa1e8a3989599143502'},
 @{name='FORCED_RECOVERY';file='L1_BROKER_V2_EXACT_PROCESS_TERMINATE_ATTEMPT_20261106.lock';sha='59823e4cd684195692dc5988a4af3eb484b05c4f7e5597e34140c1e21ac01dc9'}
)
$originalHead='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$sourceCommit='782f101f001973f8c23f23b22ae2b0896232d722'
$scmExe=Join-Path $bin 'TTMP01Broker.attestationV2.exe'
$scmSha='a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a'
$csc=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$cscSha='eca02e6b15cde93009a59a3d129d5a77fb5008f2e1cf62cf573b6737c747ecc3'
$sources=@(
 @{name='BROKER';file=(Join-Path $qaDir 'exact_sources\BrokerAttestationServiceV3.cs');sha='8bbcb2bb7b9f0d69e20ebd8ac04fa6216b20c986207b4215617bac8ffb782ca4'},
 @{name='WORKER';file=(Join-Path $qaDir 'exact_sources\TTMWorkerNativeProbeV4.cs');sha='0e81e2a2ae9914daff20956d3d85f54b98dfa921ddd1764c771b8e9bae5cef04'},
 @{name='CHECKER';file=(Join-Path $qaDir 'exact_sources\Independent-QA-BrokerV3-WorkerV4-Static.py');sha='f75ce6ecf16fc5a3d00807dc958f4421027578f1aab7a587144c5ca2ab32642d'}
)
$exe=Join-Path $bin 'TTMP01Broker.attestationV3.exe'
$dll=Join-Path $bin 'TTMWorkerNativeProbeV4.dll'
$marker=Join-Path $stage 'L1_V3_V4_EXACT_SOURCE_COMPILE_ATTEMPT_20261107.lock'
$id='L1_V3_V4_COMPILE_ONLY_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $root ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$rec=[ordered]@{
 schema='ttm.p01.l1.v3v4.exact_source_compile_only.v1';run_id=$id
 mode=$(if($CompileOnce){'COMPILE_ONCE'}else{'READONLY_PREFLIGHT'})
 original_head=$originalHead;source_commit=$sourceCommit;qa_commit=$qaCommit
 qa_sha256=$qaSha;checks=[ordered]@{};steps=@();outputs=[ordered]@{}
 compile_marker_sha256=$null;errors=@();verdict='BLOCK'
 scm_action='NONE';worker_or_acl_mutation=$false;W01_W12='NOT_EXECUTED'
 L1_grouped_QA='NOT_AUTHORIZED';P01='OPEN';P02='NOT_OPENED'
}
function Gate([string]$n,[string]$v,[string]$d){
 $rec.checks[$n]=@{status=$v;detail=$d};Write-Host ('TTM_CSC_'+$n+'='+$v)
}
function Block([string]$why){throw [InvalidOperationException]::new($why)}
function Hash([string]$p){return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function NoReparse([string]$path){
 while($path -and (Test-Path -LiteralPath $path)){
  if(((Get-Item -LiteralPath $path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Block 'REPARSE_POINT'}
  $parent=Split-Path -Parent $path;if($parent -eq $path){break};$path=$parent
 }
}
function Pin([string]$name,[string]$path,[string]$sha){
 NoReparse $path
 if($sha -notmatch '^[0-9a-f]{64}$' -or -not(Test-Path -LiteralPath $path -PathType Leaf) -or
    (Hash $path) -cne $sha){Block ('PIN_MISMATCH_'+$name)}
 Gate $name 'PASS_EXACT' $sha
}
function GitRead([string[]]$gitArgs){
 $out=@(& git.exe -C $wt @gitArgs 2>&1)
 if($LASTEXITCODE -ne 0){Block 'ORIGINAL_GIT_READ_FAILED'}
 return (($out -join [Environment]::NewLine).Trim())
}
function RunCompiler([string]$name,[string[]]$compilerArgs,[string]$destination){
 $oldPref=$ErrorActionPreference;$ErrorActionPreference='Continue'
 try{$lines=@(& $csc @compilerArgs 2>&1);$rc=$LASTEXITCODE}
 finally{$ErrorActionPreference=$oldPref}
 $diagnostics=(($lines|ForEach-Object {$_.ToString()}) -join [Environment]::NewLine)
 if($diagnostics.Length -gt 16384){$diagnostics=$diagnostics.Substring(0,16384)}
 $rec.steps+=@([ordered]@{component=$name;exit_code=$rc;diagnostics=$diagnostics})
 if($rc -ne 0 -or -not(Test-Path -LiteralPath $destination -PathType Leaf)){
  Gate $name 'FAIL' ('csc exit '+$rc);Block ('COMPILER_FAILED_'+$name)
 }
 $rec.outputs[$name]=[ordered]@{path=$destination;sha256=(Hash $destination);size=(Get-Item -LiteralPath $destination).Length}
 Gate $name 'PASS' (Hash $destination)
}
try{
 $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin -or [Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){Block 'ELEVATED_WINDOWS_REQUIRED'}
 foreach($p in @($root,$wt,$stage,$bin,$qaDir,$qaFile,$qaMarker,$csc,$marker,$exe,$dll,$receiptDir)){NoReparse $p}
 if((GitRead @('rev-parse','HEAD')) -cne $originalHead -or
    (GitRead @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106' -or
    (GitRead @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Block 'FROZEN_ORIGINAL_GIT_MISMATCH'}
 Gate 'FROZEN_ORIGINAL' 'PASS' $originalHead
 $svc=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $svc -or $svc.State -ne 'Stopped' -or [int]$svc.ProcessId -ne 0 -or
    $svc.StartMode -ne 'Manual' -or $svc.StartName -ine 'NT AUTHORITY\LocalService' -or
    $svc.PathName.Trim().Trim([char]34).Trim() -ine $scmExe){Block 'SCM_CHANGED_OR_NOT_STOPPED_PID0'}
 Gate 'SCM' 'PASS_STOPPED_PID0' 'Read-only'
 Pin 'SCM_V2_EXE' $scmExe $scmSha
 Pin 'QA_MARKER' $qaMarker $qaMarkerSha
 foreach($entry in $historicalMarkers){Pin ('HIST_'+$entry.name) (Join-Path $stage $entry.file) $entry.sha}
 Pin 'QA_RECEIPT' $qaFile $qaSha
 Pin 'CSC_BINARY' $csc $cscSha
 foreach($source in $sources){Pin $source.name $source.file $source.sha}
 $qa=[IO.File]::ReadAllText($qaFile)|ConvertFrom-Json
 if($qa.run_id -cne $qaRun -or $qa.source_commit -cne $sourceCommit -or
    $qa.verdict -cne 'PASS_WINDOWS_PYTHON_STATIC_QA_AND_COMPILE_ONLY_PREFLIGHT_NO_BINARY' -or
    $qa.python_checker_exit -ne 0 -or
    $qa.python_checker_result.verdict -cne 'PASS_SOURCE_ONLY_NO_WINDOWS_NATIVE' -or
    $qa.python_checker_result.static_checks_total -ne 46 -or
    $qa.python_checker_result.static_checks_passed -ne 46 -or
    $qa.python_checker_result.negative_fixture_total -ne 9 -or
    $qa.python_checker_result.negative_fixture_passed -ne 9 -or
    $qa.compiler_preflight.sha256 -cne $cscSha -or
    $qa.compiler_preflight.invocation -cne 'NOT_EXECUTED' -or
    $qa.qa_marker_sha256 -cne $qaMarkerSha -or
    $qa.compiler_preflight.target_broker_exe -ine $exe -or
    $qa.compiler_preflight.target_worker_dll -ine $dll){Block 'QUALIFIED_QA_CONTRACT_MISMATCH'}
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Block 'GH_CLI_REQUIRED'}
 & gh.exe auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Block 'GH_AUTH_FAILED'}
 $uri='repos/minhtri22/TokenToModel-Lab/contents/artifacts/qa/p01/'+$qaRun+'.json?ref='+$qaCommit
 $response=@(& gh.exe api $uri 2>&1)
 if($LASTEXITCODE -ne 0){Block 'GITHUB_QA_READ_FAILED'}
 $remote=($response -join [Environment]::NewLine)|ConvertFrom-Json
 if($remote.sha -cne $qaBlob){Block 'GITHUB_QA_BLOB_MISMATCH'}
 $hashAlg=[Security.Cryptography.SHA256]::Create()
 try{$backSha=([BitConverter]::ToString($hashAlg.ComputeHash([Convert]::FromBase64String(($remote.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
 finally{$hashAlg.Dispose()}
 if($backSha -cne $qaSha){Block 'GITHUB_QA_BYTES_MISMATCH'}
 Gate 'QUALIFIED_QA' 'PASS_46_9' $qaCommit
 $disk=Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
 $os=Get-CimInstance Win32_OperatingSystem
 if([int64]$disk.FreeSpace -lt 2147483648 -or [int64]$os.FreePhysicalMemory -lt 2097152){Block 'RESOURCE_GUARD'}
 if((Test-Path -LiteralPath $exe) -or (Test-Path -LiteralPath $dll) -or (Test-Path -LiteralPath $marker)){Block 'OUTPUT_OR_MARKER_ALREADY_EXISTS'}
 Gate 'OUTPUT_PRISTINE' 'PASS' 'No binary or attempt marker present'
 if(-not $CompileOnce){
  $rec.verdict='PREFLIGHT_PASS_NO_COMPILATION'
  Gate 'ACTION' 'NOT_EXECUTED' 'Explicit -CompileOnce and separate approval required'
 }else{
  New-Item -ItemType Directory -Path $receiptDir -ErrorAction Stop|Out-Null
  $mb=[Text.Encoding]::UTF8.GetBytes(('run_id='+$id+[Environment]::NewLine+'qa_sha256='+$qaSha+[Environment]::NewLine))
  $s=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
  try{$s.Write($mb,0,$mb.Length);$s.Flush()}finally{$s.Dispose()}
  $rec.compile_marker_sha256=Hash $marker
  Gate 'ONE_SHOT_MARKER' 'PASS_CREATED' 'Atomic no replay'
  $temp=Join-Path $receiptDir 'csc_tmp'
  New-Item -ItemType Directory -Path $temp -ErrorAction Stop|Out-Null
  $oldTemp=$env:TEMP;$oldTmp=$env:TMP
  try{
   $env:TEMP=$temp;$env:TMP=$temp
   $brokerArgs=@('/nologo','/target:exe','/debug-','/optimize+',
     ('/out:'+$exe),'/reference:System.dll','/reference:System.Core.dll',
     '/reference:System.ServiceProcess.dll',$sources[0].file)
   RunCompiler 'BROKER_V3' $brokerArgs $exe
   $workerArgs=@('/nologo','/target:library','/debug-','/optimize+',
     ('/out:'+$dll),'/reference:System.dll','/reference:System.Core.dll',$sources[1].file)
   RunCompiler 'WORKER_V4' $workerArgs $dll
  }finally{$env:TEMP=$oldTemp;$env:TMP=$oldTmp}
  $rec.verdict='PASS_COMPILE_ONLY_NO_SERVICE_ACTION'
 }
}catch{
 $rec.errors+=$_.Exception.Message
 $rec.verdict='BLOCK_OR_COMPILE_FAILED'
 Write-Host ('TTM_CSC_BLOCK='+$_.Exception.Message)
}finally{
 $evidenceOk=$false
 if($CompileOnce){
  try{
   New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
   $rec['utc']=[DateTime]::UtcNow.ToString('o')
   $file=Join-Path $receiptDir ($id+'.json')
   [IO.File]::WriteAllText($file,($rec|ConvertTo-Json -Depth 16),(New-Object Text.UTF8Encoding $false))
   $receiptHash=Hash $file
   Write-Host ('TTM_CSC_RECEIPT='+$file)
   Write-Host ('TTM_CSC_SHA256='+$receiptHash)
   $path='artifacts/qa/p01/'+$id+'.json'
   $request=Join-Path $receiptDir 'github_create.json'
   $requestJson=@{branch=$branch;message=('evidence(p01): one-shot V3/V4 compile '+$id);
     content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
   [IO.File]::WriteAllText($request,$requestJson,(New-Object Text.UTF8Encoding $false))
   $response=@(& gh.exe api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$path) --input $request 2>&1)
   if($LASTEXITCODE -ne 0){Block 'GITHUB_UPLOAD_FAILED'}
   $saved=($response -join [Environment]::NewLine)|ConvertFrom-Json
   $read=@(& gh.exe api ('repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$saved.commit.sha) 2>&1)
   if($LASTEXITCODE -ne 0){Block 'GITHUB_READBACK_FAILED'}
   $object=($read -join [Environment]::NewLine)|ConvertFrom-Json
   $sha=[Security.Cryptography.SHA256]::Create()
   try{$readHash=([BitConverter]::ToString($sha.ComputeHash([Convert]::FromBase64String(($object.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
   finally{$sha.Dispose()}
   if($readHash -cne $receiptHash){Block 'GITHUB_SHA256_MISMATCH'}
   Write-Host ('TTM_CSC_GITHUB_COMMIT='+$saved.commit.sha)
   $evidenceOk=$true
   Write-Host 'TTM_CSC_GITHUB_READBACK=PASS'
  }catch{
   $rec['verdict']='BLOCK_EVIDENCE_PUBLICATION_NOT_QUALIFIED'
   Write-Host ('TTM_CSC_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  }
 }
}
Write-Host ('TTM_CSC_VERDICT='+$rec.verdict)
Write-Host 'TTM_CSC_SCM_ACTION=NONE'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
if((-not $CompileOnce -and $rec.verdict -eq 'PREFLIGHT_PASS_NO_COMPILATION') -or
   ($CompileOnce -and $evidenceOk -and $rec.verdict -eq 'PASS_COMPILE_ONLY_NO_SERVICE_ACTION')){exit 0}
exit 3
