# Pack ONLY the already-frozen H768 private source into a new ZIP inside the TTM project.
# PowerShell 5.1; no H768 selection, no science, no writes outside project root.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$old = Join-Path $root '_tmp\ttm_semantic4x3_h768_seal_v1_20261110'
$stage = Join-Path $root '_tmp\ttm_semantic4x3_h768_private_bundle_stage_v1'
$zip = Join-Path $root '_tmp\TTM_SEMANTIC4X3_H768_PRIVATE_V1_20261110.zip'
$files = [ordered]@{
  'H768_PUBLIC_SEAL.json'='9725B1254CDE81B77E23B85AB479A08CAFC14AF0A7A536C7722CA87C7F2A5AA0'
  'H768_MEMBERSHIP_PRIVATE.json'='0AB671AE59FF4300D8257F2689261D6328AFD7563C0AA66B363BC22348C1628F'
  'H768_WINDOWS_PRIVATE.npz'='1EB5B54B4BB7744E23FFFD0FD755D5C91853A773DCC0D2219F777B47BA6A53DF'
}
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'TTM_ROOT_MISSING' }
if (-not (Test-Path -LiteralPath $old -PathType Container)) { throw 'H768_FROZEN_SOURCE_MISSING' }
if ((Test-Path -LiteralPath $stage) -or (Test-Path -LiteralPath $zip)) {
    throw 'H768_PRIVATE_BUNDLE_ALREADY_EXISTS_NO_OVERWRITE'
}
foreach ($name in $files.Keys) {
  $path = Join-Path $old $name
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "MISSING_H768_FILE_$name" }
  $digest = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
  if ($digest -ine $files[$name]) { throw "SOURCE_SHA256_MISMATCH_$name" }
}
$public = Get-Content -LiteralPath (Join-Path $old 'H768_PUBLIC_SEAL.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($public.status -ne 'H768_SEALED_NOT_SCORED' -or [int]$public.stories -ne 768 -or [int]$public.windows -ne 1000 -or [int]$public.targets -ne 186655 -or [bool]$public.claim_created) {
    throw 'H768_PUBLIC_SEAL_CONTRACT_MISMATCH'
}
New-Item -ItemType Directory -Path (Join-Path $stage 'h768') -Force | Out-Null
foreach ($name in $files.Keys) {
  Copy-Item -LiteralPath (Join-Path $old $name) -Destination (Join-Path (Join-Path $stage 'h768') $name) -ErrorAction Stop
  $digest = (Get-FileHash -LiteralPath (Join-Path (Join-Path $stage 'h768') $name) -Algorithm SHA256).Hash
  if ($digest -ine $files[$name]) { throw "STAGED_SHA256_MISMATCH_$name" }
}
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($stage, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
if (-not (Test-Path -LiteralPath $zip -PathType Leaf)) { throw 'H768_BUNDLE_NOT_CREATED' }
Write-Output 'TTM_SEMANTIC4X3_H768_PRIVATE_BUNDLE=PASS_SOURCE_PINS'
Write-Output ('H768_BUNDLE_PATH=' + $zip)
Write-Output ('H768_BUNDLE_SHA256=' + (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash)
Write-Output 'CLAIM=NOT_CREATED'
Write-Output 'SCIENCE=NOT_EXECUTED'
