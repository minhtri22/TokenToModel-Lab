#requires -Version 5.1
$ErrorActionPreference = 'Stop'
$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$Runner = Join-Path $Root '_tmp\TTM_D1_EXPLORATORY_DEV32_ONE_SHOT_20261112.py'
$ExpectedBlob = '4f7dddd52833362a52068527a3db78c2b0845578'
$Out = Join-Path $Root '_tmp\TTM_D1_EXPLORATORY_DEV32_ONE_SHOT_20261112'
$Owner = Join-Path $Out 'D1_EXP32_OWNER_PRIVATE_RAW.json'
$Blind = Join-Path $Out 'D1_EXP32_BLIND64_PRIVATE.json'
$Safe = Join-Path $Out 'D1_EXP32_SAFE_SUMMARY.json'

function Check-Hash([string]$File,[string]$Expected) {
    if (-not (Test-Path -LiteralPath $File -PathType Leaf)) { throw "MISSING_$([IO.Path]::GetFileName($File))" }
    $actual = (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -cne $Expected) { throw "SHA_MISMATCH_$([IO.Path]::GetFileName($File))" }
}

if (-not (Test-Path -LiteralPath $Py -PathType Leaf)) { throw 'PYTHON312_MISSING' }
if (-not (Test-Path -LiteralPath $Runner -PathType Leaf)) { throw 'DEV32_RUNNER_MISSING' }
$Version = (& $Py --version 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $Version -notmatch '^Python 3\.12\.') { throw 'PYTHON_312_REQUIRED' }
# Native Git blob SHA1 avoids Windows PowerShell Python -c argument quoting.
$source = [IO.File]::ReadAllText($Runner,[Text.Encoding]::UTF8)
$lf = [string][char]10
$source = $source.Replace((([string][char]13)+$lf),$lf)
if (-not $source.EndsWith($lf)) { $source += $lf }
[byte[]]$raw = [Text.Encoding]::UTF8.GetBytes($source)
[byte[]]$head = [Text.Encoding]::ASCII.GetBytes("blob $($raw.Length)")
[byte[]]$joined = [byte[]]::new($head.Length + 1 + $raw.Length)
[Array]::Copy($head,0,$joined,0,$head.Length)
$joined[$head.Length] = [byte]0
[Array]::Copy($raw,0,$joined,$head.Length+1,$raw.Length)
$algo = [Security.Cryptography.SHA1]::Create()
try { $blob = ([BitConverter]::ToString($algo.ComputeHash($joined))).Replace('-','').ToLowerInvariant() }
finally { $algo.Dispose() }
if ($blob -cne $ExpectedBlob) { throw 'DEV32_RUNNER_GIT_BLOB_MISMATCH' }
Write-Host "TTM_D1_DEV32_RUNNER_BLOB=$blob"
Check-Hash (Join-Path $Root '_tmp\TTM_SMALL4M_D1_NEW_DEV_PRIVATE_V2_20261111.json') 'f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8'
Check-Hash (Join-Path $Root '_tmp\CF1_STEP1024_PINNED.pt') 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
Check-Hash (Join-Path $Root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json') 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
Write-Host 'TTM_D1_DEV32_FROZEN_SOURCES=PASS'
$os = Get-CimInstance Win32_OperatingSystem
$freeGiB = [math]::Round(([double]$os.FreePhysicalMemory*1024 / 1GB), 3)
if ($freeGiB -lt 8) { throw ("MEMORY_BELOW_FROZEN_FLOOR_GIB=" + $freeGiB) }
Write-Host "TTM_D1_DEV32_AVAILABLE_GIB=$freeGiB"

if ((Test-Path -LiteralPath $Owner -PathType Leaf) -and
    (Test-Path -LiteralPath $Blind -PathType Leaf) -and
    (Test-Path -LiteralPath $Safe -PathType Leaf)) {
    Write-Host 'TTM_D1_DEV32=EXISTING_READBACK_ONLY'
} elseif (Test-Path -LiteralPath $Out) {
    throw 'DEV32_PARTIAL_OUTPUT_NO_RERUN'
} else {
    & $Py $Runner
    if ($LASTEXITCODE -ne 0) { throw 'DEV32_CPU_EXPLORATORY_FAILED' }
}
foreach ($f in @($Owner,$Blind,$Safe)) {
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { throw 'DEV32_OUTPUT_INCOMPLETE' }
}
$report = Get-Content -LiteralPath $Safe -Raw -Encoding UTF8 | ConvertFrom-Json
if ($report.schema -cne 'ttm.d1.exploratory_dev32.safe_summary.v1' -or
    $report.status -cne 'EXECUTED_EXPLORATORY_DEV_ONLY_NOT_ADJUDICATED' -or
    $report.selected_prompt_count -ne 32 -or
    $report.neutral_prompt_count -ne 16 -or
    $report.teacher_forced.teacher_forced_candidate_calls -ne 96 -or
    $report.blind_texts_generated -ne 64 -or
    $report.rollout.GREEDY.count -ne 32 -or
    $report.rollout.NUCLEUS.count -ne 32 -or
    $report.no_new_train_steps -ne $true -or
    $report.GPU_calls -ne 0 -or
    $report.TEST_Q1Q2_access -cne 'NONE') { throw 'DEV32_SAFE_REPORT_INVALID' }
$ownerSha = (Get-FileHash -LiteralPath $Owner -Algorithm SHA256).Hash.ToLowerInvariant()
$blindSha = (Get-FileHash -LiteralPath $Blind -Algorithm SHA256).Hash.ToLowerInvariant()
if ($ownerSha -cne $report.raw_owner_sha256 -or $blindSha -cne $report.blind_packet_sha256) { throw 'DEV32_LOCK_SHA_MISMATCH' }
$safeSha = (Get-FileHash -LiteralPath $Safe -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host 'TTM_D1_DEV32_CPU_EXPLORATORY=PASS_EXECUTED_SCOPED'
Write-Host 'D1_DEV32_TEACHER_FORCED=96 D1_DEV32_GENERATED=64'
Write-Host "D1_DEV32_OWNER_RAW_SHA256=$ownerSha"
Write-Host "D1_DEV32_BLIND64_SHA256=$blindSha"
Write-Host "D1_DEV32_SAFE_SHA256=$safeSha"
Write-Host "D1_DEV32_SWITCH_FAMILIES=$($report.teacher_forced.both_positive_family_count)"
Write-Host "D1_DEV32_SWITCH_ADJUSTED_FAMILIES=$($report.teacher_forced.both_positive_prior_adjusted_family_count)"
Write-Host "D1_DEV32_GREEDY_EOS=$($report.rollout.GREEDY.eos_early_count)"
Write-Host "D1_DEV32_NUCLEUS_EOS=$($report.rollout.NUCLEUS.eos_early_count)"
Write-Host "D1_DEV32_SAFE_REPORT=$Safe"
Write-Host "D1_DEV32_BLIND64_PRIVATE=$Blind"
Write-Host 'D1_DEV32_TRAINING=NO D1_DEV32_TEST_Q1Q2=SEALED D1_CONFIRMATORY_512=HOLD'
