# TTM × SIX G1 v1e — Two Windows fault paths: owner result readback and distinct Codex review packet

**Task:** `TTM_SIX_G1_V1E_OWNER_WINDOWS_TWO_FAULT_RECEIPT_THEN_DISTINCT_ADJUDICATION`  
**Date:** 2026-11-10 (Asia/Bangkok)  
**Current scientific authorization:** `G1_SCIENCE_LOCK=HOLD`; `OWNER_SCIENCE_PERMIT=NOT_ISSUED`; `G1_PRIVATE_TEST_OPENED=NO`; `SCIENCE_EXECUTED=NO`.

## 1. Exact version and chain of custody

- Repository: `https://github.com/minhtri22/TokenToModel-Lab.git`.
- **Reviewed source baseline**, fixed regardless of future branch movement: `1efca4ca080572dcd22bbe658701b221ca46f7dd`, branch `implementation/ttm-six-g1-production-gates-methods-v1e-20261110`.
- Source Win32 v1e: `scripts/research/six_ttm/g1_win32_job_failure_path_v1e_candidate.py`, Git blob SHA1 `ec5f3b5d633b8b0feb5ae98c2d8c8c9f45896eb7`, SHA256 `eb5d1b71a991eb4ca46d801057806e2a580c6bcd2487080bfe3e2c15a6008309`.
- PowerShell v1e runner: `scripts/research/six_ttm/Run-G1-Win32FailureModes-PS51-V1E.ps1`, Git blob SHA1 `348205f54acd0134e233d0f79563f099a121bc1d`, SHA256 `3cc1ee9f9991a17b6c890853f1f0c5d0f8f132400b5ca2a41adc40f89355ebd6`.
- Signed boundary v1e: `scripts/research/six_ttm/g1_signed_boundary_contract_v1e_candidate.py`, blob `e91fe583db1aa5b112aecd5b8d2830a5da17dd3e`.
- Preregistered methods amendment *candidate* v1e: `docs/research/six-ttm/G1_METHODS_V1E_PRETEST_FROZEN_AMENDMENT_CANDIDATE_20261110.md`, blob `d2737a9c2fb31d8398119622fe1ff78c295c8fa8`.
- Author Linux CPU QA receipt: `docs/research/six-ttm/G1_V1E_AUTHOR_CPU_QA_RECEIPT_20261110.json`, **61/61 synthetic/static PASS** (53 signed-boundary, 8 Win32 static).
- Frozen v1c research `d5d0c5346a595557a76349f900d09be50bce289c`. Previous independent Windows adjudication HOLD `efbbc1fddfd61e775d30a0481622312f8fb93c51`. Preserve `main=b57b44e7287f842e81050c1faee337f636333dd0`, PR#12, lineage.md, original manifests, source v1c and checkpoints.

## 2. Windows owner-run: exact evidence read back

**Location (PRIVATE; keep raw files on Windows):** `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\G1_WIN32_FAILURE_MODES_20261110_014528_d95df4e35c3e`.

Owner PowerShell 5.1 downloaded two raw source files from the exact immutable GitHub commit, checked SHA256 of each, and printed:

```text
G1_V1E_TWO_SOURCE_PINS=PASS_2_OF_2
G1_WIN32_V1E_QA_DIR=D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\G1_WIN32_FAILURE_MODES_20261110_014528_d95df4e35c3e
G1_WIN32_V1E_STATUS=PASS_TWO_NEW_WIN32_FAILURE_PATH_CASES_NO_SCIENCE
G1_WIN32_V1E_RECEIPT_SHA256=abd96217121dbd442f4b7eae5e5b49a08d761f51518a01bcc60ea43672159924
G1_SCIENCE_LOCK=HOLD
```

The assistant independently retrieved and read the private JSON receipt, its checksum text and the four log files using read-only connected Windows file access. The checksum text **matches the owner's CLI receipt hash**, but **raw bytes were not independently hashed by the assistant**; Codex **must** recompute all SHA256 on Windows.

| Mode / observation | Readback result |
|---|---|
| `harmless-assign-fault-qa` | `fault_mode=post_create_pre_assign`; `child_exited=true`; `cleanup_verified=true`; `PASS_HARMLESS_OWNED_CHILD_REAP_ONLY` |
| `harmless-resume-fault-qa` | `fault_mode=post_assign_pre_resume`; `child_exited=true`; `cleanup_verified=true`; `PASS_HARMLESS_OWNED_CHILD_REAP_ONLY` |
| Both logs | `platform=nt`, `production_qualified=false`, `real_gpu_used=false`, `science_executed=false`; stderr empty |
| Receipt | Schema `ttm.six.g1.win32_failure_path_owner_qa.v1e`; Python `3.12`; no real TEST, no owner permit, science HOLD |

**Digests recorded in the owner receipt (Codex must rehash original bytes):**

