# TTM-Small-4M — Controlled prompt-serialization ablation, post-hoc exploratory result

**Date:** 2026-11-09 · **Task:** `TTM_SMALL4M_PROMPT_SERIALIZATION_CONTROLLED_ABLATION_PREREG_AND_ONE_SMALL_INFERENCE_BATCH` · **Original checkpoint branch:** T4 gốc, not EmbeddingGemma2.

## Immutable prerequisite and run order

The [preregistration was committed before new inference](https://github.com/minhtri22/TokenToModel-Lab/commit/fb5699857e435efb85c20e1be6baa7a206bb835e). Prereg source JSON SHA256: `b32e8f322e1a067271690fe181aed7ba1ec4bc9735d527209db9174bdadc719a`. One-shot CLAIM was created before generation; old 32 outputs were **reused verbatim** (original SHA256 `8c9cb99dcfd6e0f6eb507552c9bbcf6b0acfbf2d98d798a99c1e6358ea62cd2e`), never regenerated.

The experiment removes exactly **one trailing ASCII space** from each of the same 8 prompts. Both original T4 checkpoints 1024 and 1280, both decoders (greedy; sampled temperature 0.8 / top-k 40 / top-p 0.9), the same seed `20261109+int(prompt_id[1:])`, max 64 new BPE tokens. **32 new actual CPU generations** compared one-to-one against **32 old generations**. No new prompt set, TEST, Q1/Q2, TRAIN, VAL or training runs.

## Checkpoint/source pins

- 1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; 1280 SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`.
- Original P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; tokenizer merges SHA256 `aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af`.
- New 32-sample raw `CLEAN_GENERATIONS_UNADJUDICATED.json` SHA256 `eaa98bb4b1da6079513d96a73a23ea33a30fe43df0e736806a9294fa47530021`.

## Observed results

The primary metric was **at least one previously frozen exact distinctive anchor word** present in the newly generated continuation, never counted from the prompt. This is only a lexical proxy, not a semantic measure.

| Checkpoint / Decoder | Baseline lexical hit | Trimmed lexical hit | First newline baseline → trimmed | Early EOS baseline → trimmed | Repeated 3-gram baseline → trimmed |
|---|---:|---:|---:|---:|---:|
| 1024 / greedy | 0/8 | 1/8 | 8/8 → 0/8 | 0/8 → 2/8 | 35.89% → 29.84% |
| 1024 / sampled | 0/8 | 1/8 | 7/8 → 0/8 | 0/8 → 1/8 | 4.64% → 3.23% |
| 1280 / greedy | 0/8 | 0/8 | 8/8 → 0/8 | 0/8 → 2/8 | 32.46% → 39.00% |
| 1280 / sampled | 0/8 | 1/8 | 6/8 → 0/8 | 0/8 → 1/8 | 3.83% → 1.81% |

**Total:** distinctive lexical anchor mentioned in **0/32 → 3/32**; first generated token newline **29/32 → 0/32**; early EOS **0/32 → 6/32**. Step 1024 contributes 2 new anchor mentions, step 1280 contributes 1.

The 3 new keyword hits are thin: P03 1024/sampled mentions `Sam` but departs from pears/grandmother for a toy car; P05 1024/greedy and 1280/sampled mention `garden` but do not continue the robot Pip/sunflower planting story. In P02 1280/greedy, the model changes from Lumo/fox/bridge to unrelated friends and apology themes.

## Verdict with strict scope

- **`ABALATION_POSITIVE_LEXICAL`** under the precommitted exact-anchor criterion, 3/32 > 0/32.
- **`INITIAL_TOKEN_SERIALIZATION_EFFECT=CONFIRMED_SCOPED`** (29/32 newline to 0/32).
- **`SEMANTIC_ADHERENCE_GAIN=NOT_ESTABLISHED`**; no demonstrated causal follow-through on characters or events; step 1280 has no demonstrated advantage over 1024 on clean prompts.
- **`POSTHOC_EXPLORATORY_ONLY`**: the same 8 previously evaluated prompts and previously seen baseline outputs are reused. No human-blind independent re-rating or out-of-sample confirmatory inference was done. 6 early EOS cases complicate interpretation of output lengths and repetition metrics.

## Evidence integrity and custody

An independent read-only source/material/metric implementation gave **`PASS_42_OF_42_SOURCE_MATERIAL_AND_ARITHMETIC`**. This is technical and arithmetic QA **not** independent human-quality review. All 32/32 old/new cross-product IDs, exact one-space edit, checkpoint pins, seeds, token legality, frozen anchor list, and aggregate arithmetic checked. Negative lexical-boundary fixtures were included. It did not generate tokens or access model weights in its audit step.

- Local full evidence bundle `TTM_SMALL4M_PROMPT_SERIALIZATION_ABLATION_20261109.zip` **24,469 bytes**, SHA256 `05a7d1b3f063acbc23d82a7121db37a9b6f6cffef7e4a0d696dcb3486b31fc77`; bundle `manifest.json` SHA256 `595e7fc83f3fd2fe3ea3fe6e2f40070ab2285d724021583113f720a67f42b734`. ZIP independently tested via zip reader against member SHA-256. Full local Markdown report SHA256 `d49cdb970aa58614db0d021c9900c9ef836b82da0ef5a6d203aee3d89e77a075`.
- Archive contains the frozen prereg/one-shot claim, new raw text/IDs, both scripts, summary and QA; does **not** contain checkpoints, private BPE merge pairs, raw TRAIN/VAL/TEST, or consumed Q1/Q2.
- `main`, `lineage.md` L0017 and PR#13 merge status remain unchanged. No new science PASS/FAIL is being appended from this scoped post-hoc diagnostic.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_POSTHOC_ABLATION_SEMANTIC_REVIEW_AND_NEXT_DATA_DECISION`. Blind human/independent scoring (0–3) of all 32 original-versus-trimmed pairs (8 prompts × 2 checkpoints × 2 decoders), then choose a new genuinely unseen prompt set if seeking confirmatory quality claims. No immediate further training.
