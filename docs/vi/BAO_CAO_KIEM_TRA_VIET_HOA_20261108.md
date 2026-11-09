# Báo cáo rà soát và chuẩn hóa ngôn ngữ tài liệu TTM — 08/11/2026

## 1. Phạm vi và nguyên tắc

- Kho nguồn: `minhtri22/TokenToModel-Lab`; nhánh `research/ttm-small-4m-colab-pilot-prereg-20261108`, PR #12 là bản nháp (Draft).
- Đã kiểm kê **57 tài liệu Markdown có nội dung diễn giải** trên nhánh nghiên cứu và nhánh `main`: **42 tài liệu có nội dung chính đã là tiếng Việt** và **15 tài liệu cần bản tiếng Việt chuẩn hóa riêng**. Trong 15 bản bổ sung gồm 11 hồ sơ thử nghiệm tích hợp (Pilot), 2 hồ sơ P00 và 2 tệp hướng dẫn gói mã.
- Nguyên tắc ngôn ngữ: **tiếng Việt trước, thuật ngữ chuyên ngành tiếng Anh trong ngoặc đơn**, ví dụ *tiền đăng ký thực nghiệm (Preregistration)*, *điểm lưu mô hình (Checkpoint)* và *tương đương số học (Numerical Parity)*. Với tên sản phẩm/thư viện, tên lệnh, tên tệp, trường JSON, mã trạng thái máy, SHA và commit, **giữ nguyên đúng ký tự**.
- **Không dịch ngược bằng chứng bất biến:** mã nguồn Python/PowerShell, notebook `.ipynb`, cấu hình JSON, dữ liệu, biên bản `evidence/`, log, ảnh SVG/PNG và `lineage.md` giữ nguyên. Không chuyển đổi thầm bất kỳ hồ sơ lịch sử `FAIL`/`STOP` hoặc `NOT_EXECUTED` thành `PASS` do kết quả mới.
- Bản dịch được đặt riêng tại `docs/vi/` và có đường dẫn tới hồ sơ nguyên bản; mục lục chính là `docs/vi/README.md`. Tài liệu đang dùng trên `main` đã chủ yếu viết tiếng Việt, nhưng vẫn có mã nhận dạng và nhãn kỹ thuật tiếng Anh cố ý giữ để dễ đối chiếu.

## 2. Kết quả chỉnh sửa

| Nhóm | Số tài liệu | Xử lý |
|---|---:|---|
| Đã có diễn giải chính bằng tiếng Việt | 42 | Rà soát và đưa vào mục lục; không sửa lại hồ sơ khoa học hoặc lịch sử chỉ vì ngôn ngữ |
| Hồ sơ pilot T1–T3/T4 | 11 | Tạo bản tiếng Việt riêng tại `docs/vi/pilot/` |
| Hồ sơ P00 lịch sử bằng tiếng Anh | 2 | Tạo bản tiếng Việt riêng tại `docs/vi/qa/` và `docs/vi/experiments/` |
| Hướng dẫn mã T1/T2 có thuật ngữ lẫn tiếng Anh | 2 | Tạo bản tiếng Việt riêng tại `docs/vi/tools/` |
| **Tổng** | **57** | **15 bản dịch bổ sung**, **42 tài liệu đã có tiếng Việt làm ngôn ngữ chính** |

Ngoài các bản dịch, đã cập nhật liên kết tới mục lục trong `README.md` và mở rộng `docs/TERMINOLOGY_VI.md` bằng từ điển thuật ngữ cho T1–T4. Không chỉnh sửa cấu trúc P00–P12 hoặc các hợp đồng thí nghiệm đã đăng ký.

## 3. Kiểm tra độc lập ở mức nội dung và liên kết

- **15/15 bản dịch** đã được tạo, đọc lại từ GitHub và xác nhận nội dung khớp chính xác với nội dung đã phát hành.
- Đối chiếu chuỗi mã băm SHA-1/SHA-256 và các địa chỉ nguồn (URL) giữa 15 cặp hồ sơ: **không thiếu mã băm hay địa chỉ được trích dẫn**.
- Đối chiếu mã định danh trong hai hướng dẫn gói mã; sau sửa, **không thiếu tên tệp và các định danh đặt trong dấu mã (Backticks)** so với bản gốc. Những trường hợp vô tình chuyển đổi tên hàm hoặc mã trạng thái trong dự thảo đã được sửa trước khi đóng đợt.
- Mục lục đã kiểm tra có **15 dòng dẫn bản dịch** và **42 dòng dẫn tài liệu tiếng Việt gốc**. Liên kết nội bộ của **15 bản dịch** được kiểm tra theo đường dẫn tương đối, **không phát hiện liên kết sai** trong phạm vi được xác minh.
- Các thao tác chỉ thêm tài liệu, mục lục, từ điển và liên kết hướng dẫn trên nhánh PR #12. **`main`, `lineage.md`, mã nguồn, kết quả QA và mô hình không thay đổi.**

## 4. Giới hạn phán quyết

- Đây là **kiểm tra thống nhất ngôn ngữ tài liệu**, không phải kiểm định lại các kết quả khoa học, mã nguồn hoặc chất lượng mô hình.
- Việc giữ nguyên tên máy, mã trạng thái và thuật ngữ trong tên lớp/hàm là **ngoại lệ cần thiết**, không phải đoạn văn tiếng Anh chưa dịch.
- **42 tài liệu đã có tiếng Việt** được rà soát và lập mục lục, không tạo bản sao vô ích. Không tuyên bố đã chỉnh từng chữ tiếng Anh nằm trong tên mã, log hoặc hình ảnh.
- **T1/T2/T3 đã đạt phạm vi kiểm thử kỹ thuật**, T4 vẫn `SCIENCE_LOCK=HOLD` và `T4_TRAIN=NOT_STARTED`. Báo cáo dịch thuật **không cấp quyền thực nghiệm T4**.
- Phán quyết chỉ phản ánh các tài liệu đã kiểm kê tại thời điểm rà soát; tài liệu phát sinh sau đó phải tuân theo `docs/TERMINOLOGY_VI.md`.

## 5. Cách sử dụng

Đọc [mục lục tài liệu tiếng Việt](README.md), bắt đầu từ [phán quyết hiện hành T1–T3 và khóa T4](pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md), sau đó tra [từ điển thuật ngữ dự án](../TERMINOLOGY_VI.md). Với mỗi hồ sơ cũ, kiểm tra liên kết **Nguồn** nếu cần đối chiếu kết quả tại thời điểm lập biên bản.

**Bước thực hiện tiếp theo:** tiếp tục tiền đăng ký khoa học tổng hợp T4 và một lượt thử năng lực GPU bằng dữ liệu tổng hợp; không làm lại kiểm thử T1–T3 đã khóa chỉ vì cập nhật ngôn ngữ.
