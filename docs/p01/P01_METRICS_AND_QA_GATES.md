# P01 — Thước đo, cách hiểu và cổng kiểm định trước thực thi

**Trạng thái:** `METRIC_CONTRACT_PROPOSAL_ONLY`. Bảng này là tiêu chí **dự kiến**, không chứa kết quả đo P01. Không tự gán PASS khi chưa chạy.

## 1. Cách định nghĩa các phép đo

| Chỉ số | Đo cái gì? | Cách tính và đơn vị | Điều kiện đạt dự kiến | Ý nghĩa / điều không được suy ra |
|---|---|---|---|---|
| Hoàn nguyên byte (Byte Round-trip) | Nội dung sau mã hóa–giải mã có bằng byte gốc? | Số mẫu khớp byte / tổng mẫu hợp lệ, % | **100%** trên toàn bộ bộ mẫu đã khóa | Bảo toàn thông tin; không chứng minh mô hình ngôn ngữ giỏi |
| Hoàn nguyên Unicode (Text Round-trip) | Chuỗi văn bản có giữ nguyên từng mã Unicode? | Số chuỗi khớp chính xác / tổng chuỗi hợp lệ, % | **100%**, kể cả dạng Unicode tổ hợp | Không chấp nhận mất dấu hoặc chuẩn hóa âm thầm |
| Mã ngoài miền (Out-of-range IDs) | Có mã token không hợp lệ? | Số lần `id < 0` hoặc `id >= vocab_size` | **0** mã phát ra, đầu vào sai phải báo lỗi | Ngăn hỏng Embedding; chưa chứng minh B1 tương thích P00 |
| Token không xác định (Unknown Token) | Văn bản/byte hợp lệ có phải dùng token UNK? | Số UNK / tổng token | **0** với cơ chế quay về byte | Không đồng nghĩa BPE nén tốt hoặc học tốt |
| Tái lập bộ từ vựng (Deterministic Vocab) | Hai lượt tạo BPE trên cùng TRAIN có giống nhau? | So SHA-256 của định dạng chuẩn vocab + merges ở **2 tiến trình sạch** | **Trùng chính xác** | Tái lập kỹ thuật, không phải kết quả khoa học |
| Rò rỉ dữ liệu chia tập (Cross-split Leakage) | Cùng nhóm/nội dung xuất hiện ở nhiều tập? | Số `group_id`, raw hash và normalized hash giao nhau | **0** giao cắt cho từng loại | Điều kiện cần, không tự chứng minh không có gần trùng |
| Quyền sử dụng dữ liệu (Rights Admission) | Có nguồn chưa đủ quyền? | Số bản ghi nguồn thiếu giấy phép/chấp thuận | **0** nguồn không được duyệt trong TRAIN | Không thay thế đánh giá pháp lý chuyên môn |
| Dữ liệu cá nhân (PII Admission) | Có nguồn nhạy cảm chưa xử lý? | Số tài liệu chưa qua rà soát PII nhưng được nhận vào TRAIN | **0** | Giảm rủi ro riêng tư; chưa phải kiểm định an toàn sản phẩm |
| Tỷ lệ token trên byte (Tokens per Byte) | Mã hóa tạo bao nhiêu token từ byte? | `N_token / N_byte_UTF8`, token/byte (trừ mẫu rỗng) | Báo cáo, **không khóa ngưỡng tốt hơn** khi chưa có corpus | Ít token không tự đồng nghĩa loss thấp hơn hoặc chất lượng tốt hơn |
| Hiệu quả nén (Compression Ratio) | BPE ngắn hơn đường byte bao nhiêu? | `1 - N_token_BPE/N_token_B0`, % trên cùng byte đầu vào | Báo cáo; không dùng một tập đơn lẻ làm kết luận | Phải tính chi phí lưu vocab, không phải hiệu năng GPU |
| Sức chứa ngữ cảnh P00 (Context Compatibility) | Token B0 có vượt `max_seq_len=64`? | Số token trên từng đầu vào | Nếu vượt 64 thì báo lỗi/chia đoạn theo hợp đồng riêng, **không cắt thầm** | Không sửa mô hình P00 để giấu lỗi |
| Bộ nhớ đỉnh (Peak RAM) | Quy trình tiêu thụ bao nhiêu RAM cao nhất? | Byte/GiB từ đo thực tế | Chỉ được phép chạy khi ngân sách đã khóa và môi trường đủ | Phục vụ an toàn vận hành, không chứng minh mô hình tốt |
| Dung lượng đĩa (Disk Footprint) | Dữ liệu gốc + dẫn xuất + từ vựng + bằng chứng chiếm bao nhiêu? | Byte/GiB | Không vượt mức ngân sách đã được duyệt | Bảo vệ workplace, ngăn hết đĩa |
| Lỗi âm thầm (Silent Replacement Count) | Có Unicode lỗi bị thay bằng ký tự khác mà không báo? | Số trường hợp lỗi bị che giấu | **0** | Bắt buộc chế độ strict |

Lưu ý: B0 có tỷ lệ 1 token/byte khi mã hóa byte thuần túy; không được đem một token BPE so với một ký tự Unicode như thể cùng đơn vị.

## 2. Công thức và ví dụ để hiểu phép đo

### Hoàn nguyên

`roundtrip_rate = 100 * count(decode(encode(x)) == x) / count(valid_inputs)`

Đây là phép kiểm tra **đúng tuyệt đối**: chỉ cần một chữ Việt bị đổi từ ký tự gộp sang ký tự tổ hợp nhưng không giữ chuỗi gốc, kết quả đó là FAIL trong hợp đồng không chuẩn hóa.

