#requires -Version 5.1
# S1 combined-native runner candidate. Default PRECHECK is read-only.
# No native permit exists; ExecuteOnce is forbidden until a later formal decision.
[CmdletBinding()]
param(
 [ValidateSet('Preflight','ExecuteOnce')][string]$Mode='Preflight',
 [string]$PermitCommit='',
 [string]$PermitSha256=''
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$original=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$receipts=Join-Path $root 'worktrees\_ttm_p01_l1_qa_receipts'
$nativeRoot=Join-Path $root 'worktrees\_ttm_p01_l1_native_s1_20261107'
$marker=Join-Path $stage 'L1_S1_NATIVE_COMBINED_ONE_SHOT_ATTEMPT_20261107.lock'
$permitRemote='artifacts/qa/p01/S1_NATIVE_COMBINED_PERMIT_20261107.json'
$permitId='TTM_P01_L1_S1_NATIVE_COMBINED_PERMIT_20261107'
$oneShotId='TTM_P01_L1_S1_NATIVE_COMBINED_ONCE_20261107'
$sourceRef='e1ff28ca2808164dfbd51a902492a0218c345c54'
$frozen='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$branchExpected='implementation/p01-i0a-s-f0-static-20261106'
$originExpected='https://github.com/minhtri22/TokenToModel-Lab.git'
$csc='C:\WINDOWS\Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$cscSha='eca02e6b15cde93009a59a3d129d5a77fb5008f2e1cf62cf573b6737c747ecc3'
$svcV2=Join-Path $stage 'broker_service\TTMP01Broker.attestationV2.exe'
$src=@(
 @{k='HARNESS';f='TTMS1IsolatedCancellationHarness.cs';p='qa/p01/windows/S1/TTMS1IsolatedCancellationHarness.cs';blob='872c67174c6fbbcea9941fe3bfa0acee3cddfb7c';sha='fd179c74fa1a136d791a5f9f6394ea657c58e7a46d1983c0eafa81051e99d6a9'},
 @{k='WATCHDOG';f='TTMS1IsolatedJobWatchdogEngineV2.cs';p='qa/p01/windows/S1/TTMS1IsolatedJobWatchdogEngineV2.cs';blob='5763ca10025bb928f161a0f33fa493d436107375';sha='f8c07f486a4e373810e75ec1cf99d79414f66d7e74c65851d0ff268b949640c3'},
 @{k='HOST';f='TTMS1JobWatchdogHostV1.cs';p='qa/p01/windows/S1/TTMS1JobWatchdogHostV1.cs';blob='7eedfab02ab995507e36a9beee25772393dc70ab';sha=''}
)
$priorMarkers=@(
 @{f='L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_ATTEMPT_20261107.lock';sha='d39f4cd82c48c0401d48089c961f353663955671135c1e76ede06334b0b0f877'},
 @{f='L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_V2_ATTEMPT_20261107.lock';sha='506425d4fcd9e82fc0aa2d6c0056e0dda69f03a7ebbf270e43c97d3ddb2215d0'},
 @{f='L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_V3_ATTEMPT_20261107.lock';sha='c923fa283a3737bcdb2dcefed2c384899187cee532c8d580a589e0c7fda7d4ea'}
)
function Fail([string]$why){throw ('TTM_S1_COMBINED_BLOCK_'+$why)}
function SafePath([string]$p){
 $cur=$p
 while(-not [string]::IsNullOrEmpty($cur)){
  if(Test-Path -LiteralPath $cur){
   if(((Get-Item -LiteralPath $cur -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Fail 'REPARSE_POINT'}
  }
  $parent=Split-Path -Parent $cur
  if($parent -eq $cur -or [string]::IsNullOrEmpty($parent)){break}
  $cur=$parent
 }
}
function HashData([byte[]]$bytes){
 $hash=[Security.Cryptography.SHA256]::Create()
 try{return ([BitConverter]::ToString($hash.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()}
 finally{$hash.Dispose()}
}
function HashPath([string]$p){
 SafePath $p
 if(-not(Test-Path -LiteralPath $p -PathType Leaf)){Fail 'FILE_PIN_MISSING'}
 return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Cmd([string]$exe,[string[]]$argv){
 $previous=$ErrorActionPreference
 $ErrorActionPreference='Continue'
 try{$lines=@(& $exe @argv 2>&1);$code=$LASTEXITCODE}
 finally{$ErrorActionPreference=$previous}
 return [pscustomobject]@{code=$code;output=(($lines|ForEach-Object{$_.ToString()})-join [Environment]::NewLine)}
}
function Fetch([string]$p,[string]$ref,[string]$blob){
 $u='repos/minhtri22/TokenToModel-Lab/contents/'+$p+'?ref='+$ref
 $r=Cmd 'gh.exe' @('api',$u)
 if($r.code -ne 0){Fail ('GH_FETCH_'+$p)}
 $json=$r.output|ConvertFrom-Json
 if($blob -ne '' -and $json.sha -cne $blob){Fail 'GH_BLOB_MISMATCH'}
 $bytes=[Convert]::FromBase64String(($json.content -replace '\s',''))
 return [pscustomobject]@{data=$bytes;sha=(HashData $bytes);blob=$json.sha}
}
function ServiceSnapshot {
 $v=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'"
 if($null -eq $v){Fail 'BROKER_MISSING'}
 $img=$v.PathName.Trim().Trim([char]34).Trim()
 if($v.State -ne 'Stopped' -or [int]$v.ProcessId -ne 0 -or
    $v.StartMode -ne 'Manual' -or $v.StartName -ine 'NT AUTHORITY\LocalService' -or
    $img -ine $svcV2){Fail 'BROKER_NOT_STOPPED_V2'}
 return [ordered]@{name=$v.Name;state=$v.State;pid=[int]$v.ProcessId;start=$v.StartMode;account=$v.StartName;image=$img}
}
function Preconditions {
 if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){Fail 'WINDOWS'}
 foreach($p in @($root,$original,$stage,$receipts,$nativeRoot,$marker,$csc,$PSCommandPath)){SafePath $p}
 if(-not(Test-Path $original -PathType Container) -or
    -not(Test-Path $receipts -PathType Container)){Fail 'PROJECT_WORKTREES'}
 $head=Cmd 'git.exe' @('-C',$original,'rev-parse','HEAD')
 $branch=Cmd 'git.exe' @('-C',$original,'branch','--show-current')
 $origin=Cmd 'git.exe' @('-C',$original,'remote','get-url','origin')
 if($head.code -ne 0 -or $head.output.Trim() -cne $frozen -or
    $branch.code -ne 0 -or $branch.output.Trim() -cne $branchExpected -or
    $origin.code -ne 0 -or $origin.output.Trim() -cne $originExpected){Fail 'FROZEN_ORIGIN_HEAD_BRANCH'}
 $scm=ServiceSnapshot
 foreach($m in $priorMarkers){if((HashPath (Join-Path $stage $m.f)) -cne $m.sha){Fail 'PRIOR_MARKER_CHANGED'}}
 if((HashPath (Join-Path $stage 'broker_service\TTMP01Broker.attestationV3.exe')) -cne '0751f89fee519367580e89b2e99b5347ee49c6b4c15f67ebf7d43706ac78ec5c'){Fail 'BROKER_V3_PIN'}
 if((HashPath (Join-Path $stage 'broker_service\TTMWorkerNativeProbeV4.dll')) -cne 'b36b5868b09b4da7bdb7198f3acd86923aba57f29a993fc8188bcb1cdc729f36'){Fail 'WORKER_V4_PIN'}
 if((HashPath $csc) -cne $cscSha){Fail 'CSC_PIN'}
 if(Test-Path -LiteralPath $marker){Fail 'NATIVE_MARKER_ALREADY_USED_NO_REPLAY'}
 if(Test-Path -LiteralPath $nativeRoot){Fail 'NATIVE_OUTPUTS_NOT_PRISTINE'}
 $os=Get-CimInstance Win32_OperatingSystem
 $disk=Get-PSDrive -Name 'D'
 if(([int64]$os.FreePhysicalMemory*1024) -lt 2147483648 -or
    [int64]$disk.Free -lt 1073741824){Fail 'RESOURCE_BOUNDARY'}
 if((Cmd 'gh.exe' @('auth','status')).code -ne 0){Fail 'GITHUB_AUTH'}
 Write-Host 'TTM_S1_COMBINED_FROZEN_SCM_MARKERS=PASS_READONLY'
 return $scm
}
$sources=@{}
function FetchSources {
 foreach($f in $src){
  $v=Fetch $f.p $sourceRef $f.blob
  if($f.sha -ne '' -and $v.sha -cne $f.sha){Fail ('SOURCE_PIN_'+$f.k)}
  $sources[$f.k]=$v
 }
 Write-Host 'TTM_S1_COMBINED_SOURCES=PASS_EXACT_GIT_BLOB_SHA256'
}
function AuthorizedPermit {
 if($PermitCommit -cnotmatch '^[0-9a-f]{40}$' -or
    $PermitSha256 -cnotmatch '^[0-9a-f]{64}$'){Fail 'PERMIT_COMMIT_SHA_REQUIRED'}
 $obj=Fetch $permitRemote $PermitCommit ''
 if($obj.sha -cne $PermitSha256){Fail 'PERMIT_DIGEST'}
 $p=[Text.Encoding]::UTF8.GetString($obj.data)|ConvertFrom-Json
 if($p.schema -cne 'ttm.p01.l1.s1.native_combined_permit.v1' -or
    $p.decision -cne 'AUTHORIZED_ONCE_EXACT_SOURCE_S1_NATIVE' -or
    $p.permit_id -cne $permitId -or $p.one_shot_id -cne $oneShotId -or
    $p.scope -cne 'S1_ISOLATED_COMPILE_AND_SINGLE_NATIVE_SMOKE' -or
    $p.original_head -cne $frozen -or $p.source_commit -cne $sourceRef -or
    $p.harness_sha256 -cne $sources.HARNESS.sha -or
    $p.watchdog_sha256 -cne $sources.WATCHDOG.sha -or
    $p.host_sha256 -cne $sources.HOST.sha -or
    $p.runner_sha256 -cne (HashPath $PSCommandPath) -or
    $p.compiler_sha256 -cne $cscSha -or
    $p.scm_actions -cne 'FORBIDDEN' -or [int]$p.allowed_native_runs -ne 1){
  Fail 'PERMIT_CONTENT_NOT_AUTHORIZED'
 }
 Write-Host 'TTM_S1_COMBINED_PERMIT=PASS_EXACT_ONCE'
 return $obj
}
function Compile([string]$label,[string[]]$args){
 $r=Cmd $csc $args
 $info=[ordered]@{target=$label;exit_code=$r.code;
   output_sha256=(HashData ([Text.Encoding]::UTF8.GetBytes($r.output)));
   output_preview=$r.output.Substring(0,[Math]::Min($r.output.Length,12000))}
 if($r.code -ne 0){Fail ('COMPILER_'+$label+'_FAILED')}
 return $info
}
# No active permit is supplied or issued in the present design step.
$receipt=$null;$receiptPath='';$markerCreated=$false;$uploaded=$false;$passed=$false;$exitCode=3
try{
 $scmBefore=Preconditions
 FetchSources
 if($Mode -eq 'Preflight'){
  Write-Host 'TTM_S1_COMBINED_PRECHECK=PASS_SOURCE_ONLY'
  Write-Host 'TTM_S1_COMBINED_PERMIT=NOT_ISSUED'
  Write-Host 'TTM_S1_COMBINED_NATIVE=NOT_EXECUTED'
  return
 }
 $permit=AuthorizedPermit
 $runId='S1_NATIVE_COMBINED_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ').ToUpperInvariant()+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8).ToUpperInvariant()
 $dir=Join-Path $receipts $runId
 $build=Join-Path $nativeRoot 'build'
 $receiptPath=Join-Path $dir ($runId+'.json')
 foreach($p in @($dir,$build,$receiptPath)){SafePath $p}
 if(Test-Path -LiteralPath $dir){Fail 'RECEIPT_NOT_PRISTINE'}
 $receipt=[ordered]@{
  schema='ttm.p01.l1.s1.native_combined_once_receipt.v1';run_id=$runId;
  source_ref=$sourceRef;permit_ref=$PermitCommit;permit_sha256=$PermitSha256;
  frozen_head=$frozen;scm_before=$scmBefore;scm_after=$null;marker_sha256='';
  sources=@();compile=@();host=$null;errors=@();verdict='BLOCK';
  science_execution='NOT_EXECUTED';SCM_action='NONE';P01='OPEN';P02='NOT_OPENED'
 }
 # Consume exact native one-shot BEFORE any compiler invocation.
 $content=@('schema=ttm.p01.l1.s1.native_one_shot_marker.v1',
   ('permit_id='+$permitId),('permit_sha256='+$PermitSha256),
   ('one_shot_id='+$oneShotId),('run_id='+$runId),'') -join [string][char]10
 $bytes=[Text.Encoding]::UTF8.GetBytes($content)
 $fh=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try{$fh.Write($bytes,0,$bytes.Length);$fh.Flush()}finally{$fh.Dispose()}
 $markerCreated=$true
 $receipt.marker_sha256=HashPath $marker
 Write-Host 'TTM_S1_COMBINED_NATIVE_MARKER=PASS_CREATED'
 New-Item -ItemType Directory -Path $dir -ErrorAction Stop|Out-Null
 New-Item -ItemType Directory -Path $build -Force -ErrorAction Stop|Out-Null
 foreach($f in $src){
  $dest=Join-Path $dir $f.f
  [IO.File]::WriteAllBytes($dest,$sources[$f.k].data)
  if((HashPath $dest) -cne $sources[$f.k].sha){Fail 'LOCAL_SOURCE_MISMATCH'}
  $receipt.sources+=@([ordered]@{name=$f.k;blob=$f.blob;sha256=$sources[$f.k].sha})
 }
 $permitFile=Join-Path $dir 'S1_NATIVE_COMBINED_PERMIT.json'
 [IO.File]::WriteAllBytes($permitFile,$permit.data)
 if((HashPath $permitFile) -cne $PermitSha256){Fail 'LOCAL_PERMIT_MISMATCH'}
 $s1exe=Join-Path $build 'TTMS1IsolatedCancellationHarness.exe'
 $hostexe=Join-Path $build 'TTMS1JobWatchdogHostV1.exe'
 if((Test-Path $s1exe) -or (Test-Path $hostexe)){Fail 'BUILD_OUTPUT_NOT_PRISTINE'}
 $receipt.compile+=@(Compile 'S1' @('/nologo','/target:exe','/platform:x64','/langversion:5',
   ('/out:'+$s1exe),'/reference:System.Core.dll','/reference:System.Security.dll',
   (Join-Path $dir $src[0].f)))
 $s1sha=HashPath $s1exe
 $receipt.compile+=@(Compile 'HOST' @('/nologo','/target:exe','/platform:x64','/langversion:5',
   ('/out:'+$hostexe),'/reference:System.Core.dll','/reference:System.Runtime.Serialization.dll',
   (Join-Path $dir $src[1].f),(Join-Path $dir $src[2].f)))
 $hostsha=HashPath $hostexe
 $receipt['s1_sha256']=$s1sha;$receipt['host_sha256']=$hostsha
 $outFile=Join-Path $dir 'host.stdout.txt'
 $errFile=Join-Path $dir 'host.stderr.txt'
 if((Test-Path $outFile) -or (Test-Path $errFile)){Fail 'HOST_LOG_EXISTS'}
 # Only exact owned host Process object can be terminated on timeout.
 $argsHost=@($root,$s1exe,$s1sha,$permitFile,$PermitSha256,$marker,
   $receipt.marker_sha256,$runId)|ForEach-Object{'"'+($_ -replace '"','')+'"'}
 $sp=@{FilePath=$hostexe;ArgumentList=$argsHost;WorkingDirectory=$build;
   RedirectStandardOutput=$outFile;RedirectStandardError=$errFile;PassThru=$true;NoNewWindow=$true}
 $owned=Start-Process @sp
 $timedOut=$false;$terminationConfirmed=$false;$nativeExit=-1
 try{
  if(-not $owned.WaitForExit(30000)){
   $timedOut=$true
   $owned.Kill()
   $terminationConfirmed=$owned.WaitForExit(3000)
  }
  if($owned.HasExited){$nativeExit=$owned.ExitCode}
 }finally{$owned.Dispose()}
 $stdout=[IO.File]::ReadAllBytes($outFile)
 $stderr=[IO.File]::ReadAllBytes($errFile)
 $text=[Text.Encoding]::UTF8.GetString($stdout)
 $receipt.host=[ordered]@{exit=$nativeExit;timeout=$timedOut;
   termination_confirmed=$terminationConfirmed;
   stdout_sha256=(HashData $stdout);stderr_sha256=(HashData $stderr);
   stdout_preview=$text.Substring(0,[Math]::Min($text.Length,12000))}
 if($timedOut -or $nativeExit -ne 0 -or $stderr.Length -ne 0 -or $stdout.Length -gt 8192){
  Fail 'HOST_EXIT_TIMEOUT_OR_STDERR'
 }
 $lines=@($text.Replace([string][char]13+[string][char]10,[string][char]10).TrimEnd([char]10).Split([char]10))
 $required=@('TTM_S1_HOST_VERDICT=PASS_ISOLATED_S1_ONLY',
   'TTM_S1_HOST_JOB_CHECKED=TRUE','TTM_S1_HOST_EXIT_CONFIRMED=TRUE',
   'TTM_S1_HOST_STDOUT_BOUNDED=TRUE','TTM_S1_HOST_STDERR_EMPTY=TRUE')
 foreach($line in $required){if(-not($lines -ccontains $line)){Fail 'HOST_RESULT_INCOMPLETE'}}
 if($lines.Length -ne 11){Fail 'HOST_OUTPUT_LINE_COUNT'}
 $receipt.scm_after=ServiceSnapshot
 if(($receipt.scm_before|ConvertTo-Json -Compress) -cne
    ($receipt.scm_after|ConvertTo-Json -Compress)){Fail 'SCM_CHANGED'}
 $receipt.verdict='PASS_ISOLATED_S1_NATIVE_ONLY'
 $passed=$true
}catch{
 if($null -ne $receipt){$receipt.errors+=@($_.Exception.Message)}
 Write-Host ('TTM_S1_COMBINED_BLOCK='+$_.Exception.Message)
}finally{
 if($markerCreated){
  if($null -eq $receipt.scm_after){
   try{$receipt.scm_after=ServiceSnapshot}
   catch{$receipt.errors+=@('SCM_AFTER_'+$_.Exception.Message);$passed=$false}
  }
  try{
   $receipt['utc']=[DateTime]::UtcNow.ToString('o')
   [IO.File]::WriteAllText($receiptPath,($receipt|ConvertTo-Json -Depth 18),
       (New-Object Text.UTF8Encoding $false))
   $localSha=HashPath $receiptPath
   $target='artifacts/qa/p01/'+$runId+'.json'
   $payload=@{branch='audit/p01-l1-native-security-critical-fix-20261106';
     message=('evidence(p01): S1 native one shot '+$runId);
     content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($receiptPath))}|ConvertTo-Json -Compress
   $uploadInput=Join-Path $dir 'github_upload_request.json'
   [IO.File]::WriteAllText($uploadInput,$payload,(New-Object Text.UTF8Encoding $false))
   $up=Cmd 'gh.exe' @('api','-X','PUT',
       ('repos/minhtri22/TokenToModel-Lab/contents/'+$target),'--input',$uploadInput)
   if($up.code -ne 0){Fail 'GITHUB_RECEIPT_UPLOAD'}
   $commit=($up.output|ConvertFrom-Json).commit.sha
   if($commit -cnotmatch '^[0-9a-f]{40}$'){Fail 'GITHUB_COMMIT'}
   $verify=Fetch $target $commit ''
   if($verify.sha -cne $localSha){Fail 'GITHUB_SHA_READBACK'}
   $uploaded=$true
   Write-Host ('TTM_S1_COMBINED_RECEIPT='+$receiptPath)
   Write-Host ('TTM_S1_COMBINED_RECEIPT_SHA256='+$localSha)
   Write-Host ('TTM_S1_COMBINED_GITHUB_COMMIT='+$commit)
   Write-Host 'TTM_S1_COMBINED_GITHUB_READBACK=PASS'
  }catch{
   $passed=$false
   Write-Host ('TTM_S1_COMBINED_EVIDENCE_BLOCK='+$_.Exception.Message)
  }
 }
}
$verdict='BLOCK'
if($passed -and $uploaded){$verdict='PASS_ISOLATED_S1_NATIVE_ONLY';$exitCode=0}
Write-Host ('TTM_S1_COMBINED_VERDICT='+$verdict)
Write-Host 'TTM_S1_COMBINED_SCM_ACTION=NONE'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
exit $exitCode
