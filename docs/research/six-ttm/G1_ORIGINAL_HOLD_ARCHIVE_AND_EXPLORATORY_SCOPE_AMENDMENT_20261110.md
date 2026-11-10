# TTM × SIX — G1 original HOLD archive & independent exploratory public-prompt protocol

**Ngày:** 2026-11-10  
**Decision:** `G1_ORIGINAL=FEASIBILITY_HOLD_ARCHIVED_FOR_CURRENT_RESOURCES` · `G1_SCIENCE_LOCK=HOLD`. No resources provisioned, TEST not opened, original Git source not modified. The original G1 can be reconsidered only on *new actual evidence* of an independent witness and protected Colab TEST boundary.

## A. Không sửa hợp đồng gốc

- **Original G1**: Qwen3-0.6B→Qwen3-1.7B hidden-state functional transfer; 128 TRAIN, 64 DEV, 64 private TEST from the sealed TTM pilot TRAIN lineage; 8 probes, 1000/1000 permutations, 2000 bootstrap and one-shot TEST. Frozen research commit `d5d0c5346a595557a76349f900d09be50bce289c` and G1 original SHA manifest `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6`. All held on original science gate, science authorization not issued.
- The prior technical provision plan `5ef0a7467600ea4cea75508529c4c43bd9953b51` remains an archived scoped approval, not a successful Phase A/Phase B.
- Do not append technical/feasibility HOLD to `lineage.md` (research scientific PASS/FAIL only). No merge to `main`, no PR #12 change or checkpoint edits. Original G1 results do not exist.

## B. Separate exploratory contract, effective only for authorized public fictional prompts

**Experiment ID:** `TTM_SIX_G1_EXPLORE_AUTHORED_PUBLIC_QWEN_DEV_V1`. **Scope:** `REAL_MODEL_EXPLORATORY / NO_G1_PRIVATE_DATA / NO_TEST / NOT_G1_CONFIRMATORY`.

The owner requested an early real-model exploratory experiment. This contract authorizes *no* private TinyStories, no reads of G1 TEST/TTM pilot VAL/TEST and no science one-shot. It uses only 16 invented fictional situations (names, place, time, event), four templates each: **64 distinct prompts**. Split 12 entire situations (48 prompts) TRAIN, four unseen entire situations (16 prompts) DEV by SHA-sorted group ID, with exact prompt SHA uniqueness. There is **no TEST split**; no use of original G1 manifest, source sample IDs or previously consumed TEST data.

### Model/model budget

- Two genuine frozen Qwen3 models, not simulation: `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca` and `Qwen/Qwen3-1.7B@70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.
- Original G1 weight SHA-256 expected and checked from downloaded file bytes *before* model load. Run on an interactive **Colab Free Tesla T4 if actually allocated**, sequentially load 0.6B then 1.7B, `eval()`, `inference_mode()`, `hidden_states[28]` last token, with separate tokenization and no generation/chat template.
- For speed, score **two predeclared pairs**, taken from the original eight and now explicitly a new exploratory design: `Everyone felt safe/afraid`, `story ended happily/sadly`, each as a continuation measured by per UTF-8-byte normalized conditional log-likelihood. This change is **not** an amendment to the original G1 confirmatory contract.
- Only TRAIN/DEV metrics: ridge alpha=10, A→P hidden alignment to target functional probe, direct source→probe, TRAIN-mean, group-shuffled target-hidden negative control (32 permutations preserving 4-row groups); group-mean CKA on four DEV groups **descriptive only**, no p-value or power claim. The two estimators are *not information-budget-equivalent*; no inference of SIX superiority.
- One screening run, group split seed 20261110. STOP if no T4, model-weight SHA mismatch, CUDA peak reserved >12 GiB, wall budget >1800 s, any prompt/split mismatch. No training of teacher/student weights, no TEST metric. No guarantee of T4 availability or completion time.
- No Google Drive mount, no cloud TEST staging, no API secrets or personal material. Save compact `.npz` features, JSON results and SHA receipt only under `/content/g1_explore_public_qwen_dev_v1`; user explicitly downloads ZIP at the end. Colab session interruption can invalidate ephemeral files; no hidden background run.

### Interpretation & gates

`EXPLORATORY_SIGNAL` may be reported when A→P DEV MAE < TRAIN-mean DEV MAE and better than median group-shuffle negative; if it fails, `EXPLORATORY_NO_SIGNAL`. Either way, always report B-direct and 4-group sample limitations. These are **descriptive screening rules**, not formal significance. One seed/4 groups are inadequate for effect claims. No `PASS_G1`, `FAIL_G1`, publication or transfer benefit to TTM. If runtime fails or artifact incomplete: `TECHNICAL_STOP / NO_RESULT`.

**Author-only offline QA:** dataset/group split, zero TEST, deterministic metrics and numeric finite checks. Actual real-model result remains `NOT_EXECUTED` until user runs the Colab notebook and submits receipt.

## C. Deliverables and next step

Self-contained offline-QA + Colab notebook `.ipynb` (downloadable) and exact Python source `.py` are generated separately. These artifacts should be pinned with SHA in a new exploratory branch, **never** on original frozen G1 or main. A different reviewer may inspect the completed numeric receipt, but no repeat of original G1 infra QA required.

**Bước thực hiện tiếp theo:** run one real Qwen exploratory notebook on Free T4 (if present), collect `result.json`, exact code/manifest/model hashes and DEV A→P / direct / shuffle metrics, evaluate a finite `EXPLORATORY_SIGNAL / EXPLORATORY_NO_SIGNAL / TECHNICAL_STOP` decision, then decide whether to redesign a distinct confirmatory experiment. Original G1 remains HOLD.
