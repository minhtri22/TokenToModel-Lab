# TTM-Small-4M × EmbeddingGemma 2 — thí nghiệm GPU MỚI 2.048 × 4.096, preregistration

**Ngày:** 2026-11-09. **Người sở hữu phê duyệt:** thí nghiệm độc lập mới với **2.048 bước mỗi nhánh**, không tự động tiếp tục từ checkpoint của thí nghiệm GPU 1.024 bước vừa hoàn tất. **Trạng thái khi khóa tài liệu này:** `NOT_EXECUTED`, chưa có `CLAIM.json` hoặc kết quả mới.

**RUN_ID mới duy nhất:** `ttm_small4m_gemma2_directswap_2048x4096_t4_gpu_20261109_v1`.

## 1. Scientific question

Trên cùng Transformer TTM-Small-4M đã huấn luyện trước (P02 step1024), liệu **2.048 optimizer updates thích nghi mới, mỗi bước 4.096 nhãn TRAIN**, có giúp cách thay embedding trực tiếp bằng input token vectors EmbeddingGemma 2 đạt **NLL VAL thấp hơn cả hai đối chứng TTM gốc** (A tied, B untied), đồng thời tốt hơn **đối chứng donor vector hoán vị D** không?

### Lưu ý đúng khái niệm

- **Một experiment mới**: tất cả A/B/C/D đều **khởi tạo lại từ hai artifact bất biến gốc** (`T4 original checkpoint step1024` và `candidate_initialization`), **optimizer mới** và `RUN_ID` mới. **KHÔNG** dùng bất kỳ weight, optimizer, checkpoint `READY` hay `CLAIM` nào từ 1.024-bước GPU trước, 64-bước CPU hoặc các phiên TRAIN trước.
- **2.048 bước bổ sung** từ cùng điểm khởi tạo TTM checkpoint step1024; không được gọi là model huấn luyện from-scratch 2.048 bước, và không so C được tiếp tục 2.048 bước với B dừng ở 1.024.
- Giữ seed và hyperparameters như GPU1024 (`SEED=20261109`, train sampler `20261180`) để giữ khả năng so sánh *lịch TRAIN*, nhưng vì đây là các execution mới/điều kiện runtime khác, kết quả tại step1024 **không được giả định bitwise trùng** với run cũ. Toàn bộ kết luận phải dựa trên **đối chứng đồng thời** của run mới.
- Một seed + VAL đã được đánh giá nhiều lượt: **exploratory/descriptive only**, không khẳng định khoa học confirmatory, generalization trên unseen TEST hoặc lợi ích ngữ nghĩa causal của pretrained donor.

## 2. Locked input and four arms

| Arm | Initial state from frozen originals | What trains |
|---|---|---|
| **A** | P02 trained step1024, original tied `tok/head` | All original P02 parameters |
| **B** | Clone untied output-head of same P02 checkpoint; initial A/B logits exactly equal | P02 parameters and separate LM head |
| **C** | Exact saved EmbeddingGemma 2 input-token mapped candidate `[2048,512]`, 1.917 valid token IDs, pretrained donor table frozen, 512→256 ridge adapter, cloned output head | Projection and original decoder/head parameters; raw donor rows/fallback frozen |
| **D** | Same frozen donor vectors **permuted only across 1.917 valid IDs** by seed 20261109; same shape/valid mask/fallback; ridge0.01 refit to original frozen TTM embedding (no VAL) | Exactly same trainable-policy and architecture as C |

Pinned input SHA-256 (the *same verified originals* as the completed GPU1024 experiment):
- TTM P02 original step1024 `checkpoint.pt` = `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- EmbeddingGemma 2 donor-mapped `candidate_initialization.pt` = `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`.
- Frozen TRAIN/VAL NPZ = `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; manifest = `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`. NPZ contains TRAIN+VAL only, no TEST.
- P02 exact source `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`, EmbeddingGemma input swap source `d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39`. Both files frozen from prior project source, not regenerated.
- Donor revision `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e` was already used to produce the candidate. **No new donor download needed**.

## 3. Equal per-arm budget and exact training policy

