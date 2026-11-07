#requires -Version 5.1
# S1 source-only integrated QA: Windows PS 5.1 parse, Python contracts, GitHub receipt.
# Never compiles/runs C#, consumes a native marker, or changes SCM.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$receiptRoot=Join-Path $root 'worktrees\_ttm_p01_l1_qa_receipts'
$original=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$marker=Join-Path $stage 'L1_S1_NATIVE_COMBINED_ONE_SHOT_ATTEMPT_20261107.lock'
$python=Join-Path $env:USERPROFILE 'miniforge3\python.exe'
$ref='8e2a2033187d22e8c44c7493e8853dafe974715f'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$files=@(
 @{id='HOST';f='TTMS1JobWatchdogHostV1.cs';p='qa/p01/windows/S1/TTMS1JobWatchdogHostV1.cs';blob='7eedfab02ab995507e36a9beee25772393dc70ab';sha='986b622a4318459c68f666911b19f964ba0c129799139d5151a371bc4c8414b8'},
 @{id='RUNNER';f='Invoke-TTM-P01-L1-S1-CombinedNativeOnce-PS51.ps1';p='qa/p01/windows/S1/Invoke-TTM-P01-L1-S1-CombinedNativeOnce-PS51.ps1';blob='611ac1506176c53fc6b51de7ea54d228a161bb98';sha='463789ce69aa025271e36e6748339b89a626f82a3bdf61b1738b881c27a02505'},
 @{id='ENGINE';f='TTMS1IsolatedJobWatchdogEngineV2.cs';p='qa/p01/windows/S1/TTMS1IsolatedJobWatchdogEngineV2.cs';blob='5763ca10025bb928f161a0f33fa493d436107375';sha='f8c07f486a4e373810e75ec1cf99d79414f66d7e74c65851d0ff268b949640c3'},
 @{id='QA';f='Independent-QA-S1-HostRunner-IntegratedStatic.py';p='qa/p01/windows/S1/Independent-QA-S1-HostRunner-IntegratedStatic.py';blob='46f240f23d6644ef3b81a1971d4253bb64087ecf';sha='5f1ff0d53d79b2211faa39614733d2c5c129e6d4aefacc880e9a03db98c8e49a'}
)
function StopGate([string]$m){throw ('BLOCK_'+$m)}
function ShaBytes([byte[]]$b){
 $h=[Security.Cryptography.SHA256]::Create()
 try{return ([BitConverter]::ToString($h.ComputeHash($b))).Replace('-','').ToLowerInvariant()}
 finally{$h.Dispose()}
}
function ShaFile([string]$p){return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function Run([string]$e,[string[]]$a){
 $old=$ErrorActionPreference;$ErrorActionPreference='Continue'
 try{$out=@(& $e @a 2>&1);$exitCode=$LASTEXITCODE}
 finally{$ErrorActionPreference=$old}
 return [pscustomobject]@{exit=$exitCode;out=(($out|ForEach-Object{$_.ToString()})-join [Environment]::NewLine)}
}
function DenyReparse([string]$p){
 $q=$p
 while($q){
  if(Test-Path -LiteralPath $q){
   if(((Get-Item -LiteralPath $q -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){StopGate 'REPARSE'}
  }
  $up=Split-Path -Parent $q
  if(-not $up -or $up -eq $q){break}
  $q=$up
 }
}
function SCM{
 $svc=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'"
 if($null -eq $svc -or $svc.State -ne 'Stopped' -or [int]$svc.ProcessId -ne 0 -or
    $svc.StartMode -ne 'Manual' -or $svc.StartName -ine 'NT AUTHORITY\LocalService'){StopGate 'SCM'}
 return [ordered]@{state=$svc.State;pid=[int]$svc.ProcessId;image=$svc.PathName;account=$svc.StartName}
}
function Fetch($p,$blob,$sha){
 $response=Run 'gh.exe' @('api',('repos/minhtri22/TokenToModel-Lab/contents/'+$p+'?ref='+$ref))
 if($response.exit -ne 0){StopGate 'GITHUB_FETCH'}
 $obj=$response.out|ConvertFrom-Json
 if($obj.sha -cne $blob){StopGate 'GITHUB_BLOB'}
 $bytes=[Convert]::FromBase64String(($obj.content -replace '\s',''))
 if((ShaBytes $bytes) -cne $sha){StopGate 'GITHUB_SOURCE_SHA'}
 return [pscustomobject]@{data=$bytes;sha=$sha}
}
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){StopGate 'WINDOWS'}
foreach($p in @($root,$receiptRoot,$original,$stage,$marker,$python)){DenyReparse $p}
if(Test-Path -LiteralPath $marker){StopGate 'NATIVE_MARKER_ALREADY_CONSUMED'}
if(-not(Test-Path -LiteralPath $receiptRoot -PathType Container)){StopGate 'RECEIPT_ROOT'}
$head=Run 'git.exe' @('-C',$original,'rev-parse','HEAD')
$origin=Run 'git.exe' @('-C',$original,'remote','get-url','origin')
if($head.exit -ne 0 -or $head.out.Trim() -cne 'f2e333df2f9ca24a8e483507c3cfc386ad9c76f0' -or
 $origin.exit -ne 0 -or $origin.out.Trim() -cne 'https://github.com/minhtri22/TokenToModel-Lab.git'){StopGate 'FROZEN_GIT'}
$before=SCM
$runid='S1_HOST_RUNNER_STATIC_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$dir=Join-Path $receiptRoot $runid
DenyReparse $dir
if(Test-Path -LiteralPath $dir){StopGate 'QA_DIR_ALREADY_EXISTS'}
New-Item -ItemType Directory -Path $dir -ErrorAction Stop|Out-Null
$receiptPath=Join-Path $dir ($runid+'.json')
$report=[ordered]@{schema='ttm.p01.l1.s1.host_runner_windows_integrated_static.v1';
 run_id=$runid;source_commit=$ref;inputs=@();scm_before=$before;scm_after=$null;
 ps51_parser='NOT_EXECUTED';python=$null;errors=@();verdict='BLOCK';
 native_compilation='NOT_EXECUTED';S1_native='NOT_EXECUTED';SCM_action='NONE'}
$pass=$false;$github=$false
try{
 foreach($f in $files){
  $destination=Join-Path $dir $f.f
  [IO.File]::WriteAllBytes($destination,(Fetch $f.p $f.blob $f.sha).data)
  if((ShaFile $destination) -cne $f.sha){StopGate 'LOCAL_SHA'}
  $report.inputs+=@([ordered]@{key=$f.id;sha=$f.sha;blob=$f.blob})
 }
 Write-Host 'TTM_S1_STATIC_SOURCES=PASS_EXACT'
 $tokens=$null;$parseErrors=$null
 [Management.Automation.Language.Parser]::ParseFile((Join-Path $dir $files[1].f),[ref]$tokens,[ref]$parseErrors)|Out-Null
 if($null -ne $parseErrors -and @($parseErrors).Length -gt 0){
  $report['parse_errors']=@($parseErrors|ForEach-Object{$_.Message})
  StopGate 'PS51_PARSE'
 }
 $report.ps51_parser='PASS'
 Write-Host 'TTM_S1_STATIC_PS51_PARSE=PASS'
 $args=@('-B',(Join-Path $dir $files[3].f),
  '--host',(Join-Path $dir $files[0].f),
  '--runner',(Join-Path $dir $files[1].f),
  '--engine',(Join-Path $dir $files[2].f),
  '--host-sha256',$files[0].sha,'--runner-sha256',$files[1].sha,
  '--engine-sha256',$files[2].sha)
 $run=Run $python $args
 $report.python=[ordered]@{exit=$run.exit;sha256=(ShaBytes ([Text.Encoding]::UTF8.GetBytes($run.out)));
  output=$run.out.Substring(0,[Math]::Min(24000,$run.out.Length))}
 $parsed=$null
 try{$parsed=$run.out|ConvertFrom-Json}catch{$report.python['parse_error']=$_.Exception.Message}
 if($null -ne $parsed){
  $report.python['verdict']=$parsed.verdict
  $report.python['positives']=$parsed.positive_passed
  $report.python['negatives']=$parsed.negative_rejected
  $report.python['positive_failed']=$parsed.positive_failed
  $report.python['negative_failed']=$parsed.negative_failed
 }
 if($run.exit -ne 0 -or $null -eq $parsed -or
    $parsed.verdict -cne 'PASS_SOURCE_ONLY' -or
    $parsed.positive_passed -ne 66 -or $parsed.positive_total -ne 66 -or
    $parsed.negative_rejected -ne 22 -or $parsed.negative_total -ne 22){StopGate 'PYTHON_STATIC_QA'}
 Write-Host 'TTM_S1_STATIC_INTEGRATED_QA=PASS_66_66_NEG_22_22'
 $report.scm_after=SCM
 if(($report.scm_before|ConvertTo-Json -Compress) -cne
    ($report.scm_after|ConvertTo-Json -Compress)){StopGate 'SCM_CHANGED'}
 if(Test-Path $marker){StopGate 'NATIVE_MARKER_CHANGED'}
 $report.verdict='LOCAL_STATIC_PASS_PENDING_GITHUB_READBACK'
 $pass=$true
}catch{
 $report.errors+=@($_.Exception.Message)
 Write-Host ('TTM_S1_STATIC_BLOCK='+$_.Exception.Message)
}finally{
 if($null -eq $report.scm_after){
  try{$report.scm_after=SCM}catch{$report.errors+=@('SCM_AFTER_'+$_.Exception.Message);$pass=$false}
 }
 try{
  $report['utc']=[DateTime]::UtcNow.ToString('o')
  [IO.File]::WriteAllText($receiptPath,($report|ConvertTo-Json -Depth 18),(New-Object Text.UTF8Encoding $false))
  $hash=ShaFile $receiptPath
  $target='artifacts/qa/p01/'+$runid+'.json'
  $req=@{branch='audit/p01-l1-native-security-critical-fix-20261106';
    message=('qa(p01): S1 host runner integrated Windows static '+$runid);
    content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($receiptPath))}|ConvertTo-Json -Compress
  $upload=Join-Path $dir 'github_request.json'
  [IO.File]::WriteAllText($upload,$req,(New-Object Text.UTF8Encoding $false))
  $sent=Run 'gh.exe' @('api','-X','PUT',('repos/minhtri22/TokenToModel-Lab/contents/'+$target),'--input',$upload)
  if($sent.exit -ne 0){StopGate 'GITHUB_UPLOAD'}
  $commit=($sent.out|ConvertFrom-Json).commit.sha
  if($commit -cnotmatch '^[0-9a-f]{40}$'){StopGate 'GITHUB_COMMIT'}
  $get=Run 'gh.exe' @('api',('repos/minhtri22/TokenToModel-Lab/contents/'+$target+'?ref='+$commit))
  if($get.exit -ne 0){StopGate 'GITHUB_READBACK'}
  $from=$get.out|ConvertFrom-Json
  $bytes=[Convert]::FromBase64String(($from.content -replace '\s',''))
  if((ShaBytes $bytes) -cne $hash){StopGate 'GITHUB_READBACK_SHA'}
  $github=$true
  Write-Host ('TTM_S1_STATIC_RECEIPT='+$receiptPath)
  Write-Host ('TTM_S1_STATIC_SHA256='+$hash)
  Write-Host ('TTM_S1_STATIC_GITHUB_COMMIT='+$commit)
  Write-Host 'TTM_S1_STATIC_GITHUB_READBACK=PASS'
 }catch{Write-Host ('TTM_S1_STATIC_EVIDENCE_BLOCK='+$_.Exception.Message)}
}
Write-Host 'TTM_S1_STATIC_NATIVE=NOT_EXECUTED'
Write-Host 'TTM_S1_STATIC_SCM_ACTION=NONE'
if($pass -and $github){Write-Host 'TTM_S1_STATIC_VERDICT=PASS_WINDOWS_SOURCE_ONLY';exit 0}
Write-Host 'TTM_S1_STATIC_VERDICT=BLOCK';exit 3
