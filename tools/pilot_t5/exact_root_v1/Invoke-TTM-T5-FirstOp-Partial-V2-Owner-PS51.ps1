[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[a-f0-9]{40}$')]
    [string] $ExpectedCommit,
    [string] $ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string] $Python312 = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if ($PSVersionTable.PSVersion.Major -ne 5) {
    throw 'POWERSHELL_51_REQUIRED'
}
if (-not (Test-Path -LiteralPath $Python312 -PathType Leaf)) {
    throw 'PYTHON312_NOT_FOUND'
}
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$expectedProject = 'D:\WORK\RESEARCH\TokenToModel-Lab'
if ($ProjectRoot.TrimEnd('\') -ine $expectedProject.TrimEnd('\')) {
    throw 'NOT_EXACT_TTM_WORKSPACE'
}

$gitExe = (Get-Command -Name git.exe -CommandType Application -ErrorAction Stop).Source
$oldStage = Join-Path $ProjectRoot '_tmp\ttm_t5_exact_root_discovery_run_v1_20261110'
$oldReceipt = Join-Path $oldStage 'DISCOVERY_RUN_RECEIPT.json'
$newReceiptDir = Join-Path $ProjectRoot '_tmp\ttm_t5_exact_root_discovery_recovery_v2_20261110'
$srcStage = Join-Path $ProjectRoot '_tmp\ttm_t5_exact_root_v2_source_package_20261110'

if (-not (Test-Path -LiteralPath $oldReceipt -PathType Leaf)) {
    throw 'ORIGINAL_FAILED_RECEIPT_NOT_FOUND'
}
$oldSHA = (Get-FileHash -LiteralPath $oldReceipt -Algorithm SHA256).Hash.ToLowerInvariant()
if ($oldSHA -ne 'e2cbc797e133a7e4fc4d949293dd9bd847b881e18b39f3c72bcfa9debfbc8e96') {
    throw 'ORIGINAL_RECEIPT_SHA_CHANGED'
}
if ((Test-Path -LiteralPath $newReceiptDir) -or (Test-Path -LiteralPath $srcStage)) {
    throw 'V2_ALREADY_ATTEMPTED_OR_PARTIAL_NO_RETRY_NO_OVERWRITE'
}
& $Python312 -c 'import sys; assert sys.version_info[:2] == (3, 12)'
if ($LASTEXITCODE -ne 0) { throw 'NOT_PYTHON312' }

# Only project-local downloads and proof. No re-run of the original binary.
New-Item -ItemType Directory -Path $srcStage -ErrorAction Stop | Out-Null
$bProbe = Join-Path $srcStage 'gelu_erf_probe'
New-Item -ItemType Directory -Path $bProbe -ErrorAction Stop | Out-Null

function Get-TTMExactSource {
    param(
        [Parameter(Mandatory=$true)][string] $RelativePath,
        [Parameter(Mandatory=$true)][string] $TargetFile,
        [Parameter(Mandatory=$true)][string] $ExpectedBlob
    )
    if (Test-Path -LiteralPath $TargetFile) {
        throw "DO_NOT_OVERWRITE_EXISTING_SOURCE:$TargetFile"
    }
    $url = "https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/$ExpectedCommit/$RelativePath"
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $TargetFile -ErrorAction Stop
    $sha = (& $gitExe -C $ProjectRoot hash-object $TargetFile).Trim()
    if ($LASTEXITCODE -ne 0 -or $sha -ne $ExpectedBlob) {
        throw "GITHUB_EXACT_SOURCE_BLOB_MISMATCH:$RelativePath"
    }
    Write-Host "SOURCE_BLOB_PASS=$RelativePath"
}

$base = 'tools/pilot_t5/exact_root_v1'
$auditor = Join-Path $srcStage 'independent_firstop_signed_tensor_audit_v2.py'
$test = Join-Path $srcStage 'test_firstop_v2_shape_recovery.py'
$runner = Join-Path $srcStage 'recover_partial_discovery_audit_and_gelu_erf_once.py'
$cpp = Join-Path $bProbe 'ttm_t5_firstop_trace_probe.cpp'
$cmake = Join-Path $bProbe 'CMakeLists.txt'

Get-TTMExactSource -RelativePath "$base/independent_firstop_signed_tensor_audit_v2.py" -TargetFile $auditor -ExpectedBlob 'c523c470f8ec69b4938992f44b16a4127c3d08ae'
Get-TTMExactSource -RelativePath "$base/test_firstop_v2_shape_recovery.py" -TargetFile $test -ExpectedBlob '4b93a12784647701b578309bd925c04bc61c2674'
Get-TTMExactSource -RelativePath "$base/gelu_erf_probe/ttm_t5_firstop_trace_probe.cpp" -TargetFile $cpp -ExpectedBlob 'bd7d408885703a80055c2baf296a44f3006462b7'
Get-TTMExactSource -RelativePath "$base/gelu_erf_probe/CMakeLists.txt" -TargetFile $cmake -ExpectedBlob '066fef8e2a248efcaf25c71443bebd13cfb27be6'
Get-TTMExactSource -RelativePath "$base/recover_partial_discovery_audit_and_gelu_erf_once.py" -TargetFile $runner -ExpectedBlob '34bfcf1d1ca0803bfd9b05beafd5214dc7ad8fe9'

$env:PYTHONDONTWRITEBYTECODE = '1'
# py_compile is native PS5.1-safe, and any __pycache__ stays in TTM _tmp.
& $Python312 -m py_compile $auditor $test $runner
if ($LASTEXITCODE -ne 0) {
    throw 'PYTHON312_STATIC_PARSE_FAILED_NO_NATIVE'
}

Write-Host 'OWNER_SCOPE=ALREADY_APPROVED_INTEGRATED_D01_D02'
Write-Host 'ORIGINAL_STAGE=HOLD_AND_NATIVE_A_IMMUTABLE'
Write-Host 'V2_SOURCE_AND_PARSER=PASS'
Write-Host 'RECOVERY_V2=START_AUDIT_SAVED_A_THEN_ONLY_UNRUN_B'

& $Python312 -B $runner --project-root $ProjectRoot --auditor-v2 $auditor --test-v2 $test --b-probe-source $bProbe --approve-recovery-scope 'I_APPROVE_RESUME_ONLY_TTM_T5_UNRUN_GELU_ERF_D01_D02'

if ($LASTEXITCODE -ne 0) {
    Write-Warning 'RECOVERY_V2_HOLD_NO_RETRY: Preserve original stage, new package, evidence and logs.'
}
