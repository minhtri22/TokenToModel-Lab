# CODEX HANDOFF — TTM-SM4M-DIAG-Q001 last mile, ONE integrated admission + real failure diagnosis

**Date:** 2026-11-16 · **Operation:** `TTM_SM4M_DIAG_Q001_CODEX_LAST_MILE_NATIVE_JOB_OBJECT_OWNER_SCOPE_RUNTIME_AND_ONE_I1_ADJUDICATION`  
**Repo:** https://github.com/minhtri22/TokenToModel-Lab  
**Draft PR:** https://github.com/minhtri22/TokenToModel-Lab/pull/28  
**Review issue:** https://github.com/minhtri22/TokenToModel-Lab/issues/29  
**Exact last-mile source HEAD before manifest:** `9e3ced7bb9e2b5820bab762e51611d84fda0a194`; manifest commit `91b6e14793d7149dae86b24c293174040314259a`. Codex: read actual HEAD/compare before editing, record exact SHA.  
**Machine:** `DESKTOP-4PSD0G2`, Windows 11, PowerShell 5.1, Python 3.12 at `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe`. Project `D:\WORK\RESEARCH\TokenToModel-Lab`.  
**Q1 baseline main:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`. **Already granted owner GO:** `GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL`. **NO repeat GO** and **NO micro-permits**.  
**Current:** `HOLD_I1`, I2 not executed. Owner explicitly confirms internal noncommercial research.

## What has been actually accomplished — do not repeat

Codex previous exact source `77f6e946975a8b5cd5859297f6d0f161bb13f629`: Windows PS5 parser 6/6; source oracle 18/18; author negatives 44/44; Codex adversarial 22/22; launcher-prefix 9/9; watchdog native 5/5 standalone and 5/5 OnePack. GitHub evidence at [receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/957617b5fabd60115ae02f3cc0e3b993090fefd8/artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_RECEIPT_20261116.json). Preserve these, do **not** spend a second iteration re-running unchanged tests just to count more PASS.

**This last-mile update now exists on PR #28**, source-only author static 15/15, not native:
- `windows_rss_native.py`: Win32 standard-library `GetProcessMemoryInfo` replaces unavailable `psutil` in `ttm_sm4m_diag_q001.py`. Exact Git-blob import pin, updated runner SHA-256 in `Run-Approved-OneShot-PS51.ps1`.
- `windows_job_memory_limit.py`: Win32 Job Object proof of concept uses `CREATE_SUSPENDED → AssignProcessToJobObject → ResumeThread`, `JOB_OBJECT_LIMIT_JOB_MEMORY`, `KILL_ON_JOB_CLOSE`. **Candidate only; not integrated. Hard committed memory ≠ hard RSS.**
- `owner_internal_admission.py`: owner-only scoped admission policy tied to exact checked-in owner amendment source Git blob and Issue #29 comment. `ttm_sm4m_diag_q001.py` now branches between scoped **owner_internal** mode and unmodified legacy 3-signer mode. No fake keys or signatures.
- `test_owner_internal_admission_source.py`: 14 negative/mock source QA cases, NOT YET EXECUTED on Windows.
- Owner declaration: [issue #29](https://github.com/minhtri22/TokenToModel-Lab/issues/29#issuecomment-6916584568), [scope amendment](TTM_SM4M_DIAG_Q001_OWNER_INTERNAL_SCOPE_AND_LAST_MILE_AMENDMENT_20261116.md).
- Source file Git blobs, code owner/runner/RSS pins, 15/15 static checks and an honest checker erratum: [last-mile manifest](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_LAST_MILE_OWNER_INTERNAL_SOURCE_MANIFEST_20261116.json). No private checkpoint/tokenizer access yet.

## ONE Codex implementation/QA packet — not separate approvals

**A. Exact-source native preflight and tests**: Under one Codex-owned *scoped worktree within project root*, fetch exact PR HEAD, verify Git blobs against manifest and absence of unrelated changes; use Python312 explicit executable. No CMD from RemoteMCP Canonical (managed durable allowlist blocked it). Run **only no-model native checks**:
```powershell
$ErrorActionPreference = 'Stop'
$Repo = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
# Change $WT to YOUR exact Codex-owned scoped worktree, beneath $Repo.
$WT = 'D:\WORK\RESEARCH\TokenToModel-Lab\.worktrees\sm4m-q001-lastmile'
$Dir = Join-Path $WT 'tools\pilot_t4\direct_failure_diag_q001\preexec_candidate_20261116'
git -C $WT rev-parse HEAD
& $Py -c 'import sys; assert sys.version_info[:2]==(3,12)'
& $Py (Join-Path $Dir 'windows_rss_native.py')
& $Py -c "import sys; sys.path.insert(0,r'$Dir'); from windows_rss_native import current_process_rss_bytes; print('NATIVE_RSS_BYTES',current_process_rss_bytes())"
& $Py -m unittest -v (Join-Path $Dir 'test_owner_internal_admission_source.py')
& $Py (Join-Path $Dir 'windows_job_memory_limit.py') --struct-shape
& $Py (Join-Path $Dir 'windows_job_memory_limit.py') --native-smoke
```
Use proper `unittest` invocation if positional PowerShell handling requires it; do not claim the commands succeeded without native receipt. The owner-policy negative QA tests use mocked/dummy hashes only; **NO real tokenizer or checkpoint access** during these tests.

**B. Enforce actual Job Object protection before ANY I2**: Independently validate Python ctypes struct layouts, kernel32 function signatures, nested job behavior, std handle inheritance, suspended child assignment before resume, early/late errors, job-wide committed memory cap, descendants, exit status and kill-on-close; add scaled real Windows **negative memory pressure** fixture and receipt. Integrate a verified, SHA-pinned wrapper into guarded I2 launcher, with a hard 12 GiB **job-wide committed-memory** ceiling **in addition** to the existing sampled 12 GiB tree-RSS guard. Report both without conflation; the hard committed cap is an extra conservative mechanism, not a changed preregistered RSS endpoint. On OS cap/resource/timeout failure → `HOLD_RESOURCE_INCOMPLETE`, not a model scientific FAIL. If this cannot be verified, `HOLD_I1_RESOURCE_GUARD`.

**C. Owner scope vs artificial three-signer bureaucracy**: This is a **solo local owner-authorized noncommercial research** diagnostic. Three external Ed25519 people are not required for the scoped owner-internal mode; historical triple signer path remains unchanged and fail closed. Review and negative-test `owner_internal_admission.py` and runner mode routing so local fake permit, wrong root/host, Q1/seed/steps, expired packet, spoofed owner ref, altered module/owner document, wrong token inventory and fixture digest are denied. Do not invent signatures or label third-party legal provenance verified. Upstream TinyStories declares `cdla-sharing-1.0` (https://huggingface.co/datasets/roneneldan/TinyStories); local owner commits to internal no-redistribution. Actual checkpoint and tokenizer **byte SHA/rights source custody** still must be checked once owner-scoped admission is valid.

**D. Exact checkpoint/tokenizer/fixture custody, once gate C holds**: Find the **original, not surrogate** private T4 checkpoint; verify SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, 45,074,891 bytes, step1024, P02 blob `9762343e06cf800b50574c2871ae1ed58537fb18`. Verify actual tokenizer source inventory bytes and special token exclusions, freeze all original 80 deterministic token-ID cases with case/group SHA and no leakage. Use no old TEST/FINAL24. Do not publish the private checkpoint/tokenizer bytes or private paths unnecessarily. If bytes do not match, HOLD; no checkpoint swap, reseed or retry.

**E. One exact I1 review decision, then (if genuine PASS) one I2**: A distinct reviewer who did not implement the last-mile changes should inspect exact code and new real Windows QA/evidence. This is a **technical audit**, not a demand for 3 organizational signers. One adjudication `I1_PASS_SCOPED_INTERNAL_RESEARCH` or `HOLD_I1`. If PASS, use owner's existing conditional GO for **exactly one** CPU FP32 batch 256 steps, seed 20261116, 24 TRAIN/56 probe, 900s wall, 12GiB sampled RSS plus hard job commit cap, 1GiB output; no repeat or adaptive TEST. Write measured loss, 24/24 train fit, heldout recombination/counterfactual/novel-ID/absent, candidate-vs-full logits, STOP reason and SHA evidence to GitHub, then formal scoped result. If HOLD, provide the **first real blocker**, not a new Question Gate.

## Final evidence — GitHub is source of truth

Commit scoped source, native PS5/Win32 test stdout/stderr and receipts, exact environment binary/version, Job Object negative QA, owner-internal admission negative QA, checkpoint/tokenizer only SHA summaries, 80-case fixture hashes, independent exact-head verdict and single I1 PASS/HOLD. Reconcile Issue #29 and PR #28 (remain Draft, no merge while HOLD); do not rewrite Codex prior QA, `lineage.md`, Q1 or P02. No new micro-permit. If native QA cannot run, state `NOT_EXECUTED`.

**Success is one actual Small-4M failure-localization run; not another source-only PASS table.**
