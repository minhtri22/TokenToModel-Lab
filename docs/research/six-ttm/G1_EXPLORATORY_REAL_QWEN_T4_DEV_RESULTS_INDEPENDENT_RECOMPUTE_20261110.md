# TTM × SIX — Real Qwen exploratory DEV: independent numeric adjudication

**Ngày:** 2026-11-10  
**Experiment ID:** `TTM_SIX_G1_EXPLORE_AUTHORED_PUBLIC_QWEN_DEV_V1`  
**Một phán quyết:** **`EXPLORATORY_NO_SIGNAL`** — for **A→P incremental functional benefit under the preregistered exploratory screening rule**, **not** failure of original G1, not absence of every predictive relationship.  
**Review mode:** independent recomputation from supplied `source_features.npz`, `target_features.npz` and source code by assistant; *not* a distinct external human/Codex peer adjudication. No model rerun, no private TEST read.

## 1. Chain of custody and integrity

- Owner-uploaded ZIP `TTM_SIX_G1_EXPLORE_REAL_QWEN_DEV_RESULTS.zip`: SHA256 `6f98560117219cf3cecc37fb87ff562a784fe82238d9b2d831cbda7634488d9f`, ZIP CRC `PASS`, exactly five files, no unsafe extracted paths.
- Exact experiment script in ZIP SHA256 `9688deb1d1157c93fb7090e5b1c12ea4bc56ed0dedadb0597d84ceb4e68e82eb`; Git blob SHA1 `c82ff40c0187677e6753db3beb56e7c93ea7d1b3`, matching public pinned GitHub commit `15f7661f2fec5ec2cef0cac26154d2183bb5f33f`.
- Independently reconstructed prompt SHA/split/manifest from **literal AST data only**, without executing user-supplied code: SHA256 `ae86b8e847e74c97b7f69d88a08f133902173bc4c4df104f413447c1cd6fa40d`; matches all returned manifest pins.
- Source features NPZ SHA256 `d255e71cc5d7a1f975c1c1f24d4181b325ff49e971fab234bb7a97750672b270`, shape 64×1024, float32, all finite; target features NPZ SHA256 `d4c7dfa681f023c5af132d67ba6857b9462916815125c9bec2d1b4ab3a134bd8`, hidden 64×2048 and probes 64×2, float32, all finite. NPZ processed with `allow_pickle=False`; all 64 rows align with deterministic 48 TRAIN (12 groups), 16 DEV (4 groups), 0 TEST.
- Result JSON SHA256 `62dcb9df129ac6caf698de1033f13f52f01d1ee280588a3897648e351149f344`; manifest receipt JSON SHA256 `85db441d1ed535eecf67a2f35fe74c6d0983233a0cc8337e5c65c6e95ecb04b5`. Values are exactly reproduced independently (tolerance ≤3×10^-12) for 8/8 metrics by separate NumPy calculations.
- Owner result reports T4, 329.08 seconds, exact Qwen model revisions and verified model weight hashes. This reviewer **did not have Colab GPU execution transcript or original model weight bytes**; Qwen execution and in-Colab hashes are **owner-artifact claims backed by compatible tensors and loading code**, not separately attested model/GPU operation.

## 2. Quantitative DEV outcomes

**Metric:** MAE over 16 DEV prompts from 4 disjoint scenario groups; lower is better. 

| Method | DEV MAE | Relation |
|---|---:|---|
| A→P: source hidden→target hidden→2 functional probes | 0.065537960 | Candidate mechanism |
| Direct source hidden→2 functional probes | 0.061827128 | Best of the shown predictors |
| TRAIN response mean | 0.067550507 | Baseline |
| Group-shuffle null, median of 32 draws | 0.065511059 | Required negative comparison |
| Group-shuffle null, best of 32 draws | 0.065063108 | Observed minimum; not a confidence bound |