### Tỷ lệ token/byte

Ví dụ minh họa, **không phải kết quả đã đo**: chuỗi UTF-8 có 20 byte. B0 tạo 20 token nên tỷ lệ = 1 token/byte. Nếu BPE tạo 13 token thì tỷ lệ = 0,65 token/byte; tỷ lệ giảm `1 - 13/20 = 35%`.

Điều này chỉ cho thấy số token giảm ở ví dụ; không chứng minh quá trình huấn luyện GPT nhanh hơn 35%, độ chính xác tốt hơn 35% hay RAM giảm 35%.

### Không rò rỉ

`overlap_train_test = |group_ids_train ∩ group_ids_test|`

Phải bằng 0. Cần kiểm tra thêm cặp TRAIN/VALIDATION và VALIDATION/TEST cũng như raw hash và normalized hash. Nếu thấy nhóm gần trùng chưa được quyết định, ghi `INCONCLUSIVE_REQUIRES_REVIEW` dù số raw hash giao nhau bằng 0.

### Tái lập

Hai tiến trình riêng cùng đọc bản chụp TRAIN đã khóa và cùng cấu hình BPE, tuần tự dữ liệu, chính sách phá hòa phải tạo **cùng bytes của tệp vocab/merges đã chuẩn hóa**. Không chỉ so số token hoặc hình dạng tệp.

## 3. Bản đồ kiểm thử dự kiến

| Nhóm thử | Nội dung | Tình huống từ chối (Negative Test) |
|---|---|---|
| T01 | B0 hoàn nguyên byte | ID âm hoặc `>=256` |
| T02 | Unicode tiếng Việt NFC/NFD | Tự đổi chuẩn hóa |
| T03 | Văn bản đa ngữ và emoji | Mất byte trong chuỗi nhiều byte |
| T04 | CRLF, tab, NUL, chuỗi rỗng | Thay `\r\n` bằng `\n` |
| T05 | UTF-8 không hợp lệ | Giải mã thành ký tự thay thế |
| T06 | B1 học quy tắc ghép có thứ tự | Thay thứ tự đầu vào làm thay rules khi cấu hình đã khóa |
| T07 | B1 hoàn nguyên byte và byte fallback | UNK cho byte hợp lệ |
| T08 | Không trộn token có từ vựng khác P00 | Chuyển mã `>=256` vào Embedding 256 |
| T09 | Quy tắc chia tài liệu và bản sao | Nhóm trùng nằm hai tập |
| T10 | TEST không tham gia học BPE | Truy cập TEST khi xây merges |
| T11 | Kiểm soát nguồn và dữ liệu cá nhân | Nhận corpus thiếu giấy phép hoặc chưa rà PII |
| T12 | Giới hạn bộ nhớ và dung lượng | Vượt hạn mức mà vẫn tự tiếp tục |
| T13 | Định danh cấu hình + SHA-256 + log bất biến | Trùng `run_id`, sửa file đã khóa |
| T14 | Tương thích ngữ cảnh P00 | Cắt thầm chuỗi quá 64 token |

Các trường hợp trên phải được chốt với bộ kiểm thử độc lập trước khi triển khai; số mẫu/seed và giới hạn tài nguyên chưa khóa nên không được tuyên bố QA đạt.

## 4. Ngưỡng đóng các cổng

### Cổng D0 — Chấp thuận hồ sơ thiết kế

Bắt buộc: đúng baseline P00, hợp đồng API, không mâu thuẫn miền token, kế hoạch dữ liệu/giấy phép, quy tắc chống rò rỉ, bảng đo có ý nghĩa, danh mục kiểm thử sai và trạng thái chặn thực thi. Rà soát độc lập tài liệu đạt thì chỉ được `DESIGN_ACCEPTED`, **không** cấp quyền chạy.

### Cổng D1 — Khóa tiền đăng ký thực nghiệm

Chỉ được xét sau khi xác định corpus hợp pháp, số nhóm, nguyên tắc phân chia, số mẫu F0, cỡ vocab B1, tie-breaker, ngưỡng gần trùng, seed, ngân sách RAM/đĩa, mã nguồn, định dạng artefact, QA độc lập và tập TEST nguyên vẹn. Không được điều chỉnh ngưỡng khoa học sau khi nhìn TEST.

### Cổng I0 — Quyết định triển khai

Cần Git sạch, đúng SHA HEAD và `origin`, vị trí worktree được phê duyệt bên trong workplace, nguồn dữ liệu hợp lệ, tiền kiểm tài nguyên và cho phép thao tác cụ thể. Chỉ tại đây mới cân nhắc tạo worktree P01.

### Cổng E0 — Cho phép đo/huấn luyện BPE

Chỉ sau `I0`, kiểm thử tĩnh/âm tính đạt và quyết định một lượt chạy độc lập. Không chạy huấn luyện GPT ở P01.

## 5. Phân loại kết quả bắt buộc

- `PASS`: đạt đầy đủ phép thử đã tiền đăng ký ở phạm vi tương ứng.
- `FAIL`: có mẫu sai hoặc vượt giới hạn; giữ log và mã băm, không đổi ngưỡng để biến FAIL thành PASS.
- `INCONCLUSIVE`: thiếu nguồn, số nhóm ít, phép đo không đồng nhất hoặc TEST không còn nguyên vẹn.
- `NOT_EXECUTED`: trường hợp hiện tại; chỉ có thiết kế, **chưa có kết quả thực nghiệm P01**.

**Trạng thái P01 hiện tại:** `DESIGN_ONLY`; `NO_QA_EXECUTION`; `NO_DATA`; `NO_MODEL_TRAINING`.
