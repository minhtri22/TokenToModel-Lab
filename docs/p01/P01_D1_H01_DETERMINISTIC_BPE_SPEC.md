# P01 D1 — H01: Đặc tả thuật toán ghép cặp byte có thể tái lập (Deterministic Byte Pair Encoding)

**Phiên bản đề xuất:** `TTM_BPE_D1_V1_DESIGN`  
**Trạng thái:** `SPEC_COMPLETE_FOR_REVIEW_NOT_IMPLEMENTED`. Không có chương trình BPE được thực thi hoặc huấn luyện.

## 1. Mục tiêu và ranh giới

Đặc tả một thuật toán BPE thuần byte cho ứng viên B1, giúp hai tiến trình độc lập tạo cùng bảng ghép khi dùng **cùng dữ liệu TRAIN được đóng băng**. Đường đối chứng B0 là ánh xạ byte `0..255` và hoàn nguyên chính xác.

- Không lấy quy tắc ghép từ VALIDATION, TEST hoặc nguồn không được cấp quyền.
- Không tự sửa `vocab_size=256` của P00. Các mã B1 từ 256 trở đi **không tương thích trực tiếp** với lớp nhúng (Embedding) hiện tại.
- Mỗi tài liệu là một chuỗi riêng: không có ghép cặp xuyên ranh giới tài liệu.
- Không chuẩn hóa Unicode, thay lỗi, cắt văn bản hoặc đưa tiền tố đặc biệt vào chuỗi byte được mã hóa. Muốn so khớp dữ liệu gần trùng phải dùng **khóa phụ**, không sửa byte gốc.
- Chưa cấp ID cho `BOS/EOS/PAD/UNK`; phải có hợp đồng riêng nếu bổ sung về sau.

## 2. Bảng mã và quy tắc lặp

1. Biểu diễn mỗi tài liệu bằng mảng byte UTF-8 gốc, sau khi quyền dữ liệu và chia tập được phê duyệt. Với đầu vào byte tùy ý, không diễn giải UTF-8 để học bảng ghép.
2. Tập từ vựng khởi tạo gồm **256 token**: token `i` giải mã ra đúng byte `i`, với `0 <= i <= 255`.
3. Ở một vòng lặp, đếm **mọi cặp vị trí kề nhau** `(left_id, right_id)` trong từng tài liệu TRAIN, kể cả các cặp ứng viên chồng lấn khi đang đếm. Mỗi lần xuất hiện đóng góp 1; không trọng số theo tài liệu, không ghép qua biên giới tài liệu.
4. Chọn cặp có tần suất cao nhất; nếu bằng nhau, chọn cặp có bộ số nguyên `(left_id,right_id)` **nhỏ nhất theo thứ tự từ điển**. Không dựa vào thứ tự tệp, ngôn ngữ máy hay thứ tự lặp bảng băm.
5. Nếu số lần xuất hiện của cặp được chọn **nhỏ hơn 2**, dừng. Nếu không, cấp mã mới `256 + merge_index`, với `merge_index` bắt đầu từ 0. Nội dung byte của token mới là nối nội dung byte của hai token con.
6. Áp dụng cặp đã chọn trong **tất cả** tài liệu, từ trái sang phải, không chồng lấn (leftmost non-overlapping). Ví dụ trên chuỗi ba token `A A A`, ghép `(A,A)` thành `AA, A`, không ghép hai lần trên cùng token `A`.
7. Đếm lại từ đầu và lặp tới khi đạt `target_vocab_size` hoặc không còn cặp có tần suất ít nhất 2.
8. Quy tắc dừng sớm hợp lệ: `actual_vocab_size <= target_vocab_size`; ghi số quy tắc thực tế; **không** tạo token giả chỉ để đạt kích thước mục tiêu.

**Ứng viên chính cho kiểm định sau này:** `target_vocab_size = 2048` (đề xuất D1, chưa được cấp khóa khoa học). Biến thể `4096` cần tiền đăng ký và ngân sách/đối chứng riêng; không tự nâng khi kết quả 2048 chưa thuận lợi.

## 3. Mã hóa dữ liệu mới và hoàn nguyên

