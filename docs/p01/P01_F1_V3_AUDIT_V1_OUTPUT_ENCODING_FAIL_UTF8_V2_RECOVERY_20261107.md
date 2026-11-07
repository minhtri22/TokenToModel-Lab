# TTM P01 F1 — Kiểm toán độc lập V1: lỗi cp1252 và sửa UTF-8 V2

Ngày 07/11/2026. Đây là **hồ sơ kỹ thuật**, không phải phán quyết khoa học hay giấy phép mở E0.

## Lỗi V1 có bằng chứng

Người dùng đã chạy `TTM_P01_F1_V3_INDEPENDENT_ADMISSION_AUDIT_PS51_V1.ps1`. Python dùng `miniforge3`, trace tới `encodings/cp1252.py`, từ chối khi in ký tự tiếng Việt `\u1ed9` tại `print(json.dumps(audit(...), ensure_ascii=False, indent=2))`. Lỗi nằm ở **xuất báo cáo JSON qua redirected stdout**, sau khi hàm tính toán trả kết quả; không có căn cứ công nhận bộ kiểm toán V1 đã PASS.

Đọc lại Windows: biên bản audit V1 không tồn tại, thư mục tạm V1 đã được dọn; snapshot V2/V3, 30 cặp Wikipedia và 10 cặp Wikisource còn nguyên. Không huấn luyện hay chia TEST.

## Sửa host encoding giới hạn ở V2

Tệp V2 (đính kèm hội thoại, không sửa source code GitHub): `TTM_P01_F1_V3_INDEPENDENT_AUDIT_UTF8_RECOVERY_V2_PS51.ps1`

- SHA-256 V2 PowerShell: `211E0B4E90273904A923ABB7FBE56EB38647094E7A9B8A304A1B02D6938938E7`.
- SHA-256 Python nhúng **không đổi**: `920BF8867E1D9CB45BE62B1849B66AB52E033A882DB9B0B7D994BF44517AE42F`; byte nội dung nhúng được đối chiếu đúng với V1.
- Đặt `PYTHONIOENCODING=utf-8:strict`, `PYTHONUTF8=1`, `ProcessStartInfo.StandardOutputEncoding=UTF8`, `StandardErrorEncoding=UTF8`; không dùng `chcp` toàn hệ thống, không sửa Python nguồn.
- Mỗi lượt có marker riêng dùng `FileMode.CreateNew`; thư mục tạm và biên bản V2 khác tên V1, không ghi đè. Lượt V2 chỉ chạy một lần sau khi SHA và PS5.1 parser PASS.
- Kiểm tra ngoại tuyến mô phỏng stdout `cp1252` cho kết quả lỗi đúng kiểu; chuyển `PYTHONIOENCODING=utf-8:strict` cho kết quả JSON UTF-8 PASS. Đây là kiểm thử riêng việc mã hóa; **không** phải PS5.1/Windows runtime PASS.

## Hợp đồng giữ nguyên

40 tài liệu và H03 đã khóa không tải lại; chỉ kiểm toán đọc nguồn và xuất metadata. Không sửa K1/K2, S1, P00 hoặc `lineage.md`. Không chia TRAIN/VALIDATION/TEST, không chạy E0, không tự cấp `F1=ALLOW`. Ngưỡng 30 nhóm giữ nguyên, nhưng quyền theo trang và PII là cổng cuối bắt buộc.

## Bước tiếp theo

`TTM_P01_F1_V3_INDEPENDENT_AUDIT_UTF8_V2_ONESHOT_AND_RIGHTS_PII_ADJUDICATION`: người dùng kiểm SHA và parser PS5.1, thực hiện một lượt V2, đọc lại receipt metadata-only. Sau QA độc lập, chỉ chốt những trang đủ quyền/PII và nhóm tối thiểu 30, rồi một QA tích hợp Docker trước E0.
