# Source-QA ONLY. Does not access checkpoint or invoke model inference.
# Runs from the project root; no files or worktrees written outside project.
param(
  [string] $ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab',
  [string] $CandidatePath = ''
)
$ErrorActionPreference = 'Stop'
if (-not $CandidatePath) { $CandidatePath = Join-Path $ProjectRoot '_tmp\ttm_sm4m_diag_q001_candidate\ttm_sm4m_diag_q001.py' }
$Python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'PYTHON312_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $CandidatePath -PathType Leaf)) { throw 'SOURCE_CANDIDATE_NOT_FOUND' }
$root = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\') + '\'
$actual = [IO.Path]::GetFullPath($CandidatePath)
if (-not $actual.StartsWith($root,[StringComparison]::OrdinalIgnoreCase)) { throw 'CANDIDATE_OUTSIDE_PROJECT_ROOT' }
& $Python -c 'import sys; assert sys.version_info[:2] == (3,12), sys.version'
if ($LASTEXITCODE -ne 0) { throw 'PYTHON_VERSION_HOLD' }
& $Python $CandidatePath source-qa
if ($LASTEXITCODE -ne 0) { throw 'SOURCE_QA_HOLD' }
Write-Output 'TTM_SM4M_DIAG_Q001_SOURCE_QA_COMPLETE_NO_MODEL_EXECUTION'
