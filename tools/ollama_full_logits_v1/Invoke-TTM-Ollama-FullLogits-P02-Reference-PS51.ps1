# PowerShell 5.1 — P02 step1024 reference once (NO Ollama, NO training, NO TEST).
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$CheckpointPath,
    [string]$Python312 = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$branch = 'research/ttm-t5-ollama-full-logits-20261111'
$work = [IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$root = [IO.Path]::GetFullPath($root).TrimEnd('\')
$work = $work.TrimEnd('\')
$checkpoint = [IO.Path]::GetFullPath($CheckpointPath)
function Assert-ProjectChild([string]$p) {
    if (-not $p.StartsWith(($root + '\'),[System.StringComparison]::OrdinalIgnoreCase)) {
        throw ('PATH_OUTSIDE_PROJECT_ROOT:' + $p)
    }
}
Assert-ProjectChild $work
Assert-ProjectChild $checkpoint
if (-not (Test-Path -LiteralPath $checkpoint -PathType Leaf)) { throw 'ORIGINAL_STEP1024_CHECKPOINT_MISSING' }
if (-not (Test-Path -LiteralPath $Python312 -PathType Leaf)) { throw 'PYTHON312_NOT_FOUND' }
$branchActual = (& git.exe -C $work branch --show-current | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $branchActual -ne $branch) { throw 'WRONG_TTM_RESEARCH_WORKTREE' }
$src = Join-Path $work 'src\p02\transformer_core.py'
$pre = Join-Path $work 'artifacts\qa\ttm-ollama-full-logits\TTM_OLLAMA_FULL_LOGITS_F32_PREREG_20261111.json'
foreach ($entry in @(
    @{File=$src; Blob='9762343e06cf800b50574c2871ae1ed58537fb18'},
    @{File=$pre; Blob='fdcb81064a6c55b3dca5f71e18defff0895c0568'}
)) {
    $hash = (& git.exe -C $work hash-object -- $entry.File | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $hash -ne $entry.Blob) { throw 'PINNED_SOURCE_GIT_BLOB_MISMATCH' }
}
$ckptSHA = (Get-FileHash -LiteralPath $checkpoint -Algorithm SHA256).Hash.ToLowerInvariant()
if ($ckptSHA -ne 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b') {
    throw 'STEP1024_CHECKPOINT_SHA_MISMATCH'
}
# Avoid nested double quotes in Windows PowerShell 5.1 native command argument passing.
# torch.__version__ is printed directly so no quoted string literal reaches python -c.
& $Python312 -B -c 'import sys, torch; assert sys.version_info[:2] == (3,12); print(torch.__version__)'
if ($LASTEXITCODE -ne 0) { throw 'PYTHON312_TORCH_NOT_READY' }
Write-Output 'PYTHON312_TORCH_IMPORT=PASS'
$tools = Join-Path $work 'tools\ollama_full_logits_v1'
$tests = Join-Path $tools 'test_fl01_fl04_p02_reference.py'
$producer = Join-Path $tools 'produce_fl01_fl04_p02_reference.py'
$checker = Join-Path $tools 'verify_fl01_fl04_p02_reference.py'
foreach ($f in @($tests,$producer,$checker)) {
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { throw 'MISSING_REFERENCE_SOURCE' }
}
$env:PYTHONDONTWRITEBYTECODE = '1'
& $Python312 -B $tests
if ($LASTEXITCODE -ne 0) { throw 'REFERENCE_OFFLINE_QA_FAILED' }
$stage = Join-Path $root '_tmp\ttm_ollama_full_logits_reference_fl01_fl04_20261111'
if (Test-Path -LiteralPath $stage) { throw 'REFERENCE_STAGE_ALREADY_EXISTS_NO_OVERWRITE' }
New-Item -ItemType Directory -Path $stage -ErrorAction Stop | Out-Null
$ref = Join-Path $stage 'REFERENCE_P02_F32_FL01_FL04.jsonl'
$seal = Join-Path $stage 'REFERENCE_INDEPENDENT_SEAL.json'
& $Python312 -B $producer --project-root $root --worktree $work --checkpoint $checkpoint --output $ref
if ($LASTEXITCODE -ne 0) { throw 'P02_REFERENCE_PRODUCER_FAILED_KEEP_PARTIAL_NO_RETRY' }
& $Python312 -B $checker --project-root $root --prereg $pre --reference $ref --seal $seal
if ($LASTEXITCODE -ne 0) { throw 'REFERENCE_INDEPENDENT_AUDIT_FAILED_KEEP_EVIDENCE' }
Write-Output ('P02_REFERENCE_SHA256=' + (Get-FileHash -LiteralPath $ref -Algorithm SHA256).Hash.ToLowerInvariant())
Write-Output ('P02_REFERENCE_SEAL_SHA256=' + (Get-FileHash -LiteralPath $seal -Algorithm SHA256).Hash.ToLowerInvariant())
Write-Output 'OLLAMA_FULL_LOGITS_REFERENCE=PASS_4_OF_4_X_2048_SCOPED'
Write-Output 'OLLAMA_FULL_LOGITS_INFERENCE=NOT_EXECUTED'
Write-Output 'T5_WINDOWS_F32=PASS_SCOPED_UNCHANGED'
