#requires -Version 5.1
<#
TTM VM V4 R8 G2: diagnostics for exactly three owner-observed Python.exe
SHA matches. Read only. Never rerun original preexec or overwrite receipt.
No key access, package install, runtime creation, R8/G_pre/G3, or GitHub mutation.
All printed results are status-only; stderr/manifest contents are not printed.
#>
[CmdletBinding()]
param([string]$ProjectRoot='D:\WORK\RESEARCH\TokenToModel-Lab')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'

$Root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
$Receipt=Join-Path $Root '_private\r8_custody\receipts\g2-owner-windows-protected-trust-boundary-preexec-20261115.json'
$ReceiptSHA='c0bf90955d09501b5dcdb7ab912635a666895b23c5c855494ddfb7381ce37795'
$ExeSHA='0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14'

if(-not (Test-Path -LiteralPath $Receipt -PathType Leaf)){throw 'ORIGINAL_G2_RECEIPT_MISSING'}
$ActualReceipt=(Get-FileHash -LiteralPath $Receipt -Algorithm SHA256).Hash.ToLowerInvariant()
if($ActualReceipt -cne $ReceiptSHA){throw 'ORIGINAL_G2_RECEIPT_SHA256_MISMATCH'}
Write-Host 'ORIGINAL_G2_RECEIPT=PASS_SHA256_PRESERVED'

$Candidates=@(
    [pscustomobject]@{ Id='P07_XPU'; Rel='_runtime\p07\venv_xpu_cp312\Scripts\python.exe' },
    [pscustomobject]@{ Id='GEMMA2_A0D'; Rel='_tmp\ttm_gemma2_a0d_isolated_offline_bfd60812929e47c884391da954057d8c\venv\Scripts\python.exe' },
    [pscustomobject]@{ Id='R8_G2_EXACT'; Rel='_tmp\TTM_VM_R8_G2_EXACT_RUNTIME_20261115\venv\Scripts\python.exe' }
)

# Use only single quotes inside Python code to avoid PowerShell 5.1 native
# command-line double-quote stripping. -I isolates environment; -B forbids
# bytecode writes. Metadata is read, packages are not imported as modules.
$Code="import sys,json,importlib.metadata as m; n=('numpy','scipy','scikit-learn','joblib','threadpoolctl'); v={x:next((d.version for d in m.distributions() if (d.metadata.get('Name') or '').lower()==x.lower()),'NOT_INSTALLED') for x in n}; print(json.dumps({'py':'.'.join(map(str,sys.version_info[:3])),'prefix':sys.prefix,'base_prefix':sys.base_prefix,'versions':v},sort_keys=True))"

function Invoke-MetadataProbe([string]$Executable,[string]$Snippet){
    # Capture native stderr to avoid PS 5.1 NativeCommandError under Stop.
    # Never show traceback: only command status and sanitized metadata.
    $Saved=$ErrorActionPreference
    $Raw=@()
    $Exit=$null
    try{
        $ErrorActionPreference='Continue'
        $Raw=@(& $Executable -I -B -c $Snippet 2>&1)
        $Exit=$LASTEXITCODE
    } catch {
        return [pscustomobject]@{State='EXECUTION_EXCEPTION';Exit=-1;Json=$null}
    } finally {
        $ErrorActionPreference=$Saved
    }
    if($null -eq $Exit -or $Exit -ne 0){
        return [pscustomobject]@{State='NONZERO_EXIT';Exit=$Exit;Json=$null}
    }
    $Lines=@($Raw | Where-Object {$_ -is [string]} | ForEach-Object {$_.Trim()} |
       Where-Object {$_.StartsWith('{') -and $_.EndsWith('}')})
    if($Lines.Count -ne 1){return [pscustomobject]@{State='UNEXPECTED_STDOUT';Exit=0;Json=$null}}
    try{
        $Data=($Lines[0] | ConvertFrom-Json -ErrorAction Stop)
        if($null -eq $Data.versions -or $null -eq $Data.py -or $null -eq $Data.prefix){
            return [pscustomobject]@{State='INVALID_JSON_SHAPE';Exit=0;Json=$null}
        }
        return [pscustomobject]@{State='PASS_JSON';Exit=0;Json=$Data}
    }catch{
        return [pscustomobject]@{State='JSON_PARSE_FAILED';Exit=0;Json=$null}
    }
}

