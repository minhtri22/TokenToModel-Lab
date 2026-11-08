# TTM-Small-4M T4 — Independent exact-source archive verification and single integrated scientific-admission adjudication

**Date:** 2026-11-08. **PR #12** open DRAFT; **reviewed HEAD** `97b7a88196487caf348e50c158272fd09f174f62`; main `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`. **Verdict: HOLD_MATERIAL_ADMISSION_GAPS, no T4 science authorization issued.** The next review must evaluate the missing material prerequisites *together*, not create a separate permit for every small technical check.

## A. Exact source archival — PASS and CLOSED

Windows one-shot operator result: `TTM_T4_SOURCE_ARCHIVE=PASS_19_FILES_EXACT_REMOTE_READBACK`, cleanup `PASS_SCOPED`. GitHub independent readback of HEAD versus parent `8e32fffc44544beccd80dbf0034e24ed070ddb1c` finds exactly **19** added files in one commit and no unrelated modifications:

- 15 files under `tools/pilot_t4/integrated/` match the original `TTM_SMALL4M_T4_INTEGRATED_PREREG_CAPACITY_AND_TRAINER_20261108.zip` SHA256 `cda8e692ce614c804bdffa1850abe6faeb0c51bccc0a8a0c1fbdee0145a0f524`.
- 4 files under `tools/pilot_t4/gpu_integration/` match `TTM_T4_SYNTHETIC_TRAINER_GPU_INTEGRATION_V1_20261108.zip` SHA256 `a3f122bfbe0e5c59bfe7a74fb140c782dcb0a19b2036cb20ac906e6109657a94`.
- For **every one** of the 19 files, independently calculated Git object SHA1 `sha1("blob <bytes>\\0" + bytes)` from original ZIP contents matched the exact GitHub `fetch_file(...,ref=97b7a881...)` blob SHA. **19/19 PASS.**
- Independently reran frozen `tests/test_t4_integrated.py` on isolated CPU: **13/13 PASS**. This is additional non-scientific code QA; does not replace the prior GPU independent integration PASS.
- PR stays DRAFT; main and historical P07 are not modified; do not rerun Archive, T1/T2/T3, or consumed GPU tests.

## B. Methodological and bounded-pilot contract — REVIEWED_SCOPED, not generalization proof

