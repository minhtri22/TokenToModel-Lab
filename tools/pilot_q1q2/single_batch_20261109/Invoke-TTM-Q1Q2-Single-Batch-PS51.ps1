param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{40}$')][string]$ExpectedHead,
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{64}$')][string]$RunnerSha,
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-f]{64}$')][string]$TestSha,
    [ValidateSet('QA','Preview','Execute')][string]$Mode='QA'
)
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$main='b57b44e7287f842e81050c1faee337f636333dd0'
$branch='research/ttm-small4m-q1q2-quality-single-batch-20261109'
$remote='https://github.com/minhtri22/TokenToModel-Lab.git'
$py='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$src=Join-Path $root ('_tmp\TTM_Q1Q2_BOOTSTRAP_'+$ExpectedHead.Substring(0,12))
$out=Join-Path $root '_tmp\ttm_q1q2_ollama_once_v1'
$stage=Join-Path $out 'github_publish_checkout'
$readback=Join-Path $out 'github_readback_checkout'
$prefix='artifacts/qa/q1q2/TTM_Q1Q2_ONCE_V1'
$runner='ttm_q1q2_single_batch.py'
$test='test_ttm_q1q2_offline.py'
function Require([bool]$ok,[string]$why) { if (-not $ok) { throw $why } }
function GitValue([string[]]$Cmd) {
    $txt=(& git -C $root @Cmd 2>&1 | Out-String).Trim()
    Require ($LASTEXITCODE -eq 0) ('GIT_FAILED:'+($Cmd -join ' '))
    return $txt
}
function CheckSha([string]$path,[string]$want) {
    Require (Test-Path -LiteralPath $path -PathType Leaf) ('FILE_MISSING:'+ $path)
    Require (((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()) -ceq $want) ('SHA256_MISMATCH:'+ $path)
}
function NoReparse([string]$path) {
    $here=[IO.Path]::GetFullPath($path)
    while ($true) {
        if (Test-Path -LiteralPath $here) {
            $it=Get-Item -LiteralPath $here -Force
            Require (-not (($it.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) ('REPARSE_POINT:'+ $here)
        }
        $parent=[IO.Path]::GetDirectoryName($here)
        if ([string]::IsNullOrEmpty($parent) -or $parent -ceq $here) { break }
        $here=$parent
    }
}
Require (Test-Path -LiteralPath (Join-Path $root '.git')) 'REPO_MISSING'
Require ((GitValue @('symbolic-ref','--short','HEAD')) -ceq 'main') 'LOCAL_BRANCH_NOT_MAIN'
Require ((GitValue @('rev-parse','HEAD')) -ceq $main) 'LOCAL_MAIN_NOT_PINNED'
Require ((GitValue @('remote','get-url','origin')) -ceq $remote) 'WRONG_GITHUB_ORIGIN'
$remoteSha=(& git -C $root ls-remote origin ('refs/heads/'+$branch) 2>&1 | Out-String).Trim()
Require ($LASTEXITCODE -eq 0) 'GITHUB_BRANCH_LOOKUP_FAILED'
Require ($remoteSha -match ('^'+$ExpectedHead+'\s+refs/heads/')) 'Q1Q2_HEAD_CHANGED'
Require (Test-Path -LiteralPath $py -PathType Leaf) 'PYTHON312_NOT_FOUND'
& $py -I -c 'import sys; assert sys.version_info[:2] == (3, 12); import regex'
Require ($LASTEXITCODE -eq 0) 'PYTHON312_DEPENDENCIES_HOLD'
NoReparse $root
NoReparse $src
NoReparse $out
Require (-not (Test-Path -LiteralPath $src)) 'BOOTSTRAP_ALREADY_EXISTS_NO_OVERWRITE'
New-Item -ItemType Directory -Path $src -ErrorAction Stop | Out-Null
foreach($name in @($runner,$test)) {
    $url='https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/'+$ExpectedHead+'/tools/pilot_q1q2/single_batch_20261109/'+$name
    Invoke-WebRequest -Uri $url -UseBasicParsing -OutFile (Join-Path $src $name) -TimeoutSec 60
}
CheckSha (Join-Path $src $runner) $RunnerSha
CheckSha (Join-Path $src $test) $TestSha
Write-Host 'TTM_Q1Q2_SOURCE_GITHUB_SHA256=PASS'
& $py -I (Join-Path $src $test)
Require ($LASTEXITCODE -eq 0) 'OFFLINE_UNIT_QA_FAILED'
& $py -I (Join-Path $src $runner) --mode qa
Require ($LASTEXITCODE -eq 0) 'FROZEN_INPUT_QA_FAILED'
Write-Host 'TTM_Q1Q2_OFFLINE_QA=PASS'
if ($Mode -ceq 'QA') { Write-Host 'TTM_Q1Q2_NATIVE=NOT_EXECUTED'; exit 0 }
& $py -I (Join-Path $src $runner) --mode preview
Require ($LASTEXITCODE -eq 0) 'NATIVE_PREVIEW_FAILED_NO_CLAIM'
Write-Host 'TTM_Q1Q2_PREVIEW=PASS_READONLY'
if ($Mode -ceq 'Preview') { Write-Host 'TTM_Q1Q2_NATIVE=NOT_EXECUTED'; exit 0 }
Require (-not (Test-Path -LiteralPath $out)) 'ONE_SHOT_CONSUMED_NO_RERUN'
& $py -I (Join-Path $src $runner) --mode execute
$nativeExit=$LASTEXITCODE
Require (Test-Path -LiteralPath (Join-Path $out 'RESULT.json') -PathType Leaf) 'NATIVE_RESULT_MISSING_KEEP_CLAIM'
$native = Get-Content -LiteralPath (Join-Path $out 'RESULT.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$required=([string]$native.status -ceq 'PASS_EXECUTED_SCOPED' -and $nativeExit -eq 0)
Write-Host ('TTM_Q1Q2_NATIVE_RESULT='+$native.status)
Write-Host ('TTM_Q1Q2_NATIVE_EXIT='+$nativeExit)
# Publish PASS or HOLD evidence once, without rerunning a single native request.
Require (-not (Test-Path -LiteralPath $stage)) 'PUBLISH_CHECKOUT_EXISTS'
& git clone --no-tags --single-branch --branch $branch $remote $stage
Require ($LASTEXITCODE -eq 0) 'EVIDENCE_CLONE_FAILED_PRESERVE_NATIVE'
$checkoutHead=(& git -C $stage rev-parse HEAD).Trim()
Require ($checkoutHead -ceq $ExpectedHead) 'PUBLISH_BRANCH_MOVED_KEEP_LOCAL_EVIDENCE'
$dest=Join-Path $stage ($prefix.Replace('/','\'))
Require (-not (Test-Path -LiteralPath $dest)) 'EVIDENCE_ALREADY_EXISTS'
New-Item -Path $dest -ItemType Directory -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $out 'CLAIM.json') -Destination $dest
Copy-Item -LiteralPath (Join-Path $out 'RESULT.json') -Destination $dest
if (Test-Path -LiteralPath (Join-Path $out 'raw')) {
    Copy-Item -LiteralPath (Join-Path $out 'raw') -Destination (Join-Path $dest 'raw') -Recurse
}
$manifest=@{}
Get-ChildItem -LiteralPath $dest -Recurse -File | ForEach-Object {
    $rel=$_.FullName.Substring($dest.Length+1).Replace('\','/')
    $manifest[$rel]=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
}
$manifestPath=Join-Path $dest 'PUBLISHED_FILES_SHA256.json'
[IO.File]::WriteAllText($manifestPath,($manifest | ConvertTo-Json -Depth 6)+"`n",(New-Object System.Text.UTF8Encoding($false)))
& git -C $stage add -- $prefix
Require ($LASTEXITCODE -eq 0) 'GIT_ADD_EVIDENCE_FAILED'
& git -C $stage -c user.name='TTM Research Evidence' -c user.email='ttm-evidence@users.noreply.github.com' commit -m ('evidence(q1q2): single native batch '+$native.status)
Require ($LASTEXITCODE -eq 0) 'GIT_COMMIT_EVIDENCE_FAILED'
$evidenceCommit=(& git -C $stage rev-parse HEAD).Trim()
& git -C $stage push origin ('HEAD:refs/heads/'+$branch)
Require ($LASTEXITCODE -eq 0) 'GITHUB_PUSH_FAILED_KEEP_RAW'
Write-Host ('TTM_Q1Q2_EVIDENCE_COMMIT='+$evidenceCommit)
# Independent GitHub readback into a separate fresh checkout.
Require (-not (Test-Path -LiteralPath $readback)) 'READBACK_DIR_EXISTS'
& git clone --no-tags --single-branch --branch $branch $remote $readback
Require ($LASTEXITCODE -eq 0) 'GITHUB_READBACK_CLONE_FAILED'
Require ((& git -C $readback rev-parse HEAD).Trim() -ceq $evidenceCommit) 'GITHUB_READBACK_COMMIT_MISMATCH'
foreach($e in $manifest.GetEnumerator()) {
    $p=Join-Path $readback (($prefix+'/'+$e.Key).Replace('/','\'))
    CheckSha $p $e.Value
}
$manifestExpected=(Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
CheckSha (Join-Path $readback (($prefix+'/PUBLISHED_FILES_SHA256.json').Replace('/','\'))) $manifestExpected
Write-Host ('TTM_Q1Q2_GITHUB_READBACK=PASS_ALL_'+($manifest.Count+1)+'_EVIDENCE_FILES')
Write-Host 'TTM_Q1Q2_ONE_SHOT_CONSUMED=TRUE'
Write-Host 'TTM_Q1Q2_RAW_LOCAL=PRESERVED_UNTIL_INDEPENDENT_ADJUDICATION'
# Cleanup is limited to this run's temporary Git clones/bootstrap; preserve one-shot
# CLAIM, RESULT, raw outputs, and model store until scientific adjudication.
if ($required) {
    foreach ($temporary in @($readback,$stage,$src)) {
        try {
            NoReparse $temporary
            Require ($temporary.StartsWith((Join-Path $root '_tmp')+'\',[StringComparison]::OrdinalIgnoreCase)) 'CLEANUP_PATH_OUTSIDE_PROJECT_TMP'
            Remove-Item -LiteralPath $temporary -Recurse -Force -ErrorAction Stop
            Write-Host ('TTM_Q1Q2_SCOPED_TEMP_CLEANED='+$temporary)
        } catch {
            Write-Host ('TTM_Q1Q2_CLEANUP_HOLD_PRESERVED='+$temporary+' ERROR='+$_.Exception.Message)
        }
    }
} else {
    Write-Host 'TTM_Q1Q2_CLEANUP=SKIPPED_PARTIAL_HOLD'
}
Write-Host 'TTM_Q1Q2_RAW_AND_MODEL_STORE=PRESERVED_UNTIL_SCIENCE_ADJUDICATION'
if (-not $required) { Write-Host 'TTM_Q1Q2_MERGE_DECISION=HOLD_PARTIAL';exit 4 }
Write-Host 'TTM_Q1Q2_MERGE_DECISION=HOLD_PENDING_SCIENCE_REVIEW'
exit 0
