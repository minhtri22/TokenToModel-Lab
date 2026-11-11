# TTM — External-Facts CPU Pilot: One-Shot TRAIN/DEV Preregistration & Readiness

**Operation:** `TTM_VM_EXTERNAL_FACTS_CPU_PILOT_ONE_SHOT_TRAIN_DEV_PREREG_AND_READINESS`  
**Ngày:** 2026-11-11  
**Nhánh độc lập:** `research/ttm-vector-memory-architecture-20261111`, không liên quan thay đổi P00–P12.  
**Quyết định:** `PREEXEC_TECHNICAL_READINESS=PASS_SCOPED` · `SCIENCE_EXECUTION=NOT_AUTHORIZED/NOT_EXECUTED` · `TEST=SEALED`. Không merge `main`.

## 1. Câu hỏi đã khóa

Transformer P02 TTM-Small-4M (checkpoint thật bước 1280) có thể dùng **Reader học riêng trên TRAIN** để khai thác một ánh xạ *thực thể tưởng tượng → nhãn 5 chữ* chỉ có trong bộ nhớ ngoài, tăng xác suất câu trả lời đúng khi so với Reader không có memory và cùng Reader nhận memory sai, mà **không thay đổi bất kỳ trọng số GPT gốc** hay không?

Đây chỉ là bài toán toy **external-fact binding**: không chứng minh kiến thức ngữ nghĩa, RAG tổng quát, khả năng lưu trữ/thay thế weights hoặc chất lượng văn bản mở.

## 2. Ghim nguồn và giới hạn quyền

| Thành phần | Pin |
|---|---|
| P02 original source Git blob | `9762343e06cf800b50574c2871ae1ed58537fb18` |
| Checkpoint SHA-256, step 1280 | `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc` |
| Oracle Reader source Git blob | `7ce728b2874284b87933237c890e54ce3d9fd651` |
| TRAIN 256 Git blob | `9e86317c055047fffebfb2d802889e69987a8c8b` |
| DEV 64 Git blob | `ffc9d211508fbedc84db31235ecaad8d07596ece` |
| T1 TRAIN-only tokenizer manifest SHA-256 | `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` |
| Owner's tokenizer QA receipt SHA-256 | `bc688ca5bcc4084a19d3e95b0f7d555c283d8b1b1319ff255c5baf9e66c7b34b` |

Tokenizer QA từ máy chủ dự án báo `PASS_REAL_T1_TOKENIZER` trên 320 trường hợp, `MAX_QUESTION=43`, `MAX_ANSWER=4`, `MAX_JOINT=47`, không có answer-prefix mismatch, TEST không mở. **Chưa lấy và tính lại SHA độc lập của chính receipt Windows**. Trình chạy sau này từ chối khi thiếu file receipt thật hoặc sai SHA.

TEST 64 trường hợp đã mã hóa AES-256-GCM và khóa ngoài GitHub (ciphertext/escrow tách thư mục). **Không giải mã, không chấm, không đưa secret/key vào runner**, không xác nhận người giám sát độc lập. Bộ dữ liệu TRAIN/DEV toy là công khai, khác hoàn toàn TinyStories TRAIN/VAL cũ; ánh xạ TEST chỉ có trong bộ nhớ niêm phong.

## 3. Ba nhánh công bằng

- `A_NO_MEMORY`: **cùng Reader sau huấn luyện**, bypass hoàn toàn, không đọc memory (logits bằng GPT gốc).
- `B_CORRECT_MEMORY`: cùng weights, câu hỏi và 3 fact cards; Oracle tìm bản ghi bằng đúng khóa thực thể **trong câu hỏi**, không dùng trường `answer`/`target_key`.
- `C_WRONG_MEMORY`: cùng khóa, số bản ghi, thứ tự và distractors; đổi duy nhất giá trị của bản ghi mục tiêu thành nhãn sai. **Scoring vẫn trên gold answer chung**.

Oracle mask chỉ để **một key hoạt động**, do đó không phải phép kiểm tra *learned query/key selection* hoặc semantic retrieval. Không được gọi `Recall@3` của truy xuất ngữ nghĩa đã PASS. `RETRIEVED_TOPK` là nghiên cứu tiếp theo và không được thay thế bằng Oracle để mở TEST.

## 4. Quy tắc học CPU một lần — không thay sau khi thấy DEV

- Mô hình: đúng P02 gốc `vocab=2048`, `n_embd=256`, `n_layer=4`, `n_head=4`, `context=256`, tied head. **Tất cả P02 requires_grad=False; không tính gradient hay cập nhật checkpoint.**
- T1 BPE thật; không train lại tokenizer. Memory key/value được mã hóa riêng bằng cách lấy **mean của frozen token embeddings** (theo mã Reader đã khóa); facts không nằm trong question prompt.
- Reader `GatedOracleReader` khởi tạo zero-output. **Query/key projections bị đóng băng** trong chế độ Oracle vì singleton mask cho chúng gradient học lựa chọn bằng 0. Chỉ học `value_proj + output_proj + gate_net`: **110.689 tham số** (Reader tổng 143.457).
- Seed `20261111`; CPU FP32, torch deterministic, 2 CPU threads; AdamW `lr=0.001`, weight decay `0`, clip gradient norm `1.0`; không scheduler, dropout, hyperparameter grid.
- TRAIN chính xác **256 stories**; batch 16 stories; 8 epochs, mỗi epoch hoán vị theo `torch.randperm(..., seed=20261111+epoch)`. **128 optimizer steps**, không kéo dài khi FAIL hoặc train thêm seed khác.
- Feature Transformer frozen được tính **một lần dưới no_grad**; training dùng cache hidden/key/value, gradient **chỉ** trong Reader. Memory TRAIN chứa fact của *chính từng story* và distractors của story đó, không dùng DEV.
- One-shot ID `TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1`; marker `ONE_SHOT_STARTED.json` tạo trước optimizer; nếu thư mục evidence đã tồn tại phải dừng, **không resume/retry tự động**, kể cả khi chạy lỗi.
- Output riêng tư chỉ dưới root dự án; không đăng checkpoint/TEST/secret hoặc reversible hidden states lên GitHub. GitHub chỉ nhận công bố aggregate và mã sau khi review.

