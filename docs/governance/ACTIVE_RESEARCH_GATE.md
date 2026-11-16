# TTM — Active Research Gate (bảng trạng thái quản trị chính)

**Source of truth:** `main` tại GitHub; [TTM Question-First Policy](TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md).  
**Đây là bảng điều phối sửa được, không phải khoa học lineage.**  
**Snapshot governance:** 2026-11-16. QuestionID lịch sử `TTM-P0A-MEAS-Q001` vẫn `Q4_CLOSED_HOLD_EVIDENCE_INSUFFICIENT`, P0B không được mở. Owner vừa yêu cầu đăng ký **một Question Gate ENGINEERING khác biệt** `TTM-SM4M-DIAG-Q001` để chẩn đoán overfit/generation/generality bằng token IDs tổng hợp; **Q1 đăng ký trên main sau governance merge/readback**, Q2/Q3 source design chỉ do tác giả đề xuất, Q4 owner execution vẫn PENDING. **Không có quyền implementation branch, model/checkpoint access, science execution, hay thay đổi lineage**. E0–E6 của P0A vẫn HOLD. `SM4M-Q001` lịch sử CLOSED giữ nguyên.

## 0. ENGINEERING Question Gate mới — phân biệt rõ với P0A đã đóng

| Trường | Trạng thái |
|---|---|
| `active_question_id` | [TTM-SM4M-DIAG-Q001](ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_REGISTERED_QUESTION_AND_ONEPACK_20261116.md) · `ENGINEERING · Q1_REGISTERED_SOURCE_ONLY` (hiệu lực sau governance merge/readback) |
| `question_goal` | Chẩn đoán trực tiếp P02/T4: tải đúng checkpoint → loss/gradient → tiny overfit → novel pairing/counterfactual → full-vocabulary greedy vs restricted candidate |
| `Q2_Q3` | `AUTHOR_SOURCE_DESIGN_PREPARED · INDEPENDENT_REVIEW_NOT_EXECUTED`; không phải Q2/Q3 đã được owner accept |
| `Q4` | `OWNER_SCOPED_IMPLEMENT_AND_ONE_SHOT_EXECUTION_GO_HOLD_PENDING` |
| `I1_I4` | `NOT_AUTHORIZED · NOT_EXECUTED` |
| `checkpoint_model_rights` | `AD00_AD01C_E6_NOT_VERIFIED`; không có quyền truy cập weights hoặc chạy mô hình |
| `execution_permit` | `NO`; một binary owner GO/HOLD sau distinct preexec review |
| `protocol` | [Frozen-design JSON](../../artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_FROZEN_ONEPACK_PREEXEC_CONTRACT_20261116.json); fixture/runner bytes vẫn chưa tạo, chưa hash |
| `previous_owner_choice` | `KEEP_NO_ACTIVE_QUESTION` trước thời điểm owner **đồng ý đăng ký Question Gate ENGINEERING khác biệt**; không phải phép cấp science |
| `scientific_lineage` | `UNCHANGED` |

## 1. Hồ sơ lịch sử P0-A và Q001 đã đóng — các trường Q1–Q4 dưới đây không phải trạng thái của DIAG-Q001

