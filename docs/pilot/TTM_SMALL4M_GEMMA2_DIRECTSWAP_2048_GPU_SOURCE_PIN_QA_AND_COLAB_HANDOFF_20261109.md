# TTM-Small-4M × EmbeddingGemma 2 — 2.048 GPU steps: source pin, offline QA and owner Colab handoff

**Date:** 2026-11-09. **Mode:** owner-approved independent NEW experiment. **Science status:** `GPU2048_NOT_EXECUTED`, no `CLAIM`, `RESULT`, new NLL or checkpoint from this experiment verified yet. **Run ID**: `ttm_small4m_gemma2_directswap_2048x4096_t4_gpu_20261109_v1`.

## 1. Frozen protocol was published BEFORE runnable source

- [Scientific preregistration](TTM_SMALL4M_GEMMA2_DIRECTSWAP_2048_GPU_EQUAL_EXPOSURE_ONE_SHOT_PREREG_20261109.md), immutable commit **`d942c32ed3da053a57e8ff22b1bc00d412a88ea7`**.
- New source builder [`ttm_build_directswap2048_from_locked1024.py`](../../tools/embeddinggemma2_swap/ttm_build_directswap2048_from_locked1024.py), frozen to immutable commit **`c50585dc7f58a1c377d26630d8234b2f6ce058eb`**; SHA256 **`548491a1ab964bd7204d0e71773d47b524cb544b00ac80f6741fd90e722f11b0`**, Git blob SHA1 **`529ca089df4b2450d7b9ff4b62640e00208b28f5`**.
- Builder downloads *previously published immutable* [GPU1024 source archive](../../tools/embeddinggemma2_swap/TTM_GEMMA2_DIRECTSWAP_GPU1024_SOURCE_20261109.zip) at exact Git commit `a22a7d3913b049b93006efa9475ca574ab2877a9`, verifies archive SHA256 **`e544c645635a28fe140802421d03a7928a7f0446d2df33bbfe4ec129e3a6ea27`**, verifies all three source entries, applies deterministic literal transformation and fail-closed resume arm marker, checks resulting source before execution.
- Resulting immutable Python runner `ttm_directswap2048_gpu_once.py` SHA256 **`0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e`**. Original P02 SHA256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`; token-swap SHA256 `d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39`.
- User-facing [Google Colab notebook](../../tools/embeddinggemma2_swap/TTM_GEMMA2_DIRECTSWAP_GPU2048_COLAB_20261109.ipynb), immutable commit **`6872eeeab83770006c466add7a898aab873aa85f`**, Git blob SHA1 `cad8812941b10af3d7815a8a7f23c22a9c79a69b`. Notebook pins builder commit, builder SHA and final runner SHA; **no manual ZIP download necessary**.

## 2. Static engineering QA, not a training result

- Offline source reconstruction using the exact original ZIP is **byte-for-byte identical** with pinned SHA `0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e`.
- **29/29 static/CPU-fixture assertions PASS**. Source modules compile and import, actual private `TRAIN/VAL` NPZ / manifest and mapped donor candidate fingerprints matched the locked values, A/B initial logits equal on CPU fixture, C/D compatible and differ, C/D source table frozen, projection trainable, no TEST keys. **Original trained checkpoint was not run as part of this 29/29 smoke.**
- Frozen new TRAIN schedule SHA256 **`81e4834f991607e8c3143bb67ed4a9ade93faa5f9526f630dc79e85bb0e51a52`**, 2.048 exact steps × 4.096 labels each. First 1.024 sampled steps are identical to prior GPU1024 schedule SHA256 `19ddc05128c188b86bda2f02de6389946944fe287c26abbf7d24cc5f9681e8f2`, but the **experiment is still entirely new**: all four arms restart from frozen T4 step1024 and fresh optimizers. Previously trained GPU1024-arm checkpoints are **never resumed or loaded**.
- No GPU science run or new `CLAIM` was performed while creating these sources. No TEST scoring, no new scientific PASS/FAIL, no `lineage.md` change authorized at this stage.

## 3. Fixed owner-execution procedure

1. Open the above GitHub Colab notebook with **T4 GPU**, leave `RESUME=False`, run once when TTM-Small T5 does not need the slot. Its source/dataset/checkpoint SHA checks occur before consuming the new unique RUN_ID.
2. New isolated Drive output location: `MyDrive/TTM_Small4M_EmbeddingSwap/ttm_small4m_gemma2_directswap_2048x4096_t4_gpu_20261109_v1`. Once CLAIM is made, never change source, optimizer, seed, model, schedule or cohort for this RUN_ID. No overlap with old GPU1024 results.
3. Four sequential arms A/B/C/D each 2.048 optimizer steps × 4.096 TRAIN labels; all receive one identical precomputed schedule. FP32 T4, fresh AdamW lr 1e-4, microbatch max8. Checkpoint READY-last and SHA after step **512, 1024, 1536, 2048** in each arm.
4. If interrupted **after a valid READY**, set `RESUME=True` and continue *same* RUN_ID. If an arm has started but no READY, fail closed with `STARTED_ARM_WITHOUT_READY_NO_AUTO_REPLAY`; never silently restart already consumed optimization. Keep partial artifacts. A successful output line `TTM_GPU2048_STATUS=COMPLETED_UNADJUDICATED` plus new `RESULT.json` is still **pending independent QA**, not an adjudication.
5. After all 4 arms complete, one VAL score on 61.122 labels/256 stories (already-used VALIDATION, exploratory), 1.000 paired bootstrap seed20261109 and signed contrasts A−C/B−C/D−C. Only positive 95% lower bounds for all three = `DIRECT_SWAP_2048_POSITIVE_EXPLORATORY`; else `DIRECT_SWAP_2048_BENEFIT_NOT_ESTABLISHED`. Do not use TTM TEST again.

**Next only after result:** verify CLAIM, SHA of all four final checkpoints and READY, compare per-story sums/CI, independently reload/check CPU logits, then append one scientific outcome `lineage.md` on research branch. **Only after 2.048 run is adjudicated** revisit `TTM_SMALL4M_EMBEDDINGGEMMA2_RESIDUAL_GATED_ARCHITECTURE_DESIGN_AND_MINIMAL_PROOF`. Main/PR#12/TTM T5 remain independent.
