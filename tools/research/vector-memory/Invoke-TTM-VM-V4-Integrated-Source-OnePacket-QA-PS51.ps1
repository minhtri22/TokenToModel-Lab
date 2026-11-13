#requires -Version 5.1
<# V4 INTEGRATED SOURCE-ONLY QA. Runs 60+20 mock checks, no Reader/PROBE/TEST/GPU.
A single owner Windows action; code obtained from exact Git commit and blob pins.
#>
param()
$ErrorActionPreference = 'Stop'
$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Branch = 'research/ttm-vector-memory-architecture-20261111'
$CodeCommit = 'f1b30e4e19192be51e707f110af688cb21113edb'
$Py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$Stage = Join-Path $Root '_tmp\TTM_VM_V4_INTEGRATED_SOURCE_QA_20261113'
$Evidence = Join-Path $Root '_evidence\vector-memory'
$QA60 = Join-Path $Evidence 'TTM_VM_V4_NATIVE_SOURCE_MOCK_QA60_20261113.json'
$QA20 = Join-Path $Evidence 'TTM_VM_V4_NATIVE_ASSEMBLER_MOCK_QA20_20261113.json'
$Summary = Join-Path $Evidence 'TTM_VM_V4_NATIVE_SOURCE_QA80_HOLD_RECEIPT_20261113.json'
$Pin = [ordered]@{
 'v4_fixed_retrieval_calibration.py' = 'e3d2fa5c0a95d1f1d32b6dda38bf82518dfa5327'
 'v4_source_rights_annotation_custody.py' = '63feab1c9a9e3c5feeffb9f438f8d4b1d6c50f06'
 'v4_independent_source_mock_qa.py' = 'd576cbe0586af14d747085c1589b1a30b6bc0d12'
 'v4_cal_probe_private_packet_assembler.py' = '70875eb9aacab21eb8c7b9d14cc2835b5b9b5c2f'
 'v4_assembler_source_mock_qa.py' = '37761198db30ffdf682de83d51420fd215c29fa1'
}

if (-not (Test-Path -LiteralPath $Py -PathType Leaf)) { throw 'HOLD_PYTHON312_MISSING' }
$V = (& $Py -c "import sys; print('.'.join(map(str,sys.version_info[:2])))").Trim()
if ($LASTEXITCODE -ne 0 -or $V -ne '3.12') { throw 'HOLD_NOT_PY312' }
$Origin = (& git.exe -C $Root remote get-url origin).Trim()
if ($LASTEXITCODE -ne 0 -or $Origin -notin @(
 'https://github.com/minhtri22/TokenToModel-Lab',
 'https://github.com/minhtri22/TokenToModel-Lab.git')) {
 throw 'HOLD_WRONG_ORIGIN'
}
if ((Test-Path -LiteralPath $Stage) -or (Test-Path -LiteralPath $QA60) -or
    (Test-Path -LiteralPath $QA20) -or (Test-Path -LiteralPath $Summary)) {
 throw 'HOLD_PRIOR_NATIVE_QA_STAGE_OR_RECEIPT_REFUSE_OVERWRITE'
}
& git.exe -C $Root fetch origin $Branch
if ($LASTEXITCODE -ne 0) { throw 'HOLD_GIT_FETCH_FAILED' }
New-Item -ItemType Directory -Path $Stage -Force | Out-Null
$UTF8 = New-Object System.Text.UTF8Encoding($false)
foreach ($Name in $Pin.Keys) {
 $Spec = '{0}:tools/research/vector-memory/{1}' -f $CodeCommit,$Name
 $Lines = @(& git.exe -C $Root show $Spec)
 if ($LASTEXITCODE -ne 0 -or $Lines.Count -eq 0) {
  throw ('HOLD_GIT_SHOW_NOT_FOUND:' + $Name)
 }
 $Target = Join-Path $Stage $Name
 [IO.File]::WriteAllText($Target,([string]::Join("`n",[string[]]$Lines)+"`n"),$UTF8)
 $Hash = (& git.exe -C $Root hash-object --no-filters -- $Target).Trim()
 if ($LASTEXITCODE -ne 0 -or $Hash -ne $Pin[$Name]) {
  throw ('HOLD_SOURCE_BLOB_MISMATCH:'+$Name+':'+$Hash)
 }
}
$env:PYTHONDONTWRITEBYTECODE = '1'
& $Py -B (Join-Path $Stage 'v4_independent_source_mock_qa.py') --out $QA60
if ($LASTEXITCODE -ne 0) { throw 'HOLD_NATIVE_QA60_FAILED' }
& $Py -B (Join-Path $Stage 'v4_assembler_source_mock_qa.py') --out $QA20
if ($LASTEXITCODE -ne 0) { throw 'HOLD_NATIVE_QA20_FAILED' }

