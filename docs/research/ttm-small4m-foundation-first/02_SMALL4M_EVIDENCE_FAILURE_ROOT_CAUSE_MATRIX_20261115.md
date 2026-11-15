# TTM-Small-4M — SM4M-F1: Evidence, Failure & Root-Cause Matrix

**Operation:** TTM_SMALL4M_FOUNDATION_FIRST_COMPONENT_SPEC_AND_ROOT_CAUSE_RESEARCH_REBASE_SINGLE_GATE  
**Ngày:** 2026-11-15 · **Mode:** READ-ONLY SOURCE SYNTHESIS / DESIGN ONLY  
**Main baseline:** `fbe4a1ed58eef66f896bbfe0471926b7cc45298e`. `lineage.md` main đã được hợp nhất bởi PR #19: giữ L0011–L0012, L0015–L0022, L0025–L0026 và L0028; **không thêm hay sửa entry ở gate này**.  
**Định nghĩa:** `PASS` = chỉ đạt điều kiện chính xác của study/QA; `FAIL` = không đạt ngưỡng của study, không phải mô hình không thể học; `HOLD` = chưa hợp lệ/không được cấp quyền; `NOT_EXECUTED` = chưa đo; `UNVERIFIED` = không đủ nguồn cho claim. Không quy `FAIL` về một thành phần khi thiếu đối chứng.

## A. Evidence ledger — Small-4M core, không trộn hai nghiên cứu độc lập

