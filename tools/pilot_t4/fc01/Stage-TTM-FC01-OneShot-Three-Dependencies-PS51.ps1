#requires -Version 5.1
# Copy three source-only dependencies from already QA-pinned FC01 V2 source.
# No source edits, no overwrite, no private corpus regeneration, no GPU, no training.
$ErrorActionPreference='Stop'
$Root='D:\WORK\RESEARCH\TokenToModel-Lab'
$Source=Join-Path $Root '_tmp\fc01_onepacket_20261113_v2'
$Stage=Join-Path $Root '_tmp\TTM_FC01_COLAB_ABC_EXTRA_MODULES_20261113'
if(-not (Test-Path -LiteralPath (Join-Path $Root '.git'))){throw 'FC01_WRONG_REPOSITORY_ROOT'}
$Files=@(
 @{Name='fc01_build_private_corpus.py';Sha='a9978a1961a2d062e5229ad91593eddb01f7fcfab00c4dfb55cc3df316053c98'}
 @{Name='fc01_integrated_static_qa.py';Sha='f4f205ed4be0021faf99b3e73f4c0fb80ef4d1ce095ee5985507ca3f1e33cc3e'}
 @{Name='fc01_pinned_bpe.py';Sha='d90ddbcdbea8450d7605cf7e65936efd032344b8d7793c2272d4d0870cfbff01'}
)
foreach($F in $Files){
 $File=Join-Path $Source $F.Name
 if(-not (Test-Path -LiteralPath $File -PathType Leaf)){throw ('FC01_DEPENDENCY_SOURCE_MISSING:'+$F.Name)}
 $Hash=(Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
 if($Hash -cne $F.Sha){throw ('FC01_DEPENDENCY_SOURCE_SHA256_MISMATCH:'+$F.Name+':'+$Hash)}
}
Write-Host 'FC01_ABC_DEPENDENCIES_SOURCE=PASS_3_OF_3'
if(-not (Test-Path -LiteralPath $Stage)){New-Item -ItemType Directory -Path $Stage -ErrorAction Stop | Out-Null}
if(-not (Test-Path -LiteralPath $Stage -PathType Container)){throw 'FC01_STAGE_NOT_DIRECTORY'}
$Names=@(Get-ChildItem -LiteralPath $Stage -Force)
if($Names.Count -gt 0){
 if($Names.Count -ne $Files.Count){throw 'FC01_STAGE_UNEXPECTED_CONTENT_NO_OVERWRITE'}
 foreach($F in $Files){
  $Dest=Join-Path $Stage $F.Name
  if(-not (Test-Path -LiteralPath $Dest -PathType Leaf)){throw ('FC01_STAGE_MISSING_DEPENDENCY:'+$F.Name)}
  $Hash=(Get-FileHash -LiteralPath $Dest -Algorithm SHA256).Hash.ToLowerInvariant()
  if($Hash -cne $F.Sha){throw ('FC01_STAGE_MODIFIED_DEPENDENCY:'+$F.Name+':'+$Hash)}
 }
 Write-Host 'FC01_ABC_DEPENDENCY_STAGE=EXISTING_EXACT_REUSE'
} else {
 foreach($F in $Files){
  $Dest=Join-Path $Stage $F.Name
  Copy-Item -LiteralPath (Join-Path $Source $F.Name) -Destination $Dest -ErrorAction Stop
  $Hash=(Get-FileHash -LiteralPath $Dest -Algorithm SHA256).Hash.ToLowerInvariant()
  if($Hash -cne $F.Sha){throw ('FC01_STAGE_SHA256_POSTCOPY_FAIL:'+$F.Name)}
 }
 Write-Host 'FC01_ABC_DEPENDENCY_STAGE=CREATED_NEW'
}
Write-Host 'FC01_ABC_DEPENDENCY_SHA256=PASS_3_OF_3'
Write-Host ("FC01_UPLOAD_3_MODULES_TO_DRIVE_INPUT=" + $Stage)
Write-Host 'FC01_SCIENCE_EXECUTED=NO FC01_TRAINING_STEPS=0 FC01_TEST=SEALED'
