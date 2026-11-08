# TTM T1 — independent QA closure; T3 Colab/Google Drive handoff (2026-11-08)

## Evidence (frozen, no further T1 execution)

- User attachment `TTM_T1_INDEPENDENT_QA.json` independently hashed: SHA256 `0fd1c3e9b97478e35e292b4c5a68c49757cc736136d9aafcbe00129dbc8dfea5`, 1882 bytes. Identical JSON read from local Windows project. Stored byte-identical as `evidence/pilot/t1-real/TTM_T1_INDEPENDENT_QA.json`, Git blob `3b5613fdabc00f44b7524ac9dad486b1be5c3b00`.
- Auditor status `PASS_INDEPENDENT_T1_REAL_SOURCE_SPLIT_BPE_NATIVE_QA`; dataset exact revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`; TRAIN raw SHA `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`, VALID raw SHA `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`.
- Independent source stats: 2,119,489 TRAIN stories scanned; 320,241 TRAIN exact duplicate instances; 21,990 VALID scanned; 6,601 exact collisions with original full TRAIN removed. Active pilot: 2048 TRAIN / 256 VAL / 64 TEST; pairwise near-duplicate clearance at 5-word Jaccard threshold 0.85, scope **only active pilot subsets** (not all unused TRAIN). `train_near_rejected_by_independent_audit=0`.
- Split manifest SHA256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; TRAIN BPE file SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` and internal manifest SHA256 `6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6`, 768 TRAIN-only fit stories, vocab 2048 IDs, 1791 merges.
- Native pinned llama.cpp F32 tokenizer 20/20 exact, logits 10/10 top1 exact with max abs error `0.0008438229900207261` (threshold <=0.001), GGUF SHA256 `68c0684d75fe12965427c93f34052172d59b480a74f52804648a4751ed5c8747`. Native receipt SHA256 `04ade9824c4f63f0f3a169bb918cd78bd4c4133965168e4aec5bd85f83868ea3`.

## Adjudication and limits

**T1_REAL_SOURCE_SPLIT_TRAIN_ONLY_BPE_F32=PASS_INDEPENDENT_TECHNICAL_SCOPED**. This closes data provenance, split integrity within agreed bounded pilot, and tokenizer/GGUF parity. It does **not** claim no near-duplicates against all unused source stories or a trained model. The pilot-specific sample size policy remains a prereg amendment to be accepted in the combined science gate; scientific evidence is not created by engineering QA. Append-only `lineage.md` unchanged.

## T3 next (not executed on Colab)

- Frozen notebook in this repo: `tools/pilot_t1t3/TTM_T3_Colab_Drive_Resume_Synthetic_20261108.ipynb` Git blob `92f76f1f3232c899771184e627e7d85a5495bf1e`.
- User-authorized Google Colab runtime requires CUDA. No scientific T4 train or TinyStories access. Notebook embeds SHA-pinned P02 and trainer. Compares 20 continuous synthetic steps to 10 steps + checkpoint save to Drive + readback/restore + 10 steps, preserving model, optimizer, scheduler, Python/PyTorch/CUDA RNG, sampler and cursor. It writes `READY.json`, `checkpoint_step10.pt`, `T3_RESUME_REPORT.json`, `COLAB_PIP_FREEZE.txt`, `COLAB_ENVIRONMENT.json` under `MyDrive/TTM/ttm-small-pilot/t3_resume_synthetic_20261108_v1/` once, then flush/unmount.
- **Independent acceptance not just Colab stdout:** after Colab unmount, use connected Google Drive metadata and content to independently verify actual file presence, READY SHA matches `.pt` bytes (if connector exposes raw bytes), report `pass=true`, CUDA device, 20 vs 10+10 loss/model/optimizer/scheduler/sampler parity, environment SHA. If checkpoint raw byte inspection is unavailable, classify as partial/HOLD rather than claim full durable readback.
- Google Drive search for `ttm-small-pilot` returned no matches as of this review. **T3_COLAB_DRIVE=NOT_EXECUTED**. Colab authentication and GPU execution require user's Colab session; cannot claim backend ran without its receipt.

**Gate:** `T1_INDEPENDENT=PASS_SCOPED`, `T2_F32=PASS`, `T3_LOCAL_CPU_RESUME=PASS`, `T3_COLAB_DRIVE=NOT_EXECUTED`, `T4_SCIENCE_LOCK=HOLD`, `T4_GPU_TRAIN=NOT_STARTED`. PR #12 remains draft; no merge, no P07 changes.

**Next:** one synthetic T3 Colab/Drive execution on the frozen notebook, then independent Drive readback and combined acceptance. No rerun T1. Avoid creating micro permits for routine setup steps.