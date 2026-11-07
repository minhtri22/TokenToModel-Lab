# TTM P05 Windows PS5.1 — exact source, synthetic CPU QA, scoped worktree cleanup.
# Never runs P01 E0, P03 training, P04 real heldout, or P06.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$ExpectedOrigin = 'https://github.com/minhtri22/TokenToModel-Lab.git'
$ExpectedMain = '88bde037705607730cfc24e36875aa865d3a380c'
$ExpectedHead = '9afbdcdbd5c39da0ae5d92da327498cb3ad866d9'
$ExpectedBranch = 'feature/p05-dense-kv-cache-20261107'
$Python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$EvidenceDir = Join-Path $Root 'evidence\p05'
$WorktreeBase = Join-Path $Root 'worktrees'
$RunId = 'TTM_P05_WINDOWS_CPU_QA_' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '_P' + $PID
$Worktree = Join-Path $WorktreeBase ('p05-windows-qa-' + $RunId)
$ReceiptPath = Join-Path $EvidenceDir ($RunId + '.json')
$UnitPath = Join-Path $EvidenceDir ($RunId + '.unittest.log')
$IndependentPath = Join-Path $EvidenceDir ($RunId + '.independent.log')
$Encoding = New-Object System.Text.UTF8Encoding($false)
$OwnedWorktreeAdded = $false
$Cleanup = 'NOTHING_CREATED'
$Failure = $null
$GitExe = $null
$HeadBefore = $null
$HeadAfter = $null

$ExpectedBlobs = [ordered]@{
    'src/p05/dense_kv_cache.py' = 'd835e5d7bb07fea447c5a869b13c70327ab05a53'
    'tests/p05/test_dense_kv_cache.py' = '2fa25a579a600b3c80c28ac7ef07b253805e3490'
    'tools/p05/independent_dense_kv_qa.py' = '2e318b38b0a4e5a33a407515908d31d0c7d32e6d'
    'src/p02/transformer_core.py' = '9762343e06cf800b50574c2871ae1ed58537fb18'
}
$ExpectedSHA256 = [ordered]@{
    'src/p05/dense_kv_cache.py' = '45e3b2e153a4d37578a5dfacc86a313a5026c89eba13fcff41b59a0143b50412'
    'tests/p05/test_dense_kv_cache.py' = '616638f65de58008245c059ffcae4114898f7985296b505cb5209b6b8f84598f'
    'tools/p05/independent_dense_kv_qa.py' = '3da42c253daebf6cde229ebeaf305263c370fbdf23133582e9271b480b300d97'
    'src/p02/transformer_core.py' = 'e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07'
}

$Receipt = [ordered]@{
    schema = 'ttm.p05.windows.cpu_synthetic_integrated_qa.v1'
    run_id = $RunId
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    repository = $ExpectedOrigin
    expected_main = $ExpectedMain
    expected_head = $ExpectedHead
    expected_branch = $ExpectedBranch
    local_head_before = $null
    local_head_after = $null
    python = $Python
    python_version = $null
    pytorch_version = $null
    source_git_blobs = [ordered]@{}
    source_sha256 = [ordered]@{}
    unit_tests = [ordered]@{ pass = $false; exit_code = $null; count = 0; log = $UnitPath; log_sha256 = $null }
    independent_tests = [ordered]@{ pass = $false; exit_code = $null; count = 0; log = $IndependentPath; log_sha256 = $null }
    benchmark = $null
    cleanup = $Cleanup
    dataset = 'SYNTHETIC_TOKEN_IDS_ONLY'
    p01_e0 = 'DO_NOT_RERUN'
    p01_test = 'NOT_READ'
    p03 = 'NOT_EXECUTED'
    p04_real_heldout = 'NOT_EXECUTED'
    p06 = 'NOT_OPENED'
    main_changes_by_runner = 'NONE_EXPECTED'
    verdict = 'NOT_EXECUTED'
    failure = $null
}

