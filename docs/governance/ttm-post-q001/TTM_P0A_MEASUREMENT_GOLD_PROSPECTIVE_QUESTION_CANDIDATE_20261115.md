# TTM P0-A — Ứng viên câu hỏi Measurement / Source-visible Gold (chưa đăng ký Q1)

**Scope:** `DESIGN_ONLY · CANDIDATE_Q1_NOT_REGISTERED`.  
**Căn cứ owner:** [P0-A selection](TTM_POST_Q001_P0A_OWNER_SELECTION_AND_PRIORITY_DEPENDENCY_LOCK_20261115.md).  
**Template:** [TTM Research Question Gate](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/templates/TTM_RESEARCH_QUESTION_GATE.md).  
**Baseline exact `main`:** `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7`; [Q001 Q4 closure](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/sm4m-q001/SM4M_Q001_Q4_OWNER_CLOSURE_AND_GOVERNANCE_MERGE_DECISION_20261115.md); [Q3-reviewed AD timing matrix](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json); [lineage](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md) Git blob `3409e036241deb1da6674619a2abc834bea8a2d6`.  
**Identity:** `P0A-CANDIDATE` chỉ là mã bản dự thảo, **không phải QuestionID chính thức**.

## A. Q1 candidate — Một câu hỏi và quyết định có thể thay đổi

**Câu hỏi duy nhất, có thể bác bỏ (v2):** Trong *một họ assertion* `LOCATED_AT(entity_id, location_id, reference_time_id)` với thời điểm được nêu tường minh, có thể định nghĩa hợp đồng source-visible gold mà người phân xử chỉ gán `TRUE/FALSE/UNKNOWN` sau khi item được admission, witness còn trong **effective model-visible prefix sau prompt rendering/tokenization/context truncation** và trong **rater-visible evidence có cùng fact**, không nhập `UNKNOWN_VALID` với `REJECT_MISSING_WITNESS`/invalid hay không? Có hay không, phải thay đổi quyết định `KEEP/SIMPLIFY/PIVOT/STOP/HOLD` theo luật xác định trước.

**Scope v2:** chỉ một quan hệ địa điểm của một entity tại một reference-time rõ trong cùng nguồn hiển thị. Loại khỏi construct đa-hop, mục đích, chuỗi biến đổi trạng thái, coreference không giải được, thời gian ngầm và Long-CoT. Chưa chứng minh nguồn TinyStories chứa đủ item thuộc họ này; không tự xây corpus/gold. Dùng `ITEM_ADMISSION_STATUS` (ELIGIBLE hay REJECT_*) tách khỏi `FACT_LABEL` (TRUE/FALSE/UNKNOWN). `INVALID` là item REJECT do schema/ontology, không phải một kết quả fact-label và không nằm trong denominator.

**Quy tắc canonical v2:** [Integrated independent-HOLD remediation contract](TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_SOURCE_CONTRACT_20261115.md) và machine-readable contract v2 dưới đây là định nghĩa ưu tiên khi bất kỳ câu mô tả broad v1 nào mâu thuẫn. Reviewer original: `HOLD_Q1_SOURCE_DESIGN` với F-CONSTRUCT, F-PARITY, F-DECISION; **chưa có re-review mới**. Benchmark/gold `NOT_VALIDATED`; Q1 `NOT_REGISTERED`.

**Decision evidence:** `KEEP` cần tất cả admissibility/rights/actual gold/rater/threshold được xác thực trong một prospective protocol hợp lệ; `SIMPLIFY` cần chứng minh một tiểu lớp lỗi có thể loại bỏ trước khi nhìn kết quả; `PIVOT` cần chứng minh scope hiện tại bất khả thi cùng một oracle hợp pháp thay thế (đăng ký Q riêng); `STOP` cần chứng minh bất khả thi không thể cứu/không có hướng hợp pháp; `HOLD` là mặc định khi quyền, witness, parity, gold/rater, budget hay threshold chưa được xác minh. PASS Q1 *design-only* không được đồng nhất KEEP.


