# A0D OWNER PINNED SOURCE READBACK PS5.1 V2: avoids quoting-sensitive python -c.
# Apply only to the previously supplied PS1 within TTM project _tmp folder.
# Idempotent and fail-closed; no model, training, or source data mutations.
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$script = Join-Path $root '_tmp\TTM_GEMMA2_A0D_OWNER_PINNED_OFFICIAL_READBACK_PS51.ps1'
if (-not (Test-Path -LiteralPath $script -PathType Leaf)) { throw 'HOLD_ORIGINAL_OWNER_SCRIPT_NOT_FOUND' }
$s = [System.IO.File]::ReadAllText($script)
$old = 'print("%d.%d" % sys.version_info[:2])'
$replacement = 'print(sys.version_info[0] * 100 + sys.version_info[1])'
$oldCheck = "if (`$Version -ne '3.12') { throw 'HOLD_PYTHON_VERSION_NOT_312' }"
$newCheck = "if (`$Version -ne '312') { throw 'HOLD_PYTHON_VERSION_NOT_312' }"
if ($s.Contains($replacement) -and $s.Contains($newCheck)) {
    Write-Output 'A0D_OWNER_PYTHON_VERSION_QUOTE_FIX=ALREADY_PRESENT'
} elseif ($s.Contains($old) -and $s.Contains($oldCheck)) {
    $s = $s.Replace($old, $replacement).Replace($oldCheck, $newCheck)
    [System.IO.File]::WriteAllText($script, $s, (New-Object System.Text.UTF8Encoding($false)))
    Write-Output 'A0D_OWNER_PYTHON_VERSION_QUOTE_FIX=PASS_APPLIED'
} else { throw 'HOLD_UNEXPECTED_SOURCE_TO_AVOID_UNSAFE_REPLACEMENT' }
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'HOLD_PYTHON312_EXE_MISSING' }
$v = (& $py -c 'import sys; print(sys.version_info[0] * 100 + sys.version_info[1])' | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $v -ne '312') { throw 'HOLD_PYTHON312_VERSION' }
Write-Output 'A0D_PYTHON312_VERSION=PASS'
Write-Output ('A0D_FIXED_SCRIPT=' + $script)
