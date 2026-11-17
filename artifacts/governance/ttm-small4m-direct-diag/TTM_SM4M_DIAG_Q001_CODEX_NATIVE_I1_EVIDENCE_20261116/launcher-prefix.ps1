param([Parameter(Mandatory=$true)][string]$ProjectRoot)
$ErrorActionPreference='Stop'
$source=Join-Path $ProjectRoot 'tools\pilot_t4\direct_failure_diag_q001\preexec_candidate_20261116'
$launcher=Join-Path $source 'Run-Approved-OneShot-PS51.ps1'
$watchdog=Join-Path $source 'Watch-TTM-SM4M-ProcessTree-PS51.ps1'
$t=$null;$errs=$null
$ast=[System.Management.Automation.Language.Parser]::ParseFile($launcher,[ref]$t,[ref]$errs)
if (@($errs).Count) {throw 'LAUNCHER_AST_INVALID'}
$text=[IO.File]::ReadAllText($launcher)
$start=$ast.ParamBlock.Extent.EndOffset
$stop=$text.IndexOf('if (-not (Test-Path -LiteralPath $Python -PathType Leaf))')
$end=[Math]::Min($stop,$text.Length)
if ($start -ge $end) {throw 'NO_AUDITABLE_MODULE_PREFIX'}
$prefix=$text.Substring($start,$end-$start)
if ($prefix -match '(Start-Process|release-preflight|\& \$Python|--checkpoint|Join-Path \$ProjectRoot)') {
    throw 'UNEXPECTED_EXECUTION_IN_PREFIX'
}
# Evaluate only the source admission prefix inside a QA function with a
# disposable source directory. Never call the launcher or its Python process.
$snippet=[scriptblock]::Create("param([string]" + '$PSScriptRoot,[string]$ExpectedRunnerSHA256,[string]$ExpectedWatchdogSHA256,[string]$RunnerPath)'+
    [Environment]::NewLine+$prefix+[Environment]::NewLine+"'BOUND_VERIFIED_WATCHDOG'")
$qa=Join-Path $ProjectRoot ('_tmp\codex-launcher-check-'+$PID)
New-Item -ItemType Directory -Path $qa | Out-Null
$watchCopy=Join-Path $qa ([IO.Path]::GetFileName($watchdog))
$marker=Join-Path $qa 'UNPINNED_MODULE_RAN'
$pin=(Get-FileHash -LiteralPath $watchdog).Hash.ToLowerInvariant()
$runnerPin=(Get-FileHash -LiteralPath (Join-Path $source 'ttm_sm4m_diag_q001.py')).Hash.ToLowerInvariant()
$results=[ordered]@{}
function Check-Prefix([string]$name,[string]$runner,[string]$watch,[string]$runnerPath,[string]$expected) {
    try {$actual=& $snippet $qa $runner $watch $runnerPath}
    catch {$actual=$_.Exception.Message}
    $results[$name]=[ordered]@{expected=$expected;actual=$actual;passed=($actual -ceq $expected)}
}
Copy-Item -LiteralPath $watchdog -Destination $watchCopy
Check-Prefix 'correct_pinned_watchdog_loaded' $runnerPin $pin '' 'BOUND_VERIFIED_WATCHDOG'
Check-Prefix 'foreign_runner_path_denied' $runnerPin $pin (Join-Path $qa 'other.py') 'HOLD_RUNNER_PATH_NOT_PINNED'
Check-Prefix 'malformed_runner_sha' 'bad' $pin '' 'HOLD_RUNNER_PIN_FORMAT'
Check-Prefix 'wrong_runner_sha' ('0'*64) $pin '' 'HOLD_RUNNER_PIN_NOT_REVIEWED'
Check-Prefix 'malformed_watchdog_sha' $runnerPin 'bad' '' 'HOLD_WATCHDOG_PIN_FORMAT'
[IO.File]::WriteAllText($watchCopy,"[IO.File]::WriteAllText('$marker','injected')")
$injectedPin=(Get-FileHash -LiteralPath $watchCopy).Hash.ToLowerInvariant()
Check-Prefix 'caller_rehash_of_injected_watchdog_denied' $runnerPin $injectedPin '' 'HOLD_WATCHDOG_PIN_NOT_REVIEWED'
Check-Prefix 'changed_watchdog_bytes_denied' $runnerPin $pin '' 'HOLD_WATCHDOG_SOURCE_SHA'
$results['injected_module_side_effect_absent']=@{passed= -not (Test-Path -LiteralPath $marker)}
$spawn=@($ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.CommandAst] -and
    $node.GetCommandName() -eq 'Start-Process' },$true))
$authOffset=$text.IndexOf('& $Python $RunnerPath release-preflight')
$checkpointOffset=$text.IndexOf('if (-not (Test-Path -LiteralPath $CheckpointPath')
$results['admission_precedes_checkpoint_probe_and_spawn']=[ordered]@{
    spawn_count=$spawn.Count;preflight_offset=$authOffset;checkpoint_probe_offset=$checkpointOffset
    spawn_offset=$spawn[0].Extent.StartOffset
    passed=($spawn.Count -eq 1 -and $stop -lt $authOffset -and $authOffset -lt $checkpointOffset -and
        $checkpointOffset -lt $spawn[0].Extent.StartOffset)
}
$passed=@($results.Values | Where-Object {$_.passed}).Count
[ordered]@{scope='PS51_AST_AND_ISOLATED_MODULE_ADMISSION_PREFIX';powershell=$PSVersionTable.PSVersion.ToString()
    launcher_called=$false;model_executed=$false;passed=$passed;total=$results.Count;checks=$results
} | ConvertTo-Json -Depth 8
if ($passed -ne $results.Count) {exit 2}
