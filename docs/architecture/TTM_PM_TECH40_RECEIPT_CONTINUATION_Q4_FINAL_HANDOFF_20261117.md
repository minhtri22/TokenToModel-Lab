# HANDOFF — TTM PM TECH40 exact original receipt -> TinyStories @1024 matched replication Q4

**Operation:** `TTM_PM_TECH40_PASS_TO_TINYSTORIES1024_EXACT_RECEIPT_CONTINUATION_AND_INTEGRATED_Q4_ONEPACK`  
**Ngày:** 2026-11-17 · **Repository:** `minhtri22/TokenToModel-Lab` · **Draft PR:** #44.  
**Locked baseline main:** `59ee3f30b996405fddc087ab60102b59a021f8ea` — unchanged.  
**PM decision:** `GO_CONDITIONAL_EXACT_OLD_TECH40_CUSTODY_FOR_1024_REPLICATION_VAL_ONLY`. Not GO unconditionally.

## 1. Provenance, input custody and exact byte requirement

From user's Colab stdout:

`PASS_FULL_P02_SYNTHETIC_40_SCOPED · GPU=Tesla T4 · torch=2.11.0+cu128 · python=3.12.13 · 40/40 steps ×4096 targets · P02=3,749,376 params · FP16 · 13.2061s wall · worst=0.03436s · peak CUDA reserved=320,864,256 bytes · test_accessed=false · science_executed=false`.

**Original runner blob:** `113434e25fe19cff27b47f428cf99a0a57ae4fcf` from historical commit `2b8a3613dea0daa5babf6f85fc7ea4ec093d4135`. **Current repaired wrapper blob:** `933f42b514de5fac650bfa2a421844c51b9b7c64` from `500c9e119fb1bc3e424abacd1afa3bb1aa2aba7e`. Exact source comparison must show byte-identical extracted implementations for 22 critical functions, including recipe, model init, optimizer/trainer, capacity receipt validation, checkpoint READY, resume, paired bootstrap and comparator. Allowed wrapper changes only: `cuda_guard`, `one_session`, `main`, plus added `live_t4_preflight`. No post-hoc silent reinterpretation of the old receipt as a new runner execution.

**Expected original raw receipt SHA256, candidate reconstructed from user's complete stdout:** `1a273db7f175578cdc9cf6a976d4679835a42d86a1c0c1604a6ea4e64596a1d9`. This is a *prediction*, **not** an independently fetched hash of the actual Colab file. No TECH40 receipt file is presently accessible in connected Google Drive; searching `TECHNICAL_SYNTHETIC_40.json`, `TTM_40_1024` and `TECH40` returned no hit. Until the original exact bytes are inspected in Colab, **`BYTE_CUSTODY=HOLD`**.

The continuation script requires three **existing original files** in the exact same session root, e.g. `/content/TTM_MATCHED_4M_SESSIONS/TTM_40_1024__<original_RUN_ID>/`:
- `TECHNICAL_SYNTHETIC_40.json`: actual raw bytes, SHA256 must equal frozen candidate.
- `SESSION_LOCK.json`: original run ID, original runner Git blob, frozen recipe/pack/checkpoint identities, `integrated_go_sha256=null`.
- `SESSION_STATUS.json`: `TECHNICAL_40_PASS_SCIENCE_HOLD_NO_Q4`, exact receipt SHA, `science_executed=false`, `compare_executed=false`, `test_accessed=false`.

No repaired/approximated receipt is accepted. If the original Colab runtime reset and the session files disappeared, execution **HOLD**; never reconstruct the missing raw receipt from pasted stdout and claim byte custody. Preexisting TECH40 PASS remains documented as user-console engineering evidence even in that situation.

## 2. Single integrated PM Q4 decision

Immutable public PM decision: `docs/architecture/TTM_PM_Q4_TECH40_REUSE_1024_VAL_ONLY_DECISION_20261117.json`. Git blob `8b99e436dd1c31bde3c684167be8a475a73b0dcc`.

**Verdict:** `GO_CONDITIONAL_EXACT_OLD_TECH40_CUSTODY_FOR_1024_REPLICATION_VAL_ONLY`, specifically for:
- TTM P02 exact 3,749,376-parameter decoder-only GPT, context256, BPE2048, seed20261108.
- 2048 frozen TinyStories TRAIN /256 historical VAL, train pack SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`, manifest SHA256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece49468acb53322d650`; NO TEST.
- 1024 optimizer steps, 4096 valid scored labels/step; *fresh* random model, old TECH40 weights thrown away.
- Original Small-4M T4 checkpoint LEFT@1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; new GPT RIGHT@1024.
- Development-only paired 256-story NLL and 2,000 paired bootstrap resamples; neither model-improvement claim nor a new sealed TEST.
- Persistent *owner Google Drive* target, READY-last checkpoint@256,512,768,1024 with full optimizer/scheduler/RNG/scaler, no overwrites and at most one continuation claim.
- An exact original TECH40 byte readback, original source comparison, frozen Q4 Git blob, actual old private pack/checkpoint byte custody and T4 runtime readback **all must PASS inside Colab before optimizer step 1**.

