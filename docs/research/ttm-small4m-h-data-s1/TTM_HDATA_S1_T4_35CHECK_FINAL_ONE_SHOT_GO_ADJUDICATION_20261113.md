# TTM H-DATA-S1 — T4 independent readback & one owner GO release (NO AUTO TRAIN)

**Operation:** `TTM_HDATA_S1_COLAB_T4_NATIVE_2ARM_FP16_INTERRUPTED_RESUME_INDEPENDENT_READBACK_SINGLE_GATE_NO_SCIENCE`  
**Date:** 2026-11-13  
**Research branch:** `research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113`  
**Owner decision:** **`GO_SCOPED_ONE_SHOT_OWNER_MANUAL_DISPATCH_NO_AUTO_TRAIN`**.

## 1. Exact owner Colab T4 receipt

An authenticated read of the owner-private Drive receipt yielded **1735 exact bytes**, SHA-256
`c93fe27e275cd7a1bcd80f369b2a54667a3da3a5b6a942482f80c0b80c38af8c`,
equal to the reported owner hash. No private checkpoint, TRAIN token array, plaintext FINAL, key or secret mapping was copied to GitHub.

Receipt reports native **Tesla T4**, **Torch 2.14.1+cu130**, both arms H0/H1 `PASS_FULL_STATE_EXACT` for direct steps 1025–1026 versus 1025→disk checkpoint→resume 1026. Scope: full model, AdamW, scheduler, GradScaler, Torch/Python/NumPy RNG, sampler state, H1 exposure; each arm reports 4 QA optimizer updates, exactly **8 QA updates total**, 4096 labels per step, **0 science optimizer updates**, **0 science inference**. Temporary QA checkpoints were removed.

An independently implemented receipt **readback** checked 35/35 values and hashes, 0 failed; this independently verifies the receipt's consistency and frozen source pins but **does not represent a second independent Tesla T4 run or human peer review**. Public-safe receipt: `artifacts/qa/ttm-small4m-h-data-s1/preexec_real_train/TTM_HDATA_S1_T4_NATIVE_INDEPENDENT_READBACK_20261113.json`.

## 2. Existing frozen inputs and rights

TRAIN/VAL pack SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`. P02 parent checkpoint step 1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. BPE2048 SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. Full prereg paired schedule SHA256 `bcb354d29540e3a348b76173cdad1a6e2832dc81f995c717b68be6926d456591` from original real TRAIN metadata; 128 steps/arm, 4096 targets/step, 2928 windows/arm. H1 chooses 100% first windows and is a strong distribution shift, not a demonstrated scientific gain.

Owner scope-specific internal research rights receipt SHA256 `f1ae54c94d8c6a4a55febd4544b7c474ae73f060e8e9f64b426b5ca91740de2f`, TinyStories upstream declared CDLA-Sharing-1.0. Prior A/C rights were **not** reused. This is a scoped owner and source card review, not external legal certification.

NEW FINAL HF01–HF24 stays sealed and never reused old FINAL/NEXT24. AES-256-GCM mapping was created before any owner QA model forward, encrypted ciphertext SHA256 `de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d`. Owner-private ZIP exact Drive readback 4159 bytes SHA256 `c5c5d6eae6ce38d892348878ae200d5bbcd42406b53f7b0c43e8876a145d48d4`. No key or clear arm mapping on GitHub.

## 3. Production runner source QA and safety amendment

Original science runner candidate was frozen as source-only, no science executed. An exact pre-outcome, pre-train guard amendment strengthened two fail-closed properties without changing the prereg scientific treatment:

1. **Exactly one fixed run root**: `/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_h_data_s1_20261113/science_one_shot_v1`. Owner lock and runtime path must match. A duplicate new run or unsupported resume fails closed.
2. **Strict actual forward budget**: no additional FP16 GradScaler retry model-forwards are silently accepted. If retry occurs or targets/window count/optimizer updates drift, abort with `HOLD`; do not report that run as valid science. No alternative policy or result-driven tuning authorized.

Updated production runner Git blob SHA1 `d9a80aea9a80f5bf2e98f2fe4b054e5830944823`; SHA256 `eae016e92adc862e71d98920844ebd7c36bacbc3c9157c5a5e33d31aa77ded28`. Native QA runner source SHA256 `7db0f999934036fc4f87beda9cd5a131377147d7307e9de5ac3a52b547882e62`, **unchanged**, so owner T4 QA receipt remains tied to same QA code. The source-only GitHub Actions run `43431126776` passed after checking the strict guard pins. This CI is **not** real T4 training.

## 4. Single integrated GO/HOLD adjudication

| Gate | Adjudication |
|---|---|
| prereg, NEW FINAL freeze, matched real TRAIN sampler metadata | PASS |
| new H-DATA internal owner authorization, scoped upstream license review | PASS_SCOPED |
| AES escrow created, balanced 12/12 and 3/3 strata; owner Drive exact-byte SHA | PASS |
| native T4 real P02 H0/H1 interrupted-resume parity | PASS_SCOPED |
| independent 35/35 readback | PASS_SCOPED |
| production runner source SHA/CI and no-retry/one-root strict guards | PASS_SCOPED |
| completed 128-step H0/H1 science training | NOT_EXECUTED |
| new FINAL24 inference, scoring or unblind | NOT_EXECUTED |

**Owner decision:** `GO_SCOPED_ONE_SHOT_OWNER_MANUAL_DISPATCH_NO_AUTO_TRAIN`. This **only releases the frozen source for owner-initiated future one-shot science training**, not the scientific result and not an automated run. The code's exact owner GO lock is stored at `artifacts/qa/ttm-small4m-h-data-s1/preexec_real_train/TTM_HDATA_S1_OWNER_SCIENCE_ONE_SHOT_GO_LOCK_20261113.json`. Execute only against the exact locked Tesla T4 runtime/source. If the first run fails, retain failure evidence; never silently restart from a different run root, reuse consumed FINAL, or tune from outcomes. Resume only from a valid READY-last checkpoint and no unreconciled in-flight step.

## 5. Scope and next operation

**At this adjudication:** `SCIENCE_TRAINING=0`, `SCIENCE_INFERENCE=0`, `OWNER_AUTO_DISPATCH=FALSE`, `TEST_Q1_Q2_OOD=SEALED`, `FINAL_HF01_HF24=SEALED`, `MAIN=UNCHANGED`.

**Next:** `TTM_HDATA_S1_OWNER_T4_TWO_ARM_ONE_SHOT_128X4096_SCIENCE_DISPATCH_AND_READY_LAST_RECEIPT_NO_FINAL_INFERENCE`. A separate **explicit owner manual dispatch** is required. The future trained checkpoints and VAL NLL must undergo independent QA/adjudication before NEW FINAL inference. No final quality claim before blind rater score freeze/unblind.
