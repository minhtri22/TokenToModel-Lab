# G1 — Windows 11 target QA readback and distinct Codex adjudication packet

**Date:** 2026-11-10, Asia/Bangkok. **Scope:** TTM × SIX G1 trusted-boundary QA; private synthetic-only.  
**Owner-run verdict:** `QA_COMPLETED_PRODUCTION_HARD_GATES_HOLD`.  
**Scientific gate:** `G1_SCIENCE_LOCK=HOLD`; owner science permit **NOT ISSUED**.

## 1. Exact evidence provenance

- Repository: `minhtri22/TokenToModel-Lab`.
- Candidate code baseline: `implementation/ttm-six-g1-trusted-runtime-witness-20261109@cdaf13b4ac131b0117aadb836fd42810c63978db`.
- V1 quoting correction documented at `9c444e88666838c7bf7ccd4acf7b0af3ddc1bce6`, V2 runner SHA256 `28d6294e4213c9f2d2741b2b22b6a1c6839137bc88cf7fa429706aad65150b33`.
- Frozen research branch remains `d5d0c5346a595557a76349f900d09be50bce289c`; Codex V1c review commit `d478282e16a4728f064892564b949e671e13cdd2`; frozen `main` `b57b44e7287f842e81050c1faee337f636333dd0`.
- Target local QA directory (kept PRIVATE, never published): `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\G1_TRUST_BOUNDARY_WINDOWS_QA_20261110_003825_4116bd1e`.
- Owner CLI printed `G1_WINDOWS_QA_RECEIPT_SHA256=ecbca346db8dff459ca8659101e60391a3edd54df585d11dbede69cc93ec177e`. `LOCAL_SHA256_RECEIPT.txt` contains the **same value**. The assistant independently read both files over connected read-only remote file access; this checks text consistency but **does not independently recompute raw receipt-byte SHA256**.
- Receipt schema `ttm.six.g1.windows_trust_boundary_local_qa.v1`; creation timestamp `2026-11-10T00:38:25.3702224+07:00`; original ZIP SHA256 `5584dfb61d293f2946b66ef9f5e4bb4a0703c415ced0946ff2bacc302e95013c`. ZIP entries/hashes `true` per owner receipt.
- Environment: Windows 11 (NT build 26300), PowerShell 5.1, Python 3.12, D: formatted NTFS. Execution from non-elevated owner PowerShell; project `main` was unchanged per receipt.
- Raw inventory log contains local SID/account/DACL information. **Do not push unredacted log or private receipt to a public GitHub repository.** Only reviewer with legitimate local access should inspect raw evidence.

## 2. Observed target QA — not production trust admission

| Target test | Actual observed result | Permitted conclusion |
|---|---|---|
| Python 3.12 native CLI and V2 runner | Runner completed, exit 0, receipt emitted | `PASS_WINDOWS_RUNNER_EXECUTION` |
| Original source/ZIP SHA and project boundary | Bundle SHA verified; Git originally unchanged | `PASS_SOURCE_INTEGRITY_LOCAL_REPORTED` |
| Synthetic admission controller/witness | `PASS_G1_TRUSTED_BOUNDARY_SIMULATION_ONLY`, 45/45 | `PASS_AUTHOR_SYNTHETIC_45_OF_45_WINDOWS` only |
| Win32 Job Object forced termination | `child_exited=true`, `forced_kill_verified=true`, `timed_out=true`; harmless sleep worker | `PASS_HARMLESS_CHILD_WIN32_ONLY` |
| Win32 Job Object non-timeout path | Exit 0, `child_exited=true`, `forced_kill_verified=false` | `PASS_HARMLESS_CHILD_WIN32_ONLY` |
| Real SID/DACL listing | Log written, read-only inventory complete | `PASS_READONLY_INVENTORY_NOT_WORKER_NEGATIVE_ACCESS` |
| Distinct worker-principal TEST denial | No separate Windows worker logon used | `NOT_TESTED` |
| Four production ACL directories (broker/controller/worker/witness) | All four `provisioned=false`, `acl_directory_owners_distinct=false` | `HOLD`, no trust-boundary claim |
| Synthetic current-user sentinel ACL | Current owner able to read; four inherited rules | Does **not** demonstrate deny-access for separate worker |
| Authenticated external source/pack writer | None deployed | `NOT_TESTED` |
| Independent witness in separate rollback domain | None deployed | `NOT_TESTED` |
| Controller-resistant monotonic one-shot | Only synthetic controller/witness tests | `NOT_TESTED` |
| Real GPU/T4 watchdog | No GPU or model invoked; patch only tested on CPU child | `NOT_TESTED` |
| Owner production public key / permit | Not provisioned / not issued | `HOLD` |
| V1d methodology amendment | Awaiting independent scientific approval | `HOLD` |

