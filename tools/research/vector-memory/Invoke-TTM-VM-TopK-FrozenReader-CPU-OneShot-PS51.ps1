# TTM Vector Memory Top-k: one integrated owner gate, PowerShell 5.1.
# Without -ExecuteOnce: preflight only. With -ExecuteOnce: exactly ONE CPU PROBE.
# No training, previous DEV, sealed TEST or GPU. Writes inside project root D:.
[CmdletBinding()]
param([switch]$ExecuteOnce)
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$branch = 'research/ttm-vector-memory-architecture-20261111'
$pin = '9e46bb4662fcffc66f85ae7d4d479a017f69b293'
$wt = Join-Path $root 'worktrees\ttm-vm-topk-source-20261112'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$privateDir = Join-Path $root '_evidence\vector-memory'
$reader = Join-Path $privateDir 'TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1\reader_private.pt'
$ck = Join-Path $root '_tmp\vector-memory\checkpoint.pt'
$t1 = Join-Path $root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
$src = 'tools/research/vector-memory'
$runner = Join-Path $wt "$src/frozen_topk_probe_one_shot.py"
$qa = Join-Path $wt "$src/independent_frozen_topk_runner_qa.py"
$qaOutput = Join-Path $privateDir 'TTM_VM_TOPK_CPU_ONESHOT_RUNNER_OWNER_QA_20261112.json'
$runDir = Join-Path $privateDir 'TTM_VM_TOPK_NONTEST_FROZEN_READER_PROBE_ONCE_V1'
$report = Join-Path $runDir 'PROBE_AGGREGATE_PUBLIC.json'
function GitExact {
    param([string[]]$Arguments)
    $data = & git.exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('HOLD_GIT_COMMAND_FAILED:' + ($Arguments -join ' ')) }
    return $data
}
function RequireSHA {
    param([string]$Path, [string]$Expected, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw ('HOLD_MISSING_' + $Label) }
    $got = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($got -ne $Expected) { throw ('HOLD_SHA_' + $Label + ':' + $got) }
}
function RequireBlob {
    param([string]$Relative, [string]$Expected)
    $filePath = Join-Path $wt $Relative
    if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) { throw ('HOLD_BLOB_FILE_MISSING:' + $Relative) }
    $actual = (GitExact -Arguments @('-C',$wt,'hash-object','--',$Relative)).Trim()
    if ($actual -ne $Expected) { throw ('HOLD_SOURCE_BLOB_MISMATCH:' + $Relative) }
}
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'HOLD_ROOT_MISSING' }
if (-not (Test-Path -LiteralPath $wt -PathType Container)) { throw 'HOLD_TOPK_WORKTREE_MISSING' }
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'HOLD_PY312_MISSING' }
if (Test-Path -LiteralPath $runDir) { throw 'HOLD_ONE_SHOT_ALREADY_CONSUMED_NO_RERUN' }
$origin = (GitExact -Arguments @('-C',$root,'remote','get-url','origin')).Trim()
if ($origin -notin @('https://github.com/minhtri22/TokenToModel-Lab',
                     'https://github.com/minhtri22/TokenToModel-Lab.git')) {
    throw 'HOLD_WRONG_GITHUB_ORIGIN'
}
$mainBefore = (GitExact -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim()
$top = (GitExact -Arguments @('-C',$wt,'rev-parse','--show-toplevel')).Trim()
if ([IO.Path]::GetFullPath($top).TrimEnd('\') -ine [IO.Path]::GetFullPath($wt).TrimEnd('\')) {
    throw 'HOLD_WRONG_EXACT_TOPK_WORKTREE'
}
$dirty = @(GitExact -Arguments @('-C',$wt,'status','--porcelain=v1','--untracked-files=all'))
if (@($dirty | Where-Object { $_ -and $_.Trim() }).Count -ne 0) {
    throw 'HOLD_DIRTY_TOPK_WORKTREE'
}
$current = (GitExact -Arguments @('-C',$wt,'rev-parse','HEAD')).Trim()
if ($current -ne $pin) {
    GitExact -Arguments @('-C',$root,'fetch','origin',("refs/heads/" + $branch + ":refs/remotes/origin/" + $branch)) | Out-Null
    $type = (GitExact -Arguments @('-C',$root,'cat-file','-t',$pin)).Trim()
    if ($type -ne 'commit') { throw 'HOLD_SOURCE_COMMIT_NOT_FOUND' }
    GitExact -Arguments @('-C',$wt,'checkout','--detach',$pin) | Out-Null
}
if ((GitExact -Arguments @('-C',$wt,'rev-parse','HEAD')).Trim() -ne $pin) { throw 'HOLD_WRONG_FROZEN_SOURCE_COMMIT' }
RequireBlob "$src/frozen_topk_probe_one_shot.py" 'd6e2cb2b087342234f8f722de70b6de429c550c3'
RequireBlob "$src/independent_frozen_topk_runner_qa.py" '11d98c4d8528f0d1312652242362cc5e867e327f'
RequireBlob "$src/topk_reader_integration.py" 'ccab713f8c5a4b913259088225daffcf5382be41'
RequireBlob "$src/oracle_reader_source_only.py" '7ce728b2874284b87933237c890e54ce3d9fd651'
RequireBlob "$src/topk_nontest_probe.py" 'b08e2120a2ac9d4e270ee48fdca77e4a4743e22c'
RequireBlob "$src/cpu_pilot_readiness.py" '6c43d2889f39a4ad537ace78ecbff40294089031'
RequireBlob 'tools/pilot_t4/integrated/p02_source_exact.py' '9762343e06cf800b50574c2871ae1ed58537fb18'
RequireBlob 'tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py' 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
RequireSHA $ck 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc' 'ORIGINAL_BACKBONE'
RequireSHA $t1 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc' 'REAL_T1_MANIFEST'
RequireSHA $reader 'c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f' 'L0020_PRIVATE_READER'
& $py -c 'import sys,torch,numpy,regex;assert sys.version_info[:2]==(3,12);assert torch.__version__'
if ($LASTEXITCODE -ne 0) { throw 'HOLD_PYTHON312_DEPENDENCIES' }
if (-not (Test-Path -LiteralPath $qaOutput -PathType Leaf)) {
    & $py $qa --out $qaOutput
    if ($LASTEXITCODE -ne 0) { throw 'HOLD_INDEPENDENT_SCORER_QA_FAILED' }
}
$record = Get-Content -LiteralPath $qaOutput -Raw -Encoding UTF8 | ConvertFrom-Json
if ($record.status -ne 'PASS_PREEXEC_SCOPED_SOURCE_QA' -or
    $record.checks_passed -ne 66 -or $record.checks_total -ne 66 -or
    $record.execution.probe_science_runs -ne 0 -or $record.execution.test_opened -ne $false) {
    throw 'HOLD_QA_RECEIPT_INVALID'
}
if ((GitExact -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim() -ne $mainBefore) {
    throw 'HOLD_MAIN_REF_CHANGED'
}
Write-Output 'OWNER_CPU_PROBE_ONE_SHOT_DECISION=GO_SCOPED'
Write-Output ('PINNED_SCIENCE_SOURCE_COMMIT=' + $pin)
Write-Output 'INDEPENDENT_SCORER_QA=PASS_66_66'
Write-Output 'READER_L0020_SHA256=PASS'
Write-Output 'PROBE_SCIENCE_NOT_STARTED=TRUE'
Write-Output 'DEV_TEST_NOT_OPENED=TRUE'
Write-Output 'MAIN_UNCHANGED=TRUE'
if (-not $ExecuteOnce) {
    Write-Output 'EXECUTION_NOT_REQUESTED=TRUE'
    exit 0
}
if (Test-Path -LiteralPath $runDir) { throw 'HOLD_ONE_SHOT_ALREADY_STARTED_NO_RERUN' }
& $py $runner --execute-once --project-root $root --checkout $wt --checkpoint $ck --reader $reader --t1-manifest $t1 --output-dir $runDir
if ($LASTEXITCODE -ne 0) { throw 'ONE_SHOT_FAILED_DO_NOT_RETRY_OR_CLEAN' }
if (-not (Test-Path -LiteralPath $report -PathType Leaf)) { throw 'SCIENCE_RESULT_MISSING_DO_NOT_RERUN' }
$done = Get-Content -LiteralPath $report -Raw -Encoding UTF8 | ConvertFrom-Json
if ($done.cases -ne 128 -or $done.test_opened -ne $false -or $done.optimizer_steps -ne 0) {
    throw 'SCIENCE_RESULT_SCHEMA_HOLD'
}
Write-Output ('SCIENCE_VERDICT=' + $done.verdict)
Write-Output ('RECALL_AT_1=' + $done.recall.r1)
Write-Output ('RECALL_AT_3=' + $done.recall.r3)
Write-Output ('PROBE_RESULT_SHA256=' + (Get-FileHash -LiteralPath $report -Algorithm SHA256).Hash)
Write-Output 'TEST_NOT_OPENED=TRUE'
