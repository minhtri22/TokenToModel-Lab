# TTM T4 — TRAIN/VAL private pack producer readback and real-window capacity adjustment

**Date:** 2026-11-08. **Scope:** T4 *zero-science* technical preflight, GitHub PR #12 DRAFT. Source/data/architecture T1–T3 unchanged. **Do not upload private token NPZ or original TinyStories text to GitHub.** `lineage.md` remains unchanged, science lock HOLD.

## Producer execution and readback

PowerShell 5.1 script pin/parser PASS; `Run-TTM-T4-Data-Pack-PS51.ps1 -Mode Preview` PASS READONLY, `-Mode Execute` finished `T4_TRAIN_VAL_PACK=PASS_PRIVATE_NO_TEST`, with shell's separate `Get-FileHash` for the NPZ matching the producer manifest. RemoteDesktop read-only confirmed exactly two files in `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t4_data_pack_v1` and independently read manifest text.

- Private NPZ: `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz` **1,186,107 bytes**, SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; **NEVER PUBLISH**.
- Original TRAIN and VALID source SHA pinned exactly `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f` and `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`. Frozen T1 split SHA `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; BPE manifest file SHA `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, internal BPE SHA `6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6`.
- `TRAIN=2048 stories`, `VAL=256 stories`, `TEST tokenized=0` (producer metadata claim, not yet independent array-level readback).
- TRAIN `2691 windows`, `498287 valid target positions`, mean `185.1679672984021` per window, `24.228911185432925%` full 256-target windows, minimum 1. VAL `328 windows`, `61122 target positions`, minimum 2.
- Proposed science exposure budget = `1024×4096=4194304` target exposures; this is **8.417446170580408×** the distinct TRAIN target *positions* in the frozen pilot, not 8.42× unique vocabulary tokens. Repeated exposures can materially increase memorization/overfit risk. Report train/val gap and per-step window draw counts, never change source scope based on VAL.

## Independent arithmetic cross-check (based on producer manifest + already verified GPU report)

The complete `T4_CAPACITY_REPORT.json` downloaded independently from Drive SHA256 `c55a568496a888bc3abc95c0231a5ed17d3a6f366361571b6f89a4457d09f1ee`, archived byte-identical in `evidence/pilot/t4-capacity/`. Real window inflation `256/185.1679672984021 = 1.3825285428`; conservative additional factor `×1.10` yields total `1.5207813971`. *Heuristic only*:

| Precision | Microbatch windows | Synthetic projected 1024-step +25% reserve | Shape-corrected +extra10% (seconds) |
|---|---:|---:|---:|
| fp32 | 2 | 125.41 s | **190.72 s** |
| fp16 | 2 | 155.31 s | **236.19 s** |
| fp16 | 4 | 70.30 s | **106.91 s** |
| fp16 | 8 | 37.23 s | **56.62 s** |

FP16/mb8 is currently **best provisional technical candidate**. Synthetic fixed `gradient_accumulation=2` corresponded to 16 full 256-token windows; it is **not the actual real-data accumulation**. Mean real step needs about 22.12 windows (often ~23); trainer must accumulate **dynamically** until exactly 4096 non-PAD targets, and report real `windows_drawn` per step. Never freeze accumulation=2 from the synthetic trace.

**Budget note:** 56.62 seconds is an extrapolation of short synthetic compute-only benchmarks, **not** a realistic certified runtime; VAL, dataset movement, GPU jitter, checkpoint hashing/Drive and sample-window-length variance remain unmeasured. Science cap remains 5400s with no auto extension.

## Remaining integrated acceptance, no micro-permits

An independent, SHA-pinned audit script has been prepared as conversation artifact `TTM_T4_PRIVATEPACK_INDEPENDENT_QA_AND_CAPACITY_V1_20261108.zip` SHA256 **`00011d0eff3b914abdd4d366a463040c5d3273dfb75ed4d2e1296c7475fba610`**. It checks the actual private NPZ arrays, 8 TRAIN/VAL keys only, shapes/dtypes/masks/targets, story EOS boundaries and window joins, no TEST arrays, source manifest hashes, and independent budget arithmetic. Python AST, synthetic positive/negative tests **PASS 3/3**; **NOT run on actual private Windows NPZ yet**. Only writes a non-sensitive JSON QA receipt to a fresh `_tmp/ttm_t4_privatepack_independent_qa_v1` directory. No TRAIN rerun, no GPU.

Next **single integrated scientific material QA** after private pack: independently audit NPZ and capacity corrected receipt, archive only sanitized metadata to PR, perform one bounded synthetic **real-shaped window** trainer + Drive/READY integration and source-pin review, then decide one-shot science permit. No T4 TinyStories training until all PASS.

**Current states:** `T1/T2/T3=PASS_SCOPED`; `T4_PRIVATE_PACK_PRODUCER=PASS_SHA_READBACK`; `T4_PRIVATE_PACK_INDEPENDENT_QA=NOT_EXECUTED`; `T4_GPU_SYNTHETIC_CAPACITY=PASS_PROVISIONAL`; `T4_CAPACITY_CORRECTED=PROVISIONAL`; `T4_SCIENCE_LOCK=HOLD`; `T4_TRAIN=NOT_STARTED`.
