# P01 L1 — Native Broker V2 SCM binary switch gate (2026-11-06)

## Confirmed predecessor

User-run receipt `L1_BROKER_V2_COMPILE_20261106T153011358Z_0d55b78e` was verified against GitHub commit `82ad048e899c33bfff576d12eda706d3b00aa8a4`. Both V2 binaries compiled natively on Windows; neither binary was activated. The installed SCM service remains the stopped, manual-start `TTMP01Broker` service pointing to V1.

Pinned artifacts:
- V1 executable `TTMP01Broker.fixed.exe`: SHA-256 `56a780db6aa61fdd556540da340a3be223df2e41e1a7295bb33d05628dbf87ef`
- V2 executable `TTMP01Broker.attestationV2.exe`: SHA-256 `a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a`
- V2 C# source `BrokerAttestationServiceV2.cs`: SHA-256 `42ef0c0046d9b90ec0584211010341e7a04b93ea9541cb36ada66fdc2d830fae`
- V2 native probe DLL `TTMWorkerNativeProbeV2.dll`: SHA-256 `ea44cc5fca81e7f1e692726502dea0ad97ab543bc86f2abef52a25e1ffa96eb6`

## Approved narrow scope

`qa/p01/windows/Switch-TTM-P01-L1-SCM-ToBrokerV2-PS51.ps1` is a one-shot SCM **configuration only** step.

The script requires all of:
1. Exact pinned original P01 worktree HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, branch and origin, and no reparse ancestors.
2. SHA-256 matching all four pinned source/EXE/probe artifacts; worker account with exact SID; pinned service SID; existing credential and ledger presence with no credential content read.
3. Protected staging, binary and evidence directory ACLs containing the intended service SID, checked read-only.
4. Installed `TTMP01Broker` exists, **STOPPED**, configured as manual LocalService with unrestricted service SID and its original V1 executable path.
5. Elevated Windows PowerShell 5.1 and explicit `-Apply`.

Only then it creates a **new local TTM project-scoped durable marker** using `FileMode.CreateNew` to forbid replay. It invokes **only** `sc.exe config TTMP01Broker binPath= <V2 EXE>` with discrete argv; records the native exit and raw output; reads back `sc.exe qc` and `Win32_Service` configuration and verifies the EXE SHA-256. Does **not** start the service or edit service SID/start mode, worker, ACL, credential, ledger, scientific evidence, P00 or F0.

After any failure or partial switch: **no automatic rollback, no second -Apply, no deletion of marker.** Preserve state for independent adjudication. The GitHub readback uses an exact new run-specific QA receipt path and SHA-256. If GitHub receipt upload fails, the original local receipt remains.

## Static source audit

- Script Git blob: `f8b83c3ebd4f22bbf16eaca2fce29ad02ed09063`
- Static source-contract checks: **24/24 present**, recorded in `artifacts/qa/p01/L1_BROKER_V2_SCM_SWITCH_STATIC_PREFLIGHT_20261106.json`.
- This does NOT prove PowerShell runtime syntax, native SCM switch, broker startup, actual service SID in the token, DACL enforcement, pipe peer SID or real worker denied-open. All remain separate native gates.

## Verdict

`V2_NATIVE_COMPILE=PASS`
`V2_SCM_BINARY_SWITCH=NOT_EXECUTED`
`V2_SERVICE_START=NOT_EXECUTED`
`NATIVE_SECURITY=NOT_QUALIFIED`
`W01_W12=NOT_EXECUTED`
`GROUPED_L1_QA=NOT_AUTHORIZED`
`P01=OPEN`, `P02=NOT_OPENED`

Keep original HEAD, P00, ten F0 results, governance and P00–P12 roadmap. Engineering QA only; do not append to scientific `lineage.md`.
