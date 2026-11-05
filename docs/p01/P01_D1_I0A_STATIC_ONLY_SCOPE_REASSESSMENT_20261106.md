# P01 D1 — Đánh giá lại phạm vi I0A: chỉ viết mã nguồn tĩnh

**Operation:** `TTM_P01_D1_I0A_STATIC_ONLY_SCOPE_REASSESSMENT_AND_SEPARATE_PERMIT_DECISION`  
**Ngày:** 2026-11-06. **Trạng thái:** `PASS_METHOD_SCOPE_DESIGN_ONLY`, **không cấp quyền triển khai**.  
**Repository:** `https://github.com/minhtri22/TokenToModel-Lab.git`.  
**Nhánh thiết kế:** `design/p01-tokenizer-data-prereg-20261105`, PR #4 Draft.  
**GitHub main đã xác minh:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.  
**HEAD trước khi lập văn bản:** `66c1d59c5ea077c5644411c203611d1c511f7229`.  
**Windows mới nhất:** lần đọc trên RemoteMCP trong công việc này trả `device is offline`; **không khẳng định trạng thái Windows hiện thời**. Console ngày 05/11/2026 là bằng chứng có thời điểm, không phải permit vĩnh viễn.

## 1. Câu hỏi phải phân xử

Có cần **worker runtime đã bị cô lập và QA âm tính hoàn tất** mới được **viết mã nguồn** của chính tokenizer, checker và guard hay không?

**Quyết định phương pháp: KHÔNG.** Không đồng nhất quyền viết tệp nguồn có kiểm soát với quyền thực thi mã nguồn đó. Nếu bắt buộc chứng minh Job Object / Write Broker chạy hiệu quả trước khi viết chúng, cổng tạo vòng lặp không thể thỏa mãn.

Tuy vậy, việc viết tệp hoặc tạo worktree là **thao tác ghi thật của control plane**, vẫn cần giới hạn đích, định danh chủ thể đáng tin cậy, Git pin và một permit riêng. Phát hiện DACL `Authenticated Users: Modify` ở P00 và `.git` không được giải quyết bằng cách nói `không có worker`; cần ngăn control plane thao tác ngoài allowlist và không tự gỡ/đổi ACL của thư mục dùng chung.

## 2. Phân định I0A và QA0

| Hạng mục | I0A-S — sau permit riêng | QA0 — yêu cầu permit mới |
|---|---|---|
| Viết/commit `.py`, `.json`, hướng dẫn kỹ thuật | **CÓ**, chỉ exact allowlist và nhánh triển khai đã khóa | QA code đầu vào phải được SHA-pin |
| Tạo worktree | **Có thể**, chỉ đúng 1 đường bên trong project và chỉ nếu permit riêng cho phép | Không tạo thêm worktree để né guard |
| Đọc đặc tả, golden SHA, review diff, phân tích cú pháp từ bên ngoài không import code P01 | Có thể cân nhắc nếu exact permit nêu rõ lệnh và phạm vi, tuyệt đối không sinh tệp runtime | Được phép theo QA0 nếu permit |
| Chạy/import module P01, `pytest`, `python -m ...`, train/encode/decode qua P01 | **CẤM** | Chỉ permit QA0, fixtures F0, fail closed |
| Sinh fixture file, snapshots, `merges.ttmbpe`, receipts chạy | **CẤM** | Chỉ QA0 riêng; không khoa học |
| Tạo Job Object, child process, thử crash/timeout/kill/disk quota | **CẤM** | Chỉ QA0 riêng với sandbox/broker và negative QA |
| Đọc/tải F1/F2, scientific TEST; huấn luyện BPE/GPT | **CẤM** | QA0 vẫn cấm; chỉ E0 sau approval khoa học |
| Đổi `lineage.md`, `main`, P00, `.git/hooks`, dữ liệu khác | **CẤM** | Không tự mở |

**Nhãn đề xuất:** `I0A_STATIC_SOURCE_AUTHORING_ONLY` và `QA0_DYNAMIC_EXECUTION_SEPARATE`. Không được gọi việc viết mã I0A là `implementation QA PASS`.

## 3. Đường thực thi quản trị an toàn và nhanh nhất

Hai lựa chọn để chủ sở hữu quyết định **ở cổng permit sau**, không thực hiện ở bước này:

**Phương án A — kiểm soát bởi GitHub, không dùng worktree Windows trong I0A-S:** tách nhánh triển khai từ một SHA đã ghim; tạo/chỉnh đúng file nguồn qua GitHub API; kiểm tra diff/SHA và độc lập review. Không thực thi mã. Ưu điểm: tránh rủi ro ghi lên P00/.git trên Windows khi tác giả chỉ viết mã; nhược điểm: chưa chứng minh khả năng build trên máy đích, sẽ cần bước sync/QA0 riêng. **Phải kiểm tra tự động hóa CI/workflows trước khi write**; không được mặc định push code là không chạy nếu repo có workflow tự kích hoạt. GitHub-first là phương án **ưu tiên để đánh giá** nếu không cần worktree local ở bước authoring.

**Phương án B — một worktree thủ công trong đúng local project:** `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105`; dùng tác tử/quy trình Git đáng tin cậy, preflight exact ref/branch/status/reparse/đường dẫn và trạng thái tài nguyên ở thời điểm cấp permit. Thao tác `git worktree add` sẽ sửa metadata **chỉ bên trong .git của project**, không phải thao tác thuần đọc; phải được cấp quyền chính xác và không mở rộng sang P00. Không được chọn phương án này nếu node offline hay không chứng minh được đường dẫn va chạm/nguồn, hoặc nếu chỉ có quyền của một worker chưa tin cậy. **Không yêu cầu QA0 restricted-token negative QA trước việc soạn mã**, nhưng control plane phải chịu trách nhiệm không ghi ngoài allowlist.

