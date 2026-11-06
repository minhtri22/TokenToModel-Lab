# P01 D1 — H03: Phát hiện trùng/gần trùng và chia tập không rò rỉ

**Phiên bản đề xuất:** `TTM_P01_DEDUP_SPLIT_D1_V1_DESIGN`  
**Trạng thái:** `SPEC_COMPLETE_FOR_REVIEW_NO_CORPUS` — chưa chạy trên dữ liệu thực, chưa khóa về khoa học.

## 1. Mục đích và phạm vi bằng chứng

Mục tiêu là tránh đưa hai bản gần như cùng một nội dung vào hai tập khác nhau, làm kết quả kiểm định quá lạc quan. Không dùng dữ liệu TEST để điều chỉnh ngưỡng hoặc lựa chọn mô hình.

**Lưu ý khoa học:** không có một phép dò gần trùng nào chứng minh được “không còn mọi rò rỉ ngữ nghĩa”; một bản viết lại bằng từ khác có thể thoát khỏi ngưỡng n-gram. Tiêu chí `0` chỉ có nghĩa **không còn giao cắt theo quy tắc dò đã được tiền đăng ký**, không phải bảo đảm tuyệt đối.

## 2. Bảo toàn bản gốc và khóa tìm trùng

- Bản gốc được lưu byte-for-byte với `raw_sha256`, quyền sử dụng và nguồn. Không biến đổi bản này khi mã hóa B0/B1.
- Khóa đối chiếu văn bản (Comparison Key) được tạo **riêng**, chỉ cho tài liệu UTF-8 hợp lệ: giải mã nghiêm ngặt → chuẩn hóa Unicode NFC → đổi CRLF và CR thành LF → Unicode `casefold()` → mọi chuỗi ký tự khoảng trắng Unicode thành đúng một dấu cách ASCII → xóa khoảng trắng hai đầu.
- Khóa trên là **đề xuất dùng để gom nhóm**, không được đưa vào mã hóa token hay thay byte nguồn. Phiên bản Unicode và `casefold` của môi trường phải được pin ở I0, không mặc định giống nhau giữa Python khác phiên bản.
- Tài liệu gốc không đọc được UTF-8, tài liệu rỗng sau xử lý, không có giấy phép hoặc chưa rà soát dữ liệu cá nhân (PII) bị `QUARANTINE_OR_REJECT`, không được tự chuyển vào TRAIN.
- Tạo `canonical_sha256 = SHA256(UTF8(comparison_key))`. Bản gốc giống hệt hoặc khóa giống hệt được đánh dấu `EXACT_OR_CANONICAL_DUPLICATE`.

## 3. Phép đo gần trùng (Near-duplicate Metric) đã đề xuất

**Chiều dài** là số mã điểm Unicode (Unicode Code Points) của khóa sau chuẩn hóa, **không** phải số byte và không phải số token BPE.

- Nếu một trong hai khóa có độ dài **dưới 8**: chỉ xem trùng khi chuỗi khóa **bằng chính xác**; không dùng xấp xỉ do tỷ lệ dương tính giả cao.
- Nếu hai khóa đều dài ít nhất 8 và **ít nhất một khóa ngắn hơn 40**: tính khoảng cách chỉnh sửa Levenshtein (đơn vị mã điểm Unicode). Đánh dấu gần trùng nếu cả `min(lengthA,lengthB)/max(lengthA,lengthB) >= 0.8` và `1 - edit_distance/max(lengthA,lengthB) >= 0.9`. So bằng số nguyên để không phụ thuộc sai số dấu phẩy động.
- Nếu cả hai khóa dài **từ 40 trở lên**: lập tập các n-gram gồm **5 mã điểm Unicode liên tiếp** (character 5-grams). Gọi `A,B` là hai tập; Jaccard `J = |A ∩ B| / |A ∪ B|`. Đánh dấu gần trùng nếu `J >= 0.85` **và** tỷ lệ chiều dài ngắn/dài `>= 0.8`.
- Các ngưỡng `8`, `40`, `5`, `0.80`, `0.90`, `0.85` là **giá trị thiết kế đề xuất trước khi nhìn dữ liệu**, không phải ngưỡng tối ưu thực nghiệm. Cần thẩm định âm tính trên fixture và chấp thuận D1 trước thực thi.

So sánh ngưỡng bằng phép nhân số nguyên, ví dụ `20*intersection >= 17*union` cho Jaccard 0.85, và `5*shorter >= 4*longer` cho tỷ lệ 0.8. Tập n-gram phải được tạo từ mã điểm Unicode đã chuẩn hóa, không từ byte UTF-8.

### Khác biệt giữa trùng và gần trùng

- Hai tài liệu có `raw_sha256` khác nhau vẫn có thể trùng sau NFC/casefold.
- Hai tài liệu có cả `raw_sha256` và `canonical_sha256` khác nhau vẫn có thể gần trùng theo Levenshtein/Jaccard.
- Hai tài liệu có nội dung tương đương về ý nhưng sửa câu sâu có thể không đạt ngưỡng; báo cáo phải ghi **độ bao phủ của quy tắc**, không phát biểu “không có rò rỉ ngữ nghĩa”.

## 4. Thuật toán nhóm trùng và thứ tự quyết định

