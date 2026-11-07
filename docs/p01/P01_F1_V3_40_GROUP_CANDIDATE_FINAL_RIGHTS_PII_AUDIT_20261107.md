# TTM P01 — V3 40 nhóm ứng viên: đối chứng SHA và thẩm định F1 tinh gọn
Ngày: 07/11/2026. Nhánh audit kế nhiệm, không sửa pha khoa học hay `main`.

## Bằng chứng V3
Đã đối chiếu SHA-256 tệp upload V3: `9fcdebbd53eb538d8f4a6743d7e2a0c9584b379bee50ce09a6b1b711e9c15db9`. Tệp JSON được copy **đúng byte** vào `artifacts/qa/p01/TTM_P01_F1_VI_GENERAL_WP30_REVIEW_V3_20261107.json`, Git blob `64b970615be7503a8141d8635699bf5a5a18a3ff`. Đã đọc lại folder Windows: 30 cặp WP V3, 10 cặp WS V2, cả hai biên bản và marker.

V3 ghi 30 WP đúng revision và SHA-256, 10 WS tiền nhiệm, tổng 40 nhóm theo thuật toán H03. Điều kiện >=30 nhóm đạt **PASS_CANDIDATE**. Chưa có `ALLOW` cho TRAIN hoặc snapshot đã phê duyệt.

## Đánh giá độc lập điều kiện quyền/PII
- Metadata Wikipedia khớp `Creative Commons Attribution-Share Alike 4.0` cùng URL giấy phép; phải kiểm tra ngoại lệ từng trang, ghi nguồn/revision và attribution. Giấy phép chung **không** tự chứng nhận nội dung riêng từng trang.
- Wikisource có nhãn `PVCC-cũ` nhưng cần xem bản in, bản dịch và thông tin người biên tập. Từ V2, ưu tiên rà soát `WS001` (tag 75%), `WS012` (tag 50%), `WS014` (bản dịch Wikisource) và `WS009` (ghi đè tác giả).
- Không nộp nội dung bản quyền hoặc PII lên GitHub; không được tự đánh dấu 40/40 `ALLOW` từ kết quả máy quét.

Nguồn công khai: https://foundation.wikimedia.org/wiki/Terms_of_Use ; https://www.mediawiki.org/wiki/Wikimedia_APIs/Content_reuse ; https://en.wikisource.org/wiki/Wikisource:Copyright_policy .

## Bộ kiểm tra độc lập — một gói, không mở cổng kỹ thuật vi mô
Đã chuẩn bị bản PowerShell `TTM_P01_F1_V3_INDEPENDENT_ADMISSION_AUDIT_PS51_V1.ps1` SHA-256 `12CC51D176080B7BF17AA9EB87FC64B6EF5E561523C51F6714DE86F8C0A72ED9`; Python nhúng SHA-256 `920BF8867E1D9CB45BE62B1849B66AB52E033A882DB9B0B7D994BF44517AE42F`. Python AST và tự kiểm thử ngoại tuyến PASS; **PS51 parse và chạy Windows chưa thực thi**.

Chỉ đọc chính xác 40 cặp raw/derived, xác minh SHA-256 từ receipt V2+V3, kiểm metadata và regex PII/bản quyền, độc lập tính lại H03, sinh một biên bản metadata-only tại `evidence/p01/TTM_P01_F1_V3_INDEPENDENT_RIGHTS_PII_AUDIT_20261107.json`. Không tải thêm, không sửa nguồn, không chuyển sang `approved_sources`, không chia TRAIN/VALIDATION/TEST, không chạy BPE. Vẫn HOLD nếu chưa có xác nhận per-page rights + PII. Script chỉ đính kèm hội thoại, không commit mã chạy.

## Đường găng hữu hạn
1. Chạy một lượt bộ QA metadata-only đã pin; đọc lại đúng receipt.
2. Review thực chất chỉ các cờ PII, trường hợp third-party, trang văn bản/phần dịch còn vướng. Với tài liệu được chấp thuận, giữ evidence giấy phép và ghi công theo revision.
3. Nếu >=30 nhóm còn đủ sau quyền/PII, khóa snapshot và split H03 theo seed 20261105 với TEST sealed; một gói kiểm thử bảo vệ Docker Linux CPU; sau đó E0 TRAIN-only đúng một lượt theo science permit.
4. Nếu không đạt >=30 sau loại trừ, ghi gap, không phục hồi nguồn bị loại bằng thay đổi ngưỡng/seed tùy tiện.

Giữ P00–P12, F0, K1/K2 PASS, S1 FAIL, các marker, `lineage.md` append-only; `P01=OPEN`, `P02=NOT_OPENED` và `E0=NOT_EXECUTED`.
