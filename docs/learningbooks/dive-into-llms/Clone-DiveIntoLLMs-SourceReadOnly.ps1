#Requires -Version 5.1
<#
.SYNOPSIS
  Clone upstream Dive into LLMs for local READ-ONLY source study.
  No installation, no model execution, no repository commit or cleanup.
.DESCRIPTION
  Pinned source snapshot into TTM_ROOT\_tmp\learningbooks\dive-into-llms.
  Sparse checkout only upstream README text; PDFs/notebooks are not checked out.
  This is a helper script, NOT evidence of execution.
#>
[CmdletBinding()]
param(
    [string]$TtmRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab'
)
$ErrorActionPreference = 'Stop'
$SourceUrl = 'https://github.com/Lordog/dive-into-llms.git'
$ExpectedHead = 'f84c04268794ef94f8949808bbc14ab8636763a0'
$Files = @(
    'README.md',
    'documents/chapter1/README.md',
    'documents/chapter2/README.md',
    'documents/chapter3/README.md',
    'documents/chapter4/README.md',
    'documents/chapter10/README.md',
    'documents/chapter11/README.md'
)

function Invoke-GitChecked {
    param([string[]]$Argv)
    & git @Argv
    if ($LASTEXITCODE -ne 0) { throw ('GIT_COMMAND_FAILED: ' + ($Argv -join ' ')) }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'GIT_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $TtmRoot -PathType Container)) { throw 'TTM_ROOT_NOT_FOUND' }
$RealRoot = (& git -C $TtmRoot rev-parse --show-toplevel)
if ($LASTEXITCODE -ne 0) { throw 'TTM_GIT_ROOT_UNVERIFIED' }
$RealRoot = [System.IO.Path]::GetFullPath($RealRoot.Trim()).TrimEnd('\')
$ExpectedRoot = [System.IO.Path]::GetFullPath($TtmRoot).TrimEnd('\')
if (-not [string]::Equals($RealRoot, $ExpectedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'TTM_ROOT_SCOPE_MISMATCH'
}
$Origin = (& git -C $TtmRoot remote get-url origin)
if ($LASTEXITCODE -ne 0 -or $Origin -notmatch '(?i)github\.com[:/]minhtri22/TokenToModel-Lab(\.git)?$') {
    throw 'TTM_ORIGIN_MISMATCH'
}
$Parent = Join-Path $TtmRoot '_tmp\learningbooks'
$Dest = Join-Path $Parent 'dive-into-llms'
if (Test-Path -LiteralPath $Dest) { throw 'SOURCE_DEST_ALREADY_EXISTS_NO_OVERWRITE' }
New-Item -ItemType Directory -Path $Parent -Force | Out-Null

Invoke-GitChecked -Argv @('clone', '--depth', '1', '--filter=blob:none', '--no-checkout', $SourceUrl, $Dest)
$Patterns = @('/README.md', '/documents/chapter1/README.md', '/documents/chapter2/README.md',
              '/documents/chapter3/README.md', '/documents/chapter4/README.md',
              '/documents/chapter10/README.md', '/documents/chapter11/README.md')
Invoke-GitChecked -Argv (@('-C', $Dest, 'sparse-checkout', 'set', '--no-cone') + $Patterns)
Invoke-GitChecked -Argv @('-C', $Dest, 'checkout', '--detach', $ExpectedHead)

$ActualHead = (& git -C $Dest rev-parse HEAD)
if ($LASTEXITCODE -ne 0 -or $ActualHead.Trim() -ne $ExpectedHead) { throw 'UPSTREAM_COMMIT_PIN_MISMATCH' }
$Records = @()
foreach ($Relative in $Files) {
    $FilePath = Join-Path $Dest ($Relative.Replace('/', '\'))
    if (-not (Test-Path -LiteralPath $FilePath -PathType Leaf)) { throw ('MISSING_SOURCE_FILE: ' + $Relative) }
    $Hash = (Get-FileHash -LiteralPath $FilePath -Algorithm SHA256).Hash.ToLowerInvariant()
    $Records += [pscustomobject]@{ path = $Relative; sha256 = $Hash }
}
$Receipt = [ordered]@{
    operation = 'TTM_DIVE_INTO_LLMS_UPSTREAM_PINNED_CLONE_READONLY'
    source = $SourceUrl
    expected_head = $ExpectedHead
    actual_head = $ActualHead.Trim()
    status = 'PASS_SCOPED_SOURCE_CLONE_ONLY'
    scientific_execution = $false
    model_download = $false
    rights_to_publish_translation = 'NOT_VERIFIED'
    files = $Records
}
$ReceiptPath = Join-Path $Parent 'source_clone_receipt.json'
$Receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $ReceiptPath -Encoding UTF8
Write-Output ('UPSTREAM_CLONE=PASS_PINNED ' + $ExpectedHead)
Write-Output ('RECEIPT=' + $ReceiptPath)
Write-Output 'NO_SCIENCE=TRUE; NO_TRANSLATION_PUBLISH=TRUE; NO_COMMIT=TRUE'
