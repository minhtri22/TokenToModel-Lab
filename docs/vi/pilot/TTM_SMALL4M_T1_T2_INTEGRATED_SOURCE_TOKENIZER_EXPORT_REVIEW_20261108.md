# TTM-Small-4M — Rà soát tổng hợp tiền đăng ký T1/T2 (2026-11-08)

> **Bản tiếng Việt chuẩn hóa của tài liệu thiết kế lịch sử.** Những phán quyết `NOT_VERIFIED`/`HOLD` trong thân bài là trạng thái lúc lập hồ sơ; kết quả kỹ thuật cập nhật nằm trong [biên bản đóng T1–T3](TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md). Không sửa hoặc thay thế [hồ sơ gốc](../../pilot/TTM_SMALL4M_T1_T2_INTEGRATED_SOURCE_TOKENIZER_EXPORT_REVIEW_20261108.md).

> **CẬP NHẬT VÀ CHỨNG CỨ ƯU TIÊN (2026-11-08):** [T2 F32 native closure và quyết định F16 không chặn pilot](TTM_T2_F32_NATIVE_CLOSURE_AND_F16_GATE_AMENDMENT_20261108.md). T2 synthetic GGUF F32 đã PASS native tokenizer 20/20, logits 10/10 trên fixture mới khóa trước. Các trạng thái `GGUF=NOT_EXECUTED` và `T2=HOLD` ở dưới là biên bản lịch sử tại lúc lập tài liệu, **không còn là trạng thái hiện tại của T2 F32**. T1 nguồn TinyStories thật, tokenizer thật, T3 resume và science lock vẫn HOLD; F16 backend vẫn BLOCKED và được tách khỏi đường găng pilot.


**Nhánh nghiên cứu:** `research/ttm-small-4m-colab-pilot-prereg-20261108` · PR #12 · mốc đối chứng (Baseline) `main@1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`  
**Phán quyết:** `DESIGN_SPEC_REVIEW=PASS_SCOPED` · `DATA_SOURCE_RIGHTS=PASS_CARD_AND_LICENSE_REVIEW` · `SOURCE_REVISION=PINNED` · `RAW_FILE_SHA256=NOT_VERIFIED` · `STORY_PARSER=NOT_VERIFIED` · `GGUF_FEASIBILITY=SUPPORTED_ARCH_WITH_OPEN_MAPPING_GAPS` · `SCIENCE_LOCK=HOLD`.  
**Phạm vi:** chỉ tài liệu. Không tải tập ngữ liệu (Corpus), không chạy GPU, không học bộ tách token (Tokenizer Training), không chuyển đổi GGUF (GGUF Conversion), không mở TEST hoặc thực nghiệm khoa học; không sửa P00–P12, P07 hay `lineage.md`.

## A. Quyết định nguồn, giấy phép và gốc dữ liệu

| Trường | Quyết định thẩm định |
|---|---|
| Bộ dữ liệu (Dataset) | `roneneldan/TinyStories` — bộ dữ liệu (Dataset) trên Hugging Face |
| **Commit SHA-1 đúng 40 ký tự** | `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64` |
| File **TRAIN gốc** | `TinyStories-train.txt` |
| File **VALID gốc** | `TinyStories-valid.txt`; được chia thành VAL và TEST riêng theo chính sách mục B |
| Loại trừ | `TinyStoriesV2-GPT4-*.txt`, `data/*.parquet`, `TinyStories_all_data.tar.gz`, nguồn WP30 P01 |
| Giấy phép được công bố | SPDX `CDLA-Sharing-1.0`, kiểm tra thẻ dữ liệu (Dataset Card) tại commit đã ghim (Pinned Commit) |
| Nguồn tham chiếu | https://huggingface.co/datasets/roneneldan/TinyStories/tree/f54c09fd23315a6f9c86f9dc80f725de7d8f9c64 · https://huggingface.co/datasets/roneneldan/TinyStories/commit/f54c09fd23315a6f9c86f9dc80f725de7d8f9c64 |
| License chính thức | https://cdla.dev/sharing-1-0/ ; FAQ https://cdla.dev/faq-resources/faq/ |
| **File SHA-256** | **Chưa xác thực**: cần tính trên bytes gốc sau lần acquisition hợp lệ; không ghi số đo suy đoán |

