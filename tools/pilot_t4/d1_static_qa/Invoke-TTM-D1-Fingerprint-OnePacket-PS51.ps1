#requires -Version 5.1
$ErrorActionPreference = 'Stop'
$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$Script = Join-Path $Root '_tmp\TTM_D1_FINGERPRINT_ONEPACKET_20261112.py'
$ExpectedGitBlob = 'ec4a45e3bed4863475caf1d0d0915dcefe8e12d6'
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
# Git blob SHA-1 in .NET: UTF-8 bytes, normalized CRLF, terminal LF if transport removed it.
# No embedded Python -c string (PowerShell 5.1 strips its quotes).
$sourceText = [System.IO.File]::ReadAllText($Script, [System.Text.Encoding]::UTF8)
$newline = [string][char]10
$windowsNewline = ([string][char]13) + $newline
$canonicalText = $sourceText.Replace($windowsNewline, $newline)
if (-not $canonicalText.EndsWith($newline)) {
    $canonicalText += $newline
}
[byte[]]$sourceBytes = [System.Text.Encoding]::UTF8.GetBytes($canonicalText)
[byte[]]$headerBytes = [System.Text.Encoding]::ASCII.GetBytes("blob $($sourceBytes.Length)")
[byte[]]$blobBytes = [byte[]]::new($headerBytes.Length + 1 + $sourceBytes.Length)
[System.Array]::Copy($headerBytes, 0, $blobBytes, 0, $headerBytes.Length)
$blobBytes[$headerBytes.Length] = [byte]0
[System.Array]::Copy($sourceBytes, 0, $blobBytes, $headerBytes.Length + 1, $sourceBytes.Length)
$sha1 = [System.Security.Cryptography.SHA1]::Create()
try {
    $actualBlob = ([System.BitConverter]::ToString($sha1.ComputeHash($blobBytes))).Replace('-', '').ToLowerInvariant()
}
finally {
    $sha1.Dispose()
}
if ($actualBlob -cne $ExpectedGitBlob) {
    throw 'FINGERPRINT_SOURCE_GIT_BLOB_MISMATCH'
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
