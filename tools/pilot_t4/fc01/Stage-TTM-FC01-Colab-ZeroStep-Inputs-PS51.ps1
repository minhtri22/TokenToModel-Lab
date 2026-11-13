#requires -Version 5.1
# Zero-step prep only. Copies exactly seven already pinned FC01 V2 inputs.
# No GPU, no training, no TEST, no C: research writes, no overwrite.
$ErrorActionPreference='Stop'
$Root='D:\WORK\RESEARCH\TokenToModel-Lab'
$Temp=Join-Path $Root '_tmp'
$Input=Join-Path $Temp 'TTM_FC01_COLAB_ZERO_STEP_INPUT_STAGE_20261113'
$Bundle=Join-Path $Temp 'TTM_FC01_SOURCE_BUNDLE_20261113_v2'
$Scripts=Join-Path $Temp 'fc01_onepacket_20261113_v2'
if(-not (Test-Path -LiteralPath (Join-Path $Root '.git'))){throw 'FC01_WRONG_GIT_ROOT'}
$Items=@(
 @{Name='FC01_OWNER_PRIVATE_DATA.json';Source=(Join-Path $Bundle 'FC01_OWNER_PRIVATE_DATA.json');Sha='becc0408880aaed8bd5eb6fdf3997e62d5131c187a48331a03ae37d41aaa1aa3';Kind='SHA256'}
 @{Name='T4_PRIVATE_TRAIN_VAL_WINDOWS.npz';Source=(Join-Path $Bundle 'T4_PRIVATE_TRAIN_VAL_WINDOWS.npz');Sha='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913';Kind='SHA256'}
 @{Name='T4_PRIVATE_PACK_MANIFEST.json';Source=(Join-Path $Bundle 'T4_PRIVATE_PACK_MANIFEST.json');Sha='ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650';Kind='SHA256'}
 @{Name='CF1_STEP1024_PINNED.pt';Source=(Join-Path $Bundle 'CF1_STEP1024_PINNED.pt');Sha='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b';Kind='SHA256'}
 @{Name='T1_BPE2048_REAL_TRAIN_MANIFEST.json';Source=(Join-Path $Bundle 'T1_BPE2048_REAL_TRAIN_MANIFEST.json');Sha='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc';Kind='SHA256'}
 @{Name='p02_exact.py';Source=(Join-Path $Bundle 'p02_exact.py');Sha='9762343e06cf800b50574c2871ae1ed58537fb18';Kind='GIT_BLOB_SHA1'}
 @{Name='fc01_train_eval_once.py';Source=(Join-Path $Scripts 'fc01_train_eval_once.py');Sha='b786a4468ba104786df7683da9b1cf19d2334d9cc203dd19c3e7d6f10e2e93be';Kind='SHA256'}
)
function Assert-Pin($Path,$Item){
 if(-not (Test-Path -LiteralPath $Path -PathType Leaf)){throw ('FC01_MISSING_INPUT:'+ $Item.Name)}
 if($Item.Kind -eq 'GIT_BLOB_SHA1'){
   $Got=(& git hash-object --no-filters -- $Path).Trim().ToLowerInvariant()
   if($LASTEXITCODE -ne 0){throw ('FC01_GIT_BLOB_CHECK_FAILED:'+ $Item.Name)}
 } else {
   $Got=(Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
 }
 if($Got -cne $Item.Sha){throw ('FC01_INPUT_PIN_MISMATCH:'+ $Item.Name+':'+$Got)}
}
foreach($Item in $Items){Assert-Pin $Item.Source $Item}
Write-Host 'FC01_COLAB_INPUT_SOURCE_PINS=PASS_7_OF_7'
if(Test-Path -LiteralPath $Input){
 if(-not (Test-Path -LiteralPath $Input -PathType Container)){throw 'FC01_COLAB_STAGE_PATH_NOT_DIR'}
 $Children=@(Get-ChildItem -LiteralPath $Input -Force)
 if($Children.Count -ne $Items.Count){throw 'FC01_COLAB_STAGE_ALREADY_EXISTS_DIFFERENT_CONTENT_NO_OVERWRITE'}
 foreach($Item in $Items){
   Assert-Pin (Join-Path $Input $Item.Name) $Item
 }
 Write-Host 'FC01_COLAB_INPUT_STAGE=EXACT_PREEXISTING_REUSED'
} else {
 New-Item -ItemType Directory -Path $Input -ErrorAction Stop | Out-Null
 foreach($Item in $Items){
   $target=Join-Path $Input $Item.Name
   if(Test-Path -LiteralPath $target){throw ('FC01_COLAB_STAGE_TARGET_ALREADY_EXISTS:'+ $Item.Name)}
   Copy-Item -LiteralPath $Item.Source -Destination $target -ErrorAction Stop
   Assert-Pin $target $Item
 }
 Write-Host 'FC01_COLAB_INPUT_STAGE=CREATED_NEW'
}
Write-Host 'FC01_COLAB_INPUT_SHA_PIN=PASS_7_OF_7'
Write-Host "FC01_UPLOAD_THE_SEVEN_FILES_IN=$Input"
Write-Host 'FC01_TRAINING=NO FC01_GPU=NO FC01_TEST=SEALED FC01_SCIENCE_GO=NOT_GRANTED'
