# TTM × SIX G1 — Trusted boundary and witness integration candidate

Version: integration-simulation-v1, 2026-11-09. Do not use for science or Qwen.

**Pinned base:** `minhtri22/TokenToModel-Lab` at reviewed v1c `d5d0c5346a595557a76349f900d09be50bce289c`. Prior Codex HOLD review at `d478282e16a4728f064892564b949e671e13cdd2`. Existing implementation candidate at `51636a3187ed9e22658b55de2c9a4060127ac30d`.

## What this packet adds

- `g1_trusted_runtime_witness_candidate.py`: synthetic-only ledger-to-witness two-boundary reconciliation; STOP on one-sided rollback and witness outage; TEST acknowledgment before synthetic TEST open, package staging with exclusive link; hardlink and path protections; real science hard-locked.
- `test_g1_trusted_runtime_witness_candidate.py`: adversarial CPU tests and regression fixtures, no private data.
- `g1_win32_job_object_watchdog_candidate.py`: Windows-only harmless child Job Object launcher using suspended start, attach-before-resume, kill-on-job-close. **Windows runtime execution NOT YET TESTED**.
- `Run-G1-TrustedRuntime-WindowsReadOnly-PS51.ps1`: PowerShell 5.1 inventory; reports only, never changes ACL/process, does not read private data.
- `G1_OWNER_SCOPE_AND_METHODS_V1D_REVIEW_CANDIDATE_20261109.md`: integrated owner scope and methods amendment, not approved.
- `G1_TRUSTED_RUNTIME_WITNESS_QA_RECEIPT_20261109.json`: synthetic test evidence, SHA256 source file pins and outstanding gates.

## Local CPU verification

```
python test_g1_trusted_runtime_witness_candidate.py
python g1_trusted_runtime_witness_candidate.py --mode status
python g1_win32_job_object_watchdog_candidate.py --mode status
```

## Windows owner read-only verification (no elevated prompt)

```
$script = 'D:\WORK\RESEARCH\TokenToModel-Lab\scripts\research\six_ttm\Run-G1-TrustedRuntime-WindowsReadOnly-PS51.ps1'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script
```

The script is intentionally not a source-installer. If it has not been copied to the project root, use a project-internal copy; **never download and execute unverified text**. Capture stdout and exact SHA-256 of script as owner evidence. `icacls`/`Get-Acl` and the Windows Job Object test are independent, separate work: inventory alone does NOT prove forbidden access or force-kill.

## Admission and review

Keep `G1_SCIENCE_LOCK=HOLD`, `OWNER_SCIENCE_PERMIT=NOT_ISSUED`, no real TEST, no source transfer, no training, no Qwen. External owner trust anchor and independently controlled witness absent. This is a **candidate**, not a production launcher. Distinct Codex reviewer must test with **separate Windows principal/SID**, file ACL negative tests, a trusted signed witness and Job Object kill before any owner science decision. Owner may approve the *engineering project* without authorizing real science.
