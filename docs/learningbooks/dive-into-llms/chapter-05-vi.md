> **Ranh giới:** Đây là ghi chú học thuật do trợ lý tổng hợp từ chủ đề của giáo trình nguồn; chưa phải dịch toàn văn, không được dùng làm nguồn chứng minh năng lực hoặc thành công của bất kỳ dự án nghiên cứu nào.

# Ghi chú học tập — Chương 05: Thủy vân đầu ra mô hình

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 5](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter5) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Phân loại:** Ghi chú kiến thức học tập độc lập, không suy diễn từ nghiên cứu đang tiến hành · **Trạng thái:** `STUDY_NOTES_ONLY / NOT_FULL_TRANSLATION / NOT_SCIENCE`

## Bài học cốt lõi
Thủy vân văn bản (text watermark) thêm một tín hiệu thống kê vào quá trình chọn token để về sau có thể đánh giá nguồn gốc của văn bản. Một phương pháp watermark có thể làm đổi phân bố xác suất sinh; vì thế đánh giá cần nhìn cả khả năng phát hiện, chất lượng văn bản và độ bền trước biến đổi.

Bộ từ vựng có thể được chia theo một hàm phụ thuộc ngữ cảnh thành tập ưu tiên và tập còn lại. Decoding được điều chỉnh để một tập được chọn thường xuyên hơn. Bộ phát hiện dùng thống kê tổng hợp thay vì tìm một chuỗi ký tự cố định.

## Hiểu metric
- True positive rate (TPR): số văn bản có watermark nhận diện đúng chia số văn bản có watermark.
- False positive rate (FPR): số văn bản sạch bị nhận nhầm chia số văn bản sạch.
- AUC: khả năng xếp hạng tương đối qua các ngưỡng; AUC cao không tự đảm bảo FPR đủ thấp cho một ứng dụng thực.
- Robustness: khả năng phát hiện sau biên tập/paraphrase/translation; cần ghi mức sửa và phương pháp sửa.

Ví dụ: nếu không đặt rõ FPR tối đa, một detector đơn giản báo “có watermark” cho mọi văn bản sẽ có TPR 100% nhưng vô dụng.

## Bài tập không thực thi
Đưa ra bảng nhầm lẫn 2×2 với số liệu giả định: TP=80, FN=20, FP=4, TN=96. Tính TPR=0.80 và FPR=0.04 bằng tay. Sau đó giải thích tại sao không thể lấy bảng giả định này làm evidence.

## Kiểm tra độ tin cậy
Một thuật toán watermark phụ thuộc tokenizer, model, decoding, distribution shift và chính sách truy cập. Không suy diễn khả năng truy xuất người tạo hoặc đảm bảo bản quyền từ một kết quả đo watermark.

## Ranh giới
Không triển khai detector, không thay logits của bất kỳ mô hình đang nghiên cứu nào, không dùng dữ liệu người thật và không kích hoạt API.
