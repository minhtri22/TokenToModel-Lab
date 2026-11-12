# TTM V2 NONTEST CPU: source-pin, independent mock QA, owner one-shot GO/HOLD.
# Default: PREEXEC ONLY. -ExecuteOnce: consume exactly one 192-case CPU run.
# Existing fixture/checkpoint/Reader are read-only; all new files are inside project D:.
[CmdletBinding()]
param([switch]$ExecuteOnce)
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $root 'worktrees\ttm-vm-v2-source-20261112'
$source = 'tools/research/vector-memory'
$sourcePin = 'df7865a420cbd5d58d5f24a55b85f99c9242038e'
$branch = 'research/ttm-vector-memory-architecture-20261111'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$fixture = Join-Path $root '_evidence\vector-memory\TTM_VM_V2_NONTEST_NEW192_ID_ALIAS_DESC_20261112.private.json'
$reader = Join-Path $root '_evidence\vector-memory\TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1\reader_private.pt'
$ck = Join-Path $root '_tmp\vector-memory\checkpoint.pt'
$t1 = Join-Path $root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
$runDir = Join-Path $root '_evidence\vector-memory\TTM_VM_V2_NONTEST_192_FROZEN_READER_CPU_ONESHOT_V1'
$qaDir = Join-Path $root '_evidence\vector-memory'
$qaOutput = Join-Path $qaDir 'TTM_VM_V2_FROZEN_SCORER_INDEPENDENT_OWNER_QA_20261112.json'
$runner = Join-Path $wt "$source/v2_frozen_reader_cpu_one_shot.py"
$qa = Join-Path $wt "$source/v2_independent_one_shot_scorer_qa.py"
$expectedFixture = '1d7c02ab082a3c34345953dc5146e5a93f8c6f44e11132ea8abb0594efcc0b9d'

# Prevent Windows Python from writing bytecode or temporary QA files on C:.
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONNOUSERSITE = '1'
$tmp = Join-Path $root '_tmp\vector-memory\v2-owner-qa-temp'
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
$env:TEMP = $tmp
$env:TMP = $tmp
$env:TMPDIR = $tmp

function GitRead {
    param([string[]]$Arguments)
    $v = & git.exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('GIT_READ_FAILED:' + ($Arguments -join ' ')) }
    return $v
}
function CheckBlob {
    param([string]$Relative, [string]$Expected)
    $path = Join-Path $wt $Relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw ('HOLD_SOURCE_MISSING:'+$Relative) }
    $actual = (GitRead -Arguments @('-C',$wt,'hash-object','--',$Relative)).Trim()
    if ($actual -ne $Expected) { throw ('HOLD_SOURCE_GIT_BLOB_MISMATCH:'+$Relative) }
}
function CheckSHA {
    param([string]$Path,[string]$Expected,[string]$Name)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw ('HOLD_INPUT_MISSING:'+$Name) }
    $actual = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $Expected) { throw ('HOLD_SHA256_MISMATCH:'+$Name) }
}
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'HOLD_ROOT_MISSING' }
if (-not (Test-Path -LiteralPath $wt -PathType Container)) { throw 'HOLD_V2_SOURCE_WORKTREE_MISSING' }
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'HOLD_PYTHON312_MISSING' }
if (Test-Path -LiteralPath $runDir) { throw 'HOLD_ONE_SHOT_ALREADY_STARTED_NO_RETRY' }
$origin = (GitRead -Arguments @('-C',$root,'remote','get-url','origin')).Trim()
if ($origin -notin @('https://github.com/minhtri22/TokenToModel-Lab',
                     'https://github.com/minhtri22/TokenToModel-Lab.git')) { throw 'HOLD_WRONG_ORIGIN' }
