#requires -Version 5.1
<#
TTM VM V4 R8 G2 owner-Windows scoped preexecution readback.
Harmless sentinel only. NO real key, G_pre, R8 data, G3, GitHub writes, permit.
One private public-safe receipt, never overwrite. No cleanup workaround.
Use explicitly pinned ProtectedSourceRoot and PythonExe if available.
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$ProtectedSourceRoot = '',
    [string]$PythonExe = '',
    [string]$GitHubCliExe = '',
    [string]$TrustedGhSha256 = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Operation = 'TTM_VM_V4_R8_G2_OWNER_WINDOWS_PROTECTED_TRUST_BOUNDARY_INTEGRATED_PREEXEC_SINGLE_GATE'
$Expected = [ordered]@{
    'folds_raters.py'='02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae'
    'r8_production_caller.py'='3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206'
    'test_g0_algorithm_version_binding.py'='2ce86fe549e1625790fcab72c076df2f12d648b048a350570d5c97a026431ae2'
    'gold_contract.py'='8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5'
    'restricted_oracles.py'='34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1'
}
$Tag = 'ttm-vm-v4-r8-g2-commitment-sentinel-20261115'
$Asset = 'ttm-vm-r8-g2-public-sentinel.json'
$ExpectedAssetSha = 'f589347fc615f73826104a0121fd46e842ea210414df8c26f75c0c13c2ffc54f'
$Root = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
$PrivateRoot = Join-Path $Root '_private\r8_custody'
$ReceiptDir = Join-Path $PrivateRoot 'receipts'
$ReceiptPath = Join-Path $ReceiptDir 'g2-owner-windows-protected-trust-boundary-preexec-20261115.json'
$Tmp = Join-Path $Root '_tmp\TTM_VM_R8_G2_OWNER_PREEXEC_20261115'
$States = [ordered]@{
    FROZEN_SOURCE_5_OF_5='NOT_VERIFIED'
    RUNTIME_EXACT_PIN='NOT_VERIFIED'
    WINDOWS_DPAPI_CURRENTUSER_SENTINEL='NOT_EXECUTED'
    GITHUB_REAL_SENTINEL_ATTESTATION='NOT_EXECUTED'
    GITHUB_CLI_TRUSTED_EXECUTABLE='NOT_VERIFIED'
    GPRE_AUTHENTIC_HMAC='NOT_EXECUTED'
    PRE_G3_LAUNCHER_BOUNDARY='NOT_ATTESTED'
    G3_GENERATOR='NOT_REGISTERED'
    G3_EXECUTED=$false
    R8_GENERATED=$false
    OWNER_BACKUP_POLICY='ACCEPT_NO_INDEPENDENT_BACKUP_R8_D_ONLY'
    RETENTION_AMENDMENT='HOLD_INDEPENDENT_ACCEPTANCE'
}
$Hashes = [ordered]@{}
$Meta = [ordered]@{
    operation=$Operation
    run_utc=[DateTime]::UtcNow.ToString('o')
    candidate_commit='9448ade9f3d5ffa8361d62485a68e49701c55c13'
    scientific_source_commit='84d9d5c95e9962ccfe294852570e261b145fe403'
    sentinel_tag=$Tag
    sentinel_asset_sha256_expected=$ExpectedAssetSha
    modes='READ_ONLY_SCIENCE; PUBLIC_GITHUB_SENTINEL; NO_G3'
}
function Mark([string]$key,[string]$value) {
    $States[$key] = $value
    Write-Host ("{0}={1}" -f $key, $value)
}
function Is-Reparse([string]$path) {
    $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
    return (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
}
if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
    throw 'PROJECT_ROOT_NOT_FOUND'
}
if (-not (Test-Path -LiteralPath $ReceiptDir -PathType Container)) {
    throw 'EXISTING_PRIVATE_RECEIPT_DIR_NOT_FOUND; do not create another custody root'
}
if ((Is-Reparse $Root) -or (Is-Reparse $PrivateRoot) -or (Is-Reparse $ReceiptDir)) {
    throw 'REPARSE_POINT_IN_CUSTODY_PATH'
}
if (Test-Path -LiteralPath $ReceiptPath) {
    throw 'ONE_SHOT_RECEIPT_ALREADY_EXISTS; preserve prior receipt and do not overwrite'
}