| ID / bằng chứng | Cấp | Quan sát đã khóa | Gate khoa học / QA | Suy ra được / không suy ra |
|---|---|---|---|---|
| SM-E01: P02 core & T4 implementation | Source engineering | Decoder-only 4 blocks, embedding256, 4 heads, 3,749,376 params, BPE2048 context256 | SOURCE_PINNED, P02 QA lịch sử PASS_SCOPED | Đúng topology source; **không** tự chứng minh biểu diễn ngữ nghĩa |
| SM-E02: T4 VAL H1 | Real model science, one seed | Model VAL NLL 3.5223388517 vs TRAIN-only bigram 3.9972314170, tương đối tốt hơn 11.880537%; CI story-bootstrap lợi thế [0.45818675,0.49406158] | `PASS_H1_CONFIRMATORY_VAL_SCOPE` | Học token distribution trong pilot; **không** chứng minh fact adherence |
| SM-E03: T4 sealed TEST 64 | Real model science, descriptive one-shot | 64 stories, 14669 targets; model 3.4835910733 vs bigram 3.9736037453, tốt hơn 12.3316944% | `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED` | Hỗ trợ H1 phạm vi pilot; không được dùng lại TEST; per-token TEST không được tính lại độc lập |
| SM-E04: step1024→1280 / quality comparison | Exploratory QA / quality | VAL NLL giảm tiếp ~3.522339→3.498089, nhưng chất lượng đánh giá mù không có lợi ích ứng viên đủ ngưỡng | `NO_DEMONSTRATED_GAIN_SCOPED` | NLL vs chất lượng không đồng nhất; chưa xác định giới hạn capacity |
| SM-E05: FRESH12 serialization | 48 outputs, AI-rater; blinded | Prompt adherence mean 0.291667 cả baseline và trim; 35/48 điểm 0; Δ=0 | `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED` | Loại bỏ cách cứu bằng trailing whitespace trong phạm vi đo; rater AI duy nhất |
| SM-E06: FRESH16 V2 | Hai phiên chấm AI theo **hai nhiệm vụ khác nhau**: S1 chấm 32 đầu ra; S2 chấm 16 cặp; không có inter-rater agreement trên cùng items | H1 adherence≥2: 0/16 vs ngưỡng 12/16; H2 counterfactual: 0/8 vs 6/8 | `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED`; tally QA PASS | Bám prompt/CF không đạt; chưa biết do data, loss, capacity, decoding hay thước đo |
| SM-E07: CF1 DEV36 teacher-forced | Fixed checkpoint, non-TEST | Đúng cả hai ngữ cảnh 0/36; đúng A 1/36, B 35/36; không đổi preferred candidate 0/36 | `NO_DEMONSTRATED_SWITCH_SCOPED` | Tín hiệu fact conditioning yếu/có prior candidate B; evaluator có nguy cơ confound vị trí, không suy causal mechanism |
| SM-E08: D1 EXP32 | Fixed checkpoint, exploratory AI-rater | Greedy và nucleus mỗi bên 0/32 đạt grade≥2; 0/16 family thành công; teacher-forced S=1/16, prior-adjusted=2/16 | `WEAK_FACT_CONDITIONING_EXPLORATORY`, decoder-rescue not supported | Nucleus giảm repetition nhưng không giải quyết factual adherence; input-byte provenance rater chưa verified |
| SM-E09: A/C FINAL24 | Actual 128-update/arm, 24 pairs, blinded AI scores | **Điểm adherence tuyệt đối A=0.6667/3, C=0.6667/3**, chỉ **hiệu số C−A=0**; C strict wins 1/24; CI lower -0.125 | `FAIL_CANDIDATE_EFFICACY_GATE_NO_DEMONSTRATED_C_GAIN`; arithmetic 107/107 PASS | Cấu hình objective C ở study này **không** vượt A; đóng one-shot |
| SM-E10: H-DATA-S1 FINAL24 | Actual 128-update/arm; 24 pairs = **48 continuations**; 5 axes × 48 = **240 scores**, riêng 3 trục primary × 48 = **144 axis-level scores** | **48/48 continuations** được chấm 0 trên cả actor, object, goal (144/144 primary axis-scores=0); H0=0, H1=0, Δ=0, wins=0/24; VAL H1 3.505761 vs H0 3.511286 | `NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT`; 3 primary gates và goal-improvement FAIL | Một thay đổi dữ liệu có NLL tốt hơn nhẹ nhưng không có hiệu quả ngữ nghĩa trên đánh giá đã khóa; không suy toàn bộ data approaches vô hiệu |
| SM-E11: FC01 A/B/C | Real exploratory 3 arms, 256 updates/arm, 1 seed | 64 lexical-holdout families; A 4/64, B 3/64, C contrastive 38/64, nhưng entity_location C 1/16 | `PASS_SCOPED_EXPLORATORY_FC01_NO_CONFIRMATORY_RELEASE` | Tín hiệu objective C−B **trên template family**; chưa có OOD mechanism/new-template generalization |
| SM-E12: D1 Bridge R1 | Construct/source-only design & independent review | Boolean gate category + x0 lookup giải 32/32 OOD action sides; benchmark thiếu task-relevant action-causal novelty. Closure sau 330 constructive scenarios: admitted OOD=0 | `GO_CLOSE_R1_FORMULATION_DESIGN_ONLY`; `D1_BRIDGE_SCIENCE=HOLD` | Không dùng blueprint để chứng minh reasoning; đóng công thức R1, không tự mở benchmark thay thế |
| SM-E13: Q1/Q2 / T5/T6 | Tool/infra QA | Q1/Q2 chưa hoàn tất; T5 parity F32 scoped, T6 CPU synthetic merged | QA PASS_SCOPED / Q1Q2 partial HOLD | Không dùng tốc độ/tokenizer parity làm bằng chứng chất lượng |
| SM-E14: P07/P08 / scaling | Infra readiness | P07 paused; P08 not opened, scaling unapproved | `HOLD / NOT_OPENED` | Chưa có bằng chứng GPU, MoE hoặc tăng tham số chữa được chất lượng |
| SM-E15: private TRAIN/VAL/weights & rights | Custody/rights | Chứng cứ SHA và prior review, nhưng gate này không đọc private bytes | `PRIOR_RECEIPTS_ONLY / NOT_REVERIFIED_THIS_GATE` | Không được đổi thành rights PASS hoặc checkpoint byte audit mới |

### Tài liệu bằng chứng chính (source refs cố định)

