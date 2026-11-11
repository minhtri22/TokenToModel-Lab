# Source-only / private-source read-only FRESH16 integrated QA. NO inference.
[CmdletBinding()]
param(
    [string]$Checkpoint1024 = '',
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
    & git.exe -C $root worktree add --track -b $branch $work "origin/$branch"
    if($LASTEXITCODE -ne 0){throw 'RESEARCH_WORKTREE_ADD_FAILED'}
}
$actual=(& git.exe -C $work branch --show-current | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $actual -ne $branch){throw 'WRONG_RESEARCH_WORKTREE'}
$dirty=(& git.exe -C $work status --porcelain --untracked-files=all | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $dirty){throw 'WORKTREE_DIRTY'}
$head=(& git.exe -C $work rev-parse HEAD | Out-String).Trim()
if($LASTEXITCODE -ne 0){throw 'RESEARCH_HEAD_MISSING'}
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
