# TTM FRESH16 V2 E0 — Python 3.12 Windows source-only preparation.
# Default PREPARE: verifies original checkpoints/model weights without any forward pass.
# RUN is explicitly gated by a separate owner GO permit; this file never grants GO.
[CmdletBinding()]
param(
    [ValidateSet('Prepare','Run')]
    [string]$Mode = 'Prepare',
    [Parameter(Mandatory=$true)]
    [string]$ExpectedHead,
    [string]$GoPermitPath = '',
    [string]$GoPermitSHA256 = '',
    [string]$MapAnchorCommit = ''
)
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $root 'worktrees\ttm-fresh16-quality-20261111'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$runner = Join-Path $wt 'tools\research\ttm_small4m_quality_gap\ttm_fresh16_v2_e0.py'
$runDir = Join-Path $root '_tmp\ttm_fresh16_v2_e0_20261111'
$branch = 'research/ttm-small4m-prompt-adherence-continuation-design-20261111'

foreach ($path in @($root, $wt, $py, $runner)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw ('MISSING_PATH:' + $path)
    }
}
$actualBranch = (& git -C $wt branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $actualBranch -ne $branch) {
    throw 'WRONG_RESEARCH_BRANCH'
}
$actualHead = (& git -C $wt rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualHead -ne $ExpectedHead) {
    throw 'SOURCE_HEAD_NOT_PINNED'
}
$dirty = & git -C $wt status --porcelain --untracked-files=all
if ($LASTEXITCODE -ne 0 -or $dirty) {
    throw 'DIRTY_RESEARCH_WORKTREE'
}
& $py -c 'import sys; assert sys.version_info[:2] == (3, 12)'
if ($LASTEXITCODE -ne 0) {
    throw 'PYTHON312_REQUIRED'
}
$arguments = @(
    '--mode', $Mode.ToLowerInvariant(),
    '--project-root', $root,
    '--worktree', $wt,
    '--expected-head', $ExpectedHead,
    '--run-dir', $runDir
)
if ($Mode -eq 'Run') {
    if (-not $GoPermitPath -or -not $GoPermitSHA256 -or -not $MapAnchorCommit) {
        throw 'RUN_NOT_AUTHORIZED_MISSING_OWNER_PERMIT_OR_ANCHOR'
    }
    $arguments += @(
        '--permit', $GoPermitPath,
        '--permit-sha256', $GoPermitSHA256,
        '--map-anchor-commit', $MapAnchorCommit
    )
}
& $py $runner @arguments
if ($LASTEXITCODE -ne 0) {
    throw ('FRESH16_E0_' + $Mode.ToUpperInvariant() + '_HOLD')
}
