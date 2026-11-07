param(
    [switch]$AllowImagePull,
    [string]$HostPythonPath = 'C:\Users\minht\miniforge3\python.exe'
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Evidence = Join-Path $Root 'evidence\p01'
$Temp = Join-Path $Root 'tmp'
$Bootstrap = Join-Path $Temp 'ttm-p01-wp30-e0-bootstrap-20261107'
$Staging = Join-Path $Temp 'ttm-p01-wp30-e0-stage-20261107'
$Final = Join-Path $Root 'experiments\p01\TTM_P01_F1_WP30_E0_DOCKER_20261107'
$Marker = Join-Path $Evidence 'TTM_P01_F1_WP30_E0_DOCKER_20261107.once'
$Receipt = Join-Path $Evidence 'TTM_P01_F1_WP30_E0_DOCKER_20261107.json'
$Failed = Join-Path $Evidence 'TTM_P01_F1_WP30_E0_DOCKER_FAILURE_20261107.txt'
$EngineSHA = '2f1b85c52b198046ffb472f284488b6d0ce17bcff7697062f6767e6f0ae6a53d'
$CheckerSHA = 'ae07e11942e09cd910231e48f86d0e8d2d541ca80f8abbb6fbdcf2476ccb67c1'
$EngineGzipBase64 = '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'
$CheckerGzipBase64 = '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'
$createdBootstrap = $false
$createdStage = $false
$consumed = $false
$priorEnc = $env:PYTHONIOENCODING
$priorUtf8 = $env:PYTHONUTF8

function Get-GzipBytes([string]$b64) {
    $bytes = [Convert]::FromBase64String($b64)
    $inputStream = [IO.MemoryStream]::new()
    $inputStream.Write($bytes,0,$bytes.Length)
    $inputStream.Position = 0
    $gzip = [IO.Compression.GzipStream]::new($inputStream, [IO.Compression.CompressionMode]::Decompress)
    $output = [IO.MemoryStream]::new()
    try { $gzip.CopyTo($output); return $output.ToArray() }
    finally { $gzip.Dispose(); $inputStream.Dispose(); $output.Dispose() }
}
function Verify-ExecutableBytes([byte[]]$data,[string]$expected) {
    $sha256 = [Security.Cryptography.SHA256]::Create()
    try {
       $h = ([BitConverter]::ToString($sha256.ComputeHash($data))).Replace('-', '').ToLowerInvariant()
       if ($h -cne $expected) { throw 'EMBEDDED_PYTHON_SHA256_MISMATCH' }
    } finally { $sha256.Dispose() }
}
# Docker expected-not-found checks must NOT be invoked through PowerShell's native
# stderr stream when $ErrorActionPreference=Stop (Windows PowerShell 5.1).
# Read-only, bounded, process-level probes avoid altering caller error preferences.
function Invoke-DockerReadProbe([string]$dockerExe,[string]$arguments) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $dockerExe
    $psi.Arguments = $arguments
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    try {
        if (-not $p.Start()) { throw 'DOCKER_READ_PROBE_START_FAILED' }
        $stdout = $p.StandardOutput.ReadToEnd()
        $stderr = $p.StandardError.ReadToEnd()
        if (-not $p.WaitForExit(15000)) {
            try { $p.Kill() } catch {}
            throw 'DOCKER_READ_PROBE_TIMEOUT_15S'
        }
        return @{ ExitCode = [int]$p.ExitCode; StdOut = $stdout; StdErr = $stderr }
    } finally { $p.Dispose() }
}
# V4 recovery: Windows PowerShell 5.1 Start-Process -PassThru can return an unusable/null
# ExitCode. Use a single .NET Process object with async pipe draining to avoid
# native stderr promotion and stdout/stderr deadlocks. No E0 marker is touched.
function Invoke-DockerBounded([string]$dockerExe,[string]$arguments,[int]$timeoutMs) {
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $dockerExe
    $psi.Arguments = $arguments
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = [Text.Encoding]::UTF8
    $psi.StandardErrorEncoding = [Text.Encoding]::UTF8
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    try {
        if (-not $p.Start()) { throw 'DOCKER_BOUNDED_PROCESS_START_FAILED' }
        $stdoutTask = $p.StandardOutput.ReadToEndAsync()
        $stderrTask = $p.StandardError.ReadToEndAsync()
        if (-not $p.WaitForExit($timeoutMs)) {
            try { $p.Kill() } catch {}
            [void]$p.WaitForExit(3000)
            throw ('DOCKER_BOUNDED_PROCESS_TIMEOUT_MS_' + $timeoutMs)
        }
        $p.WaitForExit()
        $o = [string]$stdoutTask.GetAwaiter().GetResult()
        $e = [string]$stderrTask.GetAwaiter().GetResult()
        if ($o.Length -gt 4194304 -or $e.Length -gt 4194304) {
            throw 'DOCKER_BOUNDED_OUTPUT_LIMIT_EXCEEDED'
        }
        return @{ ExitCode = [int]$p.ExitCode; StdOut = $o; StdErr = $e }
    } finally { $p.Dispose() }
}
function Write-OwnedDockerLog([string]$path,[string]$content) {
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($path,$content,$utf8)
}
function Get-DockerErrorTail([string]$raw) {
    if ([string]::IsNullOrWhiteSpace($raw)) { return 'STDERR_EMPTY' }
    $normal = $raw -replace '\r',''
    $tail = ($normal -split '\n' | Where-Object { $_ } | Select-Object -Last 8) -join ' | '
    if ($tail.Length -gt 1400) { return $tail.Substring($tail.Length - 1400) }
    return $tail
}
function Check-DockerImage([string]$dockerExe,[string]$tag) {
    $v = Invoke-DockerReadProbe $dockerExe ('image inspect --format={{.Id}} ' + $tag)
    if ($v.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($v.StdOut)) { return '' }
    return ([string]$v.StdOut).Trim()
}
function Test-DockerContainerName([string]$dockerExe,[string]$name) {
    $v = Invoke-DockerReadProbe $dockerExe ('container inspect ' + $name)
    return ($v.ExitCode -eq 0)
}
function Pull-DockerImageBeforeMarker([string]$dockerExe,[string]$tag) {
    $stdout = Join-Path $Bootstrap 'docker_pull.stdout.txt'
    $stderr = Join-Path $Bootstrap 'docker_pull.stderr.txt'
    $run = Invoke-DockerBounded $dockerExe ('pull ' + $tag) 300000
    Write-OwnedDockerLog $stdout $run.StdOut
    Write-OwnedDockerLog $stderr $run.StdErr
    if ($run.ExitCode -ne 0) {
        throw ('DOCKER_IMAGE_PULL_FAILED_PRE_MARKER_EXIT_' + $run.ExitCode + ': ' + (Get-DockerErrorTail $run.StdErr))
    }
    Write-Host ('TTM_E0_DOCKER_IMAGE_PULL=PASS_PRE_MARKER: ' + $tag)
}
function Check-DockerGuardCapability([string]$dockerExe,[string]$tag,[string]$mount,[string]$name) {
    $stdout = Join-Path $Bootstrap 'docker_probe.stdout.txt'
    $stderr = Join-Path $Bootstrap 'docker_probe.stderr.txt'
    $params = @('run','--rm','--pull=never','--name',$name,
       '--network=none','--cpus=4','--memory=4g','--memory-swap=4g',
       '--pids-limit=96','--read-only','--cap-drop=ALL',
       '--security-opt=no-new-privileges','--ulimit','fsize=33554432:33554432',
       '--tmpfs','/tmp:rw,nosuid,noexec,size=128m',
       '--mount',$mount,$tag,'python','-I','-B','--version')
    $run = Invoke-DockerBounded $dockerExe ([string]::Join(' ',$params)) 90000
    Write-OwnedDockerLog $stdout $run.StdOut
    Write-OwnedDockerLog $stderr $run.StdErr
    if ($run.ExitCode -ne 0) {
        throw ('DOCKER_GUARD_CAPABILITY_FAILED_PRE_MARKER_EXIT_' + $run.ExitCode + ': ' + (Get-DockerErrorTail $run.StdErr))
    }
    $version = $run.StdOut.Trim()
    if ($version -notmatch '^Python 3\.12\.') { throw ('DOCKER_PYTHON_VERSION_NOT_312_PRE_MARKER: ' + $version) }
    Write-Host ('TTM_E0_DOCKER_PYTHON_VERSION=' + $version)
}

