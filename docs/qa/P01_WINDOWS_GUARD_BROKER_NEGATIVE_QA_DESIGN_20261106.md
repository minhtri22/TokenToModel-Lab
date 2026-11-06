# P01 C09 — Windows Job Object + Write Broker independent negative QA design

**Operation:** `TTM_P01_QA0_WINDOWS_SECURITY_GUARD_IMPLEMENTATION_AND_INDEPENDENT_NEGATIVE_QA_DESIGN`  
**Branch:** `implementation/p01-i0a-s-f0-static-20261106`, **source base:** `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.  
**Date:** 2026-11-06. **Status:** `SOURCE_IMPLEMENTED_PARTIAL_RUNTIME_HOLD`.

## Goal and non-goals

The F0 functional suite already passed offhost 10/10; do not rerun or modify that result. This line addresses **Windows runtime protection**, not data semantics or GPT training. P00, Git main, `lineage.md`, the existing Windows worktrees, real corpus and scientific TEST must remain untouched.

The exact C09 design requires job-wide **committed** memory `4294967296` bytes (4 GiB), a monotonic 1800-second wall clock budget, `KILL_ON_JOB_CLOSE`, no breakaway, assignment while suspended, 2 GiB aggregated write limit, create-new output, and rejection of escapes. Job Object does NOT restrict filesystem writes. The old `max_peak_rss_bytes` name in H05 is not equivalent and must not be silently substituted.

## Code included in this source successor

- `runtime/p01/windows_job_guard.py`: complete Win32 Job Object creation/limit set and query-back via `ctypes` (lazy Windows-only), a suspended-process attachment/membership verification helper, handle ownership and termination. `start_worker` **still raises `GuardNotEstablished`**: no `CreateProcessW`/restricted-token spawn, resume thread, independent child containment, real watchdog or worker OS isolation has been implemented. The exposed `suspended=True` argument is a caller assertion, **not an attested OS state**, so it alone must never authorize resume.
- `runtime/p01/write_quota_broker.py`: strict policy validation, Windows-path lexical denials and a deterministic **dry-run reservation ledger** checking 2 GiB quota *before write*, create-new/case-fold collision, malformed types. `write_file` **still raises `BrokerUnavailable`**. There is deliberately no open/CreateFile call: a real privileged broker must use trusted directory handles, reparse resistance, create-new atomicity, ACL/token restriction, safe accounting under concurrency and readback. Merely checking a path by `resolve()` followed by `open()` has an unsolved time-of-check/time-of-use race.
- `qa/p01/independent_windows_guard_policy_negative.py`: nine `unittest` negative policy cases (pure mocks/no OS actions). They are **not** substitutes for Windows negative W01–W12. No automatic import or `__main__` test entrypoint.

## Independent W01–W12 plan (REAL WINDOWS — not executed)

| ID | Setup | Required independent evidence / PASS |
|---|---|---|
| W01 | Worker requests >4 GiB job-committed memory | OS refuses excess commit; verify actual job limit and failure code (don't infer process killed) |
| W02 | Two workers combine beyond 4 GiB | Aggregated job limit blocks; independent job readback |
| W03 | Worker creates child through CreateProcess | Child in job, peak/limit account; WMI process launch prohibited |
| W04 | Worker attempts breakaway | API flags include neither BREAKAWAY_OK nor SILENT_BREAKAWAY_OK; escape attempt blocked |
| W05 | Simulated failure of AssignProcessToJobObject | Suspended worker terminated, **never** ResumeThread |
| W06 | Incompatible pre-existing parent job | Fail closed; no unbounded fallback |
| W07 | Worker sleeps past monotonic timeout | Supervisor calls TerminateJobObject, zero active children after wait |
| W08 | Last job handle closes unexpectedly | Children terminate; guard handle inheritance and all descendants |
| W09 | Concurrent writes beyond 2 GiB, and bypass attempt | Atomic broker pre-write reservation rejects, worker OS permissions deny direct write |
| W10 | UNC, absolute/drive-relative, ADS, reserved names, symlink/junction, reparse swap | No file outside exact P01 workspace created, concurrent path race tested |
| W11 | Insufficient disk/RAM or no source rights | Worker not created, no P00 access |
| W12 | Missing, truncated, corrupted receipt | Independent checker rejects rather than labels PASS |

**Independent reviewer:** must not import production tokenizer/checker as its oracle. Capture exact Win32 API return values, LastError, flags and JobMemoryLimit from `QueryInformationJobObject`, PID/job association, monotonic time, `ActiveProcesses`, signed source SHA and output paths. Do not use big 4-GiB allocation on the production notebook without a separate resource permit. For early W01/W02 negative QA, scale a **diagnostic-only** job limit in an isolated disposable environment and never confuse it with 4 GiB certification; a real confirmatory test requires its own approval.

## Findings / blockers before official Windows QA0

1. `WINDOWS_NATIVE_JOB_API=CODE_ONLY_UNTESTED`: Win32 ctypes structs and calls have not been exercised on Windows; no proof of nested jobs or handle lifetime.
2. `WORKER_RESTRICTED_TOKEN=UNIMPLEMENTED`: Job Object permits writes under inherited ACL if token is not constrained.
3. `BROKER_OS_HANDLE_RELATIVE_CREATE_NEW=UNIMPLEMENTED`: all direct write paths remain deliberately denied.
4. `WALL_CLOCK_WATCHDOG_AND_PROCESS_TREE=UNIMPLEMENTED`.
5. `INDEPENDENT_W01_W12_RUNTIME=NOT_EXECUTED`. Pure Python policy negatives alone cannot certify W01–W12.

## Decision

`GUARD_POLICY_SOURCE=IMPLEMENTED_FOR_REVIEW`  
`JOB_OBJECT_SET_QUERY_ATTACH_SOURCE=IMPLEMENTED_UNTESTED`  
`BROKER_LEXICAL_QUOTA_PRECHECK=IMPLEMENTED_DRY_RUN_ONLY`  
`WORKER_EXECUTION_AND_DISK_WRITES=DENY_BY_DEFAULT`  
`NEGATIVE_POLICY_TEST_SOURCE=PREPARED_NOT_RUN_ON_WINDOWS`  
`WINDOWS_QA0_SECURITY_ADMISSION=HOLD`  
`F0_OFFHOST_FUNCTIONAL_RESULT=PASS_10_OF_10_UNCHANGED`  
`P00_MAIN_LINEAGE=UNCHANGED`.

**Next gate:** `TTM_P01_QA0_WINDOWS_JOB_GUARD_AND_BROKER_NATIVE_COMPLETION_SEPARATE_NEGATIVE_QA_PREFLIGHT`. Complete actual restricted-token launcher, broker-only filesystem rights and atomic open, monotonic watchdog; independently review source and test without touching P00. No claim of Windows runtime PASS until native tests are observed.
