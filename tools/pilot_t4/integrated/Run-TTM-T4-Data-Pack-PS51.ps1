<# TTM T4 read-only Preview / one-shot private TRAIN+VAL data pack. No Git writes/training/TEST tokens. #>
[CmdletBinding()]
param([ValidateSet('Preview','Execute')][string]$Mode='Preview')
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$project='https://github.com/minhtri22/TokenToModel-Lab.git'
$baseline='1a9d8cba56564d6d36257fe95c34f2fd52c4f48a'
$raw=Join-Path $root 'datasets\tinystories_v1_original_pinned'
$t1=Join-Path $root '_tmp\ttm_t1_real_source_v1'
$output=Join-Path $root '_tmp\ttm_t4_data_pack_v1'
$py=Join-Path $root '_tmp\ttm_t2\py313_cpu_venv\Scripts\python.exe'
$tools=Split-Path -Parent $MyInvocation.MyCommand.Path

function SHA([string]$p) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)){throw ('MISSING_FILE='+$p)}
    return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()
}
function RequireSHA([string]$p,[string]$h) {
    if ((SHA $p) -cne $h){throw ('SHA_MISMATCH='+$p)}
}
function GitOut([string[]]$a) {
    $value=(& git @a 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0){throw ('GIT_EXIT_FAILURE='+$value)}
    return $value
}
if (-not (Test-Path -LiteralPath $root -PathType Container)){throw 'WRONG_REPOSITORY_NOT_FOUND'}
$gitTop=GitOut -a @('-C',$root,'rev-parse','--show-toplevel')
if ($gitTop.Replace('/','\').TrimEnd('\') -ine $root.TrimEnd('\')){throw 'WRONG_GIT_TOP'}
$origin=GitOut -a @('-C',$root,'remote','get-url','origin')
if ($origin -cne $project -and $origin -cne 'https://github.com/minhtri22/TokenToModel-Lab'){throw 'WRONG_ORIGIN'}
if ((GitOut -a @('-C',$root,'rev-parse','refs/heads/main')) -cne $baseline){throw 'LOCAL_MAIN_DRIFT'}
if ((GitOut -a @('-C',$root,'ls-remote','origin','refs/heads/main')).Split("`t")[0] -cne $baseline){throw 'REMOTE_MAIN_DRIFT'}
$expect=@{
    't1_source_split_tokenizer.py'='91bcc4b5a871c51556ebeb2616d52e995f9850165e69054fea963e395db0603f'
    'source_t2\ttm_gpt2_bpe2048.py'='36d66a1f569b502b7c9def6215fa296de57822146f7845b6d67151982d4ce961'
    'p02_source_exact.py'='e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07'
}
foreach($k in $expect.Keys){RequireSHA (Join-Path $tools $k) $expect[$k]}
RequireSHA (Join-Path $raw 'TinyStories-train.txt') 'c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f'
RequireSHA (Join-Path $raw 'TinyStories-valid.txt') '94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4'
RequireSHA (Join-Path $t1 'T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json') '9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
RequireSHA (Join-Path $t1 'T1_BPE2048_REAL_TRAIN_MANIFEST.json') 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
if (-not (Test-Path -LiteralPath $py -PathType Leaf)){throw 'PINNED_TTM_CPU_PYTHON_MISSING'}
if (Test-Path -LiteralPath $output){throw 'T4_PRIVATE_PACK_ALREADY_EXISTS_NO_RERUN'}
if (-not (Test-Path -LiteralPath (Join-Path $tools 't4_data_pack.py') -PathType Leaf)){throw 'T4_DATA_PACK_SCRIPT_MISSING'}
Write-Host 'TTM_T4_DATA_SOURCE_T1_SHA_AND_ORIGIN=PASS_EXACT'
Write-Host ('TTM_T4_DATA_MODE='+$Mode)
Write-Host 'T4_TEST_NOT_TOKENIZED=TRUE'
if($Mode -eq 'Preview'){
    Write-Host 'TTM_T4_DATA_PACK_PREVIEW=PASS_READONLY'
    exit 0
}
& $py (Join-Path $tools 't4_data_pack.py') --repo $root --out $output
if($LASTEXITCODE -ne 0){throw ('T4_DATA_PACK_EXIT='+$LASTEXITCODE+' KEEP_INPUTS_OUTPUT_NO_RERUN')}
Write-Host 'TTM_T4_PRIVATE_PACK_EXECUTED_READBACK_REQUIRED'
Write-Host 'TTM_T4_SCIENCE_NOT_EXECUTED'
