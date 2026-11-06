# P01 D1 — Quyết định phạm vi nguồn và chuẩn hóa đại lượng giới hạn bộ nhớ

**Mã quyết định:** `TTM_P01_D1_SOURCE_SCOPE_AND_MEMORY_METRIC_DESIGN_DECISION`  
**Ngày:** 05/11/2026. **Nhánh:** `design/p01-tokenizer-data-prereg-20261105`.  
**Mốc trước PR #4:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.  
**Chế độ:** `DESIGN_ONLY_NO_IMPLEMENTATION`. Tài liệu này là quyết định thiết kế cho đường tiền cấp quyền tương lai, **không phải permit I0, permit dữ liệu hay khóa thực nghiệm khoa học**.

## 1. Quyết định riêng H02 — Phạm vi nguồn

| Phạm vi | Chứng cứ có trong hồ sơ | Quyết định tại D1 | Phép làm được lúc này |
|---|---|---|---|
| **F0 — Mẫu byte/tài liệu giả lập tự tạo** | Đặc tả F00–F11, oracle byte/SHA, ví dụ C07/Jaccard, hợp đồng checker C01–C10 đã được thẩm định ở mức thiết kế | **CHỌN `F0_ONLY_DESIGN_AND_ORACLE_REVIEW`** | Đọc/viết tài liệu, xác minh bất biến và thiết kế QA; **chưa cấp quyền tạo file fixture, code hay chạy** |
| **F1 — Văn bản sở hữu hoặc được cấp quyền cụ thể** | Chưa có danh mục nguồn được phê duyệt gồm quyền học tokenizer, SHA-256 và trạng thái PII | **`HOLD_NO_APPROVED_SOURCE`** | Chỉ soạn mẫu hồ sơ xin duyệt nguồn; không thu thập hoặc đọc nguồn để huấn luyện |
| **F2 — Nguồn bên thứ ba/corpus công khai** | Có ví dụ chính sách giấy phép nhưng chưa có source snapshot cụ thể, quyền sử dụng từng nguồn hoặc chứng cứ điều khoản áp dụng | **`HOLD_NO_APPROVED_SOURCE`** | Chỉ nghiên cứu quyền sử dụng bằng nguồn công khai; không tải corpus |
| Nguồn từ dự án khác/tài khoản/email | Không có quyết định riêng về quyền và phạm vi | **EXCLUDED** | Không truy xuất hoặc đưa vào P01 |

**H02 tại thời điểm này:** `SOURCE_SCOPE=F0_ONLY_DESIGN_AND_ORACLE_REVIEW`; `H02_F1_F2_RIGHTS_ADMISSION=HOLD`. Việc đã chọn F0 **không biến F0 thành TRAIN/VALIDATION/TEST khoa học** và không cho phép học BPE để kết luận về chất lượng hay tỉ lệ token/byte trên corpus thật.

### Điều kiện cấp nguồn F1/F2 về sau, bắt buộc theo từng nguồn

Một `source_id` chỉ được đề xuất `ALLOW` khi có: chủ sở hữu/đơn vị cấp phép, URL/địa chỉ gốc, bằng chứng quyền học tokenizer và tạo bản dẫn xuất, nghĩa vụ ghi công/tái phân phối, chính sách bảo mật/PII, điều khoản lưu giữ/xóa, `source_snapshot_id`, số byte, số tài liệu, `source_sha256`, trạng thái rà soát và chủ thể phê duyệt. Thiếu một mục cần thiết ⇒ `PENDING_OR_REJECT`, không đưa vào TRAIN, không tải thay thế và không mở E0.

Đường F1/F2 sẽ có quyết định thẩm định nguồn và khóa thí nghiệm **riêng** trước mọi thu thập hoặc học BPE. Đề xuất nguồn Wikimedia hoặc dữ liệu “công khai” trước đây **không** phải quyết định `ALLOW`.

## 2. Quyết định riêng H05 — Đại lượng bộ nhớ chuẩn cho thiết kế I0

**Chấp thuận làm chuẩn hợp đồng thiết kế kế nhiệm (Design-level Canonical Field):**

`max_job_commit_bytes = 4294967296` (**4 GiB**)

Đại lượng này là **tổng committed virtual memory của tất cả tiến trình trong Windows Job Object** (Job-wide Commit), được thiết kế để cưỡng chế qua `JOBOBJECT_EXTENDED_LIMIT_INFORMATION.JobMemoryLimit` cùng `JOB_OBJECT_LIMIT_JOB_MEMORY`. Đây **không** phải RAM vật lý khả dụng, RSS/Working Set hoặc `PrivateBytes` của một tiến trình. Nguồn Microsoft Learn:
- https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information
- https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information
- https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects

| Thuộc tính | Quyết định thiết kế | Cách dùng |
|---|---|---|
| `max_job_commit_bytes` | `4294967296` (4 GiB), **CANONICAL_FOR_I0_DESIGN** | Giới hạn bộ nhớ cam kết toàn Job, chỉ trở thành hard limit khi Job Object được thiết lập và kiểm tra thật |
| `max_peak_rss_bytes` lịch sử H05 | **DEPRECATED_FOR_FUTURE_GUARD_CONFIG_NOT_REWRITTEN** | Giữ nguyên tài liệu cũ, **không** tự quy đổi hay diễn giải biên bản RSS thành Job Commit |
| `peak_job_commit_bytes` | `MEASUREMENT_REQUIRED_AT_QA0` | Số đo giám sát đỉnh Job Commit, không đủ nếu chưa xác minh cờ giới hạn |
| `peak_working_set_bytes` | `OPTIONAL_DIAGNOSTIC` | Không được dùng để quyết định PASS giới hạn 4 GiB |
| `min_free_ram_preflight_bytes` | `8589934592` (8 GiB) — ngưỡng ứng viên | Đo mới trước lúc chạy; console trước đây chỉ là ảnh chụp |
| `max_wall_seconds` | `1800` | Theo thời gian thực của supervisor, không phải `JOB_OBJECT_LIMIT_JOB_TIME` (CPU time) |
| `max_temp_and_evidence_bytes` | `2147483648` (2 GiB) | Cần Write Broker/quyền ghi và kiểm thử riêng; Job Object memory limit **không** cưỡng chế quota đĩa |

**Tính nguyên trạng:** không sửa `configs/phase0_reference.json`, không tạo config runtime P01 và không thay tên trường trong biên bản H05 lịch sử. Khi I0A được cấp phép riêng, cấu hình kế nhiệm phải dùng `max_job_commit_bytes`; nếu phát hiện cả hai tên cũ/mới trong cùng config với ý nghĩa mơ hồ ⇒ `FAIL_CLOSED_CONFIG_CONFLICT`. Không được tự bỏ trần hoặc thay cơ chế khi Job Object không khả dụng.

**Phân biệt giới hạn và hành vi dừng:** Job Memory Limit có thể từ chối cấp phát vượt trần nhưng không mặc nhiên kết thúc Job. Trách nhiệm supervisor là phân loại lỗi và kết thúc toàn cây theo quy tắc đã duyệt; `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` là biện pháp bảo vệ khi handle cuối đóng, không thay việc giám sát.

## 3. Số đo tài nguyên hiện có và giới hạn suy luận

Console Windows do người dùng cung cấp tại `2026-11-05T11:01:18.0864528Z`: RAM khả dụng `10.959 GiB`, D: trống `34.869 GiB`, D: sau dự phòng `32.807 GiB`, đều đạt ngưỡng ứng viên. Đây chỉ là **snapshot chỉ đọc**, không có Job Object được khởi tạo hoặc kiểm thử. Chưa có `peak_job_commit_bytes` thực nghiệm, chạy timeout, bảo vệ quota 2 GiB hoặc chứng cứ hệ thống tệp không bị vượt quyền.

Kết luận đúng: `H05_PRESTART_CANDIDATE_CAPACITY=PASS_AT_SNAPSHOT`; `H05_RUNTIME_GUARD_QA=NOT_EXECUTED`. Không nhận `I0_READY` chỉ từ số RAM/đĩa trống.

## 4. Đánh giá cho bước kế tiếp

| Hạng mục | Kết luận tại D1 |
|---|---|
| Chọn F0 làm phạm vi **thiết kế và kiểm tra oracle** | `PASS_SCOPE_DECISION` |
| Quyền nguồn F1/F2 | `HOLD` |
| Chuẩn tên/đơn vị bộ nhớ **trong tài liệu thiết kế kế nhiệm** | `PASS_DESIGN_CANONICAL_FIELD` |
| Cấu hình/runtime Job Object trên Windows | `NOT_IMPLEMENTED` |
| Huấn luyện tokenizer hoặc mô hình | `NOT_AUTHORIZED` |
| Khóa khoa học D1 / permit I0 | `NOT_GRANTED` |

**Quyết định cuối:** `TTM_P01_D1_SOURCE_SCOPE_AND_MEMORY_METRIC=DECIDED_DESIGN_ONLY`. Mọi nguồn dữ liệu, mã checker/guard, worktree P01, QA động hoặc thay cấu hình phải qua quyết định riêng. Xem `P01_D1_I0_PREAUTH_GATE_CONTRACT_20261105.md`.
