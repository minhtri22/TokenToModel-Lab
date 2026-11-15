# TTM — Ma trận ưu tiên hướng nghiên cứu sau Q001 (source-only)

**Operation:** `TTM_POST_Q001_RESEARCH_DIRECTION_PRIORITY_MATRIX_SOURCE_ONLY_SINGLE_GATE` · **Ngày:** 2026-11-15  
**Trạng thái:** `DESIGN_ONLY · NO_NEW_QUESTION · NO_SCIENCE_PERMIT`.  
**Exact `main`:** [3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7](https://github.com/minhtri22/TokenToModel-Lab/commit/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7); **lineage Git blob:** `3409e036241deb1da6674619a2abc834bea8a2d6`.  
**Closure:** `Q4_CLOSED_HOLD_NEW_SCIENCE`; `ROOT_CAUSE_NOT_IDENTIFIED`; `KEEP_HISTORICAL_REFERENCE_ONLY`; `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`.  

## 1. Phương pháp và đầu vào

Dựa trên [`lineage.md`](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md), [Q4 closure](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/sm4m-q001/SM4M_Q001_Q4_OWNER_CLOSURE_AND_GOVERNANCE_MERGE_DECISION_20261115.md), [canonical active gate](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/ACTIVE_RESEARCH_GATE.md), [Q3-reviewed causal matrix](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json), [Q3 independent report](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/sm4m-q001/SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_REVIEW_20261115.md), [Phase Plan P00–P12](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/PHASE_PLAN.md), [historical global branch audit](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/TTM_GLOBAL_BRANCH_EVIDENCE_QA_AND_RESEARCH_PRIORITY_20261114.md), [Mole-Syn watchlist](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/sm4m-q001/SM4M_Q001_PROSPECTIVE_LITERATURE_WATCHLIST_20261115.md). Nguồn đã pin tại exact main `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7`.

**Quy tắc xếp hạng:** điều kiện hard veto/admission trước; sau đó xét giá trị phân biệt các giả thuyết cạnh tranh; chỉ sau cùng xét rủi ro và chi phí ở mức định tính. `P0/P1/P2/P3` là **thứ tự thu thập bằng chứng/đề xuất thiết kế**, không phải xác suất root cause, không phải cổng science PASS. `P4` là tài liệu tương lai, **không cùng thước đo thực nghiệm** với Small-4M. Không dùng MCDA weights giả tạo hay tự bịa sample/GPU/time.

## 2. Ma trận ưu tiên chính

| Mức | Hướng nghiên cứu | Bằng chứng nguồn chính | Câu hỏi để phân biệt giả thuyết | Điều kiện nếu *sau này* owner mở Q mới | Kết luận hiện tại |
|---|---|---|---|---|---|
| **P0 PRECONDITION** | **Phép đo, ontology, gold nhìn thấy (measurement/construct)** | FRESH16 H1 0/16 H2 0/8; D1 R1 0/16 OOD admitted; H-DATA one blind AI rater; D1 EXP32 rater-visible bytes unverified | Gold/TRUE/FALSE/UNKNOWN/INVALID có suy ra được từ đúng dữ liệu người chấm được thấy hay không? | AD-01R_IF_SOURCE_REQUIRED, AD-02, AD-03_BEFORE_AUTHORING_AND_FREEZE, AD-04_BEFORE_SCORING, AD-05, AD-07 | `FIRST_REVIEW_PRIORITY_NO_GOLD_CREATION` |
| **P0 PRECONDITION** | **Khả năng phân biệt nguyên nhân (causal identifiability)** | NLL VAL PASS không là adherence; Q3 yêu cầu AD-03/AD-06 trước authoring/freeze | Teacher-forced correct-minus-wrong fact preference so với free generation trên cùng fact/checkpoint có phân biệt được conditioning và rollout? | AD-03, AD-05, AD-06_BEFORE_AUTHORING_AND_FREEZE, AD-07, AD-00, AD-01C_BEFORE_MODEL, AD-08_FUTURE_NEW_Q_AND_PERMIT | `SECOND_DEPENDENCY_NOT_PARALLEL_Q` |
| **P1 COMPETING MECHANISMS** | **Dữ liệu và độ phủ quan hệ (data/coverage)** | 498,287 TRAIN target positions exposed ~8.417×; FC01 data arm B=3/64 vs baseline A=4/64 (lexical-family); H-DATA-S1 no demonstrated gain | Các motifs/relations state/fact có nằm trong TRAIN hợp lệ hay không; can thiệp data-only có thay đổi margin với compute tương đương? | P0_MEASUREMENT, P0_IDENTIFIABILITY, AD-01R/T, AD-05, AD-06, AD-07, AD-08 | `TIED_WITH_OBJECTIVE_NO_TIEBREAK` |
| **P1 COMPETING MECHANISMS** | **Mục tiêu học và fact conditioning (learning objective)** | T4 NLL PASS; FC01 A=4 B=3 C=38/64 lexical family (entity-location C=1/16); A/C FINAL24 C-A=0 | Objective-only có chuyển được quan hệ sang unseen template hay chỉ học lexical shortcut? Có tách được loss khỏi negative supervision/extra compute? | P0_MEASUREMENT, P0_IDENTIFIABILITY, AD-01, AD-05, AD-06, AD-07, AD-08 | `TIED_WITH_DATA_NO_TIEBREAK` |
| **P2 CONDITIONAL DIAGNOSTIC** | **Độ dài ngữ cảnh/vị trí (context/window)** | Trained T4 actual context 256 + learned absolute position; source windows reset; no matched fact-distance controlled study | Visible fact bị truncate hay mất tác dụng chỉ do khoảng cách/vị trí khi nuisance được giữ nguyên? | P0_MEASUREMENT, AD-01T, AD-03, AD-06, AD-07, AD-08 | `ONLY_IF_POSITION_DEPENDENCE_TESTABLE` |
| **P2 CONDITIONAL DIAGNOSTIC** | **Chiến lược sinh/rollout (decoding)** | D1 EXP32 greedy and nucleus both 0/32 adherence≥2; nucleus improves repetition, but rater packet byte provenance not verified | Model ưu tiên fact đúng ở teacher force nhưng thất bại khi free-generate ở cùng fact không? | P0_MEASUREMENT, P0_IDENTIFIABILITY, AD-03, AD-04, AD-05, AD-06, AD-07, AD-08 | `NO_GREEDY_NUCLEUS_PATCH_NOW` |
| **P3 DEFER ARCHITECTURE** | **Capacity / attention / FFN / MoE** | T4 actual 3,749,376 params, 4 layers/4 heads; Q001/Q3 no proven T4 core architecture bug; no capacity-only experiment | Capacity-only matched control có tạo gain bền vững sau khi đo/gold/data/objective đã hợp lệ không? | P0_MEASUREMENT, P1_CONFOUNDS_RESOLVED, AD-01, AD-06, AD-07, AD-08 | `DEFER` |
| **P4 LONG HORIZON REFERENCE** | **Suy luận có cấu trúc/Long CoT/Mole-Syn** | Owner-approved arXiv 2601.06002v2 paper; behavior transitions deep reasoning/reflection/exploration; results from much larger models, NOT Small-4M | Reasoning behavior topology có ý nghĩa hơn keyword/verbosity khi chuyển giao? Tương hợp scale/context/rights thế nào? | NEW_QUESTION_OWNER_AUTHORIZATION, INDEPENDENT_CONSTRUCT_AND_GOLD, RIGHTS_CUSTODY, PREREG_AND_EVALUATION | `WATCHLIST_NOT_SCIENCE` |

**Đọc ma trận đúng cách:** `METRIC_GOLD` (P0-A) đứng trước `CAUSAL_IDENTIFIABILITY` (P0-B). `DATA_COVERAGE` và `OBJECTIVE_ALIGNMENT` **đồng hạng P1**; không có bằng chứng xác lập cái nào là root cause. Context và decoder chỉ xét khi có phép đo hợp lệ và một confound cụ thể. Capacity, attention, FFN và MoE **chưa có controlled capacity effect**, do đó `DEFER_NO_PATCH`. Long-CoT/Mole-Syn chỉ là tài liệu được owner chấp nhận, **không là đề xuất train 3,75M model**.

## 3. Đối chiếu các kết quả chính với lineage (không pool endpoints)

| Lineage exact main | Điều thực sự được chứng minh |
|---|---|
| [L0010](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md#L118-L127) | P01 Wikipedia E0 byte-BPE scoped QA, separate corpus |
| [L0011](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md#L129-L138) | T4 VAL NLL model 3.5223388517 vs bigram 3.9972314170, PASS H1 scoped, 1024 steps x4096 labels, ~498287 unique targets |
| [L0012](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md#L140-L148) | T4 TEST64 model NLL 3.48359107334 vs bigram 3.97360374532, descriptive PASS, TEST consumed sealed |
| [L0015](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md#L171-L179) | FRESH16 H1 0/16, H2 0/8 scoped FAIL, not refutation of NLL |
| [L0016](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md#L181-L188) | FC01 lexical family primary A4/64 B3/64 C38/64; entity-location C1/16; not OOD |
| [L0022](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md#L235-L245) | D1 R1 design closure, OOD admitted 0/16, science HOLD |
| [L0025-L0026](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md#L257-L260) | H-DATA S1 and FINAL24 negatives scoped, metrics/rater limits |
| [L0013-L0014](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md#L150-L159) | T5 numerical parity results independent from semantic failure |

Đặc biệt: NLL VAL/TEST chứng minh **token likelihood** tốt hơn bigram trong scope, không chứng minh fact adherence. FRESH16 và FC01 không đo cùng outcome; FC01 38/64 chỉ là lexical family, không phải OOD. D1 Bridge R1 `GO_CLOSE_R1_FORMULATION_DESIGN_ONLY` không là Science GO. Các FAIL/HOLD không được hồi tố sửa/xóa khỏi lineage.

## 4. Nhánh kỹ thuật/độc lập không được trộn với Small-4M

- **T5_NUMERIC** (`engineering`): L0013–L0014: 32/32 strict logits parity fail, 4/4 heldout GELU_ERF pass in distinct fixtures/config; separate from T4 factual learning failure. Disposition: `SEPARATE_ENGINEERING_PARITY_GATE_NO_AUTO_PATCH`.
- **T6_P07_P08** (`engineering`): L0027 T6 technical merged; P07 PAUSED; P08 NOT_OPENED; phase plan P00–P12 unchanged. Disposition: `PRESERVE_PREVIOUS_PHASE_HOLDS`.
- **VM** (`independent_scientific_programme`): L0023 historical scoped PASS/FAIL and R8 G0/G1/G2 HOLD, separate from T4. Disposition: `NO_CROSS_ARM_INFERENCE`.
- **EMBEDDINGGEMMA2** (`independent_scientific_programme`): L0024 OOD256 PASS scoped, not direct fact-conditioning evidence in T4. Disposition: `NO_CROSS_ARM_INFERENCE`.
- **HISTORIC_GLOBAL_BRANCH_INVENTORY** (`governance`): L0028–L0029 64/65 branches are 2026-11-14 snapshots, not current count; local lineage IDs may collide. Disposition: `SOURCE_HEAD_PIN_REQUIRED`.

Chú ý: L0013 strict logits FAIL là chênh lệch **runtime GGUF/GELU**, không chứng minh Transformer học sai; L0014 chỉ PASS trên 4 fixture GELU_ERF riêng. P07 `PAUSED`, P08 `NOT_OPENED`; train-first pilot không tự mở P09/P10. L0028–L0029 có số nhánh theo snapshot 14/11, **không phải số nhánh hôm nay**. Local `lineage` IDs tại VM/Embedding/H-DATA có thể trùng ID trong `main`: dùng StudyID + exact branch HEAD/source blob.

## 5. Admission trước mỗi quyết định tương lai

Quy tắc `AD-00…AD-08` giữ nguyên từ Q2/Q3: AD-00 hiện chỉ `PARTIAL_PUBLIC_SOURCE_MATCHED`; AD-01/02/03/04/05 chưa verified, AD-06 chưa executed, AD-07 chưa frozen. Giá trị `AD-08=Q3_AND_Q4_NOT_COMPLETED` trong **source Q2 lịch sử** không phải trạng thái live; Q4 đã CLOSED nhưng **new-science permission vẫn NOT_GRANTED**.

- **Abstract source-only design:** Không truy cập private weights, không tạo gold.
- **Trước production authoring:** AD-01R nếu cần access, AD-02 construct, AD-03 visible-gold witness feasibility, AD-05 shortcut guards, AD-06 one-variable matched identifiability.
- **Trước item freeze:** AD-01T nếu token-sensitive, từng fact/witness có thể truy được, paired controls/length policy, AD-07 prospective metric+blind custody.
- **Trước model execution:** exact checkpoint AD-01C và source AD-00, separate owner permit AD-08.
- **Trước scoring:** AD-04 independent gold/rater calibration và kiểm lại AD-03/05/06, không lần đầu kiểm gold lúc scoring.

**Hard veto:** `INVALID_CONSTRUCT_OR_HIDDEN_ONLY_GOLD · NO_OWNER_Q_OR_RIGHTS · NO_IDENTIFIABLE_ONE_VARIABLE_PAIR · NO_MEASUREMENT_PARITY · NO_RUNTIME_CUSTODY · REUSE_SEALED_TEST_FINAL · BENCHMARK_LEAKAGE`. Chúng là điều kiện dừng, không cho phép vượt bằng tổng điểm. Không có phép kiểm thử khoa học mới nào trong hồ sơ này.

## 6. Reasoning / Long CoT / Mole-Syn — tuyến đọc dài hạn

Tài liệu [*The Molecular Structure of Thought* — arXiv:2601.06002v2](https://arxiv.org/abs/2601.06002) dùng cấu trúc hành vi long CoT (deep reasoning, self-reflection, self-exploration) và Mole-Syn; một phần là phép **ẩn dụ đồ thị/phân tử**, không xác nhận neural mechanism. Bài báo dùng các LLM lớn hơn nhiều, không xác nhận hiệu quả ở TinyStories T4 3,749,376 tham số, context256. Không đưa bài mới thành `P14` của 13 tài liệu Q2 đã khóa; không mở data, objective, CoT training, MoE hay benchmark từ paper trong gate này.

## 7. Owner-facing kết luận và bước kế tiếp

**Đề xuất A (mặc định):** owner chỉ xem xét **một** candidate Question Gate mới về measurement/construct/gold source-visible; không sáng tạo fixtures, gold, thresholds hoặc permit trong ma trận này. **Đề xuất B (phụ thuộc A):** teacher-forced conditional preference vs free-generation, vẫn phải thiết kế để xác định confounds và nhận quyền nguồn. Không mở A/B đồng thời. Nếu A không feasible, giữ HOLD và không chạy vòng qua capacity/Long-CoT.

**Bất biến:** `ROOT_CAUSE_IDENTIFIED=false`, `SCIENCE_EXECUTED=false`, `NEW_QUESTION_REGISTERED=false`, `RESEARCH_BRANCH_OPENED=false`, `F0_F2_RESTARTED=false`, `LINEAGE_UNCHANGED`, `NO_MODEL_PATCH`, `NO_NEW_GOLD_OR_SCORER`.

## Bước thực hiện tiếp theo — duy nhất (đề xuất; chưa có owner GO)

`TTM_POST_Q001_PROSPECTIVE_QUESTION_SELECTION_OWNER_REVIEW_SINGLE_GATE`

Trình owner **một quyết định**: có chọn `METRIC_GOLD` làm câu hỏi tiền đăng ký kế nhiệm (vẫn phải lập Q mới và independent review) hay `HOLD`? Đây **không** phải yêu cầu chạy Science, không tạo micro-permit hoặc mở F0–F2.
