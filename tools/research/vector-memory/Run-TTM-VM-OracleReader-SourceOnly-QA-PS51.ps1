# TTM VM Oracle Reader source-only QA, PS 5.1, inside project root only.
$ErrorActionPreference = 'Stop'
$workspace = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$inside = $root.StartsWith(($workspace.TrimEnd('\') + '\'), [StringComparison]::OrdinalIgnoreCase)
if (($root -ne $workspace) -and (-not $inside)) { throw 'TTM_WORKTREE_OUTSIDE_WORKSPACE_DENIED' }
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'PYTHON312_MISSING' }
& $py -c 'import sys,torch;assert sys.version_info[:2]==(3,12);print("PY312_TORCH_READY",torch.__version__)'
if ($LASTEXITCODE -ne 0) { throw 'PYTHON312_OR_TORCH_FAIL' }
$dir = Join-Path $root '_evidence\vector-memory\oracle-reader-source-only'
$primary = Join-Path $dir 'TTM_VM_ORACLE_READER_SOURCE_ONLY_QA_20261111.json'
$secondary = Join-Path $dir 'TTM_VM_ORACLE_READER_INDEPENDENT_QA_20261111.json'
if ((Test-Path -LiteralPath $primary) -or (Test-Path -LiteralPath $secondary)) { throw 'NO_OVERWRITE_ONE_SHOT_SOURCE_QA' }
New-Item -Path $dir -ItemType Directory -Force | Out-Null
& $py (Join-Path $root 'tools\research\vector-memory\test_oracle_reader_source_only.py') --repo-root $root --out $primary
if ($LASTEXITCODE -ne 0) { throw 'PRIMARY_SOURCE_QA_FAILED' }
& $py (Join-Path $root 'tools\research\vector-memory\oracle_reader_independent_audit.py') --repo-root $root --result $primary --out $secondary
if ($LASTEXITCODE -ne 0) { throw 'INDEPENDENT_SOURCE_QA_FAILED' }
$a = Get-Content -LiteralPath $primary -Raw | ConvertFrom-Json
$b = Get-Content -LiteralPath $secondary -Raw | ConvertFrom-Json
if ($a.status -ne 'PASS_SOURCE_ONLY_SYNTHETIC_QA' -or $a.checks_passed -ne 35 -or $b.status -ne 'PASS_INDEPENDENT_SOURCE_ONLY' -or $b.checks_passed -ne 15) { throw 'ORACLE_QA_UNEXPECTED_STATUS' }
Write-Output 'TTM_VM_ORACLE_READER_SOURCE_QA=PASS_35_35'
Write-Output 'TTM_VM_ORACLE_READER_INDEPENDENT_QA=PASS_15_15'
Write-Output ('PRIMARY_SHA256=' + (Get-FileHash -Algorithm SHA256 -LiteralPath $primary).Hash)
Write-Output ('INDEPENDENT_SHA256=' + (Get-FileHash -Algorithm SHA256 -LiteralPath $secondary).Hash)
Write-Output 'TEST=NOT_OPENED; TRAINING=NOT_EXECUTED; GPU=NOT_USED'
