# HANDOFF — TTM Small-4M SM4M-F2 IR01–IR07 Distinct Independent Remediation Re-review

**Date:** 2026-11-15  
**Operation to execute:** `TTM_SMALL4M_F2_IR01_IR07_DISTINCT_INDEPENDENT_SOURCE_DESIGN_REREVIEW_SINGLE_GATE`  
**Mode:** `READ_ONLY · SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE_EXECUTION · NO_REPOSITORY_WRITES`.  
**Repo:** `minhtri22/TokenToModel-Lab`. Branch: `research/ttm-small4m-foundation-first-single-gate-20261115`.  
**Previous failed exact candidate:** `07adab6262e50b5e17c6ea816bb133866e0a11d2`; **independent verdict preserved** `HOLD_REVISE_DESIGN` (4 HIGH,3 MEDIUM).  
**New candidate identity:** Reviewer must pin the exact commit supplied by owner that has **parent 07adab…** and exactly the revised 06/07/author receipt plus add-only review evidence, author QA and this handoff. **Do not review a floating branch HEAD**. New source blob pins:
- 06 protocol: `a5cc0c51363de9772c27418ea667475c25c791b0`
- 07 admission: `d0ca205935c01a815aaebe86c90f4e3daf1a1291`
- 09 same-author adversarial QA: `4fa489a0e941f142cdec454b08f64bf0be1d6a8e`
- Author QA JSON: `01e589c62fded5e733bb50a24bbe73d83fe36ee0`
- Updated author design JSON: read and verify its exact Git blob from the owner-supplied **commit**; that receipt binds to this handoff's Git blob. Do not use an unverified floating ref.
- Original independent F2 HOLD report Git blob `e43774e67d9f0c20961bfb0c350971957153ad14`; SHA-256 `c4a43c9236debc967a9a4c088c158074f5fbf0201648677c53e6ea49cffd5376`.
- Original independent F2 HOLD JSON Git blob `eca67249b8bdd54e42d83c3e17395afa2605ee9f`; SHA-256 `70685237d07b20bb7b40b3028195e835b88b544e60151d7f0eb150f60a7357d2`.
- MD1 frozen: commit `33021a421f05bb3bfa0999ad12bc3bd144366da9`, blob `384d077600ed864a917fdd5e74b5a5bca0ed8766`. Owner original Foundation F01–F05 closure `c233dff20b9b020aefd732ce62bfa2e7aebd3985` remains valid **design-only**.

## 1. Purpose / epistemic discipline

Read complete original independent F2 report and JSON; **evaluate author changes in 06,07 and receipt against the original seven findings**, and then independently attack the new contract. Do not mark a finding closed just because the author listed it. The author ran **44/44 static/symbolic checks**, not independent science, not real gold, not real rater/scorer/proxy. Reviewer must make a distinct assessment and identify new loopholes.

One integrated decision: `GO_DESIGN_SCOPED` or `HOLD_REVISE_DESIGN`. A scoped design GO is **never** permission for data authoring, calibration, AI raters, checkpoint forward, GPU, model inference, training, F3/F4 or merge.

## 2. Seven mandatory distinct review lanes

**IR-01 HIGH — admission dependency:** Trace every state `S0→S1→S2→S3→S4→S5` and every G00–G12 P/E guard. Determine whether a single conditional **future** owner decision can authorize bounded private authoring and preregistered nuisance/scorer QA **without** requiring data evidence before it exists, then require independent per-item rights/gold/proxy/custody QA before conditional score release. Explicitly test S4 impossible without exact owner conditional scoring clause, distinct evidence check and immutable release. Does any action require an unattainable prior permission? All actual permits must still be false.

**IR-02 HIGH — semantic feasibility:** For each stratum (object_custody/social_relation/causal_obstacle/temporal_rule), is the independent fact/predicate/witness logic sufficient to ensure a valid 3-bit cube exists? Review all 12 Hamming-1 edge obligations/core, not just gold bit equality. If actor/object/goal are causally coupled, can a full cube be made without an unnatural task weakening? Treat absence of actual data as correct `PREEXEC_PENDING`, but absence of coherent construct logic as `DESIGN_DEFECT`.

