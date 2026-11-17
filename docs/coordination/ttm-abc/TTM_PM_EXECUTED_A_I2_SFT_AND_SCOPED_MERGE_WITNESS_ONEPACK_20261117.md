# TTM PM — EXECUTED integrated evidence OnePack for A-I2 · real SFT · scoped merge

**Operation:** `TTM_PM_ABC_EXECUTED_INTEGRATED_WITNESS_AND_SCOPED_MERGE_SOURCE_QA_ONEPACK`  
**Date:** 2026-11-17 · **Mode:** independent GitHub exact-byte/source audit + **real cross-platform GitHub Actions source-only QA**. No new model run, GPU, real SFT, I2, native one-shot, TEST or merge-to-main.
**Previous owner ruling**: [three-way evidence-based HOLD](https://github.com/minhtri22/TokenToModel-Lab/blob/d0aefb35838245ec14f5dc435835dea5433d5077/docs/coordination/ttm-abc/TTM_PM_ABC_OWNER_SINGLE_INTEGRATED_GO_HOLD_ADJUDICATION_20261117.md) preserved. PM now **performed the independently controlled scoped-merge candidate work instead of requesting agents A/B/C to repeat it**.

## 1. New real work performed by PM

1. Read/froze [PR #34](https://github.com/minhtri22/TokenToModel-Lab/pull/34), [#36](https://github.com/minhtri22/TokenToModel-Lab/pull/36), [#37](https://github.com/minhtri22/TokenToModel-Lab/pull/37), and [#35](https://github.com/minhtri22/TokenToModel-Lab/pull/35), and existing upstream PM distinct PASS/known HOLD. Excluded source from [PR #28](https://github.com/minhtri22/TokenToModel-Lab/pull/28) and [#33](https://github.com/minhtri22/TokenToModel-Lab/pull/33) where Q001 pre-execution parent still HOLD.
2. Constructed a **real Git tree** by taking exact B37 tree `572c39608b909a9661e67b8650aab20b9c9b1a13` at `ff4304e04f44de69a07cd767b2a7f400d6e95e88` and overlaying **all 30 Git blob SHAs of C35** at `4efe93ce0a3910c449972b3f7e9911a004fe2b3c`. Result **source tree `8518da41b7287a8f4b0bc96dc0e6b0228f097af7`**, staged commit **`9b096b6cf5e9486df1a9ab7220974af3fac0f496`**. The commit has B37 as its parent; this is a *review-stage composition*, not a GitHub merge of the source PRs into main.
3. Opened [review-only **Draft PR #38**](https://github.com/minhtri22/TokenToModel-Lab/pull/38), base **`design/ttm-b-abc-shared-feasibility-20261117`** (B37 source), not main; source-only independent PM QA test and CI workflow added in two files on top. Final QA HEAD **`123629595c64c694bfcc2c932037f700628d7253`**.
4. Independently verified the exact source-file inventory: PR34 **11**, PR36 **27**, PR37 **8**, PR35 **30** = **76 unique file paths**, each `added`, no duplicate, no modifications/deletions relative to main `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`. From B37 to source candidate, **exactly 30 C files added and all 30 original C Git blob SHAs preserved**; no B runtime code was modified. From main to source candidate, **76 files added only**. PM's two QA-only files are **excluded** from the 76-file source scope.
5. Executed new independent source tests on the **combined checkout**: Git blob pins of C registry/B remap/B bridge/T4 BPE/C oracle, A root pointer and 37/26/14 typed crosswalk (63 distinct logical fields), 7 physical artifact sha256 **from committed Git objects**, preserved exact B dispositions, and hard BPE-vs-special ID collision. No private weights or real checkpoint loaded.
6. Executed original Track C synthetic contract tests again **only on this new combined tree**, not to re-prove frozen C M4 science. No B Core synthetic train/resume repeated; prior source-identical B/BC cross-platform QA remains separately anchored. Cross-platform runner used Python3.12 stdlib (`-S -B`), no `pip install`, GPU, model, or external data.

## 2. Verified CI and exact evidence

| Workflow (at candidate SHA `123629...`) | Windows 3.12 | Linux 3.12 | Outcome |
|---|---|---|---|
| [PM combined source QA run **#44026751082**](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/44026751082): PM source tests | **5/5 PASS** | **5/5 PASS** | 0 failed, 0 skipped |
| Same PM run, original C tests on combined source | **60/60 PASS** | **60/60 PASS** | 0 failed, 0 skipped |
| [C source-only workflow run **#44026750768**](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/44026750768) | **18/18 PASS** | **18/18 PASS** | Independent workflow, same 18 already included within C's 60; **do not double count as unique** |

**Source identity:** PR38 vs B37 = **32 added files**, namely C exact **30/30 blobs** and PM source-only QA **2** (review-only). Original external approvals:
- [BC v2 PM distinct engineering PASS](https://github.com/minhtri22/TokenToModel-Lab/blob/82aaf2a881bd677afd8f6e600eb570aea897fdba/docs/research/ttm-abc/bc-sft/independent_review/BC_V2_F05_F06_PM_FINAL_DISTINCT_ENGINEERING_ADJUDICATION_20261117.md): no B code change in combined source.
- [ABC V4 design alignment PASS](https://github.com/minhtri22/TokenToModel-Lab/blob/fa28b89e4ee93b3de4561deaa2a7b9a086fa340b/docs/coordination/ttm-abc/TTM_PM_ABC_CCR01_F01_F03_FINAL_DISTINCT_EXACT_SOURCE_ADJUDICATION_20261117.md).
- [Full **76-file Git blob provenance manifest**](https://github.com/minhtri22/TokenToModel-Lab/blob/3759081be19fde97196a10cec23fe25abaff5158/artifacts/ttm-abc/governance/TTM_PM_ABC_76_FILE_COMPOSITE_SOURCE_MANIFEST_20261117.json) (must link new HEAD eventually).

### Preserved failed initial QA and corrected custody method

Initial [PM CI **#44026585729**](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/44026585729) = Linux PASS, Windows FAIL. PM independently read Windows failure logs: **Windows checkout CRLF smudged text worktree bytes**, making Git blob SHA1 and 7 checked-in artifact raw SHA256 differ from committed Git data. This was a **test-harness byte-source error**, not observed corruption of source Git objects. PM amended only `tests/ttm_pm_abc/test_pm_bc_c_combined_source_only_20261117.py` at commit **`123629595c64c694bfcc2c932037f700628d7253`** to use local `git cat-file blob HEAD:path` for exact committed Git bytes. New workflow passed Windows/Linux with exact source and artifact hashes, while old failed run remains in GitHub. **Real on-disk Windows checkout fidelity and production filesystem atomicity remain separate R5/owner-runner issues; this CI does not certify those.**

## 3. PM triage of three requested owner choices after doing the work

| Choice | Updated evidence availability | Formal PM adjudication now |
|---|---|---|
| **A-I2 one-shot** | A I1 source/scorer + V4 accepted design remain locked; 65/3 V4 native cases not executed, preflight historical exit2, signer/principal/epoch/NTFS writer race/ledger/global-slot checkpoint-bound execution still lack a complete authorized witness. Composite merge candidate **intentionally excludes A parent**. | **`HOLD_A_I2_RELEASE`** (unchanged, not re-open a QA micro-permit) |
| **Real SFT science** | B M3, BC v2 and C M4 design already scoped PASS; new exact combined source QA PASS **does not provide actual historical T4 weights**, source corpus rights/gold/heldout, token-to-byte spans, stop protocol, measured resource/FLOPs or frozen independent exact real-candidate QA. Direct BPE T4 IDs257–2047 ↔ BC role special IDs257–262 remain **INCOMPATIBLE**, external role-sidecar design not implemented. | **`HOLD_REAL_SFT_RELEASE`** (unchanged) |
| **Scoped merge B34/BC36/B37 + C35** | **New real 76-file Git tree**, exact additive blob identity, independent cross-platform PM source QA (5+60 per OS) plus preexisting B/BC QA from immutable exact source. Zero B runtime changes and no A preexec. Draft PR38 only a reviewer vehicle. | **`PASS_SCOPED_COMPOSITE_SOURCE_QA`**. **`HOLD_MERGE_EXECUTION`** until owner exact merge set, main protection/rules readback and any final required merged-tree runner/security QA |

**New authoritative incremental progress:** the merge candidate's *source QA blocker* is **closed for this exact tree**. Do not convert a source-level QA PASS into an unconditional merge authorization, but do not restart C/B contract design or rerun their existing science-adjacent gates either.

### Scope of a future authorized merge set (candidate, not command)

On unchanged main, a content-equivalent target **could** use B chain `#34 → #36 → #37` followed by exact C data from `#35`, or equivalent independently reviewed staging order (all current 76 changed paths are disjoint). All source C files are already present in the composite reviewer commit, so do **not** merge PR35 a second time after integrating a branch with those exact paths. **Do not merge PR38 itself**: its two tests/workflow are PM reviewer-only, and its target base is B37, not main. Future release needs scoped path manifest/sha, confirmed branch protections/owner decision and exact candidate combined-tree QA. Source is safe to *review*, not approved to merge.

A separate clean-scoped Track A I1 source/doc candidate, if desired, must exclude #28 HOLD parent; it is **not** created here and no A source is claimed to be present in the B/C/C candidate. The historical negative and reviewer dissent remain linked in PR/lineage candidates; do not overwrite.

## 4. R0–R8 and owner authority — one consolidated decision packet

- **R0:** ABC source and candidate integration **PASS_SCOPED for 76-file reviewer tree**. Exact real I2/SFT runnable source binding remains HOLD.
- **R1:** I1 metric PASS scoped; real C gold/rater/byte-denominator validation HOLD.
- **R2:** private data/rights/family split/heldout **OWNER_PRIVATE_CUSTODY_UNVERIFIED**, not a claim of invalid rights.
- **R3:** actual T4 weights + strict real loader / byte BPE span proof HOLD, direct codec collision unresolved for runtime.
- **R4:** real science owner-host/GPU resource, full session timing, watchdog/memory cap HOLD; historical B M3 scoped QA not a new SFT native permit.
- **R5:** A V4 accepted design; real Ed25519 owner signer, NTFS atomic race, ledger/TOCTOU native QA HOLD. Windows Git checkout text conversion from initial PM run is separately recorded; Git-object hashes verified in reviewer CI.
- **R6:** historical Q001 frozen test cannot be rekeyed; prospective new SFT equal-compute prereg not frozen.
- **R7:** **combined B/C/C source QA PASS** for PR38 exact candidate, **not** native/real-science QA. A V4 65 negatives+3 positives still DESIGN_ONLY.
- **R8:** no signed GO for I2/SFT or exact scoped merge. Branch protections main had HTTP 403 under current connector, so merge policy **UNVERIFIED**; GitHub `mergeable` doesn't replace permission. No PR merged.

**Decision law:** No science or merge GO from source QA alone. `PASS_SCOPED_COMPOSITE_SOURCE_QA` qualifies exact current code/docs as a review candidate; `HOLD_MERGE_EXECUTION` explicitly blocks publishing to main. If branch changes, re-pin candidate rather than use mutable HEAD.

## 5. PM final action and evidence completeness

**PM performed**: built Git tree, created isolated Draft PR38, implemented independent tests, triggered and inspected Win/Linux CI, preserved FAIL+fixed test readback, verified 76-source blob manifest, and assembled this single integrated release/merge packet on GitHub. **A/B/C are not assigned any repetitive remediation**. No automatic next phase, micro-permit, experimental trial, main/lineage mutation or merge has been started.

**Current lock**: `A_I2_HOLD · REAL_SFT_HOLD · SCOPED_COMPOSITE_SOURCE_QA_PASS · MERGE_EXECUTION_HOLD · ABC_DESIGN_PASS_PRESERVED · NO_NEW_SCIENCE · NO_GPU · MAIN_UNCHANGED · LINEAGE_UNCHANGED`.
