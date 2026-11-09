# G1 — PowerShell origin guard STOP and scoped V2 recovery

**Ngày:** 2026-11-09  
**Thao tác:** `TTM_SIX_XMODEL_G1_PRIVATE_MANIFEST_SELFTEST_ORIGIN_GUARD_RECOVERY_V2`  
**Status:** `V1_SELFTEST_STOP_ORIGIN_MISMATCH` · `V2_SOURCE_QA_PASS_10_10` · `V2_WINDOWS_RUNTIME_NOT_EXECUTED` · `G1_SCIENCE_LOCK_HOLD`.

## Owner evidence retained

User's PowerShell console:
```text
STOP_REPO_ORIGIN_MISMATCH
At D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\G1_MANIFEST_RUNNER_V1A.ps1:29
STOP_G1_SelfTest_FAILED
```

This failure was raised in PowerShell's Git origin guard, **before** invoking Python `--mode selftest`. Therefore `G1_SELFTEST=NOT_EXECUTED_BY_OWNER_ATTEMPT`, not scientific FAIL. It does not revoke T1 manifest PASS or Qwen3-0.6B technical PASS. Tokenizer setup, private manifest seal, raw data scan, independent G1 QA and Qwen3-1.7B smoke were **not** performed by this failed wrapper invocation.

## Direct readonly Git config inspection

Connected RemoteDesktop `machine-1` read:
`D:\WORK\RESEARCH\TokenToModel-Lab\.git\config`: `[remote "origin"] url = https://github.com/minhtri22/TokenToModel-Lab.git`.

This locally configured value matches the authorized TTM repository. This **does not** establish what `git remote get-url origin` returned inside the owner's PS5.1 session: system/global Git URL rewrites may change the effective value, and the original combined conditional lacked separate telemetry. The precise cause of V1 STOP remains `UNDETERMINED` pending readback; do not bypass a mismatched effective remote or change the repo's Git config to make the wrapper pass.

## V2 amendment — targeted, additive

Original `Run-G1-PrivateManifest-PS51.ps1` remains unchanged and the STOP evidence is preserved.

New `scripts/research/six_ttm/Run-G1-PrivateManifest-PS51-v2.ps1`, Git blob `02a8dd4a9827f88070e5953034cff68d81ac6aaa`, creation commit `3f57ead46db9e48734f6e4fb44eadce43f2baa79`:
- Captures `git config --local --get remote.origin.url` and `git remote get-url origin` with independent exit statuses, nonempty single-line requirements.
- Normalizes lower case and whitespace; logs both effective/configured values with HTTPS credentials masked.
- Uses explicit `$allowedOrigins -contains $value` flags rather than one mixed `-or ... -notcontains` expression.
- **Both** values must match the original four HTTPS/SSH accepted spellings of `minhtri22/TokenToModel-Lab`; mismatches STOP with a distinct code. No override, whitelist expansion, Git config mutation or unsafe fallback.
- Keeps original Python producer Git blob `aee230060f8202907953e0eeab0ae5b1099a584e`, no-overwrite, strict project path, Python312, explicit `Seal` owner scope gate, independent QA and no science.
- 10/10 focused source-structure checks **PASS** with GitHub readback. PowerShell 5.1 parser/runtime test **not executed by assistant** due managed RemoteDesktop tool refusing arbitrary command dispatch without task lease.

## Recovery

Download V2 to a **fresh** project-local file under `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\`, verify Git blob exact `02a8dd4a9827f88070e5953034cff68d81ac6aaa`, then run **only** `-Mode SelfTest`. Never overwrite the failed original launcher. If `G1_REPO_ORIGIN_DUAL_ATTESTATION=PASS` and `PASS_SYNTHETIC_SELFTEST_NO_FILES_NO_SCIENCE`, the local SELFTEST technical gate closes. If it still STOPs, retain both origin diagnostic lines (credentials redacted) to investigate; do not bypass.

No change to `main`, PR#12, checkpoint, `lineage.md`, T1 original manifest or Qwen0.6B one-shot.

**Next:** `TTM_SIX_XMODEL_G1_PRIVATE_MANIFEST_SELFTEST_V2_READBACK_THEN_SCOPED_DATA_MATERIALIZATION`.
