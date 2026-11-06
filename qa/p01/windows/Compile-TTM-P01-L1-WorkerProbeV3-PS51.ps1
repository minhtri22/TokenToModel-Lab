#requires -Version 5.1
# TTM P01 L1 — V3 WORKER CLIENT COMPILE ONLY.
# No service start/stop, SCM configuration, account, ACL, credential or ledger mutation.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $repo 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $repo 'worktrees\_ttm_p01_l1_service_provision_20261106\broker_service'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$head='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$brokerV2Exe=Join-Path $stage 'TTMP01Broker.attestationV2.exe'
$brokerV2Sha='a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a'
$probeV2=Join-Path $stage 'TTMWorkerNativeProbeV2.dll'
$probeV2Sha='ea44cc5fca81e7f1e692726502dea0ad97ab543bc86f2abef52a25e1ffa96eb6'
$probeV3Source=Join-Path $stage 'TTMWorkerNativeProbeV3.cs'
$probeV3Dll=Join-Path $stage 'TTMWorkerNativeProbeV3.dll'
$probeV3Commit='28e43406f65cd38b08e12d2061664d0202139a9c'
$probeV3GitBlob='0414705e093780a6da3b9d2466abe67586db108e'
$id='L1_WORKER_V3_COMPILE_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$evidenceDir=Join-Path $repo ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$rec=[ordered]@{
 schema='ttm.p01.l1.native_worker_v3_compile_gate.v1'
 run_id=$id
 original_head=$head
 broker_v2_sha256=$brokerV2Sha
 prior_probe_v2_sha256=$probeV2Sha
 probe_v3_source_commit=$probeV3Commit
 probe_v3_source_blob=$probeV3GitBlob
 checks=[ordered]@{}
 compiler_output=@()
 compiler_exit=$null
 artifact_sha256=[ordered]@{}
 verdict='BLOCK'
 errors=@()
 SCM_changed=$false
 service_started=$false
 ACL_changed=$false
 worker_changed=$false
 W01_W12='NOT_EXECUTED'
 L1_grouped_QA='NOT_AUTHORIZED'
}
function Gate([string]$name,[string]$value,[string]$detail) {
 $rec.checks[$name]=[ordered]@{status=$value;detail=$detail}
 Write-Host ('TTM_V3_'+$name+'='+$value)
}
function Block([string]$reason){throw [InvalidOperationException]::new($reason)}
function Sha256([string]$path){return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function ReadGit([string[]]$GitArguments){
 $out=@(& git.exe -C $wt @GitArguments 2>&1)
 if($LASTEXITCODE -ne 0){Block 'GIT_COMMAND_FAILED'}
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
try {
 $admin=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
 if(-not $admin){Block 'ADMIN_REQUIRED'}
 Gate 'ADMIN' 'PASS' 'Elevated administrator token'
 foreach($p in @($wt,$stage,$brokerV2Exe,$probeV2,$probeV3Source,$probeV3Dll)){NoReparse $p}
 if((ReadGit -GitArguments @('rev-parse','HEAD')) -cne $head){Block 'ORIGINAL_HEAD_MISMATCH'}
 if((ReadGit -GitArguments @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Block 'ORIGINAL_BRANCH_MISMATCH'}
 if((ReadGit -GitArguments @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Block 'ORIGIN_MISMATCH'}
 Gate 'PINNED_ORIGINAL' 'PASS' 'Local original read-only'
 if((Sha256 $brokerV2Exe) -cne $brokerV2Sha -or (Sha256 $probeV2) -cne $probeV2Sha){Block 'V2_BINARY_PIN_MISMATCH'}
 Gate 'ORIGINAL_BINARY_PINS' 'PASS' 'Broker V2 EXE and V2 worker DLL preserved'
 $svc=Get-Service -Name TTMP01Broker -ErrorAction Stop
 if($svc.Status -ne 'Stopped'){Block 'BROKER_SERVICE_NOT_STOPPED'}
 $cim=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'" -ErrorAction Stop
 if($null -eq $cim -or $cim.StartName -ine 'NT AUTHORITY\LocalService' -or $cim.StartMode -ne 'Manual' -or
  $cim.PathName.Trim().Trim([char]34).Trim() -ine $brokerV2Exe){Block 'SCM_V2_CONFIG_UNEXPECTED'}
 Gate 'SCM_V2_STOPPED' 'PASS' 'Broker V2 installed but not started; no SCM changes'
 if((Test-Path -LiteralPath $probeV3Source) -or (Test-Path -LiteralPath $probeV3Dll)){Block 'V3_ALREADY_ATTEMPTED_NO_OVERWRITE'}
 $rw=[int][System.IO.Pipes.PipeAccessRights]::ReadWrite
 $newInstance=[int][System.IO.Pipes.PipeAccessRights]::CreateNewInstance
 if(($rw -band $newInstance) -ne 0){Block 'PIPE_READWRITE_INCLUDES_CREATE_INSTANCE_UNEXPECTED'}
 Gate 'PIPE_CLIENT_MASK' 'PASS_EXCLUDES_CREATE_INSTANCE' ('ReadWrite='+$rw+';CreateNewInstance='+$newInstance)
 $compiler=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
 if(-not(Test-Path -LiteralPath $compiler -PathType Leaf)){Block 'WINDOWS_CSC_MISSING'}
 if(-not(Get-Command gh.exe -ErrorAction SilentlyContinue)){Block 'GH_REQUIRED'}
 & gh auth status 1>$null 2>$null
 if($LASTEXITCODE -ne 0){Block 'GH_AUTH_FAILED'}
 $api='repos/minhtri22/TokenToModel-Lab/contents/qa/p01/windows/TTMWorkerNativeProbeV3.cs?ref='+$probeV3Commit
 $raw=@(& gh api $api 2>&1)
 if($LASTEXITCODE -ne 0){Block 'PINNED_V3_SOURCE_FETCH_FAILED'}
 $source=($raw -join [Environment]::NewLine)|ConvertFrom-Json
 if($source.sha -cne $probeV3GitBlob){Block 'PINNED_V3_GIT_BLOB_MISMATCH'}
 $bytes=[Convert]::FromBase64String(($source.content -replace '\s',''))
 $sourceText=[Text.Encoding]::UTF8.GetString($bytes)
 if(-not $sourceText.Contains('PipeAccessRights.ReadWrite') -or $sourceText.Contains('PipeDirection.InOut,PipeOptions.None')){Block 'V3_CLIENT_ACCESS_CONTRACT_MISMATCH'}
 [IO.File]::WriteAllBytes($probeV3Source,$bytes)
 Gate 'V3_SOURCE_PIN' 'PASS' 'Exact source blob downloaded into new TTM filename'
 $result=@(& $compiler '/nologo' '/target:library' ('/out:'+$probeV3Dll) '/reference:System.dll' '/reference:System.Core.dll' $probeV3Source 2>&1)
 $rec.compiler_exit=$LASTEXITCODE
 $rec.compiler_output=@($result|ForEach-Object {"$_"})
 if($LASTEXITCODE -ne 0 -or -not(Test-Path -LiteralPath $probeV3Dll -PathType Leaf)){
  Gate 'WINDOWS_CSC' 'FAIL' ('Exit='+$LASTEXITCODE)
  Block 'V3_WINDOWS_COMPILATION_FAILED'
 }
 $rec.artifact_sha256=[ordered]@{source=Sha256 $probeV3Source;dll=Sha256 $probeV3Dll}
 Gate 'WINDOWS_CSC' 'PASS' 'V3 worker probe compiled natively with exact access mask'
 $rec.verdict='PASS_COMPILE_ONLY_V3_NOT_EXECUTED'
} catch {
 $rec.errors+= $_.Exception.Message
 $rec.verdict='BLOCK_OR_COMPILE_FAIL'
 Write-Host ('TTM_V3_BLOCK='+$_.Exception.Message)
} finally {
 try {
  New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
  $rec['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $evidenceDir ($id+'.json')
  [IO.File]::WriteAllText($file,($rec|ConvertTo-Json -Depth 12),(New-Object Text.UTF8Encoding $false))
  $sha=Sha256 $file
  Write-Host ('TTM_V3_EVIDENCE_LOCAL='+$file)
  Write-Host ('TTM_V3_EVIDENCE_SHA256='+$sha)
  $path='artifacts/qa/p01/'+$id+'.json'
  $request=Join-Path $evidenceDir 'github_create.json'
  $body=@{branch=$branch;message=('evidence(p01): worker V3 explicit access compile '+$id);content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$body,(New-Object Text.UTF8Encoding $false))
  $up=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$path) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_EVIDENCE_UPLOAD_FAILED'}
  $saved=($up -join [Environment]::NewLine)|ConvertFrom-Json
  $download=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$saved.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Block 'GITHUB_EVIDENCE_READBACK_FAILED'}
  $obj=($download -join [Environment]::NewLine)|ConvertFrom-Json
  $h=[Security.Cryptography.SHA256]::Create()
  try{$readhash=([BitConverter]::ToString($h.ComputeHash([Convert]::FromBase64String(($obj.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally{$h.Dispose()}
  if($readhash -cne $sha){Block 'GITHUB_EVIDENCE_SHA256_MISMATCH'}
  Write-Host ('TTM_V3_GITHUB_COMMIT='+$saved.commit.sha)
  Write-Host 'TTM_V3_GITHUB_READBACK=PASS'
  $exit=if($rec.verdict -eq 'PASS_COMPILE_ONLY_V3_NOT_EXECUTED'){0}else{3}
 } catch {
  Write-Host ('TTM_V3_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exit=5
 }
}
Write-Host 'TTM_V3_NATIVE_WORKER_PROBE=NOT_EXECUTED'
Write-Host 'TTM_V2_SERVICE_START=NOT_EXECUTED'
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exit
