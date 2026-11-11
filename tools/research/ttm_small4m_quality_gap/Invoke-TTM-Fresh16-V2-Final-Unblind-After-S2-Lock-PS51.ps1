# TTM FRESH16 V2 - Exact S2 byte recovery and frozen unblind/tally.
# NEVER run before committed S1 and S2 score SHA locks. No inference or training.
# Must operate in the original pinned worktree, no new Git worktrees or resets.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $root 'worktrees\ttm-fresh16-quality-20261111'
$branch = 'research/ttm-small4m-prompt-adherence-continuation-design-20261111'
$source = 'c05872354d892a9656f8f98642866f7eebfd0f50'
$s1Commit = '5fd1d923de52d18709a39332400e3e98e6dfb31d'
$s2Commit = '9c02e0f3c7d3073e742de7fc75a08e5a48ec9afe'
$s1Rel = 'artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_S1_SCORE_SHA_ANCHOR.json'
$s2Rel = 'artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_S2_PAIR_SHA_ANCHOR.json'
$s1SHA = 'd08d59a9fe9738ef798aa2e0449345cb76e5c9f24f825a37685f928052028d35'
$s2SHA = '517643feba73c96003334a1e8a9095ebd091aaff3e764ddd87faf91dbf78b31b'
$s2KnownCRLFSHA = 'f677073cd67ffa7b4954a9e6fb5a384ac32c6f62176b579822949e11fcb5b2a8'
$mapSHA = 'eb570460b1423bb4b2355ccb5b7b56862c641721d5ecf62f7136224b71ea20a8'
$dir = Join-Path $root '_tmp\ttm_fresh16_v2_e0_20261111'
$s1 = Join-Path $dir 'TTM_FRESH16_V2_S1_SCORES_EXACT_LOCKED_LF_PRIVATE.json'
$s2Transport = Join-Path $dir 'TTM_FRESH16_V2_S2_PAIR_SCORES_TRANSPORT_CRLF_PRIVATE.json'
$s2Exact = Join-Path $dir 'TTM_FRESH16_V2_S2_PAIR_SCORES_EXACT_LOCKED_LF_PRIVATE.json'
$s2Packet = Join-Path $dir 'S2_BLIND_PACKET_PRIVATE.json'
$final = Join-Path $dir 'FINAL_TALLY_PRIVATE.json'
$mapFile = Join-Path $dir 'BLIND_MAP_PRIVATE.json'
$gate = Join-Path $wt 'tools\research\ttm_small4m_quality_gap\ttm_fresh16_v2_packet_gate.py'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
foreach ($p in @($root,$wt,$dir)) {
    if (-not (Test-Path -LiteralPath $p -PathType Container)) { throw "FINAL_GATE_MISSING_DIRECTORY: $p" }
}
foreach ($p in @($s1,$s2Transport,$s2Packet,$mapFile,$gate,$py)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw "FINAL_GATE_MISSING_INPUT: $p" }
}
if (Test-Path -LiteralPath $final) { throw 'FINAL_TALLY_EXISTS_DO_NOT_RERUN' }
$branchActual = (& git -C $wt branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $branchActual -ne $branch) { throw 'FINAL_GATE_WRONG_BRANCH' }
$head = (& git -C $wt rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne $source) { throw 'FINAL_GATE_FROZEN_SOURCE_DRIFT' }
$dirty = @(& git -C $wt status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0 -or $dirty.Count -ne 0) { throw 'FINAL_GATE_WORKTREE_DIRTY' }
if ((Get-FileHash -LiteralPath $s1 -Algorithm SHA256).Hash.ToLowerInvariant() -ne $s1SHA) { throw 'FINAL_GATE_S1_SHA_CHANGED' }
if ((Get-FileHash -LiteralPath $mapFile -Algorithm SHA256).Hash.ToLowerInvariant() -ne $mapSHA) { throw 'FINAL_GATE_BLIND_MAP_SHA_CHANGED' }

& git -C $wt fetch origin "refs/heads/$branch"
if ($LASTEXITCODE -ne 0) { throw 'FINAL_GATE_FETCH_COMMIT_OBJECTS_FAILED' }
foreach ($item in @(@($s1Commit,$s1Rel),@($s2Commit,$s2Rel))) {
    & git -C $wt cat-file -e ($item[0] + ':' + $item[1])
    if ($LASTEXITCODE -ne 0) { throw 'FINAL_GATE_LOCKED_GIT_RECEIPT_MISSING' }
}
if ((& git -C $wt rev-parse HEAD).Trim() -ne $source) { throw 'FINAL_GATE_E0_HEAD_CHANGED_AFTER_FETCH' }
$s1Anchor = (& git -C $wt show ($s1Commit + ':' + $s1Rel) | Out-String) | ConvertFrom-Json
$s2Anchor = (& git -C $wt show ($s2Commit + ':' + $s2Rel) | Out-String) | ConvertFrom-Json
if ($s1Anchor.s1_score_file_sha256 -ne $s1SHA -or
    $s2Anchor.s2_pair_file_sha256 -ne $s2SHA -or
    $s2Anchor.s1_score_file_sha256 -ne $s1SHA -or
    $s2Anchor.sealed_map_sha256 -ne $mapSHA -or
    $s2Anchor.source_head -ne $source) { throw 'FINAL_GATE_COMMITTED_SHA_CONTRACT_INVALID' }

