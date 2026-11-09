# TTM EmbeddingGemma 2 — D1 R_gold one-shot: independent science receipt adjudication

**Ngày:** 2026-11-09 (Colab run UTC 02:00, Asia/Bangkok ~09:00).
**Operation:** `TTM_EMBEDDINGGEMMA2_D1_RGOLD_OWNER_RUN_ONCE_THEN_INDEPENDENT_SCIENCE_QA`
**Run ID:** `ttm_embedgemma2_d1_rgold_one_shot_20261109_v1`
**Formal scoped verdict: `PASS_RGOLD_SCREEN_SCOPED_SYNTHETIC`.**
**Independent offline QA: `PASS_1273_OF_1273`.** This is independent hash + per-group metric/CI/criterion recomputation from frozen outputs; **not a second model execution, human peer review, or independent replay of raw Qwen logits**.

## 1. Immutable source and original Drive evidence

User-run Colab original evidence:
- Run folder: https://drive.google.com/drive/folders/1qRTvDpGa4tYw3PKG3QJ0iI3VkTQAN0ZB
- `CLAIM.json` (original, SHA-256 `bd893f53b1877c09a7886afc6420a4a21c68d869f7fbb08a218ea074062a8fc1`): https://drive.google.com/file/d/1fuzN4oDzT-4iqD3SvJ0kXwWeXNJ13hF0/view
- `RESULT.json` (original, SHA-256 `43e7a78d763a5f3bcf3a049b97d3ae59b0e6010f42d106eb3d1efc652c01735b`): https://drive.google.com/file/d/1T2JD7P31mz6_X_oa2nXh4plXCkUp4qZL/view
- 60 individual group files: https://drive.google.com/drive/folders/1TS27swxIXljzUhl5MPddqSgvFBTazTod
- Frozen 60-group fixture SHA-256 `0215719de94f86a4f2b7a48959ca81343014c127e74799f737901a57b33f341a`; source-file Git blob SHA-1 `d6b23349d65724c5a7aaba41604b396facabfbe8`; fixture Git commit `b10deb62567571dc4aa68e5aad9fe06b55d1e23b`.
- Runtime science source SHA-256 `221a3dde64b29a24bd86c6b8035cf501007163c5c0b458205379da0dfc89a70a`, recomputed on the original source bytes in the previously issued ZIP package. `CLAIM.config_sha256=09a03152701c3d0ceea493fdd2af076109f54dc6b6ba9c708755f87e0953aea0`, independent canonical JSON rehash matches; RESULT matches claim.
- Original `RESULT.status=COMPLETED_UNADJUDICATED_RGOLD_SCREEN_PASS_CONSERVATIVE_NONEXACT_GUARD`; this document, **not** the original result, provides the separate scoped adjudication. Do not alter CLAIM, RESULT, group files or run ID.

The inputs were individually retrieved read-only through the owner's Google Drive connector, and SHA-256 was recomputed for every one of the 60 downloaded files against `RESULT.per_group_sha256`: **60/60 exact matches**. Group schema, IDs, question uniqueness, config hash linkage, cohort and target masks passed; offline audit ran **1,273 checks, all PASS**. All metric recomputation used saved per-group numerical values, not untrusted aggregate verdict fields. Numeric GPU inference was *not* repeated.

## 2. Frozen decision-rule recomputation

Locked main metric is equal-weight **group average** over 48 independent *fixture group IDs* of within-group mean answer-only `NLL(R0)-NLL(R_gold)`. Qwen teacher-forcing scorer included the assistant end-of-turn `<|im_end|>` token **in the loss denominator**, equally for each paired arm, as declared by the frozen CLAIM. It should be called `answer+end-token normalized NLL`, not a raw answer-only token-count metric without end marker. No post-result threshold change was made.

| Criterion | Locked threshold | Independent recomputation | Verdict |
|---|---|---|---|
| Primary mean group improvement | CI lower > **0.10** nats/token | mean **7.447853279750011**; paired group percentile 95% CI **[6.894292531469365, 8.04105708922633]**, **B=10,000**, seed `20261108` | **PASS** |
| EM with correct evidence `R_gold` | ≥ **0.60** | **91/96 = 0.9479166666666666** | **PASS** |
| EM improvement over no-evidence `R0` | ≥ **0.10** | `0.9479166666666666 - 0 = 0.9479166666666666` | **PASS** |
| Wrong-evidence sanity | group mean `NLL(R_wrong)-NLL(R_gold)>0` | **5.64740384731736** nats/token | **PASS** |
| No-answer guard | ≤ **6** unsupported responses among 24, conservative any nonexact UNKNOWN count | **0/24**, 0/12 bad groups | **PASS** |

