# P01 D1 — C07/G04-03: Bộ oracle 5-gram/Jaccard từ byte gốc (chỉ thiết kế)

**Phiên bản:** `TTM_P01_C07_EXACT_5GRAM_ORACLE_V1_DESIGN`.  
**Nguồn xây dựng:** chuỗi ASCII tự tạo tại môi trường tính toán tách khỏi repo P01; **không** chạy tokenizer, checker, BPE hoặc đọc corpus.  
**Quy tắc đối chứng:** H03 dùng **mã điểm Unicode** (Unicode Code Point), tập 5-gram, Jaccard ≥ `17/20=0,85` và tỉ lệ chiều dài ngắn/dài ≥ `4/5=0,8` khi cả hai khóa dài ≥40. Kiểm tra bằng **số nguyên**, không so float hoặc làm tròn trước khi ra quyết định.

## 1. Byte nguồn có thể tái dựng độc lập

| ID | Văn bản ASCII chính xác | Độ dài byte / mã điểm | SHA-256 của byte |
|---|---|---:|---|
| `A40` | `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN` | 40 | `08b14f5392d7acf18d7613f91b41ba279d5a3e0758877059b5da1da18b939817` |
| `J_OVER42` | `0bcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN78` | 42 | `75fc666b46e08e8117089c92c3218b8a69126aa0a5d4f90431d6b850ba99f2b5` |
| `J_EQUAL42` | `01cdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN78` | 42 | `1a55db11874e4790898629c8329be1ba518a9fa37c12ee78cbaa8ca69f727c4f` |
| `J_UNDER42` | `012defghijklmnopqrstuvwxyzABCDEFGHIJKLMN78` | 42 | `9dfe37f99bfe55ead8acfb58682e54e45a676cfa63c2a995b3e3c65273c11d24` |
| `LEN40` | `abcde` lặp đúng 8 lần | 40 | `7acfe8b823ea933d6a1293f4b9c42b8feaeecb67534098c51044ad2e4fa7a928` |
| `LEN50` | `abcde` lặp đúng 10 lần | 50 | `789f9a739bc07cadfcfd2746eee40746d0a72c38d401e232115d8fd466ce919c` |
| `LEN51` | `abcde` lặp đúng 10 lần, thêm `a` | 51 | `a574daa21408d742a42b74da22440ccb810cac3d0dcf51da6694bafd61a6601d` |

**Quy tắc byte nguồn:** tất cả ký tự thuộc ASCII, nên `raw_hex` xác định duy nhất bằng cách nối mã hex của từng ký tự; không có bước đổi Unicode. Để tránh việc một trình so khớp được sửa âm thầm đầu vào, checker phải tự so SHA-256 của các byte UTF-8 đọc trực tiếp với 7 giá trị trong bảng. Không lấy SHA do bộ gom nhóm tự công bố làm oracle.

## 2. Tập 5-gram gốc và sai khác hoàn chỉnh

Tập 5-gram `G(A40)` có đúng 36 chuỗi, sắp theo ASCII:

`ABCDE BCDEF CDEFG DEFGH EFGHI FGHIJ GHIJK HIJKL IJKLM JKLMN abcde bcdef cdefg defgh efghi fghij ghijk hijkl ijklm jklmn klmno lmnop mnopq nopqr opqrs pqrst qrstu rstuv stuvw tuvwx uvwxy vwxyz wxyzA xyzAB yzABC zABCD`

Đối với mỗi `B`, **toàn bộ tập 5-gram B** được xác định bằng `G(B) = (G(A40) \ LOSS) ∪ ADD`; không chỉ là thống kê số lượng:

| B | LOSS: 5-gram có trong A, không có trong B | ADD: 5-gram có trong B, không có trong A |
|---|---|---|
| `J_OVER42` | `abcde` | `0bcde`, `KLMN7`, `LMN78` |
| `J_EQUAL42` | `abcde`, `bcdef` | `01cde`, `1cdef`, `KLMN7`, `LMN78` |
| `J_UNDER42` | `abcde`, `bcdef`, `cdefg` | `012de`, `12def`, `2defg`, `KLMN7`, `LMN78` |

Ví dụ: `|G(A40)|=36`; đối với `J_EQUAL42`, `|G(B)|=36-2+4=38`, giao `=36-2=34`, hợp `=36+38-34=40`; do đó Jaccard chính xác `34/40=0,85`.

## 3. Oracle biên ngưỡng chính xác

