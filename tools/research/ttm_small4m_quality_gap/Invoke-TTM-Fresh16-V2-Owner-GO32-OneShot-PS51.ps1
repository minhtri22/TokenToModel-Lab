# TTM FRESH16 V2 - EXACTLY ONE owner GO CPU execution (no retry, no QA repetition).
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $root 'worktrees\ttm-fresh16-quality-20261111'
$branch = 'research/ttm-small4m-prompt-adherence-continuation-design-20261111'
$source = 'c05872354d892a9656f8f98642866f7eebfd0f50'
$goCommit = 'd123fbb8b41d53fe76ad1ff14d4ac4e8907c31ea'
$anchor = 'd95b09f894dd7ef975b375a794f50a1d7905e0d6'
$mapExpected = 'eb570460b1423bb4b2355ccb5b7b56862c641721d5ecf62f7136224b71ea20a8'
$runnerBlob = 'f069f2bdaa2d9691a1ce6c9746ff8f2923beb1d8'
$goRel = 'artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_GO_32_CPU_ONE_SHOT_OWNER_AUTHORIZED_20261111.json'
$anchorRel = 'artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_PRIVATE_MAP_SHA_ANCHOR.json'
$dir = Join-Path $root '_tmp\ttm_fresh16_v2_e0_20261111'
$preparedPath = Join-Path $dir 'PREPARED.json'
$mapPath = Join-Path $dir 'BLIND_MAP_PRIVATE.json'
$permitPath = Join-Path $dir 'GO_32_CPU_ONE_SHOT_OWNER_PERMIT.json'
$startedPath = Join-Path $dir 'RUN_STARTED.json'
$finishedPath = Join-Path $dir 'RUN_FINISHED.json'
$s1Path = Join-Path $dir 'S1_BLIND_PACKET_PRIVATE.json'
$rawPath = Join-Path $dir 'RAW_OUTPUTS_PRIVATE.jsonl'
$wrapper = Join-Path $wt 'tools\research\ttm_small4m_quality_gap\Invoke-TTM-Fresh16-V2-E0-PS51.ps1'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'

