# TTM-Small-4M × EmbeddingGemma 2 — frozen VALIDATION CPU A/B/C/D one-shot adjudication

**Date:** 2026-11-09. **Run ID:** `ttm_small4m_embeddinggemma2_frozen_val_ab_cpu_once_20261109_v1`.

**Formal verdict: `FROZEN_INITIALIZATION_BENEFIT_NOT_ESTABLISHED`** on the *previously-used* TinyStories VALIDATION cohort; **`INDEPENDENT_RECEIPT_QA=PASS_46_OF_46`**. This is a real CPU model-forward ablation, not a synthetic smoke. No training, no GPU, no TEST, and no RAG.

## 1. Ex-ante protocol and exact source

- [Preregistered protocol](TTM_SMALL4M_EMBEDDINGGEMMA2_FROZEN_VALIDATION_AB_CPU_PREREG_20261109.md), commit `46a37bd34299aeda16ebac7e0cf5cbf7f3772624`, **published before model scoring**.
- Frozen trained step1024 PyTorch checkpoint SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; candidate EmbeddingGemma 2 mapped input SHA256 `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`. Neither altered.
- Private VALIDATION-containing NPZ SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; private pack manifest SHA256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`. The pack contains both TRAIN and VAL, but executable code referenced **only** `val_x`, `val_y`, `val_count`, `val_story_index`. No TEST data exist in pack.
- Model sources exact P02 SHA256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`, swap module `d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39`. Frozen runner SHA256 `2fe53494c2706f4741b9c063fe64630999253ff35ccdfa0061020327be85b755` and independent QA script SHA256 `f122ca620359dd0ebeb311d7f19514e529410d8ab23f69a8e00ef6b474a96372`.
- Single exact run CLAIM SHA256 `ed63d2b72a610237728aaed0e730041f1cfc0750747b97cfa022f4e23c41e506`; original RESULT SHA256 `a5f1b0a0c1c81f543e181d56f0697e73c5c796cbdbf7395f935e58aa6331923e`; private per-story sums SHA256 `c0cbc7edf88aeae3fc899896272be0d6dca49606c9a643847153982b3aee77a3`; independent receipt QA SHA256 `bb3b672e2336e25397ae8095225ba688067d3526f9b0e9b88f4e7096c1dda3c2`.
- Complete exact evidence packet for owner: `TTM_SMALL4M_EMBEDDINGGEMMA2_FROZEN_VAL_AB_CPU_ONCE_EVIDENCE_20261109.zip`, SHA256 `2659a0bb17b5411fecfef536e365de824a29e04f73bc234284bdcfc3f29549ce`, 18,047 bytes; contains source + original receipt snapshots including private per-story sums. **Do not place private per-story contents or original VAL arrays in public GitHub.**

## 2. Frozen arms and actual observed metrics

The 4 models received the exact same 328 VAL windows / 256 stories / 61,122 nonmasked next-token targets, no updates to weights, CPU FP32 (PyTorch 2.10.0+cpu). Computation took ~23.026 seconds of model scoring; no CUDA GPU.

| Arm | Definition | Actual token-weighted NLL |
|---|---|---:|
| A | Trained tied-head TTM-Small-4M checkpoint step1024 | **3.522338851682218** |
| B | Same trained checkpoint, cloned/untied output head | **3.522338851682218** |
| C | Same checkpoint with pretrained EmbeddingGemma 2 input-mapped vectors and initialized ridge adapter, no adaptation training | **4.348096266099754** |
| D | Same donor vector marginal distribution, 1917 valid token rows randomly **permuted**, seed `20261109`, **new identical ridge(.01) fit** against trained TTM input rows, same fallback/transformer/head | **6.443825625799108** |

Arm A and B **identical per story** and initial logits equal, so untie itself did not explain effects. Baseline A exactly reproduces prior VAL NLL `3.522338851682218` from original T4 H1 QA (no model retraining).

Two-sided 95% paired story-bootstrap; **1,000 resamples**, seed `20261109`, weighted by actual scored targets in resampled stories:

| Improvement, positive means second arm better | Observed mean (nats/token) | CI95% |
|---|---:|---:|
| A − C | **−0.8257574144175357** | **[−0.8423488811919678, −0.8106557264002213]** |
| D − C | **+2.0957293596993543** | **[2.0634174827959995, 2.1264773635261816]** |
| A − D | **−2.92148677411689** | **[−2.955480258088354, −2.8871334115518255]** |

**Primary pre-registered descriptive decision:** C does **not** beat A, though it beats D. The locked requirement for `FROZEN_INITIALIZATION_TRANSFER_POSITIVE` was **both** `CI_lower(A−C)>0` and `CI_lower(D−C)>0`. Only the latter is true. Thus **`FROZEN_INITIALIZATION_BENEFIT_NOT_ESTABLISHED`**; neither confirmation of usefulness nor global rejection of pretrained Gemma/architecture.

**Coverage on real VAL**:
- Vocabulary type count `1,917 / 2,048` (**93.60%**) mapped.
- Input token occurrence count for scored positions `61,108 / 61,122` (**99.9771%**) mapped.
- Target label occurrence count `60,852 / 61,122` (**99.5583%**) correspond to mapped type IDs.
- 130 incomplete UTF-8 fragment types plus EOS fall back to trained TTM input embedding; the above coverage values count the same masked scoring positions. Large coverage alone does **not** imply lower NLL.

## 3. Independent QA and interpretation limit

**Independent receipt QA** parsed the original CLAIM/RESULT and private 256-story loss sums, checked all original input hashes, recomputed all arm NLLs, all pairwise effects and all bootstrap intervals from scratch, cross-checked direct val-token masking/coverage and confirmed no TEST/training. **46/46 PASS**. It was an independent **arithmetic/data-integrity review**, not a second PyTorch inference or human external peer review.

What the data show:
1. The input EmbeddingGemma 2 replacement is **architecturally executable** but degrades *frozen* trained TTM perplexity/NLL: `C NLL 4.3481 > A NLL 3.5223`.
2. Correctly paired donor vectors plus the ridge adapter yield a much better initialized model than the same donor vectors with token association randomized and adapter refitted (`C < D`). **This alone does not prove donor semantic transfer**, because alignment geometry, tokenizer identity and ridge fit to the original TTM embedding may explain the difference.
3. This comparison used **existing VAL already consulted for T4 H1**; findings are descriptive, **not clean blind generalization**, and only measure frozen-initialization, **not** potential gains after training adaptation. No claim about GGUF/Ollama parity, R1/R2/R3 or TTM production readiness.
4. Since no adaptation budget was preauthorized, **do not run new fine-tuning in this phase**. If considering a successor, lock a small equal-budget supervised adaptation on TRAIN only (A/B/C/D, all same optimizer steps) *before* observing new adapted metrics; continue without accessing sealed TEST.

This negative scientific result must be appended to `lineage.md` only, on the isolated embedding-swap branch, **without changing previous TTM H1 PASS or T4 TEST descriptive outcome**; the source code and QA should be kept separately in the downloadable private evidence package.

**Final:** `FROZEN_VALIDATION_AB=COMPLETED_ONCE` · `IND_QA=PASS_46/46` · `C_IMPROVES_OVER_A=NO` · `C_IMPROVES_OVER_D=YES` · `TRAIN_STEPS=0` · `TEST_READ=NO` · `D1_G4_R1_R2_R3=DEFERRED` · `TTM_T5=PRIORITY_FIRST`.
