# TTM D1 — G4 R1/R2/R3: single integrated scientific admission decision

**Date:** 2026-11-09  
**Work item:** `TTM_EMBEDDINGGEMMA2_D1_G4_R1_R2_R3_SINGLE_INTEGRATED_SCIENCE_DECISION`  
**Decision:** **`READY_FOR_OWNER_G4_R1_R2_R3_ONCE`** under the **unchanged G4 source-selection/metric contract**.  
**Actual execution:** `R1=NOT_EXECUTED`; `R2=NOT_EXECUTED`; `R3=NOT_EXECUTED`; `R_GOLD=ALREADY_CONSUMED_PASS_PRESERVED`; `SCIENCE_RESULT=NONE`. No Colab run or model download was done during this admission decision.
**Priority:** TTM-Small-4M T5 first. The owner must not launch this G4 Colab session while it conflicts with TTM-Small T5 compute/quota.

## Basis, frozen sources, and scope

- Prior scientific gate: `PASS_RGOLD_SCREEN_SCOPED_SYNTHETIC`, independent offline QA 1273/1273, recorded in appended lineage `L0011`. Original R_gold run `ttm_embedgemma2_d1_rgold_one_shot_20261109_v1` is consumed and MUST NOT rerun. Its original `RESULT.json` exact SHA-256 `43e7a78d763a5f3bcf3a049b97d3ae59b0e6010f42d106eb3d1efc652c01735b` is required before any new claim.
- G4 protocol machine contract: `docs/research/fixtures/TTM_EMBEDDINGGEMMA2_D1_SQUAD_RETRIEVAL_AND_R_GOLD_SOURCE_LOCK_CANDIDATE_20261108.json`, Git blob SHA-1 `52d92e1c054afcf85ec5334e275f9b75ec084e83`, frozen at commit `b10deb62567571dc4aa68e5aad9fe06b55d1e23b`.
- Public SQuAD v1.1 validation only: `rajpurkar/squad@7b6d24c440a36b6815f21b70d25016731768db1f`, `plain_text/validation-00000-of-00001.parquet`, SHA-256 `8c6646d36bd5a95061e076788cf3161d11f6f3e7d625dac7a83bbed0a49f69f7`. **No train dataset, no blind TEST claim**. Preserve Stanford/Wikipedia attribution, CC BY-SA 4.0, no raw-text redistribution into this public repo.
- Full index of original 2067 unique `(title,context)` validation passages. `passage_id=SHA256(UTF8(title)+b'\n'+UTF8(context))`. Article group `SHA256(UTF8(NFKC(title)))`. For each of 48 article groups, choose 3 questions with the lowest SHA256 of UTF8(question_id), tie by ID, giving 144 questions. Selection **must not** read answers, model outputs or retrieval ranks; if actual counts/schema/IDs/near-duplicate policy violate G4, STOP rather than substitute cohort.
- R1: G4 BM25, NFKC + casefold Unicode word tokens, k1=1.2, b=0.75, smoothed positive IDF, unique query terms, deterministic passage-ID tie.
- R2: `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e`, official text-only ST pipeline, 768d normalized `float32` on Tesla T4 (NO `float16`). Query `prompt_name=QuestionAnswering`; document bytes `title: {title} | text: {context}` **without double prompt**. No silent truncation above 8192 tokens. Cosine similarity and same stable passage-ID tie.
- Frozen generator R3: `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`, no training. Exactly R2 top-3 original full passage texts in rank order, never a vector or SQuAD answer field in Qwen prompt. Answer-only causal teacher-forced NLL includes assistant end-of-turn marker; greedy decode `max_new_tokens=24`, Exact Match. No Adapter/LLM fusion, no PagedAttention/GQA claim.
- Retrieval metric: passage-source Hit@3 primary, MRR@3 secondary. Bootstrap **48 article-group means**, 10,000 resamples, seed `20261108`; evidence of R2 superiority only if 95% percentile CI **lower >0.0** for `mean(R2_hit3-R1_hit3)`; otherwise `NO_EVIDENCE_OF_SUPERIORITY`, not proof that embedder is invalid.
- R3 `S_SHORT`: source text, prompt, answer tokens and greedy allowance all fit effective length; no truncation. `S_LONG` descriptive only, no dropping based on outcomes. A single fixed Qwen system/user template is pinned in the source before results; R3 first published SQuAD answer is the frozen target for NLL and any published reference is accepted for EM. These are pre-execution implementation clarifications within the previously fixed G4 descriptive R3 scope, not new outcome thresholds.

