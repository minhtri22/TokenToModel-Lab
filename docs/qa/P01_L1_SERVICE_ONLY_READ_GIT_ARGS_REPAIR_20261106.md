# TTM P01 L1 — service-only recovery Git identity guard FAIL, repair (2026-11-06)

## Immutable user-observed evidence
- Run: `L1_SC_CREATE_SERVICE_ONLY_RECOVERY_20261106T152201194Z_75b850c6`
- Receipt GitHub commit: `cddc0e986f201d35bdd26e0d0f8214eb2a9f710d`
- Receipt path: `artifacts/qa/p01/L1_SC_CREATE_SERVICE_ONLY_RECOVERY_20261106T152201194Z_75b850c6.json`
- Windows-reported receipt SHA-256: `8d645788faf1bf1ef6a3f422016610808911405973d71dc1558b0d85ae08a7de`
- Outcome: `LOCAL_GIT_IDENTITY_FAILED`. Empty `checks`, `sc_create_exit=null`, `sc_sidtype_exit=null`. Service creation **NOT ATTEMPTED** in this run. W01–W12 NOT_EXECUTED, grouped L1 NOT_AUTHORIZED.
- Prior independent Windows read-only diagnostic found service absent (SCM 1060), worker account/credential/ledger already present with protected ACL. No new service-account mutation claimed.

## Source correction
The recovery helper was defined as `function Read-Git([string[]]$args)`, shadowing the automatic PowerShell variable `$args`. Its calls also used positional-array splatting instead of an explicit named array parameter. This can prevent the intended arguments from reaching `git.exe`. In-source correction:
- `$args` renamed to `$GitArguments`;
- explicit `Read-Git -GitArguments @('rev-parse','HEAD')`, similarly for branch/origin;
- native invocation `git.exe -C $wt @GitArguments`.

Corrected GitHub commit: `a92665bb8344904d055d3e6202c44b6e189fc008`.
Corrected source Git blob: `378608e940cabc06d9d3cc4bcc347ba7d3c758f2`.
Static audit readback: 12/12 targeted guards satisfied; **not a Windows-native execution**.

## Next gate
Run the corrected script with **new unique local filename** after verifying Git blob, under elevated Windows PowerShell 5.1. Existing account and ACL are **reused read-only**. Script is permitted to register *only* missing `TTMP01Broker` service, with manual start and LocalService user, and captures exact SCM result. It does **not** start broker, recreate accounts, change ACL, touch ledger/credentials, delete staging, run W01–W12 or grouped L1. No rerun of the old script. On any BLOCK or partial state, stop and preserve evidence.

`SC_SERVICE_RECOVERY=NOT_YET_EXECUTED_CORRECTED_SOURCE`
`BROKER_SID_NATIVE=NOT_ATTESTED`
`PIPE_DACL_NATIVE=NOT_EXECUTED`
`WORKER_DENIED_OPEN=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`
`P01=OPEN`, `P02=NOT_OPENED`.
