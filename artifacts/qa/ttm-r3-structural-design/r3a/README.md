# R3A — GitHub source of truth: anti-known-shortcut amendment

**Date:** 2026-11-11 · **Status:** `R3A_TOY_QA=PASS_SCOPED`, `R3_SCIENTIFIC_DISCRIMINATION=HOLD_FOR_ORIGINAL`, `O0=HOLD_DESIGN_ONLY`, `O1=DEFER`.

**What changed?** R3 original fails to discriminate latest direct lexical update from graph reasoning: the exact reviewer Python scored **384/384**. R3A adds answer-critical alias definitions, delegated/cancelled goals and alias-bound questions. The identical latest-write `predict` logic now scores **208/384**.

## Files committed directly to GitHub (not a downloadable ZIP)

| File | SHA-256 / status |
|---|---|
| [Generator](../../../../tools/research/semantic_state_r3/r3a_generator.py) | `b2bca78463063b2aedf7ef657f1a28b3c0f6f1bc3f16f59ffe6f6ac04a7c5cbe` |
| [Checker (no generator import)](../../../../tools/research/semantic_state_r3/r3a_independent_checker.py) | `1d1c3ba2f11ac83cb3d6d5f6b090f6b8476294f2de25d2ed3c17fd5d52b8907d` |
| [CPU QA 44 tests](../../../../tools/research/semantic_state_r3/r3a_integrated_cpu_qa.py) | `812ce00b5992aeaa84a9ec3d1d1d372adcc7f893a17e016da72d47b25ff44127` |
| [Complete public oracle JSON](R3A_PUBLIC_ORACLE.json) | `b509fae3f63399c978d532c2686d147bd4ba41e44b2aa9135dcd38360e6ffb08` |
| [Complete shuffled 384-row model-input JSON](R3A_MODEL_INPUT_ONLY.json) | `2510866d82641bd27207082566d6b4dbb867e59516794e422dff8fb041646402` |
| [Independent checker QA report](R3A_CHECKER_REPORT.json) | 384/384 |
| [Latest-write baseline replay on R3A](R3A_LATEST_WRITE_BASELINE.json) | 208/384 |
| [Original exact reviewer Python replay on R3](R3_ORIGINAL_CODEX_BASELINE_EXACT_PYTHON_FULL_REPLAY.json) | 384/384 |
| [CPU raw log](R3A_CPU_QA.log) | 44/44 PASS incl. 30 negative tests |
| [Complete SHA/git-blob manifest and scoped decision](R3A_SOURCE_OF_TRUTH_SHA256_AND_OWNER_SCOPED_DECISION_20261111.json) | source of truth |

[Owner-scoped adjudication & experiment limitations](../../../../docs/research/TTM_R3_ADVERSARIAL_REVIEW_OWNER_ADJUDICATION_AND_R3A_MINIMAL_ANTISHORTCUT_CPU_QA_20261111.md) · [Codex adversarial review handoff](../../../../docs/research/TTM_R3A_CODEX_ADVERSARIAL_SHORTCUT_AND_O0_PILOT_REVIEW_HANDOFF_20261111.md).

## Deterministic CPU replay

From repository root, replay entirely inside the TTM workspace (PowerShell 5.1, Python 3.12):

```powershell
$ErrorActionPreference = 'Stop'
$P = 'D:\\WORK\\RESEARCH\\TokenToModel-Lab'
Set-Location $P
$py = 'C:\\Users\\minht\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'
$dir = Join-Path $P '_tmp\\r3a_replay_readonly_20261111'
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$source = 'tools\\research\\semantic_state_r3'
$data = 'artifacts\\qa\\ttm-r3-structural-design\\r3a'
foreach ($name in @('r3a_generator.py','r3a_independent_checker.py','r3a_integrated_cpu_qa.py')) {
  Copy-Item (Join-Path $source $name) $dir -Force
}
Copy-Item (Join-Path $data 'R3A_PUBLIC_ORACLE.json') (Join-Path $dir 'R3A_ORACLE.json') -Force
Copy-Item (Join-Path $data 'R3A_MODEL_INPUT_ONLY.json') $dir -Force
& $py (Join-Path $dir 'r3a_independent_checker.py') --oracle (Join-Path $dir 'R3A_ORACLE.json') --model (Join-Path $dir 'R3A_MODEL_INPUT_ONLY.json') --out (Join-Path $dir 'R3A_REPLAY.json')
& $py (Join-Path $dir 'r3a_integrated_cpu_qa.py')
Get-FileHash (Join-Path $dir 'R3A_ORACLE.json') -Algorithm SHA256
Get-FileHash (Join-Path $dir 'R3A_MODEL_INPUT_ONLY.json') -Algorithm SHA256
```

This creates only temporary replay files under the project's own `_tmp` directory, **not** TRAIN/TEST artifacts and not a new science run. Compare hashes against the manifest. No training/GPU/model inference occurs.

The dataset is **public** and its answers are on GitHub. Never treat it as a science blind FINAL or as proof that a state module is necessary. Reviewer has not yet tested new heuristics against R3A.
