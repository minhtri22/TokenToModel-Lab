# P01 D1 — H02 và H05: Điều kiện nguồn dữ liệu hợp pháp và ngân sách tài nguyên

**Trạng thái:** `SOURCE_UNSELECTED_RESOURCE_BUDGET_PROPOSED_NOT_LOCKED`. Đây là yêu cầu cấp quyền tương lai, **không** phải lệnh tải dữ liệu.

## 1. H02 — Quyết định về nguồn dữ liệu

| Loại nguồn | Quyết định thiết kế | Có được dùng tại thời điểm này? |
|---|---|---|
| F0 — Chuỗi giả lập do dự án tự định nghĩa (Synthetic Fixture) | Dùng làm bộ kiểm tra kỹ thuật, không huấn luyện mô hình/bộ BPE | Chỉ lưu đặc tả trên GitHub; chưa chạy |
| F1 — Văn bản do người dùng sở hữu hoặc có quyền hợp lệ | Chỉ nhận từng nguồn nếu có bằng chứng quyền dùng để học thuật toán, tạo dẫn xuất và phạm vi phân phối mong muốn | **Chưa**, hiện không có danh mục nguồn được duyệt |
| F2 — Văn bản từ bên thứ ba/corpus công khai | Không mặc định công khai = được phép học hoặc tái phân phối; phải kiểm tra giấy phép/điều khoản từng nguồn | **Cấm tải ở D1 thiết kế** |
| Dữ liệu từ dự án khác, email, tài khoản kết nối | Chỉ xét sau quyết định riêng về phạm vi và quyền riêng tư | **Không đưa vào P01** |

**Danh mục nguồn bắt buộc (Source Admission Manifest)** trước D1 lock:

- `source_id`, `original_location`, `owner_or_author`, `license_id`, `license_evidence_uri`, `rights_reviewed_at`, `reviewer`, `permitted_uses` (gồm huấn luyện tokenizer, tạo dẫn xuất, tái phân phối nếu áp dụng).
- `source_sha256`, `byte_count`, `document_count`, `encoding`, `pii_status`, `copyright_status`, `admission_decision`.
- `source_snapshot_id` và phân loại các hạn chế địa lý, thời gian, xóa, ghi nhận tác giả.
- Nếu không xác nhận đầy đủ, đặt `admission_decision=REJECT_OR_PENDING`; mọi bản ghi TRAIN phải có quyết định `ALLOW` rõ ràng.

**Hiện trạng được kiểm chứng:** chưa có source manifest F1/F2 được cung cấp hoặc thẩm định. Do đó **H02 không thể được đóng thực tế**; không tự tạo giấy phép hoặc chọn corpus thay người dùng.

## 2. H05 — Ngân sách thử nghiệm đề xuất (Prospective Resource Budget)

Bộ giới hạn tối đa được chọn ở mức **ứng viên D1** để có thể tiền kiểm trên máy Windows sau này. Các giá trị này không khẳng định RAM/đĩa hiện đang trống và chưa là permit:

| Tham số | Giá trị đề xuất | Tác dụng |
|---|---:|---|
| `max_source_bytes` | 67.108.864 byte (**64 MiB**) | Ngăn nhận corpus quá lớn |
| `max_document_count` | **2.000 tài liệu** | Giới hạn thuật toán đối chiếu từng cặp gần trùng |
| `max_peak_rss_bytes` | 4.294.967.296 byte (**4 GiB**) | Giới hạn RAM đỉnh của tiến trình thực thi tương lai |
| `min_free_ram_preflight_bytes` | 8.589.934.592 byte (**8 GiB**) | Chặn nếu RAM thực tế không đủ dự phòng |
| `min_free_d_preflight_bytes` | 17.179.869.184 byte (**16 GiB**) | Chặn khi ổ D: không còn dự phòng |
| `min_free_d_after_reserve_bytes` | 12.884.901.888 byte (**12 GiB**) | Phải còn chỗ trống sau ngân sách cấp phát |
| `max_temp_and_evidence_bytes` | 2.147.483.648 byte (**2 GiB**) | Hạn chế bộ nhớ đĩa cho dữ liệu trung gian và log |
| `max_wall_seconds` | **1.800 giây** | Chặn lượt chạy quá thời gian |
| `execution_device` | CPU, không GPU | Không làm phát sinh kiểm định XPU/PagedAttention |
| `target_vocab_size` | **2.048** (đề xuất B1 chính) | Chỉ cấp phép thực nghiệm BPE khi có quyết định riêng |

