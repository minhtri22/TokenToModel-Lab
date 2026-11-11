# TTM Vector Memory - exact real T1 BPE compatibility QA, Windows PowerShell 5.1
# Run from the research branch checkout/worktree inside owner root. Read-only inputs.
# One output receipt under owner root _evidence. No TEST decrypt, training, inference or GPU.
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$checkoutRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..\..')).Path
$allowedPrefix = $root.TrimEnd('\') + '\'
if (($checkoutRoot -ne $root) -and (-not $checkoutRoot.StartsWith($allowedPrefix, [StringComparison]::OrdinalIgnoreCase))) { throw 'CHECKOUT_OUTSIDE_TTM_ROOT_DENIED' }
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$manifest = Join-Path $root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
$source = Join-Path $checkoutRoot 'tools\pilot_t4\integrated\source_t2\ttm_gpt2_bpe2048.py'
$runner = Join-Path $checkoutRoot 'tools\research\vector-memory\real_t1_bpe_compat_audit.py'
$train = Join-Path $checkoutRoot 'artifacts\research\vector-memory\TTM_EXTERNAL_FACTS_TRAIN_256_V1.json'
$dev = Join-Path $checkoutRoot 'artifacts\research\vector-memory\TTM_EXTERNAL_FACTS_DEV_64_V1.json'
$outDir = Join-Path $root '_evidence\vector-memory'
$out = Join-Path $outDir 'TTM_VM_REAL_T1_BPE_COMPAT_QA_20261111.json'
$expected = 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'

if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'TTM_ROOT_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'PYTHON_312_NOT_FOUND' }
& $py -c 'import sys; assert sys.version_info[:2] == (3,12), sys.version'
if ($LASTEXITCODE -ne 0) { throw 'WRONG_PYTHON_VERSION' }
if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
  Write-Output 'HOLD_REAL_T1_MANIFEST_MISSING'
  exit 2
}
$found = (Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash.ToLowerInvariant()
if ($found -ne $expected) { throw 'T1_MANIFEST_SHA256_MISMATCH' }
foreach ($inputPath in @($source, $runner, $train, $dev)) {
  if (-not (Test-Path -LiteralPath $inputPath -PathType Leaf)) {
    throw ("REQUIRED_INPUT_MISSING: " + $inputPath)
  }
}
if (Test-Path -LiteralPath $out) { throw 'EXISTING_QA_RECEIPT_REFUSE_OVERWRITE' }
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

& $py $runner --tokenizer-manifest $manifest --t1-bpe-source $source --train-fixture $train --dev-fixture $dev --out $out
$rc = $LASTEXITCODE
if ($rc -ne 0) { throw ("T1_BPE_QA_FAIL_OR_HOLD_EXIT_" + $rc) }

$report = Get-Content -LiteralPath $out -Raw | ConvertFrom-Json
if ($report.status -ne 'PASS_REAL_T1_TOKENIZER') { throw 'T1_BPE_QA_NOT_PASS' }
if ($report.test_status -ne 'NOT_READ_OR_DECRYPTED') { throw 'TEST_GUARD_UNEXPECTED' }
Write-Output ('STATUS=' + $report.status)
Write-Output ('CASES=' + $report.input_cases)
Write-Output ('MAX_QUESTION_TOKENS=' + $report.max_question_tokens)
Write-Output ('MAX_ANSWER_TOKENS=' + $report.max_answer_tokens)
Write-Output ('MAX_JOINT_TOKENS=' + $report.max_combined_tokens)
Write-Output ('ANSWER_PREFIX_MISMATCHES=' + $report.answer_boundary_prefix_mismatches)
Write-Output ('RECEIPT_SHA256=' + (Get-FileHash -LiteralPath $out -Algorithm SHA256).Hash)
Write-Output 'TEST_NOT_OPENED=PASS'
