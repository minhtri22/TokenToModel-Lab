> **Ranh giới:** Đây là ghi chú học thuật do trợ lý tổng hợp từ chủ đề của giáo trình nguồn; chưa phải dịch toàn văn, không được dùng làm nguồn chứng minh năng lực hoặc thành công của bất kỳ dự án nghiên cứu nào.

# Ghi chú học tập — Chương 01: Tinh chỉnh và triển khai mô hình

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 1](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter1) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Phân loại:** Ghi chú kiến thức học tập độc lập, không suy diễn từ nghiên cứu đang tiến hành · **Trạng thái:** `STUDY_NOTES_ONLY / NOT_FULL_TRANSLATION / NOT_SCIENCE`

## Bài học cốt lõi
Một hệ thống dùng mô hình ngôn ngữ có tối thiểu năm phần khác nhau: nguồn dữ liệu, bộ chuyển thành token, mô hình, thuật toán tối ưu và giao thức đánh giá. Khi huấn luyện hoặc tinh chỉnh (fine-tuning), kết quả chịu tác động đồng thời của tất cả các phần này. Không nên suy luận “kiến trúc tốt hơn” chỉ vì một cấu hình được huấn luyện lâu hơn hoặc được cấp dữ liệu dễ hơn.

Phân biệt tiền huấn luyện (pretraining) — học phân bố chuỗi từ lượng văn bản lớn — với tinh chỉnh có giám sát (supervised fine-tuning, SFT), thường huấn luyện trên các cặp chỉ dẫn–phản hồi. Một demo suy luận chạy được không chứng minh cải thiện năng lực. Chỉ số loss giảm trên tập TRAIN cũng không chứng minh chuyển giao trên các trường hợp TEST chưa từng thấy.

## Mô hình hóa pipeline
Một lượt hợp lệ cần chốt thứ tự: dữ liệu gốc → lọc nguồn/rights → chia nhóm không chồng lặp → chuẩn hóa → tokenizer → batch → forward → loss → update → đánh giá đã khóa. Các bước lọc và chuẩn hóa phải lưu provenance; nếu làm trước khi chia nhóm một cách không kiểm soát có thể gây rò rỉ TRAIN/TEST.

Loss token dự đoán tiếp theo thường có dạng:
`L = - (1/N) Σ_i log p_θ(y_i | x_<i)`.
Cần xác định token bị mask, padding và cách cộng mẫu số N trước khi so sánh. Hai con số “loss” tính trên cách mask khác nhau không có giá trị đối chứng trực tiếp.

## Ví dụ tự học, không chạy mô hình
Tạo một bảng gồm các cột `item_id`, `source_id`, `group_id`, `split`, `license_status`, `token_count`, `mask_policy`. Viết bằng lời ba trường hợp mà một hàng dữ liệu không được vào tập đánh giá: thiếu quyền dùng, trùng nhóm với TRAIN, và sai cấu trúc nhãn. Đây là bài tập phân tích hồ sơ, không tạo dữ liệu hay gold thực nghiệm.

## Câu hỏi tự kiểm tra
1. Vì sao TRAIN loss giảm nhưng TEST không đổi?
2. Thế nào là rò dữ liệu theo `group_id`?
3. Nếu chỉ thay tokenizer, điều kiện nào phải giữ cố định?
4. Đầu ra demo có phải chứng cứ science PASS không?

## Điều kiện dừng
Không khởi chạy notebook upstream, không tự cấp nguồn dữ liệu, không ghi kết quả vào `lineage.md` khi mới hoàn thành bài tập lý thuyết.
