# A0D owner-local OFFLINE Windows Python 3.12 + official Transformers 5.19 readback.
# Installs dependencies ONLY in a NEW venv inside TTM _tmp; uses installed torch.
# No download, no model weights, no training, no forward, no Git changes.
[CmdletBinding()]
param(
    [string]$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$WheelsZip = '',
    [string]$OwnerReceipt = '',
    [string]$T1Manifest = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$CanonicalRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab'
if (-not (Test-Path -LiteralPath $Root -PathType Container)) { throw 'HOLD_TTM_ROOT_NOT_FOUND' }
$Root = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
if ($Root -ine $CanonicalRoot) { throw 'HOLD_NONCANONICAL_ROOT' }

$Tmp = Join-Path $Root '_tmp'
$Previous = Join-Path $Tmp 'ttm_gemma2_a0d_owner_readback'
$OutDir = Join-Path $Root 'artifacts\qa\ttm-embeddinggemma2\a0d_owner_local_readback'
$ArchiveName = 'TTM_GEMMA2_A0D_WINDOWS_PY312_TRANSFORMERS_5_19_OFFLINE_WHEELS_20261111.zip'
if (-not $WheelsZip) { $WheelsZip = Join-Path $Tmp $ArchiveName }
if (-not $OwnerReceipt) {
    $OwnerReceipt = Join-Path $OutDir 'TTM_GEMMA2_A0D_OWNER_READBACK_20261111_103151_259.json'
}
$ExpectedArchiveSha = '17b292711ec27df09513c51013fd654155de9fe0a24b3534f56cd43b3b3a8b44'
$ExpectedOwnerReceiptSha = 'ACAFB99EDEBB9979F5BA5872B459B3F1C00978A44D0142C6B21F49367D524B90'
$ExpectedPythonBlob = '6258b9f824e3ff8aabb1baba899f2a37894e8599'
$ExpectedT1Sha = 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
$ExpectedSources = [ordered]@{
    'config.json' = 'b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3'
    'tokenizer.json' = '4d777ef5bdc1aa36227abdfb77c3e49e7b9c892d16e1b6bda41c393504828be4'
    'tokenizer_config.json' = '17bd5d6e9364ca49a534e1502076593317c298d4a663623091ed45388f004874'
}
$SourceSizes = @{
    'config.json' = 4455L; 'tokenizer.json' = 32170510L; 'tokenizer_config.json' = 1599L
}
$PipBase = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$SourcePy = Join-Path $Previous 'ttm_a0d_pinned_official_source_readback.py'
New-Item -ItemType Directory -Force -Path $Tmp,$OutDir | Out-Null
$Session = Join-Path $Tmp ('ttm_gemma2_a0d_isolated_offline_' + [guid]::NewGuid().ToString('N'))
$VenvDir = Join-Path $Session 'venv'
$WheelDest = Join-Path $Session 'wheels'
$Status = 'HOLD_NOT_RUN'
$HoldReason = $null
$Version = $null
$ModelResult = $null
$ReadbackExit = $null
$PipExit = $null
$DonorDir = $null
$ArchiveHash = $null
$FilesVerified = @()

try {
    if (-not (Test-Path -LiteralPath $WheelsZip -PathType Leaf)) { throw 'HOLD_OFFLINE_WHEELHOUSE_ZIP_MISSING' }
    $WheelsZip = (Resolve-Path -LiteralPath $WheelsZip).Path
    if (-not $WheelsZip.StartsWith($Tmp + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'HOLD_WHEELHOUSE_MUST_BE_TTM_TMP'
    }
    $ArchiveHash = (Get-FileHash -LiteralPath $WheelsZip -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($ArchiveHash -ne $ExpectedArchiveSha) { throw 'HOLD_WHEELHOUSE_ARTIFACT_SHA256' }
    Write-Output 'A0D_WHEELHOUSE_ARCHIVE_SHA=PASS'

    if (-not (Test-Path -LiteralPath $OwnerReceipt -PathType Leaf)) { throw 'HOLD_PREVIOUS_OWNER_RECEIPT_NOT_FOUND' }
    if ((Get-FileHash -LiteralPath $OwnerReceipt -Algorithm SHA256).Hash -ne $ExpectedOwnerReceiptSha) {
        throw 'HOLD_PREVIOUS_OWNER_RECEIPT_SHA256_CHANGED'
    }
    $Prev = Get-Content -LiteralPath $OwnerReceipt -Raw | ConvertFrom-Json
    if ($Prev.status -ne 'HOLD_OFFICIAL_CPU_SOURCE_READBACK_FAILED' -or
        $Prev.official_python_report.gate -ne 'OFFICIAL_CLASS_IMPORT_ImportError' -or
        $Prev.t1_manifest_found -ne $true) {
        throw 'HOLD_PREVIOUS_OWNER_RECEIPT_NOT_EXPECTED'
    }
    $DonorDir = [string]$Prev.donor_source_dir
    $DonorDir = (Resolve-Path -LiteralPath $DonorDir).Path
    if (-not $DonorDir.StartsWith($Previous + '\',[System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'HOLD_DONOR_SOURCE_OUTSIDE_A0D_TMP'
    }
    foreach ($Name in @('config.json','tokenizer.json','tokenizer_config.json')) {
        $P = Join-Path $DonorDir $Name
        if (-not (Test-Path -LiteralPath $P -PathType Leaf)) { throw ('HOLD_DONOR_MISSING_' + $Name) }
        if ((Get-Item -LiteralPath $P).Length -ne $SourceSizes[$Name] -or
            (Get-FileHash -LiteralPath $P -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedSources[$Name]) {
            throw ('HOLD_DONOR_SOURCE_PIN_' + $Name)
        }
        Write-Output ('A0D_DONOR_' + $Name + '=PASS_SHA256')
    }
    $FilesVerified = @('config.json','tokenizer.json','tokenizer_config.json')

    if (-not (Test-Path -LiteralPath $SourcePy -PathType Leaf)) { throw 'HOLD_CANONICAL_PYTHON_SOURCE_NOT_CACHED' }
    $Blob = (& git hash-object -- $SourcePy | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $Blob -ne $ExpectedPythonBlob) { throw 'HOLD_CANONICAL_PYTHON_SOURCE_GIT_BLOB' }

    if (-not $T1Manifest) {
        $FoundT1 = Get-ChildItem -LiteralPath $Root -Recurse -File -Filter 'T1_BPE2048_REAL_TRAIN_MANIFEST.json' -ErrorAction SilentlyContinue
        foreach ($Entry in $FoundT1) {
            if ((Get-FileHash -LiteralPath $Entry.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -eq $ExpectedT1Sha) {
                $T1Manifest = $Entry.FullName; break
            }
        }
    }
    if (-not $T1Manifest -or -not (Test-Path -LiteralPath $T1Manifest -PathType Leaf) -or
        (Get-FileHash -LiteralPath $T1Manifest -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedT1Sha) {
        throw 'HOLD_T1_EXACT_MANIFEST_NOT_FOUND'
    }
    Write-Output 'A0D_T1_PRIVATE_MANIFEST_SHA=PASS'

    if (-not (Test-Path -LiteralPath $PipBase -PathType Leaf)) { throw 'HOLD_PY312_EXE_NOT_FOUND' }
    $Version = (& $PipBase -c 'import sys; print(sys.version_info[0] * 100 + sys.version_info[1])' | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $Version -ne '312') { throw 'HOLD_PYTHON_NOT_312' }

    New-Item -ItemType Directory -Path $Session,$WheelDest -Force | Out-Null
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $Zip = [System.IO.Compression.ZipFile]::OpenRead($WheelsZip)
    try {
        $Seen = @{}
        foreach ($Entry in $Zip.Entries) {
            $Rel = $Entry.FullName.Replace('\','/')
            $Parts = @($Rel.Split('/'))
            if ($Rel.StartsWith('/') -or $Rel.Contains(':') -or ($Parts -contains '..') -or ($Parts -contains '.')) {
                throw 'HOLD_WHEELHOUSE_ZIP_PATH_ESCAPE'
            }
            if (-not $Entry.Name) { continue }
            if (($Entry.Name -ne 'WHEELHOUSE_SHA256_MANIFEST.json') -and
                (-not $Entry.Name.EndsWith('.whl',[System.StringComparison]::OrdinalIgnoreCase))) {
                throw 'HOLD_WHEELHOUSE_UNEXPECTED_ENTRY'
            }
            if ($Seen.ContainsKey($Entry.Name)) { throw 'HOLD_WHEELHOUSE_DUPLICATE_ENTRY' }
            $Seen[$Entry.Name]=$true
        }
        if ($Seen.Count -ne 32 -or -not $Seen.ContainsKey('WHEELHOUSE_SHA256_MANIFEST.json')) {
            throw 'HOLD_WHEELHOUSE_ENTRY_COUNT'
        }
    }
    finally { $Zip.Dispose() }
    [System.IO.Compression.ZipFile]::ExtractToDirectory($WheelsZip,$WheelDest)
    $ManifestFile = @(Get-ChildItem -LiteralPath $WheelDest -Filter 'WHEELHOUSE_SHA256_MANIFEST.json' -File -Recurse)
    if ($ManifestFile.Count -ne 1) { throw 'HOLD_WHEELHOUSE_MANIFEST_COUNT' }
    $Wheels = Get-Content -LiteralPath $ManifestFile[0].FullName -Raw | ConvertFrom-Json
    if ($Wheels.status -ne 'PASS_WHEELHOUSE_COMPLETE' -or
        $Wheels.platform -ne 'win_amd64' -or
        $Wheels.python_version -ne '3.12' -or
        $Wheels.transformers_pin -ne '5.19.0' -or
        @($Wheels.wheels).Count -ne 31 -or
        $Wheels.contains_torch -ne $false) {
        throw 'HOLD_WHEELHOUSE_MANIFEST_BAD'
    }
    $WheelsDir = $ManifestFile[0].DirectoryName
    foreach ($File in $Wheels.wheels) {
        $WheelPath = Join-Path $WheelsDir $File.name
        if (-not (Test-Path -LiteralPath $WheelPath -PathType Leaf)) { throw 'HOLD_WHEEL_MISSING' }
        if ((Get-Item -LiteralPath $WheelPath).Length -ne [long]$File.bytes -or
            (Get-FileHash -LiteralPath $WheelPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$File.sha256) {
            throw ('HOLD_WHEEL_HASH_' + $File.name)
        }
    }
    Write-Output 'A0D_WINDOWS_31_WHEELS_SHA=PASS'

    $env:HF_HOME = Join-Path $Session 'hf_cache'
    $env:TMP = Join-Path $Session 'tmp'
    $env:TEMP = $env:TMP
    $env:PIP_CACHE_DIR = Join-Path $Session 'pip_cache'
    $env:PIP_NO_INDEX = '1'
    $env:PIP_DISABLE_PIP_VERSION_CHECK = '1'
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $env:OMP_NUM_THREADS = '2'
    $env:MKL_NUM_THREADS = '2'
    New-Item -ItemType Directory -Path $env:TMP | Out-Null

    & $PipBase -m venv --system-site-packages $VenvDir
    if ($LASTEXITCODE -ne 0) { throw 'HOLD_VENV_CREATION_FAILED' }
    $VenvPy = Join-Path $VenvDir 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $VenvPy -PathType Leaf)) { throw 'HOLD_VENV_PYTHON_MISSING' }

    $PipLog = Join-Path $Session 'offline_pip_install.log'
    $EapSaved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & $VenvPy -m pip install --no-index --find-links $WheelsDir --no-cache-dir --disable-pip-version-check 'transformers==5.19.0' 2>&1 | Out-File -LiteralPath $PipLog -Encoding UTF8
        $PipExit = $LASTEXITCODE
    }
    finally { $ErrorActionPreference = $EapSaved }
    if ($PipExit -ne 0) {
        $Tail = @(Get-Content -LiteralPath $PipLog -Tail 12) -join ' | '
        throw ('HOLD_OFFLINE_PIP_INSTALL_' + $Tail.Substring(0,[Math]::Min($Tail.Length,600)))
    }
    Write-Output 'A0D_ISOLATED_OFFLINE_TRANSFORMERS_INSTALL=PASS'

    $EapSaved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $Lines = @(& $VenvPy $SourcePy --source-dir $DonorDir --t1 $T1Manifest --cpu-init 2>&1)
        $ReadbackExit = $LASTEXITCODE
    }
    finally { $ErrorActionPreference = $EapSaved }
    foreach ($Line in $Lines) {
        $Str = "$Line"
        if ($Str -match '^\s*\{') {
            try { $ModelResult = ConvertFrom-Json -InputObject $Str } catch {}
        }
    }
    if ($ReadbackExit -ne 0 -or -not $ModelResult) { throw 'HOLD_OFFICIAL_READBACK_FAILURE_NO_PASS_JSON' }
    if ($ModelResult.status -ne 'PASS_OFFICIAL_CLASS_AND_SOURCE_T1_MAPPING' -or
        $ModelResult.T1_mapping.mapped -ne 1917 -or
        $ModelResult.T1_mapping.multi_id_mapped -ne 50 -or
        $ModelResult.parameter_count -ne 271002624 -or
        $ModelResult.state_tensor_count -ne 413 -or
        $ModelResult.transformers_version -ne '5.19.0') {
        throw ('HOLD_OFFICIAL_CPU_OR_T1_CHECK_' + [string]$ModelResult.status)
    }
    $Status = 'PASS_OWNER_OFFICIAL_CPU_CLASS_AND_EXACT_T1_MAPPING'
    Write-Output 'A0D_OWNER_OFFICIAL_CLASS_T1_MAPPING=PASS'
}
catch {
    $Status = 'HOLD_ISOLATED_OFFLINE_CPU_READBACK'
    $HoldReason = $_.Exception.Message
    Write-Output ('A0D_ISOLATED_HOLD_REASON=' + $HoldReason)
}
finally {
    $Record = [ordered]@{
        schema='ttm.gemma2.a0d.isolated_offline_owner_cpu_readback.v1'
        source_head='07d2e0e7760625b7f984f53c91fd61512158daab'
        wheel_artifact_id=13846859761
        status=$Status
        failure_reason=$HoldReason
        wheel_archive_sha256=$ArchiveHash
        wheelhouse_wheel_sha_count_expected=31
        python_version_code=$Version
        project_root=$Root
        project_local_venv=$VenvDir
        donor_source_dir=$DonorDir
        source_sha_file_count=$FilesVerified.Count
        t1_manifest_present=[bool]$T1Manifest
        official_readback_exit=$ReadbackExit
        official_readback=$ModelResult
        pip_exit=$PipExit
        training=$false
        pretrained_weights_loaded=$false
        model_forward=$false
        OOD256_rescore=$false
        T4_execution_authorized=$false
    }
    $Timestamp=(Get-Date).ToUniversalTime().ToString('yyyyMMdd_HHmmss_fff')
    $ReceiptPath=Join-Path $OutDir ('TTM_GEMMA2_A0D_ISOLATED_CPU_READBACK_' + $Timestamp + '.json')
    $Record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
    $Digest=(Get-FileHash -LiteralPath $ReceiptPath -Algorithm SHA256).Hash
    Write-Output ('A0D_ISOLATED_READBACK_STATUS=' + $Status)
    Write-Output ('A0D_ISOLATED_READBACK_RECEIPT=' + $ReceiptPath)
    Write-Output ('A0D_ISOLATED_READBACK_RECEIPT_SHA256=' + $Digest)
}
if ($Status -ne 'PASS_OWNER_OFFICIAL_CPU_CLASS_AND_EXACT_T1_MAPPING') { exit 2 }
