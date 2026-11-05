# P01 D1 — Thẩm định quyết định phạm vi nguồn và tiền cấp quyền I0A

**Mã thẩm định:** `TTM_P01_D1_SOURCE_SCOPE_AND_I0_PREAUTH_GATE_DECISION_DESIGN_ONLY`  
**Ngày:** 05/11/2026. **Nhánh:** `design/p01-tokenizer-data-prereg-20261105` (PR #4).  
**Gốc GitHub main:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.  
**Phương thức:** đọc chéo bốn hợp đồng từ GitHub, so logic cho phép/từ chối, đối chiếu cách dùng Job Object với tài liệu Microsoft. **Không** đọc corpus, chạy lệnh trên Windows, chạy BPE/checker hoặc Job Object.

## 1. Bằng chứng và độ tin cậy

| Nguồn | Git blob SHA-1 đã đọc lại | Vai trò |
|---|---|---|
| `P01_D1_SOURCE_SCOPE_AND_MEMORY_METRIC_DECISION_20261105.md` | `27d38f57b3ede4de5f0543dd5869cf3bcdff42e5` | Quyết định H02/H05 hiện tại |
| `P01_D1_I0_PREAUTH_GATE_CONTRACT_20261105.md` | `1be5f0de7d3e45b030d393310cc377db911f57a1` | Ma trận I0A-01..09, QA0, E0 |
| `P01_D1_C07_C09_INDEPENDENT_DESIGN_ADJUDICATION_20261105.md` | `d573ed7ae933975da54f1fb5799dc2897a4c87fc` | H04 10/10 `PASS_DESIGN` |
| `P01_D1_H02_H05_SOURCE_RESOURCE_GATE.md` | `e58165d7d5cb1b01595a484aa64f2e35274480ab` | Giới hạn tài nguyên ứng viên và nguồn |
| Bộ hướng dẫn Microsoft Learn về Job Objects | Đường dẫn API công khai trong quyết định H05 | Xác nhận Job Commit ≠ RSS, CPU time ≠ Wall-clock |

Rà soát **15/15 tiêu chí nhất quán văn bản** đã đạt. Đây là một phép kiểm tra chéo hồ sơ, **không phải kiểm định động độc lập** hay đánh giá của bên thứ ba. 15/15 không phải 15 bài thử mô hình.

## 2. Đánh giá ba quyết định thiết kế

### D-SOURCE — F0 hay F1/F2?

**PASS_DESIGN_SCOPE:** chọn **F0-only cho thiết kế và rà soát oracle**, vì trong hồ sơ P01 chưa có bất kỳ nguồn F1/F2 nào với nguồn gốc, giấy phép, quyền học tokenizer, trạng thái PII và SHA được duyệt. Không suy ra nguồn ngoài dự án không tồn tại; chỉ kết luận **không có nguồn đủ chứng cứ để nhận vào P01 hiện tại**.

Dữ liệu F0 không thể tự nhiên trở thành TRAIN/VALIDATION/TEST khoa học. Chưa được phép materialize fixture F0 hoặc chạy checker; chỉ tiếp tục chuẩn bị hồ sơ.

### D-MEMORY — `max_job_commit_bytes`

**PASS_DESIGN_CANONICAL_FIELD:** chọn `max_job_commit_bytes=4294967296` (4 GiB) để thay thế tên ứng viên `max_peak_rss_bytes` trong **cấu hình kế nhiệm tương lai**, không sửa biên bản cũ. Job Object với `JOB_OBJECT_LIMIT_JOB_MEMORY` cưỡng chế tổng committed virtual memory trên toàn job, không cưỡng chế RSS và không tự bảo vệ file. `max_wall_seconds=1800` là wall-clock của supervisor, không phải Job CPU time.

**HOLD_IMPLEMENTATION:** chưa có cấu hình kế nhiệm, Job Object được cài, tiến trình con được bảo vệ, write broker/ACL, golden receipt hoặc QA âm tính. Trường `max_job_commit_bytes` được chuẩn hóa **trên giấy**, không tự tạo giá trị runtime đã đo hay cấp permit.

### D-I0 — Điều kiện tiền cấp quyền

**PASS_CONTRACT_STRUCTURE:** phân tầng D1 (thiết kế), I0A (triển khai tĩnh F0 nếu được cấp riêng), QA0 (chạy kỹ thuật F0/guard nếu được cấp riêng), E0 (corpus thật sau khóa khoa học và source ALLOW). Việc phân tầng tránh điều kiện vòng tròn là yêu cầu checker đã chạy trước khi được quyền viết checker.

**PREAUTH_HOLD:** các đường cấp quyền vẫn thiếu chứng cứ và quyết định riêng; không có giấy phép ngầm phát sinh từ việc có văn bản quy trình.

## 3. Phân loại chính xác I0A-01..09

| ID | Trạng thái | Tại sao chưa được phép triển khai |
|---|---|---|
| I0A-01 — Git/local | **HOLD_EVIDENCE** | Chưa có xác minh Git sạch/HEAD và worktree trên Windows **tại thời điểm cấp quyền mới** |
| I0A-02 — Worktree/đường dẫn | **HOLD_EVIDENCE** | Chưa có vị trí worktree P01, allowlist và đánh giá reparse được phê duyệt |
| I0A-03 — Oracle/định dạng | **HOLD_EVIDENCE** | Có 10/10 hợp đồng `PASS_DESIGN` nhưng chưa có golden binary merges/manifest pin byte trước triển khai |
| I0A-04 — Phạm vi F0 | **PASS_DESIGN_SCOPE** | Chỉ F0 thiết kế; không tự cho phép ghi fixture hoặc chạy |
| I0A-05 — Ngân sách/đơn vị | **PASS_DESIGN_ONLY** | Trần `max_job_commit_bytes` đã rõ, chưa có config thực thi |
| I0A-06 — Kiến trúc Job Object/ghi đĩa | **PASS_DESIGN_ONLY** | Quy trình suspended/assign/broker đã nêu, chưa kiểm định trên Windows |
| I0A-07 — Tài nguyên hiện tại | **HOLD_RECHECK** | Snapshot Windows trước đây đạt ứng viên, phải đo mới ngay trước permit |
| I0A-08 — Danh mục mã/QA | **HOLD_EVIDENCE** | Chưa có danh sách file mã cho I0A, checker riêng và golden evidence byte |
| I0A-09 — Quyền quyết định | **NOT_GRANTED** | Không có quyết định chính xác cấp quyền viết mã/tạo worktree/chạy |

**Tổng:** `3 PASS_DESIGN_ONLY`, `5 HOLD_EVIDENCE`, `1 NOT_GRANTED`. Không có bài kiểm tra I0A thực thi; các cổng khác nhau không được cộng thành “8/9 PASS” hoặc biến `NOT_GRANTED` thành `HOLD`.

## 4. Các nguy cơ dẫn tới PASS giả

1. Từ vựng BPE 2048 đưa trực tiếp vào P00 256 ID: dù một mẫu chạy được với ID thấp, vẫn vi phạm hợp đồng B1/P00.
2. Chính sách F0-only bị coi thành quyền đọc corpus F1/F2: không hợp lệ; mỗi source cần `ALLOW` riêng.
3. Bộ đếm RSS hoặc RAM còn trống được dùng để báo Job Commit đạt: sai đại lượng; phải báo `CONTRACT_MISMATCH`.
4. QA0 bị ngộ nhận đã đạt vì Job Object API tồn tại trong tài liệu: sai, mã/guard chưa chạy.
5. Cổng E0 bị mở khi QA0 synthetic PASS nhưng nguồn F1/F2 thiếu quyền: E0 vẫn `HOLD`.
6. Một chương trình tự ghi `PASS` vào receipt nhưng độc lập không đọc lại file hoặc chưa có golden manifest: `EVIDENCE_INTEGRITY_HOLD`.

## 5. Điều kiện gửi quyết định I0A tiếp theo

Chỉ được trình một quyết định riêng về triển khai tĩnh F0 sau khi: (a) mốc Git/workspace và khả năng rollback đã được kiểm tra chỉ đọc; (b) danh mục tệp/giới hạn ghi và đường dẫn worktree đề xuất được duyệt; (c) golden byte format/negative QA và các quy tắc không ghi đè được pin; (d) ngân sách tức thời đủ, quản trị nguồn F0 rõ; (e) xác nhận thực thi đúng một lần và chủ thể quyết định cấp quyền I0A ký nhận. Nếu **bất kỳ** cổng nào còn HOLD, quyết định I0A phải là NOT_GRANTED.

Điều kiện cho QA0/E0 và permit dữ liệu là **các quyết định kế tiếp**, không được mở khi I0A mới đủ hồ sơ. Nếu có thay đổi khoa học về nguồn, metric, thuật toán, ngưỡng hoặc split, phải dùng hồ sơ kế nhiệm chứ không ghi đè nguồn D1.

## 6. Phán quyết

`P01_D1_SOURCE_SCOPE_DECISION=PASS_F0_ONLY_DESIGN`  
`P01_D1_F1_F2_SOURCE_ADMISSION=HOLD_NO_VERIFIED_SOURCE`  
`P01_D1_MEMORY_METRIC_CANONICALIZATION=PASS_DESIGN_ONLY`  
`P01_D1_I0A_PREAUTH_CONTRACT=PASS_SCOPED_DOCUMENT`  
`P01_D1_I0A_PREAUTH_ADMISSION=HOLD_5_EVIDENCE_1_PERMISSION`  
`P01_D1_H04_CHECKER_CONTRACT=PASS_10_OF_10_DESIGN_ONLY`  
`P01_D1_H04_DYNAMIC_QA=NOT_EXECUTED`  
`P01_D1_H05_RUNTIME_GUARD_QA=NOT_EXECUTED`  
`P01_D1_SCIENTIFIC_PREREG_LOCK=NOT_GRANTED`  
`P01_I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`P01_QA0_EXECUTION_PERMIT=NOT_GRANTED`  
`P01_E0_SCIENTIFIC_EXECUTION_PERMIT=NOT_GRANTED`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_DATA_DOWNLOAD_AUTHORIZED=false`  
`P01_TOKENIZER_TRAINING_AUTHORIZED=false`  
`P01_MODEL_TRAINING_AUTHORIZED=false`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`

**Bước thực hiện tiếp theo:** `TTM_P01_D1_I0A_F0_STATIC_IMPLEMENTATION_PREAUTH_EVIDENCE_AND_DESIGN_ADJUDICATION` — chuẩn bị bằng chứng chính xác cho I0A-01/02/03/07/08 bằng quy trình chỉ đọc và hồ sơ, sau đó quyết định cấp quyền riêng. Chưa tạo worktree, triển khai mã, tải corpus, chạy QA hoặc huấn luyện.