$main = (GitRead -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim()
$top = (GitRead -Arguments @('-C',$wt,'rev-parse','--show-toplevel')).Trim()
if ([IO.Path]::GetFullPath($top).TrimEnd('\') -ine [IO.Path]::GetFullPath($wt).TrimEnd('\')) {
    throw 'HOLD_WRONG_WORKTREE_ROOT'
}
$dirty = @(GitRead -Arguments @('-C',$wt,'status','--porcelain=v1','--untracked-files=all'))
if (@($dirty | Where-Object { $_ -and $_.Trim() }).Count -ne 0) { throw 'HOLD_V2_WORKTREE_DIRTY' }
$head = (GitRead -Arguments @('-C',$wt,'rev-parse','HEAD')).Trim()
if ($head -ne $sourcePin) {
    GitRead -Arguments @('-C',$root,'fetch','origin',$branch) | Out-Null
    if ((GitRead -Arguments @('-C',$root,'cat-file','-t',$sourcePin)).Trim() -ne 'commit') {
        throw 'HOLD_SOURCE_PIN_UNAVAILABLE'
    }
    GitRead -Arguments @('-C',$wt,'checkout','--detach',$sourcePin) | Out-Null
}
if ((GitRead -Arguments @('-C',$wt,'rev-parse','HEAD')).Trim() -ne $sourcePin) {
    throw 'HOLD_SOURCE_HEAD_DRIFT'
}
CheckBlob "$source/v2_frozen_reader_cpu_one_shot.py" 'e9e29c35e4eeeda6ed3ad5a4481a75b51e5b4eab'
CheckBlob "$source/v2_independent_one_shot_scorer_qa.py" '06ba0bd001293f759a0783f81e3ce4cc9ae0142e'
CheckBlob "$source/v2_nontest_fixture.py" '01703d4786872a66459593d27cd7607b66c895dd'
CheckBlob "$source/v2_nontest_retrievers.py" 'dc733eda42d768d695309e3a1d5df25aeabb28b7'
CheckBlob "$source/v2_independent_source_qa.py" 'a9ad31e4054cdd904174a49be2fbac14e92ee906'
CheckBlob "$source/oracle_reader_source_only.py" '7ce728b2874284b87933237c890e54ce3d9fd651'
CheckBlob "$source/topk_reader_integration.py" 'ccab713f8c5a4b913259088225daffcf5382be41'
CheckBlob "$source/cpu_pilot_readiness.py" '6c43d2889f39a4ad537ace78ecbff40294089031'
CheckBlob 'tools/pilot_t4/integrated/p02_source_exact.py' '9762343e06cf800b50574c2871ae1ed58537fb18'
CheckBlob 'tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py' 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
CheckBlob 'lineage.md' '5bc9c2a2b6f17fb74ef76e747f695ca9223b0e55'

CheckSHA $fixture $expectedFixture 'NEW_192_PROBE'
CheckSHA $reader 'c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f' 'L0020_READER'
CheckSHA $ck 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc' 'FROZEN_P02'
CheckSHA $t1 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc' 'REAL_T1'
& $py -B -c 'import sys,torch,numpy,regex;assert sys.version_info[:2]==(3,12);assert torch.__version__'
if ($LASTEXITCODE -ne 0) { throw 'HOLD_PY312_DEPENDENCY_PROBE' }

if (-not (Test-Path -LiteralPath $qaOutput -PathType Leaf)) {
    New-Item -ItemType Directory -Path $qaDir -Force | Out-Null
    & $py -B $qa --out $qaOutput
    if ($LASTEXITCODE -ne 0) { throw 'HOLD_78_QA_FAILED' }
}
$result = Get-Content -LiteralPath $qaOutput -Raw -Encoding UTF8 | ConvertFrom-Json
if ($result.status -ne 'PASS_INDEPENDENT_ONE_SHOT_SCORER_QA' -or
    $result.checks_total -ne 78 -or $result.checks_passed -ne 78 -or
    $result.real_192_fixture_scored -ne $false -or
    $result.trained_reader_opened -ne $false -or
    $result.TEST_opened -ne $false -or $result.optimizer_steps -ne 0) {
    throw 'HOLD_OWNER_QA_RECEIPT_INVALID'
}
$ckResults = @($result.checks.PSObject.Properties)
if ($ckResults.Count -ne 78 -or @($ckResults | Where-Object { $_.Value -ne $true }).Count -ne 0) {
    throw 'HOLD_OWNER_QA_BOOLEAN_CHECKS'
}
if ((GitRead -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim() -ne $main) {
    throw 'HOLD_MAIN_CHANGED'
}
Write-Output 'V2_CPU_ONESHOT_PREEXEC=GO_SCOPED'
Write-Output ('V2_PINNED_SOURCE_COMMIT=' + $sourcePin)
Write-Output 'V2_FROZEN_SCORER_QA=PASS_78_78'
Write-Output 'V2_PROBE_SHA256=PASS'
Write-Output 'V2_READER_SHA256=PASS'
Write-Output 'V2_BACKBONE_T1_SHA256=PASS'
Write-Output 'V2_PROBE_SCIENCE=NOT_EXECUTED'
Write-Output 'OLD_PROBE_DEV_TEST=UNCHANGED_SEALED'
Write-Output ('V2_QA_RECEIPT_SHA256=' + (Get-FileHash -LiteralPath $qaOutput -Algorithm SHA256).Hash)
if (-not $ExecuteOnce) {
    Write-Output 'EXECUTION_NOT_REQUESTED=TRUE'
    exit 0
}
if (Test-Path -LiteralPath $runDir) { throw 'HOLD_ALREADY_CONSUMED_NO_RETRY' }
& $py -B $runner --execute-once --project-root $root --checkout $wt --checkpoint $ck --reader $reader --t1-manifest $t1 --fixture $fixture --output-dir $runDir
if ($LASTEXITCODE -ne 0) { throw 'V2_ONE_SHOT_FAILED_DO_NOT_RERUN_OR_CLEAN' }
$aggregate = Join-Path $runDir 'PROBE_AGGREGATE_PUBLIC.json'
if (-not (Test-Path -LiteralPath $aggregate -PathType Leaf)) {
    throw 'HOLD_RESULT_NOT_FOUND_DO_NOT_RERUN'
}
$science = Get-Content -LiteralPath $aggregate -Raw -Encoding UTF8 | ConvertFrom-Json
if ($science.cases -ne 192 -or $science.optimizer_steps -ne 0 -or $science.test_opened -ne $false) {
    throw 'HOLD_RESULT_SCHEMA_INVALID'
}
Write-Output ('V2_SCIENCE_VERDICT=' + $science.verdict)
Write-Output ('V2_S2_RECALL_AT_1=' + $science.strata.S2_DESC_PARAPHRASE.recall1)
Write-Output ('V2_S2_HITS_AT_1=' + $science.strata.S2_DESC_PARAPHRASE.hits1)
Write-Output ('V2_AGGREGATE_SHA256=' + (Get-FileHash -LiteralPath $aggregate -Algorithm SHA256).Hash)
Write-Output 'V2_TEST_NOT_OPENED=TRUE'
