# TTM P01 L1 — Controlled native Windows service provisioning checkpoint

Date: 2026-11-06. Engineering evidence only, **not a scientific verdict**.

## Independent evidence already verified
- Original worktree HEAD: `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- User-provided native receipt `L1_WINDOWS_NATIVE_SECURITY_20261106T132450275Z_5830bbb6` was committed as `8742417f16931f48215287465f0b5ee2dfead513`, with three hard BLOCKs: absent broker service, missing worker account, and unprovisioned evidence-root ACL. W01–W12: NOT_EXECUTED.
- Remote command surface returned `managed mode requires task_job_submit`. No TTM-scoped task/lease permitted remote Windows work, so remote work was not attempted through any substitute identity.

## New source changes, all on successor GitHub branch
- `runtime/p01/windows/BrokerAttestationService.cs`: SCM-compatible **attestation-only** LocalService executable; service SID must be present in token groups; explicit `PipeSecurity`, nonbuilt-in worker SID allow rule, `RunAsClient` peer SID validation; **rejects all WRITE operations**. It is **not an operational trusted file broker**.
- `qa/p01/windows/Invoke-TTM-P01-L1-NativeServiceProvision.ps1`: Windows PowerShell 5.1, guarded `-Apply`. On a fresh target with elevated rights, creates one dedicated worker account with a cryptographically random password; retains QA credentials only as user-scoped DPAPI under a locked TTM directory; compiles the source into a native .NET Windows service executable; configures a demand-start LocalService service SID; applies explicitly protected directory ACL and ledger-file ACL under TTM; attempts service start/stop; writes a terminal receipt even after partial failure; commits to the same GitHub branch and verifies exact SHA-256 readback. The script refuses an already existing account/service/path, and never merges, checks out, fetches or resets the pinned worktree.
- `qa/p01/windows/TTMWorkerNativeProbe.cs`: stand-alone native Windows test for fresh worker-token impersonation, read-only `OPEN_EXISTING` denied write access, and authenticated Named Pipe worker-peer acknowledgment. **Not invoked by the provisioning script yet**.

Source pin (Git blobs at reviewed commit `a3f19ba60110ad5799f7f415f5584b0ab643ea95`):
- Service C#: `ac3d4f88974930f67549445f8e37c9809ce61516`
- Provision script: `0250176d3b9e421ca07efd1bde2b7e10e856abe7`
- Native worker probe C#: `7fec3d8366c274f932db144648ad6b889e986c49`

## Independent static source checks
14/17 design-contract features present. Three critical native-evidence gates absent:
1. The provisioning script does not execute the worker-token denied-write / pipe peer probe.
2. No independently executed Windows pipe DACL readback.
3. No W01–W12 native negative test execution.

No claim of a successful C# compiler run, installation, ACL enforcement, worker token confinement, live IPC, or Windows W01–W12 is made. None has been executed on the target computer in this checkpoint.

## Operational safety
- Only elevated operator may run `-Apply`. This *does* create a machine-local user and a demand-start service, and changes ACL within a new dedicated TTM workspace; it is not read-only.
- The script is **one-shot and refuses pre-existing identities**. If partial provisioning fails, it preserves the exact state for adjudication rather than deleting accounts/services automatically; do not rerun -Apply blindly.
- The DPAPI credential file must never be added to Git, downloaded to external machines, or exposed in logs; it is readable by the same Windows user who provisioned it, if DPAPI context remains available.
- An SCM "Running" status or ACL set call is **not** equivalent to denied-open proof. It is explicitly recorded at narrower scope.
- Because this is an attestation-only broker, user data writes and L1 grouped QA remain forbidden.

## Gate decision
`WINDOWS_SERVICE_SOURCE=IMPLEMENTED_CANDIDATE`
`WORKER_IDENTITY_ACL_PROVISIONING=NOT_YET_EXECUTED`
`PIPE_SERVICE_SID_NATIVE=NOT_ATTESTED`
`WORKER_EFFECTIVE_DENIED_OPEN=NOT_EXECUTED`
`W01_W12_NATIVE=NOT_EXECUTED`
`L1_GROUPED_QA_PERMIT=NOT_GRANTED`
`P01_CLOSURE=PENDING`
`P02=NOT_OPENED`

Do not append this engineering checkpoint to scientific `lineage.md`. Do not modify P00, original worktree HEAD, 10 F0 results, or P00–P12 order.
