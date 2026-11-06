# TTM P01 L1 — V2 recovery adjudication and lean V3 shutdown / V4 pipe ACL successor

Date: 2026-11-07. Engineering QA only; original frozen research worktree and `lineage.md` unchanged.

## I. Formal engineering adjudication

Source: exact native Windows receipt `L1_BROKER_V2_EXACT_PROCESS_RECOVERY_V3_20261106T170736634Z_c6d1a217`, GitHub commit `a5a0006f6586a78b6a748fea018625c65e569c8f`, file SHA-256 `2252add34aff11fdd11889bceceedb1f3e8da47c40db8fcbd5e71cb2881ad6a5`.

The receipt confirms kernel-handle verification of the original `TTMP01Broker` process PID 26200, source EXE pin, process creation timestamp and SCM binding; all three earlier markers were intact and a new force-recovery marker was created once (SHA-256 `59823e4cd684195692dc5988a4af3eb484b05c4f7e5597e34140c1e21ac01dc9`). `TerminateProcess` was called on that precise process handle and `WaitForSingleObject` verified the exit. SCM then read `Stopped`, PID `0`. SCM `WIN32_EXIT_CODE=1067` confirms **not a graceful service stop**. No SCM configuration, account, ACL, science or prior-marker mutation was recorded.

**Verdict:** `PASS_EXACT_TTM_PROCESS_RECOVERED_WITH_FORCED_TERMINATION`, limited to this observed one-shot infrastructure recovery. No claim of a currently stopped service without a new live readback. Previous `ERROR_PIPE_BUSY=231` and failed normal stop `1061` remain in evidence. The worker V3 denied-open tests and peer handshake were not executed.

## II. Smallest useful successor

Design and implement **two separate source-only successors**; do not edit V1/V2 or frozen P01/F0.

1. **Broker V3 graceful stop:** Replace blocking single-instance `WaitForConnection()` and unsynchronized `active` handling with cancelable asynchronous connection wait / read under an explicit stop signal and synchronized pipe ownership. No queued writes or filesystem effects. `OnStop` should cancel pending operations, release pipe, and verify service-thread exit within a strict finite bound. Never declare STOP success merely because `Stop-Service` was invoked. Preserve manual LocalService, exact worker/service SID checks, read-before-`RunAsClient`, protected explicit DACL, and deny-all writes. No fallback listener with default DACL.
2. **Worker probe V4 handle-based pipe DACL readback:** Keep pinned worker identity and `PipeAccessRights.ReadWrite` (must not include `CreateNewInstance=0x4`). After the worker opens a *real connected pipe handle*, call Win32 `GetSecurityInfo` on that **handle**, not `GetFileSecurityW` on `\\.\pipe\...` by name. Request `DACL_SECURITY_INFORMATION` only; require `READ_CONTROL`. Copy the self-relative descriptor into managed memory, parse actual allowed ACE SIDs and access masks, reject broad allow identities and worker `CreateNewInstance`, `WRITE_DAC`, `WRITE_OWNER`. Do not publish raw SDDL or credentials. Then perform the individual negative worker directory/ledger rights tests and the existing peer-SID handshake. Do not write evidence/ledger.
   
Microsoft platform references:
- `GetSecurityInfo` explicitly accepts a named-pipe handle; READ_CONTROL is required to read its DACL: https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo
- Named pipe DACL and specific client rights: https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights
- The .NET Framework async wait requires an asynchronous pipe instance: https://learn.microsoft.com/en-us/dotnet/api/system.io.pipes.namedpipeserverstream.beginwaitforconnection
- `EndWaitForConnection` must be called once for every begin attempt: https://learn.microsoft.com/en-us/dotnet/api/system.io.pipes.namedpipeserverstream.endwaitforconnection

## III. Three-step minimal technical process (no new science)

**Step 1 — Implement + source-only independent QA:** Author two new source files, preserve previous compilation and all one-shot markers. QA must review precise cancel behavior including stop while idle, stop during handshake, peer connects but sends zero bytes, wrong SID, and service-thread unexpected exit. Audit C# marshalling, `LocalFree`, handle ownership, worker DACL exact ACE mask checks; parse PowerShell 5.1 launch scripts without executing native tests. Confirm no service, account, SCM, ACL or worker-secret side effects.

**Step 2 — Native compile-only Windows:** Run exactly one controlled compiler script for broker V3 and probe V4. Record C# source and compiled EXE/DLL SHA-256, native compiler outputs, exact original P01 worktree, stage disk/permissions, GitHub evidence hash readback. Do **not** switch SCM executable or start the broker at this step.

**Step 3 — Separate narrow native service smoke:** After compile-only and independent review PASS, authorize one SCM binary switch to exact V3 (service must still be stopped), and one new one-shot smoke with three minimum scenarios: (A) service starts + no client + normal SCM stop, (B) valid worker pipe handle DACL + distinct denied rights + peer handshake, (C) service stop after connected worker or stalled client. All need bounded timeouts, exact identity, strict per-scenario PASS/FAIL and verified final Stopped/PID0. Any failure preserves evidence; no retries and no automatic generic force-kill. Do not bundle W01–W12 or L1 grouped QA into this smoke.

## IV. Safety / scope

Prior infrastructure incident is **closed for the specific old process**; native security remains **unqualified**. No source or binary change to V2; **do not restart V2**. No system restart, no cleanup, no marker deletion, no local worktree outside `D:\WORK\RESEARCH\TokenToModel-Lab`, no repository merge, no P02 and no P00/F0 retest. Scientific `lineage.md` is append-only for science and must not be modified for this engineering recovery.

Current flags:
`P01=OPEN`,
`P02=NOT_OPENED`,
`NORMAL_SCM_STOP=FAIL_UNRESOLVED`,
`PIPE_DACL_HANDLE_AUDIT=NOT_EXECUTED`,
`WORKER_NEGATIVE_RIGHTS=NOT_EXECUTED`,
`W01_W12=NOT_EXECUTED`,
`L1_GROUPED_QA=NOT_AUTHORIZED`.
