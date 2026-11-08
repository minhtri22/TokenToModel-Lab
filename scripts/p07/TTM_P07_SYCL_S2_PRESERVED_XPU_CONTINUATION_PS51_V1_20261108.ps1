# TTM P07 S2 — SYCL stage-only successor. Defaults to Preview. PowerShell 5.1.
# Original V1 one-shot is already consumed and MUST NOT be re-run or deleted.
[CmdletBinding()]
param(
    [ValidateSet('Preview','Execute')][string]$Mode = 'Preview',
    [string]$ApprovalToken = '',
    [string]$ExpectedP07Head = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Repo = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Origin = 'https://github.com/minhtri22/TokenToModel-Lab.git'
$MainPin = '4731f75cda6aa86b1dd2929b3f10d11fbbed0812'
$P07Ref = 'refs/heads/feature/p07-paged-attention-kernel-design-20261107'
$OriginalP07Head = '4024941b96358828804ea77481e860550c5547a0'
$OriginalRunId = 'P07_GPU_ENABLEMENT_20261108T024525Z_P28364'
$OriginalReceiptSHA = '9A619F41412A6BE87FCD7A307477A148AE80C6BD8801206CFC5791FB7AF3B647'
$OriginalTorchVersion = '2.12.1+xpu'
$ApprovedScope = 'TTM_P07_APPROVE_SYCL_STAGE_ONLY_PRESERVED_XPU_V1'
$CompilerVersion = '2026.2.0'
$IntelConda = 'https://software.repos.intel.com/python/conda/'
$CondaForge = 'https://conda.anaconda.org/conda-forge'
$OneGiB = [double]1073741824
$BaseDGiB = 34.561     # D: free immediately before V1, from the frozen receipt
$UsedByV1GiB = 6.037  # 34.561 - 28.524, fixed cumulative charge
$MaxTotalGiB = 18.000
$MinFreeGiB = 12.000
$RepoRuntime = Join-Path $Repo '_runtime\p07'
$Venv = Join-Path $RepoRuntime 'venv_xpu_cp312'
$Wheels = Join-Path $RepoRuntime 'wheels'
$CondaPkgs = Join-Path $RepoRuntime 'conda_pkgs'
$CondaEnv = Join-Path $RepoRuntime 'sycl_conda'
$TempRoot = Join-Path $RepoRuntime 'tmp'
$Evidence = Join-Path $Repo 'evidence\p07\gpu_enablement'
$OriginalReceipt = Join-Path $Evidence ($OriginalRunId + '.json')
$OriginalLock = Join-Path $Evidence 'P07_GPU_ENABLEMENT_V1_ONE_SHOT.lock'
$SuccessorLock = Join-Path $Evidence 'P07_SYCL_S2_V1_ONE_SHOT.lock'
$CondaExe = Join-Path $env:USERPROFILE 'miniforge3\Scripts\conda.exe'
$CondaBat = Join-Path $env:USERPROFILE 'miniforge3\condabin\conda.bat'
$NewRun = 'P07_SYCL_S2_' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '_P' + $PID
$Scratch = Join-Path $TempRoot ($NewRun + '_owned')
$State = [ordered]@{
    schema='ttm.p07.sycl_s2_preserved_xpu_continuation.v1'; run_id=$NewRun
    source_v1_run_id=$OriginalRunId; source_v1_sha256=$OriginalReceiptSHA.ToLowerInvariant()
    source_v1_final='FAIL_OR_INCONCLUSIVE_NO_AUTORERUN'; source_v1_xpu='PASS_REAL_GPU_COMPUTE'
    mode=$Mode; status='NOT_STARTED'; failure=$null; approval=$false
    repo=$Origin; main_pin=$MainPin; source_branch_head=$OriginalP07Head
    expected_branch_head=$ExpectedP07Head; branch_head_observed=$null
    stages=[ordered]@{source_and_scope='NOT_EXECUTED'; source_wheel_rehash='NOT_EXECUTED'
        preserved_xpu_metadata='NOT_EXECUTED'; conda_download='NOT_EXECUTED'
        conda_archive_rehash='NOT_EXECUTED'; conda_install='NOT_EXECUTED'
        sycl_direct_page_canary='NOT_EXECUTED'}
    original_wheel_count=30; source_wheels_verified=0; compiler_archives=@()
    compiler_version_expected=$CompilerVersion; sycl=$null
    original_lock_preserved=$true; gpu_dispatched_in_successor=$false
    pytorch_downloaded_or_installed_again=$false; torch_canary_rerun=$false
    p01_e0='NOT_RERUN'; p01_test='NOT_READ'; p01_p06='UNCHANGED'
    p07_full_kernel='NOT_EXECUTED'; p08='NOT_OPENED'
    git_fetch_checkout_merge_push=$false; driver_or_system_python_updated=$false
    disk_v1_before_gib=$BaseDGiB; disk_v1_after_gib=28.524
    disk_v1_charged_gib=$UsedByV1GiB; total_budget_gib=$MaxTotalGiB
    remaining_budget_at_v1_end_gib=11.963; min_free_d_gib=$MinFreeGiB
    free_d_before_successor_gib=$null; free_d_after_successor_gib=$null
    log_paths=@(); cleanup='NOT_ATTEMPTED'; receipt_path=$null
}

function Assert-OwnerPath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path).TrimEnd('\')
    $base = [IO.Path]::GetFullPath($Repo).TrimEnd('\') + '\'
    if (-not $full.StartsWith($base, [StringComparison]::OrdinalIgnoreCase)) { throw ('OUTSIDE_PROJECT_SCOPE: ' + $full) }
    $cursor = $full
    while ($cursor.StartsWith($base, [StringComparison]::OrdinalIgnoreCase)) {
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw ('REPARSE_POINT_FORBIDDEN: ' + $cursor) }
        }
        $cursor = [IO.Path]::GetDirectoryName($cursor)
        if ([string]::IsNullOrEmpty($cursor)) { break }
    }
}
function FreeDGiB {
    $d = Get-PSDrive -Name 'D' -ErrorAction Stop
    return [Math]::Round([double]$d.Free / $OneGiB, 3)
}
function Guard-TotalDisk {
    $free = FreeDGiB
    if ($free -lt $MinFreeGiB) { throw ('FREE_DISK_BELOW_12_GIB_' + $free) }
    # Always count the original 6.037 GiB, even if unrelated data has since been removed.
    $observedUsed = [Math]::Max($UsedByV1GiB, ($BaseDGiB - $free))
    if ($observedUsed -gt $MaxTotalGiB) { throw ('TOTAL_18_GIB_BUDGET_EXCEEDED_' + $observedUsed) }
    if (($State.free_d_before_successor_gib - $free) -gt 11.963) { throw 'SUCCESSOR_11_963_GIB_CAP_EXCEEDED' }
}
function NativeRead([string]$Exe, [string[]]$Arguments) {
    $oldPreference = $ErrorActionPreference
    try { $ErrorActionPreference='Continue'; $lines = @(& $Exe @Arguments 2>&1); $exitCode=$LASTEXITCODE }
    finally { $ErrorActionPreference=$oldPreference }
    $out = ($lines | ForEach-Object { $_.ToString() }) -join "`n"
    if ($exitCode -ne 0) { throw ('READ_COMMAND_FAIL_' + $exitCode + ': ' + $out) }
    return $out.Trim()
}
function LoggedCommand([string]$Exe, [string[]]$Arguments, [string]$Tag) {
    $log = Join-Path $Evidence ($NewRun + '.' + $Tag + '.log')
    Assert-OwnerPath $log
    $oldPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference='Continue'
        & $Exe @Arguments *>&1 | Out-File -LiteralPath $log -Encoding utf8
        $exitCode=$LASTEXITCODE
    } finally { $ErrorActionPreference=$oldPreference }
    $State.log_paths += $log
    if ($exitCode -ne 0) { throw ($Tag + '_EXIT_' + $exitCode + ' LOG=' + $log) }
    return $log
}
function WriteUtf8([string]$Path,[string]$Value) {
    Assert-OwnerPath $Path
    [IO.File]::WriteAllText($Path,$Value,(New-Object Text.UTF8Encoding($false)))
}
function NewOwned([string]$Path) {
    Assert-OwnerPath $Path
    if (-not (Test-Path -LiteralPath $Path)) { [void](New-Item -ItemType Directory -Path $Path -ErrorAction Stop) }
    Assert-OwnerPath $Path
}
function ValidateSourceState {
    foreach ($p in @($OriginalReceipt,$OriginalLock,$Venv,$Wheels,$CondaExe,$CondaBat)) {
        if (-not (Test-Path -LiteralPath $p)) { throw ('PRESERVED_SOURCE_MISSING: ' + $p) }
    }
    foreach ($p in @($OriginalReceipt,$OriginalLock,$Venv,$Wheels,$Evidence,$CondaPkgs,$CondaEnv,$TempRoot)) { Assert-OwnerPath $p }
    if (Test-Path -LiteralPath $SuccessorLock) { throw 'S2_ONE_SHOT_ALREADY_CONSUMED_NO_RERUN' }
    if (Test-Path -LiteralPath $CondaEnv) { throw 'S2_CONDA_TARGET_ALREADY_EXISTS_NO_OVERWRITE' }
    $originalHash = (Get-FileHash -LiteralPath $OriginalReceipt -Algorithm SHA256).Hash
    if ($originalHash -cne $OriginalReceiptSHA) { throw 'ORIGINAL_RECEIPT_SHA256_MISMATCH' }
    $v1 = Get-Content -LiteralPath $OriginalReceipt -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($v1.schema -cne 'ttm.p07.single_isolated_gpu_enablement.v1' -or
        $v1.run_id -cne $OriginalRunId -or
        $v1.status -cne 'FAIL_OR_INCONCLUSIVE_NO_AUTORERUN' -or
        $v1.failure -cne 'PYTORCH_XPU_DISK_BUDGET_6_GIB_EXCEEDED') { throw 'SOURCE_V1_VERDICT_MISMATCH' }
    if ($v1.expected_main -cne $MainPin -or $v1.expected_p07_head -cne $OriginalP07Head) { throw 'SOURCE_V1_GIT_PIN_MISMATCH' }
    if ($v1.stages.wheel_download -cne 'PASS_HASHED' -or
        $v1.stages.xpu_install -cne 'PASS_OFFLINE_PINNED_WHEELS' -or
        $v1.stages.xpu_compute -cne 'PASS_REAL_GPU_COMPUTE') { throw 'SOURCE_XPU_NOT_PASS' }
    if ($v1.stages.compiler_download -cne 'NOT_EXECUTED' -or
        $v1.stages.compiler_install -cne 'NOT_EXECUTED' -or
        $v1.stages.sycl_direct_page_index -cne 'NOT_EXECUTED') { throw 'SOURCE_SYCL_ALREADY_RAN' }
    if ($v1.xpu.torch -cne $OriginalTorchVersion -or -not $v1.xpu.available -or $v1.xpu.device_count -lt 1) { throw 'SOURCE_XPU_RUNTIME_STATUS_MISMATCH' }
    if (@($v1.wheels).Count -ne 30) { throw 'SOURCE_WHEEL_COUNT_NOT_30' }
    if ([Math]::Abs(($v1.disk_free_before_gib - $v1.disk_free_after_gib) - $UsedByV1GiB) -gt 0.002) { throw 'SOURCE_DISK_DELTA_MISMATCH' }
    $lockText = [IO.File]::ReadAllText($OriginalLock).Trim()
    $expectedLock = ($OriginalRunId + "`n" + $OriginalP07Head).Replace("`r`n","`n")
    if ($lockText.Replace("`r`n","`n") -cne $expectedLock) { throw 'ORIGINAL_V1_LOCK_MISMATCH' }
    $State.stages.source_and_scope='PASS_SOURCE_V1_BYTE_HASH_LOCK_AND_STAGES'
    return $v1
}