| Cặp | `|A|` 5-gram | `|B|` 5-gram | Giao | Hợp | Jaccard (phân số chính xác) | Độ dài ngắn/dài | Kỳ vọng |
|---|---:|---:|---:|---:|---:|---:|---|
| `A40 / J_UNDER42` | 36 | 38 | 33 | 41 | `33/41≈0,804878` | `40/42` | **NOT_DUPLICATE** |
| `A40 / J_EQUAL42` | 36 | 38 | 34 | 40 | `34/40=0,850000` | `40/42` | **NEAR_DUPLICATE** |
| `A40 / J_OVER42` | 36 | 38 | 35 | 39 | `35/39≈0,897436` | `40/42` | **NEAR_DUPLICATE** |

Để chống PASS giả ở bước trích 5-gram, checker phải so **từng phần tử** của tập (G), LOSS/ADD và số đếm; so duy nhất `J>=0.85` là chưa đủ.

### Kiểm tra riêng tỉ lệ chiều dài 0,8 với Jaccard = 1

Với mọi chuỗi `LEN40`, `LEN50`, `LEN51`, tập 5-gram chính xác gồm **5** phần tử: `abcde`, `bcdea`, `cdeab`, `deabc`, `eabcd`. Mỗi cặp giữa chúng có `J=5/5=1`.

- `LEN40/LEN50`: `40/50=0,8`, đáp ứng cả hai điều kiện ⇒ **NEAR_DUPLICATE**.
- `LEN40/LEN51`: `40/51≈0,784314`, vi phạm điều kiện độ dài ⇒ **NOT_DUPLICATE**, dù Jaccard bằng 1.
- Trường hợp thực thi phải dùng **phép AND** giữa điều kiện tỉ lệ chiều dài và Jaccard. Khi ngưỡng được chạm đúng bằng, phải nhận; ngay dưới ngưỡng phải từ chối.

## 4. Oracle bắc cầu cho nhóm liên thông

Xét ba tài liệu `A40`, `J_OVER42`, `J_UNDER42`:
- `A40 ∼ J_OVER42`: `35/39≈0,897436` ⇒ **có cạnh**.
- `J_OVER42 ∼ J_UNDER42`: `35/41≈0,853659` ⇒ **có cạnh**.
- `A40 ∼ J_UNDER42`: `33/41≈0,804878` ⇒ **không có cạnh**.

Dù không tồn tại cạnh trực tiếp ở cặp thứ ba, nhóm liên thông phải chứa **đủ ba tài liệu**. `raw_sha256` nhỏ nhất theo thứ tự byte trong nhóm là của `A40`. Theo định nghĩa H03, `group_id = SHA256(ASCII("TTM-P01-GROUP-V1\\0") || bytes32(raw_sha256(A40)))`, với `\\0` ở đây biểu thị **một byte NUL**, không phải hai ký tự dấu gạch chéo và số 0. Kỳ vọng:

`81299a537c69ee8268b6ce1d021dc5ff558245820bc9293a5286d849273a432a`

Nếu checker chỉ tin `group_id` do hệ thống đang kiểm thử phát ra mà không kiểm tra cạnh và thành phần liên thông từ byte nguồn, **không được** kết luận PASS.

## 5. Phương pháp kiểm tra độc lập và trường hợp lỗi

- Tính SHA-256 trên byte gốc; so `raw_hex` tái tạo từ chuỗi ASCII với giá trị kỳ vọng và SHA đã ghim.
- Lấy 5 mã điểm Unicode liên tiếp (không phải byte 5 hoặc token BPE 5); tạo **tập** 5-gram, không phải đa tập (Multiset).
- So tập từng phần tử hoặc phép chênh LOSS/ADD; nếu một byte, một ký tự hoặc một 5-gram khác oracle thì FAIL ngay cả khi Jaccard vẫn vượt ngưỡng.
- Tính các ngưỡng bằng tích chéo số nguyên: `20*intersection >= 17*union`; `5*shorter_length >= 4*longer_length`; không chấp nhận giá trị float đã làm tròn.
- Không chia nhóm trên bản dữ liệu chưa duyệt giấy phép. Những chuỗi ở đây là **fixtures thiết kế F0**, không phải tập TRAIN/TEST thực nghiệm.
- Dấu hiệu PASS giả: bỏ điều kiện chiều dài; chuyển nhầm sang nhánh Levenshtein dù cả hai chuỗi dài ≥40; so từ đa tập thay vì tập; tính n-gram từ bytes thay vì mã điểm Unicode; quên nối nhóm theo bắc cầu.

**Kết luận phạm vi:** `C07_EXACT_5GRAM_ORACLE=SPECIFIED_AND_ARITHMETICALLY_RECOMPUTED`. Chưa có `C07_DYNAMIC_QA`, chưa có `TEST`, chưa có dữ liệu corpus và chưa cấp `I0`.
