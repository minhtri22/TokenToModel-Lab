#requires -Version 5.1
<#
Read-only reconciliation after an already-written one-shot G2 owner Windows receipt.
No GitHub writes, source import, HMAC key access, G_pre/G3, or new receipt.
Nothing is created, overwritten, moved or deleted.
#>
[CmdletBinding()]
param([string]$ProjectRoot='D:\WORK\RESEARCH\TokenToModel-Lab')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
$private=Join-Path $root '_private\r8_custody'
$receipt=Join-Path $private 'receipts\g2-owner-windows-protected-trust-boundary-preexec-20261115.json'
$expectedReceipt='c0bf90955d09501b5dcdb7ab912635a666895b23c5c855494ddfb7381ce37795'
if(-not (Test-Path -LiteralPath $receipt -PathType Leaf)) {throw 'EXISTING_G2_RECEIPT_NOT_FOUND'}
$sha=(Get-FileHash -LiteralPath $receipt -Algorithm SHA256).Hash.ToLowerInvariant()
if($sha -cne $expectedReceipt) {throw 'G2_EXISTING_RECEIPT_SHA256_MISMATCH'}
Write-Host 'EXISTING_G2_RECEIPT_SHA256=PASS'
Write-Host 'EXISTING_G2_RECEIPT_PRESERVED=TRUE'
$expected=[ordered]@{
'folds_raters.py'='02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae'
'r8_production_caller.py'='3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206'
'test_g0_algorithm_version_binding.py'='2ce86fe549e1625790fcab72c076df2f12d648b048a350570d5c97a026431ae2'
'gold_contract.py'='8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5'
'restricted_oracles.py'='34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1'
}
if(-not (Test-Path -LiteralPath $private -PathType Container)) {throw 'PRIVATE_ROOT_NOT_FOUND'}
$matches=New-Object 'System.Collections.Generic.List[string]'
$candidates=@(Get-ChildItem -LiteralPath $private -Recurse -File -Filter 'folds_raters.py' -ErrorAction Stop)
foreach($item in $candidates) {
  if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {continue}
  $d=$item.Directory.FullName
  $pass=$true
  foreach($kv in $expected.GetEnumerator()) {
    $f=Join-Path $d $kv.Key
    if(-not (Test-Path -LiteralPath $f -PathType Leaf)) {$pass=$false;break}
    $info=Get-Item -LiteralPath $f -Force
    if(($info.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){$pass=$false;break}
    $hash=(Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant()
    if($hash -cne $kv.Value) {$pass=$false;break}
  }
  if($pass -and -not $matches.Contains($d)) {$matches.Add($d)}
}
if($matches.Count -eq 1) {
  Write-Host 'FROZEN_SOURCE_5_OF_5=PASS_READONLY_BYTE_MATCH'
  Write-Host ('PROTECTED_SOURCE_ROOT_CANDIDATE=' + $matches[0])
} elseif($matches.Count -eq 0) {
  Write-Host 'FROZEN_SOURCE_5_OF_5=NOT_FOUND_WITHIN_EXISTING_PRIVATE_ROOT'
} else {
  Write-Host 'FROZEN_SOURCE_5_OF_5=MULTIPLE_MATCHES_REQUIRE_ORIGINAL_CUSTODY_PIN'
  Write-Host ('FROZEN_SOURCE_MATCH_COUNT=' + $matches.Count)
}
# Candidate interpreter discovery: matching version/dependencies alone is NOT custody pin.
$pythonCandidates=New-Object 'System.Collections.Generic.List[string]'
foreach($cmd in @(Get-Command -Name python.exe -All -ErrorAction SilentlyContinue)) {
    if($cmd -and $cmd.Source -and (Test-Path -LiteralPath $cmd.Source -PathType Leaf) -and
       -not $pythonCandidates.Contains($cmd.Source)) {$pythonCandidates.Add($cmd.Source)}
}
$knownPython312=Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
if((Test-Path -LiteralPath $knownPython312 -PathType Leaf) -and
   -not $pythonCandidates.Contains($knownPython312)) {$pythonCandidates.Add($knownPython312)}
$code='import sys,importlib.metadata as m;v=".".join(map(str,sys.version_info[:3]));p=[m.version(x) for x in ("numpy","scipy","scikit-learn")];print(v+" "+",".join(p))'
$found=0
foreach($python in $pythonCandidates) {
  try {
    $output=(& $python -I -B -c $code 2>$null | Out-String).Trim()
    if($LASTEXITCODE -eq 0 -and $output -ceq '3.12.10 2.3.5,1.17.0,1.8.0') {
      $found++
      Write-Host ('RUNTIME_MATCHING_VERSION_CANDIDATE=' + $python)
      Write-Host ('RUNTIME_CANDIDATE_EXE_SHA256=' + (Get-FileHash -LiteralPath $python -Algorithm SHA256).Hash.ToLowerInvariant())
    }
  } catch {continue}
}
if($found -eq 0) {Write-Host 'RUNTIME_MATCHING_VERSION_CANDIDATE=NONE_IN_BOUNDED_DISCOVERY'}
Write-Host 'RUNTIME_EXACT_PIN=NOT_ATTESTED_WITHOUT_ORIGINAL_MANIFEST'
Write-Host 'REAL_HMAC_V2=NOT_EXECUTED'
Write-Host 'G3=NOT_EXECUTED'
Write-Host 'G2=HOLD_INTEGRATED'