- A→P improves over TRAIN mean by **2.98%** of baseline MAE; the direct probe improves by **8.47%**.
- A→P is **6.00% worse** than direct MAE; direct is better than A→P in *all four* DEV scenario groups (descriptive).
- A→P MAE is **0.000026901 larger** (worse) than median shuffled control; only **13/32** shuffled controls are worse than A→P. This is **not** a hypothesis-test p-value.
- DEV R² per probe against TRAIN mean: A→P `[0.0932580577159543, 0.021399525059608182]`, direct `[0.22215439789523062, 0.08010319881814554]`.
- CKA on **only four DEV group means**: `0.96765794`; geometry-only diagnostic, not independently validated functional transfer evidence.

## 3. Apply the *predeclared* exploratory contract literally

Source: `docs/research/six-ttm/G1_ORIGINAL_HOLD_ARCHIVE_AND_EXPLORATORY_SCOPE_AMENDMENT_20261110.md` at pinned `15f7661f2fec5ec2cef0cac26154d2183bb5f33f`.

| Required condition for `EXPLORATORY_SIGNAL` | Actual | Decision |
|---|---|---|
| A→P MAE < TRAIN-mean MAE | 0.065537960 < 0.067550507 | **PASS** |
| A→P MAE < median group-shuffled MAE | 0.065537960 > 0.065511059 | **FAIL** |

**Terminal scoped verdict: `EXPLORATORY_NO_SIGNAL`.** This means the proposed **two-stage A→P mechanism did not meet the early positive-signal rule**; it does **not** negate the direct source→target response predictive association (which improved MAE), and does not turn four DEV groups into a proper significance test. A-to-P and direct approaches were *not information-budget matched*, so this is a screen, not a mechanistic causal attribution.

## 4. Data/rights/scope and limitations

- Data: only 16 authored fictional situations ×4 paraphrases, grouped 12 TRAIN/4 DEV. No original TinyStories, original G1 manifest, TTM pilot original VAL/TEST, or G1 sealed TEST referenced by inspected source/manifest. User result states `G1_private_TEST_opened=false` and `G1_original_science_executed=false`; those are **consistent with the inspected code**, not proof of every external runtime action.
- The artifact includes both Qwen feature tensors; **keep raw NPZ and original ZIP private** and publish only aggregate metrics and digest summaries.
- Only 2 probes rather than 8, one exploratory split/seed, four independent DEV groups and 32 negative permutations; no confirmatory p-value, no 80% power, no assertion on robust generalization.
- Qwen embeddings/target responses were sampled on the owner's runtime, not rerun or independently instrumented in this review.
- Do **not** append this exploratory NO_SIGNAL to original scientific `lineage.md` as an original G1 PASS/FAIL; preserve original `G1_SCIENCE_LOCK=HOLD` and `G1_ORIGINAL=FEASIBILITY_HOLD_ARCHIVED`.

## 5. Scientific disposition

**Stop/close this exact A→P exploratory candidate as an unpromising screen under its preregistered criteria.** Preserve source, zipped tensors and evidence. A next *distinct* exploratory contract may evaluate direct functional-response transfer to TTM-Small-4M or a substantially revised representation objective with matched compute and data budgets, **before** any new run. Do not automatically promote the current direct-probe finding to G2/G3 formal science and do not unseal G1 original TEST.

**Bước thực hiện tiếp theo:** `TTM_SIX_G1_EXPLORE_NO_SIGNAL_RESULT_ARCHIVE_AND_DISTINCT_FOLLOWUP_SCIENCE_DECISION` — archive sanitized result receipt and choose one new, finite testable hypothesis/contract; no more original-G1 infrastructure provisioning.

**States:** `EXPLORATORY_RESULT=EXPLORATORY_NO_SIGNAL` · `RESULT_NUMERIC_QA=PASS_8_OF_8` · `REAL_QWEN_EXECUTION=OWNER_REPORTED` · `ORIGINAL_G1=FEASIBILITY_HOLD_ARCHIVED` · `PRIVATE_TEST=UNCHANGED_SEALED` · `G1_SCIENCE_LOCK=HOLD`.