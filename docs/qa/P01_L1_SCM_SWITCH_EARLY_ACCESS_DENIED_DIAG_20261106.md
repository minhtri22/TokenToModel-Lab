# TTM P01 L1 — Early ACCESS_DENIED on broker V2 SCM switch (2026-11-06)

## Grounded Windows evidence

User reported `TTM_SWITCH_SCRIPT_PIN=PASS`, then `TTM_SWITCH_BLOCK=Access is denied` in run `L1_BROKER_V2_SCM_SWITCH_20261106T154152987Z_88979b11`. Exact receipt was verified from GitHub commit `14b51937f861f26f05d53b38f0808522e462e5d9`; Windows-reported receipt SHA-256: `14038c32f7915b33a1d6d3e89eb3d197bd2a7ce97c63718a1cbb42fc55557849`.

The receipt contains:
- `checks={}`;
- `sc_config_exit=null`, `sc_config_output=[]`, `sc_qc_before=[]`, `sc_qc_after=[]`;
- `scm_binpath_changed=false`;
- `service_started=false`;
- `worker_account_changed=false`, `ACL_changed=false`.

The switch source first checks pinned worktree existence and then invokes `NoReparse` on the worktree, staging, binaries, SID config, DPAPI credential, ledger and one-shot marker. That function uses `Test-Path` plus `Get-Item -Force` before the first PASS check. **Because no check was written, the exception is strongly consistent with a protected-path metadata access denial before git/SCM.** This is a source-derived hypothesis, **not a proven exact failing path**. The script's Administrator gate occurs much later, so lack of elevation is a material possibility. Do not assume it was the cause.

No evidence indicates the one-shot marker was created or `sc.exe config` ran during this invocation. Marker absence and current SCM binPath must nevertheless be independently rechecked before any future switch. Do not delete a marker or replay the previous `-Apply` automatically.

## Read-only independent diagnosis

New source: `qa/p01/windows/Inspect-TTM-P01-L1-SwitchAccessDenied-PS51.ps1`.

- Captures current token's elevated Administrator membership **before** any protected-path reads.
- Traces the same path walk in source order, catching each path's `Get-Item` metadata exception and exact stopped-at path. Never opens credential or ledger **contents**.
- Classifies `Test-Path=false` as `ABSENT_OR_INACCESSIBLE`, never proof of marker absence.
- Reads only current `Win32_Service` state/config and original worktree git identity, with no service mutations, no changes to accounts, ACLs, or staging.
- Creates only a unique, append-only QA receipt under TTM's already-approved receipts directory, pushes it to the successor GitHub branch and independently checks downloaded content SHA-256.
- Reports `TTM_ACCESS_DIAG_ADMIN_ELEVATED`, `TTM_ACCESS_DIAG_PATH_*`, `TTM_ACCESS_DIAG_FIRST_ERROR_PATH` (if any), `TTM_ACCESS_DIAG_ONE_SHOT_REPLAY`, `TTM_ACCESS_DIAG_SCM_PRESENT`, `TTM_ACCESS_DIAG_GITHUB_COMMIT`, `TTM_ACCESS_DIAG_GITHUB_READBACK`.

Script git blob at static audit: `abdaba86dbfa73cf3016e32ffc833ab67c8c48da`.
Static checks: 16/16 scope predicates present; **no Windows execution has occurred on this diagnostic**.

## Gates

`SCM_SWITCH_ACCESS_ERROR=BLOCK_UNRESOLVED`
`ROOT_CAUSE=UNCONFIRMED`
`SCM_V2_BINPATH_SWITCH=NOT_ATTESTED`
`SERVICE_START=NOT_EXECUTED`
`WORKER_DENIED_OPEN=NOT_EXECUTED`
`PIPE_DACL=NOT_EXECUTED`
`W01_W12=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`
`P01=OPEN`
`P02=NOT_OPENED`

Preserve P00, original HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, 10 F0 results, project-local scope and P00–P12 roadmap. Engineering QA only; no scientific lineage entry. Do not execute existing switch `-Apply` again until exact denied path and SCM state are adjudicated.
