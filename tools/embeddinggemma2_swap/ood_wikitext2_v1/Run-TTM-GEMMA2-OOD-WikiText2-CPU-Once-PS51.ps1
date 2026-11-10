$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$work = Join-Path $root '_tmp\ttm_gemma2_ood_wikitext2_cpu_v1_20261111'
if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) { throw 'HOLD_PROJECT_ROOT_NOT_GIT' }
if (-not (Test-Path -LiteralPath $py)) { throw 'HOLD_PYTHON312_NOT_FOUND' }
$actualRoot = (& git -C $root rev-parse --show-toplevel).Trim().Replace('/','\')
if ($actualRoot.TrimEnd('\') -ine $root.TrimEnd('\')) { throw 'HOLD_PROJECT_ROOT_MISMATCH' }
& $py -c 'import sys; assert sys.version_info[:2] == (3,12)'
if ($LASTEXITCODE -ne 0) { throw 'HOLD_PYTHON_VERSION' }
New-Item -ItemType Directory -Force -Path $work | Out-Null
$privateTemp = Join-Path $work 'tmp'
New-Item -ItemType Directory -Force -Path $privateTemp | Out-Null
$env:TEMP = $privateTemp
$env:TMP = $privateTemp
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PIP_DISABLE_PIP_VERSION_CHECK = '1'
$env:PIP_NO_CACHE_DIR = '1'
$env:PIP_CACHE_DIR = Join-Path $work 'pip-cache'
$deps = Join-Path $work 'deps'
$env:PYTHONPATH = $deps

$sourceCommit = 'ec2532b8ef81d06083f3b9e00d10a3bbb874ae23'
$reviewCommit = '7707b88fde6dbfa42397db537d85deba5c43f8d7'
$sourcePath = 'tools/embeddinggemma2_swap/ood_wikitext2_v1/ttm_ood_wikitext2_cpu_seal.py'
$reviewPath = 'tools/embeddinggemma2_swap/ood_wikitext2_v1/ttm_ood_wikitext2_independent_readback.py'
$sourceSHA = 'a874fb75e4007b67a41c0287fa942bbbe4d23ac71a1386194050b14ec18fc200'
$reviewSHA = '8678669c32288d015f8d713392042b0bb89306c6acdc8c01768907e9349b9b0e'
function Ensure-PinnedFile([string]$file, [string]$commit, [string]$remotePath, [string]$sha256) {
    $target = Join-Path $work $file
    $partial = $target + '.partial'
    if (-not (Test-Path -LiteralPath $target)) {
        if (Test-Path -LiteralPath $partial) { throw ('HOLD_SCRIPT_PARTIAL_EXISTS: ' + $partial) }
        $uri = 'https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/' + $commit + '/' + $remotePath
        Invoke-WebRequest -UseBasicParsing -Uri $uri -OutFile $partial
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $partial).Hash -ine $sha256) { throw 'HOLD_DOWNLOADED_SCRIPT_SHA_DRIFT' }
        Move-Item -LiteralPath $partial -Destination $target
    }
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash -ine $sha256) { throw 'HOLD_PINNED_SCRIPT_SHA_DRIFT' }
    return $target
}
$runner = Ensure-PinnedFile 'ttm_ood_wikitext2_cpu_seal.py' $sourceCommit $sourcePath $sourceSHA
$checker = Ensure-PinnedFile 'ttm_ood_wikitext2_independent_readback.py' $reviewCommit $reviewPath $reviewSHA

# Install strictly into the TTM project, never global Python, if modules are missing.
& $py -c 'import pyarrow, numpy, regex'
if ($LASTEXITCODE -ne 0) {
    New-Item -ItemType Directory -Force -Path $deps | Out-Null
    & $py -m pip install --disable-pip-version-check --no-cache-dir --target $deps 'pyarrow==19.0.1' 'numpy==2.2.6' 'regex==2025.7.34'
    if ($LASTEXITCODE -ne 0) { throw 'HOLD_PROJECT_ONLY_DEPENDENCY_INSTALL' }
    & $py -c 'import pyarrow, numpy, regex'
    if ($LASTEXITCODE -ne 0) { throw 'HOLD_PYTHON_MODULES_UNAVAILABLE' }
}

& $py $runner --mode fixture
if ($LASTEXITCODE -ne 0) { throw 'HOLD_FIXTURE_QA' }
$seal = Join-Path $work 'OOD256_PUBLIC_SEAL.json'
if (-not (Test-Path -LiteralPath $seal)) {
    # One integrated CPU run; no model load, GPU, training or OOD scoring.
    & $py $runner --mode execute --repo $root 2>&1 | Tee-Object -FilePath (Join-Path $work 'SOURCE_CPU_RUN_LOG.txt')
    if ($LASTEXITCODE -ne 0) { throw 'HOLD_OOD_SOURCE_CPU_NOT_SEALED' }
}
& $py $checker --repo $root 2>&1 | Tee-Object -FilePath (Join-Path $work 'INDEPENDENT_CPU_READBACK_LOG.txt')
if ($LASTEXITCODE -ne 0) { throw 'HOLD_OOD_INDEPENDENT_CPU_QA' }
Write-Host ('TTM_GEMMA2_OOD_PUBLIC_SEAL_SHA256=' + (Get-FileHash -Algorithm SHA256 -LiteralPath $seal).Hash.ToLowerInvariant())
Write-Host 'TTM_GEMMA2_OOD_FINAL=PASS_SCOPED_SOURCE_SEAL_AND_INDEPENDENT_CPU_QA'
Write-Host 'OOD_INFERENCE=NOT_EXECUTED; MODEL_FORWARD=0; GPU=0; TRAINING=0; LINEAGE=UNCHANGED'
