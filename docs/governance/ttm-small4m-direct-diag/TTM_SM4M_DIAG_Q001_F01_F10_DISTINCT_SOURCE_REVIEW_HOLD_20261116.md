# DISTINCT EXACT-SOURCE REVIEW — TTM-SM4M-DIAG-Q001 F01–F10

**Date:** 2026-11-16  
**Operation:** `TTM_SM4M_DIAG_Q001_F01_F10_EXACT_REMEDIATED_CANDIDATE_DISTINCT_NEGATIVE_QA_RIGHTS_CUSTODY_AND_SINGLE_I1_ADJUDICATION`  
**Repository:** `minhtri22/TokenToModel-Lab` · **Draft PR:** [#28](https://github.com/minhtri22/TokenToModel-Lab/pull/28) · **Review assignment:** [Issue #29](https://github.com/minhtri22/TokenToModel-Lab/issues/29)  
**Reviewed candidate exact HEAD:** `18fabe4255823e573b7ab5156974310eab8e71d9` (not any later moving branch HEAD).  
**Q1 main:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` · **earlier distinct HOLD source:** `fb0bd357fbcc95adcc94d39e94c4bdb54c1714d5` · **earlier HOLD evidence commit:** `cbc27333e13b586a8da1c0b1a3741660a61faf25`.

**SOURCE VERDICT:** `HOLD_DIAG_Q001_REMEDIATED_SOURCE`.  
**SEPARATE I1 RELEASE VERDICT:** `HOLD_I1`.  
**I2:** `NOT_EXECUTED`; **REAL MODEL/CHECKPOINT/TOKENIZER/FIXTURE ACCESSED:** `FALSE`.  
**Review classification:** Distinct conversational AI source assessor using connected GitHub read-only fetch and independent hashing logic. **NOT** attested independent organization, **NOT** native Windows 5.1/Python 3.12 execution, **NOT** an external rights signer. GitHub commit is through owner's connected identity, not proof of external reviewer identity. No model science was conducted.

## Source custody readback

- PR #28 HEAD returned `18fabe4255823e573b7ab5156974310eab8e71d9` at review time; 17 changed filenames all within `tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/`, `docs/governance/ttm-small4m-direct-diag/`, or `artifacts/governance/ttm-small4m-direct-diag/`.
- F01–F10 manifest: **10/10** Git blob SHA-1 exact matches via `fetch_file(ref=18fabe4255823e573b7ab5156974310eab8e71d9)`.
- Distinct SHA-256 computation on UTF-8 GitHub file contents with a separately implemented FIPS-180-4 style JavaScript SHA-256 function: **9/9** existing manifest SHA-256 pins match (self-test SHA-256("abc") matched known digest). `README.md` has no SHA-256 pin in author manifest; independently calculated digest: `abeecba82e6492cb84b28c140d77672e6dc05eb4011fda15523f55c9b211070d`. This README digest is a source readback, **not** an author-published pin.
- Original FB0 review MD and JSON blobs match exact source at `cbc27333...`: MD `a72a5c2f853d3337b86bce14597b1170faf1870f`; JSON `63d3a4d5cb904447be5e4e1ee990cc885cdc2ac1`. Neither was overwritten.
- `lineage.md` blob `3409e036241deb1da6674619a2abc834bea8a2d6` and `src/p02/transformer_core.py` blob `9762343e06cf800b50574c2871ae1ed58537fb18` remain byte-identical vs Q1 main; existing Q1 protocol and old TEST/FINAL remain outside proposed PR diff.
- Original author `31/31` Linux Python 3.13 mock/source checks were read **as a receipt only**; we did not rerun them. The current source-level review therefore must not be labeled native independent negative QA.

## Independent F01–F10 adjudication

| Finding | Source readback and revised disposition |
|---|---|
| **F01 BLOCKER** | Three-role Ed25519 verification is present in `release_auth_v2.py:41-111`, but trusted keys are intentionally empty (`line 20`), so only fail-closed behavior is presently reviewable. **New unresolved source finding: root-local nonce replay**. `claim_one_shot(root,nonce)` writes a claim under `root/_tmp/...` (`ttm_sm4m_diag_q001.py:483-507`), while the signed permit required fields (`release_auth_v2.py:63-88`) do **not** pin `root` or an externally durable nonce claim. After real signers are configured, the same signed nonce can be claimed in two different root directories. Existing negative test `independent_negative_qa_v2.py:96-98` only tests replay in the **same root**. Require single globally/durably keyed claim under signed scope, plus cross-root negative QA; no fabricated signer keys. |
| **F02 BLOCKER** | `permitted_ids` checks an actual underlying JSON-byte digest and full 2048-ID partition (`runner:67-103`): meaningful source improvement. However its upstream **original inventory provenance** and legal attestation remain `NOT_VERIFIED`. Mock digests cannot substitute real custody. |
| **F03 BLOCKER** | `fixture_freeze` persists 80 records plus 80 case and 5 group hashes (`runner:342-410`). Run validates signed records and group manifest (`353-379`). **Actual private fixture freeze and independent 80/80 oracle review are NOT_EXECUTED**. Note `read_frozen_fixture` recreates a comparison fixture *in memory* at `line 370`; it does not replace on-disk records, but the README wording “never regenerates” needs precision. Freeze receipt itself labels `independent_review=NOT_EXECUTED`; independently signed/frozen pre-I2 manifest custody not yet established. |
| **F04 BLOCKER** | Both PowerShell wrappers default to `$PSScriptRoot` and check a 64-hex runner digest. But native PS 5.1 has not run; direct Python `run`/ `fixture-freeze` currently does **not** enforce project-root confinement on all private source paths (PS wrapper enforces it only for `run`). Require native and direct-entrypoint path-escape negative QA before admission. |
| **F05 BLOCKER** | `31/31` are author Linux Python 3.13 mock/source tests, **not** a distinct independent native QA. Tests for watchdog use string-presence checks (`independent_negative_qa_v2.py:103-115`), not live time/RSS/output/child injections. All forged permit tests end early on EMPTY trusted keys; they do not test rejection by an actually configured trust store. Missing distinct Windows Python 3.12/PS 5.1 adversarial readback. |
| **F06 BLOCKER** | No authentic owner/reviewer/rights public keys, no verified AD-00/AD-01C/E6 rights, live T4 checkpoint SHA, actual tokenizer rights, or exact Windows dependencies. **Mandatory hard veto**; do not read private bytes or create arbitrary signatures to force a PASS. |
| **F07 MAJOR** | `runner:441-452, 550-613` includes parameter fingerprints, L2 norms, `abs_delta>0`, sampled RSS, Python/Torch versions, baseline/post records. Source-scoped implementation verified, but empirical weight update and 256-step validity are **NOT_EXECUTED**. |
| **F08 MAJOR / I1-BLOCKING** | `Run-Approved-OneShot-PS51.ps1:44-64` watchdog polls 900s, RSS and output; process-tree kill exists. **New source gaps:** `Get-Process -Id $proc.Id` reads **parent RSS only**, not aggregate descendants; time/RSS/output checks occur only **inside** `while (-not $proc.WaitForExit(1000))`, so oversized output or a breach immediately before normal exit may bypass post-exit checks. No actual Windows resource/child kill test. Fix and test native deterministic adversarial cases before I1. |
| **F09 MINOR** | Historical `17/17` is correctly replaced by `18/18`. New README says author negative QA `30/30` while its new receipt/manifest say `31/31`; correct this new documentary mismatch without altering historic receipts. README SHA-256 missing from remediation manifest. |
| **F10 MINOR** | Source explicitly labels restricted 4-way gold index zero with low-sorted distractors (`runner:153-165,611`); this diagnostic has an acknowledged interpretation bias, no calibrated benchmark or decoder-fault claim. Do not amend frozen Q1 choices post hoc. |

## I1 separate blocker ledger

1. **B01 / F01:** Before external key installation, design a signed-scope, durable **cross-root nonce-replay** guard and adversarial QA. No local mock authorization.
2. **B02 / F05+F08:** Source corrective QA plus clean **Windows PS 5.1 / Python 3.12** independent negative run with injected wall/RSS/aggregate stdout+stderr/output and child process termination. Source-string checks and an author Linux receipt do not close this.
3. **B03 / F06+F02+F03:** Externally proven owner/reviewer/rights signer custody, AD-00/AD-01C/E6 authorization, verified exact T4 checkpoint/tokenizer bytes **after** lawful admission, prospectively frozen and independently reviewed 80-case fixture.
4. **B04 / F04+F07:** Verified direct-entrypoint path containment, reviewer-pinned executable/guard hashes, Windows runtime torch/psutil; empirical weights remain unexecuted until science I2.

## Governance and handoff

- Keep prior `HOLD_DIAG_Q001_CANDIDATE_SOURCE` intact. New author remediation is materially improved but **not** a distinct native PASS. No I1 release on this packet.
- Owner conditional GO `GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL` remains in force, not an unconditional right to open model or train; **no new owner micro-permit**.
- No PR #28 merge, no edits to `lineage.md`, no sealed TEST/FINAL, no private model/fixture, and no I2 retry/reseed.
- This evidence is committed to a **separate evidence branch** based on Q1 main, leaving the exact review target and its historical HOLD intact.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_SM4M_DIAG_Q001_F01_F10_EXACT_REMEDIATED_CANDIDATE_DISTINCT_NEGATIVE_QA_RIGHTS_CUSTODY_AND_SINGLE_I1_ADJUDICATION` — one integrated exact-head remediation readback + independently executed negative QA + lawful rights/custody reassessment + single I1 adjudication; only if all explicit gates PASS may the already-conditionally-approved one I2 256-step CPU run occur.
