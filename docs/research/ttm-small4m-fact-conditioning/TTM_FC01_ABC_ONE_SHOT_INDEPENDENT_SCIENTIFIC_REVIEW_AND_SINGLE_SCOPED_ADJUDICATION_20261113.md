# TTM-Small-4M FC01 — Kiểm toán hậu nghiệm độc lập và phân xử khoa học có phạm vi

**Operation:** `TTM_SMALL4M_FC01_ABC_ONE_SHOT_INDEPENDENT_BYTE_CUSTODY_PRIMARY_RECOMPUTATION_SINGLE_ADJUDICATION_NO_GPU`  
**Ngày:** 13/11/2026  
**Review mode:** Read-only, no GPU, no training rerun, no blind mapping access.  
**Reviewer:** AI independent recomputation of frozen bytes/scores; **không phải external independent human reviewer**.  
**Phán quyết duy nhất:** **`PASS_SCOPED_EXPLORATORY_FC01_NO_CONFIRMATORY_RELEASE`**.

## 1. Chứng cứ gốc trên Google Drive đã truy xuất

- Owner terminal receipt: `FC01_ABC_ONE_SHOT_TERMINAL_RECEIPT.json`, SHA-256 tính lại `67b66ee06f6821e324c678367174d110a4620200f6f9639fb3fc0ebd1d966df1` = owner đã công bố. [Drive](https://drive.google.com/file/d/1yLbk_EMuPjTY0pWgMb2FA1I8D_fH8jVs/view).
- Primary public-safe: `FC01_EVAL64_PUBLIC_SAFE_RECEIPT.json`, SHA-256 `a1a7702d0560b7e1d8b2fd4e1201b29af0d5fd7b07f2b3ebd0b266e89464b532`. [Drive](https://drive.google.com/file/d/1Km3gVAPVb07qZtVgXV1mGUHigALf6qqJ/view).
- Primary **private** `FC01_EVAL64_OWNER_PRIVATE.json` SHA-256 `3e3e6e932fafb0c72873c2277dd5ad2571e1fdafcde8f24903b14a3966f7329d`, **không đưa nội dung private lên GitHub**; [Drive private](https://drive.google.com/file/d/1PylqahM2e84beuKEkJoS83To4q9PmySC/view).
- Secondary public-safe: SHA-256 `3917d2aaa0e592a0d414d9b04ad8ad45d0630bae19e95343a5b020313d9ba6e2`, `blinded_count=96`, `rater_scores=0`, `mapping_not_published=true`.
- Đã xem tên tệp `FC01_SECONDARY_BLIND96_PRIVATE.json` và `FC01_SECONDARY_OWNER_MAPPING_PRIVATE.json` để kiểm kê nhưng **không đọc nội dung hai tệp**; giữ blind/unblind chính xác như đã đăng ký. Hash nêu trong safe receipt mới chỉ là producer-reported; không gọi independent byte verified.

## 2. Khóa thực thi và huấn luyện thực tế

GO lock SHA tính lại trực tiếp từ `FC01_OWNER_GO.json` là `8b274e3bc976e73ad25a689e8044dda2fcb98766a8d2cdd890cb08d6f582c091`; authorization `FC01_ALL_THREE_ARMS_ONE_SHOT_GO`, đúng ba arm, 256 updates/arm, seed `20261112`, T4 Free/paid $0 owner-attested.

Terminal report: `start=2026-11-13T13:59:25Z`, `end=2026-11-13T14:02:18Z`, wall `172.786s`, **768** optimizer updates mục tiêu/được ghi nhận, training không retry, `TEST_Q1Q2=SEALED`, `D1_CONFIRMATORY=HOLD`.

Tự tải lại cả ba checkpoint STEP256 (tổng ~135 MB), tính SHA-256, nạp bằng CPU `torch.load(..., weights_only=True)`, kiểm tất cả các khóa:

| Arm | STEP256 SHA-256 | AdamW states (step=256) | Runner elapsed (giây) |
|---|---|---:|---:|
| A_BASE_MLE | `259f6bc80509b966b32ae187e426e9b8429f738ccdd8268ac397214c8ce32b8b` | 52/52 | 34.895 |
| B_CF_MLE | `e58485ed4cb6b6de13707d18de9a8a4b96283f3500f892c2e9dd78777b6043b6` | 52/52 | 34.033 |
| C_CF_CONTRAST | `3a531fd2046b7bb77c32799062e62ebdef3bc6bd492d4e6be59b5b388e5aded6` | 52/52 | 59.560 |

Mỗi checkpoint có schema `ttm.fc01.frozen_resume.v1`, `step=256`, `optimizer_updates_so_far=256`, corpus SHA `becc0408880aaed8bd5eb6fdf3997e62d5131c187a48331a03ae37d41aaa1aa3`, parent SHA `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, cùng GO lock; cursor `core=3072 / candidate=1024 / synth=262144`; 53 model state entries, **không NaN/Inf** trong model hay AdamW states. Checkpoint đầy đủ **không đồng nghĩa** resume từ STEP064 đã được diễn tập; thực tế `RESUME_NOT_EXECUTED`. Runner elapsed là thời gian monotonic nội bộ, không phải GPU hardware utilization telemetry.

## 3. Tính lại primary đúng hợp đồng

**Primary** là một family đạt `success = (mA > 0) && (mB > 0)`. Đọc 64 family/arm, đối chiếu đúng cùng 64 ID giữa A/B/C; mỗi category có 16 family; tự tính 192 success flags từ hai margin và đối chiếu tất cả 192 với dữ liệu và public-safe summary: **PASS**.

| Arm | Đúng / 64 | Tỉ lệ |
|---|---:|---:|
| A — baseline single-condition MLE | 4/64 | 6.25% |
| B — counterfactual data MLE | 3/64 | 4.6875% |
| C — counterfactual contrastive | 38/64 | 59.375% |

**Chênh lệch B−A**: `-0.015625` (−1.5625 điểm phần trăm), bootstrap 10,000 mẫu phân tầng theo category `95% CI [-0.09375, +0.0625]`.  
**Chênh lệch C−B**: `+0.546875` (+54.6875 điểm phần trăm), `95% CI [+0.4375, +0.640625]`.

Tái lập đúng **100%** cả point estimates và percentile CI bằng mã Python độc lập `numpy.random.default_rng(20261113)` với bốn strata category × 16 families, 10,000 bootstrap resamples. Không đổi primary, threshold, seed, metric hay chấm lại bằng một phương pháp hậu nghiệm.

## 4. Heterogeneity phải công bố, tránh hiểu sai

| Category (16/arm) | A | B | C |
|---|---:|---:|---:|
| entity_location | 1 | 0 | **1** |
| causal_reasoning | 0 | 1 | **10** |
| rule_constraint | 0 | 0 | **16** |
| goal_persistence | 3 | 2 | **11** |

Kết luận **không đồng đều**: C tốt nhất với `rule_constraint=16/16`, nhưng `entity_location=1/16`. FC01 đo **64 family lexical holdout trên bốn template semantics chung**, không phải 64 reasoning problems hoàn toàn mới. Không tuyên bố transfer qua template mới, OOD, hoặc reasoning tổng quát.

**TinyStories VAL NLL sau STEP256**: A `3.56461566`; B `3.56488641`; C `3.56456425` trên `61,122` targets chung. Đây là mô tả phụ, **không phải** kiểm định không-thua-kém đã đăng ký.

## 5. Giới hạn độc lập, quyền và cổng khoa học

- Source B/C identical byte theo QA trước, cùng checkpoint P02/T1, seed và equal update budget; runner C bổ sung contrastive objective. Trong **phạm vi FC01**, hiệu ứng mục tiêu C−B dương mạnh theo primary đã khóa. **B−A không có bằng chứng cải thiện** (CI chứa 0).
- Chưa chấm mù `blind96`; chưa có human independent review. Bảng ánh xạ được giữ riêng, chưa mở. Do blind và mapping **đang cùng thư mục Drive owner**, reviewer tương lai **chỉ được nhận blind packet**, không được truy cập folder cha/mapping.
- Chỉ một training seed, không có repeated-seed replication. Không mở D1 confirmatory 512, TEST/Q1Q2 hoặc FC02 capacity.
- Không sửa/retrain/reseed hoặc re-evaluate ngoài phạm vi frozen primary.

## 6. Formal single scoped adjudication

- `EXECUTION_INTEGRITY=PASS_ABC_768_OF_768`
- `CHECKPOINT_SHA_BYTE_CUSTODY=PASS_3_OF_3`
- `PRIMARY_SCORE_AND_BOOTSTRAP_REPRODUCTION=PASS_EXACT`
- `OBJECTIVE_EFFECT_C_MINUS_B=PASS_POSITIVE_SCOPED_FC01`
- `DATA_EFFECT_B_MINUS_A=NOT_DEMONSTRATED`
- `GENERALIZATION_NEW_TEMPLATE=NOT_ESTABLISHED`
- `SECONDARY_BLIND96=NOT_SCORED`
- **`OVERALL=PASS_SCOPED_EXPLORATORY_FC01_NO_CONFIRMATORY_RELEASE`**
- **`NEXT_STAGE=GO_INDEPENDENT_BLIND96_SCORING_ONLY`**, no GPU, no TRAIN rerun, mapping untouched.
- `D1_CONFIRMATORY=HOLD`, `TEST_Q1Q2=SEALED`, `FC02=NOT_OPENED`, `lineage.md=UNCHANGED_PENDING_FINAL_SECONDARY_REVIEW`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_FC01_BLIND96_INDEPENDENT_AI_RATER_SCORING_FREEZE_AND_SINGLE_POSTHOC_ADJUDICATION_NO_GPU`. Cần đưa duy nhất blind96 cho một reviewer khác, không kèm mapping, score freeze và SHA trước unblind; không tự ý cấp D1.
