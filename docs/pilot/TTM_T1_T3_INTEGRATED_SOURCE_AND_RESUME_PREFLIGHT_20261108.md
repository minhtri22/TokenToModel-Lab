# TTM-Small4M T1/T3 integrated source and Colab/Drive preflight — 2026-11-08

**PR #12, DRAFT. Source-only / synthetic QA. No scientific T4 run or Colab access claimed.**

## Source and rights review

- Pinned HF source: `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, raw original `TinyStories-train.txt` and `TinyStories-valid.txt` only, not V2, not generated Parquet.
- Official pinned file metadata: `TinyStories-train.txt` SHA256 **`c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`** (~1.92 GB); `TinyStories-valid.txt` SHA256 **`94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`** (~19.4MB). These are **remote advertised digests**, not locally read bytes. File download/independent hash verification **NOT EXECUTED**.
- License dataset-card `CDLA-Sharing-1.0`, official https://cdla.dev/sharing-1-0/. Computational Use allowed subject to terms; publication of Data/Enhanced Data requires license and attribution compliance; do not upload original story text or raw data to public GitHub. No commercial-use guarantee independently issued; record remaining privacy/content rights review.
- Story separator: literal `<|endoftext|>` in UTF-8 raw bytes, streaming parser; preserved raw SHA and individual story identity via SHA256, model text strips only boundary whitespace, retains interior Unicode and CRLF. Parser tested on synthetic chunked fixture only; real raw first/last boundaries remain to be verified.

## Proposed pilot-bound T1 selection policy (explicit amendment pending integrated review)

- Full original TRAIN and VALID files are read and SHA-checked first. Remove TRAIN exact duplicates by story digest. Deterministically choose TRAIN 2048 actual stories by seed-hashed content priority, then near-deduplicate sampled TRAIN with Jaccard word-5gram >=0.85.
- From original VALID only, assign 80% VAL, 20% TEST by deterministic hash buckets, remove exact duplicates versus all raw TRAIN, then choose a **bounded actual evaluation subset VAL=256 / TEST=64** after exhaustive word-5gram Jaccard >=0.85 screening against the sampled model TRAIN and admitted other active eval stories. Full original VALID is not copied into public artifacts. TEST identifiers are listed in sealed manifest, never used to train BPE.
- BPE fit on first **768 of selected TRAIN stories** (ordered hash priority), not VAL/TEST. Exactly 256 byte base IDs + EOS 256 + 1791 merges. Efficient weighted-unique-segment implementation *proven same 1791 ordered merges* as frozen T2 reference on 720 synthetic TRAIN stories. Preserve regex, token, merge, provenance hash and runtime native parity.
- These specific pilot subset sizes are a proposed change to earlier broad split wording and must be accepted **before scientific T4**. Evaluation generalizes only to this bounded pilot subset; near-dup screening is exhaustive on active subsets, not a claim that all ~2M raw train stories and all valid stories are mutually near-dup-free.
- `T1_REAL_SOURCE_SPLITS=NOT_EXECUTED`, `T1_REAL_TRAIN_BPE=NOT_EXECUTED`, `T1_REAL_BPE_LLAMA_PARITY=NOT_EXECUTED`. Scripts are packaged for one-shot Windows source read, SHA verification, split, BPE fitting, and re-export F32/native parity, no science.

## T3 checkpoint / resume

- Exact P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, model 3,749,376 parameters, context capacity 256, 2048 IDs.
- **Local CPU synthetic actual execution PASS**: baseline 20 steps vs 10 + checkpoint readback + resume 10 with PyTorch `2.10.0+cpu`. Max loss/weight/optimizer state absolute error **0**; scheduler state exact; sampler and Python RNG restored; checkpoint stores model/optimizer/scheduler/sampler/torch CPU and CUDA RNG/cursor. Full checkpoint ~45,067,099 bytes, SHA256 `7aec610f77a3d50079706e5bbbda11a63b81801b45b2255a6ea322b6a531afda`. READY-last manifest, SHA readback PASS **on local simulated Drive filesystem**.
- **Colab/Drive actual runtime NOT EXECUTED**. Notebook prepared with embedded SHA-checked original P02 and trainer sources. On Colab mounts user-authorized MyDrive, requires an actual CUDA GPU, writes checkpoint into `MyDrive/TTM/ttm-small-pilot/t3_resume_synthetic_20261108_v1/`, includes environment pip freeze/torch/CUDA fingerprint and `drive.flush_and_unmount()`. Independent Google Drive readback still required after running; no claim of T3 Colab PASS until that happens.
- Colab allocation T4 in user's screenshot is only configuration intent; actual hardware availability/time limits vary and are not guaranteed (official Google Colab FAQ).

## T2 archived source handoff

- Previously independently verified T2 F32 native PASS 20/20 tokenizer, 10/10 logits; F16 optional BLOCKED. Source ZIP `TTM_SMALL4M_T2_F32_GPT2_TRAIN_ONLY_INTEGRATED_QA_20261108.zip` exact SHA256 `d6fd9d09a031c4c19e099f0d66d7d5fcccc0e8543ea602d7268ec6cb415dbcb9` was byte-reopened and all seven member SHA-256 verified. A single package contains these exact seven source files plus T1/T3 source and Colab notebook; scoped PowerShell worktree archiver will commit the code to this PR with source hashes checked and zero change to main. **Not committed yet**; do not claim archived before remote readback.

## Integrated decision table

| Gate | Actual state |
|---|---|
| T2 F32 synthetic GGUF native | PASS technical (prior locked) |
| T2 F16 backend | BLOCKED, optional optimization |
| T1 dataset identity, card and license review | PASS remote metadata, publication conditions recorded |
| T1 original raw TRAIN/VALID exact SHA on Windows | NOT_EXECUTED |
| T1 story-level split/near-dup/real TRAIN BPE/native QA | NOT_EXECUTED |
| T3 local synthetic CPU 20 vs 10+10 | **PASS** |
| T3 actual Colab CUDA + Google Drive READY/readback | **NOT_EXECUTED** |
| Source T2/T1/T3 code archival on PR | READY, pending exact GitHub commit readback |
| SCIENCE_LOCK/T4 | **HOLD / NOT_STARTED** |

**Bước thực hiện tiếp theo:** run single integrated Windows source/PR archive preflight and pinned T1 pipeline, then one user-authorized Colab notebook T3 synthetic test, read back Drive receipt and full source hashes. Only then decide on one combined prereg science unlock. Never auto-rerun consumed one-shot; do not append engineering QA to `lineage.md`.