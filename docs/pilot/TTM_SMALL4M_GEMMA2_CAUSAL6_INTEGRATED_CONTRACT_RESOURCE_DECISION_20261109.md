
# TTM-Small-4M × EmbeddingGemma 2: Hợp đồng tích hợp sáu nhánh và quyết định tài nguyên

Ngày 09/11/2026. Operation: TTM_SMALL4M_EMBEDDINGGEMMA2_CAUSAL_6_ARM_INTEGRATED_CONTRACT_AND_RESOURCE_DECISION.
Branch: research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109.
Quyết định owner: chốt một lần thiết kế, ngân sách, dữ liệu, phân xử và nguồn lực; KHÔNG cấp phép chạy lại bất cứ thực nghiệm cũ nào.
Trạng thái: INTEGRATED_CONTRACT=FROZEN_V1; SOURCE_RUNNER=NOT_STAGED; NEW_H512=SELECTION_RULE_FROZEN_NOT_SEALED; FREE_T4_RESOURCE=CONDITIONAL; TRAINING=NOT_EXECUTED; CLAIM=NOT_CREATED.

## 1. Phạm vi và giả thuyết

L0017 ghi PASS xác nhận chất lượng của direct-swap checkpoint C (các arm A/B/C/D cố định, 2048 update bổ sung từ T4 bước 1024) trên 320 truyện mới. L0018 ghi FAIL khoa học trong phạm vi residual gate 32 bước G/R, vì G không vượt R, mặc dù G nhỉnh hơn B. Đây là hai cơ chế khác nhau và không mâu thuẫn; giữ nguyên cả L0017 và L0018.

Câu hỏi lần này là hiệu ứng gán vector donor cho đúng token trong direct-swap, vai trò của phương pháp khởi tạo projector, và phần tương tác với việc cho phép Transformer thích nghi. Không đưa width512 vào cùng phép thử; vẫn hidden=256, vocab=2048, context=256, 4 blocks, 4 heads, output head untied. Không GGUF/Ollama.

## 2. Sáu nhánh cố định

Mọi arm từ cùng checkpoint TTM T4 step1024, cùng tokenizer, masks, vị trí và output head đã sao chép nhưng tách trọng số (untied). Embedding donor row 512 chiều đóng băng, 1917 mapped token types; 130 unmapped fragments + EOS fallback bảo toàn E0 và không nhận gradient từ donor.

| Arm | Donor | Initial projector 512 to 256 | Trainable |
|---|---|---|---|
| RR-F | Real correctly mapped | ridge from real pairs | projector + decoder blocks + position + output head |
| RP-F | Permuted over mapped rows | EXACT SAME ridge matrix bytes as RR-F | same as RR-F |
| RR-A | Real correctly mapped | same ridge initialization as RR-F | projector only |
| RP-A | Permuted over mapped rows | same ridge initialization as RR-A | projector only |
| OR-F | Real correctly mapped | orthogonal Procrustes + scale on real pairs | projector + decoder blocks + position + output head |
| OP-F | Permuted over mapped rows | EXACT SAME orthogonal matrix bytes as OR-F | same as OR-F |

Ridge formula on 1917 real token-row pairs X [1917,512] donor and Y [1917,256] TTM: P=(X^T X + 0.01 I)^(-1) X^T Y, shape [512,256], lookup z @ P. It must match the original C initialization recipe before CLAIM. Orthogonal alternative: thin SVD(X^T Y)=U Sigma V^T; Q=U V^T (Q^T Q=I256); s=<XQ,Y>_F/||XQ||_F^2, require finite s>0, P_orth=sQ. Orthogonality is ONLY an initialization condition, not enforced throughout training.

Permutation seed 2026110913, on the 1917 mapped token rows only, never fallback. Fit each projection ONCE to REAL pairs; use same projected-vector multiset for real and permuted in a pair. Verify sorted hashes and norms before CLAIM. Unlike historical R/D, DO NOT refit ridge for permuted. F pairs match trainable counts/FLOPs, A pair matches trainable counts/FLOPs, but F vs A does not: analyze F–A only as a limited interaction. Shared projector fitted to real pairs retains correspondence information, so primary comparison is not proof of pure pretraining semantics.

