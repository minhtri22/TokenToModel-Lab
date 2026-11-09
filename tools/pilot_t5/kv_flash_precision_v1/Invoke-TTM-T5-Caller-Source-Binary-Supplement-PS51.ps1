# Owner-local read-only forensic supplement for a completed TTM T5 Preview.
# It never reruns Preview, any model, llama.cpp, Torch, or the original 8 fixtures.
# Writes one NEW evidence JSON inside the TTM project, preserving old receipts.
[CmdletBinding()]
param(
    [string]$ProjectRoot='D:\WORK\RESEARCH\TokenToModel-Lab'
)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\')
if($root -ine 'D:\WORK\RESEARCH\TokenToModel-Lab'){throw 'PROJECT_ROOT_MISMATCH'}
if(-not (Test-Path -LiteralPath (Join-Path $root '.git'))){throw 'PROJECT_GIT_NOT_FOUND'}
$evidenceDir=Join-Path $root '_tmp\ttm_t5_f32_kvflash_owner_gate_20261109'
$preview=Join-Path $evidenceDir 'OWNER_LOCAL_PREVIEW_SINGLE_20261109.json'
$supplement=Join-Path $evidenceDir 'OWNER_LOCAL_SOURCE_BINARY_SUPPLEMENT_V1_20261109.json'
$originalSource='C:\Users\minht\Downloads\TTM_T5_F32_NUMERIC_LOCALIZATION_PS51_PRECLAIM_RECOVERY_V2_20261108\ttm_t5_layer_probe.cpp'
$oldBinary=Join-Path $root '_tmp\ttm_t5_numeric_localization_v1\build\Release\ttm_t5_layer_probe.exe'
$oldCmake=Join-Path $root '_tmp\ttm_t5_numeric_localization_v1\build\CMakeCache.txt'
$oldLog=Join-Path $root '_tmp\ttm_t5_numeric_localization_v1\fixture_0\native_run.log'
$expectedPreview='80be696c6e834a6028e1e3c4325c1eb624af65e69566a871019e83b089232d63'
$expectedSource='8a8324a10c67c6f868fe130d6ea7c535edb6364c8d04988600163e7b4a4b828e'
$expectedBinary='62fda558309502fdef9c736243b9a6194262fe0b5667949a0872fbe5c33e4de2'
function Get-TTMSHA([string]$p){return (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant()}
if(Test-Path -LiteralPath $supplement){throw 'SUPPLEMENT_ALREADY_EXISTS_ONE_SHOT_NO_OVERWRITE'}
foreach($p in @($preview,$originalSource,$oldBinary,$oldCmake,$oldLog)){
    if(-not (Test-Path -LiteralPath $p -PathType Leaf)){throw ('REQUIRED_FILE_NOT_FOUND: '+$p)}
    $it=Get-Item -LiteralPath $p -Force
    if($it.Attributes -band [IO.FileAttributes]::ReparsePoint){throw ('REPARSE_FILE_DENIED: '+$p)}
}
if((Get-TTMSHA $preview) -ne $expectedPreview){throw 'FROZEN_PREVIEW_SHA_MISMATCH'}
$old=Get-Content -LiteralPath $preview -Raw | ConvertFrom-Json
if($old.schema -ne 'ttm.t5.owner_local_preview_single.v1' -or
   $old.status -ne 'HOLD_OWNER_RUN_GATE' -or
   $old.native_inference -ne 'NOT_EXECUTED' -or
   $old.historical_strict -ne 'FAIL_7_OF_8_PRESERVED'){
    throw 'FROZEN_PREVIEW_STATUS_NOT_ACCEPTABLE'
}
$sourceSha=Get-TTMSHA $originalSource
$binarySha=Get-TTMSHA $oldBinary
$cmakeSha=Get-TTMSHA $oldCmake
$logSha=Get-TTMSHA $oldLog
$candidates=@($old.caller_cpp_candidates | Where-Object {$_.name -ceq 'ttm_t5_layer_probe.cpp'})
if($candidates.Count -ne 1){throw 'PREVIEW_SOURCE_INVENTORY_NOT_UNIQUE'}
$checks=[ordered]@{
    PreviewSHA=((Get-TTMSHA $preview) -eq $expectedPreview)
    SourceHashSameAsPreviewInventory=($sourceSha -eq $candidates[0].sha256)
    SourceHashMatchesOwnerObservedPin=($sourceSha -eq $expectedSource)
    OldExeSHA=($binarySha -eq $expectedBinary)
    OldExeSHAAgreesWithPreview=($binarySha -eq $old.old_probe_binary_sha256)
    OldCmakeSHAAgreesWithPreview=($cmakeSha -eq $old.old_cmake_cache_sha256)
    OldLogSHAAgreesWithPreview=($logSha -eq $old.old_native_log_sha256)
    OriginalNativeStillUntouched=($old.native_inference -eq 'NOT_EXECUTED')
    SourceAndBinaryHaveDistinctSHA=($sourceSha -ne $binarySha)
}
$cmake=Get-Content -LiteralPath $oldCmake
$sourceDirLines=@($cmake | Where-Object {$_ -match '^(ttm_t5_layer_probe_SOURCE_DIR:STATIC|CMAKE_HOME_DIRECTORY:INTERNAL)='})
$expectedParent='C:/Users/minht/Downloads/TTM_T5_F32_NUMERIC_LOCALIZATION_PS51_PRECLAIM_RECOVERY_V2_20261108'
$checks.BuildCmakeSourceDir=(@($sourceDirLines | Where-Object {$_ -match [regex]::Escape($expectedParent)}).Count -ge 1)

# Static lexical inspection only, NOT runtime proof. Preserve exact line numbers.
$raw=[IO.File]::ReadAllText($originalSource)
$rawLines=$raw -split "\r?\n"
$sourceHits=@()
for($i=0;$i -lt $rawLines.Length;$i++){
    if($rawLines[$i] -match '\bllama_context_default_params\b|\.type_k\b|\.type_v\b|\.flash_attn_type\b|llama_init_from_model\b'){
        $sourceHits+=@{line_number=($i+1);source_text=$rawLines[$i].Trim()}
    }
}
$uncommented=[regex]::Replace($raw,'(?s)/\*.*?\*/','')
$uncommented=[regex]::Replace($uncommented,'(?m)//[^\r\n]*','')
$usesDefault=($uncommented -match '\bllama_context_default_params\s*\(')
function Inspect-TTMField([string]$text,[string]$field,[bool]$hasDefaults) {
    $expression='\.'+[regex]::Escape($field)+'\s*=\s*([^;]+);'
    $matches=[regex]::Matches($text,$expression)
    $references=[regex]::Matches($text,'\.'+[regex]::Escape($field)+'\b').Count
    $rhs=@($matches | ForEach-Object {$_.Groups[1].Value.Trim()})
    $status='UNKNOWN_OR_DYNAMIC'
    if($matches.Count -eq 1 -and $references -eq 1 -and $rhs[0] -in @('GGML_TYPE_F16','GGML_TYPE_F32')){
        $status='EXPLICIT_STATIC_'+$rhs[0]
    } elseif($matches.Count -eq 0 -and $references -eq 0 -and $hasDefaults){
        $status='DEFAULT_FROM_LLAMA_CONTEXT_PARAMS_STATIC_ONLY'
    } elseif($matches.Count -gt 1){
        $status='MULTIPLE_ASSIGNMENTS_AMBIGUOUS'
    }
    return @{static_classification=$status;assignments=$rhs;reference_count=$references;assignment_count=$matches.Count}
}
$k=Inspect-TTMField $uncommented 'type_k' $usesDefault
$v=Inspect-TTMField $uncommented 'type_v' $usesDefault
$flash=Inspect-TTMField $uncommented 'flash_attn_type' $usesDefault
$ready=$true
foreach($c in $checks.GetEnumerator()){if(-not $c.Value){$ready=$false}}
$status=if($ready){'PASS_SOURCE_BINARY_HASH_INTEGRITY_STATIC_KV_PROOF_PENDING'}else{'HOLD_SHA_OR_CMAKE_INTEGRITY'}
$receipt=[ordered]@{
    schema='ttm.t5.caller_source_binary_supplement.owner_local.v1'
    original_preview_sha256=$expectedPreview
    original_preview_path=$preview
    source_path=$originalSource
    source_sha256=$sourceSha
    source_expected_sha256=$expectedSource
    historical_probe_executable_path=$oldBinary
    historical_probe_executable_sha256=$binarySha
    historical_probe_executable_expected_sha256=$expectedBinary
    cmake_sha256=$cmakeSha
    historical_log_sha256=$logSha
    cmake_source_dir_lines=$sourceDirLines
    checks=$checks
    uses_llama_context_default_params=$usesDefault
    caller_type_k=$k
    caller_type_v=$v
    caller_flash_attn_type=$flash
    source_relevant_lines=$sourceHits
    status=$status
    static_semantic_only=$true
    actual_runtime_KV_type='NOT_PROVEN_BY_SOURCE_ALONE'
    source_to_executable_bitwise_build_linkage='NOT_INDEPENDENTLY_PROVEN'
    original_preview_preserved=$true
    native_execution='NOT_EXECUTED'
    new_reference='NOT_GENERATED'
    new_2x2_runs=0
    historical_strict='FAIL_7_OF_8_PRESERVED'
}
$utf8=New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($supplement,(ConvertTo-Json -InputObject $receipt -Depth 16)+[Environment]::NewLine,$utf8)
Write-Output ('SUPPLEMENT_STATUS='+$status)
Write-Output ('SOURCE_SHA256='+$sourceSha)
Write-Output ('BINARY_SHA256='+$binarySha)
Write-Output ('SOURCE_BINARY_DISTINCT='+$checks.SourceAndBinaryHaveDistinctSHA)
Write-Output ('KV_K_STATIC='+$k.static_classification)
Write-Output ('KV_V_STATIC='+$v.static_classification)
Write-Output ('FLASH_STATIC='+$flash.static_classification)
Write-Output ('SOURCE_RELEVANT_LINES='+$sourceHits.Count)
Write-Output ('RESULT='+$supplement)
Write-Output ('RESULT_SHA256='+(Get-TTMSHA $supplement))
Write-Output ('NATIVE=NOT_EXECUTED')
