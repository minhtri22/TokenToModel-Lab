# TTM Agent C — BC v2 F05/F06 exact-head contract re-review

**Operation:** `TTM_C_BC_V2_F05_F06_EXACT_HEAD_CONTRACT_AND_NEGATIVE_QA_REREVIEW_SINGLE_GATE`  
**Date:** 2026-11-17 · **Role:** Agent C (Contract Owner / Technical Reviewer), **NOT the final third-party PM adjudicator**  
**Mode:** DISTINCT-FROM-B-AUTHOR CONTRACT QA · SYNTHETIC CPU ONLY · NO SCIENCE · NO GPU · NO MERGE  
**C decision:** **`C_CONTRACT_COMPATIBILITY_PASS_SCOPED_V2_F05_F06_CLOSED`**  
**Program engineering gate:** **`BC-5=HOLD_DISTINCT_FINAL_QA_AND_PM_ADJUDICATION`**

## 1. Admission and frozen source custody

Read direct GitHub PR metadata, source diff, code, receipt and CI. **The pre-remediation candidate is not the current implementation.**

| Source | Exact pin |
|---|---|
| [Draft B/C PR #36](https://github.com/minhtri22/TokenToModel-Lab/pull/36) latest evidence HEAD | `09de6a46574146d863f416e056fcf01091f3efb8`; open, Draft, not merged at review |
| **B v2 corrected implementation tested by CI** | **`a83e1526bce842761f3051dad28b90a55395a6aa`** |
| Pre-fix B PR #36 source HEAD | `dc151252070e0b118d14f3459823f8e89c6b6723` |
| Source B original v2 | `724f62a025b8ecc7c452b9ee16c926adfd2b8c7e` (historical, not substitute for corrected code) |
| C original contract PR #35 | `a5255422f695205fe45d3bba5ad748b157cb1f32` (Draft) |
| C v2 oracle, exact copied blob | `9ae5e8b189b361a496bc7bfd9ec0342bc24a7e72` |
| [Historical independent failure](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43923286066) | `1 PASS / 2 FAIL`, original PM test, job `133495938264` |
| [B corrected CI](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43928511412) | SUCCESS, Windows/Linux Python 3.12 at `a83e1526...` |
| [B core regression CI](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43928511207) | SUCCESS at same code HEAD |

The [exact B diff](https://github.com/minhtri22/TokenToModel-Lab/compare/dc151252070e0b118d14f3459823f8e89c6b6723...a83e1526bce842761f3051dad28b90a55395a6aa) contains **four and only four paths**: `src/ttm_track_b/bc_sft_bridge_v2.py`, `tests/test_bc_sft_bridge_v2.py`, the byte-identical PM negative test `tests/ttm_track_bc/test_pm_distinct_v2_manifest_negative_20261117.py`, and CI workflow `.github/workflows/track-bc-sft-interface-py312.yml`. From tested source commit `a83e1526...` to B latest PR HEAD `09de6a46...`, the diff contains **only two new documentation/receipt paths**; B implementation and tests unchanged.

### Independently read-back source file hashes

| File | Git blob SHA-1 | Source SHA-256 |
|---|---|---|
| `src/ttm_track_b/bc_sft_bridge_v2.py` | `c56d98b520fef387fab43bac87b7a9247287b17c` | `4fcbcf45d90c1ca577d3762ac4c26369d0c51e88cbe1f9bd8e172c8847c6157e` |
| `tests/test_bc_sft_bridge_v2.py` | `a27395e4b3167534b87363e4d79d5880b73670d0` | `59ddacce72c184ec8ea4d530e5f7683e9420befb567f111d0ea739f1219dfa70` |
| PM frozen `test_pm_distinct_v2_manifest_negative_20261117.py` | `3003566952116f3bc0e4ba21c7306fda460a3017` | `dcf76526cad5eb5d4491fafe8edf89408ec1d711c8bbabc93984d3935faac644` |
| B workflow `track-bc-sft-interface-py312.yml` | `be250d278fddb95c364e0ccdd57f87d56d123e0a` | `707778cee61175d421aaa382cbb9c39faac83d6ea31bb77403534edf6a5fa7f9` |

These SHA-256 values were recomputed from fetched source content using an independent SHA-256 implementation that passed empty and `abc` known vectors; source blobs were fetched by **exact B CI commit**, not branch-name lookup.

## 2. F05/F06 remediation read directly in B code

**BC-QA-F05 PASS_C_NEGATIVE:** `_check_manifest_shape` now requires `m.get("bridge_schema")==BRIDGE_SCHEMA`, with expected `ttm.bc.c_string_to_b_bytes.v2`, and raises `ValueError("BRIDGE_SCHEMA_VERSION_MISMATCH")` for omitted, fake aliases, invalid types or older names. The manifest can have all seven original bytes and hashes valid, yet the forged `bridge_schema` is **rejected**. B authors did not mutate or rehash the seven original artifact files.

**BC-QA-F06 PASS_C_NEGATIVE:** `verify_bundle` checks `manifest_path=path/"manifest.json"` and explicitly rejects `is_symlink() or not is_file()` before `read_bytes()`. A symlink to an **external but byte-identical canonical manifest** is rejected. Missing filename is already rejected by the file-set guard (`BUNDLE_FILE_SET_MISMATCH`), whereas a directory occupying `manifest.json` fails `SYMLINK_OR_MISSING_MANIFEST`; either is fail-closed.

**Security scope:** these are **path-level** checks. They are not atomic with `read_bytes()`; do not certify TOCTOU-resistant `O_NOFOLLOW` or Windows HANDLE / junction / all-reparse-point safety. Trusted immutable CI bundle root only, no production untrusted path admission.

## 3. Contract controls A01–A16

| Control | C exact-head verdict | Evidence |
|---|---|---|
| A01 byte namespace 0..255 vs specials 256..262 | **PASS_C_SCOPED** | B v2 source immutable relative to original v2; C 19 regression |
| A02 strict UTF-8 C-string→B-byte codec | **PASS_C_SCOPED** | NUL, multibyte Vietnamese, surrogate negative, separate byte-only path |
| A03 role provenance and mask rejection | **PASS_C_SCOPED** | independent manual wire and per-bit forged flags |
| A04 +1 input/target alignment | **PASS_C_SCOPED** | exact `x,y`/role mask known-answer |
| A05 assistant EOT and final EOS supervision | **PASS_C_SCOPED** | user EOT ignored; no double EOS |
| A06 masked CE + valid denominator | **PASS_C_SCOPED** | ignore=-100; valid-target loss oracle |
| A07 actual B loss callsite | **PASS_C_SCOPED** | `cross_entropy_valid` source and prior C CPU test |
| A08 right padding, no cross-dialog packing | **PASS_C_SCOPED** | physical fixed 32 inputs; masks/labels 3/3 |
| A09 causal future isolation | **PASS_C_SCOPED** | unchanged synthetic P02 CPU probe |
| A10 contextual prompt gradient | **PASS_C_SCOPED** | direct prompt CE zero, contextual gradient >0; no optimizer |
| A11 model context limit | **PASS_MODEL_BOUND_PATH_SCOPED** | actual pack max_len33; generic oracle max257 is not training API authorization |
| A12 versioned metadata checkpoint | **PASS_C_SCOPED** | `sft_checkpoint.v2` is metadata-only, weights NOT_CREATED, resume=false; legacy rejected |
| A13 byte provenance and source flags | **PASS_C_SCOPED** | structured role intent, `DECLARED_UNVERIFIED` authenticity not mistaken for independent origin attestation |
| A14 seven physical hashes, LF and mutation | **PASS_C_SCOPED** | new negative suite and independent 7/7 GitHub SHA |
| A15 actual B code used at C entry | **PASS_C_SCOPED** | review branch parented at exact `a83e...`; C 19 tests import B source and same C oracle |
| A16 final distinct engineer QA and owner resources | **HOLD_PM_DISTINCT_FINAL** | C is not the final independent reviewer; owner Windows V3/resource dissent remains unresolved |

BC-F01..F04 previously passed on prior B v2 source remain **PASS_C_COMPATIBILITY_SCOPED**, with **no new regression found** in the amended exact B code. New BC-QA-F05 and BC-QA-F06 both **PASS_C_SCOPED**.

## 4. Agent C's separate exact-candidate tests (not B-authored)

A new branch `review/ttm-c-bc-v2-f05-f06-20261117` was created **from exact B tested code `a83e1526bce842761f3051dad28b90a55395a6aa`**. It adds only C tests and a review workflow; it did **not** edit B implementation, B PR #36, main or lineage.

- [C cross-track workflow run #43932738585](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43932738585): **SUCCESS**; Linux job **133529185493**, Windows job **133529184970**, Python3.12, PyTorch CPU2.10.0.
- **C fresh F05/F06 negative suite:** **15/15 PASS** on each OS, **0 skipped**. Checks positive bundle, fake alias, missing, wrong types, symlink to external byte-identical manifest, missing/non-file, all seven actual bytes, all seven manifest hashes, recomputed forged semantic bytes, old checkpoint/schema, LF/CRLF, role/mask/target and exact Git blob pins.
- **C original 19 cross-track regression:** **19/19 PASS** on each OS, **0 skipped**; includes actual bounded P02 CPU forward/backward, valid-target CE, causal/right padding, contextual gradients, **optimizer steps 0**, no science.
- **Historic PM independent FAIL preserved:** [run #43923286066](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43923286066) has original 3 cases: valid fixture PASS; forged bridge alias FAIL; external symlink FAIL. The unmodified original PM 3-case suite ran 3/3 PASS on B author CI at repaired B source, but does not by itself count as a fresh PM reviewer execution.
- **Agent C first independent run failed**: [run #43932448976](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43932448976): C's new case `test_06` wrongly demanded error `SYMLINK_OR_MISSING_MANIFEST` for an **absent filename**; B correctly rejects earlier as `BUNDLE_FILE_SET_MISMATCH`. Only the C assertion/comment changed in the next review commit, **not B code**. Second C run #43932738585 succeeded 15+19 per OS; first error remains in CI history.

**Independence statement:** the 15 new cases and the separate 19-case cross-track regression were written/curated by **Agent C**, not Agent B. This is **distinct contract QA from the implementer**, but it is **not** the PM's third-party final independent adjudication.

## 5. Physical artifact SHA and semantic re-validation

Original pre-fix GitHub commit `dc151252...` and newest corrected B evidence HEAD `09de6a46...` contain **byte-identical 8/8 Git blobs** for `artifacts/ttm-abc/bc-sft/v2/actual_bytes/*.json` plus `MANIFEST_CANONICAL_LF.json`. **No artifact regeneration required.** All seven are canonical sorted compact JSON UTF-8 with one terminal LF and **no CRLF**.

| Exact original artifact | Independently recomputed SHA-256 at B new HEAD |
|---|---|
| `tokenizer.json` | `c1d7f880382d28eb099fcae6a620b4587228486d6a1a149cf99dc7bcc527bbf5` |
| `chat_template.json` | `6c818dda5ce614483406864bd7289a5131b8e0e2826c732b767afec3aa63b100` |
| `serialized_inputs.json` | `03f351b4ddfddaad7fa465ee19e538a9ed199d3602bd772185ac49bc58c2a6e0` |
| `target_masks.json` | `4a70ef9b946f1a262dc3210c82098ea3e138ea406ffd4f31bc23d2e82149cc50` |
| `target_labels.json` | `9d1a3f3d7f0e910fc318fe6ff5e0353a926d50e45acc278f06cd5b9f610b90cf` |
| `config.json` | `c3bd53773db03bb5c86d4279f94453c022d77d198ad49cefe4ab11bbf2420423` |
| `checkpoint_schema.json` | `63c73293084fc3a30f77da375e694f443e972d049ec667d9d20e09b849920888` |

**Manifest:** `17f91e6d3881404909b6cb8c1cd4a2272a92f8b67c179806c2af68768e86d0a2`; Git blob `cba9f094d5d05787ffb50ffdef849049945bbfc8`. It retains exact `bridge_schema=ttm.bc.c_string_to_b_bytes.v2`, `schema=ttm.bc.synthetic.sft_pack.v2`, `checkpoint_schema=ttm.bc.synthetic.sft_checkpoint.v2`, and canonical version `ttm.bc.canonical_json_utf8_sorted_compact_lf.v2`.

**Independent semantic reconstruction (not only SHA check):** all **3/3 real committed synthetic records** had correct IDs `0..255`, BOS/SYS/USER/ASSIST/EOT/EOS, one-role-per-span source encoding; `x` length32, one-token shift, assistant EOT/final EOS targets, user/system/pad ignored; reconstructed `serialized_ids`, raw flags, shifted flags, labels `y`, valid counts and source SHA matched each artifact record; TRAIN 2 vs VAL 1, not real scientific data. Source role origin remains `DECLARED_UNVERIFIED`. The checkpoint definition explicitly `METADATA_ONLY_NO_ACTUAL_CHECKPOINT`, `weights=NOT_CREATED`, `resume_enabled=false`.

## 6. Gate outcome, boundaries, PM handback

| Gate | C adjudication |
|---|---|
| BC-QA-F05 | **PASS_C_NEGATIVE_SCOPED** |
| BC-QA-F06 | **PASS_C_NEGATIVE_SCOPED** |
| BC-F01..F04 | **PASS_C_COMPATIBILITY_SCOPED, regression PASS** |
| BC-0..BC-4 | **PASS_C_ENGINEERING_CONTRACT_SCOPED** |
| BC-5 | **HOLD_DISTINCT_FINAL_QA_PM_ADJUDICATION** |
| B-M3 | Prior PM `PASS_ADJUDICATED_SCOPED`, **V3 historical HOLD** and `HOLD_PEAK_ACCOUNTING` reviewer dissent all preserved |
| C M4 | Prior `PASS_DESIGN_SCOPED` unchanged; real data rights HOLD |
| Science / GPU / TEST64 / FRESH16 / FINAL24 / merge | **NOT_AUTHORIZED, NOT_EXECUTED** |

**No** Windows V3 rerun, no optimizer training, no model weights loaded, no new TEST, no merge PR #33/#34/#35/#36. **No** direct changes by Agent C to B implementation, `main` or `lineage.md`. Security bounded: `is_symlink()/is_file()` path guard is not atomic and does not prove arbitrary Win32 reparse/junction safety.

**Final Agent C decision:** **`C_CONTRACT_COMPATIBILITY_PASS_SCOPED_V2_F05_F06_CLOSED`** on B's corrected exact source `a83e1526...`. It does **not** by itself authorize `BC_INTERFACE_PASS_ENGINEERING_SCOPED`.

### Bước thực hiện tiếp theo — duy nhất

`TTM_PM_BC_V2_F05_F06_DISTINCT_FINAL_QA_AND_ENGINEERING_GATE_ADJUDICATION_SINGLE_GATE`

Third-party reviewer/PM checks this pinned evidence packet and gives one **`BC_INTERFACE_PASS_ENGINEERING_SCOPED`** or **`HOLD_BC_INTERFACE`** decision. No micro-permits or V3 rerun.
