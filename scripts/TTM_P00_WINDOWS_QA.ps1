# TokenToModel-Lab P00 Windows checkout and local QA.
# Scope: exact workplace only. No delete, no force, no merge, no push.
[CmdletBinding()]
param([string]$PythonExe = 'C:\Users\minht\miniforge3\python.exe')
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Remote = 'https://github.com/minhtri22/TokenToModel-Lab.git'
$Branch = 'feature/p00-source-docs-diagrams-20261105'
$BaselineMain = 'f2ed098b033431924a3cbabdc9af89d7bbd7b378'
$RequiredSourceAncestor = '5b8ca8acf2365a9a16a1155fcf3f62c137368b45'
$WorktreesRoot = Join-Path $Root 'worktrees'
$Worktree = Join-Path $WorktreesRoot 'p00-source-docs-diagrams-20261105'
$oldEnv = @{}

function Assert-PathSafety([string]$path) {
    $canon = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    $full = [IO.Path]::GetFullPath($path).TrimEnd('\')
    if ($full -ine $canon -and -not $full.StartsWith(($canon + '\'), [StringComparison]::OrdinalIgnoreCase)) {
        throw "TTM_PATH_ESCAPE: $full"
    }
    $cur = $full
    while (-not [string]::IsNullOrWhiteSpace($cur)) {
        if (Test-Path -LiteralPath $cur) {
            $item = Get-Item -LiteralPath $cur -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "TTM_REPARSE_POINT_REJECTED: $cur"
            }
        }
        $parent = [IO.Path]::GetDirectoryName($cur)
        if ([string]::IsNullOrWhiteSpace($parent) -or $parent -ieq $cur) { break }
        $cur = $parent
    }
    return $full
}
function Invoke-TtmGit([string[]]$GitArgs) {
    $output = @(& $script:GitExe -C $Root @GitArgs)
    if ($LASTEXITCODE -ne 0) { throw "TTM_GIT_FAILED($LASTEXITCODE): $($gitArgs -join ' ') $($output -join ' ')" }
    return $output
}
function Invoke-TtmGitWorktree([string[]]$GitArgs) {
    $output = @(& $script:GitExe -C $Worktree @GitArgs)
    if ($LASTEXITCODE -ne 0) { throw "TTM_GIT_WORKTREE_FAILED($LASTEXITCODE): $($gitArgs -join ' ') $($output -join ' ')" }
    return $output
}
try {
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { throw "TTM_ROOT_MISSING: $Root" }
    $null = Assert-PathSafety $Root
    $null = Assert-PathSafety $WorktreesRoot
    $null = Assert-PathSafety $Worktree
    $gitCommand = Get-Command -Name 'git.exe' -CommandType Application -ErrorAction SilentlyContinue
    if (-not $gitCommand) { throw 'TTM_GIT_UNAVAILABLE' }
    $script:GitExe = $gitCommand.Source
    if (-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) { throw "TTM_PYTHON_UNAVAILABLE: $PythonExe" }

    foreach ($key in @('TEMP','TMP','TMPDIR','PIP_CACHE_DIR','PYTHONPYCACHEPREFIX',
                      'PYTHONDONTWRITEBYTECODE','TORCH_HOME','HF_HOME',
                      'XDG_CACHE_HOME','MPLCONFIGDIR','TRITON_CACHE_DIR')) {
        $oldEnv[$key] = [Environment]::GetEnvironmentVariable($key,'Process')
    }
    $Temp = Join-Path $Root 'tmp'
    $Cache = Join-Path $Root 'cache'
    $null = Assert-PathSafety $Temp
    $null = Assert-PathSafety $Cache
    [IO.Directory]::CreateDirectory($Temp) | Out-Null
    [IO.Directory]::CreateDirectory($Cache) | Out-Null
    $env:TEMP = $Temp; $env:TMP = $Temp; $env:TMPDIR = $Temp
    $env:PIP_CACHE_DIR = $Cache
    $env:PYTHONPYCACHEPREFIX = Join-Path $Cache 'pycache'
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $env:TORCH_HOME = $Cache; $env:HF_HOME = $Cache
    $env:XDG_CACHE_HOME = $Cache; $env:MPLCONFIGDIR = $Cache
    $env:TRITON_CACHE_DIR = $Cache

    # Read-only remote identity check before any local Git changes.
    $mainRef = @(& $script:GitExe ls-remote --heads $Remote 'refs/heads/main')
    if ($LASTEXITCODE -ne 0 -or $mainRef.Count -ne 1 -or
        (($mainRef[0] -split '\s+')[0] -ine $BaselineMain)) { throw 'TTM_REMOTE_MAIN_PIN_MISMATCH' }
    $featureRef = @(& $script:GitExe ls-remote --heads $Remote ("refs/heads/" + $Branch))
    if ($LASTEXITCODE -ne 0 -or $featureRef.Count -ne 1) { throw 'TTM_REMOTE_P00_BRANCH_MISSING' }

    $gitPath = Join-Path $Root '.git'
    if (-not (Test-Path -LiteralPath $gitPath)) {
        if (Test-Path -LiteralPath (Join-Path $Root 'README.md')) {
            throw 'TTM_UNTRACKED_README_PRESENT_BEFORE_GIT_INITIALIZATION'
        }
        $allowed = @('.remotemcp','worktrees','TTM_P00_READY.zip','_import','tmp','_tmp','cache','evidence','runs','checkpoints','datasets')
        foreach ($p in (Get-ChildItem -LiteralPath $Root -Force)) {
            if ($p.Name -notin $allowed) { throw "TTM_UNKNOWN_ROOT_ENTRY: $($p.Name)" }
            $null = Assert-PathSafety $p.FullName
        }
        $null = Invoke-TtmGit -GitArgs @('init','-b','main')
        $null = Invoke-TtmGit -GitArgs @('remote','add','origin',$Remote)
        Write-Host 'TTM_LOCAL_GIT_INITIALIZED=YES'
    }
    $top = ((Invoke-TtmGit -GitArgs @('rev-parse','--show-toplevel')) | Select-Object -Last 1).Trim().Replace('/', '\')
    if ($top.TrimEnd('\') -ine $Root.TrimEnd('\')) { throw "TTM_GIT_TOPLEVEL_MISMATCH: $top" }
    $origin = ((Invoke-TtmGit -GitArgs @('remote','get-url','origin')) | Select-Object -Last 1).Trim()
    if ($origin -cne $Remote) { throw "TTM_GIT_ORIGIN_MISMATCH: $origin" }
    $null = Invoke-TtmGit -GitArgs @('fetch','--no-tags','origin','main',$Branch)
    $mainRemote = ((Invoke-TtmGit -GitArgs @('rev-parse','origin/main')) | Select-Object -Last 1).Trim()
    if ($mainRemote -ine $BaselineMain) { throw 'TTM_FETCHED_MAIN_PIN_MISMATCH' }
    $null = Invoke-TtmGit -GitArgs @('switch','main')
    $mainLocal = ((Invoke-TtmGit -GitArgs @('rev-parse','HEAD')) | Select-Object -Last 1).Trim()
    if ($mainLocal -ine $BaselineMain) { throw 'TTM_LOCAL_MAIN_NOT_AT_BOOTSTRAP_PIN' }
    $dirty = @(Invoke-TtmGit -GitArgs @('status','--porcelain','--untracked-files=no'))
    if ($dirty.Count -ne 0) { throw 'TTM_LOCAL_MAIN_TRACKED_CHANGES_PRESENT' }
    $featureHead = ((Invoke-TtmGit -GitArgs @('rev-parse',("origin/" + $Branch))) | Select-Object -Last 1).Trim()
    & $script:GitExe -C $Root merge-base --is-ancestor $RequiredSourceAncestor $featureHead
    if ($LASTEXITCODE -ne 0) { throw 'TTM_FEATURE_SOURCE_ANCESTOR_MISMATCH' }
    if (Test-Path -LiteralPath $Worktree) { throw "TTM_WORKTREE_ALREADY_EXISTS: $Worktree" }
    [IO.Directory]::CreateDirectory($WorktreesRoot) | Out-Null
    $null = Assert-PathSafety $WorktreesRoot
    $null = Invoke-TtmGit -GitArgs @('worktree','add','-b',$Branch,$Worktree,("origin/" + $Branch))
    $null = Assert-PathSafety $Worktree
    $actualHead = ((Invoke-TtmGitWorktree -GitArgs @('rev-parse','HEAD')) | Select-Object -Last 1).Trim()
    if ($actualHead -ine $featureHead) { throw 'TTM_WORKTREE_HEAD_MISMATCH' }
    Write-Host "TTM_P00_SOURCE_HEAD=$actualHead"

    $runId = 'TTM_P00_WINDOWS_LOCAL_QA_' + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $Evidence = Join-Path $Root ("evidence\p00\" + $runId)
    $null = Assert-PathSafety $Evidence
    [IO.Directory]::CreateDirectory($Evidence) | Out-Null
    $tests = @(
        @{ name='reference'; args=@('-m','unittest','discover','-s','reference/phase0','-p','test_reference.py','-v') },
        @{ name='records'; args=@('-m','unittest','discover','-s','tests','-p','test_*.py','-v') }
    )
    $results = @()
    foreach ($test in $tests) {
        $out = Join-Path $Evidence ($test.name + '.stdout.txt')
        $err = Join-Path $Evidence ($test.name + '.stderr.txt')
        $proc = Start-Process -FilePath $PythonExe -WorkingDirectory $Worktree -ArgumentList $test.args `
            -RedirectStandardOutput $out -RedirectStandardError $err -PassThru -Wait -NoNewWindow
        $results += @{
            name=$test.name; exit_code=$proc.ExitCode;
            stdout_sha256=(Get-FileHash -LiteralPath $out -Algorithm SHA256).Hash.ToLowerInvariant();
            stderr_sha256=(Get-FileHash -LiteralPath $err -Algorithm SHA256).Hash.ToLowerInvariant()
        }
        Write-Host ("TTM_P00_TEST_{0}_EXIT={1}" -f $test.name.ToUpperInvariant(),$proc.ExitCode)
    }
    $qaPass = @($results | Where-Object { $_.exit_code -ne 0 }).Count -eq 0
    $config = Join-Path $Worktree 'configs\phase0_reference.json'
    $model = Join-Path $Worktree 'reference\phase0\model.py'
    $receipt = @{
        schema='ttm.p00.windows_local_qa.v1';run_id=$runId;
        utc=(Get-Date).ToUniversalTime().ToString('o');
        repository=$Remote;workspace=$Root;branch=$Branch;
        source_commit=$actualHead;main_baseline=$BaselineMain;
        python=$PythonExe;
        config_sha256=(Get-FileHash -LiteralPath $config -Algorithm SHA256).Hash.ToLowerInvariant();
        model_sha256=(Get-FileHash -LiteralPath $model -Algorithm SHA256).Hash.ToLowerInvariant();
        tests=$results;local_tests_pass=$qaPass;
        independent_qa='NOT_PERFORMED';scientific_training='NOT_PERFORMED';
        merge_authorized=$false
    }
    $receiptPath = Join-Path $Evidence 'QA_RECEIPT.json'
    [IO.File]::WriteAllText($receiptPath,($receipt|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
    Write-Host "TTM_P00_WINDOWS_LOCAL_TESTS=$(if ($qaPass) { 'PASS' } else { 'FAIL' })"
    Write-Host 'TTM_P00_INDEPENDENT_QA=PENDING'
    Write-Host 'TTM_P00_MERGE=NOT_AUTHORIZED'
    Write-Host "TTM_P00_QA_RECEIPT=$receiptPath"
    if (-not $qaPass) { throw 'TTM_P00_LOCAL_QA_FAILED_EVIDENCE_PRESERVED' }
} finally {
    foreach ($key in $oldEnv.Keys) {
        [Environment]::SetEnvironmentVariable($key,$oldEnv[$key],'Process')
    }
}
