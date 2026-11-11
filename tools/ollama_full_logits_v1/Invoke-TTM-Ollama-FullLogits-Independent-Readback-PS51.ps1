# Pure read-only scientific audit of existing one-shot outputs. No Ollama runtime.
[CmdletBinding()]
param([string]$Python312='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$wt=[IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$branch='research/ttm-t5-ollama-full-logits-20261111'
$py=$Python312
if(-not (Test-Path -LiteralPath $py -PathType Leaf)){throw 'PYTHON312_NOT_FOUND'}
if(-not $wt.StartsWith(($root+'\'),[StringComparison]::OrdinalIgnoreCase)){throw 'WORKTREE_OUTSIDE_PROJECT'}
$actual=(& git.exe -C $wt branch --show-current | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $actual -ne $branch){throw 'WRONG_RESEARCH_BRANCH'}
$head=(& git.exe -C $wt rev-parse HEAD | Out-String).Trim()
if($LASTEXITCODE -ne 0){throw 'WORKTREE_HEAD_MISSING'}
$dirty=(& git.exe -C $wt status --porcelain --untracked-files=all | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $dirty){throw 'WORKTREE_DIRTY'}
$base=Join-Path $wt 'tools\ollama_full_logits_v1'
& $py -B (Join-Path $base 'test_independent_fl01_fl04_final_readback.py')
if($LASTEXITCODE -ne 0){throw 'INDEPENDENT_OFFLINE_QA_FAILED'}
Write-Output 'INDEPENDENT_OFFLINE_QA=PASS'
& $py -B (Join-Path $base 'independent_fl01_fl04_final_readback.py') --project-root $root --worktree $wt --expected-head $head
if($LASTEXITCODE -ne 0){throw 'INDEPENDENT_READBACK_HOLD_PRESERVE_ORIGINAL_EVIDENCE'}
