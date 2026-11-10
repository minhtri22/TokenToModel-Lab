# HANDOFF — Codex AI nội bộ phản biện R3 sau preflight CPU

**Không thực thi khoa học.** Nguồn: GitHub `minhtri22/TokenToModel-Lab`, nhánh `research/ttm-r3-structural-state-tracing-design-20261111`; ghim exact HEAD khi tiếp nhận. Chủ dự án đã thực hiện kiểm thử toy R3; Codex **chưa** làm vòng R3 này.

1. Đọc [mục lục canonical](../../artifacts/qa/ttm-r3-structural-design/runtime/README.md), mã generator/checker/test, **hai JSON đầy đủ** và source manifest SHA-256; xác minh Git blob/SHA rồi chạy lại CPU read-only trong worktree riêng **nằm trong root dự án**. Không sửa các nguồn đã khóa để khiến QA PASS.
2. Thử phá `r3_independent_checker.py` bằng các đột biến chưa có trong 42 negatives: root/record leakage, duplicate JSON keys Unicode, wrong `answer` và `source_events`, precondition HANDOFF/DELEGATE/CANCEL, alias shadowing, graph motif split collision, event permutation hợp lệ nhưng checker từ chối, story/oracle cross contamination, query-binding leaks, counterfactual B thay sai key; báo exact ACCEPT/REJECT.
3. Kiểm chéo **độc lập từ visible text** 96 nhóm × 4 ô; không import generator để tính đáp án. Xác định 3 motif DEV và 3 CHALLENGE có đủ để gọi `structural split` chưa, các lối tắt mới do family/split, độ dài, vị trí và từ khóa. Đặc biệt đánh giá `shallow_keyed_direct=64/384`: đây chỉ là một đối chứng đơn giản, không bao quát mọi heuristic không có latent state.
4. Kiểm tra `MODEL_INPUT_ONLY`: chỉ `story/question` ở root+record, nhưng **oracle public cùng repo** và thứ tự 4 ô cố định; nó không phải hidden FINAL. Nghiêm cấm dùng dữ liệu này để tuyên bố confirmatory model improvement.
5. Đánh giá giới hạn thiết kế sáu nhánh `A–F` O0/O1: `C−F` còn confound objective text-vs-head, nhãn oracle bổ sung, params/FLOPs/optimizer/seed phải được match hoặc định lượng. Không cấp quyền GPU, không đưa nhãn oracle vào inference.

Trả về báo cáo `PASS/FAIL_SCOPED` với exact Git source refs, từng finding severity và script QA riêng trên **nhánh Codex** (không đụng main, R3 source branch, PR13, lineage), chỉ khi thực thi thật. Không tự nhận external human validation.

**Tiêu chí quyết định chủ dự án sau phản biện:** nếu có bypass nghiêm trọng, `R3_SOURCE=HOLD_AMENDMENT_REQUIRED`; nếu không, `R3_PUBLIC_TOY=DEV_DIAGNOSTIC_READY`, vẫn cần một bộ FINAL chưa lộ đáp án và science budget công bằng trước khi đánh giá neural O0/O1.

**Bước thực hiện tiếp theo:** `TTM_R3_CODEX_SCOPED_ADVERSARIAL_QA_AND_O0_BASELINE_NEURAL_PILOT_DESIGN_SINGLE_OWNER_DECISION`. Handoff chỉ là hướng dẫn, **CODEX_R3_REVIEW=PENDING**.
