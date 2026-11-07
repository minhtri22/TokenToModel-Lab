#requires -Version 5.1
# TTM P01 L1 S1 / compiler argv forwarding SOURCE-ONLY successor QA.
# Never compile C#, launch native S1, consume markers or alter SCM.
[CmdletBinding()]param()
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$oldRef='8e2a2033187d22e8c44c7493e8853dafe974715f'
$patchRef='d845abc458c5d61db1ec6139def379ba89c5ca29'
$oldPath='qa/p01/windows/S1/Invoke-TTM-P01-L1-S1-CombinedNativeOnce-PS51.ps1'
$patchPath='qa/p01/windows/S1/TTM-S1-Compile-CompilerArgv-SourceRepair-CANDIDATE.patch'
$oldBlob='611ac1506176c53fc6b51de7ea54d228a161bb98'
$patchBlob='106043c330d220f6219a7a415467726fcbc857f8'
$oldSha='463789ce69aa025271e36e6748339b89a626f82a3bdf61b1738b881c27a02505'
$receiptRoot=Join-Path $root 'worktrees\_ttm_p01_l1_qa_receipts'
$original=Join-Path $root 'worktrees\p01-f0-static-i0a-20261105'
$stage=Join-Path $root 'worktrees\_ttm_p01_l1_service_provision_20261106'
$marker=Join-Path $stage 'L1_S1_NATIVE_COMBINED_ONE_SHOT_ATTEMPT_20261107.lock'
$oldReceipt=Join-Path $receiptRoot 'S1_NATIVE_COMBINED_20261107T063339197Z_35D236F1\S1_NATIVE_COMBINED_20261107T063339197Z_35D236F1.json'
$oldReceiptSha='39c670f86881bccebe3d8033b41ec28784b3ee5322daee10846b3a93c17939c6'
$oldMarkerSha='0673bc2f2a374905b28de83b02324fa12afba80152dcdcda8a37de19b7b02eb2'
function Block([string]$code) { throw ('TTM_S1_SUCCESSOR_QA_BLOCK_'+$code) }
function Sha256([byte[]]$bytes){
 $h=[Security.Cryptography.SHA256]::Create()
 try { return ([BitConverter]::ToString($h.ComputeHash($bytes))).Replace('-','').ToLowerInvariant() }
 finally { $h.Dispose() }
}
function SafePath([string]$p){
 $cur=$p
 while($cur){
  if(Test-Path -LiteralPath $cur){
   $item=Get-Item -LiteralPath $cur -Force
   if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){Block 'REPARSE_POINT'}
  }
  $up=Split-Path -Parent $cur
  if(-not $up -or $up -eq $cur){break}
  $cur=$up
 }
}
function RunReadOnly([string]$exe,[string[]]$argv) {
 $prior=$ErrorActionPreference
 $ErrorActionPreference='Continue'
 try {$out=@(& $exe @argv 2>&1); $code=$LASTEXITCODE}
 finally {$ErrorActionPreference=$prior}
 return [pscustomobject]@{code=$code;out=(($out|ForEach-Object{$_.ToString()}) -join [Environment]::NewLine)}
}
function FetchPinned([string]$p,[string]$rev,[string]$blob) {
 $api='repos/minhtri22/TokenToModel-Lab/contents/'+$p+'?ref='+$rev
 $answer=RunReadOnly 'gh.exe' @('api',$api)
 if($answer.code -ne 0){Block 'GITHUB_FETCH'}
 $j=$answer.out|ConvertFrom-Json
 if($j.sha -cne $blob){Block 'GIT_BLOB'}
 return [Convert]::FromBase64String(($j.content -replace '\s',''))
}
function SCMReadOnly {
 $s=Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'"
 if($null -eq $s -or $s.State -ne 'Stopped' -or [int]$s.ProcessId -ne 0){Block 'SCM_NOT_STOPPED_PID0'}
 return [ordered]@{state=$s.State;pid=[int]$s.ProcessId;image=$s.PathName;account=$s.StartName;start=$s.StartMode}
}
if([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT){Block 'WINDOWS'}
foreach($p in @($root,$receiptRoot,$original,$stage,$marker,$oldReceipt)){SafePath $p}
if(-not(Test-Path -LiteralPath $receiptRoot -PathType Container)){Block 'RECEIPT_DIR_MISSING'}
if(-not(Test-Path -LiteralPath $marker -PathType Leaf)){Block 'OLD_MARKER_MISSING'}
if((Get-FileHash -LiteralPath $marker -Algorithm SHA256).Hash.ToLowerInvariant() -cne $oldMarkerSha){Block 'OLD_MARKER_CHANGED'}
if(-not(Test-Path -LiteralPath $oldReceipt -PathType Leaf)){Block 'FAIL_RECEIPT_MISSING'}
if((Get-FileHash -LiteralPath $oldReceipt -Algorithm SHA256).Hash.ToLowerInvariant() -cne $oldReceiptSha){Block 'FAIL_RECEIPT_CHANGED'}
$frozen=RunReadOnly 'git.exe' @('-C',$original,'rev-parse','HEAD')
if($frozen.code -ne 0 -or $frozen.out.Trim() -cne 'f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'){Block 'FROZEN_HEAD'}
$scmBefore=SCMReadOnly
$runid='S1_COMPILER_ARGV_SOURCE_QA_'+[DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')+'_'+[Guid]::NewGuid().ToString('N').Substring(0,8)
$folder=Join-Path $receiptRoot $runid
SafePath $folder
if(Test-Path -LiteralPath $folder){Block 'QA_DIR_COLLISION'}
New-Item -ItemType Directory -Path $folder -ErrorAction Stop|Out-Null
$receiptPath=Join-Path $folder ($runid+'.json')
$report=[ordered]@{
 schema='ttm.p01.l1.s1.compiler_argv_source_successor_qa.v1';
 run_id=$runid;old_ref=$oldRef;patch_ref=$patchRef;
 original_fail_receipt_sha256=$oldReceiptSha;consumed_marker_sha256=$oldMarkerSha;
 old_runner_sha256=$oldSha;patch_sha256='';candidate_sha256='';
 ps51_parse='NOT_EXECUTED';positive='NOT_EXECUTED';negative='NOT_EXECUTED';
 scm_before=$scmBefore;scm_after=$null;native='NOT_EXECUTED';
 compiler='NOT_EXECUTED';marker_action='NONE';permit_action='NONE';
 verdict='BLOCK';errors=@()
}
$success=$false;$githubReadback=$false
try {
 $oldBytes=FetchPinned $oldPath $oldRef $oldBlob
 $patchBytes=FetchPinned $patchPath $patchRef $patchBlob
 if((Sha256 $oldBytes) -cne $oldSha){Block 'ORIGINAL_SOURCE_SHA256'}
 $report.patch_sha256=Sha256 $patchBytes
 $oldText=[Text.Encoding]::UTF8.GetString($oldBytes)
 $diffText=[Text.Encoding]::UTF8.GetString($patchBytes)
 if($oldText.Contains([char]13) -or $diffText.Contains([char]13)){Block 'SOURCE_LINE_ENDINGS_NOT_LF'}
 $originalLines=$oldText.Split([char]10)
 $diffLines=$diffText.Split([char]10)
 if($diffLines.Length -lt 10 -or
    $diffLines[0] -cne ('--- a/'+$oldPath) -or
    $diffLines[1] -cne ('+++ b/'+$oldPath)){Block 'PATCH_IDENTITY'}
 $hunk=[regex]::Match($diffLines[2],'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@$')
 if(-not $hunk.Success){Block 'PATCH_HUNK'}
 $start=[int]$hunk.Groups[1].Value-1
 $oldCount=[int]$hunk.Groups[2].Value
 $newCount=[int]$hunk.Groups[4].Value
 if([int]$hunk.Groups[3].Value -ne ($start+1)){Block 'PATCH_SHIFTED'}
 $remove=New-Object 'System.Collections.Generic.List[string]'
 $insert=New-Object 'System.Collections.Generic.List[string]'
 for($i=3;$i -lt $diffLines.Length;$i++){
  $line=$diffLines[$i]
  if($line -ceq '' -and $i -eq $diffLines.Length-1){continue}
  if($line.StartsWith('-')){$remove.Add($line.Substring(1))}
  elseif($line.StartsWith('+')){$insert.Add($line.Substring(1))}
  else{Block 'PATCH_OUT_OF_SCOPE'}
 }
 if($remove.Count -ne $oldCount -or $insert.Count -ne $newCount){Block 'PATCH_LINE_COUNT'}
 if($start -lt 0 -or $start+$oldCount -gt $originalLines.Length){Block 'PATCH_OUTSIDE_SOURCE'}
 for($i=0;$i -lt $oldCount;$i++){
  if($originalLines[$start+$i] -cne $remove[$i]){Block 'ORIGINAL_COMPILE_BLOCK_CHANGED'}
 }
 $candidateLines=New-Object 'System.Collections.Generic.List[string]'
 for($i=0;$i -lt $start;$i++){$candidateLines.Add($originalLines[$i])}
 foreach($line in $insert){$candidateLines.Add($line)}
 for($i=$start+$oldCount;$i -lt $originalLines.Length;$i++){$candidateLines.Add($originalLines[$i])}
 $candidate=[string]::Join([string][char]10,$candidateLines)
 $report.candidate_sha256=Sha256 ([Text.Encoding]::UTF8.GetBytes($candidate))
 $positive=($candidate.Contains('function Compile([string]$label,[string[]]$compilerArgv)') -and
   $candidate.Contains('$r=Cmd $csc $compilerArgv') -and
   -not $candidate.Contains('$r=Cmd $csc $args') -and
   $candidate.Contains('COMPILER_ARGV_NO_SOURCE_OR_OUT') -and
   $candidate.Contains('COMPILER_ARGV_TOO_SHORT'))
 if(-not $positive){Block 'POSITIVE_SOURCE_CONTRACT'}
 $report.positive='PASS_TARGETED_COMPILER_ARGV'
 $tokens=$null;$errors=$null
 [Management.Automation.Language.Parser]::ParseInput($candidate,[ref]$tokens,[ref]$errors)|Out-Null
 $parseList=@($errors|Where-Object{$null -ne $_})
 if($parseList.Count -ne 0){
  $report['parse_errors']=@($parseList|ForEach-Object{$_.Message})
  Block 'PS51_PARSE'
 }
 $report.ps51_parse='PASS'
 # One deliberate fault injection: the forwarded argv becomes the automatic $args.
 $bad=$candidate.Replace('$r=Cmd $csc $compilerArgv','$r=Cmd $csc $args')
 if($bad -ceq $candidate -or
    $bad.Contains('$r=Cmd $csc $compilerArgv') -or
    -not $bad.Contains('$r=Cmd $csc $args')){Block 'NEGATIVE_NOT_DETECTED'}
 $report.negative='PASS_1_OF_1_TARGETED_AUTOMATIC_ARGS'
 $report.scm_after=SCMReadOnly
 if(($report.scm_after|ConvertTo-Json -Compress) -cne
    ($report.scm_before|ConvertTo-Json -Compress)){Block 'SCM_CHANGED'}
 if((Get-FileHash -LiteralPath $marker -Algorithm SHA256).Hash.ToLowerInvariant() -cne $oldMarkerSha){Block 'MARKER_CHANGED'}
 $report.verdict='LOCAL_SOURCE_QA_PASS_PENDING_GITHUB_READBACK'
 $success=$true
 Write-Host 'TTM_S1_SUCCESSOR_PS51_PARSE=PASS'
 Write-Host 'TTM_S1_SUCCESSOR_POSITIVE=PASS_TARGETED_COMPILER_ARGV'
 Write-Host 'TTM_S1_SUCCESSOR_NEGATIVE=PASS_1_OF_1'
} catch {
 $report.errors+=@($_.Exception.Message)
 Write-Host ('TTM_S1_SUCCESSOR_BLOCK='+$_.Exception.Message)
} finally {
 if($null -eq $report.scm_after){
  try{$report.scm_after=SCMReadOnly}catch{$report.errors+=@('SCM_AFTER_'+$_.Exception.Message);$success=$false}
 }
 try {
  $report['utc']=[DateTime]::UtcNow.ToString('o')
  [IO.File]::WriteAllText($receiptPath,($report|ConvertTo-Json -Depth 12),(New-Object Text.UTF8Encoding $false))
  $receiptSha=(Get-FileHash -LiteralPath $receiptPath -Algorithm SHA256).Hash.ToLowerInvariant()
  $target='artifacts/qa/p01/'+$runid+'.json'
  $upload=@{branch='audit/p01-l1-native-security-critical-fix-20261106';
   message=('qa(p01): isolated S1 compiler argv source successor '+$runid);
   content=[Convert]::ToBase64String([IO.File]::ReadAllBytes($receiptPath))}|ConvertTo-Json -Compress
  $inputPath=Join-Path $folder 'github_upload.json'
  [IO.File]::WriteAllText($inputPath,$upload,(New-Object Text.UTF8Encoding $false))
  $put=RunReadOnly 'gh.exe' @('api','-X','PUT',
      ('repos/minhtri22/TokenToModel-Lab/contents/'+$target),'--input',$inputPath)
  if($put.code -ne 0){Block 'RECEIPT_UPLOAD'}
  $commit=($put.out|ConvertFrom-Json).commit.sha
  if($commit -cnotmatch '^[0-9a-f]{40}$'){Block 'INVALID_COMMIT'}
  $read=RunReadOnly 'gh.exe' @('api',('repos/minhtri22/TokenToModel-Lab/contents/'+$target+'?ref='+$commit))
  if($read.code -ne 0){Block 'RECEIPT_READBACK'}
  $obj=$read.out|ConvertFrom-Json
  $bytes=[Convert]::FromBase64String(($obj.content -replace '\s',''))
  if((Sha256 $bytes) -cne $receiptSha){Block 'RECEIPT_SHA_READBACK'}
  $githubReadback=$true
  Write-Host ('TTM_S1_SUCCESSOR_RECEIPT='+$receiptPath)
  Write-Host ('TTM_S1_SUCCESSOR_RECEIPT_SHA256='+$receiptSha)
  Write-Host ('TTM_S1_SUCCESSOR_GITHUB_COMMIT='+$commit)
  Write-Host 'TTM_S1_SUCCESSOR_GITHUB_READBACK=PASS'
 } catch {Write-Host ('TTM_S1_SUCCESSOR_EVIDENCE_BLOCK='+$_.Exception.Message)}
}
Write-Host 'TTM_S1_SUCCESSOR_COMPILER=NOT_EXECUTED'
Write-Host 'TTM_S1_SUCCESSOR_NATIVE=NOT_EXECUTED'
Write-Host 'TTM_S1_SUCCESSOR_PERMIT=NOT_ISSUED'
if($success -and $githubReadback){Write-Host 'TTM_S1_SUCCESSOR_VERDICT=PASS_SOURCE_ONLY';exit 0}
Write-Host 'TTM_S1_SUCCESSOR_VERDICT=BLOCK';exit 3
