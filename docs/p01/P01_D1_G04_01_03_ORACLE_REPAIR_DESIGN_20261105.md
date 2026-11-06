# P01 D1 — Sửa hợp đồng oracle G04-01..03 (chỉ thiết kế)

**Phiên bản:** `TTM_P01_H04_ORACLE_REPAIR_V1_DESIGN`. **Nguồn:** HEAD `f682c91002e796f4829c38c14fb866adb227513d` của PR #4.  
**Phạm vi:** bổ sung ví dụ phản chứng và quy tắc đánh giá; không sửa byte fixture F00–F11, H01/H03, mã nguồn, cấu hình hoặc biên bản lịch sử. **Không chạy chương trình tokenizer/checker.**

## G04-01 — Ma trận API × đầu vào × giai đoạn từ chối

| Trường hợp | API và đầu vào | Oracle hợp lệ / lỗi | Điểm từ chối bắt buộc |
|---|---|---|---|
| A01 | `encode_bytes(bytes([0,255]))` | ID `[0,255]` (B0) | Trước khi mã hóa nếu sai kiểu |
| A02 | `decode_bytes([0,255])` | Byte `00ff` | Trước khi đọc bảng nếu có ID không hợp lệ |
| A03 | `decode_bytes` cho F07 `c328` | Hoàn nguyên nguyên byte `c328`, **không** lỗi UTF-8 | Không gọi bộ giải mã UTF-8 |
| A04 | `decode_text([195,40])` (B0) | Lỗi `INVALID_UTF8` | Sau ghép byte, trước khi trả chuỗi |
| A05 | `encode_text` chuỗi chứa surrogate `U+D800` | Lỗi `INVALID_UNICODE_INPUT` | Ở bước UTF-8 strict, không thay thành ký tự U+FFFD |
| A06 | `decode_bytes([-1])`, `decode_bytes([256])` (B0) | `INVALID_TOKEN_ID_RANGE` | Trước truy cập bảng byte |
| A07 | `decode_bytes([True])`, `[1.0]`, `["1"]`, `[[1]]` | `INVALID_TOKEN_ID_TYPE` | Trước ép kiểu; `bool` phải bị loại dù là lớp con của `int` trong Python |
| A08 | `encode_bytes("abc")`, `encode_text(b"abc")` | `INVALID_INPUT_TYPE` | Không chuyển kiểu ngầm |
| A09 | Đầu vào rỗng đúng kiểu | Danh sách token rỗng / byte hoặc chuỗi rỗng | Không cưỡng ép EOS/BOS |
| A10 | B1 phát ID `256` và muốn dùng P00 | `TOKENIZER_MODEL_VOCAB_MISMATCH` | **Trước mọi lần gọi** Embedding của P00; không coi `IndexError` sau khi gọi P00 là PASS |

Các tên lỗi ở trên là **mã phân loại giao diện dự kiến**, chưa mặc nhiên là lớp ngoại lệ Python. Kiểm tra bắt buộc `error_code`, `failure_stage`, `no_implicit_conversion`, `no_state_mutation`; một ngoại lệ bất kỳ hoặc log ghi chữ “error” không đủ thành PASS. Với F06/F07/F08, `decode_text` phải từ chối, nhưng `decode_bytes` phải hoàn nguyên.

**Phân tách B0/B1:** B0 chấp nhận ID 0..255; B1 chấp nhận 0..`actual_vocab_size-1` theo bảng merges được ghim. Không được vô tình cho phép token đặc biệt ngoài hợp đồng.

## G04-02 — Oracle BPE nhiều vòng, bộ đọc merges âm tính

**M01:** Dữ liệu TRAIN chỉ có một tài liệu ASCII `abababab` (hex `6162616261626162`), `target_vocab_size >=258`, quy tắc dừng tần suất nhỏ hơn 2:

| Vòng | Cặp được chọn | Tần suất lúc chọn | ID cấp | Token dãy sau khi ghép |
|---:|---|---:|---:|---|
| 0 | `(97,98)` | 4 (cặp `ba` có tần suất 3) | 256 | `[256,256,256,256]` |
| 1 | `(256,256)` | 3 | 257 | `[257,257]` |
| 2 | Không có cặp với tần suất >=2 | 1 | Không cấp | Dừng với `actual_vocab_size=258`, `merge_count=2` |

**M02:** Một tài liệu `aaaaaa` (hex `616161616161`): vòng 0 đếm cặp `(97,97)` xuất hiện **5 vị trí**, ghép trái sang phải thành `[256,256,256]`. Vòng 1 đếm `(256,256)` **2 vị trí**, ghép thành `[257,256]`. Dừng vì tần suất còn lại 1. Được dùng làm oracle riêng cho lỗi đếm cặp chồng lấn khác với áp dụng ghép không chồng lấn.

**M03:** Dữ liệu gồm hai tài liệu `a` và `b` riêng biệt: `merge_count=0`; tuyệt đối không phát sinh cặp `(97,98)` xuyên ranh giới.

