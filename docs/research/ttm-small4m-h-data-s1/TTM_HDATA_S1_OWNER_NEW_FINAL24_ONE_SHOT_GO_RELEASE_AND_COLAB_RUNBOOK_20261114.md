# H-DATA-S1 — Owner NEW FINAL24 one-shot inference GO (separate release)

**Operation:** `TTM_HDATA_S1_OWNER_NEW_FINAL24_ONE_SHOT_INFERENCE_RELEASE_SINGLE_GATE`  
**Date:** 2026-11-14  
**Owner explicit decision:** `GO_HDATA_S1_NEW_FINAL24_ONE_SHOT_OWNER_INFERENCE`  
**Scope:** A **single owner-manually-launched** one-shot Tesla T4 generation of H0/H1 NEW FINAL24 neutral LEFT/RIGHT packet; no training, scoring or unblinding. No assistant-initiated model forward in this authorization operation.

## 1. Source-of-truth and approval

Owner in ChatGPT explicitly affirmed GO for the operation above. The permit is a public-safe record of this explicit owner chat decision; **not** a cryptographic signature or an independently attested human statement.

- Locked permit: `artifacts/qa/ttm-small4m-h-data-s1/science_postrun/TTM_HDATA_S1_OWNER_NEW_FINAL24_ONE_SHOT_INFERENCE_GO_PERMIT_20261114.json`
- Exact permit SHA-256: `242a0925320e9c4aeb716fca4324cdce12d384f52322589f2e403ae464702581`
- Frozen candidate source: `tools/pilot_t4/hdata_s1/ttm_hdata_s1_new_final24_blind_generation_candidate_source_only_v1.py`; SHA-256 `7953d33fa592a8890a185cedf490d7af2df9514e025395f00a1996c7bf784363`; Git blob `f257e484d0a5bccde5a7e6ff845251cb9025ed31`
- Exact **release checkout** containing both source+permit: `9ed7116b53eeb77ddbcc4b5728c81a6a971f8dfe`. This checkout is immutable and distinct from original science commit `7aec0d551c930936412b93eb49951bd1597d71b9`; source P02/BPE/AES blobs from the science era are still SHA/Git-blob pinned.
- Independent source-only release QA `tools/pilot_t4/hdata_s1/independent_hdata_s1_owner_final24_one_shot_permit_source_qa_v1.py`, GitHub Actions run [43552923301](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43552923301): **PASS**. This tested permit integrity, known science receipt, checkpoint SHA claims, notebook syntax, fail-closed default, missing-permit negative; **did not** read private prompts, AES key, model tensors or execute GPU.
- Owner-only Colab notebook: `tools/pilot_t4/hdata_s1/TTM_HDATA_S1_OWNER_NEW_FINAL24_ONE_SHOT_COLAB_20261114.ipynb`.

## 2. Scientific baseline and preserved locks

The already-completed H0/H1 science has **128 updates per arm × 4096 valid targets per update**, eight READY checkpoints and both final model/optimizer states at step **1152**. Independent prior custody verified checkpoint H0 SHA-256 `a7cdade3b70cb2ceed258edd1e3edd494ce9745633d2e528ee90232f3c95c2fe`; H1 `31d9365a470e638f77e6661252ed8d0605e9f9095da145d9f48751adcdcfcb64`. No new science updates are licensed. VAL NLL H0 `3.511285912623514`, H1 `3.5057606759493716`; VAL guardrail PASS, semantic effect PENDING.

Owner-private FINAL full file SHA-256 `b129a5c52520a25f1c40de950471622320abfa6b5414d0b16e0111ed96adc680`. Public NEW FINAL24 hash commitment SHA-256 `6c8c21c406b4bc30171244142c4226460a6735164f88fd425db7afa070a6f4f3`. Existing AES ciphertext SHA-256 `de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d`; existing escrow ZIP SHA-256 `c5c5d6eae6ce38d892348878ae200d5bbcd42406b53f7b0c43e8876a145d48d4`. No AES rekey, remapping, second prompt set or resurrection of consumed historical FINAL/NEXT24 allowed.

