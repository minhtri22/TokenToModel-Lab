# TTM-Small-4M — T1/T2/T3 technical closure and one integrated T4 science-lock review

**Date:** 2026-11-08. **Repository:** minhtri22/TokenToModel-Lab. **PR #12:** DRAFT. **Base main:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`. **Scientific execution:** NONE. Do not merge automatically, alter P07/P00–P12, or append engineering QA to `lineage.md`.

## 1. Authoritative technical adjudication after independent readback

| Gate | Verdict | Evidence and limits |
|---|---|---|
| T1 original source | **PASS** | TinyStories `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. SHA256 original TRAIN `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`; VALID `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`. No raw story data published. |
| T1 split and leakage | **PASS, bounded active pilot** | Independent QA `PASS_INDEPENDENT_T1_REAL_SOURCE_SPLIT_BPE_NATIVE_QA`; TRAIN 2048 / VAL 256 / TEST 64, exact and near-duplicate active-subset checks; no assertion of full-corpus near-duplicate coverage vs unused source stories. Independent QA SHA256 `0fd1c3e9b97478e35e292b4c5a68c49757cc736136d9aafcbe00129dbc8dfea5`. |
| T1 real BPE | **PASS** | 768 selected TRAIN stories, 2048 IDs, 1791 merges, TRAIN-only. Split manifest SHA256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; BPE manifest SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. |
| T2 actual tokenizer/native GGUF F32 | **PASS_SCOPED** | P02 source Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, llama.cpp `372dc5ca157276beb6c67b2e92477e8d662e964a`. Token IDs 20/20, full F32 logits 10/10, max abs `0.0008438229900207261` <= 0.001, 0 top1 mismatches; real TRAIN-only BPE used. This is **untrained checkpoint export feasibility**, not science or trained-checkpoint T5. |
| F16 native | **BLOCKED_OPTIONAL** | Prior V4/V5B mixed CPU graph type failures remain preserved. Required technical export proof uses F32; F16/Q8/Q4 optimization is optional proposal, not retroactive PASS. |
| T3 local CPU synthetic resume | **PASS** | 20 contiguous vs 10+checkpoint+10; exact loss/weights/optimizer equivalence on synthetic data. |
| T3 **Colab Tesla T4 + Google Drive synthetic resume** | **PASS_INDEPENDENT** | Frozen original step10 checkpoint in Drive, original failed notebook preserved, isolated `t3_resume_synthetic_20261108_v1_recovery_01` successor recovered and completed. 20 vs 10+10, loss/weight/optimizer max abs = 0; scheduler/sampler/RNG Python/CPU/CUDA exact. Report and env files downloaded independently from Drive and Git SHA blob readback exact. |
| T4 science | **NOT_EXECUTED; LOCK=HOLD** | The above technical QA does not grant model-training authority or decide H1/H2/H3. |

## 2. T3 original failure and valid recovery lineage

Original Colab GPU: **Tesla T4**, torch `2.14.1+cu130`, CUDA `13.0`. Original `t3_resume_synthetic_20261108_v1` raised `TypeError: RNG state must be a torch.ByteTensor` because `torch.load(..., map_location=cuda)` mapped CPU RNG state to CUDA. Preserve this STOP; never relabel it PASS.

Original `checkpoint_step10.pt` in Google Drive is **45,069,785 bytes**, SHA256 `3546105cb736084956c8d4bea6950fe931b658845ed29a5791c6669b40f67382`; verified once on Colab and independently by a complete 45MB Drive download. Original `READY.json`, SHA256 `c77231124003199573227425b3cdeea94f0544eec8cf0906c4443af6b6591765`, persisted independently. No checkpoint was modified or overwritten.

T3B separate successor loaded the same original file with `map_location='cpu'`, then resumed 10 steps on CUDA and compared with a 20-step same-device synthetic baseline. `T3_ORIGINAL_CHECKPOINT_SALVAGE_REPORT.json`: `pass=true`, `PASS_RECOVERED_ORIGINAL_STEP10_CHECKPOINT`, `steps_contiguous=20`, `steps_resumed_from_original_checkpoint=10`, 0 loss/weight/optimizer and 0 step10 checkpoint-state error, scheduler/sampler/RNG all exact, `science_executed=false`.

**Independent Drive ↔ GitHub evidence:**

| Artifact (GitHub path prefix `evidence/pilot/t3-colab/`) | SHA256 of original Drive bytes | Git blob SHA1 exact |
|---|---|---|
| `ORIGINAL_READY_STEP10.json` | `c77231124003199573227425b3cdeea94f0544eec8cf0906c4443af6b6591765` | `e159510a7e6daeeab9b775ab8e8bff3aa31692dc` |
| `T3_ORIGINAL_CHECKPOINT_SALVAGE_REPORT.json` | `27431e5f2df96bb566a972191c5bed5e25e5f4e04e590e19d2957c479abb3e4a` | `303968fda01dcab3319ee2d9d688615c71ec855a` |
| `COLAB_ENVIRONMENT.json` | `b25e0ff054c02bf93db72d75aff087f8d378df98ef2d6974f3bc6c44350de139` | `6d13d280bdfdad19f9f552b51f7caf7291be861d` |
| `COLAB_PIP_FREEZE.txt` | `a6eebfff272109bc4732b72d4bb1a0892d73e3db37c8f35d3afd7f32dcff0b80` | `056c738d87865d6632e80c03262b28fc1e5b8456` |

Original Drive folder: `https://drive.google.com/drive/folders/1CkAH90idd-6BM6_3fvS0U0QqdOENrWLi`; successor Drive folder `https://drive.google.com/drive/folders/1CuO93H0_gzJPW71fh_DYAQZfoCcV6Not`. **Checkpoint binary remains on private Google Drive, not public GitHub**. Colab `drive.flush_and_unmount()` succeeded; Drive connector readback of three successor files exact.

