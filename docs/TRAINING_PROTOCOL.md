# Quy trình huấn luyện mô hình từ đầu đến cuối (End-to-end Training)

Đây là kế hoạch cho các giai đoạn sau P00, **không phải báo cáo rằng mô hình P00 đã được huấn luyện thành công**.

## T0 — Kiểm tra khả năng học trên dữ liệu rất nhỏ

- Sử dụng bộ dữ liệu thử nhỏ có nguồn hợp pháp; bộ từ vựng byte (Byte-level Vocabulary) dùng để tránh phụ thuộc tokenizer ở bước đầu.
- Huấn luyện có chủ đích trên một lô rất nhỏ (Micro-batch Overfitting) để kiểm tra hàm mất mát có giảm, gradient hữu hạn và trọng số được cập nhật.
- Ghi hạt giống ngẫu nhiên (Seed), cấu hình, commit, dữ liệu và kết quả theo từng bước.
- Không dùng kết quả T0 để tuyên bố mô hình hiểu ngôn ngữ.

## T1 — Dữ liệu và bộ tách token

- Xác minh nguồn, giấy phép, quyền sử dụng; loại trùng (Deduplication), chuẩn hóa Unicode, kiểm soát dữ liệu cá nhân (PII).
- Chia độc lập tập huấn luyện, kiểm định và kiểm thử (Train/Validation/Test), kiểm tra rò rỉ dữ liệu (Data Leakage) giữa các tập.
- Huấn luyện bộ tách token (Tokenizer), khóa bộ từ vựng, bước chuẩn hóa và token đặc biệt; lưu SHA-256 của dữ liệu và sản phẩm.

## T2 — Huấn luyện mô hình đối chứng

- Ghim số lớp, số chiều, số đầu chú ý, cửa sổ ngữ cảnh, loại số học (Precision), bộ tối ưu (Optimizer), lịch tốc độ học (Learning Rate Schedule), cỡ lô, tích lũy gradient và ngân sách token.
- Theo dõi mất mát huấn luyện (Training Loss), mất mát kiểm định (Validation Loss), chuẩn gradient (Gradient Norm), thời gian, RAM/GPU và dữ liệu đã đi qua.
- Dùng cắt gradient (Gradient Clipping), điểm lưu (Checkpoint) nguyên tử và kiểm tra khả năng tiếp tục đúng (Resume Parity).
- Tách sai lỗi kỹ thuật khỏi kết quả khoa học.

## T3 — Thay đổi quy mô và thử nghiệm loại trừ

- Mỗi biến thể số lớp, kích thước ngữ cảnh, Attention, mã hóa vị trí quay (RoPE) hoặc chú ý nhóm truy vấn (GQA) trên nhánh riêng.
- So sánh A/B với cùng dữ liệu, cùng điều kiện tương ứng và ngân sách tính toán được ghi rõ.
- Báo cáo chất lượng trên dữ liệu giữ riêng (Held-out Evaluation), thời gian và chi phí; không đánh giá chỉ dựa trên Training Loss.

## T4 — Tinh chỉnh sau huấn luyện

- Khi cần trợ lý hội thoại, nghiên cứu tinh chỉnh theo hướng dẫn (Supervised Fine-Tuning) hoặc căn chỉnh hành vi (Alignment) phù hợp mục tiêu.
- Ghi nguồn dữ liệu, kiểm thử hành vi và bảo mật (Safety/Security), đồng thời đánh giá hồi quy (Regression).

## T5 — Đánh giá phát hành

- Chuẩn bị thẻ mô hình (Model Card), thẻ dữ liệu (Dataset Card), thông tin giấy phép trọng số (Weight License), thử nghiệm suy luận, hướng dẫn tái lập và báo cáo chất lượng.
- Chỉ xem xét thương mại hóa sau đánh giá riêng quyền sử dụng, quyền riêng tư, bảo mật, chất lượng và chi phí.

## Quy tắc thực nghiệm bắt buộc

Không dùng dữ liệu kiểm thử cuối (TEST) để điều chỉnh siêu tham số (Hyperparameters). Không tự chạy lại hạt giống đã khóa nếu giao thức không cho phép. Giữ mọi kết quả PASS, FAIL và chưa đủ kết luận trong các biên bản bất biến và `lineage.md`.

Xem `docs/COMPARISON_PROTOCOL.md` để hiểu ý nghĩa từng phép đo và `docs/qa/P00_POST_MERGE_AUDIT_20261105.md` để biết giới hạn P00.
