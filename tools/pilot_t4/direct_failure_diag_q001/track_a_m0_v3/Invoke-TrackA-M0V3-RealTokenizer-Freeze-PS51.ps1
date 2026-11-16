#requires -Version 5.1
<#
  Track A M0 v3 private I1 fixture custody only. NO checkpoint/model/I2.
  Invoked by owner or managed Windows task on the pinned Windows host.
  Creates a detached source worktree INSIDE original project root and a
  versioned PRIVATE fixture under _tmp. Prints hashes only, never token IDs.
  Never pushes/merges to Git; reviewer must publish sanitized evidence.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{40}$')]
    [string]$ExpectedCommit,
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{64}$')]
    [string]$ExpectedRunnerSha256,
    [string]$Root='D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$Python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Branch='research/ttm-track-a-small4m-diagnosis-20261116'
$CanonicalRoot='D:\WORK\RESEARCH\TokenToModel-Lab'
$ScorerSha='98101e871410e7255cd25f611e5eb9d7068ab264ac162e0af89ef1f1863f6587'
$OriginalBpeSha='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
$Worktree=Join-Path $Root 'worktrees\ttm-track-a-m0v3-source-20261116'
$Tokenizer=Join-Path $Root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
$FixtureDir=Join-Path $Root '_tmp\ttm_track_a_m0_v3_real_i1_20261116'
$PublicEvidence=Join-Path $Root '_evidence\ttm-track-a-m0-v3'
function Assert([bool]$Condition,[string]$Message) {
    if (-not $Condition) { throw ('HOLD_M0_REAL_CUSTODY_'+$Message) }
}
function Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
Assert ($PSVersionTable.PSVersion.Major -eq 5) 'PS51_REQUIRED'
Assert ($Root -ceq $CanonicalRoot) 'EXACT_PROJECT_ROOT'
Assert (Test-Path -LiteralPath (Join-Path $Root '.git')) 'ROOT_GIT_MISSING'
Assert (Test-Path -LiteralPath $Python -PathType Leaf) 'PYTHON312_MISSING'
$v=& $Python -c 'import sys;print("%d.%d.%d"%sys.version_info[:3])'
Assert ($LASTEXITCODE -eq 0 -and $v -match '^3\.12\.') 'PYTHON_VERSION_NOT_312'
Assert (Test-Path -LiteralPath $Tokenizer -PathType Leaf) 'ORIGINAL_T1_SOURCE_MISSING'
Assert ((Sha256 $Tokenizer) -ceq $OriginalBpeSha) 'ORIGINAL_T1_SOURCE_SHA_MISMATCH'
Assert (-not (Test-Path -LiteralPath $FixtureDir)) 'OUTPUT_EXISTS_NO_OVERWRITE'
# Ensure we will not silently use a different HEAD than the reviewer expects.
$remote=(& git -C $Root ls-remote origin "refs/heads/$Branch" 2>&1)
Assert ($LASTEXITCODE -eq 0) 'REMOTE_BRANCH_READ_FAILED'
$remoteHead=([string]$remote -split '\s+')[0].ToLowerInvariant()
Assert ($remoteHead -ceq $ExpectedCommit) 'REMOTE_HEAD_CHANGED'
if (-not (Test-Path -LiteralPath $Worktree)) {
    & git -C $Root fetch --no-tags origin "refs/heads/$Branch" | Out-Null
    Assert ($LASTEXITCODE -eq 0) 'BRANCH_FETCH_FAILED'
    & git -C $Root worktree add --detach $Worktree $ExpectedCommit | Out-Null
    Assert ($LASTEXITCODE -eq 0) 'WORKTREE_ADD_FAILED'
}
$head=(& git -C $Worktree rev-parse HEAD).Trim().ToLowerInvariant()
Assert ($LASTEXITCODE -eq 0 -and $head -ceq $ExpectedCommit) 'WORKTREE_HEAD_MISMATCH'
$dirty=@(& git -C $Worktree status --porcelain)
Assert ($LASTEXITCODE -eq 0 -and $dirty.Count -eq 0) 'WORKTREE_NOT_CLEAN'
$Runner=Join-Path $Worktree 'tools\pilot_t4\direct_failure_diag_q001\preexec_candidate_20261116\ttm_sm4m_diag_q001.py'
$Scorer=Join-Path $Worktree 'tools\pilot_t4\direct_failure_diag_q001\track_a_m0_v3\q001_m0_goldblind.py'
Assert (Test-Path -LiteralPath $Runner -PathType Leaf) 'RUNNER_MISSING'
Assert (Test-Path -LiteralPath $Scorer -PathType Leaf) 'SCORER_MISSING'
Assert ((Sha256 $Runner) -ceq $ExpectedRunnerSha256) 'RUNNER_SHA_MISMATCH'
Assert ((Sha256 $Scorer) -ceq $ScorerSha) 'SCORER_SHA_MISMATCH'
# The existing owner-internal owner_scope and T1 BPE guard independently verify
# the exact original source, then produce NEW v3 bytes only, not I2.
$out=@(& $Python -I $Runner fixture-freeze --owner-internal --root $Root --tokenizer-source $Tokenizer --out $FixtureDir 2>&1)
Assert ($LASTEXITCODE -eq 0) ('FIXTURE_FREEZE_FAILED_'+($out -join '|'))
$records=Join-Path $FixtureDir 'FIXTURE_RECORDS.json'
$manifest=Join-Path $FixtureDir 'FIXTURE_MANIFEST.json'
$receipt=Join-Path $FixtureDir 'FIXTURE_FREEZE_RECEIPT.json'
Assert ((Test-Path $records) -and (Test-Path $manifest) -and (Test-Path $receipt)) 'FREEZE_FILES_MISSING'
$m=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
Assert ($m.protocol_schema -ceq 'ttm.sm4m.q001.track_a.measurement.v3.integrated') 'PROTOCOL_MISMATCH'
Assert ($m.scorer_sha256 -ceq $ScorerSha) 'MANIFEST_SCORER_MISMATCH'
Assert ($m.case_sha256.PSObject.Properties.Count -eq 80) 'CASE_SHA_COUNT'
Assert ($m.group_sha256.PSObject.Properties.Count -eq 5) 'GROUP_SHA_COUNT'
Assert ((Sha256 $records) -ceq $m.fixture_sha256) 'FIXTURE_BYTES_MISMATCH'
$meta=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
Assert (($meta.model_run -eq $false) -and ($meta.actual_model_access -eq $false)) 'UNEXPECTED_SCIENCE'
New-Item -ItemType Directory -Path $PublicEvidence -Force | Out-Null
$report=[ordered]@{
 schema='ttm.track_a.m0v3.real_fixture_custody.v1'
 operation='A_M0_V3_INTEGRATED_REAL_FIXTURE_RUNNER_CUSTODY_NATIVE_AND_DISTINCT_I1_ADJUDICATION_SINGLE_GATE'
 source_commit=$ExpectedCommit
 runner_sha256=$ExpectedRunnerSha256
 scorer_sha256=$ScorerSha
 tokenizer_original_t1_sha256=$OriginalBpeSha
 project_root=$CanonicalRoot
 host=$env:COMPUTERNAME
 python_version=$v
 ps_major=5
 fixture_records_sha256=Sha256 $records
 fixture_manifest_sha256=Sha256 $manifest
 fixture_freeze_receipt_sha256=Sha256 $receipt
 fixture_group_hashes=$m.group_sha256
 fixture_count=80
 private_fixture_relative_path='_tmp/ttm_track_a_m0_v3_real_i1_20261116'
 public_token_ids_in_receipt=$false
 checkpoint_access=$false
 model_forward=$false
 optimizer_steps=0
 I2='NOT_EXECUTED'
 I1='PENDING_DISTINCT_REVIEW'
}
$dst=Join-Path $PublicEvidence 'TTM_A_M0_V3_REAL_FIXTURE_CUSTODY_SANITIZED.json'
Assert (-not (Test-Path -LiteralPath $dst)) 'RECEIPT_EXISTS_NO_OVERWRITE'
$json=ConvertTo-Json -InputObject $report -Depth 15
[System.IO.File]::WriteAllText($dst, $json+"\n", [System.Text.UTF8Encoding]::new($false))
Write-Host 'TTM_A_M0_V3_REAL_TOKENIZER_CUSTODY=PASS_SCOPE_ONLY'
Write-Host ('REAL_FIXTURE_SHA256='+$m.fixture_sha256)
Write-Host ('SOURCE_COMMIT='+$ExpectedCommit)
Write-Host ('RECEIPT_SHA256='+(Sha256 $dst))
Write-Host ('SANITIZED_RECEIPT='+$dst)
Write-Host 'I1=PENDING_DISTINCT_REVIEW'
Write-Host 'I2=NOT_EXECUTED'