**Kết luận quyền:** theo điều khoản CDLA-Sharing-1.0 §§1–3, quyền sử dụng (Use/Computational Use) được cấp để dùng dữ liệu cho nghiên cứu/huấn luyện, với các điều kiện của giấy phép (License). Khi công bố dữ liệu (Publish Data) hoặc dữ liệu tăng cường (Enhanced Data), phải giữ giấy phép (License) và ghi công nguồn (Attribution) và thông báo sửa đổi; mục kết quả (Results) (§1.11/§3.5) có phạm vi riêng, không đồng nghĩa với bảo đảm rằng một điểm lưu mô hình (Checkpoint) không ghi nhớ văn bản gốc. Không đăng tải dữ liệu thô (Raw Dataset) hoặc cửa sổ token hóa có thể đảo ngược (Reversible Token Windows) trong repo công khai; trước phân phối mô hình phải đánh giá hiện tượng ghi nhớ dữ liệu (Memorization)n, luật/PII và nghĩa vụ riêng. **PASS license-card review không phải xác thực dữ liệu hay cấp quyền publish thương mại cụ thể.**

Dữ liệu gốc là lớn (trang HF liệt kê train TXT xấp xỉ 1.92 GB, valid TXT xấp xỉ 19.4 MB); tập thử nghiệm giới hạn (Pilot) chỉ **lấy mẫu TRAIN có kiểm soát**, không mặc nhiên sử dụng toàn bộ 7.62 GB chế độ hiển thị bộ dữ liệu (Dataset View) hoặc V2.

## B. Cách phân chia và chống rò rỉ — hợp đồng dự kiến, trình phân tích (Parser) chưa khóa

1. Trước khi đọc toàn bộ, kiểm tra qua một mẫu nhỏ được cấp phép xem TXT có separator truyện, encoding, EOS và newline thật như thế nào. Chỉ sau khi xác định parser boundary mới khóa implementation/hash; không tách theo khung token hoặc dòng tùy tiện.
2. Sinh `story_id = SHA256(raw_story_bytes)`, phát hiện byte-exact duplicates (cùng SHA). Sinh bản normalized chỉ phục vụ tìm near-duplicates: Unicode NFC, casefold và chuẩn hóa khoảng trắng (nội dung huấn luyện vẫn giữ raw). Thuật toán candidate near-dup (ví dụ MinHash/LSH) phải được version-pin và audit recall; tính chính xác **Jaccard trên tập word 5-grams** cho cặp ứng viên với ngưỡng `>= 0.85`; log số lỗi/bỏ sót trong kiểm tra độc lập. Không gọi là chứng minh không rò rỉ nếu thuật toán tìm ứng viên không bao quát.
3. Toàn bộ chuyện lấy từ `TinyStories-train.txt` chỉ có thể vào **TRAIN**. Lấy tối đa tập chuyện theo thứ tự `SHA256(seed || story_id)` với `seed=20261108`, đủ một token pool ít nhất `4,194,304` token mục tiêu hợp lệ (Valid Target Tokens) sau tokenizer; ngưỡng mẫu/khối lượng tải tối đa phải được tính trước khi thu nhận dữ liệu (Acquisition). Không lấy tập valid để học bộ tách token (Tokenizer), mốc đối chứng (Baseline) hoặc mô hình (Model).
4. `TinyStories-valid.txt`: chỉ sau dedup/chặn giao nhau với TRAIN, phân vào **VAL/TEST** theo hash `SHA256("split-v1:" || story_id)`; byte đầu `< 0xCC` -> VAL (xấp xỉ 80%), còn lại -> TEST (xấp xỉ 20%). Không reroll tỷ lệ sau khi xem loss, không đưa TEST vào tokenizer/prompt tuning. Kiểm tra mọi split có đủ mẫu và không rỗng.
5. Nếu hai story gần trùng qua các split, quy tắc **ưu tiên TRAIN > VAL > TEST** để loại bản sao trong split thấp ưu tiên; không di chuyển chuyện TEST sang TRAIN. Lưu manifest cho từng story (ID, nguồn file, offset, split, dedup status), đếm truyện/tokens và SHA-256 trên kết quả đã chọn. Seal `TEST` cho tới lượt đánh giá duy nhất sau lựa chọn checkpoint.
6. Kiểm tra dữ liệu truyện tổng hợp có thể chứa PII, đoạn sai/hại/bất thường; chỉ công bố metadata kết quả, không coi dữ liệu synthetic là an toàn tuyệt đối.

