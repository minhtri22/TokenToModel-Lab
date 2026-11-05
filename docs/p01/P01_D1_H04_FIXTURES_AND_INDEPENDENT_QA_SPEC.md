# P01 D1 — H04: Mẫu kiểm thử byte bất biến và quy trình QA độc lập

**Mã bộ mẫu:** `TTM_P01_F0_BYTES_V1_DESIGN`  
**Trạng thái:** `FIXTURE_SPEC_PINNED_IN_GIT_NOT_MATERIALIZED`. Những chuỗi dưới đây là **giá trị nguồn thiết kế tĩnh**, không phải dữ liệu huấn luyện. Chưa chạy bộ tách token.

## 1. Quy tắc tạo và đối chiếu byte gốc

- `raw_bytes` là byte thực từ chuỗi hex (chữ hoa/chữ thường không ảnh hưởng giá trị) hoặc ký hiệu lặp `41 × 64`, `41 × 65`.
- SHA-256 trong bảng được tính theo đúng byte nguồn, **không** tính theo ký tự của chuỗi hex, Markdown hay kết thúc dòng.
- Đối với API byte, kiểm tra `decode_bytes(encode_bytes(raw_bytes)) == raw_bytes` kể cả khi byte không phải UTF-8 hợp lệ.
- Đối với API văn bản, chỉ nhận chuỗi Unicode hợp lệ; `encode_text` dùng UTF-8 strict; `decode_text` từ dãy byte sai phải ném lỗi, không thay ký tự `U+FFFD`.
- Không dùng dữ liệu F0 để học từ vựng BPE rồi suy ra chỉ số thống kê về chất lượng; F0 chỉ thử tính đúng và hành vi từ chối.
- Nguồn mẫu là các chuỗi ngắn tự biên soạn trong hồ sơ này; không lấy từ corpus web, file cá nhân hay nguồn riêng tư.

## 2. Danh mục 12 mẫu byte có mã băm

| Mã | Định nghĩa byte đầu vào | Số byte | SHA-256 byte nguồn | Hợp đồng kỳ vọng |
|---|---|---:|---|---|
| F00 | rỗng | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | B0/B1 trả mảng token rỗng; giải mã byte rỗng |
| F01 | `48656c6c6f2c2031323321` | 11 | `52ce7f8d6d1f955e01b896c8fb38de421b4f9d0a2978fb1e3a3c9f3a6efa80ff` | ASCII có dấu câu, không đổi nội dung |
| F02 | `e1baaf` | 3 | `096b1b5c74b5228a3eefceac7aefcc39432b35b7d24ee4885b1dd06d1045dc77` | Chữ “ắ” ở dạng gộp sẵn |
| F03 | `61cc86cc81` | 5 | `0d840a58efa73fdc1557f97b80dabbda05d19cdeeb808319a484f6a66afd05dc` | Cùng chữ nhìn giống F02 nhưng dạng tổ hợp; **không** được đổi byte thành F02 |
| F04 | `41f09f9880` | 5 | `3c94a0388b52318853918f13698b0677f047c0f298aba9732f8f3f637f652084` | ASCII kèm emoji, hoàn nguyên UTF-8 |
| F05 | `410d0a0942` | 5 | `257631603b5242f4a3990499e6134ee263935a1d4433329bff06531313ed2e58` | Giữ nguyên CRLF và tab, không đổi thành LF |
| F06 | `007fff` | 3 | `4234f1064f32788dc9487507f9eeecd0cdf7df6bd010fd1dad8026226e222813` | Byte API hoàn nguyên; text API giải mã phải từ chối vì `FF` |
| F07 | `c328` | 2 | `eddf68639913a3cb8331cdfe7f87559e0beccf2c289c0d90ac4d89b3204004f8` | UTF-8 lỗi; byte API được phép, text API từ chối |
| F08 | `eda080` | 3 | `91a681b998555fb475479817b126c94e57e52011fa1842c5d188795a4a05226b` | Chuỗi byte mô phỏng surrogate UTF-8 không hợp lệ; text API từ chối |
| F09 | byte `41` lặp đúng **64 lần** | 64 | `d53eda7a637c99cc7fb566d96e9fa109bf15c478410a3f5eb4d4c4e26cd081f6` | B0 tạo 64 token; hợp đồng P00 có thể chấp nhận chiều dài này |
| F10 | byte `41` lặp đúng **65 lần** | 65 | `836203944f4c0280461ad73d31457c22ba19d1d99e232dc231000085899e00a2` | B0 tạo 65 token; khi đưa vào P00 max 64 phải từ chối hoặc xử lý phân đoạn riêng, **không cắt thầm** |
| F11 | `54c3b4692068e1bb8d632041492e20e4bda0e5a5bd` | 21 | `660e1acf58874284bde116a57d853dfb4057e7d8acf69d7026bcdf24e79665a3` | Chữ Việt, chữ Latin và chữ Hán; giữ nguyên byte |

**Ví dụ đối chiếu:** F02 có 3 byte còn F03 có 5 byte. Khóa dùng để **tìm bản trùng** có thể coi chúng tương đương sau NFC, nhưng bộ tách token phải giải mã về **đúng 3 hoặc 5 byte nguồn** tương ứng.

## 3. Mẫu thử âm tính không phải byte nguồn hợp lệ

