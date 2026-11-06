# P01 L1 — V2 SCM switch PASS / V3 worker explicit named-pipe access

Date: 2026-11-06. **Engineering QA, not science.**

## Verified predecessor
- Original local HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- User Windows receipt `L1_BROKER_V2_SCM_SWITCH_20261106T155323454Z_31650e56`, independently retrieved from commit `98f96dfd002fde146b0922501510b3229ad63bc9`.
- SCM binPath changed from V1 to exact V2 executable, `sc.exe config` exit 0 and `Win32_Service` readback PASS. LocalService, stopped, demand/manual start unchanged. One-shot marker SHA-256 `29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1` was recorded and must never be deleted/replayed.
- V2 EXE SHA-256 `a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a`.
- V2 worker probe DLL SHA-256 `ea44cc5fca81e7f1e692726502dea0ad97ab543bc86f2abef52a25e1ffa96eb6`.

## Additional source-level security finding
The compiled worker V2 probe connects with `NamedPipeClientStream(..., PipeDirection.InOut, ...)`. Windows maps broad generic write access to a bitmask that includes `FILE_APPEND_DATA` (same bit as `FILE_CREATE_PIPE_INSTANCE`). The broker DACL intentionally denies worker instance-creation rights. Therefore relying on a broad generic client open can fail even when the worker SID is correctly authorized. Reference: https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights.

Successor `qa/p01/windows/TTMWorkerNativeProbeV3.cs` requests the explicit .NET `PipeAccessRights.ReadWrite`, whose bitmask excludes `CreateNewInstance`, with `TokenImpersonationLevel.Impersonation`. The V3 source retains separate worker-token denied-open checks for individual directory rights and ledger write, and no evidence-writing operation.

Source Git blob `0414705e093780a6da3b9d2466abe67586db108e` (source commit `28e43406f65cd38b08e12d2061664d0202139a9c`).

## Next gate: V3 worker-only Windows compilation
`qa/p01/windows/Compile-TTM-P01-L1-WorkerProbeV3-PS51.ps1` has source Git blob `b856750fe6205a41b76ce1c17a34be415ff79af1`. Static source review: 21/21 contracts present (not a Windows run). It:
1. Requires elevated PowerShell 5.1, pinned original HEAD/branch/origin, V2 SCM installed stopped/manual/LocalService, exact V2 broker and probe binary SHA-256.
2. Verifies `PipeAccessRights.ReadWrite & PipeAccessRights.CreateNewInstance == 0` at Windows runtime.
3. Downloads V3 source using exact GitHub blob SHA, writes **only new names** `TTMWorkerNativeProbeV3.cs` and `TTMWorkerNativeProbeV3.dll` inside TTM protected staging; refuses existing files rather than overwriting.
4. Invokes Windows Framework64 `csc.exe` for the DLL only, records compile stdout/exit, source and DLL SHA-256.
5. Publishes a separate new QA receipt under TTM, commits to the same audit branch, verifies GitHub SHA-256 readback.
6. Does not start/stop or change SCM, account, ACL, DPAPI/ledger, P00, F0, W01–W12, or L1 grouped QA.

The earlier candidate `Invoke-TTM-P01-L1-BrokerV2-NativeSecurityOneShot-PS51.ps1` is **explicitly blocked at native dispatch** pending this V3 compile gate; do not use `-Execute` from that older script. A separately locked native attestation launcher is required after V3 Windows compilation. The named-pipe DACL readback must be independently verified; an Administrator readback may fail if not granted READ_CONTROL, so a BLOCK cannot be relabeled PASS.

## Current decisions
`SCM_V2_SWITCH=PASS`;
`WORKER_V3_SOURCE=STATIC_ONLY`;
`WORKER_V3_WINDOWS_COMPILE=NOT_EXECUTED`;
`BROKER_V2_NATIVE_START=NOT_EXECUTED`;
`WORKER_TOKEN_PIPE_DACL=NOT_QUALIFIED`;
`W01_W12=NOT_EXECUTED`;
`L1_GROUPED_QA=NOT_AUTHORIZED`;
`P01=OPEN`;
`P02=NOT_OPENED`.

Keep P00, locked ten F0 results, original worktree and P00–P12 roadmap unchanged. Do not append engineering QA to scientific lineage.
