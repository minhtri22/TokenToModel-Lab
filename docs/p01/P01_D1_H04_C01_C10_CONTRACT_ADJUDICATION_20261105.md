# P01 D1 — Thẩm định độc lập hợp đồng C01–C10

**Ngày:** 05/11/2026. **Loại:** chỉ đánh giá thiết kế (Design-only).  
**Nguồn đánh giá:** PR #4, HEAD `29a486fce0944bd2b726322ea3a6b1abb64f9c5e`; mốc `main=92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.
**Căn cứ:** `P01_D1_H04_INDEPENDENT_CHECKER_DESIGN_GATE_20261105.md`, `P01_D1_H04_FIXTURES_AND_INDEPENDENT_QA_SPEC.md`, H01 BPE, H03 trùng/gần trùng, H02/H05 nguồn và tài nguyên.

**Quy ước:** `PASS_DESIGN` chỉ nghĩa hợp đồng đủ rõ ở phạm vi ghi; `HOLD_DESIGN` nghĩa thiếu điều kiện để kiểm thử độc lập; `FAIL_DESIGN` nghĩa có mâu thuẫn xác định. **Mọi C01–C10 đều `NOT_EXECUTED`.** Rà soát này tách tiêu chí khỏi kiểm tra tĩnh trước đó, nhưng không phải kết luận của chuyên gia bên thứ ba.

| Cổng | Quyết định hợp đồng | Căn cứ và vấn đề cần đóng |
|---|---|---|
| **C01 — Byte B0** | **PASS_DESIGN** | Miền 0–255 có oracle trực tiếp: byte `i` phải mã hóa thành ID `i` và giải mã về byte `i`, đủ 256/256. Không thay bằng kiểm tra số lượng đơn thuần. |
| **C02 — F0 hoàn nguyên** | **PASS_DESIGN** | 12 mẫu F00–F11 có byte và SHA-256 riêng, gồm NFC/NFD, CRLF, byte sai UTF-8. B1 sau này phải dùng bảng merges được đóng dấu; chưa có phép chạy. |
| **C03 — Unicode lỗi** | **HOLD_DESIGN** | Cần bảng oracle theo API và loại lỗi: `decode_bytes` chấp nhận byte bất kỳ nhưng `decode_text` phải từ chối UTF-8 lỗi; `encode_text` từ chối surrogate đơn lẻ. Không coi ngoại lệ bất kỳ là PASS. |
| **C04 — ID lỗi** | **HOLD_DESIGN** | Phải liệt kê riêng ID âm, vượt vocab, `True`, số thực, chuỗi, lồng danh sách; khóa loại lỗi. B1 ID 256 vào P00 phải được chặn **trước** lớp nhúng, không chỉ dựa vào exception sau khi gọi model. |
| **C05 — BPE** | **HOLD_DESIGN** | TIE01/OVERLAP01/BOUNDARY01 chủ yếu khóa vòng đầu. Cần oracle nhiều vòng và parser từ chối merges sai magic, truncated, byte thừa, ID trỏ tương lai, quy tắc trùng, kích thước vượt trần. |
| **C06 — Tái lập** | **HOLD_DESIGN** | Cần khóa thứ tự/định dạng snapshot TRAIN, cấu hình, phiên bản và hai tiến trình riêng; so chính xác bytes + SHA-256 `merges.ttmbpe`, không chỉ so số merges. |
| **C07 — Chống rò rỉ** | **HOLD_DESIGN** | Chỉ so `group_id` có thể bỏ sót gần trùng khi phân nhóm sai. Cần oracle dưới/bằng/trên ngưỡng, nhóm bắc cầu, chia tập độc lập, bằng chứng chặn đọc TEST trong lúc học BPE. |
| **C08 — Quyền nguồn** | **HOLD_DESIGN** | Cần thử trạng thái `ALLOW/PENDING/REJECT`, PII chưa duyệt, giấy phép thiếu/hết hạn, checksum sai, dưới 30 nhóm. Chưa có nguồn F1/F2 được chấp thuận. |
| **C09 — Giới hạn tài nguyên** | **HOLD_DESIGN** | Console Windows đạt RAM/đĩa **trước** chạy nhưng chưa có oracle giới hạn RAM toàn cây tiến trình, thời gian, đĩa, biên bản dừng và chống chạy lại. |
| **C10 — Bằng chứng** | **HOLD_DESIGN** | Cần chuẩn manifest nguồn/mã/fixture, vị trí trong workspace, kiểm SHA từ đường độc lập, nguyên tắc không ghi đè, xử lý lỗi và đọc lại. Biên bản tự công bố hash không đủ xác minh độc lập. |

## Phản ví dụ bắt buộc cho bản hợp đồng sửa

- F07 byte `c328`: `decode_bytes` hoàn nguyên hai byte, `decode_text` báo lỗi UTF-8.
- B1 có ID 256: lớp kiểm tra tương thích phải chặn trước khi gọi P00 `vocab_size=256`.
- TIE01 vòng đầu: cặp `(97,98)` và `(98,97)` cùng tần suất 3; quy tắc phá hòa chọn `(97,98)`. OVERLAP01 `aaaa`: đếm 3 vị trí nhưng chỉ ghép 2 cặp không chồng lấn.
- Hai tài liệu có cùng nội dung gần trùng nhưng `group_id` khác phải bị checker phát hiện; kết quả chia tập không được dùng lại làm oracle duy nhất.
- RAM `10.959 GiB`, D: trống `34.869 GiB` chỉ là ảnh chụp tài nguyên ở thời điểm đo, chưa chứng minh bộ giới hạn tiến trình.

## Các điều kiện chặn I0

| Mã | Yêu cầu trước khi xét lại |
|---|---|
| G04-01 | Khóa ma trận API × đầu vào × lỗi kỳ vọng và giai đoạn từ chối |
| G04-02 | BPE oracle nhiều vòng; merges hợp lệ và các lỗi parser |
| G04-03 | Trường hợp trùng/gần trùng sát ngưỡng và oracle nhóm/split độc lập |
| G04-04 | Snapshot TRAIN, tái lập hai tiến trình, bằng chứng TEST không bị học |
| G04-05 | Danh mục giấy phép/PII và phản ví dụ từ chối nguồn |
| G04-06 | Thiết kế giới hạn RAM/đĩa/thời gian cho toàn cây tiến trình và biên bản lỗi |
| G04-07 | Chuẩn hóa evidence manifest, hash độc lập, biên bản bất biến |
| G04-08 | Thẩm định độc lập lại toàn bộ G04-01..07, ghim commit/SHA trước quyết định |

**Tổng:** `PASS_DESIGN=2`, `HOLD_DESIGN=8`, `FAIL_DESIGN=0`, `EXECUTED=0`. Không tự biến HOLD thành PASS. 0 FAIL chỉ nghĩa chưa xác định mâu thuẫn tất yếu trong phần nguồn đã đọc.

**Quyết định:** `H04_CHECKER_CONTRACT=HOLD_WITH_SCOPED_PASS`; `P01_D1_SCIENTIFIC_LOCK=NOT_GRANTED`; `I0_IMPLEMENTATION=NOT_AUTHORIZED`; `PR4_MERGE=NOT_AUTHORIZED`. Không tạo worktree P01, không tải dữ liệu, không huấn luyện BPE/GPT, không dọn P00.

**Bước tiếp theo:** `TTM_P01_D1_H04_CHECKER_ORACLE_AND_FAIL_CLOSED_CONTRACT_REPAIR_DESIGN_ONLY` — hoàn thiện G04-01..07 trên giấy rồi thẩm định G04-08 riêng.
