# PowerShell 5.1; read-only Git sources and public synthetic QA. No Git write, no GPU.
param(
    [string]$Repo = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$Python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Repo -PathType Container)) {
    throw "HOLD_REPO_MISSING: $Repo"
}
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "HOLD_PYTHON312_NOT_FOUND: $Python"
}
$Script = Join-Path $PSScriptRoot 'ttm_d1_bridge_v6_r1_r3_integrated_qa_20261114.py'
if (-not (Test-Path -LiteralPath $Script -PathType Leaf)) {
    throw "HOLD_QA_SCRIPT_MISSING: $Script"
}
$RepoFull = [IO.Path]::GetFullPath($Repo)
$Out = Join-Path $RepoFull '_tmp\TTM_D1_V6_R1_R3_CANDIDATE_20261114'
Write-Output ('FROZEN_SOURCE_HEAD=dd52804685d186c17e600221ffb16ce78aea12ea')
Write-Output ('REPO=' + $RepoFull)
Write-Output ('PYTHON=' + $Python)
& $Python $Script --repo $RepoFull --out $Out
if ($LASTEXITCODE -ne 0) {
    throw ('HOLD_SOURCE_QA_EXIT=' + $LASTEXITCODE)
}
Write-Output ('OUTPUT_DIR=' + $Out)
Write-Output 'GIT_WRITE=FALSE GPU=0 TRAIN=0 INFERENCE=0 PRIVATE_GOLD=NO'
