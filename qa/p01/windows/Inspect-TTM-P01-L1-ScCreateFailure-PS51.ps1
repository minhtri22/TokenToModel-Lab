#requires -Version 5.1
# TTM P01 L1: READ ONLY inventory after SC_CREATE_FAILED; GitHub evidence write only.
[CmdletBinding()] param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$repo='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=Join-Path $repo 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $repo 'worktrees\_ttm_p01_l1_service_provision_20261106'
$branch='audit/p01-l1-native-security-critical-fix-20261106'
$head='f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$exe=Join-Path $stage 'broker_service\TTMP01Broker.fixed.exe'
$expectedExe='56a780db6aa61fdd556540da340a3be223df2e41e1a7295bb33d05628dbf87ef'
$id='L1_SC_CREATE_READONLY_DIAGNOSTIC_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[guid]::NewGuid().ToString('N').Substring(0,8)
$receiptDir=Join-Path $repo ('worktrees\_ttm_p01_l1_qa_receipts\'+$id)
$r=[ordered]@{schema='ttm.p01.l1.sc_create_readonly_diagnostic.v1';run_id=$id;source_failure_commit='e4d3cee3935759f351d9fdeb0c19f57b41b1f5da';original_head=$head;checks=[ordered]@{};verdict='BLOCK_DIAGNOSTIC_ONLY';errors=@();W01_W12='NOT_EXECUTED';L1_grouped_QA='NOT_AUTHORIZED';account_or_service_changed=$false}
function Set-Check([string]$key,[string]$value,[string]$reason) {
 $r.checks[$key]=[ordered]@{status=$value;detail=$reason}
 Write-Host ('TTM_DIAG_'+$key+'='+$value)
}
function Fail([string]$why){throw [InvalidOperationException]::new($why)}
try {
 if(-not(Test-Path -LiteralPath $wt -PathType Container)){Fail 'EXACT_WORKTREE_ABSENT'}
 $original=(& git.exe -C $wt rev-parse HEAD)
 if($LASTEXITCODE -ne 0 -or $original.Trim() -cne $head){Fail 'ORIGINAL_HEAD_MISMATCH'}
 $origin=(& git.exe -C $wt remote get-url origin)
 if($LASTEXITCODE -ne 0 -or $origin.Trim() -ine 'https://github.com/minhtri22/TokenToModel-Lab.git'){Fail 'ORIGIN_MISMATCH'}
 Set-Check 'LOCAL_HEAD' 'PASS' 'Original HEAD pinned; no Git writes'
 if(-not(Test-Path -LiteralPath $exe -PathType Leaf)){Fail 'VERIFIED_BINARY_ABSENT'}
 $hash=(Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash.ToLowerInvariant()
 if($hash -cne $expectedExe){Fail 'EXE_SHA256_MISMATCH'}
 Set-Check 'BINARY_SHA256' 'PASS' $hash
 $user=Get-LocalUser -Name 'TTMP01Worker' -ErrorAction SilentlyContinue
 if($null -eq $user){Set-Check 'WORKER_ACCOUNT' 'BLOCK' 'Worker account missing'}
 else {Set-Check 'WORKER_ACCOUNT' 'PRESENT_NOT_REATTESTED' ('SID='+$user.SID.Value+';Enabled='+$user.Enabled)}
 $svc=Get-Service -Name 'TTMP01Broker' -ErrorAction SilentlyContinue
 if($null -eq $svc){Set-Check 'SERVICE' 'ABSENT' 'SCM service not found'}
 else {Set-Check 'SERVICE' 'PRESENT_DO_NOT_RECREATE' ('Status='+$svc.Status.ToString())}
 $query=@(& sc.exe query 'TTMP01Broker' 2>&1)
 $r['sc_query_exit']=$LASTEXITCODE
 $r['sc_query_lines']=@($query | ForEach-Object {"$_"})
 $qc=@(& sc.exe qc 'TTMP01Broker' 2>&1)
 $r['sc_qc_exit']=$LASTEXITCODE
 $r['sc_qc_lines']=@($qc|ForEach-Object {"$_"})
 foreach($name in @('broker_service','evidence')) {
  $p=Join-Path $stage $name
  if(-not(Test-Path -LiteralPath $p -PathType Container)){
   Set-Check ('DIR_'+$name.ToUpperInvariant()) 'ABSENT' 'Expected directory absent'
  } else {
   $acl=Get-Acl -LiteralPath $p
   $rules=@($acl.Access | ForEach-Object {($_.IdentityReference.Value+':'+$_.FileSystemRights.ToString()+':'+$_.AccessControlType.ToString())})
   $r.checks['DIR_'+$name.ToUpperInvariant()]=[ordered]@{status='PRESENT_ACL_READBACK_ONLY';owner=$acl.Owner;protected=$acl.AreAccessRulesProtected;rules=$rules}
   Write-Host ('TTM_DIAG_DIR_'+$name.ToUpperInvariant()+'=PRESENT_ACL_READBACK_ONLY')
  }
 }
 $cred=Join-Path $stage 'broker_service\worker_credential.dpapi.xml'
 Set-Check 'CREDENTIAL_FILE' $(if(Test-Path -LiteralPath $cred -PathType Leaf){'PRESENT_NO_CONTENT_READ'}else{'ABSENT'}) 'Credential bytes and password never read'
 $ledger=Join-Path $stage 'evidence\broker_ledger.sqlite3'
 Set-Check 'LEDGER_FILE' $(if(Test-Path -LiteralPath $ledger -PathType Leaf){'PRESENT_NOT_MODIFIED'}else{'ABSENT'}) 'No ledger write or read'
 $r.verdict='READONLY_DIAGNOSTIC_COMPLETE_NO_PROVISION'
} catch {
 $r.errors+= $_.Exception.Message
 $r.verdict='BLOCK_READONLY_DIAGNOSTIC'
 Write-Host ('TTM_DIAG_BLOCK='+$_.Exception.Message)
} finally {
 try {
  New-Item -ItemType Directory -Path $receiptDir -Force|Out-Null
  $r['utc']=[DateTime]::UtcNow.ToString('o')
  $file=Join-Path $receiptDir ($id+'.json')
  [IO.File]::WriteAllText($file,($r|ConvertTo-Json -Depth 12),(New-Object Text.UTF8Encoding $false))
  $sha=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
  Write-Host ('TTM_DIAG_RECEIPT='+$file)
  Write-Host ('TTM_DIAG_SHA256='+$sha)
  $request=Join-Path $receiptDir 'github_create.json'
  $apiPath='artifacts/qa/p01/'+$id+'.json'
  $body=@{branch=$branch;message=('evidence(p01): read-only SC_CREATE failure inventory '+$id);content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($file))}|ConvertTo-Json -Compress
  [IO.File]::WriteAllText($request,$body,(New-Object Text.UTF8Encoding $false))
  $response=@(& gh api -X PUT ('repos/minhtri22/TokenToModel-Lab/contents/'+$apiPath) --input $request 2>&1)
  if($LASTEXITCODE -ne 0){Fail 'GITHUB_EVIDENCE_UPLOAD_FAILED'}
  $created=($response -join [Environment]::NewLine)|ConvertFrom-Json
  $readback=@(& gh api ('repos/minhtri22/TokenToModel-Lab/contents/'+$apiPath+'?ref='+$created.commit.sha) 2>&1)
  if($LASTEXITCODE -ne 0){Fail 'GITHUB_EVIDENCE_READBACK_FAILED'}
  $back=($readback -join [Environment]::NewLine)|ConvertFrom-Json
  $hasher=[Security.Cryptography.SHA256]::Create()
  try {$backSha=([BitConverter]::ToString($hasher.ComputeHash([Convert]::FromBase64String(($back.content -replace '\s',''))))).Replace('-','').ToLowerInvariant()}
  finally {$hasher.Dispose()}
  if($backSha -cne $sha){Fail 'EVIDENCE_SHA256_READBACK_MISMATCH'}
  Write-Host ('TTM_DIAG_GITHUB_COMMIT='+$created.commit.sha)
  Write-Host 'TTM_DIAG_GITHUB_READBACK=PASS'
  $exit=if($r.verdict -eq 'READONLY_DIAGNOSTIC_COMPLETE_NO_PROVISION'){0}else{3}
 } catch {
  Write-Host ('TTM_DIAG_GITHUB_READBACK=FAIL '+$_.Exception.Message)
  $exit=5
 }
}
Write-Host 'TTM_W01_W12=NOT_EXECUTED'
Write-Host 'TTM_L1_GROUPED_QA=NOT_AUTHORIZED'
exit $exit
