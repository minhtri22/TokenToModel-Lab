#requires -Version 5.1
# Directly staged FC01 one-packet source QA. NO ZIP, NO GPU, NO TRAINING.
$ErrorActionPreference='Stop'
$Root='D:\WORK\RESEARCH\TokenToModel-Lab'
$Dir=Join-Path $Root '_tmp\fc01_onepacket_20261113'
$Python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$Inner=Join-Path $Dir 'Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1'
$Expected=@{
 'fc01_build_private_corpus.py'='1fc0000bfe507fdceebc0a595fc703b5c66fdb74a70f07dcc4e23a745e6a3b90'
 'fc01_integrated_static_qa.py'='d3fec73129766a2ff1f95bc3690de41a85cb6621ff3b0abe0a945e86359284b0'
 'fc01_pinned_bpe.py'='d90ddbcdbea8450d7605cf7e65936efd032344b8d7793c2272d4d0870cfbff01'
 'fc01_independent_contract_tests.py'='419c3beca59193de2b29c8e26a9cfc9ba0583346f4da160c72ee17fc6b291d3f'
 'fc01_train_eval_once.py'='b80c7fe84c22f3474520019a1649396f01d4dba9a757c5a9651279797c4434e7'
 'Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1'='714bbe2490d20eb6faddbfdaf983c352c09b886fd2259e76b23041bb4b7f864f'
 'README_FC01_ONEPACKET_VI.md'='f0aa8bf7e31f627802aa8469ad67bd197c208c98991a82c840119f13d90b6231'
}
if (-not (Test-Path -LiteralPath (Join-Path $Root '.git'))) {throw 'FC01_WRONG_PROJECT_ROOT'}
if (-not (Test-Path -LiteralPath $Dir -PathType Container)) {throw 'FC01_STAGED_DIRECTORY_MISSING'}
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {throw 'FC01_PYTHON312_MISSING'}
foreach($Name in @($Expected.Keys | Sort-Object)){
 $File=Join-Path $Dir $Name
 if(-not (Test-Path -LiteralPath $File -PathType Leaf)){throw ('FC01_STAGED_FILE_MISSING:'+$Name)}
 $Hash=(Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
 if($Hash -cne $Expected[$Name]){throw ('FC01_STAGED_SOURCE_SHA256_MISMATCH:'+$Name+':'+$Hash)}
 Write-Host ('FC01_SOURCE_SHA256_PASS:'+$Name)
}
Write-Host 'FC01_SEVEN_STAGED_SOURCES=PASS_EXACT_SHA256'
Write-Host 'FC01_MODE=SOURCE_ONLY_NO_GPU_NO_TRAINING_NO_TEST'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Inner
if($LASTEXITCODE -ne 0){throw ('FC01_OWNER_SOURCE_QA_HOLD_EXIT_'+$LASTEXITCODE)}
Write-Host 'FC01_OWNER_SOURCE_QA_INTEGRATED=PASS_SCOPED'
Write-Host 'FC01_SCIENCE_GO=NOT_GRANTED_BY_THIS_SCRIPT'
