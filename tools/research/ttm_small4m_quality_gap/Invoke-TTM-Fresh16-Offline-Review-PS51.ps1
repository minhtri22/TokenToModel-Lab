# Source-only / private-source read-only FRESH16 integrated QA. NO inference.
[CmdletBinding()]
param(
    [string]$Checkpoint1024 = 'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_causal6_source_h512_stage_20261109\input\checkpoint.pt',
    [string]$Checkpoint1280 = '',
    [string]$Python312 = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$branch='research/ttm-small4m-prompt-adherence-continuation-design-20261111'
$work=Join-Path $root 'worktrees\ttm-fresh16-quality-20261111'
if(-not (Test-Path -LiteralPath $Python312 -PathType Leaf)){throw 'PYTHON312_MISSING'}
if(-not (Test-Path -LiteralPath $root -PathType Container)){throw 'TTM_ROOT_MISSING'}
if(-not (Test-Path -LiteralPath $work -PathType Container)){
    & git.exe -C $root show-ref --verify --quiet "refs/heads/$branch"
    if($LASTEXITCODE -eq 0){
        & git.exe -C $root worktree add $work $branch
    } else {
        & git.exe -C $root worktree add --track -b $branch $work "origin/$branch"
    }
    if($LASTEXITCODE -ne 0){throw 'RESEARCH_WORKTREE_ADD_FAILED'}
}
$actual=(& git.exe -C $work branch --show-current | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $actual -ne $branch){throw 'WRONG_RESEARCH_WORKTREE'}
$dirty=(& git.exe -C $work status --porcelain --untracked-files=all | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $dirty){throw 'WORKTREE_DIRTY'}
$head=(& git.exe -C $work rev-parse HEAD | Out-String).Trim()
if($LASTEXITCODE -ne 0){throw 'RESEARCH_HEAD_MISSING'}
# Read only: verify local original checkpoint files before creating the QA receipt.
# The science archive and previous one-shot results are not accessed.
$stage=Join-Path $root '_tmp\ttm_fresh16_integrated_offline_review_20261111'
if(Test-Path -LiteralPath $stage){throw 'OFFLINE_RECEIPT_STAGE_EXISTS_PRESERVE_FOR_INSPECTION'}
$manifest=Join-Path $root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
if(-not (Test-Path -LiteralPath $manifest -PathType Leaf)){
    throw 'NATIVE_T1_BPE_MANIFEST_ABSENT_NO_STAGE_CREATED'
}
if(-not (Test-Path -LiteralPath $Checkpoint1024 -PathType Leaf)){
    throw 'ORIGINAL_STEP1024_LOCAL_PATH_ABSENT_NO_STAGE_CREATED'
}
$sha1024=(Get-FileHash -LiteralPath $Checkpoint1024 -Algorithm SHA256).Hash.ToLowerInvariant()
if($sha1024 -ne 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'){
    throw 'ORIGINAL_STEP1024_LOCAL_SHA_MISMATCH'
}
Write-Host 'FRESH16_CHECKPOINT1024_LOCAL_SHA=PASS'
# No arbitrary model selection: look only for exact pinned SHA and known byte size.
if(-not $Checkpoint1280){
    $matches=@()
    $tmp=Join-Path $root '_tmp'
    foreach($file in @(Get-ChildItem -LiteralPath $tmp -Recurse -File -ErrorAction Stop)){
        if($file.Extension -ne '.pt' -or $file.Length -ne 45075275){continue}
        $hash=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        if($hash -eq 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'){
            $matches+=,$file.FullName
        }
    }
    if($matches.Count -eq 0){
        throw 'STEP1280_NOT_FOUND_UNDER_TTM_TMP_NO_STAGE_CREATED'
    }
    $Checkpoint1280=@($matches | Sort-Object)[0]
}
$full1280=[IO.Path]::GetFullPath($Checkpoint1280)
if(-not $full1280.StartsWith(($root+'\'),[StringComparison]::OrdinalIgnoreCase)){
    throw 'STEP1280_OUTSIDE_TTM_PROJECT'
}
if(-not (Test-Path -LiteralPath $Checkpoint1280 -PathType Leaf)){
    throw 'ORIGINAL_STEP1280_LOCAL_PATH_ABSENT'
}
$sha1280=(Get-FileHash -LiteralPath $Checkpoint1280 -Algorithm SHA256).Hash.ToLowerInvariant()
if($sha1280 -ne 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'){
    throw 'ORIGINAL_STEP1280_LOCAL_SHA_MISMATCH'
}
Write-Host 'FRESH16_CHECKPOINT1280_LOCAL_SHA=PASS'

$tools=Join-Path $work 'tools\research\ttm_small4m_quality_gap'
$tests=Join-Path $tools 'test_fresh16_integrated_offline_review.py'
$runner=Join-Path $tools 'ttm_fresh16_integrated_offline_review.py'
& $Python312 -B $tests
if($LASTEXITCODE -ne 0){throw 'FRESH16_OFFLINE_UNIT_QA_FAILED'}
Write-Host 'TTM_FRESH16_OFFLINE_UNIT_QA=PASS'
$argsList=@('-B',$runner,'--project-root',$root,'--worktree',$work,'--expected-head',$head)
if($Checkpoint1024){$argsList+=@('--checkpoint-1024',$Checkpoint1024)}
if($Checkpoint1280){$argsList+=@('--checkpoint-1280',$Checkpoint1280)}
& $Python312 @argsList
if($LASTEXITCODE -ne 0){throw 'FRESH16_NATIVE_PREFLIGHT_HOLD_PRESERVE_RECEIPT'}
