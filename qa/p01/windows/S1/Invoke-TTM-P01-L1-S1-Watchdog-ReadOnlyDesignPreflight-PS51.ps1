#requires -Version 5.1
# TTM P01 L1 S1 — read-only watchdog design preflight.
# NO child launch, no C# compilation, no SCM mutations, no marker creation.
[CmdletBinding()]
param([ValidateSet('ReadOnlyPreflight')][string]$Mode = 'ReadOnlyPreflight')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$project = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$original = Join-Path $project 'worktrees\p01-f0-static-i0a-20261105'
$stage = Join-Path $project 'worktrees\_ttm_p01_l1_service_provision_20261106'
$receipts = Join-Path $project 'worktrees\_ttm_p01_l1_qa_receipts'
$originalHead = 'f2e333df2f9ca24a8e483507c3cfc386ad9c76f0'
$expectedOrigin = 'https://github.com/minhtri22/TokenToModel-Lab.git'
$expectedBranch = 'implementation/p01-i0a-s-f0-static-20261106'
$serviceImage = Join-Path $stage 'broker_service\TTMP01Broker.attestationV2.exe'
$smokeExe = Join-Path $stage 'broker_service\TTMS1IsolatedCancellationHarness.exe'

$sourceRef = '3add36f538c6fe39658ea72d91034b8c8a5f666a'
$harnessPath = 'qa/p01/windows/S1/TTMS1IsolatedCancellationHarness.cs'
$harnessBlob = '872c67174c6fbbcea9941fe3bfa0acee3cddfb7c'
$harnessSha = 'fd179c74fa1a136d791a5f9f6394ea657c58e7a46d1983c0eafa81051e99d6a9'
$qaRef = 'f61af1431ff41c3588657b57828d7928a30c2832'
$qaPath = 'artifacts/qa/p01/L1_S1_WINDOWS_INDEPENDENT_SOURCE_QA_V3_20261107T034902580Z_81c28d5c.json'
$qaBlob = '673d12839b3821820732361b43540ccc5c748ffc'
$qaSha = '52f5f8c896a5306b3f5e3fd4b85b3763a97a193273c49dbe809e5a065efe5c33'

$expectedMarkers = @(
 @{ Path = (Join-Path $stage 'L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_ATTEMPT_20261107.lock');
    Sha = 'd39f4cd82c48c0401d48089c961f353663955671135c1e76ede06334b0b0f877' },
 @{ Path = (Join-Path $stage 'L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_V2_ATTEMPT_20261107.lock');
    Sha = '506425d4fcd9e82fc0aa2d6c0056e0dda69f03a7ebbf270e43c97d3ddb2215d0' },
 @{ Path = (Join-Path $stage 'L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_V3_ATTEMPT_20261107.lock');
    Sha = 'c923fa283a3737bcdb2dcefed2c384899187cee532c8d580a589e0c7fda7d4ea' }
)
$binaryPins = @(
 @{ Path = (Join-Path $stage 'broker_service\TTMP01Broker.attestationV3.exe');
    Sha = '0751f89fee519367580e89b2e99b5347ee49c6b4c15f67ebf7d43706ac78ec5c' },
 @{ Path = (Join-Path $stage 'broker_service\TTMWorkerNativeProbeV4.dll');
    Sha = 'b36b5868b09b4da7bdb7198f3acd86923aba57f29a993fc8188bcb1cdc729f36' }
)

