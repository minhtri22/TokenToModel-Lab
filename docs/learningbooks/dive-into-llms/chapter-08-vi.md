# Chương 08: Kiến trúc ngôn ngữ đa phương thức

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 8](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter8) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Mức liên quan:** TTM · **Trạng thái:** `VI_STUDY_GUIDE_AUTHORED / SOURCE_NOTE_ONLY / NO_SCIENCE`

## Bài học cốt lõi
Multimodal LLM (MLLM) xử lý hơn một loại tín hiệu: chữ, hình, âm thanh, video. Một thiết kế thường gồm bộ mã hóa chuyên biệt (encoder), phép chiếu sang không gian biểu diễn chung (projection/adapter), lõi suy luận và bộ giải mã theo từng modality. Việc cùng chạy trong một hệ thống chưa chứng minh các biểu diễn đã căn chỉnh (aligned).

Hai phương án kiến trúc dễ nhầm:
- Early fusion: ghép thông tin trước hoặc trong lõi chung.
- Late fusion: kết hợp dự đoán/biểu diễn sau khi xử lý từng nhánh.
Sự khác biệt ảnh hưởng tới độ trễ, chi phí và khả năng đối chứng phân biệt nguồn lỗi.

## Tách câu hỏi khoa học
1. Kỹ năng một modality có chuyển sang modality khác không?
2. Adapter có làm mất thông tin cần thiết của nguồn?
3. Lỗi do encoder, projection, core model hay decoder?
4. Baseline chỉ dùng văn bản có cùng lượng thông tin hữu dụng hay không?

Một kết quả tốt khi ghép thêm hình ảnh có thể chỉ do cung cấp thêm dữ liệu, không phải do cơ chế fusion tốt hơn. Muốn kết luận cần ngân sách thông tin và truy cập được khống chế.

## Ví dụ tự học
Giả định ta có bản mô tả đối tượng và một vector ảnh. Đề xuất ba đối chứng: text-only, vector-only, text+vector. Viết điều kiện để nguồn text không chứa câu trả lời ở một nhóm nhưng vector có chứa, và điều kiện ngược lại. Sau đó đặt ngưỡng chi phí trước khi nhìn đầu ra.

## Liên hệ TTM/CLDP
**TTM:** bổ trợ cho hướng EmbeddingGemma2/Gemini Embedding2 — so sánh adapter/cross-attention với text retrieval under equal information budget. Hiện vẫn thiết kế riêng, không tự cấp science.
**CLDP:** không được suy từ module visual alignment sang state representation của Layered Blackboard; chỉ mượn nguyên lý kiểm soát thông tin đầu vào.

## Câu hỏi
1. Đâu là baseline công bằng?
2. Vì sao không thể dùng số chiều vector để làm đại diện đầy đủ cho lượng thông tin?
3. Khi nào nên HOLD vì provenance của embedding?
4. Có cần pretrained decoder mới để kiểm tra giả thuyết hiện tại không?

## Ranh giới
Không tải NExT-GPT hoặc model đa phương thức; không đổi objective hay kiến trúc TTM trong nhánh tài liệu.
