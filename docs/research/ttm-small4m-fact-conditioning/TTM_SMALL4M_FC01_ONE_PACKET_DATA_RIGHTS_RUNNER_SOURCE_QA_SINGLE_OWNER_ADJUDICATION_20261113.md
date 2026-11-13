# TTM-Small-4M / FC01 — Một lượt readiness tích hợp: dữ liệu, quyền, runner và QA

**Operation:** `TTM_SMALL4M_FC01_ONE_PACKET_DATA_RIGHTS_CORPUS_RUNNER_SOURCE_QA_SINGLE_OWNER_GO_HOLD_NO_GPU`  
**Ngày:** 13/11/2026  
**Chế độ:** DESIGN+SOURCE+STATIC_QA, không GPU/optimizer/inference, không giải mù và không mở D1.  
**Quyết định DUY NHẤT:** **`HOLD_INTEGRATED_PREEXEC_PENDING_EXACT_OWNER_BPE_AND_COLAB_RUNTIME`**. Không phải phát hiện khoa học âm tính của FC01.

## 1. Vị trí TTM so với clip video 35 giây do owner gửi

Clip là mô hình minh họa học có giám sát trên chữ số 3: dự đoán `ŷ=f(x;W)`, tính lỗi `e=ŷ-y`, loss bình phương `L`, tính gradient qua backpropagation, rồi cập nhật `W←W−η∇L`. Clip mô tả **cơ chế cập nhật trọng số** trong mạng neuron, không chứng minh mô hình đã học bất kỳ quy tắc suy luận nào.

TTM đã có huấn luyện Transformer P02 3.749.376 tham số thực, tokenizer BPE2048, checkpoint step1024 và phép đo VAL NLL; DEV32 exploratory cho kết quả teacher-forced S=1/16, S'=2/16 và factual adherence 0/32 cho cả greedy/nucleus theo AI rater, với hạn chế provenance input từ phiên chấm. **FC01 nằm ở bước thiết kế can thiệp vào dữ liệu và loss** để kiểm tra liệu gradient có học được phụ thuộc dữ kiện hay không; không phải dự án chưa biết backprop. Video không có dữ liệu benchmark để định vị TTM trên một bảng xếp hạng.

## 2. Dữ liệu phản thực mới, đã thực sự tạo (không chỉ blueprint)

Một generator Python 3.12/stdlib độc lập, không đọc D1/TEST/Q1Q2, đã xuất một gói private mới:

- `384` lexical-scene family, `4` category × 96 scene/category.
- `TRAIN=256` (64/category), `VAL=64` (16/category), `EVAL_HOLDOUT=64` (16/category).
- Cặp prompt `A/B` cho mỗi family, hai paraphrase và một neutral prompt, kèm `yA/yB`.
- `A_BASE_MLE=512` synthetic episodes, D0 singleton cân bằng 256 fact A/256 fact B; mỗi family chỉ có 1 fact và 2 paraphrase.
- `B_CF_MLE=512` episodes, 1 fact A và 1 fact B mỗi family; hoán đổi thứ tự A/B giữa paraphrase0/paraphrase1 theo parity family để tránh confound format.
- `C_CF_CONTRAST`: episode bytes giống **chính xác** B, 512 episodes; chỉ khác objective trong runner.
- **SHA-256 gói private corpus canonical:** `7214213c79002943cbb9f7d0c6c25a81ba7f522c7218dcd4297a2c8465084bd6`.

**Quan trọng về độ độc lập:** 384 scene là những tổ hợp định danh/đồ vật và phrasing trên **4 template semantics chung**; chúng là family ID không trùng, **không phải 384 bài toán suy luận độc lập về mặt cấu trúc**. Claim ở FC01 phải giới hạn trong chuyển giao lexical family trên shared templates, không tuyên bố reasoning novel-template. Candidate BPE equality và non-overlap nghĩa/nguồn sealed chưa được chứng nhận. Dữ liệu do script mới tạo không thay đổi một byte DEV32 đã đóng.

**Bằng chứng private:** file `FC01_OWNER_PRIVATE_DATA.json` (993KB), `FC01_SAFE_DATA_GENERATION_RECEIPT.json`, đóng trong ZIP private riêng, **không commit văn bản/holdout lên GitHub**. Gói private trên sandbox cần người dùng tải về để lưu local; bản Windows hiện chưa được tạo từ exact pinned T1 manifest.

## 3. Nguồn TinyStories và quyền sử dụng

Đã xác minh bằng manifest T4 hiện tồn tại trên Windows:

