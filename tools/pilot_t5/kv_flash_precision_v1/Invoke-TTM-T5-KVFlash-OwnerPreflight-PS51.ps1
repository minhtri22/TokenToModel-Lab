# PowerShell 5.1. READ-ONLY preflight plus a single scoped project-local receipt.
# NO model inference, training, native execution, downloads, checkout or overwrite.
[CmdletBinding()]
param(
    [ValidateSet('Preview','OwnerGate')][string]$Mode = 'Preview',
    [string]$ProjectRoot = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$WorktreePath = 'D:\WORK\RESEARCH\TokenToModel-Lab',
    [string]$OriginalCallerSource = '',
    [string]$CheckpointFile = '',
    [string]$GGUFFile = '',
    [string]$ReferenceFile = '',
    [string]$CandidateExecutable = '',
    [string]$CandidateExeSHA256 = '',
    [switch]$CallerAttested,
    [switch]$OwnerApproval
)
$ErrorActionPreference = 'Stop'
# Resolve executable explicitly: PowerShell command lookup is case-insensitive.
$gitExe = (Get-Command -Name 'git.exe' -CommandType Application -ErrorAction Stop).Source
$expected = @{
  Branch='research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109'
  P02GitBlob='9762343e06cf800b50574c2871ae1ed58537fb18'
  PreregGitBlob='3b12cc1883ab20e2d9e3a92e6907586c1b4cad36'
  CheckpointSHA256='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
  GGUFsha256='5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5'
  OriginalProbeClaimSHA256='62fda558309502fdef9c736243b9a6194262fe0b5667949a0872fbe5c33e4de2'
  LlamaCommit='372dc5ca157276beb6c67b2e92477e8d662e964a'
  SourceDir='C:\Users\minht\Downloads\TTM_T5_F32_NUMERIC_LOCALIZATION_PS51_PRECLAIM_RECOVERY_V2_20261108'
}
$root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
$work=[IO.Path]::GetFullPath($WorktreePath).TrimEnd('\')
if ($root -ne 'D:\WORK\RESEARCH\TokenToModel-Lab') {throw 'PROJECT_ROOT_MISMATCH'}
if (-not (($work -eq $root) -or $work.StartsWith(($root+'\'),[StringComparison]::OrdinalIgnoreCase))) {
 throw 'WORKTREE_OUTSIDE_PROJECT'
}
if (-not (Test-Path -LiteralPath (Join-Path $work '.git'))) {throw 'WORKTREE_GIT_METADATA_NOT_FOUND'}
function Sha($p) { return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() }
function Invoke-TTMGit([string[]]$GitArgs) {
    $v=& $gitExe -C $work @GitArgs 2>&1
    if($LASTEXITCODE -ne 0){throw "GIT_COMMAND_FAILED:$($GitArgs -join ' ') $v"}
    return ($v | Out-String).Trim()
}
function InProject([string]$p) {
    if (-not $p -or -not (Test-Path -LiteralPath $p -PathType Leaf)) {return $false}
    $candidate=[IO.Path]::GetFullPath($p)
    if (-not $candidate.StartsWith(($root+'\'),[StringComparison]::OrdinalIgnoreCase)) {return $false}
    $cur=Get-Item -LiteralPath $p -Force
    while($cur -and $cur.FullName.Length -ge $root.Length) {
        if($cur.Attributes -band [IO.FileAttributes]::ReparsePoint) {return $false}
        if($cur.PSIsContainer){$cur=$cur.Parent}else{$cur=$cur.Directory}
    }
    return $true
}
$checks=[ordered]@{}
$notes=New-Object System.Collections.Generic.List[string]
$branchName=Invoke-TTMGit -GitArgs @('rev-parse','--abbrev-ref','HEAD')
$checks.Branch=($branchName -eq $expected.Branch)
$checks.CleanTracked=([string]::IsNullOrWhiteSpace((Invoke-TTMGit -GitArgs @('status','--porcelain','--untracked-files=no'))))
$checks.P02GitBlob=( (Invoke-TTMGit -GitArgs @('hash-object','src/p02/transformer_core.py')) -eq $expected.P02GitBlob)
$relativePrereg='artifacts/qa/ttm-t5-parity/TTM_T5_KV_FLASH_2X2_FRESH_SYNTHETIC_PREREG_20261109.json'
$checks.PreregGitBlob=((Invoke-TTMGit -GitArgs @('hash-object',$relativePrereg)) -eq $expected.PreregGitBlob)
$llamaRoot=Join-Path $root '_tmp\ttm_t2\llama.cpp'
if(Test-Path -LiteralPath (Join-Path $llamaRoot '.git')) {
    $actualLlama=(& $gitExe -C $llamaRoot rev-parse HEAD 2>&1 | Out-String).Trim()
    $checks.LlamaCommit=($LASTEXITCODE -eq 0 -and $actualLlama -eq $expected.LlamaCommit)
} else { $checks.LlamaCommit=$false }
$cache=Join-Path $root '_tmp\ttm_t5_numeric_localization_v1\build\CMakeCache.txt'
$log=Join-Path $root '_tmp\ttm_t5_numeric_localization_v1\fixture_0\native_run.log'
$checks.OldBuildRecord=(Test-Path -LiteralPath $cache)
$checks.OldFlashRuntimeLog=$false
if(Test-Path -LiteralPath $log) {
  $checks.OldFlashRuntimeLog=((Select-String -LiteralPath $log -SimpleMatch -Pattern 'FLASH_ATTN_EXT' | Measure-Object).Count -gt 0)
}
$historicDir=''
if($checks.OldBuildRecord){
  $hits=Select-String -LiteralPath $cache -Pattern '^ttm_t5_layer_probe_SOURCE_DIR:STATIC=(.*)$'
  if($hits.Count -eq 1){$historicDir=$hits[0].Matches[0].Groups[1].Value.Replace('/','\')}
}
$checks.OldCMakeSourceDir=($historicDir.TrimEnd('\') -ieq $expected.SourceDir)
$checks.CallerSourceSHA=$false
$checks.CallerSourceParams=$false
$callerEvidence=@{source='';sha256='';type_k='UNKNOWN';type_v='UNKNOWN';flash='RUNTIME_GRAPH_FLASH_ATTN_EXT_ONLY';text_lines=@()}
if($OriginalCallerSource) {
  $source=[IO.Path]::GetFullPath($OriginalCallerSource)
  $sourceParent=[IO.Path]::GetDirectoryName($source).TrimEnd('\')
  if($sourceParent -ine $expected.SourceDir){throw 'CALLER_SOURCE_NOT_IN_HISTORIC_CMAKE_DIRECTORY'}
  if(-not (Test-Path -LiteralPath $source -PathType Leaf)){throw 'CALLER_FILE_NOT_FOUND'}
  $callerEvidence.source=$source
  $callerEvidence.sha256=Sha $source
  $checks.CallerSourceSHA=($callerEvidence.sha256 -eq $expected.OriginalProbeClaimSHA256)
  $raw=[IO.File]::ReadAllText($source)
  $withoutBlock=[regex]::Replace($raw,'(?s)/\*.*?\*/','')
  $withoutComments=[regex]::Replace($withoutBlock,'(?m)//[^\r\n]*','')
  $lines=($withoutComments -split "\r?\n")
  $callerEvidence.text_lines=@($lines | Where-Object {$_ -match '\.type_k\s*=|\.type_v\s*=|\.flash_attn_type\s*=|llama_context_default_params\s*\('} | ForEach-Object {$_.Trim()})
  $usesDefaults=($withoutComments -match 'llama_context_default_params\s*\(')
  foreach($field in @('type_k','type_v')){
    $matches=[regex]::Matches($withoutComments,'\b[A-Za-z_][A-Za-z_0-9]*\.'+$field+'\s*=\s*(GGML_TYPE_F16|GGML_TYPE_F32)\s*;')
    $allReferences=[regex]::Matches($withoutComments,'\.'+$field+'\b').Count
    if($matches.Count -eq 1 -and $allReferences -eq 1){
      $callerEvidence[$field]=$matches[0].Groups[1].Value
    } elseif($matches.Count -eq 0 -and $allReferences -eq 0 -and $usesDefaults) {
      $callerEvidence[$field]='DEFAULT_GGML_TYPE_F16_STATIC_INFERENCE'
    } else { $callerEvidence[$field]='AMBIGUOUS' }
  }
  $checks.CallerSourceParams=($callerEvidence.type_k -ne 'AMBIGUOUS' -and $callerEvidence.type_v -ne 'AMBIGUOUS' -and $callerEvidence.type_k -ne 'UNKNOWN' -and $callerEvidence.type_v -ne 'UNKNOWN')
}
$checks.GGUFExact=(InProject $GGUFFile)
if($checks.GGUFExact){$checks.GGUFExact=((Sha $GGUFFile) -eq $expected.GGUFsha256)}
$checks.CheckpointExact=(InProject $CheckpointFile)
if($checks.CheckpointExact){$checks.CheckpointExact=((Sha $CheckpointFile) -eq $expected.CheckpointSHA256)}
$checks.ReferenceReady=(InProject $ReferenceFile)
if($checks.ReferenceReady){$checks.ReferenceReady=((Get-Content -LiteralPath $ReferenceFile | Measure-Object -Line).Lines -eq 8)}
$checks.CandidateExecutablePinned=(InProject $CandidateExecutable)
if($checks.CandidateExecutablePinned){
  $checks.CandidateExecutablePinned=($CandidateExeSHA256 -match '^[a-fA-F0-9]{64}$' -and (Sha $CandidateExecutable) -eq $CandidateExeSHA256.ToLowerInvariant())
}
$checks.CallerOwnerAttested=($CallerAttested.IsPresent -and $checks.CallerSourceSHA -and $checks.CallerSourceParams)
$checks.OwnerApproval=$OwnerApproval.IsPresent
# This tool NEVER runs the executable; it only decides whether an owner-approved run could be started.
$allReady=@($checks.GetEnumerator() | Where-Object { -not $_.Value }).Count -eq 0
$status=if($Mode -eq 'OwnerGate' -and $allReady){'READY_FOR_ONE_NEW_SYNTHETIC_BATCH_NOT_EXECUTED'}else{'HOLD_OWNER_RUN_GATE'}
$receipt=[ordered]@{
  schema='ttm.t5.f32_kv_flash.owner_run_gate.v1'
  mode=$Mode; status=$status; project_root=$root; worktree=$work
  caller=$callerEvidence; checks=$checks; expected=$expected
  fixed_threshold=0.001; new_synthetic_fixtures=8; n_conditions=4
  native_execution='NOT_EXECUTED'; training='NO'; test='UNTOUCHED'
  old_strict_logits='FAIL_7_OF_8_PRESERVED'
}
$tmpRoot=Join-Path $root '_tmp'
if((Get-Item -LiteralPath $tmpRoot -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'TEMP_ROOT_REPARSE_POINT'}
$outDir=Join-Path $root '_tmp\ttm_t5_f32_kvflash_owner_gate_20261109'
if((Test-Path -LiteralPath $outDir) -and ((Get-Item -LiteralPath $outDir -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'OUTPUT_DIR_REPARSE_POINT'}
if(-not (Test-Path -LiteralPath $outDir)){New-Item -ItemType Directory -Path $outDir -Force | Out-Null}
$name='TTM_T5_KVFLASH_'+$Mode+'_'+([DateTime]::UtcNow.ToString('yyyyMMdd_HHmmss_fffffff'))+'.json'
$outPath=Join-Path $outDir $name
$txt=ConvertTo-Json -InputObject $receipt -Depth 15
$utf8=New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($outPath,$txt+[Environment]::NewLine,$utf8)
Write-Output ("T5_OWNER_GATE_STATUS="+$status)
Write-Output ("CALLER_SOURCE_SHA_MATCH="+$checks.CallerSourceSHA)
Write-Output ("CALLER_TYPE_K="+$callerEvidence.type_k)
Write-Output ("CALLER_TYPE_V="+$callerEvidence.type_v)
Write-Output ("RESULT="+$outPath)
Write-Output ("RESULT_SHA256="+(Sha $outPath))
if($status -ne 'READY_FOR_ONE_NEW_SYNTHETIC_BATCH_NOT_EXECUTED' -and $Mode -eq 'OwnerGate'){exit 3}