# Strictly read-only phase; no GPU hardware inventory repeated, no imports or GPU dispatch.
if ($PSVersionTable.PSVersion.Major -ne 5) { throw 'PS51_REQUIRED' }
if (-not (Test-Path -LiteralPath (Join-Path $Repo '.git'))) { throw 'REPO_NOT_FOUND' }
$env:GIT_OPTIONAL_LOCKS='0'
$git = (Get-Command git.exe -ErrorAction Stop).Source
$originActual = NativeRead $git @('-C',$Repo,'remote','get-url','origin')
if ($originActual -cne $Origin) { throw 'ORIGIN_MISMATCH' }
$mainRemote = NativeRead $git @('-C',$Repo,'ls-remote','origin','refs/heads/main')
$mainSha = ($mainRemote -split '\s+')[0].ToLowerInvariant()
if ($mainSha -cne $MainPin) { throw ('REMOTE_MAIN_MOVED_' + $mainSha) }
$branchRemote = NativeRead $git @('-C',$Repo,'ls-remote','origin',$P07Ref)
$branchSha = ($branchRemote -split '\s+')[0].ToLowerInvariant()
if ($branchSha -notmatch '^[0-9a-f]{40}$') { throw 'REMOTE_P07_REF_NOT_RESOLVED' }
$State.branch_head_observed = $branchSha
if ($ExpectedP07Head -ne '' -and ($ExpectedP07Head -notmatch '^[0-9a-f]{40}$' -or $ExpectedP07Head -cne $branchSha)) { throw 'P07_BRANCH_PIN_MISMATCH' }
$original = ValidateSourceState
$State.free_d_before_successor_gib = FreeDGiB
$availableBudget = [Math]::Min(11.963, ($State.free_d_before_successor_gib - $MinFreeGiB))
if ($Mode -eq 'Preview') {
    Write-Host 'TTM_P07_S2_MODE=PREVIEW_READONLY'
    Write-Host ('TTM_P07_S2_SOURCE_V1_RUN=' + $OriginalRunId)
    Write-Host 'TTM_P07_S2_SOURCE_XPU=PASS_PRESERVED_NOT_RERUN'
    Write-Host 'TTM_P07_S2_SOURCE_LOCK=PASS_PRESENT_UNCHANGED'
    Write-Host ('TTM_P07_S2_P07_BRANCH_HEAD=' + $branchSha)
    Write-Host ('TTM_P07_S2_FREE_D_GIB=' + $State.free_d_before_successor_gib)
    Write-Host ('TTM_P07_S2_AVAILABLE_BUDGET_GIB=' + [Math]::Round($availableBudget,3))
    Write-Host 'TTM_P07_S2_INSTALL_AND_GPU_DISPATCH=NOT_AUTHORIZED_NOT_EXECUTED'
    Write-Host ('TTM_P07_S2_APPROVAL_REQUIRED=' + $ApprovedScope)
    exit 0
}
if ($ApprovalToken -cne $ApprovedScope) { throw 'S2_EXPLICIT_APPROVAL_MISSING' }
if ($ExpectedP07Head -notmatch '^[0-9a-f]{40}$' -or $ExpectedP07Head -cne $branchSha) { throw 'S2_EXACT_BRANCH_PIN_REQUIRED' }
if ($State.free_d_before_successor_gib -lt 24.0 -or $availableBudget -lt 8.0) { throw 'S2_DISK_START_OR_BUDGET_GUARD_BLOCK' }
$mem = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory
if (($mem / 1MB) -lt 8.0) { throw 'S2_RAM_FREE_BELOW_8_GIB' }
$tracked = NativeRead $git @('-C',$Repo,'-c','core.hooksPath=NUL','status','--porcelain','--untracked-files=no')
if ($tracked.Length -ne 0) { throw 'TRACKED_WORKTREE_CHANGES_BLOCK_S2' }
$vp = Join-Path $Venv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $vp)) { throw 'SOURCE_XPU_PYTHON_MISSING' }
$wheels = @(Get-ChildItem -LiteralPath $Wheels -File | Sort-Object Name)
if ($wheels.Count -ne 30 -or @($wheels | Where-Object {$_.Extension -ne '.whl'}).Count -ne 0) { throw 'SOURCE_WHEELHOUSE_SET_CHANGED' }
# All source integrity checks, including heavy hashing, occur BEFORE consuming successor permit.
foreach ($entry in $original.wheels) {
    $wheel = Join-Path $Wheels $entry.file
    if (-not (Test-Path -LiteralPath $wheel)) { throw ('SOURCE_WHEEL_MISSING_' + $entry.file) }
    $file = Get-Item -LiteralPath $wheel
    if ($file.Length -ne $entry.bytes) { throw ('SOURCE_WHEEL_SIZE_MISMATCH_' + $entry.file) }
    $h = (Get-FileHash -LiteralPath $wheel -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($h -cne $entry.sha256) { throw ('SOURCE_WHEEL_HASH_MISMATCH_' + $entry.file) }
    $State.source_wheels_verified++
}
if ($State.source_wheels_verified -ne 30) { throw 'SOURCE_WHEELS_NOT_FULLY_VERIFIED' }
$State.stages.source_wheel_rehash='PASS_30_EXACT'
# Metadata check only: do not run XPU GPU tensor or reinstall PyTorch.
$pipInfo = NativeRead $vp @('-B','-I','-m','pip','show','torch')
if ($pipInfo -notmatch '(?m)^Version:\s*2\.12\.1\+xpu\s*$') { throw 'PRESERVED_TORCH_VERSION_NOT_XPU' }
$State.stages.preserved_xpu_metadata='PASS_NO_GPU_DISPATCH'
Guard-TotalDisk
# From this point the new S2 permit is consumed even if Conda fails; original V1 lock is immutable.
Assert-OwnerPath $SuccessorLock
$handle=[IO.File]::Open($SuccessorLock,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try {
    $bytes=[Text.Encoding]::UTF8.GetBytes($NewRun+"`n"+$branchSha+"`n"+$OriginalRunId+"`n")
    $handle.Write($bytes,0,$bytes.Length)
} finally { $handle.Dispose() }
$State.approval=$true
$State.status='RUNNING'
try {
    NewOwned $CondaPkgs
    NewOwned $Scratch
    $sentinel = Join-Path $Scratch 'P07_S2_OWNED_SENTINEL.txt'
    WriteUtf8 $sentinel $NewRun
    $env:TEMP=$Scratch
    $env:TMP=$Scratch
    $env:CONDA_PKGS_DIRS=$CondaPkgs
    $env:CONDA_NO_PLUGINS='true'
    $env:CONDA_ENVS_PATH=Join-Path $RepoRuntime 'conda_envs'
    $env:CONDARC=Join-Path $Scratch 'condarc.yml'
    WriteUtf8 $env:CONDARC "channels: []`nshow_channel_urls: false`n"
    $State.stages.conda_download='RUNNING'
    $argsDownload=@('create','--yes','--no-default-packages','--download-only',
      '--prefix',$CondaEnv,'--override-channels','--channel',$IntelConda,'--channel',$CondaForge,
      ('dpcpp_win-64='+$CompilerVersion),('intel-sycl-rt='+$CompilerVersion))
    [void](LoggedCommand $CondaExe $argsDownload 'conda_download_only')
    Guard-TotalDisk
    $archives=@(Get-ChildItem -LiteralPath $CondaPkgs -File -Recurse |
      Where-Object { $_.Name -match '(\.conda|\.tar\.bz2)$' } | Sort-Object FullName)
    if ($archives.Count -lt 1) { throw 'S2_CONDA_ARCHIVES_NOT_PRESENT' }
    foreach ($archive in $archives) {
        $State.compiler_archives += [ordered]@{relative_path=$archive.FullName.Substring($CondaPkgs.Length+1);
            bytes=$archive.Length;sha256=(Get-FileHash -LiteralPath $archive.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
    }
    WriteUtf8 (Join-Path $Evidence ($NewRun+'.conda_archive_lock.json')) ($State.compiler_archives|ConvertTo-Json -Depth 8)
    $State.stages.conda_download='PASS_ARCHIVES_HASHED'
    foreach ($info in $State.compiler_archives) {
        $full=Join-Path $CondaPkgs $info.relative_path
        Assert-OwnerPath $full
        if ((Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant() -cne $info.sha256) { throw 'S2_CONDA_ARCHIVE_HASH_MISMATCH' }
    }
    $State.stages.conda_archive_rehash='PASS_EXACT'
    Guard-TotalDisk
    $State.stages.conda_install='RUNNING'
    $argsInstall=@('create','--yes','--no-default-packages','--offline',
      '--prefix',$CondaEnv,'--override-channels','--channel',$IntelConda,'--channel',$CondaForge,
      ('dpcpp_win-64='+$CompilerVersion),('intel-sycl-rt='+$CompilerVersion))
    [void](LoggedCommand $CondaExe $argsInstall 'conda_offline_install')
    Guard-TotalDisk
    $icx=@(Get-ChildItem -LiteralPath $CondaEnv -File -Filter 'icx.exe' -Recurse)
    if ($icx.Count -ne 1) { throw 'S2_ICX_NOT_UNIQUE_IN_ISOLATED_ENV' }
    $compiler=$icx[0].FullName
    Assert-OwnerPath $compiler
    $State.stages.conda_install='PASS_ISOLATED_COMPILER_PRESENT'
    $State.sycl=[ordered]@{compiler_path=$compiler;expected_version=$CompilerVersion;backend='REQUIRE_LEVEL_ZERO'}
    $source=@'
#include <sycl/sycl.hpp>
#include <cmath>
#include <iostream>
#include <string>
int main() {
  try {
    namespace s=sycl;
    s::queue q{s::gpu_selector_v};
    std::string gpu=q.get_device().get_info<s::info::device::name>();
    std::string vendor=q.get_device().get_info<s::info::device::vendor>();
    if (vendor.find("Intel") == std::string::npos) return 12;
    if (q.get_backend() != s::backend::ext_oneapi_level_zero) return 13;
    constexpr int R=2,T=5,B=2,P=6,H=2,D=3;
    int* table=s::malloc_shared<int>(R*3,q);
    float* pool=s::malloc_shared<float>(P*B*H*D,q);
    float* out=s::malloc_shared<float>(R*T*H*D,q);
    if(!table||!pool||!out) return 14;
    const int pages[R*3]={4,1,5,0,3,2};
    for(int x=0;x<R*3;++x)table[x]=pages[x];
    for(int x=0;x<P*B*H*D;++x)pool[x]=float(x)/16.0f;
    q.parallel_for(s::range<1>(R*T*H*D),[=](s::id<1> id){
      int i=int(id[0]),r=i/(T*H*D),t=(i/(H*D))%T,h=(i/D)%H,d=i%D;
      int page=table[r*3+(t/B)];
      int offset=t%B;
      out[i]=pool[((page*B+offset)*H+h)*D+d];
    }).wait_and_throw();
    float max_err=0;
    for(int r=0;r<R;++r)for(int t=0;t<T;++t)for(int h=0;h<H;++h)for(int d=0;d<D;++d){
      int p=pages[r*3+t/B],off=t%B;
      float want=float(((p*B+off)*H+h)*D+d)/16.0f;
      int i=((r*T+t)*H+h)*D+d;
      float err=std::fabs(out[i]-want);
      if(!std::isfinite(err))return 15;
      if(err>max_err)max_err=err;
      if(err>1e-6f)return 16;
    }
    s::free(table,q);s::free(pool,q);s::free(out,q);
    std::cout<<"TTM_P07_SYCL_S2_DIRECT_PAGE=PASS;backend=level_zero;requests=2;tokens=5;max_abs="<<max_err<<";gpu="<<gpu<<"\n";
    return 0;
  } catch(const std::exception& ex) {std::cerr<<ex.what()<<"\n";return 17;}
}
'@
    $sourceFile=Join-Path $Scratch 'p07_s2_direct_page.cpp'
    $exeFile=Join-Path $Scratch 'p07_s2_direct_page.exe'
    WriteUtf8 $sourceFile $source
    $State.sycl['source_sha256']=(Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash.ToLowerInvariant()
    $vcvars=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat'
    if (-not (Test-Path -LiteralPath $vcvars)) { throw 'S2_VCVARS64_NOT_FOUND' }
    $buildCmd=Join-Path $Scratch 'build_s2.cmd'
    $cmd='@echo off' + "`r`n" + 'call "' + $vcvars + '" >nul' + "`r`n" +
      'if errorlevel 1 exit /b 91' + "`r`n" + 'call "' + $CondaBat + '" activate "' + $CondaEnv + '"' + "`r`n" +
      'if errorlevel 1 exit /b 92' + "`r`n" + '"' + $compiler + '" -fsycl -std=c++17 -O0 "' +
      $sourceFile + '" -o "' + $exeFile + '"' + "`r`n" + 'exit /b %errorlevel%' + "`r`n"
    WriteUtf8 $buildCmd $cmd
    $State.stages.sycl_direct_page_canary='RUNNING_COMPILE'
    [void](LoggedCommand $env:ComSpec @('/d','/c',$buildCmd) 'sycl_compile')
    if (-not (Test-Path -LiteralPath $exeFile)) { throw 'S2_COMPILED_EXE_MISSING' }
    Guard-TotalDisk
    $runCmd=Join-Path $Scratch 'run_s2.cmd'
    $runText='@echo off' + "`r`n" + 'call "' + $CondaBat + '" activate "' + $CondaEnv + '"' + "`r`n" +
      'if errorlevel 1 exit /b 93' + "`r`n" + '"' + $exeFile + '"' + "`r`n" + 'exit /b %errorlevel%' + "`r`n"
    WriteUtf8 $runCmd $runText
    $State.gpu_dispatched_in_successor=$true
    $gpuLog=LoggedCommand $env:ComSpec @('/d','/c',$runCmd) 'sycl_direct_page_canary'
    $gpuText=[IO.File]::ReadAllText($gpuLog)
    if ($gpuText -notmatch 'TTM_P07_SYCL_S2_DIRECT_PAGE=PASS;backend=level_zero;requests=2;tokens=5;max_abs=0(;|\r|\n)') { throw 'S2_DIRECT_PAGE_OUTPUT_MISMATCH' }
    $State.stages.sycl_direct_page_canary='PASS_REAL_GPU_DIRECT_PHYSICAL_PAGES_TWO_REQUESTS'
    Guard-TotalDisk
    $State.status='PASS_SYCL_DIRECT_PAGE_ONLY_P07_G1_PENDING'
    # Delete ONLY the fresh successor scratch with exact ownership; preserved V1 temp/venv/wheels/locks survive.
    if ([IO.File]::ReadAllText($sentinel) -cne $NewRun) { throw 'S2_TEMP_SENTINEL_INVALID' }
    Assert-OwnerPath $Scratch
    Remove-Item -LiteralPath $Scratch -Recurse -Force -ErrorAction Stop
    $State.cleanup='PASS_ONLY_S2_OWNED_SCRATCH_DELETED'
} catch {
    $State.status='FAIL_OR_INCONCLUSIVE_NO_AUTORERUN'
    $State.failure=$_.Exception.Message
    $State.cleanup='PRESERVED_S2_AND_V1_FOR_DIAGNOSIS_NO_DELETION'
} finally {
    $State.free_d_after_successor_gib=FreeDGiB
    $State.receipt_path=Join-Path $Evidence ($NewRun+'.json')
    WriteUtf8 $State.receipt_path ($State | ConvertTo-Json -Depth 12)
    $finalSha=(Get-FileHash -LiteralPath $State.receipt_path -Algorithm SHA256).Hash
    Write-Host ('TTM_P07_SYCL_S2_RECEIPT=' + $State.receipt_path)
    Write-Host ('TTM_P07_SYCL_S2_RECEIPT_SHA256=' + $finalSha)
    Write-Host ('TTM_P07_SYCL_S2_FINAL=' + $State.status)
    Write-Host ('TTM_P07_SYCL_S2_CLEANUP=' + $State.cleanup)
}
if ($State.status -ne 'PASS_SYCL_DIRECT_PAGE_ONLY_P07_G1_PENDING') { exit 1 }
exit 0
