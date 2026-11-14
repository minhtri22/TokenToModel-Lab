# TTM H-DATA-S1 FINAL24 — Owner-authorized one-shot read-only AES unblind and formal adjudication

**Operation:** `TTM_HDATA_S1_FINAL24_OWNER_UNBLIND_ON_FROZEN_AI_SCORE_SINGLE_GATE`  
**Date:** 2026-11-14  
**Explicit owner authorization:** `GO_HDATA_S1_FINAL24_OWNER_UNBLIND_ON_FROZEN_AI_SCORE`  
**Research classification:** `EXPLORATORY_SCOPED_AI_REVIEW` (one independent blind AI rater, not human gold)  
**Formal scientific outcome:** `H_DATA_S1_NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT`  
**Execution state:** `UNBLIND=EXECUTED_ONCE_READ_ONLY`; no training, generation, scoring edits, AES rekey, or repeat FINAL24.

## 1. Chain of custody, original frozen inputs, and explicit GO

A separately committed permit records the owner's explicit GO in this conversation:

`artifacts/qa/ttm-small4m-h-data-s1/blind240/TTM_HDATA_S1_OWNER_EXPLICIT_ONE_SHOT_UNBLIND_GO_PERMIT_20261114.json` (permit commit `e483dc9997fecd5b62b9eadcfc46612e39b6df5a`). This permit is an owner-chat approval receipt, **not** an independent cryptographic human signature.

Only these exact, previously frozen bytes were accepted:

| Artifact | SHA-256 |
|---|---|
| Blind rater score file, 240 scores and 24 notes | `81a680be56c7535a2a14137be69d121c76a43cb28f2b93995b020471609966f4` |
| Independently verified canonical 240-score array | `fcbd93e8c2580566eb0414301a9afa5a13d07b2c179c8fe686bad3ccd68a167e` |
| Separate blind rater SHA freeze receipt | `fdf09445234fbf6d7a5d5092f685590720dfede88672d6229060768cc9cce449` |
| Original sealed neutral FINAL24 packet | `60be28c7bde777c61d984209fad31a049702b806ef3d015c2af8a9c64ad1ccd8` |
| Owner one-shot FINAL24 generation receipt | `e2fca65f2d1571a8e61c365ea69d34dc4876af6c5741a55c25ec60aa6d17a4df` |
| Owner original AES backup ZIP | `c5c5d6eae6ce38d892348878ae200d5bbcd42406b53f7b0c43e8876a145d48d4` |
| Owner original encrypted blind escrow JSON | `de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d` |
| Science READY-last owner receipt | `e30a2281580b1f6ea33856577f0a244cd02e226dc8a3db00d207a8fe13cce4b5` |

The original, sealed 24-pair mapping was decrypted **once**, in memory, with `AES-256-GCM` using the pre-existing owner's encrypted escrow and key, the frozen AAD and verified nonce/key lengths. SHA-256 of the authenticated plaintext mapping matched both the encrypted escrow and owner key receipts; its 24 pair IDs and four strata matched the frozen mapping schema. Balance: **LEFT H0/H1 = 12/12**, each of four strata **3/3**. No per-pair arm identity, decrypted AES plaintext, key, owner private prompt, reviewer note, or continuation was written to the public outputs.

Before decrypting, the original scored file (240/240 integer values, 24/24 nonempty notes), neutral packet and canonical array were independently validated. The canonical array was reconstructed **byte-for-byte** from the frozen score file, with `ensure_ascii=False,sort_keys=True,separators=(',',':')`. No scoring was changed.

## 2. Exact preregistered primary evaluation

**Frozen primary endpoint:** mean (H1 minus H0) of the three binary semantic retention axes on the same 24 prompt pairs. The per-continuation primary score is an integer in 0–3.

| Primary gate | Exact readback | Threshold | Adjudication |
|---|---:|---:|---|
| H0 mean primary score | **0.000** | — | Descriptive |
| H1 mean primary score | **0.000** | — | Descriptive |
| Mean paired H1−H0 | **0.000** | ≥ 0.500 | **FAIL** |
| Strict H1 pair wins | **0/24** (24 ties) | ≥ 16/24 | **FAIL** |
| Paired bootstrap 95% CI | **[0.000, 0.000]** | lower > 0 | **FAIL** |

The independent source implementation executed **20,000 paired bootstrap resamples** of the original 24 pair differences with `numpy.default_rng(20261113)` and fixed 2.5th/97.5th quantiles. All primary pair differences are exactly zero, so all bootstrap estimates are zero. This is a consequence of frozen scoring, not a claim of general statistical equivalence.

