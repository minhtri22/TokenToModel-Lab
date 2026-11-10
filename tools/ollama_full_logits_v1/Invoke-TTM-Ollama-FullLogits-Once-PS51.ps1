# Run EXACT one isolated Ollama full-logits capture after offline tests.
[CmdletBinding()]
param([string]$Python312='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe')
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$work=[IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$branch='research/ttm-t5-ollama-full-logits-20261111'
if(-not $work.StartsWith(($root+'\'),[System.StringComparison]::OrdinalIgnoreCase)){throw 'OUTSIDE_TTM_ROOT'}
if(-not (Test-Path -LiteralPath $Python312 -PathType Leaf)){throw 'PYTHON312_NOT_FOUND'}
$actual=(& git.exe -C $work branch --show-current | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $actual -ne $branch){throw 'WRONG_BRANCH'}
$head=(& git.exe -C $work rev-parse HEAD | Out-String).Trim()
if($LASTEXITCODE -ne 0){throw 'GIT_HEAD_READ_FAILED'}
$dirty=(& git.exe -C $work status --porcelain --untracked-files=all | Out-String).Trim()
if($LASTEXITCODE -ne 0 -or $dirty){throw 'DIRTY_RESEARCH_WORKTREE'}
$dir=Join-Path $work 'tools\ollama_full_logits_v1'
& $Python312 -B (Join-Path $dir 'test_isolated_ollama_full_logits_once.py')
if($LASTEXITCODE -ne 0){throw 'OFFLINE_NEGATIVE_QA_FAILED'}
Write-Output 'OLLAMA_FULL_LOGITS_OFFLINE_QA=PASS'
& $Python312 -B (Join-Path $dir 'run_isolated_ollama_fl01_fl04_once.py') --project-root $root --worktree $work --expected-head $head
if($LASTEXITCODE -ne 0){throw 'ONE_SHOT_HOLD_PRESERVE_EVIDENCE'}
