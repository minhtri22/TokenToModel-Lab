> **Ranh giới:** Đây là ghi chú học thuật do trợ lý tổng hợp từ chủ đề của giáo trình nguồn; chưa phải dịch toàn văn, không được dùng làm nguồn chứng minh năng lực hoặc thành công của bất kỳ dự án nghiên cứu nào.

# Ghi chú học tập — Chương 06: Đánh giá chống vượt rào an toàn

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 6](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter6) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Phân loại:** Ghi chú kiến thức học tập độc lập, không suy diễn từ nghiên cứu đang tiến hành · **Trạng thái:** `STUDY_NOTES_ONLY / NOT_FULL_TRANSLATION / NOT_SCIENCE`

## Bài học cốt lõi
Jailbreak assessment nghiên cứu khả năng hệ thống có thể bị dẫn dắt rời khỏi chính sách hoặc yêu cầu an toàn. Khác với việc phát triển jailbreak tấn công hệ thống thực, bài học ở đây là cách thiết kế chu kỳ đánh giá có ranh giới rõ: chọn mẫu thử, biến đổi tình huống, lọc điều kiện, đánh giá và dừng.

Một hệ thống đánh giá an toàn cần tránh việc lấy nhãn của cùng mô hình đang bị kiểm tra làm chuẩn chân lý. Kết quả “không vi phạm trong một bộ prompt” cũng không chứng minh an toàn trong mọi bối cảnh.

## Phân loại phép thử
1. Đúng hành vi an toàn trong yêu cầu hợp lệ.
2. Từ chối đúng yêu cầu không hợp lệ.
3. Không từ chối quá mức đối với yêu cầu bình thường.
4. Giữ được quyết định qua đổi cách diễn đạt, ngôn ngữ hoặc cấu trúc ngữ cảnh.
5. Báo lỗi và giới hạn khi gặp bối cảnh không đủ thông tin.

Cần chốt policy, taxonomy lỗi và cách phân xử bất đồng giữa raters. Accuracy gộp có thể che giấu false refusal và unsafe compliance cùng một lúc.

## Bài tập an toàn
Tạo 6 thẻ tình huống không nhạy cảm, ví dụ: yêu cầu đưa thông tin cá nhân không có quyền chia sẻ, yêu cầu chỉnh dữ liệu nghiên cứu không có quyền owner, yêu cầu xem log chưa được xác thực. Tự xác định nhãn `ALLOW`, `DENY`, `ASK_FOR_AUTHORIZATION`; ghi chứng cứ chính sách thay vì trực giác.

## Điều kiện dừng
Không chạy chiến dịch tấn công, không đưa prompt độc hại hoặc secrets thật vào tài liệu, không suy rộng từ demo đến production safety. Toàn bộ phần này là giáo trình phòng vệ và kiểm toán.
