# TTM — Trạng thái nghiên cứu hiện hành trên main (Active Research Gate)

**Loại:** bảng điều phối được phép cập nhật, **không phải `lineage.md`** và không phải chứng cứ science PASS/FAIL.  
**Chính sách điều khiển:** [TTM-GOV-QF-20261115-V1](TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md).  
**Hiệu lực ban đầu:** commit quản trị thêm tài liệu này vào `main` (xem Git history, không tự bịa commit SHA của chính tài liệu).  
**Ngày snapshot:** 2026-11-15. **Đây là nguồn trạng thái chủ động tại thời điểm publish**, không là tuyên bố mọi nhánh hiện có đã được kiểm toán.

## 1. Gate duy nhất và trạng thái

| Trường | Giá trị |
|---|---|
| `policy_gate` | `TTM-GOV-QF-20261115-V1` — `GOVERNANCE_LOCKED_EFFECTIVE_ON_MAIN_AT_INTRODUCING_COMMIT` (policy still unchanged) |
| `active_scientific_question` | `SM4M-Q001 · Q2_AUTHOR_PACKET_FROZEN · OWNER_Q2_SCOPE_ACCEPTED · Q3_REVIEW_AUTHORIZED_NOT_EXECUTED · Q4_NOT_DECIDED` |
| `next_question_candidate` | `NONE_PENDING_Q001_CLOSURE`; F0–F2 **not authorized** until SM4M-Q001 Q4 owner closure |
| `scientific_execution` | `NOT_AUTHORIZED` |
| `new_research_branch_permission` | `NO` cho đến khi question gate được đăng ký, đánh giá, kết luận và owner quyết định |
| `main_canonical_ref` | `main`; kiểm tra HEAD mới nhất **khi bắt đầu mỗi gate**, không ghi một SHA tương lai sai |
| `research_gate_control` | `ONE_ACTIVE_QUESTION_ONLY · SM4M-Q001_REGISTERED` |
| `new_branch_count_authorized` | 0 |
| `historical_branches` | GitHub snapshot quan sát 68 refs, **không đồng nghĩa 68 ACTIVE**; chưa được phép xóa |
| `open_pull_requests` | Snapshot 3 PR Draft #13, #14, #18; không tự merge |
| `lineage` | L0000–L0029 trên main là lịch sử append-only; từ policy này **chỉ thêm scientific PASS/FAIL có implement HEAD** |
| `policy_bootstrap_merge_scope` | Docs-only, không có science/implementation merge |

## 2. Các nghiên cứu cần bảo toàn và routing

| Nhóm | Pinned reference / source | Trạng thái điều phối theo gate |
|---|---|---|
| Small-4M Foundation First F2 | `research/ttm-small4m-foundation-first-single-gate-20261115` exact HEAD `9b55596f580b36b436cf6bdb2ed5a4e45c6992de` | Thiết kế F2 đã tác giả tự QA có phạm vi 82/82; hai verdict độc lập trước đó `HOLD_REVISE_DESIGN`; bản sửa mới `DISTINCT_REVIEW_PENDING`. **PAUSED_PENDING_ARCHITECTURE_DECISION**; không merge code và không thực thi |
| Foundation F01–F05 | Owner design decision tại `c233dff20b9b020aefd732ce62bfa2e7aebd3985` | `GO_DESIGN_SCOPED` **chỉ** kết thúc năm finding ở phạm vi thiết kế; không là science GO |
| T4 checkpoint, VAL/TEST, FRESH16, A/C, H-DATA, FC01 | Exact science refs trong F0/F1 của nhánh Foundation First và `lineage.md` hiện hữu | Kết quả khoa học/FAIL/HOLD lịch sử bất biến; không chạy lại TEST/FINAL, không score lại |
| EmbeddingGemma 2 / Vector Memory / TTM×SIX | Branch/historical evidence theo global inventory trên main | Giữ riêng kết quả scoped; không tự mở nghiên cứu, không nhập vào Small-4M |
| T5/T6/P07/P08 / PR Draft | Theo `docs/governance/` và PR trên GitHub | Engineering / infrastructure / Draft giữ nguyên; không tự merge |

## 3. Quy tắc cập nhật sau mỗi gate

