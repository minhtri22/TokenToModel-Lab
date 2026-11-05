param([string]$PythonExe = 'python')
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$source = Join-Path $root 'reference\phase0\test_reference.py'
if (-not (Test-Path -LiteralPath $source)) { throw 'Wrong project or missing phase0 reference test' }
$expected = Join-Path $root 'PROJECT_CHARTER.md'
if (-not (Test-Path -LiteralPath $expected)) { throw 'Project guard failed' }
Push-Location $root
try {
    Write-Host 'QA_SCOPE=CPU_REFERENCE_AND_REGISTRY_ONLY'
    & $PythonExe -m unittest discover -s tests -p 'test_*.py' -v
    if ($LASTEXITCODE -ne 0) { throw 'Registry QA FAIL' }
    & $PythonExe -m unittest discover -s reference/phase0 -p 'test_reference.py' -v
    if ($LASTEXITCODE -ne 0) { throw 'Reference QA FAIL' }
    Write-Host 'LOCAL_QA=PASS_SCOPE_LIMITED'
    Write-Host 'NOTE=No training, Git mutation, downloads, or cleanup performed'
} finally { Pop-Location }