## 3. Huấn luyện cố định, một RUN_ID

Run ID: ttm_small4m_gemma2_causal6_2048x4096_free_t4_20261109_v1.
SIX arms x 2048 optimizer updates x 4096 effective labels per update = 8,388,608 training target exposures each, 50,331,648 across the study. Training starts from T4 step1024 for each arm, not from previously trained C/D; not 2048 total-from-scratch.

Same complete TRAIN packet schedule for every arm: 2048 windows-packets from frozen 2691 T4 TRAIN windows, sampled uniformly with replacement via NumPy default_rng(2026110914). For each step choose ordered windows until >=4096 non-ignored targets, truncate last window targets with -100. Batch micro-windows max 8; accumulate sum-cross-entropy/4096 across all microbatches; exactly one optimizer.step after all accumulated gradients. No re-shuffling or arm-specific sampling. Loss is token-weighted. No cross-story context.

Optimizer: fresh AdamW for each arm, lr=0.0001 constant, betas=(0.9,0.95), eps=1e-8, wd=0.1, global gradient clip=1.0. No warmup/decay, sweeps, early stopping, VAL selection, or T4 historical optimizer state. Set torch/model seed=2026110912. FP32, no AMP, no TF32, deterministic CUDA if supported, record software/hardware/RNG state. Donor vectors and fallback frozen. Source parity against original direct-swap C2048 runner SHA256 0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e is required before CLAIM; if any incompatible loss/schedule/model initialization is found, HOLD and resolve only before consuming science.

## 4. Data sources and new H512 holdout

Frozen source TTM step1024 SHA256 cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b, donor candidate SHA256 c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3, T4 TRAIN/VAL NPZ SHA256 184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913, pack manifest SHA256 ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650. T1 split SHA256 9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9 and BPE manifest-file SHA256 cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc.
TRAIN 2048 stories, 2691 windows, 498287 distinct TRAIN targets; VAL history 256 stories, 328 windows, 61122 targets. TinyStories-train SHA256 c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f; TinyStories-valid SHA256 94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4.

H512: exactly 512 NEW valid stories drawn without reference to model outputs from original pinned TinyStories-valid. Before CLAIM, exclude exact SHA story memberships of T1 TRAIN/VAL/TEST and consumed L0017 320 via private membership SHA256 bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47. No materializing, decoding, scoring historical TEST or reusing L0017 320 as a science dataset. Order remaining eligible unique SHA256(raw story) by SHA256(ASCII "TTM_CAUSAL6_H512_V1_20261109", NUL, lowercase hex story SHA256); take first 512, with no post-hoc replacement.

Before CLAIM, run 5-word shingle Jaccard >=0.85 near-duplicate audit within H512 and versus T1 2048 TRAIN and 256 old VALIDATION. Old 320 and 64 TEST only receive exact-hash exclusion, not new text read; residual near-duplicates with those sources and unknown donor pretraining remain possible and must be disclosed. If any defined data gate fails, HOLD; do not change selection seed after observing results. Seal private H512 membership, hashes, token-window counts and audit receipt; publish only hash/counts. New H512 is from same family TinyStories-valid, not a cross-domain independent corpus. Zero training on H512.

Old VAL256 used only for final descriptive diagnostics, never interim selection. New H512 released to scorer only once after all six final READY checkpoints, not for hyperparameter/seed selection. Entire 320 L0017 holdout consumed: never forward score, train or select on it.

## 5. Metrics and scientific decision

Score each arm once on identical new H512 sealed story/token windows. Metric L(arm)=sum over stories of NLL sums / sum over stories of target counts (token-weighted). Paired story bootstrap, 2000 draws with replacement from the 512 stories, NumPy default_rng(2026110915), same story indices for all arms; use ratio of sums per draw, two-sided percentile CI95.

