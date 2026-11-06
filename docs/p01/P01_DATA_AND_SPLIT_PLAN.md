# P01 — Kế hoạch nguồn dữ liệu, giấy phép, chia tập và chống rò rỉ

**Trạng thái:** `PROPOSED_NO_DATA_ACQUIRED`. Chưa tải hoặc đọc corpus để huấn luyện, chưa cấp quyền ghi bất kỳ tập dữ liệu mới nào.

## 1. Phân cấp dữ liệu và quyết định

| Cấp dữ liệu | Nguồn dự kiến | Được làm trong bước thiết kế này? | Vai trò |
|---|---|---|---|
| F0 — Trường hợp kiểm thử được viết trong tài liệu (Synthetic Fixtures) | Chuỗi nhỏ tự tạo, không trích từ corpus thực hoặc dữ liệu cá nhân | Chỉ mô tả, chưa chạy | Kiểm tra Unicode, mã hóa–giải mã, lỗi và bất biến |
| F1 — Tập văn bản thuộc quyền sử dụng hợp lệ (Licensed/Owned Corpus) | Nội dung do người dùng sở hữu hoặc có giấy phép phù hợp | **Chưa**; cần danh mục nguồn và quyết định riêng | Huấn luyện bộ tách token BPE ở bước được cấp quyền |
| F2 — Bộ dữ liệu bên ngoài quy mô lớn (External Corpus) | Nguồn công khai có điều khoản rõ ràng, không đồng nghĩa được tái phân phối | **Cấm tải ở bước này** | Ứng viên nghiên cứu sau khi đã rà soát nguồn, giấy phép và tài nguyên |

Không mặc nhiên coi tài liệu lấy từ web là hợp lệ cho huấn luyện hay phân phối thương mại. Không sử dụng dữ liệu của SIX/CQG/ARN, email cá nhân, tài khoản liên kết hoặc repo khác làm nguồn P01 nếu chưa có quyết định cho phép theo từng nguồn.

## 2. Bộ trường hợp F0 được tiền đăng ký (không phải dữ liệu huấn luyện)

| Mã | Đầu vào minh họa | Mục đích |
|---|---|---|
| U00 | Chuỗi rỗng | Dãy mã rỗng, lỗi ở ứng dụng cần token không rỗng |
| U01 | `Xin chào Việt Nam!` | Dấu tiếng Việt, khoảng trắng, dấu câu |
| U02 | `ắ` và dạng Unicode tổ hợp tương đương | Giữ nguyên chuỗi gốc, không ép chuẩn hóa |
| U03 | `Tôi đang học AI.` | Văn bản Việt pha từ tiếng Anh |
| U04 | `😀 你好 مرحبا` | Emoji và nhiều hệ chữ |
| U05 | Tab, xuống dòng `\r\n` và xuống dòng `\n` | Bảo toàn byte và kiểu xuống dòng |
| U06 | Byte NUL `0x00`, các byte `0x00` và `0xFF` | Hoàn nguyên byte; `0xFF` đơn lẻ không giải mã Unicode strict |
| U07 | Chuỗi dài hơn 64 byte/token | Chính sách báo lỗi độ dài khi ghép với P00; không cắt thầm |
| U08 | Mã token âm, mã 256 trong B0, giá trị không nguyên | Từ chối đầu vào không hợp lệ |
| U09 | Unicode surrogate đứng riêng | Báo lỗi mã hóa Unicode nghiêm ngặt |
| U10 | Cùng nội dung trước/sau chuẩn hóa NFC | Chống trùng để chia tập, nhưng không sửa byte nguyên bản |

**Quy tắc:** Khi triển khai, phải lưu từng mẫu cùng byte kỳ vọng và SHA-256, không phụ thuộc nội dung sinh từ mô hình; không thay bộ mẫu sau khi nhìn kết quả TEST mà không tạo phiên bản kế nhiệm và biên bản giải trình.

## 3. Danh mục nguồn và giấy phép (Source & Rights Manifest)

Trước khi nhận F1/F2 phải có danh mục trên từng nguồn:
- `source_id`, đường dẫn gốc/URL nguồn, nhà sở hữu/quyền tác giả và ngày thu thập.
- Giấy phép hoặc bằng chứng sở hữu (`license_id`), điều khoản dùng để huấn luyện, quyền tạo bản dẫn xuất và quyền phân phối thương mại nếu cần.
- Giới hạn sử dụng, vùng áp dụng, điều kiện giữ nguồn, thời gian lưu, điều kiện xóa và chính sách riêng tư.
- `raw_sha256`, kích thước byte, số lượng tài liệu/nhóm, kiểu mã hóa; tách bản gốc bất biến và bản xử lý.
- `pii_review_status`, `rights_review_status`, `source_admission_status` và người/quy trình quyết định.
- Bất kỳ nguồn `UNKNOWN`, `DENIED`, thiếu hồ sơ hoặc chứa dữ liệu nhạy cảm chưa xử lý đều `REJECT`; không chuyển thành TRAIN.

