#requires -Version 5.1
$ErrorActionPreference = 'Stop'
$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$Script = Join-Path $Root '_tmp\TTM_D1_FINGERPRINT_ONEPACKET_20261112.py'
$ExpectedGitBlob = '9d6dfd13c2e55cf121097c14f9b6b2b95667ae15'
$Out = Join-Path $Root '_tmp\TTM_D1_ONEPACKET_FINGERPRINT_20261112'
$Private = Join-Path $Out 'D1_PRIVATE_FINGERPRINT_INDEX.json'
$Safe = Join-Path $Out 'D1_PUBLIC_SAFE_SUMMARY.json'

if (-not (Test-Path -LiteralPath $Py -PathType Leaf)) { throw 'PY312_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $Script -PathType Leaf)) { throw 'FINGERPRINT_SCRIPT_NOT_FOUND' }
if (-not (Test-Path -LiteralPath (Join-Path $Root '_tmp\TTM_D1_FINGERPRINT_AC_FINAL24_PUBLIC_PINNED_20261112.json') -PathType Leaf)) {
    throw 'PINNED_AC_PUBLIC_SOURCE_NOT_STAGED'
}
& $Py -c 'import sys; assert sys.version_info[:2] == (3,12)'
if ($LASTEXITCODE -ne 0) { throw 'WRONG_PYTHON_VERSION' }
$actualBlob = (& git hash-object --no-filters -- $Script).Trim().ToLowerInvariant()
if ($LASTEXITCODE -ne 0) { throw 'SOURCE_GIT_HASH_FAILED' }
if ($actualBlob -cne $ExpectedGitBlob) {
    # Transport may change LF to CRLF. The normalized blob must still match Git.
    $normCode = 'import hashlib,pathlib,sys; b=pathlib.Path(sys.argv[1]).read_bytes().replace(b"\r\n",b"\n"); print(hashlib.sha1(b"blob "+str(len(b)).encode()+b"\x00"+b).hexdigest())'
    $actualBlob = (& $Py -c $normCode $Script).Trim().ToLowerInvariant()
    if ($LASTEXITCODE -ne 0 -or $actualBlob -cne $ExpectedGitBlob) {
        throw 'FINGERPRINT_SOURCE_GIT_BLOB_MISMATCH'
    }
}
Write-Host "FINGERPRINT_SOURCE_GIT_BLOB=$actualBlob"
if ((Test-Path -LiteralPath $Private -PathType Leaf) -and (Test-Path -LiteralPath $Safe -PathType Leaf)) {
    Write-Host 'FINGERPRINT_ONE_SHOT=EXISTING_READBACK_ONLY'
} elseif (Test-Path -LiteralPath $Out) {
    throw 'FINGERPRINT_PARTIAL_OUT_EXISTS_NO_RERUN'
} else {
    & $Py $Script
    if ($LASTEXITCODE -ne 0) { throw 'FINGERPRINT_ONE_SHOT_HOLD' }
}
if (-not (Test-Path -LiteralPath $Private -PathType Leaf) -or -not (Test-Path -LiteralPath $Safe -PathType Leaf)) {
    throw 'FINGERPRINT_OUTPUT_MISSING'
}
$report = Get-Content -LiteralPath $Safe -Raw -Encoding UTF8 | ConvertFrom-Json
if ($report.schema -cne 'ttm.d1.fingerprint_static_onepacket_receipt.v1' -or
    $report.private_fingerprint_record_count -ne 344 -or
    $report.source_counts.D1_DEV -ne 128 -or
    $report.source_counts.D1_NEUTRAL_PRIOR -ne 64 -or
    $report.source_counts.FRESH16_USED -ne 16 -or
    $report.source_counts.CF1_DEV36 -ne 72 -or
    $report.source_counts.AC_FINAL24 -ne 24 -or
    $report.source_counts.Q1_FRESH12_PUBLIC -ne 28 -or
    $report.model_training_executed -ne $false -or
    $report.model_inference_executed -ne $false) {
    throw 'FINGERPRINT_REPORT_SCOPE_MISMATCH'
}
$actualPrivateSha = (Get-FileHash -LiteralPath $Private -Algorithm SHA256).Hash.ToLowerInvariant()
if ($report.private_fingerprint_index_sha256 -cne $actualPrivateSha) { throw 'FINGERPRINT_PRIVATE_INDEX_SHA_MISMATCH' }
$safeSha = (Get-FileHash -LiteralPath $Safe -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host 'TTM_D1_FINGERPRINT_READBACK=PASS_SCOPED'
Write-Host "D1_PRIVATE_INDEX_SHA256=$actualPrivateSha"
Write-Host "D1_SAFE_SUMMARY_SHA256=$safeSha"
Write-Host "D1_SOURCE_RECORDS=$($report.private_fingerprint_record_count)"
Write-Host "D1_PRIVATE_FLAGS=$($report.private_flag_count)"
foreach($n in @('FRESH16_USED','CF1_DEV36','Q1_FRESH12_PUBLIC','AC_FINAL24','AC_DEV12')) {
    $m = $report.comparisons.$n
    Write-Host "D1_$($n)_COMPARISONS=$($m.comparisons)"
    Write-Host "D1_$($n)_EXACT_OVERLAPS=$($m.exact_normalized_matches)"
}
Write-Host "D1_PUBLIC_RECEIPT=$Safe"
Write-Host 'D1_SEALED_TEST_Q1Q2=UNTOUCHED'
Write-Host 'D1_TRAINING=NO D1_INFERENCE=NO'
