#requires -Version 5.1
# FC01 source-only QA launcher. Zero GPU/training/inference.
# This script ONLY stages the exact SHA-locked ZIP the user explicitly downloaded.
$ErrorActionPreference = 'Stop'
$Repo = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Tmp = Join-Path $Repo '_tmp'
$Folder = Join-Path $Tmp 'fc01_onepacket_20261113'
$InnerPS = Join-Path $Folder 'Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1'
$ZipName = 'TTM_FC01_ONEPACKET_SOURCE_QA_RUNNER_20261113.zip'
$ZipSHA = '601b9ded14c3db013f1c3d237461f4144ea3fbc86deffc2749e825a261043b36'
$Checks = @{
  'fc01_build_private_corpus.py' = '1fc0000bfe507fdceebc0a595fc703b5c66fdb74a70f07dcc4e23a745e6a3b90'
  'fc01_integrated_static_qa.py' = 'd3fec73129766a2ff1f95bc3690de41a85cb6621ff3b0abe0a945e86359284b0'
  'fc01_pinned_bpe.py' = 'd90ddbcdbea8450d7605cf7e65936efd032344b8d7793c2272d4d0870cfbff01'
  'fc01_independent_contract_tests.py' = '419c3beca59193de2b29c8e26a9cfc9ba0583346f4da160c72ee17fc6b291d3f'
  'fc01_train_eval_once.py' = 'b80c7fe84c22f3474520019a1649396f01d4dba9a757c5a9651279797c4434e7'
  'Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1' = '714bbe2490d20eb6faddbfdaf983c352c09b886fd2259e76b23041bb4b7f864f'
  'README_FC01_ONEPACKET_VI.md' = 'f0aa8bf7e31f627802aa8469ad67bd197c208c98991a82c840119f13d90b6231'
}
if (-not (Test-Path -LiteralPath (Join-Path $Repo '.git'))) {
  throw 'FC01_WRONG_PROJECT_ROOT'
}
if (-not (Test-Path -LiteralPath $Tmp -PathType Container)) {
  throw 'FC01_TMP_DIRECTORY_MISSING'
}
if (-not (Test-Path -LiteralPath $InnerPS -PathType Leaf)) {
  if (Test-Path -LiteralPath $Folder) {
    throw 'FC01_PARTIAL_SCRIPT_DIR_EXISTS_NO_OVERWRITE'
  }
  $Zip = $null
  $CandidatePaths = @(
    (Join-Path $env:USERPROFILE ('Downloads\' + $ZipName)),
    (Join-Path $env:USERPROFILE ('Desktop\' + $ZipName)),
    (Join-Path $Tmp $ZipName)
  )
  foreach ($Candidate in $CandidatePaths) {
    if (-not (Test-Path -LiteralPath $Candidate -PathType Leaf)) { continue }
    $Hash = (Get-FileHash -LiteralPath $Candidate -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Hash -ceq $ZipSHA) {
      $Zip = $Candidate
      break
    }
  }
  if ($null -eq $Zip) {
    Write-Host 'FC01_ZIP_NOT_IN_STANDARD_DOWNLOAD_PATHS: SELECT_THE_DOWNLOADED_ZIP_IN_FILE_DIALOG'
    Add-Type -AssemblyName System.Windows.Forms
    $Dialog = New-Object System.Windows.Forms.OpenFileDialog
    $Dialog.Title = 'Select TTM FC01 source ZIP that you downloaded from ChatGPT'
    $Dialog.Filter = 'ZIP archives (*.zip)|*.zip'
    $Dialog.FileName = $ZipName
    $Dialog.CheckFileExists = $true
    $Dialog.Multiselect = $false
    $State = $Dialog.ShowDialog()
    if ($State -ne [System.Windows.Forms.DialogResult]::OK) {
      throw 'FC01_ZIP_NOT_DOWNLOADED_OR_NO_FILE_SELECTED'
    }
    $Zip = $Dialog.FileName
  }
  if (-not (Test-Path -LiteralPath $Zip -PathType Leaf)) {
    throw 'FC01_SELECTED_ZIP_MISSING'
  }
  $RealZipSHA = (Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($RealZipSHA -cne $ZipSHA) {
    throw ('FC01_ZIP_SHA256_MISMATCH:' + $RealZipSHA)
  }
  Write-Host "FC01_SOURCE_ZIP_SHA256=$RealZipSHA"
  Expand-Archive -LiteralPath $Zip -DestinationPath $Tmp -ErrorAction Stop
}
foreach ($Name in $Checks.Keys) {
  $File = Join-Path $Folder $Name
  if (-not (Test-Path -LiteralPath $File -PathType Leaf)) {
    throw ('FC01_UNPACKED_FILE_MISSING:' + $Name)
  }
  $Actual = (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($Actual -cne $Checks[$Name]) {
    throw ('FC01_UNPACKED_FILE_SHA_MISMATCH:' + $Name)
  }
}
Write-Host 'FC01_SOURCE_ARCHIVE_AND_7_FILES_SHA256=PASS'
Write-Host 'FC01_MODE=SOURCE_READINESS_ONLY_NO_GPU'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $InnerPS
if ($LASTEXITCODE -ne 0) {
  throw ('FC01_INNER_READINESS_RETURNED_' + $LASTEXITCODE)
}
