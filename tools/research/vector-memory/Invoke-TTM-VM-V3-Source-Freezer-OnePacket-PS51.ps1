# V3 source-only owner onepacket. No Reader inference, training, DEV/TEST, GPU.
# Windows PowerShell 5.1. Writes only under D:\WORK\RESEARCH\TokenToModel-Lab.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$branch = 'research/ttm-vector-memory-architecture-20261111'
$sourcePin = '51268b205648060ad0fa13276d67180c2fcaddbb'
$wt = Join-Path $root 'worktrees\ttm-vm-v3-source-20261112'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$subdir = 'tools/research/vector-memory'
$source = Join-Path $wt $subdir
$evidence = Join-Path $root '_evidence\vector-memory'
$qaFile = Join-Path $evidence 'TTM_VM_V3_FRESH256_OWNER_SOURCE_QA_20261112.json'
$fixture = Join-Path $evidence 'TTM_VM_V3_FRESH256_NONTEST_PRIVATE_20261112.json'
$reviewDir = Join-Path $evidence 'TTM_VM_V3_P1_BLIND_HUMAN_REVIEWS_20261112'
$receipt = Join-Path $reviewDir 'P1_TWO_REVIEWER_VALIDATED_RECEIPT.json'
$reviewA = Join-Path $reviewDir 'P1_REVIEW_A_SIGNED.json'
$reviewB = Join-Path $reviewDir 'P1_REVIEW_B_SIGNED.json'
$fixtureSHA = 'd473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONNOUSERSITE = '1'

function GitExact {
    param([string[]]$Arguments)
    $res = & git.exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw ('GIT_FAILED:' + ($Arguments -join ' ')) }
    return $res
}
function RequireBlob {
    param([string]$Relative,[string]$Expected)
    $filePath = Join-Path $wt $Relative
    if (-not (Test-Path -LiteralPath $filePath -PathType Leaf)) { throw ('MISSING_SOURCE:' + $Relative) }
    $sha = (GitExact -Arguments @('-C',$wt,'hash-object','--',$Relative)).Trim()
    if ($sha -ne $Expected) { throw ('SOURCE_BLOB_MISMATCH:' + $Relative) }
}

