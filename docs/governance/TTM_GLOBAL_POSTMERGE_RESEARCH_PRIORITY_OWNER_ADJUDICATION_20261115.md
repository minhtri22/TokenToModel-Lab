# TTM — Phân xử ưu tiên nghiên cứu sau hợp nhất PR #20 (owner review packet)

**Operation:** `TTM_GLOBAL_POSTMERGE_RESEARCH_PRIORITY_OWNER_ADJUDICATION_SINGLE_GATE`  
**Ngày:** 15/11/2026 · `READ_ONLY / SOURCE_ONLY / DESIGN_ONLY / NO_SCIENCE_EXECUTION`  
**Main exact pin:** `d8974676b8a67b038a1e3b042bd6299cfa8fad0a` · main tree `7a018b73e165b387a24e6d3f2b77b961ced46152`  
**Nguồn mới chưa nhập main:** Foundation First `97731311ba2fc3a8000c2532bd4e5a0470c437ba` trên nhánh `research/ttm-small4m-foundation-first-single-gate-20261115`.

## 1. Kết luận ưu tiên một lượt

**Đề xuất quản trị duy nhất:** `KEEP_SMALL4M_FOUNDATION_FIRST_ACTIVE_SOURCE_DESIGN_ONLY__PAUSE_INDEPENDENT_WORKSTREAM_EXECUTION__ARCHIVE_NEGATIVES`.

Đây là đề xuất phân bổ **ưu tiên đọc/kiểm toán thiết kế**, không phải quyết định owner phê duyệt science/phase. `OWNER_RATIFICATION=PENDING`. Chưa append lineage vì chưa có owner priority ratification chính thức. Không cấp phép M0, model forward, training, GPU, TEST, benchmark, FC02, MoE hoặc P07.

