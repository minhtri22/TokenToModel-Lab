# TTM-Small-4M × EmbeddingGemma 2 — frozen VALIDATION CPU A/B/C/D contract

**Date:** 2026-11-09. **Operation:** `TTM_SMALL4M_EMBEDDINGGEMMA2_FROZEN_VALIDATION_AB_CPU_ONCE`. **Status at registration:** `SCIENCE_NOT_EXECUTED`. **Run identifier:** `ttm_small4m_embeddinggemma2_frozen_val_ab_cpu_once_20261109_v1`.

## Locked inputs, data boundary and time of decision

This is a **descriptive/exploratory fixed-checkpoint ablation** on the *already used* TinyStories VALIDATION split. It is not fresh held-out confirmatory science. User expressly requested this CPU-only one-pass comparison; no Colab or GPU execution is required. Do **not** train, tune on VAL, read TEST arrays, reload SQuAD or Qwen, alter original checkpoint, or replace any prior R_gold/TTM science result.

Read-only private artifacts from the owner's Google Drive:
- `checkpoint.pt` SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, step 1024, 45,074,891 bytes.
- `candidate_initialization.pt` SHA-256 `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`, 21,835,865 bytes. This candidate contains actual EmbeddingGemma 2 mapped rows from pinned model `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e`, 1917 mapped BPE IDs, 130 incomplete UTF-8 fallback IDs and one EOS fallback.
- `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz` SHA-256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`, 1,186,107 bytes, contains TRAIN/VAL but **only val_x, val_y, val_count, val_story_index used for this evaluation**.
- `T4_PRIVATE_PACK_MANIFEST.json` SHA-256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`, 1,382 bytes.
- `src/p02/transformer_core.py` SHA-256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07` from frozen TTM repo.
- `ttm_embeddinggemma2_swap.py` from `tools/embeddinggemma2_swap/source_bundle_20261109.zip` SHA-256 `bce8ffa8bc954d7f1ba87b08c033e6e8c3dbc925be39cc4b78ef90b6d66a026e`.

## Fixed arms before scoring

- **A — trained baseline, tied**: exact P02 `GPT` from T4 step1024.
- **B — negative structural control**: `control_untied(A)`, identical pretrained weights but distinct input/head parameters. **Require exact logits equality A=B on at least one full VAL minibatch and identical aggregate scores**; otherwise flag integritiy failure.
- **C — pretrained donor token swap**: exact saved `candidate_initialization.pt`, input 2048×512 donor rows, frozen donor lookup, trainable 512→256 projection *without training in this run*, 130 invalid-UTF8 + EOS fallback, original trained P02 blocks and cloned output head.
- **D — randomized donor token association**: take C's 1917 valid 512-d donor vectors and apply a **seeded uniform permutation of those vectors between the valid TTM token IDs**, keeping masks, fallback, raw vector distribution, model checkpoint, output head and architecture identical. **Recompute the same ridge 0.01 512→256 alignment against the frozen original TTM token rows, using no VAL/TEST, just as for C.** Permutation seed `20261109`. This is a randomized token-to-vector control, **not IID Gaussian donor vectors**, designed to isolate identity-specific transfer from donor marginal statistics/capacity; it does not isolate every source of pretrained geometry.

## Calculation and decision

- Use only `val_x` and `val_y` (identical for A–D); `val_count` and `val_story_index` specify masks and story grouping. Exactly **328 windows, 256 stories and 61,122 valid next-token targets**. Validation-only cross-entropy: `F.cross_entropy(logits.float().reshape(-1,2048), targets.reshape(-1), ignore_index=-100, reduction='none')`; token-mean NLL is total NLL divided by 61,122. All models `eval()`, inference-mode, float32 CPU, no optimizer step. Reset neither checkpoint nor validation cohort.
- Report **A/B/C/D token-weighted NLL**, `A_NLL-C_NLL`, `D_NLL-C_NLL`, `A_NLL-D_NLL`; per-story sums and valid-token counts for **256 stories**, not independent windows. Fixed story-bootstrap **B=1000, seed=20261109**, resample 256 story IDs with replacement, ratio `sum(loss_A - loss_C)/sum(target_counts)`, likewise `D-C`; two-sided 95% percentile intervals.
- Coverage: report **1917/2048 vocabulary type coverage**, and real **frequency-weighted input-token coverage** among `val_x` at scored positions, plus separate target-label coverage among `val_y` where target != -100. No claim of semantics from raw coverage.
- Descriptive signal `FROZEN_INITIALIZATION_TRANSFER_POSITIVE` requires both `CI_low(A-C) > 0` and `CI_low(D-C) > 0`; if not, label `FROZEN_INITIALIZATION_BENEFIT_NOT_ESTABLISHED`, **not** claim underlying architecture or transfer-after-training failure. **B mismatch** or nonfinite/drop/missing labels invalidates run, not posthoc sample removal. There is no performance-tuning loop authorized by this comparison.
- Private per-story evidence and model artifacts remain outside GitHub. Public repo may receive **only aggregate numbers, exact hashes, unidentifying protocol/QA status and append-only lineage scientific decision**, not raw TRAIN/VAL token arrays.

**Next decision after A/B/C/D:** If C favorable, consider one fixed-budget learning adaptation comparison (same TRAIN, no TEST) with A, B, C, D; else assess whether ridge init or tokenization mismatch is the main cause before proposing new science. The frozen comparison *alone* does not prove or disprove pretrained-semantic transfer in a trained TTM model.

**D1 G4 R1/R2/R3 remains DEFERRED.** TTM-Small T5 artifacts and PR #12 must remain untouched.