**WHY:** [L0011/L0012](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md) NLL VAL/TEST PASS theo bigram **không** kiểm định fact adherence; [L0015](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md) FRESH16 scoped FAIL; [L0016](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md) FC01 lexical C38/64 nhưng entity-location C1/16; [L0022](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/lineage.md) D1 R1 ontology OOD admitted 0/16; D1 EXP32 thiếu exact rater-visible byte. Chỉ có câu trả lời causal khi measurement có thể kiểm chứng.

**OBSERVED từ nguồn:** `Q001_ROOT_CAUSE_NOT_IDENTIFIED`, `Q3_PASS_SOURCE_SCOPE`, `Q4_CLOSED_HOLD_NEW_SCIENCE`; AD-02/03/04/05 chưa verified, AD-06 chưa thực hiện.  
**INFERRED, chưa chứng minh:** một phần floor ở rubric có thể do gold hidden-only, ontology mơ hồ hoặc evaluator shortcuts; đây là **rủi ro**, không là kết luận “AI rater đã sai”.  
**UNKNOWN:** quyền truy cập nguồn task cụ thể, danh tính source-visible fact packet, semantic witness, agreement giữa independent adjudicators, calibrated error/abstention, tokenization/lexical overlap, tính khả thi counterfactual; chưa có dữ liệu mới.  
**Đã tiêu thụ, cấm chạy lại:** TEST64, FRESH16, FINAL24/72 (nếu thuộc study sealed), các private mapping/trọng số. Không tạo một “fresh TEST” bằng đổi tên dữ liệu cũ.

**Independent Q1 design status (current):** `HOLD_Q1_SOURCE_DESIGN · AUTHOR_REMEDIATED_PENDING_DISTINCT_REREVIEW`. Reviewer summary describes three HIGH blockers; the reviewer Markdown and JSON at local Windows path are **not archived or byte-verified here**. Do not cite the summary as an archived original receipt.

## B. Q2 candidate — cơ chế cạnh tranh, lý do chọn framework

| ID | Cơ chế / giải thích cạnh tranh | Dự đoán có thể bác bỏ | Điều cần chứng minh trước khi tiếp tục |
|---|---|---|---|
| `M0_VISIBLE_CONSTRUCT` | Construct hợp lệ, gold suy được từ cùng exposed evidence | Adjudicators độc lập có thể chỉ rõ witness và thống nhất nhãn theo quy tắc prereg | Visible packet invariant, typed entity/event/time roles, TRUE/FALSE/UNKNOWN/INVALID |
| `M1_HIDDEN_ONLY` | Gold nằm trong `E_core`/hidden state, không xuất hiện trong rater-visible packet | Gold có thể xác định khi xem hidden source nhưng không thể xác định từ exposed-only input | **HOLD** benchmark rater-visible; không “sửa” bằng lén nhìn hidden source |
| `M2_AMBIGUITY` | Actor/object/goal/time/referent thiếu định nghĩa; nhiều nhãn đều hợp lý | Disagreement có thể giải thích bằng nguồn thiếu hoặc ontology; `UNKNOWN/INVALID` tăng | Simplify ontology hoặc PIVOT task; không ép mọi case thành binary |
| `M3_SHORTCUT` | Lexical cue/order/length/style quyết định rater label thay vì fact | Negative control cùng từ vựng nhưng khác fact đảo nhãn mà rater/metric không đảo phù hợp | Balanced counterfactual, group-disjoint motif, no answer leakage |
| `M4_RATER` | Lỗi/bias của một AI rater gây artifact độc lập với model | Same-task calibrated independent judges disagree hoặc đổi kết luận theo vị trí/định dạng | Blind calibration, same packet, explicit adjudication; S1/S2 FRESH16 khác task **không** là inter-rater agreement |

