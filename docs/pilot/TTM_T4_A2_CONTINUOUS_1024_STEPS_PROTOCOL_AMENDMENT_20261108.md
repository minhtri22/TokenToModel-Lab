# TTM-Small-4M — T4 protocol amendment A2: run 1,024 steps continuously

**Date:** 2026-11-08. **Requested directly by the experiment owner:** run the *whole planned* 1,024 optimizer steps in one Colab Free session if possible; do **not** voluntarily stop at step 256. This supersedes only the unapproved 55-minute/session and 90-minute/total hard time caps in historical T4 design snapshots. All older STOP/PASS receipts are preserved.

## Unchanged scientific question (single pilot)

- Original source/split/BPE/pilot locked: TinyStories 2,048 TRAIN / 256 VAL / 64 sealed TEST, 768 TRAIN-only stories for 2,048-ID BPE. No extra data, no test access.
- Frozen P02 transformer 3,749,376 parameters, git blob `9762343e06cf800b50574c2871ae1ed58537fb18`.
- One seed `20261108`, **1,024 optimizer steps × exactly 4,096 scored target token positions per step** = 4,194,304 exposures. AdamW 3e-4, linear warmup32 then cosine3e-5, gradient clip1.0. FP16, microbatch8 windows, *dynamic* number of accumulations to exactly 4,096 valid targets (the old synthetic fixed accumulation2 is not binding).
- VAL at steps128/256/.../1,024; final checkpoint **step1,024 only** is the primary H1 decision; Add-0.1 TRAIN-only bigram, at least 5% relative VAL NLL gain plus story-bootstrap95% absolute-gain lower bound >0, 1,000 resamples seed20261109. TEST remains sealed until final result adjudication, no parameter tuning from intermediate VAL.
- Full checkpoint/READY-last at steps **256/512/768/1,024**, *no planned stop at these checkpoints*. Running longer than a previous 55/90-minute estimate is not a science failure. Free Tier only ($0) remains; Colab provider may disconnect at its own discretion.

## Interruption/recovery (one logical training run)

If the free Colab session ends unexpectedly, resume **the same RunID from the most recent SHA-verified READY checkpoint**, restoring model, optimizer, scheduler, sampler, Python/NumPy/PyTorch CPU/CUDA RNG and GradScaler. Do not create a new scientific seed/run or overwrite an existing checkpoint. Work since the last checkpoint may need to be recomputed deterministically. If a partial checkpoint exists without READY, stop and inspect; never silently treat it as valid. If step1,024 completed, do not rerun.

## Exact data and proof

- Private Google Drive folder `https://drive.google.com/drive/folders/1fXyRvNyVWSgIV-XB-vyT5DZal8JEM0-E` verified by authenticated connector readback 2026-11-08:
  - `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz`: **1,186,107 bytes**, SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`
  - `T4_PRIVATE_PACK_MANIFEST.json`: **1,382 bytes**, SHA256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`.
- Capacity technical report `c55a568496a888bc3abc95c0231a5ed17d3a6f366361571b6f89a4457d09f1ee`, Tesla T4. It supports feasibility, **not** a guarantee about wall-time or a threshold for H1.
- Prior source archive `97b7a88196487caf348e50c158272fd09f174f62`, 19/19 blobs PASS. Frozen synthetic T4 GPU/Drive checkpoint-resume PASS. These were not TinyStories scientific training.
- A2 source changes are limited to (i) science runner retaining all 1,024 steps without local arbitrary timer stop, (ii) GPU capacity reviewer retaining VRAM selection and timing observations but not rejecting an otherwise feasible Free Tier run at 90 minutes, (iii) streaming progress/checkpoint logs. A2 runner SHA256 `c6298f3381efd4b54e4b3e7aeb8143354f36bb1ed9fd87d08900cee18f7f90e6` and Git blob `76c4d0155cd0736919f41682f240b47ad3d7c428`; A2 capacity reviewer SHA256 `8db7ce9111744523a6c2e558a50677e19c56788298a0619eb4cfa924ea6a03c2`, blob `e407ff07007778367a485f6bae4b17457ddd83d9`. Original T4 frozen files remain intact.

**Authorization boundary:** The owner explicitly selected 1,024-step direct training. The Colab notebook must independently verify the exact data/source bytes and run-folder uniqueness before creating an exact one-shot lock and launching TRAIN; executing the notebook is the user's intentional start action. Until then, `T4_SCIENCE=NOT_STARTED`. Do not append technical changes to `lineage.md`; append scientific PASS or FAIL only after results are adjudicated.

**Bước thực hiện tiếp theo:** open the A2 one-session notebook on Colab Free T4 and run all. It will start once, go to 1,024 without a planned stop, preserve 256/512/768/1,024 READY checkpoints, and output `T4_FINAL_UNADJUDICATED.json` for scientific adjudication. If Colab disconnects, use the same notebook/RunID and verified latest checkpoint.
