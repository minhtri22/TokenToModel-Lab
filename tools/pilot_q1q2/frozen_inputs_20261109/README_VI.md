# TTM — Q1/Q2 batch input đã khóa (chưa chạy mô hình)

- Mục tiêu: đánh giá mô hình TTM-Small-4M sau Ollama compatibility PASS, bằng **16 lời dẫn mới** (8 everyday, 4 cause/effect, 4 entity consistency).
- Tệp `Q1_ORIGINAL_PROMPTS.json`: 16 lời dẫn tiếng Anh **tự biên soạn**; không sao chép corpus TinyStories, không dùng TEST 64 truyện.
- `Q1_FROZEN_48_RUN_MATRIX.json`: 16 greedy (temperature 0, top_p 1.0, seed không áp dụng), 32 sampled (temperature 0.8, top_p 0.9, seed 101/102), tối đa 64 token, context 256.
- `Q2_FROZEN_24_MEASUREMENT_MATRIX.json`: 4 lời dẫn, context 128 hoặc 256, 3 lần đo, greedy, 32 token; 1 warmup riêng cho mỗi context, không tính thống kê.
- `Q1Q2_FROZEN_CONFIG.json` ghi baseline, thước đo, rubric 0–3, tiêu chí ra quyết định sơ bộ và giới hạn so sánh công bằng.
- Tệp `Q1Q2_LOCK_MANIFEST.json` ghim SHA-256. Chạy `python QA_FROZEN_INPUTS.py` để xác minh, **chỉ đọc và không gọi Ollama**.
- Không có runner tự thực thi. Muốn chạy Q1/Q2 thật phải bổ sung script kiểm chứng SHA, quyền sở hữu cổng mới, nguồn tokenizer chính xác, model store bản sao, chống chạy trùng, cap RAM/disk/time và nguyên tắc bất biến; sau đó kiểm thử tích hợp độc lập. Không chạm phiên inference-only đã tiêu thụ.
- Vocab BPE2048 được train trên TRAIN-only. Các chỉ số n-gram trong báo cáo dùng token IDs BPE thật, không trộn với từ tách bằng khoảng trắng. Trước chạy phải xác minh độ dài token hóa của 4 prompt Q2 nhỏ hơn 128 trên đúng tokenizer.
- Tốc độ dùng `eval_count/eval_duration_ns`, báo median và range theo context; không ngụy nhận TTFT từ nonstreaming.
- Q1 là đánh giá thăm dò (`EXPLORATORY`); các ngưỡng chỉ là tiêu chí kỹ thuật để quyết định nghiên cứu tiếp, không phải chứng nhận khoa học hay thương mại.
