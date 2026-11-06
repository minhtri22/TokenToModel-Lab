# TTM P01 L1 — Broker V3 graceful stop + Worker V4 handle-DACL — source static implementation

Date: 2026-11-07 (engineering QA, not science).

## Canonical scope and provenance

- Repository `minhtri22/TokenToModel-Lab`, audit branch `audit/p01-l1-native-security-critical-fix-20261106`.
- Original frozen P01 worktree `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105`, exact HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- P00 and ten F0 results are unchanged; P00–P12 architecture and ordering unchanged. `lineage.md` is scientific append-only and was not edited.
- Previous V2 one-shot forced process recovery `PASS_EXACT_TTM_PROCESS_RECOVERED_WITH_FORCED_TERMINATION` (GitHub `a5a0006f6586a78b6a748fea018625c65e569c8f`), SCM Stopped/PID0 at its readback. This is **not** evidence that the service is stopped right now; no live SCM query in this source-only step. Prior ordinary-stop `1061` and named-pipe DACL read `231` BLOCKs stay unchanged.

## New implementation (source files only)

1. **Broker V3:** `runtime/p01/windows/BrokerAttestationServiceV3.cs`, Git blob `2fc1b63d6e21e7d8ac86184251974e9960572f3f`.
   - Preserves `TTMP01Broker`, `TTM_P01_L1_BROKER_V1`, LocalService and derived service SID token checks, explicit protected three-principal DACL (SYSTEM, exact broker service SID, exact worker SID).
   - Uses `PipeOptions.Asynchronous` for a single server instance; `BeginWaitForConnection/EndWaitForConnection`, `BeginRead/EndRead` and `BeginWrite/EndWrite`. A manual-reset stop event and `CancelIoEx` attempt to cancel pending overlapped I/O; *only* the server thread owns and disposes its pipe.
   - `OnStop` signals stop and waits at most 8 seconds for the thread, refusing to claim success on an unverified join. Reads a client message before `RunAsClient`, checks exact worker SID and supports only read-only `AUTH_PROBE`; other requests are denied. It never writes an evidence file.
   - **Limitation:** `CancelIoEx` only *requests* cancellation; Windows must confirm actual completion. The source-only review cannot prove deadlock-free shutdown (especially when a client is silent or a cancellation completion races with `EndWaitForConnection`). No PASS for normal STOP until a separate native idle/connected/stalled test.

2. **Worker V4:** `qa/p01/windows/TTMWorkerNativeProbeV4.cs`, Git blob `63d5407ccb3f9e15f8dda59ee6323a0e5009d860`.
   - Requires a real local worker `LogonUser` + impersonation; checks token user SID, and always reverts impersonation. Opens the same named pipe with explicit `PipeAccessRights.ReadWrite`, excluding `CreateNewInstance`, using an asynchronous client.
   - Calls Win32 `GetSecurityInfo` with `SE_FILE_OBJECT=1`, `DACL_SECURITY_INFORMATION=4` on `client.SafePipeHandle`; **never** opens a second named pipe instance to read DACL. Checks self-relative/protected DACL, exact SYSTEM/service/worker allow ACEs and access masks, forbids create-instance, WRITE_DAC and WRITE_OWNER, hashes the security descriptor, and calls `LocalFree`.
   - Separately requests seven forbidden directory rights and existing ledger generic write, requiring ACCESS_DENIED each time. Then requests `AUTH_PROBE` and validates `AUTH_PEER_OK_NO_WRITE`, with an asynchronous bounded receive and `CancelIoEx` on timeout. Does not create/modify evidence or ledger.
   - **Limitations:** No Windows compile or live handle-based DACL result. Exact ACE mask representation might differ after Windows mapping; any such discrepancy must remain BLOCK pending analysis, never be loosened to force PASS. The cancellation timeout branch is also unqualified on Windows.

## Independent static QA

Separate checker `qa/p01/windows/Independent-QA-BrokerV3-WorkerV4-Static.py`, Git blob `0d42c4f7a4ac08c59022449210a323feed3a7495`. It is read-only, uses the Python standard library, tests source contracts and C# bracket/literal balance, and runs negative mutation fixtures. Its JSON output goes to stdout; it does not write local files, change any Windows state or execute target C# code.

