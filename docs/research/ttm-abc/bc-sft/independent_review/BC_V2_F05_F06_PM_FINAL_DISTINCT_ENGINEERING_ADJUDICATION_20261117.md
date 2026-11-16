# TTM B/C v2 F05–F06 — PM final distinct engineering adjudication

**Operation:** `TTM_PM_BC_V2_F05_F06_DISTINCT_FINAL_QA_AND_ENGINEERING_GATE_ADJUDICATION_SINGLE_GATE`  
**Date:** 2026-11-17  
**Decision:** **`BC_INTERFACE_PASS_ENGINEERING_SCOPED`** (synthetic CPU interface, trusted immutable bundle inputs, Python 3.12 CI); **NOT** permission for real SFT, scientific claim, GPU, historical TEST, untrusted-host filesystem or merge.  
**Independence:** new tests authored/run by distinct PM ChatGPT reviewer in a separate GitHub branch using linked owner's account, **not** an independently authenticated human auditor.

## 1. Frozen exact source, branches and custody

- B integration [Draft PR #36](https://github.com/minhtri22/TokenToModel-Lab/pull/36) **exact HEAD** `09de6a46574146d863f416e056fcf01091f3efb8`, currently open, Draft, unmerged.
- Exact B **source/tests inspected and CI-tested** `a83e1526bce842761f3051dad28b90a55395a6aa`. Compare `a83e1526..09de6a46` shows **only two added docs/receipt files** and no changes to executable code/tests. Corrected `src/ttm_track_b/bc_sft_bridge_v2.py` **Git blob** `c56d98b520fef387fab43bac87b7a9247287b17c`, SHA-256 as independently pinned by B/C `4fcbcf45d90c1ca577d3762ac4c26369d0c51e88cbe1f9bd8e172c8847c6157e`.
- Original failing source PR36 HEAD `dc151252070e0b118d14f3459823f8e89c6b6723` has immutable [PM reviewer CI run #43923286066](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43923286066): 1 positive PASS, two deliberately rejecting negatives FAIL.
- C [Draft PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35) latest HEAD `00afd25aa2234e30f7602592d49d5d9f2947965b`. C exact review [report](https://github.com/minhtri22/TokenToModel-Lab/blob/9578291ae7c64ac58960fca679356e956ad9d51b/docs/research/ttm-abc/track-c/independent_review/C_BC_V2_F05_F06_EXACT_HEAD_REVIEW_20261117.md) at evidence `9578291ae7c64ac58960fca679356e956ad9d51b`, separately authored 15 new + 19 original tests per OS.
- **Eight source artifact paths** (seven actual canonical JSON files plus `MANIFEST_CANONICAL_LF.json`) were directly read back from B PR36 latest HEAD and old pre-F05/F06 HEAD, with **8/8 exact Git blob SHA-1 equality** and textual byte-domain equality. Manifest Git blob `cba9f094d5d05787ffb50ffdef849049945bbfc8`, independently reported SHA256 `17f91e6d3881404909b6cb8c1cd4a2272a92f8b67c179806c2af68768e86d0a2`. Previous PM distinct [review](https://github.com/minhtri22/TokenToModel-Lab/blob/e26a754c0bb6c3ca435e175e03a9fd7c62a8967b/docs/research/ttm-abc/bc-sft/independent_review/TTM_PM_A_I1_AND_BC_V2_DISTINCT_QA_ADJUDICATION_20261117.md) independently recomputed SHA256 for **7/7** actual canonical JSON files and reconstructed source role/shift/mask/labels **3/3**.

## 2. Exact B patch closes both independently demonstrated defects

Diff [pre-fix B HEAD to amended tested commit](https://github.com/minhtri22/TokenToModel-Lab/compare/dc151252070e0b118d14f3459823f8e89c6b6723...a83e1526bce842761f3051dad28b90a55395a6aa) changes only four paths: B v2 bridge, B v2 regression, copied *unmodified* original PM three-case negative suite, and B CI workflow. No GitHub artifact bytes changed.

- **BC-QA-F05** — `_check_manifest_shape()` now checks `m.get("bridge_schema") == BRIDGE_SCHEMA` (B source lines 280–281), rejecting missing, alias, incorrect type or old version. No rehashing the seven files can hide a forged version.
- **BC-QA-F06** — `verify_bundle()` checks `manifest_path.is_symlink() or not manifest_path.is_file()` **before** reading manifest bytes (lines 370–375). Existing seven artifact symlink checks stay intact.
- Both changes are deliberately *path-level* and are not promised race-free or Windows HANDLE/reparse-point-proof.

## 3. Fresh PM third-actor independent CI — 12 PASS / 0 FAIL / 0 SKIP **per OS**

New review branch **`review/ttm-pm-bc-v2-f05-f06-final-distinct-20261117`** forked **exact B PR36 evidence HEAD `09de6a46...`**. B source, its original 3 reviewer tests, C source, prior receipts and data all unchanged. Reviewer added new test `tests/ttm_track_bc/test_pm_final_distinct_v2_manifest_boundary_20261117.py` and workflow `.github/workflows/track-bc-pm-f05-f06-final-distinct-py312.yml` only.

Independent [GitHub Actions #43937370201](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43937370201), **CI-tested reviewer branch HEAD `ce047feeb511949319f2788758506bbdbc962807`**:
- **Linux Python 3.12**, job **`133545393767`**: original PM frozen negatives **3/3 PASS**; newly authored reviewer controls **9/9 PASS**; no failed/skip.
- **Windows Python 3.12**, job **`133545394363`**: original PM frozen negatives **3/3 PASS**; new 9/9 PASS; no failed/skip. Windows symlink creation was actually executed; none skipped.
- Workflow explicitly checks exact source Git blob `c56d98b520fef387fab43bac87b7a9247287b17c` and original PM frozen test blob `3003566952116f3bc0e4ba21c7306fda460a3017`, then runs `python -B -m unittest`. No `torch` import, model forward, optimizer, GPU or science in **this independent CI run**.
- New cases verify valid bundle & seven real SHA fields; fake/missing/old/wrong-type bridge schema; external byte-identical manifest symlink; directory masquerading as manifest; **all seven artifact symlinks**, **all seven artifact modifications**, recomputed SHA on semantically wrong target; CRLF canonical mismatch; legacy schema rejection. Test outcomes were read from the **raw job logs**, not only Actions' status label.

Independent job source proof is stronger than B branch rerunning the PM-authored suite: **distinct branch, workflow and new third-actor negative tests**. CI environment remains GitHub-hosted, not the owner's physical Windows host.

## 4. Supporting B/C author and cross-track CI (not substituted for distinct QA)

- B amended [Actions #43928511412](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43928511412) at `a83e1526...`: Windows Python3.12.10 job `133514324483`, Linux Python3.12.16 job `133514325422`, both **29/29 v1**, **26/26 v2**, **3/3 original PM**, **18/18 C oracle routed through B**, actual seven SHA readback and a bounded P02 CPU forward/backward. No skips. Probe: **7 valid assistant targets, 25 ignored direct targets**, NLL ~7.64458 versus independent double-precision oracle, nonzero prompt context gradients, direct prompt CE zero, causal/right-pad isolation, `optimizer_steps=0`.
- B [core regression #43928511207](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43928511207) Linux/Windows jobs `133514323517`/`133514322980` SUCCESS on exact corrected source.
- Agent C separate [Actions #43932738585](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43932738585), 15 new F05/F06 + 19 Part B regression **34/34 PASS** per Windows/Linux Python3.12, no skips, B source unchanged. C formally issued `C_CONTRACT_COMPATIBILITY_PASS_SCOPED_V2_F05_F06_CLOSED`. C is a contract owner, not final third-party PM adjudicator.

## 5. Formal PM decision and explicit boundary

| Gate | Final status for this *exact synthetic CPU interface* |
|---|---|
| BC-0 exact custody | `PASS_SOURCE_PIN_AND_EIGHT_BLOB_READBACK_SCOPED` |
| BC-1 C UTF-8 typed bridge/byte IDs | `PASS_ENGINEERING_SCOPED` |
| BC-2 roles, masks, shift, EOT/EOS, loss | `PASS_ENGINEERING_SCOPED` |
| BC-3 finite synthetic CPU forward/backward, no optimizer | `PASS_ENGINEERING_SCOPED` |
| BC-4 versioned schema/canonical byte/7 SHA | `PASS_FAIL_CLOSED_TRUSTED_BUNDLE_SCOPED`; F01–F06 closed for tested scope |
| **BC-5 distinct integration QA** | **`PASS_DISTINCT_WINDOWS_LINUX_PY312_ENGINEERING_SCOPED`** (PM 12/12 per OS, C 34/34 per OS) |
| **B/C interface** | **`BC_INTERFACE_PASS_ENGINEERING_SCOPED`** |
| Owner-host hard job memory resource admission for **future real SFT** | **`HOLD_NOT_EXECUTED_ON_NEW_SFT_CANDIDATE`**; this decision does not reuse old B-M3 V3 native cap |
| Full Windows filesystem containment/TOCTOU/junction security | **`NOT_VERIFIED`**, trusted immutable root only |
| SFT science, checkpoint weights, historical TEST/GPU | **`NOT_AUTHORIZED` / `NOT_EXECUTED`** |
| PR #33/#34/#35/#36 merge, main/lineage update | **`NOT_AUTHORIZED`** |

**Why the scoped engineering PASS is sound:** PM original [integrated contract](https://github.com/minhtri22/TokenToModel-Lab/blob/40788f557799c7c8a688df32271510aab73a9180/docs/coordination/ttm-abc/TTM_PM_BC_F01_F04_WIRE_SCHEMA_CUSTODY_INTEGRATED_AMENDMENT_HANDOFF_20261117.md) states final `BC_INTERFACE_PASS_ENGINEERING_SCOPED` requires exact candidate, C Part B acceptance, independent negative runtime QA. All are now satisfied. The same contract separately prohibits auto-transferring older B0/B1 native/science resource permits to **new SFT training**, and says new candidate requires its own resource policy before such execution. Thus PASS validates the **synthetic engineering interface** and **does not waive prospective resource release admission**.

**Historical B-M3 reconciliation:** earlier PM `PASS_ENGINEERING_BASELINE_SCOPED_BY_ADJUDICATION` remains published; original native V3 `HOLD_NATIVE_QA` phase `job_memory_negative` remains immutable with above-cap `PeakJobMemoryUsed`, and newer reviewer `HOLD_PEAK_ACCOUNTING` dissent is retained. No V3 rerun or retroactive relabel. Track A M0 v3 I1 `PASS_SCOPED_MEASUREMENT`, I2 `HOLD_RELEASE_PREFLIGHT` unchanged.

**No hidden access claim:** same GitHub-connected account published separate reviewer files; no distinct human credential custody.

### Single next operation

`TTM_PM_ABC_SCOPED_ENGINEERING_CLOSURE_LINEAGE_INVENTORY_AND_PROSPECTIVE_RELEASE_BARRIER_DESIGN_SINGLE_GATE`

Read-only coordination of A I1 + B M3 + C M4 + B/C interface scoped engineering results into one release-barrier matrix. Determine what would be required **prospectively** for science/owner-run resource protection, without opening I2, SFT science, GPU or merging PRs; avoid micro-permit chain. GitHub remains source of truth.
