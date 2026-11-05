# P01 D1 — Thẩm định phương pháp và quyết định chưa khóa tiền đăng ký

**Mã đánh giá:** `TTM_P01_D1_PREREGISTRATION_METHOD_REVIEW_20261105`  
**Ngày:** 05/11/2026  
**Nhánh:** `design/p01-tokenizer-data-prereg-20261105`  
**Mốc đối chứng:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`  
**Kết luận:** `PASS_SCOPED_DOCUMENT_METHOD_REVIEW`; `D1_SCIENTIFIC_PREREG_LOCK=HOLD`.

## 1. Phương pháp thẩm định

Đánh giá lần hai dựa trên các **bất biến và phản ví dụ kỹ thuật**, thay vì chỉ xác nhận có tiêu đề hoặc từ khóa. Đọc lại bốn đặc tả H01/H02/H03/H04/H05 từ GitHub và đối chiếu với hợp đồng P00, tài liệu D0 và cổng quản trị.

Bằng chứng kiểm tra riêng, **không chạy BPE**:
- Kiểm tra tính hiện diện và nhất quán của **18/18 điều kiện cấu trúc** trong các tệp thiết kế trên GitHub.
- Tái tính SHA-256 bằng hàm băm tiêu chuẩn từ **12 chuỗi byte giả lập** trong F00–F11: **12/12 mã khớp**.
- Đối chiếu F02/F03 sau Unicode NFC: cùng biểu diễn chuẩn hóa, nhưng SHA byte gốc khác nhau, đúng yêu cầu tách khóa đối chiếu khỏi dữ liệu nguồn.
- Kiểm tra quy tắc giải mã UTF-8 nghiêm ngặt trên byte giả lập F06/F07/F08 bằng thư viện tiêu chuẩn: **3/3 bị từ chối**. Đây là kiểm tra oracle thiết kế trong môi trường chuẩn bị, **không phải kết quả thử bộ tách token P01 trên Windows**.
- Lượt kiểm tra từ khóa đầu tiên được 17/18 do dùng sai chuỗi dò “ít nhất 30 nhóm”; kiểm tra lại mệnh đề đúng “tối thiểu 30 nhóm” đạt 18/18. Lỗi dò không được tính là FAIL khoa học.

**Giới hạn về tính độc lập:** đây là lượt rà soát thứ hai theo tiêu chí khác và tính SHA bằng đường riêng; không phải kết quả do chuyên gia bên ngoài hay một bộ thực thi độc lập trên Windows thực hiện. Không tự phát `INDEPENDENT_DYNAMIC_QA_PASS`.

## 2. Bảng thẩm định H01–H05

| Mã | Nội dung được hoàn thiện | Trạng thái đặc tả | Bằng chứng còn thiếu trước khóa D1 |
|---|---|---|---|
| **H01** | Thuật toán BPE byte 0–255, đếm cặp, phá hòa theo ID, ghép không chồng lấn, dừng khi tần suất dưới 2, định dạng byte chuẩn cho merges | `DESIGN_SPEC_DEFINED` | Thẩm định độc lập giả mã và khóa chính xác format/nguồn trước I0; kiểm thử tái lập thuộc giai đoạn thực thi sau cấp quyền |
| **H02** | Danh mục giấy phép và quyết định nhận từng nguồn, từ chối dữ liệu thiếu quyền/PII | `ADMISSION_POLICY_DEFINED` | **Chưa có nguồn nào đủ hồ sơ quyền sử dụng** ⇒ `HOLD_SOURCE_RIGHTS` |
| **H03** | Khóa đối chiếu NFC riêng, ngưỡng Levenshtein/Jaccard đề xuất, nhóm liên thông, chia tập nhóm bằng SHA với seed 20261105, 0 giao cắt | `DESIGN_SPEC_DEFINED` | Chưa có dữ liệu thật, chưa biết tỷ lệ dương tính giả/âm tính giả; ngưỡng mới là ứng viên **chưa phê duyệt khóa khoa học** |
| **H04** | 12 mẫu byte F0–F11 có hex và SHA-256, tám mẫu âm tính N01–N08 và oracle BPE/near-duplicate | `FIXTURE_ORACLE_DEFINED` | **Chưa có mã QA độc lập được phê duyệt**; chưa materialize fixture và chưa thực thi |
| **H05** | Ngân sách ứng viên 64 MiB/2.000 tài liệu, RAM đỉnh 4 GiB, RAM khả dụng tối thiểu 8 GiB, ổ D: tối thiểu 16 GiB, giới hạn 1.800 giây | `BUDGET_PROPOSED` | **Chưa đo RAM/đĩa tại thời điểm chạy** và chưa chứng minh bộ giới hạn tiến trình hoạt động ⇒ `HOLD_RESOURCE_PREFLIGHT` |

**Đánh giá:** cả năm thiếu hụt đã có giải pháp hoặc chính sách **ở mức tài liệu**. Tuy nhiên, H02, H04 và H05 vẫn còn phụ thuộc vào bằng chứng chưa tồn tại; H03 chưa có thẩm định ngưỡng trên nguồn hợp pháp. Không gán `D1_LOCK_PASS` chỉ vì bảng viết đủ.

## 3. Phản biện cần lưu trước quyết định khóa

1. **Phá hòa BPE:** chọn bộ ID số nguyên nhỏ nhất là xác định, nhưng khác với phá hòa của một thư viện BPE ngoài dự án. B1 chỉ được so với chính hợp đồng đã ghi, không mặc nhiên tương đương tokenizer thương mại.
2. **Cặp chồng lấn:** đếm mọi vị trí liền nhau nhưng ghép thực tế không chồng lấn; hai thao tác khác nhau là chủ ý và phải được kiểm thử bằng `aaaa`.
3. **NFC và khả năng hoàn nguyên:** chuẩn hóa chỉ xảy ra trên khóa phát hiện trùng, không trên byte nguồn; nếu mã hóa qua NFC và trả byte NFC thay cho NFD, đó là FAIL hợp đồng B0/B1.
4. **Nhóm liên thông:** một chuỗi nối A–B–C có thể gom cả A và C dù chúng không trực tiếp gần nhau. Đây là lựa chọn bảo thủ chống rò rỉ, nhưng có thể làm giảm số nhóm độc lập; phải báo số nhóm và các nhóm lớn bất thường.
5. **Phạm vi kiểm tra gần trùng:** Jaccard/Levenshtein không phát hiện được mọi bản diễn đạt lại. Cấm tuyên bố “rò rỉ bằng 0 tuyệt đối”; chỉ được ghi giao cắt bằng 0 theo quy tắc tiền đăng ký.
6. **Kích thước từ vựng và P00:** B1 2048 token không thể đưa trực tiếp vào P00 256 token; đòi hỏi hợp đồng mới ở giai đoạn triển khai, không âm thầm thay mã P00.
7. **Nguồn lực:** ngân sách đề xuất là mức trần thử nghiệm, không phải bằng chứng máy Windows có đủ dung lượng; việc thiếu phép đo thực tế chặn quyền chạy.
8. **Quyền dữ liệu:** nếu chưa có một `source_id` được phê duyệt, không có lý do để tải corpus, chạy học BPE hoặc phát hành một khóa khoa học giả.

## 4. Các tiêu chí quyết định D1 tiếp theo

Muốn xét `D1_SCIENTIFIC_PREREG_LOCK` ở một quyết định riêng cần:
- Tệp đặc tả H01/H03/H04 được thẩm định và ghim **commit + SHA-256**; không có sửa ngầm sau khi đã cấp khóa.
- Ít nhất một nguồn F1 được xác minh quyền sử dụng (hoặc quyết định phạm vi chỉ F0, đồng nghĩa không có kết luận nén trên corpus thật); mỗi nguồn có ID, bằng chứng quyền, SHA-256 và chính sách PII.
- Quy tắc chia tập, seed, ngưỡng gần trùng, số nhóm tối thiểu và chính sách xử lý nhóm lớn đã được phê duyệt **trước khi xem TEST**.
- Bộ kiểm tra QA độc lập và cách tạo fixture đã qua kiểm định tĩnh ở một cổng riêng; không tự coi mô tả fixture là mã đã chạy.
- Thiết bị Windows, RAM/đĩa, phạm vi cache/temp, bộ giới hạn tiến trình và ngân sách byte/thời gian được kiểm tra thực tế trước cấp permit.
- Có quyết định rõ về phạm vi triển khai `I0` và thực nghiệm `E0`, mỗi bước có cổng riêng; không tạo worktree/tải dữ liệu ngay khi chỉ có tài liệu.

## 5. Kết luận

- `P01_D1_GAP_DOCUMENTATION=COMPLETE_WITH_LIMITATIONS`
- `P01_D1_METHOD_REVIEW=PASS_SCOPED_DOCUMENT_ONLY`
- `P01_D1_SCIENTIFIC_PREREG_LOCK=HOLD_SOURCE_QA_RESOURCE`
- `P01_IMPLEMENTATION_AUTHORIZED=false`
- `P01_DATA_DOWNLOAD_AUTHORIZED=false`
- `P01_TOKENIZER_TRAINING_AUTHORIZED=false`
- `P01_MODEL_TRAINING_AUTHORIZED=false`
- `P01_WORKTREE_CREATION_AUTHORIZED=false`
- `P00_CLEANUP_AUTHORIZED=false`

PR #4 cần **tiếp tục ở trạng thái nháp, không hợp nhất**. Việc cho phép xử lý các khoảng trống bằng kiểm tra chỉ đọc hoặc bổ sung hồ sơ không đồng nghĩa cấp quyền thực thi.

## 6. Nguồn tham khảo độc lập

- Unicode Normalization Forms: https://www.unicode.org/reports/tr15/
- Bài báo tổng quan về đặc tính thuật toán BPE: https://doi.org/10.1162/COLI.a.23

Các ngưỡng và giới hạn số trong D1 là **quyết định thiết kế đề xuất của TTM**, không phải ngưỡng được các nguồn trên xác nhận là tối ưu cho tiếng Việt.
