> **Ranh giới:** Đây là ghi chú học thuật do trợ lý tổng hợp từ chủ đề của giáo trình nguồn; chưa phải dịch toàn văn, không được dùng làm nguồn chứng minh năng lực hoặc thành công của bất kỳ dự án nghiên cứu nào.

# Ghi chú học tập — Chương 03: Chỉnh sửa kiến thức và tính cục bộ

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 3](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter3) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Phân loại:** Ghi chú kiến thức học tập độc lập, không suy diễn từ nghiên cứu đang tiến hành · **Trạng thái:** `STUDY_NOTES_ONLY / NOT_FULL_TRANSLATION / NOT_SCIENCE`

## Bài học cốt lõi
Knowledge editing nghiên cứu cách sửa một thông tin hoặc hành vi trong mô hình mà không làm hỏng phần còn lại. Giá trị của chương không chỉ nằm ở thuật toán chỉnh tham số, mà còn ở cách phân biệt bốn thuộc tính của kết quả: reliability (đáp đúng mục tiêu đã sửa), generality (đúng dưới diễn đạt tương đương), locality (không làm đổi câu trả lời ngoài mục tiêu) và portability (khả năng kéo theo suy luận liên quan nếu được định nghĩa).

Một lần sửa có thể đạt reliability tuyệt đối trên prompt mục tiêu nhưng thất bại locality: những thông tin không liên quan bị thay đổi. Vì vậy, “đã chỉnh sửa thành công” là kết luận đa điều kiện, không phải một metric.

## Định nghĩa phép đo tự học
Với tập mục tiêu T, biến thể V và câu hỏi không đích U, có thể đặt:
- `R = số mục T đúng / |T|`
- `G = số biến thể V đúng / |V|`
- `L = số câu U giữ nguyên hành vi hợp lệ / |U|`

Không nên tính mẫu số khi tập chưa được kiểm kê, loại trừ và xác minh quyền. Không coi sự đồng thuận giữa các output sinh tự động là gold chuẩn. Các tập T/V/U phải được phân biệt từ trước khi nhìn kết quả can thiệp.

## Tình huống minh họa
Giả sử hệ thống cần cập nhật một quy tắc ưu tiên khi hai điều kiện cùng đúng. Kiểm tra tối thiểu: (i) đúng chính trường hợp mới, (ii) vẫn đúng các biến thể cách diễn đạt của trường hợp đó, (iii) không đổi hành vi ở các nhánh khác, (iv) giữ tính quyết định khi cùng một đầu vào được xử lý lặp lại. Chỉ là ví dụ giả lập trên giấy, không phải bằng chứng thực nghiệm.

## Bài tập
Tự lập ma trận ba trục R/G/L cho một quy tắc tổng hợp 2 trạng thái; viết ít nhất một negative control và một điều kiện phải HOLD khi thiếu mẫu số.

## Ranh giới
Chưa dùng EasyEdit, ROME hay MEND trên checkpoint của một nghiên cứu đang tiến hành. Đọc tài liệu về công cụ không phải giấy phép thay implementation.