**Framework hợp nhu cầu:** `5W1H` để khóa WHO nhìn gì và WHAT là gold; `construct validity + falsification` để kiểm witness; `FMEA hard-veto` cho hidden-gold, leakage, invalid labels, biased adjudicator. Không dùng MCDA/RPN khi chưa có empirical scores; 5 Whys không chứng minh chuỗi nhân quả.

| Option | Ưu điểm và điều kiện | Hard veto / giới hạn | Hiện trạng |
|---|---|---|---|
| `KEEP` | Source-visible fact contract có witness; có thể phân biệt đúng/sai/chưa biết | Thiếu rights/witness/calibration → HOLD | `NOT_DECIDED` |
| `SIMPLIFY` | Giảm task xuống construct có thể quyết định, ví dụ loại bỏ relation phụ thuộc event chưa được biểu diễn | Không được thay gold/hypothesis sau khi thấy outcomes | `NOT_DECIDED` |
| `PIVOT` | Định nghĩa độc lập programmatic oracle **nếu** thông tin parity và quyền hợp lệ | Không lấy oracle kín làm gold cho rater không được thấy dữ liệu | `NOT_DECIDED` |
| `STOP` | Dừng task không thể adjudicate hoặc rights invalid | Không coi STOP benchmark là FAIL model | `NOT_DECIDED` |
| `HOLD` | Giữ hồ sơ khi chưa xác minh witness/rater/rights | Không chạy workaround thực nghiệm | `CURRENT_DEFAULT` |

## B.1. Contract precision from three reviewer blockers

- **F-CONSTRUCT:** `UNKNOWN_VALID` requires a bounded *complete* visible evidence domain and a well-formed assertion whose truth cannot be established; an author-prelabel `TRUE/FALSE` losing its decisive witness is `REJECT_MISSING_WITNESS`, not UNKNOWN. `INVALID` means schema/referent failure, not a fact outcome. `FALSE` requires explicit negation or a visible same-time exclusivity axiom, not closed-world omission.
- **F-PARITY:** compare `MODEL_EFFECTIVE_VISIBLE_PREFIX` **after** prompt builder, tokenization and truncation (T4 context 256) to `RATER_EFFECTIVE_VISIBLE_EVIDENCE`. Both must retain the *decisive* witness; stored source hash alone does not prove this. Future receipt requires effective-prefix hash, token ranges, witness span, rater payload hash, rights and tokenizer pin; all currently `NOT_CAPTURED`. If rater sees W but model lost W, `HOLD_PARITY_LOST_AFTER_TRUNCATION` **before item freeze**.
- **F-DECISION:** scope is only `LOCATED_AT(entity_id, location_id, reference_time_id)`; use the five-branch decision table and priority rules in the [integrated contract](TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_SOURCE_CONTRACT_20261115.md). Requirements for Q1 question design are **not** actual gold/scorer admission. No thresholds/sample size are frozen. Three findings remain **AUTHOR_REMEDIATED_PENDING_DISTINCT_REREVIEW**.

## C. Q3 candidate — Minimal evidence và admission theo pha, chưa được thực hiện

**Phần đã có thể QA trên nguồn public:** đối chiếu mẫu Question Gate, source pins, original failure modes, thiết kế của `AD-02/03/04/05/06`, lịch sử negative evidence; không cần model, private gold hay TEST.

**Phần *không được coi đã đạt*:** item-level proof, gold/case construction, blinded independent rater calibration, lexical leakage audit, validity threshold, CI, sample size/power, data rights, exact checkpoint bytes và science budget. **Không bịa threshold**; chỉ khóa các yêu cầu logic trước khi prospective rubric được owner cho phép.

