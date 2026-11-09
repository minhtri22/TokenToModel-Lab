# TTM-Small-4M × EmbeddingGemma 2 — final direct-swap 1,024-step GPU adaptation, preregistration

**Date:** 2026-11-09. **Scope:** owner-authorized **one final** longer test of the already-implemented *direct token-embedding replacement* before deciding whether to move to a residual/gated mechanism. **Mode:** scientific one-shot with resumable checkpoints under the **same** RUN_ID. **No experiment has executed at preregistration time.**

**RUN_ID:** `ttm_small4m_gemma2_directswap_1024x4096_t4_gpu_20261109_v1`.

## Scientific rationale and fairness boundary

Original TTM-Small-4M P02 trained for **1,024 optimizer steps × 4,096 nonmasked TRAIN target labels** = **4,194,304 target exposures**, not merely 1,024 steps with an arbitrary batch. The previous 64-step comparison used only 512 targets per step and did not establish a successful benefit of Gemma. To test whether longer adaptation might close the gap, freeze a **second 1,024-step incremental continuation** on exactly 4,096 valid labels per step *for all compared arms*. This continues a decoder that has already had 1,024 T4 steps. **It is not a from-scratch 1,024-step matched comparison** and must never be described as one. The full original T4 optimizer state is **not reused**, since the token-swapped candidate has no matching state; every arm starts from an identically specified **fresh** optimizer. No reuse of 64-step final weights.

- **A:** tied original trained P02 step1024, full trainable P02.
- **B:** untied output-head copy of A, all trainable original P02 + output head.
- **C:** exact Gemma-2-mapped donor candidate generated against original T4 step1024, 1,917/2,048 valid token types, fixed 512-d pretrained donor rows + fallback, **trainable** 512→256 ridge-initialized projection, original P02 blocks/positions and untied head trainable.
- **D:** same donor vectors permuted across valid token IDs with NumPy seed 20261109 and ridge 0.01 recomputed from original T4 token embedding, same parameter structure / trainable policy as C. D is a **token-association-shuffle control**, not a Gaussian donor. No donor encoder runtime.

**All arms:** fixed **1,024 optimizer steps, precisely 4,096 target labels each = 4,194,304 exposures per arm**; 16,777,216 total exposures across four arms. Single exact schedule of TRAIN-only windows generated with `np.random.default_rng(20261109+71)`; same window order and truncation; use source pack `train_x,train_y,train_count` only for training. Microbatches of **at most 8 windows** with gradient accumulation to exactly 4,096 valid next-token labels per optimizer step. AdamW **fresh**, constant LR `1e-4`, betas `(0.9,0.95)`, eps `1e-8`, weight decay `0.1`, gradient clip L2 norm `1.0`; these match the earlier 64-step optimizer (except larger exact-label budget), not the original T4 warmup schedule. **No optimization during validation.** CUDA FP32 (no autocast, no TF32), one Tesla T4 Free runtime, seed `20261109`, sequential A→B→C→D to cap VRAM. The nominal equal budget is **steps and valid target-label exposures**, not equal FLOPs because C/D have adapters.

## Frozen source and input identity

- Existing trained `checkpoint.pt` step1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- Existing mapped `candidate_initialization.pt` SHA256 `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`.
- TRAIN/VAL pack `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz` SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`. Pack manifest `T4_PRIVATE_PACK_MANIFEST.json` SHA256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`. This pack has **no TEST**. 2,691 TRAIN windows (498,287 unique labeled targets), 328 VAL windows (61,122 targets across 256 stories). Original source: TinyStories TRAIN-only BPE2048; no new corpus sampling or tokenizer fitting.
- P02 `src/p02/transformer_core.py` exact SHA256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`; `ttm_embeddinggemma2_swap.py` exact SHA256 `d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39`.
- Runner SHA256 and Git source commit will be recorded in a **single source-release readback** before GPU run. No private inputs in public GitHub.
- Existing T4 main model / previous 64-step checkpoints are never mutated. TTM-Small T5 remains priority: only launch the T4 notebook if the available Colab T4 slot is not needed for T5.

## Execution, resume and budget containment

One owner-authorized claim, not one permit per technical substep. Check exact input hashes, model metadata, dataset mask and frozen code before first optimizer update; create a durable `CLAIM.json` in a **fresh** Drive RUN_ID folder. Stop rather than silently altering hyperparameters, dataset cohort or source code. Save fresh named checkpoints for each arm at **256/512/768/1024 steps**, including model, optimizer, RNG, step, train-schedule hash, fixed source hashes and a last-written `READY.json` after SHA256 readback. Store these in new Drive namespace; never overwrite original T4/64-step/TTM-Small checkpoints. A Colab interruption can be resumed only from a verified READY checkpoint under the **same RUN_ID, same runner SHA, source pins, CUDA environment and frozen schedule**; no new experiment ID or start-over-on-failure. Partial checkpoints stay as evidence and are not counted completed. If GPU unavailable, stop before consuming CLAIM or any science.

**Hard stop:** if Colab preempts or the configured total GPU runtime cap is reached, preserve available checkpoints and `INCOMPLETE_NO_VERDICT`, do not silently treat 256/512/768 as final. The owner may continue the *same* RUN_ID if the original budget remains; no new 1024×4 run.

## Scoring, statistics and stopping decision

**After all four arms reach exactly 1,024 steps**, evaluate the *same* 328 locked VALIDATION windows exactly once in CUDA FP32 model eval() mode, 61,122 labels / 256 stories. Per-token cross-entropy `F.cross_entropy(logits.float(),targets,ignore_index=-100,reduction='none')` with original target masks. Compute token-weighted arm NLL, paired 256-story bootstrap with **1,000 resamples, seed 20261109**, for contrasts `A−C`, `B−C`, `D−C`. Larger positive means C better.

**Primary pre-registered exploratory GO rule:** `CI95_lower(A−C)>0` AND `CI95_lower(B−C)>0` AND `CI95_lower(D−C)>0`. Otherwise conclude **`DIRECT_SWAP_1024_BENEFIT_NOT_ESTABLISHED`** and follow the owner's conditional decision: **STOP** further naive direct-swap training; move to the separate *residual/gated embedding* architecture **DESIGN**, not automatically train that alternative.

Even a positive result remains only a **reused-VAL single-seed exploratory** signal (the same VAL was used for prior T4, 64-step and fixed-checkpoint comparisons); no blind held-out generalization claim and no reread of sealed TEST. Do not choose checkpoint or LR from interim VAL. Preserve primary NLL even if it contradicts expectation.

**QA/adjudication:** retain original CLAIM, checkpoints/READY, original RESULT, per-story sums, code SHA and independent recomputation before an append-only *new scientific* `lineage.md` entry. Never put private TRAIN/VAL tokens, per-story sums, checkpoint bytes or remote credentials in public GitHub.

**No GPU training was executed by writing this preregistration.** `D1_G4_R1_R2_R3=DEFERRED`; `TTM_SMALL_T5=PRIORITY_FIRST`.
