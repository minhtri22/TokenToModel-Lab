> **Ranh giới:** Đây là ghi chú học thuật do trợ lý tổng hợp từ chủ đề của giáo trình nguồn; chưa phải dịch toàn văn, không được dùng làm nguồn chứng minh năng lực hoặc thành công của bất kỳ dự án nghiên cứu nào.

# Ghi chú học tập — Chương 11: RLHF và tối ưu chính sách bằng PPO

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 11](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter11) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Phân loại:** Ghi chú kiến thức học tập độc lập, không suy diễn từ nghiên cứu đang tiến hành · **Trạng thái:** `STUDY_NOTES_ONLY / NOT_FULL_TRANSLATION / NOT_SCIENCE`

## Bài học cốt lõi
Reinforcement Learning from Human Feedback (RLHF) gồm ít nhất ba khối phải tách: thu thập preference/feedback, xây dựng tín hiệu reward, và tối ưu policy. PPO là một thuật toán RL dùng cập nhật có kiểm soát; thuật toán PPO không tự tạo ra gold đúng, không tự khắc phục dữ liệu preference sai lệch.

Reward model là xấp xỉ, không phải chân lý. Nếu tối ưu quá mạnh theo một proxy, model có thể khai thác điểm yếu của proxy (reward hacking). Cần theo dõi chất lượng thực, sự đa dạng và độ lệch khỏi policy đối chứng.

## Các đại lượng cần hiểu
Reward tổng thường gồm phần thưởng nhiệm vụ và penalty giữ policy gần reference:
`r_total = r_task - β * KL(policy || reference)`.
Đây là biểu diễn khái niệm; cách tính KL và phân bổ reward trên token tùy protocol. Đổi `β` đồng thời đổi mẫu, reward model và số lượt update sẽ làm mất khả năng nhận diện nguyên nhân.

PPO thường giới hạn mức thay đổi qua tỷ lệ xác suất action:
`ρ_t = π_new(a_t|s_t) / π_old(a_t|s_t)`.
Nhưng việc giới hạn cập nhật không đảm bảo policy an toàn hay đúng nhiệm vụ.

## Bài tập trên giấy
Một reward model cho điểm cao câu trả lời dài, bất kể đáp án. Xây dựng negative control gồm hai câu trả lời: đáp án đúng ngắn và đáp án sai dài. Hãy giải thích vì sao reward ranking có thể ngược accuracy và tại sao cần independent rater.

## Tự kiểm tra
1. Reward và gold có cùng vai trò không?
2. Vì sao KL penalty cần reference rõ ràng?
3. Điều gì khiến reward hacking khó thấy trong demo?
4. Khi nào nên chọn đánh giá tốt hơn thay cho huấn luyện thêm?

## Ranh giới
Không tải reward model/IMDB, không chạy PPO, không thay checkpoint hiện có và không dùng tutorial này làm bằng chứng owner GO.
