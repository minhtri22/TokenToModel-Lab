# TTM FRESH16 V2 - S2 blinded 16-pair packet, after committed S1 SHA lock.
# No inference, no rescore, no checkpoint unblinding, and no worktree reset.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $root 'worktrees\ttm-fresh16-quality-20261111'
$branch = 'research/ttm-small4m-prompt-adherence-continuation-design-20261111'
$source = 'c05872354d892a9656f8f98642866f7eebfd0f50'
$s1Commit = '5fd1d923de52d18709a39332400e3e98e6dfb31d'
$s1Rel = 'artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_S1_SCORE_SHA_ANCHOR.json'
$s1SHA = 'd08d59a9fe9738ef798aa2e0449345cb76e5c9f24f825a37685f928052028d35'
$mapSHA = 'eb570460b1423bb4b2355ccb5b7b56862c641721d5ecf62f7136224b71ea20a8'
$dir = Join-Path $root '_tmp\ttm_fresh16_v2_e0_20261111'
$s1File = Join-Path $dir 'TTM_FRESH16_V2_S1_SCORES_PRIVATE.json'
$s2File = Join-Path $dir 'S2_BLIND_PACKET_PRIVATE.json'
$mapFile = Join-Path $dir 'BLIND_MAP_PRIVATE.json'
$finishedFile = Join-Path $dir 'RUN_FINISHED.json'
$gate = Join-Path $wt 'tools\research\ttm_small4m_quality_gap\ttm_fresh16_v2_packet_gate.py'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
foreach ($p in @($root,$wt)) {
    if (-not (Test-Path -LiteralPath $p -PathType Container)) { throw "S2_MISSING_DIRECTORY: $p" }
}
foreach ($p in @($s1File,$mapFile,$finishedFile,$gate,$py)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw "S2_MISSING_FILE: $p" }
}
if (Test-Path -LiteralPath $s2File) { throw 'S2_PACKET_EXISTS_NO_OVERWRITE' }
$actualBranch = (& git -C $wt branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $actualBranch -ne $branch) { throw 'S2_WRONG_BRANCH' }
$actualHead = (& git -C $wt rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualHead -ne $source) { throw 'S2_SOURCE_HEAD_CHANGED' }
$dirty = @(& git -C $wt status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0 -or $dirty.Count -ne 0) { throw 'S2_WORKTREE_DIRTY' }
$actualScoreSha = (Get-FileHash -LiteralPath $s1File -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualScoreSha -ne $s1SHA) {
    # Transport-specific correction ONLY. The first RemoteDesktop text write
    # converted original UTF-8 LF bytes to CRLF; original scores are unchanged.
    # Never update the S1 Git anchor, overwrite the source, or rescore.
    $expectedCrlfSHA = 'b33e3c11a9634985ba33de8d5bda2b9ec1ecdc99fb904c6dc2df26d82afc5952'
    if ($actualScoreSha -ne $expectedCrlfSHA) {
        throw "S2_UNRECOGNIZED_S1_SHA_DRIFT_PRESERVE: $actualScoreSha"
    }
    $canonicalPath = Join-Path $dir 'TTM_FRESH16_V2_S1_SCORES_EXACT_LOCKED_LF_PRIVATE.json'
    if (-not (Test-Path -LiteralPath $canonicalPath)) {
        # Lossless, BYTE-LEVEL reversal of precisely CRLF -> LF.
        # Validate the candidate SHA before creating a new private file.
        $inputBytes = [System.IO.File]::ReadAllBytes($s1File)
        $buffer = New-Object System.IO.MemoryStream
        try {
            for ($i = 0; $i -lt $inputBytes.Length; $i++) {
                if (($inputBytes[$i] -eq 13) -and (($i + 1) -lt $inputBytes.Length) -and ($inputBytes[$i + 1] -eq 10)) {
                    continue
                }
                $buffer.WriteByte($inputBytes[$i])
            }
            $restoredBytes = $buffer.ToArray()
        } finally {
            $buffer.Dispose()
        }
        $digest = [System.Security.Cryptography.SHA256]::Create()
        try {
            $candidateSHA = ([System.BitConverter]::ToString($digest.ComputeHash($restoredBytes))).Replace('-','').ToLowerInvariant()
        } finally {
            $digest.Dispose()
        }
        if ($candidateSHA -ne $s1SHA) {
            throw "S2_LF_RESTORATION_SHA_NOT_LOCKED_PRESERVE: $candidateSHA"
        }
        # Exclusive creation; old CRLF file is never modified or deleted.
        $stream = [System.IO.File]::Open($canonicalPath,[System.IO.FileMode]::CreateNew,[System.IO.FileAccess]::Write,[System.IO.FileShare]::None)
        try {
            $stream.Write($restoredBytes,0,$restoredBytes.Length)
            $stream.Flush($true)
        } finally {
            $stream.Dispose()
        }
    }
    $s1File = $canonicalPath
    $actualScoreSha = (Get-FileHash -LiteralPath $s1File -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualScoreSha -ne $s1SHA) {
        throw "S2_RESTORED_OR_EXISTING_S1_COPY_NOT_SHA_LOCKED_PRESERVE: $actualScoreSha"
    }
    Write-Host 'FRESH16_S1_LF_TRANSPORT_RECOVERY=PASS_EXACT_LOCKED_BYTES'
    Write-Host "FRESH16_S1_LOCKED_CANONICAL_PRIVATE=$s1File"
}
$actualMapSha = (Get-FileHash -LiteralPath $mapFile -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualMapSha -ne $mapSHA) { throw 'S2_MAP_SHA_DRIFT' }
$finished = Get-Content -LiteralPath $finishedFile -Raw -Encoding UTF8 | ConvertFrom-Json
if ($finished.original_outputs -ne 32 -or $finished.inference_executed -ne $true) { throw 'S2_CPU32_NOT_FINISHED' }
& git -C $wt fetch origin "refs/heads/$branch"
if ($LASTEXITCODE -ne 0) { throw 'S2_GIT_FETCH_FAILED' }
& git -C $wt cat-file -e ($s1Commit + ':' + $s1Rel)
if ($LASTEXITCODE -ne 0) { throw 'S2_S1_SHA_LOCK_COMMIT_MISSING' }
if ((& git -C $wt rev-parse HEAD).Trim() -ne $source) { throw 'S2_E0_HEAD_MOVED' }