**Source-of-truth:** [MAIN_MATRIX](https://github.com/minhtri22/TokenToModel-Lab/blob/d8974676b8a67b038a1e3b042bd6299cfa8fad0a/docs/governance/TTM_GLOBAL_BRANCH_EVIDENCE_QA_AND_RESEARCH_PRIORITY_20261114.md) và [MAIN_LINEAGE](https://github.com/minhtri22/TokenToModel-Lab/blob/d8974676b8a67b038a1e3b042bd6299cfa8fad0a/lineage.md); snapshot 65 nhánh đã khóa ở PR20. GitHub quan sát hiện thời `67` nhánh (số mới không ghi đè snapshot cũ), 3 PR Draft #13/#14/#18. [FOUNDATION_SCOPE](https://github.com/minhtri22/TokenToModel-Lab/blob/97731311ba2fc3a8000c2532bd4e5a0470c437ba/docs/research/ttm-small4m-foundation-first/04_SMALL4M_SCOPE_ISOLATION_DECISION_20261115.md) là tài liệu proposal của branch mới chứ **chưa merge vào main**.

## 2. Vì sao Foundation First là trọng tâm

**Tín hiệu phân phối:** T4 decoder-only có 3.749.376 tham số, bốn layer, bốn attention heads, embedding=256, context=256, BPE=2048 ([FOUNDATION_ARCHITECTURE_F0](https://github.com/minhtri22/TokenToModel-Lab/blob/97731311ba2fc3a8000c2532bd4e5a0470c437ba/docs/research/ttm-small4m-foundation-first/01_SMALL4M_ARCHITECTURE_COMPONENT_SPEC_20261115.md)). [T4_VAL](https://github.com/minhtri22/TokenToModel-Lab/blob/d8974676b8a67b038a1e3b042bd6299cfa8fad0a/docs/pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md) cho VAL NLL 3,522339 so với TRAIN-only bigram 3,997231 (~11,88% lợi thế, 1 seed); [T4_TEST](https://github.com/minhtri22/TokenToModel-Lab/blob/d8974676b8a67b038a1e3b042bd6299cfa8fad0a/docs/pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md) TEST64 one-shot mô tả ~12,33% lợi thế. Đây là PASS phân bố token scoped, không là PASS fact/prompt adherence.

**Khoảng trống chất lượng:** [FRESH16](https://github.com/minhtri22/TokenToModel-Lab/blob/0ec28d44587fde9ad4acba8cccae65648e367181/docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCIENTIFIC_ADJUDICATION_20261111.md) H1 0/16 và H2 0/8; [CF1](https://github.com/minhtri22/TokenToModel-Lab/blob/d725c39094a5a584fd76386145db21ca6dc5eaf6/docs/research/TTM_CF1_DEV36_ONE_SHOT_INDEPENDENT_SCORE_READBACK_AND_SCIENCE_ADJUDICATION_20261111.md) đổi lựa chọn theo fact 0/36; [HDATA](https://github.com/minhtri22/TokenToModel-Lab/blob/33021a421f05bb3bfa0999ad12bc3bd144366da9/docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_FINAL24_OWNER_UNBLIND_FORMAL_ADJUDICATION_20261114.md) H0/H1 đều 0 trên 144/144 axis-level primary scores; A/C FINAL24 A=C=0,6667/3 nhưng Δ=0, **khác** sàn tuyệt đối H-DATA. [FC01](https://github.com/minhtri22/TokenToModel-Lab/blob/6023ed90612e614ce4bbdc45fee88689fbed6b6e/docs/research/ttm-small4m-fact-conditioning/TTM_FC01_ABC_ONE_SHOT_INDEPENDENT_SCIENTIFIC_REVIEW_AND_SINGLE_SCOPED_ADJUDICATION_20261113.md) có tín hiệu contrastive C=38/64 ở lexical family, nhưng category entity_location chỉ 1/16, 1 seed, chưa có structural-OOD chứng nhận. [D1_R1_CLOSURE](https://github.com/minhtri22/TokenToModel-Lab/blob/d8974676b8a67b038a1e3b042bd6299cfa8fad0a/docs/research/ttm-small4m-fact-conditioning/TTM_D1_R1_INDEPENDENT_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_REVIEW_20261114.md) đã đóng benchmark hiện tại, không chứng minh ontology bất khả thi.

**Không xác định root cause:** dữ liệu, objective, attention, capacity, decoding và measurement đều chưa được tách bằng đối chứng causal đủ mạnh. Nhãn `ROOT_CAUSE_IDENTIFIED=NO`. Hiện nên phân xử phép đo (measurement validity) trước để tránh coi zero score là nguyên nhân model hoặc sửa model theo một rubric không phân biệt từng trục.

## 3. Trạng thái Foundation First F0–F4 mới nhất (nguồn ngoài main)

| Gate | Nguồn / mức thực chứng | Quyết định portfolio |
|---|---|---|
| F0 cấu phần mô hình | Author source specification, independent PASS scoped được báo trong [FOUNDATION_ROADMAP_F0_F4](https://github.com/minhtri22/TokenToModel-Lab/blob/97731311ba2fc3a8000c2532bd4e5a0470c437ba/docs/research/ttm-small4m-foundation-first/03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md); private weights chưa rehash | REFERENCE; không chạy lại |
| F1 tổng hợp evidence | Initial independent review `HOLD_REVISE_DESIGN` F01–F05; author đã sửa trong [FOUNDATION_EVIDENCE_F1](https://github.com/minhtri22/TokenToModel-Lab/blob/97731311ba2fc3a8000c2532bd4e5a0470c437ba/docs/research/ttm-small4m-foundation-first/02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md), re-review độc lập **PENDING** | **P0 — một independent exact-HEAD re-review** |
| F2 measurement | M0 gốc chỉ là polarity: 32 `111` và 32 `000`, không nhận diện tách actor/object/goal; per-axis/partial/ambiguous/anti-shortcut chỉ là prospective amendment | DESIGN_HOLD; M0 chưa được phép chạy |
| F3 tối ưu một thành phần | Không được phép chọn data, objective, attention hoặc size trước khi F2 phân biệt nguyên nhân | NOT_OPENED |
| F4 phân xử và closure | Không có nghiên cứu mới cần phân xử | NOT_OPENED |

**Điều kiện tối thiểu F2 về phương pháp, không phải lệnh:** M0 threshold gốc sensitivity/specificity từng trục ≥28/32; per-axis agreement ≥0,85 trên cùng 64 ID của hai raters; không lấy M0 polarity PASS làm chứng cứ nhận diện per-axis. Dự thảo per-axis riêng/partial/unsure cần prereg gold, anti-shortcut, denominators, rights, blind custody, independent QA và owner decision **một gói** trước execution. F01–F05 sửa của tác giả chưa được một distinct reviewer xác nhận tại HEAD mới.

## 4. Ma trận quyết định theo portfolio (không phải per-branch priority của snapshot)

| Hướng | Portfolio | Kết quả khoa học/QA hiện tại | Quyết định đề xuất | Điều kiện thay đổi |
|---|---|---|---|---|
| TTM-Small-4M Foundation First F0–F4 | **P0** CORE_RESEARCH | F0 independent PASS source scoped as author-reported; F1 author remediation F01–F05 awaiting distinct re-review; F2 design-only HOLD, M0 NOT_EXECUTED; F3/F4 NOT_OPENED | `KEEP_ACTIVE_DESIGN_READ_ONLY` | ONE DISTINCT F01–F05 integrated source/design QA at exact foundation HEAD; no M0 execution |
| EmbeddingGemma 2 / OOD256 independent program | **P1** SEPARATE_RESEARCH | OOD256 CLOSED_PASS_SCOPED; causal semantic-vs-geometry unresolved; A0E NO_GO_HOLD | `PAUSE_NEW_SCIENCE; PRESERVE_RESULT` | Potential geometry-matched residual control design only after separate owner reprioritization |
| Vector Memory V4 | **P1** SEPARATE_RESEARCH | R7 FROZEN_FAIL; R8 G0/G1/G2 HOLD; R8 NOT_GENERATED; reader=0 | `PAUSE_NEW_SCIENCE; HOLD_BOUNDARIES` | If owner later prioritizes, close source F02/F03 and custody/rights as one integrated review |
| P07 GPU PagedAttention / P08 | **P2** TECHNICAL_INFRA | XPU GPU smoke PASS_SCOPED; V1 overall FAIL_OR_INCONCLUSIVE 6.037>6.0 GiB; P07 G1/G2 NOT_EXECUTED; P08 NOT_OPENED | `PAUSED_NO_AUTORERUN` | Preserve receipts; no GPU kernel dispatch without independent backend and owner decision |
| T5/T6 inference serving and PR #14/#18 docs | **P2** TECHNICAL_GOVERNANCE | T6 CLOSED_MERGED_SCOPED; T5 raw logits 4/4 scoped; PR14/18 Draft and rights not released | `PRESERVE_BASELINE; DOCS_REVIEW_CONDITIONAL` | No new runtime; optional separate docs-only QA on draft PRs |
| MoE / alternate attention / scaling | **P3** UNOPENED_HYPOTHESIS | NO_CAUSAL_ROOT_CAUSE_PROOF; NOT_OPENED | `DO_NOT_OPEN` | Only if future F2 shows context/access or capacity bottleneck, one component prereg in F3 |
| FRESH12/FRESH16, CF1, A/C FINAL24, H-DATA, D1 R1, O0/R3A, SIX G1 | **P3** HISTORICAL_NEGATIVE_OR_SCOPED | CONSUMED / FAIL_SCOPED / CLOSED_HOLD / EXPLORATORY_NO_SIGNAL (study-specific) | `ARCHIVE_PRESERVE_NO_RERUN` | Reference by pinned SHA and lineage source-local ID; no rerun/re-score |

**Lưu ý:** EmbeddingGemma 2 và Vector Memory **độc lập** với Small-4M; không dùng donor residual, retrieval, R8 reader hay LLM scorer của chúng làm điều kiện GO cho F0–F4. [EMBED_OOD256](https://github.com/minhtri22/TokenToModel-Lab/blob/d4550cb9c88103ccfb4ce0b3683c13f4136e4bd1/docs/pilot/TTM_GEMMA2_OOD256_12ARM_FINAL_INDEPENDENT_SCIENTIFIC_ADJUDICATION_20261111.md) OOD256 co-primary PASS scoped (tau +0,06836, gamma +0,04798) nhưng không cô lập semantics. [EMBED_A0E](https://github.com/minhtri22/TokenToModel-Lab/blob/2583dadc254a7b1f0bcc1e6b283f1226407752c8/docs/pilot/TTM_GEMMA2_A0E_OWNER_GOLD_CUSTODIAN_FOURARM_NULL_QA_FINAL_NO_GO_20261111.md) A0E `NO_GO_HOLD`, 5/13 scoped PASS và 8 HOLD. [VM_R8](https://github.com/minhtri22/TokenToModel-Lab/blob/8dec9438bff96922e5defd64550971c309d5b32f/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G0_G1_G2_F01_F03_DISTINCT_INDEPENDENT_READBACK_ADJUDICATION_20261114.md) R8 `HOLD_INTEGRATED` (G0 boundary, G1 rights/owner, G2 private custody). [P07](https://github.com/minhtri22/TokenToModel-Lab/blob/06b047856a841a2213803608edfe336588857f59/artifacts/qa/p07/P07_ONE_SHOT_XPU_PASS_DISK_BUDGET_BLOCK_20261108.json) XPU compute PASS scoped nhưng V1 tiêu thụ 6,037 GiB > 6 GiB budget, P07 G1/G2 kernel chưa thực thi; [T6](https://github.com/minhtri22/TokenToModel-Lab/blob/d023dd16f4c07a954d2ae1d3af150ab3439b40f2/docs/governance/TTM_T6_POST_MERGE_CLOSURE_AND_P07_P08_DEPENDENCY_REVIEW_20261114.md) T6 `CLOSED_MERGED_SCOPED`, P08 `NOT_OPENED`.

## 5. Kết quả âm tính không được xóa hoặc cứu hậu nghiệm

| Outcome | Hành động | Không được làm |
|---|---|---|
| FRESH12/FRESH16 / CF1 DEV36 / D1 EXP32 | Lưu dưới exact SHA/lineage, giữ FAIL scoped | Không rerun/re-score TEST hoặc dùng điểm cũ cho prereg mới |
| A/C FINAL24 | Đóng kết quả C−A=0, A=C=0,6667/3 | Không gộp với H-DATA absolute floor |
| H-DATA-S1 FINAL24 | `NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT`, sàn 144/144 primary trục trong protocol | Không suy mọi data hypothesis vô hiệu |
| FC01 | Giữ `PASS_SCOPED_EXPLORATORY`, category heterogeneity | Không biến 38/64 lexical family thành causal OOD GO |
| D1 R1 | `GO_CLOSE_R1_FORMULATION_DESIGN_ONLY` và science HOLD | Không xây lại 32 blueprint hay mở FC02 |
| O0/R3A/TTM×SIX G1 | Lưu verdict FAIL/HOLD/exploratory theo nguồn nhánh; không mở science | Không coi exploratory absence of gain là global impossibility |

## 6. Chính sách merge và custody

- **Không đổi `main`, `lineage.md` hoặc mã khoa học** trong operation này. Phiên bản Foundation First ngoài main vẫn diverged; không nhập mã hoặc tài liệu Foundation vào main mặc định.
- Bản ghi này là author/assistant governance synthesis. Không tự nhận independent science QA. Các nguồn đã đọc tại commit nhưng **không chạy lại thí nghiệm, không rehash private checkpoint/data hoặc independent reviewer attachments**.
- Các nghiên cứu khác bị `COORDINATION_PAUSE` là **tạm dừng ưu tiên trong portfolio**, không xóa hay biến PASS/FAIL thành HOLD; nghiên cứu độc lập sau này cần quyết định owner riêng.
- Không tạo chuỗi micro-permits; một lượt source/design review tích hợp của F01–F05 trước bất kỳ quyết định M0 hoặc phase mới.

## 7. Phán quyết và owner ratification

**PORTFOLIO_SOURCE_QA:** `PASS_SCOPED_SOURCES_READ_AND_PRIORITIES_PROPOSED`.  
**RECOMMENDATION:** `KEEP_SMALL4M_FOUNDATION_FIRST_ACTIVE_SOURCE_DESIGN_ONLY__PAUSE_INDEPENDENT_WORKSTREAM_EXECUTION__ARCHIVE_NEGATIVES`.  
**OWNER_PRIORITY_RATIFICATION:** `PENDING_EXPLICIT_OWNER_DECISION`.  
**SCIENCE:** `HOLD`; **TRAIN/GPU/INFERENCE:** 0; **TEST Q1/Q2:** SEALED; **FC02:** NOT_OPENED; **D1 benchmark:** NOT_AUTHORIZED.

## Bước thực hiện tiếp theo — duy nhất

`TTM_SMALL4M_FOUNDATION_FIRST_F01_F05_DISTINCT_EXACT_HEAD_SOURCE_DESIGN_REVIEW_SINGLE_GATE` — sau owner xác nhận ưu tiên thiết kế, giao một reviewer độc lập kiểm exact source Foundation First `97731311ba2fc3a8000c2532bd4e5a0470c437ba`, rà soát F01–F05, per-axis validity và tình trạng F0/scope, trả một GO_DESIGN_SCOPED/HOLD_REVISE_DESIGN. Không science execution hoặc merge.
