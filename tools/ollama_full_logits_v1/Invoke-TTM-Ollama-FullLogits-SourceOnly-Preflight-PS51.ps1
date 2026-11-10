# TTM Ollama full-logits isolated source-only preflight; Windows PowerShell 5.1.
# This script DOES NOT build, start Ollama, consume a one-shot permit or run inference.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$LlamaSourceRoot,
    [string]$Python312 = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$project = [IO.Path]::GetFullPath('D:\WORK\RESEARCH\TokenToModel-Lab').TrimEnd('\')
$checkout = [IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot))).TrimEnd('\')
$source = [IO.Path]::GetFullPath($LlamaSourceRoot).TrimEnd('\')
$expectedBranch = 'research/ttm-t5-ollama-full-logits-20261111'

function Assert-ProjectChild([string]$PathValue) {
    if (-not $PathValue.StartsWith(($project + '\'), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ('TTM_PROJECT_BOUNDARY_FAIL: ' + $PathValue)
    }
}

if (-not (Test-Path -LiteralPath $project -PathType Container)) { throw 'PROJECT_ROOT_NOT_FOUND' }
if (-not (($checkout -eq $project) -or $checkout.StartsWith(($project + '\'), [System.StringComparison]::OrdinalIgnoreCase))) {
    throw 'CHECKOUT_OUTSIDE_TTM_PROJECT'
}
Assert-ProjectChild $source
if (-not (Test-Path -LiteralPath $source -PathType Container)) { throw 'PINNED_LLAMA_SOURCE_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $Python312 -PathType Leaf)) { throw 'PYTHON312_NOT_FOUND' }

$branch = ((& git.exe -C $checkout branch --show-current) | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $branch -ne $expectedBranch) {
    throw ('WRONG_BRANCH: ' + $branch)
}
$pre = Join-Path $checkout 'artifacts\qa\ttm-ollama-full-logits\TTM_OLLAMA_FULL_LOGITS_F32_PREREG_20261111.json'
$patch = Join-Path $checkout 'tools\ollama_full_logits_v1\ttm_ollama_full_logits_b11963_hook.patch'
$test = Join-Path $checkout 'tools\ollama_full_logits_v1\test_independent_full_logits_audit.py'
$cpp = Join-Path $source 'tools\server\server-context.cpp'
foreach ($f in @($pre,$patch,$test,$cpp)) {
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) {
        throw ('MISSING_REQUIRED_SOURCE: ' + $f)
    }
}
$preregBlob = ((& git.exe hash-object -- $pre) | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $preregBlob -ne 'fdcb81064a6c55b3dca5f71e18defff0895c0568') {
    throw 'PREREG_GIT_BLOB_CHANGED'
}
$serverBlob = ((& git.exe hash-object -- $cpp) | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $serverBlob -ne '2bd1ab9ec00ca581c70bac014f7ca6d3d2bae0ae') {
    throw 'PINNED_SERVER_CONTEXT_SOURCE_BLOB_MISMATCH'
}

Push-Location -LiteralPath $source
try {
    & git.exe apply --check -- $patch
    if ($LASTEXITCODE -ne 0) { throw 'GIT_APPLY_CHECK_FAILED_NO_PATCH_APPLIED' }
} finally {
    Pop-Location
}
Write-Output 'OLLAMA_FULL_LOGITS_PATCH_APPLY_CHECK=PASS_SOURCE_ONLY'

& $Python312 -B -c "import sys; assert sys.version_info[:2] == (3,12)"
if ($LASTEXITCODE -ne 0) { throw 'PYTHON312_VERSION_GATE_FAIL' }
& $Python312 -B $test
if ($LASTEXITCODE -ne 0) { throw 'PYTHON_OFFLINE_NEGATIVE_TESTS_FAIL' }
Write-Output 'OLLAMA_FULL_LOGITS_AUDITOR_OFFLINE_QA=PASS'
Write-Output 'OLLAMA_FULL_LOGITS_NATIVE_BUILD=NOT_EXECUTED'
Write-Output 'OLLAMA_FULL_LOGITS_REFERENCE=NOT_EXECUTED'
Write-Output 'OLLAMA_FULL_LOGITS_INFERENCE=NOT_EXECUTED'
Write-Output 'T5_WINDOWS_F32=PASS_SCOPED_UNCHANGED'
