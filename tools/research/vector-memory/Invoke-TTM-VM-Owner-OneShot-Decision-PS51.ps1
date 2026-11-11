# TTM Vector Memory — one integrated owner preflight decision (PowerShell 5.1).
# Default read-only. -SyncPinnedWorktree updates only a clean detached research
# worktree under the TTM root to the exact prereg commit. NEVER runs science.
param([switch]$SyncPinnedWorktree)
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $root 'worktrees\ttm-vm-external-20261111'
$branch = 'research/ttm-vector-memory-architecture-20261111'
$pin = 'c41b6c8bc01a4c367bf619a6df6e05e5e2fb9d47'
$python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$checkpoint = Join-Path $root '_tmp\vector-memory\checkpoint.pt'
$manifest = Join-Path $root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
$receipt = Join-Path $root '_evidence\vector-memory\TTM_VM_REAL_T1_BPE_COMPAT_QA_20261111.json'
$runDir = Join-Path $root '_evidence\vector-memory\TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1'

function RequireFile($path, $label) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw ('HOLD_MISSING_' + $label) }
}
function RequireSha($path, $expected, $label) {
    RequireFile $path $label
    $found = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($found -ne $expected) { throw ('HOLD_SHA256_' + $label + ':' + $found) }
}
function Git {
    $output = & git.exe @args
    if ($LASTEXITCODE -ne 0) { throw ('HOLD_GIT_COMMAND_FAILED_' + ($args -join '_')) }
    return $output
}
function AssertBlob($relative, $expected) {
    $actual = (Git -C $wt hash-object -- $relative).Trim()
    if ($actual -ne $expected) { throw ('HOLD_DIRTY_OR_WRONG_BLOB_' + $relative) }
}
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'HOLD_PROJECT_ROOT_MISSING' }
if (-not (Test-Path -LiteralPath $wt -PathType Container)) { throw 'HOLD_RESEARCH_WORKTREE_MISSING' }
$origin = (Git -C $root remote get-url origin).Trim()
$canonicalOrigin = ($origin -replace '^git@github\.com:', 'https://github.com/')
if ($canonicalOrigin -notmatch '^https://github\.com/minhtri22/TokenToModel-Lab(\.git)?$') {
    throw 'HOLD_WRONG_ORIGIN'
}
$mainBefore = (Git -C $root rev-parse refs/heads/main).Trim()
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'HOLD_PYTHON312_MISSING' }
if (Test-Path -LiteralPath $runDir) { throw 'HOLD_ONE_SHOT_ALREADY_STARTED_OR_CONSUMED' }
$top = (Git -C $wt rev-parse --show-toplevel).Trim()
if ([IO.Path]::GetFullPath($top).TrimEnd('\') -ine [IO.Path]::GetFullPath($wt).TrimEnd('\')) {
    throw 'HOLD_NOT_EXPECTED_RESEARCH_WORKTREE'
}
$dirty = @(Git -C $wt status --porcelain=v1 --untracked-files=all)
if (@($dirty | Where-Object { $_ -and $_.Trim() }).Count -ne 0) {
    throw 'HOLD_DIRTY_WORKTREE_REFUSE_CHECKOUT'
}
$localHead = (Git -C $wt rev-parse HEAD).Trim()
if ($localHead -ne $pin) {
    if (-not $SyncPinnedWorktree) {
        Write-Output ('HOLD_PINNED_CHECKOUT_MISMATCH_LOCAL=' + $localHead)
        Write-Output ('EXPECTED_SCIENCE_COMMIT=' + $pin)
        Write-Output 'SYNC_PERMITTED_ONLY_WITH_-SyncPinnedWorktree'
        exit 2
    }
    # Fetch only research ref. Does NOT change main, and checkout is detached.
    Git -C $root fetch origin ("refs/heads/" + $branch + ":refs/remotes/origin/" + $branch) | Out-Null
    $available = (Git -C $root cat-file -t $pin).Trim()
    if ($available -ne 'commit') { throw 'HOLD_PINNED_COMMIT_MISSING' }
    Git -C $wt checkout --detach $pin | Out-Null
}
if ((Git -C $wt rev-parse HEAD).Trim() -ne $pin) { throw 'HOLD_HEAD_NOT_FROZEN' }
$dirty2 = @(Git -C $wt status --porcelain=v1 --untracked-files=all)
if (@($dirty2 | Where-Object { $_ -and $_.Trim() }).Count -ne 0) {
    throw 'HOLD_DIRTY_AFTER_SYNC'
}
AssertBlob 'tools/pilot_t4/integrated/p02_source_exact.py' '9762343e06cf800b50574c2871ae1ed58537fb18'
AssertBlob 'tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py' 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
AssertBlob 'tools/research/vector-memory/oracle_reader_source_only.py' '7ce728b2874284b87933237c890e54ce3d9fd651'
AssertBlob 'tools/research/vector-memory/cpu_pilot_one_shot.py' '13701b8768c463d845762c690768abae2040eba2'
AssertBlob 'tools/research/vector-memory/cpu_pilot_readiness.py' '6c43d2889f39a4ad537ace78ecbff40294089031'
AssertBlob 'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_TRAIN_256_V1.json' '9e86317c055047fffebfb2d802889e69987a8c8b'
AssertBlob 'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_DEV_64_V1.json' 'ffc9d211508fbedc84db31235ecaad8d07596ece'

RequireSha $checkpoint 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc' 'CHECKPOINT'
RequireSha $manifest 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc' 'REAL_T1_MANIFEST'
RequireSha $receipt 'bc688ca5bcc4084a19d3e95b0f7d555c283d8b1b1319ff255c5baf9e66c7b34b' 'REAL_T1_RECEIPT'
$report = Get-Content -LiteralPath $receipt -Raw -Encoding UTF8 | ConvertFrom-Json
if ($report.status -ne 'PASS_REAL_T1_TOKENIZER' -or
    $report.input_cases -ne 320 -or
    $report.answer_boundary_prefix_mismatches -ne 0 -or
    $report.test_status -ne 'NOT_READ_OR_DECRYPTED') {
    throw 'HOLD_REAL_T1_RECEIPT_CONTENT'
}
& $python -c 'import sys,torch,numpy,regex;assert sys.version_info[:2]==(3,12);assert hasattr(torch,"__version__")'
if ($LASTEXITCODE -ne 0) { throw 'HOLD_PYTHON_DEPENDENCIES' }
if ((Git -C $root rev-parse refs/heads/main).Trim() -ne $mainBefore) { throw 'HOLD_MAIN_CHANGED' }
Write-Output 'GO_OWNER_PREEXEC_ALL_PINS_PASS=TRUE'
Write-Output ('FROZEN_RESEARCH_CHECKOUT=' + $pin)
Write-Output 'T1_RECEIPT_RAW_SHA256=PASS'
Write-Output 'CHECKPOINT_T1_SOURCE_FIXTURES=PASS'
Write-Output 'ONE_SHOT_OUTPUT_ABSENT=PASS'
Write-Output 'TRAINING_NOT_EXECUTED=TRUE'
Write-Output 'DEV_NOT_SCORED=TRUE'
Write-Output 'TEST_NOT_OPENED=TRUE'
Write-Output 'MAIN_NOT_CHECKED_OUT_OR_CHANGED=TRUE'