- [T4 H1 VAL](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md); [T4 TEST](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md).
- [FRESH12](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-small4m-q1q2-quality-single-batch-20261109/docs/pilot/ttm-small4m-source-of-truth/TTM_FRESH12_OWNER_CONTROLLED_UNBLIND_AND_SCOPED_QUALITY_ADJUDICATION_20261110.md); [FRESH16](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-small4m-prompt-adherence-continuation-design-20261111/docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCIENTIFIC_ADJUDICATION_20261111.md).
- [CF1 DEV36](https://github.com/minhtri22/TokenToModel-Lab/blob/review/ttm-cf1-dev36-one-shot-scoped-science-adjudication-20261111/docs/research/TTM_CF1_DEV36_ONE_SHOT_INDEPENDENT_SCORE_READBACK_AND_SCIENCE_ADJUDICATION_20261111.md); [D1 EXP32](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-small4m-prompt-adherence-continuation-design-20261111/docs/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_EXP32_TERMINAL_EXPLORATORY_CLOSEOUT_AND_NEXT_RESEARCH_DIRECTION_20261112.md).
- [A/C FINAL24](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-small4m-post-final24-negative-archive-hypotheses-20261112/docs/research/TTM_AC_FINAL24_INDEPENDENT_QA_AND_FORMAL_ADJUDICATION_20261112.md); [H-DATA-S1 FINAL24](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113/docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_FINAL24_OWNER_UNBLIND_FORMAL_ADJUDICATION_20261114.md).
- [FC01 source-scoped science](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-small4m-d1-v6-r1r3-integrated-source-qa-20261114/docs/research/ttm-small4m-fact-conditioning/TTM_FC01_ABC_ONE_SHOT_INDEPENDENT_SCIENTIFIC_REVIEW_AND_SINGLE_SCOPED_ADJUDICATION_20261113.md); [D1 R1 final HOLD closure](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/research/ttm-small4m-fact-conditioning/TTM_D1_R1_INDEPENDENT_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_REVIEW_20261114.md).
- [Global lineage & branch matrix](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/governance/TTM_GLOBAL_LINEAGE_MERGE_AUDIT_AND_RESEARCH_DIRECTION_MATRIX_20261114.md); [main lineage.md](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/lineage.md). Source global inventory có nhiều `UNVERIFIED_CURRENT_GATE`: không thay thành FAIL hoặc PASS bằng suy đoán.

## B. Phân loại nguyên nhân — giả thuyết không phải phán quyết

| Hypothesis | Ủng hộ ban đầu | Bác bỏ / hạn chế | Ưu tiên chẩn đoán | Gate hiện tại |
|---|---|---|---|---|
| H-MEAS: thước đo/rater có sàn 0 hoặc không phân biệt kết quả đúng | **H-DATA-S1**: 48/48 continuations đều 0 trên ba trục (144 primary axis-scores). **FRESH12**: 35/48 grade 0. **A/C**: A=C=0.6667/3 và Δ=0, **không phải absolute floor** | M0 gốc chưa hiệu chuẩn riêng actor/object/goal; người chấm có thể dùng shortcut valence chung; đồng thời có thể mô hình thực sự yếu. Các thước đo khác protocol không được pooling | **P0 có điều kiện: kiểm độ tin cậy của phép đo trước khi diễn giải zero scores**, không xác nhận thước đo là nguyên nhân | `NOT_TESTED; M0_DESIGN_HOLD` |
| H-COND: mô hình chưa mã hóa/sử dụng conditioning từ fact | CF1 switch 0/36, D1 EXP32 fact score 1/16 | Teacher-forced metric và vị trí lựa chọn có confounds; chưa trực tiếp đo internal representation | P1 | `PLAUSIBLE_NOT_PROVEN` |
| H-DATA: chất lượng, độ phủ, ngân sách train hoặc lặp exposure không đủ | TRAIN 2048 stories, target reuse ~8.417×, thiếu task labels rõ ràng | H-DATA-S1 H1 không thắng không bác bỏ mọi thiết kế dữ liệu; chưa có controlled data-dose | P1 sau đo hợp lệ | `UNDERDETERMINED` |
| H-OBJ: next-token MLE không đủ tín hiệu mục tiêu | NLL tốt nhưng fact poor; FC01 C−B dương trên family | A/C FINAL24 và H-DATA failures; FC01 shortcut/template confounds | P1 sau đo hợp lệ | `MIXED_SCOPED` |
| H-DEC: decoding làm mất năng lực đã học | Greedy repetitive, nucleus cải thiện hình thức | D1 EXP32 nucleus vẫn 0/32 adherence; CF1 teacher-forced yếu | P2 | `DECODER_ONLY_RESCUE_NOT_SUPPORTED` |
| H-CONTEXT / ATTENTION: truy cập dữ kiện suy giảm theo độ dài/vị trí | Cần kiểm context=256 và distance/distractors | Chưa có contrast short vs distractor hợp lệ đã QA | P2 | `NOT_ESTABLISHED` |
| H-CAP: 4M parameters không đủ | 4 blocks, small embedding, yếu ở task phức tạp | Chưa có controlled capacity scaling với same-data/objective/budget | P3 | `NOT_TESTED` |
| H-TOOL: parity/cache/backend là lỗi chất lượng | Có T5 parity issues đã được giới hạn | T4 torch trực tiếp cũng FAIL adherence; QA kỹ thuật không bằng science | Không làm giả thuyết lõi | `NOT_ROOT_CAUSE_EVIDENCE` |

**Kết luận nhân quả hiện tại:** `ROOT_CAUSE_IDENTIFIED=NO`. Không có bằng chứng cho phép viết `ATTENTION_CAUSED_FAIL`, `MODEL_TOO_SMALL_CAUSED_FAIL`, `DATA_ONLY_CAUSED_FAIL` hoặc `DECODING_ONLY_CAUSED_FAIL`. FC01 tạo giả thuyết objective đáng giữ nhưng không chứng minh generalization. **F2 chỉ có thể ưu tiên kiểm chuẩn H-MEAS như một cổng đo lường có điều kiện.** M0 gốc đo cực tính đúng/sai rõ nhưng **không** nhận diện độc lập actor/object/goal; cần hợp đồng kiểm soát từng trục và trường hợp đúng một phần bằng prospective design amendment, chưa được cấp execution. Không suy M0 PASS thành lỗi mô hình và không gộp A/C Δ=0 với H-DATA-S1 absolute-zero.

## C. Bảo toàn nghiêm ngặt các kết quả đã tiêu thụ

`TEST64`, `FRESH12`, `FRESH16`, `CF1_DEV36`, `D1_EXP32`, `AC_FINAL24`, `HDATA_FINAL24`, `FC01_EVAL64` và các one-shot huấn luyện đã đóng: **không rerun, không re-score, không tái tạo seed, không gỡ sealed TEST/OOD/Q1Q2** để cứu ngưỡng. Giữ đúng sha và metadata nguồn riêng của từng nghiên cứu, không đưa raw TRAIN/VAL/TEST/escrow sang GitHub.


## D. Một gói remediation F01–F05 sau kiểm toán độc lập (15/11/2026)

**Nguồn kiểm toán độc lập do owner cung cấp:** `TTM_SMALL4M_FOUNDATION_FIRST_DISTINCT_INDEPENDENT_REVIEW_20261115.md` (SHA-256 của bản attachment được nhận: `3113f5b7c38e794de0504c859bdc0c0ee63d9fe5b285b2c9f29eb2ca194c84f4`) và `TTM_SMALL4M_FOUNDATION_FIRST_INDEPENDENT_REVIEW_RECEIPT_20261115.json` (SHA-256 bản attachment: `e8bc21c533d46d3212fd8bac779d4e5e01ab8e906decce208261def2548158ef`). Đây là metadata để nối provenance; **không tuyên bố hai file đã được lưu lên GitHub**. Frozen review verdict: `HOLD_REVISE_DESIGN`; sửa tài liệu tác giả không hồi tố thay verdict độc lập.

| Reviewer finding | Cách sửa trong gói tác giả | Không được thay |
|---|---|---|
| `SM4M-IR-F01` HIGH | M0 là **polarity calibration scoped**; không có per-axis identification khi ba nhãn biến thiên đồng thời; F2 roadmap bổ sung thiết kế prospective orthogonal/partial/uncertain controls và khóa anti-shortcut trước admission | Không đổi bộ MD1 gốc, không tạo data, không nêu root cause |
| `SM4M-IR-F02` HIGH | A/C FINAL24: `A=C=0.6667/3`, **ΔC−A=0**; H-DATA-S1 mới có **absolute primary zero**. Đây là hai protocol và rater khác nhau | Không pooling hoặc đổi primary scores |
| `SM4M-IR-F03` MEDIUM | H-DATA-S1: **48 continuations** (24 cặp ×2) và **144 scores ở 3 trục primary**, trong tổng **240 scores ở 5 trục** | Không tạo thêm observation hay re-score |
| `SM4M-IR-F04` MEDIUM | F2 khóa trước tương lai TP/TN/FP/FN từng trục, agreement, denominator, missing/invalid, blindness, gold/rights/PII/custody | Không đổi ngưỡng M0 gốc 28/32 và 0.85 |
| `SM4M-IR-F05` LOW | FRESH16 S1 chấm 32 đầu ra; S2 chấm 16 cặp; không có reliability estimate trên cùng items | Giữ nguyên FRESH16 0/16, 0/8 |

**Trạng thái sửa:** `AUTHOR_REMEDIATION_PREPARED_FOR_DISTINCT_QA`, **không** là `INDEPENDENT_FINDINGS_CLOSED`. F0 và scope isolation không sửa; reviewer phải tái kiểm F01–F05 trên exact new HEAD. Source/core science giữ `HOLD`.

**F1 gate output:** `EVIDENCE_MATRIX_COMPILED_AUTHOR_REVIEW`; `HYPOTHESES_PRIORITY_DESIGN_ONLY`; `DISTINCT_INITIAL_QA=HOLD_REVISE_DESIGN`; `REMEDIATION_INDEPENDENT_REREVIEW=PENDING`; `SCIENCE=NO_NEW_EXECUTION`.
