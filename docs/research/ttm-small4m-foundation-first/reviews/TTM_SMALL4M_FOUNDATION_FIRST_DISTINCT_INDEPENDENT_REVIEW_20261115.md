# TTM-Small-4M Foundation First — Distinct Independent Source, Evidence & Design Review

**Ngày kiểm toán:** 2026-11-15  
**Operation:** `TTM_SMALL4M_FOUNDATION_FIRST_DISTINCT_INDEPENDENT_SOURCE_EVIDENCE_AND_DESIGN_REVIEW_SINGLE_GATE`  
**Reviewer role:** Independent AI Scientific & Source Reviewer (không phải chứng nhận của human reviewer)  
**Mode:** `READ_ONLY · SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE_EXECUTION`  
**Repository:** [minhtri22/TokenToModel-Lab](https://github.com/minhtri22/TokenToModel-Lab)  
**Baseline commit:** `fbe4a1ed58eef66f896bbfe0471926b7cc45298e`  
**Exact candidate commit:** `4c97f2b1d1836b31d55b649e78a8b69fecc44482`  
**Kết luận DUY NHẤT:** **`HOLD_REVISE_DESIGN`**

> Không có phát hiện mã nguồn bị thay đổi hay đổi kết quả khoa học. HOLD phát sinh từ lỗ hổng thực chất trong **logic thiết kế phân biệt H-MEAS** và cách diễn giải chỉ số A/C tại F2. Đây là phán quyết *thiết kế*, không phải FAIL Small-4M, không phải lệnh đào tạo.

## A. Nguồn đọc và tính toàn vẹn

### A1. Bốn tài liệu candidate — exact pins

| Tài liệu | Git blob SHA-1 đã giao và đọc lại | Đối chiếu |
|---|---|---|
| [01_SMALL4M_ARCHITECTURE_COMPONENT_SPEC_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/01_SMALL4M_ARCHITECTURE_COMPONENT_SPEC_20261115.md) | `22e823b0a9069f07a6d6912b6425762528e2f655` | MATCH — connector-reported |
| [02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md) | `834200abc5a55791c42f27224b8296f70243edb6` | MATCH — connector-reported |
| [03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md) | `4b1c5dea92f900d93adfa5747db0ccb6b8b10eaa` | MATCH — connector-reported |
| [04_SMALL4M_SCOPE_ISOLATION_DECISION_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/04_SMALL4M_SCOPE_ISOLATION_DECISION_20261115.md) | `4c3f3c000096dfe31d05e1fb2765e180276ddc76` | MATCH — connector-reported |

Đọc bằng GitHub connector `fetch_file(path,ref=candidate)`. SHA trên là **Git blob SHA-1 do API GitHub trả về**, đối chiếu với handoff, **không phải SHA-256**. Không có phép kiểm SHA-256 trên nguyên byte qua một binary transport độc lập trong lượt này; không suy rằng private weights/data đã được chứng thực.

### A2. Source tại baseline

| Source | Git blob SHA-1 GitHub trả về | Kết quả |
|---|---|---|
| [`src/p02/transformer_core.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/src/p02/transformer_core.py) | `9762343e06cf800b50574c2871ae1ed58537fb18` | MATCH — pinned source |
| [`tools/pilot_t4/integrated/t4_capacity_smoke.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/tools/pilot_t4/integrated/t4_capacity_smoke.py) | `c9a6f256ba975228683ee7de2a1090e649110e97` | MATCH — pinned source |
| [`tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py) | `76c4d0155cd0736919f41682f240b47ad3d7c428` | MATCH — pinned source |
| [`tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py) | `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6` | MATCH — pinned source |
| [`tools/pilot_t4/integrated/t1_source_split_tokenizer.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/tools/pilot_t4/integrated/t1_source_split_tokenizer.py) | `3ef500ddd8259153e7e3d4602915a51b7060a40f` | MATCH — pinned source |

Đã trực tiếp đọc nội dung implementation, không dựa riêng vào bốn tài liệu của tác giả. Baseline và candidate commit đều tồn tại theo commit readback. Cấu hình `P02Config` mặc định **không phải** config trained T4.

### A3. Báo cáo khoa học và prospective protocol gốc

| Study | Nguồn GitHub ở commit cố định | Git blob SHA-1 |
|---|---|---|
| T4 VAL | [`c1a471087ae3…`](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md) | `c1a471087ae30f31a696fbf786230eff3773a0d1` |
| T4 TEST64 | [`cf2bcb1c48d1…`](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md) | `cf2bcb1c48d172afacb6b1f7406320851bfcbf65` |
| FRESH12 | [`1862a39ed54c…`](https://github.com/minhtri22/TokenToModel-Lab/blob/72cbf73c3adb78f9d4111f702de71fa10f713533/docs/pilot/ttm-small4m-source-of-truth/TTM_FRESH12_OWNER_CONTROLLED_UNBLIND_AND_SCOPED_QUALITY_ADJUDICATION_20261110.md) | `1862a39ed54cdc80c39213b615a3f7c4a4526d65` |
| FRESH16 | [`ae8ded5bb03a…`](https://github.com/minhtri22/TokenToModel-Lab/blob/0ec28d44587fde9ad4acba8cccae65648e367181/docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCIENTIFIC_ADJUDICATION_20261111.md) | `ae8ded5bb03a595f9af4f333ef96271ed3991d7d` |
| CF1 DEV36 | [`d6a094b2a9d0…`](https://github.com/minhtri22/TokenToModel-Lab/blob/d725c39094a5a584fd76386145db21ca6dc5eaf6/docs/research/TTM_CF1_DEV36_ONE_SHOT_INDEPENDENT_SCORE_READBACK_AND_SCIENCE_ADJUDICATION_20261111.md) | `d6a094b2a9d0977728d5d2f13c7c945d7cb8ee96` |
| D1 EXP32 | [`f53da235027b…`](https://github.com/minhtri22/TokenToModel-Lab/blob/0ec28d44587fde9ad4acba8cccae65648e367181/docs/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_EXP32_TERMINAL_EXPLORATORY_CLOSEOUT_AND_NEXT_RESEARCH_DIRECTION_20261112.md) | `f53da235027be331682bf1a5b86b0d1e94cd5373` |
| A/C FINAL24 | [`1af1b6d3743f…`](https://github.com/minhtri22/TokenToModel-Lab/blob/37165ce6eea0bb4b04d316e2998da579c91d13cf/docs/research/TTM_AC_FINAL24_INDEPENDENT_QA_AND_FORMAL_ADJUDICATION_20261112.md) | `1af1b6d3743f5e986edcc3ef1e737b0f05188d3c` |
| H-DATA-S1 | [`9cfb02e86c38…`](https://github.com/minhtri22/TokenToModel-Lab/blob/ef4cc05037f98129082cd429a75092b8cc822efb/docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_FINAL24_OWNER_UNBLIND_FORMAL_ADJUDICATION_20261114.md) | `9cfb02e86c3893b2f927b1529c637bba797f40ae` |
| FC01 | [`0a425cbadfaf…`](https://github.com/minhtri22/TokenToModel-Lab/blob/b5dd5890b73a29744530ed3a1ffbc0dc7ae5195a/docs/research/ttm-small4m-fact-conditioning/TTM_FC01_ABC_ONE_SHOT_INDEPENDENT_SCIENTIFIC_REVIEW_AND_SINGLE_SCOPED_ADJUDICATION_20261113.md) | `0a425cbadfaf644a117693fce1c9b80b069185a7` |
| D1 R1 | [`43fa3aed1a80…`](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/research/ttm-small4m-fact-conditioning/TTM_D1_R1_INDEPENDENT_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_REVIEW_20261114.md) | `43fa3aed1a802dde05511cf76afba6737eb47aa3` |
| MD1 | [`384d077600ed…`](https://github.com/minhtri22/TokenToModel-Lab/blob/33021a421f05bb3bfa0999ad12bc3bd144366da9/docs/research/ttm-hdata-fail4-md1/TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md) | `384d077600ed864a917fdd5e74b5a5bca0ed8766` |

Hai nguồn quản trị thêm: [`lineage.md`](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/lineage.md) (Git blob `fa8d0f520bf64f89e32954b2f71d2ed5f017ea15`); [global lineage/branch matrix](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/governance/TTM_GLOBAL_LINEAGE_MERGE_AUDIT_AND_RESEARCH_DIRECTION_MATRIX_20261114.md) (Git blob `d10c44605c66ec51e7e22eea0895ad37b662089`). Đây là readback các **báo cáo/nguồn công khai**, không phải đọc trực tiếp tất cả raw scores và raw private checkpoint.

### A4. Diff readback (GitHub compare exact SHA)

- `base=fbe4a1ed58eef66f896bbfe0471926b7cc45298e`
- `candidate=4c97f2b1d1836b31d55b649e78a8b69fecc44482`
- Compare status `ahead`; `ahead_by=4`, `behind_by=0`, `total_commits=4`, merge base trùng baseline.
- Đúng **4 added Markdown** tại `docs/research/ttm-small4m-foundation-first/`, tổng 252 dòng thêm; **0 modified**, **0 deleted**.
- Không đổi `lineage.md`, source/trainer, tokenizer, checkpoint, dataset hay archived evidence **trong diff giữa đúng hai commit này**. Đối chiếu diff không đại diện cho trạng thái working tree trên Windows hay HEAD di động của nhánh.

**Git integrity conclusion:** `PASS_SCOPED_EXACT_GITHUB_COMPARE`.

## B. F0 — Architecture & Component Specification

| Hạng mục | Đối chiếu mã nguồn | Phán quyết |
|---|---|---|
| Kiến trúc | Decoder-only GPT/Transformer, 4 pre-LN residual blocks, causal attention full mask | PASS |
| Vocabulary | 2048; byte-level pretokenized BPE, EOS ID 256, 1791 merges | PASS source |
| Context / d_model | 256 / 256 trong `CONFIG` T4; P02 defaults context=64, d=64, layers=2 | PASS |
| Attention | 4 heads × 64 chiều, QKV projection và output projection | PASS |
| Position | Learned absolute positional embedding | PASS |
| MLP | Linear 256→1024→256, GELU | PASS |
| Normalization | 2 LayerNorm mỗi block + final LayerNorm; RMSNorm chỉ là tùy chọn source, T4 không chọn | PASS |
| Output | `head.weight = tok.weight`, no bias; 2048 logits | PASS |
| Objective | Next-token cross-entropy; T4 masked targets `ignore_index=-100` (4096 valid labels/step) | PASS |
| T4 optimizer | AdamW `(lr=3e-4, betas=(0.9,0.95), eps=1e-8, wd=0.1)`, warmup 32 + cosine, 1024 optimizer steps | PASS source |
| Nghiên cứu khác | Không phát hiện RoPE/GQA/MoE trong P02 core/T4 CONFIG | PASS scoped |
| Checkpoint T4 private | Chỉ prior reported SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` | **NOT_REVERIFIED** |

**Đếm tham số tĩnh (unique):**

- Token embedding: `2048×256 = 524,288`.
- Position embedding: `256×256 = 65,536`.
- QKV+attention projection/block: `(256×768+768)+(256×256+256) = 263,168`.
- FFN/block: `(256×1024+1024)+(1024×256+256) = 525,568`.
- Hai LayerNorm/block: `2×(256+256) = 1,024`.
- Mỗi block `789,760`; bốn block `3,159,040`; final LayerNorm `512`.
- Tổng = **`3,749,376`**. Tied output head không tính lần hai.

**F0 verdict:** `PASS_SOURCE_SCOPED`; không cấp quyền khoa học hoặc xác minh rằng mô hình suy luận nhân quả.

## C. F1 — Evidence & Failure Matrix (15 groups / 8 hypotheses)

| Study | Dữ kiện từ báo cáo gốc | Phạm vi phán quyết |
|---|---|---|
| T4 VAL H1 | NLL model 3.5223388517, bigram 3.9972314170, lợi thế 11.880537% | `PASS_H1_CONFIRMATORY_VAL_SCOPE` (1 seed, 256 VAL) |
| T4 sealed TEST64 | Model 3.4835910733, bigram 3.9736037453, 12.331694%; 14,669 labels | `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED`; consumed, không per-token recompute lần này |
| FRESH12 | Adherence mean baseline=trim=0.291667, Δ=0; 35/48 đầu ra grade 0 | No demonstrated serialization rescue scoped |
| FRESH16 V2 | H1 0/16 (threshold 12/16), H2 0/8 (threshold 6/8) | `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED`; source/tally QA PASS riêng |
| CF1 DEV36 | Hai ngữ cảnh đúng 0/36, A 1/36, B 35/36, preference switch 0/36 | Failure scoped; evaluator có label/position confounds |
| D1 EXP32 | Greedy 0/32 và nucleus 0/32 grade≥2; teacher-forced S=1/16 | Exploratory, rater-input byte provenance **NOT_VERIFIED** |
| A/C FINAL24 | A và C **đều adherence mean 0.6667**; C−A=0; strict C wins 1/24 | `FAIL_CANDIDATE_EFFICACY_GATE_NO_DEMONSTRATED_C_GAIN` |
| H-DATA-S1 FINAL24 | 48 continuations, actor/object/goal đều 0 ở cả H0/H1; Δ=0, wins=0/24 | `H_DATA_S1_NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT` |
| FC01 exploratory | A=4/64, B=3/64, C=38/64; C entity_location chỉ 1/16 | `PASS_SCOPED_EXPLORATORY_FC01_NO_CONFIRMATORY_RELEASE`; không chứng minh OOD/new-template |
| D1 Bridge R1 | 330 constructive cases khảo sát có giới hạn, 0 admitted OOD; construct validity chưa đạt | `GO_CLOSE_R1_FORMULATION_DESIGN_ONLY`, science `HOLD` |
| Infra/rights/checkpoints | T5/T6 QA có phạm vi; Q1Q2 chưa hoàn thành; private bytes không reverified | Không nâng thành scientific PASS |

Các nghiên cứu kỹ thuật, tốc độ, byte/score arithmetic và parity không được chuyển thành năng lực sinh ngữ nghĩa. Không gán FAIL nghiên cứu thành chứng minh capacity/attention/data/objective riêng lẻ vô dụng.

Kiểm **15 hàng evidence** `SM-E01..SM-E15` và **8 giả thuyết** `H-MEAS`, `H-COND`, `H-DATA`, `H-OBJ`, `H-DEC`, `H-CONTEXT/ATTENTION`, `H-CAP`, `H-TOOL`: sự phân biệt quan sát/giả thuyết nhìn chung phù hợp, ngoại trừ findings F02/F03 về cách dùng đơn vị và hiệu số.

**F1 verdict:** `PASS_WITH_REMEDIATION`; `ROOT_CAUSE_IDENTIFIED=NO`.

## D. F2 — Causal-discrimination design (M0)

Đối chiếu trực tiếp MD1: 32 lõi đối chứng mới (4 strata×8), 64 continuations (32 positive/32 negative), hai raters độc lập; **mỗi rater/trục sensitivity ≥28/32 và specificity ≥28/32**; giữa hai raters **agreement ≥0.85 trên mỗi trục**. Giữ nguyên mọi ngưỡng: **không sửa prospective threshold**.

**M0 đo được điều gì:** khả năng phân biệt cực tính đúng/sai *rõ ràng* theo gold được soạn, trên các ví dụ calibration. Đây là precondition hữu ích.

**M0 chưa đo được điều gì:** (a) độ nhạy riêng actor vs object vs goal vì ba trục đổi đồng thời; (b) khả năng phân biệt lỗi vi tế, đáp án hỗn hợp, continuation mơ hồ/thiếu dữ kiện; (c) sự tương đương human gold; (d) lỗi evaluator trong đúng phân phối văn bản Small-4M bị đánh 0; (e) model so với evaluator là nguyên nhân độc nhất. Thêm agreement ≥0.85 không làm hai raters dùng cùng shortcut trở nên đúng.

**F2 reviewer conclusion:** `HOLD_M0_DISCRIMINATOR_DESIGN` cho đến khi diễn giải và đối chứng anti-shortcut được chốt về mặt *thiết kế* bằng một prospective amendment được owner duyệt. M0 FAIL → `HOLD_MEASUREMENT`, không train. M0 PASS sau remediation cũng chỉ là `CALIBRATION_SCOPED_PASS`, không là blanket validity hoặc science GO. Không mở M1/M2/M3 hay tận dụng lại TEST/FINAL cũ.

### Thứ tự F0 → F4

| Phase | Đánh giá độc lập |
|---|---|
| **SM4M-F0** | Source specification đủ cơ sở `PASS_SOURCE_SCOPED` |
| **SM4M-F1** | Evidence mapping đúng phần lớn; remediation F02/F03 |
| **SM4M-F2** | Thiết kế M0 cần sửa substantive; **DESIGN_ONLY; NOT_EXECUTED** |
| **SM4M-F3** | **NOT_OPENED**; chỉ một thành phần được phép xem xét về tương lai, không tối ưu đồng thời |
| **SM4M-F4** | **NOT_OPENED**, chưa có quyền adjudication khoa học mới |

## E. Scope isolation

Đã đọc `04_SCOPE_ISOLATION`, `lineage.md` main và global 64-branch inventory. Isolation về mặt **nội dung bốn tài liệu: PASS**:

- EmbeddingGemma 2 và Vector Memory giữ **INDEPENDENT**; kết quả cũ bảo toàn; không thêm donor, adapter, retriever, Reader vào T4 core.
- MoE, scaling, SIX–TTM, R3/O1, P07/P08, kiến trúc mới không tự mở.
- `PAUSE ≠ FAIL` và `UNVERIFIED_CURRENT_GATE` không đổi thành PASS/FAIL.
- Không merge nhánh hoặc hồi tố sửa `lineage.md` trong candidate diff.
- Đây là xác minh phạm vi **tài liệu tại commit candidate**, không chứng nhận toàn bộ status live của mọi nhánh.

**Scope verdict:** `PASS_SOURCE_SCOPED`.

## F. Finding matrix — mọi finding phải có tám trường

| ID | Severity | Discrepancy | Required remediation |
|---|---|---|---|
| SM4M-IR-F01 | **HIGH** | Ba nhãn trục biến đổi đồng thời. Rater dùng một shortcut nhận biết 'positive/negative' tổng thể vẫn có thể vượt cả ba ngưỡng; không kiểm riêng sự nhạy với mỗi trục, trường hợp đúng một phần hoặc đầu ra tự nhiên mơ hồ. Agreement không khắc phục shortcut chung. | Sửa cách diễn giải F2 và hợp đồng thiết kế: M0 chỉ chứng nhận độ phân biệt trên đối chứng cực tính rõ; ghi điều kiện kiểm tra gold độc lập, anti-shortcut và kiểm soát riêng trục bằng prospective amendment trước khi cân nhắc thực thi. Không tạo dữ liệu trong review, không đổi 28/32 hay 0.85. |
| SM4M-IR-F02 | **HIGH** | Đồng nhất hiệu số hai arm bằng 0 với các điểm tuyệt đối ở sàn 0. Hai chỉ báo thống kê khác bản chất, trên protocol/rater/task khác nhau. | Chỉnh lập luận roadmap: A/C cho NO_INCREMENTAL_GAIN (không phải all-zero absolute); H-DATA-S1 mới là all-zero absolute; không pooling các thước đo khác protocol. Giữ nguyên mọi số/score/thresh gốc và ưu tiên P0 có tính điều kiện. |
| SM4M-IR-F03 | **MEDIUM** | '48/48 axes' dùng mẫu số của continuation làm số trục; không rõ 48 đoạn hay 144 giá trị trục. | Đổi cách viết thành '48/48 continuations có cả ba trục bằng 0 (144 axis-level scores)', sau khi đối chiếu đúng frozen receipt; tuyệt đối không sửa score lịch sử. |
| SM4M-IR-F04 | **MEDIUM** | Các ngưỡng có nhưng quy tắc chấm máy và quy trình custody trước khi thực thi còn thiếu chi tiết có thể kiểm toán; tài liệu F2 không đánh dấu explicit PREEXEC BLOCK cho các chi tiết này. | Trước bất kỳ owner decision về M0 execution, khóa contract tính mẫu số, per-axis confusion matrices, cùng 64 items, anonymization, inter-rater scheme, invalid handling, gold provenance/rights/PII và independent review. Không sửa ngưỡng M0 đã có. |
| SM4M-IR-F05 | **LOW** | Mô tả ngắn không nhắc đây là hai nhiệm vụ khác nhau; dễ bị hiểu nhầm là double-score agreement. | Chú thích rater S1/S2 đánh giá các endpoint khác nhau; không có agreement benchmark. |

### Chi tiết có thể truy vết từng finding

#### SM4M-IR-F01 — HIGH

- **Claim:** M0 hiện là phép phân biệt H-MEAS trước khi xem xét cơ chế mô hình.
- **Exact source:** https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md#L24-L37; https://github.com/minhtri22/TokenToModel-Lab/blob/33021a421f05bb3bfa0999ad12bc3bd144366da9/docs/research/ttm-hdata-fail4-md1/TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md#L38-L42
- **Observed evidence:** 32 lõi × (positive đúng cả actor/object/goal, negative sai cả ba); từng rater và từng trục sens/spec ≥28/32, inter-rater agreement ≥0.85.
- **Discrepancy:** Ba nhãn trục biến đổi đồng thời. Rater dùng một shortcut nhận biết 'positive/negative' tổng thể vẫn có thể vượt cả ba ngưỡng; không kiểm riêng sự nhạy với mỗi trục, trường hợp đúng một phần hoặc đầu ra tự nhiên mơ hồ. Agreement không khắc phục shortcut chung.
- **Scientific impact:** M0 PASS không loại trừ việc AI rater đánh 0 sai đối với một số đầu ra mô hình, cũng không chứng minh lỗi mô hình; việc dùng M0 làm discriminator quyết định có nguy cơ khóa sai giả thuyết.
- **Required remediation:** Sửa cách diễn giải F2 và hợp đồng thiết kế: M0 chỉ chứng nhận độ phân biệt trên đối chứng cực tính rõ; ghi điều kiện kiểm tra gold độc lập, anti-shortcut và kiểm soát riêng trục bằng prospective amendment trước khi cân nhắc thực thi. Không tạo dữ liệu trong review, không đổi 28/32 hay 0.85.

#### SM4M-IR-F02 — HIGH

- **Claim:** Tài liệu F2 dùng 'A/C và H-DATA-S1 có điểm 0 trùng nhau' để biện minh ưu tiên H-MEAS.
- **Exact source:** https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md#L37; https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md#L20-L21; https://github.com/minhtri22/TokenToModel-Lab/blob/37165ce6eea0bb4b04d316e2998da579c91d13cf/docs/research/TTM_AC_FINAL24_INDEPENDENT_QA_AND_FORMAL_ADJUDICATION_20261112.md#L37-L45
- **Observed evidence:** A/C FINAL24: adherence tuyệt đối A=0.6667/3, C=0.6667/3; chỉ hiệu số C−A=0. H-DATA-S1: cả H0 và H1 có điểm semantic primary tuyệt đối 0/3.
- **Discrepancy:** Đồng nhất hiệu số hai arm bằng 0 với các điểm tuyệt đối ở sàn 0. Hai chỉ báo thống kê khác bản chất, trên protocol/rater/task khác nhau.
- **Scientific impact:** Phóng đại mức độ phổ quát của measurement-floor hypothesis và làm yếu cơ sở xếp H-MEAS ưu tiên P0.
- **Required remediation:** Chỉnh lập luận roadmap: A/C cho NO_INCREMENTAL_GAIN (không phải all-zero absolute); H-DATA-S1 mới là all-zero absolute; không pooling các thước đo khác protocol. Giữ nguyên mọi số/score/thresh gốc và ưu tiên P0 có tính điều kiện.

#### SM4M-IR-F03 — MEDIUM

- **Claim:** F1 mô tả '48/48 H-DATA-S1 semantic axes = 0'.
- **Exact source:** https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md#L39-L42; https://github.com/minhtri22/TokenToModel-Lab/blob/ef4cc05037f98129082cd429a75092b8cc822efb/docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_FINAL24_OWNER_UNBLIND_FORMAL_ADJUDICATION_20261114.md#L33-L55
- **Observed evidence:** 24 cặp ×2 arm =48 continuations; mỗi continuation có ba trục primary actor/object/goal và mỗi trục được báo 0.
- **Discrepancy:** '48/48 axes' dùng mẫu số của continuation làm số trục; không rõ 48 đoạn hay 144 giá trị trục.
- **Scientific impact:** Thiếu minh bạch đơn vị quan sát khi cân nhắc false-zero và agreement.
- **Required remediation:** Đổi cách viết thành '48/48 continuations có cả ba trục bằng 0 (144 axis-level scores)', sau khi đối chiếu đúng frozen receipt; tuyệt đối không sửa score lịch sử.

#### SM4M-IR-F04 — MEDIUM

- **Claim:** Hợp đồng M0 nêu 'two-blind-independent-rater' và agreement ≥0.85 trên mỗi trục.
- **Exact source:** https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md#L30-L35; https://github.com/minhtri22/TokenToModel-Lab/blob/33021a421f05bb3bfa0999ad12bc3bd144366da9/docs/research/ttm-hdata-fail4-md1/TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md#L38-L42
- **Observed evidence:** MD1 có ngưỡng sens/spec ≥28/32 mỗi rater/trục và agreement ≥0.85 mỗi trục, nhưng chưa đóng băng công thức agreement, mẫu số, xử lý missing/invalid, định nghĩa human-gold hay cơ chế chứng minh không lộ nhãn.
- **Discrepancy:** Các ngưỡng có nhưng quy tắc chấm máy và quy trình custody trước khi thực thi còn thiếu chi tiết có thể kiểm toán; tài liệu F2 không đánh dấu explicit PREEXEC BLOCK cho các chi tiết này.
- **Scientific impact:** Hai nhóm reviewer có thể áp dụng công thức/mẫu số khác và cùng tuyên PASS; không nhất thiết là lỗi ở giai đoạn design-only, nhưng là lỗ hổng admission.
- **Required remediation:** Trước bất kỳ owner decision về M0 execution, khóa contract tính mẫu số, per-axis confusion matrices, cùng 64 items, anonymization, inter-rater scheme, invalid handling, gold provenance/rights/PII và independent review. Không sửa ngưỡng M0 đã có.

#### SM4M-IR-F05 — LOW

- **Claim:** F1 ghi 'FRESH16 independent AI-rater' có thể đọc như hai rater đồng thuận.
- **Exact source:** https://github.com/minhtri22/TokenToModel-Lab/blob/4c97f2b1d1836b31d55b649e78a8b69fecc44482/docs/research/ttm-small4m-foundation-first/02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md#L17; https://github.com/minhtri22/TokenToModel-Lab/blob/0ec28d44587fde9ad4acba8cccae65648e367181/docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCIENTIFIC_ADJUDICATION_20261111.md#L9-L13
- **Observed evidence:** FRESH16 dùng hai cuộc trò chuyện riêng: S1 chấm 32 đầu ra, S2 chấm 16 cặp; không có inter-rater reliability đo trên cùng items.
- **Discrepancy:** Mô tả ngắn không nhắc đây là hai nhiệm vụ khác nhau; dễ bị hiểu nhầm là double-score agreement.
- **Scientific impact:** Rủi ro diễn giải quá độ độ tin cậy đo lường, không làm thay đổi 0/16 hay 0/8.
- **Required remediation:** Chú thích rater S1/S2 đánh giá các endpoint khác nhau; không có agreement benchmark.

## G. Một gói remediation tích hợp, không tạo micro-permit

1. Chỉnh lại cơ sở H-MEAS trong F1/F2: không lấy `C−A=0` làm bằng chứng rằng A và C đều có semantic absolute floor=0; mô tả đúng 48 continuations × ba axes và nguồn scope.
2. Khóa giới hạn ý nghĩa của M0 và thiết kế chống shortcut trước khi owner xét mở thực thi (định nghĩa per-axis evidence, positive/negative/partial diagnostic controls tương lai, independent gold, blind provenance, rater formulas). **Đây là yêu cầu sửa thiết kế**, không cho phép tạo dữ liệu/chấm mới; giữ nguyên 32/64 và ngưỡng MD1 nếu chưa có amendment có thẩm quyền.
3. Chuẩn hóa caveat rater FRESH16 và quy tắc measurement, provenance. Không sửa mọi frozen scores, checkpoint, ngưỡng, seed, consent/rights hay kết quả âm tính.

Các sửa đổi cần đi thành **một gói thiết kế duy nhất** cho owner xem xét, không chia thành micro-permit hoặc tự mở F2 execution.

## H. Phán quyết, giới hạn và khóa bảo toàn

**Final decision: `HOLD_REVISE_DESIGN`.**

Lý do: **hai finding HIGH chưa được giải quyết** (SM4M-IR-F01 và F02). Không có bằng chứng GitHub source mismatch; F0 và scope isolation PASS scoped, nhưng F2 chưa đủ điều kiện `GO_DESIGN_SCOPED` theo chính chuẩn bàn giao.

**Giới hạn kiểm toán thực tế:**
- GitHub connector trả về nội dung UTF-8 và blob SHA-1 tại commit pinned; chúng tôi không được cấp kênh raw-byte private, không trực tiếp tính SHA-256 trên nguyên byte public hoặc weights, và không chứng minh chữ ký crypto independent của owner.
- Chưa đọc độc lập *tất cả* raw receipts thuộc 15 nhóm (chỉ các báo cáo gốc được liệt kê); kết luận historical evidence là source-report reconciliation, không phải forensic reenactment.
- Không kiểm live Windows checkout, permission của private weights/data, trạng thái mới nhất ngoài commit cố định hay khoa học thực nghiệm. Không claim SHA-256 của bốn documents.
- Không chạy checkpoint, GPU, forward, generation, training, evaluation, TEST hay FINAL. Không ghi, commit, push, merge hoặc tạo PR trên GitHub.
- Không có xác nhận human independent reviewer.

**Preservation locks:**
`SCIENCE=HOLD` · `GPU=NO` · `TRAINING=NO` · `MODEL_INFERENCE=NO` · `TEST/FINAL=UNTOUCHED` · `ROOT_CAUSE_IDENTIFIED=NO` · `F2=DESIGN_ONLY_NOT_EXECUTED` · `F3=NOT_OPENED` · `F4=NOT_OPENED` · `MERGE=NOT_AUTHORIZED` · `REPOSITORY_MODIFIED=FALSE`.

**Bước thực hiện tiếp theo — duy nhất:** **trình owner phán quyết tích hợp `HOLD_REVISE_DESIGN` và một gói remediation F01–F05 để quyết định sửa thiết kế**, không tự kích hoạt mô hình, F2, F3, F4 hoặc merge.