function Block([string]$reason) { throw ('TTM_S1_WATCHDOG_PREFLIGHT_BLOCK=' + $reason) }
function Reject-Reparse([string]$path) {
 $current = $path
 while ($current) {
   if (Test-Path -LiteralPath $current) {
     $entry = Get-Item -LiteralPath $current -Force
     if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
       Block ('REPARSE_PATH_' + $current)
     }
   }
   $next = Split-Path -Parent $current
   if ([string]::IsNullOrEmpty($next) -or $next -eq $current) { break }
   $current = $next
 }
}
function Sha-File([string]$path) {
 if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { Block ('MISSING_' + $path) }
 Reject-Reparse $path
 return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Sha-Bytes([byte[]]$bytes) {
 $hash = [Security.Cryptography.SHA256]::Create()
 try { return ([BitConverter]::ToString($hash.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant() }
 finally { $hash.Dispose() }
}
function Read-GitHub-Pin([string]$path,[string]$ref,[string]$blob,[string]$sha) {
 $uri = 'repos/minhtri22/TokenToModel-Lab/contents/' + $path + '?ref=' + $ref
 $raw = & gh.exe api $uri
 if ($LASTEXITCODE -ne 0) { Block ('GITHUB_FETCH_' + $path) }
 $result = $raw | ConvertFrom-Json
 if ($result.sha -cne $blob) { Block ('GITHUB_GIT_BLOB_' + $path) }
 $bytes = [Convert]::FromBase64String(($result.content -replace '\s', ''))
 if ((Sha-Bytes $bytes) -cne $sha) { Block ('GITHUB_SHA256_' + $path) }
 return [Text.Encoding]::UTF8.GetString($bytes)
}
function Check-Service {
 $s = Get-CimInstance Win32_Service -Filter "Name='TTMP01Broker'"
 if ($null -eq $s) { Block 'SERVICE_NOT_FOUND' }
 $image = $s.PathName.Trim().Trim([char]34).Trim()
 if ($s.State -cne 'Stopped' -or [int]$s.ProcessId -ne 0 -or
     $s.StartMode -cne 'Manual' -or
     $s.StartName -ine 'NT AUTHORITY\LocalService' -or
     $image -ine $serviceImage) { Block 'SERVICE_NOT_FROZEN_V2_STOPPED_PID0' }
 Write-Host 'TTM_S1_WATCHDOG_SCM=PASS_STOPPED_PID0_READONLY'
}

if ($Mode -cne 'ReadOnlyPreflight') { Block 'MODE_FORBIDDEN' }
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { Block 'WINDOWS_REQUIRED' }
foreach ($p in @($project,$original,$stage,$receipts,$smokeExe)) { Reject-Reparse $p }
if (-not (Test-Path -LiteralPath $original -PathType Container)) { Block 'ORIGINAL_WORKTREE_MISSING' }
if (-not (Test-Path -LiteralPath $stage -PathType Container)) { Block 'STAGE_MISSING' }
if (Test-Path -LiteralPath $smokeExe) { Block 'S1_NATIVE_BINARY_ALREADY_MATERIALIZED' }
$head = & git.exe -C $original rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $head.Trim() -cne $originalHead) { Block 'ORIGINAL_HEAD_MISMATCH' }
$branch = & git.exe -C $original branch --show-current
if ($LASTEXITCODE -ne 0 -or $branch.Trim() -cne $expectedBranch) { Block 'ORIGINAL_BRANCH_MISMATCH' }
$origin = & git.exe -C $original remote get-url origin
if ($LASTEXITCODE -ne 0 -or $origin.Trim() -cne $expectedOrigin) { Block 'ORIGINAL_REMOTE_MISMATCH' }
Write-Host 'TTM_S1_WATCHDOG_ORIGINAL=PASS_EXACT_READONLY'
Check-Service

foreach ($m in $expectedMarkers) {
 if ((Sha-File $m.Path) -cne $m.Sha) { Block 'HISTORICAL_S1_MARKER_MISMATCH' }
}
Write-Host 'TTM_S1_WATCHDOG_V1_V2_V3_MARKERS=PASS_EXACT_PRESERVED'

foreach ($binary in $binaryPins) {
 if ((Sha-File $binary.Path) -cne $binary.Sha) { Block 'BROKER_OR_WORKER_BINARY_PIN_MISMATCH' }
}
Write-Host 'TTM_S1_WATCHDOG_BROKER_WORKER_BINARY_PINS=PASS_EXACT_READONLY'

$harness = Read-GitHub-Pin $harnessPath $sourceRef $harnessBlob $harnessSha
if ($harness -notlike '*TTM_P01_S1_ISOLATED_*' -or
    $harness -notlike '*CancelIoEx*') { Block 'HARNESS_SOURCE_CONTRACT_MISMATCH' }
Write-Host 'TTM_S1_WATCHDOG_HARNESS_SOURCE=PASS_EXACT_READONLY'

$qa = Read-GitHub-Pin $qaPath $qaRef $qaBlob $qaSha | ConvertFrom-Json
if ($qa.verdict -cne 'BLOCK_WINDOWS_S1_SOURCE_QA' -or
    $qa.python_checker.exit_code -ne 0 -or
    $qa.python_checker.verdict -cne 'PASS_SOURCE_STATIC_NO_NATIVE' -or
    $qa.python_checker.positive_passed -ne 41 -or
    $qa.python_checker.negative_rejected -ne 16 -or
    $qa.s1_native_execution -cne 'NOT_EXECUTED' -or
    $qa.service_action -cne 'NONE') { Block 'V3_PYTHON_QA_EVIDENCE_MISMATCH' }
Write-Host 'TTM_S1_WATCHDOG_PYTHON_V3=PASS_REUSED_EVIDENCE_NO_RERUN'
Check-Service

$os = Get-CimInstance Win32_OperatingSystem
$freeRamBytes = [int64]$os.FreePhysicalMemory * 1024
$drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($stage).Substring(0,1))
if ($freeRamBytes -lt 2147483648 -or [int64]$drive.Free -lt 1073741824) {
 Block 'RESOURCE_PREFLIGHT_RAM_2GIB_DISK_1GIB'
}
Write-Host 'TTM_S1_WATCHDOG_RESOURCES=PASS_DESIGN_PREFLIGHT_ONLY'
Write-Host 'TTM_S1_WATCHDOG_SOURCE_GATE=PASS_READONLY'
Write-Host 'TTM_S1_WATCHDOG_PERMIT=NOT_ISSUED'
Write-Host 'TTM_S1_WATCHDOG_JOB_OBJECT=NOT_IMPLEMENTED'
Write-Host 'TTM_S1_WATCHDOG_NATIVE_BINARY=NOT_COMPILED'
Write-Host 'TTM_S1_WATCHDOG_EXECUTION=NOT_AUTHORIZED'
Write-Host 'TTM_S1_WATCHDOG_SCM_ACTION=NONE'
Write-Host 'TTM_S1_WATCHDOG_VERDICT=PASS_READONLY_DESIGN_PREFLIGHT_NO_NATIVE'
