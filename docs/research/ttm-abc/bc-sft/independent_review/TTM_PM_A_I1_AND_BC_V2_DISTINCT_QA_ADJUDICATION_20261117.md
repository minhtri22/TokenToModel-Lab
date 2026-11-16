# TTM PM — A I1 scoped closure + B/C v2 distinct exact-candidate adjudication

**Operation:** `TTM_PM_TRACK_A_I1_CLOSURE_AND_BC_V2_DISTINCT_QA_INTEGRATED_ADJUDICATION_ONEPACK`  
**Date:** 2026-11-17 · **Source of truth:** GitHub readback; all review evidence additive on `review/ttm-pm-a-i1-bc-v2-distinct-source-20261117` branched from frozen B integration HEAD. **No merge, no real SFT, GPU, scientific model execution, historical TEST access or mutation of A/B/C branches.**

## I. Track A: PM accepts I1 measurement, keeps I2 blocked

- [Draft PR #33](https://github.com/minhtri22/TokenToModel-Lab/pull/33) remains open/unmerged at **`771314c07ba061ebeb1baa87018248ed73181079`**.
- **Exact executable I1 source:** `ec197b5f00d3a037420390edd11ee55047e1d37f`; [independent evidence](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/REVIEW.md) 35/35 source logic + 38/38 owner-native custody, 80/80 cases across 5/5 groups and fixed fixture SHA256 `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`. The current PR HEAD added evidence/status/handoff only after exact reviewed code.
- **PM gate:** `A_I1=PASS_SCOPED_MEASUREMENT` accepted without a claim of scientific capability. `I2=NOT_EXECUTED`; release preflight remains **`HOLD_OWNER_INTERNAL_I1_NOT_PASS`** (exit 2, historical pointer); TOCTOU no-overwrite gap and wrapper receipt/metadata binding are release risks. A historical HOLD is preserved. No automatic pointer rewrite, nonce, checkpoint access or I2 launch.
- **PM release ruling:** `HOLD_I2_RELEASE`; no executable I2 authorization. A may only design prospective fixes pending owner release authority.

## II. B/C v2 source and CI custody

- B [Draft PR #36](https://github.com/minhtri22/TokenToModel-Lab/pull/36) at **`dc151252070e0b118d14f3459823f8e89c6b6723`**; tested B code `724f62a025b8ecc7c452b9ee16c926adfd2b8c7e`. GitHub compare shows only eleven new docs/evidence + seven physical artifacts/manifest since tested code (no subsequent executable or test edits). B v2 bridge blob `f2cc02821efa4f9628964657d90c7a98c4d67e13`.
- B v2 [author CI](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43918069534): Windows Python3.12.10 & Linux Python3.12.16 passed original 29/29, new 24/24, C's exact 18/18 routed via B bridge, finite P02 CPU forward/backward with **zero optimizer**.
- C [Draft PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35) at **`a5255422f695205fe45d3bba5ad748b157cb1f32`**; C Part B [CI](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43919831949) 19/19 separately authored acceptance checks on Windows/Linux Python3.12; C verdict `C_CONTRACT_COMPATIBILITY_PASS_SCOPED`. C is the contract author and **not** the third-party distinct reviewer.

**New PM-independent byte readback:** reviewer fetched all 7 GitHub actual-byte JSON files at exact B PR36 HEAD, computed SHA-256 with an independently implemented SHA-256 over UTF-8 bytes (validated against public test vectors `abc` and empty text), compared each digest with its corresponding `MANIFEST_CANONICAL_LF.json` entry, and checked each file's JSON structure, one final LF, no CRLF and canonical compact sorted serialization. **7/7 MATCH**. Manifest itself independently SHA-256 matched `17f91e6d3881404909b6cb8c1cd4a2272a92f8b67c179806c2af68768e86d0a2`. Independent byte-domain role/mask/shift reconstruction for all three synthetic records **3/3 MATCH** (TRAIN/TRAIN/VAL, valid assistant label counts 7,4,5, no role-authentication claim).

The above independently supports `BC-F01..BC-F04=CLOSED_ENGINEERING_SCOPED` and C's Part B acceptance for their scoped functional assertions. It **does not** establish a full fail-closed manifest boundary or a real SFT checkpoint.

## III. Fresh PM third-party negative tests — 1 PASS / 2 FAIL

**Exact B implementation under test:** unchanged B v2 source from `724f62a...`, present at PR36 HEAD `dc151252...`. The PM created *new*, not B/C-authored reviewer tests on a separate branch:
`tests/ttm_track_bc/test_pm_distinct_v2_manifest_negative_20261117.py`; runner workflow `.github/workflows/track-bc-pm-distinct-manifest-qa-py312.yml`. No B/C source files modified.

**Independent GitHub Actions** [run #43923286066](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43923286066) Python **3.12 Linux**, **FAILED**, with:
- `test_01_valid_fixture_is_accepted` **PASS**.
- `test_02_forged_bridge_schema_must_fail_closed` **FAIL**: `AssertionError: ValueError not raised : BC-QA-F05: forged bridge alias accepted`.
- `test_03_manifest_symlink_must_fail_closed` **FAIL**: `AssertionError: ValueError not raised : BC-QA-F06: manifest symlink accepted`.
- `Ran 3 tests in 0.022s; FAILED (failures=2)`; the preflight asserts Python 3.12, imports the exact B bridge, and emits `BC_DISTINCT_NO_MODEL_NO_SCIENCE`. No Torch or model execution in this reviewer run.

**Root causes pinned by source readback:**

1. **BC-QA-F05 — forged bridge version accepted.** `src/ttm_track_b/bc_sft_bridge_v2.py` lines **273–285** `_check_manifest_shape` checks pack, checkpoint, canonical, B/C source SHA and seven digest string shapes, but **not** `m.get("bridge_schema")==BRIDGE_SCHEMA`. Rewriting only `manifest.json` to a different arbitrary `bridge_schema` with correct v2 canonical bytes and all seven original artifact hashes still passes `verify_bundle()`. Violates explicit versioned bridge binding / fail-closed metadata.
2. **BC-QA-F06 — manifest symlink accepted.** In `verify_bundle` lines **361–379**, the code rejects a symlink for the root and each of seven artifact files, but not `path/"manifest.json"` before `.read_bytes()`. A symlink to an external copy of valid canonical manifest bytes is accepted; violates the stated no-symlink manifest/byte-custody boundary. This is a *synthetic filesystem QA* issue, not evidence of malicious data in the real repo.

Neither counterexample changes the valid 7/7 fixture hashes or invalidates prior author CI. The two new tests are **real executed independent runtime FAIL**, not just static speculation; the failures were on the GitHub-hosted Linux runner, not owner Windows. Both tests were deliberately written to demand rejection and correctly fail against the current source; do not relabel them PASS.

**Minimal remediation (Agent B, one amendment, no micro-permit):**
- In `_check_manifest_shape`, require `m.get("bridge_schema")==BRIDGE_SCHEMA` and reject all unknown aliases. Unit negative with forged but canonicalized `manifest.json` and unchanged 7 artifact hashes.
- In `verify_bundle`, reject symlink `manifest.json` before reading bytes; preserve the existing seven-file symlink guards and file-set check. Negative link to a valid external canonical manifest must fail on platforms that support symlink creation. Ensure root/parent reparse-point policy explicitly scoped rather than silently relied upon.
- Retain the seven immutable v2 source artifact bytes and SHAs if unaffected; a source-code change necessarily requires a **new exact candidate source SHA and a new CI/reviewer run**, not tampering with existing evidence. Preserve this failing reviewer run as historical.

## IV. PM gate matrix

| Gate | PM result at currently reviewed exact source | Notes |
|---|---|---|
| A I1 | `PASS_SCOPED_MEASUREMENT` | review 35/35; 38/38; 80/80; source unchanged |
| A release/I2 | `HOLD_RELEASE_PREFLIGHT` / `NOT_EXECUTED` | no owner release GO; TOCTOU advisory |
| BC-0 | `PASS_SOURCE_PIN_AND_BYTE_READBACK_SCOPED` | B/C exact source; seven real JSON SHA + manifest |
| BC-1 | `PASS_TYPED_CODEC_SCOPED` | B author + C Part B + independent 3-row reconstruction |
| BC-2 | `PASS_ROLE_SHIFT_MASKED_CE_SCOPED` | B author + C Part B tests, no independent model training |
| BC-3 | `PASS_SYNTHETIC_CPU_AUTHOR_AND_C_PARTB_SCOPED` | P02 forward/backward zero optimizer |
| BC-4 | **`HOLD_DISTINCT_FAIL_CLOSED_MANIFEST_F05_F06`** | functional 7/7 hashes PASS; version/symlink negatives FAIL |
| BC-5 | **`HOLD_DISTINCT_QA_FAILED_2_OF_3`** | must rerun new independent exact-candidate negatives after minimal fix |
| B M3 | `PASS_ENGINEERING_BASELINE_SCOPED_BY_PRIOR_PM_WITH_PEAK_COUNTER_DISSENT` | V3 `HOLD_NATIVE_QA` immutable; do not transfer M3 permission to SFT |
| C M4/Part B | `PASS_DESIGN_SCOPED` / `PASS_C_COMPATIBILITY_SCOPED` | no production SFT science certification |
| Real SFT / GPU / TEST / merge | `NOT_AUTHORIZED` | Draft PRs unchanged |

**One next operation**: `TTM_PM_BC_V2_MANIFEST_FAIL_CLOSED_F05_F06_EXACT_HEAD_AMENDMENT_AND_DISTINCT_RERUN_SINGLE_GATE`. Implement two targeted guards in Agent B PR36, rerun the same 3 independent tests on exact amended candidate plus existing B/C regression in one batch, obtain C contract confirmation on new SHA, then PM adjudicates PASS/HOLD without new science, no V3 rerun and no micro-permit.

**Review independence caveat:** Source/QA authored by a distinct PM ChatGPT session; publication uses the linked owner's GitHub credentials and does not establish an independently authenticated human reviewer.
