# P01 D1 — G04-08: Thẩm định chéo sau sửa hợp đồng checker

**Mã:** TTM_P01_D1_H04_G04_08_INDEPENDENT_CONTRACT_REVIEW_DESIGN_ONLY.
**Ngày:** 05/11/2026. **Chỉ thiết kế**; không chạy tokenizer/checker, không sử dụng dữ liệu hoặc thay Windows.
**Đối chứng:** main 92facee15d7c0d46b0e84ddf5b6d8b2073e078f7; PR #4 giữ trạng thái nháp.
**Nguồn đọc lại:** G04-01..03 Git blob 98b1c653a5bef4ac0c94d4d6fc0c239362f5bbba; G04-04..07 Git blob 67d3845c9491d105f864525fa4eed021bf29c29f. Đây là rà soát chéo theo tiêu chí khác với bộ kiểm tra từ khóa, không phải đánh giá của chuyên gia bên thứ ba.

## 1. Kết quả bảy hợp đồng sửa

| Cổng | Quyết định thiết kế | Điều kiện đã được bổ sung và khoảng trống còn lại |
|---|---|---|
| G04-01 | **PASS_DESIGN** | A01–A10 khóa API byte/text, ID, mã lỗi và điểm chặn trước P00; chưa có kiểm thử động. |
| G04-02 | **PASS_DESIGN** | M01–M04 có nhiều vòng BPE, không chồng lấn, phá hòa và quy tắc parser; thiếu golden bytes thật của merges trước I0. |
| G04-03 | **HOLD_DESIGN** | K01–K08 có oracle số học, NFC/Levenshtein/Jaccard/nhóm. Chưa có cặp văn bản cụ thể tạo tập 5-gram đúng sát ngưỡng 0,85, nên lỗi trích n-gram vẫn có thể cho PASS giả. |
| G04-04 | **PASS_DESIGN** | Đã mô tả snapshot TRAIN dạng binary có độ dài, thứ tự ID, payload và SHA, so sánh hai tiến trình; TEST không có quyền đọc. Chưa có corpus ALLOW hoặc chạy thực tế. |
| G04-05 | **PASS_DESIGN** | R01–R08 bao phủ quyền ALLOW/PENDING/REJECT, PII, checksum, nhóm tối thiểu; H02 nguồn F1/F2 vẫn HOLD riêng. |
| G04-06 | **HOLD_DESIGN** | Có yêu cầu bảo vệ toàn cây process và ca dừng, nhưng chưa chọn duy nhất bộ đếm RAM trên Windows (commit/private bytes so với RSS) và oracle dừng trên Job Object, nên chưa đủ khóa cơ chế bảo vệ. |
| G04-07 | **PASS_DESIGN** | Có manifest, hash, đường dẫn an toàn, create-new, đọc lại độc lập và JCS; chưa có golden manifest byte hoặc kiểm thử động trước I0. |

**Tổng G04:** 5 PASS_DESIGN, 2 HOLD_DESIGN, 0 FAIL_DESIGN; 7/7 NOT_EXECUTED.

## 2. Quyết định C01–C10 sau sửa

| Nhóm | Trước sửa (L0015) | Sau sửa G04-08 |
|---|---|---|
| C01 — B0 toàn miền byte | PASS_DESIGN | **PASS_DESIGN** |
| C02 — F0 hoàn nguyên | PASS_DESIGN | **PASS_DESIGN** |
| C03 — Unicode lỗi | HOLD_DESIGN | **PASS_DESIGN** |
| C04 — ID ngoài miền | HOLD_DESIGN | **PASS_DESIGN** |
| C05 — BPE nhiều vòng, parser | HOLD_DESIGN | **PASS_DESIGN** |
| C06 — Tái lập | HOLD_DESIGN | **PASS_DESIGN** |
| C07 — Chống rò rỉ | HOLD_DESIGN | **HOLD_DESIGN** |
| C08 — Quyền dữ liệu | HOLD_DESIGN | **PASS_DESIGN** |
| C09 — Giới hạn tài nguyên | HOLD_DESIGN | **HOLD_DESIGN** |
| C10 — Bằng chứng | HOLD_DESIGN | **PASS_DESIGN** |

