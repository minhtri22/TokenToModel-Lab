$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$base=Join-Path $root '_tmp\ttm_gemma2_ood_wikitext2_cpu_v1_20261111'
if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) { throw 'HOLD_TTM_ROOT_GIT' }
if (-not (Test-Path -LiteralPath $base)) { throw 'HOLD_OOD256_SEAL_DIR' }
$expected=[ordered]@{
 'OOD256_PUBLIC_SEAL.json'='0091b56b27c68f1bb724b63181097434d6c7c5922e5cc1de929423b5b0c45438'
 'OOD256_PRIVATE_MEMBERSHIP.json'='627c99db8b39b6479fdb074a82b0ab7eea0367dde49bf0072c29ff410ecdcd5f'
 'OOD256_PRIVATE_WINDOWS.npz'='3ec7655c512c5d13d4c0d04d1ddbae80b8ea0106aee82064e8dd806786d8336a'
}
foreach ($entry in $expected.GetEnumerator()) {
  $file=Join-Path $base $entry.Key
  if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw ('HOLD_MISSING_' + $entry.Key) }
  $sha=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($sha -cne $entry.Value) { throw ('HOLD_SHA_' + $entry.Key) }
}
$zip=Join-Path $base 'OOD256_COLAB_PRIVATE_TRANSFER.zip'
if (Test-Path -LiteralPath $zip) { throw 'HOLD_TRANSFER_ALREADY_EXISTS_NO_OVERWRITE' }
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
$partial=$zip+'.partial'
if (Test-Path -LiteralPath $partial) { throw 'HOLD_TRANSFER_PARTIAL_EXISTS' }
$archive=[System.IO.Compression.ZipFile]::Open($partial,[System.IO.Compression.ZipArchiveMode]::Create)
try {
  foreach ($entry in $expected.GetEnumerator()) {
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
      $archive,(Join-Path $base $entry.Key),$entry.Key,
      [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
  }
} finally { $archive.Dispose() }
Move-Item -LiteralPath $partial -Destination $zip
Write-Host ('OOD256_PRIVATE_TRANSFER_READY='+$zip)
Write-Host ('OOD256_PRIVATE_TRANSFER_SHA256='+(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant())
Write-Host 'OOD256_PRIVATE_INPUTS=PASS_SHA_3_OF_3; RAW_TEXT_NOT_PACKAGED; MODEL_FORWARD=0; SCIENCE=NOT_EXECUTED'
