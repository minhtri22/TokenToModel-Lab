# TTM-Small4M — T4 synthetic GPU trainer independent closure & single science gate review

**2026-11-08**. PR #12 **DRAFT**, base main `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`. **Not a TinyStories scientific run, result or authorization.** P00–P12, historical P07, and append-only scientific `lineage.md` are unchanged. No experimental TEST data opened.

## I. Frozen GPU T4 integration — independent Drive QA

The owner ran the frozen `TTM_T4_Synthetic_Trainer_GPU_Drive_Integration_20261108_v1.ipynb` in Colab; console `PASS_SYNTHETIC_T4_TRAINER_GPU_DRIVE_RESUME` and `DRIVE_FLUSH=COMPLETED`.

Connector-based independent readback **after unmount** retrieved all report/markers and the **entire 45,074,891-byte** Drive checkpoint. A separate SHA256 over the actual downloaded binary matched the original checkpoint `READY.json` and report. No checkpoint or private token data uploaded to GitHub.

| Evidence | Exact SHA256 | Scope |
|---|---|---|
| `T4_SYNTHETIC_TRAINER_INTEGRATION_REPORT.json` | `15e1e063beceda878db051eb6bbd49d9373ad4e1bf736883df2a585818676dc3` | Colab GPU experiment report |
| `COLAB_ENVIRONMENT.json` | `c0a1d927550cb62995e8d267c3f57230c5e98e0877473b464e64ff7d5f57704e` | Tesla T4, torch 2.14.1+cu130, CUDA 13.0 |
| `INTEGRATION_READY.json` | `cca9d1f459d849c25d751c25cd1ce7697028ad20433bd1f9880b2359b9f14b21` | Final READY-last marker, cross-linked report and environment |
| `CHECKPOINT_STEP1_READY.json` | `99035af596baf892eaa2e793aef6013b539ef26c95911fab4eed97c0368d5a5e` | Checkpoint SHA and step; science lock all zeros, synthetic pack all ones |
| `CHECKPOINT_STEP1_PROGRESS.json` | `ff9f2d21eb75c97cb07d4f4d4cb087e7e6b081df454ef90e7ff0ebcb5844e5a6` | 4,096 scored targets at step 1 |
| `checkpoint.pt` (Drive only) | `7c9f790a8ee2b44057f1111167f8fcf0da041a42680531e505844799c68cb961` | 45,074,891 bytes, independently streamed/read back |

Original Drive folder: https://drive.google.com/drive/folders/1ECT85kFY8IaKP9_IO1blHQBxIq-ADcaI ; checkpoint subfolder: https://drive.google.com/drive/folders/1Mdqt_cXhPQdVOskbHtrYJD1NxjdX3wAq

All five small evidence files were uploaded to `evidence/pilot/t4-trainer-gpu/` and exact Git blob readback PASS. This is a technical evidence archive, not an entry into `lineage.md`.

**GPU integrated result:**
- Exact P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, **3,749,376 parameters**, Tesla T4.
- Two optimizer steps at **4,096 non-PAD scored labels/step**, **FP16 + microbatch 8** with *dynamic* window accumulation: 22 windows in step 1, 23 in step 2; synthetic mean valid target/window 185.93.
- Step 2 continuous vs step 2 restored from the original step-1 checkpoint: **loss/weights/optimizer/scheduler max absolute differences = 0**, sampler and CUDA RNG equal. VAL synthetic 12 stories / 2,301 scored targets, evaluator ran.
- GPU step1 wall-time 1.095s (first-time overhead), step2 continuous 0.098s, restored 0.080s; CUDA reserved peak 408,944,640 bytes. **Two steps are not an end-to-end 1024-step runtime guarantee.**
- `candidate_only=true`; `science_executed=false`, `private_pack_accessed=false`, `tiny_stories_used=false`, `test_used=false`, `h1_scientific_result=NOT_APPLICABLE_SYNTHETIC_ONLY`.

**Verdict:** `T4_SYNTHETIC_GPU_TRAINER_DRIVE_RESUME=PASS_INDEPENDENT_TECHNICAL`. The earlier T3 original CUDA-RNG fault is retained STOP separately from its valid T3B recovery.

## II. Complete technical evidence matrix