## 3. Single remaining *integrated* science admission decision for T4

The separate T1/T2/T3 *technical* gates are now **CLOSED**. Do **not** add permit/certificate cycles for their routine subchecks or rerun consumed QA. Only the following **scientific/material** fields remain to freeze and formally accept, in one integrated preregistration and capacity review:

1. **Source rights/scope and dataset policy:** approve actual original source license obligations and limited public release; explicitly accept bounded pilot TRAIN/VAL/TEST **2048/256/64** with TRAIN-only BPE **768** and active-subset near-dup limitation. Fix exact manifest and TEST-seal behavior, source SHA, tokenizer SHA, one-shot seed. Raw stories stay private.
2. **Scientific hypotheses/evaluation:** keep H1 VALID NLL at least **5% below** frozen add-alpha smoothed bigram with story-level bootstrap **95% CI** for NLL gap excluding 0; H2 resume parity; H3 trained-checkpoint Windows GGUF/Ollama. Freeze uniform/unigram/bigram code, alpha, bootstrap 1000 rounds/seed, VAL-only selection and single held-out TEST use; independent QA before science.
3. **Finite training run:** proposed **1024 optimizer steps × 4096 target tokens/step**, seed **20261108**, AdamW peak LR **3e-4**, warmup **32**, cosine to **3e-5**, VAL every **128** steps, cap **90 GPU minutes**. Before science, choose **effective batch, microbatch, gradient accumulation, FP32/AMP dtype and GPU memory budget** based on ONE bounded **synthetic capacity** smoke on the currently available class; pin Colab runtime/environment and expected runtime. A 20-step batch(2×32) resume proof alone cannot substantiate 4096 target tokens/step within 90 minutes. If impossible, HOLD and amend prereg before entering science, not silently reduce budget.
4. **Execution implementation:** version/pin actual T4 loader (TRAIN only, no TEST reads), source+tokenizer manifests, optimizer/scheduler, every-batch loss/eval/curve, baseline evaluator, full READY-last Drive checkpoint and resume cursor/RNG recovery; validate one integrated zero-science preflight and storage/space. T4 training runner and checkpoints are **NOT yet developed/executed to an accepted scientific lock**; don't assume notebook T3 is a T4 trainer.
5. **Governance:** independent prereg review and explicit one-shot science authorization only after all above PASS. Preserve append-only `lineage.md` for true scientific PASS/FAIL; no technical infrastructure logs in scientific lineage. P00–P12 unchanged, P07 preserved; PR #12 remains **DRAFT** until source+contract reviewed.

## 4. Final states and next step

`T1_INDEPENDENT=PASS_SCOPED` · `T2_F32=PASS_SCOPED` · `T3_COLAB_DRIVE_SYNTHETIC_RESUME=PASS_INDEPENDENT` · `T3_ORIGINAL_FAILED_RUN=STOP_PRESERVED` · `F16=BLOCKED_OPTIONAL` · `T4_CAPACITY=NOT_VALIDATED_FOR_4096_TOKENS_STEP` · `T4_TRAINER=NOT_LOCKED` · `SCIENCE_LOCK=HOLD` · `T4_TRAIN=NOT_STARTED`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_T4_SINGLE_INTEGRATED_PREREG_FINALIZATION_AND_SYNTHETIC_CAPACITY_PREFLIGHT`. Resolve the listed five material sections in ONE coordinated pass, freeze all hashes/evaluation/runtime budget, obtain independent science lock; only then consider T4 one-shot Colab training.
