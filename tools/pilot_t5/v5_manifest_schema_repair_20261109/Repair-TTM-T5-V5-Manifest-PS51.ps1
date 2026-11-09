param(
    [ValidateSet('PatchOnly','PatchAndSmoke')]
    [string]$Mode = 'PatchOnly'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# This repairs ONE manifest-schema literal in the already-extracted V5 wrapper.
# It neither edits scientific files nor modifies the consumed V1-V4 trials.
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$name = 'TTM_T5_OLLAMA_V5_TIMEWAIT_GUARD_20261109'
$source = Join-Path (Join-Path $root '_tmp') $name
$wrapper = Join-Path $source 'Invoke-TTM-T5-Timewait-V5-PS51.ps1'
$manifestPath = Join-Path $source 'SOURCE_SHA256_MANIFEST.json'
$zip = Join-Path $env:USERPROFILE ('Downloads\' + $name + '.zip')
$oneShot = Join-Path (Join-Path $root '_tmp') 'ttm_t5_ollama_compat_only_single_v5final'
$backup = $wrapper + '.original_sha856a61d3.bak'
$staging = $wrapper + '.schema_fix.tmp'

$zipExpected = '0c27593dd01c5e652709c03b6a0019533aa602e178d1e4251052bc69bf01ef33'
$manifestExpected = 'bc1bb30df9907c52df7e292b7a0c039d3c48b6944d122e0015f2131b378b53df'
$wrapperBefore = '856a61d364f14523dce2572cde3185542733c46cfb9aeedbfaf80e1b82d46fdb'
$wrapperAfter = '238570d7c98e228d351dbe9ebcd6992fb018ba482d9d0078008d4ab8a2c5c8ad'
$schemaBefore = 'ttm.t5.final.minimal.compat.one_shot.source.manifest.v1'
$schemaAfter = 'ttm.t5.v5.timewait_guard.one_shot.source.manifest.v1'

if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) { throw 'WRONG_PROJECT_ROOT' }
if (-not (Test-Path -LiteralPath $zip -PathType Leaf)) { throw 'ORIGINAL_V5_ZIP_MISSING' }
if (-not (Test-Path -LiteralPath $wrapper -PathType Leaf)) { throw 'V5_WRAPPER_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw 'V5_MANIFEST_NOT_FOUND' }
if (Test-Path -LiteralPath $oneShot) { throw 'V5_ONE_SHOT_ALREADY_CLAIMED_NO_REPAIR_OR_RERUN' }
if ((Test-Path -LiteralPath $backup) -or (Test-Path -LiteralPath $staging)) {
    throw 'PREVIOUS_SCHEMA_REPAIR_ATTEMPT_PRESENT_NO_OVERWRITE'
}
foreach ($p in @($root, (Join-Path $root '_tmp'), $source, $wrapper, $manifestPath, $zip)) {
    $item = Get-Item -LiteralPath $p -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw ('REPARSE_PATH_DENIED:' + $p)
    }
}
$origin = & git -C $root remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) { throw 'GIT_ORIGIN_UNAVAILABLE' }
$accepted = @('https://github.com/minhtri22/TokenToModel-Lab.git',
              'https://github.com/minhtri22/TokenToModel-Lab',
              'git@github.com:minhtri22/TokenToModel-Lab.git')
if ($accepted -cnotcontains ([string]$origin).Trim()) { throw 'WRONG_REPO_ORIGIN' }

function Assert-FileSha([string]$path, [string]$want, [string]$label) {
    $got = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($got -cne $want) { throw ('SHA256_MISMATCH_' + $label + ':' + $got) }
}
Assert-FileSha $zip $zipExpected 'ORIGINAL_ZIP'
Assert-FileSha $manifestPath $manifestExpected 'MANIFEST'
Assert-FileSha $wrapper $wrapperBefore 'ORIGINAL_WRAPPER'
$manifestObj = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifestObj.schema -cne $schemaAfter) { throw 'V5_MANIFEST_SCHEMA_NOT_EXPECTED' }
foreach ($entry in $manifestObj.source_files.PSObject.Properties) {
    if ($entry.Name -cnotmatch '^[A-Za-z0-9_.-]+$') { throw 'INVALID_SOURCE_FILENAME' }
    $file = Join-Path $source $entry.Name
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw ('SOURCE_FILE_MISSING:' + $entry.Name)
    }
    Assert-FileSha $file (([string]$entry.Value).ToLowerInvariant()) ('SOURCE_' + $entry.Name)
}
Write-Host 'T5_V5_SCHEMA_REPAIR_INPUT_SHA256=PASS'

$originalBytes = [System.IO.File]::ReadAllBytes($wrapper)
$text = [System.Text.Encoding]::UTF8.GetString($originalBytes)
if (([regex]::Matches($text,[regex]::Escape($schemaBefore))).Count -ne 1) {
    throw 'SCHEMA_REPAIR_OLD_OCCURRENCE_NOT_EXACTLY_ONE'
}
if ($text.Contains($schemaAfter)) { throw 'SCHEMA_REPAIR_NEW_SCHEMA_ALREADY_PRESENT' }
$patched = $text.Replace($schemaBefore,$schemaAfter)
$tokens = $null
$errorsFound = $null
[System.Management.Automation.Language.Parser]::ParseInput(
    $patched,[ref]$tokens,[ref]$errorsFound
) | Out-Null
if ($errorsFound.Count -gt 0) { throw 'REPAIRED_PS51_PARSE_FAILED' }
$patchedBytes = [System.Text.Encoding]::UTF8.GetBytes($patched)
[System.IO.File]::WriteAllBytes($staging,$patchedBytes)
Assert-FileSha $staging $wrapperAfter 'REPAIRED_STAGING'

# Atomic replacement: preserve original wrapper as an exact-byte backup.
[System.IO.File]::Replace($staging,$wrapper,$backup)
Assert-FileSha $wrapper $wrapperAfter 'REPAIRED_WRAPPER'
Assert-FileSha $backup $wrapperBefore 'BACKUP_ORIGINAL'
Assert-FileSha $manifestPath $manifestExpected 'MANIFEST_POST'
if (Test-Path -LiteralPath $oneShot) { throw 'UNEXPECTED_V5_CLAIM_AFTER_PATCH' }
Write-Host 'T5_V5_SCHEMA_REPAIR=PASS_ONE_LITERAL_ONLY'
Write-Host ('T5_V5_PATCHED_WRAPPER_SHA256=' + $wrapperAfter)
Write-Host 'T5_V5_ORIGINAL_WRAPPER_BACKUP=PASS'
Write-Host 'T5_V5_MANIFEST_AND_RUNTIME_SOURCE=UNCHANGED'
Write-Host 'T5_V5_OLLAMA_RUNTIME=NOT_EXECUTED_BY_PATCH'
if ($Mode -eq 'PatchOnly') { exit 0 }

# This explicit mode continues the same previously-authorized V5 one-shot.
# The wrapper runs SHA checks, 47 mock tests, preview, then (only on PASS) Smoke.
if (Test-Path -LiteralPath $oneShot) { throw 'V5_CLAIM_EXISTS_NO_EXECUTION' }
Write-Host 'T5_V5_PATCHED_WRAPPER_SMOKE=START_IF_PREFLIGHT_PASSES'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $wrapper -Mode Smoke
$rc = $LASTEXITCODE
Write-Host ('T5_V5_PATCHED_WRAPPER_EXIT=' + $rc)
Write-Host 'T5_V5_NO_AUTOMATIC_RERUN=TRUE'
exit $rc
