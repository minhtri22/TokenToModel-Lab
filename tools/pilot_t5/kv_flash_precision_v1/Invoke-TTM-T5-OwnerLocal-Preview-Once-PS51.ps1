# TTM-T5 owner-local one-shot Preview bootstrap; PowerShell 5.1 only.
# Scope: GitHub source SHA pin, exact caller C++ from historical Downloads folder (READ ONLY),
# old probe binary/checkpoint/GGUF manifests (READ ONLY), preflight receipt within project.
# NEVER calls llama.cpp native executable or generates new reference/model output.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-fA-F]{40}$')][string]$ExpectedCommit,
    [string]$ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab'
)
$ErrorActionPreference='Stop'
# Resolve executable explicitly: PowerShell command lookup is case-insensitive.
$gitExe = (Get-Command -Name 'git.exe' -CommandType Application -ErrorAction Stop).Source
$root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
if ($root -ine 'D:\WORK\RESEARCH\TokenToModel-Lab') { throw 'PROJECT_ROOT_MISMATCH' }
$branch='research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109'
$work=Join-Path $root 'worktrees\ttm-t5-kvflash-preview-20261109'
$shaCallerExpected='8a8324a10c67c6f868fe130d6ea7c535edb6364c8d04988600163e7b4a4b828e'
$shaOldBinaryExpected='62fda558309502fdef9c736243b9a6194262fe0b5667949a0872fbe5c33e4de2'
$historicSourceDir='C:\Users\minht\Downloads\TTM_T5_F32_NUMERIC_LOCALIZATION_PS51_PRECLAIM_RECOVERY_V2_20261108'
$gguf=Join-Path $root '_tmp\ttm_t5_trained_f32_v1\TTM-Small4M-T4-step1024-F32.gguf'
$oldExe=Join-Path $root '_tmp\ttm_t5_numeric_localization_v1\build\Release\ttm_t5_layer_probe.exe'
$oldLog=Join-Path $root '_tmp\ttm_t5_numeric_localization_v1\fixture_0\native_run.log'
$oldCmake=Join-Path $root '_tmp\ttm_t5_numeric_localization_v1\build\CMakeCache.txt'
$receiptDir=Join-Path $root '_tmp\ttm_t5_f32_kvflash_owner_gate_20261109'
$marker=Join-Path $receiptDir 'OWNER_LOCAL_PREVIEW_SINGLE_20261109.json'
function Sha([string]$p) {(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
function Invoke-TTMGit {
    param(
        [Parameter(Mandatory=$true)][string[]]$Items,
        [string]$RepoPath = $root
    )
    # Git writes progress to stderr on SUCCESS; WinPS 5.1 2>&1 + Stop
    # incorrectly treats that progress as a terminating NativeCommandError.
    $savedEap = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(& $gitExe -C $RepoPath @Items 2>&1)
        $status = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $savedEap
    }
    if ($status -ne 0) {
        throw ('GIT_FAILED exit='+$status+' argv='+($Items -join ' ')+' output='+($output -join ' '))
    }
    return (($output | ForEach-Object { [string]$_ }) -join "`n").Trim()
}
function ParentNoReparse([string]$path,[string]$stop) {
    $n=[IO.Path]::GetFullPath($path)
    while($n.Length -ge $stop.Length) {
        if(Test-Path -LiteralPath $n) {
            $it=Get-Item -LiteralPath $n -Force
            if($it.Attributes -band [IO.FileAttributes]::ReparsePoint){throw ('REPARSE_PATH_DENIED '+$n)}
        }
        if($n -ieq $stop){break}
        $n=Split-Path -Path $n -Parent
        if(-not $n){throw 'PARENT_TRAVERSAL'}
    }
}
if(-not (Test-Path -LiteralPath (Join-Path $root '.git'))){throw 'PROJECT_GIT_MISSING'}
ParentNoReparse -path (Join-Path $root 'worktrees') -stop $root
ParentNoReparse -path $receiptDir -stop $root
ParentNoReparse -path $work -stop $root
if(Test-Path -LiteralPath $marker){throw 'PREVIEW_ALREADY_EXECUTED_ONE_SHOT_MARKER_EXISTS'}
$origin=Invoke-TTMGit -Items @('remote','get-url','origin')
if($origin -notmatch '^(https://github\.com/|git@github\.com:|ssh://git@github\.com/)(minhtri22/TokenToModel-Lab)(\.git)?$'){
 throw ('GIT_REMOTE_ORIGIN_NOT_CANONICAL '+$origin)
}
# Fetch writes only project-local Git metadata (FETCH_HEAD), no main checkout/merge.
$null=Invoke-TTMGit -Items @('fetch','--quiet','--no-tags','origin',('refs/heads/'+$branch))
$fetched=Invoke-TTMGit -Items @('rev-parse','FETCH_HEAD')
if($fetched -ine $ExpectedCommit){throw ('GITHUB_HEAD_SHA_DIFFERENT expected='+$ExpectedCommit+' actual='+$fetched)}
$localRef='refs/heads/'+$branch
# show-ref --quiet returns 1 when absent; that alone is NOT a failure.
$null=(& $gitExe -C $root show-ref --verify --quiet $localRef)
$refExists=($LASTEXITCODE -eq 0)
if(-not (Test-Path -LiteralPath $work)){
    if($refExists){
        $existing=Invoke-TTMGit -Items @('rev-parse',$localRef)
        if($existing -ine $ExpectedCommit){throw 'EXISTING_LOCAL_BRANCH_OLD_WITHOUT_WORKTREE_HOLD'}
        $null=Invoke-TTMGit -Items @('worktree','add',$work,$branch)
    } else {
        $null=Invoke-TTMGit -Items @('worktree','add','-b',$branch,$work,$ExpectedCommit)
    }
}
# Recover a partially-created worktree WITHOUT deletion/reset/force.
# Verify this worktree owns precisely the intended branch before updating.
$wtName=Invoke-TTMGit -RepoPath $work -Items @('rev-parse','--abbrev-ref','HEAD')
$wtHead=Invoke-TTMGit -RepoPath $work -Items @('rev-parse','HEAD')
if($wtName -cne $branch){throw 'EXISTING_WORKTREE_WRONG_BRANCH_HOLD'}
if($wtHead -ine $ExpectedCommit){
    if(-not $refExists){throw 'EXISTING_WORKTREE_LOCAL_REF_NOT_FOUND_HOLD'}
    $localHead=Invoke-TTMGit -Items @('rev-parse',$localRef)
    if($wtHead -ine $localHead){throw 'EXISTING_WORKTREE_REF_MISMATCH_HOLD'}
    $dirty=Invoke-TTMGit -RepoPath $work -Items @('status','--porcelain','--untracked-files=all')
    if(-not [string]::IsNullOrWhiteSpace($dirty)){throw 'EXISTING_WORKTREE_DIRTY_HOLD_NO_RESET'}
    # No rebase, checkout --force, reset --hard, branch deletion, or clobber.
    $null=(& $gitExe -C $root merge-base --is-ancestor $wtHead $ExpectedCommit)
    if($LASTEXITCODE -ne 0){throw 'EXPECTED_COMMIT_NOT_FAST_FORWARD_DESCENDANT_HOLD'}
    $null=Invoke-TTMGit -RepoPath $work -Items @('merge','--ff-only','--no-edit',$ExpectedCommit)
    $wtHead=Invoke-TTMGit -RepoPath $work -Items @('rev-parse','HEAD')
}
if($wtHead -ine $ExpectedCommit){throw 'WORKTREE_HEAD_NOT_AT_PIN_AFTER_FAST_FORWARD'}
$wtStatus=Invoke-TTMGit -RepoPath $work -Items @('status','--porcelain','--untracked-files=all')
if(-not [string]::IsNullOrWhiteSpace($wtStatus)){throw 'WORKTREE_NOT_CLEAN_AFTER_FAST_FORWARD'}
$preflight=Join-Path $work 'tools\pilot_t5\kv_flash_precision_v1\Invoke-TTM-T5-KVFlash-OwnerPreflight-PS51.ps1'
if(-not (Test-Path -LiteralPath $preflight -PathType Leaf)){throw 'PINNED_GITHUB_PREVIEW_SCRIPT_MISSING'}

$caller=''
$inventory=@()
if(Test-Path -LiteralPath $historicSourceDir -PathType Container){
  $candidateSources=@(Get-ChildItem -LiteralPath $historicSourceDir -Filter '*.cpp' -File)
  foreach($f in $candidateSources){
    $digest=Sha $f.FullName
    $inventory+=@{name=$f.Name;sha256=$digest;expected_match=($digest -eq $shaCallerExpected)}
    if($digest -eq $shaCallerExpected){
      if($caller){throw 'MULTIPLE_SOURCE_FILES_MATCH_PIN'}
      $caller=$f.FullName
    }
  }
}
$oldBinarySha=if(Test-Path -LiteralPath $oldExe -PathType Leaf){Sha $oldExe}else{'MISSING'}
$oldBinaryShaMatch=($oldBinarySha -eq $shaOldBinaryExpected)
$oldBuildSha=if(Test-Path -LiteralPath $oldCmake -PathType Leaf){Sha $oldCmake}else{'MISSING'}
$oldLogSha=if(Test-Path -LiteralPath $oldLog -PathType Leaf){Sha $oldLog}else{'MISSING'}
$ggufFound=(Test-Path -LiteralPath $gguf -PathType Leaf)
$callArgs=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$preflight,'-Mode','Preview','-ProjectRoot',$root,'-WorktreePath',$work)
if($caller){$callArgs+=@('-OriginalCallerSource',$caller,'-CallerAttested')}
if($ggufFound){$callArgs+=@('-GGUFFile',$gguf)}
# New reference and candidate executable remain NOT_EXECUTED/UNCOMPILED in Preview.
# Capture child-process stderr as data, not as a WinPS 5.1 terminating error.
$savedEap=$ErrorActionPreference
try {
    $ErrorActionPreference='Continue'
    $preflightOutput=@(& powershell.exe @callArgs 2>&1)
    $preflightExit=$LASTEXITCODE
} finally {
    $ErrorActionPreference=$savedEap
}
if($preflightExit -ne 0){throw ('OWNER_PREVIEW_COMMAND_FAILED '+($preflightOutput -join "`n"))}
if(-not (Test-Path -LiteralPath $receiptDir)){throw 'PREVIEW_DID_NOT_WRITE_EVIDENCE_FOLDER'}
$resultLine=@($preflightOutput | Where-Object {$_ -like 'RESULT=*'})
$receipt=if($resultLine.Count -eq 1){[string]$resultLine[0].Substring(7)}else{''}
if(-not $receipt -or -not (Test-Path -LiteralPath $receipt -PathType Leaf)){throw 'PREVIEW_RECEIPT_PATH_NOT_FOUND'}
$parsed=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
if($parsed.mode -ne 'Preview' -or $parsed.native_execution -ne 'NOT_EXECUTED'){throw 'PREVIEW_RECEIPT_UNSAFE'}
$summary=[ordered]@{
 schema='ttm.t5.owner_local_preview_single.v1'; status=$parsed.status
 branch=$branch; git_head=$wtHead; source_git_script_sha256=(Sha $preflight)
 original_caller_source=$caller; caller_cpp_candidates=$inventory
 original_caller_expected_sha256=$shaCallerExpected
 old_probe_binary_expected_sha256=$shaOldBinaryExpected; old_probe_binary_sha256_match=$oldBinaryShaMatch
 old_probe_binary_sha256=$oldBinarySha; old_cmake_cache_sha256=$oldBuildSha; old_native_log_sha256=$oldLogSha
 gguf_path_present=$ggufFound; gguf_sha256=if($ggufFound){Sha $gguf}else{'MISSING'}
 frozen_checkpoint_new_reference='NOT_PROVIDED_PREVIEW_ONLY'
 new_probe_compiled_binary='NOT_PROVIDED_PREVIEW_ONLY'
 caller_type_k=$parsed.caller.type_k; caller_type_v=$parsed.caller.type_v
 preview_receipt=$receipt; preview_receipt_sha256=(Sha $receipt)
 checks=$parsed.checks
 native_inference='NOT_EXECUTED'; training='NO'; test='UNTOUCHED'; historical_strict='FAIL_7_OF_8_PRESERVED'
}
$json=ConvertTo-Json -InputObject $summary -Depth 18
[IO.File]::WriteAllText($marker,$json+"`n",(New-Object System.Text.UTF8Encoding($false)))
Write-Output ('OWNER_PREVIEW='+$parsed.status)
Write-Output ('CALLER_SOURCE_SHA_MATCH='+$parsed.checks.CallerSourceSHA)
Write-Output ('CALLER_TYPE_K='+$parsed.caller.type_k)
Write-Output ('CALLER_TYPE_V='+$parsed.caller.type_v)
Write-Output ('HISTORICAL_BINARY_SHA256='+$oldBinarySha)
Write-Output ('HISTORICAL_BINARY_SHA_MATCH='+$oldBinaryShaMatch)
Write-Output ('NEW_BINARY=NOT_COMPILED')
Write-Output ('NEW_REFERENCE=NOT_EXECUTED')
Write-Output ('RESULT='+$marker)
Write-Output ('RESULT_SHA256='+(Sha $marker))
Write-Output ('HISTORICAL_STRICT=FAIL_7_OF_8_PRESERVED')
