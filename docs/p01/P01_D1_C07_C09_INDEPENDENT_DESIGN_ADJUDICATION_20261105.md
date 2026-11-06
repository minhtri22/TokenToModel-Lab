# P01 D1 — Thẩm định lại độc lập C07/C09 sau khi đóng khoảng trống thiết kế

**Quyết định:** `TTM_P01_D1_G04_03_06_REMAINING_DESIGN_HOLD_CLOSURE`  
**Ngày:** 05/11/2026  
**Phạm vi:** đối chiếu oracle số học từ byte giả lập và hợp đồng Windows ở mức tài liệu, **không** viết/chạy mã dự án, không đo tài nguyên động, không mở I0.  
**Nhánh:** `design/p01-tokenizer-data-prereg-20261105`, GitHub main đối chứng `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.

**Nguồn chính xác đọc lại từ GitHub:**
- C07 oracle: `docs/p01/P01_D1_C07_G04_03_EXACT_5GRAM_ORACLE_DESIGN_20261105.md`, Git blob `77643bf8aa4f7901ba057452b740a02d914560d7`.
- C09 Job Object: `docs/p01/P01_D1_C09_G04_06_WINDOWS_JOB_OBJECT_GUARD_DESIGN_20261105.md`, Git blob `be817aa97892b7f2c0f56d689f551b17395f5a5f`.
- H05 phụ lục phân biệt RSS và commit: Git blob `e58165d7d5cb1b01595a484aa64f2e35274480ab`.
- Lượt G04-08 trước sửa: `docs/p01/P01_D1_G04_08_INDEPENDENT_CONTRACT_READBACK_20261105.md`. Giữ nguyên HOLD lịch sử trong báo cáo đó; quyết định mới không thay nội dung nguồn cũ.

## 1. Phương pháp đối chứng độc lập

**C07:** dùng dữ liệu giả lập tự tạo độc lập với BPE và dự án; dựng tập 5-gram và phép giao/hợp bằng **hai đường tính khác nhau** (Python tham chiếu và JavaScript xét tập ký tự), đối chiếu SHA-256 raw byte, phép AND ngưỡng chiều dài, trường hợp Unicode nhiều byte và nhóm bắc cầu. Không materialize fixture trong workplace Windows; không đọc hay sử dụng corpus TRAIN/TEST.

**C09:** đối chiếu thuật ngữ và cờ Windows Job Object với tài liệu Microsoft công khai về giới hạn Job committed memory, tiến trình con, nested job, tạo process ở trạng thái suspended, sự kiện và time limit. Đây là **đối chiếu tài liệu kỹ thuật**, không phải chạy Job Object thực tế, không chứng minh tính chính xác của mã chưa tồn tại.

Bộ kiểm tra cấu trúc cuối đã xác nhận có oracle byte, nhóm, ranh giới Jaccard, nguồn Unicode, mô hình limit, cổng deny-before-resume, timeout wall, giới hạn đĩa riêng và 12 trường hợp âm tính. Hai tiêu chí dò từ vựng đầu tiên không khớp vì Markdown đặt tên hằng trong dấu backtick; kiểm tra lại theo đúng mệnh đề cho kết quả đạt. Lỗi của bộ dò **không** được ghi thành FAIL khoa học.

## 2. Thẩm định C07 — Chống rò rỉ dựa trên oracle cụ thể

| Kiểm tra | Bằng chứng | Kết luận |
|---|---|---|
| Q07-01 | 7 chuỗi ASCII tự tạo với SHA-256 byte nguồn đã ghim và biểu diễn hex | PASS_DESIGN |
| Q07-02 | Dữ liệu văn bản dài ≥40 mã điểm; Jaccard dưới/bằng/trên `0,85` là `33/41`, `34/40`, `35/39` | PASS_DESIGN |
| Q07-03 | Tập 5-gram gốc 36 phần tử và các chênh lệch LOSS/ADD hoàn chỉnh; không chỉ so tỷ số | PASS_DESIGN |
| Q07-04 | Điều kiện độ dài `40/50=0,8` được nhận, `40/51<0,8` bị loại dù cùng tập 5-gram | PASS_DESIGN |
| Q07-05 | A gần B, B gần C, A không gần C; cả ba cùng thành phần liên thông, group SHA theo prefix 17 byte | PASS_DESIGN |
| Q07-06 | Hai chuỗi Unicode `ắ` lặp 40 và `ắ` lặp 39 + `é`; code-point 5-gram khác byte 5-gram, raw SHA phân biệt | PASS_DESIGN |
| Q07-07 | Có chặn FAIL nếu sai một 5-gram, chỉ so `group_id`, tính nhầm theo byte, hoặc dùng làm tròn float | PASS_DESIGN |

**Verdict C07:** `C07_CONTRACT_DESIGN=PASS`, **không phải** `LEAKAGE_QA=PASS`. Những ngưỡng trong H03 là đề xuất chưa được đánh giá trên corpus thật; bản paraphrase ngữ nghĩa vẫn có thể lọt. Cần trình checker được cấp phép ở cổng sau với oracle độc lập và negative QA trước mọi kết luận khoa học.

## 3. Thẩm định C09 — Giới hạn Windows

| Kiểm tra | Hợp đồng và tính đúng về thiết kế | Kết luận |
|---|---|---|
| Q09-01 | Đo cưỡng chế `Job-wide Committed Memory`, trần `4294967296` byte, **không** hoán đổi với RSS | PASS_DESIGN |
| Q09-02 | `JOB_OBJECT_LIMIT_JOB_MEMORY`, `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, không bật hai cờ breakaway | PASS_DESIGN |
| Q09-03 | Worker `CREATE_SUSPENDED`, chỉ resume sau `AssignProcessToJobObject` và `IsProcessInJob` PASS | PASS_DESIGN |
| Q09-04 | Kiểm tra nested-job, child không nằm trong job, handle lộ quyền; mọi thất bại phải chặn I0 | PASS_DESIGN |
| Q09-05 | `1800s` dùng đồng hồ wall-clock, **không** đổi thành CPU user time; giám sát viên bên ngoài job | PASS_DESIGN |
| Q09-06 | Giới hạn byte tệp là cổng riêng: broker + hạn mức trước ghi + hạn chế quyền filesystem, không giả định Job Object tự giới hạn đĩa | PASS_DESIGN |
| Q09-07 | W01–W12 thử vượt commit, vượt wall-clock, vượt quota, breakaway, nested job sai, sai receipt, hết đĩa | PASS_DESIGN |
| Q09-08 | Phân biệt allocation-failure, notification không được bảo đảm và trạng thái `INCONCLUSIVE`; không tự tuyên bố PASS nếu thiếu evidence | PASS_DESIGN |

