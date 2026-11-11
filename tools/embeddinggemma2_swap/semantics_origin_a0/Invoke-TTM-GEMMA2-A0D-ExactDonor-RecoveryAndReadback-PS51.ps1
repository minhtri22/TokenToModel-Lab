# TTM GEMMA2 A0D — exact donor SOURCE ONLY recovery + owner-local readback.
# PowerShell 5.1; no pretrained weights, training, model.forward or Git changes.
# All intentional writes stay inside D:\WORK\RESEARCH\TokenToModel-Lab.
[CmdletBinding()]
param(
    [string]$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$T1Manifest = ''
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ExpectedRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab'
if (-not (Test-Path -LiteralPath $Root -PathType Container)) { throw 'HOLD_PROJECT_ROOT_MISSING' }
$Root = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
if ($Root -ine $ExpectedRoot) { throw 'HOLD_ROOT_NOT_CANONICAL_TTM_PROJECT' }

$Revision = 'f9972ac22e696a105c482202646979e33e4b5a1e'
$WorkDir = Join-Path $Root '_tmp\ttm_gemma2_a0d_owner_readback'
$DonorDir = Join-Path $WorkDir ('official_donor_source_' + $Revision)
$OutDir = Join-Path $Root 'artifacts\qa\ttm-embeddinggemma2\a0d_owner_local_readback'
$OriginalScript = Join-Path $Root '_tmp\TTM_GEMMA2_A0D_OWNER_PINNED_OFFICIAL_READBACK_PS51.ps1'
$ExpectedFileSha = [ordered]@{
    'config.json' = 'b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3'
    'tokenizer.json' = '4d777ef5bdc1aa36227abdfb77c3e49e7b9c892d16e1b6bda41c393504828be4'
    'tokenizer_config.json' = '17bd5d6e9364ca49a534e1502076593317c298d4a663623091ed45388f004874'
}
$ExpectedBytes = @{
    'config.json' = 4455L
    'tokenizer.json' = 32170510L
    'tokenizer_config.json' = 1599L
}

New-Item -ItemType Directory -Path $WorkDir,$DonorDir,$OutDir -Force | Out-Null
if (-not (Test-Path -LiteralPath $OriginalScript -PathType Leaf)) {
    throw 'HOLD_ORIGINAL_A0D_READBACK_SCRIPT_MISSING'
}
$FileResults = New-Object System.Collections.ArrayList
$RecoveryStatus = 'PENDING'
$Failure = $null
$ChildExit = $null
$ChildStatus = $null
$ChildReceipt = $null
$ChildReceiptSha = $null

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    foreach ($Name in @('config.json','tokenizer.json','tokenizer_config.json')) {
        $Dest = Join-Path $DonorDir $Name
        $Downloaded = $false
        if (-not (Test-Path -LiteralPath $Dest -PathType Leaf)) {
            if (Test-Path -LiteralPath $Dest) { throw ('HOLD_DEST_NOT_A_FILE_' + $Name) }
            $Url = 'https://huggingface.co/google/embeddinggemma-2/resolve/' + $Revision + '/' + $Name + '?download=true'
            $Part = Join-Path $DonorDir ($Name + '.' + [guid]::NewGuid().ToString('N') + '.part')
            try {
                Invoke-WebRequest -Uri $Url -UseBasicParsing -OutFile $Part -ErrorAction Stop
                if (-not (Test-Path -LiteralPath $Part -PathType Leaf)) { throw ('HOLD_DOWNLOAD_NOT_CREATED_' + $Name) }
                $N = (Get-Item -LiteralPath $Part).Length
                $Sha = (Get-FileHash -LiteralPath $Part -Algorithm SHA256).Hash.ToLowerInvariant()
                if ($N -ne $ExpectedBytes[$Name] -or $Sha -ne $ExpectedFileSha[$Name]) {
                    throw ('HOLD_DOWNLOAD_SOURCE_SIZE_OR_SHA_MISMATCH_' + $Name)
                }
                Move-Item -LiteralPath $Part -Destination $Dest -ErrorAction Stop
                $Downloaded = $true
            }
            finally {
                if (Test-Path -LiteralPath $Part -PathType Leaf) {
                    Remove-Item -LiteralPath $Part -Force
                }
            }
        }
        $ActualBytes = (Get-Item -LiteralPath $Dest -ErrorAction Stop).Length
        $ActualSha = (Get-FileHash -LiteralPath $Dest -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($ActualBytes -ne $ExpectedBytes[$Name] -or $ActualSha -ne $ExpectedFileSha[$Name]) {
            throw ('HOLD_EXISTING_DONOR_SOURCE_SIZE_OR_SHA_MISMATCH_' + $Name)
        }
        $State = if ($Downloaded) { 'DOWNLOADED_VERIFIED_SHA256' } else { 'EXISTING_VERIFIED_SHA256' }
        [void]$FileResults.Add([ordered]@{
            name = $Name; bytes = $ActualBytes; sha256 = $ActualSha; status = $State
        })
        Write-Output ('A0D_DONOR_' + $Name + '=PASS_SHA256')
    }
    $RecoveryStatus = 'PASS_DONOR_3_OF_3_EXACT_PIN'

    $Args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$OriginalScript,'-Root',$Root,'-DonorDir',$DonorDir)
    if ($T1Manifest) { $Args += @('-T1Manifest', $T1Manifest) }
    $ChildLines = @(& powershell.exe @Args 2>&1)
    $ChildExit = $LASTEXITCODE
    foreach ($Line in $ChildLines) {
        $S = "$Line"
        Write-Output $S
        if ($S.StartsWith('A0D_OWNER_READBACK_STATUS=')) { $ChildStatus = $S.Substring('A0D_OWNER_READBACK_STATUS='.Length) }
        if ($S.StartsWith('A0D_OWNER_RECEIPT=')) { $ChildReceipt = $S.Substring('A0D_OWNER_RECEIPT='.Length) }
        if ($S.StartsWith('A0D_OWNER_RECEIPT_SHA256=')) { $ChildReceiptSha = $S.Substring('A0D_OWNER_RECEIPT_SHA256='.Length) }
    }
    if ($ChildExit -ne 0 -or $ChildStatus -ne 'PASS_OWNER_EXACT_SOURCE_OFFICIAL_CLASS_T1_MAPPING') {
        $RecoveryStatus = 'HOLD_OWNER_READBACK_NOT_FULLY_PASS'
    } else {
        $RecoveryStatus = 'PASS_OWNER_EXACT_SOURCE_OFFICIAL_CLASS_T1_MAPPING'
    }
}
catch {
    $RecoveryStatus = 'HOLD_SOURCE_RECOVERY_OR_READBACK'
    $Failure = $_.Exception.Message
    Write-Output ('A0D_RECOVERY_HOLD_REASON=' + $Failure)
}
finally {
    $Record = [ordered]@{
        schema = 'ttm.gemma2.a0d.owner_source_recovery_readback.v1'
        operation = 'TTM_GEMMA2_A0D_OWNER_WINDOWS_PINNED_SOURCE_RECOVERY_AND_T1_MAPPING_SINGLE_READBACK'
        source_revision = $Revision
        status = $RecoveryStatus
        file_receipts = @($FileResults.ToArray())
        donor_source_dir = $DonorDir
        child_status = $ChildStatus
        child_exit_code = $ChildExit
        child_receipt = $ChildReceipt
        child_receipt_reported_sha256 = $ChildReceiptSha
        failure_reason = $Failure
        weights_downloaded = $false
        model_forward = $false
        training_executed = $false
        t4_permit_granted = $false
    }
    $DateTag = (Get-Date).ToUniversalTime().ToString('yyyyMMdd_HHmmss_fff')
    $ReceiptPath = Join-Path $OutDir ('TTM_GEMMA2_A0D_RECOVERY_READBACK_' + $DateTag + '.json')
    $Record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
    $ReceiptHash = (Get-FileHash -LiteralPath $ReceiptPath -Algorithm SHA256).Hash
    Write-Output ('A0D_RECOVERY_STATUS=' + $RecoveryStatus)
    Write-Output ('A0D_RECOVERY_RECEIPT=' + $ReceiptPath)
    Write-Output ('A0D_RECOVERY_RECEIPT_SHA256=' + $ReceiptHash)
}
if ($RecoveryStatus -notlike 'PASS_OWNER_*') { exit 2 }