function Invoke-DockerWorker([string]$dockerExe,[string]$image,[string]$imageID,[string]$label) {
    $name = 'ttm-p01-wp30-e0-' + $label + '-20261107'
    $current = Check-DockerImage $dockerExe $image
    if ($current -cne $imageID) { throw 'DOCKER_IMAGE_CHANGED_DURING_E0' }
    $worker = Join-Path $Staging $label
    [void][IO.Directory]::CreateDirectory($worker)
    $stdout = Join-Path $worker 'stdout.txt'
    $stderr = Join-Path $worker 'stderr.txt'
    $mountInput = 'type=bind,source=' + (Join-Path $Staging 'train_only') + ',target=/train,readonly'
    $mountEngine = 'type=bind,source=' + (Join-Path $Staging 'engine') + ',target=/engine,readonly'
    $mountOutput = 'type=bind,source=' + $worker + ',target=/out'
    $params = @('run','--rm','--pull=never','--name',$name,
       '--network=none','--cpus=4','--memory=4g','--memory-swap=4g',
       '--pids-limit=96','--read-only','--cap-drop=ALL',
       '--security-opt=no-new-privileges','--ulimit','fsize=33554432:33554432',
       '--tmpfs','/tmp:rw,nosuid,noexec,size=128m',
       '--mount',$mountInput,'--mount',$mountEngine,'--mount',$mountOutput,
       '--workdir','/engine',$image,'python','-I','-B','/engine/f1_e0_integrated.py',
       'worker','--input','/train','--out','/out')
    # Exact project paths are space-free; argv and all limits remain unchanged.
    $argString = [string]::Join(' ', $params)
    try {
       $run = Invoke-DockerBounded $dockerExe $argString 600000
    } catch {
       # A timeout may leave the Docker container alive after the client exits.
       # Only the exact E0-owned container name may be targeted for recovery.
       if ($_.Exception.Message -like '*DOCKER_BOUNDED_PROCESS_TIMEOUT*') {
           try { [void](Invoke-DockerReadProbe $dockerExe ('kill ' + $name)) } catch {}
       }
       throw
    }
    Write-OwnedDockerLog $stdout $run.StdOut
    Write-OwnedDockerLog $stderr $run.StdErr
    if ($run.ExitCode -ne 0) {
       throw ('DOCKER_WORKER_FAILED_' + $label + '_EXIT_' + $run.ExitCode + ': ' + (Get-DockerErrorTail $run.StdErr))
    }
    Write-Host ('TTM_E0_DOCKER_WORKER_' + $label.ToUpperInvariant() + '=PASS')
    $run.StdOut -split "`n" | Where-Object { $_ } | ForEach-Object { Write-Host $_ }
}