if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'RESEARCH_ROOT_MISSING' }
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'PYTHON312_MISSING' }
$origin = (GitExact -Arguments @('-C',$root,'remote','get-url','origin')).Trim()
if ($origin -notin @('https://github.com/minhtri22/TokenToModel-Lab','https://github.com/minhtri22/TokenToModel-Lab.git')) {
    throw 'WRONG_GITHUB_ORIGIN'
}
$mainBefore = (GitExact -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim()
if (-not (Test-Path -LiteralPath $wt -PathType Container)) {
    GitExact -Arguments @('-C',$root,'fetch','origin',$branch) | Out-Null
    if ((GitExact -Arguments @('-C',$root,'cat-file','-t',$sourcePin)).Trim() -ne 'commit') {
        throw 'FROZEN_SOURCE_PIN_NOT_COMMIT'
    }
    GitExact -Arguments @('-C',$root,'worktree','add','--detach',$wt,$sourcePin) | Out-Null
}
$top = (GitExact -Arguments @('-C',$wt,'rev-parse','--show-toplevel')).Trim()
if ([IO.Path]::GetFullPath($top).TrimEnd('\') -ine [IO.Path]::GetFullPath($wt).TrimEnd('\')) {
    throw 'WRONG_EXACT_WORKTREE'
}
if ((GitExact -Arguments @('-C',$wt,'rev-parse','HEAD')).Trim() -ne $sourcePin) {
    throw 'FROZEN_WORKTREE_HEAD_MISMATCH'
}
$dirty = @(GitExact -Arguments @('-C',$wt,'status','--porcelain=v1','--untracked-files=all'))
if (@($dirty | Where-Object { $_ -and $_.Trim() }).Count -ne 0) {
    throw 'FROZEN_WORKTREE_NOT_CLEAN'
}
RequireBlob "$subdir/v3_fresh256_fixture.py" '5f51b8b464e54a370f3a3fa99d91307118f52f46'
RequireBlob "$subdir/v3_nonoracle_retriever.py" '68bfeaaf1d0acf0cf446e4d734e34368fbf8f702'
RequireBlob "$subdir/v3_p1_reviewer_custody.py" 'beaaa78126282439c94b2d0d525297e6b35266a5'
RequireBlob "$subdir/v3_independent_source_qa.py" '041e174579e5a842a0d4dfa46637fe036e9954ec'
RequireBlob 'lineage.md' '2d526cf4c6dae2dfbbbad1722f5cd77d7e7efd82'
& $py -B -c 'import sys; assert sys.version_info[:2] == (3,12)'
if ($LASTEXITCODE -ne 0) { throw 'WRONG_PYTHON_VERSION' }

New-Item -ItemType Directory -Path $evidence -Force | Out-Null
if (-not (Test-Path -LiteralPath $qaFile -PathType Leaf)) {
    & $py -B (Join-Path $source 'v3_independent_source_qa.py') --out $qaFile
    if ($LASTEXITCODE -ne 0) { throw 'V3_INDEPENDENT_QA_FAILED' }
}
$qa = Get-Content -LiteralPath $qaFile -Raw -Encoding UTF8 | ConvertFrom-Json
$failed = @($qa.checks.PSObject.Properties | Where-Object { $_.Value -ne $true }).Count
if ($qa.status -ne 'PASS_SOURCE_STRUCTURAL_AND_MOCK_RETRIEVER_QA' -or
    $qa.qa_passed -ne 99 -or $qa.qa_total -ne 99 -or $failed -ne 0 -or
    $qa.private_fixture_sha256 -ne $fixtureSHA -or
    $qa.actual_v3_probe_retrieval_calls -ne 0 -or $qa.Reader_forward_calls -ne 0 -or
    $qa.test_opened -ne $false) {
    throw 'V3_QA_RECEIPT_INVALID'
}
if (-not (Test-Path -LiteralPath $fixture -PathType Leaf)) {
    & $py -B (Join-Path $source 'v3_fresh256_fixture.py') --project-root $root --out $fixture --write-once
    if ($LASTEXITCODE -ne 0) { throw 'V3_PRIVATE_FIXTURE_WRITE_FAILED_NO_OVERWRITE' }
}
$actualSHA = (Get-FileHash -LiteralPath $fixture -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualSHA -ne $fixtureSHA) { throw ('V3_FIXTURE_SHA_MISMATCH:' + $actualSHA) }
if ((Get-Item -LiteralPath $fixture).Length -ne 2128853) { throw 'V3_FIXTURE_BYTES_MISMATCH' }

$tplA = Join-Path $reviewDir 'P1_REVIEW_A_TEMPLATE.json'
$tplB = Join-Path $reviewDir 'P1_REVIEW_B_TEMPLATE.json'
if (-not (Test-Path -LiteralPath $tplA) -and -not (Test-Path -LiteralPath $tplB)) {
    & $py -B (Join-Path $source 'v3_p1_reviewer_custody.py') --project-root $root --fixture $fixture --packet-dir $reviewDir --generate-once
    if ($LASTEXITCODE -ne 0) { throw 'V3_BLIND_REVIEW_TEMPLATE_CREATE_FAILED' }
}
if (-not (Test-Path -LiteralPath $tplA -PathType Leaf) -or
    -not (Test-Path -LiteralPath $tplB -PathType Leaf)) {
    throw 'V3_REVIEW_TEMPLATE_PARTIAL_OR_MISSING'
}
$items = @([pscustomobject]@{Path=$tplA; Slot='A'},[pscustomobject]@{Path=$tplB; Slot='B'})
foreach ($item in $items) {
    $template = Get-Content -LiteralPath $item.Path -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($template.slot -ne $item.Slot -or $template.fixture_sha256 -ne $fixtureSHA -or
        @($template.cases).Count -ne 32 -or
        $template.attest_independent_semantic_mapping -ne $false) {
        throw 'V3_REVIEW_TEMPLATE_SCHEMA_INVALID'
    }
}
$human = 'HOLD_PENDING_TWO_INDEPENDENT_P1_HUMAN_REVIEWS'
if ((Test-Path -LiteralPath $reviewA -PathType Leaf) -and
    (Test-Path -LiteralPath $reviewB -PathType Leaf)) {
    if (Test-Path -LiteralPath $receipt) { throw 'REVIEW_RECEIPT_ALREADY_EXISTS_REFUSE_OVERWRITE' }
    & $py -B (Join-Path $source 'v3_p1_reviewer_custody.py') --project-root $root --fixture $fixture --packet-dir $reviewDir --review-a $reviewA --review-b $reviewB --receipt-out $receipt
    if ($LASTEXITCODE -ne 0) { throw 'P1_HUMAN_REVIEW_ADJUDICATION_FAILED_HOLD' }
    $human = 'PASS_TWO_DISTINCT_P1_REVIEW_ATTESTATIONS'
}
if ((GitExact -Arguments @('-C',$root,'rev-parse','refs/heads/main')).Trim() -ne $mainBefore) {
    throw 'MAIN_REF_CHANGED'
}
Write-Output 'V3_OWNER_SOURCE_QA=PASS_99_99'
Write-Output ('V3_SOURCE_COMMIT=' + $sourcePin)
Write-Output 'V3_FIXTURE_256_SHA256=PASS'
Write-Output ('V3_FIXTURE_SHA256=' + $fixtureSHA)
Write-Output ('V3_SOURCE_QA_RECEIPT_SHA256=' + (Get-FileHash -LiteralPath $qaFile -Algorithm SHA256).Hash)
Write-Output ('V3_P1_HUMAN_REVIEW=' + $human)
Write-Output 'V3_RETRIEVER_ON_REAL_256=NOT_EXECUTED'
Write-Output 'V3_READER_INFERENCE=NOT_EXECUTED'
Write-Output 'OLD_PROBE_DEV_TEST=UNCHANGED_SEALED'
Write-Output 'MAIN_AND_LINEAGE=UNCHANGED'
if ($human -ne 'PASS_TWO_DISTINCT_P1_REVIEW_ATTESTATIONS') {
    Write-Output 'V3_OWNER_SOURCE_GO_HOLD=HOLD_P1_REVIEW'
} else {
    Write-Output 'V3_OWNER_SOURCE_GO_HOLD=PASS_SOURCE_ONLY_NO_SCIENCE_RELEASE'
}
Write-Output 'V3_CPU_SCIENCE_RELEASE=HOLD_NO_PINNED_V3_SCIENCE_SCORER'
