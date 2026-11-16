> **Ranh giới:** Đây là ghi chú học thuật do trợ lý tổng hợp từ chủ đề của giáo trình nguồn; chưa phải dịch toàn văn, không được dùng làm nguồn chứng minh năng lực hoặc thành công của bất kỳ dự án nghiên cứu nào.

# Ghi chú học tập — Chương 07: Giấu tin trong văn bản sinh

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 7](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter7) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Phân loại:** Ghi chú kiến thức học tập độc lập, không suy diễn từ nghiên cứu đang tiến hành · **Trạng thái:** `STUDY_NOTES_ONLY / NOT_FULL_TRANSLATION / NOT_SCIENCE`

## Bài học cốt lõi
Steganography (giấu tin) là việc che giấu sự tồn tại của thông điệp trong một vật mang trông bình thường. Trong mô hình ngôn ngữ, lựa chọn token có thể mang các bit phụ nếu người gửi và người nhận chia sẻ quy tắc mã hóa. Điều này khác với encryption: mã hóa làm nội dung khó đọc, còn giấu tin làm tín hiệu khó bị nhận ra.

Hai cách cơ bản là fixed-length coding (mỗi lựa chọn gắn một số bit cố định) và Huffman coding (mã có độ dài biến đổi). Chúng tạo trade-off giữa lượng thông tin nhúng, độ trôi phân bố văn bản và khả năng giải mã.

## Khung suy luận
Gọi `B` là số bit giấu và `T` là số token văn bản, tỷ lệ payload là `B/T` bit/token. Chỉ số này tự nó chưa nói gì về độ tự nhiên hoặc khả năng bị detector nhận ra. Mất một token có thể làm lệch đồng bộ khiến thông điệp giải mã sai; vì vậy độ bền sau biên tập là thuộc tính riêng cần đo.

## Tình huống minh họa
Một phương án giả định nhúng bit bằng lựa chọn giữa hai từ đồng nghĩa. Phân tích nguyên nhân thất bại nếu paraphrase đổi từ hoặc bộ từ vựng không chứa cặp hợp lệ. Không cần sinh văn bản thật để chứng minh thí nghiệm giả định có failure mode.

## Tự kiểm tra
1. Giấu tin và watermark giống/khác nhau ở đâu?
2. Payload tăng có thể giảm điều gì?
3. Vì sao cần so sánh với văn bản không nhúng?
4. Khi nào một detector có nhiều false positive?

## Ranh giới
Không triển khai kênh trao đổi bí mật hoặc truy xuất dữ liệu không được phép. Giáo trình chỉ phục vụ nhận biết cơ chế và rủi ro.
