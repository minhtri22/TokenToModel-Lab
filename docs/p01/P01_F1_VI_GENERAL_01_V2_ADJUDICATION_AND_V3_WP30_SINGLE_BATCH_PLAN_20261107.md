# TTM P01 — Biên bản F1 V2 và kế nhiệm V3 có giới hạn

Ngày: 07/11/2026. Mã: `TTM_P01_F1_SNAPSHOT_V2_READBACK_AND_WP30_V3_TARGETED_RECOVERY`.

## 1. Kết quả thực tế và phạm vi phán quyết

Tệp biên bản Windows `evidence/p01/TTM_P01_F1_VI_GENERAL_01_SOURCE_SNAPSHOT_20261107.json` được người dùng tải lên, SHA-256 kiểm tra độc lập `c4b1faa9abd3562816cc3de880cbcfec6a02542829aab31d9ca81d0651871049`, trùng console. Snapshot V2 hoàn tất tiền tiếp nhận: 100 ứng viên, 83 được fetch/parse, 10 văn bản Wikisource đạt sàng lọc tự động, 10 nhóm H03. Vẫn thiếu 20 nhóm so với ngưỡng 30, chưa có `F1=ALLOW`. Trên Windows đọc lại được receipt, marker V2 cùng 10 cặp `.source/.txt` trong quarantine. Không có split TRAIN/VALIDATION/TEST, không có E0.

| Nguồn | Sàng lọc tự động PASS | HOLD | Mã HOLD |
|---|---:|---:|---|
| Wikipedia | 0 | 70 | RIGHTS_UNCLEAR 70; trong đó PII_OR_SECRET_PATTERN 4 |
| Wikisource | 10 | 10 | COLLECTION_OR_PARSE_FAILED 7; RIGHTS_UNCLEAR 3 |
| VBPL | 0 | 10 | COLLECTION_OR_PARSE_FAILED 10 |

10 bài Wikisource được coi là **ứng viên**; page tag PD và bộ lọc regex không thay thế thẩm định quyền phiên bản/bản dịch và PII độc lập.

## 2. Nguyên nhân kỹ thuật Wikipedia HOLD 70/70

Code Python V1 nguồn băm `9da5b25f2b8b45a62f1f88d7e6142e4cfa9d9b3b69caa513f16361c0b35bdb5b` xác định site CC bằng điều kiện chuỗi `'creativecommons' / 'cc by-sa' / 'ghi công'`; metadata thực tế ghi `Creative Commons Attribution-Share Alike 4.0` và URL `https://creativecommons.org/licenses/by-sa/4.0/deed.vi`. Chuỗi hiển thị có dấu cách trong `Creative Commons`, khiến điều kiện fail cho toàn bộ bài. **Đây là lỗi phát hiện giấy phép**, không chứng minh 70 bài vi phạm hay chưa đủ quyền.

Wikimedia và CC BY-SA cho phép nhiều hình thức sử dụng có điều kiện: ghi công, chỉ rõ thay đổi và chia sẻ tương tự nếu áp dụng khi phân phối. Phải kiểm từng bài về ngoại lệ/đoạn bên thứ ba và quyền riêng tư. Không chuyển `RIGHTS_UNCLEAR` sang `ALLOW` hồi tố.

- https://foundation.wikimedia.org/wiki/Terms_of_Use
- https://www.mediawiki.org/wiki/Wikimedia_APIs/Content_reuse
- https://creativecommons.org/licenses/by-sa/4.0/

## 3. Kế nhiệm tối thiểu V3 — không làm lại snapshot 100 nguồn

Từ chính 100 URL và source revision **đã cố định** trong V2, chọn 30 bài Wikipedia không bị bộ lọc PII cũ gắn cờ, trải đều địa lý, lịch sử, văn hóa, khoa học, công nghệ và đời sống. Mã ID đã đóng băng: `WP006, WP008, WP011, WP012, WP016, WP017, WP021, WP022, WP023, WP025, WP027, WP029, WP031, WP032, WP033, WP035, WP036, WP037, WP042, WP043, WP044, WP048, WP049, WP053, WP054, WP061, WP062, WP063, WP068, WP070`. Danh sách JSON đính kèm `TTM_P01_F1_VI_GENERAL_WP30_PINNED_SELECTION_V3.json`, SHA-256 `d28d88d82750ac85568cc994c58b1690b72862b17ef0ee4148bbeb3a1b5c7084`.

V3 sẽ:
1. Kiểm SHA-256 biên bản V2 và nguyên trạng 10 cặp tệp Wikisource.
2. Xác minh tên giấy phép chính xác **kèm URL CC BY-SA 4.0** của site; vẫn ghi HOLD ngoại lệ từng trang.
3. Chỉ gọi API theo `oldid` từng bài trong 30 bài đã khóa; so sánh cả SHA-256 HTML nguồn và SHA-256 văn bản dẫn xuất với biên bản V2. Nội dung khác mã băm ⇒ HOLD, không chấp nhận lặng lẽ.
4. Sàng lọc lại PII trên byte trích xuất; chỉ lưu bài qua điều kiện kỹ thuật vào quarantine **mới**, không sửa 10 tài liệu ban đầu.
5. Đối chiếu H03 giữa tối đa 30 Wikipedia mới và 10 Wikisource cũ. Nếu >=30 nhóm chỉ ghi `PASS_CANDIDATE`, còn `F1_ADMISSION=HOLD_INDEPENDENT_RIGHTS_AND_PII_REVIEW`; chưa chia TEST, chưa E0.

**Source pins:**
- `TTM_P01_F1_VI_GENERAL_WP30_V3_PS51_ONE_SHOT.ps1`: `a46384850b0f8b0c0f28da1be32725613f5b5bbc2c66824e9423d416f1b478ec`
- `TTM_P01_F1_VI_GENERAL_WP30_PINNED_REVIEW_V3.py`: `e67c873c4f08b007945b5ed1bb3be70ca3329805e778ca46dc2fec392b4c6a4f`
- Bundle ZIP: `7d85e14f17d94860ffe2dcd9a4eacdfdaf6c28b5a93daa43f412b1c00f28b688`

Kiểm tra Python AST, byte bằng nhau của ba tệp nhúng, 30 ID nằm đúng nguồn cũ và các trường hợp giấy phép dương/âm: **PASS**. **Chưa chạy parser PowerShell 5.1 trên Windows hoặc V3 network**, không tuyên bố runtime PASS.

## 4. Phạm vi và đường găng

Chỉ sử dụng `D:\WORK\RESEARCH\TokenToModel-Lab`, marker và receipt V3 riêng, không dọn/xóa ngoài thư mục tạm sở hữu. Không thay đổi source gốc CQG/Wikimedia, không đưa văn bản gốc lên GitHub. F0 10/10, K1/K2, S1 FAIL và `lineage.md` giữ nguyên; không merge main, không huấn luyện.

`F1=HOLD` · `E0=NOT_EXECUTED` · `P01=OPEN` · `P02=NOT_OPENED`.

**Bước kế tiếp:** chạy đúng một lượt V3 trên Windows, đối chiếu receipt. Khi đủ 30 nhóm từ nội dung byte đã xác minh, thẩm định quyền/PII **một gói** và khóa snapshot/split; sau đó một gói QA Docker an toàn, mới mở E0 TRAIN-only.
