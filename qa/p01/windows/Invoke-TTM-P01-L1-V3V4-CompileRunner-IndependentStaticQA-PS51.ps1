#requires -Version 5.1
# TTM P01 L1: independent Windows PS5.1 PARSE and source-only QA.
# Never invokes the target compile runner or csc.exe.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$tools=Join-Path $root 'worktrees\_ttm_p01_l1_tools'
$original=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$sourceCommit='9bd43e88752448d7bdb9d5941ebef8c3ed269d4e'
$pin=@(
 @{name='RUNNER';path='qa/p01/windows/Invoke-TTM-P01-L1-V3V4-ExactSource-CompileOnly-PS51.ps1';blob='a3a130a17d54598631aafd2706d0341a990ee971';filename='Invoke-TTM-P01-L1-V3V4-ExactSource-CompileOnly-PS51.ps1'},
 @{name='QA';path='qa/p01/windows/Independent-Audit-TTM-V3V4-CompileRunner-Static.py';blob='1448fcd2a697a00babf49b1bf3942388188765af';filename='Independent-Audit-TTM-V3V4-CompileRunner-Static.py'}
)
$marker=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106\L1_V3_V4_COMPILE_RUNNER_INDEPENDENT_STATIC_QA_ATTEMPT_20261107.lock'
$id='L1_V3_V4_COMPILE_RUNNER_INDEPENDENT_STATIC_QA_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $root ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$rec=[ordered]@{
 schema='ttm.p01.l1.v3v4.compile_runner_windows_static_qa.v1'
 run_id=$id;source_commit=$sourceCommit;checks=[ordered]@{}
 source_files=@();parse_errors=@();python_checker=[ordered]@{}
 one_shot_marker_sha256=$null;verdict='BLOCK';errors=@()
 csc_executed=$false;service_action='NONE';SCM_changed=$false
 W01_W12='NOT_EXECUTED';L1_grouped_QA='NOT_AUTHORIZED'
}
function Gate([string]$key,[string]$status,[string]$detail){
 $rec.checks[$key]=@{status=$status;detail=$detail}
 Write-Host ('TTM_CSC_QA_'+$key+'='+$status)
}
function Fail([string]$why){throw [InvalidOperationException]::new($why)}
function Sha([string]$path){return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function ShaBytes([byte[]]$bytes){
 $hasher=[Security.Cryptography.SHA256]::Create()
 try{return ([BitConverter]::ToString($hasher.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()}
 finally{$hasher.Dispose()}
}
function NoReparse([string]$path){
 while($path -and (Test-Path -LiteralPath $path)){
  $item=Get-Item -LiteralPath $path -Force
  if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Fail 'REPARSE_BOUNDARY'}
  $parent=Split-Path -Parent $path;if($parent -eq $path){break};$path=$parent
 }
}
try{
 $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin){Fail 'ADMIN_REQUIRED'}
 foreach($p in @($root,$tools,$original,$receiptDir,$marker)){NoReparse $p}
 if(-not(Test-Path -LiteralPath $tools -PathType Container)){Fail 'TTM_TOOLS_MISSING'}
 $head=(& git.exe -C $original rev-parse HEAD)
 if($LASTEXITCODE -ne 0 -or $head.Trim() -cne 'f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'){Fail 'ORIGINAL_HEAD_CHANGED'}
 Gate 'ORIGINAL' 'PASS' 'Frozen research HEAD read-only'
 $py=Join-Path $env:USERPROFILE 'miniforge3\python.exe'
 if(-not(Test-Path -LiteralPath $py -PathType Leaf)){Fail 'PINNED_PYTHON_MISSING'}
 & gh.exe auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Fail 'GITHUB_AUTH_FAILED'}
 # One-shot marker checked before the download; atomic CreateNew later.
 if(Test-Path -LiteralPath $marker){Fail 'STATIC_QA_MARKER_ALREADY_EXISTS_NO_REPLAY'}
 New-Item -ItemType Directory -Path $receiptDir -ErrorAction Stop | Out-Null
 foreach($item in $pin){
  $uri='repos/minhtri22/TokenToModel-Lab/contents/'+$item.path+'?ref='+$sourceCommit
  $raw=@(& gh.exe api $uri 2>&1)
  if($LASTEXITCODE -ne 0){Fail ('SOURCE_FETCH_FAILED_'+$item.name)}
  $doc=($raw -join [Environment]::NewLine)|ConvertFrom-Json
  if($doc.sha -cne $item.blob){Fail ('SOURCE_BLOB_MISMATCH_'+$item.name)}
  $destination=Join-Path $receiptDir $item.filename
  NoReparse $destination
  if(Test-Path -LiteralPath $destination){Fail 'SOURCE_ALREADY_EXISTS'}
  [IO.File]::WriteAllBytes($destination,[Convert]::FromBase64String(($doc.content -replace '\s','')))
  $rec.source_files+=@([ordered]@{name=$item.name;git_blob=$item.blob;sha256=(Sha $destination);path=$destination})
  Gate ('SOURCE_'+$item.name) 'PASS_EXACT_BLOB' $item.blob
 }
 $runner=Join-Path $receiptDir $pin[0].filename
 $qa=Join-Path $receiptDir $pin[1].filename
 $tokens=$null;$parseErrors=$null
 [Management.Automation.Language.Parser]::ParseFile($runner,[ref]$tokens,[ref]$parseErrors)|Out-Null
 $rec.parse_errors=@($parseErrors|ForEach-Object {$_.ToString()})
 if($rec.parse_errors.Count -ne 0){Fail 'POWERSHELL51_PARSE_FAILED'}
 Gate 'PS51_PARSE' 'PASS_ZERO_ERRORS' 'Native PowerShell 5.1 AST parser'
 # Reserve exact QA attempt before executing independent Python fixture checker.
 $bytes=[Text.Encoding]::UTF8.GetBytes(('run_id='+$id+[Environment]::NewLine+'source_commit='+$sourceCommit+[Environment]::NewLine))
 $fs=[IO.File]::Open($marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
 try{$fs.Write($bytes,0,$bytes.Length);$fs.Flush()}finally{$fs.Dispose()}
 $rec.one_shot_marker_sha256=Sha $marker
 Gate 'ONE_SHOT_MARKER' 'PASS_CREATED' 'No replay; no cleanup'
 $prior=$ErrorActionPreference;$ErrorActionPreference='Continue'
 try{$output=@(& $py -B $qa --runner $runner 2>&1);$pythonExit=$LASTEXITCODE}
 finally{$ErrorActionPreference=$prior}
 $transcript=(($output|ForEach-Object {$_.ToString()}) -join [Environment]::NewLine)
 $parsed=$null
 try{$parsed=$transcript|ConvertFrom-Json}catch{
  $rec.python_checker=[ordered]@{exit_code=$pythonExit;error=$transcript.Substring(0,[Math]::Min(4096,$transcript.Length))}
 }
 if($null -eq $parsed -or $pythonExit -ne 0){Fail 'INDEPENDENT_PYTHON_STATIC_QA_FAILED'}
 $rec.python_checker=[ordered]@{
  exit_code=$pythonExit;verdict=$parsed.verdict
  positive_total=$parsed.positive_total;positive_pass=$parsed.positive_pass
  negative_total=$parsed.negative_total;negative_rejected=$parsed.negative_rejected
  failed=@($parsed.failed);negative_fail=@($parsed.negative_fail)
  runner_sha256=$parsed.runner_sha256
 }
 if($parsed.verdict -cne 'PASS_SOURCE_ONLY_NO_NATIVE_PARSE' -or
    $parsed.positive_total -lt 40 -or $parsed.positive_pass -ne $parsed.positive_total -or
    $parsed.negative_total -ne 12 -or $parsed.negative_rejected -ne 12 -or
    $parsed.runner_sha256 -cne (Sha $runner)){Fail 'STATIC_QA_CONTRACT_NOT_PASS'}
 Gate 'PYTHON_STATIC_QA' 'PASS_SOURCE_ONLY' ('Positive='+$parsed.positive_pass+'/'+$parsed.positive_total+';Negative='+$parsed.negative_rejected+'/12')
 $rec.verdict='PASS_WINDOWS_PS51_PARSE_AND_INDEPENDENT_SOURCE_QA_NO_COMPILATION'
}catch{
 $rec.errors+=$_.Exception.Message
 $rec.verdict='BLOCK_WINDOWS_SOURCE_QA'
 Write-Host ('TTM_CSC_QA_BLOCK='+$_.Exception.Message)
}finally{
 $published=$false
 try{
  New-Item -ItemType Directory -Path $receiptDir -Force | Out-Null
  $rec['utc']=[DateTime]::UtcNow.ToString('o')
  $outFile=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($outFile,($rec|ConvertTo-Json -Depth 16),(New-Object Text.UTF8Encoding $false))
  $sha=Sha $outFile
  Write-Host ('TTM_CSC_QA_RECEIPT='+$outFile)
  Write-Host ('TTM_CSC_QA_SHA256='+$sha)
  $target='artifacts/qa/p01/'+$id+'.json'
  $request=Join-Path $receiptDir 'github_create.json'
  $payload=@{branch=$branch;message=('evidence(p01): independent V3V4 compile runner PS51 static QA '+$id);
      content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($outFile))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$payload,(New-Object Text.UTF8Encoding $false))
  $sent=@(& gh.exe api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$target) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Fail 'GITHUB_UPLOAD_FAILED'}
  $saved=($sent -join [Environment]::NewLine)|ConvertFrom-Json
  $back=@(& gh.exe api ('repos/minhtri22/TokenToModel-Lab/contents/'+$target+'?ref='+$saved.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Fail 'GITHUB_READBACK_FAILED'}
  $remote=($back -join [Environment]::NewLine)|ConvertFrom-Json
  $hash=ShaBytes ([Convert]::FromBase64String(($remote.content -replace '\s','')))
  if($hash -cne $sha){Fail 'GITHUB_SHA256_MISMATCH'}
  $published=$true
  Write-Host ('TTM_CSC_QA_GITHUB_COMMIT='+$saved.commit.sha)
  Write-Host 'TTM_CSC_QA_GITHUB_READBACK=PASS'
 }catch{Write-Host ('TTM_CSC_QA_GITHUB_READBACK=FAIL '+$_.Exception.Message)}
}
Write-Host 'TTM_CSC_QA_COMPILER_EXECUTED=NO'
Write-Host 'TTM_CSC_QA_SCM_ACTION=NONE'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
if($published -and $rec.verdict -eq 'PASS_WINDOWS_PS51_PARSE_AND_INDEPENDENT_SOURCE_QA_NO_COMPILATION'){exit 0}
exit 3
