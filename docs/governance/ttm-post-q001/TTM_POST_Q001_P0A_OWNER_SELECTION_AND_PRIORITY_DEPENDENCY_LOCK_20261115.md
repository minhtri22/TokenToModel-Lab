# TTM — Quyết định owner về thứ tự ưu tiên sau Q001 (P0-A đầu tiên)

**Operation:** `TTM_POST_Q001_PROSPECTIVE_QUESTION_SELECTION_OWNER_REVIEW_SINGLE_GATE`  
**Owner statement, 2026-11-15:** “Đồng ý thực hiện theo ma trận và ưu tiên”; đề cập đầy đủ P0-A, P0-B, P1, P2, P3, P4.  
**Decision interpretation:** `GO_SELECT_P0A_MEASUREMENT_GOLD_FIRST_FOR_SOURCE_ONLY_QUESTION_DESIGN`. Đây là quyết định **ưu tiên triển khai công việc thiết kế/đăng ký Q kế nhiệm**, chưa phải `GO_SCOPED_IMPLEMENT`, không phải chấp thuận chạy thí nghiệm hay tự merge.  
**Repository:** `minhtri22/TokenToModel-Lab` · `main` source exact `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7` · [ma trận đã được owner đồng ý](TTM_POST_Q001_RESEARCH_DIRECTION_PRIORITY_MATRIX_20261115.md) trên [PR #22](https://github.com/minhtri22/TokenToModel-Lab/pull/22).  
**Q001:** [`Q4_CLOSED_HOLD_NEW_SCIENCE`](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/sm4m-q001/SM4M_Q001_Q4_OWNER_CLOSURE_AND_GOVERNANCE_MERGE_DECISION_20261115.md).  
**Question Gate kế nhiệm:** `CANDIDATE_ONLY · NOT_REGISTERED_ON_MAIN`. `ACTIVE_RESEARCH_GATE.md` và `lineage.md` giữ nguyên cho đến khi được phép đăng ký chính thức.

## 1. Thứ tự owner đã chấp nhận

| Thứ tự phụ thuộc | Hướng | Disposition sau chọn |
|---|---|---|
| `P0-A` | Measurement / construct / source-visible gold / AI-rater | **SELECTED_FOR_NEXT_SOURCE_ONLY_Q_CANDIDATE** |
| `P0-B` | Causal identifiability / matched teacher forcing vs generation | `DEPENDENT_ON_P0A · NOT_OPENED` |
| `P1` (đồng hạng) | Data diversity và learning objective | `TIED_UNRESOLVED · NOT_OPENED` |
| `P2` (có điều kiện) | Context/window và decoder/rollout | `CONDITIONAL · NOT_OPENED` |
| `P3` | Capacity / attention / FFN / MoE | `DEFER_PATCH · NOT_OPENED` |
| `P4` | Reasoning / Long-CoT / Mole-Syn | `OWNER_ACCEPTED_LITERATURE_REFERENCE_ONLY` |

Thứ tự trên là **dependency order**, không là xác suất root cause hay phán quyết rằng evaluator chắc chắn sai. Để P0-B có ý nghĩa phải có source-visible factual truth và cặp one-variable matched khả thi; không sử dụng P1/P2/P3/P4 như đường vòng khi phép đo bị HOLD.

## 2. Một hành động tích hợp được cho phép trong gate này

**Author:** dựng *một* câu hỏi P0-A khả năng bác bỏ, dựa trên nguồn công khai đã khóa, phân biệt OBSERVED/INFERRED/UNKNOWN, các ứng viên `KEEP/SIMPLIFY/PIVOT/STOP/HOLD`, hard veto, điều kiện gold source-visible, cùng tiêu chuẩn evidence và cách QA independent về sau.  
**Output:** [Prospective source-only candidate](TTM_P0A_MEASUREMENT_GOLD_PROSPECTIVE_QUESTION_CANDIDATE_20261115.md) + [machine contract](../../../artifacts/governance/ttm-post-q001/TTM_P0A_OWNER_SELECTION_AND_SOURCE_ONLY_DESIGN_CONTRACT_20261115.json) + author QA.  
**Q1 registration:** chỉ thành hiệu lực khi Question Gate hồ sơ hợp lệ **được ghi vào `main`** theo [Question-First Policy](https://github.com/minhtri22/TokenToModel-Lab/blob/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md); Draft PR #22 **không** phải Q1 registration.  
**Reviewer:** một reviewer khác vai trò tác giả ở bước review thích hợp; author QA không là independent adjudication. Gộp mọi sửa cần thiết thành một packet, không lập chuỗi micro-permit.

## 3. Bất biến khoa học và quyền hạn

- `NEW_QUESTION_REGISTERED=false`; `GO_SCOPED_IMPLEMENT=false`; `SCIENCE_EXECUTION=false`; `F0_F2_RESTART=false`.
- `GOLD/DATASET/SCORER/RUBRIC_EXECUTABLE=false`; `MODEL_INFERENCE/TRAINING/GPU=false`.
- `TEST64/FINAL24/FINAL72=SEALED_NO_REPLAY`; private corpus, checkpoint và rater packets không được truy cập/lộ thêm.
- `ROOT_CAUSE_NOT_IDENTIFIED`; `KEEP_HISTORICAL_REFERENCE_ONLY`; `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`.
- `lineage.md` append-only **không thay đổi**; nghiên cứu độc lập VM/EmbeddingGemma 2 không trở thành evidence của P0-A.
- Không tự merge PR #22, không mở nhánh nghiên cứu, không vá T4/attention/FFN, không tự tăng model capacity, không mở Long-CoT training.

## Bước thực hiện tiếp theo — duy nhất

`TTM_P0A_MEASUREMENT_GOLD_PROSPECTIVE_Q1_SOURCE_ADMISSION_AND_DISTINCT_REVIEW_SINGLE_GATE`

Kiểm tra tích hợp toàn bộ đề cương P0-A: khả năng trả lời câu hỏi, các cơ chế cạnh tranh, hard veto quyền nguồn/visible gold, negative controls, phản chứng, tiêu chuẩn dừng; review độc lập scoped. **Chỉ sau khi Question Gate hợp lệ mới được trình hồ sơ đăng ký trên `main` và quyết định riêng về triển khai; không có quyền science ngầm.**
