# TTM P01 L1 — Windows CS1513 compile FAIL recovery (2026-11-06)

## Confirmed evidence
- User ran Windows PowerShell elevated; `ADMIN_REQUIRED` was resolved.
- The original worktree HEAD and GitHub authentication both passed.
- `BrokerAttestationService.cs(131,4): error CS1513: } expected` from Framework64 compiler.
- Terminal evidence already published by user in GitHub commit `c622fd78727e22c51c131f6ec8f066f98ff8aa08` under `artifacts/qa/p01/L1_SERVICE_PROVISION_20261106T140131649Z_20877669.json`, SHA-256 reported `d30d30926f312f9ad59ab73bf1a03a531334217fc1c98273d964410262dec96c`.
- C# source at `3954551912794bc0886b898b3900c87201450f72` missed the closing brace of `namespace TTMP01`. New corrected source commit `6109897e3697bec6a3fbadb561f1d9ec907f589a`, blob `d15e9b8c255777098b1baafad0a9fb6d4e95df13`, differs from the previous source by **exactly one final `}`**.
- Previous `-Apply` created the dedicated staging directories and attempted C# compilation; it stopped **before** `New-LocalUser`, `sc create`, service SID/ACL changes, Windows worker launch and W01–W12. Those operations are not evidenced by this run.

## No-replay recovery
- `qa/p01/windows/Recover-TTM-P01-L1-CS1513-Compile-PS51.ps1` fetches the exactly pinned corrected source, requires the existing old source, verifies the one-brace delta, writes *new filenames* `BrokerAttestationService.fixed.cs` and `TTMP01Broker.fixed.exe` in the existing staging directory, and invokes the target machine's Framework64 compiler.
- It explicitly forbids preexisting TTM broker service/worker account and refuses overwriting any recovery file. It does not modify ACLs, install services, run worker, F0, W01–W12 or grouped L1.
- It creates a new run-specific JSON evidence receipt under the TTM repository, commits it to the same successor branch via GitHub CLI and independently checks downloaded content SHA-256.
- A Windows compile PASS, if obtained, **does not** authorize the original `-Apply` or prove the service is secure. A separate **recovery-aware provisioning script** is required, and the original `-Apply` must never be replayed because its staging path already exists.

## Gate
`WINDOWS_SERVICE_CSC_V1=FAIL_RECORDED`
`CS1513_SOURCE_FIX=COMMITTED_NOT_WINDOWS_COMPILED`
`WINDOWS_USER_AND_SERVICE=NOT_PROVISIONED`
`NATIVE_WORKER_ACL_AND_PIPE_DACL=NOT_ATTESTED`
`W01_W12_NATIVE=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`
`P01=OPEN`
`P02=NOT_OPENED`

Keep P00, original local P01 HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, 10 F0 results and phase order unchanged. This is implementation QA, not a science lineage entry.
