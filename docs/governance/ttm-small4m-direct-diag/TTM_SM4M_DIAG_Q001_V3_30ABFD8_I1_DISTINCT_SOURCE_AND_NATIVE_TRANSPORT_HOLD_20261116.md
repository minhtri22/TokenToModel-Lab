# TTM-SM4M-DIAG-Q001 — V3 exact-HEAD independent I1 reassessment

**Date:** 2026-11-16  
**Operation:** `TTM_SM4M_DIAG_Q001_V3_EXACT_HEAD_NATIVE_NEGATIVE_QA_AND_RIGHTS_CUSTODY_SINGLE_I1_READBACK`  
**Exact frozen candidate:** `30abfd8efe18a2d116c2f1fd16ff67a6332ea49c`  
**Repository:** `minhtri22/TokenToModel-Lab` · Draft PR [#28](https://github.com/minhtri22/TokenToModel-Lab/pull/28) (unmerged) · review assignment [#29](https://github.com/minhtri22/TokenToModel-Lab/issues/29)  
**Q1 main baseline:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`  
**Source-only independent assessment:** `HOLD_DIAG_Q001_V3_SOURCE`  
**ONE I1 adjudication:** **`HOLD_I1`**  
**I2 CPU:** `NOT_EXECUTED` · actual private data/model read: `FALSE` · native Windows negative QA: `NOT_EXECUTED`.

## Readback method & scope

- Used connected GitHub `fetch_file(ref=30abfd8efe18a2d116c2f1fd16ff67a6332ea49c)` for all **13 V3 manifest entries**; compared independently calculated UTF-8 SHA-256 (FIPS-180-4 implementation; `abc` known-vector self-test PASS), GitHub-returned Git blob SHA-1 and byte lengths. **13/13 for all three checks**. Source manifest Git blob: `ac1f44cd8a4d6eabee10b7f7eaf681c5be15ec69`.
- Retrieved `Run-Approved-OneShot-PS51.ps1` through both `fetch_file` and `fetch_blob(20129b81cb32595b1639e6b6aa714109cc50fa01)` to independently confirm the exact defective line.
- `lineage.md` Git blob `3409e036241deb1da6674619a2abc834bea8a2d6`, and `src/p02/transformer_core.py` Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, are identical between V3 HEAD and Q1 baseline.
- GitHub PR #28 HEAD equals `30abfd8efe18a2d116c2f1fd16ff67a6332ea49c`, is draft/unmerged; review issue #29 and PR comments show no later authenticated signer/rights or Windows native receipt. These are source/provenance observations, **not** a native execution receipt or an external-human signoff.

## Newly independently detected source blockers

**V3-N05 — malformed PowerShell launcher (HARD BLOCK).** `Run-Approved-OneShot-PS51.ps1:18` is exactly:

```powershell
if ($ExpectedRunnerSHA256 -cnotmatch '^[0-9a-f]{64}
```

Unclosed single-quoted regex and incomplete `if` cannot parse as a valid PowerShell statement. The same bytes were returned by GitHub blob and file APIs, with SHA-256 `334b91e07e1eaccf97a1dd6a60758557143a46ad1161dac57b1c6c5caa44d9db`. This is a deterministic **source defect**, not an assertion that Windows native QA was executed.

**V3-N06 — watchdog SHA parameter is inert (HARD BLOCK).** The launcher declares `ExpectedWatchdogSHA256` at line 12 but never uses it after parameter declaration. `Get-FileHash` at line 25 verifies the *runner*, not `Watch-TTM-SM4M-ProcessTree-PS51.ps1`. The author V3 Python source test merely checks that both `ExpectedWatchdogSHA256` and `Get-FileHash` appear somewhere; it therefore would not detect this missing binding. It also checks the exact 64-hex regex string, which is **absent** from the current launcher.

**V3-N07 — watchdog function not loaded (HARD BLOCK).** Launcher lines 42-48 call `Invoke-TTMDiagProcessWatch` without dot-sourcing or importing `Watch-TTM-SM4M-ProcessTree-PS51.ps1`. The function is defined in that *separate* file, not in the launcher. Explicit reviewed-module loading and its hash validation must precede launching any process. No inference is made about a hypothetical externally preloaded shell environment.

**V3-N08 — sampled RSS is not a hard memory cap (OPEN).** `Watch-TTM-SM4M-ProcessTree-PS51.ps1` polls aggregate parent+observed descendants. This is better than parent-only accounting but cannot guarantee instantaneous 12 GiB enforcement. Need native adversarial data, child PID termination, wall/RSS/output observations and adjudication whether a Windows Job Object hard cap is mandatory under the frozen resource contract.

## Custody and transport checks

- **F01:** V3 binds `D:\WORK\RESEARCH\TokenToModel-Lab` and `DESKTOP-4PSD0G2`; nonce ledger is located at canonical root `_evidence/ttm_sm4m_diag_q001_onetime_claims` with `O_EXCL`. These are visible source improvements. Cross-root/cross-worktree *native* replay, directory tampering, deletion and remote replay remain unproven; author mock substitutions are not authenticated signer checks.
- **F04:** Python `exact_scoped_path` uses `Path.resolve` and exact trusted root. Real Windows junction/reparse and canonical path-escape negative tests were **not executed**.
- **F05/F08 native:** GitHub `Invoke-DIAG-Q001-Watchdog-NativeNegativeQA-PS51.ps1` contains five planned synthetic no-model cases. No live PowerShell 5.1/Python 3.12 receipt. RemoteDesktop `machine-1` (`DESKTOP-4PSD0G2`) was ONLINE with 0 authoritative active node jobs in signed heartbeat. One authorized managed-project registration attempt at `D:\WORK\RESEARCH\TokenToModel-Lab` failed immediately at **`project_register_on_device`** with **`remote project kind changed`**; therefore no task/lease/job was dispatched. No legacy `run_command` bypass used.
- **F06 HARD VETO:** `release_auth_v2.py` at the exact HEAD defines `TRUSTED_ED25519_PUBLIC_KEYS = {}`. Authentic three-role owner/distinct-reviewer/rights-custodian custody, AD-00/AD-01C/E6 lawful rights, token inventory/underlying provenance, T4 checkpoint (SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; size 45,074,891), actual private tokenizer and independently reviewed frozen 80 records are **NOT_VERIFIED**. Do not fabricate keys/permissions or read private bytes prior to lawful admission.
- **F02/F03/F07/F09/F10:** public source includes underlying taxonomy digest logic, 80 case/group hashes, a parameter delta gate, pinned README and restriction-bias caveat. None of these proves real private fixture/model execution. Reviewer does not upgrade author `31/31` historical Linux mock to a native PASS.

## One gate decision, no simulation of success

`HOLD_I1` on exact `30abfd8efe18a2d116c2f1fd16ff67a6332ea49c`.

**Earliest observed transport failure:** `project_register_on_device` → `remote project kind changed`.  
**Earliest identified launcher failure:** PowerShell parser at `Run-Approved-OneShot-PS51.ps1:18`.  
**Independent hard veto even after repairing those:** unconfigured authenticated signers and unverified AD-00/AD-01C/E6 rights / tokenizer / checkpoint / frozen fixture custody.

I1 is **NOT** released; I2 stays `NOT_EXECUTED`. Owner's existing `GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL` is preserved and must **not** be solicited again. No forked experiment, no TEST/FINAL24 reads, no Q1/main/lineage alteration, no PR #28 merge. GitHub evidence written through owner's connected identity does **not** establish an independent external human or organizational signer.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_SM4M_DIAG_Q001_V3_LAUNCHER_BLOCKER_REMEDIATION_MANAGED_NATIVE_NEGATIVE_QA_AND_RIGHTS_CUSTODY_ONEPACK` — fix parse/actual watchdog pin+load in a NEW fixed candidate, then one managed Windows no-model negative QA and external attestation of rights/custody; release I1 only after every original gate independently passes. No new GO or micro-permit requested.
