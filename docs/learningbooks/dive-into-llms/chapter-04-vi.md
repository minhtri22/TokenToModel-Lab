> **Ranh giới:** Đây là ghi chú học thuật do trợ lý tổng hợp từ chủ đề của giáo trình nguồn; chưa phải dịch toàn văn, không được dùng làm nguồn chứng minh năng lực hoặc thành công của bất kỳ dự án nghiên cứu nào.

# Ghi chú học tập — Chương 04: Suy luận toán học và chưng cất tri thức

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 4](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter4) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Phân loại:** Ghi chú kiến thức học tập độc lập, không suy diễn từ nghiên cứu đang tiến hành · **Trạng thái:** `STUDY_NOTES_ONLY / NOT_FULL_TRANSLATION / NOT_SCIENCE`

## Bài học cốt lõi
Một quy trình dạy mô hình suy luận toán học có thể có teacher tạo lời giải, bộ lọc xác nhận, tập dữ liệu, SFT và đánh giá. Chưng cất (distillation) chuyển thông tin từ teacher sang student; nó không mặc định cho student sở hữu năng lực suy luận rộng như teacher. Một mẫu giải dài có thể chứa lỗi logic hoặc lời giải tự tin nhưng sai.

Cần tách ít nhất ba khả năng cạnh tranh:
1. Student học được quy tắc giải toán có thể chuyển giao.
2. Student học bề mặt văn bản/định dạng câu trả lời của teacher.
3. Student nhớ những dạng bài gần trùng với TRAIN.

## Công thức và định nghĩa
Accuracy trên tập câu hỏi chỉ có ý nghĩa nếu gold, cách khớp đáp án và mẫu số đã khóa. Với bài toán có nhiều cách viết đáp án, cần canonicalization (ví dụ phân số tối giản) được đăng ký trước. Không đổi metric sau khi xem dự đoán.

So sánh hai objective có thể viết:
`Δ = Accuracy(objective_B) - Accuracy(objective_A)`,
nhưng phải giữ `training_tokens`, `number_of_updates`, nguồn, checkpoint ban đầu và decoding ở mức so sánh công bằng. Nếu không giữ được tất cả, cần nêu confounder chứ không báo hiệu ứng nhân quả.

## Bài tập trên giấy
Chọn bài toán giả định “tính tổng các số chẵn đầu tiên”. Viết phương pháp sinh gold có thể kiểm tra bằng công thức độc lập với teacher. Liệt kê perturbations giữ đáp án như cũ và những perturbations đổi đáp án. Ghi rõ điều gì làm mẫu không hợp lệ.

## Khả năng tài nguyên
README nguồn nêu Qwen2.5-Math-1.5B, dữ liệu DeepMath-103K, yêu cầu GPU ít nhất 40 GB VRAM và khoảng 50 GB dung lượng. Đây là tài nguyên của ví dụ nguồn, không phải yêu cầu tải hoặc chạy trên thiết bị người học.

## Câu hỏi tự kiểm tra
1. Teacher giỏi có đảm bảo dữ liệu tốt không?
2. Vì sao kiểm định final answer cần nguồn gold độc lập?
3. Khi nào một so sánh SFT là không cân bằng?
4. Bao giờ nên STOP thay vì tăng model size?
