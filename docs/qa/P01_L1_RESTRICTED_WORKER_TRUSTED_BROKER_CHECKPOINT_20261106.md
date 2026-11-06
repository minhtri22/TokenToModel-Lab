# TTM P01 L1 — Restricted worker and trusted broker implementation checkpoint

Date: 2026-11-06. **Engineering status: PARTIAL / SECURITY GATE FAIL.**

## Pinned baseline and immutable constraints

- Repository: `minhtri22/TokenToModel-Lab`.
- Original local P01 HEAD: `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- All changes herein are committed only to `audit/p01-l1-native-security-critical-fix-20261106`. The original local worktree and P00 must remain unchanged.
- The previous six static-security findings remain retained in `docs/qa/P01_L1_NATIVE_SECURITY_STATIC_FAIL_20261106.md`.

## Implemented in this successor branch

1. `qa/p01/durable_broker_quota_v1.py`: SQLite-backed cross-process quota *ledger*. Each reservation uses `BEGIN IMMEDIATE`, an exact 2 GiB aggregate limit, unique case-insensitive names, idempotent operation identity, fail-closed replay checks, explicit `PENDING`, `COMMITTED`, and `FAILED_HELD` states, and synchronous durable commit. Reservations are **never automatically refunded** on unknown failures or restart.
2. `qa/p01/test_durable_broker_quota_v1.py`: independent unit cases for persistence, replay, name collisions, invalid filename and quota rules.
3. Earlier `qa/p01/native_guard_lifecycle_v2.py` remains **mock-only**; it is not a real Windows supervisor and cannot authorize native execution.

## Evidence classification

A related prototype was run in an isolated Linux Python environment: **10/10 quota ledger tests PASS**, including concurrent processes, after correcting a database connection resource warning. This prototype is semantically equivalent, but its source formatting differs from the GitHub publication; therefore this result is **NOT** an exact-commit test of the two GitHub files. The GitHub regression script has **NOT_EXECUTED** status on target Windows. Preserve this distinction in QA and do not claim qualification.

## Unresolved critical security gates

| Gate | Required evidence | Current |
| --- | --- | --- |
| A1 dedicated worker identity | Native Windows SID, restricted primary token, effective DACL negative opens, token and process receipts | **NOT_IMPLEMENTED / BLOCK** |
| A2 native supervisor | CREATE_SUSPENDED → Job limits query-back → membership → verified resume/termination under one owner | **NOT_QUALIFIED / BLOCK** |
| A3 broker process isolation | Distinct trusted service SID and privileged handle-only broker with authenticated IPC | **NOT_IMPLEMENTED / BLOCK** |
| A4 directory/ACL integrity | Immutable approved evidence directory inside existing P01 worktree, no junction/reparse escape, actual denied-open proof | **NOT_QUALIFIED / BLOCK** |
| A5 atomic evidence publication | No visible partial evidence, durable file hash/size readback before promotion, crash recovery | **NOT_IMPLEMENTED / BLOCK** |
| A6 shared quota | Durable cross-process ledger source and negative tests | **PARTIAL / NOT_WINDOWS_QUALIFIED** |
| A7 W01–W12 | One approved Windows-native negative QA run with exact file hashes and process evidence | **NOT_EXECUTED** |

## Implementation constraints for successor

- Broker must run under a different trusted identity, preferably a managed local Windows service with a service SID; worker SID must not have direct write permission to evidence root or ledger database.
- Do not use `CreateRestrictedToken(DISABLE_MAX_PRIVILEGE)` as proof of sandbox isolation. Verify actual token SIDs and DACL effective rights and attempt a prohibited write *from worker's token* under a separately approved negative test.
- Broker IPC authentication must be bound to the worker SID/job and exact operation id. Application-level secrets alone are not sufficient for OS confinement.
- Evidence root must reside inside the P01 project workspace and remain handle-pinned. Root path must reject junction, symlink, reparse traversal and post-check substitution; protect directory ACL from worker renaming.
- A ledger reservation is **not itself a file-writing authorization**. The trusted broker must independently validate request, quota, exact filename and write bytes, publish atomically, then verify readback before finalizing state. Keep `FAILED_HELD` if any step is uncertain.
- Never run L1 tests via an unconstrained `subprocess` or `python -m unittest discover`.

## Independent adjudication

`NATIVE_SECURITY_CRITICAL_FIX=PARTIAL`
`SHARED_QUOTA_LEDGER_SOURCE=IMPLEMENTED_CANDIDATE`
`TARGET_WINDOWS_SECURITY_BOUNDARY=NOT_QUALIFIED`
`W01_W12_NATIVE=NOT_EXECUTED`
`GROUPED_L1_QA_PERMIT=NOT_GRANTED`
`P01_CLOSURE=PENDING`
`P02=NOT_OPENED`

Do not append these engineering details to scientific `lineage.md`. Keep the previous engineering QA FAIL append-only in the dedicated audit files.
