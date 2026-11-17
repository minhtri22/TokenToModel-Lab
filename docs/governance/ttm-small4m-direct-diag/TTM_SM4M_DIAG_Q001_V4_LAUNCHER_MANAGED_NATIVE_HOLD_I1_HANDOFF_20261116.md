# HANDOFF — TTM-SM4M-DIAG-Q001 V4 · launcher remediation + actual managed transport verdict

**Date:** 2026-11-16 · **Operation:** `TTM_SM4M_DIAG_Q001_V3_LAUNCHER_BLOCKER_REMEDIATION_MANAGED_NATIVE_NEGATIVE_QA_AND_RIGHTS_CUSTODY_ONEPACK`  
**Repository:** `minhtri22/TokenToModel-Lab` · [Draft PR #28](https://github.com/minhtri22/TokenToModel-Lab/pull/28) · [Review Issue #29](https://github.com/minhtri22/TokenToModel-Lab/issues/29).  
**Original independent V3 review:** `30abfd8efe18a2d116c2f1fd16ff67a6332ea49c` · [HOLD evidence](https://github.com/minhtri22/TokenToModel-Lab/blob/b02ee93946bcca16f03f51ad5364ad554dcc61f9/docs/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_V3_30ABFD8_I1_DISTINCT_SOURCE_AND_NATIVE_TRANSPORT_HOLD_20261116.md) (`HOLD_I1`).  
**Exact remediation source tested for SHA custody before this handoff:** `d42c44040da89ab6c5d275a9389ba920ef18db68`; source/evidence manifest: [14-file V4 JSON](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_V4_LAUNCHER_MANAGED_NATIVE_SOURCE_MANIFEST_20261116.json), Git blob `a4c14a4a1125b71ae985b1671212e06e0fc96d46`, manifest commit `37c2635325e15f92ff7a7481688efb7cf239c1ec`. **Reviewer must pin the later current PR exact HEAD** for full evidence readback, not reinterpret historical review HEAD.  
**Question Gate:** `TTM-SM4M-DIAG-Q001` already registered on Q1 main `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`. **Owner conditional GO:** `GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL` remains preserved, not a run permit by itself.

## Executed source remediation vs actual negative QA

1. **V3-N05 launcher syntax:** The malformed `ExpectedRunnerSHA256` regexp line was replaced with a complete valid-looking PowerShell `if`. GitHub readback exact blob `8f2c528ef37219891a7ab017de32357a6711c86f`, SHA-256 `01e4a3e58e0d8a0414a724c744c6f8d4b071b4e1187f427e70cdbb3a58d48985`. This is **source correction**; *native parser was not executed*.
2. **V3-N06 watchdog SHA binding:** The launcher now validates `ExpectedWatchdogSHA256` as 64 lowercase hex, hashes `Watch-TTM-SM4M-ProcessTree-PS51.ps1` with `Get-FileHash -Algorithm SHA256`, compares byte hash and fails closed before creating the model process.
3. **V3-N07 actual module loading:** The launcher dot-sources the hash-verified watchdog and uses `Get-Command ... -CommandType Function` to check `Invoke-TTMDiagProcessWatch` *before* `Start-Process`.
4. **F05/F08 native QA fixture:** Changed the `exit_big` synthetic process to emit 65536 bytes on **watched stdout**, not an irrelevant side file. Added `Invoke-DIAG-Q001-I1-NativeSourceOnePack-PS51.ps1` that pins the 5 source SHA-256 digests, uses `[System.Management.Automation.Language.Parser]::ParseFile` over scripts, checks watchdog load/hash order and orchestrates Python mock and five native watchdog negative cases. No model checkpoint, private tokenizer or scientific fixture is provided to these tests. **No native PASS is claimed**.

Manifest SHA-256 self-test `SHA256("abc")` passed. 14/14 Git blob, SHA-256 and UTF-8 byte lengths were read from exact correction head and pinned. Eleven V3 unmodified files retained historical Git blobs. This is an **author GitHub source custody readback**, not an external independent review, PS parser receipt or native Windows QA.

## The managed Windows task route was found; command allowlist still vetoes execution

- Windows node `machine-1` / `DESKTOP-4PSD0G2` ONLINE. Recovered legitimate existing **GIT** project `prj_1544c3e94ebd4b2947bc84e9` (active binding, eligible for new tasks), instead of calling `project_register_on_device` again.
- Created managed source-only task `tsk_2d1d91bd29582300c60fc10d` under that project. Its initial local base was older `1edb95cc3925ff18f0c644e94888139af854fae5`, therefore no QA was executed against that base.
- Exact GitHub source branch fetch job `rjob_d1aed9b564b40a33f2352da9db4581c2` **SUCCEEDED**; exact task-worktree source reset job `rjob_802c07f720fc2a5ab6ae2dadf2272a4c` **SUCCEEDED**, stdout `HEAD is now at d42c440 ...`. The task scoped to its own worktree; `main` and `lineage.md` not changed.
- On re-claimed task lease, the **no-model** Windows PowerShell source QA command submitted as operation `TTM_SM4M_DIAG_Q001_MANAGED_PS51_SOURCE_ONLY_NATIVE_ONEPACK_20261116`, proxy job `rjob_bd75ffaedd5706d82f436097a0201b0e`, was **REJECTED in POST_PROXY_PRE_NODE**: `COMMAND_NOT_ALLOWED` — `executable 'powershell' is not in durable allowlist`. No `node_job_id` was assigned; terminal evidence says `scientific_execution_started=false`. The transport-level summary contains a contradictory generic `scientific_execution_started=true` field; rely on terminal `node_job_id=null` and command error for the narrower claim *no command was dispatched to the node*. **No actual native PS5.1 process or model ran**.
- The rejection is terminal: `replacement_job_forbidden=true`. Do **not** try `powershell.exe` via legacy `run_command`, Python `subprocess`, path aliases or another executable to evade the managed durable allowlist. A legitimate control-plane allowlist admission/update is required before a NEW authorized source QA attempt.

## F06 hard veto remains fully open

`release_auth_v2.py` still deliberately has `TRUSTED_ED25519_PUBLIC_KEYS={}`. No authentic owner/distinct-reviewer/rights-custodian signer custody, no AD-00/AD-01C/E6 exact rights attestation, no verified private original tokenizer inventory or live T4 step1024 checkpoint SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` / length 45,074,891 bytes, no independently reviewed frozen 80-case fixture. Do not create fake trust anchors, permit JSON, checkpoint surrogate or scientific fixture to force a PASS. No access to historical TEST/FINAL24; P02 and `lineage.md` unchanged.

**V3-N08 remains OPEN:** sampled aggregate process RSS is NOT proven to meet an instantaneous hard 12GiB OS memory cap; Windows negative QA and possible Job Object admission require reviewer consideration. Do not describe sampled bounds as hard enforcement.

## Integrated I1 decision — single verdict

**`HOLD_I1`**: corrected source paths available for distinct review but actual Windows native tests `NOT_EXECUTED`, transport `COMMAND_NOT_ALLOWED`, signer/source/rights `NOT_VERIFIED`, I2 `NOT_EXECUTED`, PR #28 remains Draft/unmerged, no science checkpoint/model run, no `lineage.md` change. Previous independent V3 HOLD remains an immutable historical verdict, not retroactively replaced.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_SM4M_DIAG_Q001_V4_EXACT_SOURCE_NATIVE_ALLOWLIST_AND_RIGHTS_SINGLE_I1_ADJUDICATION` — independent agent checks V4 exact source, restores the **approved** managed PowerShell native QA route without bypass, completes real no-model Windows negative QA and external signer/rights/custody proof, then issues exactly one `I1_PASS` or `HOLD_I1`. On genuine PASS only, apply the existing conditional GO for one bounded CPU run, never auto-retry.
