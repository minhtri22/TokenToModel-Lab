# TTM P01 L1 — Win32 marker-attested SCM V2 binary switch successor

Date: 2026-11-06. This is an **engineering QA** document, not science.

## Last independently observed state
User Windows diagnostic run `L1_SCM_SWITCH_EARLY_DENIED_DIAG_20261106T154855810Z_0acfaf95`, GitHub evidence commit `b1ab271d18cc310c590602d24299a6e906f04cc5`, reported:
- Administrator elevated = true **during diagnosis**; all ten TTM paths had readable metadata.
- SCM `TTMP01Broker` stopped/manual, LocalService, still configured to `TTMP01Broker.fixed.exe` (V1).
- Original local HEAD/branch/origin matched pins.
- One-shot marker classified `ABSENT_OR_INACCESSIBLE`. This is **not** proof of absence.
- Prior switch run `14b51937f861f26f05d53b38f0808522e462e5d9` stopped with `Access is denied` before any script check or native SCM command was logged, `scm_binpath_changed=false`. The specific failed operation and privilege of that earlier run are not proven.

## Successor script
`qa/p01/windows/Switch-TTM-P01-L1-SCM-ToBrokerV2-V2-PS51.ps1`.

Pinned Git blob `84b7af9ae236515a181111ff3c2dbfc50069aadb`; new source commit `a71e2cde6eb75b7f07de448b26ff588d241dea40`. Static scan 19/19 guarded conditions present, not a Windows-native execution.

Differences from previous failed script:
1. Check elevated Administrator token **before any protected TTM path walk**. Return BLOCK before touching stage if not elevated.
2. After old-head, hash, worker, service identity/ACL, SCM and credential-presence checks, use Win32 `GetFileAttributesW` on exact fixed one-shot marker. If attributes returned, existing marker blocks. If `INVALID_FILE_ATTRIBUTES`, require `GetLastWin32Error()==2` (`ERROR_FILE_NOT_FOUND`), otherwise fail closed, including access denied (5), path not found (3), sharing or other errors. The staging parent is separately required to exist and be readable.
3. Maintain second independent atomic `FileMode.CreateNew` check when actually creating marker before `sc.exe config`.
4. The only SCM mutation is `sc.exe config TTMP01Broker binPath= <exact pinned V2 EXE>` with separate argv elements. No service start. Read back via `sc.exe qc` and `Win32_Service`; verify new executable checksum and manual, stopped, LocalService conditions.
5. Always create a separate unique TTM QA receipt and publish to GitHub successor branch; verify SHA-256 downloaded readback. Previous receipts are never overwritten.

## Windows operator path

Run an independent Git blob verified local copy of the **new V2 successor script**, not the previous `Switch-TTM-P01-L1-SCM-ToBrokerV2-V1.ps1`; elevated Windows PowerShell 5.1 required. Execute **once**. If any BLOCK/partial result, keep marker and SCM state, do not retry or clean without a new independent adjudication.

The one-shot action is permitted only if **all** current run guardrails pass. It changes the Windows Service Control Manager binPath of an existing service, and must therefore be treated as a machine configuration action, not a read-only audit.

## Gates

`SCM_V2_SWITCH_SUCCESSOR_SOURCE=STATIC_PASS`
`NATIVE_MARKER_ABSENCE=NOT_EXECUTED`
`SCM_V2_BINPATH_SWITCH=NOT_EXECUTED`
`V2_SERVICE_START=NOT_EXECUTED`
`WORKER_REAL_DENIED_OPEN=NOT_EXECUTED`
`PIPE_DACL_NATIVE=NOT_EXECUTED`
`W01_W12=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`
`P01=OPEN`
`P02=NOT_OPENED`.

Preserve P00, original local HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, ten F0 results, and P00–P12 sequence.