Các giá trị là **giới hạn ứng viên được chọn trước khi đo dữ liệu thật**, không phải giá trị tối ưu. Việc sửa giá trị sau khi đã xem kết quả phải dùng hồ sơ kế nhiệm (Successor), ghi rõ lý do.

### Tính toán trước khi thực thi

- Đọc RAM khả dụng thực tế, dung lượng ổ D: trống, trạng thái CPU và đường dẫn cache/temp, kiểm tra mọi đường dẫn đều ở trong `D:\WORK\RESEARCH\TokenToModel-Lab`.
- Định lượng dung lượng dự kiến: bản gốc bất biến + bản xử lý + chỉ mục gần trùng + bộ quy tắc BPE + log + biên bản. Nếu tổng vượt `max_temp_and_evidence_bytes` hoặc đĩa sau dự phòng còn dưới 12 GiB, **từ chối**.
- Cơ chế bảo vệ RAM/thời gian (Process Resource Guard) phải được triển khai và kiểm tra âm tính trước khi chạy; không dựa vào thông số RAM 32 GiB lắp đặt.
- Giới hạn phải áp dụng **trong** lượt chạy và dừng an toàn khi sắp vượt, không chỉ kiểm tra tại điểm bắt đầu.
- Khi quá tải, ghi `RESOURCE_LIMIT_STOP`; không tự giảm cỡ corpus để tuyên bố PASS cùng một kế hoạch nghiên cứu.

## 3. Phạm vi hệ thống tệp và quyền truy cập

Sau khi được duyệt và khi có worktree P01 hợp lệ trong workspace dự án:
- `datasets/approved_sources/`: dữ liệu gốc có quyền hợp lệ, chỉ đọc sau nhận.
- `datasets/derived/`: bản dẫn xuất và danh mục SHA-256.
- `_tmp/p01/` hoặc `tmp/p01/`: trung gian, chỉ trong workplace.
- `evidence/p01/`: biên bản và kiểm tra kết quả.
- `cache/p01/`: bộ nhớ đệm; không ghi ngoài dự án.

**Tất cả chỉ là đường dẫn dự kiến. Không có thư mục nào được tạo ở bước D1 này.** Không dọn P00; mọi lệnh xóa hoặc chuyển đường dẫn cần quyết định riêng.

## 4. Điều kiện dừng và trạng thái

- Không có nguồn `ALLOW` ⇒ `H02=HOLD_SOURCE_RIGHTS`.
- Không đo được RAM/đĩa tại thời điểm chạy ⇒ `H05=HOLD_RESOURCE_PREFLIGHT`.
- Chưa có bộ giới hạn runtime được kiểm chứng ⇒ `H05=HOLD_GUARD_QA`.
- Bất kỳ nguồn thiếu quyền, dữ liệu cá nhân chưa xử lý hoặc quyền mơ hồ ⇒ `REJECT_OR_QUARANTINE`.
- Không đủ 30 nhóm sau gom trùng ⇒ `INSUFFICIENT_GROUPS`, không tạo TEST hợp lệ.

**Quyết định:** `H02_POLICY_SPEC_DEFINED_BUT_ADMISSION_PENDING`; `H05_PROSPECTIVE_LIMITS_DEFINED_BUT_NOT_MEASURED`; `P01_D1_LOCK=HOLD`; `P01_DATA_DOWNLOAD=FORBIDDEN`; `P01_BPE_TRAINING=FORBIDDEN`.