**Tổng C01–C10:** 8 PASS_DESIGN, 2 HOLD_DESIGN, 0 FAIL_DESIGN, 10 NOT_EXECUTED. PASS_DESIGN chỉ nghĩa đủ đặc tả để xây phép thử sau một permit riêng, không phải checker/huấn luyện đã được chạy.

## 3. Phản biện và đính chính

- Bản G04-03 lúc tạo ban đầu đã ghi sai mẫu số Jaccard khi cố định kích thước hai tập nhưng thay số giao. Đã sửa trước lần thẩm định này: với |A|=18, |B|=19, giao 16 có union 21 => J=16/21; giao 17 có union 20 => J=17/20; giao 18 có union 19 => J=18/19. Đây là lỗi oracle thiết kế, **không phải FAIL thực nghiệm**.
- BPE M01 từ chuỗi abababab tạo hai lượt (97,98)->256, (256,256)->257; thiếu kiểm tra parser hoặc thứ tự ghép vẫn có thể tạo PASS giả. Golden merges byte phải được đóng dấu trước I0.
- Console Windows đo RAM 10.959 GiB và D: trống 34.869 GiB chỉ đủ ngưỡng ứng viên trước chạy; không thay cho giới hạn runtime.
- Hồ sơ F0-only chưa có nguồn thực tế ALLOW; không được kết luận chất lượng BPE hoặc gỡ khóa thực nghiệm bằng kết quả kiểm tra byte mẫu.

## 4. Điều kiện còn phải đóng trước khi xét I0

1. R-G04-03: tạo ít nhất ba cặp văn bản UTF-8 có byte, hex, SHA-256 và tập 5-gram tính độc lập, lần lượt dưới/bằng/trên ngưỡng; bổ sung ca tỉ lệ chiều dài và nhóm bắc cầu.
2. R-G04-06: chọn đúng một bộ đếm bộ nhớ, giới hạn trên toàn cây process, cơ chế gắn Job Object trước chạy, chống breakaway, dừng an toàn và oracle âm tính có receipt.
3. R-G04-07: golden manifest byte/JCS và parser độc lập là yêu cầu trước I0 dù C10 đã PASS ở mức đặc tả.
4. H02: nguồn F1/F2 có giấy phép/PII/SHA hoặc giữ F0-only; H05: guard có QA âm tính; mọi quyết định khóa D1/I0 phải tách riêng.

## 5. Quyết định cuối

- TTM_P01_D1_G04_08_DESIGN_REVIEW=COMPLETED_WITH_HOLD
- TTM_P01_D1_H04_PASS_DESIGN=8
- TTM_P01_D1_H04_HOLD_DESIGN=2
- TTM_P01_D1_H04_FAIL_DESIGN=0
- TTM_P01_D1_H04_DYNAMIC_TESTS_EXECUTED=0
- TTM_P01_D1_SCIENTIFIC_LOCK=NOT_GRANTED
- TTM_P01_I0_IMPLEMENTATION_PERMIT=NOT_GRANTED
- P01_WORKTREE_CREATION_AUTHORIZED=false
- P01_DATA_DOWNLOAD_AUTHORIZED=false
- P01_TRAINING_AUTHORIZED=false
- PR4_MERGE_AUTHORIZED=false
- P00_CLEANUP_AUTHORIZED=false

**Bước tiếp theo:** TTM_P01_D1_G04_03_06_REMAINING_DESIGN_HOLD_CLOSURE — khóa oracle văn bản 5-gram thực và quy tắc Job Object/bộ đếm RAM ở mức thiết kế; thẩm định lại C07/C09 trong quyết định riêng.
