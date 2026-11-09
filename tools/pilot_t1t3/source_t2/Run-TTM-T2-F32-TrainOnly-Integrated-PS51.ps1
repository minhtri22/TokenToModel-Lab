<#
.TTM T2 F32-first native tokenizer/logits synthetic integration, PowerShell 5.1.
Preview: read-only. Execute: optionally installs only regex==2026.5.9 into
existing TTM CPU venv on D:, then creates a fresh one-shot output directory.
Never alters TTM local Git repository tracked source or science lineage.
#>
[CmdletBinding()]
param([ValidateSet('Preview','Execute')][string]$Mode='Preview')
$ErrorActionPreference='Stop'
$repo = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$work = Join-Path $repo '_tmp\ttm_t2'
$source = Split-Path -Parent $MyInvocation.MyCommand.Path
$v3 = Join-Path $env:USERPROFILE 'Downloads\TTM_T2_V3'
$python = Join-Path $work 'py313_cpu_venv\Scripts\python.exe'
$target = Join-Path $work 'f32_pretok_trainonly_v1'
$script = Join-Path $source 'ttm_t2_f32_integrated.py'
$checker = Join-Path $source 'Check-TTM-T2-Regex.py'

function Assert-Hash([string]$Name,[string]$Expected){
    $targetFile=Join-Path $source $Name
    if(-not (Test-Path -LiteralPath $targetFile -PathType Leaf)) {
        throw ('TTM_T2_FILE_MISSING='+$Name)
    }
    $got=(Get-FileHash -LiteralPath $targetFile -Algorithm SHA256).Hash.ToLowerInvariant()
    if($got -cne $Expected.ToLowerInvariant()){
        throw ('TTM_T2_PIN_MISMATCH='+$Name)
    }
}

function Invoke-Native([string]$Exe,[string[]]$Arguments){
    # Native apps may write progress to stderr while returning status 0.
    # PowerShell 5.1 ErrorActionPreference=Stop with 2>&1 can misreport this.
    $ErrorActionPreference='Continue'
    $lines=@(& $Exe @Arguments 2>&1)
    $exit=$LASTEXITCODE
    foreach($line in $lines){Write-Host ([string]$line)}
    return $exit
}

if(-not (Test-Path -LiteralPath $repo -PathType Container) -or
   -not (Test-Path -LiteralPath $python -PathType Leaf) -or
   -not (Test-Path -LiteralPath $v3 -PathType Container)){
   throw 'TTM_T2_REQUIRED_EXISTING_ENV_OR_REPO_MISSING'
}
if((Resolve-Path -LiteralPath $repo).Path.ToLowerInvariant() -cne 'd:\work\research\tokentomodel-lab'){
   throw 'TTM_T2_PROJECT_BOUNDARY_MISMATCH'
}
if(Test-Path -LiteralPath $target){throw 'TTM_T2_F32_ONE_SHOT_ALREADY_CONSUMED_DO_NOT_RERUN'}

Assert-Hash 'ttm_gpt2_bpe2048.py' '36d66a1f569b502b7c9def6215fa296de57822146f7845b6d67151982d4ce961'
Assert-Hash 'ttm_t2_f32_integrated.py' '61351df745d5a2d0048640daadf2004e6467cea928f990d189962ffe612b8143'
Assert-Hash 'Check-TTM-T2-Regex.py' 'f17718d78bc9731c2a03a4de2c7a2dec54053ea7ddee92c05d68103ed3668870'
Assert-Hash 'TTM_T2_F32_NEW_FIXTURES_FROZEN_20261108.json' '5a4ba58db3ad7c1ad0a7c6a790c08184d43c1e3a081ad2dcaf2d4c3b9dbeb9f2'
Write-Host 'TTM_T2_F32_SOURCE_AND_NEW_FIXTURE_PINS=PASS'

$driverArgs=@('--repo',$repo,'--work',$work,'--v3-source',$v3,'--package',$source,'--mode','preview')
$previewCode=Invoke-Native $python (@($script)+$driverArgs)
if($previewCode -ne 0){throw ('TTM_T2_F32_NATIVE_PREVIEW_FAILED='+$previewCode)}

$depCode=Invoke-Native $python @($checker)
if($depCode -ne 0 -and $depCode -ne 3){throw ('TTM_T2_REGEX_DEPENDENCY_WRONG='+$depCode)}

if($Mode -eq 'Preview') {
    if($depCode -eq 3){Write-Host 'TTM_T2_F32_REGEX_WILL_INSTALL_ONLY_ON_EXECUTE=regex==2026.5.9'}
    Write-Host 'TTM_T2_F32_PREVIEW=PASS_READONLY'
    Write-Host 'TTM_T2_F32_SCIENCE=NOT_EXECUTED'
    exit 0
}

if($depCode -eq 3) {
    $temp = Join-Path $work 'py313_install_tmp'
    if(-not (Test-Path -LiteralPath $temp -PathType Container)){
        throw 'TTM_T2_EXISTING_D_TEMP_NOT_FOUND'
    }
    $env:TEMP=$temp; $env:TMP=$temp; $env:PIP_NO_CACHE_DIR='1'
    Write-Host 'TTM_T2_F32_DEP_INSTALL_SCOPE=TTM_CPU_VENV_ONLY'
    $installCode=Invoke-Native $python @('-m','pip','install','--no-cache-dir','--only-binary=:all:','--disable-pip-version-check','--no-deps','regex==2026.5.9')
    if($installCode -ne 0){throw ('TTM_T2_F32_REGEX_WHEEL_INSTALL_FAILED='+$installCode)}
    $depCode=Invoke-Native $python @($checker)
    if($depCode -ne 0){throw 'TTM_T2_F32_REGEX_POST_INSTALL_VERSION_MISMATCH'}
}

# Repeat exact preflight immediately before first and only write.
if(Test-Path -LiteralPath $target){throw 'TTM_T2_F32_ALREADY_STARTED_NO_RERUN'}
$driverArgs[-1]='execute'
$runCode=Invoke-Native $python (@($script)+$driverArgs)
if($runCode -ne 0){throw ('TTM_T2_F32_INTEGRATION_NOT_PASS_EXIT='+$runCode+';KEEP_REPORT_NO_RERUN')}
Write-Host 'TTM_T2_F32_EXECUTION=COMPLETED_READBACK_REQUIRED'
