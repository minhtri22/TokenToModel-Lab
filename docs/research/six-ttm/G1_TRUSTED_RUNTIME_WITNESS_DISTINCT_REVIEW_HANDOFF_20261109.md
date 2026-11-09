# HANDOFF — G1 trusted runtime, owner scope và witness: kiểm định tích hợp độc lập

**Ngày 09/11/2026 · trạng thái `REVIEW_PENDING / PRODUCTION_HARD_GATES=HOLD / G1_SCIENCE_LOCK=HOLD`**

## 1. Vai trò và provenance

Bạn là **Codex reviewer độc lập**, không phải người viết gói ứng viên. Có thể dùng subagents để kiểm toán công thức/phân quyền/Windows API, nhưng không tự nhận source QA của tác giả là independent PASS.

- Repo: `https://github.com/minhtri22/TokenToModel-Lab`.
- Local root: `D:\WORK\RESEARCH\TokenToModel-Lab`.
- Candidate branch: `implementation/ttm-six-g1-trusted-runtime-witness-20261109`.
- Frozen G1 v1c: `d5d0c5346a595557a76349f900d09be50bce289c`.
- Prior distinct v1c HOLD: `d478282e16a4728f064892564b949e671e13cdd2`, review branch `review/ttm-six-g1-v1c-codex-distinct-20261109`.
- Previous integrated synthetic candidate: `51636a3187ed9e22658b55de2c9a4060127ac30d`.
- T1 SHA256: `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; sealed G1 128/64/64 metadata SHA256: `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6`.
- Do not change research/main/review branches, PR #12, `lineage.md`, TTM-Small-4M checkpoint, sealed manifests, v1c source blobs, Qwen one-shots.

## 2. Exact source under this implementation branch (Git blobs)

| Path | Git blob |
|---|---|
| `scripts/research/six_ttm/g1_trusted_runtime_witness_candidate.py` | `f7db10a711c9f83d5e9c414ab2b183eed3313421` |
| `scripts/research/six_ttm/test_g1_trusted_runtime_witness_candidate.py` | `1849fa8c1f799018b7b4dc55d7c37a5ac61b91ff` |
| `scripts/research/six_ttm/g1_win32_job_object_watchdog_candidate.py` | `afd182da02cdc86b7b55063fafd8c5ab9e6a138c` |
| `scripts/research/six_ttm/Run-G1-TrustedRuntime-WindowsReadOnly-PS51.ps1` | `5dc3720eeee17503912da0919cfed65acd53ea16` |
| `docs/research/six-ttm/G1_OWNER_SCOPE_AND_METHODS_V1D_REVIEW_CANDIDATE_20261109.md` | `a470394aab9dd404fa885bd0190dac82ef40a694` |
| `docs/research/six-ttm/G1_TRUSTED_RUNTIME_WITNESS_QA_RECEIPT_20261109.json` | `a844c8d6f252b20f065f64d116a9ebd8fdc1c148` |

## 3. QA baseline: not independent review

Author's isolated Linux CPU test output: `PASS_G1_TRUSTED_BOUNDARY_SIMULATION_ONLY`, **45/45** checks. Covered: witness-before-TEST read, out-of-order state STOP, hardlink/symlink, controller-only DB rollback vs witness, witness-only deletion vs DB, outage during ack blocks TEST, orphan staging file STOP, worker root deletion cannot reset external state, synthetic CPU child forced kill. `OWNER_PUBLIC_KEY_SHA256=None`, `OWNER_SCIENCE_SCOPE_GRANTED=False`, science disabled. No real TinyStories/TEST, no model, no T4.

Independent reviewer must run **new** fixtures, not only replay the 45. Especially try both controller+witness coordinated rollback, user-controlled witness edits, forged ledger authority and controller/worker root ACL being same principal. If same actor can roll back both domains the candidate must remain HOLD.

## 4. Five integrated production trust components and one methods gate

**Gate A — Owner authority / trusted launcher:** Verify Ed25519 trust anchor administered by owner independent of worker, immutable executable hash/HEAD/manifest/reviewer/methods/split/run/workspace/expiry, verified before any data/GPU. Current synthetic controller intentionally cannot issue production permit; no key is provisioned. Do not create an owner key, password or permit in this review.

**Gate B — Trusted split broker:** True principal/SID/DACL separation must deny worker TRAIN/DEV read access to TEST even via alternate path/hardlink/junction/reparse. Merely rejecting `st_nlink>1` is insufficient proof of isolation, and a future hardlink creation may be possible. Require negative `AccessDenied` from a *different Windows token*, no real TEST read. Broker source staging must be separately approved by owner.

**Gate C — Trusted pack writer + transaction ledger:** Validate same-open-file hash of exact bytes parsed, source lineage, exclusive writer role, two-phase pack/receipt, orphan/crash consistency, namespace races, same-user path substitution and ledger/witness synchronization. Current SQLite + directory witness is a **simulation**.

**Gate D — One-shot monotonic external witness:** Must survive rollback of worker **and** controller, not merely worker or controller alone. A distinct credential/host or immutable service with signed monotonic ack is needed; same Windows account and an adjacent D: folder do not qualify. Failure before/after `TEST_EXTRACT_CONSUMED` must block TEST forever until owner adjudication; no silent retry.

**Gate E — OS watchdog:** Inspect `g1_win32_job_object_watchdog_candidate.py`: `CreateProcessW(CREATE_SUSPENDED)`, `AssignProcessToJobObject` before `ResumeThread`, kill-on-job-close, `TerminateJobObject` on timeout, no breakaway. Windows self-test is *harmless CPU process only*, NOT qualified until real Windows result. Require 3,600s/model and 7,200s total persisted budgets, T4 peak VRAM cap and independent supervisor/watchdog. Do not start model GPU science.

**Gate F — Methods:** Independently adjudicate v1a first-occurrence/dedup, v1b paired bootstrap with fixed whole-TEST denominator, v1c CKA conservative ties and v1d consolidated interpretation. Check exchangeability, TEST n=64 power limitation, A→P linearity vs B-direct, near-duplicates and permitted `INCONCLUSIVE`. A source-based review PASS is not owner permit.

All six gates are **one admission decision**, not micropermits. Gate-local PASS is distinct from production PASS.

## 5. Allowed Windows QA, project-scoped and no private data

Use an *isolated project-local worktree* or exact pinned source files under `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp`. Verify SHA with `git hash-object --no-filters` first. Do not modify current `main` checkout. Use Windows Python 3.12 local interpreter only for safe synthetic scripts.

1. Run `test_g1_trusted_runtime_witness_candidate.py` on Windows with a project-local scratch directory (script uses OS temp by default; reviewer should override `TMP/TEMP` to project-local `_tmp` to meet workspace boundary).
2. Run `Run-G1-TrustedRuntime-WindowsReadOnly-PS51.ps1`, print-only. It reads Git/ACL inventory but does not prove DENY. Do not create or edit users, SIDs, privileges or services without separate owner approval.
3. After inspecting the Win32 source, optionally execute `python g1_win32_job_object_watchdog_candidate.py --mode harmless-sleep-qa --sleep-seconds 3 --timeout-ms 150` and `--sleep-seconds 0 --timeout-ms 3000`. Both use a harmless child and do not touch existing OS processes. Capture exit code/child termination receipts.
4. Try new synthetic file-alias, crash, interleaved concurrent submissions, DB rollback, witness rollback and combined rollback. Mark `NOT_TESTED` where OS privilege, separate identities or external witness are not available.
5. Never apply `icacls /grant`, `/deny`, `/reset` or modify trusted roots in this **review-only** QA.

## 6. Required return and verdict

Produce a single reviewer artifact `G1_TRUSTED_RUNTIME_WITNESS_DISTINCT_QA_<DATE>.md` with original verified HEAD/Git blobs, command/exit/receipt for each runnable QA, actual OS principal/SID/ACL evidence when possible, all six gates `PASS/FAIL/NOT_TESTED`, exact new defects and concrete remediation. End with **one** `PASS_DISTINCT_REVIEWER`, `HOLD` or `FAIL` decision. Do not infer production qualification from a simulation. Even a reviewer PASS does not grant G1 science; a separate owner decision is needed after gates are closed.

**G1_SCIENCE_LOCK=HOLD · OWNER_SCIENCE_PERMIT=NOT_ISSUED · REAL_TEST_OPENED=NO · SCIENCE_EXECUTED=NO**.