# HANDOFF — TTM H-DATA-S1 independent NEW FINAL24 blind rater (24 pairs / 240 scores)

**Operation:** `TTM_HDATA_S1_FINAL24_INDEPENDENT_FRESH_CHAT_BLIND_240_SCORE_FREEZE_NO_UNBLIND`  
**Date:** 2026-11-14  
**Reviewer role:** Independent blind rater (if AI, declare `EXPLORATORY_SCOPED_AI_REVIEW`, not human gold)  
**Status:** `RATING_NOT_STARTED` · `UNBLIND_NOT_EXECUTED`  
**Study run ID:** `TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1`

## Custody and input boundaries

The owner has completed exactly one new FINAL24 generation; independent byte/schema QA of its 24-neutral-pair packet is PASS. Its SHA-256, **verified by independent byte recomputation from the private Google Drive file**, is:

`60be28c7bde777c61d984209fad31a049702b806ef3d015c2af8a9c64ad1ccd8`

The packet filename is **`BLIND_FINAL24_RATER_PACKET.json`** and it contains 24 records `R01`–`R24`, each with `prompt_text`, `LEFT`, `RIGHT`, 48 continuations total; its bytes count is **14,801**. The owner must supply the actual packet to the independent rater securely (e.g. attach in a **fresh ChatGPT chat**, or grant rater narrowly scoped access). Do **not** publish it to public GitHub. The independent reviewer must verify this exact SHA before any scoring.

Additional permitted input (public-safe): frozen contract `docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_BLIND_SCORING_AND_ADJUDICATION_CONTRACT_20261113.json` and blank 24-record score template `docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_BLIND240_UNSCORED_TEMPLATE_SOURCE_ONLY_20261114.json`. Source QA report `artifacts/qa/ttm-small4m-h-data-s1/science_postrun/TTM_HDATA_S1_NEW_FINAL24_INDEPENDENT_PACKET_BYTE_CUSTODY_BLIND_GATE_20261114.json` is public-safe evidence of custody, not an answer key.

**Forbidden inputs for the rater:** owner generation receipt `OWNER_PRIVATE_GENERATION_RECEIPT.json` (contains per-arm statistics), one-shot sentinel, original owner private FINAL24/dev input, AES key, private H0/H1 mapping, anchor/key metadata, model weights, unblind labels, TRAIN/VAL/TEST, and source or generator code that reveals arm or sampling configuration. Do not search GitHub for answer keys or source fixtures.

## Exact immutable scoring contract

For each R01–R24, score **both** LEFT and RIGHT on exactly five named axes:

| Axis | Allowed integer values | Frozen meaning |
|---|---|---|
| `actor_retention` | 0 or 1 | 1 only if the continuation clearly keeps or uniquely refers to the original actor in a semantically consistent event; invented/ambiguous actor = 0 |
| `object_relation_retention` | 0 or 1 | 1 only if original object or unambiguous synonym remains in an appropriate action/relation; generic thematic mention = 0 |
| `goal_or_rule_progress` | 0 or 1 | 1 only if continuation advances, attempts or preserves the goal or temporal rule; ignores/contradicts = 0 |
| `coherence` | 0–3 | 0 unreadable; 1 fragmented; 2 mostly coherent; 3 coherent |
| `consistency` | 0–3 | 0 direct contradiction; 1 substantial drift; 2 mostly consistent; 3 consistent with prompt |

Total: **24 pairs × 2 sides × 5 axes = 240 integer scores**, plus exactly **24 nonempty short notes**, one per pair. If binary anchor support is ambiguous, score 0, do not force model-level wins, do not infer whether LEFT or RIGHT is the experimental model.

Only use the **prompt and two continuations** for each record. Evaluate exactly once in pair order; do not alter outputs, infer provenance, access other model trials, re-sample or tune rubric against observed data. Uncertain outcomes are part of the blind evidence.

## Freeze protocol (before any owner unblind)

1. Copy the blank `TTM_HDATA_S1_BLIND240_UNSCORED_TEMPLATE_SOURCE_ONLY_20261114.json` into a **new score file**. Fill all 240 integer fields (correct binary/ordinal ranges) and 24 nonempty `note` fields. Keep `pair_id=R01`.. `R24`, LEFT/RIGHT identity and field names fixed. Set score status to `SCORED_FROZEN_PENDING_UNBLIND`, and classify an AI rater correctly.
2. Use the locked `tools/pilot_t4/hdata_s1/ttm_hdata_s1_blind240_source_only_and_score_freeze_validator_v1.py --mode verify-scored --contract <FROZEN_CONTRACT> --scores <RATER_SCORE_FILE>` to validate; it returns (a) SHA-256 of the **exact score file bytes** and (b) SHA-256 of the **canonical score-array** with JSON `ensure_ascii=False,sort_keys=True,separators=(',',':')`. Alternatively recompute both with independent verified procedure.
3. Put the two SHA values into a **separate freeze receipt**, not into the score file being SHA-hashed; a file cannot straightforwardly contain its own exact SHA without self-reference. Freeze the completed score file and receipt in independent custody **before any unblind**. Do not edit them afterward.
4. Provide only the frozen score file, the two SHA values, rater classification and 24 notes to independent adjudication. **No H0/H1 mapping/unblind in this scoring chat.**

The owner-side evaluator (not rater) later uses frozen scoring and a **separately authorized** unblind to assess the unchanged primary gate: mean H1−H0 score `>=0.5`, strict pair wins `>=16/24`, paired 20,000-bootstrap CI95 lower `>0` with seed `20261113`; component and secondary guardrails remain unchanged. This handoff does **not** authorize unblinding or a scientific efficacy declaration.

## State at transfer

`OWNER_NEW_FINAL24_GENERATION=EXECUTED_ONCE` · `PACKET_SHA_AND_SCHEMA=PASS` · `NEW_FINAL_RATING=NOT_EXECUTED` · `SCORE_SHA_FREEZE=NOT_EXECUTED` · `UNBLIND=NOT_EXECUTED` · `SEMANTIC_BENEFIT=PENDING`.

**Do not rerun** NEW FINAL24 generation; do not provide `OWNER_PRIVATE_GENERATION_RECEIPT.json` to the rater.