try {
    Write-Host 'TTM_P01_F1_E0_DOCKER_PRECHECK=START'
    if (-not (Test-Path -LiteralPath (Join-Path $Root '.git'))) { throw 'PROJECT_GIT_NOT_FOUND' }
    $git = (Get-Command git.exe -ErrorAction Stop).Source
    $origin = (& $git -C $Root remote get-url origin 2>&1)
    if ($LASTEXITCODE -ne 0) { throw 'GIT_ORIGIN_READ_FAILED' }
    $origin = ([string]$origin).Trim()
    if ($origin -cnotmatch '^(https://github\.com/minhtri22/TokenToModel-Lab(?:\.git)?|git@github\.com:minhtri22/TokenToModel-Lab\.git)$') {
        throw ('WRONG_GIT_ORIGIN: ' + $origin)
    }
    foreach ($p in @($Bootstrap,$Staging,$Final,$Marker,$Receipt,$Failed)) {
       if (Test-Path -LiteralPath $p) { throw ('ONE_SHOT_OR_OUTPUT_ALREADY_EXISTS: ' + $p) }
    }
    $py = $HostPythonPath
    if (-not (Test-Path -LiteralPath $py)) { throw 'MINIFORGE_PYTHON_NOT_FOUND' }
    # Host 3.12 is an explicit owner preference. Do not downgrade the shared
    # Miniforge base; allow selection of a separately installed Python 3.12.
    # Windows PowerShell 5.1 removes nested quotes in native argv for Python -c.
    # Use a flag-only version query, avoiding Python code and all inner quoting.
    $hostPyVersion = (& $py --version)
    if ($LASTEXITCODE -ne 0) { throw 'HOST_PYTHON_VERSION_CHECK_FAILED_NO_MARKER' }
    $hostPyVersion = ([string]$hostPyVersion).Trim()
    Write-Host ('TTM_E0_HOST_PYTHON_VERSION=' + $hostPyVersion)
    if ($hostPyVersion -notmatch '^Python 3\.12\.[0-9]+(?:\s|$)') {
        throw ('HOST_PYTHON_NOT_312_NO_MARKER: ' + $hostPyVersion + '; use -HostPythonPath with an existing Python 3.12 executable')
    }
    $env:PYTHONIOENCODING = 'utf-8:strict'; $env:PYTHONUTF8 = '1'
    [void][IO.Directory]::CreateDirectory($Temp)
    [void][IO.Directory]::CreateDirectory($Evidence)
    [void][IO.Directory]::CreateDirectory($Bootstrap)
    $createdBootstrap = $true
    $engine = Join-Path $Bootstrap 'f1_e0_integrated.py'
    $checker = Join-Path $Bootstrap 'independent_e0_checker.py'
    $engineBytes = Get-GzipBytes $EngineGzipBase64
    $qaBytes = Get-GzipBytes $CheckerGzipBase64
    Verify-ExecutableBytes $engineBytes $EngineSHA
    Verify-ExecutableBytes $qaBytes $CheckerSHA
    [IO.File]::WriteAllBytes($engine,$engineBytes)
    [IO.File]::WriteAllBytes($checker,$qaBytes)
    & $py -B $engine selftest
    if ($LASTEXITCODE -ne 0) { throw 'ENGINE_OFFLINE_SELFTEST_FAILED' }
    & $py -B $engine preflight --root $Root
    if ($LASTEXITCODE -ne 0) { throw 'F1_DATA_PRECHECK_FAILED_NO_MARKER' }
    $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
    if ([int64]$os.FreePhysicalMemory * 1024 -lt 8589934592) { throw 'RAM_FREE_BELOW_8GIB_NO_MARKER' }
    $drive = [IO.DriveInfo]::new('D')
    if ([int64]$drive.AvailableFreeSpace -lt 17179869184) { throw 'DISK_FREE_BELOW_16GIB_NO_MARKER' }
    $dockerExe = (Get-Command docker.exe -ErrorAction Stop).Source
    $dockerMode = (& $dockerExe info --format '{{.OSType}}' 2>&1)
    if ($LASTEXITCODE -ne 0 -or ([string]$dockerMode).Trim() -cne 'linux') {
        throw 'DOCKER_LINUX_ENGINE_UNAVAILABLE_NO_MARKER'
    }
    $image = 'python:3.12-slim'
    $imageId = Check-DockerImage $dockerExe $image
    if (-not $imageId) {
        if (-not $AllowImagePull) { throw 'DOCKER_IMAGE_NOT_CACHED_NO_MARKER: docker pull python:3.12-slim (or rerun -AllowImagePull)' }
        Pull-DockerImageBeforeMarker $dockerExe $image
        $imageId = Check-DockerImage $dockerExe $image
        if (-not $imageId) { throw 'DOCKER_IMAGE_STILL_MISSING_NO_MARKER' }
    }
    Write-Host ('TTM_E0_DOCKER_IMAGE_ID=' + $imageId)
    # No-science Docker capability check before consuming the E0 marker.
    $probeName = 'ttm-p01-wp30-e0-capability-20261107'
    if (Test-DockerContainerName $dockerExe $probeName) { throw 'DOCKER_PROBE_NAME_OCCUPIED_NO_MARKER' }
    $probeDir = Join-Path $Bootstrap 'probe'
    [void][IO.Directory]::CreateDirectory($probeDir)
    $probeMount = 'type=bind,source=' + $probeDir + ',target=/probe,readonly'
    Check-DockerGuardCapability $dockerExe $image $probeMount $probeName
    Write-Host 'TTM_E0_DOCKER_GUARD_CAPABILITY_PREFLIGHT=PASS_NO_SCIENCE'
    foreach ($label in @('a','b')) {
       $name = 'ttm-p01-wp30-e0-' + $label + '-20261107'
       if (Test-DockerContainerName $dockerExe $name) { throw ('DOCKER_CONTAINER_NAME_OCCUPIED_NO_MARKER: ' + $name) }
    }
    # Marker is created ONLY after frozen-source, fixture, resource and cached-image preflight.
    $f = [IO.File]::Open($Marker,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try {
       $m = [Text.Encoding]::ASCII.GetBytes('TTM_P01_F1_WP30_E0_DOCKER_SINGLE_SHOT_20261107')
       $f.Write($m,0,$m.Length)
    } finally { $f.Dispose() }
    $consumed = $true
    Write-Host 'TTM_P01_E0_ONE_SHOT_MARKER_CREATED=YES'
    & $py -B $engine stage --root $Root --staging $Staging
    $createdStage = Test-Path -LiteralPath $Staging
    if ($LASTEXITCODE -ne 0) { throw 'SOURCE_STAGE_FAILED_AFTER_MARKER' }
    Invoke-DockerWorker $dockerExe $image $imageId 'a'
    Invoke-DockerWorker $dockerExe $image $imageId 'b'
    & $py -B $engine adjudicate --root $Root --staging $Staging --final $Final
    if ($LASTEXITCODE -ne 0) { throw 'E0_INTEGRATED_ADJUDICATION_FAILED' }
    & $py -B $checker --root $Root --result $Final
    if ($LASTEXITCODE -ne 0) { throw 'INDEPENDENT_E0_QA_FAILED' }
    if (Test-Path -LiteralPath $Receipt) { throw 'RECEIPT_COLLISION' }
    [IO.File]::Copy((Join-Path $Final 'e0_integrated_result.json'),$Receipt,$false)
    Write-Host ('TTM_P01_E0_MERGES_SHA256=' + (Get-FileHash (Join-Path $Final 'merges.ttmbpe') -Algorithm SHA256).Hash)
    Write-Host ('TTM_P01_E0_RECEIPT_SHA256=' + (Get-FileHash $Receipt -Algorithm SHA256).Hash)
    Write-Host 'TTM_P01_E0_INTEGRATED_QA=PASS_PENDING_FORMAL_P01_CLOSURE'
    Write-Host 'TTM_P02_P03_P04=NOT_OPENED_PENDING_P01_CLOSURE'
    Write-Host ('TTM_P01_E0_OUTPUT=' + $Final)
} catch {
    $msg = $_.Exception.Message
    if ($consumed) {
        try {
           $f = [IO.File]::Open($Failed,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
           try {
               $raw = [Text.Encoding]::UTF8.GetBytes('E0_CONSUMED_FAIL: ' + $msg)
               $f.Write($raw,0,$raw.Length)
           } finally { $f.Dispose() }
        } catch { Write-Host 'TTM_E0_FAILURE_RECEIPT_WRITE_FAILED' }
    }
    Write-Host ('TTM_P01_E0_FAIL_OR_HOLD=' + $msg)
    throw
} finally {
    $env:PYTHONIOENCODING = $priorEnc; $env:PYTHONUTF8 = $priorUtf8
    # Delete ONLY the two exact temp paths newly created by this script inside the TTM workspace.
    if ($createdBootstrap -and $Bootstrap.StartsWith(($Temp + '\'),[StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $Bootstrap)) {
        Remove-Item -LiteralPath $Bootstrap -Recurse -Force
    }
    if ($createdStage -and $Staging.StartsWith(($Temp + '\'),[StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $Staging)) {
        Remove-Item -LiteralPath $Staging -Recurse -Force
    }
    Write-Host 'TTM_P01_E0_OWNED_TEMP_CLEANUP=COMPLETE_SCOPED'
}
