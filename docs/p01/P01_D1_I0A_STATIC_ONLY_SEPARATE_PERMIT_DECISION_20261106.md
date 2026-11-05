# P01 D1 — Quyết định RIÊNG về cấp quyền I0A-S tĩnh

**Operation:** `TTM_P01_D1_I0A_STATIC_ONLY_SCOPE_REASSESSMENT_AND_SEPARATE_PERMIT_DECISION`  
**Ngày:** 2026-11-06. **Repository:** `minhtri22/TokenToModel-Lab`.  
**Nhánh thiết kế:** `design/p01-tokenizer-data-prereg-20261105`, PR #4 Draft.  
**Source of method review:** `docs/p01/P01_D1_I0A_STATIC_ONLY_SCOPE_REASSESSMENT_20261106.md`.  
**Quyết định phạm vi:** `PASS_DESIGN_SCOPE`.  
**Quyết định cho phép viết mã:** **`I0A_STATIC_IMPLEMENTATION_PERMIT=NOT_GRANTED`**.

## 1. Kết quả quyết định

**Chấp thuận về mặt phương pháp** việc đưa yêu cầu thử nghiệm runtime token/AppContainer/Job Object/write broker sang cổng QA0, vì I0A-S chỉ được viết mã **chứ không chạy** mã mới. Đây là cách giải vòng lặp triển khai guard trước khi kiểm tra guard.

**Không cấp quyền thi hành I0A-S trong bước này**: chưa có chỉ thị riêng cho phép tạo worktree hoặc tệp mã, chưa có lựa chọn phương án A/B và chưa pin được exact GitHub HEAD cho nhánh triển khai. Remote Windows hiện báo device offline nên không đủ cơ sở cấp permit phương án B.

**Đề xuất ưu tiên:** phương án **A** — viết source-only bằng GitHub trên **nhánh triển khai được cấp riêng**, không cần worktree Windows trong I0A-S, sau khi kiểm tra GitHub workflow triggers; nếu người dùng yêu cầu code local, phương án **B** với đúng một worktree dưới root dự án là hợp lệ về mặt thiết kế nhưng cần preflight Windows ngay trước grant. Đề xuất A/B không tự động cho phép tạo branch hoặc commit code.

## 2. Mẫu nội dung phải có của một permit tương lai

Chỉ phát hành nếu chủ sở hữu đồng ý bằng một lượt quyết định **mới** với ít nhất:
- `PERMIT_OPERATION_ID=TTM_P01_I0A_S_STATIC_SOURCE_ONE_SHOT`; `PERMIT_MODE=A_GITHUB_ONLY` hoặc `B_ONE_LOCAL_WORKTREE`.
- `EXACT_SOURCE_REPO=minhtri22/TokenToModel-Lab`, `BASE_SHA=<readback 40-hex>`, `IMPLEMENTATION_BRANCH=<new exact branch authorized>`.
- Với B: `LOCAL_ROOT=D:\WORK\RESEARCH\TokenToModel-Lab`, `ONE_WORKTREE_PATH=D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105`; bảo vệ P00/.git; Git metadata chỉ được ghi bởi công cụ Git được kiểm soát bên trong root; tuyệt đối không tạo bản sao/worktree ngoài dự án.
- `ALLOWLIST` của 10 file nguồn trong tài liệu cũ **cộng 2 ứng viên cốt lõi** `src/p01/byte_bpe.py`, `src/p01/data_dedup_split.py`, **sau khi kiểm tra va chạm**; không cho phép tạo file khác tùy ý.
- `MAX_NEW_P01_FILE_COUNT=12` từ allowlist, không ghi đè tệp đã có, không touch P00/main/trainer/checkpoints/corpus.
- `EXECUTION_ALLOWED=false`, `PYTHON_IMPORT_ALLOWED=false`, `TEST_RUNNING_ALLOWED=false`, `FIXTURE_MATERIALIZATION_ALLOWED=false`, `CORPUS_DOWNLOAD_ALLOWED=false`, `NETWORK_DEPENDENCY_INSTALL_ALLOWED=false`, `TRAINING_ALLOWED=false`.
- `AUTOMATED_WORKFLOW_RUN_ALLOWED=false`; nếu kiểm tra thấy push sẽ tự kích hoạt workflow thực thi source/test và không thể chặn, `HOLD` và không tạo push.
- `SCOPE_CHECK=EXACT_PATHS_ONLY`, `POSTWRITE_DIFF_AND_SHA_READBACK=REQUIRED`, `INDEPENDENT_STATIC_REVIEW=REQUIRED`; không tự đánh dấu PASS nếu một file bị viết ra ngoài allowlist.
- `ONE_SHOT_NO_AUTO_RERUN=true`, `P00_CLEANUP=false`, `PR4_MERGE=false`, `QA0_PERMIT=false`, `E0_PERMIT=false`.
- `OWNER_EXPLICIT_APPROVAL=<new authorizing statement>`; văn bản này **không** điền `PERMIT_GRANTED` thay người dùng.

**Thẩm định chỉ đọc tối thiểu ngay trước grant**: GitHub main/PR/diff, exact SHA, kiểm tra tên file/workflow; với B còn có Windows online, Git sạch, P00 đúng pin, reparse/candidate collision, tài nguyên ở thời điểm thực hiện. Không chuyển rủi ro ACL lâu dài thành điều kiện vô hạn cho việc viết code tĩnh; vẫn yêu cầu bảo vệ P00 ở tầng thao tác ghi.

## 3. Tách quyết định với cổng QA0/E0

- I0A-S: hồ sơ mã, code review, source hashes, không chạy nội dung P01.
- QA0: khi mã đã được pin và có permit **mới**, thực hiện Windows runtime technical QA với isolation thực tế, negative tests W01–W12; không dùng F1/F2.
- E0: chỉ khi H02 source rights, D1 science prereg và QA0 được phê duyệt, mới được học byte BPE trên TRAIN hợp pháp. Không tự mở GPT training.

## 4. Phán quyết ghi nhận

`I0A_STATIC_SCOPE_REASSESSMENT=PASS_DESIGN_ONLY`  
`I0A_STATIC_SCOPE_PERMIT_ELIGIBILITY=CONDITIONAL_YES`  
`I0A_STATIC_IMPL_MODE_PREFERENCE=A_GITHUB_ONLY_PENDING_OWNER_SELECTION`  
`I0A_SOURCE_ALLOWLIST_EXPANSION=PROPOSED_12_PENDING_COLLISION_REVIEW`  
`I0A_WINDOWS_CURRENT_STATUS=OFFLINE_NO_LIVE_PREFLIGHT`  
`I0A_OWNER_PERMISSION=NOT_GRANTED`  
`I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`QA0_EXECUTION_PERMIT=NOT_GRANTED`  
`E0_SCIENTIFIC_PERMIT=NOT_GRANTED`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_SOURCE_FILE_CREATION_AUTHORIZED=false`  
`P01_SOURCE_FILE_EXECUTION_AUTHORIZED=false`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`.

**Bước tiếp theo:** `TTM_P01_I0A_S_STATIC_SOURCE_ONE_SHOT_EXACT_PERMIT_REQUEST`. Người dùng chọn A hoặc B và cấp quyền **riêng** sau khi xem exact SHA và danh mục tệp. Chưa có bất kỳ thao tác tạo nhánh/worktree/code, tải corpus, thực thi hoặc dọn dẹp.
