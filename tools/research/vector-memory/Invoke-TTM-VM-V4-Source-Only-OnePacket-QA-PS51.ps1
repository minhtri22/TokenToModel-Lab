#requires -Version 5.1
<# V4 SOURCE-ONLY PINNED QA. NO CAL64/PROBE256, no Reader, no GPU or TEST.
Single source/mock QA invocation. Leaves historical science untouched.
#>
param()
$ErrorActionPreference = 'Stop'

$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Branch = 'research/ttm-vector-memory-architecture-20261111'
$SourceCommit = 'd8d348c44605918f64e57e10f34225162d7349f7'
$Python312 = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$Stage = Join-Path $Root '_tmp\TTM_VM_V4_SOURCE_QA_PINNED_20261113'
$Receipt = Join-Path $Root '_evidence\vector-memory\TTM_VM_V4_SOURCE_MOCK_QA_20261113.json'
$Files = [ordered]@{
  'v4_fixed_retrieval_calibration.py' = 'e3d2fa5c0a95d1f1d32b6dda38bf82518dfa5327'
  'v4_source_rights_annotation_custody.py' = '63feab1c9a9e3c5feeffb9f438f8d4b1d6c50f06'
  'v4_independent_source_mock_qa.py' = 'd576cbe0586af14d747085c1589b1a30b6bc0d12'
}

if (-not (Test-Path -LiteralPath $Python312 -PathType Leaf)) {
    throw 'HOLD_PYTHON312_NOT_FOUND'
}
if ((& $Python312 -c "import sys; print('.'.join(map(str,sys.version_info[:2])))").Trim() -ne '3.12') {
    throw 'HOLD_NOT_PYTHON312'
}
$Origin = (& git.exe -C $Root remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0 -or $Origin -notin @(
    'https://github.com/minhtri22/TokenToModel-Lab',
    'https://github.com/minhtri22/TokenToModel-Lab.git')) {
    throw 'HOLD_WRONG_GITHUB_ORIGIN'
}
if ((Test-Path -LiteralPath $Stage) -or (Test-Path -LiteralPath $Receipt)) {
    throw 'HOLD_SOURCE_QA_ALREADY_STAGED_OR_RECEIPT_EXISTS_NO_OVERWRITE'
}
& git.exe -C $Root fetch origin $Branch
if ($LASTEXITCODE -ne 0) { throw 'HOLD_FETCH_FAILED' }

New-Item -ItemType Directory -Path $Stage -Force | Out-Null
$UTF8 = New-Object System.Text.UTF8Encoding($false)
foreach ($Name in $Files.Keys) {
    $RelPath = 'tools/research/vector-memory/' + $Name
    $Spec = '{0}:{1}' -f $SourceCommit,$RelPath
    $Lines = @(& git.exe -C $Root show $Spec)
    if ($LASTEXITCODE -ne 0 -or $Lines.Count -eq 0) {
        throw ('HOLD_PINNED_SOURCE_MISSING_' + $Name)
    }
    $Target = Join-Path $Stage $Name
    # Git source is UTF-8 LF with a single terminal LF.
    [IO.File]::WriteAllText($Target, ([string]::Join("`n",[string[]]$Lines) + "`n"), $UTF8)
    $Blob = (& git.exe -C $Root hash-object --no-filters -- $Target).Trim()
    if ($LASTEXITCODE -ne 0 -or $Blob -ne $Files[$Name]) {
        throw ('HOLD_GIT_BLOB_MISMATCH_' + $Name + '_' + $Blob)
    }
}

$env:PYTHONDONTWRITEBYTECODE = '1'
& $Python312 -B (Join-Path $Stage 'v4_independent_source_mock_qa.py') --out $Receipt
if ($LASTEXITCODE -ne 0) {
    throw 'HOLD_V4_SOURCE_ONLY_NATIVE_MOCK_QA_FAILED'
}
$QA = Get-Content -LiteralPath $Receipt -Raw -Encoding UTF8 | ConvertFrom-Json
if ($QA.status -ne 'PASS_V4_SOURCE_MOCK_QA' -or
    $QA.qa_total -ne 60 -or $QA.qa_passed -ne 60 -or
    $QA.CAL64_actual_scored -ne $false -or
    $QA.PROBE256_actual_scored -ne $false -or
    $QA.reader_forward_calls -ne 0 -or
    $QA.test_opened -ne $false -or $QA.gpu_used -ne $false) {
    throw 'HOLD_NATIVE_MOCK_QA_RECEIPT_INVALID'
}
$Failures = @($QA.checks.PSObject.Properties | Where-Object { $_.Value -ne $true })
if ($Failures.Count -ne 0 -or @($QA.checks.PSObject.Properties).Count -ne 60) {
    throw 'HOLD_NATIVE_MOCK_QA_BOOLEAN_CHECKS'
}
$Hash = (Get-FileHash -LiteralPath $Receipt -Algorithm SHA256).Hash
Write-Host 'V4_SOURCE_ONLY_QA=PASS_60_60'
Write-Host "V4_SOURCE_COMMIT=$SourceCommit"
Write-Host "V4_SOURCE_QA_RECEIPT_SHA256=$Hash"
Write-Host 'V4_MODEL_WEIGHT_BYTES_OWNER=NOT_VERIFIED'
Write-Host 'V4_SOURCE_RIGHTS_OWNER=NOT_ATTESTED'
Write-Host 'V4_CAL64=NOT_GENERATED'
Write-Host 'V4_PROBE256=NOT_GENERATED'
Write-Host 'V4_READER_INFERENCE=NOT_EXECUTED'
Write-Host 'V4_TEST=SEALED;GPU=NO;LINEAGE=L0023;MAIN=UNCHANGED'
Write-Host 'V4_SCIENCE_RELEASE=HOLD_OWNER_RIGHTS_MODEL_BYTES_CAL_PROBE_AI_CUSTODY'
