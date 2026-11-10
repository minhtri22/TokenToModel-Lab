[CmdletBinding()]
param(
    [switch]$ApplyCleanup,
    [string]$Root='D:\WORK\RESEARCH\TokenToModel-Lab'
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest

# Scope: remove only the clean merged T5 worktree. Do not touch _tmp/evidence,
# patched isolated llama worktrees, unrelated worktrees, main or remote refs.
$merge='df126b2d4beaee865faa24d8a7e9720bb59693aa'
$prHead='45918caed31a6d3c6c4d226b6f1d01cf2c113afa'
$expectedRoot='D:\WORK\RESEARCH\TokenToModel-Lab'
$targetRel='worktrees\ttm-t5-kvflash-preview-20261109'
$git=(Get-Command git.exe -CommandType Application -ErrorAction Stop).Source

function Canon([string]$p) {
    return [System.IO.Path]::GetFullPath($p).TrimEnd('\').ToLowerInvariant()
}
function GitText([string[]]$argv) {
    $out=@(& $git @argv)
    if($LASTEXITCODE -ne 0) {
        throw ('GIT_EXIT_'+$LASTEXITCODE+': '+($argv -join ' '))
    }
    return ($out -join [Environment]::NewLine).Trim()
}
function ExactSHA([string]$path,[string]$expected) {
    if(-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw ('MISSING_EVIDENCE: '+$path)
    }
    $hash=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if($hash -ne $expected){throw ('EVIDENCE_SHA_CHANGED: '+$path)}
    return $hash
}
if($PSVersionTable.PSVersion.Major -ne 5){throw 'PS51_REQUIRED'}
$Root=(Resolve-Path -LiteralPath $Root -ErrorAction Stop).Path
if((Canon $Root) -ne (Canon $expectedRoot)){throw 'EXACT_PROJECT_ROOT_REQUIRED'}
$target=Join-Path $Root $targetRel
if(-not (Test-Path -LiteralPath $target -PathType Container)){
    throw 'TARGET_T5_WORKTREE_NOT_FOUND'
}
if(-not (Test-Path -LiteralPath (Join-Path $target '.git') -PathType Leaf)){
    throw 'TARGET_NOT_A_LINKED_WORKTREE'
}
$stage=Join-Path $Root '_tmp\ttm_t5_postmerge_worktree_cleanup_v1_20261110'
if(Test-Path -LiteralPath $stage){throw 'CLEANUP_STAGE_ALREADY_EXISTS_NO_OVERWRITE'}
New-Item -ItemType Directory -Path $stage -ErrorAction Stop | Out-Null
$receipt=Join-Path $stage 'POSTMERGE_WORKTREE_CLEANUP_RECEIPT.json'
$record=[ordered]@{
    schema='ttm.t5.postmerge.worktree_cleanup.v1'
    mode=$(if($ApplyCleanup){'APPLY_CLEANUP'}else{'AUDIT_ONLY'})
    status='HOLD_PRECHECK_NOT_COMPLETED'
    merge_sha=$merge
    merged_pr_head=$prHead
    target=$target
    other_worktrees_untouched=$true
    patched_llama_variant_untouched=$true
    original_scientific_evidence_untouched=$true
    main_checkout_untouched=$true
    PR13_untouched=$true
    local_T5_branch_ref_untouched=$true
    remote_T5_branch_ref_untouched=$true
    worktree_removed=$false
    provenance=@{}
    error=''
}
try {
    $top=GitText @('-C',$Root,'rev-parse','--show-toplevel')
    if((Canon $top) -ne (Canon $Root)){throw 'GIT_ROOT_MISMATCH'}
    $origin=GitText @('-C',$Root,'remote','get-url','origin')
    if($origin -notmatch '(?i)github[.]com[:/]minhtri22/TokenToModel-Lab(?:[.]git)?$'){
        throw 'NOT_EXPECTED_GITHUB_ORIGIN'
    }
    $remote=GitText @('-C',$Root,'ls-remote','origin','refs/heads/main')
    if($remote -notmatch '^[a-f0-9]{40}\s+refs/heads/main$'){
        throw 'REMOTE_MAIN_AMBIGUOUS'
    }
    $remoteHead=($remote -split '\s+')[0]
    $null=GitText @('-C',$Root,'fetch','--no-tags','origin','refs/heads/main')
    $fetched=GitText @('-C',$Root,'rev-parse','FETCH_HEAD')
    if($fetched -ne $remoteHead){throw 'MAIN_REMOTE_MOVED_DURING_FETCH'}
    & $git -C $Root merge-base --is-ancestor $merge $fetched
    if($LASTEXITCODE -ne 0){throw 'PR16_MERGE_NOT_IN_MAIN'}
    & $git -C $Root merge-base --is-ancestor $prHead $merge
    if($LASTEXITCODE -ne 0){throw 'PR16_SOURCE_NOT_MERGED'}
    $wtTop=GitText @('-C',$target,'rev-parse','--show-toplevel')
    if((Canon $wtTop) -ne (Canon $target)){throw 'WORKTREE_IDENTITY_MISMATCH'}
    $wtHead=GitText @('-C',$target,'rev-parse','HEAD')
    $wtBranch=GitText @('-C',$target,'branch','--show-current')
    & $git -C $Root merge-base --is-ancestor $wtHead $merge
    if($LASTEXITCODE -ne 0){throw 'WORKTREE_HEAD_UNMERGED'}
    $entries=GitText @('-C',$Root,'worktree','list','--porcelain')
    $paths=@($entries -split '\r?\n' | Where-Object {
        $_ -match '^worktree\s+'
    } | ForEach-Object {$_.Substring(9).Trim()})
    $match=@($paths | Where-Object {
        try {(Canon $_) -eq (Canon $target)}catch{$false}
    })
    if($match.Count -ne 1){throw 'WORKTREE_NOT_UNIQUELY_REGISTERED'}
    $changes=GitText @('-C',$target,'status','--porcelain','--untracked-files=all')
    if($changes.Length -ne 0){throw 'DIRTY_WORKTREE_WILL_NOT_DELETE'}
    $checks=[ordered]@{
        gguf=@('_tmp\ttm_t5_trained_f32_v1\TTM-Small4M-T4-step1024-F32.gguf','5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5')
        first_discovery=@('_tmp\ttm_t5_exact_root_discovery_run_v1_20261110\DISCOVERY_RUN_RECEIPT.json','e2cbc797e133a7e4fc4d949293dd9bd847b881e18b39f3c72bcfa9debfbc8e96')
        discovery_v2=@('_tmp\ttm_t5_exact_root_discovery_recovery_v2_20261110\RECOVERY_V2_RECEIPT.json','1f01b2991d0faae4e93c7faff8ab59cf53268f68c36085460949ff3402669bf1')
        confirmation=@('_tmp\ttm_t5_c01c04_gelu_erf_confirmatory_one_shot_20261110\CONFIRMATORY_ONCE_RECEIPT.json','95ed3c419e42df493dc314abeb42e47afa1bf72fcb90d2c7246ff4c55d645e88')
        strict_audit=@('_tmp\ttm_t5_c01c04_gelu_erf_confirmatory_one_shot_20261110\C01_C04_INDEPENDENT_STRICT_AUDIT.json','1d5e050e9aefbeb5720a5f86986ecbcffe2a51a8c7605d07c85467553b8b8887')
        P02_reference=@('_tmp\TTM_T5_C01_C04_P02_FP32_FROZEN_REFERENCE_20261110.zip','e5d522bd5234c46af77dbb85990779bd09e25d35be587538cec577ee486c5996')
    }
    foreach($key in $checks.Keys){
        $pair=$checks[$key]
        $record['provenance'][$key]=ExactSHA (Join-Path $Root $pair[0]) $pair[1]
    }
    $variant=Join-Path $Root '_tmp\ttm_t5_exact_root_v1_20261110\trace_gelu_erf\src\models\gpt2.cpp'
    if(-not (Test-Path -LiteralPath $variant -PathType Leaf)){
        throw 'PATCHED_LLAMA_SOURCE_NOT_FOUND'
    }
    $record['target_head']=$wtHead
    $record['target_branch']=$wtBranch
    $record['remote_main']=$remoteHead
    $record['status']='PASS_AUDIT_ALL_GATES'
    Write-Host 'T5_WORKTREE_PREFLIGHT=PASS'
    Write-Host ('T5_EVIDENCE_PIN=PASS_'+$checks.Count+'_OF_'+$checks.Count)
    if($ApplyCleanup) {
        $null=GitText @('-C',$Root,'worktree','remove','--',$target)
        if(Test-Path -LiteralPath $target){
            throw 'GIT_REMOVE_RETURNED_BUT_WORKTREE_STILL_EXISTS'
        }
        $record['worktree_removed']=$true
        $record['status']='PASS_CLEAN_MERGED_WORKTREE_REMOVED'
        Write-Host 'T5_WORKTREE_CLEANUP=PASS_REMOVED'
        Write-Host 'T5_LOCAL_REMOTE_BRANCH_REFS=RETAINED_FOR_LINEAGE'
    } else {
        Write-Host 'T5_WORKTREE_CLEANUP=AUDIT_ONLY'
    }
} catch {
    $record['status']='HOLD_NO_FORCE_NO_RETRY'
    $record['error']=$_.Exception.Message
} finally {
    $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding UTF8
    $hash=(Get-FileHash -LiteralPath $receipt -Algorithm SHA256).Hash.ToLowerInvariant()
    Write-Host ('T5_CLEANUP_STATUS='+$record.status)
    Write-Host ('T5_CLEANUP_RECEIPT='+$receipt)
    Write-Host ('T5_CLEANUP_RECEIPT_SHA256='+$hash)
}
if($record['status'] -eq 'HOLD_NO_FORCE_NO_RETRY'){
    throw ('T5_CLEANUP_FAIL_CLOSED: '+$record['error'])
}