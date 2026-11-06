# P01 L1 — One-shot resume from verified Windows executable

**Engineering runbook (2026-11-06).** Source/audit prepared, **Windows provision not executed by ChatGPT**.

## Provenance
- Repository: https://github.com/minhtri22/TokenToModel-Lab
- Successor branch: `audit/p01-l1-native-security-critical-fix-20261106`.
- Original local P01 HEAD: `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`; preserve it, original worktree and ten locked F0 results.
- Windows compile PASS receipt commit: `d05790f9130c9b1dc96a90f14cacdbfc63404a09`.
- Verified Windows executable SHA-256: `56a780db6aa61fdd556540da340a3be223df2e41e1a7295bb33d05628dbf87ef`.
- Verified C# source SHA-256: `8916fe262bf27d9176a648dd625b5fbb602f87a2cf69967fe9339def6d3561e4`.
- Source contract: `artifacts/qa/p01/L1_VERIFIED_BINARY_PROVISION_RESUME_STATIC_GATE_20261106.json` (22 checks present; **STATIC_ONLY**).

## Script
`qa/p01/windows/Resume-TTM-P01-L1-FromVerifiedBinary-PS51.ps1`.

The script defaults to read-only preflight and requires explicit `-Apply` for creation. It is **not** the previous provisioning `-Apply` script. It refuses unexpected existing service, account, credential, ledger, missing verified files, or reparse ancestors. On unexpected state it writes BLOCK evidence rather than resetting or cleaning state.

On an eligible fresh target:
1. Requires elevated PowerShell and exact prior worktree, HEAD, branch, origin, and source/executable hashes.
2. Creates a non-admin `TTMP01Worker` local account with random password. Saves password only as user-scoped DPAPI under the TTM project directory with protected ACL. No secret is uploaded to GitHub.
3. Applies protected ACL to the pre-existing staging parent, broker executable directory, evidence directory (worker read/traverse only) and ledger/credential file (no worker access).
4. Registers a **manual/demand-start** `TTMP01Broker` Windows LocalService service with unrestricted service SID, exact precompiled EXE. Its logic refuses file-write requests and only supports an authentication diagnostic.
5. Tries to start it and independently probes a real worker logon token: `OPEN_EXISTING` denied-write against the evidence directory and named-pipe peer SID handshake; separately attempts native DACL readback through pinned inspector. A narrow success does **not** prove job/process confinement.
6. Attempts to stop only a service started by the invocation. Never deletes service/account/ledger or cleans staging after partial failure.
7. Records terminal PASS/BLOCK/FAIL with source hashes; creates a new evidence JSON under TTM only, commits it to the successor branch with `gh api`, reads it back and verifies SHA-256.

## Operator safety constraints
- Running `-Apply` **changes a Windows local account, the Windows Service Control Manager and ACLs**. Elevated rights are required.
- This is a **one-shot** manual action. After any incomplete or BLOCK result, **do not rerun**: preserve state, analyze the receipt, and design a targeted, independently reviewed recovery.
- If native DACL inspector cannot open pipe, returns BLOCK or no peer token can connect, record the failure; do not substitute synthetic PASS.
- No external worktree deletion, no modification to P00, main, lineage, original P01 HEAD or F0 results.
- `W01_W12=NOT_EXECUTED`, `L1_GROUPED_QA=NOT_AUTHORIZED`. Even PASS for service/ACL probes would not make the broker a production data-writing service. The service has no full payload authorization/HMAC writer integrated.

## Adjudication gates
`NATIVE_SERVICE_PROVISION=AWAITING_OPERATOR_RUN`
`NATIVE_ACL_PIPE_PROBES=AWAITING_OPERATOR_RUN`
`W01_W12=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`
`P01=OPEN`
`P02=NOT_OPENED`.