foreach ($p in @($root,$wt,$py,$wrapper,$preparedPath,$mapPath)) {
    if (-not (Test-Path -LiteralPath $p)) { throw "FRESH16_REQUIRED_FILE_MISSING: $p" }
}
foreach ($p in @($permitPath,$startedPath,$finishedPath,$s1Path,$rawPath)) {
    if (Test-Path -LiteralPath $p) { throw "FRESH16_ONE_SHOT_ALREADY_INITIALIZED_NO_RETRY: $p" }
}
$actualBranch = (& git -C $wt branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $actualBranch -ne $branch) { throw 'FRESH16_WRONG_BRANCH' }
$actualHead = (& git -C $wt rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualHead -ne $source) { throw 'FRESH16_SOURCE_HEAD_DRIFT_NO_SCIENCE' }
$dirty = @(& git -C $wt status --porcelain=v1 --untracked-files=all)
if ($LASTEXITCODE -ne 0 -or $dirty.Count -ne 0) { throw 'FRESH16_DIRTY_WORKTREE_NO_SCIENCE' }
$prep = Get-Content -LiteralPath $preparedPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($prep.source_head -ne $source -or $prep.runner_git_blob -ne $runnerBlob -or $prep.sealed_map_sha256 -ne $mapExpected -or $prep.inference_executed -ne $false) { throw 'FRESH16_PREPARED_DRIFT' }
$mapActual = (Get-FileHash -LiteralPath $mapPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($mapActual -ne $mapExpected) { throw 'FRESH16_MAP_SHA_DRIFT' }
Write-Host 'FRESH16_OWNER_GO=GRANTED_SINGLE_RUN'
Write-Host "FRESH16_SOURCE_HEAD=$actualHead"
Write-Host "FRESH16_MAP_SHA256=$mapActual"

# FETCH IS NOT MERGE; frozen local HEAD stays at E0 source, never follow newer branch tip.
& git -C $wt fetch origin "refs/heads/$branch"
if ($LASTEXITCODE -ne 0) { throw 'FRESH16_GO_FETCH_FAILED' }
& git -C $wt cat-file -e ($goCommit + '^{commit}')
if ($LASTEXITCODE -ne 0) { throw 'FRESH16_OWNER_GO_COMMIT_UNAVAILABLE' }
& git -C $wt cat-file -e ($anchor + ':' + $anchorRel)
if ($LASTEXITCODE -ne 0) { throw 'FRESH16_MAP_ANCHOR_COMMIT_UNAVAILABLE' }
$headAfter = (& git -C $wt rev-parse HEAD).Trim()
if ($headAfter -ne $source) { throw 'FRESH16_SOURCE_CHANGED_DURING_FETCH' }

# Copy exact Git-committed permit bytes (PowerShell 5.1 BOM/newlines do not intervene).
$pythonCode = @'
import hashlib, json, os, subprocess, sys
wt, commit, rel, dst, source, anchor, mapsha, runner = sys.argv[1:]
data = subprocess.check_output(["git", "-C", wt, "show", commit + ":" + rel])
obj = json.loads(data.decode("utf-8"))
if not (obj.get("decision") == "GO_32_CPU_ONE_SHOT"
        and obj.get("source_head") == source
        and obj.get("map_anchor_commit") == anchor
        and obj.get("sealed_map_sha256") == mapsha
        and obj.get("runner_git_blob") == runner
        and obj.get("S1_rater_session")
        and obj.get("S2_adjudicator_session")
        and obj["S1_rater_session"] != obj["S2_adjudicator_session"]):
    raise RuntimeError("OWNER_GO_FIELDS_MISMATCH")
with open(dst, "xb") as f:
    f.write(data)
    f.flush()
    os.fsync(f.fileno())
print("FRESH16_GO_PERMIT_SHA256=" + hashlib.sha256(data).hexdigest(), flush=True)
'@
# Windows PowerShell 5.1 mangles quotes in python.exe -c with multi-line code.
# Save exact UTF-8 Python source to a new project-local helper and run by filename.
# This change affects permit materialization only, never the pinned E0 science runner.
$helper = Join-Path $root '_tmp\ttm_fresh16_v2_go32_permit_materializer_20261111.py'
if (Test-Path -LiteralPath $helper) {
    throw 'FRESH16_GO_HELPER_ALREADY_EXISTS_PRESERVE_NO_OVERWRITE'
}
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
$helperBytes = $utf8NoBom.GetBytes($pythonCode + [Environment]::NewLine)
$helperStream = [System.IO.File]::Open($helper, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
try {
    $helperStream.Write($helperBytes, 0, $helperBytes.Length)
    $helperStream.Flush($true)
} finally {
    $helperStream.Dispose()
}
& $py $helper $wt $goCommit $goRel $permitPath $source $anchor $mapExpected $runnerBlob
if ($LASTEXITCODE -ne 0) { throw 'FRESH16_GO_PERMIT_MATERIALIZATION_HOLD' }
$permitSHA = (Get-FileHash -LiteralPath $permitPath -Algorithm SHA256).Hash.ToLowerInvariant()

# Execution writes RUN_STARTED before the first forward, with strict no-retry semantics.
Write-Host 'FRESH16_CPU32_ONE_SHOT=REQUESTED'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $wrapper -Mode Run -ExpectedHead $source -GoPermitPath $permitPath -GoPermitSHA256 $permitSHA -MapAnchorCommit $anchor
if ($LASTEXITCODE -ne 0) { throw "FRESH16_SCIENCE_STOP_PRESERVE_ALL_NO_RETRY_EXIT_$LASTEXITCODE" }
foreach ($p in @($startedPath,$finishedPath,$s1Path,$rawPath)) {
    if (-not (Test-Path -LiteralPath $p)) { throw "FRESH16_OUTPUT_MISSING_NO_RETRY: $p" }
}
$started = Get-Content -LiteralPath $startedPath -Raw -Encoding UTF8 | ConvertFrom-Json
$finished = Get-Content -LiteralPath $finishedPath -Raw -Encoding UTF8 | ConvertFrom-Json
$s1Packet = Get-Content -LiteralPath $s1Path -Raw -Encoding UTF8 | ConvertFrom-Json
$actualS1Sha = (Get-FileHash -LiteralPath $s1Path -Algorithm SHA256).Hash.ToLowerInvariant()
$actualRawSha = (Get-FileHash -LiteralPath $rawPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($started.permit_sha256 -ne $permitSHA -or $finished.original_outputs -ne 32 -or $s1Packet.records.Count -ne 32 -or $s1Packet.schema -ne 'ttm.fresh16.v2.s1_packet.v1') { throw 'FRESH16_RUN_COMPLETENESS_FAIL_NO_RETRY' }
if ($finished.S1_packet_sha256 -ne $actualS1Sha -or $finished.raw_outputs_sha256 -ne $actualRawSha) { throw 'FRESH16_FINAL_HASH_MISMATCH_NO_RETRY' }
$opaqueIds = @($s1Packet.records | ForEach-Object { $_.opaque_id } | Sort-Object -Unique)
if ($opaqueIds.Count -ne 32) { throw 'FRESH16_S1_OPAQUE_ID_DUPLICATE' }
Write-Host 'FRESH16_CPU32_RUN=PASS_ONE_SHOT_32_OUTPUTS'
Write-Host "FRESH16_RAW_OUTPUTS_SHA256=$actualRawSha"
Write-Host "FRESH16_S1_PACKET_SHA256=$actualS1Sha"
Write-Host "FRESH16_S1_PACKET_PRIVATE=$s1Path"
Write-Host 'FRESH16_S2_PACKET=NOT_YET_CREATED_AWAIT_S1_SHA_COMMIT'
Write-Host 'FRESH16_CHECKPOINT_UNBLIND=FORBIDDEN_UNTIL_S2_LOCK'
Write-Host 'FRESH16_RETRY=FORBIDDEN'
