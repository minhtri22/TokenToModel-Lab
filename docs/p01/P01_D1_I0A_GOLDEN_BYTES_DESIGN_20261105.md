# P01 D1 — Mẫu byte chuẩn I0A: merges, snapshot và manifest (Golden Bytes)

**Mã:** `TTM_P01_I0A_GOLDEN_BYTES_V1_DESIGN`. **Ngày:** 05/11/2026.  
**Trạng thái:** `GOLDEN_DESIGN_CONSTRUCTED_NO_P01_RUNTIME`. Các byte dưới đây được tính trong **môi trường đánh giá độc lập**, không tải dữ liệu, không dùng mã tokenizer P01, không tạo fixture trong workplace Windows. Không có huấn luyện BPE hay kiểm thử động P01.

## 1. BPE M01 — Golden `merges.ttmbpe`

Đối tượng là fixture thiết kế `abababab` (hex `6162616261626162`) trong đặc tả M01; chỉ dùng để xác định **đầu ra mong đợi**. `target_vocab_size=258`, `actual_vocab_size=258`, `merge_count=2`. Hai quy tắc:

- `rank=0`: `(left=97,right=98,new=256)` — cặp `ab` có 4 vị trí;
- `rank=1`: `(left=256,right=256,new=257)` — cặp `256,256` có 3 vị trí sau lượt đầu.

Định dạng nhị phân: đúng 11 byte magic `TTM_BPE_V1\0`, tiếp theo 3 số `uint32 little-endian`, rồi mỗi quy tắc gồm 3 số `uint32 little-endian`; không dấu thời gian, không ký tự xuống dòng cuối. `11+12+2×12=47 byte`.

**Hex chính xác (47 byte):**

```text
54544d5f4250455f563100020100000201000002000000610000006200000000010000000100000001000001010000
```

**SHA-256 trên 47 byte nhị phân:** `11c72190c6f3b757d260c426c357a4de8ff36313495f2299da81638386289e8d`.

Trường hợp phải từ chối: thiếu byte magic hoặc byte NUL; `merge_count` khác độ dài file; thêm/truncate một byte; `actual!=256+count`; `new_id!=256+rank`; tham chiếu token chưa tạo; cùng cặp bị khai báo lần hai; `target<256`; tệp lớn hơn ngưỡng. Đừng chấp nhận parser chỉ đọc một phần tệp rồi in `PASS`.

## 2. Snapshot TRAIN nhị phân — **chỉ minh họa định dạng, không phải source ALLOW**

Để kiểm tra writer/reader tương lai mà **không giả vờ đã nhận nguồn F1/F2**, ví dụ này dùng nhãn nguồn `F0-SPEC-NOT-APPROVED` và bản ghi giả lập `F0-M01`, byte payload `abababab`. Đây là **golden serialization test vector**, không phải snapshot được phép học, không phải mẫu khoa học và không được cấp quyền E0.

Định dạng theo phụ lục G04-04: ASCII prefix `TTM_P01_TRAIN_V1\n`; SHA-256 32 byte của source-manifest marker; SHA-256 32 byte của config marker; số bản ghi `u32le(1)`; `u32le(len(document_id)) + UTF8(document_id)`; `u32le(len(source_id)) + UTF8(source_id)`; `raw_sha256[32]`; `group_id[32]`; `u64le(8)`; 8 byte payload.

- `source-manifest marker` **không phải manifest nguồn hợp pháp**: ASCII `TTM_P01_F0_GOLDEN_NO_REAL_SOURCE\n`, SHA-256 `3fd48e766c989656426013ee5e8e453afbf14548daa750c386673de02058a33d`.
- `config marker`: ASCII `TTM_P01_F0_GOLDEN_CONFIG_ONLY\n`, SHA-256 `6ed0342615243efc6a190e69881592f25f80b9cac388b2f17e1cdc549355b433`.
- `document_id = F0-M01` — đúng 6 byte ASCII; `source_id = F0-SPEC-NOT-APPROVED` — đúng 20 byte ASCII.
- `raw_sha256(abababab)`: `9ba3d1c770bd1d031494bbd49d53e1e0b6b5512a4b3a2d56d274e4bb173a2a00`.
- `group_id = SHA256(ASCII("TTM-P01-GROUP-V1") || 0x00 || bytes32(raw_sha256))`: `8349b7cc4446092bf34f4deaa1488582e849571e4e46546172450923b4625e6f`.

