#requires -Version 5.1
# TTM P01 L1: compile-only recovery after CS1513. No account/service/ACL changes.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $repo 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $repo 'worktrees\_ttm_p01_l1_service_provision_20261106\broker_service'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$base='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$commit='6109897e3697bec6a3fbadb561f1d9ec907f589a'
$blob='d15e9b8c255777098b1baafad0a9fb6d4e95df13'
$id='L1_CS1513_REPAIR_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $repo ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$r=[ordered]@{schema='ttm.p01.l1.cs1513_compile_recovery.v1';run_id=$id;source_commit=$commit;original_head=$base;checks=[ordered]@{};compiler_output=@();verdict='BLOCK';W01_W12='NOT_EXECUTED';grouped_L1='NOT_AUTHORIZED';errors=@()}
function Write-RepairCheck($name,$status,$detail) {$r.checks[$name]=@{status=$status;detail=$detail};Write-Host ('TTM_REPAIR_'+$name+'='+$status)}
function Deny($reason){throw [InvalidOperationException]::new($reason)}
function GR([string[]]$v){$out=@(& git.exe -C $wt @v 2>&1);if($LASTEXITCODE -ne 0){Deny 'GIT_READ_FAIL'};return ($out -join [char]10).Trim()}
function NoReparse($p){while($p -and (Test-Path -LiteralPath $p)){$item=Get-Item -LiteralPath $p -Force;if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Deny 'REPARSE_PATH'};$q=Split-Path -Parent $p;if($q -eq $p){break};$p=$q}}
try {
 if(-not(Test-Path -LiteralPath $stage -PathType Container)){Deny 'EXISTING_STAGING_ABSENT'}
 NoReparse $stage;NoReparse $wt
 if((GR @('rev-parse','HEAD')) -cne $base){Deny 'HEAD_MISMATCH'}
 if((GR @('branch','--show-current')) -cne 'implementation/p01-i0a-s-f0-static-20261106'){Deny 'BRANCH_MISMATCH'}
 if((GR @('remote','get-url','origin')) -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Deny 'ORIGIN_MISMATCH'}
 Write-RepairCheck 'PINNED_LOCAL' 'PASS' 'No local Git mutations'
 if(Get-Service -Name TTMP01Broker -ErrorAction SilentlyContinue){Deny 'SERVICE_ALREADY_EXISTS'}
 if(Get-LocalUser -Name TTMP01Worker -ErrorAction SilentlyContinue){Deny 'ACCOUNT_ALREADY_EXISTS'}
 $old=Join-Path $stage 'BrokerAttestationService.cs'
 if(-not(Test-Path -LiteralPath $old -PathType Leaf)){Deny 'OLD_SOURCE_MISSING'}
 $legacy=[Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($old))
 if(-not $legacy.EndsWith(('  }'+[char]10))){Deny 'UNEXPECTED_OLD_SOURCE'}
 $fixed=Join-Path $stage 'BrokerAttestationService.fixed.cs'
 $binary=Join-Path $stage 'TTMP01Broker.fixed.exe'
 if((Test-Path -LiteralPath $fixed) -or (Test-Path -LiteralPath $binary)){Deny 'RECOVERY_ALREADY_EXISTS'}
 $csc=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
 if(-not(Test-Path -LiteralPath $csc)){Deny 'CSHARP_COMPILER_MISSING'}
 $api='repos/minhtri22/TokenToModel-Lab/contents/runtime/p01/windows/BrokerAttestationService.cs?ref='+$commit
 $json=@(& gh api $api 2>&1)
 if($LASTEXITCODE -ne 0){Deny 'GH_FETCH_FAIL'}
 $src=($json -join [char]10)|ConvertFrom-Json
 if($src.sha -cne $blob){Deny 'SOURCE_GIT_BLOB_MISMATCH'}
 $bytes=[Convert]::FromBase64String(($src.content -replace '\s',''))
 if([Text.Encoding]::UTF8.GetString($bytes) -cne ($legacy+'}'+[char]10)){Deny 'MORE_THAN_ONE_BRACE_CHANGE'}
 [IO.File]::WriteAllBytes($fixed,$bytes)
 Write-RepairCheck 'FIX_SOURCE' 'PASS' 'Exact one closing brace only, old source retained'
 $lines=@(& $csc '/nologo' '/target:exe' ('/out:'+$binary) '/reference:System.dll' '/reference:System.Core.dll' '/reference:System.ServiceProcess.dll' $fixed 2>&1)
 $code=$LASTEXITCODE
 $r.compiler_output=@($lines|ForEach-Object {"$_"})
 if($code -ne 0 -or -not(Test-Path -LiteralPath $binary)){Write-RepairCheck 'WINDOWS_CSC' 'FAIL' ('exit='+$code);Deny 'WINDOWS_COMPILE_FAILED'}
 Write-RepairCheck 'WINDOWS_CSC' 'PASS' 'Exact source built; service NOT installed or started'
 $r.binary_sha256=(Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash.ToLowerInvariant()
 $r.source_sha256=(Get-FileHash -LiteralPath $fixed -Algorithm SHA256).Hash.ToLowerInvariant()
 $r.verdict='PASS_COMPILE_ONLY'
} catch {
 $r.errors+= $_.Exception.Message
 $r.verdict='BLOCK_OR_COMPILE_FAIL'
 Write-Host ('TTM_REPAIR_BLOCK='+$_.Exception.Message)
} finally {
 try {
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $r['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($file,($r|ConvertTo-Json -Depth 12),(New-Object Text.UTF8Encoding $false))
  $sha=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
  Write-Host ('TTM_REPAIR_RECEIPT='+$file)
  Write-Host ('TTM_REPAIR_SHA256='+$sha)
  $path='artifacts/qa/p01/'+$id+'.json'
  $request=Join-Path $receiptDir 'upload.json'
  $body=@{message=('evidence(p01): compile recovery '+$id);branch=$branch;content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$body,(New-Object Text.UTF8Encoding $false))
  $up=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$path) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Deny 'GITHUB_UPLOAD_FAIL'}
  $u=($up -join [char]10)|ConvertFrom-Json
  $read=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$path+'?ref='+$u.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Deny 'GITHUB_READBACK_FAIL'}
  $rr=($read -join [char]10)|ConvertFrom-Json
  $s=[Security.Cryptography.SHA256]::Create()
  try {$got=([BitConverter]::ToString($s.ComputeHash([Convert]::FromBase64String(($rr.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally {$s.Dispose()}
  if($got -cne $sha){Deny 'GITHUB_SHA256_READBACK_MISMATCH'}
  Write-Host ('TTM_REPAIR_GITHUB_COMMIT='+$u.commit.sha)
  Write-Host 'TTM_REPAIR_GITHUB_READBACK=PASS'
  $exitCode=if($r.verdict -eq 'PASS_COMPILE_ONLY'){0}else{3}
 } catch {
  Write-Host ('TTM_REPAIR_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exitCode=5
 }
}
Write-Host 'TTM_W01_W12_NATIVE=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exitCode