# Frozen original packet gate checks S1 SHA and generates pairs with blinded checkpoint IDs.
& $py $gate --mode package-s2 --project-root $root --worktree $wt --run-dir $dir --expected-head $source --s1-scores $s1File --s1-anchor-commit $s1Commit
if ($LASTEXITCODE -ne 0) { throw 'S2_PACKET_GATE_FAILED_PRESERVE_EXISTING_FILES' }
if (-not (Test-Path -LiteralPath $s2File -PathType Leaf)) { throw 'S2_PACKET_NOT_CREATED' }
$packet = Get-Content -LiteralPath $s2File -Raw -Encoding UTF8 | ConvertFrom-Json
if ($packet.schema -ne 'ttm.fresh16.v2.s2_packet.v1' -or $packet.s1_score_file_sha256 -ne $s1SHA -or $packet.pairs.Count -ne 16) {
    throw 'S2_PACKET_SCHEMA_OR_COUNT_ERROR_PRESERVE'
}
$pairsUnique = @($packet.pairs | ForEach-Object { $_.opaque_pair_id } | Sort-Object -Unique)
$memberRows = @($packet.pairs | ForEach-Object { $_.members })
$memberIDs = @($memberRows | ForEach-Object { $_.opaque_id } | Sort-Object -Unique)
if ($pairsUnique.Count -ne 16 -or $memberRows.Count -ne 32 -or $memberIDs.Count -ne 32) {
    throw 'S2_PACKET_DUPLICATE_OR_MISSING_MEMBER_PRESERVE'
}
if (@($packet.pairs | Where-Object { $_.members.Count -ne 2 }).Count -ne 0) {
    throw 'S2_PACKET_MEMBER_COUNT_ERROR_PRESERVE'
}
foreach ($m in $memberRows) {
    $fields = @($m.PSObject.Properties.Name | Sort-Object)
    $allowed = @('generated_text_only','locked_s1_adherence_0_3','opaque_id','prompt_text')
    if (@(Compare-Object -ReferenceObject $allowed -DifferenceObject $fields).Count -ne 0) {
        throw 'S2_PACKET_MEMBER_FIELD_LEAK_PRESERVE'
    }
}
$actualPacketSha = (Get-FileHash -LiteralPath $s2File -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host 'FRESH16_S1_SCORE_SHA_LOCK=PASS'
Write-Host "FRESH16_S1_SCORE_SHA256=$actualScoreSha"
Write-Host 'FRESH16_S2_PACKET=PASS_16_BLIND_PAIRS'
Write-Host "FRESH16_S2_PACKET_SHA256=$actualPacketSha"
Write-Host "FRESH16_S2_PACKET_PRIVATE=$s2File"
Write-Host 'FRESH16_S2_SCORING=NOT_EXECUTED'
Write-Host 'FRESH16_UNBLIND=NO'
Write-Host 'FRESH16_INFERENCE_RERUN=FORBIDDEN'
