# TTM — T4 integrated pilot scientific prereg + synthetic GPU capacity preflight (2026-11-08)

**Status:** `PR #12 DRAFT`; T1–T3 engineering gates PASS, **T4 science HOLD**. Main pinned `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`. The prior T3 GPU error remains a retained STOP with T3B recovery separately PASS. P00–P12/P07/`lineage.md` unchanged. This document supersedes stale T4 state snapshots but not original evidence.

## Locked candidate decisions (technical/scientific proposal, NOT a permit)

- **Data**: TinyStories `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, original TRAIN SHA256 `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`, VALID `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`; split manifest `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`, real BPE manifest `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. User-selected bounded pilot **TRAIN 2,048 / VAL 256 / TEST 64**, tokenizer fitted on **768 TRAIN only**. TEST is sealed. Exact/near-duplicate QA is **active-subset-only**; do not claim global near-duplicate clearance. License CDLA-Sharing-1.0 obligations stay applicable; no raw story text or reversible tokens in public GitHub.
- **Model**: exact P02 blob `9762343e06cf800b50574c2871ae1ed58537fb18`, unique params **3,749,376**, vocab2048, max context256, 4 layers × 256 embedding, 4 heads, LayerNorm, tied head. GPU science only after authorization.
- **Finite budget**: seed `20261108`; **1,024 optimizer steps × 4,096 actually scored next-token targets** (non-PAD) = 4,194,304 target exposures; no cross-story windows. AdamW betas0.9/0.95, eps1e-8, WD0.1, grad clip1.0, LR peak3e-4, 32 linear warmup, cosine to3e-5; VAL every128 steps, checkpoints READY-last at256/512/768/1024; **GPU science cap 5,400 seconds**. Train windows may be reused; report target reuse factor. FP32 vs AMP-FP16, microbatch and accumulation are **NOT yet locked**, selected only after Colab zero-science synthetic capacity and private pack shape review. If capacity fails, HOLD rather than reducing budget during science.
- **Primary H1**: final step1024 VAL mean NLL per scored target must improve >=**5%** over TRAIN-only smoothed bigram (Add-α **0.1**, same BPE/token pairs), plus the **story-bootstrap 95% lower CI** on absolute NLL gain must exceed zero; 1,000 resamples, seed `20261109`. Uniform/unigram additional baselines. TEST is not used for training, validation model choice, optimizer, tokenizer or capacity; one sealed TEST evaluation after final model decision.
- **H2**: science checkpoint must preserve model/optimizer/scheduler/global step/sampler/Python/NumPy/PyTorch CPU+CUDA RNG/FP16 scaler, plus source and SHA; READY-last immutable checkpoint in Google Drive. Technical T3B GPU resumed 10 from original step10 equals 20 continuous at loss/weight/optimizer error=0. A science-run resume is a distinct later receipt.
- **H3**: after science, trained checkpoint F32 GGUF Windows llama.cpp/Ollama parity at T5; untrained T2 F32 proof is not H3 on trained checkpoint. F16 remains prior BLOCKED, optional optimization.

## Actual new work, zero-science implementation

**Bundle created:** `TTM_SMALL4M_T4_INTEGRATED_PREREG_CAPACITY_AND_TRAINER_20261108.zip`; ZIP SHA256 **`cda8e692ce614c804bdffa1850abe6faeb0c51bccc0a8a0c1fbdee0145a0f524`**; 67,712 bytes, 15 members, member CRC & SHA verified. **Bundle code is an artifact pending GitHub archiving; it is not yet GitHub committed.** Frozen member SHA manifest inside ZIP.

Contents: `T4_PREREG_INTEGRATED_CANDIDATE_20261108.json`, exact P02, exact prior T1 + BPE source, `t4_data_pack.py`, `t4_capacity_smoke.py`, `t4_capacity_accept.py`, `t4_eval.py`, `t4_train_science.py`, Windows PS5.1 runner, Colab capacity and fail-closed science notebooks, tests & README.

**Actual local offline QA:** `pytest -q tests/test_t4_integrated.py` **13/13 PASS** with torch CPU. Includes exact 4,096 non-PAD target sampling, no cross story, TRAIN-only baselines, per-story bootstrap, no TEST keys/private pack SHA, budget/memory review, science authorization negative test, exact P02 parameter count, actual CPU checkpoint write/READY-last/weights_only load, notebook AST. **No scientific TinyStories training or Tesla T4 4096-target benchmark run.** PowerShell native not yet exercised.

**Synthetic GPU capacity notebook** `TTM_T4_Synthetic_Capacity_20261108_v1.ipynb` SHA256 **`f003ac3ea97b6f7b24bfe5a6e3d9b5b980c27276dc066f1e2a55a8116bbb3c34`**: embed source SHA pinned; CUDA T4 if allocated; compare candidates FP32 mb2, FP16 mb2/4/8 with 2 warmup +4 timed optimizer steps *each using 4,096 synthetic scored targets*, capture worst step latency and peak VRAM. Conservatively project `1024*worst/(1-0.25)`; require <=5,400 sec and VRAM <=80%. Write immutable `T4_CAPACITY_REPORT.json`, `COLAB_ENVIRONMENT.json`, pip freeze, `READY.json` last into Drive `MyDrive/TTM/ttm-small-pilot/t4_capacity_synthetic_20261108_v1`; flush/unmount. This is a provisional estimate only: actual TRAIN partial windows may increase compute.

**Private data preparation**, separate one-shot after capacity: verify source SHA and existing T1 manifests, stream only selected TRAIN/VAL, serialize bounded 256-target within-story windows (mask padding -100), **no TEST tokens**, compute actual average valid targets per window/reuse and SHA; NPZ is reversible text and remains **private**, not GitHub. Review capacity with measured true target/window inflation `max(1, 256 / average_valid_targets) * 1.10` beyond the 25% synthetic reserve. A science runner is prepared but fails closed without separately approved, pinned `T4_SCIENCE_LOCK.json` and accepted capacity review. It is NOT authorized or executed.

## Integrated one-shot scientific decision still pending

| Gate | Outcome |
|---|---|
| T1 dataset/split/BPE independent QA | **PASS_SCOPED** |
| T2 real-BPE GGUF F32 native | **PASS_TECHNICAL** |
| T3 Colab/Drive synthetic resume | **PASS_INDEPENDENT** |
| T4 prereg data/H1/budget candidate | **DOCUMENTED_PENDING_ACCEPTANCE** |
| T4 CPU synthetic code QA | **PASS_13/13** |
| T4 actual CUDA 4,096-target/step capacity | **NOT_EXECUTED** |
| T4 real private TRAIN/VAL token pack | **NOT_EXECUTED** |
| T4 GPU synthetic integrated trainer/Drive QA | **NOT_EXECUTED** |
| T4 scientific one-shot authority | **NOT_GRANTED / HOLD** |
| T4 science run/TEST | **NOT_STARTED** |

**Next step:** `TTM_T4_SYNTHETIC_4096_TARGET_GPU_CAPACITY_AND_DRIVE_READBACK` — run exactly one capacity notebook on authorized Colab, read and SHA-verify Drive receipt, then prepare private data pack and integrate resource report. Only after independent review of these material gates consider one science lock; no micro-permits or reruns of T1–T3.
