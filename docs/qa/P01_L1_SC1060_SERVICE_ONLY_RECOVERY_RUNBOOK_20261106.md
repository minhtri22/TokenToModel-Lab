# TTM P01 L1 — Service-only recovery after SCM 1060 (2026-11-06)

## Observed Windows state

- Original local HEAD: `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- User diagnostic run: `L1_SC_CREATE_READONLY_DIAGNOSTIC_20261106T151647906Z_e106f8ef`.
- GitHub evidence commit: `a56692b0029296042279218e33924008edd2e64b`.
- Source evidence file: `artifacts/qa/p01/L1_SC_CREATE_READONLY_DIAGNOSTIC_20261106T151647906Z_e106f8ef.json`.
- Windows diagnostic reported source EXE SHA-256 `56a780db6aa61fdd556540da340a3be223df2e41e1a7295bb33d05628dbf87ef`.
- `TTMP01Worker` account already created, SID pinned. Dedicated protected broker directory and evidence directory with service SID present, worker RX evidence directory, encrypted credential and SQLite ledger file present.
- `sc.exe query TTMP01Broker` and `sc.exe qc TTMP01Broker` both returned exit code **1060**: named service does not exist. The earlier `SC_CREATE_FAILED` receipt lacked the exact native error, so no definitive root cause is proven.

## Corrected next action: service-only one-shot recovery

New script: `qa/p01/windows/Recover-TTM-P01-L1-SCM-ServiceOnly-PS51.ps1`.

Purpose: **register the missing service only** under `NT AUTHORITY\LocalService`, start mode `demand`, exact pinned EXE, and set service SID to `unrestricted`. It passes `sc.exe create` option names and values as separate argv elements, consistent with Microsoft's `sc.exe create` specification. It records raw SCM command output and exit code.

Mandatory guardrails:
- Never create another account, rewrite/inspect credential bytes, recreate ledger, delete staging, change ACL, start broker, run worker or invoke W01–W12.
- Verify exact original HEAD/branch/origin, no reparse ancestor, EXE SHA256, existing worker identity and non-admin membership, pinned service SID, exact SID config file, existence of DPAPI and ledger, protected stage/broker/evidence DACL, and absence of worker write rights.
- Service `TTMP01Broker` **must still be absent with SCM 1060**. If service exists or unexpected state is found, fail closed. Do not run it again after a service-create attempt.
- Require elevated Windows PowerShell 5.1 and explicit `-Apply`.
- On success or failure, persist all PASS/BLOCK/FAIL and exact SCM error/output under TTM QA receipts, publish JSON to GitHub successor branch using `gh api`, and SHA-256 readback verify.
- The script registers but **does not start** the service. Native service SID/pipe DACL, actual worker denied-open and peer authentication are separate future gates.
- If `sc create` succeeds but `sc sidtype` or readback fails, this is a **partial state**; never delete or retry automatically.

## GitHub source and status

- Recovery script source commit: `2073135e93697c3901745de3541e4fe6c691df7f`.
- Script Git blob: `ab7e139461ea0d266dcd35cae24547fc61ca7466`.
- 18/18 static source-contract predicates present; **not an independent Windows-native test**, and no Windows command has yet been executed by this new script.
- The old SC_CREATE failure evidence remains immutable; no science lineage update.

## Decision

`SERVICE_ONLY_SOURCE=PREPARED_STATIC_ONLY`
`SERVICE_RECOVERY_APPLY=NOT_EXECUTED`
`NATIVE_SERVICE_SID=NOT_ATTESTED`
`NATIVE_PIPE_DACL=NOT_EXECUTED`
`WORKER_DENIED_OPEN=NOT_EXECUTED`
`W01_W12=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`
`P01=OPEN`
`P02=NOT_OPENED`

Preserve P00, original HEAD, ten F0 results, and P00–P12 roadmap.
