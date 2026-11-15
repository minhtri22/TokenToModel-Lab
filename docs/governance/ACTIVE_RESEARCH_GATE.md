# TTM — Active Research Gate (bảng trạng thái quản trị chính)

**Source of truth:** `main` tại GitHub; [TTM Question-First Policy](TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md).  
**Đây là bảng điều phối sửa được, không phải khoa học lineage.**  
**Snapshot governance:** 2026-11-15, owner Q4 GO đã được quyết định. GitHub PR #21 và `main` hiện tại là nguồn kiểm chứng *tình trạng merge thực tế*; không tự điền commit SHA tự tham chiếu.

## 1. Trạng thái chính thức sau owner Q4

| Trường | Trạng thái |
|---|---|
| `policy` | `TTM-GOV-QF-20261115-V1 · ACTIVE` |
| `active_scientific_question` | `NONE · Q001_CLOSED` — không tự đăng ký câu hỏi kế tiếp |
| `last_closed_question` | `SM4M-Q001` |
| `Q1` | `QUESTION_REGISTERED_ON_MAIN` (lịch sử) |
| `Q2` | `AUTHOR_PACKET_FROZEN · OWNER_EVIDENCE_SCOPE_ACCEPTED` |
| `Q3` | `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED` — [exact reviewed HEAD](https://github.com/minhtri22/TokenToModel-Lab/commit/c37ac0b3901eb6fd9c658d818c02e85f66b7936e), không phải science PASS |
| `Q4` | `OWNER_DECIDED · Q4_CLOSED_HOLD_NEW_SCIENCE` — [closure](sm4m-q001/SM4M_Q001_Q4_OWNER_CLOSURE_AND_GOVERNANCE_MERGE_DECISION_20261115.md) |
| `owner_merge_decision` | `MERGE_APPROVED_GOVERNANCE_DOCS_ONLY` cho [PR #21](https://github.com/minhtri22/TokenToModel-Lab/pull/21); **provider PR state xác định đã merge thực tế hay chưa** |
| `root_cause` | `NOT_IDENTIFIED` |
| `T4_checkpoint` | `KEEP_HISTORICAL_REFERENCE_ONLY`; `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE` |
| `AD-00_to_AD-08` | Không nâng thành admission PASS; AD-01R/T/C phase-specific giữ NOT_VERIFIED; AD-03/06 design/freeze requirements |
| `scientific_execution` | `NOT_AUTHORIZED · HOLD` |
| `F0_F2` | `PAUSED_PENDING_NEW_PROSPECTIVE_QUESTION_AND_ADMISSION` |
| `next_science_question` | `NONE_REGISTERED`; không có permit hoặc nhánh thực nghiệm mới |
| `research_branch_permission` | `NO_NEW_BRANCH_AUTHORIZED` |
| `lineage` | `UNMODIFIED_APPEND_ONLY · NO_Q3_Q4_DESIGN_ENTRY` |
| `scope_exclusions` | EmbeddingGemma 2 / Vector Memory độc lập, không là chứng cứ trực tiếp trong Q001 |
| `long_cot_reference` | `SM4M-REF-PROSPECTIVE-001 · OWNER_ACCEPTED_REFERENCE_ONLY`; [arXiv 2601.06002v2](sm4m-q001/SM4M_Q001_PROSPECTIVE_LITERATURE_WATCHLIST_20261115.md) |
| `source_of_truth_main` | GitHub `main` dynamic; baseline trước PR #21 `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`; **actual post-merge SHA phải đọc từ GitHub** |

## 2. Lịch sử và quyền của các cổng

- Q1 được đăng ký trên `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`; Q2 source/architecture và causal evidence là **author scoped**, 38/38, 64/64, 59/59.
- Independent Q3 gốc HOLD trên `3c53d062c7c6ff4218d80177253dd1c061ac6362` do 4 finding; bản sửa Q3 PASS trên `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`, 18/18 symbolic QA, không xét khoa học. Sau đó hai deliverable reviewer lưu nguyên byte trong PR #21; SHA-256 JSON `7809d6ffb6f803d953eaa368b70241c43bc6ccfbce91a0f463bf4e06023a3e6f`.
- Owner Q4 explicit GO **chỉ cho đóng Q001 và merge docs/evidence**. Kết luận vẫn `ROOT_CAUSE_NOT_IDENTIFIED`, `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`; không mặc nhiên thoả mãn gold/rater, quyền dữ liệu, runner hay threshold.
- [Q4 owner closure](sm4m-q001/SM4M_Q001_Q4_OWNER_CLOSURE_AND_GOVERNANCE_MERGE_DECISION_20261115.md) quyết định `Q4_CLOSED_HOLD_NEW_SCIENCE`, `MERGE_APPROVED_GOVERNANCE_DOCS_ONLY`; merge chỉ thành công khi GitHub PR báo merged và main readback được xác minh.
- Bài [Mole-Syn arXiv:2601.06002v2](sm4m-q001/SM4M_Q001_PROSPECTIVE_LITERATURE_WATCHLIST_20261115.md) được owner chấp nhận làm **tài liệu tham khảo mở rộng**, không bổ sung vào nguồn causal Q2 frozen.
- `lineage.md` không được thêm Q2/Q3/Q4; chỉ append khi có scientific PASS/FAIL thật theo chính sách. Không chạy lại sealed TEST/FINAL, không sửa code architecture, không mở F0–F2 hay nhánh nghiên cứu mới.

## 3. Gate tiếp theo (thiết kế-only, không tự mở nghiên cứu)

**Bước thực hiện tiếp theo — duy nhất:**

`TTM_POST_Q001_RESEARCH_DIRECTION_PRIORITY_MATRIX_SOURCE_ONLY_SINGLE_GATE`

Chỉ lập một ma trận ưu tiên hướng nghiên cứu Small-4M (measurement/gold, objective/data, decoder/context, capacity) cùng tham khảo reasoning/Long CoT trong toàn TTM. Bảo toàn các kết quả độc lập ngoài scope, hiện trạng `main` và `lineage.md`. Trước bất kỳ science execution phải có một Question Gate mới được owner cho phép/đăng ký và đáp ứng đủ admission/custody, không tạo chuỗi micro-permit.
