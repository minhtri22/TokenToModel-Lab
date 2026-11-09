# G1 Windows 11 target-environment inventory (READ ONLY, PowerShell 5.1).
# No permission changes, no TEST, no Qwen, no private data, no file writes.
# Designed to be run manually in ordinary (non-elevated) PowerShell.
[CmdletBinding()]
param([string]$ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Test-ExactProjectRoot([string]$P) {
    $expected = 'D:\WORK\RESEARCH\TokenToModel-Lab'
    if (-not [string]::Equals($P.TrimEnd('\'), $expected, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'STOP_G1_PROJECT_ROOT_MISMATCH'
    }
    if (-not (Test-Path -LiteralPath $P -PathType Container)) {
        throw 'STOP_G1_PROJECT_ROOT_MISSING'
    }
    $item = Get-Item -LiteralPath $P -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'STOP_G1_PROJECT_ROOT_REPARSE'
    }
}

function Get-SafeAclInventory([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return @{ exists = $false; owner = $null; protected = $null; principal_count = 0; status = 'NOT_PROVISIONED' }
    }
    $it = Get-Item -LiteralPath $Path -Force
    if (($it.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        return @{ exists = $true; status = 'REPARSE_NOT_ACCEPTABLE'; owner = $null; protected = $null; principal_count = 0 }
    }
    $acl = Get-Acl -LiteralPath $Path
    $count = @($acl.Access).Count
    return @{ exists = $true; owner = $acl.Owner; protected = $acl.AreAccessRulesProtected;
        principal_count = $count; status = 'READ_ONLY_DACL_INVENTORY_NOT_AUTHORIZATION' }
}

Test-ExactProjectRoot $ProjectRoot
$git = Get-Command git.exe -ErrorAction SilentlyContinue
$origin = $null
$branch = $null
$head = $null
if ($null -ne $git) {
    $origin = (& $git.Source -C $ProjectRoot remote get-url origin 2>$null | Select-Object -First 1)
    $branch = (& $git.Source -C $ProjectRoot branch --show-current 2>$null | Select-Object -First 1)
    $head = (& $git.Source -C $ProjectRoot rev-parse HEAD 2>$null | Select-Object -First 1)
}
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$vol = Get-Volume -DriveLetter D -ErrorAction SilentlyContinue
$fs = if ($null -ne $vol) { $vol.FileSystem } else { 'UNKNOWN' }
$watchdog = Get-Command taskkill.exe -ErrorAction SilentlyContinue
$controller = Join-Path $ProjectRoot '_trusted\g1\controller'
$broker = Join-Path $ProjectRoot '_trusted\g1\broker'
$worker = Join-Path $ProjectRoot '_trusted\g1\worker'
$witness = Join-Path $ProjectRoot '_trusted\g1\witness'

# No passwords, secrets, JWTs, raw dataset or hidden tensors are emitted.
$receipt = [ordered]@{
    schema = 'ttm.six.g1.windows_readonly_trust_preflight.v1'
    mode = 'READ_ONLY_NO_EXECUTION_NO_FILE_WRITE'
    project_root = $ProjectRoot
    machine = $env:COMPUTERNAME
    os = [Environment]::OSVersion.VersionString
    powershell = $PSVersionTable.PSVersion.ToString()
    identity_user_sid = $identity.User.Value
    drive_d_fs = $fs
    git_origin = $origin
    git_branch = $branch
    git_head = $head
    controller_acl = Get-SafeAclInventory $controller
    broker_acl = Get-SafeAclInventory $broker
    worker_acl = Get-SafeAclInventory $worker
    witness_acl = Get-SafeAclInventory $witness
    taskkill_exists = ($null -ne $watchdog)
    job_object_forced_kill_test = 'NOT_EXECUTED'
    separate_principal_negative_access_test = 'NOT_EXECUTED'
    test_byte_read = $false
    qwen_run = $false
    owner_authority_real = 'NOT_VERIFIED'
    external_monotonic_witness = 'NOT_VERIFIED'
    science_lock = 'HOLD'
}
$receipt | ConvertTo-Json -Depth 6
