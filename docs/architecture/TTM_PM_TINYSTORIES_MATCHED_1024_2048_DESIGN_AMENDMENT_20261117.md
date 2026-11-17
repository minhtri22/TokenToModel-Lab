# TTM PM — TinyStories matched Small-4M 1024/2048 experiment design amendment

**Operation:** `TTM_PM_TINYSTORIES_MATCHED_SMALL4M_1024_2048_COMPARISON_DESIGN_ADJUDICATION_ONEPACK`
**Ngày:** 2026-11-17
**Baseline main:** `59ee3f30b996405fddc087ab60102b59a021f8ea`
**Owner directive:** reject the 40-step, vocab258, context128 experimental design and require exactly matched Small-4M model/data/step conditions before any checkpoint-to-checkpoint claim.
**PM decision:** `GO_MATCHED_EXPERIMENT_DESIGN_ONLY · HOLD_Q4_MODEL_EXECUTION · PR44_OLD_40STEP_NOTEBOOK_NOT_ADMITTED`.

## 1. Baseline exact-source facts (historical T4)

- Original validated run `t4_science_4m_1024_a2_20261108_v1`: 3,749,376 parameters; decoder-only P02, 4 layers, d_model256, 4 heads, context256, LayerNorm, tied embedding/head; BPE2048 with EOS256 (TRAIN-only tokenizer).
- Historical data provenance: TinyStories repository revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`; original pinned raw train SHA256 `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`, valid SHA256 `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`; 2,048 selected TRAIN stories, 256 selected VAL stories, 64 sealed historical TEST stories. Same exact family/story membership and BPE manifests are mandatory.
- 1,024 steps × 4,096 **valid scored target positions** per optimizer step = 4,194,304 scored token-position exposures. GPU precision FP16; microbatch 8 and dynamic gradient accumulation; checkpoints 256/512/768/1024 (READY-last). Historical step1024 checkpoint SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- Historical H1 VAL: 3.5223388517 nats/BPE-target vs TRAIN-fitted Add-α0.1 bigram 3.9972314170; this is scoped to 256 VAL stories. Old TEST already consumed in one prior sealed evaluation; no reuse.

## 2. Strict control matrix

| Dimension | Historical T4 step1024 | NEW matched step1024 | Paired prospective legacy/new step2048 |
|---|---|---|---|
| Model | 3,749,376 P02 parameters | exactly 3,749,376 and identical P02 config | same model for both prospective arms |
| Tokenizer | T1 TRAIN-only BPE2048 | exact T1 BPE2048 manifest, not UTF8 byte identity/BC-v2 | exact same frozen T1 BPE2048 |
| TRAIN/VAL | 2048/256 fixed TinyStories | same IDs, exact bytes and rights | same frozen data, no new TEST |
| Context | 256 | 256 | 256 both arms |
| Learning/eval objective | next-token full-vocab CE with EOS/source-specific masking | exactly matched shift, mask, normalization | both arms same prereg loss |
| Tokens/optimizer step | 4,096 valid targets | 4,096 valid targets | 4,096 per arm per step |
| Steps | 1,024 | 1,024 | 2,048 per arm |
| Train token exposures | 4,194,304 | 4,194,304 | 8,388,608 per arm |
| Precision/optimizer/schedule | original FP16/AdamW/seed/locked LR schedule | reproduce exact original unless a difference is explicit | freeze a **common 2,048-step schedule** before either prospective arm |

**Critical fairness rule:** Matching parameter count and step count alone is NOT enough. Pin same optimizer, beta/eps/weight decay, LR and warmup/decay, precision, sampling with replacement, dynamic accumulation, total valid-target denominator, seed and RNG/control conditions, code provenance and tokenizer. Any intentional algorithm difference is a predeclared intervention. If all are identical, this is a reproducibility test and cannot be marketed as a model-improvement experiment.

## 3. Comparisons, checkpoints and statistical interpretation

**A — direct historical comparison at step1024:** evaluate historical T4@1024 vs new P02-from-random@1024 on the **same 256 historical VAL stories** and identical BPE full-vocab NLL implementation, showing per-story paired differences, 95% paired-story bootstrap intervals, NLL/target, bpb computed from raw scored bytes where exact spans are verified, throughput, peak VRAM, wall time and sample provenance. VAL is an engineering/development comparator already used in original training; no independent confirmatory claim or new TEST access. Both runs should preserve source/weights/config manifest checksums. If the old seed's whole state cannot be reproduced, record stochastic differences and do not claim exact reproducibility.

**B — matched step2048:** a valid *two-checkpoint at 2048* claim needs legacy/control@2048 AND new-run@2048 with same TinyStories, exact architecture/size, tokenizer, 4,096 valid targets/step, **common 2048 prereg schedule and comparable random-seed/sampler policy**. Use two prospectively controlled runs from scratch and capture 1024 and 2048 in EACH run. Historical T4@1024 had a 1024-step schedule; comparing it directly to a 2048-schedule intermediate checkpoint is secondary context, not the primary same-recipe control. Run 2048 once per arm under one integrated Q4 decision after R1–R7.

**Checkpoint provenance caution:** EmbeddingGemma2 token-swap branch has four actual A/B/C/D step2048 checkpoint SHAs (`ed7419f6…`, `a4bb239a…`, `ba04731f…`, `db5bebe2…`) and 118/118 synthetic/preexecution QA, but not an adjudicated 2048 improvement on fresh real heldout. Do **not** identify its A checkpoint as the legacy control without exact architecture/data/train-loop/rights/provenance readback; if matched, it could replace a prospective legacy arm, otherwise label separate exploratory research.

**Overfitting:** 498,287 distinct historical TRAIN target positions imply roughly 8.42 scored exposures per position at 1024 and 16.84 at 2048 (average target-position reuse, not actual uniform exposures). Compare 256→512→768→1024→1536→2048 TRAIN and VAL curves at predetermined checkpoints. No early stopping or model selection on sealed TEST; no peeking at TEST.

## 4. Required implementation replacement of PR #44

- Existing PR44 runner `CFG.steps=40`, model 2 layers/d128/context128, tokenizer vocab258 **cannot be used for this science comparison**. Its source-only QA 17/17 per OS is preserved as technical evidence only; it does not imply scientific readiness.
- Replace/extend the owner-runnable Colab notebook on a new exact commit with original frozen T4 P02 config plus TRAIN-only BPE2048; disable the 40-step experimental route for comparative science and enforce correct pair IDs, step/target caps and per-story masking.
- For milestone 1024 implement exact TinyStories manifest + source readback; never silently use synthetic identity-byte pack, historical T4 weight as *initialization*, or BC-v2 roles. New model must initialize random at step0.
- For prospective milestone 2048 implement two arms and fully versioned scheduler/optimizer/stateful checkpoint-resume, atomic READY, explicit step1024/step2048 artifacts. Same exact source, data, vocab, seeds/PRNG contracts and independent paired evaluator. Not just parameter count.
- Resource QA must benchmark representative model/context/batch, optimizer, evaluation and checkpoint on the current Colab T4; hard cap per arm/total, graceful OOM/no-overwrite recovery and logging. No fixed 40-step *science* limit; synthetic quick probes remain allowed as QA but cannot be promoted.
- Dedicated independent QA and owner approval for new action, rights specific to internal computational TinyStories and fresh validation/holdout. Historical TEST remains sealed and not rerun.

## 5. Admission / PM decision

| Gate | Decision now |
|---|---|
| Engineering source R0 | PR44 old 17/17 QA stays PASS_SCOPED_OLD_VARIANT, new matched candidate NOT_IMPLEMENTED |
| R1 measurement | HOLD until exact full-vocab same-BPE paired scorer, byte spans and gold protocol |
| R2 data rights | Legacy TinyStories rights evidence reusable with conditions; new action/source/manifest family exact readback REQUIRED |
| R3 codec/checkpoint | old T4 checkpoint available for historical comparison; new from-random weights NOT_EXECUTED; 2048 provenance UNVERIFIED |
| R4 T4 resource | Python312 environment PASS, representative matched 4M x 1024/2048 resource QA NOT_EXECUTED |
| R5 A-I2 | NOT_APPLICABLE to new baseline, historical I2 stays HOLD |
| R6 prereg | DESIGN_AMENDMENT_APPROVED; prereg must freeze exact 1024 and 2048 arms, schedule, metric, alpha/CI and budget |
| R7 independent QA | NOT_EXECUTED for corrected matched experiment |
| Q4 | HOLD_NO_NEW_MODEL_DISPATCH; no real training or TEST |

**Single next operation:** `TTM_PM_TINYSTORIES_MATCHED_4M_1024_2048_COLAB_RUNNER_SOURCE_REPAIR_AND_INDEPENDENT_QA_ONEPACK`. Deliver an exact-source matched notebook and one integrated Q4 review; do not run the old PR44 MODE=PROBE/TRAIN_REAL notebook. No micro-permits, no automatic training, no main/lineage merge.
