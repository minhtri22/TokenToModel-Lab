# TTM — Active Research Gate (bảng trạng thái quản trị chính)

**Source of truth:** `main` tại GitHub; [TTM Question-First Policy](TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md).  
**Đây là bảng điều phối sửa được, không phải khoa học lineage.**  
**Snapshot governance:** 2026-11-16. Q1 của `TTM-P0A-MEAS-Q001` đã đăng ký; Q2 đã `GO_ACCEPT_Q2_SOURCE_ONLY` (PR #23 merged/readback). Owner đã `GO_ACCEPT_Q3_SOURCE_ONLY_WITH_EMPIRICAL_HOLD` dựa trên Q3 independent source answer review (hiệu lực governance khi PR #24 merged/readback). Q4 vẫn chưa được quyết định, E0–E6 empirical HOLD, khoa học không được cấp phép. Q001 lịch sử vẫn CLOSED.

## 1. Trạng thái hiện hành của một Question Gate P0-A và Q001 lịch sử

| Trường | Trạng thái |
|---|---|
| `policy` | `TTM-GOV-QF-20261115-V1 · ACTIVE` |
| `active_scientific_question` | `TTM-P0A-MEAS-Q001 · Q1_QUESTION_REGISTERED · MEASUREMENT · SOURCE_ONLY` — một Question Gate đang hoạt động, không phải permit chạy science |
| `last_closed_question` | `SM4M-Q001` (giữ nguyên kết luận lịch sử) |
| `current_question_id` | [TTM-P0A-MEAS-Q001](ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md) — loại `MEASUREMENT`, owner `GO_REGISTER_Q1_SCOPED` |
| `current_Q1` | `QUESTION_REGISTERED_ON_MAIN` sau readback; P0-A independent design `PASS_Q1_DESIGN_SCOPE` tại `a8fd21f35d56a87f869df673b318d437ed0c8b31` |
| `current_Q2` | `Q2_FRAMEWORK_AND_ALTERNATIVES_EVALUATED · GO_ACCEPT_Q2_SOURCE_ONLY · PASS_Q2_SOURCE_DESIGN_SCOPED` (hiệu lực governance sau PR #23 merged/readback) |
| `current_Q3` | `Q3_ANSWER_REVIEWED · GO_ACCEPT_Q3_SOURCE_ONLY_WITH_EMPIRICAL_HOLD · PASS_Q3_SOURCE_ANSWER_SCOPED_WITH_EMPIRICAL_HOLD` — hiệu lực trên main sau PR #24 merged/readback; **không** phải science PASS |
| `current_Q4` | `Q4_PENDING · NOT_DECIDED_FOR_NEW_QUESTION` — owner chưa phân xử KEEP/SIMPLIFY/PIVOT/STOP/HOLD cho Q4 |
| `current_owner_scope` | `GO_REGISTER_Q1_SCOPED · GO_ACCEPT_Q2_SOURCE_ONLY · GO_ACCEPT_Q3_SOURCE_ONLY_WITH_EMPIRICAL_HOLD`; CHỈ governance/source paper; `NO_GOLD/NO_SCORER/NO_SOURCE_ACCESS/NO_MODEL_RUN` |
| `P0A_actual_gold` | `NOT_VALIDATED`, rights `NOT_VERIFIED`, material-fact parity `NOT_CAPTURED`, independent rater `NOT_CALIBRATED`, threshold `NOT_FROZEN` |
| `Q001_Q1` | `QUESTION_REGISTERED_ON_MAIN` (lịch sử, không phải Q1 của P0-A) |
| `Q001_Q2` | `AUTHOR_PACKET_FROZEN · OWNER_EVIDENCE_SCOPE_ACCEPTED` (lịch sử) |
| `Q001_Q3` | `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED` — [exact reviewed HEAD](https://github.com/minhtri22/TokenToModel-Lab/commit/c37ac0b3901eb6fd9c658d818c02e85f66b7936e), không phải science PASS |
| `Q001_Q4` | `OWNER_DECIDED · Q4_CLOSED_HOLD_NEW_SCIENCE` — [closure](sm4m-q001/SM4M_Q001_Q4_OWNER_CLOSURE_AND_GOVERNANCE_MERGE_DECISION_20261115.md) |
| `owner_merge_decision` | PR #21 historical governance; [PR #23](https://github.com/minhtri22/TokenToModel-Lab/pull/23) Q2 merged/readback. P0-A Q3 owner source-only admission: [PR #24](https://github.com/minhtri22/TokenToModel-Lab/pull/24) `MERGE_APPROVED_GOVERNANCE_DOCS_ONLY_IF_FINAL_QA_PASS`; actual provider merged/readback governs completion, không phải science merge |
| `root_cause` | `NOT_IDENTIFIED` |
| `T4_checkpoint` | `KEEP_HISTORICAL_REFERENCE_ONLY`; `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE` |
| `AD-00_to_AD-08` | Không nâng thành admission PASS; AD-01R/T/C phase-specific giữ NOT_VERIFIED; AD-03/06 design/freeze requirements |
| `scientific_execution` | `NOT_AUTHORIZED · HOLD` |
| `F0_F2` | `PAUSED_PENDING_PROSPECTIVE_ADMISSION_AND_Q4_OWNER_GO` — Q1 registration **không** mở F0–F2 |
| `next_science_question` | `TTM-P0A-MEAS-Q001` vẫn là Question Gate duy nhất; Q3 source-only accepted, **Q4_OWNER_DECISION_PENDING**; không mở QuestionID/nhánh nghiên cứu, gold, runner hoặc science permit |
| `research_branch_permission` | `NO_NEW_BRANCH_AUTHORIZED` |
| `lineage` | `UNMODIFIED_APPEND_ONLY · NO_Q3_Q4_DESIGN_ENTRY` |
| `scope_exclusions` | EmbeddingGemma 2 / Vector Memory độc lập, không là chứng cứ trực tiếp trong Q001 |
| `long_cot_reference` | `SM4M-REF-PROSPECTIVE-001 · OWNER_ACCEPTED_REFERENCE_ONLY`; [arXiv 2601.06002v2](sm4m-q001/SM4M_Q001_PROSPECTIVE_LITERATURE_WATCHLIST_20261115.md) |
| `source_of_truth_main` | GitHub `main` dynamic; Q2 merge `8c38528a8d52f7262d0da188443a8166ec843a5f`; Q3 exact author-reviewed `ebf243d078dedae623a5b4028e353b4570654dff`, Q3 evidence HEAD `1754af9429c4b0f97c944b349c37ae418ee2375b`; actual PR #24 merged HEAD phải đọc lại từ GitHub |

## 2. Lịch sử và quyền của các cổng

- Q1 được đăng ký trên `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`; Q2 source/architecture và causal evidence là **author scoped**, 38/38, 64/64, 59/59.
- Independent Q3 gốc HOLD trên `3c53d062c7c6ff4218d80177253dd1c061ac6362` do 4 finding; bản sửa Q3 PASS trên `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`, 18/18 symbolic QA, không xét khoa học. Sau đó hai deliverable reviewer lưu nguyên byte trong PR #21; SHA-256 JSON `7809d6ffb6f803d953eaa368b70241c43bc6ccfbce91a0f463bf4e06023a3e6f`.
- Owner Q4 explicit GO **chỉ cho đóng Q001 và merge docs/evidence**. Kết luận vẫn `ROOT_CAUSE_NOT_IDENTIFIED`, `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`; không mặc nhiên thoả mãn gold/rater, quyền dữ liệu, runner hay threshold.
- [Q4 owner closure](sm4m-q001/SM4M_Q001_Q4_OWNER_CLOSURE_AND_GOVERNANCE_MERGE_DECISION_20261115.md) quyết định `Q4_CLOSED_HOLD_NEW_SCIENCE`, `MERGE_APPROVED_GOVERNANCE_DOCS_ONLY`; merge chỉ thành công khi GitHub PR báo merged và main readback được xác minh.
- Bài [Mole-Syn arXiv:2601.06002v2](sm4m-q001/SM4M_Q001_PROSPECTIVE_LITERATURE_WATCHLIST_20261115.md) được owner chấp nhận làm **tài liệu tham khảo mở rộng**, không bổ sung vào nguồn causal Q2 frozen.
- `lineage.md` không được thêm Q2/Q3/Q4; chỉ append khi có scientific PASS/FAIL thật theo chính sách. Không chạy lại sealed TEST/FINAL, không sửa code architecture, không mở F0–F2 hay nhánh nghiên cứu mới.

## 3. Đăng ký P0-A Q1 mới — phân biệt design PASS với science HOLD

- **Owner đã GO riêng cho đăng ký Q1**: [Question Gate TTM-P0A-MEAS-Q001](ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md). Q1 đã đăng ký; Q2 và Q3 được owner chấp nhận **source-only**, Q4 chưa được quyết định. Văn bản Q1 gốc được bảo toàn.
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
- **State machine:** `Q3_ANSWER_REVIEWED` chỉ là answer-level governance. **Q4_PENDING/NOT_DECIDED**, không `GO_SCOPED_IMPLEMENT`, không tạo gold/scorer/benchmark/model/GPU/research branch. `lineage.md` giữ byte lịch sử; PR #24 chỉ được coi đã merged sau provider/readback thực.

## 6. Bước thực hiện tiếp theo — duy nhất

`TTM_P0A_MEAS_Q4_OWNER_ALTERNATIVES_HOLD_EVIDENCE_AND_FORMAL_QUESTION_CLOSURE_SINGLE_GATE`

Chỉ một lượt owner Q4 xét KEEP/SIMPLIFY/PIVOT/STOP/HOLD dựa trên Q1–Q3 pinned evidence, với khuyến nghị `HOLD_EVIDENCE_INSUFFICIENT`; không tự đóng Q4, không tạo experimental source/gold/scorer/runner, không cấp science permit, không mở branch hay micro-permit.