| Mã | Đầu vào/điều kiện | Kỳ vọng |
|---|---|---|
| N01 | ID `-1` tại `decode_bytes` | Từ chối, không cuộn chỉ số Python |
| N02 | ID `256` tại B0 | Từ chối, không ép vào byte `00` |
| N03 | ID không phải số nguyên, bao gồm `True`, `1.5`, `"65"` | Từ chối, không ép kiểu ngầm |
| N04 | Unicode chứa mã surrogate `U+D800` đứng riêng | `encode_text` phải ném lỗi `UnicodeEncodeError` hoặc lỗi hợp đồng tương đương |
| N05 | `decode_text` trên F06/F07/F08 | Lỗi UTF-8 nghiêm ngặt, không có ký tự thay thế |
| N06 | Nhập B1 token ID `>=256` vào lớp nhúng P00 không thay | Phải chặn tại kiểm tra tương thích trước truy cập model |
| N07 | Dùng TEST để tính tần suất cặp BPE | Từ chối trước khi có truy cập đọc dữ liệu TEST |
| N08 | Chương trình vượt ngân sách RAM/thời gian hoặc nguồn chưa có quyền | Dừng có biên bản, không tự chạy lại |

## 4. Mẫu kiểm tra BPE tất định chưa thực thi

- **TIE01:** hai tài liệu byte `61626162` (abab) và `62616261` (baba). Ở vòng đầu, cặp `(97,98)` và `(98,97)` có cùng tần suất 3; bộ phá hòa phải chọn `(97,98)` và mã mới 256.
- **OVERLAP01:** một tài liệu byte `61616161` (aaaa). Cặp `(97,97)` xuất hiện ở 3 vị trí kề nhau khi đếm, nhưng khi ghép trái sang phải chỉ tạo hai token mới 256.
- **BOUNDARY01:** hai tài liệu tách biệt, thứ nhất byte `61`, thứ hai byte `62`. Không được coi `(97,98)` là cặp kề nhau xuyên ranh giới tài liệu.
- **ORDER01:** hoán vị thứ tự tài liệu TRAIN không thay các tần suất tổng hoặc thứ tự quy tắc BPE.
- **REPRO01:** hai tiến trình sạch cùng bản chụp TRAIN và cấu hình phải tạo tệp `merges.ttmbpe` giống từng byte, SHA-256 giống nhau.

Đây là **oracle thiết kế**; chưa có kết quả kiểm thử TIE/OVERLAP/BOUNDARY thực thi.

## 5. Mẫu kiểm tra gần trùng và chia tập chưa thực thi

- **DUP01:** F02 và F03 có byte khác nhau nhưng khóa NFC giống nhau ⇒ cùng nhóm; vẫn giữ nguyên bản gốc.
- **DUP02:** cùng nội dung nhưng CRLF và LF ⇒ cùng nhóm sau chuẩn hóa khóa.
- **SHORT01:** hai chuỗi 1–7 mã điểm khác nhau ⇒ không gộp gần trùng nếu không chính xác bằng nhau.
- **TRANSITIVE01:** nếu A≈B và B≈C thì A, B, C cùng `group_id`, kể cả A không gần C.
- **SPLIT01:** đổi thứ tự bản ghi đầu vào không làm đổi nhãn nhóm hoặc phân tập.
- **LEAK01:** cặp gần trùng ở hai tập ⇒ FAIL, không được sửa ngưỡng sau khi biết TEST.
- **MIN01:** chỉ có 29 nhóm ⇒ `INSUFFICIENT_GROUPS`; không được tạo TEST hợp lệ.
- **RIGHTS01:** nguồn chưa được quyền dùng ⇒ REJECT, không đưa vào TRAIN.

## 6. Hợp đồng bộ kiểm tra độc lập (Independent QA Contract)

- Chương trình tạo dữ liệu (Generator), bộ tách token (Tokenizer) và bộ kiểm tra (Checker) phải ở **các mô-đun riêng**, đọc dữ liệu qua API đã khóa; không sao chép thuật toán BPE vào checker rồi kiểm tra cùng một đường tính.
- Checker hoàn nguyên phải so sánh **raw byte đầu vào và đầu ra**; oracle của F00–F11 được khóa bằng hex và SHA-256 độc lập ở tài liệu này.
- Với BPE, checker kiểm tra invariant, các trường hợp có kết quả đã nêu (TIE01, OVERLAP01) và tệp nhị phân đúng định dạng, không dùng lại cùng hàm phá hòa ở triển khai.
- Cần kiểm tra độc lập tổng SHA-256, số mẫu hợp lệ/bị từ chối, số test âm tính, quy tắc mã lỗi, thời gian, RAM và điều kiện giới hạn.
- Mọi FAIL được lưu, không đổi oracle để khớp phần mềm; nếu phát hiện oracle thiết kế sai, lập bản đính chính kế nhiệm trước khi cấp phép.
- **Hiện chưa có mã checker, chưa có kho dữ liệu F0 được materialize, chưa có lần chạy**. Chỉ được viết mã sau cổng triển khai I0.

**Quyết định H04:** `H04_F0_SPEC_DEFINED_WITH_BYTE_SHA`; `H04_INDEPENDENT_CHECKER_IMPLEMENTED=NO`; `H04_DYNAMIC_QA=NOT_EXECUTED`; `H04_D1_LOCK=PENDING`.
