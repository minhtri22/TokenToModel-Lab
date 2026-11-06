# TTM P01 L1 — exact SCM stop recovery after native security test failure

Date: 2026-11-06. Scope: **engineering infrastructure recovery**, not science.

## Source of truth

Live Windows read-only snapshot `L1_V2_STOP_UNVERIFIED_READONLY_20261106T163110268Z_e71a460b`, GitHub evidence commit `bcbc91328045d691819faaf81fdbb5f085e8ba2f`, SHA-256 `9c8aaeff041a4c3099b9098e8b062196df0cf8fe9c0741e5a27930218abd98e7`:
- SCM service `TTMP01Broker`: `RUNNING`, PID `26200`; service `WIN32_OWN_PROCESS`, `STOPPABLE`, Manual, `NT AUTHORITY\LocalService`.
- Live image `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\_ttm_p01_l1_service_provision_20261106\broker_service\TTMP01Broker.attestationV2.exe`, SHA-256 `a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a`.
- Live process creation `2026-11-06T16:24:42.113Z` (Unix milliseconds `1793982282113`). This is an exact identity pin for recovery and must not be inferred from PID alone.
- Original worktree HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, original branch and origin confirmed.
- Prior immutable SCM switch marker SHA-256 `29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1`.
- Prior native test marker SHA-256 `f0d895e68c30b8c3845336ea8aee40d2e1ca84f96816906a952ae70ad81587c7`.
- No marker deletions, account/ACL/SCM changes or W01–W12 test in read-only diagnosis.

Incident receipt commit `45f74877a43a66e6559f2a61d6f765ffd0c7da98` documented `PIPE_DACL_NATIVE=BLOCK_PIPE_DACL_READ_231` and `SERVICE_STOP=BLOCK`. Win32 231 means `ERROR_PIPE_BUSY`, **not** DACL denied. OnStop source uses a blocking `WaitForConnection` and a 5000ms join; it is an **unconfirmed hypothesis** for the failed Stop-Service behavior.

## Next controlled recovery — one SCM stop request, NO FORCE KILL

Script: `qa/p01/windows/Recover-TTM-P01-L1-ExactSCMStop-PS51.ps1`.

Expected Git blob `f7ff0ce7498641164fc3a614abe3815ec1b0264f`. Static source contract predicates 31/31 present, **not a Windows-native execution**.

The script:
1. Requires elevated Administrator token and exact original worktree HEAD, branch and origin, no project-path reparse points.
2. Verifies SHA-256 of the V2 EXE, both immutable markers, and SCM config Manual/LocalService/pinned V2 path.
3. If service is already `Stopped` with PID 0, records state and makes **no Windows change**. If transitional, missing, wrong PID/image/creation time, BLOCK without control request.
4. If still running, requires SCM PID **26200**, live image path and process creation time within one second of the frozen incident `1793982282113` UTC milliseconds. This checks PID reuse.
5. Verifies GitHub receipt publishing access before changes and new recovery-marker absence using Win32 GetFileAttributesW with exact `ERROR_FILE_NOT_FOUND=2`.
6. With explicit `-Apply`, creates a new project-scoped anti-replay marker `L1_BROKER_V2_SCM_STOP_RECOVERY_ATTEMPT_20261106.lock` (atomic `FileMode.CreateNew`); sends **exactly one** `sc.exe stop TTMP01Broker` control; records raw output and native exit; polls SCM state for **at most 15 seconds**.
7. Records `PASS_CONTROLLED_SCM_STOP_RECOVERED` only when SCM reports `Stopped` and PID 0 after successful command. If SCM returns nonzero but the service stopped, evidence reports `RECOVERED_STATE_WITH_SCM_CONTROL_ERROR`, not a full PASS. If still running or pending, `BLOCK_STOP_RECOVERY_UNRESOLVED_NO_FORCE`.
8. Captures final SCM state in all cases, writes only a new TTM-local QA JSON receipt, publishes via `gh api` to QA branch and SHA-256 verifies readback.

The script **never sends** Stop-Process, taskkill, forced termination, second stop command, service start/config/delete; it neither reads DPAPI secrets nor modifies ACL, accounts, ledger, worktree/F0, markers, science lineage, W01–W12 or grouped QA. If unsuccessful, stop and preserve all receipts/marker; a separate reviewed recovery would be necessary to force terminate the **currently verified** service process, not blindly PID 26200.

## Hold and next gate

`LIVE_SERVICE_LAST_OBSERVED=RUNNING`
`SCM_STOP_RECOVERY=SOURCE_STATIC_ONLY`
`NATIVE_SECURITY=BLOCK`
`WORKER_PEER_PROBE=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`
`W01_W12=NOT_EXECUTED`
`P01=OPEN`
`P02=NOT_OPENED`.

Preserve P00, original HEAD, all ten F0 results, P00–P12 phases, append-only science lineage, and all QA FAIL/PASS evidence.