1. Chỉ xét các tài liệu đủ quyền sử dụng và không có trạng thái PII chưa xử lý. Danh sách đầu vào được cố định theo `document_id` duy nhất và `raw_sha256`; từ chối ID trùng nhưng byte khác.
2. Tạo cạnh vô hướng khi hai bản ghi trùng raw byte, trùng comparison key, hoặc đạt phép dò gần trùng ở mục 3. **Không** chọn danh sách ứng viên xác suất ở phiên bản V1; thực hiện đối chiếu từng cặp trong corpus nhỏ đã giới hạn.
3. Nhóm là **thành phần liên thông (Connected Component)** của đồ thị, tính bằng phép hợp tập (Union-find). Nếu `A≈B`, `B≈C`, dù `A` không gần `C`, cả ba vẫn cùng nhóm; không được chia thành các tập khác nhau.
4. Nhãn `group_id` được tạo từ `SHA256(ASCII("TTM-P01-GROUP-V1\0") || MIN_RAW_SHA256_BYTES_IN_COMPONENT)`. Chọn mã băm raw nhỏ nhất theo thứ tự byte, không phụ thuộc thứ tự tải hoặc sắp xếp các tài liệu.
5. Nếu có cặp chưa quyết định hoặc lỗi tính toán, ghi `REVIEW_REQUIRED` / `INCONCLUSIVE`, **không** tự tách nhóm để đủ số lượng tập.

**Giới hạn độ phức tạp:** tối đa 2.000 tài liệu đủ điều kiện trong một lượt V1, tối đa 64 MiB byte nguồn và tối đa `2,000*1,999/2 = 1,999,000` cặp. Nếu thời gian/RAM vượt ngân sách, phải dừng có biên bản, không đổi sang lấy mẫu xác suất hoặc ngưỡng mới trong cùng lượt. Đây là giới hạn đề xuất, vẫn cần xác minh tài nguyên máy thực tế trước khi cấp quyền.

## 5. Chia tập theo nhóm (Group Split)

**Đề xuất tiền đăng ký**: `split_seed = 20261105`, `TRAIN=80%`, `VALIDATION=10%`, `TEST=10%`, tính theo **số nhóm**, không theo số dòng tài liệu và không theo số byte.

- Cần tối thiểu **30 nhóm độc lập**. Nếu ít hơn, ghi `INSUFFICIENT_GROUPS` và không tạo tập thử chính thức; không tự tăng tỷ lệ hoặc chia một nhóm thành nhiều mảnh.
- Tính thứ tự của từng nhóm bằng `SHA256(ASCII("TTM-P01-SPLIT-V1\0") || U64LE(split_seed) || RAW32(group_id))`, rồi sắp tăng theo 32 byte băm; nếu hòa (xác suất cực nhỏ) sắp `group_id` tăng. Không phụ thuộc thứ tự tệp trên đĩa.
- Với N nhóm, `n_val = floor(N/10)`, `n_test = floor(N/10)`, `n_train = N - n_val - n_test`. Nhóm đầu trong thứ tự là VALIDATION, tiếp theo là TEST, còn lại là TRAIN.
- Toàn bộ tài liệu của cùng `group_id` phải cùng một tập. Báo cáo thêm số tài liệu, số byte và tỷ lệ nguồn/ngôn ngữ từng tập vì chia nhóm không đảm bảo phân tầng (Stratification).
- Sau chia, tính giao cắt cặp đôi của `group_id`, `raw_sha256`, `canonical_sha256` giữa TRAIN/VALIDATION/TEST. **Điều kiện bắt buộc: mỗi giao cắt bằng 0.** Bất kỳ cặp gần trùng bị phát hiện xuyên tập cũng là FAIL.
- Bộ tách token BPE **chỉ học từ TRAIN**; tập VALIDATION có thể phục vụ so sánh cấu hình đã đăng ký, nhưng **TEST không được xem để đổi ngưỡng, cỡ vocab, luật phá hòa hoặc bộ tiền xử lý**.

## 6. Các phép thử từ chối phải có trước I0

- Cặp NFC/NFD giống nghĩa nhưng khác raw byte → cùng nhóm; byte gốc không thay đổi.
- Khác chữ hoa/thường và kiểu xuống dòng → khóa tương đương, kiểm tra không làm sai byte.
- Chuỗi chỉ 1–7 mã điểm khác 1 ký tự → **không** tự gộp gần trùng.
- Hai văn bản dài thay một số ký tự → đo Jaccard; kiểm tra ranh giới chính xác `0.85` và `0.8`.
- Chuỗi ba bản A gần B, B gần C, A không gần C → vẫn thuộc một nhóm liên thông.
- Thứ tự tệp đảo ngược → cùng nhóm, cùng split, cùng SHA định dạng chuẩn.
- Mọi trường hợp chưa phân xử, dưới 30 nhóm, dữ liệu không có quyền → từ chối cấp TEST.
- Đầu vào quá 2.000 tài liệu, quá 64 MiB hoặc vượt thời gian → dừng có biên bản, không tự lấy mẫu thay thuật toán.

## 7. Kết luận

`H03_DEDUP_GROUPING_SPEC_DEFINED`; `H03_SPLIT_SEED_PROPOSED=20261105`; `H03_THRESHOLDS_PROPOSED_NOT_CALIBRATED`; `H03_CORPUS_EXECUTION=NOT_PERFORMED`; `H03_D1_LOCK=PENDING`.

Các thông số phải được duyệt khi chưa nhìn TRAIN/VALIDATION/TEST thực tế, nếu không sẽ phải mở một nhánh tiền đăng ký kế nhiệm và giải thích.
