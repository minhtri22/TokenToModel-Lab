# TTM PM — TinyStories matched Small-4M @1024/@2048 Colab T4 OnePack

**Operation:** TTM_PM_TINYSTORIES_MATCHED_4M_1024_2048_COLAB_RUNNER_SOURCE_REPAIR_AND_INDEPENDENT_QA_ONEPACK
**Ngày:** 2026-11-17. **Original main (unchanged):** 59ee3f30b996405fddc087ab60102b59a021f8ea. **Draft PR:** #44.
**Outcome:** SOURCE_CANDIDATE_IMPLEMENTED · Q4_HOLD · REAL_T4_TRAIN_NOT_EXECUTED · TEST_NOT_ACCESSED.

This document supersedes the old 40-step/d128/context128/vocab258 science proposal. The original historical text remains in Git history for traceability, not as an authorized experiment.

## 1. Exact matched recipe

| Item | Exact source/value |
|---|---|
| P02 GPT core blob | 9762343e06cf800b50574c2871ae1ed58537fb18 |
| Original T4 1024 trainer blob | 76c4d0155cd0736919f41682f240b47ad3d7c428 |
| Original T4 capacity blob | c9a6f256ba975228683ee7de2a1090e649110e97 |
| Original T4 evaluator blob | bef006bdff173fba6d8ba4aa0ef687a1732fd7c4 |
| Model | **3,749,376** unique P02 params, LayerNorm, 4 layers, d256, 4 heads, context256, vocab2048 |
| Tokenizer | Same historical T1 TRAIN-only BPE2048 (not BC-v2; no byte-vocab258) |
| Data | Same exactly pinned TinyStories pack: 2048 TRAIN stories, 256 VAL, historical TEST never read |
| TRAIN targets | 4096 valid next-token labels per step, dynamic accumulation, FP16 microbatch8 |
| Optimizer | AdamW lr3e-4, betas(.9,.95), eps1e-8, decay.1, clip1.0 |
| replica_1024 | 1024 steps, seed20261108, original 32-warmup/1024 cosine schedule, 4,194,304 target exposures |
| control_2048 | 2048 steps, seed20261108, shared 32-warmup/2048 cosine, 8,388,608 target exposures |
| replica_2048 | 2048 steps, seed20261109, **same 2048 schedule and budget**, 8,388,608 target exposures |

Frozen original pack SHA256: 184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913 (1,186,107 bytes).
Manifest SHA256: ef2e6e67d49b1d5a921b1051df329f15574f1c10cece49468acb53322d650.
BPE file SHA256: cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc; split SHA256: 9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9.
Historical T4 checkpoint@1024 SHA256: cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b.

**Scientific interpretation:** replica_1024 vs old checkpoint@1024 checks reproducibility on developmental VAL, not improvement from a changed model. control_2048 vs replica_2048 measures seed variation, not architectural improvement. Never directly compare 1024 vs 2048 as a same-budget pair. EmbeddingGemma2's A/B/C/D 2048 checkpoints are not automatically eligible controls.

## 2. Notebook and modes

Notebook: notebooks/TTM_NEW_GPT_BASELINE_T4_ONEPACK_20261117.ipynb.
Runner: src/ttm_new_gpt_baseline/runner.py.
The notebook pins runner and four unchanged original Git blobs at immutable commits. It must run Python3.12; GPU modes require real Tesla T4. No Drive auto-mount, no dataset fetching, no pip install, no TEST.

- **SOURCE_QA** (default): source SHA readback and 13 stdlib tests; Torch and private data not loaded.
- **NATIVE_QA:** on CPU, actual torch.save/load and exact frozen original checkpoint_payload/checkpoint_load, synthetic 4-step toy uninterrupted vs split2+resume2. Uses new READY-last and resume_state wrappers, checks optimizer/scheduler/RNG/parameters, corrupts file and demands SHA rejection. This is NOT full 4M FP16 T4 resume parity.
- **CAPACITY:** runs 2 warmup + 3 measured optimizer steps on random synthetic tokens using entire original 4M P02, FP16 microbatch8 and 4096 target labels per step. Report peak reserved VRAM, worst step, two-arm 2048-step projection plus 25% reserve; cap 5400s projection and 80% VRAM. Excludes real variable-length short windows, VAL, checkpoint IO/preemption.
- **PREFLIGHT:** owner-selected exact historical private TRAIN/VAL NPZ and manifest SHA and schema/rights check; no model or TEST.
- **TRAIN:** exact single arm, fresh random initial weights, 1024 or 2048 steps, owner Q4 metadata required; no old checkpoint used for initialization.
- **RESUME:** same run_id, Q4, data, arm, source/recipe, latest exact READY; restores model, optimizer, scheduler, sampler, CPU/CUDA/Python/NumPy RNG and GradScaler. No fork/overwrite/final restart.
- **COMPARE:** action-specific Q4, two exact SHA-pinned checkpoints. For 1024, historical T4 LEFT and new replica_1024 RIGHT only. For 2048, prospective control_2048 LEFT and replica_2048 RIGHT only. Paired 256-story VAL NLL bootstrap 2000 resamples; no historical TEST, no per-story private outputs.

Checkpoint storage: checkpoint steps 256,512,768,1024 for the 1024 arm and also 1536,2048 for the 2048 arms. Per-checkpoint model/optimizer/sampler/RNG/scaler in checkpoint.pt, progress.json SHA and READY.json committed last, with exact arm/recipe/data/source identity and no overwrite. Windows/Linux cross-environment bitwise parity not claimed. Default /content storage is volatile after Colab reset; owner should select durable storage before real Q4 run.

## 3. Exact Q4 metadata schema (illustration, NOT a granted GO)

Owner-supplied JSON for a TRAIN/RESUME action must have exactly these fields, with actual pinned digests and a reviewed rights reference:

    {
      "schema":"ttm.matched_4m.owner_q4.v1",
      "action":"TRAIN_OR_RESUME",
      "decision":"GO_EXACT_ONE_SHOT",
      "arm":"replica_1024",
      "run_id":"<owner-unique-8-plus-character-id>",
      "runner_git_blob":"<exact-current-runner-Git-blob-SHA1>",
      "source_main":"59ee3f30b996405fddc087ab60102b59a021f8ea",
      "recipe_sha256":"<runner-recipe_hash-for-arm>",
      "train_val_pack_sha256":"184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913",
      "rights_reference":"<reviewed-and-traceable-data-rights-evidence>",
      "resource_receipt_sha256":"<actual-T4-CAPACITY-receipt-SHA256>",
      "left_checkpoint_sha256":null,
      "right_checkpoint_sha256":null
    }

For COMPARE use action COMPARE, capacity=null, exact left/right checkpoint hashes, pair arm replica_1024 or replica_2048. These values are **declarative interlocks, not authenticated owner signatures**: rights, R4 and distinct QA must still be adjudicated. Notebook does not create a GO.

## 4. QA evidence, limitations and decision

Pure source: 13 runner tests + 15 separately implemented source-oracle tests per Windows/Linux Python3.12 CI. Native CPU synthetic: PyTorch 2.5.1 + NumPy1.26.4 verifies 4-step toy state+RNG exact resume parity and SHA tamper rejection. This is distinct TEST CODE but the same assistant authored it; **not independent human or organizational QA**.

The following are still **NOT EXECUTED**: current owner Colab representative T4 4M/2048 actual resource benchmark, full 4M FP16 resumability on GPU, real DATA rights audit, pair checkpoint evaluation, model training, independent real scorer, and original sealed TEST. Historical A/B/C and Small-4M H1 outcomes are unchanged.

**PM decision:** SOURCE_IMPLEMENTATION_SCOPED; Q4_HOLD, no automatic GPU/model action, no merge or lineage edit.
**Bước thực hiện tiếp theo — duy nhất:** reconcile exact final-head GitHub CI source+native QA and run independent QA of pinned candidate; owner then may run notebook SOURCE_QA/NATIVE_QA/CAPACITY on current Colab T4 and supply one R1–R7 packet for a single Q4 GO/HOLD (no micro-permits).
