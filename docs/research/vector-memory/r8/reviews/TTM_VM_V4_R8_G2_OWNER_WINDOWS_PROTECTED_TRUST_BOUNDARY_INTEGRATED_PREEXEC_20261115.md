# TTM VM V4 R8 G2 — Owner-Windows protected trust boundary integrated preexec

**Operation** `TTM_VM_V4_R8_G2_OWNER_WINDOWS_PROTECTED_TRUST_BOUNDARY_INTEGRATED_PREEXEC_SINGLE_GATE`  
**Date** 2026-11-15 (Asia/Bangkok)  
**Role** Implementation Agent — not independent reviewer  
**Adjudication** `G2_HOLD · HOLD_INTEGRATED`  
**No R8/G3 execution. No real G_pre key or commitment created.**

## 1. Exact inherited source and reviewer pins

- Frozen scientific source: `84d9d5c95e9962ccfe294852570e261b145fe403`; unchanged.
- Integrated production trust-boundary source candidate: `9448ade9f3d5ffa8361d62485a68e49701c55c13`.
- Existing separate independent review of earlier candidate: `94b377ce6c0d6aa9e1d08ae4ff628c215449be1f`.
- Existing 57/57 Windows 3.12.10 GitHub Actions source-only fixture QA: [run 43714211130](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43714211130).
- Retention amendment `b1231faef1b2a4166016ee78a9de6617800efeff`: `PROPOSED_NOT_EFFECTIVE`; owner backup waiver only for R8-D exploratory; `RECOVERY_NOT_VERIFIED`.

## 2. Trusted Windows route readback — not an execution permit

- RemoteMCP V2 canonical Primary linked account; `machine-1` reports **ONLINE**, signed heartbeat fresh, expected existing identity/fingerprint, root on non-OS D: research drive.
- `authoritative_active_node_jobs=0`, `capacity_resolved=true`, `capacity_reconciliation_complete=true`, `authoritative_unresolved_node_jobs=0`.
- However `research_adapter_enabled=false`, `new_job_admission_allowed=false`, and `science_job_dispatch_gate.reason=RESEARCH_ADAPTER_DISABLED`.
- Consequently **no managed task or routed node command** was created. This is a control-plane execution blocker, not a failed protected-source or DPAPI verification. It is not repaired through gateway-local compatibility execution, re-pairing, node restart, project rebinding, or use of maintenance recipes for research.
- Owner Windows protected custody preexec: `BLOCKED_ON_REMOTE_EXECUTION_ADMISSION`. Local Windows protected source SHA-256 readback and real-version scoped runtime import in this operation: `NOT_EXECUTED`.

## 3. GitHub source-only PowerShell 5.1 preexec packet

