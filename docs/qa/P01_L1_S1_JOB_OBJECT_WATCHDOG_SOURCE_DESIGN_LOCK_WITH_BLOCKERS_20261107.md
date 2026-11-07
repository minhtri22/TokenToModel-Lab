# TTM P01 L1 / S1 — Job Object watchdog source design lock (NO NATIVE PERMIT)

Date: 2026-11-07

## Outcome of the just-reported Windows read-only preflight

The user-supplied PowerShell 5.1 console shows `TTM_S1_WATCHDOG_VERDICT=PASS_READONLY_DESIGN_PREFLIGHT_NO_NATIVE`, exit code 0. Exact source, frozen original, V1–V3 QA markers, Broker V3/Worker V4 binary SHA, Python V3 QA receipt, SCM Stopped/PID0 (checked twice), and design RAM/disk prerequisites all report PASS. This is a **console report**, not a newly uploaded signed read-only preflight receipt.

No Python source QA was repeated. No C# code or S1 binary was compiled or executed, and no SCM action took place.

## Newly implemented source candidate

- File: `qa/p01/windows/S1/TTMS1IsolatedJobWatchdogEngine.cs`
- Exact source commit: `8074e76be889d9a0ecbeb7f49a5aa6b8583bc0e3`
- Git blob: `6154dcf2efc31e796544029373ff4a268b0a98d9`
- SHA-256: `53b520e4399a7546d8ecd165c4360796d330dc467afa82e2f888cbd9f053a823`
- No `Main()` and no native execution wrapper. The source is a standalone internal **engine**, not a runnable S1 permit or release.
- Independent textual static QA: **37/37** positive checks and **21/21** negative source mutations rejected. Result: `PASS_STRUCTURAL_SOURCE_AUDIT_WITH_PRE_PERMIT_BLOCKERS__NO_NATIVE_EXECUTION`.
- Evidence: `artifacts/qa/p01/S1_JOB_OBJECT_WATCHDOG_ENGINE_SOURCE_INDEPENDENT_QA_20261107.json`, commit `446d242ca1ef8c675b785f603d2ab3a95997d853`.

## Design contract now represented in source

- Exactly the project-local `TTMS1IsolatedCancellationHarness.exe`; exact SHA-256 before spawn; exclusive CreateNew stdout/stderr paths.
- Create unnamed Windows Job Object; set `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` and active-process limit 1.
- Set `STARTUPINFOEX` handle inheritance whitelist to stdin=`NUL`, stdout and stderr only.
- `CreateProcessW(CREATE_SUSPENDED)` -> `AssignProcessToJobObject` -> `ResumeThread`; reject any failure.
- 15s process deadline, 3s termination confirmation, own Job Object termination only. Never kill by process name, PID search or touch service `TTMP01Broker`.
- Exactly three stdout PASS lines and exit 0, no stderr; 8 KiB post-run stdout acceptance ceiling.
- No changes to the Broker/Worker compile-only evidence or original S1 harness.

## Safety gaps — do not issue native execution permit yet

1. **Parent crash window (HIGH):** an unexpected launcher death between `CreateProcessW(CREATE_SUSPENDED)` and `AssignProcessToJobObject` may strand a suspended unassigned child. Need a hardened decision either using supported creation-time job binding `PROC_THREAD_ATTRIBUTE_JOB_LIST` on Windows 10/11 or a demonstrably safe equivalently bounded recovery. The current existing source remains an unexecuted candidate. Official API: https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute
2. **Output quota (MEDIUM):** 8 KiB is an acceptance limit and polling check, not a guaranteed OS-level write quota. A fast child may overshoot between polls. Test/mitigate bounded output writes and disk exposure.
3. **Hash-to-create race (MEDIUM):** separate `HashFile()` and `CreateProcessW()` calls leave a possible executable file mutation window. Lock source/binary path ACL or equivalent immutable staging.
4. **P/Invoke ABI (MEDIUM):** Win32 C# layouts and STARTUPINFOEX marshaling have not been compiled or qualified against Windows x64. Static text checks cannot establish ABI compatibility.
5. **One-shot wrapper absent (MEDIUM):** exact source/permit pin, S1 binary compilation, pristine marker, runtime evidence and GitHub readback belong to a future *single* authorized native run. No permit or marker for native exists now.

## Efficient continuation — one grouped technical task

`TTM_P01_L1_V3V4_S1_WATCHDOG_CONTAINMENT_HARDENING_AND_INTEGRATED_STATIC_QA`.

Resolve the five blockers in the same engineering package. Independently test source/negative fixtures, check PowerShell 5.1 parsing and static P/Invoke structure identities on the target, and keep historical PASS/FAIL + markers pinned. Only then consider **one** one-shot permit covering the isolated S1 harness build and a single native smoke run, supervised by the watchdog. No separate permission cycles for every code review step.

Existing scientific and phase state remains: `P00=UNCHANGED`, `10_F0=UNCHANGED`, exact frozen original HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, `lineage.md=UNCHANGED`, `P01=OPEN`, `P02=NOT_OPENED`, `NORMAL_STOP=NOT_REQUALIFIED`, `NATIVE_SECURITY=NOT_QUALIFIED`, `SCM=UNCHANGED`, `S1_NATIVE=NOT_EXECUTED`, all historical markers and the P00–P12 roadmap preserved.

This source design lock is **not** an approval to build or execute S1. Static PASS is not a runtime safety claim.