- Khi Q1 mới được owner cho phép đăng ký, tạo **một** question-record trên `main`, gắn QuestionID và exact baseline HEAD; cập nhật ô `active_scientific_question`. Không tạo nhánh hoặc chạy science.
- Khi Q4 có câu trả lời + reviewer/owner decision, ghi `CLOSED_GO_SCOPED/CLOSED_HOLD/CLOSED_STOP`, bằng chứng/đường dẫn và quyết định hướng tiếp theo vào **bản ghi quản trị có thể sửa này** trên `main` trước mở nhánh kế tiếp.
- Khi I4 kết thúc một phần nghiên cứu, luôn ghi quyết định `MERGE_APPROVED` / `EVIDENCE_ONLY_NO_MERGE` / `NO_MERGE_NEEDED` / `HOLD_MERGE_REVIEW` trong closure source, giữ pinned implement HEAD. Nếu có science PASS/FAIL **đúng nghĩa**, append riêng vào `lineage.md`; nếu không, tuyệt đối không append.
- Không cập nhật `main` bằng cách merge một nhánh FAIL/HOLD chỉ để hiển thị “mới nhất”. Mới nhất ở đây là **quyết định, metadata, index chứng cứ hợp lệ và code đã được merge QA chấp thuận**.
- Nếu việc đồng bộ main bị chặn bởi PR/QA, ghi `MAIN_SYNC_BLOCKED` với lý do và không mở gate kế tiếp; không nói `main` đã cập nhật khi chưa có readback.

**Bước thực hiện tiếp theo sau policy lock:** đăng ký câu hỏi đầu tiên theo mẫu `templates/TTM_RESEARCH_QUESTION_GATE.md` và đánh giá **necessity của kiến trúc phép đo** bằng framework phù hợp. **Chưa thực hiện gate nghiên cứu trong commit chính sách này.**

## 4. SM4M-Q001 — Back-to-Basics Architecture Gate đã đăng ký (15/11/2026)

- **Đường dẫn câu hỏi:** [SM4M_Q001_BACK_TO_BASICS_ARCHITECTURE_DOC_CODE_EVIDENCE_20261115.md](SM4M_Q001_BACK_TO_BASICS_ARCHITECTURE_DOC_CODE_EVIDENCE_20261115.md).
- **Trình tự bắt buộc:** Đọc tài liệu kiến trúc → đối chiếu source thực tế và T4 checkpoint/config → mapping kết quả khoa học Small-4M theo study/branch exact HEAD → chọn framework đúng vấn đề → trả lời Q001 → independent QA → owner Q4 closure → chỉ sau đó mới xem xét F0–F2.
- **OUT OF SCOPE:** EmbeddingGemma 2 và Vector Memory không là module baseline Small-4M. Không sử dụng kết quả hai nhánh này.
- **Hoạt động được phép:** source/document read-only và lập ma trận traceability, không train, không inference, không tạo gold/scorer, không sửa code/architecture, không tạo nhánh research/implementation.
- **Trạng thái:** `Q1_REGISTERED; Q2_NOT_COMPLETED; Q3_NOT_REVIEWED; Q4_OWNER_NOT_DECIDED; F0_F2_PAUSED; SCIENCE_HOLD; LINEAGE_UNCHANGED; MERGE_NOT_AUTHORIZED`.

**Bước thực hiện tiếp theo — duy nhất:** thực hiện một lượt kiểm toán độc lập tài liệu → mã nguồn → kết quả Small-4M trên exact sources của Q001; nộp report và receipt để owner đóng Q4. Không tạo thí nghiệm trong lượt này.

## 5. Q2 owner scoped acceptance — pending governance PR merge

- **Owner decision 15/11/2026:** `ACCEPT_Q2_EVIDENCE_SCOPE_AND_ADMISSION_CRITERIA_FOR_DISTINCT_Q3_REVIEW_ONLY`. This is a scoped review authorization, **not** AD-00…AD-08 PASS, new science GO or Q4 owner closure.
- Evidence package is on one governance-only Draft PR branch in `docs/governance/sm4m-q001/` and `artifacts/governance/sm4m-q001/` with exact seven byte-preserved Git blob pins. Read acceptance `docs/governance/sm4m-q001/SM4M_Q001_OWNER_SCOPED_Q2_ACCEPTANCE_20261115.md`, then handoff `docs/governance/sm4m-q001/SM4M_Q001_DISTINCT_Q3_HANDOFF_20261115.md`.
- `Q2=AUTHOR_COMPLETED_AND_OWNER_SCOPE_ACCEPTED`; `Q3=DISTINCT_REVIEW_AUTHORIZED_NOT_EXECUTED`; `Q4=NOT_DECIDED`; `ROOT_CAUSE=NOT_IDENTIFIED`; `ADMISSION_FOR_NEW_SCIENCE=HOLD`; `F0_F2=PAUSED`.
- No research/implementation branch, model run, DATA, gold, code patch or merge authorized. The proposed governance PR **does not update `main` until it is independently reviewed and merged with owner authorization**.
- Single next step: distinct independent Q3 source/design review from the pinned governance PR HEAD; after Q3 verdict request owner Q4, not before.
