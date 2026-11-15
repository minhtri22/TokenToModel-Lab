# TTM — Active Research Gate (trạng thái quản trị duy nhất)

**Document type:** trạng thái điều phối có thể cập nhật, **KHÔNG** phải `lineage.md` và không phải scientific PASS/FAIL.  
**Policy:** [TTM-GOV-QF-20261115-V1](TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md) (đã có hiệu lực trên `main`).  
**Snapshot date:** 2026-11-15.  
**Location of this revision:** đề xuất trên **Draft PR #21**, chưa có hiệu lực trên `main` đến khi độc lập QA và owner cho merge.  
**Source-of-truth main baseline:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`; **Q3 independently reviewed exact amendment HEAD:** `c37ac0b3901eb6fd9c658d818c02e85f66b7936e` (subsequent Q3 receipt publication commit does NOT redefine the reviewed candidate). Original Q3 HEAD `3c53d062c7c6ff4218d80177253dd1c061ac6362`.

## 1. Trạng thái duy nhất của gate đang hoạt động

| Trường | Trạng thái tại candidate PR #21 |
|---|---|
| `policy_gate` | `TTM-GOV-QF-20261115-V1 · ACTIVE` |
| `active_question` | `SM4M-Q001` — duy nhất |
| `Q1` | `QUESTION_REGISTERED_ON_MAIN` |
| `Q2` | `AUTHOR_PACK_FROZEN · OWNER_EVIDENCE_SCOPE_ACCEPTED` (chỉ scope, không AD PASS) |
| `Q3` | `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED · DISTINCT_REVIEW_ON_PINNED_c37ac0b · NOT_SCIENCE_ADMISSION` |
| `Q3_original_exact_head` | `3c53d062c7c6ff4218d80177253dd1c061ac6362`; 2 HIGH (`Q3-F01/F02`), 1 MEDIUM (`Q3-F03`), 1 LOW (`Q3-F04`) |
| `Q4` | `OWNER_CLOSURE_NOT_DECIDED` |
| `root_cause` | `NOT_IDENTIFIED` |
| `baseline` | `KEEP_HISTORICAL_REFERENCE_ONLY`; `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE` |
| `AD-00..AD-08` | Original Q2 statuses preserved; **NONE blanket-upgraded to PASS** |
| `scientific_execution` | `HOLD · NOT_AUTHORIZED` |
| `new_research_branch` | `NOT_AUTHORIZED`; 0 newly authorized |
| `F0_F2` | `PAUSED_PENDING_OWNER_Q4_AND_SEPARATE_NEW_SCIENCE_ADMISSION` |
| `merge_decision` | `HOLD_MERGE_REVIEW_PENDING_EXPLICIT_OWNER_Q4`; Draft PR #21 **NOT_MERGED** |
| `lineage` | `APPEND_ONLY · UNCHANGED`; science PASS/FAIL only, never Q2/Q3 design QA |
| `main_sync` | `MAIN_SYNC_BLOCKED_PENDING_EXPLICIT_OWNER_Q4_AND_MERGE_GO_HOLD`; source-of-truth main remains unchanged |
| `other_programmes` | EmbeddingGemma 2 / Vector Memory outside Q001; historical state preserved |
| `branch_governance` | One short-lived `governance/sm4m-q001-q2-owner-scoped-q3-packet-20261115`; **NOT** research/implementation branch |

## 2. Truy vết sự kiện, không có trạng thái cạnh tranh

- `Q1`: câu hỏi back-to-basics có trên `main` tại `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`. Exact question [Q001](SM4M_Q001_BACK_TO_BASICS_ARCHITECTURE_DOC_CODE_EVIDENCE_20261115.md).
- `Q2`: bảy tài liệu tác giả exact pinned tại `3c53d062c7c6ff4218d80177253dd1c061ac6362` và bảng SHA trong [Owner Scope Acceptance](sm4m-q001/SM4M_Q001_OWNER_SCOPED_Q2_ACCEPTANCE_20261115.md). Tự QA 38/38, 64/64, 59/59 là **author scoped QA**.
- `Owner acceptance`: chỉ phạm vi và admission criteria, **không** công nhận causal cause hoặc execution permit.
- `Independent Q3`: verdict **`HOLD_Q3_REMEDIATION`** trên exact `3c53d062c7c6ff4218d80177253dd1c061ac6362`. [Original Q3 report](sm4m-q001/SM4M_Q001_Q3_DISTINCT_INDEPENDENT_REVIEW_20261115.md) và JSON receipt gốc là tệp `Q3_RECEIPT.json` trong ZIP do reviewer tải lên; SHA-256 JSON `529490652a7f140153292ec090496c1b5deec8ca36f54b25aa5b63c98cbd08ba`. **ZIP không có bản GitHub byte-exact trong PR này**; không được tuyên bố đã archive. Q3 HOLD là review design, không phải scientific FAIL.
- `Q3 remediation`: [one integrated amendment](sm4m-q001/SM4M_Q001_Q3_INTEGRATED_REMEDIATION_AND_PHASE_CONTRACT_20261115.md) điều chỉnh thời điểm AD-01/03/06, [versioned matrix v2](../../artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json), [versioned literature v2](sm4m-q001/SM4M_Q001_Q2_LITERATURE_TRIAGE_Q3_REMEDIATION_V2_20261115.md). **7 bản Q2 gốc vẫn giữ nguyên byte**; không chuyển trạng thái admission.
- `Q3 distinct re-readback`: **PASS** source/design on immutable amended HEAD `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`; [independent report](sm4m-q001/SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_REVIEW_20261115.md) and [exact independent receipt](../../artifacts/governance/sm4m-q001/SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_RECEIPT_20261115.json), SHA-256 `7809d6ffb6f803d953eaa368b70241c43bc6ccfbce91a0f463bf4e06023a3e6f`. No science PASS or Q4 grant.
- `Q4`: **PENDING**. [Owner Q4 decision request](sm4m-q001/SM4M_Q001_Q4_OWNER_DECISION_REQUEST_Q3_ACCEPTED_20261115.md) offers scoped GO/HOLD choices; it is NOT an owner authorization.

## 3. Quy tắc khoa học và branch

Giữ nguyên mọi kết quả T4 VAL/TEST, FRESH12/FRESH16, CF1, D1 EXP32, A/C, H-DATA-S1, FC01, D1 R1 theo đúng phạm vi. Không chạy lại TEST/FINAL đã niêm phong, không truy cập private bytes ngoài quyền hiện hành, không mở F0–F2, không đánh đồng QA source với science. Không tạo nhánh nghiên cứu mới, không dọn nhánh lịch sử và không merge implementation HOLD/FAIL. Các nhánh lịch sử không mặc nhiên là ACTIVE.

Các snapshot trước (policy lock, đăng ký Q1, owner acceptance, Q3 HOLD) được bảo toàn bằng lịch sử Git; **không giữ các câu “bước tiếp theo” lịch sử trong bản active này**.

## Bước thực hiện tiếp theo — duy nhất

`SM4M_Q001_Q4_OWNER_CLOSURE_AND_PR21_GOVERNANCE_ONLY_MERGE_GO_HOLD_SINGLE_GATE`

Independent Q3 PASS đã được nhận trên exact reviewed HEAD; **owner Q4 cần quyết định GO/HOLD** về closure Q001 và merge governance-only PR #21. Không tự merge, không mở khoa học và không kết luận root cause đã xác định.
