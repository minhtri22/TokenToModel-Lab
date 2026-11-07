# TTM — Quyết định thử nhanh mô hình P00 trên dữ liệu F1 Wikipedia

Ngày: 07/11/2026. Loại kết quả: **DEMO_ONLY / ENGINEERING FEEDBACK**, không phải thực nghiệm P01 E0, P02, P03 hoặc kết quả khoa học.

## Quyết định chủ dự án và điểm nghẽn được tháo

Chủ dự án yêu cầu bỏ các vòng xác nhận giấy phép Wikipedia theo từng trang không có rủi ro cụ thể, để **chạy và nhìn thấy mô hình hoạt động** sớm. Wikipedia tiếng Việt sử dụng chung giấy phép CC BY-SA 4.0 đối với phần lớn nội dung văn bản; bằng chứng nguồn hiện có là 30 revision pinned + URL lịch sử tác giả + SHA-256 từng tệp, kiểm tra độc lập 40 cặp raw/text, nhóm H03=40 và PII/copyright regex flag=0. Việc không có cờ tự động không chứng minh quyền của mọi nội dung trích dẫn bên thứ ba. Vẫn lưu ghi công, nguồn và các ngoại lệ phát hiện sau; **không** phân phối văn bản hoặc checkpoint công khai như sản phẩm thương mại trong demo này.

Đối với **demo nội bộ** thay vì tiếp nhận nguồn cho E0 chính thức, không đòi thêm một chuỗi 30 giấy phép riêng. Sử dụng tối đa 12 KiB từ mỗi trong 30 tài liệu Wikipedia đang cách ly, chỉ đọc, offline và không đi qua TRAIN/VALIDATION/TEST khoa học. Giữ 10 Wikisource ở HOLD riêng; không dùng tài liệu CQG-J3.

Nguồn chính sách:
- https://foundation.wikimedia.org/wiki/Terms_of_Use
- https://www.mediawiki.org/wiki/Wikimedia_APIs/Content_reuse
- https://creativecommons.org/licenses/by-sa/4.0/

## Có sẵn mã mô hình GPT

`reference/phase0/model.py`: PyTorch decoder-only GPT, 2 lớp Attention với causal mask, lớp Embedding và MLP. `reference/phase0/train.py` đã có vòng huấn luyện CPU. Vì vậy hướng nhanh nhất là sử dụng đúng `reference/phase0/model.py` đã khóa cho một demo huấn luyện và sinh byte, **không xây kiến trúc mới hoặc mở P02/P03**. Demo sử dụng byte vocab=256 (P00), **không được gọi là E0 BPE tokenizer hay mô hình đã học tiếng Việt đầy đủ**.

## Một lệnh chạy từ Downloads

Tệp đính kèm cuộc hội thoại:
`TTM_P00_F1_WP30_QUICK_GPT_DEMO_PS51_V1.ps1`, SHA-256 `E7F6C5F0B23CCAD87EBC9FE40CD4BB574838659D147F36AC9E1EE896DC97F50D`.
Python nhúng: `TTM_P00_F1_WP30_QUICK_GPT_DEMO_V1.py`, SHA-256 `324A6AE460E42AD64A75FD7FAC2CA3761CF6DEE3D55316ED7EC152C61D84E827`.

- Tiền kiểm fail-closed: Git origin và mã Git blob P00, Python/PyTorch có sẵn, hai receipt SHA khóa, 30 tài liệu Wikipedia TXT SHA khóa, 30 group IDs độc lập.
- Runtime: CPU 4 threads, 36 bước huấn luyện GPT PyTorch thực, byte vocab 256, đầu vào tối đa 400 KiB, kết quả `loss_before`, `loss_after`, mẫu sinh byte, checkpoint.
- Không cài hoặc tải package, không truy cập mạng, không sửa file dataset hoặc tracked Git. Lưu riêng tại `D:\WORK\RESEARCH\TokenToModel-Lab\demos\TTM_P00_F1_WP30_QUICK_GPT_DEMO_V1_20261107`; marker một lượt tại `evidence/p01`. Tạm ở `tmp` và chỉ xóa thư mục tạm do chính script tạo.
- Chạy thử trên môi trường tác giả với dữ liệu **tổng hợp**, PyTorch 2.10.0 CPU: preflight PASS, 36 steps hoàn thành, checkpoint/sample/report tạo được, loss fixed batch giảm; **không phải chạy trên máy Windows người dùng, chưa đủ tuyên bố demo công việc hoàn tất**.
- Không cấp phép E0/TOKENIZER BPE khoa học, không sửa F0 K1 K2 S1 FAIL, `lineage.md` hoặc trạng thái P01–P12.

## Bước tiếp theo

1. Kiểm SHA PowerShell và chạy một lượt trên Windows, nhận `demo_report.json`, `sample.txt`, checkpoint.
2. Dùng phản hồi thực tế để xem mô hình P00 hoạt động, rồi chốt P01 nguồn/hợp đồng E0 đủ điều kiện và chuyển P02/03 theo lộ trình. Không cần làm thêm 30 hồ sơ riêng.
