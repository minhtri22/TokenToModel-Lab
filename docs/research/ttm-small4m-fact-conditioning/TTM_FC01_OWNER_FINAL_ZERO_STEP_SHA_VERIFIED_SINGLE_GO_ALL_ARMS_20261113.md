# TTM-Small-4M FC01 — Final Zero-Step Readback and Single GO Adjudication

**Operation:** `TTM_SMALL4M_FC01_T4_FP32_DRIVE_RESUME_RIGHTS_SINGLE_INTEGRATED_SCIENCE_RELEASE_GO_HOLD_ZERO_TRAIN_STEPS`  
**Date:** 2026-11-13  
**Single scientific readiness decision: `GO_FOR_ALL_THREE_ARMS`**. 
**Arms:** `A_BASE_MLE`, `B_CF_MLE`, `C_CF_CONTRAST`. 
**No training started** by this adjudication; no GPU dispatch or FC01 owner release lock was created.

## Independent verification of bytes in user-connected Google Drive

- Original Colab receipt file: `FC01_T4_FP32_DRIVE_ZERO_STEP_READINESS_20261113T130706Z.json`, Google Drive file ID `1Sn7u4Ot54AKBHBaILFoHSQzAIPdDPwsl`, byte size 2457. Retrieved exact binary contents from Drive, computed SHA-256 **`f7d833493175a61e0e8cb13ec6805957b659e909d2d4fdd72d3d25796f4a23ac`**. It matches the owner-reported checksum.
- Colab snapshot file: `FC01_ZERO_STEP_DURABILITY_20261113T130706Z.pt`, Google Drive file ID `1f_eY2lz82RELQdHbQ3XP1rTQ19v2-Ehw`, byte size 15028313. Retrieved exact raw contents, independently computed SHA-256 **`2a31952b268ddbbafff4f32500e866d5341a3ea576a6219dbe830b5304cec1fd`**, matching receipt.
- Independently loaded the snapshot on CPU with `torch.load(...,weights_only=True)` (PyTorch 2.10.0+cpu); verified schema `ttm.fc01.zero_step.preflight.snapshot.NOT_SCIENCE_CHECKPOINT.v1`, `optimizer_updates_so_far=0`, 53 model state dict entries, optimizer state empty, both CPU/CUDA + Python/numpy RNG entries, and core/candidate/synthetic cursors all 0. Do not count state_dict entries or raw tensor elements as unique model parameters because tied weights may appear under multiple keys.

## Evidence from actual Colab zero-step session

- `status=PASS_COLAB_ZERO_STEP_SCOPED_ONLY_NOT_SCIENCE_GO`; `cuda_device_name=Tesla T4`; `torch_version=2.14.1+cu130`; `fp32=CUDA_T4_FP32_CONFIGURED_TF32_DISABLED`.
- Owner toggled `owner_rights_acknowledged=true` and `owner_free_t4_cost_cap_acknowledged=true`. **Self-attestation, not third-party legal review**. License publicly declared `CDLA-Sharing-1.0` for TinyStories.
- Colab notebook verified seven pinned inputs (six SHA256 plus P02 Git blob), loaded real P02 step1024 model in FP32, created optimizer and RNG/cursor snapshot at step0, saved and reloaded in Drive and reported exact model/optimizer/RNG/cursor roundtrip PASS.
- Both standalone Drive files retrieved with exact SHA. Colab itself recorded **zero optimizer steps**, **zero model inference**, **no data resealing breach**.

## Persistent untested runtime risk — never overstate

- `real_runner_step64_resume=NOT_EXECUTED_ZERO_STEPS_ONLY`. An optimizer with **empty state at step0** cannot prove restoring AdamW moment state after actual gradient updates. The zero-step snapshot is explicitly **not** a legal or scientific runner `--resume` checkpoint.
- Actual source-only runner test and separate negative checker passed before this gate (`PASS_16_OF_16`, exact T1 BPE). No full A/B/C gradient training is claimed.
- PyTorch deterministic CUDA operations may require `CUBLAS_WORKSPACE_CONFIG` set before initializing the CUDA runtime. Neither this adjudication nor the zero-step notebook tests model forward/backward. Do not disable determinism to make a science run succeed. Abort and preserve failure receipt if an exact frozen environment fails.
- Owner acknowledged a $0-paid Free T4 cap, but Colab did not expose independently verifiable billing; actual cost observation is outside the evidence. Runner's budget cap is 3600 GPU seconds per arm and 10800 GPU seconds total, not a guarantee of T4 availability or completion.

## Formal verdict and next implementation action

One integrated pre-execution gate requested **zero optimizer steps**. Every preexec observation that can be verified without gradient execution has passed. Because a real post-step resume cannot logically be proved with zero steps, it is recorded as a **bounded execution-stage risk**, not misrepresented as `PASS`. 

**`GO_FOR_ALL_THREE_ARMS` = technical/scientific readiness GO, not a command to launch training now.** The existing runner still requires an exact owner-authored `FC01_OWNER_GO.json` + SHA; this review did not create, sign or forge that artifact. No micro-permit is opened. The single owner execution workflow, if chosen, must use exactly the frozen A/B/C contract, immutable data/parent/T1 SHA, Free T4 / $0 paid cap and unchanged source; any discrepancy is terminal HOLD with no automatic rerun/reseed.

**Preserved:** `FC01_NEW_TRAIN_STEPS=0` · `D1_CONFIRMATORY=HOLD` · `TEST_Q1Q2=SEALED` · `DEV32=CLOSED` · `MAIN=UNCHANGED` · `LINEAGE=UNCHANGED` · `FC02_CAPACITY=NOT_OPENED`.

**Canonical machine-readable evidence:** `artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_T4_ZERO_STEP_RECEIPT_INDEPENDENT_CUSTODY_SINGLE_GO_ALL_ARMS_20261113.json`.
