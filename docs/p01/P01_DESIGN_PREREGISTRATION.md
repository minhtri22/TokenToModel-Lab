# P01 — Thiết kế và tiền đăng ký bộ tách token và luồng dữ liệu (Tokenizer & Data Pipeline)

**Mã hồ sơ:** `TTM_P01_DESIGN_PREREGISTRATION_20261105_V01`  
**Trạng thái:** `DESIGN_ONLY_DRAFT_PENDING_INDEPENDENT_REVIEW`  
**Nhánh chỉ chứa tài liệu:** `design/p01-tokenizer-data-prereg-20261105`  
**Mốc GitHub trước nhánh:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`  
**Phạm vi được phép ở bước này:** đọc, thiết kế, viết tiêu chí, kiểm toán tĩnh tài liệu và tiền kiểm Git trên Windows.  
**Phạm vi bị cấm:** tải dữ liệu, huấn luyện bộ tách token hoặc mô hình, chạy thực nghiệm, tạo cây làm việc (Git Worktree) P01, xóa dữ liệu hoặc dọn cây làm việc P00.

## 1. Câu hỏi kỹ thuật được tiền đăng ký

Làm thế nào chuyển văn bản tiếng Việt và văn bản đa ngôn ngữ thành mã token theo một hợp đồng **không làm mất thông tin, tái lập được và không rò rỉ dữ liệu kiểm định** trước khi xây vòng huấn luyện GPT?

P01 có hai đường so sánh được đề xuất:
- **B0 — Đường đối chứng byte:** mỗi byte UTF-8 ứng với một mã từ 0 tới 255. Không cần dữ liệu để học bộ từ vựng. Đây là đường tương thích trực tiếp với mô hình P00.
- **B1 — Ứng viên ghép cặp byte (Byte Pair Encoding — BPE):** xuất phát từ 256 token byte, học quy tắc ghép trên **tập huấn luyện đã được cho phép**, dùng cơ chế quay về byte (Byte Fallback) cho chuỗi mới. B1 là ứng viên nghiên cứu riêng, **không thay thế hay sửa P00 trong bước này**.

Không kết luận BPE tốt hơn theo chất lượng mô hình, tốc độ hay thương mại hóa trước khi có corpus, mẫu đối chứng và phép đo thực tế.

## 2. Nguồn gốc P00 và bất biến

Nguồn đã qua QA: `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`; mốc mã + tài liệu P00: `c66e27a5d1e68958d42c825fd40f8a273994e0a0`; commit hồ sơ gần nhất: `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.

Cấu hình P00 `configs/phase0_reference.json` có `vocab_size=256`, `max_seq_len=64`, `n_layer=2`, `n_head=4`, `n_embd=64`; trạng thái **`PROPOSED_NOT_FROZEN`**. Lớp nhúng token (Token Embedding) và đầu dự đoán đầu ra (Language Model Head) hiện đều nhận đúng 256 token.

**Quy tắc tương thích:** B0 phát mã 0–255 và có thể cấp đầu vào cho P00 khi chiều dài không vượt 64. B1 có mã ghép từ 256 trở lên, **không được** cấp trực tiếp cho P00 hiện tại; phải có bước quyết định riêng cho lớp nhúng, kích thước đầu ra, trọng số, cấu hình và QA ở giai đoạn sau. Không được im lặng đổi `vocab_size`, trọng số hoặc mã nguồn P00.

## 3. Hợp đồng đầu vào/đầu ra (Input/Output Contract)

### B0 — Byte, không học từ dữ liệu

| Giao diện dự kiến | Đầu vào | Đầu ra | Bất biến |
|---|---|---|---|
| `encode_text` | Chuỗi Unicode hợp lệ | Danh sách số nguyên `list[int]` | Lấy byte UTF-8 nghiêm ngặt (strict), mỗi byte đúng một mã 0–255 |
| `decode_text` | Danh sách mã byte | Chuỗi Unicode | Ghép byte rồi giải mã UTF-8 nghiêm ngặt; chuỗi byte UTF-8 lỗi phải báo lỗi |
| `encode_bytes` | Chuỗi byte tùy ý | `list[int]` | Mã đúng từng byte, không tự chuẩn hóa |
| `decode_bytes` | `list[int]` | Chuỗi byte | Đảo ngược chính xác, từ chối mã ngoài 0–255 |

