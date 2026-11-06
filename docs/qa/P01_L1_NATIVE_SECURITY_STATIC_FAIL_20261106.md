# TTM P01 L1 — Independent native security audit and remediation gate

Date: 2026-11-06. Status: **FAIL (STATIC SECURITY)**. This is **not** a BPE scientific FAIL.

## Exact provenance
- Repository: `minhtri22/TokenToModel-Lab`
- Immutable original HEAD: `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- Local original worktree: `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105`.
- Evidence branch created directly from the immutable original HEAD. Local HEAD must not move.
- Candidate (staged untracked, not committed original branch): `qa/p01/native_win32_process_backend.py`, SHA-256 `4488e491acbe3694fa106b587544bbe4e1841e9d5502db6903d1dd69e8cc08d7`.
- Candidate (staged untracked): `qa/p01/native_win32_handle_broker.py`, SHA-256 `7a5946405bee5e74be49c17ad7189ac5ccbc699a3e1613c06e26927084ffe431`.

## Independent reproducibility: static-only, not Windows-native
The audit was re-run in an isolated Linux Python session against those candidate files. An AST-based checker detected all six missing control classes; result: `all_six_confirmed=true`, `STATIC_SOURCE_ONLY`. The seven fake-backend lifecycle negative tests passed: **7/7**. This validates fail-closed *mock* handling only. W01–W12 native Windows checks were **NOT_EXECUTED**; their PASS cannot be inferred.

## Static FAIL findings
| Severity | Finding | Gate |
| --- | --- | --- |
| CRITICAL | No single orchestrator guarantees restricted suspended creation → assign Job → verify job/membership → Resume, with verified kill on every failure path | BLOCK |
| CRITICAL | CreateRestrictedToken with DISABLE_MAX_PRIVILEGE is not sufficient evidence that worker DACL access denies unbrokered writes | BLOCK |
| CRITICAL | Broker is a Python class, not an independently isolated trusted process; worker could bypass it | BLOCK |
| HIGH | Root path/reparse checks and handle identity not proven against time-of-check/time-of-use rename/reparse attacks | BLOCK |
| HIGH | A failed or partial WriteFile leaves an incomplete output without atomic commit/quarantine | BLOCK |
| HIGH | 2 GiB quota is only process-local and not durable or synchronized between broker processes/restarts | BLOCK |

Additional: handle tracking removes a handle before CloseHandle success; partial process creation may leak handles; neither signed worker-policy attestation nor exact executable hash receipt is emitted. No verified OS process containment evidence exists.

## Mandatory repair and re-audit
1. Implement a *single* fail-closed native supervisor that owns handles, enforces exact executable + argv identity, verifies restricted primary token, assignment and job-wide 4 GiB committed-memory queryback, prohibits breakaway, resumes only after checks, enforces 1,800 s wall time and verifies tree exit.
2. Use a dedicated low-rights identity and explicit ACL on an approved evidence root strictly within the P01 worktree; independently prove unauthorized worker opens fail without a broker.
3. Put a minimal file-writing broker in a different trusted process; enforce handle-relative, create-new writes with no path traversal, validated immutable directory identity, atomic publication, durable/restart-safe shared 2 GiB accounting, and failure receipts.
4. Re-audit source and independent negative tests, then request a *separate native Windows W01–W12 permit*. Report each native case with source/executable SHA-256, Job Object queryback, observed process tree, before/after file inventories and explicit PASS/FAIL. Preserve FAIL evidence.
5. Only after W01–W12 PASS may the separate single grouped L1 QA permit be evaluated.

## Governance
`NATIVE_SECURITY_STATIC_AUDIT=FAIL`
`WIN32_REAL_EXECUTION=NOT_EXECUTED`
`W01_W12_NATIVE=NOT_EXECUTED`
`L1_GROUPED_QA_PERMIT=NOT_GRANTED`
`L1_SCIENTIFIC_VERDICT=NOT_EVALUATED`

No real corpus, GPT training, F0 rerun, Windows-native job or P02 work. P00 and original local P01 HEAD unchanged. This report is engineering QA evidence and does not make an entry in scientific `lineage.md`.
