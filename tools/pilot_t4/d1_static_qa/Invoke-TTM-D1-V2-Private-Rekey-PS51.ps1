# TTM D1 V2 static private seed rekey + QA, one shot. PowerShell 5.1.
# No TTM inference, training, TEST, Q1Q2, FRESH16 rerun, or lineage mutation.
$ErrorActionPreference = 'Stop'
$Repo = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Tmp = Join-Path $Repo '_tmp'
$Py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$Source = Join-Path $Tmp 'TTM_D1_V2_PRIVATE_REKEY_STATIC_ONCE_20261111.py'
$V1 = Join-Path $Tmp 'TTM_SMALL4M_D1_NEW_DEV_PRIVATE_20261111.json'
$V2 = Join-Path $Tmp 'TTM_SMALL4M_D1_NEW_DEV_PRIVATE_V2_20261111.json'
$Rater = Join-Path $Tmp 'TTM_SMALL4M_D1_BLIND_RATER_TEMPLATE_V2_20261111.json'
$Receipt = Join-Path $Tmp 'TTM_SMALL4M_D1_V2_VERSIONED_PRIVATE_REKEY_STATIC_RECEIPT_20261111.json'
$ExpectedGitBlob = '8b6a26693610eb4b1e7984dff937eadf1114be44'
$ExpectedV1Raw = 'c43dde98c4fd2328ece9baba549c8bbc369964f0d19d4ecd9f8bb081d3256957'
$ExpectedV1Bytes = 266415

if (-not (Test-Path -LiteralPath $Repo -PathType Container)) { throw 'D1_WRONG_PROJECT_ROOT' }
foreach ($path in @($Py,$Source,$V1)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "D1_MISSING_SOURCE:$path" }
}
foreach ($path in @($V2,$Rater,$Receipt)) {
    if (Test-Path -LiteralPath $path) { throw "D1_V2_ALREADY_EXISTS_NO_RERUN_OR_OVERWRITE:$path" }
}

# Verify Git blob SHA-1 of normalized UTF-8 source.
$Text = [System.IO.File]::ReadAllText($Source, [System.Text.Encoding]::UTF8)
$Text = $Text.Replace("`r`n","`n")
$SourceBytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
$Header = [System.Text.Encoding]::ASCII.GetBytes("blob $($SourceBytes.Length)`0")
$Payload = New-Object byte[] ($Header.Length + $SourceBytes.Length)
[System.Array]::Copy($Header,0,$Payload,0,$Header.Length)
[System.Array]::Copy($SourceBytes,0,$Payload,$Header.Length,$SourceBytes.Length)
$HashObject = [System.Security.Cryptography.SHA1]::Create()
try {
    $ActualGitBlob = [System.BitConverter]::ToString($HashObject.ComputeHash($Payload)).Replace('-','').ToLowerInvariant()
} finally {
    $HashObject.Dispose()
}
if ($ActualGitBlob -ne $ExpectedGitBlob) {
    throw "D1_V2_PYTHON_SOURCE_GIT_BLOB_MISMATCH:$ActualGitBlob"
}
$V1Hash = (Get-FileHash -LiteralPath $V1 -Algorithm SHA256).Hash.ToLowerInvariant()
$V1Size = (Get-Item -LiteralPath $V1).Length
if ($V1Hash -ne $ExpectedV1Raw -or $V1Size -ne $ExpectedV1Bytes) {
    throw "D1_V1_PRIVATE_RAW_SHA_OR_BYTES_MISMATCH:$V1Hash/$V1Size"
}
& $Py -c "import sys; assert sys.version_info[:2] == (3, 12)"
if ($LASTEXITCODE -ne 0) { throw 'D1_PY312_MISMATCH' }

# Exactly one static private-data execution. Python exclusively creates outputs.
& $Py $Source
if ($LASTEXITCODE -ne 0) { throw "D1_V2_STATIC_QA_FAILURE_EXIT_$LASTEXITCODE" }

foreach ($path in @($V2,$Rater,$Receipt)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "D1_V2_EVIDENCE_MISSING:$path" }
}
$Meta = Get-Content -LiteralPath $Receipt -Encoding UTF8 -Raw | ConvertFrom-Json
$V2Raw = (Get-FileHash -LiteralPath $V2 -Algorithm SHA256).Hash.ToLowerInvariant()
$RaterRaw = (Get-FileHash -LiteralPath $Rater -Algorithm SHA256).Hash.ToLowerInvariant()
if ($V2Raw -ne $Meta.new_private_v2_raw_sha256 -or $RaterRaw -ne $Meta.scorer_template_raw_sha256) {
    throw 'D1_V2_POSTWRITE_SHA_READBACK_MISMATCH'
}
if ($Meta.decision -ne 'HOLD_SINGLE_FULL_BATCH_NO_SCIENCE' -or $Meta.scientific_execution -ne 'NO') {
    throw 'D1_V2_SCIENCE_RELEASE_UNEXPECTED'
}
Write-Host 'TTM_D1_V2_INDEPENDENT_POSTWRITE_SHA=PASS'
Write-Host "D1_V2_RAW_SHA256=$V2Raw"
Write-Host "D1_V2_RAW_BYTES=$($Meta.new_private_v2_raw_bytes)"
Write-Host "D1_V2_LF_SHA256=$($Meta.new_private_v2_lf_sha256)"
Write-Host "D1_V2_SCORER_SHA256=$RaterRaw"
Write-Host 'D1_V2_PRIVATE_OVERLAP=NOT_VERIFIED'
Write-Host 'D1_V2_RATER=UNASSIGNED'
Write-Host 'D1_V2_SCIENCE_EXECUTED=NO'
Write-Host 'D1_V2_SINGLE_OWNER_SCIENCE_RELEASE=HOLD'
