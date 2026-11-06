#requires -Version 5.1
# TTM P01 L1: exact-source independent Python static QA ON WINDOWS + compile-only PREFLIGHT.
# NEVER invokes csc, starts/stops SCM, changes account/ACL or touches science/F0.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$original=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$originalHead='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$sourceCommit='782f101f001973f8c23f23b22ae2b0896232d722'
$auditBranch='audit/p01-l1-native-security-critical-fix-20261106'
$items=@(
 @{name='BROKER_V3';path='runtime/p01/windows/BrokerAttestationServiceV3.cs';blob='2fc1b63d6e21e7d8ac86184251974e9960572f3f';file='BrokerAttestationServiceV3.cs'},
 @{name='WORKER_V4';path='qa/p01/windows/TTMWorkerNativeProbeV4.cs';blob='63d5407ccb3f9e15f8dda59ee6323a0e5009d860';file='TTMWorkerNativeProbeV4.cs'},
 @{name='INDEPENDENT_QA';path='qa/p01/windows/Independent-QA-BrokerV3-WorkerV4-Static.py';blob='0d42c4f7a4ac08c59022449210a323feed3a7495';file='Independent-QA-BrokerV3-WorkerV4-Static.py'}
)
$priorMarkers=@(
 @{name='SWITCH';file='L1_SCM_V2_SWITCH_ATTEMPT_20261106.lock';sha='29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1'},
 @{name='NATIVE';file='L1_BROKER_V2_WORKER_V3_NATIVE_SECURITY_ATTEMPT_20261106.lock';sha='f0d895e68c30b8c3845336ea8aee40d2e1ca84f96816906a952ae70ad81587c7'},
 @{name='SCM_STOP';file='L1_BROKER_V2_SCM_STOP_RECOVERY_ATTEMPT_20261106.lock';sha='f1ca3d0899fe6637a512e44dd073b449d4805ca8f8a8afa1e8a3989599143502'},
 @{name='EXACT_PROCESS';file='L1_BROKER_V2_EXACT_PROCESS_TERMINATE_ATTEMPT_20261106.lock';sha='59823e4cd684195692dc5988a4af3eb484b05c4f7e5597e34140c1e21ac01dc9'}
)
$marker=Join-Path $stage 'L1_V3_V4_INDEPENDENT_STATIC_QA_V4_ATTEMPT_20261107.lock'
$id='L1_V3_V4_WINDOWS_INDEPENDENT_STATIC_QA_V4_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$evidenceDir=Join-Path $root ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$srcDir=Join-Path $evidenceDir 'exact_sources'
$python=Join-Path $env:USERPROFILE 'miniforge3\python.exe'
$csc=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
$receipt=[ordered]@{
 schema='ttm.p01.l1.v3_v4_windows_independent_python_static_preflight.v4'
 run_id=$id
 source_commit=$sourceCommit
 original_head=$originalHead
 predecessor_block_commit='c68e7f1871db0a68f9e3a9cd54b43e87ccbb1658'
 predecessor_preqa_block_commit='ac246d1b4c8b4bea4ffda57196a77e4b9ab0d2b8'
 mode='PYTHON_STATIC_ONLY_AND_COMPILER_PRESENCE_READONLY'
 checks=[ordered]@{}
 source_files=@()
 python_identity=[ordered]@{}
 python_checker_exit=$null
 python_checker_result=[ordered]@{}
 python_checker_stdout_sha256=$null
 python_checker_stderr=$null
 compiler_preflight=[ordered]@{}
 system_capacity=[ordered]@{}
 qa_marker_sha256=$null
 verdict='BLOCK'
 errors=@()
 service_started=$false
 scm_changed=$false
 windows_csc_executed=$false
 binary_compiled=$false
 marker_cleanup=$false
 W01_W12='NOT_EXECUTED'
 L1_grouped_QA='NOT_AUTHORIZED'
 P01='OPEN'
 P02='NOT_OPENED'
}
function Gate([string]$name,[string]$status,[string]$detail){
 $receipt.checks[$name]=[ordered]@{status=$status;detail=$detail}
 Write-Host ('TTM_V3V4_'+$name+'='+$status)
}
function Halt([string]$msg){throw [InvalidOperationException]::new($msg)}
function HashFile([string]$p){return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function HashBytes([byte[]]$bytes){
 $sha=[Security.Cryptography.SHA256]::Create()
 try{return ([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()}
 finally{$sha.Dispose()}
}
function NoReparse([string]$path){
 $current=$path
 while($current -and (Test-Path -LiteralPath $current)){
  $item=Get-Item -LiteralPath $current -Force -ErrorAction Stop
  if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Halt 'REPARSE_PATH_REFUSED'}
  $parent=Split-Path -Parent $current
  if($parent -eq $current){break}
  $current=$parent
 }
}
function GitRead([string[]]$argsList){
 $output=@(& git.exe -C $original @argsList 2>&1)
 if($LASTEXITCODE -ne 0){Halt 'FROZEN_GIT_READ_FAILED'}
 return (($output -join [Environment]::NewLine).Trim())
}
function GitHubExactBytes([string]$path,[string]$blob){
 $uri='repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$sourceCommit
 $out=@(& gh.exe api $uri 2>&1)
 if($LASTEXITCODE -ne 0){Halt 'PINNED_GITHUB_SOURCE_FETCH_FAILED'}
 $entry=($out -join [Environment]::NewLine)|ConvertFrom-Json
 if($entry.sha -cne $blob){Halt 'PINNED_SOURCE_GIT_BLOB_MISMATCH'}
 return ,([Convert]::FromBase64String(($entry.content -replace '\s','')))
}
try{
 $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin){Halt 'ADMIN_REQUIRED'}
 Gate 'ADMIN' 'PASS' 'Elevated PowerShell 5.1 on target machine'
 if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){Halt 'NOT_NATIVE_WINDOWS'}
 foreach($p in @($root,$original,$stage,$marker,$evidenceDir,$srcDir)){NoReparse $p}
 if((GitRead @('rev-parse','HEAD')) -cne $originalHead){Halt 'FROZEN_HEAD_MISMATCH'}
 if((GitRead @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Halt 'FROZEN_BRANCH_MISMATCH'}
 if((GitRead @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Halt 'FROZEN_ORIGIN_MISMATCH'}
 Gate 'ORIGINAL_HEAD' 'PASS' 'Frozen F0 worktree HEAD/branch/origin read-only'
 $scm=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $scm -or $scm.State -ne 'Stopped' -or [int]$scm.ProcessId -ne 0){Halt 'BROKER_SERVICE_NOT_STOPPED'}
 if($scm.StartMode -ne 'Manual' -or $scm.StartName -ine 'NT AUTHORITY\LocalService' -or
    $scm.PathName.Trim().Trim([char]34).Trim() -ine (Join-Path $stage 'broker_service\TTMP01Broker.attestationV2.exe')){Halt 'BROKER_SCM_CONFIG_MISMATCH'}
 Gate 'SCM_READONLY' 'PASS_STOPPED_PID0' 'No service commands issued'
 foreach($entry in $priorMarkers){
  $p=Join-Path $stage $entry.file
  NoReparse $p
  if(-not(Test-Path -LiteralPath $p -PathType Leaf)){Halt ('PREVIOUS_MARKER_MISSING_'+$entry.name)}
  if($entry.sha.Length -ne 64 -or (HashFile $p) -cne $entry.sha){Halt ('PREVIOUS_MARKER_SHA256_MISMATCH_'+$entry.name)}
  Gate ('MARKER_'+$entry.name) 'PASS_EXACT' $entry.sha
 }
 if(-not(Test-Path -LiteralPath $python -PathType Leaf)){Halt 'PINNED_MINIFORGE_PYTHON_MISSING'}
 # No quote characters inside the Python -c argument: PowerShell 5.1 native argument
 # passing can strip embedded double quotes and corrupt the command.
 $identityCode='import platform,sys;print(platform.system(),platform.node(),sys.version.split()[0],sys.maxsize.bit_length()+1,sep=chr(124))'
 $priorActionPreference=$ErrorActionPreference
 $ErrorActionPreference='Continue'
 try {
  $pver=@(& $python -B -c $identityCode 2>&1)
  $identityExit=$LASTEXITCODE
 } finally { $ErrorActionPreference=$priorActionPreference }
 if($identityExit -ne 0 -or $pver.Count -ne 1){
  $receipt.python_identity=[ordered]@{probe_exit=$identityExit;probe_output=(($pver|ForEach-Object {$_.ToString()}) -join [Environment]::NewLine)}
  Halt 'PYTHON_IDENTITY_FAILED'
 }
 $identity=([string]$pver[0]).Split('|')
 if($identity.Count -ne 4 -or $identity[0] -ne 'Windows' -or $identity[3] -ne '64'){Halt 'PYTHON_NOT_WINDOWS_X64'}
 $receipt.python_identity=[ordered]@{exe=$python;platform=$identity[0];machine=$identity[1];version=$identity[2];pointer_width=$identity[3]}
 Gate 'WINDOWS_PYTHON' 'PASS' ('Windows '+$identity[2]+' x64')
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Halt 'GH_CLI_MISSING'}
 & gh.exe auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Halt 'GITHUB_AUTH_FAILED'}
 Gate 'GITHUB_AUTH' 'PASS' 'Receipt upload and readback available'
 # Win32 GetFileAttributesW via Python STDIN. No quoted Python code is
 # passed through Windows PowerShell 5.1 native command-line arguments.
 # Does not invoke Add-Type, csc.exe, or any file-writing Python helper.
 $win32Code=@'