[Preexec PowerShell script](https://github.com/minhtri22/TokenToModel-Lab/blob/3bf15b8f3fde05f49d10b382906602d14ba5e14b/docs/research/vector-memory/r8/preexec/Invoke-TTM-VM-R8-G2-OwnerWindows-Integrated-Preexec-PS51.ps1)

- Pinned source Git commit: `3bf15b8f3fde05f49d10b382906602d14ba5e14b`.
- Git blob SHA-1: `7ee3aaef058e9b8d705a00e1e9a0382d8b3d8773`.
- SHA-256 of exact script bytes: `f69a9cd4595172e901686d0e6395e0b5a071c3815f761ea025dc1e340ba7978d`.
- Windows PowerShell 5.1 syntax/static contract is checked in [GitHub Actions workflow](https://github.com/minhtri22/TokenToModel-Lab/blob/3bf15b8f3fde05f49d10b382906602d14ba5e14b/.github/workflows/ttm-vm-r8-g2-owner-windows-preexec-staticqa.yml).
- The script reads five protected source hashes from a *caller-pinned* existing private directory when provided, checks an explicitly selected Python 3.12.10 and package pins when provided, tests harmless in-memory DPAPI CurrentUser protect/unprotect, and verifies the public GitHub prerelease by real `gh release verify` and `gh release verify-asset`.
- If an exact `TrustedGhSha256` is not provided, the GitHub CLI executable hash is recorded but classified `NOT_ATTESTED`; passing a signed release check is not the same as attesting the exact deployed CLI binary.
- It writes one sanitized receipt to the **already-existing private custody receipts directory** with no overwrite, and leaves its public download scratch for policy-conformant cleanup. No key, gold, private fold, blueprint or private receipt is uploaded.
- It does **not** call `WindowsDPAPIKeyReader.read_key`, generate a real HMAC key, compute real G_pre allocation or invoke `ProductionBoundaryCandidate.dispatch` or G3. Missing protected source/runtime arguments result in `NOT_EXECUTED`, not PASS.

### Scope-locked hosted Windows evidence

[GitHub Actions run 43715605806](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43715605806), head `3bf15b8f3fde05f49d10b382906602d14ba5e14b`, completed/success:

| Hosted Windows step | Actual observation |
| --- | --- |
| PS5.1 AST parser | `PS51_PREEXEC_PARSE=PASS` |
| Source-only safety contract | `PS51_SAFE_STATIC_CONTRACT=PASS` |
| In-memory DPAPI CurrentUser harmless sentinel | `PASS_SCOPED_SAME_PROFILE_ONLY` |
| GitHub public immutable release asset readback + signature | `PASS_SCOPED_GITHUB_SIGNED_PUBLIC_SENTINEL` |
| Protected source 5/5 on owner Windows | `NOT_EXECUTED_SOURCE_ROOT_NOT_PINNED` |
| Exact owner Python 3.12 scoped runtime | `NOT_EXECUTED_PYTHON_EXE_NOT_PINNED` |
| Owner Windows custody | `NOT_EXECUTED` |
| Real G_pre HMAC / G3 | `NOT_EXECUTED` |

Prior hosted run 43715283272 failed due an erroneous static test field name; run 43715505996 correctly exercised GitHub signing but failed to load the DPAPI assembly. Both failures were preserved and fixed prospectively; no historical results were rewritten.

GitHub itself also returned immutable sentinel metadata for [existing prerelease](https://github.com/minhtri22/TokenToModel-Lab/releases/tag/ttm-vm-v4-r8-g2-commitment-sentinel-20261115): tag `ttm-vm-v4-r8-g2-commitment-sentinel-20261115`, `immutable=true`, published `2026-11-15T08:16:24Z`, asset digest `sha256:f589347fc615f73826104a0121fd46e842ea210414df8c26f75c0c13c2ffc54f`.

## 4. Honest integrated disposition

| Requirement | State |
| --- | --- |
| Frozen G0 source and existing local runtime/custody | Preserved prior `PASS_SCOPED`, not rerun in this operation |
| Hosted Windows PS5.1 and public sentinel smoke | `PASS_SCOPED` |
| Actual owner-protected 5 source hashes and import | `NOT_EXECUTED_REMOTE_JOB_ADMISSION_DISABLED` |
| Actual owner DPAPI/custodian HMAC V2 and lock | `NOT_EXECUTED` |
| Actual signed G_pre release and independent acceptance | `NOT_CREATED` / `HOLD` |
| Production mandatory launcher / real G3 path | `NOT_ATTESTED` |
| One-shot anti-rollback after remote release deletion | `NOT_PROVEN` |
| Distinct retention amendment review | `HOLD` |
| Integrated G2 | **`G2_HOLD · HOLD_INTEGRATED`** |

No source change to the frozen scientific implementation; no merge, new owner phase, GPU science, R8 cases, HMAC key or real G_pre commitment. The next evidence dependency is one readback of this exact PowerShell packet in existing owner Windows custody through a policy-compliant execution route or explicitly user-initiated local one-shot. No additional cloud, backup device, or micro-permits are required.

**The hosted Windows result cannot be reclassified as protected owner-Windows admission.**
