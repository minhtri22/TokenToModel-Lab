#requires -Version 5.1
# FC01 scoped byte repair. Source bytes only, no training, GPU or TEST.
$ErrorActionPreference = 'Stop'
$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Dir = Join-Path $Root '_tmp\fc01_onepacket_20261113'
$Launcher = Join-Path $Root '_tmp\Invoke-TTM-FC01-Direct-Staged-Readiness-PS51.ps1'
if (-not (Test-Path -LiteralPath (Join-Path $Root '.git'))) { throw 'FC01_ROOT_IS_NOT_GIT_REPOSITORY' }
if (-not (Test-Path -LiteralPath $Dir -PathType Container)) { throw 'FC01_STAGED_SOURCE_DIRECTORY_MISSING' }
if (-not (Test-Path -LiteralPath $Launcher -PathType Leaf)) { throw 'FC01_EXISTING_QA_LAUNCHER_MISSING' }

# The LF and CRLF byte hashes were independently computed from the archived source ZIP.
$Entries = @(
  @{Name='fc01_build_private_corpus.py'; LF='1fc0000bfe507fdceebc0a595fc703b5c66fdb74a70f07dcc4e23a745e6a3b90'; CRLF='9361a825366c0c201698ba19e4c2469d766e191781f8bc60ed7f4d5d1cee1767'}
  @{Name='fc01_integrated_static_qa.py'; LF='d3fec73129766a2ff1f95bc3690de41a85cb6621ff3b0abe0a945e86359284b0'; CRLF='241b6d7fb9b16885d26cc57be8059a9a69fd6a930c205368c687ea73161e1b04'}
  @{Name='fc01_pinned_bpe.py'; LF='d90ddbcdbea8450d7605cf7e65936efd032344b8d7793c2272d4d0870cfbff01'; CRLF='b8c9340b0c02a181446a2e7f1e7a6000cc84d3b9b8d7659ba162d9df02732058'}
  @{Name='fc01_independent_contract_tests.py'; LF='419c3beca59193de2b29c8e26a9cfc9ba0583346f4da160c72ee17fc6b291d3f'; CRLF='bf09861af83e7dec579cac53ba22be78b49269935a3f18090c18116f28f781e7'}
  @{Name='fc01_train_eval_once.py'; LF='b80c7fe84c22f3474520019a1649396f01d4dba9a757c5a9651279797c4434e7'; CRLF='80603bd3fff9c70d30d9e73cd70035d6e3f3db6978e2199dc73a1f52c445b85c'}
  @{Name='Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1'; LF='714bbe2490d20eb6faddbfdaf983c352c09b886fd2259e76b23041bb4b7f864f'; CRLF='011f46df4476f73ca9cd4f3de28456288fa0b450737ee5e63875849bea3934ed'}
  @{Name='README_FC01_ONEPACKET_VI.md'; LF='f0aa8bf7e31f627802aa8469ad67bd197c208c98991a82c840119f13d90b6231'; CRLF='fd68742478c42025dbe45a2fc3d4364b2b479f67b7982edd71fb61ee6bba4b45'}
)
$UTF8 = [System.Text.UTF8Encoding]::new($false, $true)
$Sha = [System.Security.Cryptography.SHA256]::Create()
$Prepared = @()
try {
  # Preflight all seven files before any write. Unknown bytes cause a hard stop.
  foreach ($E in $Entries) {
    $File = Join-Path $Dir $E.Name
    if (-not (Test-Path -LiteralPath $File -PathType Leaf)) { throw ('FC01_MISSING_SOURCE:' + $E.Name) }
    $Bytes = [System.IO.File]::ReadAllBytes($File)
    $Got = ([System.BitConverter]::ToString($Sha.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant()
    if ($Got -ceq $E.LF) {
      $Prepared += @{Name=$E.Name; Path=$File; Action='UNCHANGED'; Expected=$E.LF; Data=$null}
    }
    elseif ($Got -ceq $E.CRLF) {
      $Text = $UTF8.GetString($Bytes)
      $Fixed = $Text.Replace(([string][char]13 + [string][char]10), [string][char]10)
      if ($Fixed.Contains([string][char]13)) { throw ('FC01_UNEXPECTED_CR_BYTE:' + $E.Name) }
      $NewBytes = $UTF8.GetBytes($Fixed)
      $FixedHash = ([System.BitConverter]::ToString($Sha.ComputeHash($NewBytes))).Replace('-','').ToLowerInvariant()
      if ($FixedHash -cne $E.LF) { throw ('FC01_NORMALIZATION_RESULT_MISMATCH:' + $E.Name + ':' + $FixedHash) }
      $Prepared += @{Name=$E.Name; Path=$File; Action='NORMALIZE_CRLF_TO_LF'; Expected=$E.LF; Data=$NewBytes}
    }
    else {
      throw ('FC01_UNRECOGNIZED_SOURCE_SHA256_NO_WRITE:' + $E.Name + ':' + $Got)
    }
  }
  Write-Host 'FC01_SEVEN_FILES_PREFLIGHT=PASS_KNOWN_LF_OR_EXACT_CRLF'
  foreach ($P in $Prepared) {
    if ($P.Action -eq 'NORMALIZE_CRLF_TO_LF') { [System.IO.File]::WriteAllBytes($P.Path, [byte[]]$P.Data) }
    $Verified = (Get-FileHash -LiteralPath $P.Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Verified -cne $P.Expected) { throw ('FC01_POSTWRITE_SHA_MISMATCH:' + $P.Name + ':' + $Verified) }
    Write-Host ('FC01_SOURCE_SHA256_PASS:' + $P.Name + ':' + $P.Action)
  }
  Write-Host 'FC01_SOURCE_BYTES_EXACT_LF_7_OF_7=PASS'
}
finally { $Sha.Dispose() }
Write-Host 'FC01_NOW_INVOKE_EXISTING_SOURCE_QA_NO_GPU'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Launcher
if ($LASTEXITCODE -ne 0) { throw ('FC01_EXISTING_SOURCE_QA_RETURNED_NONZERO:' + $LASTEXITCODE) }
Write-Host 'FC01_OWNER_SOURCE_QA=PASS_SCOPED'
Write-Host 'FC01_SCIENCE_GO=NOT_GRANTED_BY_SOURCE_QA'
