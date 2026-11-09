# TTM-Small-4M × EmbeddingGemma 2 — equal-budget 64-step CPU adaptation scientific adjudication

**Ngày:** 2026-11-09. **Kết quả khoa học thăm dò:** `ADAPTED_TRANSFER_BENEFIT_NOT_ESTABLISHED` (âm tính theo tiêu chí đã khóa). **QA độc lập trên nguyên checkpoint, mô hình tính lại NLL:** `PASS_61_OF_61`. Không sử dụng GPU, TEST, RAG hay chỉnh checkpoint T4 gốc. Không tự mở huấn luyện tiếp.

## 1. Phạm vi tiền đăng ký trước kết quả

- [Preregistration](TTM_SMALL4M_EMBEDDINGGEMMA2_SHORT_64_STEP_EQUAL_BUDGET_ADAPTATION_PREREG_20261109.md) commit `efdc8fa8a3b71fa9e05b26821c22d39f88c3e22f`, ghi **trước CLAIM và bước tối ưu đầu**.
- [Source lock trước chạy](TTM_SMALL4M_GEMMA2_ADAPT64_SOURCE_PIN_20261109.md) commit `9520e754262b98722683416e1b2a00c4df0e33ce`; nguồn Python SHA256 `e423daccc678d893947f93c13b2e8a12c8dca3a4875c5546f3a80131cd0d61ca` và gói nguồn SHA256 `0db4efe16aa2dc68811e029b5d74d7baa6bc615802ea94d0e4b9f49f33f2cadf`, lưu tại [Drive riêng tư](https://drive.google.com/file/d/182Q3r71f6965mojeO-VhaRR5DL0O9Pfz/view).
- RUN_ID duy nhất `ttm_small4m_gemma2_equal64_adapt_cpu_20261109_v1`, nguồn TTM step1024 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, EmbeddingGemma2-mapped candidate `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`, pack TRAIN+VAL `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913` (không chứa TEST).
- A: checkpoint TTM gốc tied; B: head untied; C: pretrained donor-token mapping 512→256 ridge; D: donor vector permutation đúng 1.917 valid IDs với cùng mặt nạ/fallback, refit ridge0.01. Đối chứng B khác A sau huấn luyện là hợp lệ vì untie biến đổi đường gradient, mặc dù logits A=B trước thích nghi.
- **Đúng 64 AdamW optimizer steps × 512 valid targets mỗi bước = 32.768 target exposures mỗi arm**, tất cả dùng **cùng lịch mẫu TRAIN**, NumPy seed `20261109+71`, schedule SHA256 `f16682b8b9cc2506753296719c8bc124103ef6a65e5fbcf98876bd8476aa82a6`; LR=1e-4 hằng, betas(.9,.95), eps1e-8, wd0.1, clip1, fresh optimizer mỗi arm, CPU FP32. Đây là ngân sách **bước/tokens như nhau**, không phải đồng nhất FLOPs do kích thước adapter C/D lớn hơn.
- VAL **328 windows / 256 stories / 61.122 target labels**, cùng phép NLL như T4, chấm sau 64 bước, không chọn checkpoint theo VAL, paired bootstrap 1000 lần seed 20261109 theo truyện. Nguồn VAL này đã dùng cho T4 trước đây nên kết quả chỉ thăm dò, không dùng từ “confirmatory”.

## 2. Kết quả thực tế (lower NLL is better)

| Arm | Frozen NLL prior (step0) | After 64 training steps NLL | Difference after − before |
|---|---:|---:|---:|
| **A** tied original | 3.5223388517 | **3.6203496575** | +0.0980108058 (worse) |
| **B** untied control | 3.5223388517 | **3.6190452345** | +0.0967063828 (worse) |
| **C** actual EmbeddingGemma2 mapped | 4.3480962661 | **3.9190499451** | −0.4290463210 (better than own start) |
| **D** permuted donor | 6.4438256258 | **4.2870530828** | −2.1567725430 (better than own start) |

**After 64-step paired story-bootstrap CI95%, 1000 resamples:**

| Difference (positive = right-hand model better) | Mean gap | 95% CI | Prespecified comparison |
|---|---:|---:|---|
| A−C | **−0.2987002876** | **[−0.3099962949, −0.2886758762]** | C does not beat A |
| B−C | **−0.3000047106** | **[−0.3115587235, −0.2899196944]** | C does not beat B |
| D−C | **+0.3680031377** | **[+0.3559535590, +0.3803695708]** | C beats permuted D |

Main preregistered descriptive success required lower CI >0 for **all 3** comparisons A−C, B−C, D−C. **Only D−C passes.** Verdict: **`ADAPTED_TRANSFER_BENEFIT_NOT_ESTABLISHED`**. C improved vs its own start, and gap C−A reduced from +0.825757 to +0.298700 nats/token, but C remains significantly worse. D's large improvement arises partly from its much worse initial NLL and must not be misinterpreted as learning faster than C.

- TRAIN step1 loss A/B `3.3475875854`, C `4.2446894646`, D `6.4221253395`. TRAIN step64 A `3.2879831791`, B `3.2902469636`, C `3.7334232330`, D `4.1649427414`.
- All four arms complete 64 steps, all training losses finite. Sum logged CPU adaptation seconds **44.7883** across arms (excludes model scoring and auxiliary I/O). No GPU used; historical TTM step1024 was **not rerun**.
- Four new final model checkpoints are preserved separately; no overwrite of original step1024 or original Gemma candidate.

## 3. Source, immutable evidence and independent QA

- **Private Drive evidence directory:** https://drive.google.com/drive/folders/1bcZ_2PNUi6jMoDgYhK2vHmZG9THfcTDg .
- [Private receipts + per-story sums + code + console archive](https://drive.google.com/file/d/1bnrUq2Ty5zhbGvPo0GC94OkEeGf5OZdy/view): **25,632 bytes**, SHA256 `8b6051d3299fbaad43518ea53c829885e9a750298a09f1b8be04c5113eb0f963`.
- [Private new 4 adapted model checkpoints](https://drive.google.com/file/d/1IB_hMlnmxNR-OVSXhsP196-H0WJhvHAE/view): **68,510,251 bytes** compressed, SHA256 `115c438f2cc1f3b3c3464b40e3eb87402d38a2c514a5edc178671e2e851927e8`.
- Original CLAIM SHA256 `fa9c2dce53eba66129c1d93368c257848eadc613877e8062f2fcd2a698bb93e8`; original RESULT SHA256 `8d31f890c84a56c4f1a58293eaa2dee9d8ded3e7720599f5b6407f482f83d703`; private per-story loss sums SHA256 `098150722f43b57c3146421cfab05b09d51399f201e889bde377e0efa619bc94`; independent QA SHA256 `6634aefb7917c792ff8398be84df0b7c5b2b8df49befda2b5bae77ff380a6405`.
- Trained checkpoint SHA256 A `a958966ab5c57be3efc817d581aa2415053c1c9679b46b5cd3fc145c0d016f75`; B `b8ffcf6fc2836050960ffc1a7b3fd76aff52a3b0a751c45bbe14c0a9f0829783`; C `b51662b510c208acbe27557a866c6b874d35516caeffc8281bb445f62a466243`; D `0291072058df82678457eee022bdf9473132678db745676dcc0e1fbdd9064cd4`. Private weights **not** committed publicly.
- **Independent CPU QA 61/61 PASS**: exact source / original / new checkpoint SHA linkage; four independent model reloads from final serialized weights and complete 256-story VAL numerical replay (not just recalculating aggregate metrics); recompute all NLLs and paired story-bootstrap CIs; verify training budget and absence TEST keys. This does **not** independently replicate 64 optimizer-step trajectories from scratch, and does **not** constitute human external peer review.

## 4. Scientific adjudication and no further execution authorized

**Completed with negative answer in current scope:** a 64-step equal-sample adaptation with this ridge-based, Gemma-derived token embedding **did not outperform the original TTM-Small-4M**; its remaining 0.299 nats/token gap is not a rounding or measurement issue. C better than D is useful evidence of nonrandom token assignment under this control, **not** proof that pretrained semantics caused improvement. Since A/B worsen compared with their own frozen checkpoint, one uniform learning rate/optimizer may not be an optimal stable schedule for previously trained P02; this is a limitation, not grounds to change any parameter posthoc.

This result does **not** falsify all EmbeddingGemma transfer options (residual blend, distillation, partial freeze, other tokenizer alignment), and does not prove improvement after longer training. But **do not launch 128/256/1024 more steps or alter the adapter based on the same VAL in this experiment**.

**Next recommended science-governance decision:** `TTM_SMALL4M_EMBEDDINGGEMMA2_MECHANISM_REVIEW_AND_STOP_GO_DESIGN_ONLY` — finite read-only decision whether to stop this naive direct-swap line, or preregister one materially distinct causal mechanism (e.g., residual/gated donor initialization) under a *separate* justified hypothesis and budget. Keep TTM-Small T5 main priority and D1 G4 RAG deferred. Historical T4 H1 PASS and T4 TEST results remain intact.

**Final:** `ADAPT64=COMPLETED_ONCE` · `EQUAL_STEP_LABEL_BUDGET=PASS` · `INDEPENDENT_QA=PASS_61/61` · `SCOPED_BENEFIT=NOT_ESTABLISHED` · `TEST=SEALED_FOR_THIS_STUDY` · `GPU_USED=NO` · `TRAINING_SUCCESSOR=NOT_AUTHORIZED`.