## 3. Components, secondary guardrails, and generation diagnostics

| Component / guardrail | H0 | H1 | Delta H1−H0 | Frozen verdict |
|---|---:|---:|---:|---|
| Actor retention mean | 0 | 0 | 0 | PASS (≥ −0.125) |
| Object-relation retention mean | 0 | 0 | 0 | PASS (≥ −0.125) |
| Goal/rule progress mean | 0 | 0 | 0 | **FAIL** (strictly > 0) |
| Coherence mean (0–3) | 0.708333 | 0.666667 | −0.041667 | PASS (≥ −0.25) |
| Consistency mean (0–3) | 1 | 1 | 0 | PASS (≥ −0.25) |

The science VAL guardrail remains **PASS**: H0 NLL `3.511285912623514`, H1 NLL `3.5057606759493716`; relative H1−H0 regression `−0.0015735650162462102` (approximately −0.1574%, well below the allowed +5%).

The original generation receipt, without any additional model forward, reports:

| Diagnostic | H0 | H1 | Interpretation |
|---|---:|---:|---|
| EOS stops | 7/24 | 4/24 | Reported as preregistered, not an independent win gate |
| Cap of 64 tokens reached | 17/24 | 20/24 | Reported as preregistered |
| Under 8 words | 0 | 0 | PASS: H1 ≤ H0 |

**Combined frozen gate outcomes:** 7 PASS, 4 FAIL among 11 source-defined checks. The four failures are the **three primary gates** and the **goal-progress improvement guardrail**. The contract's `outcome_otherwise` applies.

## 4. Final scientific decision and honest limitations

**FORMAL ADJUDICATION: `H_DATA_S1_NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT`.**

This closes the preregistered **H-DATA-S1 FINAL24 comparison** under the already frozen AI scores. The experiment **did not demonstrate** an H1 semantic benefit relative to H0. Neither source integrity, readiness, valid AES blinding nor the slightly lower H1 VAL NLL overturns the preregistered failure to retain actors, object relations and goal/rule progress on new prompts.

This is a 24-pair, one-rater **exploratory**, one-seed comparison. It is not a human gold evaluation, a broad instruction-following benchmark, a multi-seed confirmatory result, or proof that H1 can never improve under another *prospectively registered* design. No ad hoc rescoring, changing thresholds, reparsing the same FINAL, hidden extra sampling, or repeat generation is permitted as a means of reversing this result.

## 5. Evidence and immutable source provenance

Public-safe exact aggregate JSON:
`artifacts/qa/ttm-small4m-h-data-s1/blind240/TTM_HDATA_S1_FINAL24_READONLY_UNBLIND_PUBLIC_AGGREGATE_20261114.json`  
SHA-256 `23df562a73c7f83096ba4ec683da81823d0104a80fbf689b01b4310348e3a7e2`, Git blob SHA-1 `6e65e09de495e9c196fecd307427e25c835958b5`. Independently verified the public GitHub file has the **exact same blob** as the locally executed 4,225-byte report.

Audit source (no embedded key or plaintext mapping):
`tools/pilot_t4/hdata_s1/ttm_hdata_s1_owner_readonly_AES_unblind_adjudicator_v1.py`, SHA-256 `fe56fc553b3b318bc57bd3238d627bd2435bbac4957d11fc06acd9ab565975ab`, Git blob SHA-1 `72088d4cda26a25ef7c1f42fe73b7ca283fe0234`.

Owner Google Drive copy of the public-safe exact aggregate:
`TTM/ttm-small-pilot/ttm_small4m_h_data_s1_20261113/public_safe/TTM_HDATA_S1_FINAL24_READONLY_UNBLIND_PUBLIC_AGGREGATE_20261114.json` — uploaded and downloaded for independent byte readback, **exact match** of 4,225 bytes and SHA-256. Also mirrored to the private ChatGPT Library folder used for earlier blind240 custody.

Only the above public-safe aggregate, auditor script, permit and report are committed to GitHub; the raw score JSON, notes, AES key, decrypted per-pair mappings, original prompts, model weights and original private escrow remain private. `main` remains unchanged.

**Follow-on recommendation:** Close this original scientific gate as `NO_DEMONSTRATED_BENEFIT`; if pursuing H1 mechanisms, open a **separate prospective, design-only diagnostic** using fresh data and distinct preregistration. Do not reopen the consumed FINAL24 or training one-shot.
