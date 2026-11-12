# TTM Vector Memory V2: 192 NONTEST fixture source QA + on-D byte SHA freeze ONLY.
# No model inference, no training, no old PROBE scoring, no DEV/TEST, no GPU.
# Windows PowerShell 5.1; Python312 read-only on C:, outputs solely under project D:.
[CmdletBinding()]
param([switch]$GenerateFixture)
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$branch = 'research/ttm-vector-memory-architecture-20261111'
$sourcePin = 'be3d24e6e86b7983f8882a6689a09fd6155fded7'
$wt = Join-Path $root 'worktrees\ttm-vm-v2-source-20261112'
$python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$rel = 'tools/research/vector-memory'
$qaOutput = Join-Path $root '_evidence\vector-memory\TTM_VM_V2_SOURCE_NEGATIVE_QA_OWNER_20261112.json'
$fixtureOutput = Join-Path $root '_evidence\vector-memory\TTM_VM_V2_NONTEST_NEW192_ID_ALIAS_DESC_20261112.private.json'
$expectedFixtureSHA = '1d7c02ab082a3c34345953dc5146e5a93f8c6f44e11132ea8abb0594efcc0b9d'
$expectedLineageBlob = '5bc9c2a2b6f17fb74ef76e747f695ca9223b0e55'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONNOUSERSITE = '1'