- Văn bản rỗng được biểu diễn bằng dãy token rỗng. Việc dùng trong bước huấn luyện/suy luận cần quy tắc độ dài không rỗng riêng.
- Dấu cách, xuống dòng CRLF, tab, ký tự NUL, dấu tiếng Việt dạng tổ hợp (Combining Marks) và emoji phải được bảo toàn nguyên vẹn khi mã hóa–giải mã.
- **Không** tự chuẩn hóa Unicode (Normalization) hay dùng chế độ thay lỗi (errors='replace') trong hợp đồng hoàn nguyên B0.
- Đầu vào Unicode có mã thay thế đơn lẻ (Unpaired Surrogate) phải báo lỗi; không âm thầm thay nội dung.
- Không cấp mã token đặc biệt (Special Token) trong khoảng 0–255 vì mọi giá trị đã được sử dụng cho byte.

### B1 — BPE dự kiến, chưa triển khai

- Khởi đầu từ bảng byte 0–255. Mỗi quy tắc ghép là một cặp token và một mã token mới; phải ghi thứ tự quy tắc, phiên bản định dạng, nguồn huấn luyện, SHA-256 và cách giải mã.
- Không ghép xuyên ranh giới tài liệu. Khi tần suất bằng nhau, phải có luật phá hòa cố định (Deterministic Tie-breaker), dự kiến dùng thứ tự từ điển của biểu diễn byte rồi mã token; luật cuối cùng phải được kiểm duyệt trước thực thi.
- Kích thước từ vựng ứng viên để nghiên cứu: `2048` và `4096`, bên cạnh B0 `256`. Các kích thước này là **đề xuất thiết kế**, chưa khóa hay chứng minh tối ưu.
- Bộ tách token chỉ được học trên phần dữ liệu **TRAIN** đã qua kiểm soát; không học từ `VALIDATION` hay `TEST`.
- Token đặc biệt như `BOS/EOS/PAD` chưa được cấp mã trong P01 ở giai đoạn thiết kế. Khi được đề xuất, phải dùng vùng mã không va chạm từ vựng thực, ghi cơ chế xử lý và kiểm tra tương thích mô hình riêng.
- Tệp bộ từ vựng (Vocabulary), tập quy tắc ghép (Merge Rules) và cấu hình được băm SHA-256; bộ giải mã phải hoàn nguyên chính xác byte gốc khi dùng chuỗi token hợp lệ.

### Bản ghi dữ liệu (Dataset Record)

Một bản ghi dự kiến có: `document_id`, `source_id`, `source_sha256`, `license_id`, `rights_status`, `encoding`, `byte_count`, `content_sha256`, `group_id`, `split`, `normalization_policy`, `pii_review_status`, `tokenizer_id`, `record_schema_version`. Tệp gốc và tệp đã xử lý là hai thực thể khác nhau, mỗi tệp có SHA-256.

Không lưu nội dung có dữ liệu cá nhân hoặc văn bản không đủ quyền sử dụng lên GitHub.

## 4. Phạm vi P01, không bao gồm

**Trong P01 sau khi được cấp quyền riêng:** triển khai bộ tách token byte và ứng viên BPE, kiểm soát dữ liệu, phân tách dữ liệu, kiểm thử hoàn nguyên, xác minh tính quyết định, kiểm tra rò rỉ, đo tỷ lệ token/byte và tài nguyên.

**Ngoài P01:** thay đổi kiến trúc Attention/Transformer, huấn luyện GPT/P02–P03, thay đổi lớp Embedding hoặc đầu dự đoán P00, tối ưu GPU/PagedAttention, học trên TEST, tải bộ dữ liệu khi chưa có nguồn và giấy phép đã duyệt.

