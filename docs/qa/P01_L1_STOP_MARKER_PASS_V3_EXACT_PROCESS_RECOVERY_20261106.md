# TTM P01 L1 — STOP marker PASS, quarantine V2, clean exact-process recovery V3

Date: 2026-11-06 UTC. Engineering QA only. No scientific `lineage.md` entry.

## Independent finding

The immutable Windows forensic receipt `L1_STOP_MARKER_MISMATCH_READONLY_20261106T170118472Z_ebead616` at GitHub commit `8f8dfde1fda2a8907a1bae04f6459f486f0f68ec` verifies:

- Actual `L1_BROKER_V2_SCM_STOP_RECOVERY_ATTEMPT_20261106.lock` SHA256 = `f1ca3d0899fe6637a512e44dd073b449d4805ca8f8a8afa1e8a3989599143502`.
- Original expected hash = exact same 64-character SHA256.
- Actual and expected bytes = 130/130; first different byte = null.
- SCM `TTMP01Broker` still RUNNING, PID 26200 at the time of this snapshot.
- `L1_BROKER_V2_EXACT_PROCESS_TERMINATE_ATTEMPT_20261106.lock`: `NOT_CONFIRMED_PRESENT`; this DOES NOT demonstrate absence. Exact Win32 `GetFileAttributesW` remains mandatory during the recovery run.
- No forced process termination or SCM mutation happened in this diagnostic. Original HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0` remains pinned.

The first exact-process recovery script had a **63-character expected marker SHA**, causing `PRIOR_MARKER_SHA256_CHANGED_SCM_STOP_RECOVERY` before any handle/termination. The previously reported claim that it matched was false; the corrected conclusion is `FAIL_IMPLEMENTATION_PIN_FORMAT`, **not marker tampering**.

## Quarantine of V2 source corruption

The intermediate **unexecuted** `qa/p01/windows/Recover-TTM-P01-L1-ExactProcessAfter1061-V2-PS51.ps1` at Git blob `f630efdf62345f8a983ae7cf76d171bbd85646bb` is invalid. Its source contains a malformed regex string in the marker guard and duplicated trailing script content after `exit $exitCode` (489 lines versus 294 in predecessor). It must **never** be executed. Preserve the commit for QA evidence and don't overwrite it.

## Clean V3 source

Script `qa/p01/windows/Recover-TTM-P01-L1-ExactProcessAfter1061-V3-PS51.ps1`, Git blob `0928fc1879ce2ac8bf344ab5fa2c65c73bc74e38`.

Rebuilt from immutable, earlier Windows parse-passed V1 source `24de8b99bf3c11250af5002d57603ebf0365713b`, with only:
- Exact 64-character `SCM_STOP_RECOVERY` SHA taken directly from committed original stop receipt.
- Strict 64-character hex format predicate on every pinned marker.
- New V3 run ID/schema and cross-references to both failure and successful forensic receipts.
- Unique V3 GitHub source path; original artifacts and V2 remain unmodified.

The rebuilt file contains 297 lines, exactly one `TerminateProcess` site inside a native helper operating on a previously verified kernel HANDLE; one terminal exit, two expected `Add-Type` blocks with closed here-strings. GitHub static text checks passed. **Windows PowerShell `Parser.ParseFile` has NOT yet been run on V3**. The launcher must parse the exact locally downloaded blob and BLOCK on any parse error *before* using the explicit terminate switch.

## One-shot safe recovery contract

On a live Windows host, V3 must confirm elevated administrator, exact original HEAD/branch/origin, SHA256 pinned V2 EXE and all 3 original marker hashes, exact SCM Manual + LocalService + V2 binPath, SCM still Running PID 26200, exact image and process creation timestamp `1793982282113` milliseconds. Then it checks the force-recovery marker absent via `GetFileAttributesW` with last error 2. It validates the live process's identity via OS HANDLE creation timestamp, full image path and STILL_ACTIVE; before *explicit* termination, it rereads SCM. A new TTM-scoped anti-replay marker is created atomically with `FileMode.CreateNew`; the native helper reopens and revalidates the exact HANDLE, then calls `TerminateProcess` **at most once**. It polls SCM and requires `Stopped/PID0` for infrastructure recovery PASS; it never restarts the service. On any mismatch or partial recovery, BLOCK, preserve evidence, no retries.

This is a **forcible termination** of the exact dedicated TTM broker, with potential loss of its transient in-memory state; no generic process kill is permitted. No SCM configuration changes, ACL/account mutation, worker or credential/ledger changes, no deletion of any marker or QA history, no P00/F0, W01–W12 or grouped L1 runs.

## Current status

- `SCM_STOP_MARKER_INTEGRITY=PASS`.
- `EXACT_PROCESS_RECOVERY_V3=STATIC_SOURCE_LOCKED_NO_WINDOWS_PARSE_OR_RUNTIME_YET`.
- `TTMP01Broker=RUNNING_LAST_OBSERVED_PID_26200`.
- `BROKER_NATIVE_SECURITY=BLOCK` from Win32 231 DACL read and failed service Stop.
- `P01=OPEN`, `P02=NOT_OPENED`; `W01_W12=NOT_EXECUTED`, `L1_GROUPED_QA=NOT_AUTHORIZED`.
- Keep original HEAD, ten F0 results, all governance gates and approved P00–P12 sequence unchanged.

Next gate: `TTM_P01_L1_CLEAN_V3_WINDOWS_SOURCE_PARSE_AND_EXACT_PROCESS_RECOVERY`. Do not claim successful recovery until the new native Windows receipt is independently read back and adjudicated.
