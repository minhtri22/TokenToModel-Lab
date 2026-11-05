# Quy tắc ghi nhận và so sánh cấu hình (Comparison Protocol)

## Mỗi cấu hình cần lưu gì?

Các trường máy đọc giữ nguyên tên kỹ thuật:

`config_id`, `config_sha256`, `git_sha`, `dataset_sha256`, `tokenizer_sha256`, `split_id`, `seed`, `dtype`, `device`, `backend`, `torch_version`, `n_layers`, `n_heads`, `n_kv_heads`, `d_model`, `context_length`, `block_size`, `batching`, `optimizer`, `lr_schedule`, `train_tokens`, `checkpoint_sha256`.

Chưa dùng trường nào phải ghi `not_applicable` hoặc giải thích rõ, không tự bịa giá trị. Một lần chạy (Run) phải có mã riêng, thời gian, nhánh, commit, bộ dữ liệu và mã băm để tái hiện.

## Bảng đo phải giải thích được cho người đọc

| Nhóm | Phép đo | Đo cái gì? | Hiểu kết quả ra sao? |
|---|---|---|---|
| Tính đúng | Sai lệch logits tối đa (Maximum Absolute Logit Error) | Độ chênh lệch lớn nhất giữa hai đường tính | Càng gần 0 càng khớp; phải so với ngưỡng định trước |
| Nhân quả | Số lần nhìn trước token (Causal Leak Count) | Token tương lai có ảnh hưởng vị trí trước không | 0 trong phạm vi đã thử là đạt; không khẳng định mọi trường hợp |
| Huấn luyện | Mất mát huấn luyện (Training Loss) | Mức sai giữa dự đoán và mục tiêu trên dữ liệu huấn luyện | Giảm thường là tốt, nhưng có thể ghi nhớ quá mức |
| Khả năng khái quát | Mất mát kiểm định (Validation Loss) | Mức sai trên dữ liệu không dùng cập nhật trọng số | Cần theo dõi cùng với train loss để phát hiện học quá mức |
| Ngôn ngữ | Độ bối rối (Perplexity) | Giá trị biến đổi từ mất mát token | Thấp hơn thường tốt khi cùng tokenizer/dữ liệu |
| Suy luận | Thời gian token đầu tiên (TTFT) | Độ trễ từ yêu cầu đến token đầu | Thấp hơn thường tốt nếu cùng tải |
| Suy luận | Thời gian mỗi token tiếp theo (TPOT) | Độ trễ sinh các token tiếp theo | Thấp hơn thường tốt nếu cùng tải |
| Thông lượng | Token mỗi giây (Tokens per Second) | Số token xử lý mỗi giây | Cao hơn thường tốt nếu cùng tải và phần cứng |
| Bộ nhớ | Đỉnh RAM/GPU (Peak RSS/GPU Memory) | Mức dùng bộ nhớ cực đại | Thấp hơn có lợi nếu chất lượng không giảm |
| Bộ nhớ phân trang | Tỷ lệ phân mảnh (Fragmentation Ratio) | Phần tài nguyên được cấp nhưng chưa dùng hiệu quả | Cần thống nhất công thức trước khi so sánh |
| Độ bền | Lỗi hết bộ nhớ (Out-of-Memory Count) | Số lần vượt khả năng cấp phát | Cần ghi cả ngữ cảnh lỗi và cách khôi phục |
| Chi phí | Thời gian thực và điện năng (Wall Time/Energy) | Tài nguyên thực dùng cho lần chạy | Chỉ so khi đo được trực tiếp và có điều kiện ngang bằng |

## Điều kiện so sánh công bằng

- Chất lượng: cùng dữ liệu kiểm định được giữ riêng (Held-out Dataset), cùng bộ tách token (Tokenizer) hoặc giải thích khác biệt, cùng tiêu chí.
- Tốc độ: cùng trọng số mô hình, số token đầu vào/đầu ra, độ đồng thời, loại số (dtype), thiết bị, trình điều khiển, chế độ khởi động nóng (Warm-up) và số lượt đo.
- Sai số: ghi cả chênh lệch tuyệt đối (Absolute Error) và tương đối (Relative Error), nêu ngưỡng trước khi chạy.
- Tài nguyên: ghi CPU, RAM, bộ nhớ GPU, phân mảnh, thời gian, số lần OOM và điện năng nếu có.
- Không lấy hai lượt chạy với tải khác nhau để tuyên bố phần trăm cải thiện như thể cùng điều kiện.

## Kết quả P00 — giải thích trước khi mở pha mới

| Phép đo | P00 trên Windows | Diễn giải chính xác |
|---|---:|---|
| Sai lệch logits tối đa (Maximum Absolute Logit Difference) | `2.384185791015625e-07` | Đường thường và đường KV phân trang gần tương đương; ngưỡng kiểm thử `2e-5` |
| Sai lệch tiền tố nhân quả (Causal Prefix Difference) | `0.0` | Không phát hiện rò rỉ token tương lai ở fixture; ngưỡng `1e-6` |
| Mất mát mẫu next-token (Gradient Smoke Loss) | `5.489449977874756` | Chỉ xác nhận tính được loss/gradient; **không** là kết quả huấn luyện mô hình |
| Kiểm thử Windows cục bộ (Local QA) | 13/13 PASS | Kiểm thử chức năng và quản trị |
| Kiểm thử bổ sung độc lập (Independent QA) | 6/6 PASS | Kiểm tra bằng fixture khác, không phải thẩm định thương mại |

P00 là mốc đầu tiên, **không có phiên bản tiền nhiệm** để tính tỷ lệ cải thiện. Chưa đo hiệu năng nhân GPU, thông lượng, phân mảnh hoặc chất lượng ngôn ngữ.

## Báo cáo bắt buộc sau mỗi giai đoạn

1. Thay đổi, giả thuyết và mốc đối chứng (Baseline).
2. Bảng cấu hình trước/sau, mã băm và dữ liệu đầu vào.
3. Mỗi phép đo có đơn vị, chiều tốt/xấu, ngưỡng đạt, chênh lệch và sự bất định.
4. Kiểm thử độc lập, kết quả FAIL được giữ, đường dẫn bằng chứng.
5. Quyết định giữ/bỏ/thử tiếp (Keep/Reject/Retest) và giới hạn điều có thể kết luận.

Sử dụng `templates/PHASE_COMPARISON.md`; không suy ra quan hệ nhân quả từ hai lượt chạy không tương đương.