A separate JavaScript static reviewer fetched the three exact files **back from GitHub** and executed **48/48 positive source/lexical checks** and **12/12 negative mutations rejected**. See `artifacts/qa/p01/L1_BROKER_V3_WORKER_V4_SOURCE_STATIC_QA_20261107.json`. These results are only *textual/lexical static validation*, not .NET compilation and not an external human security certification. The committed Python checker has **not yet been executed** on Windows, and C# source has **not been compiled**.

For the subsequent independent local Python QA, read-only invocation once the audit branch is checked out into an **explicit, new project-local QA worktree** or the files have been placed in an approved TTM project-local staging directory:

```powershell
& "C:\Users\minht\miniforge3\python.exe" -B "qa\p01\windows\Independent-QA-BrokerV3-WorkerV4-Static.py" --broker "runtime\p01\windows\BrokerAttestationServiceV3.cs" --worker "qa\p01\windows\TTMWorkerNativeProbeV4.cs"
```

This is a command **example** relative to an approved project-local TTM checkout; do not run it from an unrelated repository and do not auto-create/delete worktrees. The QA output includes both positive/negative results and source SHA256, but is not a native security verdict. An evidence wrapper must additionally pin exact Git blob/SHA256, pass an independent Windows PowerShell 5.1 preflight, and GitHub-upload the resulting JSON before a separate native compile decision.

## Next integration/negative-test matrix — NOT executed

| Case | Expected outcome |
|---|---|
| B0: start broker V3 with no client, send ordinary SCM stop | Service Stopped, PID0 within bounded time |
| B1: worker connected but sends no payload, then SCM stop | Pending read cancelled, service Stopped/PID0 |
| B2: valid worker request, verify DACL via same connected handle | Exact 3-SID DACL PASS, read-only peer handshake PASS |
| B3: wrong SID / unpinned client | No authenticated OK reply |
| B4: worker tries to open seven forbidden directory rights | Seven independent ACCESS_DENIED results |
| B5: worker tries to write existing SQLite ledger | ACCESS_DENIED |
| B6: service stop races connection/read/write/cancellation | No hang, no second broker instance, final Stopped/PID0 |
| B7: malformed/no payload client + timeout | No authenticated OK, bounded stop |
| B8: unexpected DACL owner/ACE/mask / broad grants | BLOCK, never weaken DACL |
| B9: errors during `CancelIoEx` or `EndWaitForConnection` | BLOCK with unmodified environment and preserved receipts |

Every native scenario requires an exact separately authorized one-shot harness and evidence. **No native test, installation, SCM switch, start/stop or worker impersonation occurred in this phase.**

## Strict gate status

`BROKER_V3_SOURCE=IMPLEMENTED_STATIC_ONLY`
`WORKER_V4_SOURCE=IMPLEMENTED_STATIC_ONLY`
`STATIC_SOURCE_CHECK=48/48`
`NEGATIVE_SOURCE_FIXTURES=12/12`
`INDEPENDENT_PYTHON_CHECKER=COMMITTED_NOT_EXECUTED`
`WINDOWS_CSC_COMPILE=NOT_EXECUTED`
`SCM_V3_SWITCH=NOT_EXECUTED`
`BROKER_V3_START=NOT_EXECUTED`
`NATIVE_SECURITY=NOT_QUALIFIED`
`W01_W12=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`
`P01=OPEN`, `P02=NOT_OPENED`.

Future gates: `TTM_P01_L1_V3_V4_INDEPENDENT_STATIC_QA_TARGET_AND_WINDOWS_COMPILE_ONLY_PREFLIGHT`, followed only after PASS by a separate, bounded one-shot compile-only gate. No binary install/SCM switch/start is authorized now.

Microsoft platform sources:
- https://learn.microsoft.com/en-us/dotnet/api/system.io.pipes.namedpipeserverstream.beginwaitforconnection
- https://learn.microsoft.com/en-us/dotnet/api/system.io.pipes.namedpipeserverstream.endwaitforconnection
- https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex
- https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo
- https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights
