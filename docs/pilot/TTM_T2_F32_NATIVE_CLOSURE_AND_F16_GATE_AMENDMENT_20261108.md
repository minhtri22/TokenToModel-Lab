# TTM-Small-4M — T2 F32 native integrated QA closure and F16 gate amendment

**Ngày:** 2026-11-08. **Scope:** PR #12 DRAFT, T2 xuất GGUF khả thi trên dữ liệu tổng hợp (zero-science), không phải kết quả huấn luyện mô hình. Exact baseline main: `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.

## 1. Independent readback and provenance

Biên bản CPU được đối chiếu từ JSON do chủ dự án đính kèm và độc lập đọc lại trực tiếp từ Windows:

- Original Windows path: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\f32_pretok_trainonly_v1\TTM_T2_F32_GPT2_PRETOKENIZER_INTEGRATED_QA.json`
- Exact raw SHA256: `21fbaa01e2b9e57f500884c6f4d77c25203d1d4ee89944abf91028c1770348ef`. Đã commit byte-identical tại `evidence/pilot/t2-f32/TTM_T2_F32_GPT2_PRETOKENIZER_INTEGRATED_QA.json` với Git blob `d156c0699c5b1ecafcafbd832796a06f3d24b433`.
- Frozen fixture file SHA256: `5a4ba58db3ad7c1ad0a7c6a790c08184d43c1e3a081ad2dcaf2d4c3b9dbeb9f2`, 20 tokenizer + 10 logits; đã commit byte-identical tại `evidence/pilot/t2-f32/TTM_T2_F32_NEW_FIXTURES_FROZEN_20261108.json`, Git blob `2b187347a89531202cebf9e6062a2b737e079714`.
- Existing model source P02 Git blob: `9762343e06cf800b50574c2871ae1ed58537fb18`; llama.cpp frozen `372dc5ca157276beb6c67b2e92477e8d662e964a`; V5B native probe SHA256 `080c096d52448f665df43ebc962d7a62b17a0781326bc6358e8535d25f37c963`.
- Exact code bundle ZIP SHA256: `d6fd9d09a031c4c19e099f0d66d7d5fcccc0e8543ea602d7268ec6cb415dbcb9`. Source file hashes pinned in GitHub `evidence/pilot/t2-f32/BUNDLE_SHA256_MANIFEST.json` blob `63ab6fcd98fd9f15695d35f2dfaac652efc6a671`. **ZIP and extracted code are still user-visible chat artifacts, not committed to GitHub**; must publish before merging PR #12. Manifest source has field `native_windows=NOT_EXECUTED` because it was created BEFORE Windows execution and must not be retroactively changed.
- Actual GGUF F32 SHA256: `474bc1dcb472cca429ce07747bdaf6ecbe8a7e9b66ce4d5e8658ad919e5e191e`; 15,052,128 bytes, 52 tensors, max abs weight readback error zero.
- BPE: 2048 IDs = 256 byte + EOS=256 + 1791 TRAIN-only GPT-2 pretokenized merges; source commit hash of synthetic BPE `e85028842955334cad014d6f1365f95d79ec953f7cab3a0a2f75ded83bcb1a08`; raw file SHA256 `652d74488646d8d329792a37cef3ba1bfcd221d7ec7ee57dc6700208a3ca1fca`. Full generated manifest remains on Windows under one-shot work directory; remote read truncated a 20k-character segment, so it was NOT copied incompletely to GitHub.
- CPU native tokenizer exact IDs **20/20 PASS**; logits 2048-dimensional vectors **10/10 PASS**, max absolute diff `0.0008438229900207261` <= prereg `0.001`, top1 mismatch 0.
- Negative controls `reject_VAL`, `reject_TEST`, `reject_wrong_source`, `reject_unknown_token_id`, `reject_EOS_decode` all true.
- `train_data=SYNTHETIC_TRAIN_FIXTURE_ONLY_NOT_TINYSTORIES`, `gpu_used=false`, `science_executed=false`. No real dataset acquired.

## 2. Integrated technical decision

**T2_F32_EXPORT_FEASIBILITY=PASS_TECHNICAL_SCOPED.** P02 initialized untrained weights + 2048-ID BPE fit only to synthetic TRAIN + GGUF F32 + real llama.cpp CPU met 20/20 fresh tokenizer checks and 10/10 fresh logit checks. This is sufficient to close the *synthetic F32 export feasibility* problem, NOT to claim trained-checkpoint conversion, Ollama deployment, dataset quality or scientific H1.

**F16 critical-path change:** for the roughly 3.75M-parameter pilot, F32 correctness remains mandatory before long training; F16 and Q8/Q4 are deferred into optional optimization/deployment A/B. V4/V5B failures stay recorded as `F16_BACKEND_BLOCKED`, never relabeled PASS. This is a scoped draft-pilot exit-criterion amendment, preserving the complete P00–P12 architecture, prior test outcomes, P07 status and the distinction between technical QA vs scientific lineage. Review/merge still required before claiming project-wide governance lock.

## 3. Non-negotiable remaining gates

- T1: TinyStories revision & rights review, verify raw-file SHA256 bytes, story-boundary parser, exact/near-dup coverage, TRAIN/VAL/TEST manifests, no TEST leakage, train 2048 BPE on **real TRAIN only**, then recheck native tokenizer parity for the **actual** frozen merges/IDs.
- T3: Colab T4 runtime capacity synthetic smoke, locked dependencies/environment, Google Drive READY-last checkpoint readback, and continuous 20 steps vs 10-save-resume-10 equivalence including optimizer/scheduler/RNG/cursor.
- Before T4: one combined prereg scientific gate for source, budget, invariants and tests; no new permit for each minor technical subcheck.
- T5: the *trained checkpoint* Windows GGUF/llama.cpp/Ollama numerical and generation validation (not implied by synthetic T2).
- No science entry in append-only `lineage.md` for the QA results.

| Gate | Adjudication |
|---|---|
| `T2_F32_NEW_FROZEN_TOKENIZER_NATIVE` | **PASS 20/20** |
| `T2_F32_NEW_FROZEN_LOGITS_NATIVE` | **PASS 10/10 (max 0.00084382299)** |
| `T2_F32_SYNTHETIC_EXPORT` | **PASS / TECHNICALLY CLOSED** |
| `T2_F16_CPU` | **BLOCKED, preserved** |
| `T1_REAL_DATA_AND_TRAINONLY_BPE` | NOT_EXECUTED |
| `T3_COLAB_DRIVE_RESUME` | NOT_EXECUTED |
| `T5_TRAINED_CHECKPOINT_EXPORT` | NOT_EXECUTED |
| `SCIENCE_LOCK` | **HOLD** |
| `COLAB_T4` | **NOT_STARTED** |

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_T1_T3_TINYSTORIES_SOURCE_SPLIT_AND_COLAB_DRIVE_RESUME_INTEGRATED_PREFLIGHT`. Preserve consumed engineering QA evidence. Upload the exact code ZIP/extracted byte-pinned source to this PR before merge; do not generate a new T2 run. No TinyStories TRAIN or Colab GPU train before real-source and resume gates.