Dữ liệu nằm dưới `D:\WORK\RESEARCH\TokenToModel-Lab\datasets\` sau khi được duyệt; không ghi vào GitHub, không dùng cache nằm ngoài workplace và không đụng dự án khác.

## 4. Tiền xử lý (Preprocessing), bản gốc và bảo toàn

- Giữ nguyên byte gốc, có mã băm SHA-256. Nếu cần chuyển mã ký tự, tách thành bản dẫn xuất và ghi quy tắc cùng mã băm; không thay thế bản gốc.
- Hợp đồng hoàn nguyên byte B0/B1 **không áp dụng chuẩn hóa văn bản**. Chỉ sử dụng khóa chuẩn hóa riêng cho kiểm tra trùng (Deduplication).
- Đề xuất khóa chống trùng: Unicode NFC, chuẩn hóa dòng, xóa khoảng trắng ở mép và `casefold()` để tạo *khóa nhóm*, **không** dùng khóa đó làm nội dung mã hóa cho mô hình. Cần kiểm duyệt tác động trước khi khóa.
- Phát hiện gần trùng (Near-duplicate Detection) phải có định nghĩa tỷ lệ, cách lấy mẫu và xử lý các cặp có độ dài rất ngắn. Chưa định trước ngưỡng Jaccard vì không có corpus; cổng tiền đăng ký khoa học phải khóa ngưỡng và phương pháp **trước** khi chạy.
- Không đưa nội dung tài liệu nhận diện cá nhân lên log; log chỉ ghi mã băm và tổng hợp đã khử định danh.

## 5. Chia tập (Train/Validation/Test Split) và rò rỉ

**Đề xuất** tỷ lệ chia theo *nhóm tài liệu*, không theo dòng: `80% TRAIN / 10% VALIDATION / 10% TEST`. Đây là tỷ lệ ứng viên cần thẩm định khi có số lượng nhóm, không phải một split đã được thực hiện.

- Gán `group_id` trước chia tập để mọi tài liệu trùng/đạo xuất cùng nhóm ở cùng một tập; chia theo nhóm không để đoạn văn của cùng tài liệu ở các tập khác nhau.
- Phép phân nhóm và phép chia phải quyết định (Deterministic), ghi `split_policy_version`, `split_seed` hoặc muối băm, nhóm nguồn và mã nguồn.
- Với tập quá nhỏ, không ép tỷ lệ để tạo tập VALIDATION/TEST rỗng rồi tuyên bố thành công. Phải báo `INSUFFICIENT_GROUPS` và chờ quyết định dữ liệu riêng.
- Bộ từ vựng và các quy tắc BPE chỉ được học bằng tài liệu trong TRAIN. VALIDATION dùng để quan sát khi kiểm tra quy tắc đã khóa; TEST giữ riêng để đánh giá cuối, không dùng để chọn cỡ vocab, phá hòa, chuẩn hóa hoặc ngưỡng.
- Sau khi chia, đo số nhóm giao nhau giữa TRAIN/VALIDATION, TRAIN/TEST, VALIDATION/TEST; **ngưỡng bắt buộc là 0**.
- Kiểm tra trùng SHA-256 nội dung gốc và khóa nội dung chuẩn hóa giữa các tập; giao cắt phải bằng 0. Những cặp gần trùng chưa giải quyết phải được báo `REVIEW_REQUIRED`, không suy ra không rò rỉ chỉ vì SHA khác nhau.
- Nếu cần thay tỷ lệ, thuật toán hoặc seed chia sau khi nhìn số liệu, phải tạo đề xuất kế nhiệm; không chỉnh sửa tiền đăng ký gốc.

## 6. Giới hạn tài nguyên, quyền tải và thời điểm khóa

Trước F1/F2, tiền kiểm Windows phải ghi RAM khả dụng, đĩa D: khả dụng, chi phí bản dữ liệu gốc + trung gian + chỉ mục + bằng chứng, độ lớn corpus ước tính, dung lượng băm và mô hình BPE ứng viên. **Không tự đưa ra quota dựa trên RAM lắp đặt; phải kiểm tra dung lượng thật tại thời điểm thực thi.**

Các trường `max_source_bytes`, `max_disk_bytes`, `max_ram_peak_bytes`, `max_document_count`, `max_tokenizer_train_seconds` hiện `NOT_LOCKED`; vì thế chưa được phép nhận corpus hoặc bắt đầu huấn luyện BPE.

Không dùng việc có sẵn đường dẫn hoặc token truy cập làm lý do thu thập dữ liệu. Quyền tải phải được xác nhận riêng từng nguồn cùng giới hạn.

## 7. Kết luận

`P01_DATA_SOURCE=NOT_SELECTED`; `P01_RIGHTS_REVIEW=PENDING`; `P01_SPLIT=DESIGN_ONLY`; `P01_DATA_DOWNLOAD=FORBIDDEN`; `P01_TEST_SEAL=NOT_CREATED`; `P01_SCIENCE=NOT_EXECUTED`.

Xem `P01_METRICS_AND_QA_GATES.md` để biết các tiêu chí bắt buộc trước khi một tập dữ liệu được chấp thuận.
