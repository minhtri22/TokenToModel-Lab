# TTM-Small-4M × EmbeddingGemma 2 — Phản biện đối kháng thiết kế xác nhận 2.048 bước

**Ngày:** 09/11/2026. **Phạm vi:** phân tích tĩnh (desk review), không phải kiểm định thực nghiệm độc lập của bên thứ ba; không đào tạo, không đánh giá checkpoint, không kiểm tra dữ liệu thực.

**Tài liệu được phản biện:** docs/pilot/TTM_SMALL4M_EMBEDDINGGEMMA2_2048_POST_ADJUDICATION_STOP_GO_AND_CONFIRMATORY_DESIGN_ONLY_20261109.md

## 1. Đánh giá hai phương án

| Phương án | Thông tin mới tối đa | GPU mới | Quyết định |
|---|---|---:|---|
| Chấm checkpoint A/B/C/D đã khóa trên nhóm truyện mới | Kiểm tra khả năng lặp ưu thế của C trên những truyện chưa dùng để lựa chọn | 0 | **GO_DESIGN_ONLY** |
| Huấn luyện ngay kiến trúc dư có cổng (residual/gated) | Đổi câu hỏi khoa học; chưa xác nhận tín hiệu direct-swap của C, thêm tham số/đối chứng | Chưa biết | **DEFER**; chỉ bảo toàn tài liệu cơ chế |
| Chạy thêm 1.024 bước hoặc đổi siêu tham số của C trên VAL cũ | Tăng nguy cơ chọn theo kết quả và không tạo đánh giá độc lập | >0 | **STOP** |

**Phản biện về thứ tự:** chưa có lý do khoa học để đốt thêm GPU nhằm sửa một tín hiệu có thể được kiểm tra bằng checkpoint đã có. Tuy vậy, phép chấm mới cũng không làm giảm nhu cầu seed độc lập nếu sau này muốn kết luận tính ổn định qua huấn luyện.

## 2. Những điểm có thể gây phán quyết sai

| Nguy cơ | Mức | Cách xử lý trước khi đánh giá |
|---|---|---|
| Dùng lại bất kỳ nhóm VAL/TEST đã xem | Chặn | Loại theo story hash/manifest, chỉ dùng membership của TEST, không mở raw TEST |
| Chọn ứng viên từ VALID gốc còn gần trùng với TRAIN | Chặn | Xác minh exact toàn TRAIN; mở rộng near-dup audit ngoài tập T1 pilot, công khai giới hạn recall |
| Nguồn bản mới không cùng revision và byte SHA | Chặn | Ghim đúng revision/tệp SHA hoặc tạo thiết kế mới trước khi xem dự đoán |
| Dùng nhiều cửa sổ từ cùng truyện như độc lập | Chặn | Tính tổng loss và nhãn mỗi truyện; bootstrap ghép cặp theo truyện |
| Chọn lại độ dài/số truyện sau khi nhìn NLL | Chặn | Cố định 320 truyện và ngưỡng 50.000 nhãn trước chấm, thiếu thì HOLD |
| Chạy code chấm cùng lỗi với code huấn luyện | Chặn | Bộ chấm độc lập, kiểm tra cấu trúc/fixture và SHA; không đổi source sau CLAIM |
| Báo PASS vì C chỉ thắng D | Chặn | Cần cả A−C, B−C, D−C có CI thấp >0 |
| Suy rộng từ một seed thành ưu thế pretrained donor | Nghiêm trọng | Giữ tên kết luận giới hạn fixed-checkpoint, yêu cầu nhiều seed/hypothesis riêng khi cần |

## 3. Ranh giới suy luận cần bảo vệ

- Một tập truyện mới từ **cùng tệp VALID nguyên bản** có thể là dữ liệu chưa dùng trong quá trình quyết định của chủ nghiên cứu; đây là kiểm tra **ngoài nhóm truyện đã dùng** (new-story holdout), không nhất thiết là thử nghiệm ngoài phân phối (out-of-distribution).
- Không có chứng cứ donor EmbeddingGemma 2 chưa từng thấy các truyện này trong pretraining. Không diễn giải PASS như chứng minh chống rò rỉ khỏi kho huấn luyện donor.
- Phân tích bootstrap giúp đánh giá biến thiên giữa **truyện trong tập mới**, nhưng không bắt được biến thiên giữa những lượt huấn luyện với seed khác.
- D khác C không chỉ ở thông tin ngữ nghĩa; ridge, cơ chế fallback, tham số và tác động huấn luyện có thể cùng ảnh hưởng. Đối chứng D là điều kiện cần hữu ích, không phải chứng minh nhân quả đủ.
- Tập nguồn có giấy phép CDLA-Sharing-1.0, nhưng vẫn cần rà soát nghĩa vụ xuất bản và quyền riêng tư; không đưa raw data hoặc dữ liệu riêng tư theo truyện vào GitHub công khai.

## 4. Kiểm định hợp đồng ở giai đoạn thiết kế

| Điều kiện | Trạng thái |
|---|---|
| Đối chiếu L0015/L0016, bốn SHA checkpoint | PASS_SOURCE_READBACK |
| Chọn thứ tự ưu tiên quyết định STOP/GO | PASS_DESIGN_REVIEW |
| Quy tắc đối chứng và ngưỡng PASS/FAIL được đề xuất trước kết quả | PASS_DESIGN_REVIEW |
| Đã tạo tập 320 truyện chưa dùng | NOT_EXECUTED |
| Đã kiểm đủ chống trùng, nguồn và quyền cho tập mới | HOLD |
| Bộ đánh giá độc lập đủ điều kiện và SHA nguồn | NOT_EXECUTED |
| Đã tính kết quả khoa học trên tập mới | NOT_EXECUTED |
| Thí nghiệm GPU mới | NOT_AUTHORIZED |
| Ghi thêm kết quả vào lineage.md | NO_DESIGN_ONLY |

**Kết luận phản biện:** PASS_DESIGN_WITH_SOURCE_DATA_HOLD. **Không cho phép đánh giá thực** cho đến khi niêm phong nguồn và hợp đồng bộ chấm; ưu tiên duy trì lựa chọn CPU zero-GPU. Không giả nhận đây là chứng nhận độc lập thực nghiệm.

**Bước thực hiện tiếp theo:** TTM_SMALL4M_EMBEDDINGGEMMA2_NEW_HOLDOUT_SOURCE_RIGHTS_MEMBERSHIP_AND_EVALUATOR_CONTRACT_SEAL.
