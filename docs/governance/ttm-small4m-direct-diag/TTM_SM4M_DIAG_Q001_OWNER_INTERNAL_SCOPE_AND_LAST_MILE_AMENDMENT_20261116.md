# Owner internal research scope — Q001 last-mile admission amendment

**Operation:** `TTM_SM4M_DIAG_Q001_I1_LAST_MILE_HARD_MEMORY_RIGHTS_SIGNERS_RUNTIME_AND_DISTINCT_ADJUDICATION_ONEPACK`  
**Date:** 2026-11-16 · **Owner scope:** one noncommercial local synthetic diagnostic of the existing owner's T4 step-1024 Small-4M model on `DESKTOP-4PSD0G2`; no public checkpoint/dataset redistribution.  
**Authoritative user message:** owner confirms this is internal research and explicitly opposes continued self-imposed governance blocking. Recorded verbatim in [Issue #29 owner-scope clarification](https://github.com/minhtri22/TokenToModel-Lab/issues/29#issuecomment-6916584568). The earlier `GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL` remains in force; owner is **not** asked to repeat it.

## Owner decision and necessary distinction

**Owner permission for local internal use: ACCEPTED AS DECLARATION** (`OWNER_DECLARED_INTERNAL_SCOPE`). This replaces the project-created administrative demand for **three independently sourced Ed25519 role signatures** solely for this local owner-managed **ENGINEERING diagnostic**. For a single-person research project, mandatory external owner/reviewer/rights-custodian signers do not by themselves prove scientific integrity, and cannot remain an ever-expanding self-imposed gate. Do **not** create fabricated keys, forge `VERIFIED_SCOPED` strings, or mark old code's `TRUSTED_ED25519_PUBLIC_KEYS={}` as PASS. **The release_auth_v2.py runtime still denies execution until an explicit new single-owner admission path is implemented and native-tested.** This is a policy admission amendment, not a claim code has already been changed.

Separate categories of evidence:
- `OWNER_DECLARED_INTERNAL_SCOPE`: supported by explicit owner instruction, not a signed legal title transfer.
- `UPSTREAM_LICENSE_LABEL_DOCUMENTED`: upstream [roneneldan/TinyStories](https://huggingface.co/datasets/roneneldan/TinyStories) declares `cdla-sharing-1.0`; this does not independently prove exact local derived-checkpoint provenance or waive license terms.
- `CHECKPOINT_AND_TOKENIZER_BYTES_VERIFIED`: **NOT_YET**, requires local SHA/size, source lineage and private custody readback under owner permission.
- `NATIVE_RESOURCE_ENFORCEMENT`: **NOT_YET**; OS Job Object committed memory limit and sampled RSS are **distinct metrics**, both must be recorded accurately.
- `DISTINCT_TECHNICAL_QA`: **NOT_YET on latest code**; separate source review validates experiment implementation, not three organizational signatures.

**This is an admission-policy amendment only.** The frozen scientific question, exact checkpoint `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` (45,074,891 bytes), P02 blob `9762343e06cf800b50574c2871ae1ed58537fb18`, TRAIN 24 / nontrain 56, seed `20261116`, max 256 steps, CPU FP32, 900s wall, 12 GiB sampled tree RSS and 1 GiB total output **are unchanged**. No TEST/FINAL24 replay, no multiple seeds/retries, no new QID, no `lineage.md` changes from source QA.

## Concrete last-mile technical implementation candidates

1. **Python 3.12 runtime without psutil**: `windows_rss_native.py` uses stdlib Win32 `GetProcessMemoryInfo` for current-process WorkingSetSize; `ttm_sm4m_diag_q001.py` has an exact Git-blob pin of that module; `Run-Approved-OneShot-PS51.ps1` has a re-pinned runner SHA-256. This avoids global Python package mutation. **Native Windows QA pending**; this is not tree-wide memory enforcement.
2. **Hard OS safety under review**: `windows_job_memory_limit.py` is an independent source-only Win32 prototype. It creates the child with `CREATE_SUSPENDED`, applies `JOB_OBJECT_LIMIT_JOB_MEMORY` + `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, assigns the child before `ResumeThread`, and fails closed on native error. **NOT yet connected to I2**, not native-tested. The cap applies to **job committed memory**, not RSS. Preserve parallel sampled tree RSS 12GiB check; if the hard commit cap trips, classify `HOLD_RESOURCE_INCOMPLETE`, never model FAIL. Review Win32 handles, nested jobs, inherited std handles, process-tree cleanup and Python3.12 Win32 structs before integration.
3. **One-owner internal admission replacement**: Codex implements a transparent, narrowly scoped check tied to this exact GitHub owner declaration and Q1 SHA, plus existing proof of checkpoint, tokenizer, fixture, source integrity and single-use nonce. No third-party signature ceremony, no fake cryptographic identity, no removable/downgraded byte/fixture/seed/resource gate. Keep the old 3-signer logic auditable; version the replacement; ensure independently negative-tested fake/local permit denial. Record the owner decision as `OWNER_DECLARED_INTERNAL_SCOPE` and original-source provenance separately.
4. **Only truly independent technical review**: Codex has already completed 6/6 PowerShell parser, source 18/18, author negatives 44/44, Codex adversarial 22/22 and watchdog 5/5 twice on previous exact source. Preserve historical evidence. New QA focuses only on the changed runtime module, Win32 Job Object wrapper, simplified permission path and evidence byte/custody. One distinct exact-head review remains useful for error detection, not a legal signer requirement.

## I1 release decision rule — one integration, no micro-permits

Current status **`HOLD_I1`** because latest Python/JobObject sources are not native-qualified, wrapper not connected, exact private checkpoint/tokenizer/real 80-case fixture not read back, and old release_auth cannot satisfy internal admission. This HOLD is now **engineering/custody**, not a demand to gather three ceremonial signatures.

When owner-internal admission logic is reviewed and actual Windows negative QA, checkpoint/tokenizer exact bytes, 80-case fixture, 900s/12GiB/1GiB stop enforcement and process cleanup PASS, a distinct reviewer may issue `I1_PASS_SCOPED_INTERNAL_RESEARCH`; then the existing owner's conditional GO authorizes **one** I2 execution. If any truly required item fails, report one `HOLD_I1` with evidence; no paper-only cycle to create additional approval roles.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_SM4M_DIAG_Q001_CODEX_LAST_MILE_NATIVE_JOB_OBJECT_OWNER_SCOPE_RUNTIME_AND_ONE_I1_ADJUDICATION` — integrate and negative-test native protection + owner-only policy, read back owner-controlled checkpoint and tokenizer hashes, return one I1 PASS/HOLD with a GitHub evidence receipt; run I2 only after genuine PASS under the prior GO.