**Hex chính xác (199 byte, nối các dòng sau, không thêm khoảng trắng hoặc newline):**

```text
54544d5f5030315f545241494e5f56310a
3fd48e766c989656426013ee5e8e453afbf14548daa750c386673de02058a33d
6ed0342615243efc6a190e69881592f25f80b9cac388b2f17e1cdc549355b433
01000000
0600000046302d4d3031
1400000046302d535045432d4e4f542d415050524f564544
9ba3d1c770bd1d031494bbd49d53e1e0b6b5512a4b3a2d56d274e4bb173a2a00
8349b7cc4446092bf34f4deaa1488582e849571e4e46546172450923b4625e6f
0800000000000000
6162616261626162
```

**SHA-256 trên đúng 199 byte sau khi nối:** `026744455f6a71b178702ce077737ff9c416b3cc716b5711f6b8ef6d0779697d`.

Đây là **ví dụ cấu trúc**, được cố tình thiết kế để **không đủ quyền học BPE**. Reader nào phân loại marker `F0-SPEC-NOT-APPROVED` thành `ALLOW` là FAIL nguồn. Một nguồn thật cần `source_manifest` và `config` được duyệt, SHA chính xác và các điều kiện H02/H03 riêng.

## 3. Manifest JSON chuẩn — Golden JCS, **không phải receipt đã chạy**

Áp dụng JSON Canonicalization Scheme theo **RFC 8785** (I-JSON; thứ tự thuộc tính xác định). Golden dưới đây chỉ thử chức năng chuẩn hóa JSON với **4 trường**, cố ý dùng `operation_id=DESIGN_ONLY_NO_RUN`. **Không** là manifest hoàn chỉnh của một lần chạy được chấp thuận.

**Byte UTF-8 chính xác (109 byte, một dòng, không BOM/newline):**

```json
{"files":[],"final_status":"INCONCLUSIVE","operation_id":"DESIGN_ONLY_NO_RUN","schema":"TTM_P01_EVIDENCE_V1"}
```

**SHA-256 của 109 byte:** `492204b007b172f734a38bf0d80db357a57efff90e319f2dbaf3b63f9135e826`.

