#Requires -Version 5.1
<#
G1: read-only verification of the ORIGINAL TTM T1 split manifest.
No writes, no source story read, no model load, no training, no TEST access beyond
hash-only membership metadata already present in the original T1 manifest.
The 128/64/64 G1 prefix manifest is NOT created by this verification.
#>
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$manifestRel = '_tmp\ttm_t1_real_source_v1\T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json'
$manifest = Join-Path $root $manifestRel
$expectedManifest = '9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
$expectedTrain = 'c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f'
$expectedValid = '94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4'
$expectedRev = 'f54c09fd23315a6f9c86f9dc80f725de7d8f9c64'

if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) { throw 'STOP_PROJECT_GIT_MISSING' }
$originOutput = & git -C $root remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) { throw 'STOP_GIT_ORIGIN_UNKNOWN' }
$origin = ([string]($originOutput | Select-Object -First 1)).Trim().ToLowerInvariant()
$allowed = @(
  'https://github.com/minhtri22/tokentomodel-lab',
  'https://github.com/minhtri22/tokentomodel-lab.git',
  'git@github.com:minhtri22/tokentomodel-lab',
  'git@github.com:minhtri22/tokentomodel-lab.git'
)
if ($allowed -notcontains $origin) { throw 'STOP_GIT_ORIGIN_MISMATCH' }

$pathsToVerify = @(
  $root,
  (Join-Path $root '_tmp'),
  (Join-Path $root '_tmp\ttm_t1_real_source_v1'),
  $manifest
)
foreach ($p in $pathsToVerify) {
  if (-not (Test-Path -LiteralPath $p)) { throw ('STOP_REQUIRED_PATH_MISSING:' + $p) }
  $info = Get-Item -LiteralPath $p -Force
  if (($info.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw ('STOP_REPARSE_POINT:' + $p)
  }
}
$size = (Get-Item -LiteralPath $manifest).Length
$actualSha = (Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actualSha -ne $expectedManifest) {
  throw ('STOP_T1_MANIFEST_SHA256_MISMATCH actual=' + $actualSha)
}

$utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)
$payload = [IO.File]::ReadAllText($manifest, $utf8Strict)
$d = ConvertFrom-Json -InputObject $payload
if ($d.schema -ne 'ttm.t1.real.stories.split.v1') { throw 'STOP_T1_SCHEMA_MISMATCH' }
if ($d.repo -ne 'roneneldan/TinyStories') { throw 'STOP_T1_REPO_MISMATCH' }
if ($d.revision -ne $expectedRev) { throw 'STOP_T1_REVISION_MISMATCH' }
if ($d.license -ne 'CDLA-Sharing-1.0') { throw 'STOP_T1_LICENSE_MISMATCH' }
if ($d.source_sha256.'TinyStories-train.txt' -ne $expectedTrain) {
  throw 'STOP_T1_ORIGINAL_TRAIN_HASH_FIELD_MISMATCH'
}
if ($d.source_sha256.'TinyStories-valid.txt' -ne $expectedValid) {
  throw 'STOP_T1_ORIGINAL_VALID_HASH_FIELD_MISMATCH'
}
if ($d.negative_privileged_access -ne 'NO_TEST_READ_FOR_TOKENIZER_FIT') {
  throw 'STOP_T1_PRIVILEGED_ACCESS_FIELD_MISMATCH'
}
$counts = @{TRAIN=2048; VAL=256; TEST=64}
$seen = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($split in @('TRAIN','VAL','TEST')) {
  $rows = @($d.splits.$split)
  if ($rows.Count -ne $counts[$split]) {
    throw ('STOP_T1_SPLIT_COUNT_' + $split + ':' + $rows.Count)
  }
  foreach ($id in $rows) {
    $str = [string]$id
    if ($str -cnotmatch '^[0-9a-f]{64}$') { throw 'STOP_T1_INVALID_ID_FORMAT' }
    if (-not $seen.Add($str)) { throw 'STOP_T1_CROSS_SPLIT_OR_INTERNAL_DUPLICATE' }
  }
}
if ($seen.Count -ne 2368) { throw 'STOP_T1_TOTAL_UNIQUE_IDS' }

$result = [ordered]@{
  schema = 'ttm.six.g1.t1_original_manifest_readonly_qa.v1'
  status = 'PASS_T1_ORIGINAL_MANIFEST_BYTES_AND_2368_IDS'
  manifest_sha256 = $actualSha
  manifest_size_bytes = [int64]$size
  source_revision = $expectedRev
  train_count = 2048
  val_count = 256
  test_count = 64
  unique_ids = $seen.Count
  g1_prefix_manifest_status = 'NOT_GENERATED'
  qwen17_smoke_status = 'NOT_EXECUTED_BY_THIS_SCRIPT'
  source_raw_story_bytes_read = $false
  ttm_train_val_test_story_text_read = $false
  writes_performed = $false
  science_executed = $false
  decision = 'T1_ORIGINAL_BYTES_PASS_DOES_NOT_GRANT_G1_SCIENCE'
}
Write-Output ($result | ConvertTo-Json -Depth 6 -Compress)