- `TinyStories-train.txt` trong `datasets/tinystories_v1_original_pinned`: SHA-256 theo gói T4 `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`.
- SHA này **khớp công bố SHA-256 upstream** của original `TinyStories-train.txt` trên Hugging Face. URL: https://huggingface.co/datasets/roneneldan/TinyStories/blob/main/TinyStories-train.txt
- `TinyStories-valid.txt`: SHA trong T4 manifest `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`.
- T4 private TRAIN/VAL pack chứa `2691 TRAIN` windows, `328 VAL` windows, schema đã pin; `contains_test=false`; pack SHA-256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; manifest SHA-256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`.
- Tokenizer T1 file SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Dataset card upstream công bố license `cdla-sharing-1.0`; việc dùng phải tuân thủ điều kiện giấy phép và attribution. https://huggingface.co/datasets/roneneldan/TinyStories

**Phạm vi kết luận quyền:** upstream có khai báo license và repo đang có bản local gắn SHA từ T4; **chưa thực hiện việc băm lại toàn file TRAIN 1.92GB ở lượt hiện tại**, chưa kiểm quyền reuse bản copy local ở mức owner. Gói PS chạy một lần có kiểm SHA file thật và không phát sinh nguồn khác. Không gán `FULL_RIGHTS_QA_PASS` chỉ từ card.

## 4. Runner huấn luyện, đánh giá và one-shot custody đã dựng

Đã tạo gói mã nguồn (nộp qua artifact trong cuộc trò chuyện; hash được ghi nhận, **chưa phải các file đã commit source trên GitHub**):

- `fc01_build_private_corpus.py`: tạo dữ liệu deterministic, refused overwrite.
- `fc01_pinned_bpe.py`: đúng T1 BPE source manifest đã pin, chỉ đọc.
- `fc01_integrated_static_qa.py`: kiểm family split/cue/labels, B/C equality, và nếu có manifest gốc thì kiểm exact BPE prefix/length/overflow.
- `fc01_independent_contract_tests.py`: kiểm âm, toán học contrastive và one-shot.
- `fc01_train_eval_once.py` có `--audit`, `--train`, `--evaluate`, `--secondary`. Chế độ training yêu cầu receipt owner GO của cả ba nhánh và exact SHA; không có receipt sẽ báo HOLD, không sử dụng GPU. Cùng checkpoint step1024/P02/BPE, 256 updates×16×256 token slots/arm, 4 microbatch (3 core +1 synthetic)/step, AdamW, 1 training seed khóa; C bổ sung pairwise softplus contrastive.
- `--evaluate` buộc phải có đủ **ba final checkpoint step256**, chấm 64 family holdout × 6 candidates × 3 model = 1152 scores, bootstrap 10k theo family.
- `--secondary`: 32 greedy outputs/arm × 3 arm = 96 private outputs, blind ID/mapping tách biệt; **không chấm mù trong lượt readiness này**.
- Save checkpoints step0/64/128/192/256, có optimizer/RNG/cursor và SHA; chỉ resume cùng logical run, không best-VAL.
- `Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1`: khi chạy local trên máy owner, băm trực tiếp TinyStories/T4/BPE/checkpoint; tạo corpus once, exact BPE QA, 15 negative tests, đóng gói input train/val-only, chạy `--audit`; **không train**.

**SHA-256 ZIP mã nguồn:** `601b9ded14c3db013f1c3d237461f4144ea3fbc86deffc2749e825a261043b36`; **SHA-256 ZIP private:** `da579dd6d5f2e92baa9fba524c30177a32d2d340fad6b6f7ca71a8f4bc9004b1`.

**Giới hạn:** Các file chạy hiện ở artifact zip trong phiên này; chưa có execution thực của P02 + tokenizer + DATA trên Windows hay Colab, và chưa xác minh reproducibility checkpoint resume trên T4. Không gọi trainer `DYNAMIC_QA=PASS`. Bộ PS cũng chưa chạy trên Windows, không giả báo đã staging local.

## 5. Kết quả QA duy nhất đã thực thi

**QA tĩnh/độc lập về mã:** `15/15 PASS` trên runtime container CPU với corpus 384 family, gồm kiểm mutation âm duplicate, nhãn âm, cue A/B, đối chứng B/C giống byte, source checksum, sampler deterministic, toy contrastive gradient, source-one-shot no overwrite và science GO absent. Tất cả là **self-authored separate-checker QA**, không phải external human independent review.

**Exact T1 private BPE QA:** `NOT_EXECUTED` do private manifest thực tế chỉ có trên Windows; toy-BPE test không thay thế được.  
**Runner --audit trên pinned full owner bundle:** `NOT_EXECUTED`.  
**Real Colab FP32/Drive resume QA:** `NOT_EXECUTED`.  
**Science GPU train/inference:** `NONE`.  
**TEST/Q1Q2:** `SEALED`, không đọc.

## 6. SINGLE OWNER GO/HOLD và Bước thực hiện tiếp theo

**ONE DECISION: `HOLD_INTEGRATED_PREEXEC`.** Các điều kiện khoa học thiết kế giữ nguyên; lý do không phải thiếu thêm micro-permit:

1. Pinned tokenizer candidate length and prefix exact QA chưa chạy trên máy có file gốc; không biết chắc candidate length A/B equal.
2. Source raw TRAIN và T4 pack phải được rehash trực tiếp, source rights compliance cần được làm rõ trong một lượt local.
3. Runner `--audit` và kiểm tính chạy/resume trong runtime dự kiến chưa được xác minh; 3 T4 GPU-hour là trần, **không phải** estimate đo.
4. Four shared templates limit semantic generalization: chốt phạm vi inference `SCOPED_TEMPLATE_GENERALIZATION`.

**Một gói PS5.1 để hoàn tất readiness trên Windows** đã nằm trong ZIP code; thực hiện sau khi giải nén vào `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\fc01_onepacket_20261113`, một lệnh: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\fc01_onepacket_20261113\Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1"`. Nếu PASS, chỉ trở thành `PASS_OWNER_SOURCE_QA`; quyết định science GO phải dựa vào exact source bytes và runtime colab, không được tự suy diễn thành đã train.

**Các trạng thái phải giữ:** `FC01_DESIGN=FROZEN`, `FC01_CORPUS_CANDIDATE_BYTES=FROZEN_LOCAL`, `FC01_STATIC_QA=PASS_15/15`, `FC01_EXACT_OWNER_BPE_QA=NOT_EXECUTED`, `FC01_SCIENCE=HOLD_PREEXEC`, `TRAINING=NO`, `GPU=NO`, `NEW_INFERENCE=NO`, `FC02_CAPACITY=NOT_OPENED`, `DEV32=CLOSED_UNCHANGED`, `D1_CONFIRMATORY=HOLD`, `TEST_Q1Q2=SEALED`, `LINEAGE=UNCHANGED`, `MAIN=UNCHANGED`.