function Invoke-ExactProcess {
    param(
        [Parameter(Mandatory=$true)][string]$Exe,
        [Parameter(Mandatory=$true)][string[]]$Argv,
        [Parameter(Mandatory=$true)][string]$Cwd,
        [int]$TimeoutSeconds = 180
    )
    # All command arguments in this pinned project use paths without spaces or quotes.
    foreach ($arg in $Argv) {
        if ($arg -match '[\s"]') { throw 'UNSUPPORTED_ARGUMENT_WITH_SPACE_OR_QUOTE' }
    }
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $Exe
    $psi.Arguments = [string]::Join(' ', $Argv)
    $psi.WorkingDirectory = $Cwd
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.EnvironmentVariables['PYTHONDONTWRITEBYTECODE'] = '1'
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    try {
        if (-not $proc.Start()) { throw 'PROCESS_START_FAILED' }
        $outTask = $proc.StandardOutput.ReadToEndAsync()
        $errTask = $proc.StandardError.ReadToEndAsync()
        if (-not $proc.WaitForExit($TimeoutSeconds * 1000)) {
            try { $proc.Kill() } catch {}
            $proc.WaitForExit()
            throw ('PROCESS_TIMEOUT_' + $TimeoutSeconds + '_SECONDS')
        }
        $proc.WaitForExit()
        return [pscustomobject]@{
            ExitCode = [int]$proc.ExitCode
            StdOut = [string]$outTask.Result
            StdErr = [string]$errTask.Result
        }
    } finally { $proc.Dispose() }
}

function Invoke-TTMGit {
    param([Parameter(Mandatory=$true)][string[]]$ArgsList, [int]$TimeoutSeconds = 180)
    $z = Invoke-ExactProcess -Exe $GitExe -Argv (@('-C', $Root) + $ArgsList) -Cwd $Root -TimeoutSeconds $TimeoutSeconds
    if ($z.ExitCode -ne 0) {
        $details = ($z.StdErr + ' ' + $z.StdOut).Trim()
        if ($details.Length -gt 1200) { $details = $details.Substring(0,1200) }
        throw ('GIT_EXIT_' + $z.ExitCode + ': ' + $details)
    }
    return $z.StdOut.Trim()
}

function Write-ExactLog {
    param([string]$Path, $Result)
    $content = ('EXIT=' + $Result.ExitCode + "`r`n=== STDOUT ===`r`n" + $Result.StdOut + "`r`n=== STDERR ===`r`n" + $Result.StdErr)
    [System.IO.File]::WriteAllText($Path, $content, $Encoding)
}