import ctypes
import sys
kernel=ctypes.WinDLL("kernel32",use_last_error=True)
get_attributes=kernel.GetFileAttributesW
get_attributes.argtypes=[ctypes.c_wchar_p]
get_attributes.restype=ctypes.c_uint32
attributes=get_attributes(sys.argv[1])
win32_error=ctypes.get_last_error() if attributes==0xffffffff else 0
print(str(attributes)+"|"+str(win32_error))
'@
 $native=@()
 $nativeExit=$null
 $oldPreference=$ErrorActionPreference
 $ErrorActionPreference='Continue'
 try{
  $native=@($win32Code | & $python -B - $marker 2>&1)
  $nativeExit=$LASTEXITCODE
 }finally{$ErrorActionPreference=$oldPreference}
 $nativeText=(($native|ForEach-Object {$_.ToString()}) -join [Environment]::NewLine).Trim()
 $receipt['marker_probe']=[ordered]@{
  method='PYTHON_STDIN_CTYPES_WIN32_GETFILEATTRIBUTES'
  process_exit=$nativeExit
  output=$nativeText.Substring(0,[Math]::Min($nativeText.Length,2048))
 }
 if($nativeExit -ne 0 -or $native.Count -ne 1){Halt 'NATIVE_MARKER_STDIN_PROBE_FAILED'}
 $parts=([string]$native[0]).Trim().Split('|')
 if($parts.Count -ne 2 -or $parts[0] -notmatch '^\d+$' -or $parts[1] -notmatch '^\d+$'){Halt 'NATIVE_MARKER_STDIN_PROBE_UNREADABLE'}
 $attr=[uint32]$parts[0]
 $err=[int]$parts[1]
 if($attr -ne [uint32]::MaxValue){Halt 'V3V4_STATIC_QA_V4_ALREADY_ATTEMPTED_NO_REPLAY'}
 if($err -ne 2){Halt ('STATIC_QA_V4_MARKER_ABSENCE_NOT_PROVEN_WIN32_'+$err)}
 Gate 'NEW_MARKER_ABSENCE' 'PASS_WIN32_2' 'New QA marker not present'
 New-Item -ItemType Directory -Path $evidenceDir -ErrorAction Stop|Out-Null
 New-Item -ItemType Directory -Path $srcDir -ErrorAction Stop|Out-Null
 foreach($item in $items){
  $bytes=GitHubExactBytes $item.path $item.blob
  $dest=Join-Path $srcDir $item.file
  if(Test-Path -LiteralPath $dest){Halt 'SOURCE_PATH_COLLISION'}
  [IO.File]::WriteAllBytes($dest,$bytes)
  $hash=HashFile $dest
  $receipt.source_files+=@([ordered]@{name=$item.name;git_path=$item.path;git_blob=$item.blob;sha256=$hash;bytes=$bytes.Length;local_path=$dest})
  Gate ('PIN_'+$item.name) 'PASS_EXACT_GIT_BLOB' $hash
 }
 # Durable marker: no rerun even if QA or publication later fails.
 $markerBytes=[Text.Encoding]::UTF8.GetBytes(('run_id='+$id+[Environment]::NewLine+'source_commit='+$sourceCommit+[Environment]::NewLine))
 $fs=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try{$fs.Write($markerBytes,0,$markerBytes.Length);$fs.Flush()}
 finally{$fs.Dispose()}
 $receipt.qa_marker_sha256=HashFile $marker
 Gate 'ONE_SHOT_MARKER' 'PASS_CREATED' 'Append-only; never auto delete'
 $checker=Join-Path $srcDir 'Independent-QA-BrokerV3-WorkerV4-Static.py'
 $broker=Join-Path $srcDir 'BrokerAttestationServiceV3.cs'
 $worker=Join-Path $srcDir 'TTMWorkerNativeProbeV4.cs'
 $env:PYTHONDONTWRITEBYTECODE='1'
 $env:PYTHONNOUSERSITE='1'
 $out=@(& $python -B $checker --broker $broker --worker $worker 2>&1)
 $pythonExit=$LASTEXITCODE
 $receipt.python_checker_exit=$pythonExit
 $text=($out|ForEach-Object {$_.ToString()}) -join [Environment]::NewLine
 $receipt.python_checker_stdout_sha256=HashBytes ([Text.Encoding]::UTF8.GetBytes($text))
 $checkerResult=$null
 try{$checkerResult=$text|ConvertFrom-Json}catch{ $receipt.python_checker_stderr='CHECKER_JSON_PARSE_FAILED' }
 if($null -eq $checkerResult -or $pythonExit -ne 0){Halt 'INDEPENDENT_PYTHON_CHECKER_FAILED_OR_UNREADABLE'}
 $receipt.python_checker_result=[ordered]@{
  verdict=$checkerResult.verdict
  source=$checkerResult.source
  static_checks_passed=$checkerResult.static_checks_passed
  static_checks_total=$checkerResult.static_checks_total
  static_failures=@($checkerResult.static_failures)
  negative_fixture_passed=$checkerResult.negative_fixture_passed
  negative_fixture_total=$checkerResult.negative_fixture_total
  negative_fixture_failures=@($checkerResult.negative_fixture_failures)
  structural_notes=$checkerResult.structural_notes
 }
 $brokerSha=($receipt.source_files|Where-Object {$_.name -eq 'BROKER_V3'}|Select-Object -First 1).sha256
 $workerSha=($receipt.source_files|Where-Object {$_.name -eq 'WORKER_V4'}|Select-Object -First 1).sha256
 if($checkerResult.source.broker_sha256 -cne $brokerSha -or $checkerResult.source.worker_sha256 -cne $workerSha){Halt 'CHECKER_SOURCE_SHA256_READBACK_MISMATCH'}
 if($checkerResult.verdict -cne 'PASS_SOURCE_ONLY_NO_WINDOWS_NATIVE' -or
    [int]$checkerResult.static_checks_passed -ne [int]$checkerResult.static_checks_total -or
    [int]$checkerResult.negative_fixture_passed -ne [int]$checkerResult.negative_fixture_total -or
    [int]$checkerResult.negative_fixture_total -lt 8 -or
    [int]$checkerResult.static_checks_total -lt 40){Halt 'PYTHON_STATIC_QA_NOT_PASS'}
 Gate 'INDEPENDENT_PYTHON_QA' 'PASS_SOURCE_ONLY' ('Static='+$checkerResult.static_checks_passed+'/'+$checkerResult.static_checks_total+';Negative='+$checkerResult.negative_fixture_passed+'/'+$checkerResult.negative_fixture_total)
 # Compiler and host are inspected, not invoked.
 $disk=Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'" -ErrorAction Stop
 $os=Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
 $receipt.system_capacity=[ordered]@{
   D_free_bytes=[int64]$disk.FreeSpace
   physical_free_kib=[int64]$os.FreePhysicalMemory
 }
 if([int64]$disk.FreeSpace -lt 2147483648 -or [int64]$os.FreePhysicalMemory -lt 2097152){Halt 'WINDOWS_RESOURCE_PREFLIGHT_LOW'}
 if(-not(Test-Path -LiteralPath $csc -PathType Leaf)){Halt 'WINDOWS_FRAMEWORK64_CSC_MISSING'}
 $cscInfo=Get-Item -LiteralPath $csc -Force -ErrorAction Stop
 if(($cscInfo.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Halt 'CSC_REPARSE_REFUSED'}
 $receipt.compiler_preflight=[ordered]@{
  csc_path=$csc
  sha256=HashFile $csc
  file_version=$cscInfo.VersionInfo.FileVersion
  target_broker_exe=(Join-Path $stage 'broker_service\TTMP01Broker.attestationV3.exe')
  target_worker_dll=(Join-Path $stage 'broker_service\TTMWorkerNativeProbeV4.dll')
  invocation='NOT_EXECUTED'
 }
 foreach($target in @($receipt.compiler_preflight.target_broker_exe,$receipt.compiler_preflight.target_worker_dll)){
  NoReparse $target
  if(Test-Path -LiteralPath $target){Halt 'COMPILE_OUTPUT_ALREADY_EXISTS_NO_OVERWRITE'}
 }
 Gate 'COMPILER_PREFLIGHT' 'PASS_READONLY' 'Framework64 csc available, EXE/DLL target names unused; no csc invocation'
 $receipt.verdict='PASS_WINDOWS_PYTHON_STATIC_QA_AND_COMPILE_ONLY_PREFLIGHT_NO_BINARY'
}catch{
 $receipt.errors+= $_.Exception.Message
 $receipt.verdict='BLOCK_WINDOWS_STATIC_QA_OR_PREFLIGHT'
 Write-Host ('TTM_V3V4_BLOCK='+$_.Exception.Message)
}finally{
 try{
  New-Item -ItemType Directory -Path $evidenceDir -Force|Out-Null
  $receipt['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $evidenceDir ($id+'.json')
  [IO.File]::WriteAllText($file,($receipt|ConvertTo-Json -Depth 16),(New-Object Text.UTF8Encoding $false))
  $sha=HashFile $file
  Write-Host ('TTM_V3V4_RECEIPT='+$file)
  Write-Host ('TTM_V3V4_SHA256='+$sha)
  $target='artifacts/qa/p01/'+$id+'.json'
  $request=Join-Path $evidenceDir 'github_create.json'
  $body=@{branch=$auditBranch;message=('evidence(p01): target Windows independent V3/V4 Python static QA '+$id);
    content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$body,(New-Object Text.UTF8Encoding $false))
  $saved=@(& gh.exe api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$target) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_EVIDENCE_UPLOAD_FAILED'}
  $entry=($saved -join [Environment]::NewLine)|ConvertFrom-Json
  $back=@(& gh.exe api ('repos/minhtri22/TokenToModel-Lab/contents/'+$target+'?ref='+$entry.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Halt 'GITHUB_READBACK_FAILED'}
  $doc=($back -join [Environment]::NewLine)|ConvertFrom-Json
  $got=HashBytes ([Convert]::FromBase64String(($doc.content -replace '\s','')))
  if($got -cne $sha){Halt 'GITHUB_EVIDENCE_SHA256_MISMATCH'}
  Write-Host ('TTM_V3V4_GITHUB_COMMIT='+$entry.commit.sha)
  Write-Host 'TTM_V3V4_GITHUB_READBACK=PASS'
  $code=if($receipt.verdict -eq 'PASS_WINDOWS_PYTHON_STATIC_QA_AND_COMPILE_ONLY_PREFLIGHT_NO_BINARY'){0}else{3}
 }catch{
  Write-Host ('TTM_V3V4_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $code=5
 }
}
Write-Host 'TTM_V3V4_CSC_EXECUTION=NOT_EXECUTED'
Write-Host 'TTM_V3V4_SCM_ACTION=NONE'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $code
