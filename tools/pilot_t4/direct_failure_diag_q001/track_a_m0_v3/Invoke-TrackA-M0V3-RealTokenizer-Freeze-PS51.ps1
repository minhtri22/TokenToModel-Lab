#requires -Version 5.1
<#
  Historical filename retained; this revision is READBACK ONLY.
  Real T1 BPE fixture was already frozen by a distinct reviewer.
  No freeze, model forward, nonce, optimizer or checkpoint operations.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{40}$')]
    [string]$ExpectedCommit,
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{64}$')]
    [string]$ExpectedRunnerSha256,
    [Parameter(Mandatory=$true)][switch]$ReadbackOnly,
    [string]$Root='D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$Python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$Branch='research/ttm-track-a-small4m-diagnosis-20261116'
$CanonicalRoot='D:\WORK\RESEARCH\TokenToModel-Lab'
$Worktree=Join-Path $Root 'worktrees\ttm-track-a-m0v3-postfix-readback-20261116'
$Tokenizer=Join-Path $Root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
$FixtureDir=Join-Path $Root '_tmp\ttm_track_a_m0_v3_real_i1_20261116'
$EvidenceDir=Join-Path $Root '_evidence\ttm-track-a-m0-v3'
$FrozenScorerSha='98101e871410e7255cd25f611e5eb9d7068ab264ac162e0af89ef1f1863f6587'
$ScorerLF='2d0b980768a0ac3079f361d94244cd694c97ed90e978fc83fb7991dc82b5c2ac'
$ScorerCRLF='d76936db04caec358ddfb6947656d60023dee7de5c3388f810c7ecbf08288b63'
$BpeSha='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
$RecordsSha='823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d'
$ManifestSha='0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04'
function Assert([bool]$OK,[string]$Reason) {
    if (-not $OK) { throw ('HOLD_M0_READBACK_'+$Reason) }
}
function HashBytes([byte[]]$Bytes,[string]$Kind) {
    if ($Kind -eq 'sha1') { $h=[Security.Cryptography.SHA1]::Create() }
    else { $h=[Security.Cryptography.SHA256]::Create() }
    try { return ([BitConverter]::ToString($h.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant() }
    finally { $h.Dispose() }
}
function Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Assert-SourceBlob([string]$Path,[string]$Relative) {
    Assert (Test-Path -LiteralPath $Path -PathType Leaf) ('SOURCE_MISSING_'+$Relative)
    $raw=[IO.File]::ReadAllBytes($Path)
    $encoding=[Text.UTF8Encoding]::new($false,$true)
    try { $src=$encoding.GetString($raw) } catch { throw 'HOLD_M0_READBACK_INVALID_UTF8' }
    $cr=[string][char]13
    $lf=[string][char]10
    $normalized=$src.Replace(($cr+$lf),$lf)
    Assert (-not $normalized.Contains($cr)) ('MIXED_EOL_'+$Relative)
    $lfbytes=$encoding.GetBytes($normalized)
    $crlfbytes=$encoding.GetBytes($normalized.Replace($lf,($cr+$lf)))
    $got=HashBytes $raw 'sha256'
    $lfsha=HashBytes $lfbytes 'sha256'
    $crlfsha=HashBytes $crlfbytes 'sha256'
    Assert (($got -ceq $lfsha) -or ($got -ceq $crlfsha)) ('UNKNOWN_EOL_'+$Relative)
    $header=[Text.Encoding]::ASCII.GetBytes(('blob {0}' -f $lfbytes.Length)+[char]0)
    $blob=New-Object byte[] ($header.Length+$lfbytes.Length)
    [Array]::Copy($header,0,$blob,0,$header.Length)
    [Array]::Copy($lfbytes,0,$blob,$header.Length,$lfbytes.Length)
    $actualBlob=HashBytes $blob 'sha1'
    $spec=('{0}:{1}' -f $ExpectedCommit,$Relative)
    $expectedBlob=((& git -C $Root rev-parse $spec) | Out-String).Trim().ToLowerInvariant()
    Assert ($LASTEXITCODE -eq 0 -and $actualBlob -ceq $expectedBlob) ('GIT_BLOB_MISMATCH_'+$Relative)
    return @{physical=$got; lf=$lfsha; crlf=$crlfsha; blob=$actualBlob}
}
Assert ($PSVersionTable.PSVersion.Major -eq 5) 'PS51_REQUIRED'
Assert ([bool]$ReadbackOnly) 'READBACK_ONLY_REQUIRED'
Assert ($Root -ceq $CanonicalRoot) 'EXACT_ROOT'
Assert (Test-Path -LiteralPath (Join-Path $Root '.git')) 'ROOT_GIT_MISSING'
Assert (Test-Path -LiteralPath $Python -PathType Leaf) 'PYTHON312_MISSING'
$pyver=((& $Python --version 2>&1) | Out-String).Trim()
Assert ($LASTEXITCODE -eq 0 -and $pyver -match '^Python 3\.12\.') 'PYTHON312_REQUIRED'
Assert (Test-Path -LiteralPath $Tokenizer -PathType Leaf) 'BPE_SOURCE_MISSING'
Assert ((Sha256 $Tokenizer) -ceq $BpeSha) 'BPE_SHA_MISMATCH'
Assert (Test-Path -LiteralPath $FixtureDir -PathType Container) 'EXISTING_FROZEN_DIR_REQUIRED'
$remote=((& git -C $Root ls-remote origin ('refs/heads/'+$Branch)) | Out-String).Trim()
Assert ($LASTEXITCODE -eq 0 -and $remote) 'REMOTE_REF_MISSING'
Assert ((($remote -split '\s+')[0]).ToLowerInvariant() -ceq $ExpectedCommit) 'REMOTE_HEAD_CHANGED'
if (-not (Test-Path -LiteralPath $Worktree)) {
    & git -C $Root fetch --no-tags origin ('refs/heads/'+$Branch) | Out-Null
    Assert ($LASTEXITCODE -eq 0) 'REMOTE_FETCH'
    & git -C $Root worktree add --detach $Worktree $ExpectedCommit | Out-Null
    Assert ($LASTEXITCODE -eq 0) 'WORKTREE_CREATE'
}
$head=((& git -C $Worktree rev-parse HEAD) | Out-String).Trim().ToLowerInvariant()
Assert ($LASTEXITCODE -eq 0 -and $head -ceq $ExpectedCommit) 'HEAD_CHANGED'
$RunnerRel='tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/ttm_sm4m_diag_q001.py'
$ScorerRel='tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/q001_m0_goldblind.py'
$dirty=@(& git -C $Worktree status --porcelain)
Assert ($LASTEXITCODE -eq 0) 'GIT_STATUS_FAILED'
foreach ($entry in $dirty) {
    $rel=([string]$entry).Substring(3).Replace('\','/')
    Assert (($rel -ceq $RunnerRel) -or ($rel -ceq $ScorerRel)) ('UNEXPECTED_DIRTY_'+$rel)
}
$Runner=Join-Path $Worktree ($RunnerRel.Replace('/','\'))
$Scorer=Join-Path $Worktree ($ScorerRel.Replace('/','\'))
$rpin=Assert-SourceBlob $Runner $RunnerRel
$spin=Assert-SourceBlob $Scorer $ScorerRel
Assert (($rpin.lf -ceq $ExpectedRunnerSha256) -or ($rpin.crlf -ceq $ExpectedRunnerSha256)) 'RUNNER_PIN_NOT_LF_OR_CRLF'
Assert ($spin.lf -ceq $ScorerLF -and $spin.crlf -ceq $ScorerCRLF) 'SCORER_LF_CRLF_PIN'
$records=Join-Path $FixtureDir 'FIXTURE_RECORDS.json'
$manifest=Join-Path $FixtureDir 'FIXTURE_MANIFEST.json'
$receipt=Join-Path $FixtureDir 'FIXTURE_FREEZE_RECEIPT.json'
Assert ((Test-Path -LiteralPath $records -PathType Leaf) -and
        (Test-Path -LiteralPath $manifest -PathType Leaf) -and
        (Test-Path -LiteralPath $receipt -PathType Leaf)) 'FROZEN_FILES_MISSING'
Assert ((Sha256 $records) -ceq $RecordsSha) 'FROZEN_RECORD_BYTES_CHANGED'
Assert ((Sha256 $manifest) -ceq $ManifestSha) 'FROZEN_MANIFEST_BYTES_CHANGED'
$m=Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json
Assert ($m.protocol_schema -ceq 'ttm.sm4m.q001.track_a.measurement.v3.integrated') 'PROTOCOL_CHANGED'
Assert ($m.scorer_sha256 -ceq $FrozenScorerSha) 'FROZEN_SCORER_PIN_CHANGED'
Assert (@($m.case_sha256.PSObject.Properties).Count -eq 80) 'CASE_SHA_COUNT'
Assert (@($m.group_sha256.PSObject.Properties).Count -eq 5) 'GROUP_SHA_COUNT'
Assert ($m.fixture_sha256 -ceq $RecordsSha) 'RECORD_MANIFEST_MISMATCH'
$old=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
Assert ($old.model_run -eq $false -and $old.actual_model_access -eq $false) 'UNEXPECTED_SCIENCE'
New-Item -ItemType Directory -Path $EvidenceDir -Force | Out-Null
$dst=Join-Path $EvidenceDir 'TTM_A_M0_V3_POSTFIX_READBACK_SANITIZED.json'
Assert (-not (Test-Path -LiteralPath $dst)) 'NO_OVERWRITE'
$report=[ordered]@{
    schema='ttm.track_a.m0v3.postfix_readback.v1'
    source_commit=$ExpectedCommit
    runner_lf_sha256=$rpin.lf
    runner_crlf_sha256=$rpin.crlf
    scorer_lf_sha256=$ScorerLF
    scorer_crlf_sha256=$ScorerCRLF
    frozen_scorer_sha256=$FrozenScorerSha
    tokenizer_sha256=$BpeSha
    fixture_records_sha256=$RecordsSha
    fixture_manifest_sha256=$ManifestSha
    fixture_receipt_sha256=(Sha256 $receipt)
    fixture_case_count=80
    fixture_group_count=5
    readback_only=$true
    I1='HOLD_PENDING_DISTINCT_REVIEW'
    I2='NOT_EXECUTED'
    checkpoint_access=$false
    model_forward=$false
    optimizer_steps=0
}
$json=ConvertTo-Json -InputObject $report -Depth 10
[IO.File]::WriteAllText($dst,($json+[Environment]::NewLine),[Text.UTF8Encoding]::new($false))
Write-Host 'POSTFIX_PRIVATE_READBACK=PASS_SCOPED'
Write-Host ('FIXTURE_SHA256='+$RecordsSha)
Write-Host ('RECEIPT_SHA256='+(Sha256 $dst))
Write-Host 'I1=HOLD_PENDING_DISTINCT_REVIEW'
Write-Host 'I2=NOT_EXECUTED'
