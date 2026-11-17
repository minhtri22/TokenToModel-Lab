# Safe environment-only preflight. NO model/fixture read, NO output file write.
# PowerShell 5.1 / Windows 11. Run from anywhere.
param([string]$ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab')
$ErrorActionPreference = 'Stop'
$ExpectedMain = 'f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3'
$Python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) { throw 'HOLD_PROJECT_ROOT_NOT_FOUND' }
$gitHead = ((& git -C $ProjectRoot rev-parse HEAD) | Select-Object -First 1).Trim()
$gitExit = $LASTEXITCODE
Write-Output ('TTM_DIAG_Q001_LOCAL_GIT_HEAD=' + $gitHead)
Write-Output ('TTM_DIAG_Q001_LOCAL_GIT_EXACT=' + ($(if ($gitExit -eq 0 -and $gitHead -eq $ExpectedMain) {'PASS'} else {'HOLD_LOCAL_CHECKOUT_OR_MAIN_DRIFT'})))
if (Test-Path -LiteralPath $Python -PathType Leaf) {
  & $Python -c "import sys,importlib.metadata as m,json; v=sys.version_info; p={x:next((z.version for z in m.distributions() if z.metadata['Name'].lower()==x),'NOT_INSTALLED') for x in ['torch','psutil']}; print(json.dumps({'python_version':sys.version.split()[0],'python312':v[:2]==(3,12),'packages':p}))"
  if ($LASTEXITCODE -ne 0) { Write-Output 'TTM_DIAG_Q001_PYTHON_PREFLIGHT=HOLD_PACKAGE_METADATA_ERROR' }
} else {
  Write-Output 'TTM_DIAG_Q001_PYTHON_PREFLIGHT=HOLD_PYTHON312_EXACT_PATH_NOT_FOUND'
}
try {
  $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
  Write-Output ('TTM_DIAG_Q001_AVAILABLE_RAM_KIB=' + $os.FreePhysicalMemory)
  Write-Output ('TTM_DIAG_Q001_TOTAL_RAM_KIB=' + $os.TotalVisibleMemorySize)
} catch { Write-Output 'TTM_DIAG_Q001_RAM_STATUS=UNKNOWN_READONLY_CIM_FAILED' }
Write-Output 'TTM_DIAG_Q001_CHECKPOINT_RIGHTS=NOT_VERIFIED_BY_THIS_PREFLIGHT'
Write-Output 'TTM_DIAG_Q001_DISTINCT_REVIEW=NOT_VERIFIED_BY_THIS_PREFLIGHT'
Write-Output 'TTM_DIAG_Q001_MODEL_EXECUTION=NOT_PERFORMED'
Write-Output 'TTM_DIAG_Q001_FIXTURE_GENERATION=NOT_PERFORMED'