**Không tự kết hợp A và B**, không tạo 2 worktree, không cho phép `git clean/reset/prune`, không đổi ACL chung, không chạm project khác. Mọi Git worktree/dọn dẹp tương lai phải nằm trong root project; cleanup riêng `NOT_GRANTED`.

## 4. Danh mục tệp nguồn và lỗ hổng trong allowlist cũ

Hợp đồng hiện hữu `P01_D1_I0A_FILESYSTEM_AND_SOURCE_ALLOWLIST_DESIGN_20261105.md` mô tả **10 file ứng viên**: fixture generator, checker, cases, Job Object guard, write broker, source scope guard, evidence manifest, JSON config, golden vectors, QA report.

**Lỗi thiếu phạm vi để đạt mục tiêu sản phẩm:** danh mục đó **không chứa file mã triển khai cốt lõi B0/B1 Byte BPE hoặc pipeline tách nguồn**. Vì vậy không thể tuyên bố một I0A cho phép xây tokenizer nếu chỉ dùng 10 đường dẫn cũ.

Hai **đường ứng viên mới**, chưa cấp phép và phải kiểm tra va chạm với source tree trước permit:
- `src/p01/byte_bpe.py`: giao diện `encode_bytes/decode_bytes/encode_text/decode_text`, B0 và B1 deterministic, đọc/ghi định dạng merges theo H01; không chạy hoặc học mô hình;
- `src/p01/data_dedup_split.py`: cấu trúc pipeline dedup/split và tiêu chí H03, chỉ định nghĩa hàm và error contract; không đọc nguồn thật.

Tổng ứng viên **12 file** (10 cũ + 2 thêm). Các đường `src/p01/**` nói trên là **đề xuất**, không khẳng định thư mục `src` tồn tại hay tạo nó; nếu tree hiện hữu khác phải trình chỉnh lại allowlist trước permit, không tự tạo thêm tệp. Không tự thêm `train.py` hoặc `tokenizer_train*.py`, thay P00 `vocab_size=256`, hoặc cho B1 token vào P00 embedding chưa được chấp thuận.

Bộ golden bytes và test vector đã được ghi trong H04/I0A. I0A-S chỉ chép **dữ liệu literal vào source** sau grant, không tạo file fixture/test runtime.

## 5. Điều kiện tối thiểu cho một permit I0A-S thật, không quay lại ACL vô hạn

**Bắt buộc ngay trước permit:**
1. Chủ sở hữu đưa **quyết định riêng bằng lời rõ ràng** với chế độ A hoặc B, exact branch SHA, danh mục tệp, quyền Git/đường dẫn ghi, số lần và thời hạn. Lượt này **không** phải permit.
2. Đọc lại GitHub main/PR HEAD, trạng thái Draft, không merge, các file ứng viên có va chạm hay không, workflow triggers và danh mục nguồn. Với B còn cần Windows online, origin/main, P00 sạch, P01 path chưa tồn tại/reparse, local root và dự báo RAM/D tại thời điểm cấp.
3. Permit chỉ cho phép **authoring + review diff + SHA** theo danh mục; không import/run các file mới, không CI chạy tự động hoặc dùng công cụ gây side effects không định nghĩa.
4. Các file được tạo phải không ghi dữ liệu ngoài allowlist, không có động tác lúc import hoặc file scope ngoài root; tiêu chuẩn này được đánh giá **tĩnh**, không cần chạy worker.
5. Tách code writer và independent reviewer; cả hai đối chiếu SHA/contract; báo cáo trung thực `SOURCE_ONLY_NO_RUNTIME` và không tự mở QA0.

**Để QA0 chạy**, mới cần kiểm tra restricted token/AppContainer/broker, confined filesystem, Job Object attach-before-resume, quota, W01–W12, child escapes, negative path traversal/TOCTOU; **đây không phải tiền đề để viết mã I0A-S**.

## 6. Phán quyết phương pháp

`I0A_STATIC_SCOPE_SEPARATION=PASS_DESIGN_ONLY`  
`I0A_STATIC_SOURCE_AUTHORING_FEASIBLE_WITH_SCOPED_CONTROLLER=YES_CONDITIONAL`  
`I0A_STATIC_PERMIT_CANDIDATE_MODE=A_OR_B_OWNER_SELECTION_REQUIRED`  
`I0A_SOURCE_ALLOWLIST_12_FILES=PROPOSED_NOT_AUTHORIZED`  
`I0A_WINDOWS_CURRENT_PREFLIGHT=UNAVAILABLE_DEVICE_OFFLINE`  
`I0A_RUNTIME_WORKER_ISOLATION=DEFER_TO_QA0_NOT_WAIVED`  
`I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`QA0_EXECUTION_PERMIT=NOT_GRANTED`  
`E0_SCIENTIFIC_PERMIT=NOT_GRANTED`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_SOURCE_AUTHORING_AUTHORIZED=false`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`.

**Bước tiếp theo:** `TTM_P01_D1_I0A_STATIC_ONLY_EXACT_SCOPE_PERMIT_REQUEST`. Trình **một quyết định riêng** để chủ sở hữu chọn A (ưu tiên GitHub-first) hoặc B (một worktree Windows), exact SHA/allowlist và quyền một lần; khi được cấp mới triển khai source-only, không chạy code.
