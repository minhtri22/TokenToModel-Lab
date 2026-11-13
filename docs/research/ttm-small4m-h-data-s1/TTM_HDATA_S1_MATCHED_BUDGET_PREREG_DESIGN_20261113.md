# TTM-Small-4M — H-DATA-S1 matched-budget data sampling & fresh FINAL24, preregistration DESIGN ONLY

**Operation:** `TTM_SMALL4M_H_DATA_MATCHED_BUDGET_NEW_HYPOTHESIS_PREREG_AND_FRESH_EVAL_DESIGN_ONLY`  
**Date:** 2026-11-13 (Asia/Bangkok) · **Branch:** `research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113`  
**Parent Git HEAD:** `37165ce6eea0bb4b04d316e2998da579c91d13cf` · **State:** `PASS_DESIGN_FREEZE; HOLD_SCIENCE_NOT_AUTHORIZED`.

## 1. Evidence baseline — facts, not causal proof

- Model T4/P02 has **3,749,376 parameters**, BPE 2,048, context 256. Historical private pack: TRAIN 2,048 stories, 2,691 windows, 498,287 distinct valid TRAIN labels, token pack SHA `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`. These facts come from prior source-only reports; **the private TRAIN/VAL token pack is not opened in this design step**.
- Prior A/C same step-1024 parent `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, same training schedule, 128 steps x 4,096 valid targets. Suffix loss C vs uniform A did **not** demonstrate a scoped adherence improvement. Consumed A/C FINAL24 remains closed.
- H-DEC-R1 (historical L0016) reduced word-trigram repetition from 28.60% to 3.79% on NEXT24 with penalty 1.15, but adherence D0=D1=0.0417/3; H-DEC NEXT24 is also consumed and cannot be tuned/reused.
- Earlier B/D first-story-window replacement **reduced** observed unique stories 1,493 to 1,363, so it is **not** evidence that first-window sampling increased diversity. No monocausal root-cause conclusion follows from any of these measurements.

## 2. One falsifiable H-DATA-S1 hypothesis (policy-level intervention)

**H1:** Under the same source TRAIN, initial checkpoint, uniform CE, T4 architecture, exact target-label presentations and 128 optimizer updates, a **single preregistered story-coverage/early-context sampling policy** improves the preservation of original actor, object relation and goal/rule in a new held-out 24-prompt continuation set compared with the original uniform-window sampling policy.

**H0:** H1 does not meet the preregistered minimum semantic improvement; specifically the paired average binary anchor score H1−H0 is less than +0.5/3 or any mandatory quality/coverage gate fails. Lack of a PASS is not proof of equivalence or proof that data never matter.

| Constant | Control H0 | Treatment H1 |
|---|---|---|
| Initial model/optimizer/scaler/scheduler | Same frozen P02-1024, independent clone | Same identical frozen P02-1024 |
| Model, tokenizer, context | 3.749M / BPE2048 / 256 | Identical |
| TRAIN/VAL source | Original unchanged split | Same exact split; **no new documents** |
| Main loss | Uniform valid-token CE, pad ignored | Identical CE |
| Window sampler | Frozen original uniform-window replay | One predetermined story-coverage and early-window preference policy |
| Steps | 128 (step 1025→1152) | 128 |
| Valid targets | 4,096/step; total **524,288** | Exact same by step and total |
| Window forward slots | 256 per drawn window | Same draw count and 256 forward slots *for every step* |
| Decoder at evaluation | Frozen plain greedy, 64 BPE max/EOS | Same, **no repetition penalty** |

**Budget accounting:** both arms total 256 optimizer steps and **1,048,576 label presentations**. These are presentations, not novel TRAIN tokens or claims of equal FLOPs from every possible implementation. The runner must compare microbatch count, window slots, step-level targets, LR, gradients and optimizer updates. No GPU runtime/wall time is claimed yet.

### Prespecified sampler H1 candidate — must pass actual-source feasibility QA

For each H0 sampled window with *scored* count `L` (1–256), H1 selects only from existing TRAIN windows with available valid target count `>=L`, masks any extra labels to `-100`, and preserves **exactly L labels**, same number of forward windows and 256 input slots. Choose via a deterministic priority: (1) story with fewer previous H1 draws, (2) early-context/offset-0 window, (3) stable SHA-256 seeded tie-break over run ID, step, draw and candidate index. The complete priority ordering and collision behavior are **candidate design**, not yet executable/frozen source. Fail closed if any draw cannot be matched; no unrecorded fallback. Both arms must restart from independent clones of same optimizer state; H1 sampling RNG is separated from model dropout RNG to avoid accidental additional intervention.

**Pre-execution manipulation check:** Require **at least +5% relative distinct TRAIN stories sampled** AND **at least +10 percentage points absolute offset-0 window share**, compared to H0, alongside **exact equality** of step-level targets/forward windows/slots. If one condition fails, `HOLD_SAMPLER_NOT_A_VALID_POLICY_CONTRAST`, not science GO. Achieving these checks does **not** by itself prove semantic improvements. The two desired changes are bundled into **one sampler treatment**; this experiment cannot attribute the benefit solely to diversity versus early-context emphasis.

## 3. NEW held-out evaluation frozen before any future training/inference

- New original assistant-authored English prompts: `HD01–HD12` DEV12 plus **`HF01–HF24` FINAL24**. Four strata with 3 DEV and 6 FINAL each: `object_custody`, `social_relation`, `causal_obstacle`, `temporal_rule`. Prompts explicitly mention actor/object/goal but owner anchor metadata is hidden from blinded raters.
- Owner-private **36-prompt JSON** byte length **18086**, SHA-256 **`b129a5c52520a25f1c40de950471622320abfa6b5414d0b16e0111ed96adc680`**, to be stored in private Drive; original wordings not published on GitHub. SHA commitment file **`6c8c21c406b4bc30171244142c4226460a6735164f88fd425db7afa070a6f4f3`**, DEV12 public **`60e514a2329abe6b6df673058ee7656bb57287758c6ee4cc861a396a1788ba3d`**.
- 36 distinct SHA-256 prompt hashes; exact overlap with **24 consumed NEXT24 SHA commitment hashes: 0**. No consumed NEXT24 prompt plaintext was reopened. This **does not guarantee** independence from unknown TRAIN, TEST, Q1/Q2/OOD or all historical closed sets; these were not read. New within-set word-trigram max-Jaccard: **0.065217**. No universal leakage claim.
- BPE encode/decode roundtrip and final 256 context validation are **PENDING** until source-only runtime check; no model inference will be performed for those checks. No preexisting evaluation or score is copied into the new packet.
- No paired arm mapping generated yet. Before future model-forward, owner must create **new random balanced 12/12 LEFT/RIGHT**, 3/3 per stratum, seal AES-256-GCM with append-once custody and SHA without publishing key/mapping. Rater need only accept **after generation** in separate context; score freeze with SHA **before** owner unblind.

## 4. Frozen candidate scoring contract (source-only; new rubric)

Document `TTM_HDATA_S1_BLIND_SCORING_AND_ADJUDICATION_CONTRACT_20261113.json` defines five fields per text: **actor retention 0/1**, **object-relation retention 0/1**, **goal/rule progress 0/1**, **coherence 0–3** and **consistency 0–3**. The **primary 0–3 score** is the sum of the three binary anchor judgments. A fresh rater scores 24 paired prompts × two texts × five fields = **240 numeric values**, with 24 explanations, self-attested AI unless an actual human participates.

**Primary outcome:** `mean_over_24(score_H1 - score_H0)` on completely new FINAL24. **All-gate exploratory PASS** requires simultaneously:

1. Mean H1−H0 **≥+0.5/3** in anchor score (at least 12 net anchor points across 24 prompt-pairs).
2. **≥16/24** strict H1 pair wins, ties do not count.
3. Paired prompt-cluster bootstrap CI95 lower **>0**; `numpy.random.default_rng(20261113)`, 20,000 resamples, quantile 0.025/0.975, NumPy exact version to be frozen in source QA.
4. Goal/rule mean component improvement **>0**; actor and object component mean deltas each **≥−0.125**.
5. Coherence and consistency mean changes each **≥−0.25/3**; VAL NLL regression against matched H0 **≤5%**; H1 count of outputs with <8 words does not exceed H0; report EOS/cap64, no filtering.

No target can be changed after training/inference. If any gate fails, report **`H_DATA_S1_NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT`** (not universal failure). One parent, two arms, one final set, one AI rater: only exploratory scoped evidence, not independent human peer review or proof of general causality.

## 5. Data rights, custody, and one future integrated GO/HOLD gate

- Reuse pinned TinyStories internal TRAIN/VAL only; no raw TRAIN/VAL, reversible token pack, checkpoint, EOS/VOCAB manifest or private key published to GitHub. Prior owner A/C rights (`internal_A_C_only=true`) and H-DEC inference GO **do not grant H-DATA new training rights**. New owner science scope and actual source-license/rights review required.
- Confirm exact parent checkpoint SHA + optimizer/scaler/RNG resume, train pack SHA, tokenizer BPE manifest SHA, identical target budgets, sampler real window metadata, independent synthetic negatives for failed length matching, stop/restart behavior on Colab T4, owner Drive space; protect original checkpoints. Require **one signed owner scope decision** for two new arms, not micro-permits.
- Rater acceptance can be deferred until after fresh one-shot inference, but blind scheme and rater handoff template must be frozen **before** generation; no reviewer receives training logs, arm IDs, anchor ground truth or original owner keys.
- `TEST/Q1/Q2/OOD` access **NOT REQUESTED**; no reopening A/C FINAL24, H-DEC NEXT24; no untrusted web retrieval for raw data. New FINAL24 is frozen and remains unseen for model-selection and hyperparameter tuning.
- `lineage.md` append-only; main unchanged. This design-only phase creates no claimed scientific outcome.

## 6. Formal owner decision and next step

**`PASS_SOURCE_DESIGN_AND_FRESH_EVAL_SHA_FREEZE__HOLD_NEW_TRAINING_PERMISSION_SOURCE_RIGHTS_SAMPLER_REAL_QA`**.

Next single integrated gate: `TTM_HDATA_S1_ONEPACKET_SAMPLER_SOURCE_REAL_METADATA_QA_RIGHTS_T4_RESUME_AND_OWNER_GO_HOLD_PREEXEC_NO_TRAIN`.

One pass should implement/freeze sampling code, verify length-matched windows on the private TRAIN pack without exposing raw tokens, exact 128×4096 budgets, source pins/rights, owner-private BPE and context, and blinded mapping custody. Only after a separate GO can two-arm Colab T4 training/inference be initiated. Current experiment remains **DESIGN ONLY**; 0 train steps, 0 model forwards, 0 TEST/Q1/Q2/OOD accesses.