Write-Host 'TTM_P05_WINDOWS_CPU_QA=START'
try {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { throw 'PROJECT_ROOT_MISSING' }
    if (-not (Test-Path -LiteralPath (Join-Path $Root '.git'))) { throw 'NOT_A_TTM_GIT_WORKSPACE' }
    if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'PINNED_PYTHON_312_MISSING' }
    if (-not (Test-Path -LiteralPath $WorktreeBase -PathType Container)) { throw 'PROJECT_WORKTREES_DIRECTORY_MISSING' }
    if (-not (Test-Path -LiteralPath $EvidenceDir -PathType Container)) {
        New-Item -ItemType Directory -Path $EvidenceDir -ErrorAction Stop | Out-Null
    }
    foreach($p in @($Worktree, $ReceiptPath, $UnitPath, $IndependentPath)) {
        if (Test-Path -LiteralPath $p) { throw ('OWNED_RUN_PATH_COLLISION: ' + $p) }
    }
    $GitExe = (Get-Command git.exe -ErrorAction Stop).Source
    $actualRoot = Invoke-TTMGit -ArgsList @('rev-parse','--show-toplevel')
    $left = [IO.Path]::GetFullPath($Root).TrimEnd('\').Replace('/','\')
    $right = [IO.Path]::GetFullPath($actualRoot).TrimEnd('\').Replace('/','\')
    if ($left -ine $right) { throw ('WRONG_GIT_TOPLEVEL: ' + $actualRoot) }
    $origin = Invoke-TTMGit -ArgsList @('remote','get-url','origin')
    if ($origin -cne $ExpectedOrigin) { throw ('WRONG_GIT_ORIGIN: ' + $origin) }
    $HeadBefore = Invoke-TTMGit -ArgsList @('rev-parse','HEAD')
    $Receipt.local_head_before = $HeadBefore
    Write-Host ('TTM_P05_LOCAL_HEAD_BEFORE=' + $HeadBefore)

    $v = Invoke-ExactProcess -Exe $Python -Argv @('--version') -Cwd $Root -TimeoutSeconds 20
    if ($v.ExitCode -ne 0) { throw 'PYTHON_VERSION_PROBE_FAILED' }
    $vString = ($v.StdOut + ' ' + $v.StdErr).Trim()
    if ($vString -notmatch '^Python 3\.12\.[0-9]+') { throw ('HOST_NOT_PYTHON_312: ' + $vString) }
    $Receipt.python_version = $vString
    Write-Host ('TTM_P05_PYTHON_VERSION=' + $vString)

    # Always bind remote identities with the project root, never the caller's current directory.
    $remoteMain = Invoke-TTMGit -ArgsList @('ls-remote','origin','refs/heads/main') -TimeoutSeconds 120
    if (($remoteMain -split '\s+')[0] -cne $ExpectedMain) { throw 'REMOTE_MAIN_HEAD_MISMATCH' }
    $remoteBranch = Invoke-TTMGit -ArgsList @('ls-remote','origin',('refs/heads/' + $ExpectedBranch)) -TimeoutSeconds 120
    if (($remoteBranch -split '\s+')[0] -cne $ExpectedHead) { throw 'REMOTE_P05_HEAD_MISMATCH' }
    Write-Host 'TTM_P05_REMOTE_REFS=PASS_EXACT'

    $null = Invoke-TTMGit -ArgsList @('fetch','--no-tags','origin',('refs/heads/' + $ExpectedBranch)) -TimeoutSeconds 180
    $fetchHead = Invoke-TTMGit -ArgsList @('rev-parse','FETCH_HEAD')
    if ($fetchHead -cne $ExpectedHead) { throw 'FETCH_HEAD_SHA_MISMATCH' }
    $null = Invoke-TTMGit -ArgsList @('worktree','add','--detach',$Worktree,$ExpectedHead) -TimeoutSeconds 100
    $OwnedWorktreeAdded = $true
    $wtHead = Invoke-ExactProcess -Exe $GitExe -Argv @('-C',$Worktree,'rev-parse','HEAD') -Cwd $Root -TimeoutSeconds 20
    if ($wtHead.ExitCode -ne 0 -or $wtHead.StdOut.Trim() -cne $ExpectedHead) { throw 'WORKTREE_HEAD_MISMATCH' }

    foreach ($relative in @($ExpectedBlobs.Keys)) {
        $full = Join-Path $Worktree ($relative.Replace('/','\'))
        if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { throw ('MISSING_PINNED_SOURCE: ' + $relative) }
        $blob = Invoke-ExactProcess -Exe $GitExe -Argv @('-C',$Worktree,'hash-object',$relative) -Cwd $Worktree -TimeoutSeconds 20
        if ($blob.ExitCode -ne 0 -or $blob.StdOut.Trim() -cne $ExpectedBlobs[$relative]) {
            throw ('SOURCE_GIT_BLOB_MISMATCH: ' + $relative)
        }
        $hash = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($hash -cne $ExpectedSHA256[$relative]) { throw ('SOURCE_SHA256_MISMATCH: ' + $relative) }
        $Receipt.source_git_blobs[$relative] = $blob.StdOut.Trim()
        $Receipt.source_sha256[$relative] = $hash
    }
    Write-Host 'TTM_P05_SOURCE_EXACT_BLOBS=PASS_4'

    $unit = Invoke-ExactProcess -Exe $Python -Argv @('-B','-m','unittest','discover','-s','tests/p05','-p','test_*.py','-v') -Cwd $Worktree -TimeoutSeconds 120
    Write-ExactLog -Path $UnitPath -Result $unit
    $Receipt.unit_tests.exit_code = $unit.ExitCode
    $unitText = $unit.StdOut + "`n" + $unit.StdErr
    $unitCount = [regex]::Matches($unitText, '(?m)^test_[^\r\n]+\.\.\. ok\s*$').Count
    $Receipt.unit_tests['count'] = $unitCount
    $Receipt.unit_tests.log_sha256 = (Get-FileHash -LiteralPath $UnitPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($unit.ExitCode -ne 0 -or $unitCount -ne 6 -or $unitText -notmatch '(?m)^Ran 6 tests in ' -or $unitText -notmatch '(?m)^OK\s*$') {
        throw ('UNIT_TESTS_FAILED_OR_INCOMPLETE: EXIT_' + $unit.ExitCode + '_COUNT_' + $unitCount)
    }
    $Receipt.unit_tests.pass = $true
    Write-Host 'TTM_P05_WINDOWS_UNIT_TESTS=PASS_6_6'

    $ind = Invoke-ExactProcess -Exe $Python -Argv @('-B','tools/p05/independent_dense_kv_qa.py') -Cwd $Worktree -TimeoutSeconds 120
    Write-ExactLog -Path $IndependentPath -Result $ind
    $Receipt.independent_tests.exit_code = $ind.ExitCode
    $Receipt.independent_tests.log_sha256 = (Get-FileHash -LiteralPath $IndependentPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($ind.ExitCode -ne 0) { throw ('INDEPENDENT_QA_EXIT_' + $ind.ExitCode + ': ' + $ind.StdErr) }
    $report = $ind.StdOut.Trim() | ConvertFrom-Json -ErrorAction Stop
    $validNames = @('explicit_sdpa_incremental_oracle','interleaved_dense_vs_uncached',
                    'independent_kv_byte_accounting','cpu_wall_time_measured_no_speedup_claim')
    if ($report.status -cne 'PASS' -or $report.P01_TEST -cne 'NOT_READ' -or $report.P03_TRAINING -cne 'NOT_EXECUTED' -or
        $report.no_real_corpus -cne $true -or $report.checks.PSObject.Properties.Count -ne 4) {
        throw 'INDEPENDENT_QA_REPORT_SCOPE_OR_STATUS_MISMATCH'
    }
    foreach ($name in $validNames) {
        if ($report.checks.$name -cne $true) { throw ('INDEPENDENT_QA_CHECK_FAILED: ' + $name) }
    }
    $m = $report.measurements
    if ($m.status -cne 'P05_CPU_MEASURED_NO_PERFORMANCE_CLAIM' -or $m.sequence_length -ne 6 -or
        $m.repeats -ne 2 -or $m.allocated_kv_bytes -ne 65536 -or $m.logical_kv_bytes -ne 6144 -or
        $m.dense_ms.Count -ne 2 -or $m.recompute_ms.Count -ne 2) { throw 'BENCHMARK_SCHEMA_OR_KV_BYTES_MISMATCH' }
    foreach ($t in (@($m.dense_ms) + @($m.recompute_ms))) {
        $value = [double]$t
        if ($value -le 0 -or [double]::IsInfinity($value) -or [double]::IsNaN($value)) {
            throw 'BENCHMARK_TIME_INVALID'
        }
    }
    $Receipt.independent_tests['count'] = 4
    $Receipt.independent_tests.pass = $true
    $Receipt.pytorch_version = $report.torch
    $Receipt.benchmark = $m
    Write-Host 'TTM_P05_WINDOWS_INDEPENDENT_QA=PASS_4_4'
    Write-Host ('TTM_P05_KV_ALLOCATED_BYTES=' + $m.allocated_kv_bytes)
    Write-Host ('TTM_P05_KV_USED_LOGICAL_BYTES=' + $m.logical_kv_bytes)
    Write-Host 'TTM_P05_TIMING=MEASURED_NO_SPEEDUP_CLAIM'
    $Receipt.verdict = 'PASS_PENDING_P05_FORMAL_ADJUDICATION'
}
catch {
    $Failure = $_.Exception.Message
    if ($Failure.Length -gt 2400) { $Failure = $Failure.Substring(0,2400) }
    $Receipt.failure = $Failure
    $Receipt.verdict = 'FAIL_OR_INCONCLUSIVE'
    Write-Host ('TTM_P05_FAIL_OR_HOLD=' + $Failure)
}
finally {
    if ($OwnedWorktreeAdded) {
        try {
            # Ownership: this one freshly created, exact-path worktree. No recursive filesystem deletion.
            $list = Invoke-TTMGit -ArgsList @('worktree','list','--porcelain')
            $hasExact = $false
            foreach ($line in ($list -split "`r?`n")) {
                if ($line.StartsWith('worktree ')) {
                    $found = $line.Substring(9).Replace('/','\').TrimEnd('\')
                    if ($found -ieq $Worktree.Replace('/','\').TrimEnd('\')) { $hasExact = $true }
                }
            }
            if (-not $hasExact) { throw 'OWNED_WORKTREE_NOT_REGISTERED_FOR_CLEANUP' }
            $null = Invoke-TTMGit -ArgsList @('worktree','remove',$Worktree) -TimeoutSeconds 90
            if (Test-Path -LiteralPath $Worktree) { throw 'OWNED_WORKTREE_PATH_REMAINS' }
            $Cleanup = 'PASS_EXACT_OWNED_GIT_WORKTREE'
        } catch {
            $Cleanup = 'FAIL_PRESERVE_FOR_MANUAL_REVIEW: ' + $_.Exception.Message
            $Receipt.verdict = 'FAIL_OR_INCONCLUSIVE'
            if (-not $Receipt.failure) { $Receipt.failure = $Cleanup }
        }
    }
    $Receipt.cleanup = $Cleanup
    try {
        if ($GitExe) {
            $HeadAfter = Invoke-TTMGit -ArgsList @('rev-parse','HEAD')
            $Receipt.local_head_after = $HeadAfter
            if ($HeadBefore -and $HeadAfter -cne $HeadBefore) {
                $Receipt.main_changes_by_runner = 'LOCAL_HEAD_CHANGED_UNEXPECTEDLY'
                $Receipt.verdict = 'FAIL_OR_INCONCLUSIVE'
                $Receipt.failure = 'LOCAL_HEAD_CHANGED_UNEXPECTEDLY'
            } else { $Receipt.main_changes_by_runner = 'NONE_HEAD_UNCHANGED' }
        }
    } catch { $Receipt.main_changes_by_runner = 'UNVERIFIED_AFTER_RUN'; $Receipt.verdict = 'FAIL_OR_INCONCLUSIVE' }
    try {
        if (-not (Test-Path -LiteralPath $EvidenceDir -PathType Container)) {
            New-Item -ItemType Directory -Path $EvidenceDir -ErrorAction Stop | Out-Null
        }
        $Receipt.timestamp_utc = [DateTime]::UtcNow.ToString('o')
        $json = $Receipt | ConvertTo-Json -Depth 12
        [System.IO.File]::WriteAllText($ReceiptPath, $json + "`r`n", $Encoding)
        $hash = (Get-FileHash -LiteralPath $ReceiptPath -Algorithm SHA256).Hash
        Write-Host ('TTM_P05_WINDOWS_QA_RECEIPT=' + $ReceiptPath)
        Write-Host ('TTM_P05_WINDOWS_QA_RECEIPT_SHA256=' + $hash)
    } catch { Write-Host ('TTM_P05_RECEIPT_WRITE_FAILED=' + $_.Exception.Message); $Receipt.verdict = 'FAIL_OR_INCONCLUSIVE' }
    Write-Host ('TTM_P05_OWNED_WORKTREE_CLEANUP=' + $Cleanup)
    Write-Host ('TTM_P05_WINDOWS_QA_FINAL=' + $Receipt.verdict)
}
if ($Receipt.verdict -cne 'PASS_PENDING_P05_FORMAL_ADJUDICATION') { exit 1 }
exit 0