## 3. Exactly one owner Colab launch, no auto-dispatch

1. Ensure the Tesla T4 is idle (do not overlap with FC01 or other running scientific code). Open the NEW FINAL24 Colab notebook linked above from the research GitHub branch or its pinned notebook commit, **not** the previous H0/H1 training Cell 4.
2. In its second cell set **only** `HDATA_FINAL24_RUN_NOW=True`; run once. Default remains `False`. The cell self-initializes all paths and dependencies; it does not rely on variables from another FC01/H-DATA notebook.
3. The launcher mounts owner Drive, rejects existing FINAL root, verifies immutable Git checkout `9ed7116...`, source and permit SHA, existing final H0/H1 checkpoint SHA and finds the original P02/BPE pins. It invokes the exact frozen generator with `--mode generate --permit ... --permit-sha ...`, with child stdout+stderr retained in the Colab output.
4. The generator rejects any non-T4 or non-`torch 2.14.1+cu130` runtime. Before first forward it checks exact owner FULL FINAL bytes, 24 HF01–HF24 individual hashes/strata/unique ordering, ALL 24 BPE roundtrips and `len(prefix)+64 <= 256`, pinned AES map validity and balanced 12/12 LEFT and 3/3 per stratum, source checkpoint state and SHA. Only then can it create the fixed run root and one-shot sentinel.
5. Generation uses **plain greedy argmax**, up to 64 new BPE tokens or EOS=256 (no temperature, top-k, repetition penalty, adaptive decoding or outcome tuning). Both models produce 24 continuations each; AES-fixed LEFT/RIGHT assignment produces `R01–R24` with 48 continuations.
6. The owner-local outputs are in `/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_h_data_s1_20261113/new_final24_blind_generation_once_v1/`:
   - `STARTED_NO_REPLAY.json` — one-shot sentinel, created after preflight
   - `BLIND_FINAL24_RATER_PACKET.json` — **private prompt text** and neutral model-blinded continuations; share only with intended independent rater; not a public-GitHub artifact
   - `OWNER_PRIVATE_GENERATION_RECEIPT.json` — generation SHA/metadata, EOS/cap64/under8 counts (owner-side only)
7. If successful, report only `HDATA_S1_FINAL24_PACKET_SHA256`, `HDATA_S1_FINAL24_RECEIPT_SHA256`, final status and whether the root exists to independent QA. Do **not** paste AES key, owner private mapping or checkpoint tensors to public GitHub.

If any error, **do not rerun** the one-shot cell, **do not overwrite/delete** the run root or rekey AES; preserve the child traceback, sentinel and any partial data for independent adjudication. A fresh run or resume is NOT automatically released.

## 4. Next after generation — separate blind review and later owner unblind

Only when the exact packet SHA, 24 neutral pairs and 48 continuations pass private packet QA, hand the packet to a separate blinded rater. Five fixed rubric axes × two sides × 24 pairs = **240 integer judgments plus 24 nonempty notes**. Rater must freeze (a) SHA-256 of the exact complete score file bytes and (b) canonical score-array SHA-256 **before** owner unblinding; if AI, classify as `EXPLORATORY_SCOPED_AI_REVIEW`.

This GO **does not** authorize scoring, owner AES unblind, TEST/Q1/Q2/OOD opening or new model training. Existing score thresholds and paired bootstrap controls are immutable. The semantic-benefit verdict remains **PENDING**, no universal contamination-free claim.

**Authorization verdict:** `GO_HDATA_S1_NEW_FINAL24_ONE_SHOT_OWNER_INFERENCE`; `OWNER_LAUNCH=PENDING`; `MODEL_FORWARD_BY_THIS_CHAT=0`; `NEW_FINAL_ALREADY_CONSUMED_BY_THIS_CHAT=FALSE`; `SCIENCE_TRAINING_RERUN=NO`; `BLIND_SCORING=NOT_EXECUTED`; `UNBLIND=NOT_EXECUTED`; `MAIN=UNCHANGED`.
