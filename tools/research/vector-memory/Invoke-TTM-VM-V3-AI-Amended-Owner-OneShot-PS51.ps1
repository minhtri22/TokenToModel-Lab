# TTM V3 AI-amended frozen Reader owner preflight. Default: NO SCIENCE.
# Explicit -ExecuteOnce after all SHA/source/AI/QA gates: one CPU run only.
[CmdletBinding()]
param([switch]$ExecuteOnce)
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$branch = 'research/ttm-vector-memory-architecture-20261111'
$scienceSourceCommit = 'e258f117d0422e2e83d9cf5937aad889f187a2bf'
$wt = Join-Path $root 'worktrees\ttm-vm-v3-source-20261112'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$source = 'tools/research/vector-memory'
$subdir = Join-Path $wt $source
$evidence = Join-Path $root '_evidence\vector-memory'
$fixture = Join-Path $evidence 'TTM_VM_V3_FRESH256_NONTEST_PRIVATE_20261112.json'
$reader = Join-Path $evidence 'TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1\reader_private.pt'
$ck = Join-Path $root '_tmp\vector-memory\checkpoint.pt'
$t1 = Join-Path $root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
$reviewA = Join-Path $wt 'docs\research\vector-memory\P1_REVIEW_A_AI_UNVERIFIED.json'
$reviewB = Join-Path $wt 'docs\research\vector-memory\P1_REVIEW_B_AI_UNVERIFIED.json'
$nativeSourceQA = Join-Path $evidence 'TTM_VM_V3_FRESH256_OWNER_SOURCE_QA_20261112.json'
$aiReceipt = Join-Path $evidence 'TTM_VM_V3_OWNER_AI_SUBSTITUTION_CUSTODY_20261112.json'
$qaReceipt = Join-Path $evidence 'TTM_VM_V3_AI_AMENDED_SCORER_OWNER_MOCK_QA_20261112.json'
$runID = 'TTM_VM_V3_NONTEST_256_FROZEN_READER_CPU_ONESHOT_V1'
$runDir = Join-Path $evidence $runID
$fixtureSHA = 'd473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONUNBUFFERED = '1'
$ownerTmp = Join-Path $root '_tmp\vector-memory\v3-ai-owner-preexec'
New-Item -ItemType Directory -Force -Path $ownerTmp | Out-Null
$env:TEMP = $ownerTmp
$env:TMP = $ownerTmp
$env:TMPDIR = $ownerTmp

function GitRead {
    param([string[]]$Arguments)
    $output = & git.exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('GIT_FAILED:' + ($Arguments -join ' ')) }
    return $output
}
function RequireBlob {
    param([string]$Relative,[string]$Expected)
    $file = Join-Path $wt $Relative
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw ('MISSING_SOURCE:' + $Relative) }
    $actual = (GitRead -Arguments @('-C',$wt,'hash-object','--',$Relative)).Trim()
    if ($actual -ne $Expected) { throw ('SOURCE_BLOB_MISMATCH:' + $Relative) }
}
function RequireSHA {
    param([string]$File,[string]$Expected,[string]$Label)
    if (-not (Test-Path -LiteralPath $File -PathType Leaf)) { throw ('MISSING_INPUT:' + $Label) }
    $actual = (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $Expected) { throw ('INPUT_SHA_MISMATCH:' + $Label + ':' + $actual) }
}

