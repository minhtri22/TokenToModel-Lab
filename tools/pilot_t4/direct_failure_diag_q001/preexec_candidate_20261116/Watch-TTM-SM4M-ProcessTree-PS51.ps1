# Windows PowerShell 5.1 - independently testable no-model watchdog.
# This watchdog samples limits during execution and checks again at exit.
# A hard memory ceiling requires separate OS enforcement.
function Invoke-TTMDiagProcessWatch {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][Diagnostics.Process]$Process,
        [Parameter(Mandatory=$true)][string]$StdOutPath,
        [Parameter(Mandatory=$true)][string]$StdErrPath,
        [Parameter(Mandatory=$true)][string]$OutputDir,
        [int]$WallSeconds=900,
        [Int64]$MaxTreeRssBytes=12884901888,
        [Int64]$MaxTotalOutputBytes=1073741824,
        [int]$PollMilliseconds=250
    )
    if ($WallSeconds -lt 1 -or $MaxTreeRssBytes -lt 1 -or
        $MaxTotalOutputBytes -lt 1 -or $PollMilliseconds -lt 50) {
        throw 'HOLD_WATCHDOG_INVALID_CAP'
    }
    $clock=[Diagnostics.Stopwatch]::StartNew()
    $known=New-Object 'System.Collections.Generic.HashSet[int]'
    [void]$known.Add([int]$Process.Id)
    $peak=0L
    $lastBytes=0L
    $passed=$false
    $stopCode=$null
    try {
        # Keep Start-Process -PassThru's process handle for exit status.
        $null=$Process.Handle
        while ($true) {
            # Build a transitive descendant closure from the original parent and
            # every child previously observed (including an already-exited parent).
            $snapshot=@(Get-CimInstance Win32_Process -ErrorAction Stop)
            $growing=$true
            while ($growing) {
                $growing=$false
                foreach($entry in $snapshot) {
                    if ($known.Contains([int]$entry.ParentProcessId) -and
                        -not $known.Contains([int]$entry.ProcessId)) {
                        [void]$known.Add([int]$entry.ProcessId)
                        $growing=$true
                    }
                }
            }
            $sumRss=0L
            foreach($id in @($known)) {
                $processInfo=Get-Process -Id $id -ErrorAction SilentlyContinue
                if ($processInfo) {
                    $sumRss += [Int64]$processInfo.WorkingSet64
                }
            }
            $peak=[Math]::Max($peak,$sumRss)
            $lastBytes=0L
            foreach($log in @($StdOutPath,$StdErrPath)) {
                if (Test-Path -LiteralPath $log -PathType Leaf) {
                    $lastBytes += [Int64](Get-Item -LiteralPath $log -ErrorAction Stop).Length
                }
            }
            if (Test-Path -LiteralPath $OutputDir -PathType Container) {
                $files=@(Get-ChildItem -LiteralPath $OutputDir -Recurse -File -Force -ErrorAction Stop)
                foreach($file in $files) {$lastBytes += [Int64]$file.Length}
            }
            if ($clock.Elapsed.TotalSeconds -ge $WallSeconds) {
                $stopCode='HOLD_WATCHDOG_WALL_TIME'
                throw $stopCode
            }
            if ($peak -gt $MaxTreeRssBytes) {
                $stopCode='HOLD_WATCHDOG_AGGREGATE_PROCESS_TREE_RSS'
                throw $stopCode
            }
            if ($lastBytes -ge $MaxTotalOutputBytes) {
                $stopCode='HOLD_WATCHDOG_TOTAL_LOG_AND_OUTPUT_BYTES'
                throw $stopCode
            }
            # Crucial: this exit test comes AFTER checking resource bounds.
            $Process.Refresh()
            if ($Process.HasExited) {
                # Never return a success while a tracked descendant keeps running.
                $aliveChildren=@($known | Where-Object {
                    $_ -ne $Process.Id -and (Get-Process -Id $_ -ErrorAction SilentlyContinue)
                })
                if ($aliveChildren.Count -gt 0) {
                    $stopCode='HOLD_WATCHDOG_ORPHAN_DESCENDANT_AFTER_PARENT_EXIT'
                    throw $stopCode
                }
                if ($null -eq $Process.ExitCode) {throw 'HOLD_WATCHDOG_EXIT_CODE_UNAVAILABLE'}
                if ($Process.ExitCode -ne 0) {
                    $stopCode='HOLD_RUN_EXIT_'+$Process.ExitCode
                    throw $stopCode
                }
                $passed=$true
                return [pscustomobject]@{
                    Status='PASS_WATCHDOG_SAMPLE_BOUNDED'
                    PeakTreeRssBytesSampled=$peak
                    FinalTotalOutputBytes=$lastBytes
                    ElapsedSeconds=$clock.Elapsed.TotalSeconds
                    TrackedPidCount=$known.Count
                    ExitCode=$Process.ExitCode
                }
            }
            Start-Sleep -Milliseconds $PollMilliseconds
        }
    } catch {
        $_.Exception.Data['PeakTreeRssBytesSampled']=$peak
        $_.Exception.Data['LastTotalOutputBytes']=$lastBytes
        $_.Exception.Data['TrackedPids']=@($known | Sort-Object)
        $_.Exception.Data['ElapsedSeconds']=$clock.Elapsed.TotalSeconds
        throw
    } finally {
        if (-not $passed) {
            # Fail closed and attempt to stop the full tree. taskkill /T first;
            # recorded children are also killed in case parent already exited.
            if (-not $Process.HasExited) {
                & taskkill.exe /PID $Process.Id /T /F 2>$null | Out-Null
            }
            foreach($id in @($known)) {
                if ($id -eq $PID) {continue}
                $alive=Get-Process -Id $id -ErrorAction SilentlyContinue
                if ($alive) {
                    try {$alive.Kill(); $null=$alive.WaitForExit(2000)} catch {}
                }
            }
        }
        $clock.Stop()
    }
}
