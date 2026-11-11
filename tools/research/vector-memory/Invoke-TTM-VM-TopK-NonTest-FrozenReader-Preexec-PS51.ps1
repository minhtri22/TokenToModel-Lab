# TTM Top-k Non-TEST: independent source/synthetic QA + private L0020 Reader SHA custody.
# No trained inference, no training, no DEV, no sealed TEST, no GPU.
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $root 'worktrees\ttm-vm-topk-source-20261112'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$source = Join-Path $wt 'tools\research\vector-memory'
$qaDir = Join-Path $root '_evidence\vector-memory'
$qaOut = Join-Path $qaDir 'TTM_VM_TOPK_SOURCE_INDEPENDENT_QA_OWNER_20261112.json'
$readerOut = Join-Path $qaDir 'TTM_VM_TOPK_L0020_PRIVATE_READER_CUSTODY_20261112.json'

if (-not (Test-Path -LiteralPath $wt -PathType Container)) { throw 'HOLD_TOPK_WORKTREE_MISSING' }
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'HOLD_PYTHON312_MISSING' }
if (Test-Path -LiteralPath $qaOut) { throw 'HOLD_OWNER_QA_ALREADY_EXISTS_REFUSE_OVERWRITE' }
if (Test-Path -LiteralPath $readerOut) { throw 'HOLD_READER_CUSTODY_ALREADY_EXISTS_REFUSE_OVERWRITE' }
$top = (& git.exe -C $wt rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0) { throw 'HOLD_WORKTREE_GIT_FAILED' }
if ([IO.Path]::GetFullPath($top).TrimEnd('\') -ine [IO.Path]::GetFullPath($wt).TrimEnd('\')) {
    throw 'HOLD_TOPK_WORKTREE_WRONG_ROOT'
}
$dirty = @(& git.exe -C $wt status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0 -or (@($dirty | Where-Object { $_ -and $_.Trim() }).Count -ne 0)) {
    throw 'HOLD_TOPK_WORKTREE_NOT_CLEAN'
}
$sourceFiles = @('topk_nontest_probe.py','oracle_reader_source_only.py',
                 'topk_reader_integration.py','topk_private_reader_custody_preexec.py',
                 'topk_reader_compact_independent_audit.py')
foreach ($f in $sourceFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $source $f) -PathType Leaf)) {
        throw ('HOLD_REQUIRED_SOURCE_NOT_FOUND:' + $f)
    }
}
New-Item -ItemType Directory -Path $qaDir -Force | Out-Null
& $py (Join-Path $source 'topk_reader_compact_independent_audit.py') --out $qaOut
if ($LASTEXITCODE -ne 0) { throw 'HOLD_TOPK_SOURCE_INDEPENDENT_QA_FAILED' }
$qa = Get-Content -LiteralPath $qaOut -Raw -Encoding UTF8 | ConvertFrom-Json
if ($qa.status -ne 'PASS_INDEPENDENT_COMPACT_SOURCE_QA' -or $qa.checks_passed -ne 28) {
    throw 'HOLD_TOPK_SOURCE_QA_REPORT_INVALID'
}
& $py (Join-Path $source 'topk_private_reader_custody_preexec.py') `
    --project-root $root --checkout $wt --out $readerOut
if ($LASTEXITCODE -ne 0) { throw 'HOLD_L0020_PRIVATE_READER_SHA_OR_STRUCTURE' }
$reader = Get-Content -LiteralPath $readerOut -Raw -Encoding UTF8 | ConvertFrom-Json
if ($reader.status -ne 'PASS_PRIVATE_READER_SHA_AND_STRUCTURE_READBACK' -or
    $reader.forward_calls -ne 0 -or $reader.optimizer_steps -ne 0 -or
    $reader.test_opened -ne $false) { throw 'HOLD_READER_CUSTODY_INVALID' }
Write-Output 'TOPK_SOURCE_INDEPENDENT_QA=PASS_28_28'
Write-Output ('PRIVATE_READER_SHA256=' + $reader.reader_sha256)
Write-Output ('PRIVATE_READER_TENSORS=' + $reader.metadata.tensor_count)
Write-Output ('SOURCE_QA_SHA256=' + (Get-FileHash -LiteralPath $qaOut -Algorithm SHA256).Hash)
Write-Output ('CUSTODY_SHA256=' + (Get-FileHash -LiteralPath $readerOut -Algorithm SHA256).Hash)
Write-Output 'TOPK_SCIENCE=NOT_EXECUTED'
Write-Output 'CPU_TRAINING=NOT_EXECUTED'
Write-Output 'OLD_DEV_TEST=NOT_OPENED'
Write-Output 'TOPK_PROBE_MEASUREMENT_RELEASE=HOLD'