**Verdict C09:** `C09_CONTRACT_DESIGN=PASS`. Đây là quyết định về **tính đầy đủ của đặc tả có điều kiện fail-closed**, không phải chứng minh Windows Job Object hoặc write broker đã được triển khai/chạy. Quyền I0 sẽ **bị từ chối** nếu không thể chứng minh worker/child thực sự được hạn chế và kiểm thử âm tính từng cổng đạt.

**Nguồn API Microsoft:**
- https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
- https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information
- https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information
- https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs
- https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw

## 4. Phân loại kết quả H04

| Nhóm | Trước đợt đóng C07/C09 | Sau đối chiếu độc lập thiết kế |
|---|---|---|
| C01–C06, C08, C10 | 8 PASS_DESIGN | Giữ nguyên |
| C07 | HOLD_DESIGN | **PASS_DESIGN** |
| C09 | HOLD_DESIGN | **PASS_DESIGN** |
| Tổng hợp | 8 PASS / 2 HOLD | **10 PASS_DESIGN / 0 HOLD_DESIGN / 0 FAIL_DESIGN** |
| Bộ kiểm tra P01 thực thi | 0 | **0** |

**Không suy diễn**: 10/10 ở đây chỉ là số hợp đồng đủ rõ **để một bộ checker trong tương lai có thể được triển khai và đánh giá độc lập**, không phải độ chính xác của tokenizer, khả năng chống rò rỉ tuyệt đối hoặc bảo đảm chương trình không vượt tài nguyên.

## 5. Các cổng vẫn chặn D1 và I0

1. **H02:** chưa có nguồn F1/F2 thực tế đủ giấy phép, SHA-256 và rà soát PII; phạm vi chỉ là `F0_ONLY_DESIGN_AND_ORACLE_REVIEW`. Không được huấn luyện BPE trên F0 để suy diễn về corpus thật.
2. **H04 thực thi:** chưa có checker/generator nào được cho phép viết mã hoặc chạy; không có QA âm tính, cross-process reproducibility hoặc golden binary merges file trên Windows.
3. **H05:** số đo nguồn lực chỉ là ảnh chụp; chưa có bộ Job Object, cơ chế quyền ghi, broker/quota hoặc thử tải âm tính. Định danh lại `max_peak_rss_bytes` thành `max_job_commit_bytes` vẫn cần quyết định cấu hình riêng trước I0.
4. **G04-07:** cần một mẫu golden manifest theo byte định dạng JCS và đường đọc lại độc lập ở cổng triển khai; chưa có trình viết/đọc thực tế.
5. **Git quản trị:** PR #4 phải tiếp tục **nháp, chưa hợp nhất**; giữ nguyên `main`, mã P00 và mọi cây làm việc đã phê duyệt; không tạo worktree P01.

## 6. Quyết định cuối

`TTM_P01_D1_C07_CONTRACT=PASS_DESIGN`  
`TTM_P01_D1_C09_CONTRACT=PASS_DESIGN`  
`TTM_P01_D1_H04_CHECKER_CONTRACT=PASS_10_OF_10_DESIGN_ONLY`  
`TTM_P01_D1_H04_DYNAMIC_QA=NOT_EXECUTED`  
`TTM_P01_D1_SCIENTIFIC_PREREG_LOCK=HOLD_H02_H04_RUNTIME_H05_GUARD`  
`TTM_P01_I0_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_DATA_DOWNLOAD_AUTHORIZED=false`  
`P01_TOKENIZER_TRAINING_AUTHORIZED=false`  
`P01_MODEL_TRAINING_AUTHORIZED=false`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`

**Bước tiếp theo:** `TTM_P01_D1_SOURCE_SCOPE_AND_I0_PREAUTH_GATE_DECISION_DESIGN_ONLY` — quyết định độc lập phạm vi F0-only hay nguồn F1/F2 được duyệt, chuẩn hóa dự kiến `max_job_commit_bytes`, xem xét cách triển khai QA/guard ở I0; **chưa mở I0, chưa code hoặc chạy**.