function GitExact {
    param([string[]]$Arguments)
    $output = & git.exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('GIT_FAILED:' + ($Arguments -join ' ')) }
    return $output
}
function RequireGitBlob {
    param([string]$Relative,[string]$Expected)
    $file = Join-Path $wt $Relative
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw ('MISSING_SOURCE:' + $Relative) }
    $blob = (GitExact -Arguments @('-C',$wt,'hash-object','--',$Relative)).Trim()
    if ($blob -ne $Expected) { throw ('SOURCE_GIT_BLOB_MISMATCH:' + $Relative) }
}
function RequireNativeSHA {
    param([string]$File,[string]$Expected,[string]$Label)
    if (-not (Test-Path -LiteralPath $File -PathType Leaf)) { throw ('MISSING_' + $Label) }
    $got = (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($got -ne $Expected) { throw ('SHA_MISMATCH_' + $Label + '_' + $got) }
}

if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'RESEARCH_ROOT_MISSING' }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'PYTHON312_MISSING' }
$origin = (GitExact -Arguments @('-C',$root,'remote','get-url','origin')).Trim()
if ($origin -notin @('https://github.com/minhtri22/TokenToModel-Lab','https://github.com/minhtri22/TokenToModel-Lab.git')) {
    throw 'WRONG_GITHUB_ORIGIN'
}
$mainBefore = (GitExact -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim()
if (-not (Test-Path -LiteralPath $wt -PathType Container)) {
    GitExact -Arguments @('-C',$root,'fetch','origin',$branch) | Out-Null
    $type = (GitExact -Arguments @('-C',$root,'cat-file','-t',$sourcePin)).Trim()
    if ($type -ne 'commit') { throw 'SOURCE_PIN_NOT_COMMIT' }
    GitExact -Arguments @('-C',$root,'worktree','add','--detach',$wt,$sourcePin) | Out-Null
}
$top = (GitExact -Arguments @('-C',$wt,'rev-parse','--show-toplevel')).Trim()
if ([IO.Path]::GetFullPath($top).TrimEnd('\') -ine [IO.Path]::GetFullPath($wt).TrimEnd('\')) {
    throw 'WRONG_V2_WORKTREE'
}
$head = (GitExact -Arguments @('-C',$wt,'rev-parse','HEAD')).Trim()
if ($head -ne $sourcePin) { throw 'V2_SCIENTIFIC_SOURCE_CHECKOUT_MISMATCH' }
$dirty = @(GitExact -Arguments @('-C',$wt,'status','--porcelain=v1','--untracked-files=all'))
if (@($dirty | Where-Object { $_ -and $_.Trim() }).Count -ne 0) { throw 'V2_SOURCE_WORKTREE_DIRTY' }
RequireGitBlob "$rel/v2_nontest_fixture.py" '01703d4786872a66459593d27cd7607b66c895dd'
RequireGitBlob "$rel/v2_nontest_retrievers.py" 'dc733eda42d768d695309e3a1d5df25aeabb28b7'
RequireGitBlob "$rel/v2_independent_source_qa.py" 'a9ad31e4054cdd904174a49be2fbac14e92ee906'
RequireGitBlob 'lineage.md' $expectedLineageBlob
& $python -B -c 'import sys,torch;assert sys.version_info[:2]==(3,12);assert torch.__version__'
if ($LASTEXITCODE -ne 0) { throw 'PY312_TORCH_VERSION_INVALID' }

if (-not (Test-Path -LiteralPath $qaOutput -PathType Leaf)) {
    New-Item -ItemType Directory -Force -Path (Split-Path $qaOutput) | Out-Null
    & $python -B (Join-Path $wt "$rel/v2_independent_source_qa.py") --out $qaOutput
    if ($LASTEXITCODE -ne 0) { throw 'V2_INDEPENDENT_SOURCE_NEGATIVE_QA_FAILED' }
}
$qa = Get-Content -LiteralPath $qaOutput -Raw -Encoding UTF8 | ConvertFrom-Json
if ($qa.status -ne 'PASS_SOURCE_NEGATIVE_QA' -or $qa.checks_passed -ne 72 -or
    $qa.checks_total -ne 72 -or $qa.fixture_sha256 -ne $expectedFixtureSHA -or
    $qa.real_probe_retrieval_calls -ne 0 -or $qa.reader_forward_calls -ne 0 -or
    $qa.test_opened -ne $false -or $qa.old_probe_rescored -ne $false) {
    throw 'V2_INDEPENDENT_QA_RECEIPT_INVALID'
}

if ($GenerateFixture -and -not (Test-Path -LiteralPath $fixtureOutput -PathType Leaf)) {
    & $python -B (Join-Path $wt "$rel/v2_nontest_fixture.py") --project-root $root --out $fixtureOutput --write-once
    if ($LASTEXITCODE -ne 0) { throw 'V2_FIXTURE_WRITE_FAILED_DO_NOT_OVERWRITE' }
}
if (Test-Path -LiteralPath $fixtureOutput -PathType Leaf) {
    RequireNativeSHA $fixtureOutput $expectedFixtureSHA 'V2_FIXTURE'
    $bytes = (Get-Item -LiteralPath $fixtureOutput).Length
    if ($bytes -ne 1913776) { throw 'V2_FIXTURE_BYTES_MISMATCH' }
    Write-Output 'V2_PRIVATE_FIXTURE_ON_D=PASS'
    Write-Output ('V2_FIXTURE_SHA256=' + $expectedFixtureSHA)
}
else {
    Write-Output 'V2_PRIVATE_FIXTURE_ON_D=NOT_YET_GENERATED'
}
if ((GitExact -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim() -ne $mainBefore) {
    throw 'MAIN_REF_CHANGED'
}
Write-Output 'V2_SOURCE_PINS=PASS'
Write-Output 'V2_SOURCE_NEGATIVE_QA=PASS_72_72'
Write-Output ('V2_SOURCE_COMMIT=' + $sourcePin)
Write-Output ('QA_RECEIPT_SHA256=' + (Get-FileHash -LiteralPath $qaOutput -Algorithm SHA256).Hash)
Write-Output 'V2_PROBE_RETRIEVAL_OR_NLL=NOT_EXECUTED'
Write-Output 'L0021_OLD_PROBE_DEV_TEST=UNCHANGED_SEALED'
Write-Output 'V2_CPU_SCIENCE_RELEASE=HOLD_NO_PINNED_ONE_SHOT_SCORER'