## One integrated technical + science admission, not micro-permits

**New distinct run:** `ttm_embedgemma2_d1_g4_r1_r2_r3_once_20261109_v1`.  
**Drive:** `MyDrive/TTM_EmbeddingGemma2_D1_G4_Science/<RUN_ID>`.  
**Owner action:** running the exact locked Colab notebook `Runtime → Run all` on a **Free Tesla T4** constitutes authorization for this **one G4 scope**; no further Boolean owner-permission flags or separate technical QA permissions. ChatGPT cannot directly access/control the user's Colab runtime, so **no scientific run was executed by this decision**.

In the notebook, first validate exact G4 contract blob, R_gold RESULT SHA/status, Colab T4, free session selection, pinned ST6.1/Transformers5/Qwen source bytes, SQuAD SHA, cohort/mapping and resources **before creating a unique `CLAIM`**. Retain hard stop and `RESULT` if errors after CLAIM. Save per-phase and per-query original evidence; if Colab disconnects without terminal RESULT, resume only the same RUN_ID and pinned config, never re-run completed query records, do not create a replacement run. No change to R_gold originals.

Bounded envelope: max 30 minutes per Colab session, 5GiB planned new downloads, 8GiB new persistent project storage, paid spend $0. Runtime controls are best-effort for network retries and long GPU kernels; do not claim absolute limits guaranteed by a notebook.

**Source-only bundle, byte hashes** (conversation artifacts; not yet committed as source files in GitHub in this step):
- `TTM_D1_G4_R1_R2_R3_Integrated_OneShot_20261109.py` SHA-256 **`e05abde7d38ef9d6731c63ca42593dfdb2a59a44b14250e3c57364fd6ac5ec71`**.
- `TTM_D1_G4_R1_R2_R3_Integrated_Colab_20261109.ipynb` SHA-256 **`a7314667f49eaaad26ddd61bf1408b8cdf1ee8cd3b603caedb694c5b1ff3b6db`**.
- `TTM_D1_G4_Independent_Offline_QA_20261109.py` SHA-256 `f99db22030641f426d5a816ff9d340255c3900f176396b5de8c1aa59d199f4ab`.
- `TTM_D1_G4_Independent_Offline_QA_20261109.json` SHA-256 `a66cfb58ec3b1d8aab8ff4d25f034fb448907f88c2bb3fc7b8387afbf268acde`.
- Combined ZIP SHA-256 `9af3e9384a15edc4fb0aa80ec9f19ee2e838dc0379c34877fdc39a69236bc98a`.
- Offline source/algorithm tests **34/34 PASS**: deterministic label-blind selection on 10,570 synthetic QA rows / 2,067 synthetic unique passages / 48 groups, permutation stability, BM25 ranking/tie, paired group bootstrap, failure decisions, R3 prompt/top3/no-truncation, run-ID/claim/receipt and source locks. **This is not real Colab/runtime/science PASS**.

## Formal decision and limits

`G4_SINGLE_INTEGRATED_ADMISSION=READY_FOR_OWNER_RUN_ONCE`, not `R1_R2_R3=PASS`. The owner has requested a decision, not provided an observed science run; no research outcomes recorded in `lineage.md` at this point. Existing `L0011` is preserved; D2–D4 and any production claims remain closed. Only after reading the G4 terminal `RESULT.json`, original per-query receipts and independent metric/label leakage audits may an adjudicator enter a scientific PASS/NO_EVIDENCE/INCONCLUSIVE in append-only lineage.

**Next step:** launch the unchanged owner-side integrated G4 Colab notebook only when TTM-Small T5 has no shared resource conflict, and provide `TTM_G4_SCIENCE_STATUS`/`RESULT.json` for independent scientific QA. Do not re-run R_gold, and do not create new technical permit chains.

## Durable delivery to owner's connected Google Drive

The exact source+notebook+QA ZIP was uploaded to the owner's existing `TTM_EmbeddingGemma2_D1_Science` Drive folder and checked via metadata readback: [G4 integrated source + notebook + QA package](https://drive.google.com/file/d/1MNNanPTM9F565GU49Qat_17DNVoLANua/view?usp=drivesdk), 30,042 bytes, SHA-256 `9af3e9384a15edc4fb0aa80ec9f19ee2e838dc0379c34877fdc39a69236bc98a` as verified from the local bytes at upload time. This file is **source delivery only**, not a G4 scientific CLAIM or execution. The GitHub branch contains the admission decision; the ZIP source files are **not GitHub committed**, so do not misrepresent code review provenance.