**Cổng thực tế:** `STORY_BOUNDARY_PARSER=HOLD_BYTES_NOT_SEEN`, `FILE_SHA256=HOLD`, `SPLIT_MANIFEST=NOT_MATERIALIZED`. Các bước này nằm trong **một** source-data QA tích hợp, không tách thủ tục cấp phép kỹ thuật (Permit).

## C. Bộ tách token (Tokenizer) được quyết định ở mức thiết kế

- Định nghĩa tokenizer **byte-level BPE tự xây, chỉ TRAIN**, `vocab_size=2048`; IDs `0..255` cho 256 byte, `256` là EOS, `257..2047` ứng với **1,791 merges** theo thứ tự determinism. Không BOS/PAD riêng trong primary route. Không tái sử dụng tokenizer tiếng Việt P01.
- `EOS=256` chỉ chèn giữa các chuyện và sau chuyện cuối; văn bản không được chứa ID 256 trước tokenize. Không nối raw bytes của VAL/TEST vào BPE fitting. Freeze vocab, ordered merges, mọi thao tác whitespace, pretokenization/byte-to-unicode, escape special token và `SHA256(tokenizer_manifest)` trước khi train.
- Quy tắc BPE ứng viên: mỗi story được chuyển raw UTF-8 bytes trước khi BPE; merge pair có tần suất cao nhất với tie-break lexicographic bằng token ID; không tự thêm GPT-2 regex mặc định. Điều này **có thể không tương thích** GPT-2 GGUF tokenizer: một exporter không tái tạo token IDs = BLOCK ngay cả khi weight mapping đúng.
- QA bắt buộc: mã hóa–giải mã vòng tròn (Round-trip) với UTF-8/Unicode, xuống dòng (Newline), dấu cách cuối (Trailing Spaces) và ranh giới khối đọc (Chunk Boundary), 100% ID-match giữa tokenizer TTM và llama.cpp trên bộ tình huống kiểm thử (Fixtures) cố định (cả byte và mã token đặc biệt (Special Token IDs)); kiểm định bằng hiện vật tokenizer sau khi chỉ học bộ tách token từ TRAIN (TRAIN-only Fitting). Nếu chương trình thực thi (Backend) không thể biểu diễn BPE TTM, sửa riêng bộ chuyển đổi (Adapter) hoặc bổ sung kiến trúc tokenizer hỗ trợ ở T2, **không đổi BPE sau khi thấy VAL**.

## D. Mô hình P02 đúng mã nguồn (Exact Model) và ngân sách huấn luyện một lượt

