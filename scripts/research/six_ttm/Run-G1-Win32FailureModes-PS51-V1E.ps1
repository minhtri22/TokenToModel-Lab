# TTM x SIX G1: exactly TWO previously untested Win32 failure-path modes.
# Harmless suspended Python child only. NO G1 TEST/Qwen/GPU/ACL changes.
# All files and logs must remain inside D:\WORK\RESEARCH\TokenToModel-Lab\_tmp.
param(
    [string]$SourcePath = 'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\g1_win32_job_failure_path_v1e_candidate.py'
)
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$tmp = Join-Path $root '_tmp'
$PythonExe = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$ExpectedSourceSHA = 'eb5d1b71a991eb4ca46d801057806e2a580c6bcd2487080bfe3e2c15a6008309'
if ($PSVersionTable.PSVersion.Major -ne 5) { throw 'STOP_G1_REQUIRES_POWERSHELL_51' }
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'STOP_G1_PROJECT_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $tmp -PathType Container)) { throw 'STOP_G1_TMP_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) { throw 'STOP_G1_PYTHON312_NOT_FOUND' }
$rootReal = [IO.Path]::GetFullPath($root).TrimEnd('\')
$srcReal = [IO.Path]::GetFullPath($SourcePath)
if (-not $srcReal.StartsWith(($rootReal + '\_tmp\'),[StringComparison]::OrdinalIgnoreCase)) {
    throw 'STOP_G1_SOURCE_OUTSIDE_PROJECT_TMP'
}
if (-not (Test-Path -LiteralPath $srcReal -PathType Leaf)) { throw 'STOP_G1_SOURCE_MISSING' }
if ((Get-Item -LiteralPath $srcReal).Attributes -band [IO.FileAttributes]::ReparsePoint) {
    throw 'STOP_G1_SOURCE_REPARSE'
}
$sourceSHA = (Get-FileHash -LiteralPath $srcReal -Algorithm SHA256).Hash.ToLowerInvariant()
if ($sourceSHA -cne $ExpectedSourceSHA) { throw 'STOP_G1_SOURCE_SHA256_MISMATCH' }
$version = & $PythonExe -B -c 'import sys;print(sys.version_info.major,sys.version_info.minor,sep=chr(46))'
if ($LASTEXITCODE -ne 0 -or $version.Trim() -cne '3.12') { throw 'STOP_G1_PYTHON_NOT_312' }
$id = [Guid]::NewGuid().ToString('N').Substring(0,12)
$qaDir = Join-Path $tmp ('G1_WIN32_FAILURE_MODES_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + $id)
if (Test-Path -LiteralPath $qaDir) { throw 'STOP_G1_QA_DIR_ALREADY_EXISTS' }
New-Item -ItemType Directory -Path $qaDir -ErrorAction Stop | Out-Null
$result = [ordered]@{
    schema = 'ttm.six.g1.win32_failure_path_owner_qa.v1e'
    status = 'STOP_NOT_COMPLETED'
    qa_dir = $qaDir
    source_sha256 = $sourceSHA
    python_version = $version.Trim()
    tests = @()
    science_executed = $false
    g1_private_test_opened = $false
    owner_science_permit = 'NOT_ISSUED'
    science_lock = 'HOLD'
}
try {
    foreach ($mode in @('harmless-assign-fault-qa','harmless-resume-fault-qa')) {
        $outLog = Join-Path $qaDir ($mode + '.log')
        $errLog = Join-Path $qaDir ($mode + '.stderr.log')
        & $PythonExe -B $srcReal --mode $mode --sleep-seconds 8 --timeout-ms 200 1> $outLog 2> $errLog
        if ($LASTEXITCODE -ne 0) { throw ('STOP_G1_CHILD_TEST_FAILED_' + $mode) }
        $ob = Get-Content -LiteralPath $outLog -Raw | ConvertFrom-Json
        if ($ob.test -cne 'HARMLESS_FAULT_INJECTION' -or
            $ob.cleanup_verified -ne $true -or
            $ob.child_exited -ne $true -or
            $ob.production_qualified -ne $false -or
            $ob.real_gpu_used -ne $false -or
            $ob.science_executed -ne $false) {
            throw ('STOP_G1_CHILD_CLEANUP_NOT_PROVEN_' + $mode)
        }
        $result.tests += [ordered]@{
            mode = $mode
            conclusion = 'PASS_HARMLESS_OWNED_CHILD_REAP_ONLY'
            stdout_sha256 = (Get-FileHash -LiteralPath $outLog -Algorithm SHA256).Hash.ToLowerInvariant()
            stderr_sha256 = (Get-FileHash -LiteralPath $errLog -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    }
    $result.status = 'PASS_TWO_NEW_WIN32_FAILURE_PATH_CASES_NO_SCIENCE'
}
finally {
    $receipt = Join-Path $qaDir 'G1_WIN32_V1E_PRIVATE_RECEIPT.json'
    ($result | ConvertTo-Json -Depth 9) | Out-File -FilePath $receipt -Encoding utf8 -ErrorAction Stop
    $rs = (Get-FileHash -LiteralPath $receipt -Algorithm SHA256).Hash.ToLowerInvariant()
    ('G1_WIN32_V1E_RECEIPT_SHA256=' + $rs) | Out-File -FilePath (Join-Path $qaDir 'SHA256_RECEIPT.txt') -Encoding ascii
    Write-Output ('G1_WIN32_V1E_QA_DIR=' + $qaDir)
    Write-Output ('G1_WIN32_V1E_STATUS=' + $result.status)
    Write-Output ('G1_WIN32_V1E_RECEIPT_SHA256=' + $rs)
    Write-Output 'G1_SCIENCE_LOCK=HOLD'
}
if ($result.status -cne 'PASS_TWO_NEW_WIN32_FAILURE_PATH_CASES_NO_SCIENCE') { exit 1 }