# 1. Read only the five frozen files; do not read key/gold/private receipts.
if ($ProtectedSourceRoot) {
    try {
        $Src=[IO.Path]::GetFullPath($ProtectedSourceRoot).TrimEnd('\')
        $Prefix=[IO.Path]::GetFullPath($PrivateRoot).TrimEnd('\')+'\'
        if (-not $Src.StartsWith($Prefix,[StringComparison]::OrdinalIgnoreCase)) {
            throw 'PROTECTED_SOURCE_OUTSIDE_PRIVATE_CUSTODY'
        }
        if (-not (Test-Path -LiteralPath $Src -PathType Container) -or (Is-Reparse $Src)) {
            throw 'PROTECTED_SOURCE_MISSING_OR_REPARSE'
        }
        $AllOk=$true
        foreach($item in $Expected.GetEnumerator()) {
            $f=Join-Path $Src $item.Key
            if (-not (Test-Path -LiteralPath $f -PathType Leaf) -or (Is-Reparse $f)) {
                $AllOk=$false; break
            }
            $actual=(Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant()
            $Hashes[$item.Key]=$actual
            if ($actual -cne $item.Value) { $AllOk=$false }
        }
        if($AllOk) { Mark 'FROZEN_SOURCE_5_OF_5' 'PASS_SCOPED_LOCAL_BYTES' }
        else { Mark 'FROZEN_SOURCE_5_OF_5' 'HOLD_SOURCE_HASH_OR_PATH_MISMATCH' }
    }
    catch {
        Mark 'FROZEN_SOURCE_5_OF_5' 'HOLD_SOURCE_READBACK_UNAVAILABLE'
    }
}
else { Mark 'FROZEN_SOURCE_5_OF_5' 'NOT_EXECUTED_SOURCE_ROOT_NOT_PINNED' }

# 2. Strict scoped Python 3.12 runtime import; no scientific entrypoints.
if($PythonExe) {
    try {
        if(-not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {throw 'PYTHON_EXE_MISSING'}
        $code='import sys,json,importlib.metadata as m, numpy, scipy, sklearn; print(json.dumps({"python":".".join(map(str,sys.version_info[:3])),"prefix":sys.prefix,"packages":{"numpy":m.version("numpy"),"scipy":m.version("scipy"),"scikit-learn":m.version("scikit-learn")}}))'
        $raw=(& $PythonExe -I -B -c $code 2>&1 | Out-String).Trim()
        if($LASTEXITCODE -ne 0) {throw 'PYTHON_IMPORT_FAILED'}
        $p=$raw | ConvertFrom-Json
        $Meta['python_exe_sha256']=(Get-FileHash -LiteralPath $PythonExe -Algorithm SHA256).Hash.ToLowerInvariant()
        $Meta['python_version']=$p.python
        if($p.python -eq '3.12.10' -and $p.packages.numpy -eq '2.3.5' -and
           $p.packages.scipy -eq '1.17.0' -and $p.packages.'scikit-learn' -eq '1.8.0') {
            Mark 'RUNTIME_EXACT_PIN' 'PASS_SCOPED_IMPORT_VERSIONS'
        } else { Mark 'RUNTIME_EXACT_PIN' 'HOLD_RUNTIME_EXACT_PIN_MISMATCH' }
    }
    catch { Mark 'RUNTIME_EXACT_PIN' 'HOLD_RUNTIME_INSPECTION_FAILED' }
}
else { Mark 'RUNTIME_EXACT_PIN' 'NOT_EXECUTED_PYTHON_EXE_NOT_PINNED' }

# 3. Ephemeral DPAPI CurrentUser sentinel. NO stored key, ciphertext or G_pre.
$plain=$null; $decoded=$null
try {
    Add-Type -AssemblyName System.Security -ErrorAction Stop
    $plain=[Text.Encoding]::UTF8.GetBytes('TTM_VM_R8_G2_EPHEMERAL_SENTINEL_ONLY')
    $cipher=[Security.Cryptography.ProtectedData]::Protect(
       $plain,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser)
    $decoded=[Security.Cryptography.ProtectedData]::Unprotect(
       $cipher,$null,[Security.Cryptography.DataProtectionScope]::CurrentUser)
    if([Convert]::ToBase64String($plain) -cne [Convert]::ToBase64String($decoded)) {throw 'DPAPI_SENTINEL_MISMATCH'}
    Mark 'WINDOWS_DPAPI_CURRENTUSER_SENTINEL' 'PASS_SCOPED_SAME_PROFILE_ONLY'
}
catch {
    $Meta['dpapi_exception_type']=$_.Exception.GetType().FullName
    Mark 'WINDOWS_DPAPI_CURRENTUSER_SENTINEL' 'HOLD_DPAPI_EPHEMERAL_SENTINEL_FAILED'
    Write-Host ('DPAPI_SENTINEL_EXCEPTION_TYPE=' + $Meta['dpapi_exception_type'])
}
finally {
    if($null -ne $plain) {[Array]::Clear($plain,0,$plain.Length)}
    if($null -ne $decoded) {[Array]::Clear($decoded,0,$decoded.Length)}
}

# 4. Independently verify real public harmless GitHub release and its asset.
# No GitHub release creation/edit/deletion or real consumption marker.
try {
    if(-not $GitHubCliExe) {
        $cmd=Get-Command gh.exe -ErrorAction Stop
        $GitHubCliExe=$cmd.Source
    }
    if(-not (Test-Path -LiteralPath $GitHubCliExe -PathType Leaf)) {throw 'GH_NOT_FOUND'}
    $ghHash=(Get-FileHash -LiteralPath $GitHubCliExe -Algorithm SHA256).Hash.ToLowerInvariant()
    $Meta['gh_exe_sha256_observed']=$ghHash
    if($TrustedGhSha256 -and $TrustedGhSha256.ToLowerInvariant() -ceq $ghHash) {
        Mark 'GITHUB_CLI_TRUSTED_EXECUTABLE' 'PASS_EXACT_PREAPPROVED_SHA256'
    } else {
        Mark 'GITHUB_CLI_TRUSTED_EXECUTABLE' 'NOT_ATTESTED_PREAPPROVED_HASH_ABSENT_OR_MISMATCH'
    }
    $repo='minhtri22/TokenToModel-Lab'
    $metaRaw=(& $GitHubCliExe api ('repos/'+$repo+'/releases/tags/'+$Tag) 2>&1 | Out-String)
    if($LASTEXITCODE -ne 0) {throw 'RELEASE_API_FAILED'}
    $release=$metaRaw | ConvertFrom-Json
    if($release.tag_name -cne $Tag -or $release.immutable -cne $true) {throw 'RELEASE_NOT_IMMUTABLE'}
    $assetInfo=@($release.assets | Where-Object { $_.name -ceq $Asset })
    if($assetInfo.Count -ne 1 -or $assetInfo[0].digest -cne ('sha256:'+$ExpectedAssetSha)) {
        throw 'RELEASE_ASSET_DIGEST_MISMATCH'
    }
    if(Test-Path -LiteralPath $Tmp) {throw 'EXISTING_SCRATCH_NO_OVERWRITE'}
    New-Item -Path $Tmp -ItemType Directory -ErrorAction Stop | Out-Null
    $null=(& $GitHubCliExe release download $Tag -R $repo --pattern $Asset --dir $Tmp 2>&1 | Out-String)
    if($LASTEXITCODE -ne 0) {throw 'RELEASE_DOWNLOAD_FAILED'}
    $assetPath=Join-Path $Tmp $Asset
    if((Get-FileHash -LiteralPath $assetPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $ExpectedAssetSha) {
        throw 'LOCAL_RELEASE_ASSET_MISMATCH'
    }
    $null=(& $GitHubCliExe release verify $Tag -R $repo --format json 2>&1 | Out-String)
    if($LASTEXITCODE -ne 0) {throw 'GH_RELEASE_SIGNATURE_FAILED'}
    $null=(& $GitHubCliExe release verify-asset $Tag $assetPath -R $repo --format json 2>&1 | Out-String)
    if($LASTEXITCODE -ne 0) {throw 'GH_ASSET_SIGNATURE_FAILED'}
    $Meta['sentinel_published_at_utc']=$release.published_at
    Mark 'GITHUB_REAL_SENTINEL_ATTESTATION' 'PASS_SCOPED_GITHUB_SIGNED_PUBLIC_SENTINEL'
}
catch { Mark 'GITHUB_REAL_SENTINEL_ATTESTATION' 'HOLD_REMOTE_OR_CRYPTOGRAPHIC_CHECK_FAILED' }

# 5. Do NOT call ProductionBoundaryCandidate.dispatch, HMAC key reader, G3,
# or any release create/consume. Existing Python candidate has no G3 registration.
# The installed launcher/actual custodian key remain NOT_ATTESTED by design.
$Receipt=[ordered]@{
    schema='ttm.vm.v4.r8.g2.owner_windows_preexec_readback.v1'
    metadata=$Meta
    states=$States
    public_source_sha256=$Hashes
    final_decision='G2_HOLD_INTEGRATED'
    production_admission='NOT_ATTESTED'
    independent_retention_amendment='HOLD'
    note='Only harmless public sentinel and frozen source/runtime readback. No actual G_pre/G3.'
}
$payload=($Receipt | ConvertTo-Json -Depth 8)
[IO.File]::WriteAllText($ReceiptPath,$payload+[Environment]::NewLine,
    (New-Object Text.UTF8Encoding($false)))
$Meta['receipt_sha256']=(Get-FileHash -LiteralPath $ReceiptPath -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "PREEXEC_RECEIPT_SHA256=$($Meta['receipt_sha256'])"
Write-Host 'G2_INTEGRATED=HOLD_INTEGRATED'
Write-Host 'R8=NOT_GENERATED'
Write-Host 'G3=NOT_EXECUTED'
