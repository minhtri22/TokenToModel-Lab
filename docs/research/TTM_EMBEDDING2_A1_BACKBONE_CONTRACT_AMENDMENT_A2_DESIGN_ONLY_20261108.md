# TTM — A2: Đính chính mô hình nguồn và hợp đồng backbone / đối chứng

**Công việc:** `TTM_EMBEDDING2_A1_BACKBONE_CONTRACT_AMENDMENT_A2_DESIGN_ONLY`  
**Ngày:** 2026-11-08  
**Tình trạng:** `DESIGN_ONLY / TARGET_IDENTITY_CORRECTED / INTEGRATED_REVIEW_PENDING`  
**Đối tượng Google đúng do chủ dự án xác nhận:** **`google/embeddinggemma-2`** trên Hugging Face: https://huggingface.co/google/embeddinggemma-2  
**Mô hình đã bị hiểu nhầm trong các hồ sơ trước:** `gemini-embedding-2` **qua Google Gemini API**, **KHÔNG** phải mục tiêu nghiên cứu này.  
**Repository TTM:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh đang giữ nguyên tên lịch sử:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`  
**HEAD trước A2:** `db01d8d14b9a88001c8e5dc393e7676b9588837a`  
**Main đã xác minh:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.

> **Phạm vi:** Đây là một phụ lục A2 duy nhất ghi nhận việc sửa **nhận diện mô hình** và năm thiếu sót của A1. Không sửa/xóa lịch sử A0/A1/đính chính Free Tier/backbone review; không sửa tên nhánh, mã nguồn, mô hình/checkpoint, P00–P12, P07, T1–T7, PR #12 hoặc `lineage.md`; không tải mô hình, không gửi yêu cầu API, không chạy GPU/dataset/QA động/TEST, không huấn luyện, không merge, không đụng máy Windows. **Không cấp quyền D1–D4.**

## 1. Đính chính căn bản và tính hiệu lực hồ sơ lịch sử

**Kết luận nguồn:**
- `google/embeddinggemma-2` là mô hình embedding **trọng số công khai (open-weight)**, giấy phép công bố **Apache-2.0**, chạy inference cục bộ/offline sau khi có trọng số và môi trường phù hợp. Nó **không** phải Gemini Embedding 2 được gọi qua API.
- Tổng mô hình đa phương thức khoảng **740M** tham số (model implementation ghi **744,371,488**). Chỉ sử dụng **văn bản/mã nguồn** thì bỏ qua encoder ảnh/âm thanh, xấp xỉ **270M** tham số; ảnh thêm ~170M; âm thanh thêm ~300M.
- Output native **768 chiều**; Matryoshka hỗ trợ **512/256/128 chiều** sau cắt và **chuẩn hóa L2 lại** để dùng cosine similarity. Giới hạn ngữ cảnh embedding text **8.192 token**. Mô hình embedding tạo biểu diễn pooled, **không** phải một language-model head sinh token theo kiểu GPT.
- EmbeddingGemma 2 **bản thân sử dụng GQA/MQA** bên trong encoder, nhưng điều này **không** biến attention của Qwen/Pythia thành một thí nghiệm MHA-vs-GQA, cũng không biến cache embedding thành PagedAttention. Paged KV của decoder sinh văn bản là nghiên cứu inference riêng.
- **Yêu cầu số học quan trọng từ Google:** inference embedding dùng **BF16 hoặc FP32**, **KHÔNG dùng FP16**; FP16 có thể sinh NaN hoặc vector âm thầm sai. Colab Tesla T4 (Turing) không có BF16 native phù hợp để giả định mặc định; phương án thiết kế an toàn cho EmbeddingGemma 2 trên T4 là **FP32**, còn dtype của Qwen/Pythia được xác định **riêng**.
- Khi làm RAG, dùng prefix task cho query và document (ví dụ `QuestionAnswering` cho truy vấn và `Document` hoặc `title: {title} | text: {content}` cho văn bản). Mỗi chunk tạo vector riêng, tránh nhầm nhiều chunk vào một pooled vector.
- Model card còn nêu **Gemma Prohibited Use Policy**; trước sử dụng thực tế phải rà soát cả license, chính sách sử dụng và quyền đối với corpus. Không coi "Apache-2.0" là tự động cấp mọi quyền dữ liệu.

**Bằng chứng chính thức (đã đọc 2026-11-08):**
- Google model card: https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2
- Hugging Face: https://huggingface.co/google/embeddinggemma-2
- Google developer guide (2026-10-06): https://developers.googleblog.com/embeddinggemma-2-the-developer-guide/
- Google Sentence Transformers: https://ai.google.dev/gemma/docs/embeddinggemma/multimodal-embeddinggemma-with-sentence-transformers
- Bài nghiên cứu Google: https://deepmind.google/research/publications/279443/

**Những dòng trong tài liệu A0/A1 cũ không còn đúng cho mục tiêu thật:**
- Mọi `MODEL_ID=gemini-embedding-2`, thông tin "Google API service" và giấy phép/quota của **Gemini API Free Tier** được đánh dấu `SUPERSEDED_BY_A2_TARGET_CORRECTION`, không dùng làm điều kiện hoạt động của EmbeddingGemma 2.
- `TARGET_GEMINI_API_SPEND_USD=0` được hiểu lại: **API không thuộc đường thực thi dự kiến**; mô hình chạy cục bộ. Chi phí gọi API bên ngoài mục tiêu **$0**, nhưng tải checkpoint, ổ đĩa, mạng, CPU/GPU, Colab, điện, cache và training **không tự động bằng $0**.
- Việc có chính sách "Free Tier dữ liệu dùng để cải thiện sản phẩm" của **Gemini API** **không** có nghĩa văn bản đưa vào EmbeddingGemma 2 chạy cục bộ bị gửi tới Google. Cần chặn telemetry/remote calls ngoài ý muốn và xác minh quy tắc dữ liệu của pipeline được triển khai.
- A1 còn ghi `d_model=256, vocab=2048, context=256` theo TTM-Small; **không dùng chúng** cho Qwen/Pythia. Chỉ **chiều embedding đầu ra 768** của EmbeddingGemma 2 là thông số Google phù hợp để dự kiến tensor fusion.

Các tài liệu cũ được **giữ nguyên mã băm** như lịch sử giả định sai; A2 là văn bản sửa có hiệu lực ưu tiên để định hướng các tài liệu kế tiếp. Tên nhánh Git chứa từ "gemini" là di sản lịch sử, **không** phải tên model đúng; không tự rename vì nhánh hiện có tài liệu và mốc đọc lại. Việc tạo nhánh/tên sạch hơn cần quyết định quản trị riêng.

## 2. Backbone-specific contract (sửa thiếu sót A1-F3)

| Trường | `EleutherAI/pythia-160m-deduped` | `Qwen/Qwen2.5-0.5B-Instruct` |
|---|---|---|
| Vai trò | đối chứng GPT-NeoX pretrained, nghiên cứu representation | ứng viên chính instruction-tuned cho R_gold/RAG/Adapter |
| `architecture` | `GPTNeoXForCausalLM` | `Qwen2ForCausalLM` |
| `n_layers` | 12 | 24 |
| `d_model` | **768** | **896** |
| `n_query_heads` | 12 | 14 |
| `n_kv_heads` | 12 (MHA) | 2 (GQA) |
| `config_context` | 2048 | 32768 |
| `config_vocab` | 50304 | 151936 |
| Tokenizer | GPT-NeoX BPE, policy special IDs từ pinned revision | Qwen tokenizer, chat template/role tokens/EOS từ pinned revision |
| Input embedding Google | `[B,m,768]` native | `[B,m,768]` native |
| Adapter output | `[B,m,768]` | `[B,m,896]` |
| Backbone hidden | `[B,T,768]` | `[B,T,896]` |
| LM logits | `[B,T,50304]` | `[B,T,151936]` |

Cả hai là **ứng viên nguồn metadata**, chưa tải/khóa HF revision tuyệt đối. Trước chạy phải pin đúng 40-char commit SHA, checksum weights/config/tokenizer/chat_template, phiên bản thư viện và precision; không coi `main` HF là khóa. Giấy phép công bố của cả hai là Apache-2.0; review obligations theo exact version và nguồn dữ liệu riêng.

**Giới hạn thực (`L_eff`):** `min(model-config-context, runtime-supported-context, measured-resource-cap, prereg-approved-context)`. Với Pythia/Qwen, `S_SHORT/S_LONG` xác định **theo tokenizer, chat template, L_eff của từng backbone** (không dùng mặc định 256). Nếu cần đối chứng chung giữa hai backbone, định nghĩa một tập giao dựa trên khả năng chứa đầy đủ bằng chứng của **cả hai**, báo cáo riêng các tập model-specific; **không** so sánh absolute NLL/token giữa hai tokenizer khác nhau.

## 3. Fairness R3/R4/V1 và hai estimands (sửa thiếu sót A1-F1/F2)

**Giữ hai câu hỏi tách biệt:**
- `E_SYS`: `R3` (text-RAG + frozen backbone) so `V1` (EmbeddingGemma 2 vectors + trainable Adapter/Cross-Attention trên **cùng frozen backbone**). Đây là **chất lượng tổng hệ thống**, không gán chênh lệch cho riêng biểu diễn.
- `E_REPR`: `R4` (text representation từ **frozen non-EmbeddingGemma encoder** theo chunk + trainable Adapter/Cross-Attention) so `V1` (EmbeddingGemma 2 per-chunk vectors + **cùng loại** Adapter/Cross-Attention, cùng frozen backbone, budgets, split, targets). Đây là **so sánh pipeline biểu diễn**, không chứng minh thuần túy EmbeddingGemma 2 tốt hơn do chỉ một yếu tố.

**Ma trận sửa:**
| ID | Evidence / model | Backbone + training | Ý nghĩa |
|---|---|---|---|
| R0 | Không evidence | frozen Qwen hoặc frozen Pythia | Nền |
| R_gold | Evidence đúng từ diagnostic riêng dưới context | cùng frozen backbone | Năng lực sử dụng bằng chứng |
| R1 | BM25/lexical → nguyên văn | frozen backbone | Retrieval đơn giản |
| R2 | EmbeddingGemma 2 **offline retrieval** → nguyên văn | frozen backbone | Giá trị retrieval offline |
| R3 | **Chính các doc IDs R2 đã khóa** → text prompt | frozen backbone | Text baseline cho E_SYS |
| R4 | **Cùng doc IDs/source bytes** → frozen text encoder KHÔNG EmbeddingGemma 2 → vectors per chunk | trainable fusion, frozen backbone, matched R4/V1 budgets | Đối chứng biểu diễn cho E_REPR |
| V1 | **Cùng doc IDs/source bytes** → EmbeddingGemma 2 text-only → vectors per chunk | trainable fusion, frozen backbone, matched R4/V1 budgets | Đề xuất |
| V2a | V1 đã train, tráo/random vectors lúc đánh giá | không retrain | Kiểm tra phụ thuộc đúng evidence |
| V2b | Train lại với vector random/tráo theo rule định trước | cùng budget, capacity | Negative control |
| V3 | Vector EmbeddingGemma 2 đúng, fusion không attention | capacity/budget báo cáo tách | Chẩn đoán giá trị Cross-Attention |
| I1/I2 | Same evidence | MHA/GQA hoặc dense/paged được đánh giá **riêng** | Không dùng làm H1 semantic |

**R4 tối thiểu:** encoder text không dùng Google embedding (ứng viên: frozen token embeddings/pooled hidden states của **chính backbone được chọn**, không mượn TTM-Small). Chọn 1 encoder chính trước thí nghiệm; matching **trainable parameter count** không matching độ mạnh tiền huấn luyện của encoders. Nếu R4 dùng mean pooling kém chất lượng, ghi rõ **weak control**; không dùng V1>R4 để claim cải tiến do Cross-Attention. Có thể thiết kế stronger-text-encoder sensitivity khi có nguồn/quyền/budget riêng. Tránh thêm trainable projection chỉ ở một nhánh: nếu kích thước nguồn khác, dùng deterministic fixed dimensional bridge hoặc báo cáo sai lệch chính xác.

**Matched contract:** cùng frozen backbone checkpoint, evidence IDs & bytes, source documents, chunk count/order, answer targets, grouping, optimizer/steps/seed/early stopping, adapter placement, gate, mask, training examples và selection rule. Nếu trainable params/compute khác, báo `ATTRIBUTION_LIMITED` thay vì PASS nhân quả.

**Thông tin không ngang bằng:** Văn bản raw đi qua context backbone; vector đi qua kênh ngoài context. Phép thử E_SYS chấp nhận đánh giá lợi ích tổng, còn E_REPR chỉ thực hiện nếu có cơ chế đối chứng/kế toán capacity đã pin.

## 4. R_gold: cổng năng lực nền (sửa thiếu sót A1-F4)

- `R_gold` là **positive control** (không phải deployment oracle), cùng checkpoint/tokenizer/target giữa `R0` và `R_gold`. Evidence đúng được đưa bằng **văn bản gốc** một cách hợp lệ trong S_SHORT.
- Chẩn đoán trên tập riêng/VALID với tài liệu và mẫu trả lời có quyền sử dụng; khóa `N_samples`, phép chọn nhóm, prompt template, `NLL(R0)-NLL(R_gold)`, rubric accuracy và `minimum_competence_threshold` **trước chạy**, không tạo giá trị PASS tại A2.
- Gồm negative control evidence không liên quan/evidence sai, và ít nhất một kiểm tra forced-choice/Exact Match ngoài NLL; kiểm tra model có "dùng" evidence chứ không chỉ có loss thấp do format.
- Trên cùng backbone, nếu ngưỡng không đạt → `MODEL_CAPABILITY_GAP`, dừng admission D1 cho backbone đó; không phán quyết embedding/fusion FAIL. Pythia có thể không đạt R_gold mà vẫn dùng trong nghiên cứu dynamics riêng.
- Không dùng gold-doc selection từ nhãn TEST để chỉnh prompt/retrieval. TEST sealed tới khi prereg khoa học chấp thuận.

## 5. S_SHORT/S_LONG và Answer-only NLL (sửa thiếu sót A1-F5/F6)

**Split strata (định tuyến trước đánh giá):**
- Với mỗi backbone, dựng **token IDs thực tế sau chat template**. Gọi `Q_i` là prompt/question+delimiter, `D_i` là toàn bộ chunk text evidence theo thứ tự cố định, `Y_i` là target answer plus EOS/turn end được quy định, `T_eff` là context khả dụng.
- `S_SHORT`: toàn bộ text evidence trong R3 + `Q_i` + toàn bộ `Y_i` vừa `T_eff`; không truncate ở R3. Cùng doc IDs/source bytes giữa R3/R4/V1; so sánh có thể diễn giải phần lợi ích hệ thống không do buộc text bỏ bằng chứng.
- `S_LONG`: text path không chứa hết `Q+D+Y`; truncate evidence theo quy tắc cố định **không nhìn đáp án/nhãn** và dành chỗ cho answer. Side-channel V1/R4 có thể nhận nhiều hơn; đây là **lợi thế kênh ngoài context**, không gọi cùng ngân sách thông tin. Báo cáo tách; nếu `Q+Y` đã vượt context thì đánh dấu invalid theo quy tắc đã khóa.
- Định tuyến S_SHORT/S_LONG **theo tokenizer/context từng backbone**, và thêm intersection group khi báo cáo chéo backbone. `embedding_model_max_input=8192` là giới hạn encoder **riêng**, không thể dùng nó thay context Qwen/Pythia. Nếu một doc/chunk vượt giới hạn EmbeddingGemma phải split theo policy khóa, không im lặng cắt mà vẫn báo same source.

**Scoring definition (một backbone, trong một điều kiện):**
1. Khóa prompt template, special delimiters, system/user/assistant turn policy, BOS/EOS và **vị trí bắt đầu answer trong dãy token ID**. Không giả định `encode(answer)` một mình khớp suffix khi tokenizer BPE merge qua biên `prompt|answer`.
2. Chọn một hợp đồng duy nhất cho mọi R3/R4/V1 trên cùng backbone: **tokenize prompt như chuỗi tiền tố hoàn chỉnh**, tokenize answer với chính sách `add_special_tokens` và separator đã khóa, **ghép token IDs rõ ràng** để làm teacher forcing; hoặc dùng tokenize full string kèm offset/alignment được xác minh độc lập. Nếu dùng ghép IDs, nêu rõ đây là phân phối có delimiter/tokenization policy xác định, không được giả vờ là tokenization toàn văn nguyên trạng.
3. Cho `input_ids=[P_1,...,P_p,Y_1,...,Y_a]`, `causal logits[t]` dự đoán `input_ids[t+1]`. Đánh nhãn `-100` cho mọi vị trí ngoài **target answer**; phải bảo đảm token `Y_1` dự đoán từ vị trí cuối cùng của prompt, không dự đoán từ bản thân `Y_1`, và không làm rò future target.
4. `answer_only_NLL_i = -\sum_{j=1}^{a}\log p(Y_j | P,Y_{<j},evidence)/a`. Đối chứng R3/R4/V1 **trong cùng backbone** dùng cùng token IDs cho answer và cùng số answer tokens; không lấy prompt NLL hoặc perplexity chéo tokenizer thay thế.
5. Nếu full answer vượt `T_eff`, áp dụng policy cửa sổ được prereg **hoặc đánh dấu invalid**, không lặng lẽ chỉ tính phần answer dễ. Giữ per-example log-prob, total NLL, answer token count, group ID, paired `delta_SYS=R3-V1` và `delta_REPR=R4-V1`.
6. Bootstrap paired theo **source/document group** để không coi multiple tokens/paraphrases là quan sát độc lập. `delta_min`, số seed, mẫu, CI và ngưỡng PASS/FAIL **chưa khóa** và phải được review trước khi chạy khoa học.

## 6. Adapter, gate và leakage (sửa thiếu sót A1-F7/F8)

- Tensor V1: `evidence_vec:[B,m,768]` (EmbeddingGemma 2 native) `→ trainable_adapter:[B,m,d_model]`, `Q=hidden:[B,T,d_model]`, `K,V=projected_evidence` + valid mask, residual gate. `d_model=896` cho Qwen, 768 cho Pythia.
- Chốt **vị trí chèn Adapter (sau block hoặc trước LM head), số cross-attention heads, norm, gate, padding masks, empty evidence behavior, dropout, trainable-param count, optimizer, freeze policy, train steps/seed/capacity** trước science; tất cả mới là thiết kế, chưa implement.
- `gate=0` để kiểm logits parity với frozen backbone là **fixture kỹ thuật**. Với `output=H + gate*F_{adapter}(H,E)`, tại `gate=0` gradient đến trọng số Adapter lúc đầu có thể bằng 0. Vì vậy training init cần **small-nonzero gate** hoặc **staged training** được định trước; không dùng gate=0 rồi nhận vơ nhánh học đã có gradient. Ghi riêng `PARITY_MODE` và `TRAIN_MODE`.
- Kiểm tra các case `m=0` (no NaN, fallback), `m=1` (không tuyên bố chọn evidence vì softmax 1 key), `m>1` (mask từng chunk), shuffled vectors, wrong doc IDs, gate ablation và no-update frozen backbone.
- **Leakage:** mọi vector EmbeddingGemma từ tài liệu nguồn hợp lệ có trước câu hỏi/target; không encode `question + true answer` hoặc full future suffix rồi truyền vào GPT; cấm TEST trong train adapter, retrieval tuning, index selection, prompt calibration. TRAIN/VAL/TEST tách theo source-group + dedup/near-dup, metadata/title không chứa label ẩn. Evidence tự nhiên chứa thông tin đáp án hợp lệ **không phải** leakage nếu đúng điều kiện bài toán và cùng nguồn cung cấp cho các đối chứng.
- Kế hoạch inference: EmbeddingGemma 2 **frozen**; có thể encode/cached vectors **trước** huấn luyện Adapter, trên bộ dữ liệu được phép, version/hash/policy pinned. Nếu cache bị trộn model revision, truncate_dim, prompt_name hoặc source split thì `HOLD_VECTOR_LINEAGE`.

## 7. Colab Tesla T4: hợp đồng năng lực và độ chính xác — KHÔNG chạy

- EmbeddingGemma 2 **text-only ~270M FP32 weights ~1.08 GB (~1.01 GiB)**; bản full multimodal ~740M FP32 weights ~2.96 GB (~2.76 GiB). Đây là **ước lượng trọng số**, không phải peak VRAM.
- Qwen2.5-0.5B ~0.49B ở FP16 weights ~0.99 GB; Pythia 162M ở FP16 weights ~0.325 GB. Các ước lượng này **không** bao gồm activations, CUDA/runtime, optimizer, cache, training, KV, dữ liệu và mức VRAM khả dụng của phiên Colab.
- **Chặn FP16 EmbeddingGemma 2:** theo model card Google có thể NaN/degrade. Trên Tesla T4, thiết kế text encoder ưu tiên **FP32**; **không mặc định BF16** vì T4 không có native BF16 phù hợp. Dtype Qwen/Pythia có thể chọn độc lập (FP16/FP32 sau technical capacity). Đừng dùng FP16 default của backend để vô tình cast EmbeddingGemma 2.
- Tuyến giảm VRAM ưu tiên: dùng **text-only config** `vision_config=None`, `audio_config=None`; encode tài liệu offline trước rồi dùng **cache vector frozen** hợp lệ cho adapter train; hoặc dùng CPU/GPU tuần tự, không bắt cả embedding encoder và GPT backbone thường trú T4 nếu không cần.
- Việc dùng vector 256 thay 768 **không** làm giảm tham số encoder; chỉ giảm vector storage/adapter size, cần đặt ablation riêng và chuẩn hóa L2 sau truncate.
- Để huấn luyện Adapter thực sự sau này: synthetic zero-science capacity smoke, microbatch 1, context giới hạn được khóa, đo peak VRAM/latency/gradient/resume. Chưa có phép đo nào; `T4_CAPACITY=NOT_ESTABLISHED`.

## 8. GGUF, GQA và PagedAttention: không đồng nhất các tầng

- GGUF/llama.cpp hỗ trợ một số mô hình generative gốc Qwen2 và GPT-NeoX; adapter Cross-Attention tùy biến trên Qwen/Pythia **không** mặc nhiên xuất sang GGUF hoặc chạy Ollama. Semantic experiment nên dùng PyTorch reference; `FUSED_GGUF=UNESTABLISHED`.
- EmbeddingGemma 2 có thể chạy qua Python/SentenceTransformers ở local; **không khẳng định** bản GGUF/llama.cpp cho đúng revision embedding/pooling/task prefixes tương đương, trừ khi được kiểm numerical embedding parity trên successor riêng.
- GQA/MQA bên trong EmbeddingGemma 2 khác GQA decoder của Qwen. Không so Pythia MHA vs Qwen GQA để suy ra tác dụng GQA; phải có đối chứng same-model hợp lệ sau này.
- PagedAttention quản lý cache KV của decoder và phục vụ suy luận; nó **không làm vector ngữ nghĩa chất lượng hơn**. TTM P07 vẫn `PAUSED_PRESERVE`; không mở P08 hoặc sửa code core vì A2.

## 9. Điều kiện thẩm định tích hợp A2 — hữu hạn, không micro-permit

| Mã | Tiêu chí chỉ thiết kế | A2 hiện tại |
|---|---|---|
| A2-01 | Target sửa thành `google/embeddinggemma-2`, model local + Apache-2.0 + usage policy | `DOCUMENTED_REVIEW_PENDING` |
| A2-02 | Không còn chi phí/quota Gemini API là blocker chính; resource/rights local riêng | `DOCUMENTED_REVIEW_PENDING` |
| A2-03 | Hợp đồng tokenizer/d_model/vocab/context theo Qwen/Pythia, không ép 256 | `DOCUMENTED_REVIEW_PENDING` |
| A2-04 | R3/R4/V1 matched evidence/adapter budgets; E_SYS/E_REPR tách rời | `DOCUMENTED_REVIEW_PENDING` |
| A2-05 | R_gold chẩn đoán riêng + năng lực tối thiểu prereg, không TEST peek | `DOCUMENTED_REVIEW_PENDING` |
| A2-06 | S_SHORT/S_LONG theo tokenization/context từng backbone | `DOCUMENTED_REVIEW_PENDING` |
| A2-07 | Answer-only NLL đúng shift/boundary/mask, paired group scoring | `DOCUMENTED_REVIEW_PENDING` |
| A2-08 | Adapter gate parity vs train init; frozen weights gradient; leakage controls | `DOCUMENTED_REVIEW_PENDING` |
| A2-09 | EmbeddingGemma FP16 **forbidden**, FP32 T4 và local text-only cache | `DOCUMENTED_REVIEW_PENDING` |
| A2-10 | GQA/PagedAttention và GGUF fusion được phân tách, không lạm quyền P07 | `DOCUMENTED_REVIEW_PENDING` |

**Phán quyết của bước viết tài liệu:** `A2_WRITTEN_NOT_ADJUDICATED`, `TARGET_MODEL_ID_CORRECTED`, `EXECUTION_NOT_AUTHORIZED`. Review A2 có thể ACCEPT/REVISE/HOLD cho **thiết kế** mà không mở D1, và vẫn cần checkpoint, quyền corpus, snapshot model, capacity smoke và prereg khoa học trước phép chạy thật.

## 10. Bước thực hiện tiếp theo

`TTM_EMBEDDINGGEMMA2_A2_INTEGRATED_INDEPENDENT_DESIGN_REVIEW_READONLY`: đọc A2 như hồ sơ đính chính nguồn chính thức, đối chiếu Google model card và source TTM, kiểm contract Qwen/Pythia, R_gold, R3/R4/V1, precision FP32, local-only data policy, GQA/PagedAttention và GGUF. Chỉ quyết định thiết kế `ACCEPT/REVISE/HOLD`. Không tải weights, không gọi API, không code/training, không merge, không sửa khoa học/lineage. Tuyến TTM-Small T4 tiếp tục độc lập theo PR #12.