PRIMARY: tau_D=L(RP-F)-L(RR-F). Positive favors real assigned donor. PASS_SCOPED_DONOR_MAPPING_ALIGNMENT only when the one-shot full six-arm run, new holdout, source, preforward checks, independent QA all PASS AND CI95 lower(tau_D)>0. With complete valid science but CI lower <=0: DONOR_MAPPING_EFFECT_NOT_ESTABLISHED (scientific FAIL in scope). No fallback to secondary or tuning.

Exploratory secondary: tau_A=[L(RP-F)-L(RR-F)]-[L(RP-A)-L(RR-A)], and tau_P=[L(RP-F)-L(RR-F)]-[L(OP-F)-L(OR-F)]. Report point estimate and paired story CI95, but no independent PASS gates, no post-hoc multiple testing claims. The six arms lack a matched trained TTM-no-donor baseline; do NOT infer absolute gain over baseline on H512 from this study. L0017 absolute checkpoint C comparison remains independent historical evidence. With only one training seed and real-fitted shared projection, primary cannot identify pure donor semantics as the unique cause.

Independent QA: validate all source SHA/checkpoint/model masks/step counts, all six new final checkpoint hashes, bound H512 story IDs/counts in private receipt, recompute NLL + paired bootstrap from private per-story loss sums WITHOUT rescore/training; no release of story text, token IDs or weights to public GitHub. Append science PASS/FAIL to lineage.md only after separate adjudication.

## 6. Free Colab T4 resource and one-shot continuation decision

ONLY approved accelerator: Google Colab FREE NVIDIA Tesla T4 GPU, 16GB board memory, ONE arm at a time, FP32, microbatch <=8 windows; no paid quota, no local CPU/XPU full training, no distributed workers, no unauthorized SSH/remote management. T4 and access ARE NOT GUARANTEED by Colab (Google official FAQ). Resource preflight before claim: actual Tesla T4 and CUDA healthy (VRAM >=15GiB), exact software/source/algorithm parity, pinned Drive mounted, >=4GiB free Drive storage for immutable checkpoint/optimizer/receipts, memory synthetic one-batch safe (<12GiB peak allocated), no prior claim/run collision. If missing, HOLD_UNEXECUTED_RESOURCE BEFORE CLAIM, never silently downscale budget.

Owner Drive evidence folder: MyDrive/TTM/ttm-small-pilot/ttm_gemma2_causal6_2048x4096_free_t4_20261109_v1. SAVE atomically and hash model+optimizer+RNG+sampler cursor+source pins at step 256,512,768,1024,1280,1536,1792,2048 per arm. Keep last completed immutable READY; continue only within same run ID from exact READY with matched software and log, no hidden rerun or branch. If lost work is known to have advanced beyond last durable READY and is not recoverable, mark HOLD_INTERRUPTED and adjudicate rather than silently replay. If first READY does not exist after a crash, NO automatic restart. No early-stop from VALIDATION.

If six arms do not all reach full READY and H512 scoring+QA is incomplete after CLAIM, result is HOLD_INTERRUPTED_OR_INCOMPLETE, NOT scientific FAIL or PASS; do not add false science lineage. No claim of guaranteed completion in one Colab session or time estimate.

## 7. Boundary and next task

This is an INTEGRATED CONTRACT LOCK and resource decision, not a science runner or GPU execution. No CLAIM created, no H512 sealed yet, no training/validation scored, no L0019 written. L0017 and L0018 preserved, main unchanged, application/GGUF backlog DEFERRED. One subsequent integrated implementation task will build source, seal H512, run source parity and resource preflight, and execute once only if all pre-claim conditions hold; no micro-permissions.

NEXT: TTM_SMALL4M_EMBEDDINGGEMMA2_CAUSAL6_SINGLE_INTEGRATED_SOURCE_H512_SEAL_AND_FREE_T4_PREFLIGHT_THEN_ONE_SHOT.