## 5. Teacher-forced Answer-only NLL: bắt buộc theo từng story

Với `q = T1.encode(question)` và `joint = T1.encode(question + ' ' + answer)`, đầu tiên yêu cầu `joint[:len(q)] == q` (đã PASS trên 320 TRAIN/DEV).

Token mục tiêu là `joint[len(q):]` (bao gồm khoảng trắng đầu đáp án theo ngữ nghĩa BPE). Tại token mục tiêu thứ `j`, causal hidden state được tính từ `joint[:len(q)+j]` và logits dự đoán từ vị trí **`len(q)+j-1`**, tuyệt đối không tính loss trên phần question. Khi Teacher Forcing, token đáp án đã xuất hiện trước thời điểm `j` là hợp lệ; truy xuất memory vẫn chỉ dùng câu hỏi, không dùng gold label để định vị key.

Mỗi story tính **trung bình NLL trên token đáp án của riêng story**. Metric chính là **trung bình đồng trọng số trên 64 story DEV**; micro NLL/accuracy chỉ là phụ trợ, không đổi tiêu chí sau khi xem DEV.

## 6. DEV và quyết định về sau

Chọn **cố định checkpoint Reader bước 128**, chỉ chấm DEV 64 một lượt, không early-stop hoặc chọn seed theo DEV. Đánh giá A/B/C cùng reader, cùng question/label, cùng scorer. DEV screen chỉ đạt `GO_CANDIDATE` khi:

1. `mean_story_NLL(A)-mean_story_NLL(B) >= 0.05`;
2. `mean_story_NLL(C)-mean_story_NLL(B) >= 0.05`;
3. Cận dưới paired bootstrap phân vị 95% của cả hai chênh lệch lớn hơn 0 (`1000` replicates, seed `20261112/20261113`).

Nếu không đạt => `DEV_SCREEN_NO_GO`, báo cả kết quả âm và **không mở TEST/GPU**. Nếu đạt, chỉ là **ứng viên tiếp tục nghiên cứu**: còn cổng RETRIEVED_TOPK recall và phán quyết science execution/TEST một lần riêng biệt; không mặc nhiên giải mã TEST hoặc khẳng định YES.

## 7. Bằng chứng tiền kiểm đã thực hiện (không phải khoa học)

- `cpu_pilot_readiness.py` kiểm tra SHA checkpoint thật, source blob, fixture; nạp checkpoint **chỉ để kiểm tra trọng số và bypass trên token ID tổng hợp**, không đưa TRAIN/DEV vào mô hình đã học.
- `Answer-only NLL` smoke trên P02 **random weights** + tokenizer mock byte. Cơ chế teacher forcing, nhiều token đáp án, no-memory vs direct CE, zero-init, value-swap, gradient chỉ vào Reader đều PASS.
- **29/29** kiểm tra tiền kiểm CPU PASS; checkpoint thật đọc SHA đúng và full logits trên token tổng hợp **bit-exact** khi bypass và khi Reader khởi tạo zero; trọng số không đổi.
- `cpu_pilot_independent_readiness_audit.py`: **34/34** source/negative QA PASS; kiểm tra cổng `--execute-once` từ chối chạy khi không có permit (không đụng dữ liệu); no overwrite, origin pins, test-not-used.
- **Không thực thi training hoặc DEV scoring**; không đọc hay giải mã TEST; `lineage.md` không bổ sung vì không có kết quả khoa học PASS/FAIL.

## 8. Quyết định cuối của bước hiện tại

`PREREG_AND_SOURCE_READINESS=PASS_SCOPED` · `FROZEN_CHECKPOINT_SYNTHETIC_BYPASS=PASS` · `REAL_T1_OWNER_RECEIPT=PASS_OWNER_REPORTED` · `ORIGINAL_RECEIPT_INDEPENDENT_READBACK=NOT_DONE` · `TRAINER_SOURCE=STAGED_NOT_EXECUTED` · `TRAIN_DEV_SCIENCE=NOT_EXECUTED` · `TEST=SEALED`.

**Bước thực hiện tiếp theo:** `TTM_VM_EXTERNAL_FACTS_CPU_PILOT_OWNER_ONE_SHOT_EXECUTION_DECISION`: chỉ sau khi xác minh tệp receipt trên máy theo SHA gốc, QA nguồn runner tại checkout được ghim và quyết định rõ ràng cấp một lần execution CPU, mới chạy mã đã khóa; không cấp quyền tự động bởi việc hoàn tất tài liệu này.
