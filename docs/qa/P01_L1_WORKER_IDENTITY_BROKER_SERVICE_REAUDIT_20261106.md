# TTM P01 L1 — Restricted worker and trusted broker: implementation and independent source re-audit

Date 2026-11-06. Engineering conclusion: **SOURCE-CONTRACT PASS; NATIVE SECURITY NOT QUALIFIED**.

## Immutable project constraints
- Original local HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0` is preserved.
- All new content is on `audit/p01-l1-native-security-critical-fix-20261106` in `minhtri22/TokenToModel-Lab`.
- No changes to P00, `main`, original worktree, the ten previous F0 results, or P02.
- No F0 rerun, model training, real-corpus admission, Windows worker launch, production service installation or grouped L1 QA.

## Implemented in successor source branch
1. `qa/p01/worker_identity_acl_win32_v1.py` creates a restricted primary token with the Windows Restricted Code SID (`S-1-5-12`) and `WRITE_RESTRICTED`; verifies the restricting-SID list is present (`IsTokenRestricted`); provides a **non-mutating** impersonated `CreateFileW(OPEN_EXISTING)` write-access test for an explicitly chosen existing directory. A denied access check is necessary, not a proof of global filesystem confinement. No token/ACL validation was actually run on Windows.
2. `qa/p01/trusted_broker_service_v1.py` provides a broker **service entrypoint candidate**, requiring a pinned broker user SID different from the worker SID, an authenticated `AF_PIPE` `multiprocessing.connection.Listener` (HMAC `authkey`), a bounded JSON/base64 request, verified bytes SHA-256, and exactly one write request per service run. The worker is never launched by this module. Deployment under a separate OS account/SCM and pipe SDDL remain **unproven**; separate process identity cannot be inferred from source code alone.
3. `qa/p01/atomic_handle_writer_win32_v1.py` opens and pins a root directory handle inside the original P01 worktree, rejects reparse ancestors, uses `NtCreateFile` relative to root with `OBJ_DONT_REPARSE`, creates a random staging name, writes, flushes, verifies SHA-256 readback, and attempts an atomic no-replace rename with failure cleanup. It has a deliberately smaller per-request cap of **16 MiB**; the cross-process durable ledger retains the **2 GiB aggregate** limit. The native Win32 implementation and crash behavior are unqualified until W11/W12.
4. Earlier `qa/p01/durable_broker_quota_v1.py` is reused unmodified; reservation, commit and fail-held state survive restarts, with SQLite `BEGIN IMMEDIATE`. Per-request replay is explicitly rejected by the broker handler before any write.
5. `qa/p01/test_trusted_broker_protocol_v1.py` tests protocol negatives with fake writer + **exact source** durable ledger; it never creates a Windows worker.

## Exact source qualification
The source files and tests were run offline under Linux Python and then compared using Git blob hashes against their GitHub readbacks. All 5 tested source blobs matched; the source-only tests passed **15/15** with no Windows-native operations. See `artifacts/qa/p01/L1_NATIVE_WORKER_BROKER_EXACT_SOURCE_OFFLINE_QA_20261106.json`. The separate source-level audit `qa/p01/audit_worker_broker_v1_independent.py` checked nine contract properties: all PASS at **STATIC_ONLY** scope. No separate human reviewer has adjudicated security.

## Why native security remains blocked
- Restricted token is not verified by a running target Windows process; effective file permissions and token access across target directories are not demonstrated.
- Broker is implemented as a **candidate process entrypoint**, not installed or launched with a distinct Windows service identity; SCM and dedicated service SID provisioning remain open.
- Named pipe must be restricted by an explicit security descriptor and verified client identity. HMAC alone does not establish an operating-system filesystem boundary or pipe ACL.
- Parent/root directory DACL must prohibit worker rename/reparse; existing lexical checks alone are insufficient against concurrent namespace mutations.
- The writer has not passed genuine Win32 handle tests, partial-write crash tests, W11, or W12; every uncertain failure must retain quota and a negative receipt.
- W01–W12 require separate independent Windows-native evidence with exact executables and source pins. The connected remote command route reported `managed mode requires task_job_submit`; no TTM-qualified project/task permit was established, so **no substitute Windows execution occurred**.

## Decision
`WORKER_IDENTITY_SOURCE=IMPLEMENTED_CANDIDATE`
`BROKER_SERVICE_SOURCE=IMPLEMENTED_CANDIDATE`
`ATOMIC_HANDLE_WRITER_SOURCE=IMPLEMENTED_CANDIDATE`
`OFFLINE_PROTOCOL_QA=15_OF_15_PASS_EXACT_SOURCE`
`INDEPENDENT_STATIC_CONTRACT_AUDIT=PASS_STATIC_ONLY`
`WINDOWS_ACL_DENIED_OPEN=NOT_EXECUTED`
`DISTINCT_WINDOWS_SERVICE_IDENTITY=NOT_ATTESTED`
`PIPE_SDDL_AND_SECRET_ACL=NOT_QUALIFIED`
`NATIVE_W01_W12=NOT_EXECUTED`
`NATIVE_SECURITY_GATE=FAIL_NOT_QUALIFIED`
`L1_GROUPED_QA_PERMIT=NOT_GRANTED`
`P01_CLOSURE=PENDING`
`P02=NOT_OPENED`

This is a technical implementation checkpoint, **not** a scientific result. Do not append it to scientific `lineage.md`.
