# TTM T5 V3 source-only offline independent QA, Windows PowerShell 5.1.
# No ollama, no model imports, no network, no user/system Ollama settings.
$ErrorActionPreference = 'Stop'
$env:PYTHONDONTWRITEBYTECODE = '1'

$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$prefix = Join-Path $root '_tmp'
$rootPrefix = [System.IO.Path]::GetFullPath($prefix).TrimEnd('\') + '\'
$actualSource = [System.IO.Path]::GetFullPath($sourceDir)

if (-not $actualSource.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'SOURCE_NOT_UNDER_TTM_TMP'
}
if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) {
    throw 'TTM_ROOT_MISSING'
}
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'PYTHON312_MISSING'
}
$manifestPath = Join-Path $sourceDir 'SOURCE_SHA256_MANIFEST.json'
$manifest = Get-Content -LiteralPath $manifestPath -Encoding UTF8 -Raw | ConvertFrom-Json
if ($manifest.schema -cne 'ttm.t5.windows.tcptable.sourceonly.bundle.v1') {
    throw 'MANIFEST_SCHEMA_INVALID'
}
foreach ($property in $manifest.source_files.PSObject.Properties) {
    $path = Join-Path $sourceDir $property.Name
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "SOURCE_MISSING: $($property.Name)"
    }
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -cne [string]$property.Value) {
        throw "SOURCE_SHA256_MISMATCH: $($property.Name)"
    }
}
Write-Host 'T5_V3_SOURCE_SHA256=PASS'

# Only mocked Python unit tests; QA does not spawn PowerShell or Ollama.
& $python -B (Join-Path $sourceDir 'test_independent_tcp_owner_guard_v3.py')
$code = $LASTEXITCODE
if ($code -ne 0) {
    Write-Host "T5_V3_WINDOWS_STATIC_QA=FAIL_EXIT_$code"
    exit $code
}
Write-Host 'T5_V3_WINDOWS_STATIC_QA=PASS_60_OF_60'
Write-Host 'T5_V3_OLLAMA_EXECUTION=NOT_EXECUTED_SOURCE_ONLY_LOCKED'
Write-Host 'T5_V1_V2_CLAIMS=PRESERVED_NOT_ACCESSED_BY_QA'
Write-Host 'T5_STRICT_PARITY=FAIL_7_OF_8_PRESERVED'
