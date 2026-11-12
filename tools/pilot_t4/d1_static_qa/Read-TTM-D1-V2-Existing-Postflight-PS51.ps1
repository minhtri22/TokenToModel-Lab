# D1 V2 POSTFLIGHT ONLY. PowerShell 5.1; READ-ONLY, never reruns seed rekey.
$ErrorActionPreference = 'Stop'
$Root='D:\WORK\RESEARCH\TokenToModel-Lab\_tmp'
$V1=Join-Path $Root 'TTM_SMALL4M_D1_NEW_DEV_PRIVATE_20261111.json'
$V2=Join-Path $Root 'TTM_SMALL4M_D1_NEW_DEV_PRIVATE_V2_20261111.json'
$Scorer=Join-Path $Root 'TTM_SMALL4M_D1_BLIND_RATER_TEMPLATE_V2_20261111.json'
$Receipt=Join-Path $Root 'TTM_SMALL4M_D1_V2_VERSIONED_PRIVATE_REKEY_STATIC_RECEIPT_20261111.json'
$OldSHA='c43dde98c4fd2328ece9baba549c8bbc369964f0d19d4ecd9f8bb081d3256957'
$NewSHA='f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8'
$LF_SHA='1553d186eb55699506b6b920153d5c7af7f0ad26a186e1d58ffef0d1e7b4eb2e'
$ScorerSHA='ae85dddbb12b299f2f9252ad3b1df426eb7bd0af6ae52fbb73b5825c646833d4'