Trường hợp âm tính: thêm newline cuối; BOM; đổi thứ tự khóa chưa chuẩn hóa; trùng tên khóa; `NaN`; sửa một byte; đổi `final_status` thành `PASS` khi chưa có `files/source/checker` thực; đưa đường dẫn tuyệt đối hoặc `..\` ra ngoài root. Golden 4 trường không được dùng để bỏ qua những trường bắt buộc trong schema `TTM_P01_EVIDENCE_V1` khi cấp quyền QA0.

Nguồn tham khảo: https://www.rfc-editor.org/rfc/rfc8785.

## 4. Hợp đồng kiểm tra golden trước khi xin triển khai

1. Một trình tạo và một trình đọc riêng phải có code SHA/commit ghim trước QA0; không dùng chung hàm ghi/đọc để kiểm tra byte.
2. Với merges, kiểm tra 47 byte, magic, field, thứ tự ID, SHA; với snapshot kiểm tra 199 byte, các trường nguồn, SHA raw/group; với JCS kiểm tra 109 byte và quy tắc UTF-8/canonical.
3. Ít nhất một byte bị đảo hoặc thiếu ⇒ FAIL; checksum do chính writer in ra mà không được reader độc lập băm lại ⇒ HOLD/FAIL.
4. Toàn bộ ví dụ ở đây là **source specification**, không phải tệp golden đã materialize trên Windows, không phải kết quả chạy P01.
5. Không được dùng golden snapshot chứa nhãn nguồn không hợp pháp để bypass cổng giấy phép; không có quyền đọc TEST hoặc huấn luyện.

**Quyết định:** `GOLDEN_MERGES_BYTES=SPECIFIED`; `GOLDEN_SNAPSHOT_BYTES=SPECIFIED_NON_ADMISSIBLE`; `GOLDEN_JCS_BYTES=SPECIFIED_NON_RECEIPT`; `GOLDEN_RUNTIME_QA=NOT_EXECUTED`; `I0A_PERMIT=NOT_GRANTED`.

## 5. Golden manifest đủ bộ khóa trong schema — negative admission, không có lượt chạy

Ví dụ JCS 109 byte ở mục 3 chỉ kiểm tra serialization tối thiểu. Để tránh **PASS giả do schema thiếu trường**, thêm ví dụ có đủ các khóa bắt buộc từ hợp đồng G04-07. Những giá trị `null` (checker, tokenizer, thời điểm chạy, exit code) và `operation_id=DESIGN_ONLY_NO_RUN` cố tình xác định **không có lượt chạy**; việc gán `PASS` hay tiếp nhận như receipt thực thi phải bị từ chối.

**UTF-8/JCS chính xác 774 byte, không BOM/newline:**

```json
{"checker_source_sha256":null,"config_sha256":"6ed0342615243efc6a190e69881592f25f80b9cac388b2f17e1cdc549355b433","exit_code":null,"files":[],"final_status":"INCONCLUSIVE","fixture_spec_sha256":null,"git_commit_sha":"92facee15d7c0d46b0e84ddf5b6d8b2073e078f7","merges_file_sha256":"11c72190c6f3b757d260c426c357a4de8ff36313495f2299da81638386289e8d","operation_id":"DESIGN_ONLY_NO_RUN","resource_summary":{"max_job_commit_bytes":4294967296,"peak_job_commit_bytes":null,"wall_elapsed_ms":null},"run_end_utc":null,"run_start_utc":null,"schema":"TTM_P01_EVIDENCE_V1","source_manifest_sha256":"3fd48e766c989656426013ee5e8e453afbf14548daa750c386673de02058a33d","tokenizer_source_sha256":null,"train_snapshot_sha256":"026744455f6a71b178702ce077737ff9c416b3cc716b5711f6b8ef6d0779697d"}
```

**SHA-256:** `d09396eb72ff318e9820d76bb999acae01cfeb9547ae80187d0e33d970119beb`.

Đây là **golden định dạng và bài thử từ chối**, không phải một manifest hợp lệ để cấp quyền:
- Không có source F1/F2 được duyệt; trường source SHA tham chiếu marker **F0 giả lập không có quyền học**.
- Không có `checker_source_sha256`, `tokenizer_source_sha256`, `fixture_spec_sha256`, thời gian hoặc file thực.
- Tất cả mã SHA được tham chiếu là **giá trị giả lập từ thiết kế**, không phải xác nhận tệp đã materialize.
- Checker phải phân biệt **cú pháp JCS hợp lệ** với **chứng cứ nghiên cứu đủ điều kiện**. Nếu chỉ vì parse JSON và hash trùng mà kết luận `PASS`, đó là **FAIL về kiểm soát bằng chứng**.

**Bài âm tính:** đảo một byte trong một SHA, xóa trường bắt buộc, gán `final_status=PASS` mà giữ các `null`, chèn `operation_id` trùng, hoặc dùng `resource_summary` chưa có kết quả đo thật. Mọi trường hợp phải bị từ chối theo chính sách receipt thực thi; không tự sửa dữ liệu để khớp mẫu.
