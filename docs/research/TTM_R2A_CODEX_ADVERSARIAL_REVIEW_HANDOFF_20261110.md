# HANDOFF R2A — Codex AI phản biện source, shortcut và tính công bằng O0/O1

**Ngày giao:** 2026-11-10. **Người chấm:** Codex AI nội bộ (separate-session code/theory reviewer, **không phải external human validation**).  
**Nhiệm vụ:** `TTM_SMALL4M_R2A_CODEX_SCOPED_ADVERSARIAL_REVIEW_AND_O0_VS_O1_FAIR_SUPERVISION_DESIGN`.  
**Repository:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh:** `research/ttm-small4m-semantic-state-goal-toy-r2-20261110`.  
**Mốc lịch sử R2A để đối chiếu:** `d7128812ce7f98eb0c6087b4649822bc999d1088`, không coi đó là HEAD mới nhất; **luôn đọc HEAD GitHub tại lúc review**. PR #13 vẫn DRAFT/HOLD và không liên quan quyền mở science.

## 0. Điểm sửa quan trọng về Source of Truth

**Toàn bộ 8 hiện vật của ZIP R2A gốc đã được commit trực tiếp, nguyên byte lên GitHub**, bao gồm dữ liệu oracle và **384 đầu vào**. Trước đây GitHub chỉ có code/digest và hướng dẫn tái sinh; giờ không còn yêu cầu tải ZIP sandbox.

- [Sổ nguồn R2A và mọi liên kết](../../artifacts/qa/ttm-r2-semantic-toy/r2a/README.md)
- [Manifest 10/10 Git blob, SHA256 và ranh giới public/blind](../../artifacts/qa/ttm-r2-semantic-toy/r2a/R2A_COMPLETE_GITHUB_CUSTODY_MANIFEST_20261110.json)
- [Toàn bộ 384 input `story/question`](../../artifacts/qa/ttm-r2-semantic-toy/r2a/R2A_MODEL_INPUT_ONLY.json) SHA256 `72f57d704a2e4f99f06a797b8b647d93736a7093852e0c9df0f28dc59549032d`
- [256 bản ghi phản thực + 128 query probes có nhãn oracle](../../artifacts/qa/ttm-r2-semantic-toy/r2a/R2A_ORACLE_DATASET.json) SHA256 `3243d1eaae4b8727449fe4571dc81c898414b5ba300a20e7ead0819d7953286e`
- [Generator](../../tools/research/semantic_state_r2/r2a_generator.py) · [checker](../../tools/research/semantic_state_r2/r2a_independent_checker.py) · [unit tests](../../tools/research/semantic_state_r2/r2a_single_cpu_qa.py)
- [QA kết quả](../../artifacts/qa/ttm-r2-semantic-toy/r2a/R2A_INDEPENDENT_QA_20261110.json), [log QA cuối PASS](../../artifacts/qa/ttm-r2-semantic-toy/r2a/R2A_CPU_TEST_LOG_FINAL_20261110.txt), [log QA ban đầu FAIL có lý do](../../artifacts/qa/ttm-r2-semantic-toy/r2a/R2A_INITIAL_TEST_LOG_20261110.txt)
- [Audit heuristic phía ChatGPT Web](../../artifacts/qa/ttm-r2-semantic-toy/r2a/R2A_AUTHOR_SHORTCUT_AUDIT_20261110.json) và [mã audit](../../tools/research/semantic_state_r2/r2a_author_shortcut_audit_20261110.py). **Đây KHÔNG phải kết quả phản biện của Codex.**
- [Thiết kế đối chứng 5 nhánh O0/O1](TTM_R2A_O0_O1_FAIR_SUPERVISION_AND_COMPUTE_COMPARISON_DESIGN_20261110.md) + [ma trận máy](../../artifacts/qa/ttm-r2-semantic-toy/r2a/TTM_R2A_O0_O1_FAIR_SUPERVISION_MATRIX_CANDIDATE_20261110.json).

## 1. Phạm vi thực hiện khi Codex có phiên riêng

**Source/replay:** GitHub -> local repo/worktree **chỉ trong** `D:\WORK\RESEARCH\TokenToModel-Lab`; Python `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe`; PowerShell 5.1. Pin exact SHA, tránh checkout chồng lên worktree active. Xác nhận code + dataset + QA Git blob/SHA; tự viết checker đối chiếu các cặp và 384 input, không dùng `source_events` làm ground truth của prediction.

