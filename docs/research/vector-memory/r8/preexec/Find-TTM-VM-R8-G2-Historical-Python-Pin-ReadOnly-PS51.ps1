#requires -Version 5.1
<#
TTM VM V4 R8 G2 — bounded historical executable recovery diagnostic.
READ ONLY: no file creation/overwrite, no receipt modification, no secret reads,
no G_pre/key access, no GitHub mutations, no G3. Historical PASS is inherited,
not automatically reapplied to a newly found binary.
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab'
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
$expectedExe = '0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14'
$receipt = Join-Path $root '_private\r8_custody\receipts\g2-owner-windows-protected-trust-boundary-preexec-20261115.json'
$receiptSha = 'c0bf90955d09501b5dcdb7ab912635a666895b23c5c855494ddfb7381ce37795'
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'PROJECT_ROOT_MISSING' }
if (-not (Test-Path -LiteralPath $receipt -PathType Leaf)) { throw 'HISTORICAL_RECEIPT_MISSING' }
$gotReceiptSha = (Get-FileHash -LiteralPath $receipt -Algorithm SHA256).Hash.ToLowerInvariant()
if ($gotReceiptSha -cne $receiptSha) { throw 'HISTORICAL_RECEIPT_HASH_MISMATCH' }
Write-Host 'EXISTING_G2_RECEIPT_SHA256=PASS_NO_MUTATION'
Write-Host 'HISTORICAL_RUNTIME_EXECUTABLE_SHA256_PIN=0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14'
Write-Host 'HISTORICAL_RUNTIME_SOURCE=G2_CLOSEOUT_COMMIT_3ca8d799'
$match = New-Object 'System.Collections.Generic.List[string]'
$seen = New-Object 'System.Collections.Generic.HashSet[string]'
$searched = 0
$errors = 0
# Scope strictly to the existing project. This finds venv executables omitted
# by Get-Command/PATH; no installation, cleanup, or Windows-wide traversal.
foreach ($item in @(Get-ChildItem -LiteralPath $root -Recurse -Force -File -Filter 'python.exe' -ErrorAction SilentlyContinue)) {
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { continue }
    if (-not $seen.Add($item.FullName)) { continue }
    $searched += 1
    try {
        $candidateHash = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
        if ($candidateHash -ceq $expectedExe) { $match.Add($item.FullName) }
    } catch { $errors += 1 }
}
Write-Host ('PYTHON_EXE_CANDIDATE_FILES_CHECKED=' + $searched)
Write-Host ('PYTHON_EXE_HASH_ERRORS=' + $errors)
if ($match.Count -eq 0) {
    Write-Host 'HISTORICAL_PYTHON_EXE=NOT_FOUND_IN_EXISTING_PROJECT'
} elseif ($match.Count -gt 1) {
    Write-Host ('HISTORICAL_PYTHON_EXE=MULTIPLE_SAME_HASH_CANDIDATES_' + $match.Count)
    foreach ($f in $match) { Write-Host ('EXACT_SHA_MATCH_CANDIDATE=' + $f) }
} else {
    Write-Host 'HISTORICAL_PYTHON_EXE=EXACT_SHA_MATCH_CANDIDATE'
    Write-Host ('EXACT_SHA_MATCH_CANDIDATE=' + $match[0])
}
# Inspect versions only for exact-SHA matches; never execute unknown binaries.
foreach ($file in $match) {
    try {
        $code = 'import sys,json,importlib.metadata as m;print(json.dumps({"py":".".join(map(str,sys.version_info[:3])),"prefix":sys.prefix,"packages":{k:m.version(k) for k in ("numpy","scipy","scikit-learn","joblib","threadpoolctl")}}))'
        $output = (& $file -I -B -c $code 2>$null | Out-String).Trim()
        if ($LASTEXITCODE -ne 0) {
            Write-Host ('PINNED_EXE_PACKAGE_PROBE=HOLD_IMPORT_FAILED;PATH=' + $file)
            continue
        }
        $data = $output | ConvertFrom-Json
        if ($data.py -ceq '3.12.10' -and $data.packages.numpy -ceq '2.3.5' -and
            $data.packages.scipy -ceq '1.17.0' -and $data.packages.'scikit-learn' -ceq '1.8.0' -and
            $data.packages.joblib -ceq '1.5.3' -and $data.packages.threadpoolctl -ceq '3.6.0') {
            Write-Host 'PINNED_EXE_PACKAGE_PROBE=PASS_SCOPED_VERSION_MATCH_ONLY'
        } else { Write-Host 'PINNED_EXE_PACKAGE_PROBE=HOLD_PACKAGE_OR_PYTHON_MISMATCH' }
    } catch { Write-Host 'PINNED_EXE_PACKAGE_PROBE=HOLD_IMPORT_OR_METADATA_EXCEPTION' }
}
Write-Host 'RUNTIME_ORIGINAL_MANIFEST_AND_MODULE_BYTE_READBACK=NOT_ATTESTED'
Write-Host 'REAL_HMAC_V2=NOT_EXECUTED'
Write-Host 'R8=NOT_GENERATED'
Write-Host 'G3=NOT_EXECUTED'
Write-Host 'G2=HOLD_INTEGRATED'