# The remote text transfer may change only line endings. Reconstruct original
# UTF-8 bytes into a SEPARATE new private file and demand the immutable SHA.
if (-not (Test-Path -LiteralPath $s2Exact)) {
    $transportSha = (Get-FileHash -LiteralPath $s2Transport -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($transportSha -notin @($s2KnownCRLFSHA,$s2SHA)) { throw "FINAL_GATE_S2_TRANSPORT_UNKNOWN_SHA_PRESERVE: $transportSha" }
    $inBytes = [System.IO.File]::ReadAllBytes($s2Transport)
    if ($transportSha -eq $s2SHA) {
        $exactBytes = $inBytes
    } else {
        $buffer = New-Object System.IO.MemoryStream
        try {
            for ($i = 0; $i -lt $inBytes.Length; $i++) {
                if ($inBytes[$i] -eq 13 -and $i + 1 -lt $inBytes.Length -and $inBytes[$i + 1] -eq 10) { continue }
                $buffer.WriteByte($inBytes[$i])
            }
            $exactBytes = $buffer.ToArray()
        } finally { $buffer.Dispose() }
    }
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { $candidate = ([System.BitConverter]::ToString($hasher.ComputeHash($exactBytes))).Replace('-','').ToLowerInvariant() }
    finally { $hasher.Dispose() }
    if ($candidate -ne $s2SHA) { throw "FINAL_GATE_EXACT_S2_BYTES_NOT_LOCKED: $candidate" }
    $stream = [System.IO.File]::Open($s2Exact,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
    try {
        $stream.Write($exactBytes,0,$exactBytes.Length)
        $stream.Flush($true)
    } finally { $stream.Dispose() }
}
if ((Get-FileHash -LiteralPath $s2Exact -Algorithm SHA256).Hash.ToLowerInvariant() -ne $s2SHA) {
    throw 'FINAL_GATE_S2_CANONICAL_BYTES_SHA_INVALID'
}
Write-Host 'FRESH16_S2_SHA_LOCK=PASS_GIT_COMMIT_AND_EXACT_BYTES'
Write-Host "FRESH16_S2_SCORE_SHA256=$s2SHA"
Write-Host 'FRESH16_SCIENCE_FORWARD=NO'

# Invoke ORIGINAL FROZEN pre-registered gate. Only it may unblind and tally.
& $py $gate --mode unblind --project-root $root --worktree $wt --run-dir $dir --expected-head $source --s1-scores $s1 --s1-anchor-commit $s1Commit --s2-scores $s2Exact --s2-anchor-commit $s2Commit
if ($LASTEXITCODE -ne 0) { throw 'FINAL_GATE_FROZEN_TALLY_HOLD_PRESERVE_ALL_NO_RERUN' }
if (-not (Test-Path -LiteralPath $final -PathType Leaf)) { throw 'FINAL_GATE_FROZEN_TALLY_FILE_MISSING' }
$t = Get-Content -LiteralPath $final -Raw -Encoding UTF8 | ConvertFrom-Json
if ($t.schema -ne 'ttm.fresh16.v2.final_tally.v1' -or
    $t.source_head -ne $source -or
    $t.S1_scores_sha256 -ne $s1SHA -or
    $t.S2_scores_sha256 -ne $s2SHA -or
    $t.sealed_map_sha256 -ne $mapSHA -or
    $t.original_outputs -ne 32 -or
    $t.H1_denominator -ne 16 -or
    $t.H2_denominator -ne 8) {
    throw 'FINAL_GATE_TALLY_SOURCE_OR_SCHEMA_MISMATCH_PRESERVE'
}
$finalSha = (Get-FileHash -LiteralPath $final -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host 'FRESH16_FINAL_TALLY=PASS_FROZEN_GATE_EXECUTED'
Write-Host "FRESH16_FINAL_TALLY_SHA256=$finalSha"
Write-Host "FRESH16_H1_STEP1024=$($t.H1_num_ge2)/$($t.H1_denominator)"
Write-Host "FRESH16_H2_STEP1024=$($t.H2_pairs)/$($t.H2_denominator)"
Write-Host "FRESH16_FINAL_VERDICT=$($t.verdict)"
Write-Host "FRESH16_FINAL_TALLY_PRIVATE=$final"
Write-Host 'FRESH16_LINEAGE_UPDATE=NOT_DONE_WAIT_FOR_OWNER_EVIDENCE_COMMIT'
Write-Host 'FRESH16_INFERENCE_RERUN=FORBIDDEN'