$A = Get-Content -Raw -Encoding UTF8 -LiteralPath $QA60 | ConvertFrom-Json
$B = Get-Content -Raw -Encoding UTF8 -LiteralPath $QA20 | ConvertFrom-Json
if ($A.status -ne 'PASS_V4_SOURCE_MOCK_QA' -or $A.qa_passed -ne 60 -or $A.qa_total -ne 60 -or
    $B.status -ne 'PASS_ASSEMBLER_SOURCE_MOCK_QA' -or $B.qa_passed -ne 20 -or $B.qa_total -ne 20) {
 throw 'HOLD_NATIVE_QA80_MISMATCH'
}
if (@($A.checks.PSObject.Properties).Count -ne 60 -or
    @($B.checks.PSObject.Properties).Count -ne 20 -or
    @($A.checks.PSObject.Properties | Where-Object {$_.Value -ne $true}).Count -ne 0 -or
    @($B.checks.PSObject.Properties | Where-Object {$_.Value -ne $true}).Count -ne 0 -or
    $A.CAL64_actual_scored -ne $false -or $A.PROBE256_actual_scored -ne $false -or
    $B.cal_generated -ne $false -or $B.probe_generated -ne $false -or
    $A.reader_forward_calls -ne 0 -or $B.Reader_forward_calls -ne 0 -or
    $A.test_opened -ne $false -or $B.test_opened -ne $false -or
    $A.gpu_used -ne $false -or $B.gpu_used -ne $false) {
 throw 'HOLD_NATIVE_QA80_FLAGS_INCONSISTENT'
}
$SHA60 = (Get-FileHash -Algorithm SHA256 -LiteralPath $QA60).Hash
$SHA20 = (Get-FileHash -Algorithm SHA256 -LiteralPath $QA20).Hash
$Out = [ordered]@{
 schema = 'ttm.vm.v4.owner.native_source_onepacket.qa80_hold.v1'
 status = 'PASS_NATIVE_SOURCE_MOCK_QA_80_80'
 code_commit = $CodeCommit
 source_QA60_sha256 = $SHA60
 assembler_QA20_sha256 = $SHA20
 mock_only = $true
 CAL64_actual_scored = $false
 PROBE256_actual_scored = $false
 reader_forward_calls = 0
 test_opened = $false
 gpu_used = $false
 owner_BGE_local_weight_SHA = 'NOT_VERIFIED'
 rights_attestation = 'NOT_EXECUTED'
 science_release = 'HOLD_OWNER_RIGHTS_MODEL_BYTES_CAL_THRESHOLD_AND_PROBE_CUSTODY'
}
[IO.File]::WriteAllText($Summary,(($Out|ConvertTo-Json -Depth 5)+"`n"),$UTF8)
$SummarySHA = (Get-FileHash -Algorithm SHA256 -LiteralPath $Summary).Hash
Write-Host 'V4_NATIVE_SOURCE_QA=PASS_80_80'
Write-Host "V4_SOURCE_PIN=$CodeCommit"
Write-Host "V4_OWNER_QA80_RECEIPT_SHA256=$SummarySHA"
Write-Host 'V4_CAL64=NOT_GENERATED'
Write-Host 'V4_PROBE256=NOT_GENERATED'
Write-Host 'V4_READER_INFERENCE=NOT_EXECUTED'
Write-Host 'V4_TEST=SEALED;GPU=NO;LINEAGE=L0023;MAIN=UNCHANGED'
Write-Host 'V4_SCIENCE_RELEASE=HOLD_OWNER_RIGHTS_MODEL_BYTES_CAL_THRESHOLD_AND_PROBE_CUSTODY'
