# SM4M-Q001 Q2 — Khóa ma trận nguyên nhân–bằng chứng và điều kiện admission trước phép kiểm thử phân biệt

**Operation:** `SM4M_Q001_Q2_EVIDENCE_ADMISSION_AND_CAUSAL_TRIAGE_CLOSURE_SINGLE_GATE`  
**Ngày:** 15/11/2026 · **Vai trò:** tác giả Q2, **chưa phải independent Q3 / owner Q4**  
**Repository:** `minhtri22/TokenToModel-Lab` · **main SHA:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc` · **Question:** `SM4M-Q001`  
**Đầu vào immutable:** báo cáo kiến trúc Q2 và receipt gốc, báo cáo literature adversarial và receipt 64/64 (SHA-256 ở §7); Q001 policy trên `main`.  
**Phạm vi:** đọc source/evidence cũ; **không** tạo prompt, gold, mã, checkpoint, baseline mới, TEST/FINAL replay, sửa F0–F2, branch/merge/lineage.

## 1. Trả lời hiện có và giới hạn quyết định

**Kết luận của tác giả Q2:** `KEEP_HISTORICAL_REFERENCE_ONLY · HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE · ROOT_CAUSE_NOT_IDENTIFIED`. Không phát hiện bằng chứng trực tiếp đủ để quy thất bại Small-4M cho attention, FFN, embedding, số lớp hoặc số head. `PASS` 38 kiểm tra mã gốc và 64 kiểm tra tự QA literature là **source/document QA**, không phải thí nghiệm phân biệt cơ chế hoặc xác nhận private bytes.

**Tại sao chưa thể chọn một bản vá:** T4 thắng TRAIN-fitted bigram ở VAL NLL nhưng điều đó chỉ xác nhận mục tiêu dự đoán token trong phạm vi VAL. FRESH16, CF1 và các can thiệp A/C/H-DATA nhiều kết quả âm tính có phép đo, rater và đầu vào khác nhau; FC01 dương tính hẹp trên lexical family. Không được gom mẫu số, nhãn hoặc verdict để suy nguyên nhân duy nhất.

**Quy tắc admission cốt lõi:** một historical verdict có thể được lưu đúng, nhưng không có nghĩa nó đủ điều kiện giải thích **vì sao** mô hình thất bại. Giữ nguyên toàn bộ original science PASS/FAIL, không hạ thấp verdict vì thiếu gold dùng cho một mục đích mới. Chỉ đánh dấu mức độ khả dụng của bằng chứng **cho suy luận nhân quả Q001**.

## 2. Ma trận nguồn/bằng chứng đã khóa (không tạo thí nghiệm mới)

| Study | Kết quả nguồn scoped | Admitted để mô tả lịch sử? | Admitted để kết luận nguyên nhân? | Chặn suy diễn |
|---|---|---|---|---|
| `T4_VAL` | T4 step1024 VAL NLL 3.5223388517 vs TRAIN bigram 3.99723141696; ~11.88% relative gain | `YES_SCOPED` | **NO** | Không phải phép đo actor/object/goal hay factual adherence |
| `T4_TEST64` | 64 truyện/14.669 target, one-shot đã tiêu thụ | `YES_SCOPED` | **NO** | SEALED/CONSUMED: tuyệt đối không tái chạy, chấm lại hoặc chọn hyperparameter |
| `FRESH12` | Chênh adherence trung bình 0; 4 PASS/4 FAIL candidate gates; một AI rater | `YES_SCOPED` | **NO** | Không so trực tiếp với FRESH16 do khác sample và scoring |
| `FRESH16_V2` | H1 0/16 grade≥2; H2 0/8 pair; hai phiên S1 output và S2 pair chấm nhiệm vụ khác | `YES_SCOPED` | **NO** | Không được coi S1/S2 là inter-rater agreement của cùng mục |
| `CF1_DEV36` | 0/36 chuyển ưu tiên completion khi đổi ngữ cảnh A/B trên exact public DEV | `YES_SCOPED` | **NO** | FINAL72 vẫn sealed; không chứng minh lỗi của objective hoặc architecture |
| `D1_EXP32` | Greedy và nucleus đều 0/32 grade≥2; nucleus cải thiện repetition | `QUALIFIED_ONLY` | **NO** | RATER_INPUT_BYTE_PROVENANCE_NOT_VERIFIED; chỉ dùng xu hướng đã ghi, không nâng thành gold truth |
| `AC_FINAL24` | C−A=0 về adherence; absolute mean 0.6667/3; 1/24 C strict wins | `YES_SCOPED` | **NO** | Bác bỏ hiệu quả C trong điều kiện thử đã khóa, không bác bỏ mọi objective |
| `HDATA_S1` | H0=H1=0 primary trong 24 pair; one blind AI rater | `YES_SCOPED` | **NO** | Không có human gold; không kết luận mọi thay đổi data không tác dụng |
| `FC01` | A4/64 B3/64 C38/64 lexical-family, rule 16/16 nhưng entity-location 1/16 | `YES_SCOPED` | **NO** | Không chứng minh OOD, reasoning tổng quát hay template transfer |
| `D1_R1` | Ontology feasibility HOLD; admitted OOD 0/16 | `DESIGN_ONLY` | **NO** | Không dùng làm baseline benchmark đã đạt admission |

**Đính chính bắt buộc:** FRESH16 S1 chấm output, S2 chấm pair nên **không phải inter-rater agreement cùng task**. D1 EXP32 chưa xác minh byte người chấm nhìn thấy. A/C FINAL24 có mean absolute **0,6667/3**, khác H-DATA-S1 **0**. FC01 **38/64** không là OOD. H-DATA là một blind AI rater, không phải human gold. Một số historical result vẫn có giá trị theo protocol gốc, nhưng **mọi nhánh `causal=NO` trong bảng** không chứng minh root cause.

## 3. Ma trận giả thuyết — mức bằng chứng, phản chứng và phép phân biệt

| Thứ tự thu thập | Giả thuyết | Bằng chứng địa phương | Phản chứng/giới hạn quan trọng | Bằng chứng cần trước khi xét cơ chế | Trạng thái |
|---:|---|---|---|---|---|
| 1 | `H-METRIC` | `D1_EXP32`, `FRESH16_V2`, `HDATA_S1`, `D1_R1` | Không có nguồn chứng minh AI rater thực tế sai trên toàn bộ mẫu; CF1 dùng metric trực tiếp nhưng vẫn không đảo preference | `AD-02`, `AD-03`, `AD-04`, `AD-05`, `AD-07` | `UNRESOLVED_PRIORITY_FOR_ADMISSION` |
| 2 | `H-OBJECTIVE` | `T4_VAL`, `FRESH16_V2`, `CF1_DEV36`, `FC01` | A/C objective intervention không tạo gain FINAL24; FC01 chỉ theo lexical templates | `AD-00`, `AD-01`, `AD-02`, `AD-03`, `AD-04`, `AD-05`, `AD-06`, `AD-07`, `AD-08` | `UNRESOLVED_MIXED_OBJECTIVE_EFFECT` |
| 2 | `H-DATA` | `T4_VAL`, `HDATA_S1`, `FC01` | H-DATA-S1 data intervention âm tính trong phạm vi; 4,19M exposure không là mẫu độc lập | `AD-01`, `AD-02`, `AD-05`, `AD-06`, `AD-07`, `AD-08` | `UNRESOLVED_COVERAGE` |
| 3 | `H-DECODER` | `D1_EXP32` | Greedy và nucleus cùng 0/32 trong D1 EXP32; raw rater input chưa được byte verify | `AD-02`, `AD-03`, `AD-04`, `AD-05`, `AD-06`, `AD-07`, `AD-08` | `SOLE_EXPLANATION_WEAKENED` |
| 3 | `H-CONTEXT` | `T4_VAL` | Chưa có matched fact-distance; long-context LLM paper không mô tả T4 context256 | `AD-00`, `AD-01`, `AD-02`, `AD-03`, `AD-06`, `AD-07`, `AD-08` | `UNRESOLVED_WINDOW_POSITION` |
| 4 | `H-CAPACITY` | `FRESH16_V2` | TinyStories phản biện định kiến <10M không thể; không có capacity-only control | `AD-01`, `AD-02`, `AD-03`, `AD-04`, `AD-05`, `AD-06`, `AD-07`, `AD-08` | `NOT_ISOLATED` |
| 99 | `H-IMPL` |  | Chưa xác minh runtime/private weights ở Q2; 38 source checks không bảo đảm không có bug | `AD-00`, `AD-01`, `AD-08` | `NO_CONFIRMED_SOURCE_BUG_CONTINGENT` |

**Không coi thứ tự là xác suất nguyên nhân.** H-METRIC ưu tiên vì phép đo sai/không đủ thông tin khiến mọi test sau không thể diễn giải. H-OBJECTIVE và H-DATA cùng thứ tự 2, không có kết luận cơ chế nào đã được cô lập. H-DECODER riêng lẻ bị suy yếu, nhưng không loại trừ lỗi liên quan quá trình sinh. H-IMPL được theo dõi theo điều kiện nguồn, không có xác nhận code defect.

### Điều gì thật sự có thể đổi lựa chọn?
- **`H-METRIC`:** Sự thiếu hụt gold/rater/visible evidence có làm cho điểm adherence không thể diễn giải nhân quả? **Ủng hộ nếu:** Một rater sai/không phân biệt trường hợp gold 0/1/UNKNOWN hoặc có gold hidden-only; cách chấm thay đổi kết quả trên fixed admissible examples. **Làm yếu nếu:** Nhiều adjudicator độc lập phân biệt gold ổn định với source parity và kiểm metadata; kết quả model FAIL vẫn tồn tại. **Không làm trong Q2:** VERIFY_MEASUREMENT_FIRST; không coi 0 điểm mặc định sai.
- **`H-OBJECTIVE`:** MLE có tạo được preference điều kiện nhưng rollout sai, hay không tạo được preference? **Ủng hộ nếu:** Sau gold hợp lệ, teacher-forced conditional margin không đảo theo fact hoặc objective-only matched intervention có gain trước prereg. **Làm yếu nếu:** Baseline phân biệt correct/wrong fact tốt dưới teacher forcing nhưng free continuation fail; ưu tiên decoder/rollout trước objective. **Không làm trong Q2:** NO_OBJECTIVE_PATCH_UNTIL_MATCHED_CONTRAST.
- **`H-DATA`:** Diversity/coverage thực sự gồm các quan hệ state và phản thực được yêu cầu hay không? **Ủng hộ nếu:** Đếm riêng training facts/motifs cho thấy thiếu construct; can thiệp data-only matched tăng khả năng phân biệt trên novel motif. **Làm yếu nếu:** Coverage hiện hữu và gain condition margin xuất hiện không cần thêm data; hoặc data-only matched không tạo khác biệt. **Không làm trong Q2:** NO_DATA_PATCH_FROM_EXPOSURE_COUNT_ALONE.
- **`H-DECODER`:** Điều kiện hóa nội tại đúng nhưng chiến lược sinh làm mất fact? **Ủng hộ nếu:** Teacher-forced fact preference chính xác, generation fail cùng case, decoding strategy điều chỉnh được outcome mà không đổi model. **Làm yếu nếu:** Teacher-forced margin sai và nucleus/greedy cùng fail factual trong matched task. **Không làm trong Q2:** DO_NOT_RETRY_DECODER_ONLY_AS_PATCH.
- **`H-CONTEXT`:** Lỗi đến từ chứng cứ bị cắt hoặc vị trí không được tận dụng? **Ủng hộ nếu:** Fact nằm ngoài 256 tokens hoặc performance giảm rõ khi đưa same fact tới vị trí khác nhau trong context256. **Làm yếu nếu:** Fact nằm trong prompt nhìn thấy và margins không đổi theo vị trí khi các nuisance cố định. **Không làm trong Q2:** CHECK_CONTEXT_SOURCE_FIRST; NO_ROPE_PATCH.
- **`H-CAPACITY`:** Capacity 3.75M là giới hạn cần thiết hay data/objective/measurement mới là giới hạn? **Ủng hộ nếu:** Sau cùng construct và training recipe matched, controlled capacity ablation tạo cải thiện ổn định vượt điều kiện đã khóa. **Làm yếu nếu:** Model hiện đạt target khi task/coverage/evaluation được kiểm soát; hoặc không có capacity-only effect. **Không làm trong Q2:** NO_HEAD_LAYER_OR_MOE_CHANGE_NOW.
- **`H-IMPL`:** Có bất nhất between exact trained source/config/bytes/runtime đủ làm vô hiệu mọi inference không? **Ủng hộ nếu:** Exact runtime/checkpoint mismatch, token mask/split leakage hoặc output provenance lỗi có bằng chứng byte/run. **Làm yếu nếu:** Public source matches historical signed runtime/pack/weights and independent scoped QA; không chứng minh không bao giờ có bug. **Không làm trong Q2:** INVESTIGATE_ONLY_IF_CUSTODY_OR_SOURCE_MISMATCH.

## 4. Điều kiện admission có thứ tự (hard veto, không dùng điểm MCDA để vượt qua)

| Gate | Điều phải **chứng minh** bằng evidence cụ thể | Trạng thái Q2 | Khi không đạt |
|---|---|---|---|
| `AD-00` Exact source pin và outcome provenance | Git commit/blob, frozen receipt, study-specific RunID/checkpoint/tokenizer/config/split/candidate score hash; nguồn được đối chiếu mà không dùng TEST/FINAL | `PARTIAL_PUBLIC_SOURCE_MATCHED` | `HOLD_SOURCE_MISMATCH` |
| `AD-01` Private checkpoint, tokenizer, pack và quyền nguồn | Authorized custodian xác minh byte SHA256 của checkpoint/tokenizer/split, quyền dữ liệu và quyền tạo hồ sơ mới; không công bố nội dung private | `NOT_VERIFIED_IN_Q2` | `HOLD_BYTE_CUSTODY_OR_RIGHTS` |
| `AD-02` Task và construct có khả năng quyết định | Định nghĩa riêng actor/object/goal, event/time/referent, điều kiện binary và UNKNOWN/INVALID; mỗi câu có nhãn nhất quán từ sự kiện nhìn thấy; không ép 2³ khi các biến phụ thuộc | `NOT_VERIFIED_FOR_NEW_TASK` | `HOLD_CONSTRUCT_INVALID` |
| `AD-03` Visible evidence parity | Cùng exact prefix+candidate+rubric mà blind rater xem; gold adjudicator chứng minh từng trục bằng vị trí byte UTF-8 trong nguồn nhìn thấy; không dùng E_core ẩn làm chứng cứ duy nhất | `NOT_VERIFIED_IN_Q2` | `HOLD_EVIDENCE_PARITY` |
| `AD-04` Independent gold / rater competence | Gold từ xét duyệt độc lập trước scoring; calibration balanced TRUE/FALSE/UNKNOWN, false abstention, cùng việc chấm, blind isolation, recorded disagreement; ngưỡng prospective đã khóa, không tự reuse 28/32 | `NOT_VERIFIED_IN_Q2` | `HOLD_RATER_OR_GOLD_INVALID` |
| `AD-05` Negative controls và chống shortcut | Hard negatives khác đúng một fact nhưng giữ từ vựng, thứ tự, độ dài/token budget và style; group-disjoint motif/template; kiểm leakage và answer cue | `NOT_VERIFIED_IN_Q2` | `HOLD_SHORTCUT_OR_LEAKAGE` |
| `AD-06` Paired experiment identifiability | Từng cặp đối chứng chung checkpoint, cùng prompt/context/source rights, một biến can thiệp, same information and compute budget, sample unit, seed, oracle; giữ separate descriptive endpoints | `NOT_EXECUTED` | `HOLD_CONFOUNDING` |
| `AD-07` Prospective metrics and custody | Primary endpoint, margin direction, equal candidate lengths/tokenization normalization policy, CI if relevant, cutoff/failure rule, blind map and first error all frozen before generation/scoring | `NOT_FROZEN_FOR_NEXT_EXPERIMENT` | `HOLD_PREREG_OR_CUSTODY` |
| `AD-08` Authority / closure sequence | Q2 author self QA → independent Q3 → owner Q4 closure; only then new prospective Q/branch if GO and separate science authorization. Historical TEST/FINAL remain sealed. | `Q3_AND_Q4_NOT_COMPLETED` | `HOLD_OWNER_Q4_NO_EXECUTION_PERMIT` |

**Hard-stop precedence (không giả vờ chạy checker):** (1) scope/owner chưa cho phép thì **không thực thi**; (2) byte/provenance/rights không chắc thì giữ `HOLD_SOURCE_CUSTODY`; (3) construct, visible-source gold không hợp lệ thì giữ `HOLD_MEASUREMENT`; (4) rater/proxy/shortcut không đạt thì không thể dùng scores để suy nguyên nhân; (5) nếu tất cả admission đã qua nhưng thiết kế không phân biệt giả thuyết hoặc threshold chưa prereg, không mở thí nghiệm. Một lỗi ở cổng trước không thể được hợp thức hóa bằng điểm tốt ở cổng sau.

**Tình trạng tức thời:** `AD-00=PARTIAL_PUBLIC_SOURCE_MATCHED` là chứng cứ nguồn public, **không** phải `AD-01/02/03/04/05/06/07/08 PASS`. Q2 chưa có gold/source-visible packet mới, không có rater calibration thực, không có chủ sở hữu khoa học GO, không có scoring. Không được dùng bất kỳ giá trị threshold cũ M0/M0X như threshold của design mới nếu chưa độc lập freeze và chứng minh relevance.

## 5. Phép kiểm thử phân biệt *tối thiểu* chỉ là thiết kế điều kiện, chưa mở

**Câu hỏi tương lai có thể tách được:** “Trên *cùng fact và cùng checkpoint* đã admission, T4 có gán xác suất ưu tiên cho continuation đúng so với sai nhưng không thể giữ fact khi free-generate, hay không có sự ưu tiên đó ngay ở mô hình?”

**Cấu trúc tối giản đề xuất (không sản xuất mẫu trong Q2):** một story-core có source/context nhìn thấy, một fact duy nhất được đổi trong hai continuation hợp ngữ nghĩa, giữ nguyên thông tin đầu vào và budget; không buộc phải có cả 8 pattern `2³`. Freeze token boundaries, candidate lengths, lexical counterbalancing, group-disjointness, negative controls, source rights, rater provenance, primary direction/ties/threshold và quyết định dừng **trước khi** mở tác vụ thực thi.

**Primary prospectively proposed:** teacher-forced correct-minus-wrong log-likelihood margin (so sánh chiều và chính sách xử lý độ dài/tokenization được khóa; không bịa cutoff). **Secondary:** free generation adherence trên cùng case sau khi gold/rater đã admitted. Chỉ thiết kế để phân biệt nhóm cơ chế; riêng một tín hiệu thống kê không phải root-cause proof.

| Teacher-forced | Free generation | Điều gì được ưu tiên khảo sát (không phải xác nhận nguyên nhân) |
|---|---|---|
| Correct fact ưu tiên rõ | FAIL | Decoder/rollout và metric, sau khi bảo đảm conditioning evidence |
| Wrong fact ưu tiên | FAIL | Representation/objective/data, sau khi loại prompt/context và scoring confound |
| Correct fact ưu tiên rõ | PASS | Khác biệt task/distribution/gold lịch sử; giữ nguyên verdict lịch sử |
| Không có gold/source parity | Bất kỳ | **HOLD_MEASUREMENT**; không dùng kết quả để gán lỗi model |
| Mismatch checkpoint/source | Bất kỳ | **HOLD_SOURCE_CUSTODY**; không mở science |

**Khoảng trống bắt buộc:** exact model bytes, corpus rights, evidence parity, calibrator, matched tokenizer/candidate length, group and sample unit, pre-specified primary endpoint và owner GO đều **chưa** đủ trong Q2. Do đó **không thiết kế fixture thực tế và không mở một nhánh nghiên cứu**.

## 6. Đối chiếu văn liệu — mức áp dụng và anti-overclaim

| Paper | Bằng chứng ngoài được dùng **chỉ để** | URL nguồn |
|---|---|---|
| `P01` TinyStories | capacity not deterministically disqualifying; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://arxiv.org/abs/2305.07759 |
| `P02` Scaling Laws for Neural Language Models | data/model/compute effect on cross entropy; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://arxiv.org/abs/2001.08361 |
| `P03` Training Compute-Optimal Large Language Models | data and parameters in a different scale regime; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://arxiv.org/abs/2203.15556 |
| `P04` Training language models to follow instructions with human feedback | objective alignment possible on other models; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://proceedings.neurips.cc/paper_files/paper/2022/hash/b1efde53be364a73914f58805a001731-Abstract.html |
| `P05` The Curious Case of Neural Text Degeneration | decoding influences repetition and fluency; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://mlanthology.org/iclr/2020/holtzman2020iclr-curious/ |
| `P06` Lost in the Middle | position influences context use in larger long-context models; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://aclanthology.org/2024.tacl-1.9/ |
| `P07` Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena | judge position/verbosity biases; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://arxiv.org/abs/2306.05685 |
| `P08` Large Language Models are not Fair Evaluators | pairwise order bias; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://aclanthology.org/2024.acl-long.511/ |
| `P09` SummEval | different automatic/human evaluation axes; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://aclanthology.org/2021.tacl-1.24/ |
| `P10` Are Emergent Abilities of Large Language Models a Mirage? | discontinuous metric issue; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://papers.neurips.cc/paper_files/paper/2023/hash/adc98a266f45005c403b8311ca7e8bd7-Abstract-Conference.html |
| `P11` Right for the Wrong Reasons | lexical heuristic shortcuts; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://aclanthology.org/P19-1334/ |
| `P12` CLUTRR | heldout reasoning rule composition; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://aclanthology.org/D19-1458/ |
| `P13` Tracking State Changes in Procedural Text | entity/location state witness; `SUPPORTS_PLAUSIBILITY_ONLY`, chưa chứng minh TTM | https://aclanthology.org/N18-1144/ |

**Giới hạn chuyển giao:** TinyStories P01 cho thấy dưới 10M có thể làm truyện trong một thiết lập khác, không chứng minh T4; P02/P03 nói về cross entropy/scaling ở chế độ khác; P04 về alignment chứ không khẳng định cần RLHF ở 3,75M; P05/P06 về decoding/long context không chứng minh T4; P07–P10 cảnh báo metric/judge, không tuyên rater TTM sai; P11–P13 cho ý tưởng negative controls và trạng thái fact, không xác nhận benchmark F2.

## 7. Custody, auditability và trạng thái đóng gói

**SHA-256 nguyên tệp input (readback local):**
- `SM4M_Q001_INTEGRATED_ARCHITECTURE_AUDIT_20261115.md` — `4973ad744f5d2e2e9e89f46e7890a37833c43cd99fdb82405be2148a580bce06`
- `SM4M_Q001_AUDIT_RECEIPT_20261115.json` — `9fbfb2b185043685b5d24e352eb7b029b6fc36098f5a735cd699b9b5f2261f4a`
- `SM4M_Q001_Q2_AUTHOR_ADVERSARIAL_QA_LITERATURE_TRIAGE_20261115.md` — `34c553d10250b8403a4d2e7170ce6f0329fa14284ea5018f59de35af94622d36`
- `SM4M_Q001_AUTHOR_ADVERSARIAL_LITERATURE_QA_RECEIPT_20261115.json` — `5254fbb557c2074d95d7aa65e14e6c2924e8da1979e12f6fe4b1340958303a65`

**Pinned Git refs/source blobs (không đổi):**
- `MAIN`: `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`
- `Q001`: `27b8337aea9c9e82bfe98657170e592fcb3ad941`
- `LINEAGE_BLOB`: `3409e036241deb1da6674619a2abc834bea8a2d6`
- `P02`: `9762343e06cf800b50574c2871ae1ed58537fb18`
- `T4_CONFIG`: `c9a6f256ba975228683ee7de2a1090e649110e97`
- `T4_TRAINER`: `76c4d0155cd0736919f41682f240b47ad3d7c428`
- `T4_PACK`: `cdce219f2a2df27e25579f069238d4327c1d7d91`
- `T4_BPE`: `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`
- `T4_EVAL`: `bef006bdff173fba6d8ba4aa0ef687a1732fd7c4`
- `T4_VAL_RECEIPT`: `84cb94647c403ea358d8c991090bf56adc11f128`
- `FRESH12_HEAD`: `72cbf73c3adb78f9d4111f702de71fa10f713533`
- `FRESH16_HEAD`: `0ec28d44587fde9ad4acba8cccae65648e367181`
- `CF1_HEAD`: `d725c39094a5a584fd76386145db21ca6dc5eaf6`
- `AC_HEAD`: `37165ce6eea0bb4b04d316e2998da579c91d13cf`
- `HDATA_HEAD`: `ef4cc05037f98129082cd429a75092b8cc822efb`
- `FC01_HEAD`: `b5dd5890b73a29744530ed3a1ffbc0dc7ae5195a`
- `FOUNDATION_HEAD`: `9b55596f580b36b436cf6bdb2ed5a4e45c6992de`

**Không có thay đổi trên GitHub trong Q2 này.** `main` vẫn ở Q1-registered snapshot; khi chưa được owner phê duyệt quy trình cập nhật và Q3 review, đây chỉ là **gói tác giả có SHA-256 local**, không phải đã ghi main. `lineage.md` là append-only science-only: Q2 source/design không tạo entry. Không xóa hay merge nhánh FAIL/HOLD, không làm phiền EmbeddingGemma 2 và Vector Memory.

## 8. Author closure — giới hạn chính xác

**Result:** `Q2_AUTHOR_CAUSAL_ADMISSION_PACKET_FROZEN_LOCALLY · QA_PENDING_FINAL_READBACK · ROOT_CAUSE_NOT_IDENTIFIED · HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE · Q3_NOT_EXECUTED · Q4_NOT_DECIDED`. Đây không phải independent Q3 PASS hay owner GO. Reviewer tương lai vẫn có thể bác bỏ ma trận/điều kiện nếu tìm thấy lỗi ở exact source.

**Bước thực hiện tiếp theo — duy nhất:** xác minh readback và tự QA của toàn bộ gói Q2; sau đó chỉ **đề nghị owner chấp nhận phạm vi hồ sơ Q2 cho independent Q3**, không mở F0–F2/benchmarks/patch hoặc cấp khoa học GO từ tài liệu này.
