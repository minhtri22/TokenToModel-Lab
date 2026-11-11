#requires -Version 5.1
<#
TTM-Small4M A/C exact-source native Windows preexec. No science, GPU, TEST, OOD or Q1Q2.
Outputs strictly under D:\WORK\RESEARCH\TokenToModel-Lab\_tmp.
Run only once; never overwrite an existing run directory.
#>
[CmdletBinding()]
param(
    [string] $ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string] $Python312 = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ExpectedRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab'
if ([IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\') -ine $ExpectedRoot) {
    throw 'TTM_SCOPE_WRONG_PROJECT_ROOT'
}
if (-not (Test-Path -LiteralPath (Join-Path $ProjectRoot '.git'))) {
    throw 'TTM_SCOPE_PROJECT_GIT_MISSING'
}
if (-not (Test-Path -LiteralPath $Python312 -PathType Leaf)) {
    throw 'TTM_PYTHON312_MISSING_NO_INSTALL'
}
$PinnedCommit = '6628401b08ea7682cf34aa5078546e1d18e4d2cc'
$RelativeDir = 'tools/pilot_t4/prompt_conditioning_2x2'
$Pins = [ordered]@{
    'ttm_ac_objective_runner_candidate.py' = 'ad7d88672c65c6778f5956e6fc7aa656b78b998f'
    'ttm_ac_resume_store.py' = '8b02db35854cf24e77246d81dba6a8b8fe2d746e'
    'test_ttm_ac_resume_synthetic.py' = '0c6f89518b919532e1ebc8a8021f79893c4ca10d'
    'ttm_2x2_colab_runner_candidate.py' = '6c87e388da4d4a2b94dffba655861a390dfad73c'
    'real_metadata_preflight.py' = '84d54dced18b19bea2bc062216e32301c3c32dc2'
}
$RunDir = Join-Path $ProjectRoot ('_tmp\TTM_AC_NATIVE_PREEXEC_' + $PinnedCommit.Substring(0,12))
if (Test-Path -LiteralPath $RunDir) {
    throw 'TTM_NATIVE_QA_RUN_ALREADY_EXISTS_NO_RERUN'
}
New-Item -Path $RunDir -ItemType Directory -ErrorAction Stop | Out-Null
$ResultPath = Join-Path $RunDir 'NATIVE_SOURCE_QA_RESULT.json'
$Result = [ordered]@{
    schema = 'ttm.ac.native.py312.source_qa.v1'
    pinned_commit = $PinnedCommit
    status = 'HOLD_UNEXECUTED'
    python312 = $Python312
    source_git_blob_exact = $false
    syntax_compile = $false
    source_qa = $false
    synthetic_resume_tests = $false
    t4_smoke = 'NOT_EXECUTED'
    real_model_train = 'NOT_EXECUTED'
    original_TEST = 'UNTOUCHED'
    original_OOD = 'UNTOUCHED'
    original_Q1Q2 = 'UNTOUCHED'
    error = ''
}
try {
    # Fail before downloading if git is unavailable.
    $GitExe = (Get-Command git.exe -ErrorAction Stop).Source
    & $Python312 -B -c "import sys; assert sys.version_info[:2] == (3,12), sys.version"
    if ($LASTEXITCODE -ne 0) { throw 'TTM_WRONG_PYTHON_VERSION' }
    & $Python312 -B -c "import numpy, torch; print('PY312_DEPENDENCIES_PASS', torch.__version__, numpy.__version__)"
    if ($LASTEXITCODE -ne 0) { throw 'TTM_PY312_NUMPY_TORCH_MISSING_NO_INSTALL' }
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    foreach ($Name in $Pins.Keys) {
        $Uri = 'https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/' +
               $PinnedCommit + '/' + $RelativeDir + '/' + $Name
        $Destination = Join-Path $RunDir $Name
        Invoke-WebRequest -Uri $Uri -OutFile $Destination -UseBasicParsing -ErrorAction Stop
        $ActualGitBlob = (& $GitExe hash-object -- $Destination).Trim().ToLowerInvariant()
        if ($LASTEXITCODE -ne 0 -or $ActualGitBlob -ne $Pins[$Name]) {
            throw ('TTM_GITHUB_SOURCE_BLOB_MISMATCH:' + $Name)
        }
    }
    $Result.source_git_blob_exact = $true
    $Targets = @(
        'ttm_ac_objective_runner_candidate.py',
        'ttm_ac_resume_store.py',
        'test_ttm_ac_resume_synthetic.py',
        'ttm_2x2_colab_runner_candidate.py',
        'real_metadata_preflight.py'
    ) | ForEach-Object { Join-Path $RunDir $_ }
    & $Python312 -B -m py_compile @Targets
    if ($LASTEXITCODE -ne 0) { throw 'TTM_AC_PY312_PY_COMPILE_FAILED' }
    $Result.syntax_compile = $true
    $SourceOutput = & $Python312 -B (Join-Path $RunDir 'ttm_ac_objective_runner_candidate.py') --mode source-qa 2>&1
    if ($LASTEXITCODE -ne 0) { throw ('TTM_AC_SOURCE_QA_FAILED:' + ($SourceOutput -join ' ')) }
    $SourceRecord = ($SourceOutput -join [Environment]::NewLine) | ConvertFrom-Json
    if ($SourceRecord.status -ne 'PASS_SOURCE_ONLY_NO_MODEL_FORWARD') {
        throw 'TTM_AC_SOURCE_QA_STATUS_MISMATCH'
    }
    $Result.source_qa = $true
    $env:TTM_AC_QA_ROOT = $RunDir
    $TestLog = Join-Path $RunDir 'SYNTHETIC_RESUME_TEST_LOG.txt'
    $TestOutput = & $Python312 -B (Join-Path $RunDir 'test_ttm_ac_resume_synthetic.py') 2>&1
    $TestOutput | Out-File -FilePath $TestLog -Encoding utf8
    if ($LASTEXITCODE -ne 0 -or ($TestOutput -join ' ') -notmatch 'Ran 6 tests') {
        throw 'TTM_AC_SYNTHETIC_RESUME_QA_FAILED'
    }
    $Result.synthetic_resume_tests = $true
    $Result.status = 'PASS_SCOPED_NATIVE_PY312_SOURCE_AND_CPU_TOY_RESUME'
}
catch {
    $Result.status = 'HOLD_NATIVE_QA_FAILED'
    $Result.error = [string] $_.Exception.Message
}
finally {
    $Result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ResultPath -Encoding UTF8
    Write-Output ('TTM_AC_NATIVE_QA_STATUS=' + $Result.status)
    Write-Output ('TTM_AC_NATIVE_QA_RESULT=' + $ResultPath)
    Write-Output ('TTM_AC_NATIVE_QA_NO_SCIENCE=TRUE')
}
if ($Result.status -ne 'PASS_SCOPED_NATIVE_PY312_SOURCE_AND_CPU_TOY_RESUME') {
    throw ('TTM_AC_NATIVE_QA_HOLD:' + $Result.error)
}