**Admission contract theo dependency:**
1. `DESIGN_ONLY`: quan hệ actor/object/goal/event/time, positive fact witness, vùng `UNKNOWN/INVALID`, lời hứa blind/source parity và failure conditions; không tạo actual gold.
2. `BEFORE_SOURCE_ACCESS_OR_AUTHORING`: `AD-01R` quyền dữ liệu, `AD-02` typed construct, `AD-03` visible witness feasibility, `AD-05` semantic hard negatives, `AD-06` one-variable pairing *nếu muốn causal contrasts*, `AD-08` authorization.
3. `BEFORE_FIXTURE_FREEZE`: từng witness/label không hidden-only; source-disjoint/no leakage, token budget/length parity `AD-01T`, prereg metric/rater roles/UNKNOWN/invalid/stop rule `AD-07`.
4. `BEFORE_MODEL_EXECUTION`: exact checkpoint/source `AD-00/01C`, separate owner science permit. **P0-A có thể kết thúc ở design HOLD mà không dùng checkpoint.**
5. `BEFORE_SCORING`: `AD-04` independent same-task gold/rater competence, packet parity `AD-03` recheck, `AD-05/06` recheck, locked thresholds/hidden audit custody.

**Logic phản chứng tương lai (không sản xuất fixtures):** mẫu thiếu witness ⇒ `HOLD_EVIDENCE_PARITY`; same visible source nhưng nhiều valid gold ⇒ `SIMPLIFY_OR_HOLD_CONSTRUCT`; chỉ hidden `E_core` chứa đáp án ⇒ `HOLD_HIDDEN_GOLD`; lexical cue dự đoán gold mà semantic contrast không rõ ⇒ `HOLD_SHORTCUT`; cùng task rater disagree chưa được giải quyết ⇒ `HOLD_RATER_COMPETENCE`; nguồn/rights chưa có ⇒ `HOLD_RIGHTS`. Những tình huống là logic contract, không là kết quả thực nghiệm.

**Endpoints tương lai chưa prereg:** tỷ lệ item có auditable witness; nhãn unambiguous/adjudicable theo tiêu chí prospective; agreement cùng task giữa independent judges; lỗi shortcut/false abstention; số item UNKNOWN/INVALID theo lớp. `SAMPLE_COUNT=NOT_SET`, `PASS_THRESHOLD=NOT_FROZEN`, `GPU_BUDGET=NOT_AUTHORIZED`; không tự thay thế bằng số 0/16 hoặc 28/32 lịch sử.

**Một vòng independent QA** khi scope được phép: reviewer khác tác giả đọc source pinned, thẩm định construct/negative fixture contracts/rights/custody, ước lượng feasibility từ giấy tờ; ghi `PASS_Q1_DESIGN_SCOPE` hoặc `HOLD_Q1_SOURCE_DESIGN`. Reviewer không được tự claim actual gold/rater/scorer admission.

## D. Q4 candidate — Chưa có quyết định

`QUESTION_REGISTERED_ON_MAIN=false`; `Q2_DESIGN_REVIEW_NOT_EXECUTED`; `Q3_DISTINCT_REVIEW_NOT_EXECUTED`; `OWNER_Q4_NOT_DECIDED`.  
`SCIENCE_AUTHORIZED=false`; `IMPLEMENTATION_BRANCH_AUTHORIZED=false`; `GOLD_AUTHORING_AUTHORIZED=false`; `SCORER_CONSTRUCTION_AUTHORIZED=false`.  
**No implementation HEAD or experimental receipts.** Quyết định cuối chỉ được đưa ra theo chính sách sau khi Q1–Q3 có evidence hợp lệ.

## Bước thực hiện tiếp theo — duy nhất

`TTM_P0A_MEASUREMENT_GOLD_INTEGRATED_REMEDIATION_EXACT_CANDIDATE_DISTINCT_REREVIEW_SINGLE_GATE`

Một lượt re-review độc lập duy nhất đối chiếu F-CONSTRUCT/F-PARITY/F-DECISION trên exact amended source/design P0-A và xác lập liệu có đủ lý do đăng ký Question Gate trên `main`; không mở F0–F2, gold, runner hoặc micro-permit.
