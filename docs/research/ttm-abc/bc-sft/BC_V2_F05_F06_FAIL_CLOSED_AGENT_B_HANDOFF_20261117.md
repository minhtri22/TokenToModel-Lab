# Agent B — BC v2 manifest fail-closed F05/F06 · exact-head handoff

**Operation:** TTM_PM_BC_V2_MANIFEST_FAIL_CLOSED_F05_F06_EXACT_HEAD_AMENDMENT_AND_DISTINCT_RERUN_SINGLE_GATE  
**Date:** 2026-11-17 · **Role:** Agent B Implementation Owner · **Mode:** implementation and synthetic engineering QA only, no SFT science / GPU / merge / V3 rerun.  
**PR:** [Draft #36](https://github.com/minhtri22/TokenToModel-Lab/pull/36), branch integration/ttm-bc-synthetic-sft-interface-20261116, stacked on frozen Track B PR #34.  
**Exact pre-fix HEAD:** dc151252070e0b118d14f3459823f8e89c6b6723.  
**Exact corrected source + tests + CI HEAD:** a83e1526bce842761f3051dad28b90a55395a6aa. Subsequent commits should contain ONLY evidence and documentation; require fresh QA on any further code/test changes.  
**Original source tested for F05/F06:** 724f62a025b8ecc7c452b9ee16c926adfd2b8c7e.  
**PM-authored frozen independent test source:** reviewer commit e26a754c0bb6c3ca435e175e03a9fd7c62a8967b, Git blob 3003566952116f3bc0e4ba21c7306fda460a3017. The identical test bytes are copied into the PR #36 branch for exact-source CI and were **not edited**.

## 1. Source diff, intentionally minimal

In src/ttm_track_b/bc_sft_bridge_v2.py:
- F05: _check_manifest_shape() now requires manifest.get("bridge_schema") == BRIDGE_SCHEMA. Any absent, wrong type, obsolete version or fake alias raises ValueError("BRIDGE_SCHEMA_VERSION_MISMATCH"), before seven artifact readback. Existing pack, checkpoint, canonical, B/C source SHA and seven hash guards remain.
- F06: verify_bundle() now binds manifest_path=path/"manifest.json", and **before** read_bytes() rejects if manifest_path.is_symlink() OR not manifest_path.is_file(), via ValueError("SYMLINK_OR_MISSING_MANIFEST"). Seven existing artifact symlink checks remain.
- Added 2 B regression tests (test_25, test_26) to tests/test_bc_sft_bridge_v2.py. No baseline GPT Core, v1 interface, C source or data-manifest artifact code/bytes changed. The third-party reviewer 3-case test copied byte-identically, plus one CI workflow step.

**Precise Git diff:** compare [pre-fix→QA source](https://github.com/minhtri22/TokenToModel-Lab/compare/dc151252070e0b118d14f3459823f8e89c6b6723...a83e1526bce842761f3051dad28b90a55395a6aa): 4 paths, source +8/-1, B regression +40, frozen reviewer test +59 and CI workflow +2. No existing 7 artifact files or original manifest modified.

| Changed file | Git blob SHA-1 at QA HEAD | SHA-256 of exact file bytes |
|---|---|---|
| src/ttm_track_b/bc_sft_bridge_v2.py | c56d98b520fef387fab43bac87b7a9247287b17c | 4fcbcf45d90c1ca577d3762ac4c26369d0c51e88cbe1f9bd8e172c8847c6157e |
| tests/test_bc_sft_bridge_v2.py | a27395e4b3167534b87363e4d79d5880b73670d0 | 59ddacce72c184ec8ea4d530e5f7683e9420befb567f111d0ea739f1219dfa70 |
| tests/ttm_track_bc/test_pm_distinct_v2_manifest_negative_20261117.py | 3003566952116f3bc0e4ba21c7306fda460a3017 | dcf76526cad5eb5d4491fafe8edf89408ec1d711c8bbabc93984d3935faac644 |
| .github/workflows/track-bc-sft-interface-py312.yml | be250d278fddb95c364e0ccdd57f87d56d123e0a | 707778cee61175d421aaa382cbb9c39faac83d6ea31bb77403534edf6a5fa7f9 |

Hashes read back from GitHub exact SHA; SHA-256 computed over returned UTF-8 bytes with independently checked SHA-256 implementation (empty-text and "abc" test vectors). Source Git blob is unchanged after this frozen QA HEAD.

## 2. Independent negative history, immutable

Original third-party [PM GitHub Actions FAIL #43923286066](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43923286066), job **133495938264**, Linux Python3.12:
- test_01 valid fixture = PASS.
- test_02 forged manifest bridge alias = FAIL (ValueError not raised).
- test_03 external symlink to canonical manifest = FAIL (ValueError not raised).

This is a real historical **1 PASS / 2 FAIL** and was never replaced. Original test file stays at reviewer commit e26a754c0bb6c3ca435e175e03a9fd7c62a8967b with the same byte content as PR #36's copied test. Original PM report: docs/research/ttm-abc/bc-sft/independent_review/TTM_PM_A_I1_AND_BC_V2_DISTINCT_QA_ADJUDICATION_20261117.md at the same reviewer commit.

## 3. Exact amended candidate QA on GitHub

**Source and tests are frozen at commit a83e1526bce842761f3051dad28b90a55395a6aa**.

[BC CI #43928511412](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43928511412): SUCCESS on Linux and Windows Python3.12. Both jobs executed the previously failing **same 3 PM-authored test bodies** without modification:

| Job | Python | Torch | PM negative | B v1 | B v2 incl F05/F06 | C oracle | Synthetic P02 CPU |
|---|---|---|---|---|---|---|---|
| Windows job 133514324483 | 3.12.10 | 2.10.0+cpu | **3/3 PASS, 0 SKIP** | 29/29 | 26/26 | 18/18 | PASS |
| Ubuntu job 133514325422 | 3.12.16 | 2.10.0+cpu | **3/3 PASS, 0 SKIP** | 29/29 | 26/26 | 18/18 | PASS |

Windows was able to create a symlink in this CI. If a later native Windows host cannot create one, only that later test is NOT_EXECUTED_PLATFORM_RESTRICTION, **not** PASS. The current Windows Actions test itself genuinely passed.

Actual P02 synthetic forward/backward: 7 assistant labels, 25 directly ignored, independent NLL oracle tolerance met, context gradient nonzero, direct prompt-label CE zero, causal/padding isolation true, optimizer_steps=0, science_executed=false.

Previous Track B [regression CI #43928511207](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43928511207) also SUCCESS on both OS at the **same** source HEAD: Windows PS5.1 job 133514322980, Linux job 133514323517.

**Independence:** the three negative *test cases* were written on the PM distinct reviewer branch, but this passing rerun was driven by the **B branch's GitHub Actions**. It proves those original counterexamples fail closed on new code, not final independent adjudication or C signoff on the new commit.

## 4. Old seven SHA artifacts + manifest unchanged

Original seven file SHA-256 values are preserved verbatim; no data regeneration for testing, and Git blob SHA-1 before/after source fix is exactly equal for each saved artifact and manifest.

| File | SHA-256 unchanged |
|---|---|
| tokenizer.json | c1d7f880382d28eb099fcae6a620b4587228486d6a1a149cf99dc7bcc527bbf5 |
| chat_template.json | 6c818dda5ce614483406864bd7289a5131b8e0e2826c732b767afec3aa63b100 |
| serialized_inputs.json | 03f351b4ddfddaad7fa465ee19e538a9ed199d3602bd772185ac49bc58c2a6e0 |
| target_masks.json | 4a70ef9b946f1a262dc3210c82098ea3e138ea406ffd4f31bc23d2e82149cc50 |
| target_labels.json | 9d1a3f3d7f0e910fc318fe6ff5e0353a926d50e45acc278f06cd5b9f610b90cf |
| config.json | c3bd53773db03bb5c86d4279f94453c022d77d198ad49cefe4ab11bbf2420423 |
| checkpoint_schema.json | 63c73293084fc3a30f77da375e694f443e972d049ec667d9d20e09b849920888 |
| manifest.json | 17f91e6d3881404909b6cb8c1cd4a2272a92f8b67c179806c2af68768e86d0a2 |

New CI independently ran write_bundle() and verify_bundle() successfully on both OS and produced the same seven field digests. Two new CI evidence ZIP archives: 14256344475 Windows (ZIP SHA256 586228436aa6d17bb478516f162603f0ef11ab98f4cc03b149c76504737f6ed3), 14256313563 Linux (ZIP SHA256 d38f7e514c55c0387826ff1a5e83e678291fe2a900d649ecdf1fdcda5767ae78). ZIP SHA can differ due to metadata; actual seven canonical JSON SHA stay fixed.

## 5. Scope and remaining security limits

This remediation adds **path-level fail-closed checks**, not a comprehensive filesystem guarantee. Path.is_symlink() and is_file() are not atomic with read_bytes() (TOCTOU). On Windows, junctions and other reparse points, including parent-directory substitution, may require dedicated Win32 HANDLE/FILE_FLAG_OPEN_REPARSE_POINT checks. This engineering QA does **not** certify arbitrary hostile filesystem roots, all reparse-point types, race-resistant sandbox containment, or production execution. No changes to the original seven artifact symlink checks or their assumptions. The bundle root must be trusted for the scoped synthetic evidence.

## 6. Gate table

| Gate | Correct status |
|---|---|
| BC-QA-F05 | PASS_AUTHOR_REMEDIATED_AND_PM_FROZEN_TEST_RERUN (new code) |
| BC-QA-F06 | PASS_AUTHOR_REMEDIATED_AND_PM_FROZEN_TEST_RERUN (new code, Windows/Linux no skip) |
| BC-0, BC-1, BC-2, BC-3 | PASS_EXISTING_SCOPED + amended source CI |
| BC-4 | PASS_AUTHOR_CI_FAIL_CLOSED_SCOPED; independent amended exact-HEAD verdict **PENDING** |
| BC-5 | HOLD_DISTINCT_NEW_INTEGRATION, not auto-PASS |
| C Part B | Prior PASS_C_COMPATIBILITY_SCOPED for older source, **exact new amendment C review PENDING** |
| B-M3 | Older PM PASS_ENGINEERING_BASELINE_SCOPED with V3 HOLD and reviewer peak-accounting dissent preserved |
| SFT science/GPU/TEST/merge | NOT_AUTHORIZED / NOT_EXECUTED |

**B's allowed handback:** B_V2_F05_F06_IMPLEMENTED · AUTHOR_QA_PASS_SCOPED.  
**Overall BC:** HOLD_PENDING_AGENT_C_AND_DISTINCT_ADJUDICATION.

**Bước thực hiện tiếp theo — duy nhất:** TTM_BC_V2_F05_F06_AGENT_C_EXACT_CANDIDATE_CONTRACT_REVIEW_HANDOFF. Agent C must read the PR #36 **new exact HEAD**, confirm source diff and original three PM negatives, re-evaluate A01–A16 as scoped, then distinct reviewer and PM decide whether BC-5 closes. No micro-permits, no science, no merge.
