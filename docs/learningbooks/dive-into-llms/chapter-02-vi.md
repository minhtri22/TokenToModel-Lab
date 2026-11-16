# Chương 02: Prompting và chuỗi suy luận

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 2](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter2) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Mức liên quan:** TTM · **Trạng thái:** `VI_STUDY_GUIDE_AUTHORED / SOURCE_NOTE_ONLY / NO_SCIENCE`

## Bài học cốt lõi
Prompting là cách đóng gói yêu cầu tại thời điểm suy luận; nó không đồng nhất với học tham số. Zero-shot chỉ mô tả nhiệm vụ, few-shot thêm ví dụ trong ngữ cảnh. Chain-of-Thought (CoT) yêu cầu biểu diễn các bước trung gian. Một thay đổi prompt có thể tăng điểm đo mà không chứng minh mạng đã học một cơ chế suy luận mới.

Phân biệt bốn yếu tố: độ khó nhiệm vụ, template prompt, chiến lược decoding và kiến thức/khả năng vốn có của checkpoint. Nếu thay đổi nhiều yếu tố cùng lúc, sẽ không xác định được nguyên nhân của khác biệt.

## Thiết kế đối chứng trên giấy
Đặt hai nhóm prompt cùng thông tin, cùng giới hạn token, cùng tiêu chí chấm:
- A: chỉ yêu cầu đáp án.
- B: yêu cầu giải thích từng bước và đáp án.
So sánh không được dùng length advantage một cách vô thức; cần ghi ngân sách token đầu vào và đầu ra. Ngoài accuracy, nên có chỉ số answer-format và lỗi không tuân thủ yêu cầu. Nếu chấm reasoning theo văn bản do chính mô hình tạo, scorer cần tránh thưởng cho lời giải dài nhưng sai.

Self-consistency (nhiều mẫu và bỏ phiếu) tăng chi phí lấy mẫu; phải đưa toàn bộ số forward hoặc token sinh vào ngân sách. Không được so một lượt greedy với nhiều lượt sampling rồi kết luận architecture thắng.

## Phân tích shortcut
Mô hình có thể đoán bằng tín hiệu bề mặt. Đề xuất ba loại kiểm tra: đổi tên thực thể nhưng giữ logic, đảo thứ tự dữ kiện, và tạo cặp phản thực tế (counterfactual) cùng độ dài. Không dùng một ví dụ đơn lẻ để khẳng định tổng quát hóa.

## Ứng dụng với TTM/CLDP
**TTM:** phù hợp với câu hỏi liệu Small4M không tuân thủ prompt do template, dữ liệu, objective hay năng lực. Đầu ra chỉ để thiết kế đối chứng; gate P0-A hiện vẫn `CLOSED_HOLD_EVIDENCE_INSUFFICIENT`.
**CLDP:** phép tương tự là phân biệt giao thức yêu cầu với khả năng xử lý trạng thái; không biến CoT thành benchmark chứng minh compositional intelligence.

## Tự kiểm tra
1. Zero-shot khác few-shot ở đâu?
2. Vì sao CoT dài hơn chưa chắc reasoning tốt hơn?
3. Chi phí của self-consistency nên quy về đơn vị nào?
4. Làm sao kiểm tra hiệu ứng do template chứ không do dữ liệu?

## Ranh giới
Không gọi API, không tạo prompt TEST mới và không công bố điểm so sánh khoa học từ bài tập.
