param([string]$Root,[string]$Watchdog)
$ErrorActionPreference='Stop'
$python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$src=Join-Path $Root 'tools\pilot_t4\direct_failure_diag_q001\preexec_candidate_20261116'
. $Watchdog
foreach($mode in @('as_is','capture_handle')) {
 $e=Join-Path $Root '_tmp\codex-i1-evidence'
 $o=Join-Path $e ($mode+'.stdout.txt')
 $s=Join-Path $e ($mode+'.stderr.txt')
 $p=Start-Process -FilePath $python -ArgumentList @('-c','"print(42)"') -PassThru -RedirectStandardOutput $o -RedirectStandardError $s
 if ($mode -eq 'capture_handle') { $null=$p.Handle }
 try {
   $result=Invoke-TTMDiagProcessWatch -Process $p -StdOutPath $o -StdErrPath $s -OutputDir (Join-Path $e 'missing') -WallSeconds 8
   $result | ConvertTo-Json
 } catch { Write-Output ('exception='+$_.Exception.Message) }
 $p.WaitForExit()
 Write-Output ('mode='+$mode+' pid='+$p.Id+' exit='+$p.ExitCode+' null='+($null -eq $p.ExitCode))
}

