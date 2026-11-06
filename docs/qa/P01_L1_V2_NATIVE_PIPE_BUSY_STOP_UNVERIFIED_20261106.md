# TTM P01 L1 — Native Broker V2 / Worker V3 STOP_UNVERIFIED incident (2026-11-06)

## Provenance / status
Original local HEAD: `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, locked P00 and 10 F0 remain unchanged.

User Windows native attestation attempted **exactly once**, run `L1_BROKER_V2_WORKER_V3_NATIVE_SECURITY_V2_20261106T162440152Z_456c7969`.
- Receipt GitHub commit: `45f74877a43a66e6559f2a61d6f765ffd0c7da98`
- Receipt SHA-256: `c46645a686701151878f4b96b439d502a9ecaa66d5384b08f6e8a3809bc2e59c`.
- Preflight and SHA pins: PASS; service start: PASS; live process token: PASS for `LocalService` and derived service SID.
- `PIPE_DACL_NATIVE=BLOCK` with precise result `BLOCK_PIPE_DACL_READ_231`; worker rights and peer probe NOT_EXECUTED.
- `SERVICE_STOP=BLOCK` with `ServiceCommandException`, final service state `UNVERIFIED`. Historical PID `26200` is *not* an identifier safe to kill after the run; Windows can reuse PIDs.
- Native one-shot marker `L1_BROKER_V2_WORKER_V3_NATIVE_SECURITY_ATTEMPT_20261106.lock`, SHA-256 `f0d895e68c30b8c3845336ea8aee40d2e1ca84f96816906a952ae70ad81587c7`; do not clear, rename or overwrite.
- W01–W12 NOT_EXECUTED; grouped L1 QA NOT_AUTHORIZED.

## Meaning of the Windows error

Win32 `231` is `ERROR_PIPE_BUSY` — all pipe instances are busy, **not** `ACCESS_DENIED`. This makes the name-based `GetFileSecurityW` attempt an inadequate DACL verdict on a single-instance pipe. Recommended platform interface is obtaining a pipe handle and calling `GetSecurityInfo` on that handle, after a separately gated source design and one-shot decision, *not* changing any service/pipe ACL now.

Citations:
- https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--0-499-
- https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-client
- https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights

Broker V2 source also uses blocking `NamedPipeServerStream.WaitForConnection` and in `OnStop` disposes active pipe and joins server thread for 5000 ms, then throws if not joined. This is a plausible stop-path contributor, but **root cause not yet proven**. Do not patch the running EXE or attempt a restart until live Windows service state is known and separate repair is authorized.

## Next safe action: read-only SCM snapshot

`qa/p01/windows/Inspect-TTM-P01-L1-StopUnverified-PS51.ps1`, Git blob `368ccbcb35203b2190c0d2073e765505a356c69f`.

Static source review 23/23 checks present, not native executed.

The operator runs exactly one snapshot with elevated Windows PowerShell 5.1. It:
- checks elevated token, captures actual SCM state and `sc.exe queryex`, `sc.exe qc` output, process PID *currently* associated with SCM plus image path, if any;
- confirms original worktree HEAD/branch/origin, expected V2 EXE SHA and **both previously created marker hashes**;
- emits `PASS_STOPPED_NOW` only if SCM State=Stopped AND ProcessId=0; otherwise emits `BLOCK_ACTIVE_OR_TRANSITION`, and never retries or stops automatically;
- writes a new JSON receipt ONLY in the TTM project QA receipt directory, publishes it to the same GitHub audit branch, independently verifies SHA-256 readback;
- does not start/stop service, kill or signal processes, modify SCM/account/ACL, import DPAPI secrets, touch ledger data, modify/re-run F0, use research adapter, or invoke W01–W12.

If a service is still Running/Stop Pending, choose a separately reviewed recovery with exact live binary and PID checks. Do not use `Stop-Process -Id 26200` or broad `taskkill`. If the service is already Stopped and PID=0, the immediate state is recovered; historical `SERVICE_STOP=BLOCK` remains in evidence, and native security is still not qualified.

## Hold decisions

`P01=OPEN`
`P02=NOT_OPENED`
`NATIVE_SECURITY=BLOCK`
`SERVICE_FINAL_STATE=UNVERIFIED_UNTIL_LIVE_READBACK`
`NATIVE_ONE_SHOT_MARKER=CONSUMED`
`WORKER_PEER_NEGATIVE_TEST=NOT_EXECUTED`
`W01_W12=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`

Do not append engineering QA to scientific `lineage.md`; preserve P00, original HEAD, ten locked F0, P00–P12 architecture and milestones.
