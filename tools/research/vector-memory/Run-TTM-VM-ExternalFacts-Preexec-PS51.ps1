# PS5.1 read-only CPU preexecution QA; never launches one-shot trainer.
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$wt = Join-Path $root 'worktrees\ttm-vm-external-20261111'
$ck = Join-Path $root '_tmp\vector-memory\checkpoint.pt'
$manifest = Join-Path $root '_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json'
$receipt = Join-Path $root '_evidence\vector-memory\TTM_VM_REAL_T1_BPE_COMPAT_QA_20261111.json'
$out = Join-Path $wt '_evidence\vector-memory\TTM_VM_CPU_PREEXEC_READINESS_20261111.json'
$qa = Join-Path $wt '_evidence\vector-memory\TTM_VM_CPU_INDEPENDENT_PREEXEC_QA_20261111.json'
if (-not (Test-Path -LiteralPath $wt -PathType Container)) { throw 'RESEARCH_WORKTREE_MISSING' }
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'PYTHON312_MISSING' }
& $py -c 'import sys; assert sys.version_info[:2] == (3,12)'
if ($LASTEXITCODE -ne 0) { throw 'PYTHON312_REQUIRED' }
$expected = @{
  $ck='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'
  $manifest='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
  $receipt='bc688ca5bcc4084a19d3e95b0f7d555c283d8b1b1319ff255c5baf9e66c7b34b'
}
foreach ($file in @($ck,$manifest,$receipt)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw ('PINNED_INPUT_MISSING: ' + $file) }
    $h = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($h -ne $expected[$file]) { throw ('SHA256_MISMATCH: ' + $file) }
}
if ((Test-Path -LiteralPath $out) -or (Test-Path -LiteralPath $qa)) { throw 'REFUSE_OVERWRITE_EXISTING_QA' }
New-Item -ItemType Directory -Force (Split-Path $out) | Out-Null
$tools = Join-Path $wt 'tools\research\vector-memory'
& $py (Join-Path $tools 'cpu_pilot_readiness.py') `
  --root $wt --checkpoint $ck `
  --p02-source (Join-Path $wt 'tools\pilot_t4\integrated\p02_source_exact.py') `
  --reader-source (Join-Path $tools 'oracle_reader_source_only.py') --out $out
if ($LASTEXITCODE -ne 0) { throw 'CPU_PREEXEC_FAILED' }
& $py (Join-Path $tools 'cpu_pilot_independent_readiness_audit.py') --root $wt --report $out --out $qa
if ($LASTEXITCODE -ne 0) { throw 'CPU_INDEPENDENT_PREEXEC_FAILED' }
Write-Output 'TTM_VM_CPU_PREEXEC=PASS_SCOPED'
Write-Output ('RECEIPT_SHA256=' + (Get-FileHash -LiteralPath $receipt -Algorithm SHA256).Hash)
Write-Output 'TEST_NOT_OPENED=TRUE'
Write-Output 'SCIENCE_NOT_EXECUTED=TRUE'
