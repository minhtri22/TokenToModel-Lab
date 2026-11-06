# TTM P01 L1 — Broker V2 + worker V3 native one-shot test gate

Date: 2026-11-06. Engineering QA; **not a science result**.

## Immutable predecessors
- Repository: `https://github.com/minhtri22/TokenToModel-Lab`.
- QA branch: `audit/p01-l1-native-security-critical-fix-20261106`.
- Original P01 worktree: `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105`, HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- Windows SCM V2 switch: committed receipt `98f96dfd002fde146b0922501510b3229ad63bc9`; verdict `PASS_SCM_SWITCH_V2_NOT_STARTED_SECURITY_NOT_QUALIFIED`.
- SCM switch one-shot marker: `L1_SCM_V2_SWITCH_ATTEMPT_20261106.lock`, SHA-256 `29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1`.
- Windows V3 compile receipt: `L1_WORKER_V3_COMPILE_20261106T160319388Z_3fa6cd41`, commit `ac9e09112b087bae122da82279de7bcd4657b906`; verdict `PASS_COMPILE_ONLY_V3_NOT_EXECUTED`.

Exact runtime hashes:
- `TTMP01Broker.attestationV2.exe` SHA256 `a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a`.
- `BrokerAttestationServiceV2.cs` SHA256 `42ef0c0046d9b90ec0584211010341e7a04b93ea9541cb36ada66fdc2d830fae`.
- `TTMWorkerNativeProbeV3.dll` SHA256 `bd08ae55ad7eca5eb29e237467166f58f7c9fd7d6dc9ef6f4de71cbb1ba33d9d`.
- `TTMWorkerNativeProbeV3.cs` SHA256 `00964b57c60d80e4628d51cfe840f249edcc9edb16c7d44787081b74da03cfa0`.

## Final next script (not previously executed)
`qa/p01/windows/Invoke-TTM-P01-L1-BrokerV2-WorkerV3-NativeOneShot-V2-PS51.ps1`.

Pinned source Git blob `1f729ca7035939bc8fe995a27bfefae013dc88b5`. Static source inspection 34/34 guard predicates present; **not independent native QA**. Previous native launcher candidate `Invoke-TTM-P01-L1-BrokerV2-NativeSecurityOneShot-PS51.ps1` has an explicit dispatch BLOCK; do not invoke it. The intermediate worker-V3 launcher without worker-token DACL readback is also superseded.

Strict one-shot execution requires elevated Windows PowerShell 5.1 plus explicit `-Execute`, exact source/executable/marker/worker account SID pins, stopped manual `TTMP01Broker` SCM V2 LocalService and unrestricted service SID, no existing **new native-test** marker. The script checks Win32 marker absence via GetFileAttributesW with `ERROR_FILE_NOT_FOUND=2` and creates the marker atomically only once before `Start-Service`.

Native scope:
1. Start the already-registered V2 service once, report a real process PID and verify its token user SID `S-1-5-19` plus derived service SID group.
2. Independently read the **named-pipe object's DACL** under the existing local worker's impersonated token with Win32 `GetFileSecurityW`. An elevated Administrator token is deliberately not used because the pipe's secure DACL may not give it READ_CONTROL. Parse a `.NET RawSecurityDescriptor`, require protected DACL and exactly the three expected allow SIDs: SYSTEM, broker service, and worker; reject worker CreateNewInstance, WRITE_DAC and WRITE_OWNER.
3. Run the exact compiled worker V3 DLL under a real logon/impersonated worker token; test separate denied-open rights on preexisting evidence directory, denied GENERIC_WRITE open on existing ledger, and a named-pipe `AUTH_PROBE` handshake. The client uses exact `PipeAccessRights.ReadWrite`, excluding `CreateNewInstance`.
4. Stop service in `finally` if start was attempted; verify `Stopped`. If stop cannot be confirmed, override any success with `STOP_UNVERIFIED_MANUAL_INTERVENTION_REQUIRED`.
5. Persist an append-only JSON receipt to the existing TTM QA receipts directory, push to the QA branch and verify SHA-256 readback. No passwords or raw SDDL are uploaded, only redacted verdicts and hashes.

NO SCM config changes, worker/account provisioning, stage ACL changes, ledger writes, cleanup of markers, F0 reruns, W01–W12, L1 grouped QA or P02. Do NOT run again after a BLOCK, partial execution or stop failure. Observe and independently adjudicate current system state first.

## Decision boundary
Even a full PASS means **narrow native token + DACL + denied-open + SID handshake attestation only**. It does NOT establish a production broker writer, full job isolation or W01–W12 security qualification; `P01=OPEN` and `L1_GROUPED_QA=NOT_AUTHORIZED` remain.

Current gate:
`SCM_V2_SWITCH=PASS`;
`WORKER_V3_COMPILE=PASS`;
`NATIVE_TEST_RUN=NOT_EXECUTED`;
`NATIVE_SECURITY_QUALIFIED=NO`;
`W01_W12=NOT_EXECUTED`;
`L1_GROUPED_QA=NOT_AUTHORIZED`;
`P01=OPEN`;
`P02=NOT_OPENED`.

Keep P00, the ten frozen F0 results, exact original P01 HEAD and approved P00–P12 roadmap unchanged. Never append engineering QA to scientific `lineage.md`.
