# TTM P0-A Q3 — Đáp án kiểm toán chứng cứ cho câu hỏi measurement

**Operation:** `TTM_P0A_MEAS_Q3_SOURCE_EVIDENCE_ANSWER_AND_DISTINCT_QA_SINGLE_GATE`  
**QuestionID:** `TTM-P0A-MEAS-Q001` · **Ngày:** 2026-11-16 · **Repository:** `minhtri22/TokenToModel-Lab`.  
**Exact source main:** [`8c38528a8d52f7262d0da188443a8166ec843a5f`](https://github.com/minhtri22/TokenToModel-Lab/commit/8c38528a8d52f7262d0da188443a8166ec843a5f), PR #23 Q2 governance đã merged và readback PASS.  
**Q3:** `AUTHOR_ANSWER_PREPARED · DISTINCT_Q3_QA_NOT_EXECUTED · OWNER_Q3_ADMISSION_PENDING`.  
**Scope:** `SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE`: không truy cập nguồn riêng tư, không tạo corpus/item/gold/scorer/rater packet/fixture, không chạy mô hình, không mở nhánh nghiên cứu hoặc science permit, không sửa `lineage.md`.

## 1. Câu hỏi và câu trả lời Q3 tối thiểu

**Câu hỏi Q1 đã đăng ký:** Liệu có thể xây dựng phép đo hợp lệ cho một triple nguyên tử `LOCATED_AT(entity_id,location_id,reference_time_id)`, với TRUE/FALSE/UNKNOWN trên item ELIGIBLE và REJECT riêng, đồng thời bảo đảm toàn bộ fact thay đổi nhãn đều hiển thị trong model-effective và rater-effective views, để hỗ trợ lựa chọn KEEP/SIMPLIFY/PIVOT/STOP/HOLD?

**Đáp án Q3 trên chứng cứ hiện hữu:** `DESIGN_CONDITIONS_IDENTIFIED · ACTUAL_FEASIBILITY_NOT_ESTABLISHED · HOLD_EVIDENCE_INSUFFICIENT`.

- **OBSERVED / trả lời được:** Q1/Q2/Q2-review đã mô tả hợp đồng logic typed triple và thứ tự hard veto. `UNKNOWN_VALID` yêu cầu bounded complete source domain, không phải missing witness; `FALSE` cần negation hiển thị hoặc axiom exclusivity áp dụng. `REJECT` không phải nhãn thứ tư. Cơ chế M0–M4 cạnh tranh và không độc quyền; các phương án có điều kiện phản chứng. Đây là tính đầy đủ của **bản thiết kế**, không phải kiểm chứng nguồn.
- **UNKNOWN / chưa trả lời được:** Không chứng cứ về lawful AD-01R source; không có candidate sampling frame và eligible/reject denominator; không biết item thật có đủ source/time completeness; chưa capture tokenizer/truncation/model-visible/rater-visible byte parity, hidden-gold provenance; chưa có calibrated independent source-adjudicated gold/rater hoặc prospective shortcut controls; chưa khóa metric/threshold/sample size/budget/STOP; AD-01C science permit thiếu.
- **INFERRED hợp lệ:** Vì nhiều hard veto không được xác minh, **chưa đủ căn cứ để triển khai phép đo, chấm mô hình hoặc gọi nó là gold benchmark**. Nhưng thiếu chứng cứ không phải chứng minh phép đo bất khả thi, không chứng minh nguyên nhân thất bại model. Không có science PASS/FAIL hay root-cause rank.

**Giới hạn:** Q3 không được “trả lời” bằng cách lấy lịch sử T4 NLL/TEST64, FRESH16 hoặc FINAL24 như prospective source/item test. Không replay sealed TEST/FINAL và không suy nguồn/private data không tồn tại chỉ vì chưa kiểm chứng.

## 2. Các exact sources kiểm toán

- [Q1 registered](https://github.com/minhtri22/TokenToModel-Lab/blob/8c38528a8d52f7262d0da188443a8166ec843a5f/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md), blob `6b29c962b48c4134c925935409433d4ae2804110`: đúng một QuestionID, TRUE/FALSE/UNKNOWN vs REJECT, planned metrics nhưng chưa khóa.
- [Question-First policy](https://github.com/minhtri22/TokenToModel-Lab/blob/8c38528a8d52f7262d0da188443a8166ec843a5f/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md), blob `af1a879a2552f100c6669cb9ab6dc98c930d2e19`: Q1→Q2→Q3→Q4, independent reviewer bắt buộc; lineage chỉ science adjudicated.
- [Q2 source report](https://github.com/minhtri22/TokenToModel-Lab/blob/8c38528a8d52f7262d0da188443a8166ec843a5f/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md), blob `f05223a3aa8724054fcd7e4e0b2a87392a2cf789`: M0–M4 và E0–E5.
- [Q2 distinct review](https://github.com/minhtri22/TokenToModel-Lab/blob/8c38528a8d52f7262d0da188443a8166ec843a5f/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_DISTINCT_SOURCE_REVIEW_20261115.md), blob `47576b60e50137972ce8cdf814415172eebbe6d9`: PASS source design, F-H01, F-M01–M04 và X17–X21, không có review nhân sự/tổ chức độc lập bên ngoài được xác nhận.
- [Q2 AD-order clarification](https://github.com/minhtri22/TokenToModel-Lab/blob/8c38528a8d52f7262d0da188443a8166ec843a5f/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_ADMISSION_ORDER_CLARIFICATION_20261116.md), blob `40bada66289b96aa7ba8c3b9d56f3a678e621ddb`: AD-01R trước truy cập nguồn; AD-02/03/05 chỉ sau lawful limited feasibility inspection nhưng trước production authoring.
- [Q2 owner closure](https://github.com/minhtri22/TokenToModel-Lab/blob/8c38528a8d52f7262d0da188443a8166ec843a5f/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_OWNER_ADMISSION_AND_CLOSURE_20261116.md), blob `39bfe616bd0906a11a4d30a3127546f73ffd6145`: GO_ACCEPT_Q2_SOURCE_ONLY, không cấp khoa học.
- [Active gate](https://github.com/minhtri22/TokenToModel-Lab/blob/8c38528a8d52f7262d0da188443a8166ec843a5f/docs/governance/ACTIVE_RESEARCH_GATE.md), blob `8b0892208e118c869a0bf1339fadd875fd805853`: Q2 accepted, Q3 pending, Q4 undecided, science HOLD.
- `lineage.md` preserved blob `3409e036241deb1da6674619a2abc834bea8a2d6` — không thêm design/Q3.

## 3. Sufficiency ledger (có yêu cầu chứng cứ không đồng nghĩa đã có chứng cứ)

| Class | Hiện trạng thực | Kết luận veto |
|---|---|---|
| `E0_RIGHTS` | `NOT_VERIFIED` — Rights/PII/copyright/third-party processing chưa được chứng thực. Không được đọc nguồn. | `HOLD_ACCESS` |
| `E1_CONSTRUCT` | `NOT_VALIDATED` — Chỉ có typed LOCATED_AT trên giấy; thiếu candidate frame/item thật, witness, authority, bounded temporal completeness, coverage và REJECT denominator. | `HOLD_SOURCE_CONSTRUCT` |
| `E2_PARITY` | `NOT_CAPTURED` — Chưa có model-effective token prefix, rater-effective payload, full material-fact set, builder/tokenizer/window SHA. | `HOLD_FULL_FACT_PARITY` |
| `E3_SHORTCUT` | `NOT_EXECUTED` — Fact-only/cue-only matched disjoint contrast chưa chạy; không nhận diện nhân quả. | `HOLD_CAUSAL_CLAIM` |
| `E4_GOLD_RATER` | `NOT_CALIBRATED` — Không có blinded source-grounded independent gold/rater calibration cùng task; agreement không bằng correctness. | `HOLD_GOLD_RATER` |
| `E5_PREREG` | `NOT_FROZEN` — Chỉ có planned metrics; endpoint, sample unit/N, coverage/reject denominators, acceptance threshold, uncertainty/power, STOP, budget chưa khóa. | `HOLD_NOT_PREREGISTERED` |
| `E6_RUNNER` | `NOT_AUTHORIZED` — Historical T4/FINAL24 chưa được dùng lại làm Q3 study; checkpoint rights/source pins/owner science permit còn thiếu. | `HOLD_NO_SCIENCE_PERMIT` |

Xem [Q3 evidence matrix](../../../artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q3_EVIDENCE_SUFFICIENCY_MATRIX_20261116.json) cho proof obligation và đối chứng từng nhóm. Không bịa N, coverage rate, CI, threshold, cost hay material fact set thực.

## 4. Các phản chứng có thể làm thay đổi đáp án

**F-H01 + X17 — selection/eligibility bias:** Nếu 1.000 candidate mà chỉ giữ 5 item dễ và điểm 5/5, accuracy conditional không nói gì về frame. Đây là ví dụ lý luận, không phải sample thật. Phải khóa candidate frame, eligible/reject/abstain counts, reasons, denominator và threshold coverage **trước khi thấy outcome**; không sửa numerator/denominator sau scoring.

**M2 + X14 + X19 — ontology/temporal closure:** Hai địa điểm ở cùng thời điểm không mặc nhiên mâu thuẫn khi không có visible exclusivity axiom. Source chỉ đầy đủ tới 09:00 không cho phép `UNKNOWN_VALID` về 10:00. Missing evidence/time invalid => REJECT/HOLD, không gán UNKNOWN. Nhãn FALSE phải có explicit negation hoặc exclusion axiom trong view hiệu lực.

**M1 + X13 + X15 — hidden gold, truncation và parity:** Một shared positive witness không chứng minh parity nếu rater thấy refutation mà model không thấy. Cần **full label-changing material fact sets** trong exact effective views sau builder/tokenizer/window; nguồn E_core/oracle hidden tách custody. Mất decisive witness vì truncation => gate HOLD, affected item REJECT, không UNKNOWN. Chưa có byte effective thực.

**M4 + X18 — inter-rater bias:** Hai rater đồng thuận về FALSE có thể cùng sai vì hiểu sai ontology. Phải có nguồn/ontology ground truth được đánh giá độc lập, blind same-task calibration, disagreement/abstention; agreement không phải accuracy.

**M3 + F-M04 — shortcut:** Đối chứng “fact-only” đổi thông tin và “cue-only” đổi hình thức phải có group-disjoint split và matching/counterbalancing lexical/position/length. Không giả định exact text giữ nguyên khi đổi fact. Không có prospective contrast, do đó causal mechanism không identified.

**F-M01 + X20 — quyền trước truy cập:** `AD-01R` và owner legal scope phải được thẩm định trước mọi source access; chỉ sau đó có thể thực hiện lawful read-only feasibility để đánh giá AD-02/03/05. Không đòi actual source completeness trước cả quyền đọc; không cấp permit thông qua Q3.

**X21 — primary REJECT precedence:** Một item có thể vừa thiếu decisive witness do truncation vừa unresolved referent; giữ mọi reason, khóa deterministic priority trước freeze, không chọn primary thuận theo outcome.

N01–N12/X13–X16 và X17–X21 chỉ là **logic adversarial design challenges**; Q3 không chạy fixture, không được chuyển thành runtime PASS.

## 5. Minimal discriminatory evidence — prospective dependencies, không phát hành nghiên cứu

1. **Access gate:** xác minh AD-01R và third-party rater/source rights/PII trước đọc nguồn (hiện HOLD).
2. **Construct feasibility gate:** sau lawful permission, một khảo sát prospective frame cố định với ontology/time/authority/witness closure, coverage/rejection reasons; không chọn item theo đáp án đã biết (chưa được phép thực hiện).
3. **Byte parity gate:** model-effective prefix sau tokenizer/truncation và rater-effective payload, toàn bộ fact đổi nhãn, hidden key custody (chưa capture).
4. **Adjudication/identifiability gate:** source-grounded independent gold/rater cùng task; separate fact-only/cue-only controls nếu claim causal (chưa được phép).
5. **Prereg+science gate:** metric/denominator/sample uncertainty/threshold/STOP/budget khóa trước outcome; checkpoint+runner rights AD-00/01C; Q4 owner GO và science permit riêng trước model execution.

Đây là một dependency structure của phương án về sau, **không phải** micro-permit hay kế hoạch chạy tự động trong Q3.

## 6. Q4 options chuẩn bị, không tự đưa quyết định Q4

| Option | Căn cứ hiện tại |
|---|---|
| KEEP | `NOT_JUSTIFIED`: thiếu actual lawful source/gold/parity/rater/threshold |
| SIMPLIFY | `NOT_JUSTIFIED`: không có lỗi localizable tiền-outcome |
| PIVOT | `NOT_JUSTIFIED`: chưa có proof impossibility và lawful alternative oracle |
| STOP | `NOT_JUSTIFIED`: thiếu rights record ≠ irreversible scientific impossibility |
| **HOLD_EVIDENCE_INSUFFICIENT** | **`SUPPORTED_FOR_ACTUAL_ADMISSION`**, không phải science FAIL |

**Author Q3 recommendation:** `ANSWER_SCOPED_HOLD_EVIDENCE_INSUFFICIENT` đủ để reviewer phân xử Q3; nếu được independent reviewer chấp nhận, owner có thể tại Q4 chọn `CLOSED_HOLD_EVIDENCE_INSUFFICIENT` với missing-evidence/remediation conditions hoặc một HOLD gate khác theo policy. **Q4 chưa quyết định**. Không có `GO_SCOPED_IMPLEMENT` hoặc science permit.

## 7. Distinct QA và điều kiện dừng

- `AUTHOR_Q3_SOURCE_ANSWER_PREPARED` không tương đương `Q3_ANSWER_REVIEWED`.
- `DISTINCT_Q3_QA_NOT_EXECUTED`: một reviewer khác tác giả phải kiểm exact Q3 commit, đối chất E0–E6, F-H01/F-M01–M04, quyền/ngữ nghĩa, negative cases và verdict Q3; không tự lấy author QA làm independent.
- `MERGE_HOLD_PENDING_DISTINCT_Q3_QA_AND_OWNER_ADMISSION`; `ACTIVE_RESEARCH_GATE.md` trên main vẫn Q3_PENDING; nhánh này chỉ governance docs, không phải research/implementation.
- Nếu source review độc lập không đạt, sửa **trong một integrated remediation cùng PR**, không chia micro-permits. Không đổi Q1/Q2, policy, historical evidence hoặc lineage.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_P0A_MEAS_Q3_EXACT_SOURCE_DISTINCT_ANSWER_REVIEW_AND_OWNER_Q3_ADMISSION_SINGLE_GATE` — reviewer độc lập kiểm toán exact HEAD, trả PASS/HOLD cho Q3 source-only; owner quyết định admission/merge riêng, chưa Q4/science.
