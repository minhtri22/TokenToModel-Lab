# TTM P01 L1 — Minimal native smoke: static design / no execution

Date: 2026-11-07. This is an engineering design, not science or a runtime PASS.

## Frozen input

- Repo `minhtri22/TokenToModel-Lab`, QA-only branch `audit/p01-l1-native-security-critical-fix-20261106`.
- Original scientific HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`; preserve P00, all ten F0 outcomes, all historical PASS/FAIL evidence, markers, `lineage.md`, and phase order P00–P12.
- One-shot compile receipt commit `a8b7e762ba9110c3e9246fb6570a2d0246aa50d4`, SHA-256 `e20690db0ea91b3af4ba3f9b311e1f01fb8574f26273201b3b55499427002bcf`.
- Candidate Broker V3 EXE: `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\_ttm_p01_l1_service_provision_20261106\broker_service\TTMP01Broker.attestationV3.exe`; size `10240`, SHA-256 `0751f89fee519367580e89b2e99b5347ee49c6b4c15f67ebf7d43706ac78ec5c`.
- Candidate Worker V4 DLL: sibling `TTMWorkerNativeProbeV4.dll`; size `11776`, SHA-256 `b36b5868b09b4da7bdb7198f3acd86923aba57f29a993fc8188bcb1cdc729f36`.
- Compile marker `L1_V3_V4_EXACT_SOURCE_COMPILE_ATTEMPT_20261107.lock`, SHA-256 `fca9ee976878674ccdcc60c8dc1e621a01b35a472fb7e9e80f79997ef2fb7ef7`, consumed; never recompile from this marker.
- User's Windows PowerShell readback reports exact hashes for all three and `TTMP01Broker=Stopped, PID0`. GitHub receipt agrees. The adjudicator did not directly open the machine; these are observed console results, not a persistent SCM assertion.

## Scope and STOP conditions

No executable smoke is authorized by this document. **Do not** install binaries, change SCM `binPath`, start/stop service, impersonate a worker, alter local ACL/users, change SQLite, open W01–W12 or grouped L1 QA. Do not execute V2 recovery or reuse old run markers. No change to the original scientific worktree.

Design source/fixture QA must precede any native test; each native test family needs an independent exact-source permit and marker. Run a low-risk process-local I/O cancellation smoke **before** a separate SCM-changing native service trial.

Preflight must fail closed if any hash/size, original HEAD, 4 historical markers, V4 source QA marker, compiler marker, QA receipt, service identity, service SID, worker SID, project-local path, resource check, or release state differs. Protect against symlinks/reparse points and preexisting candidate output files. Current service `TTMP01Broker` must still be Manual / LocalService / V2 binary / Stopped PID0 when tested.

## Minimal staged tests — designed only

| ID | Category | Intended test | Required PASS / stopping rule |
|---|---|---|---|
| S0 | Read-only snapshot | Rehash both binaries and consumed marker, confirm old service config, exact HEAD, evidence and service PID | All pins match, SCM still Stopped/PID0. No write or service command |
| S1 | Isolated I/O smoke, no SCM | New disposable project-local *test pipe* under process-local host, asynchronous accept/read, request cancellation while client absent and silent, completion-aware cleanup | Bounded completion; no stranded host process; never touch `TTMP01Broker`, its named pipe, service binary, ledger or real worker account |
| S2 | Service start/stop, separate permit | Exact V3 SCM binary switch only after S1 PASS, then 1 bounded idle start/stop | Must be `Running` with exact PID and expected binary, then ordinary SCM stop returns `Stopped/PID0` without force/kill. Failure blocks S3 and W01–W12 |
| S3 | Stalled-client stop, separate permit | Worker connects but sends no payload, issue ordinary SCM stop while blocked in overlapped read | Thread shutdown and SCM Stopped/PID0 within bound; no forced kill, no extra service starts |
| S4 | Worker rights / DACL, separate permit | Authenticated pinned worker connected handle `GetSecurityInfo` with `SE_FILE_OBJECT=1`, `DACL_SECURITY_INFORMATION=4`; check only exact three allow ACEs and masks; seven separately denied directory rights, existing ledger write denied; worker SID handshake `AUTH_PROBE` | All exact checks PASS. Null DACL, extra/wrong ACE, forbidden rights, timeouts or mismatched SID always BLOCK. Never publish password/token/raw DACL |
| S5 | Wrong identity / unsupported operation | Negative peer SID and unknown operation probes | No success response, no file/ledger writes, broker remains bounded and recoverable |

Only execute minimum needed S2–S5; do not label any of them equivalent to the original W01–W12 suite. A service start must be followed by a separately verified stop receipt, and a failure can leave service state unresolved: never silently claim `Stopped` or attempt automatic forced recovery. A fresh recovery decision is required if native stop fails.

## Potential defects / important independent review

1. **Worker warning `CS0162` (line 179):** a compile-time constant mask comparison leaves `BLOCK_CLIENT_RIGHTS_MASK` unreachable. This is not a runtime proof of least privilege. Dynamic handle-DACL verification must test real ACE masks and denied writes independently. Preserve the warning in evidence; do not recompile solely to remove it.
2. **Broker cancellation:** `CancelIoEx` requests cancellation; actual overlapped request completion can race or fail. `OnStop` thread join is 8 seconds. Tests must separately observe final thread/service state, exact PID and stop result; `CancelIoEx` success alone is insufficient. Microsoft documents this behavior: https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex
3. **Named pipe DACL:** use the actual connected handle, not a second name-based open that previously returned Windows 231. Security descriptor is protected and permits SYSTEM, exact service SID and exact worker SID only; `FILE_GENERIC_WRITE` includes create-instance semantics and must not be substituted for granular worker rights. Reference: https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights
4. **Credential hygiene:** do not write worker password in command args, PS history, JSON, GitHub, environment dumps or logs. Separate credential-provision review is required before S4.
5. **Worker V4 binary is a DLL with a static `Run(...)` entrypoint, not a standalone executable.** An isolated test host/launcher will require its own source lock and static QA; this is not permission to build or run one now.

## Next action and evidence requirements

`TTM_P01_L1_V3V4_MINIMAL_NATIVE_SMOKE_S1_ISOLATED_CANCELLATION_HARNESS_STATIC_IMPLEMENTATION_AND_INDEPENDENT_QA`.

Create source-only isolated smoke harness and independent negative fixtures. It must not import service configuration or start the production broker; no scientific seeds. Run static QA, source/receipt hash pins and PowerShell 5.1 native syntax check **before** deciding whether S1 may run. S2/S3/S4/S5 remain not authorized and require separate one-shot permits.

**Current formal status:** `BINARY_COMPILE=PASS`, `BINARY_SHA_READBACK=PASS_REPORTED_WINDOWS`, `S0=PASS_REPORTED_WINDOWS_ONLY`, `S1..S5=NOT_EXECUTED`, `NORMAL_STOP=NOT_REQUALIFIED`, `NATIVE_SECURITY=NOT_QUALIFIED`, `P01=OPEN`, `P02=NOT_OPENED`.