| Private filename | Recorded SHA256 |
|---|---|
| `G1_WIN32_V1E_PRIVATE_RECEIPT.json` | `abd96217121dbd442f4b7eae5e5b49a08d761f51518a01bcc60ea43672159924` (owner CLI and local checksum text) |
| `harmless-assign-fault-qa.log` | `1e5a6162c8f361053c102a115b52f646e7b0b969302faccb91548644600f6cd3` |
| `harmless-resume-fault-qa.log` | `823e77a6b8376415d9df06ff29856fd22a932da57594f0490f5edea36a89e685` |
| `harmless-assign-fault-qa.stderr.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) |
| `harmless-resume-fault-qa.stderr.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) |

Win32 stdout logs are UTF-16LE JSON in the local environment. Codex must decode accordingly and verify `fault_mode`, `child_exited`, `cleanup_verified`, and `production_qualified=false` rather than treating raw file text as UTF-8 or trusting a log's exit marker. Do **not** re-run consumed two fault tests solely for readback.

**Scope of PASS:** locally forced errors in an owned harmless Python child; confirms cleanup for *these two injected cases only*. Not proof of full process-tree reclamation after arbitrary failure, a production supervisor, actual GPU termination, T4 resource limits or separate Windows principals.

## 3. Exact distinct Codex review contract

**Review task:** `TTM_SIX_G1_V1E_INTEGRATED_GATE_PRODUCTION_REVIEW_AND_MINIMAL_OWNER_DECISION`.

1. Independently read and hash the private receipt and 4 local logs. Check SHA256SUMS/owner checksum and exact source SHA/Git blobs. Preserve private raw logs in local `_tmp`; do not publish SID/account details, private keys or real TEST/story bytes.
2. Independently inspect v1e Win32 source and two actual Windows fault-path observations; verify ownership/close/TerminateProcess/TerminateJobObject/WaitForSingleObject behavior, that no unowned PID can be killed, failure-path cleanup and remaining residual process-tree conditions. Report `PASS_SCOPED` vs `NOT_TESTED_PRODUCTION` correctly; no needless repeat.
3. Review signed owner/writer/witness contract v1e for actual trust boundaries: distinct pinned public-key authorities, key-substitution, payload/version/rights/expiry, source hash, freshness challenge/nonce, ack replay, tampered pack/receipt. Synthetic Ed25519 signatures are **not** real owner authority.
4. Review v1e methods as one prospective scientific amendment, including first-occurrence/exact/near-duplicate group assumptions, exchangeability for shuffle null and bootstrap, fixed full-TEST SST paired bootstrap estimand, 64-epsilon CKA ties and potential type-I/power consequences, TEST64 statistical power and mandatory INCONCLUSIVE conditions. A correctness proof on synthetic fixtures is not a scientific amendment approval.
5. Return **one** explicit verdict (`PASS_DISTINCT_REVIEWER`, `HOLD`, or `FAIL`), plus one six-row `PASS/FAIL/NOT_TESTED` production matrix, supporting evidence and a **single owner provisioning bundle**. Separate scoped Windows QA PASS from `G1_SCIENCE_LOCK`.
6. Enumerate only material owner actions still needed to close all six gates in one batch. No micro-permits. No real TEST opening, Qwen/GPU science run, TTM checkpoint writes, `main`/PR#12/lineage.md changes or production provisioning without owner authorization.

**Six hard gates:** (1) owner authority/trusted launcher and exact signatures; (2) broker TEST isolation and real worker SID/DACL deny; (3) authenticated transactional writer/pack ledger with crash recovery; (4) separate rollback-domain monotonic witness with challenge/ACK/replay controls; (5) OS-level GPU watchdog/cumulative budget after verified Win32 QA path; (6) independent scientific methods v1e approval.

**Required output:** one report `.md`, one machine-readable adjudication receipt `.json`, exact evidence SHA256, per-gate verdict, single final decision and a finite owner action list; commit new redacted files on **new reviewer branch**, leave all source commits and private files intact. Reviewer access must be real; this handoff alone is **not** a completed independent review.

## 4. Admission remains HOLD

`V1E_SOURCE=COMMITTED` · `AUTHOR_CPU_QA=PASS_61/61` · `WINDOWS_V1E_FAULT_PATH_QA=PASS_2/2_SCOPED_OWNER` · `DISTINCT_V1E_REVIEW=PENDING` · `METHODS_V1E_REVIEW=PENDING` · `PRODUCTION_HARD_GATES=HOLD` · `OWNER_SCIENCE_PERMIT=NOT_ISSUED` · `G1_PRIVATE_TEST_OPENED=NO` · `G1_SCIENCE_LOCK=HOLD`.

**Bước thực hiện tiếp theo:** Transfer this exact reviewed-source packet and private receipt path to a *distinct Codex reviewer*; request SHA256 raw-byte verification and one integrated PASS/HOLD/FAIL, then owner provision remaining hard gates in a single approved batch, without executing science.