**Mã nguồn P02 đã khóa (Frozen Source):** `src/p02/transformer_core.py`, Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`. Chính xác `n_layer=4, n_embd=256, n_head=4, max_seq_len=256, vocab=2048, norm=layernorm, eps=1e-5, learned-pos, tied-tok-head`. Công thức đếm: embeddings `2048*256 + 256*256`, 4 khối với cơ chế chú ý (Attention) QKV và phép chiếu (Projection), 4x MLP+2 LayerNorm, final LayerNorm => **3,749,376** tham số riêng biệt (Unique Parameters) theo mã, không phải số đếm đo trong lúc chạy (Runtime).

**Đề xuất khóa phép thử chính (Primary Pilot) (không tự động kích hoạt science):**

| Tham số | Giá trị thiết kế cố định |
|---|---|
| Hạt giống thực nghiệm (Science Seed) | `20261108`; baseline/batch/split bootstrap độc lập có tên miền seed |
| Cửa sổ/context | `256` token; loss chỉ trên next-token target, tránh vượt story/split |
| Global batch | `4096` target tokens / optimizer step; microbatch/gradient accumulation cố định sau zero-science GPU memory smoke |
| Số bước | `1024`, **4,194,304** target tokens; không tự kéo dài nếu FAIL |
| Optimizer | `AdamW`, `lr_peak=3e-4`, `betas=(0.9,0.95)`, `eps=1e-8`, weight decay `0.1`, grad clip `1.0` |
| Scheduler | `32` warmup steps tuyến tính; cosine đến `lr_min=3e-5` tại step cuối |
| Độ chính xác số (Precision) | `FP32` baseline để đối chiếu tương đương (Parity); độ chính xác hỗn hợp (Mixed Precision) trên Colab chọn **một** chế độ sau phép thử nhanh (Smoke), khóa trước huấn luyện TRAIN, trạng thái bộ điều chỉnh thang (Scaler State) phải lưu trong checkpoint khi FP16 |
| VALIDATION | Mỗi `128` steps, cùng tokenizer/split, `eval` mode/no_grad; primary dùng **checkpoint cuối step 1024** |
| Ngân sách vận hành | Một GPU Colab được chọn trước khoa học; preflight synthetic đo thời gian/VRAM. Nếu ước lượng > `90` phút hoặc vượt VRAM/quota thì `CAPACITY_HOLD`, không giảm budget giữa lượt train |
| Checkpoint | Tại steps `0,256,512,768,1024`, thêm trước phiên Colab bị ngắt an toàn nếu có thể; không vượt quota T4 |

**Lưu ý khoa học:** 4,19 triệu token không cam kết văn bản sinh sẽ mạch lạc; đây là phép thử hiệu quả có ngân sách giới hạn. T3 trên dữ liệu tổng hợp (Synthetic) không phải đã huấn luyện TinyStories. Vì GPU Colab khác nhau và tốc độ chưa đo, trạng thái độ chính xác số (Precision)/lô nhỏ (Microbatch) = `HOLD_RESOURCE_SMOKE` trước khi cấp khóa khoa học cuối (Final Science Lock).

## E. Đối chứng và phán quyết đạt/không đạt (PASS/FAIL)

- `uniform`, `unigram`, `bigram` làm trơn Add-α trên **chính TRAIN cùng tokenizer**, không TRAIN trên VAL/TEST. Fix alpha ứng viên `0.1` trước khi thu nhận dữ liệu (Acquisition); alpha không được chọn bằng TEST.
- Primary `mean NLL per scored target token` trên VAL, mask EOS/padding rõ ràng; `PPL=exp(NLL)` chỉ phụ trợ. Vì mục tiêu hiệu quả, so sánh **final checkpoint step 1024** và smoothed bigram, không chọn checkpoint thắng nhất theo VAL.
- `H1 PASS` nếu `(NLL_bigram - NLL_TTM) / NLL_bigram >= 0.05` **và** cận dưới một phía (One-sided) 95% của khoảng chênh lệch bằng tái lấy mẫu ghép cặp theo truyện (Paired Story Bootstrap Gap) `NLL_bigram - NLL_TTM` **> 0**, `1000` lượt lặp tái lấy mẫu (Bootstrap Replicates), seed `20261109`, resample theo chuyện. Nếu số liệu hợp lệ nhưng không đạt điều kiện => `FAIL_H1`; nếu source/compute không hợp lệ => `INVALID_OR_INCONCLUSIVE`, không gọi kết quả khoa học không đạt (Scientific FAIL).
- TEST sealed: chỉ đánh giá một lần cuối sau khi cố định mọi quyết định; báo NLL, PPL, prompt rubric blind (10 prompts tự viết trước; không chứa TEXT), sample diversity/repetition, không tune H1 trên TEST. Không so PPL qua tokenizers khác nhau.
- Quality A/B cache bật/tắt dùng cùng weights/tokenizer/hardware/seed; so riêng logits, latency, memory. Khác LayerNorm vs RMSNorm đòi **train riêng**, nằm ngoài primary pilot. Mọi science PASS/FAIL mới ghi bổ sung `lineage.md`.

## F. Khả thi GGUF dựa trên mã llama.cpp đã ghim — điều kiện phải thử thật

**Mã dự án nguồn đã ghim (Pinned Upstream):** `ggml-org/llama.cpp@372dc5ca157276beb6c67b2e92477e8d662e964a`. Tại commit này, `conversion/gpt2.py` đăng ký `GPT2LMHeadModel` -> `MODEL_ARCH.GPT2`; `src/models/gpt2.cpp` có bộ thực thi (Backend) learned-pos, LayerNorm, fused QKV, FFN, tied output (khi output tensor vắng). Vì vậy `GPT2_BACKEND_EXISTS=PASS_SOURCE_REVIEW`. **Không chứng minh** original TTM checkpoint đã convert/execute.

| TTM tensor | Trung gian HF-compatible GPT2 | GGUF/llama.cpp semantic target |
|---|---|---|
| `tok.weight` | `transformer.wte.weight` | token embedding |
| `pos.weight` | `transformer.wpe.weight` | learned position embedding |
| `blocks.i.ln1.{weight,bias}` | `transformer.h.i.ln_1.*` | attention norm |
| `blocks.i.attn.qkv.{weight,bias}` | `transformer.h.i.attn.c_attn.*` | fused QKV |
| `blocks.i.attn.proj.{weight,bias}` | `transformer.h.i.attn.c_proj.*` | attention output |
| `blocks.i.ln2.{weight,bias}` | `transformer.h.i.ln_2.*` | FFN norm |
| `blocks.i.mlp.0.{weight,bias}` | `transformer.h.i.mlp.c_fc.*` | FFN up |
| `blocks.i.mlp.2.{weight,bias}` | `transformer.h.i.mlp.c_proj.*` | FFN down |
| `final_ln.{weight,bias}` | `transformer.ln_f.*` | output norm |
| `head.weight` tied to `tok.weight` | `lm_head.weight` hoặc omit theo exporter | output tied |

**Nguy cơ số học/tensor:** P02 `nn.Linear` lưu weights dạng `[out,in]`; GPT2 HF `Conv1D` thường mang `[in,out]`, và `conversion/gpt2.py` có bước transpose cho các tensor `c_attn/c_proj/c_fc`. Adapter cần transpose đúng **một lần** và kiểm tensor shape+SHA của 4 layers, Q/K/V ordering, EOS handling, `nn.GELU` so với backend `LLM_FFN_GELU`, LayerNorm eps, posisi và decode context reset. Metadata GGUF phải có `n_ctx=256, n_embd=256, n_layer=4, n_head=4, layer_norm_epsilon=1e-5`.

**Trình tự kiểm tra kỹ thuật T2 (Technical Sequence, không phải thực nghiệm khoa học):**
1. Không dùng dữ liệu TinyStories: instantiate random P02 theo pinned seed, fixture 8 chuỗi token IDs (ngắn/dài/context, ASCII+Unicode qua tokenizer fixture) và 16 greedy steps.
2. Thử export GGUF `F32` trước, `F16` sau, pin compiler/gguf/llama.cpp build; check tensor count, dtype, shape, tied weights, tokenizer IDs. Compare PyTorch vs llama.cpp logits trên **cùng token IDs/position IDs**, cả full-context và prefilling.
3. Mục tiêu ban đầu `F32 max_abs_logits <= 1e-3`, `F16 <= 2e-2`, 100% token-ID equality trong fixture. Khi top-1 logit margin nhỏ hơn `2*max_abs_logits`, greedy divergence được ghi `NUMERIC_TIE_AMBIGUOUS` và đánh giá logits; không được che discrepancy. Thresholds này phải lock **trước khi chạy T2** và không thay sau thấy lỗi.
4. T2 chỉ PASS nếu backend thực sự load/calculate đúng, tokenizer encode/decode/tensor parity PASS, không chỉ tạo .gguf. Nếu chưa PASS: `EXPORT_FEASIBILITY_HOLD`, sửa **adapter/backend** theo branch kỹ thuật, không sửa kiến trúc P02; không cho phép train dài.
5. Sau actual TRAIN-only tokenizer frozen, lặp lại kiểm token-ID parity **trước** science; vì fixture tokenizer synthetic không thể thay bằng chứng tokenizer thật.

**Nguồn code:** https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/conversion/gpt2.py ; https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/models/gpt2.cpp ; https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/gguf-py/gguf/tensor_mapping.py.

## G. Điểm lưu mô hình (Checkpoint), Google Colab/Drive, phục hồi (Resume) và thứ tự công việc

- `MyDrive/TTM/ttm-small-pilot/<run-id>` chỉ khi Colab có xác thực người dùng; không ghi bí mật lên repo. Notebook và `requirements.lock` cần pin version trước chạy.
- Checkpoint state gồm weights/model config, optimizer, scheduler, GradScaler (khi AMP), step, exact token cursor/permutation và global token count, tokenizer+data manifest SHA, seed + Python/NumPy/Torch/CUDA RNG, Git SHA/version runtime. Lưu snapshot trên ephemeral disk, SHA256, copy lên Drive theo thư mục immutable, readback verify từng file, ghi `READY.json` cuối. Drive mount không được giả định rename là atomic.
- Bài kỹ thuật T3 `20 continuous steps vs 10-save/resume-10` trên **synthetic tokens**, cùng GPU/runtime/dtype; chọn ngưỡng và kiểm tra parity gradient/weights/cursor/optimizer trước science. Không dùng TEST hoặc sửa science history.
- Không tự thay session/seed/corpus sau colab disconnect; resume từ checkpoint READY mới nhất. Partial checkpoints bỏ qua, không retune theo VAL.

## H. Cổng quyết định tổng hợp

| Cổng | Kết luận hiện tại | Bằng chứng cần để được khóa |
|---|---|---|
| Git/P02 | `PASS_EXACT_SOURCE_REVIEW` | P02 Git blob, nhánh PR #12 chỉ docs |
| Phiên bản nguồn HF (Source Revision) | `PASS_PINNED_REVISION` | 40-char HF commit ở mục A |
| Dữ liệu + quyền | `PASS_LICENSE_REVIEW_WITH_CONDITIONS` | Source card, official license; before TRAIN still need bytes SHA, PII, sampling/parser receipts |
| Split + tokenizer | `PASS_DESIGN_NOT_EXECUTED` | raw parser, exact SHA/near-dup audit, BPE export parity |
| Model + budget + metrics | `PASS_CANDIDATE_PREREG_DESIGN` | final lock độ chính xác số (Precision)/lô nhỏ (Microbatch) + compute synthetic benchmark trước science |
| Bộ thực thi GPT-2 của llama.cpp (Backend) | `PASS_SOURCE_REVIEW` | source pinned and tensor mapping candidate |
| **GGUF real conversion** | `NOT_EXECUTED` | T2 F32/F16 logits/token ID parity |
| Colab/Drive/resume | `NOT_EXECUTED` | T3 synthetic parity + Drive READY |
| **FINAL SCIENCE LOCK** | **`HOLD`** | các mục bytes/source/split/export/resume/resource; không chạy huấn luyện dài (Long Training) |

**Lộ trình lượt chạy (Run) ngắn nhất**: (1) T2 random+synthetic tokenizer route export feasibility (không cần TinyStories), (2) T1 file/source sampling+split/BPE once, (3) T2 actual tokenizer parity, (4) T3 synthetic Colab checkpoint/benchmark, (5) khóa tiền đăng ký tổng hợp (Integrated Preregistration Lock) một lần, (6) T4 train, (7) T5/6 so sánh. Không lập permit kỹ thuật từng hạng mục. Không merge PR #12 chỉ vì rà soát nguồn (Source Review) PASS.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_T2_GGUF_SYNTHETIC_EXPORT_CPU_IMPLEMENTATION_AND_INTEGRATED_QA`; chỉ implement + chạy fixture zero-science theo ngưỡng đã khóa, giữ source science và dataset/test chưa đụng.