**Adversarial theory/code:** tích cực tìm shortcut có thể đúng 100% mà không theo dõi queried key, gồm pattern câu, vị trí, từ vựng, entropy nhãn, cách R2A tạo A/B và query-swap chỉ từ A, lỗi metadata/counts, oracle exposure, cùng story + khác câu hỏi. Đặc biệt kiểm tra quy tắc **key-aware latest assignment**: nó đạt 100% nhưng là cách giải toán đơn giản, không minh chứng cần memory slots hay learned semantics. Kiểm các trường hợp checker chấp nhận sai: query từ key khác, source_events thay, counts sai, duplicate, split đổi, vị trí không cân bằng, label key không nhất quán. Ghi FAIL nếu phát hiện bypass, không chỉ xác nhận 36 test gốc.

**Fairness:** phản biện riêng [design 5 arm](TTM_R2A_O0_O1_FAIR_SUPERVISION_AND_COMPUTE_COMPARISON_DESIGN_20261110.md): A=O0 CE, B=O0 state supervision bằng text token, C=O1 true head, D=O1 head nhãn shuffled, E=O0 capacity matched. Phải tách **thêm nhãn oracle trong TRAIN** khỏi kiến trúc; đo active/total params, token/aux target exposures, measured FLOPs, checkpoint compatibility và information leakage. Hỏi B/C có thực sự match hay chỉ có cùng số label; nếu không chứng minh được, `FAIR_SUPERVISION=HOLD`.

**Nguyên tắc nền:** R2A public oracle có lời giải từng hàng: **không được gọi 384 input là blind FINAL**. Muốn đo khả năng tổng quát hóa phải khóa bộ R3 mới với cấu trúc sự kiện khác, nhãn chưa công bố trước adjudication. Không dùng R2A đã công khai để quyết định O1 khoa học.

## 2. Ranh giới an toàn

- Không tạo/train model, không Colab/T4/GPU, không TEST/Q1Q2, không truy cập pack TRAIN/VAL/weights TTM, không thay R2/R2A cũ.
- Không merge PR13, không sửa `main`, `lineage.md`, không xóa worktree, không force-push, không xóa QA gốc. Nhật ký của phiên Codex phải ở artifact QA mới trong root dự án.
- Codex có thể ghi một báo cáo QA/phản biện mới trên nhánh đúng sau khi đọc lại exact HEAD; **chỉ ghi file mới** và readback. Không tự cập nhật scientific status của O1.
- Không tự gọi reviewer là human hoặc external; ghi rõ `CODEX_AI_INTERNAL`.

## 3. Đầu ra yêu cầu, PASS/HOLD/FAIL và kết thúc hữu hạn

1. Báo cáo `TTM_R2A_CODEX_SCOPED_ADVERSARIAL_REVIEW_20261110.md`: exact GitHub HEAD/SHA, phương pháp độc lập, ma trận kiểm thử bổ sung, lý do và phân mức HIGH/MEDIUM/LOW, phân xử shortcut, criticism of O0/O1 fairness.
2. JSON receipt với source pins, output SHA256, tests PASS/FAIL, kết luận `R2A_VALID_SCOPED` hoặc `R2A_DESIGN_FAIL`; `NEURAL_GAIN=NOT_TESTED` luôn trừ khi có thực nghiệm được cấp quyền mới.
3. Tệp Python cho QA độc lập (nếu cần), kết quả và raw logs đúng SHA. Commit lên GitHub branch/PR riêng theo quyền chủ dự án và đọc lại; nếu không có quyền ghi, trả biên bản cùng SHA để owner lưu, không tuyên bố đã commit.
4. Chỉ đề xuất **một quyết định owner**: `KEEP_O0_ONLY`, `DESIGN_R3_BEFORE_O1`, hoặc `O0_PLUS_O1_DESIGN_CANDIDATE`. Không bật T4 trong bước này.

**Bước thực hiện tiếp theo sau review:** `TTM_R2A_CODEX_REVIEW_ADJUDICATE_THEN_R3_STRUCTURAL_STATE_TRACING_SCIENCE_DESIGN_OR_KEEP_O0`. Nếu Codex chưa nhận/có phiên thực thi, trạng thái trung thực là `CODEX_R2A_REVIEW=PENDING`, không thay bằng PASS.
