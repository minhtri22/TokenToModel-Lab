# MẪU — Một câu hỏi, một gate nghiên cứu (TTM Question-First)

**Bắt buộc đọc policy:** `docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md`. Mẫu này là **khuôn**, không phải study đã GO, không phải permit.

## A. Q1 — Câu hỏi và tính cần thiết (phải hoàn thành trước code/branch)

- `QuestionID`: [chưa cấp] · `Programme`: [TTM phase/hướng] · `Owner`: [vai trò] · `Type`: SCIENCE / MEASUREMENT / ENGINEERING / GOVERNANCE.
- **Câu hỏi duy nhất có thể trả lời/bác bỏ:** [một câu cụ thể].
- **Quyết định bị ảnh hưởng bởi đáp án:** [giữ/tối giản/thay/dừng thành phần gì]. Nếu không có quyết định sẽ thay đổi, `HOLD_QUESTION_UNJUSTIFIED`.
- **Lý do cần thiết (Why this component?)**: [điều kiện kỹ thuật/khoa học cần đáp ứng; hậu quả nếu bỏ thành phần].
- **Nguồn được quan sát (Observed):** [Git main pin, implementation HEAD đủ 40 hex, metrics/receipts exact, nguồn quyền].
- **Giả thuyết suy ra (Inferred):** [từng mục có đối chứng].
- **Chưa biết (Unknown):** [phần cần kiểm tra trước].
- **Chứng cứ lịch sử đã dùng, không được chạy lại:** [TEST/FINAL/checkpoint/prereg nếu áp dụng].

## B. Q2 — Tự lựa chọn framework và đánh giá phương án

| Vấn đề thực chất | Framework được chọn và tại sao | Đầu ra | Rủi ro áp đặt/sai lệch |
|---|---|---|---|
| [ví dụ: không rõ mục đích] | 5W1H nếu cần | Requirement / intended mechanism | Không là chứng cứ khoa học |
| [ví dụ: lặp HOLD] | 5 Whys + falsification nếu phù hợp | Những giả thuyết nguyên nhân có thể bác bỏ | Không nhầm 5 Whys thành proof |
| [ví dụ: quyết định kiến trúc] | SWOT/FMEA/Pugh/MCDA nếu cần | So sánh + hard veto | Trọng số khóa trước, sensitivity |

**Ba ứng viên tối thiểu nếu hợp lý:** `KEEP` (giữ), `SIMPLIFY` (đơn giản), `PIVOT` (thay hướng). Luôn có `STOP` và `HOLD_EVIDENCE_INSUFFICIENT`. Không bịa score; `N/A` cho phương án không phù hợp và giải thích.

| Phương án | Construct validity / hard veto | Discriminating power | Feasibility + cost | Evidence / uncertainty | Phán đoán có truy vết |
|---|---|---|---|---|---|
| KEEP | | | | | |
| SIMPLIFY | | | | | |
| PIVOT | | | | | |
| STOP / HOLD | | | | | |

**Nếu dùng MCDA:** tiêu chí và trọng số (tổng 100%) được khóa trước khi chấm; phạm vi nguồn, số điểm, uncertainty, sensitivity khi thay trọng số; veto trước điểm. Không nên dùng MCDA nếu không có dữ kiện ước lượng score.

## C. Q3 — Chứng cứ tối thiểu đủ trả lời và reviewer

- `Hypotheses`: [H0/H1 hoặc nhiều cơ chế cạnh tranh, với dự đoán phân biệt].
- `Minimum discriminating evidence`: [phép quan sát nhỏ nhất đủ thay đổi lựa chọn; chỉ khi cần dữ liệu mới và có permission].
- `Primary endpoint/threshold`: [định nghĩa, unit, acceptance/FAIL/STOP, pre-registered nếu science].
- `stop rule`: [điều kiện dừng bắt buộc, tiêu chí NO_GO/HOLD khi thiếu bằng chứng hoặc construct không hợp lệ; khóa trước chạy].
- `Negative controls / shortcut risks`: [dự kiến, reject rules].
- `Data/rights/PII/secret-custody`: [status; không cấp quyền bằng tài liệu].
- `Expected cost/time/resource ceiling`: [nếu xác định được].
- `Author adversarial QA`: [receipt/source pins; không mạo nhận independent].
- `Distinct reviewer`: [role, source scope, PASS/HOLD]. 
- `Remaining unknowns`: [nếu chưa đủ, HOLD không triển khai].

## D. Q4 — Đáp án và quyết định owner

- **Câu trả lời sau bằng chứng:** [trả lời câu hỏi A, hoặc ghi rõ chưa đủ chứng cứ].
- `Decision`: `KEEP` / `SIMPLIFY` / `PIVOT` / `STOP` / `HOLD_EVIDENCE_INSUFFICIENT`.
- `Owner`: [decision declaration + date / ref], `Reviewer`: [report SHA/ref].
- `Question closure`: `CLOSED_GO_SCOPED` / `CLOSED_STOP` / `CLOSED_HOLD` / `OPEN_HOLD`.
- `Science execution authorized?`: [NO mặc định; muốn YES cần owner permit đúng phạm vi độc lập].
- `May create one implementation branch?`: [NO mặc định; YES chỉ nếu Question closed và explicit owner `GO_SCOPED_IMPLEMENT`].
- `Implementation HEAD`: [exact 40-hex nếu đã có; không bịa future hash].
- `Final merge decision`: `MERGE_APPROVED` / `EVIDENCE_ONLY_NO_MERGE` / `NO_MERGE_NEEDED` / `HOLD_MERGE_REVIEW`.
- `Scientific lineage entry?`: [YES chỉ nếu science PASS/FAIL hợp lệ; nếu HOLD/DESIGN/QA thì NO, ghi receipt riêng].
- `main` readback/active register updated: [exact commit sau khi commit, không tự tham chiếu trong cùng file].
- **Bước thực hiện tiếp theo — duy nhất:** [chỉ một bước; không tạo micro-permit].

**Fail-closed checklist:** không có câu hỏi → HOLD; không có bằng chứng thay đổi quyết định → HOLD; question chưa đóng → không mở branch mới; author QA ≠ independent; reviewer GO_DESIGN ≠ science permission; science FAIL ≠ tự merge code; prior TEST/FINAL sealed; lineage không chứa QA/HOLD; main giữ closure metadata mới nhất.
