# TTM-Small-4M × EmbeddingGemma 2 — 64-step equal-budget adaptation preregistration

**Ngày:** 2026-11-09. **Bài thử:** `TTM_SMALL4M_EMBEDDINGGEMMA2_SHORT_EQUAL_BUDGET_ADAPTATION_DECISION`. **Trạng thái trước khi chạy:** `DESIGN_FROZEN_NOT_EXECUTED`. **Run ID:** `ttm_small4m_gemma2_equal64_adapt_cpu_20261109_v1`.

## Câu hỏi, phạm vi và đối chứng

Kiểm tra liệu chuyển giao token embedding tiền huấn luyện EmbeddingGemma 2 có cải thiện **chất lượng TTM-Small sau 64 cập nhật tối ưu** hay không, so với một mốc tied/untied và một donor-permuted control. Chỉ TRAIN hiện có, cùng mẫu ở mọi bước, chấm trên VALIDATION TinyStories đã dùng trước đó; **TEST không được đọc**, không RAG, không thay dữ liệu/tokenizer. Đánh giá chỉ mang tính **exploratory** (1 seed, VAL reused), không thể tuyên bố confirmatory hay production.

Nguồn đã được kiểm byte gốc từ Drive trước khi có kết quả:
- Checkpoint `checkpoint.pt` SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, TTM T4 step1024.
- Candidate `candidate_initialization.pt` SHA256 `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3` donor thực và adapter ridge.
- Private TRAIN+VAL pack `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz` SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; manifest SHA256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`. 2,691 TRAIN windows, 328 VAL windows, 256 VAL stories, 61,122 VAL labels. Schema excludes TEST.
- P02 source SHA256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`; swap source SHA256 `d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39`.

### Four arms (before measuring post-adaptation VAL)
- **A tied**: exact trained TTM-Small P02 step1024; train all P02 unique parameters using fresh AdamW.
- **B untied**: exact same step1024 weights, but cloned independent output head; train all P02 parameters and output head using fresh AdamW. **A=B before adaptation; A vs B may diverge during training because weight-tying changes the gradient path**.
- **C pretrained map**: exact saved 1,917 valid donor-vector rows [2048,512], frozen donor table and frozen fallback, ridge-initialized trainable [256,512] adapter; all P02 Transformer/position/head parameters trainable. No donor encoder execution.
- **D donor permutation**: permute donor rows among the same 1,917 valid IDs, fixed permutation seed `20261109`; recompute ridge 0.01 to same frozen trained input embedding table, preserving same mask and model/optimizer architecture as C. Same frozen donor lookup/gradient policy as C. No VAL used in initialization.

### Exact common training budget
- **64 AdamW steps each arm**, each with **exactly 512 valid next-token targets** (32,768 scored targets per arm). Same 64 precomputed TRAIN-only sampled windows, in same order and same truncated label budget at every step, for all arms. Sampler: NumPy `default_rng(20261109+71)`, uniform windows with replacement; truncate tail labels with `-100` to ensure exactly 512 valid labels/step. TRAIN pack and all model weights immutable originals.
- Fresh `AdamW(lr=1e-4, betas=(0.9,0.95), eps=1e-8, weight_decay=0.1)` independently for each arm; **optimizer state from the 1,024-step T4 run is not reused** (candidate has no such state). Constant LR, gradient clipping norm 1.0; loss is `cross_entropy(logits.float(), y, ignore_index=-100, reduction=sum)/512`. CPU FP32, torch 2.10.0, deterministic seeds, `eval()` during scoring; `train()` during adaptation. Source table frozen C/D; all trainable P02/control parameters updated. No hyperparameter choice after observing VAL. No validation or interim checkpoint selection during 64 steps.
- Raw result includes per-step TRAIN loss, all arms' final VAL NLL, per-story sums, all 4 arms' target counts, unchanged source SHA, actual CPU seconds and number of steps. No failed arm or partial budget can be called a complete comparison.

### Analysis rules fixed before outcomes
- Score exact **same 328 VALIDATION windows, 61,122 unmasked labels / 256 stories**, using `F.cross_entropy(logits.float(), targets, ignore_index=-100)`, token-weighted aggregate NLL. Compute paired story-bootstrap (1000 resamples with replacement, seed `20261109`) for **A−C**, **B−C**, **D−C**. Positive difference means second arm better.
- Main descriptive success criterion: `CI95_lower(A−C)>0`, `CI95_lower(B−C)>0` **and** `CI95_lower(D−C)>0`, all after adaptation. Report mixed/negative outcomes without relabeling thresholds.
- Secondary comparisons: all pairwise NLL; compare against known frozen prior VAL NLL (A/B 3.52233885, C 4.34809627, D 6.44382563) only descriptively, **not** use as early-stop or checkpoint selection. Larger loss decrease from worse starting point is not an automatic claim of better transfer.
- If model quality C is worse or fails main criterion, verdict `ADAPTED_TRANSFER_BENEFIT_NOT_ESTABLISHED` within this fixed 64-step pilot. If all three lower bounds positive, verdict `ADAPTED_TRANSFER_POSITIVE_EXPLORATORY`. One-seed reused-VAL result cannot establish causal contribution of pretrained semantics; D addresses vector-to-token assignment but also differs in ridge alignment geometry.

### Governance
One owner-authorized training experiment, not four separate permits; **source+prereg frozen before CLAIM and any optimizer step**. No rerun/auto-retry of consumed ID. Private TRAIN/VAL arrays and per-story records remain private (not in public GitHub); public GitHub receives only aggregate verdict, exact hashes, QA and append-only scientific entry `lineage.md` after independent adjudication. Never overwrite step1024 checkpoint, donor-candidate, prior one-shot, T5 artifacts, PR #12, main or D1 G4 deferred results.

**Bước thực hiện tiếp theo sau chạy:** receipt QA against frozen data, per-story recomputation and formal PASS/FAIL in scope; only then decide whether additional training or further architecture revision is warranted.
