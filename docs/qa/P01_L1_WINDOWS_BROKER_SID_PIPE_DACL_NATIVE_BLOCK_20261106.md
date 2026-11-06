# TTM P01 L1 — Windows service SID, pipe DACL and W01–W12 dispatch boundary

**Date:** 2026-11-06. **Verdict:** BLOCK_NOT_QUALIFIED / W01–W12 NOT_EXECUTED.

## Exact baseline
- Original local HEAD: `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`. No operation moved that HEAD.
- Evidence branch: `audit/p01-l1-native-security-critical-fix-20261106`; no P00 change, no F0 rerun, P02 closed.
- Remote command probe `git --version` returned `managed mode requires task_job_submit`. A qualified TTM task ID and leased command dispatch were **not** available; no native job was submitted and no fallback unguarded job was launched.
- The user's Windows service configuration and pipe DACL have **not** been read by this session, and must not be inferred from source.

## Newly implemented source-level controls
- `qa/p01/native_pipe_acl_policy_v1.py` proposes a **protected** DACL permitting SYSTEM, administrators, the dedicated service SID, and the worker SID with individual client rights `0x0012019B` (excluding `FILE_CREATE_PIPE_INSTANCE` bit `0x4`). It rejects built-in/well-known broad worker identities and blocks an unspecified/default pipe DACL. This proposal is **not applied** by existing `trusted_broker_service_v1.py`.
- `qa/p01/test_native_pipe_acl_policy_v1.py` contains ten source-only negative cases, not Win32 W01–W12.
- `qa/p01/inspect_pipe_dacl_win32_v1.py` is a read-only native inspector for a pre-existing pipe DACL. It emits a redacted receipt, checks protected DACL and identities, and refuses if absent; no pipe is created.
- `qa/p01/native_restricted_token_acl_probe_v1.py` creates a restricted **test token from the current user** and only requests OPEN_EXISTING directory write access to verify expected `ERROR_ACCESS_DENIED`. This does **not** prove a dedicated worker process or global filesystem confinement.

## Critical unresolved gap
The checked-in `qa/p01/trusted_broker_service_v1.py` currently uses Python `multiprocessing.connection.Listener(...family='AF_PIPE', authkey=...)`, with no explicit `CreateNamedPipeW` SECURITY_ATTRIBUTES / SDDL passed to Windows. HMAC channel authentication alone is **not** OS-level pipe access control. Native peer SID/job-bound attestation, SCM-provisioned service identity, explicit pipe DACL, service/worker filesystem ACLs, and atomic writer W11/W12 qualification remain absent.

Official Microsoft documentation:
- https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights
- https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createnamedpipew
- https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo
- https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getnamedpipeclientprocessid

## W01–W12 native qualification
W01 token fail; W02 least-privilege effective access; W03 suspended CreateProcessAsUser failure; W04 4GiB Job limit queryback; W05 Job assignment error; W06 membership error; W07 child breakaway; W08 >4GiB commit termination; W09 1800-second timeout; W10 outside-file write denied; W11 reparse/ADS and partial write; W12 concurrent/duplicate/aggregate quota — **ALL NOT_EXECUTED** in this session. Memory stress and write-fault tests must not be launched until the actual security boundary is attested. Do not classify redacted read-only probes as W01–W12 PASS.

## Local Windows fallback and immutable evidence
A PS5.1 fallback script `Run-TTM-P01-L1-Windows-Native-Security-QA.ps1` is supplied as a conversation artifact with SHA-256 `e488e265ae8ec8badb8160c3afcde2676a8f0255e6a2138e09ec3cbd86bc11e0`. It checks exact local repo identity, downloads source at a fixed GitHub commit with five historical SHA-256 pins, performs read-only service/SID/root-ACL inspection and optionally Win32 no-write probes, then writes a receipt **only under the TTM project's own worktrees directory** and attempts a new GitHub contents-API commit using the user's authenticated `gh` CLI. It does **not** provision the service, change ACLs, or run native W01–W12. Expected blocked exit code with successful upload: 3. If GitHub publish fails: exit 5 and preserve local evidence. Never claim the receipt uploaded without an actual returned commit and readback.

## Adjudication
`SERVICE_SID_NATIVE=NOT_ATTESTED`
`PIPE_DACL_NATIVE=NOT_ATTESTED`
`WORKER_OS_CONFINEMENT=NOT_QUALIFIED`
`W01_W12_NATIVE=NOT_EXECUTED`
`NATIVE_SECURITY_GATE=BLOCK`
`L1_GROUPED_QA_PERMIT=NOT_GRANTED`
`P01_CLOSURE=PENDING`
`P02=NOT_OPENED`

This is infrastructure/security QA evidence, not a scientific result. Keep `lineage.md` unchanged.
