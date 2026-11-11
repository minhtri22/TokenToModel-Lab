# TTM — Oracle Reader Frozen Bypass · QA source-only

**Ngày:** 2026-11-11. **Nhánh:** research/ttm-vector-memory-architecture-20261111.

**Kết quả:** PASS_SOURCE_ONLY_SYNTHETIC_QA (35/35 kiểm tra tích hợp; 15/15 kiểm tra độc lập). Đây là kết quả kỹ thuật trên dữ liệu và tensor tổng hợp, không phải kết quả khoa học trên checkpoint đã huấn luyện.

## Nguồn và giới hạn

- P02 source Git blob: 9762343e06cf800b50574c2871ae1ed58537fb18.
- TRAIN 256 truyện: Git blob 9e86317c055047fffebfb2d802889e69987a8c8b.
- DEV 64 truyện: Git blob ffc9d211508fbedc84db31235ecaad8d07596ece.
- Tokenizer T1 thật: PASS_REAL_T1_TOKENIZER theo receipt chủ máy Windows cung cấp; 320 cases, max question 43, answer 4, combined 47, prefix mismatch 0. SHA256 receipt đã báo: bc688ca5bcc4084a19d3e95b0f7d555c283d8b1b1319ff255c5baF9e66c7b34b. **Chưa có độc lập đọc bytes receipt.**
- Không nạp checkpoint đã huấn luyện, không đọc hoặc giải mã TEST, không huấn luyện adapter, không chạy inference khoa học và không sử dụng GPU.
- Bộ thử Reader chỉ dùng byte encoder giả lập (mock) và các tensor/weights ngẫu nhiên; không thay thế kiểm định tokenizer T1 thực.

## Kiến trúc đã triển khai

Question -> trích xuất một mã thực thể từ chính nội dung câu hỏi -> Oracle tìm duy nhất một key trong ba fact cards. Hàm oracle_key_mask chỉ nhận question và memory_cards, không nhận gold label, answer hoặc target_key từ metadata.

Memory Reader nhận riêng vector Key và Value, dùng Query/Key/Value projections 64/128 chiều, masked Cross-Attention, Adaptive Gate theo từng input, residual lên hidden state sau frozen P02 và trước cùng tied output head. Các đối chứng:
- No memory: mask tất cả; giữ nguyên hidden state và logits theo phép so bit-exact.
- Đúng memory: chỉ chọn một record có key trùng thực thể trong câu hỏi.
- Sai memory: đổi đúng value của record mục tiêu, giữ nguyên key, vị trí và hai distractor.

Output projection khởi tạo zero nên Reader ban đầu không thay đổi logits kể cả có memory. Khi can thiệp có kiểm soát lên output projection (không train), đổi value từ correct sang wrong làm Reader tạo logits khác nhau; bypass vẫn giữ nguyên logits.

## Bằng chứng

- Primary source-only QA 35/35 PASS: pinned P02 và fixture blobs; toàn bộ 320 TRAIN/DEV cases; negative-key cases; no-memory bit-exact; cold-init bit-exact; swap-value sensitivity; distractor masking; mixed-batch; frozen parameters; không gradient.
- Independent second-path QA 15/15 PASS: xác nhận lại nguồn, oracle không đọc gold/target metadata, foil value, zero-init bypass và random P02 full-logit parity.
- Random P02 smoke dùng đúng P02 Git blob và topology n_layer=4, n_head=4, n_embd=256, max_seq_len=256. Đầu ra full-model với bypass và cold-init Reader trùng từng phần tử. **Đây là random-weight technical smoke; checkpoint TRAINED chưa được sử dụng.**
- QA artifacts và Python runner lưu cùng thư mục tools/research/vector-memory và artifacts/research/vector-memory.

## Hạn chế khoa học

Oracle mask chỉ cho phép đúng một memory card hoạt động; attention weight ở card này bằng 1. Do đó QA không chứng minh khả năng xếp hạng truy xuất theo ngữ nghĩa hoặc learned key-query attention. Không có bằng chứng Reader giảm NLL, sao chép đúng nhãn, hoặc cải thiện mô hình. RETRIEVED_TOPK, teacher-forced answer-only NLL, cấu hình chọn qua DEV và TEST one-shot chưa chạy.

## Quyết định

**PASS** cho source-only Oracle Reader + frozen bypass wiring. **HOLD** cho huấn luyện CPU vì cổng scientific execution chưa được phê duyệt. TEST được giữ nguyên niêm phong. MAIN và P00-P12 không thay đổi. Không ghi thêm lineage.md vì chưa có PASS/FAIL khoa học.

**Bước thực hiện tiếp theo:** TTM_VM_EXTERNAL_FACTS_CPU_PILOT_ONE_SHOT_TRAIN_DEV_PREREG_AND_READINESS — tích hợp xác thực receipt T1 gốc, checkpoint SHA, scorer answer-only chính xác, negative QA, khóa một ngân sách CPU và chỉ trình quyết định thực thi sau khi cổng tiền kiểm đủ.
