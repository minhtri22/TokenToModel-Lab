#Requires -Version 5.1
<#
G1 private metadata manifest. All file writes remain under project root.
Modes: SelfTest, Preflight, Tokenizers, Seal, QA.
No TTM main/PR12/lineage writes; no GPU, no teacher model weights, no
scientific outputs. Seal requires explicit owner private-scope acceptance.
#>
[CmdletBinding()]
param(
 [ValidateSet('SelfTest','Preflight','Tokenizers','Seal','QA')]
 [string]$Mode='Preflight',
 [switch]$OwnerAcceptPrivateScope
)
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$target=Join-Path $root '_tmp\ttm_six_g1_private_manifest_v1'
$dest=Join-Path $target 'g1_private_manifest_train_only_v1a.py'
$sha='aee230060f8202907953e0eeab0ae5b1099a584e'
$sourceCommit='0dd7fd87861e53ba468249a579ceb5d3545e2fb2'
$url="https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/$sourceCommit/scripts/research/six_ttm/g1_private_manifest_train_only_v1a.py"
$py='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath (Join-Path $root '.git'))) { throw 'STOP_ROOT_NOT_GIT' }
$origin=(& git -C $root remote get-url origin | Select-Object -First 1).ToLowerInvariant().Trim()
if ($LASTEXITCODE -ne 0 -or @(
 'https://github.com/minhtri22/tokentomodel-lab',
 'https://github.com/minhtri22/tokentomodel-lab.git',
 'git@github.com:minhtri22/tokentomodel-lab',
 'git@github.com:minhtri22/tokentomodel-lab.git'
 ) -notcontains $origin) { throw 'STOP_REPO_ORIGIN_MISMATCH' }
if (-not (Test-Path -LiteralPath $py)) { throw 'STOP_PYTHON312_NOT_INSTALLED' }
& $py -c 'import sys; assert sys.version_info[:2]==(3,12),sys.version; print("G1_LOCAL_PYTHON="+sys.version.split()[0])'
if ($LASTEXITCODE -ne 0) { throw 'STOP_PYTHON312_VERSION' }
if (Test-Path -LiteralPath $target) {
 $i=Get-Item -LiteralPath $target -Force
 if (($i.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw 'STOP_TARGET_REPARSE'
 }
} else {
 New-Item -ItemType Directory -Path $target -ErrorAction Stop | Out-Null
}
if (-not (Test-Path -LiteralPath $dest)) {
 [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12
 Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $dest -ErrorAction Stop
}
$blob=(& git -C $root hash-object $dest).Trim().ToLowerInvariant()
if ($LASTEXITCODE -ne 0 -or $blob -ne $sha) { throw 'STOP_SCRIPT_GIT_BLOB_MISMATCH' }
$actualSource=Get-Item -LiteralPath $dest -Force
if (($actualSource.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
 throw 'STOP_SCRIPT_REPARSE'
}
$env:HF_HOME=Join-Path $target 'hf_home'
$env:HF_HUB_CACHE=Join-Path $target 'hf_home\hub'
$env:HF_DATASETS_CACHE=Join-Path $target 'hf_home\datasets'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPYCACHEPREFIX=Join-Path $target 'pycache'
$env:PIP_CACHE_DIR=Join-Path $target 'pipcache'
$env:TMP=Join-Path $target 'tmp'
$env:TEMP=$env:TMP
$env:TMPDIR=$env:TMP
$ErrorActionPreference='Stop'
& $py -c "import ast,pathlib; ast.parse(pathlib.Path(r'$dest').read_text(encoding='utf-8')); print('G1_SOURCE_AST_PARSE=PASS')"
if ($LASTEXITCODE -ne 0) { throw 'STOP_G1_SOURCE_AST_PARSE' }
$modeArgument=$Mode.ToLowerInvariant()
if ($Mode -eq 'QA') {
 $qaCommit='e8a70580c4cf7fd7075029ed201cb39d3a766597'
 $qaBlob='7dfc6bea2cee1773c20fee655691fc366a6a9ecd'
 $qaDest=Join-Path $target 'g1_private_manifest_independent_readonly_qa_v1.py'
 $qaUrl="https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/$qaCommit/scripts/research/six_ttm/g1_private_manifest_independent_readonly_qa_v1.py"
 if (-not (Test-Path -LiteralPath $qaDest)) {
  Invoke-WebRequest -UseBasicParsing -Uri $qaUrl -OutFile $qaDest
 }
 $qaActual=(& git -C $root hash-object $qaDest).Trim().ToLowerInvariant()
 if ($LASTEXITCODE -ne 0 -or $qaActual -ne $qaBlob) { throw 'STOP_G1_QA_SOURCE_BLOB_MISMATCH' }
 & $py -B $qaDest --mode selftest
 if ($LASTEXITCODE -ne 0) { throw 'STOP_G1_QA_SELFTEST_FAIL' }
 & $py -B $qaDest --mode verify
} elseif ($Mode -eq 'Seal') {
 if (-not $OwnerAcceptPrivateScope) {
    throw 'STOP_SCOPE_NOT_ACKNOWLEDGED_USE_-OwnerAcceptPrivateScope'
 }
 & $py -B $dest --mode seal --owner-accept-scope YES_PRIVATE_COMPUTATIONAL_G1_NO_RAW_PUBLICATION
} else {
 & $py -B $dest --mode $modeArgument
}
if ($LASTEXITCODE -ne 0) { throw ('STOP_G1_'+$Mode.ToUpperInvariant()+'_FAILED') }
Write-Output ('G1_LOCAL_STEP='+$Mode.ToUpperInvariant()+'_COMPLETED')