## 5. Giả thuyết, tiêu chí và nguy cơ

- **H1 — Không mất dữ liệu:** B0 và B1 khôi phục chính xác chuỗi byte gốc đối với dữ liệu thuộc miền đầu vào hợp lệ. Tiêu chí: 100% mẫu được khóa, không chấp nhận một byte thay đổi.
- **H2 — Tái lập:** với cùng tập TRAIN, cấu hình, thứ tự dữ liệu, thuật toán và quy tắc phá hòa, hai lần thực thi độc lập cho cùng mã SHA-256 của bộ từ vựng và quy tắc ghép. Không dùng nhận xét bằng mắt.
- **H3 — Không rò rỉ:** tài liệu, nhóm nội dung trùng nhau và dữ liệu kiểm thử giữ riêng không bị đưa vào lúc học BPE. Tiêu chí: 0 nhóm trùng giữa TRAIN/VALIDATION/TEST; mọi truy cập ngoài TRAIN phải bị từ chối hoặc được ghi thành FAIL.
- **H4 — Phạm vi từ vựng:** đường B0 phát mã đúng 0–255; B1 phát mã đúng từ 0 đến `vocab_size - 1`, có quay về byte, không có token không xác định (Unknown Token) trong đầu vào byte hợp lệ.
- **H5 — Chi phí:** đo token/byte và RAM đỉnh nhưng **không định trước B1 phải nhanh hơn hay tốt hơn** khi chưa có bộ dữ liệu và cấu hình máy được khóa. Chưa có mục tiêu cải thiện hiệu năng hợp lệ.

Đối với câu hỏi sử dụng B1 thay B0, quyết định phải dựa trên tính đúng, tính tái lập, tính tương thích, chi phí và phân tích dữ liệu đánh giá giữ riêng; không chọn ứng viên dựa trên TEST.

## 6. Giai đoạn và quyết định

1. `P01_D0`: thiết kế và tiền đăng ký như tài liệu này, QA tĩnh hồ sơ. **Hiện hành**.
2. `P01_D1`: thẩm định độc lập hợp đồng token/dữ liệu, danh mục nguồn dữ liệu và tài nguyên. Không tiêu thụ seed khoa học.
3. `P01_I0`: quyết định cấp quyền triển khai riêng, khóa mã nguồn đầu vào, tài nguyên, phạm vi worktree và bộ fixture.
4. `P01_QA0`: kiểm thử tĩnh và dữ liệu giả lập không phải nghiên cứu, giữ cả PASS/FAIL.
5. `P01_E0`: chỉ mở phép đo trên corpus được cấp phép bằng một quyết định thực thi riêng, sau khi tiền đăng ký khoa học được khóa.

Không hợp nhất nhánh triển khai vào `main` khi thiếu kiểm thử độc lập, biên bản SHA-256 và kết luận đối chứng. Không tiêu thụ TEST để sửa thuật toán, thay tham số hoặc quyết định BPE.

## 7. Điều kiện cấm ở thời điểm lập hồ sơ

`P01_IMPLEMENTATION_AUTHORIZED=false`, `P01_DATA_DOWNLOAD_AUTHORIZED=false`, `P01_TOKENIZER_TRAINING_AUTHORIZED=false`, `P01_MODEL_TRAINING_AUTHORIZED=false`, `P01_WORKTREE_CREATION_AUTHORIZED=false`, `P00_CLEANUP_AUTHORIZED=false`.

**Quyết định:** `P01_PREREG_DRAFT_DESIGN_ONLY`. Chưa có dữ liệu thật, không có phép đo P01 và không có quyết định QA khoa học. Xem chi tiết nguồn dữ liệu ở `P01_DATA_AND_SPLIT_PLAN.md`, thước đo ở `P01_METRICS_AND_QA_GATES.md`, điều kiện Windows ở `P01_WINDOWS_WORKSPACE_PREFLIGHT.md`.
