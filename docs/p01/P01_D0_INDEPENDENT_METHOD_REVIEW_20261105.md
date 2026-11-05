# P01 — Thẩm định phương pháp độc lập với bộ kiểm tra tĩnh D0

**Mã thẩm định:** `TTM_P01_D0_INDEPENDENT_METHOD_REVIEW_20261105`  
**Ngày:** 05/11/2026  
**Nhánh:** `design/p01-tokenizer-data-prereg-20261105`  
**Mốc đối chứng kỹ thuật P00:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`  
**Phương thức:** đọc nội dung hợp đồng và lập luận về khả năng bác bỏ giả thuyết, độc lập với bộ kiểm tra từ khóa D0. Đây là **thẩm định phương pháp tách riêng**, không phải chuyên gia bên thứ ba và không phải thực nghiệm.

## 1. Kết luận tổng quan

- `P01_D0_DESIGN_COHERENCE=PASS_SCOPED`: kiến trúc B0/B1 và tiêu chí kiểm định phù hợp để tiếp tục nghiên cứu thiết kế, trong phạm vi tài liệu.
- `P01_D1_SCIENTIFIC_PREREG_LOCK=HOLD`: còn thiếu các tham số bắt buộc, không thể khẳng định nghiên cứu đã khóa.
- `P01_IMPLEMENTATION=NOT_AUTHORIZED`: chưa cấp quyền viết mã nguồn, tạo worktree, tải dữ liệu hoặc chạy huấn luyện.
- `P01_LOCAL_MAIN_BASELINE_SYNC=PASS`: đã xác minh tệp gốc trên máy Windows, nội dung ghi nhận dưới đây.

## 2. Kiểm tra việc đồng bộ nguồn và bảo toàn bằng chứng

| Hạng mục | Đối chiếu | Quyết định |
|---|---|---|
| Biên bản gốc | `evidence/p00/TTM_P01_BASELINE_FAST_FORWARD_20261105T083903147Z.json` | Đọc lại qua RemoteMCP |
| SHA-256 biên bản | `ee69f32a993d011b35173074a5ea221bdffc3feb70c780b532f045e9beb58b7f` | **PASS**, trùng tệp người dùng cung cấp |
| Nguồn trước đồng bộ | `c66e27a5d1e68958d42c825fd40f8a273994e0a0` | Đúng mốc cũ |
| Local `main` và `origin/main` | `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7` | **PASS**, trùng GitHub `main` lúc kiểm tra |
| Cây làm việc P00 | `382da2c52d0fb4efe1cd9de5c92e68de79a52a20` | Giữ nguyên |
| 15 tệp bảo vệ | Đọc SHA-256 của **từng tệp** trên Windows, so với biên bản | **15/15 PASS** |
| Dọn dẹp (Cleanup) | `NONE` | Không có dọn dẹp |
| Huấn luyện (Training) | `NOT_PERFORMED` | Không có dữ liệu khoa học mới |
| Quyền mở P01 | `p01_authorized=false` | Chưa cấp |
| Bản lưu GitHub | `artifacts/qa/p01/TTM_P01_BASELINE_FAST_FORWARD_20261105T083903147Z.json` | Nội dung khớp biên bản gốc, giữ cả CRLF |

**Ý nghĩa:** 15/15 là số tệp có mã băm nội dung khớp, **không** phải 15 phép thử bộ tách token. Đồng nhất 40 ký tự mã commit cho biết lịch sử mã nguồn đang được trỏ về cùng phiên bản, không cho biết chất lượng mô hình.

## 3. Thẩm định nội dung hợp đồng — 10 điều kiện thiết kế đạt

| Mã | Chủ đề | Kết luận và căn cứ |
|---|---|---|
| D01 | Mốc P00 và phạm vi | PASS: dùng đúng từ vựng byte 256 giá trị, ngữ cảnh 64; không thay mã P00 |
| D02 | B0 bảo toàn byte | PASS về thiết kế: mã byte 0–255 và giải mã có chế độ nghiêm ngặt (strict), không chuẩn hóa |
| D03 | Unicode đặc biệt | PASS về thiết kế: phân biệt Unicode tổ hợp, CRLF, emoji, byte lỗi và surrogate không hợp lệ |
| D04 | Tách B1 khỏi P00 | PASS: không đưa mã từ vựng BPE vượt 255 vào lớp nhúng (Embedding) P00 |
| D05 | Phân tách dữ liệu | PASS về chính sách: học BPE chỉ từ TRAIN, không từ VALIDATION/TEST |
| D06 | Kiểm soát quyền dữ liệu | PASS về chính sách: thiếu bằng chứng quyền sử dụng hoặc rà soát PII thì từ chối |
| D07 | Chống rò rỉ | PASS về đặc tả: giao cắt nhóm/raw hash/normalized hash giữa ba tập phải bằng 0 |
| D08 | Các phép đo có mục đích | PASS: hoàn nguyên 100%, token/byte và nén được giải thích, không suy diễn chất lượng GPT |
| D09 | Trường hợp thử từ chối | PASS: có nhóm thử Unicode lỗi, token sai, rò rỉ, TEST truy cập trái phép, OOM |
| D10 | Quy trình cấp quyền | PASS: khóa dữ liệu, QA và quyết định triển khai là các cổng riêng, không có việc thực thi ở D0 |

Các mục PASS ở đây khẳng định **tài liệu mô tả yêu cầu đúng phạm vi**; tuyệt đối không có nghĩa chức năng đã được hiện thực hoặc kiểm thử động.

## 4. Năm thiếu hụt chặn khóa tiền đăng ký D1

| Mã | Thiếu hụt (HOLD) | Tại sao là vấn đề? | Điều kiện phải bổ sung trước D1 |
|---|---|---|---|
| H01 | Thuật toán BPE chưa định nghĩa đủ | Cùng TRAIN có thể tạo merges khác nhau tùy cách đếm cặp, xử lý ranh giới tài liệu, sắp xếp hòa điểm và định dạng lưu | Đặc tả đếm cặp ở mức byte, ranh giới tài liệu, luật phá hòa không mơ hồ, token đặc biệt, mã từ vựng cuối cùng và định dạng byte chuẩn để tính SHA |
| H02 | Chưa chọn nguồn dữ liệu có giấy phép | Không thể chứng minh quyền sử dụng, phạm vi ngôn ngữ, kích thước hoặc tách TRAIN/VALIDATION/TEST | Danh mục từng nguồn với `source_id`, giấy phép, quyền huấn luyện, SHA-256 và duyệt PII; nguồn chưa duyệt phải bị từ chối |
| H03 | Chia tập và phát hiện gần trùng chưa khóa | `group_id` và SHA giống nhau không loại trừ tài liệu gần trùng; tỷ lệ 80/10/10 không bảo đảm mỗi tập không rỗng | Xác định thuật toán nhóm, ngưỡng gần trùng, cách xử lý văn bản ngắn, số nhóm tối thiểu, seed/tie-break chia tập và điều kiện `INSUFFICIENT_GROUPS` |
| H04 | Bộ mẫu F0 chưa được đóng dấu bất biến, QA độc lập chưa có mã | Các trường hợp viết bằng văn bản chưa phải các byte mẫu có oracle kỳ vọng; có thể sửa mẫu sau khi xem kết quả | Danh mục đầu vào byte, đầu ra dự kiến, SHA-256, trường hợp lỗi và bộ kiểm tra tách biệt có mã nguồn được duyệt |
| H05 | Ngân sách tính toán và quyết định thực thi chưa khóa | Không biết nguồn lực thực tế để bảo đảm không vượt dung lượng/không tải trái quyền; cỡ vocab 2048/4096 còn là ứng viên | Đo RAM/đĩa khả dụng, ngân sách tối đa (byte/tài liệu/thời gian), phân vùng cache/temp trong workplace và cỡ từ vựng dự kiến cho mỗi thí nghiệm |

**Phân loại:** 10/10 mục đánh giá tính đầy đủ của thiết kế D0 đạt trong phạm vi; 5/5 điều kiện chuẩn bị khóa D1 **chưa đạt trạng thái sẵn sàng**. Không cộng các con số này thành tỉ lệ thành công khoa học.

## 5. Phân tích rủi ro kỹ thuật cụ thể

### 5.1. Vấn đề Unicode và hoàn nguyên

Cùng một chữ có thể biểu diễn bằng ký tự ghép sẵn hoặc tổ hợp. Nếu hợp đồng đòi hoàn nguyên byte chính xác, phép chuẩn hóa NFC trong quá trình mã hóa là **vi phạm**. Có thể dùng khóa NFC riêng khi tìm trùng nhưng không thay byte gốc. Bộ kiểm tra phải so sánh bytes, không chỉ chuỗi nhìn giống nhau.

### 5.2. Vấn đề từ vựng BPE và mô hình P00

B0 ánh xạ byte 0–255 phù hợp `vocab_size=256` của P00. B1 có thể phát mã lớn hơn 255; nếu đưa trực tiếp vào mô hình P00, lớp nhúng sẽ truy cập ngoài miền. Đây là vấn đề tương thích hợp đồng (Interface Compatibility), không được sửa âm thầm bằng thay kích thước từ vựng trong P00.

### 5.3. Vấn đề chồng lặp giữa dữ liệu

Giao cắt raw hash bằng 0 chưa bảo đảm hai tập không chứa một bài viết với khác dấu câu hoặc được biên tập lại. Chỉ ghi `LEAKAGE_PASS` khi quy tắc nhóm trùng/gần trùng đã được khóa và kiểm định. Những cặp không phân xử được là `INCONCLUSIVE` và phải ngăn đi vào TEST.

### 5.4. Vấn đề chi phí và kết luận khoa học

Giảm số token/byte không đồng nghĩa giảm chi phí hoặc cải thiện loss huấn luyện. Từ vựng lớn hơn làm thay lớp nhúng và đầu mô hình; khi so sánh chất lượng về sau phải giải thích khác biệt tham số, mẫu dữ liệu, ngân sách huấn luyện và cách chuẩn hóa phép đo.

## 6. Quyết định và thứ tự tiếp theo

1. Giữ PR #4 ở **trạng thái nháp** để chứa thiết kế D0 và biên bản QA; không hợp nhất tự động.
2. Cho phép tiếp tục **hoàn thiện thiết kế D1 trên giấy**, theo năm thiếu hụt H01–H05. Đặc biệt không được chọn nguồn thật trước khi duyệt quyền.
3. Chỉ sau kiểm định độc lập D1 PASS mới xét phát hành khóa tiền đăng ký và một quyết định riêng cho triển khai.
4. Không dùng việc đã đồng bộ Git thành lý do cấp quyền tạo worktree P01, tải corpus, huấn luyện BPE/GPT hay dọn P00.

`TTM_P01_D0_METHOD_REVIEW=PASS_SCOPED_DESIGN`  
`TTM_P01_D1_PREREG_LOCK=HOLD_H01_H05`  
`TTM_P01_IMPLEMENTATION=NOT_AUTHORIZED`  
`TTM_P01_DATA_ACQUISITION=NOT_AUTHORIZED`  
`TTM_P01_TRAINING=NOT_AUTHORIZED`