The previously approved *candidate* remains unchanged:
- Dataset `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, original pinned source SHA TRAIN `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`, VALID `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`. Bounded pilot 2048 TRAIN, 256 VAL, 64 sealed TEST, BPE2048 from 768 TRAIN only. Exact and near-duplicate audit is scoped to **active pilot subsets**, not all 2.1M raw stories. License CDLA-Sharing-1.0 obligations remain; no raw stories or reversible tokens in public repo.
- Primary fixed checkpoint step 1024, **1024 optimizer steps ×4096 actually scored non-PAD targets/step = 4,194,304 target exposures**, seed 20261108; 498,287 distinct active TRAIN positions => **8.417× mean reuse**, not 4.19M independent examples. AdamW/LR schedule and checkpoints at 256/512/768/1024 as pinned. TRAIN may be sampled with replacement, no VALID/TEST influence on sampling.
- Primary H1 success only if final step1024 VAL next-token NLL **≥5% lower** than Add-α(0.1) bigram fit to TRAIN only **and** story-bootstrap 1000 seed20261109 95% **lower bound** of absolute bigram-model NLL gain >0. TEST is sealed until one final evaluation after fixed VAL verdict. H2 resumed checkpoint and H3 *trained* model F32 GGUF/Ollama belong to post-training adjudication; T2 untrained parity is not H3.
- T1–T3, T4 independent private TRAIN/VAL pack, synthetic 4096-target capacity on Tesla T4 and synthetic GPU/Drive trainer-resume have verified PASS in **their narrow technical scopes**. Proposed FP16 microbatch-window count 8 with **dynamic** accumulation until exactly 4096 scored targets is supported as an engineering *candidate* (not yet a signed one-shot science lock). F16 GGUF backend block is **optional optimization**; not science experiment blocker.

## C. Material science-admission gaps — source archive no longer one of them

1. **Private Colab data provenance still not verified.** Exact `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz` SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`, source `T4_PRIVATE_PACK_MANIFEST.json` SHA256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`, 1,186,107-byte NPZ must be transferred privately from scoped Windows workspace to a private Drive folder. Google Drive connector search at time of review returned **no matches** for `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz`, `t4_private_pack_20261108_v1`, or `T4_CAPACITY_PRIVATE_PACK_REVIEW.json`. Absence of search hits does not categorically prove file absence, but **there is no authenticated Drive readback**. Do not publish NPZ in GitHub or conversation.
2. **Capacity review file for science runner is not yet pinned/durable on Drive.** T4 `t4_train_science.py` requires a `T4_CAPACITY_PRIVATE_PACK_REVIEW.json` with `CAPACITY_PASS_PROVISIONAL_FOR_SCIENCE_REVIEW`, the exact capacity SHA `c55a568496a888bc3abc95c0231a5ed17d3a6f366361571b6f89a4457d09f1ee`, matching real private pack manifest SHA, and selected `fp16 / microbatch_windows=8`. Recompute/accept this **once**, SHA-pin, retain the reported projected **56.6 seconds as only a heuristic**, never a proven 90-minute guarantee. Keep any prep private, no TEST tokenization.
3. **90-minute runtime-policy semantics require explicit acceptance or one minimal fix.** The frozen `t4_train_science.py` increments `elapsed_gpu_seconds_total` around each training step plus VAL, but `checkpoint_write` occurs *after* this timer, so Drive checkpoint writes and filesystem staging are not counted against the 5,400-second cap. As Colab GPU is allocated during I/O, this is not an enforceable 90-minute **end-to-end runtime** cap. For strict GPU-session budget, require a minimal frozen successor time-accounting fix and non-science QA (or explicitly scope the prereg cap to compute+VAL only with a separate independently recorded wall-time stop). No changes after looking at H1 results.

These are **three fields of one material final admission**, not three new science permits. A single independent acceptance must bind exact branch/source, private data/manifest and authenticated Drive SHA, chosen capacity review SHA, rights/scope/H1 test policy, runtime clock rule, and immutable RunID into one `T4_SCIENCE_LOCK.json` and expected SHA. The current science notebook remains fail-closed (`EXPECTED_LOCK_SHA256='NOT_ISSUED'`); no science lock issued, no T4 TinyStories training, no TEST run.

## D. Binding final verdict

| Gate | Result |
|---|---|
| `T4_SOURCE_ARCHIVE` | **PASS_19/19_EXACT** |
| `T4_SOURCE_CPU_QA` | **PASS_13/13** |
| `T1_T2_T3_AND_T4_SYNTHETIC_TECHNICAL` | **PASS_SCOPED** |
| `T4_DATA_PACK_LOCAL_INDEPENDENT` | **PASS_SCOPED** |
| `T4_PRIVATE_DATA_AUTHENTICATED_DRIVE_SHA` | **HOLD_NOT_VERIFIED** |
| `T4_CAPACITY_PRIVATE_PACK_REVIEW_DURABLE` | **HOLD_NOT_VERIFIED** |
| `T4_5400_SECOND_WALL_CLOCK_CONTRACT` | **HOLD_POLICY_OR_CODE_REVIEW** |
| `T4_SCIENCE_LOCK` | **HOLD_NOT_GRANTED** |
| `T4_TRAIN` | **NOT_STARTED** |

**Bước thực hiện tiếp theo:** `TTM_T4_FINAL_PRIVATE_DRIVE_BINDING_CAPACITY_REVIEW_AND_ONE_SHOT_SCIENCE_LOCK`. Verify private NPZ+manifest from Drive, generate/pin actual capacity review and accept/repair full runtime clock limit together; then one combined independent **GRANT or HOLD**. No rerun of consumed technical checks and no independent micro-permits.
