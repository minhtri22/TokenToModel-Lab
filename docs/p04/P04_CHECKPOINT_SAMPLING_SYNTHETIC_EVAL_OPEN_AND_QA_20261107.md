# TTM — P04 mở từ P03 đã đóng: checkpoint, sampling, đánh giá tách riêng

Ngày 07/11/2026. Mốc gốc P03 merge: `94b01b4817c3c11c8b9a9cbbc01bfc867066a596`. Kiến trúc P00–P12 giữ nguyên; P04 làm việc với Transformer Core P02 2.048 token và vòng huấn luyện P03 đã PASS.

## Phạm vi triển khai đầu tiên

- `save_checkpoint_new`: chỉ tạo mới, không ghi đè; lưu `state_dict` tensor và cấu hình + mã băm merges BPE. Đây là checkpoint kỹ thuật **ứng viên**, không phải checkpoint mô hình được huấn luyện trên Wikipedia.
- `load_checkpoint_verified`: kiểm SHA-256 tệp trước khi gọi `torch.load(weights_only=True)`; yêu cầu schema/config/merge SHA chính xác và nạp `state_dict` strict; từ chối file thay đổi hoặc tokenizer không khớp.
- `generate_tokens`: autoregressive chỉ trên CPU, top-k/temperature và local seeded generator, giới hạn context và ID token [0,2047]; tính tái lập so với oracle argmax.
- `evaluate_synthetic_heldout`: tính negative log-likelihood/perplexity theo các tensor do người gọi truyền; chỉ nhận nhãn `SYNTHETIC_HELDOUT`, inference-only, không thay đổi trọng số. Kiểm tra nhãn không chứng minh bộ dữ liệu khách quan có độc lập nếu người gọi dán sai; ở đây fixture được chủ động tạo tách biệt.

## Kết quả QA ban đầu — chỉ trên CPU ngoại tuyến

Python 3.13.5, PyTorch 2.10.0+cpu: **6/6 unittest PASS và 4/4 independent checker PASS** trên mã của ứng viên này. Kiểm tra vòng lặp khôi phục đúng logits, checkpoint bị thay đổi/nhầm tokenizer được từ chối, sinh mẫu cùng seed lặp được, đánh giá heldout khớp tính lại thủ công, không có optimizer step. **Chưa chạy Windows QA, chưa đóng P04**.

Các tệp:
- `src/p04/eval_checkpoints.py` SHA `e749c8eb880081feaf75443289a900bea352c92c9cd0df07746c1961398d180d`.
- `tests/p04/test_eval_checkpoints.py` SHA `7855a1231ac15bb1f1fba1cdad65f37c6d5fb07b5c6c3712fe2055caa3a29836`.
- `tools/p04/independent_p04_qa.py` SHA `dd154233dfb9552a001ab92c3abb017ef85ab45849dd15bbd8f5aaec0ef482ec`.

## Quyền dữ liệu và điều kiện đóng P04

Dữ liệu F1 WP30 trước đây chỉ được duyệt cho BPE E0 nội bộ, vì vậy P04 **không** truy cập WP30 TEST, không huấn luyện GPT trên Wikipedia và không suy diễn quyền thương mại. QA P04 hiện chỉ dùng token tổng hợp; kết quả perplexity trên mẫu tổng hợp không nói lên chất lượng tiếng Việt.

Bước tiếp theo duy nhất: chạy QA tích hợp P04 trên Windows máy chủ dự án (6+4 bài) với exact Git blob/head, biên bản hash và dọn worktree tạm trong dự án, rồi thẩm định/merge nếu PASS. Đánh giá thực nghiệm trên held-out văn bản thật cần một quyết định nguồn/đăng ký riêng phù hợp, không tự động mở qua QA tổng hợp.

`P01=CLOSED_SCOPED` · `P02=CLOSED_SCOPED_CPU` · `P03=CLOSED_SCOPED_SYNTHETIC_CPU` · `P04=OPEN_CANDIDATE` · `P05=NOT_OPENED` · `lineage.md=UNCHANGED`.