**Data completeness:** 48 positive groups (2 questions each), 12 negative groups (2 each); 60 group IDs, 120 unique question IDs, no invalid/missing group file or nonfinite NLL. **45/48 positive groups** have 2/2 exact correct. Five R_gold Exact Match failures were preserved, not dropped: `RG-P-007-Q2` (expected cobalt, output `FICT-1-007-ALT`), `RG-P-019-Q1/Q2` (flax → velvet), `RG-P-029-Q1/Q2` (mesh → linen).

**Limits:** Synthetic groups were generated using repeated fact templates (48 groups across only three answerable attribute kinds); group-level bootstrap is **conditional on this artificial sample** and does *not* independently validate generalization or human quality. The gold evidence contains the requested fictional answer by design. The model's no-evidence R0 mostly predicts UNKNOWN. `0/24` unsupported answers is **not a general hallucination safety certificate**. Scoring is based on stored target NLL and exact-string greedy outputs, not a blind external TEST.

## 3. One-shot integrity and resources

- Qwen source: `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`, frozen; GPU: Colab **Tesla T4**; no training.
- Parent V3 result SHA-256 `ce693326af246fdf2a3806427b46d89ce05e944a4c99e442b24004677e892427`, parent Qwen targeted result SHA-256 `b9f859bc639bd953893b3443b437f23182231e3297149c3cbaaa3bad2b84b2cd`. Parent technical V1/V3 **FAIL** statuses must remain.
- Reported total measured runtime **168.402 s**, within 1,800-second envelope; Colab source/weights setup occurred before science CLAIM; start/end timestamps of RESULT alone show the post-CLAIM portion, not total duration.
- Reported max GPU allocated memory **1,219,962,368 B** (~1.14 GiB); Drive project persistent storage **999,676,014 B** (~0.93 GiB), under 8 GiB. Values derive from original receipt (not externally instrumented hardware counters). No paid GPU claim.
- `science_executed=true`, `test_scored=false`, `retrieval_evaluation=false`, `model_training=false`. R_gold **consumed once**. Do not rerun, modify results, pick a subset or create replacement RUN_ID.

## 4. Formal adjudication and precise next gate

**`R_GOLD_SCIENCE=PASS_SCOPED_SYNTHETIC_CAPABILITY_SCREEN`** with all five predeclared numeric gates met and per-group data integrity confirmed. This is evidence **that frozen Qwen can utilize supplied oracle/ground-truth evidence** on the exact toy cohort. **EmbeddingGemma 2 did not participate in this science run**. Neither `R1` lexical retrieval nor `R2` embedding retrieval nor `R3` retrieval-augmented Qwen have run, so **no retrieval superiority, vector fusion, real-world RAG, GQA, PagedAttention or TTM-Small claims** follow. Public SQuAD validation remains a separate future scope.

**`D1_RGOLD_GATE=SATISFIED_FOR_CONSIDERING_R1_R2_R3`**, not blanket authorization. Before starting R1/R2/R3, use a **single integrated** approval/compatibility check based on the G4 frozen protocol, materialize/query the existing pinned SQuAD selection manifest and hardware budget, respect **TTM-Small T5** resource priority; run no new science without that exact scope. Do not reopen G1–G4 or repeat R_gold. No extra technical micro-permits.

**Append-only lineage:** this is the first scientific result of this D1 line and should be appended to `lineage.md` on the independent D1 branch, leaving earlier entries intact. No QA-only/infra entries from V1, V3 or Qwen targeted failure are appended as D1 science. Separate technical docs already preserve the diagnostic FAIL/PASS details.

**QA companion artifact:** `TTM_D1_RGOLD_INDEPENDENT_SCIENCE_QA_20261109.json`, exact SHA-256 `0723d3f173e09633414fe4fa7270ada55fb7e9be307ab2504d0a6c0cb38f7c0c`. The review does not replace external human validation of the synthetic fixture.

**Final:** `R_GOLD_ONE_SHOT=CONSUMED` · `INDEPENDENT_QA=PASS_1273/1273` · `R_GOLD_SCREEN=PASS_SCOPED_SYNTHETIC` · `R1_R2_R3=NOT_EXECUTED` · `D2_D4=NOT_OPENED` · `TTM_SMALL_T5=PRIORITY_FIRST`.