if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'RESEARCH_PROJECT_ROOT_MISSING' }
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'PY312_MISSING' }
if (Test-Path -LiteralPath $runDir) { throw 'ONE_SHOT_ALREADY_STARTED_NO_RETRY' }
$origin = (GitRead -Arguments @('-C',$root,'remote','get-url','origin')).Trim()
if ($origin -notin @('https://github.com/minhtri22/TokenToModel-Lab',
                     'https://github.com/minhtri22/TokenToModel-Lab.git')) {
    throw 'WRONG_ORIGIN'
}
$mainBefore = (GitRead -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim()
GitRead -Arguments @('-C',$root,'fetch','origin',$branch) | Out-Null
if ((GitRead -Arguments @('-C',$root,'cat-file','-t',$scienceSourceCommit)).Trim() -ne 'commit') {
    throw 'PINNED_SCIENCE_SOURCE_COMMIT_MISSING'
}
if (-not (Test-Path -LiteralPath $wt -PathType Container)) {
    GitRead -Arguments @('-C',$root,'worktree','add','--detach',$wt,$scienceSourceCommit) | Out-Null
}
$top = (GitRead -Arguments @('-C',$wt,'rev-parse','--show-toplevel')).Trim()
if ([IO.Path]::GetFullPath($top).TrimEnd('\') -ine [IO.Path]::GetFullPath($wt).TrimEnd('\')) {
    throw 'WRONG_RESEARCH_WORKTREE'
}
$dirty = @(GitRead -Arguments @('-C',$wt,'status','--porcelain=v1','--untracked-files=all'))
if (@($dirty | Where-Object { $_ -and $_.Trim() }).Count -ne 0) { throw 'SOURCE_WORKTREE_NOT_CLEAN' }
if ((GitRead -Arguments @('-C',$wt,'rev-parse','HEAD')).Trim() -ne $scienceSourceCommit) {
    GitRead -Arguments @('-C',$wt,'checkout','--detach',$scienceSourceCommit) | Out-Null
}
if ((GitRead -Arguments @('-C',$wt,'rev-parse','HEAD')).Trim() -ne $scienceSourceCommit) { throw 'SCIENCE_HEAD_DRIFT' }

RequireBlob "$source/v3_ai_review_custody_amendment.py" 'ede2ee6438dc9b5ba106195e529eb3124d53f31b'
RequireBlob "$source/v3_ai_amended_frozen_reader_cpu_one_shot.py" '32e2a15ba56916958102294efe4d91c4fbc812e4'
RequireBlob "$source/v3_ai_amended_independent_scorer_qa.py" 'a4c87edf055d4dbc97f2fc9721f3cb798df003b5'
RequireBlob "$source/v3_fresh256_fixture.py" '5f51b8b464e54a370f3a3fa99d91307118f52f46'
RequireBlob "$source/v3_nonoracle_retriever.py" '68bfeaaf1d0acf0cf446e4d734e34368fbf8f702'
RequireBlob "$source/v3_p1_reviewer_custody.py" 'beaaa78126282439c94b2d0d525297e6b35266a5'
RequireBlob "$source/v3_independent_source_qa.py" '041e174579e5a842a0d4dfa46637fe036e9954ec'
RequireBlob "$source/oracle_reader_source_only.py" '7ce728b2874284b87933237c890e54ce3d9fd651'
RequireBlob "$source/topk_reader_integration.py" 'ccab713f8c5a4b913259088225daffcf5382be41'
RequireBlob "$source/cpu_pilot_readiness.py" '6c43d2889f39a4ad537ace78ecbff40294089031'
RequireBlob "$source/v2_nontest_retrievers.py" 'dc733eda42d768d695309e3a1d5df25aeabb28b7'
RequireBlob 'tools/pilot_t4/integrated/p02_source_exact.py' '9762343e06cf800b50574c2871ae1ed58537fb18'
RequireBlob 'tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py' 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
RequireBlob 'lineage.md' '2d526cf4c6dae2dfbbbad1722f5cd77d7e7efd82'
RequireBlob 'docs/research/vector-memory/P1_REVIEW_A_AI_UNVERIFIED.json' '034d1511a2b971726b2607ba63f08e2be92682c3'
RequireBlob 'docs/research/vector-memory/P1_REVIEW_B_AI_UNVERIFIED.json' 'be9c573ae480455e860d331f112e2b3f94c69036'

RequireSHA $reviewA '46c9fad4b77065cf086213c64ee04145704efa8d6dd3cfbad56d80c9e1d68ed6' 'AI_A_RAW'
RequireSHA $reviewB 'fd719ada13d2e44a72d29af04d18bb5d839547b288046ce410cfa9e5b7e49cdf' 'AI_B_RAW'
RequireSHA $fixture $fixtureSHA 'V3_PRIVATE_256_FIXTURE'
RequireSHA $reader 'c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f' 'READER_L0020'
RequireSHA $ck 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc' 'P02_FROZEN'
RequireSHA $t1 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc' 'REAL_T1_MANIFEST'
RequireSHA $nativeSourceQA 'fe0cf99c8cbbfb85e07ce0f57f760cee7f24a2c8c4e01d3a21f90b4e9214b6' 'V3_OWNER_SOURCE_QA_99'
$sourceQA = Get-Content -LiteralPath $nativeSourceQA -Raw -Encoding UTF8 | ConvertFrom-Json
if ($sourceQA.checks_passed -ne 99 -or $sourceQA.checks_total -ne 99) { throw 'NATIVE_V3_SOURCE_QA_99_MISMATCH' }

& $py -B -c 'import sys,torch,numpy,regex; assert sys.version_info[:2]==(3,12); assert torch.__version__'
if ($LASTEXITCODE -ne 0) { throw 'PY312_TORCH_DEPENDENCY_GATE_FAIL' }

if (-not (Test-Path -LiteralPath $aiReceipt -PathType Leaf)) {
    & $py -B (Join-Path $subdir 'v3_ai_review_custody_amendment.py') --project-root $root --fixture $fixture --review-a $reviewA --review-b $reviewB --out $aiReceipt
    if ($LASTEXITCODE -ne 0) { throw 'AI_CUSTODY_NATIVE_QA_HOLD' }
}
$AI = Get-Content -LiteralPath $aiReceipt -Raw -Encoding UTF8 | ConvertFrom-Json
if ($AI.status -ne 'PASS_TWO_AI_BLIND_REVIEW_SOURCE_AND_GOLD_32_OF_32_EXPLORATORY' -or
    $AI.agent_agreement -ne 32 -or $AI.agent_A_gold_match -ne 32 -or
    $AI.agent_B_gold_match -ne 32 -or $AI.human_gate_satisfied -ne $false -or
    $AI.fixture_sha256 -ne $fixtureSHA -or $AI.TEST_opened -ne $false) {
    throw 'AI_CUSTODY_RECEIPT_REJECTED'
}
if (-not (Test-Path -LiteralPath $qaReceipt -PathType Leaf)) {
    & $py -B (Join-Path $subdir 'v3_ai_amended_independent_scorer_qa.py') --out $qaReceipt
    if ($LASTEXITCODE -ne 0) { throw 'V3_100_MOCK_QA_NATIVE_FAILED' }
}
$QA = Get-Content -LiteralPath $qaReceipt -Raw -Encoding UTF8 | ConvertFrom-Json
if ($QA.status -ne 'PASS_INDEPENDENT_V3_SCORER_MOCK_QA' -or
    $QA.checks_passed -ne 100 -or $QA.checks_total -ne 100 -or
    $QA.actual_new256_retriever_scored -ne $false -or
    $QA.actual_new256_reader_forward -ne $false -or
    $QA.TEST_opened -ne $false -or $QA.optimizer_steps -ne 0) {
    throw 'V3_MOCK_QA_RECEIPT_INVALID'
}
$checks = @($QA.checks.PSObject.Properties)
if ($checks.Count -ne 100 -or @($checks | Where-Object { $_.Value -ne $true }).Count -ne 0) {
    throw 'V3_MOCK_QA_NOT_100_100_TRUE'
}
if ((GitRead -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim() -ne $mainBefore) { throw 'MAIN_HEAD_CHANGED' }
if (Test-Path -LiteralPath $runDir) { throw 'ONE_SHOT_ALREADY_STARTED_NO_RETRY' }

Write-Output 'V3_AI_SUBSTITUTION_OWNER_NATIVE_PREEXEC=GO_SCOPED'
Write-Output ('V3_SCIENCE_SOURCE_COMMIT=' + $scienceSourceCommit)
Write-Output 'V3_AI_A_B_SHA_AND_GOLD=PASS_32_32'
Write-Output 'V3_HUMAN_REVIEW=NOT_SATISFIED_0_2'
Write-Output 'V3_V3_SOURCE_QA=PASS_99_99'
Write-Output 'V3_SCORER_MOCK_QA=PASS_100_100'
Write-Output 'V3_FIXTURE_READER_P02_T1_SHA=PASS'
Write-Output ('V3_AI_CUSTODY_RECEIPT_SHA256=' + (Get-FileHash -LiteralPath $aiReceipt -Algorithm SHA256).Hash)
Write-Output ('V3_NATIVE_QA_RECEIPT_SHA256=' + (Get-FileHash -LiteralPath $qaReceipt -Algorithm SHA256).Hash)
Write-Output 'V3_TEST=SEALED;GPU=NO;MAIN=UNCHANGED;LINEAGE=L0022'
if (-not $ExecuteOnce) {
    Write-Output 'V3_SCIENCE=NOT_EXECUTED'
    Write-Output 'OWNER_GO_HOLD=GO_SCOPED_PREEXEC_ONLY'
    exit 0
}
if (Test-Path -LiteralPath $runDir) { throw 'ONE_SHOT_ALREADY_STARTED_NO_RETRY' }
& $py -B (Join-Path $subdir 'v3_ai_amended_frozen_reader_cpu_one_shot.py') --execute-once --project-root $root --checkout $wt --checkpoint $ck --reader $reader --t1-manifest $t1 --fixture $fixture --review-a $reviewA --review-b $reviewB --output-dir $runDir
if ($LASTEXITCODE -ne 0) { throw 'V3_CPU_ONE_SHOT_FAILED_DO_NOT_RERUN_OR_CLEAN' }
$agg = Join-Path $runDir 'PROBE_AGGREGATE_PUBLIC.json'
if (-not (Test-Path -LiteralPath $agg -PathType Leaf)) { throw 'V3_NO_AGGREGATE_DO_NOT_RERUN' }
$result = Get-Content -LiteralPath $agg -Raw -Encoding UTF8 | ConvertFrom-Json
if ($result.cases -ne 256 -or $result.optimizer_steps -ne 0 -or $result.test_opened -ne $false -or
    $result.human_gate_satisfied -ne $false -or $result.review_class -ne 'AI_ASSISTED_EXPLORATORY_SCOPED') {
    throw 'V3_SCIENCE_RESULT_METADATA_HOLD'
}
Write-Output ('V3_SCIENCE_VERDICT=' + $result.verdict)
Write-Output ('V3_AGGREGATE_SHA256=' + (Get-FileHash -LiteralPath $agg -Algorithm SHA256).Hash)
Write-Output 'V3_ONE_SHOT_CONSUMED=TRUE'