| Gate | Verified disposition |
|---|---|
| T1 exact TinyStories source and independent pilot split | PASS, scoped 2,048 TRAIN / 256 VAL / 64 sealed TEST, 768 TRAIN BPE |
| T2 real TRAIN-tokenizer + GGUF F32 llama.cpp | PASS 20/20 tokenizer, 10/10 logits |
| T3 Colab checkpoint/resume + Drive | PASS independent, original failed attempt preserved |
| T4 private TRAIN/VAL NPZ integrity (no TEST) | PASS independent, 498,287 scored TRAIN positions, NPZ SHA `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913` |
| T4 full-length synthetic GPU capacity | PASS PROVISIONAL (not 90-minute training proof) |
| T4 dynamic-window CPU trainer + synthetic GPU/Drive integration | **PASS INDEPENDENT** |
| F16 GGUF llama.cpp deployment | BLOCKED OPTIONAL; T2 F32 is mandatory |
| T4 actual TinyStories training / H1 verdict / TEST | **NOT EXECUTED** |

## III. Exactly ONE final scientific adjudication, not a chain of micro-permits

Only material, not already PASS, conditions for issuing a T4 one-shot science lock:

1. **Reproducible executable source archive.** Archive both byte-pinned bundles to PR #12 and verify their 19 source/notebook/test files independently: `TTM_SMALL4M_T4_INTEGRATED_PREREG_CAPACITY_AND_TRAINER_20261108.zip` SHA256 `cda8e692ce614c804bdffa1850abe6faeb0c51bccc0a8a0c1fbdee0145a0f524` (15 entries), and `TTM_T4_SYNTHETIC_TRAINER_GPU_INTEGRATION_V1_20261108.zip` SHA256 `a3f122bfbe0e5c59bfe7a74fb140c782dcb0a19b2036cb20ac906e6109657a94` (4 entries). Neither is currently fully committed as T4 executable source. Preserve main, P07 and historical evidence.
2. **One integrated prereg decision.** Explicitly accept the bounded data / rights / leakage limitation, `2048/256/64` story partition, BPE trained on `768 TRAIN`, TEST sealed, **seed 20261108**, `1024 × 4096` scored target budget, AdamW/scheduler, **H1** final-step1024 VAL next-token NLL improvement **≥5%** vs TRAIN-only Add-α=0.1 bigram, story bootstrap 1000 seed20261109 with 95% lower gap CI >0, single final TEST after frozen VAL result. Source hashes and 2.048 story identities must remain fixed; no result-dependent edits.
3. **Final locked GPU setup & Drive transfer**: provisional `FP16 / microbatch 8 / dynamic exact-target accumulation` with loss scaler; actual private NPZ stays non-public and requires verified authenticated transfer to Colab Google Drive under user control (no TEST), original SHA checked there; frozen CUDA/PyTorch env and immutable READY-last checkpoints; 5,400 GPU-second cap with STOP rather than auto-extension. Model training might not meet H1; all outcomes recorded as scientific PASS/FAIL once authorized, not silently retried.
4. **Single independent source/methodology adjudication and explicit science authorization**. Reject if source hash/branch diverges, 4,096 scored labels/step cannot be maintained, effective TRAIN reuse factor 8.417x unacceptable for the stated generalization question, baseline/test access incompatible, or capacity/privacy contract changes. No single technical PASS automatically grants authority. The science notebook remains fail-closed with `EXPECTED_LOCK_SHA256=NOT_ISSUED`; no `T4_SCIENCE_LOCK.json` issued yet.

**Important interpretation:** The synthetic benchmark extrapolated only 56.62 seconds for 1024 optimizer steps under one heuristic; this is **not** scientific time-to-completion evidence. GPU trainer 2-step integration time, longer VAL and checkpoint/Drive overhead must be monitored under the 90-minute cap. Report training-vs-VAL generalization gap and actual target-position exposure reuse of ~8.42x; 4,194,304 target exposures do NOT mean 4.19M independent examples.

**Current state:** `T1–T3=PASS_SCOPED` · `T4_PRIVATE_PACK_INDEPENDENT=PASS` · `T4_GPU_CAPACITY=PASS_PROVISIONAL` · `T4_GPU_TRAINER_INTEGRATION=PASS_INDEPENDENT` · `T4_SCIENCE_LOCK=HOLD` · `T4_TRAIN=NOT_STARTED` · `PR_12=DRAFT`.

**Next action:** `TTM_T4_EXACT_SOURCE_ARCHIVE_AND_SINGLE_INTEGRATED_SCIENCE_LOCK_ADJUDICATION` — complete source archive on the current PR HEAD, one independent review of frozen scientific and privacy contract, decide GRANT or HOLD exactly once. No T1–T3 reruns or new micro-permits.