foreach($f in @($V1,$V2,$Scorer,$Receipt)) {
 if(-not (Test-Path -LiteralPath $f -PathType Leaf)){throw "D1_POSTFLIGHT_MISSING:$f"}
}
if((Get-FileHash $V1 -Algorithm SHA256).Hash.ToLowerInvariant() -ne $OldSHA){throw 'D1_V1_HASH_CHANGED'}
if((Get-FileHash $V2 -Algorithm SHA256).Hash.ToLowerInvariant() -ne $NewSHA){throw 'D1_V2_RAW_HASH_MISMATCH'}
if((Get-FileHash $Scorer -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ScorerSHA){throw 'D1_V2_SCORER_HASH_MISMATCH'}
if((Get-Item $V2).Length -ne 267645 -or (Get-Item $Scorer).Length -ne 349900){throw 'D1_V2_SIZE_MISMATCH'}
$Str=[IO.File]::ReadAllText($V2,[Text.Encoding]::UTF8).Replace("`r`n","`n")
$Sha256=[Security.Cryptography.SHA256]::Create()
try {
 $NormalSHA=[BitConverter]::ToString($Sha256.ComputeHash([Text.Encoding]::UTF8.GetBytes($Str))).Replace('-','').ToLowerInvariant()
} finally { $Sha256.Dispose() }
if($NormalSHA -ne $LF_SHA){throw 'D1_V2_NORMALIZED_SHA_MISMATCH'}

$Meta=Get-Content -LiteralPath $Receipt -Raw -Encoding UTF8 | ConvertFrom-Json
$A=Get-Content -LiteralPath $V1 -Raw -Encoding UTF8 | ConvertFrom-Json
$B=Get-Content -LiteralPath $V2 -Raw -Encoding UTF8 | ConvertFrom-Json
$R=Get-Content -LiteralPath $Scorer -Raw -Encoding UTF8 | ConvertFrom-Json
if($Meta.decision -cne 'HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE' -or
   $Meta.scientific_execution -cne 'NO' -or
   $Meta.training -cne 'NO' -or $Meta.inference -cne 'NO'){
 throw 'D1_POSTFLIGHT_UNEXPECTED_SCIENCE_RELEASE'
}
if($Meta.new_private_v2_raw_sha256 -cne $NewSHA -or
   $Meta.new_private_v2_lf_sha256 -cne $LF_SHA -or
   $Meta.scorer_template_raw_sha256 -cne $ScorerSHA -or
   $Meta.new_private_v2_raw_bytes -ne 267645 -or
   $Meta.scorer_template_raw_bytes -ne 349900){
 throw 'D1_POSTFLIGHT_RECEIPT_HASH_MISMATCH'
}
if($B.schema -cne 'ttm.small4m.d1.new_dev.private_stimulus.one_packet.v2' -or
   $B.supersedes_raw_sha256 -cne $OldSHA -or $B.version -ne 2){
 throw 'D1_POSTFLIGHT_V2_LINEAGE_MISMATCH'
}
if(@($A.families).Count -ne 16 -or @($B.families).Count -ne 16 -or
   @($A.prompts).Count -ne 128 -or @($B.prompts).Count -ne 128 -or
   @($A.neutral_prior_prompts).Count -ne 64 -or
   @($B.neutral_prior_prompts).Count -ne 64 -or
   @($B.blind_mapping_private).Count -ne 512 -or
   @($R.records).Count -ne 512){throw 'D1_POSTFLIGHT_CARDINALITY_FAIL'}
foreach($entry in @(@('families',16,@('scene','fact_A','fact_B','continuation_A','continuation_B','short_filler','long_filler')),
                   @('prompts',128,@('id','prompt_text','candidate_A','candidate_B','prompt_bpe')),
                   @('neutral_prior_prompts',64,@('id','prompt_text','prompt_bpe')))){
 $name=$entry[0];$count=[int]$entry[1];$fields=$entry[2]
 for($i=0;$i -lt $count;$i++){
  foreach($field in $fields){
   if($A.$name[$i].$field -cne $B.$name[$i].$field){throw "D1_V2_STIMULUS_CHANGED:$name"}
  }
 }
}
$OldSpec=@($A.run_parameters.decode | Where-Object {$_.method -eq 'nucleus'})
$NewSpec=@($B.run_parameters.decode | Where-Object {$_.method -eq 'nucleus'})
if($OldSpec.Count -ne 1 -or $NewSpec.Count -ne 1){throw 'D1_V2_DECODER_SPEC_INVALID'}
$OldSeeds=@($OldSpec[0].seeds);$NewSeeds=@($NewSpec[0].seeds)
if($OldSeeds.Count -ne 3 -or $NewSeeds.Count -ne 3 -or
   @($NewSeeds | Select-Object -Unique).Count -ne 3){throw 'D1_V2_SEED_COUNT_INVALID'}
foreach($s in $NewSeeds){if($OldSeeds -contains $s){throw 'D1_V2_SEED_REUSE'}}
$Map=@{}
foreach($row in $B.blind_mapping_private){
 $id=[string]$row.blind_id
 if($Map.ContainsKey($id)){throw 'D1_V2_BLIND_ID_COLLISION'}
 $Map[$id]=$true
 if($row.decoder -eq 'GREEDY'){
  if($null -ne $row.seed){throw 'D1_V2_GREEDY_SEED_PRESENT'}
 } elseif($row.decoder -eq 'NUCLEUS'){
  if($NewSeeds -notcontains $row.seed){throw 'D1_V2_INVALID_NUCLEUS_SEED'}
 } else {throw 'D1_V2_UNEXPECTED_DECODER'}
}
$RaterIds=@{}
foreach($r in $R.records){
 $id=[string]$r.blind_id
 if(-not $Map.ContainsKey($id) -or $RaterIds.ContainsKey($id)){throw 'D1_V2_SCORER_ID_MISMATCH'}
 $RaterIds[$id]=$true
 if($null -ne $r.generated_text -or $null -ne $r.adherence_0_to_3){throw 'D1_V2_SCIENCE_OUTPUT_PREPOPULATED'}
 foreach($forbidden in @('seed','decoder','truth','condition','prompt_id','candidate_A','candidate_B')){
  if($r.PSObject.Properties.Name -contains $forbidden){throw 'D1_V2_RATER_FIELD_LEAK'}
 }
}
if($Map.Count -ne 512 -or $RaterIds.Count -ne 512){throw 'D1_V2_BLIND_COVERAGE_INVALID'}
Write-Host 'TTM_D1_V2_EXISTING_POSTFLIGHT=PASS_SCOPED'
Write-Host "D1_V2_RAW_SHA256=$NewSHA"
Write-Host "D1_V2_LF_SHA256=$LF_SHA"
Write-Host "D1_V2_SCORER_SHA256=$ScorerSHA"
Write-Host 'D1_V2_NO_REKEY_RERUN=TRUE'
Write-Host 'D1_V2_STIMULUS_UNCHANGED=TRUE'
Write-Host 'D1_V2_BLIND_CUSTODY_STATIC=PASS_SCOPED'
Write-Host 'D1_V2_PRIVATE_OVERLAP=NOT_VERIFIED'
Write-Host 'D1_V2_RATER_INDEPENDENCE=NOT_ATTESTED'
Write-Host 'D1_V2_SCIENCE_EXECUTED=NO'
Write-Host 'D1_V2_SINGLE_OWNER_RELEASE=HOLD'