**IR-03 HIGH — nuisance shortcuts:** Audit mandatory NC1–NC6, feature exposure and fixed proxy family, group-disjoint core/author/template 4-fold split, 0.625 candidate ceiling and every-proxy fail closed. A failed weak control does not prove no shortcut; assess remaining global-valence, label, word/style, format, ordering and gold-coupling loopholes. Candidate thresholds not owner-frozen and no proxy actually run.

**IR-04 HIGH — UNKNOWN:** Audit evidence-based trivalent rubric 0/1/UNKNOWN versus `INVALID_SOURCE`, balanced 24 cases (per axis gold counts 8/8/8), full 3×3 confusion, target unknown recall≥7/8, non-target correctness≥14/16, false UNKNOWN≤1/16 and positive/negative ≥7/8 each (all **candidate** thresholds). Verify the always-UNKNOWN strategy cannot pass, but avoid confusing abstention with missing answer.

**IR-05 MEDIUM — inference:** n=16 M0X core clusters, 64 dependent edges per axis, four strata and n=8 M0U target cases; screen-only claims, not confirmatory external validity. Check whether arbitrary thresholds, core/stratum floors and nuisance threshold 0.625 have sufficient rationale to progress to owner prospective freeze; flag missing power and pseudo-replication.

**IR-06 MEDIUM — blinded exposure:** Each rater sees one opaque item/fresh isolated context, no other variants, no shared model memory or side-by-side interface, same underlying items for both raters, role-separated custodian; compromise `HOLD_RATER_EXPOSURE`. Does practical protocol avoid or explicitly bound prior exposure/semantic guessing?

**IR-07 MEDIUM — checker determinism:** Strict typed schema; 8 nodes/12 edges/core, M0X 16/128, M0U 24/24 with gold 8/8/8 per axis; exact M0 32/64; rejection precedence; cases `N01–N28` including source-claim and false denominator errors. Check whether every invalid condition uniquely maps to a rejection/FAIL and no valid score silently drops items or changes denominators. The **28 fixtures are specified, not executed against an implemented scorer**.

## 3. Source integrity and archive guards

Compare old candidate to owner-supplied new exact candidate. Expected scope: two modified Markdown (06/07), one modified author JSON, add-only prior independent review report/JSON, one QA report/JSON, and one distinct-review handoff. Verify exact Git blobs and that no MD1, F0/F1/F2 historical closure, `lineage.md`, source code, model, data, old TEST/FINAL or main was changed. Reviewer must note SHA-1 Git blob distinct from raw SHA-256.

Original reviewer report and receipt were uploaded by owner, SHA-256 verified from actual files, and their exact Git blob objects were computed from original bytes. Never overwrite old verdict. If this new exact candidate is not the one described above, `SOURCE_MISMATCH_HOLD`.

## 4. Verdict contract / residual barriers

`GO_DESIGN_SCOPED` only if the seven design defects are genuinely addressed in a reproducible prospective contract with no new HIGH blocker and no hidden authoring/execution permit. Otherwise `HOLD_REVISE_DESIGN` with one integrated remediation list, not micro-permits.

**Regardless of design verdict:** `F2_PREEXEC_BLOCK=TRUE; OWNER_DATA_AUTHORING_GO=FALSE; OWNER_SCORING_GO=FALSE; GOLD_NOT_CREATED; SOURCE_RIGHTS_NOT_ATTESTED; RATER_NOT_ASSIGNED; SCORER_NOT_IMPLEMENTED; NO_GPU; NO_INFERENCE; NO_TRAIN; ROOT_CAUSE_IDENTIFIED=NO; F3/F4_NOT_OPENED; MERGE_NOT_AUTHORIZED`. Existing F01–F05 design closure remains unaffected.

## 5. Required single output packet

- `TTM_SMALL4M_F2_IR01_IR07_DISTINCT_REMEDIATION_REVIEW_20261115.md`
- `TTM_SMALL4M_F2_IR01_IR07_DISTINCT_REMEDIATION_REVIEW_RECEIPT_20261115.json`

Include exact candidate full SHA, diff, each F2 IR finding severity/closure and evidence, independent review of state DAG, semantic invariance, proxy/UNKNOWN/threshold/custody/scorer validity, all G00–G12 still blocked for execution, limitations and one verdict. Read-only; do not commit/push or run any scorer, rater, calibration, model. Report and receipt go to owner.

**Bước thực hiện tiếp theo — duy nhất:** hand owner the one independent GO/HOLD decision; owner decides scoped design closure or an integrated remediation. **No automatic research execution.**
