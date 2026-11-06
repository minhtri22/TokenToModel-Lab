# P01 L1 — Broker V2 source lock and Windows compile-only gate

## Verified predecessor
- Windows native service creation was reported PASS in receipt `L1_SC_CREATE_SERVICE_ONLY_RECOVERY_20261106T152355102Z_454cdea0`, committed to GitHub at `95870061d084bcba4283167dc361874421b56c1a`.
- The receipt file SHA256 `245308dc2aab69e002fb5b1f4c3ae789795508402ec6f7a75b6f3137850252fd` was independently verified on the uploaded bytes.
- SCM reported `CreateService SUCCESS`, `ChangeServiceConfig2 SUCCESS`, LocalService, DEMAND_START, expected V1 binary path and `service_started=false`. No native security qualification is claimed.
- Original P01 HEAD remains `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, ten F0 tests remain locked.

## New static security finding — do not start V1
The installed V1 attestation-only service calls `NamedPipeServerStream.RunAsClient` immediately after `WaitForConnection` and before it performs a `pipe.Read`. Microsoft documents the impersonation identity as that of the **last message read** from the pipe. This order cannot positively attest the worker client token. The service code remains immutable for traceability; do not use the installed V1 binary as proof of working named-pipe peer SID authentication.

References:
- https://learn.microsoft.com/en-us/dotnet/api/system.io.pipes.namedpipeserverstream.runasclient
- https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient
- https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights

## Successor source candidates
- `runtime/p01/windows/BrokerAttestationServiceV2.cs`, Git blob `49b2aa5e7ce36657bfd001bfffc9019988588538`: read request BEFORE RunAsClient, then reject incorrect peer SID, respond only to `AUTH_PROBE`, never write evidence.
- `qa/p01/windows/TTMWorkerNativeProbeV2.cs`, Git blob `0e089a5a52c1c36f5ffa4813d30c55617ad379aa`: worker logon, individual denied file-access requests, separate denied ledger GENERIC_WRITE open, explicit pipe-client impersonation level.
- `qa/p01/windows/Compile-TTM-P01-L1-BrokerV2-PS51.ps1`, Git blob `ae1432192c1815fa783221d6eb0b40e97bf10d99`: no SCM, account, ACL, credential or ledger modifications; requires exact original HEAD and V1 source/binary SHA, service installed but STOPPED, elevated Windows PowerShell. Refuses existing output names. Fetches exact V2 source blobs by commit and compiles new `TTMP01Broker.attestationV2.exe` and `TTMWorkerNativeProbeV2.dll`. Commits PASS/BLOCK/FAIL with SHA-256 readback to the same branch.
- Static preflight receipt `artifacts/qa/p01/L1_BROKER_V2_STATIC_SECURITY_PREFLIGHT_20261106.json`: 20/20 source predicates present; **no Windows compiler has yet executed on V2**.

## Strict boundaries
1. Exactly one compile-only V2 pass allowed after all pins validated. No V1 start, no service binPath update yet.
2. Do not rerun on any failure or partial output: preserve source/binary files and receipts for a targeted recovery.
3. A successful compile only authorizes separate consideration of a safely pinned SCM binary-path update and native security tests. It does **not** qualify service SID, DACL, worker token, pipe client authentication or job confinement.
4. No P00, F0, W01–W12, grouped L1, P02 or other phases. `lineage.md` receives no engineering entries.

Current gate: `SCM_SERVICE_CREATED_PASS`, `BROKER_V2_COMPILE_NOT_EXECUTED`, `WINDOWS_SECURITY_NOT_QUALIFIED`, `W01_W12_NOT_EXECUTED`, `GROUPED_QA_NOT_AUTHORIZED`, `P01_OPEN`, `P02_NOT_OPENED`.