| Trường | Trạng thái |
|---|---|
| `policy` | `TTM-GOV-QF-20261115-V1 · ACTIVE` |
| `active_scientific_question` | `TTM-SM4M-DIAG-Q001 · ENGINEERING_Q1_REGISTERED_SOURCE_ONLY` — owner yêu cầu một Question Gate khác biệt, Q4/chạy mô hình vẫn HOLD; P0A Q001 tiếp tục CLOSED_HOLD |
| `last_closed_question` | `TTM-P0A-MEAS-Q001 · Q4_CLOSED_HOLD_EVIDENCE_INSUFFICIENT`; `SM4M-Q001` vẫn giữ kết luận CLOSED lịch sử |
| `current_question_id` | [TTM-SM4M-DIAG-Q001](ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_REGISTERED_QUESTION_AND_ONEPACK_20261116.md) · `Q1_REGISTERED_SOURCE_ONLY`; last closed [TTM-P0A-MEAS-Q001](ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_OWNER_CLOSED_HOLD_GOVERNANCE_CLOSURE_20261116.md) remains `CLOSED_HOLD_EVIDENCE_INSUFFICIENT` |
| `current_Q1` | `QUESTION_REGISTERED_ON_MAIN` sau readback; P0-A independent design `PASS_Q1_DESIGN_SCOPE` tại `a8fd21f35d56a87f869df673b318d437ed0c8b31` |
| `current_Q2` | `Q2_FRAMEWORK_AND_ALTERNATIVES_EVALUATED · GO_ACCEPT_Q2_SOURCE_ONLY · PASS_Q2_SOURCE_DESIGN_SCOPED` (hiệu lực governance sau PR #23 merged/readback) |
| `current_Q3` | `Q3_ANSWER_REVIEWED · GO_ACCEPT_Q3_SOURCE_ONLY_WITH_EMPIRICAL_HOLD · PASS_Q3_SOURCE_ANSWER_SCOPED_WITH_EMPIRICAL_HOLD` — hiệu lực trên main sau PR #24 merged/readback; **không** phải science PASS |
| `current_Q4` | `OWNER_DECIDED · Q4_CLOSED_HOLD_EVIDENCE_INSUFFICIENT · GO_Q4_CLOSE_HOLD_EVIDENCE_INSUFFICIENT` — đóng hồ sơ chứng cứ, không đóng vĩnh viễn giả thuyết; governance effect sau PR #25 merged/readback |
| `current_owner_scope` | `GO_REGISTER_Q1_SCOPED · GO_ACCEPT_Q2_SOURCE_ONLY · GO_ACCEPT_Q3_SOURCE_ONLY_WITH_EMPIRICAL_HOLD · GO_Q4_CLOSE_HOLD_EVIDENCE_INSUFFICIENT`; CHỈ governance/source paper; `NO_GOLD/NO_SCORER/NO_SOURCE_ACCESS/NO_MODEL_RUN` |
| `P0A_actual_gold` | `NOT_VALIDATED`, rights `NOT_VERIFIED`, material-fact parity `NOT_CAPTURED`, independent rater `NOT_CALIBRATED`, threshold `NOT_FROZEN` |
| `Q001_Q1` | `QUESTION_REGISTERED_ON_MAIN` (lịch sử, không phải Q1 của P0-A) |
| `Q001_Q2` | `AUTHOR_PACKET_FROZEN · OWNER_EVIDENCE_SCOPE_ACCEPTED` (lịch sử) |
| `Q001_Q3` | `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED` — [exact reviewed HEAD](https://github.com/minhtri22/TokenToModel-Lab/commit/c37ac0b3901eb6fd9c658d818c02e85f66b7936e), không phải science PASS |
| `Q001_Q4` | `OWNER_DECIDED · Q4_CLOSED_HOLD_NEW_SCIENCE` — [closure](sm4m-q001/SM4M_Q001_Q4_OWNER_CLOSURE_AND_GOVERNANCE_MERGE_DECISION_20261115.md) |
| `owner_merge_decision` | [PR #24](https://github.com/minhtri22/TokenToModel-Lab/pull/24) Q3 đã merge; P0-A Q4 owner `MERGE_APPROVED_GOVERNANCE_ONLY_PR25_IF_FINAL_QA_PASS` cho [PR #25](https://github.com/minhtri22/TokenToModel-Lab/pull/25), chỉ governance+evidence (không phải science/code); actual provider merged/readback quyết định hoàn thành |
| `root_cause` | `NOT_IDENTIFIED` |
| `T4_checkpoint` | `KEEP_HISTORICAL_REFERENCE_ONLY`; `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE` |
| `AD-00_to_AD-08` | Không nâng thành admission PASS; AD-01R/T/C phase-specific giữ NOT_VERIFIED; AD-03/06 design/freeze requirements |
| `scientific_execution` | `NOT_AUTHORIZED · HOLD` |
| `F0_F2` | `PAUSED_Q4_CLOSED_HOLD · PROSPECTIVE_ADMISSION_NOT_ESTABLISHED · NO_SCIENCE_PERMIT` — Q4 GO chỉ đóng governance, không phải GO thực thi F0–F2 |
| `next_science_question` | `TTM-SM4M-DIAG-Q001` is **ENGINEERING Q1**, not a science-execution permit; no other QuestionID or new research branch permitted; owner Q4 onepack GO/HOLD pending after distinct preexec review |
| `research_branch_permission` | `NO_NEW_BRANCH_AUTHORIZED` |
| `lineage` | `UNMODIFIED_APPEND_ONLY · NO_Q3_Q4_DESIGN_ENTRY` |
| `scope_exclusions` | EmbeddingGemma 2 / Vector Memory độc lập, không là chứng cứ trực tiếp trong Q001 |
| `long_cot_reference` | `SM4M-REF-PROSPECTIVE-001 · OWNER_ACCEPTED_REFERENCE_ONLY`; [arXiv 2601.06002v2](sm4m-q001/SM4M_Q001_PROSPECTIVE_LITERATURE_WATCHLIST_20261115.md) |
| `source_of_truth_main` | GitHub `main` dynamic; Q3 merged baseline `2d1b93f566c8a5c675d00d9ba9fc58c3af39fab2`; Q4 original reviewed author HEAD `f2ad56e373c453c92a321dc12fe4253a4b870864`, independent reviewer evidence HEAD `e3c883e2d688d672c82400ebb021a263b86eb05b`. PR #25 exact merge HEAD chỉ xác nhận qua provider và postmerge main readback |

## 2. Lịch sử và quyền của các cổng

- Q1 được đăng ký trên `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`; Q2 source/architecture và causal evidence là **author scoped**, 38/38, 64/64, 59/59.
- Independent Q3 gốc HOLD trên `3c53d062c7c6ff4218d80177253dd1c061ac6362` do 4 finding; bản sửa Q3 PASS trên `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`, 18/18 symbolic QA, không xét khoa học. Sau đó hai deliverable reviewer lưu nguyên byte trong PR #21; SHA-256 JSON `7809d6ffb6f803d953eaa368b70241c43bc6ccfbce91a0f463bf4e06023a3e6f`.
- Owner Q4 explicit GO **chỉ cho đóng Q001 và merge docs/evidence**. Kết luận vẫn `ROOT_CAUSE_NOT_IDENTIFIED`, `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`; không mặc nhiên thoả mãn gold/rater, quyền dữ liệu, runner hay threshold.
- [Q4 owner closure](sm4m-q001/SM4M_Q001_Q4_OWNER_CLOSURE_AND_GOVERNANCE_MERGE_DECISION_20261115.md) quyết định `Q4_CLOSED_HOLD_NEW_SCIENCE`, `MERGE_APPROVED_GOVERNANCE_DOCS_ONLY`; merge chỉ thành công khi GitHub PR báo merged và main readback được xác minh.
- Bài [Mole-Syn arXiv:2601.06002v2](sm4m-q001/SM4M_Q001_PROSPECTIVE_LITERATURE_WATCHLIST_20261115.md) được owner chấp nhận làm **tài liệu tham khảo mở rộng**, không bổ sung vào nguồn causal Q2 frozen.
- `lineage.md` không được thêm Q2/Q3/Q4; chỉ append khi có scientific PASS/FAIL thật theo chính sách. Không chạy lại sealed TEST/FINAL, không sửa code architecture, không mở F0–F2 hay nhánh nghiên cứu mới.

## 3. Đăng ký P0-A Q1 mới — phân biệt design PASS với science HOLD

- **Owner Q1–Q4:** [Question Gate TTM-P0A-MEAS-Q001](ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md) đã đăng ký; Q2 và Q3 được chấp nhận **source-only**; Q4 đã có owner `GO_Q4_CLOSE_HOLD_EVIDENCE_INSUFFICIENT`, [closure Q4](ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_OWNER_CLOSED_HOLD_GOVERNANCE_CLOSURE_20261116.md), không có science permit. Văn bản Q1 gốc bảo toàn.
- **Independent AI source/design**: [báo cáo source-only](ttm-post-q001/TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_20261115.md) và [receipt byte-exact](../../artifacts/governance/ttm-post-q001/TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_RECEIPT_20261115.json), `PASS_Q1_DESIGN_SCOPE` tại exact HEAD `a8fd21f35d56a87f869df673b318d437ed0c8b31`; human organizational independence `NOT_EXTERNALLY_ATTESTED`.
- **X13/X14/X15**: full material-fact parity (không chỉ shared W) trước freeze; exclusivity axiom không được giả định trước authoring; gate-HOLD/item-REJECT precedence rõ trước freeze. X16 nhắc design PASS không cấp runtime admission.
- **Không có actual benchmark/gold, rights, rater calibration, prompt/token parity receipt, sample/threshold hay GPU budget được phê duyệt**. `lineage.md` không đổi. Ngay cả khi PR #22 được merge governance-only, đó **không phải** `GO_SCOPED_IMPLEMENT` hoặc science result.

## 4. P0-A Q2 — owner paper acceptance, không phải science

- **Owner Q2:** `GO_ACCEPT_Q2_SOURCE_ONLY`, chỉ chấp nhận M0–M4, năm option và minima trên giấy. [Owner governance closure](ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_OWNER_ADMISSION_AND_CLOSURE_20261116.md) giữ exact original reviewed HEAD `8bf0601c716b5f6395e3b758ee066ff41c9a554d`.
- **Independent AI source/design:** [Markdown](ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_DISTINCT_SOURCE_REVIEW_20261115.md) · [receipt JSON](../../artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_DISTINCT_SOURCE_REVIEW_RECEIPT_20261115.json), `PASS_Q2_SOURCE_DESIGN_SCOPED`; human/organizational independence `NOT_EXTERNALLY_ATTESTED`.
- **Forward hard veto:** F-H01 selection/coverage denominator; F-M01–F-M04 và X17–X21. [Clarification AD-01R vs AD-02/03/05](ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_ADMISSION_ORDER_CLARIFICATION_20261116.md) không cấp source access. `AD-01R/T/C`, full parity, gold, scorer, rater, thresholds, checkpoint, owner science permit vẫn `HOLD/NOT_VERIFIED/NOT_AUTHORIZED`.
- **Governance merge:** PR #23 chỉ được xem là hoàn thành khi actual GitHub merged/readback PASS; `lineage.md` không đổi, không có science PASS/FAIL.

## 5. P0-A Q3 — owner accepted source-only answer, empirical HOLD

- **Owner Q3:** `GO_ACCEPT_Q3_SOURCE_ONLY_WITH_EMPIRICAL_HOLD`, nguồn giấy/thiết kế; [owner closure](ttm-post-q001/TTM_P0A_MEAS_Q001_Q3_OWNER_SOURCE_ONLY_ADMISSION_AND_CLOSURE_20261116.md), owner không cấp Q4/science permit.
- **Independent AI source answer review:** [report](ttm-post-q001/TTM_P0A_MEAS_Q001_Q3_DISTINCT_SOURCE_ANSWER_REVIEW_20261116.md) · [JSON receipt](../../artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q3_DISTINCT_SOURCE_ANSWER_REVIEW_RECEIPT_20261116.json), reviewed original Q3 author HEAD `ebf243d078dedae623a5b4028e353b4570654dff`, evidence HEAD `1754af9429c4b0f97c944b349c37ae418ee2375b`, `PASS_Q3_SOURCE_ANSWER_SCOPED_WITH_EMPIRICAL_HOLD`; human/organizational independence `NOT_EXTERNALLY_ATTESTED`.
- **Q3 answer:** `DESIGN_CONDITIONS_IDENTIFIED · ACTUAL_FEASIBILITY_NOT_ESTABLISHED · HOLD_EVIDENCE_INSUFFICIENT`. E0 rights `NOT_VERIFIED`; E1 source/ontology `NOT_VALIDATED`; E2 parity `NOT_CAPTURED`; E3 shortcut controls `NOT_EXECUTED`; E4 gold/rater `NOT_CALIBRATED`; E5 prereg `NOT_FROZEN`; E6 runner/permit `NOT_AUTHORIZED`.
- **Forward risks:** F-H01/X17 selection frame/coverage denominator; X13/15 full effective-view parity; X14/19 temporal source closure/ontology; X18 independent source-grounded rater correctness; X20 rights ordering; X21 deterministic multi-reason REJECT, plus F-M01–F-M04. Các điều kiện này không được nâng PASS.
- **State machine:** `Q3_ANSWER_REVIEWED` chỉ là answer-level governance. **Q4_OWNER_CLOSED_HOLD_EVIDENCE_INSUFFICIENT**, không `GO_SCOPED_IMPLEMENT`, không tạo gold/scorer/benchmark/model/GPU/research branch. `lineage.md` giữ byte lịch sử; PR #24 đã merged với provider/readback, PR #25 cần provider/readback trước khi kết luận closure trên main.

## 6. P0-A Q4 — owner CLOSED_HOLD, không phải science FAIL

- **Owner Q4:** `GO_Q4_CLOSE_HOLD_EVIDENCE_INSUFFICIENT` (ngày 2026-11-16), `TTM-P0A-MEAS-Q001=Q4_CLOSED_HOLD_EVIDENCE_INSUFFICIENT`. [Q4 owner closure](ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_OWNER_CLOSED_HOLD_GOVERNANCE_CLOSURE_20261116.md); đây là closure của vòng Q1–Q4 trên chứng cứ hiện tại, không phải STOP vĩnh viễn.
- **Q4 independent AI source decision:** [review](ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_DISTINCT_DECISION_FRAMEWORK_REVIEW_20261116.md) và [receipt](../../artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_DISTINCT_DECISION_FRAMEWORK_REVIEW_RECEIPT_20261116.json), exact author reviewed `f2ad56e373c453c92a321dc12fe4253a4b870864`, reviewer evidence `e3c883e2d688d672c82400ebb021a263b86eb05b`; verdict `PASS_Q4_SOURCE_DECISION_FRAMEWORK_SCOPED`. Human/organizational attestation `NOT_EXTERNALLY_ATTESTED`.
- **Five alternatives:** KEEP/SIMPLIFY/PIVOT/STOP thiếu cơ sở; chọn HOLD. E0 rights `NOT_VERIFIED`; E1 ontology/selection `NOT_VALIDATED`; E2 full effective parity `NOT_CAPTURED`; E3 causal shortcuts `NOT_EXECUTED`; E4 gold/rater `NOT_CALIBRATED`; E5 prereg `NOT_FROZEN`; E6 runner `NOT_AUTHORIZED`. Root cause `NOT_IDENTIFIED`.
- **Provider merge:** [PR #25](https://github.com/minhtri22/TokenToModel-Lab/pull/25) `MERGE_APPROVED_GOVERNANCE_ONLY_IF_FINAL_QA_PASS`, không merge scientific implementation; provider `merged=true` và main readback bắt buộc. Scientific `lineage.md` unchanged.
- **Next active question:** `NONE_AUTOMATIC`. Future evidence+new Question Gate cần owner riêng.

## 7. Bước thực hiện tiếp theo — duy nhất

`TTM_SM4M_DIAG_Q001_SINGLE_DISTINCT_PREEXEC_REVIEW_AND_OWNER_GO_HOLD_ONEPACK`

Một lượt review độc lập Q1–Q3 thiết kế chẩn đoán trực tiếp (24 train/56 nontrain, checkpoint T4 exact), rồi trình owner **đúng một quyết định conditional GO/HOLD cho implementation + one-shot CPU run**. Đây không phải quyền chạy có sẵn. Không mở micro-permits, không lặp câu hỏi ontology P0A, không đọc sealed TEST/FINAL. Chỉ sau owner GO và actual I1 rights/custody/runner negative QA PASS mới được I2.
