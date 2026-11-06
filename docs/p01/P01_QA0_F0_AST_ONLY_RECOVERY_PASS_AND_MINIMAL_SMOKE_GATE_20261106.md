# TTM P01 — Thẩm định kết quả phục hồi AST và ranh giới chạy thử F0 tối thiểu

**Thao tác:** `TTM_P01_QA0_F0_AST_ONLY_RECOVERY_AND_RUNTIME_GATE_DECISION`  
**Ngày:** 06/11/2026.  
**Nguồn bằng chứng:** người dùng cung cấp toàn bộ transcript PowerShell từ `TTM_P01_QA0_AST_RECOVERY_BEGIN` đến `TTM_P01_QA0_AST_RECOVERY_END`; timestamp console `2026-11-06T02:02:23.8525664Z` (09:02:23 ICT). Transcript là nội dung dán trong hội thoại, không phải bản gốc có chữ ký hay receipt node.  
**Máy:** `DESKTOP-4PSD0G2`. **Repo:** `minhtri22/TokenToModel-Lab`.  
**P01 HEAD mục tiêu:** `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.  
**Nhánh P01:** `implementation/p01-i0a-s-f0-static-20261106`.  
**Nhánh thiết kế:** `design/p01-tokenizer-data-prereg-20261105`, PR #4 Draft.

## 1. Bằng chứng quan sát Windows

Console báo: `GIT_FETCH=FORBIDDEN`, `GIT_MERGE=FORBIDDEN`, `QA0_SMOKE_TEST=NOT_AUTHORIZED`, `PYTHON_SOURCE_EXECUTION=NONE`, `CLEANUP=NONE`.  
Các đường `D_WORK/RESEARCH/ROOT/WORKTREES/P00/P01/GIT/GIT_WORKTREES` và `ORIGIN/ROOT_HEAD/P00_HEAD/P01_HEAD_AFTER_FF/P01_BRANCH/P01_TOPLEVEL` đều PASS.  
Trạng thái Git trước/sau của root/P00/P01 sạch. `WORKTREE_INVENTORY=PASS_EXACT_THREE`. Không chạy lại Fast-forward.

**Python AST:** `PYTHON_AST_PASS` tại bốn tệp:
- `src/p01/byte_bpe.py`
- `src/p01/data_dedup_split.py`
- `runtime/p01/source_scope_guard.py`
- `qa/p01/qa0_f0_smoke_test.py`

**JSON:** `JSON_PARSE_PASS` tại:
- `configs/p01_f0_static_i0a.json`
- `qa/p01/golden_vectors.json`

Cuối console: `STATIC_NO_IMPORT_EXECUTION=PASS`, `PYTHON_EXIT_CODE=0`, `ROOT_POSTCHECK_CLEAN=PASS`, `P00_POSTCHECK_CLEAN=PASS`, `P01_POSTCHECK_CLEAN=PASS`, `ROOT_HEAD_STILL/P00_HEAD_STILL/P01_HEAD_STILL=PASS`, `FAST_FORWARD=ALREADY_COMPLETED_NO_RERUN`, `QA0_DYNAMIC_EXECUTION=NOT_PERFORMED`, `QA0_SMOKE_PERMISSION=NOT_GRANTED`, `E0_SCIENCE_PERMISSION=NOT_GRANTED`, `CLEANUP=NONE`, và `TTM_P01_QA0_AST_RECOVERY_END`.

**Phán quyết:** `AST_RECOVERY=PASS_USER_CONSOLE`; `JSON_PARSE=PASS_USER_CONSOLE`; không còn cổng cú pháp INCONCLUSIVE của lần Python `-c` trước đó. Không cần chạy lại AST hoặc đồng bộ Git nếu không có thay đổi mã mới.

## 2. Đối chiếu độc lập GitHub

GitHub `refs/heads/implementation/p01-i0a-s-f0-static-20261106` vẫn chỉ commit `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`. Compare từ `7e8b37d59b10b7a71603f6b446b57b9e3a9cb645` là đúng 1 commit / 5 đường dẫn P01 đã được duyệt (3 tệp sửa, 2 tệp mới). `main=92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`; PR #4 vẫn Draft/chưa merge.

GitHub độc lập **không** chứng minh các quan sát trạng thái Windows hiện tại; kết luận Windows theo transcript người dùng. Không có mã mới được commit vào nhánh triển khai trong lượt đánh giá này.

## 3. Quyết định chạy thử F0: tách smoke chức năng và chứng nhận guard

Bốn nội dung F0 đang cần xác nhận thực tế: (1) mã hóa/giải mã Byte BPE; (2) merges M01 và Golden SHA; (3) checker độc lập phát hiện sai hỏng; (4) từ chối input/nguồn chưa được duyệt và stubs fail-closed.

**Cổng cú pháp: ĐÃ ĐÓNG.**  
**Cổng chạy smoke: CHƯA MỞ.** Điều kiện `AST=PASS` không cấp quyền `python -m unittest` cho mã mới.

**Phương án kiểm thử tối thiểu đề xuất:** sau **quyết định runtime riêng**, chạy *chỉ* 10 bài `qa/p01/qa0_f0_smoke_test.py` trên dữ liệu F0 nhúng; timeout ngắn, một Python process, no bytecode writes, không môi trường nghiên cứu thật/corpus, không tải/cài gói mạng, không tạo file output ở vùng bảo vệ. Tách biệt:
- **Functional F0 smoke** chứng minh hành vi API trên mẫu nhỏ, không phải phép thử resource/OS isolation.
- **QA0 security qualification** của Job Object, write broker, restricted token, escape/negative tests W01–W12 vẫn chưa có; `start_worker()` và `write_file()` hiện cố ý raise lỗi. Không được kết luận guard hoạt động chỉ vì kiểm thử từ chối stub PASS.
- Python `-I -S -B` không tự trở thành một sandbox hệ điều hành, không ngăn mạng hoặc ghi tệp theo ACL. Nếu chưa có môi trường cô lập thích hợp, **không chạy smoke như đã được bảo vệ**. Một kiểm thử chức năng có chấp nhận rủi ro riêng phải được người dùng chấp thuận rõ phạm vi và đánh dấu `FUNCTIONAL_DEMO_ONLY_NOT_QA0_GUARD_PASS` nếu vận hành trên quyền user thông thường; không suy diễn đã đạt cổng QA0.
- Không huấn luyện Byte BPE trên corpus thật; M01 synthetic `abababab` chỉ là phép thử tính đúng trong suite, không có quyền mở E0/GPT training.

Không cần tái mở ACL inventory, permit I0A hay quy trình fast-forward. Chỉ cần quyết định runtime theo phạm vi chính xác và cách thực thi cô lập hoặc chấp thuận demo chức năng không được xem là guard qualification.

## 4. Phán quyết

`TTM_P01_QA0_F0_AST_RECOVERY=PASS_USER_CONSOLE`  
`TTM_P01_QA0_F0_JSON_PARSE=PASS_2_OF_2_USER_CONSOLE`  
`TTM_P01_QA0_F0_PYTHON_AST=PASS_4_OF_4_USER_CONSOLE`  
`TTM_P01_QA0_F0_GIT_FAST_FORWARD=ALREADY_PASS_NO_RERUN`  
`TTM_P01_QA0_F0_P00_P01_POSTCHECK=CLEAN_USER_CONSOLE`  
`TTM_P01_QA0_F0_FUNCTIONAL_SMOKE=NOT_EXECUTED`  
`TTM_P01_QA0_F0_OS_ISOLATION=NOT_ESTABLISHED`  
`TTM_P01_QA0_F0_RUNTIME_DECISION=HOLD_SCOPE_AND_CONFINEMENT`  
`TTM_P01_E0_SCIENCE_PERMISSION=NOT_GRANTED`  
`TTM_P01_MAIN_AND_P00_UNCHANGED=YES_GITHUB_SCOPE`  
`TTM_P01_CLEANUP=NONE`.

**Bước tiếp theo:** `TTM_P01_QA0_F0_SINGLE_SHOT_FUNCTIONAL_SMOKE_EXECUTION_GATE`: chỉ xem xét một lượt smoke nhỏ để kiểm tra hàm trên F0, tách với việc chứng minh an toàn Job Object/Write Broker. Nếu chủ sở hữu chấp thuận demo chạy trên môi trường kiểm soát phù hợp, nhận output 10 test và lập verdict chức năng riêng. Nếu không có isolation, không tự coi `-I -S -B` hoặc marker admission là chứng nhận an toàn.

Không thêm `lineage.md` vì đây là kiểm định kỹ thuật, không phải thí nghiệm khoa học.