$R8ExactMatch=$false
$R8VersionMatch=$false
foreach($Record in $Candidates){
    $Id=$Record.Id
    $Executable=Join-Path $Root $Record.Rel
    Write-Host ('CANDIDATE=' + $Id)
    if(-not (Test-Path -LiteralPath $Executable -PathType Leaf)){
        Write-Host ('CANDIDATE_FILE_' + $Id + '=NOT_FOUND')
        continue
    }
    $Item=Get-Item -LiteralPath $Executable -Force
    if(($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){
        Write-Host ('CANDIDATE_FILE_' + $Id + '=REPARSE_REJECTED')
        continue
    }
    $Hash=(Get-FileHash -LiteralPath $Executable -Algorithm SHA256).Hash.ToLowerInvariant()
    if($Hash -cne $ExeSHA){
        Write-Host ('CANDIDATE_EXE_SHA_' + $Id + '=HOLD_MISMATCH')
        continue
    }
    Write-Host ('CANDIDATE_EXE_SHA_' + $Id + '=PASS_HISTORICAL_HASH')
    if($Id -eq 'R8_G2_EXACT'){$R8ExactMatch=$true}

    $ExpectedPrefix=Split-Path -Path (Split-Path -Path $Executable -Parent) -Parent
    $Cfg=Join-Path $ExpectedPrefix 'pyvenv.cfg'
    if(Test-Path -LiteralPath $Cfg -PathType Leaf){
        Write-Host ('PYVENV_CFG_' + $Id + '=PRESENT')
    }else{
        Write-Host ('PYVENV_CFG_' + $Id + '=MISSING')
    }
    $Probe=Invoke-MetadataProbe -Executable $Executable -Snippet $Code
    Write-Host ('PROBE_STATE_' + $Id + '=' + $Probe.State)
    if($Probe.State -ne 'PASS_JSON'){
        Write-Host ('PROBE_EXIT_' + $Id + '=' + $Probe.Exit)
        continue
    }
    $Data=$Probe.Json
    Write-Host ('PYTHON_VERSION_' + $Id + '=' + $Data.py)
    $Prefix=[IO.Path]::GetFullPath([string]$Data.prefix).TrimEnd('\')
    $MatchPrefix=$Prefix -ieq ([IO.Path]::GetFullPath($ExpectedPrefix).TrimEnd('\'))
    Write-Host ('VENV_PREFIX_BOUND_' + $Id + '=' + $(if($MatchPrefix){'PASS'}else{'HOLD_MISMATCH'}))

    $Expected=[ordered]@{
        numpy='2.3.5';scipy='1.17.0';'scikit-learn'='1.8.0'
        joblib='1.5.3';threadpoolctl='3.6.0'
    }
    $VersionOk=$Data.py -ceq '3.12.10'
    foreach($Key in $Expected.Keys){
        $Observed=[string]($Data.versions.PSObject.Properties[$Key].Value)
        if(-not $Observed){$Observed='NOT_INSTALLED'}
        Write-Host ('PACKAGE_' + $Id + '_' + $Key + '=' + $Observed)
        if($Observed -cne $Expected[$Key]){$VersionOk=$false}
    }
    if($VersionOk -and $MatchPrefix){
        Write-Host ('VERSION_METADATA_' + $Id + '=PASS_SCOPED')
        if($Id -eq 'R8_G2_EXACT'){$R8VersionMatch=$true}
    }else{
        Write-Host ('VERSION_METADATA_' + $Id + '=HOLD_MISMATCH')
    }
}
Write-Host ('R8_G2_EXECUTABLE_MATCH=' + $(if($R8ExactMatch){'PASS_SHA_ONLY'}else{'NOT_VERIFIED'}))
Write-Host ('R8_G2_VERSION_METADATA=' + $(if($R8VersionMatch){'PASS_SCOPED'}else{'NOT_VERIFIED'}))
Write-Host 'RUNTIME_ORIGINAL_MANIFEST_AND_LOADED_MODULE_SHA=NOT_ATTESTED'
Write-Host 'PRODUCTION_CUSTODY_HMAC_V2=NOT_EXECUTED'
Write-Host 'R8=NOT_GENERATED'
Write-Host 'G3=NOT_EXECUTED'
Write-Host 'G2=HOLD_INTEGRATED'