These conditions are **one integrated Q4**, not separate discretionary micro-permits. A `GO_CONDITIONAL` decision here is not permission to bypass a failed check. The JSON is a GitHub-recorded PM decision, **not a private cryptographic owner signature** or cross-device anti-replay authority. Implemented original-session `PM_TECH40_CONTINUATION_ONCE_CLAIM.json` uses create-exclusive write to prevent accidental reuse on that original storage location, but cannot prevent deliberate copying of all source data to new locations.

Historical science already completed once and is preserved unchanged. This new 1024 run is a **reproducibility / implementation-readback experiment**, not an architectural intervention: same model, data, seed and algorithm. Improvement on previously identified failure modes is **not established** by this protocol.

## 3. Exact implementation

**Bridge script:** `src/ttm_new_gpt_baseline/tech40_continuation.py`. It loads **the original runner byte-for-byte** for new science, not the repaired runner, so the original capacity receipt remains attributable to the exact training/capacity code. The repaired runner is separately read only to check that critical functions are identical and wrapper changes scoped.

**Colab notebook:** `notebooks/TTM_NEW_GPT_BASELINE_T4_ONEPACK_20261117.ipynb`. Notebook source cache includes SHA-pinned original runner, current wrapper, bridge and Q4 decision. `MODE=SOURCE_QA` remains default.

**Required owner actions in Colab (no manual source editing):**

1. Keep **the same Colab runtime** where TECH40 PASS occurred; do not delete or reset the original session folder.
2. Mount Drive with `from google.colab import drive; drive.mount("/content/drive")`. Existing frozen pack and checkpoint are at `/content/drive/MyDrive/TTM/ttm-small-pilot/`.
3. Choose `MODE = "BRIDGE_PREFLIGHT"` and execute notebook code cells. Auto-discovery requires exactly one original TECH40 session in `SESSION_PARENT`. For multiple sessions, set the already-provided variable `OLD_SESSION_EXPLICIT` to the exact old session path (not copy its bytes).
4. Only when `BRIDGE_PREFLIGHT` prints `PASS_TECH40_RAW_BYTES_AND_PRIVATE_DATA_CUSTODY_NOT_TRAINED`, choose `MODE = "CONTINUE_VERIFIED_40_1024"`, `RESUME_FROM_STEP = None` and execute the code cells. This mode includes every gate again, then starts NEW model random init and TinyStories@1024; **no repeat of synthetic40**.
5. If preempted with a valid checkpoint READY, rerun the same mode with `RESUME_FROM_STEP=256`, `512`, or `768`, selecting the latest actual checkpoint. If model@1024 finished but comparison not yet produced, re-entering without `RESUME_FROM_STEP` can finish comparison without re-training, after verifying RUN_LOCK and one-shot claim.

**Important:** Original session metadata is **append-only** except new once-only claim; no old receipt mutation. New model checkpoints and VAL comparison are in deterministic fresh path `replica_1024__adopt_<old_run_id>` under owner Drive. Do not change `main`, `lineage.md`, baseline checkpoint or sealed TEST in this operation.

## 4. QA and evidence

Current QA scope is source-only Windows/Linux Python3.12 (13 original stdlib runner cases +26 existing source/adversarial cases +14 distinct bridge negative cases =53 per OS) and native CPU synthetic full-P02 checkpoint/resume consistency. Bridge tests verify exact immutable old/new Git blob content, source function equality, Q4 Git blob, no false receipt from stdout-only, no double-claim, missing/private metadata and strict no-rerun synthetic40 property. These tests are authored by the same assistant across separate code paths — **not independent human reviewer**. Native Colab T4 science@1024 and paired VAL **not executed in this GitHub/PM operation**. User-owned Colab is the only machine authorized to access current original receipt bytes and execute the conditional Q4.

**Formal PM outcome:** `TECH40_USER_T4_PASS_SCOPED · OLD_NEW_SOURCE_EQUIVALENCE_PASS_SOURCE_QA · Q4_GO_CONDITIONAL_EXACT_BYTE_CUSTODY · ACTUAL_RAW_TECH40_BYTE_SHA_NOT_YET_READBACK · NEW1024_NOT_EXECUTED · PAIRED_VAL_NOT_EXECUTED · TEST_NOT_ACCESSED · MAIN_UNCHANGED`.

**Bước thực hiện tiếp theo — duy nhất:** In the existing Colab runtime, run `BRIDGE_PREFLIGHT`. If and only if all exact checks pass, the **same preauthorized Q4** permits the `CONTINUE_VERIFIED_40_1024` mode immediately; no further micro-permit. Save raw preflight and final receipts in owner Drive.
