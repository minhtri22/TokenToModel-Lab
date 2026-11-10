# HANDOFF — Codex R2 adversarial theory/source review (read-only)

**Mã việc:** `TTM_SMALL4M_R2_CODEX_ADVERSARIAL_THEORY_AND_SOURCE_REVIEW_THEN_O0_VS_O1_DECISION`  
**Ngày lập:** 2026-11-10 · **Vai:** `CODEX_INTERNAL_THEORY_AND_SOURCE_REVIEW_ONLY`.  
**Trạng thái:** handoff đã được ChatGPT Web chuẩn bị; **Codex CHƯA tiếp nhận hoặc thực hiện phản biện này**. Đây không phải FRESH12 blind reviewer; không có hidden TEST và không cần key giải mù.

## 1. Đọc đúng nguồn GitHub (không tham gia huấn luyện)

Repository: https://github.com/minhtri22/TokenToModel-Lab  
Branch: `research/ttm-small4m-semantic-state-goal-toy-r2-20261110`.  
Source-of-truth R2: [formal hypothesis / decision](TTM_SMALL4M_R2_SEMANTIC_STATE_GOAL_FORMAL_HYPOTHESIS_TOY_FEASIBILITY_20261110.md).  
Executable ground-truth mirror: [r2_runtime_integration_executed.py](../../tools/research/semantic_state_r2/r2_runtime_integration_executed.py), Git blob `4d78819e9ee7c602b7fd461a346819abd42bda1e`.  
Negative test: [negative_test_runner.py](../../tools/research/semantic_state_r2/negative_test_runner.py), Git blob `965def98940984bb5f073aa275102336f9e2bad6`.  
Separate source candidates: [generator](../../tools/research/semantic_state_r2/r2_semantic_toy_generator.py) and [independent checker](../../tools/research/semantic_state_r2/r2_independent_visible_text_checker.py).  
R1 motivation: [GPT-2/TTM/Llama4 philosophical architecture survey](TTM_ARCHITECTURE_ROUND1_GPT2_LLAMA4_PHILOSOPHICAL_SEMANTIC_ALTERNATIVES_20261110.md).

## 2. Nhiệm vụ phản biện: ưu tiên phát hiện lỗi

1. **Phản biện H-ORDER và H-STATE**: có đúng khi 128 cặp chỉ đảo thứ tự sự kiện cập nhật cùng một khóa thì việc dùng bag-of-words không xác định được đáp án? Phép thử có vô tình tiết lộ đáp án bằng lexical distribution, độ dài, split, entity ordering hay question không?
2. **Kiểm tra nguồn và chương trình thật**: chạy lại script nguồn đúng Git blob ở Python stdlib (không Tensor/GPU), xác nhận dataset SHA256 `f20915ff0559b32786961b4a19fa3dce3858cb95d18beaee1fc77ab79cb3cb08`, 128 pairs/256 texts, parser 256/256, lexical control 128/256. Kiểm chứng từng A/B có **exact word multiset** và opposing answers.
3. **Đối chiếu độc lập hai hiện thực**: chạy `r2_semantic_toy_generator.py --output <new_dir>/dataset.json` và `r2_independent_visible_text_checker.py --input <new_dir>/dataset.json --output <new_dir>/audit.json` trên dữ liệu mới. So SHA dataset với mirrored runtime; nếu lệch, báo **FAIL_REAL_IMPLEMENTATIONS_NOT_EQUAL** chứ không sửa im lặng. Chú ý source checker không dựa trên `source_events`.
4. **Kiểm tra negative QA**: chạy `negative_test_runner.py` (21 mutations), bổ sung các ca cố tình đánh lừa key-binding (sự kiện nhiễu ở cuối, trùng tên/đồng sở hữu, câu phủ định, đại từ, nhiều bước) và đánh dấu chính xác **out-of-grammar** thay vì chấm nhầm năng lực mô hình.
5. **Phê bình triết học**: liệu formalization `S_t=(owner,goal)` có thực sự kiểm tra giả thuyết Wittgenstein/Kamp/Schank hay chỉ là *toy last-write-wins*? Chỉ ra các giả định không thuộc ngôn ngữ đời thực, các tình huống không phân biệt được, và tiêu chí bác bỏ H-LEARNING về sau.
6. **Phê bình công bằng O0/O1**: đề xuất thí nghiệm mà có thể phân tách hiệu quả của (a) thêm nhãn trạng thái oracle, (b) cấu trúc đầu phụ/bộ nhớ, (c) tăng tham số/FLOPs, (d) dữ liệu truyện. Không để mô hình mới lấy thông tin oracle ở inference trong khi baseline không được phép.
7. **Quyết định nội bộ trước bước tiếp**: `R2_VALID_SCOPED` hoặc `R2_FAIL_REDESIGN` với lý do; khuyến nghị `O0_ONLY`, `O0_PLUS_O1_PROSPECTIVE`, hoặc `DEFER`. **Không cấp quyền science run/GPU** và không giả vờ đã đo neural adherence.

## 3. Cách chạy hợp lệ và ranh giới filesystem

Chỉ sử dụng workspace trong `D:\WORK\RESEARCH\TokenToModel-Lab`, đặt kiểm thử dưới một thư mục phụ mới của chính dự án; không tạo worktree hoặc cleanup ngoài root. Chạy Python 3.12, không đọc/tải TRAIN/VAL/TEST hoặc checkpoint, không cần Ollama/Colab, không gọi nghiên cứu SIX/CQG.

Lưu output thực mới, SHA-256 và bộ negative test vào nhánh phản biện **riêng** nếu chủ dự án cho ghi; mặc định **read-only GitHub**, chỉ báo cáo đánh giá bằng link PR/comment. Không merge PR13, không sửa main/lineage, không chỉnh bản QA R2 để biến FAIL thành PASS.

**Mẫu lệnh:** clone/check out đúng nhánh rồi ở thư mục mới của dự án chạy các script bằng Python 3.12; `r2_runtime_integration_executed.py` ghi `dataset.json` cạnh file Python của nó, vì vậy hãy **copy nguyên tệp sang thư mục QA mới** trước khi chạy, tránh ghi đè source worktree hoặc output cũ. `negative_test_runner.py` cũng ghi `negative_audit.json` cạnh file, chạy cùng bản copy. Không thực thi trong checkout gốc nếu output có thể đè file theo dõi.

## 4. Kết thúc và quyền khoa học

Codex báo: GitHub HEAD, Git blob của các script, SHA dataset/QA, danh sách kiểm tra PASS/FAIL có thể tái hiện, phản biện triết học và kết luận `REVIEW_PASS_SCOPED` / `REVIEW_FAIL` / `HOLD`. Nêu rõ reviewer là **Codex AI nội bộ**, không phải external/human independent reviewer.

**Dừng trước mọi huấn luyện và trước khi chủ dự án chọn phương án.** Vòng review này chỉ giúp xác định ý tưởng nào đáng kiểm định; **không làm bằng chứng hiệu quả kiến trúc R2**.