The Windows job probe used the **SHA-pinned safety-patched QA watchdog**, not the original production candidate; patch SHA256 `a033e881d42e59c18aa9af96390fe808eb2b9858ee2653ae88c5b238256393e5`.

## 3. Recorded log checksums — local private evidence only

| Log under QA `logs/` | SHA256 recorded in owner receipt |
|---|---|
| `windows_readonly_inventory.log` | `9fb7e63e550e7cb15fbcabf91d20a160319b27f5803f6e35b5f087104e1c29f1` |
| `synthetic_45.log` | `c3b3d40af2e04679f3721cde2ea31eb76d767e338364f53d262d07a2037bc52b` |
| `controller_status.log` | `627fca1dcd299caa37be51443abd43a20c014235850535812d9a7468b13c3b3a` |
| `win32_watchdog_status.log` | `30fda00e8bbed991570e91dbcae835a1e2bcfcea84a28994517fc7f59f2fb530` |
| `win32_job_forced_kill.log` | `b8d5db6116cef3eb4139fa1cd92ca0759ee0028d974f25d7af64fa811f0cc723` |
| `win32_job_normal_exit.log` | `2b432f756cd8c54b0e956f8881cdd027be6094a2eed7aae1d2ba106f2255b330` |

The assistant read the logs and parsed safe result fields, without exporting raw SID/DACL inventory. Log digest values above were read from the receipt, not independently recomputed.

## 4. Exact distinct reviewer contract — one integrated decision

**Task:** `TTM_SIX_G1_WINDOWS_REAL_QA_EVIDENCE_READBACK_AND_INTEGRATED_HARD_GATE_DISTINCT_ADJUDICATION`.

A separate Codex reviewer must:
1. Fetch all source pins at the **immutable implementation commit**, inspect the new QA receipt, and independently compute SHA256 of raw local receipt/log files, without publishing private SID/DACL.
2. Evaluate the local Windows Job Object negative and normal-exit tests, and distinguish **QA-patched watcher** from any production launcher. Determine whether the real supervisor is eligible for a bounded, non-science target test.
3. Independently check the security boundary: user/group/SID ownership and DACL inheritance of future controller/broker/worker/witness roots; if no distinct service/user principal exists, mark `NOT_TESTED`, never substitute a current-user sentinel.
4. Explicitly challenge hardlink/alias to held-out synthetic files, writer self-issued receipts, crash between pack and receipt, rollback of both witness and ledger, and OS forced-kill failure. These cannot be marked PASS merely from 45 synthetic QA cases.
5. Adjudicate the V1d scientific amendment (CKA tie tolerance, fixed-denominator bootstrap, v1a first-occurrence mapping/dedup, null exchangeability, near-dup and TEST64 power limitations).
6. Produce exactly **one verdict** `PASS_DISTINCT_REVIEWER`, `HOLD`, or `FAIL`, with per-gate `PASS/FAIL/NOT_TESTED`. No G1 science permit or private TEST opening.

**Preserve:** `main`, frozen research/review, PR#12, lineage.md, T1/G1 manifests, consumed Qwen technical runs, student checkpoints. No production ACL mutation without owner-authorized Windows identity design and an explicit scope decision. New evidence may be added only on a dedicated reviewer branch, never overwriting immutable source.

## 5. One integrated remaining work package (not six micro-permits)

The remaining operational work is a single production-boundary implementation: owner-anchored trusted launcher + distinct Windows principal, broker and negative ACL proof, trusted transactional writer, independently governed monotonic witness, OS-level kill-capable worker supervisor and the V1d methodology approval. These must be tested as a group before owner science admission. Do not rerun already consumed Qwen smokes or open real G1 TEST during qualification.

**Final state:** `WINDOWS_TARGET_QA=COMPLETED` · `WINDOWS_SYNTHETIC=PASS_45_45` · `WINDOWS_JOB_OBJECT_HARMLESS_KILL=PASS` · `SID_DACL_INVENTORY=PASS_READONLY` · `REAL_SEPARATE_WORKER_ACL=NOT_TESTED` · `PRODUCTION_HARD_GATES=HOLD` · `DISTINCT_ADJUDICATION=PENDING` · `G1_SCIENCE_LOCK=HOLD`.
