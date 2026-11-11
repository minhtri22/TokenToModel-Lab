# TTM CF1 frozen O0 / 36 public DEV pairs / one-shot CPU; PowerShell 5.1
# Everything stays within D:\WORK\RESEARCH\TokenToModel-Lab. Never reads FINAL.
[CmdletBinding()]
param(
 [string]$Root='D:\WORK\RESEARCH\TokenToModel-Lab',
 [string]$Python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe',
 [string]$Checkpoint=''
)
$ErrorActionPreference='Stop'; Set-StrictMode -Version Latest
$source='research/ttm-o0-narrative-cf1-source-scorer-blind-readiness-20261111'
$ancestor='4f5071daffa28db1468ee9af0dbd3ad2f8ab41a6'
$runnerBlob='14109c8d4e27a874e1832a480a0d7eeebed78b2f'
$evidence='evidence/ttm-cf1-step1024-dev36-once-20261111'
$checkpointSha='CB985751795C8328AD65ACF7CA4C1033CE35182C1BFBDB8C38550DE629CB271B'
$manifestSha='CBA18E60CEE3D08A353EE6D4A451017289E45AF7B4B1179C87171B9B78D7DFDC'
$Root=(Resolve-Path -LiteralPath $Root).Path
if($Root.TrimEnd('\') -ine 'D:\WORK\RESEARCH\TokenToModel-Lab'){throw 'WRONG_PROJECT_ROOT'}
if(-not (Test-Path -LiteralPath (Join-Path $Root '.git'))){throw 'NOT_TTM_REPOSITORY'}
if(-not (Test-Path -LiteralPath $Python -PathType Leaf)){throw 'PYTHON312_NOT_FOUND'}
$manifest=Join-Path $Root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
if(-not (Test-Path -LiteralPath $manifest -PathType Leaf)){throw 'T1_MANIFEST_MISSING'}
if((Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash -ne $manifestSha){throw 'T1_MANIFEST_HASH_FAIL'}
if(-not $Checkpoint){
 $hits=@()
 foreach($p in @(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter '*.pt' -ErrorAction Stop)){
  if((Get-FileHash -LiteralPath $p.FullName -Algorithm SHA256).Hash -eq $checkpointSha){$hits+= $p.FullName}
 }
 if($hits.Count -lt 1){throw 'FROZEN_STEP1024_CHECKPOINT_NOT_FOUND'}
 $Checkpoint=$hits[0]
}
$Checkpoint=(Resolve-Path -LiteralPath $Checkpoint).Path
if(-not $Checkpoint.StartsWith(($Root.TrimEnd('\')+'\'),[System.StringComparison]::OrdinalIgnoreCase)){throw 'CHECKPOINT_OUTSIDE_TTM'}
if((Get-FileHash -LiteralPath $Checkpoint -Algorithm SHA256).Hash -ne $checkpointSha){throw 'CHECKPOINT_HASH_FAIL'}
& $Python -c 'import sys,torch,regex; assert sys.version_info[:2]==(3,12)'
if($LASTEXITCODE -ne 0){throw 'PYTHON312_TORCH_REGEX_UNAVAILABLE'}
$run=Join-Path $Root '_tmp\TTM_CF1_STEP1024_DEV36_ONE_SHOT_20261111'
$stage=Join-Path $Root '_tmp\cf1_dev_only_one_shot_owner_cpu.py'
$wt=Join-Path $Root '.worktrees\cf1-dev36-once-evidence-20261111'
foreach($p in @($run,$stage,$wt)){if(Test-Path -LiteralPath $p){throw ('ONE_SHOT_ALREADY_PRESENT_REFUSE_REPLAY: '+$p)}}
& git -C $Root fetch --no-tags origin $source
if($LASTEXITCODE -ne 0){throw 'PINNED_GITHUB_FETCH_FAILED'}
$head=(& git -C $Root rev-parse FETCH_HEAD).Trim()
& git -C $Root merge-base --is-ancestor $ancestor $head
if($LASTEXITCODE -ne 0){throw 'SOURCE_ANCESTRY_CHANGED'}
$already=@(& git -C $Root ls-remote --heads origin $evidence)
if($LASTEXITCODE -ne 0 -or $already.Count -ne 0){throw 'EVIDENCE_REMOTE_EXISTS_OR_UNAVAILABLE'}
& git -C $Root cat-file -e ($runnerBlob + '^{blob}')
if($LASTEXITCODE -ne 0){throw 'EXACT_RUNNER_GIT_BLOB_MISSING'}
# Stage Python runner without PS5.1 text-redirection corruption.
# PowerShell 5.1 must not strip double quotes inside native Python -c arguments.
$blob_stage_py = "import pathlib,subprocess,sys,hashlib; b=subprocess.check_output(['git','-C',sys.argv[1],'cat-file','blob',sys.argv[3]]); assert hashlib.sha1(b'blob '+str(len(b)).encode()+bytes([0])+b).hexdigest()==sys.argv[3]; pathlib.Path(sys.argv[2]).open('xb').write(b)"
& $Python -c $blob_stage_py $Root $stage $runnerBlob
if($LASTEXITCODE -ne 0){throw 'EXACT_RUNNER_STAGE_FAILED'}
# Inner runner checks checkpoint, manifest and SIX exact Git blobs before creating run dir.
& $Python $stage --repo-root $Root --checkpoint $Checkpoint
if($LASTEXITCODE -ne 0){throw 'CF1_DEV_ONLY_FAILED_NO_AUTOMATIC_REPLAY'}
$scores=Join-Path $run 'CF1_FROZEN_O0_DEV36_SCORES.json'
$summary=Join-Path $run 'CF1_DEV36_OWNER_LOCAL_ADJUDICATION.json'
if(-not (Test-Path -LiteralPath $scores -PathType Leaf) -or -not (Test-Path -LiteralPath $summary -PathType Leaf)){throw 'SCORES_OR_SUMMARY_MISSING'}
$res=Get-Content -LiteralPath $summary -Raw -Encoding UTF8 | ConvertFrom-Json
if([int]$res.pairs -ne 36 -or [int]$res.gpu_calls -ne 0 -or [int]$res.optimizer_updates -ne 0 -or $res.final_opened){throw 'OUT_OF_SCOPE_RESULT'}
# Create a NEW evidence branch from source HEAD; never checkout/merge main.
& git -C $Root worktree add --detach $wt $head
if($LASTEXITCODE -ne 0){throw 'WORKTREE_CREATE_FAILED'}
& git -C $wt switch -c $evidence
if($LASTEXITCODE -ne 0){throw 'EVIDENCE_BRANCH_CREATE_FAILED'}
$relative='artifacts\qa\ttm-narrative-cf1\dev36_owner_once_20261111'
$dest=Join-Path $wt $relative
New-Item -ItemType Directory -Path $dest -ErrorAction Stop | Out-Null
foreach($name in @('CF1_DEV36_OWNER_LOCAL_ADJUDICATION.json','CF1_FROZEN_O0_DEV36_SCORES.json','ONE_SHOT_STDOUT.txt','ONE_SHOT_STDERR.txt')){
 Copy-Item -LiteralPath (Join-Path $run $name) -Destination (Join-Path $dest $name) -ErrorAction Stop
}
$pin=[ordered]@{
 schema='ttm.cf1.dev36.owner_one_shot.evidence_sha256.v1'; source_commit=$head
 python_runner_git_blob=$runnerBlob; scored_pairs=36
 checkpoint_sha256=$checkpointSha.ToLowerInvariant(); BPE_sha256=$manifestSha.ToLowerInvariant()
 scores_sha256=(Get-FileHash -LiteralPath $scores -Algorithm SHA256).Hash.ToLowerInvariant()
 summary_sha256=(Get-FileHash -LiteralPath $summary -Algorithm SHA256).Hash.ToLowerInvariant()
 optimizer_updates=0; gpu_calls=0; final_opened=$false; Q1Q2_TEST_opened=$false
}
$pin | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $dest 'CF1_DEV36_SOURCE_SHA256_READBACK.json') -Encoding UTF8
& git -C $wt add -- $relative
if($LASTEXITCODE -ne 0){throw 'GIT_EVIDENCE_STAGE_FAILED'}
& git -C $wt commit -m 'TTM CF1 frozen O0 DEV36 CPU one-shot evidence with SHA pins'
if($LASTEXITCODE -ne 0){throw 'GIT_EVIDENCE_COMMIT_FAILED'}
& git -C $wt push -u origin $evidence
if($LASTEXITCODE -ne 0){throw 'GIT_EVIDENCE_PUSH_FAILED_PRESERVE_LOCAL_WORKTREE'}
$local=(& git -C $wt rev-parse HEAD).Trim()
$remoteLine=@(& git -C $Root ls-remote --heads origin $evidence)
if($LASTEXITCODE -ne 0 -or $remoteLine.Count -ne 1){throw 'GITHUB_EVIDENCE_READBACK_FAILED'}
$remote=($remoteLine[0] -split '\s+')[0]
if($local -ne $remote){throw 'GITHUB_EVIDENCE_SHA_MISMATCH'}
Write-Host ('CF1_DEV_BOTH_CORRECT=' + $res.both_correct + '/36')
Write-Host ('CF1_GITHUB_EVIDENCE_HEAD=' + $remote)
Write-Host ('CF1_GITHUB_EVIDENCE_BRANCH=' + $evidence)
Write-Host 'CF1_FINAL_GPU_TRAINING_MAIN_PR13_LINEAGE_UNCHANGED=TRUE'