- Mã hóa B1: chuyển đầu vào thành token byte 0–255; **áp dụng từng quy tắc theo đúng thứ tự được huấn luyện**, mỗi lần quét trái sang phải, không chồng lấn. Bỏ qua quy tắc không xuất hiện. Không học thêm quy tắc trong quá trình suy luận.
- Giải mã B1: mỗi ID hợp lệ có chuỗi byte không rỗng, nối các chuỗi byte tương ứng theo thứ tự. Từ chối ID âm, kiểu không phải số nguyên, ID ngoài `0..actual_vocab_size-1`.
- Với giao diện chuỗi ký tự, chỉ nhận Unicode hợp lệ; mã hóa theo UTF-8 nghiêm ngặt (strict) và giải mã UTF-8 nghiêm ngặt. Với giao diện byte, phải hoàn nguyên cả chuỗi byte không hợp lệ về mặt UTF-8 mà không biến đổi.
- Nếu gặp chuỗi mới, 256 token byte cơ sở bảo đảm không cần `UNK` (Unknown Token). Không phát `UNK` như biện pháp khắc phục lỗi.
- Chuỗi rỗng mã hóa thành dãy rỗng; xử lý ngữ cảnh rỗng của mô hình là hợp đồng khác.
- Không dùng B1 vào P00 với `vocab_size=256`, kể cả khi một số mẫu B1 tình cờ có ID dưới 256.

## 4. Định dạng chuẩn để tái lập và đối chiếu SHA-256

Tạo tệp nhị phân `merges.ttmbpe` theo thứ tự byte xác định, **chưa tạo tệp này trong bước thiết kế**:

1. Đầu tệp gồm đúng 11 byte ASCII `TTM_BPE_V1\0` (10 ký tự in và một NUL; phải kiểm tra lại số byte bằng kiểm định âm tính trước I0).
2. Số nguyên không dấu 32 bit, thứ tự byte thấp trước (Little-endian): `target_vocab_size`, `actual_vocab_size`, `merge_count`.
3. Theo thứ tự vòng lặp, mỗi quy tắc gồm ba số nguyên không dấu 32 bit: `left_id`, `right_id`, `new_id`; `new_id = 256 + rank`.
4. Không dấu thời gian, đường dẫn máy, mã định danh chạy hoặc metadata biến thiên trong luồng byte `merges.ttmbpe`. Những thuộc tính đó lưu trong biên bản JSON riêng, kèm SHA-256 của TRAIN, cấu hình, phiên bản mã và của tệp nhị phân.
5. `actual_vocab_size = 256 + merge_count`; mỗi token có thể tái dựng byte bằng quy tắc trước, không phải lưu một bảng byte độc lập có thể không nhất quán.
6. SHA-256 phải được tính trên **byte đúng của tệp nhị phân**, không tính trên biểu diễn JSON có thứ tự khóa không xác định.

**Lưu ý biên tập kỹ thuật:** chuỗi `TTM_BPE_V1\0` gồm 10 ký tự ASCII in (`TTM`=3, `_`=1, `BPE`=3, `_`=1, `V1`=2) và 1 NUL, tổng cộng **11 byte**. Kiểm định parser phải từ chối magic khác hoặc độ dài bản ghi sai.

## 5. Bằng chứng bắt buộc trước khi khóa D1

- Sơ đồ giả mã (Pseudocode) độc lập cho đếm cặp, phá hòa, ghép không chồng lấn, đọc và ghi tệp.
- Bộ ví dụ âm tính về hòa tần suất, cặp chồng lấn, tài liệu rỗng, byte `00` và `FF`, biên giới tài liệu.
- Bản kê SHA-256 của snapshot TRAIN, thứ tự tài liệu, `target_vocab_size`, cấu hình và phiên bản môi trường; hai tiến trình sạch phải tạo cùng byte kết quả.
- Dữ liệu đầu vào BPE chỉ đến từ nguồn được duyệt trong `P01_D1_H02_H05_SOURCE_RESOURCE_GATE.md`.
- Có giới hạn số vòng và ngân sách thời gian/RAM; khi vượt giới hạn phải dừng có biên bản, **không** đổi số vòng hoặc nguồn ngay trong lượt chạy.

**Kết luận H01 ở mức thiết kế:** `H01_ALGORITHM_SPEC_DEFINED`; `H01_IMPLEMENTATION=NOT_STARTED`; `H01_INDEPENDENT_DYNAMIC_QA=NOT_PERFORMED`; `H01_D1_LOCK=PENDING`.

## 6. Nguồn tham khảo phương pháp

- Mô tả BPE trong *Tokenization as Finite-State Transduction*: https://doi.org/10.1162/COLI.a.23
- Unicode Normalization Forms (UAX #15): https://www.unicode.org/reports/tr15/

Các quy tắc phá hòa, định dạng nhị phân và giới hạn tài nguyên trong tài liệu này **là lựa chọn thiết kế của TTM**, không phải khẳng định tất cả bộ tách token BPE đều dùng chúng.