- A/B/C/D each **2.048 optimizer steps × 4.096 valid TRAIN targets/step = 8.388.608 target exposures**. Total over four arms = **33.554.432 exposures**. Full same fixed TRAIN window schedule for all arms. 2.691 original TRAIN windows; exact-target truncation mask `-100`; shared NumPy `default_rng(20261180)` and generated `SHA256(schedule)` pinned by source preflight/readback **before first optimizer step**. 4.096 targets are the numerator budget, not nominal batch size.
- Same optimizer policy as GPU1024: fresh `AdamW(lr=1e-4,betas=(0.9,0.95),eps=1e-8,weight_decay=.1)`, clip norm `1.0`, constant LR; `CUDA FP32_NO_TF32`, microbatch max **8 windows** and gradient accumulation. No optimizer T4/1024/64-state carry-over, no hyperparameter changes based on interim metrics.
- A/B parameters differ due to tied vs untied; C/D add `512→256` adapter; **equal TRAIN label/step/optimizer budget but not equal FLOPs or trainable parameter counts**. Report that limitation.
- No validation checkpoint selection or intermediate VAL scoring. When four arms complete, score VAL exactly once from their respective final step2048 checkpoints.
- Checkpoint READY-last at steps **512/1024/1536/2048 per arm**, writing full model + fresh optimizer + CPU/CUDA RNG states, full loss prefix, source SHA + immutable input pins, cumulative GPU seconds. SHA256 read back on mounted Drive before READY. **No overwrite** of original T4 checkpoint, earlier 64/1024 experiments, source ZIPs, `lineage.md` or T5 artifacts. 4 milestones reduces stored bytes vs 8 milestones but increases last lost-work interval on interruption.
- Single `RUN_ID`, `CLAIM` created only after GPU availability, locked exact source/input fingerprints, packed-data schema, A/B zero-change logits and TRAIN schedule checks. Resume only against **same `RUN_ID`, exact `CLAIM`, source, input hashes and verified READY**, not via previous experiment's checkpoint. No auto-retry under a new experiment ID. Incomplete state must report `INCOMPLETE_NO_VERDICT`. GPU compute cap **5.400 cumulative seconds**, as GPU1024; stops after checkpoint preservation if exceeded, without calling partial run complete.
- Choose Colab Tesla T4 only when resource is not needed for mainline TTM-Small T5. Code and checkpoint archive remain in a **new named Google Drive folder**; no public weights/data.

## 4. Exact VAL-only decision gate

After **all** arms reach step2048 READY: evaluate unchanged VALIDATION cohort (328 windows, **256 stories**, **61.122 target labels**) on identical masks (cross-entropy ignore_index=-100). Per-story weighted score `sum(loss)/sum(valid targets)`; story-level paired bootstrap **1.000 resamples seed 20261109**, 95% percentile intervals for **A−C, B−C, D−C**. **Lower NLL is better**, so improvements positive only when C wins.

- **`DIRECT_SWAP_2048_POSITIVE_EXPLORATORY`** only if **all three paired-bootstrap 95% lower CI bounds >0** and independent evidence QA passes.
- Otherwise **`DIRECT_SWAP_2048_BENEFIT_NOT_ESTABLISHED`**, preserve exact negative/mixed result even if C beats A but not B, or C beats D only.
- Science only after independent QA checks ORIGINAL CLAIM/RESULT, four final checkpoints, schedule SHA, complete logs, per-story sums/bootstrap, training exposure budget. Merely printing `RESULT.json` is `COMPLETED_UNADJUDICATED`, not final PASS.
- No TEST access; the former 64-story TTM TEST was already consumed in T4 and cannot be silently reused.
- No retrospective changing LR, bootstrap, model ranking, dataset or metric. No additional 4.096-step extension automatically authorized.
- Owner's explicit sequence: **after the 2.048-step result and independent adjudication, decide whether to execute `TTM_SMALL4M_EMBEDDINGGEMMA2_RESIDUAL_GATED_ARCHITECTURE_DESIGN_AND_MINIMAL_PROOF`; do not run that successor beforehand.** Even if direct-swap fails again, next stage is still a **separate owner science decision**.

## 5. Governance and preservation

One bounded owner-approved experiment, no technical micro-permits. Source SHA and notebook SHA published on isolated research branch *after this prereg and before the GPU CLAIM*. Public GitHub receives only source, prereg, aggregate evidence and append-only `lineage.md` **after final independent scientific verdict**, not private TRAIN/VAL arrays, per-story data or actual model/optimizer weights. D1 G4 R1/R2/R3 remains `DEFERRED`. Do not touch merged main, old PR#12, root workplace beyond TTM, TTM P00–P12 or T5 compatibility.
