# TTM H-DATA-S1 — Owner approval, source SHA, AES escrow, T4 runtime: formal one-packet decision

**Operation:** `TTM_HDATA_S1_OWNER_RIGHTS_NATIVE_T4_TRAINER_RESUME_AES_ESCROW_SINGLE_PACKET_FINAL_RELEASE_NO_AUTO_TRAIN`  
**Date:** 2026-11-13 · **Research branch:** `research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113`  
**Source-only QA commit:** `fbb57179318c6d0f42215647bc1087c6de093c5e`  
**Decision:** `HOLD_NO_AUTO_TRAIN_PENDING_T4_REAL_FP16_RESUME_PARITY_AND_INDEPENDENT_FINAL_RELEASE`.

## 1. Owner consent and scope

The owner explicitly approved H-DATA-S1 research continuation, a SHA-locked H0/H1 runner, real T4 interrupted-resume QA, and a NEW FINAL24 AES escrow before any forward. This is consent to conduct pre-execution and the narrowly scoped internal study, **not a request to auto-dispatch science training**. Original A/C rights are not recycled, source training data/TEST/Q1/Q2/OOD remain unopened in this turn, and prior FINAL24/NEXT24 remain consumed. No `main` merge.

The new owner internal source-rights receipt declares `PASS_NEW_HDATA_SCOPE_AND_LICENSE` only for private computational research on the exact unchanged TinyStories-derived TRAIN/VAL pack. Hugging Face lists `roneneldan/TinyStories` under CDLA-Sharing-1.0; the upstream agreement permits Use/Computational Use, while publication of source/enhanced Data carries obligations. No unrestricted raw data release is claimed; this is not a third-party legal certification.

**Rights receipt:** `artifacts/qa/ttm-small4m-h-data-s1/preexec_real_train/TTM_HDATA_S1_NEW_OWNER_RIGHTS_INTERNAL_CDLA_SCOPED_20261113.json` SHA256 `f1ae54c94d8c6a4a55febd4544b7c474ae73f060e8e9f64b426b5ca91740de2f`. Source:
- https://huggingface.co/datasets/roneneldan/TinyStories/blob/main/README.md
- https://cdla.dev/sharing-1-0/

## 2. AES custody before forward — PASS

- Owner-private AES-256-GCM map for `HF01–HF24` generated once; LEFT H0/H1 12/12, each of four strata 3/3. Verified local decrypt, plaintext digest and balance.
- Ciphertext JSON SHA256 `de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d`.
- Owner-private ZIP SHA256 `c5c5d6eae6ce38d892348878ae200d5bbcd42406b53f7b0c43e8876a145d48d4`, 4159 bytes.
- Original ZIP uploaded to preexisting unshared `ttm_small4m_h_data_s1_20261113/owner_private` in owner Google Drive. A separate authenticated Drive raw-byte readback of exactly 4159 bytes independently matched the original ZIP SHA256.
- **AES key/plaintext mapping were NOT committed to public GitHub.** No model forward was run.

## 3. Source pins and no-GPU CI — PASS_SCOPED

| Source | SHA-256 | Git blob SHA-1 |
|---|---|---|
| `ttm_hdata_s1_owner_blind_escrow_v1.py` | `e2d8eb50c437111324c43f3a184c3193a4d9fbd7de3a065bbe5aeb8c33adab46` | `c85b8c63a008abcad65ee546b06db44d19ae26be` |
| `ttm_hdata_s1_native_t4_h0_h1_resume_qa_v1.py` | `7db0f999934036fc4f87beda9cd5a131377147d7307e9de5ac3a52b547882e62` | `11659637df962ce2434c78d159baca9cbec97fc6` |
| `ttm_hdata_s1_two_arm_science_runner_candidate_v1.py` | `1874aebf904a57782acad963838db86f01556d2fe287927e616574b5700985a7` | `2ca2be5f95f42972701f29e005337c2ca5675cc1` |

GitHub Actions scoped source QA:
- `43422638525` PASS; `43423130180` PASS on current pinned source/receipt.
- Compiled Python AST, SHA256 and Git blobs; checked fail-closed GO checks, AES-before-forward check, no key material tracked, and science steps zero.
- This workflow **does not execute a real P02 T4 model or optimizer**, and is not a substitute for T4 parity.

The two-arm science runner is a **source-frozen candidate only**. Default mode does not train. The science mode refuses missing exact owner GO lock, real T4 QA PASS receipt, owner rights receipt, valid escrow and unchanged source/model/pack. No science GO lock or release exists yet.

## 4. Immutable research inputs

- TRAIN/VAL NPZ `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`.
- Parent P02 step 1024 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- BPE2048 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Original TRAIN H0/H1 128-step paired sampler plan `bcb354d29540e3a348b76173cdad1a6e2832dc81f995c717b68be6926d456591`, metadata QA already PASS; no need to rerun.
- NEW FINAL owner-private full prompt file `b129a5c52520a25f1c40de950471622320abfa6b5414d0b16e0111ed96adc680`; no FINAL plaintext read.

## 5. One formal GO/HOLD decision

| Gate | Result |
|---|---|
| Design/new eval freeze | PASS |
| Real TRAIN sampler + matched budget | PASS (prior frozen preexec) |
| Owner consent for internal H-DATA | PASS scoped |
| Declared upstream data license/scope | PASS scoped; not legal peer review |
| AES create, decrypt, 3/3 balance | PASS |
| Owner Drive ZIP exact-byte readback | PASS |
| GitHub source SHA/AST/secret guard | PASS scoped/no GPU |
| Colab T4 full model/optimizer/GradScaler interrupted-resume parity | **NOT_EXECUTED** |
| Production H0/H1 T4 science runtime end-to-end | **NOT_EXECUTED** |
| FINAL24 inference/score | **NOT_EXECUTED** |

**Owner single decision: `HOLD_NO_AUTO_TRAIN_PENDING_T4_REAL_FP16_RESUME_PARITY_AND_INDEPENDENT_FINAL_RELEASE`.** No trial training, no model-forward, no re-opening FINAL or NEXT24, no main mutation, no implicit GO. A later GO requires one integrated readback of the exact pinned Colab T4 actual H0/H1 two-step QA receipt, then a signed/locked one-shot science dispatch; no micro-permits.

Owner Colab runbook: `docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_OWNER_T4_RESUME_QA_RUNBOOK_20261113.md` (eight **non-science** QA optimizer updates only, if manually run on T4; science remains zero).

**Next operation:** `TTM_HDATA_S1_COLAB_T4_NATIVE_2ARM_FP16_INTERRUPTED_RESUME_INDEPENDENT_READBACK_SINGLE_GATE_NO_SCIENCE`.