**M04:** Dữ liệu TIE01 (`abab`, `baba`): vòng đầu cặp `(97,98)` và `(98,97)` đều có tần suất 3; chọn `(97,98)` theo bộ ID số nguyên nhỏ nhất. Sau ghép, các cặp còn lại có tần suất 1; dừng.

**Định dạng merges:** header phải có đúng 11 byte hex `54 54 4d 5f 42 50 45 5f 56 31 00` (ASCII `TTM_BPE_V1` rồi NUL), tiếp theo 3 số `uint32 little-endian`: target, actual, count, rồi đúng `count` bộ ba `uint32`: left, right, new. `actual=256+count`, `new=256+rank`, hai ID con của mỗi quy tắc đều phải nhỏ hơn ID mới, giá trị mục tiêu không nhỏ hơn 256. Kích thước byte toàn tệp phải **chính xác `23+12*count`**; không cho phép byte thừa.

**Ma trận parser từ chối:** sai magic (kể cả NUL), thiếu một byte, thêm một byte, count/actual mâu thuẫn, count vượt target, ID âm kiểu sai khi đưa qua API, con trỏ tương lai, cấp ID mới không liên tục, lặp đúng cùng một cặp merges, sai thứ tự little-endian và phần tệp vượt giới hạn kích thước. Một parser trả `PARTIAL_SUCCESS` cho tệp bị cắt cụt là FAIL. Các ví dụ M01–M04 là **oracle từ suy luận thiết kế**, chưa được xác nhận bằng chạy BPE trên Windows.

## G04-03 — Oracle phát hiện trùng/gần trùng độc lập

- **K01 — Khóa chuẩn hóa:** F02 `e1baaf` và F03 `61cc86cc81` có raw bytes khác nhưng khóa NFC trùng; vẫn giữ hai byte nguồn riêng.
- **K02 — Chuỗi ngắn:** `abcdefg` và `abcxefg` (7 mã điểm) không được tự đánh dấu gần trùng; chỉ có trùng chính xác mới gộp dưới 8.
- **K03 — Levenshtein:** `abcdefghij` vs `abcxefghij` dài 10, distance=1, similarity=0,9 => gần trùng nếu tỷ lệ dài 1. Trường hợp thay tiếp ký tự (`abcxyfghij`) distance=2, similarity=0,8 => không gần trùng.
- **K04 — Jaccard số học độc lập:** cố định `|A|=18, |B|=19`; nếu `|A∩B|=17` thì union=20 và `J=17/20=0,85` đúng ngưỡng. Nếu giao bằng 16 thì union=21, `J=16/21 <0,85`; nếu giao bằng 18 thì union=19, `J=18/19 >0,85`. Ba phép tính phải dùng **đúng mẫu số tương ứng**, không tái sử dụng union=20. Đây chỉ là oracle **cho bước so tỷ lệ số nguyên**, không phải cặp văn bản tạo 5-gram đã materialize; trước I0 cần thêm cặp văn bản có n-gram chính xác để chống PASS giả ở bước trích n-gram.
- **K05 — Tỷ lệ chiều dài:** `min/max=40/50=0,8` đúng ngưỡng, `39/50` không đạt. Kiểm tra riêng điều kiện AND với Jaccard; không được chỉ thử một nhánh điều kiện.
- **K06 — Bắc cầu:** nếu A≈B và B≈C, checker phải xác nhận một thành phần liên thông cả ba ngay cả khi A !≈ C; so danh sách cạnh do checker suy ra, không tin `group_id` từ phần mềm được kiểm.
- **K07 — 29/30 nhóm:** 29 => `INSUFFICIENT_GROUPS`; 30 => cho phép chia theo nhóm nếu các cổng quyền và nguồn đạt. Kỳ vọng N=30: 3 VALIDATION, 3 TEST, 24 TRAIN. Đảo thứ tự đầu vào không thay phân nhóm và nhãn split.
- **K08 — TEST giữ kín:** mô tả mẫu giả lập có một tài liệu TEST nhưng thiếu quyền đọc trong quá trình xây merges; nếu có bất cứ thao tác đọc TEST lúc học, kết quả `LEAKAGE_FAIL`. Không dùng dữ liệu TEST thật để chuẩn bị oracle.

**Phạm vi chắc chắn:** phép so Jaccard/NFC/Levenshtein chỉ chứng minh tính nhất quán của **quy tắc phát hiện trùng đã tiền đăng ký**, không thể chứng minh không còn toàn bộ bản diễn đạt lại gần nghĩa.

## Cổng quyết định G04-01..03

`G04_01_DESIGN_REPAIR=SPECIFIED`; `G04_02_DESIGN_REPAIR=SPECIFIED_WITH_MATERIALIZATION_PENDING`; `G04_03_DESIGN_REPAIR=SPECIFIED_WITH_EXACT_NGRAM_FIXTURE_PENDING`.  
**Chưa cấp `PASS_DYNAMIC_QA` hoặc `I0_IMPLEMENTATION_PERMIT`.**
