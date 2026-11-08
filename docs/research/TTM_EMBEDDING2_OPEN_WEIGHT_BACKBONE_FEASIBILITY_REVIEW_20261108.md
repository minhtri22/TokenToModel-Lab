# TTM — Đánh giá khả thi mô hình nền trọng số công khai cho Gemini Embedding 2

**Mã công việc:** `TTM_EMBEDDING2_OPEN_WEIGHT_BACKBONE_FEASIBILITY_REVIEW`  
**Ngày:** 2026-11-08  
**Phán quyết:** `DESIGN_FEASIBLE_WITH_CONDITIONS`; `PREFERRED_BACKBONE=Qwen/Qwen2.5-0.5B-Instruct`; `SECONDARY_RESEARCH_CONTROL=EleutherAI/pythia-160m-deduped`; `EXECUTION_AUTHORIZATION=NONE`  
**Phạm vi:** Thiết kế và rà soát chỉ đọc metadata/cấu hình/model card, **không tải trọng số/checkpoint**, không gọi Gemini API, không chạy thử dữ liệu, mô hình, GPU hay huấn luyện.  
**GitHub repo:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh nghiên cứu:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`  
**HEAD trước thay đổi:** `d6fe159b2ab32ac7ff9df9db6c58d76437f9976a`  
**Main đã đọc:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`  
**TTM-Small:** PR #12 tiếp tục độc lập ở nhánh `research/ttm-small-4m-colab-pilot-prereg-20261108` (tại lần kiểm tra: vẫn `open/draft`). Không sửa hoặc mượn dữ liệu/permit/nguồn của PR #12.

## 1. Câu hỏi và quyết định giữ ranh giới

**Câu hỏi khả thi:** Dùng một mô hình GPT-like có trọng số công khai, đã tiền huấn luyện, làm backbone đóng băng có giúp kiểm tra R_gold/R3/R4/V1 của nghiên cứu Gemini Embedding 2 mà không phải đợi TTM-Small-4M có khả năng hỏi đáp hay không?

**Quyết định thiết kế:**
- **Qwen2.5-0.5B-Instruct:** ứng viên chính, vì có huấn luyện chỉ dẫn (Instruction tuning) và có GQA gốc; vẫn phải có R_gold đạt năng lực thực tế trước khi suy ra có thể thử RAG.
- **Pythia-160M-deduped (bản retrained, KHÔNG phải `-v0`):** mô hình đối chứng nghiên cứu GPT-NeoX/MHA; có checkpoint trung gian để khảo sát biểu diễn và động lực học. Không giả định khả năng QA của mô hình pretrained này tương đương bản Instruct của Qwen.
- **TTM-Small-4M:** tiếp tục theo pipeline T1–T7 độc lập, ưu tiên T4 khoa học; **không** thay TTM P02, P05–P08 hoặc kết quả đã khóa. Kết quả một nghiên cứu sử dụng Qwen/Pythia không tự động là kết quả cải thiện TTM-Small.
- **GPT-3 OpenAI gốc:** không có checkpoint 175B được phát hành để dùng trong nghiên cứu này; không lấy repository tài liệu GPT-3 làm bộ trọng số.
- **Gemini API:** `gemini-embedding-2`, `STANDARD_FREE_TIER_FIRST`, `TARGET_GEMINI_API_SPEND_USD=0`; không có Paid fallback, không gọi trong pha design.

## 2. Nguồn và giấy phép (đọc không tải mô hình)

| Trường | Pythia-160M-deduped | Qwen2.5-0.5B-Instruct |
|---|---|---|
| Repo chính thức | `EleutherAI/pythia-160m-deduped` | `Qwen/Qwen2.5-0.5B-Instruct` |
| URL | https://huggingface.co/EleutherAI/pythia-160m-deduped | https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct |
| Giấy phép công bố | Apache-2.0 | Apache-2.0 |
| Kiểu kiến trúc | `GPTNeoXForCausalLM` | `Qwen2ForCausalLM` |
| Quy mô theo model card | 162,322,944 tham số | ~0.49 tỷ tham số |
| Layers | 12 | 24 |
| `hidden_size` | 768 | 896 |
| Attention | MHA: 12 Q / 12 KV heads (suy ra khi không có GQA) | GQA: 14 Q / 2 KV heads |
| Max context trong `config.json` | 2.048 | 32.768 |
| Vocab cấu hình | 50.304 | 151.936 |
| Vị trí | GPT-NeoX, RoPE một phần (rotary_pct=0.25), GELU | Qwen2, RoPE, RMSNorm, SwiGLU |
| Khả năng theo model card | Pretrained causal language model, nghiên cứu learning dynamics | Instruction-tuned causal language model, chat template |
| Checkpoint trung gian | Có nhiều revision `step...` | Không dùng checkpoint trung gian làm điều kiện dựa trên card hiện tại |
| Mục đích chính | Quan sát/đối chứng kiến trúc | R_gold, RAG, thử semantic Adapter |

**Lưu ý provenance:** `pythia-160m-deduped-v0` là bản cũ; nghiên cứu này chọn **không `-v0`**. Model card Pythia hiện hành nêu 154 checkpoint/revision theo quá trình học, bao gồm `step0` và `step143000` bằng main. Card nêu tổng tham số 162,322,944; một giao diện metadata thứ cấp có thể báo count khác, nên **khóa kiểm đếm tensor thực tế** sau khi được phép tải model, không dùng số từ công cụ metadata thay cho hồ sơ model card.

**Chưa khóa revision tuyệt đối:** ở bước design này chỉ xác nhận tên repo và các tệp metadata công khai. Trước bất kỳ download/execution phải lấy commit SHA 40 ký tự của HF, hash config/tokenizer/tokenizer_config/model weights/safetensors index, đối chiếu giấy phép ở exact revision, and version `transformers`. Không dùng `main` động như định danh thí nghiệm.

Nguồn:
- https://huggingface.co/EleutherAI/pythia-160m-deduped
- https://huggingface.co/EleutherAI/pythia-160m-deduped/blob/main/config.json
- https://github.com/EleutherAI/pythia
- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/raw/main/config.json
- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/raw/main/tokenizer_config.json

**Quyền:** Apache-2.0 cho trọng số/mã do chủ sở hữu cung cấp không tự giải quyết bản quyền/PII của bộ dữ liệu benchmark, hoặc điều khoản tái sử dụng embedding Google. Khi phát hành phải có attribution, copyright/license notice và kiểm tra các yêu cầu phân phối liên quan. Chưa kết luận thương mại sẵn sàng.

## 3. Tokenizer, template và chỉ số đối chứng

- **Pythia:** tokenizer GPT-NeoX BPE riêng (~50.304 vocab theo model config), pretrained completion, không có chat instruction format tương đương Qwen.
- **Qwen:** tokenizer Qwen2 với special tokens (đặc biệt `<|im_start|>`, `<|im_end|>`) và chat template. Model config 151.936 vocab; template, EOS, tokenizer normalization, IDs/attention mask phải được khóa riêng. Không được chấm trực tiếp trên token IDs của TTM-Small 2048 vocab.
- **Quan trọng:** `answer-only NLL` của Qwen/Pythia **không được so số tuyệt đối với nhau** khi tokenizer khác nhau. Chỉ dùng cặp R0/R_gold/R3/R4/V1 **bên trong cùng backbone, cùng tokenizer**, với cùng target answer token IDs. Nếu cần so chéo backbone, dùng độ đúng theo mẫu/câu trả lời, byte-normalized log likelihood với thận trọng, và điều kiện khác biệt mô hình đã công bố.
- Chat template trong Qwen có thể khiến prompt nhiều token hơn; định nghĩa `S_SHORT/S_LONG` bằng tokenizer và **độ dài ngữ cảnh thực của từng backbone**, chứ không áp mặc định 256 token của TTM-Small cho Qwen/Pythia.
- Các `R_gold`/R3/R4/V1 vẫn chia TRAIN/VAL/TEST và không dùng TEST để tune; benchmark/hình thức hỏi đáp phải phù hợp với cả khả năng tạo đáp án và giám sát của backbone ứng viên.

## 4. Adapter / Cross-Attention: tương thích kiến trúc, chưa chứng minh hiệu quả

**Đường tham chiếu D1:** frozen backbone + text RAG. Có thể nghiên cứu trong Hugging Face `transformers` với mẫu prompt cố định, chưa cần adapter.

**Đường D2:** frozen backbone + Gemini embedding `E` theo từng evidence chunk + trainable Adapter/Cross-Attention + gated residual. Các shape ứng viên:

| Tensor | Pythia | Qwen |
|---|---|---|
| `token_ids` | `[B,T]` int64 (GPT-NeoX) | `[B,T]` int64 (Qwen tokenizer) |
| `evidence_vectors` | `[B,m,768]` float, Gemini (ứng viên) | `[B,m,768]` float, Gemini (ứng viên) |
| `projected_evidence` | `[B,m,768]` | `[B,m,896]` |
| `hidden_state` | `[B,T,768]` | `[B,T,896]` |
| `logits` | `[B,T,50304]` | `[B,T,151936]` |

- Không có adapter/cross-attn sẵn trong hai checkpoint; phải implement trên **successor branch riêng** sau thiết kế và cổng khoa học. Không thay mặc định HF architecture dưới tên pretrained gốc.
- Khóa vị trí fusion (sau một block, trong vài block, hoặc trước LM head), các norm, gate, masks, padding, shape, positional semantics và thời điểm evidence hợp lệ. `gate=0` logits phải đối chiếu với backbone frozen trong ngưỡng được đăng ký.
- Không phải vì Qwen có **self-attention GQA** mà cross-attention tự biến thành GQA. Cross-attention có phép chiếu Q/K/V và cache vòng đời riêng; phải định nghĩa riêng. Pythia là MHA, không cần ép GQA để tham gia semantic study.
- Frozen weights không đồng nghĩa **VRAM backward bằng inference**: nếu adapter chen giữa các layer, vẫn cần đồ thị lan truyền gradient qua các phép tính của backbone để học adapter. Đo capacity trước huấn luyện.
- A1 bắt buộc giữ **hai estimands**: `E_SYS: R3 vs V1` (giá trị hệ thống), `E_REPR: R4 vs V1` (giá trị nguồn biểu diễn khi capacity fusion ngang), cùng `V2a/V2b/V3` âm tính. R4 dùng frozen text encoder tương thích với backbone đang được chọn, không dùng token embeddings của TTM-Small theo mặc định.
- `m=1` không thể học lựa chọn giữa nhiều document keys bằng softmax cross-attention; cần `m>1` trước khi claim evidence selection.

## 5. Colab Tesla T4: ước lượng bộ nhớ trên giấy, chưa capacity PASS

Theo thông số NVIDIA, Tesla T4 có **16 GB GDDR6** và hỗ trợ FP16; **không giả định BF16 là dtype tính toán phù hợp** trên Turing T4. Qwen config khai báo `torch_dtype=bfloat16` — thực thi được phép về sau phải lựa chọn FP16 hoặc FP32 có kiểm chứng số học, không tự lấy BF16 làm mặc định.

Ước lượng **chỉ đối với trọng số**, không phải peak VRAM:
- Pythia 162,322,944 tham số × 2 bytes (FP16) = **324,645,888 B ≈ 309.6 MiB**.
- Qwen khoảng 494,000,000 tham số × 2 bytes (FP16) = **988,000,000 B ≈ 942.2 MiB**.
- FP32 tối thiểu khoảng gấp đôi. Quantization 8-bit/4-bit giảm footprint trọng số nhưng có các buffer/overhead khác.

Peak VRAM còn phải cộng activations, attention buffers, CUDA context/kernel cache, KV cache, adapter weights/optimizer/gradients, text encoder/embedding cache, batch/sequence, trong đó backward và context dài có thể chi phối. **16 GB nominal ≠ 16 GB free**. Không khẳng định vừa 32K context hay train adapter thành công chỉ từ phép nhân tham số.

**Quy tắc capacity successor (chưa cho chạy):** nhận diện GPU/VRAM khả dụng, torch/CUDA/dtype/kernel/backend, tải checkpoint theo SHA, chỉ dùng **synthetic zero-science fixture** để khảo sát short-context `T∈{256,512,1024}` nếu đúng giới hạn, microbatch 1 trước, giới hạn RAM/VRAM và an toàn OOM, từ đó mới khóa length/batch/precision/gradient checkpointing/LoRA hoặc adapter budget và giá trị compute cap. Không chạy T4 TTM-Small hoặc dùng permit T3 cho nghiên cứu này.

**Kết luận capacity:** `PAPER_ESTIMATE_PLAUSIBLE`; `COLAB_T4_LOAD=NOT_EXECUTED`; `ADAPTER_BACKWARD_CAPACITY=NOT_ESTABLISHED`.

Nguồn thiết bị: https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/tesla-t4/t4-tensor-core-datasheet.pdf

## 6. GGUF, llama.cpp/Ollama và ranh giới tương thích

- `llama.cpp` hiện có các họ kiến trúc GGUF `GPTNEOX` và `QWEN2`; model card Qwen đưa liên kết tới các bản lượng tử hóa cho llama.cpp/Ollama. Điều này cho thấy **đường export/serve vanilla backbone có cơ sở khả thi**, không phải bằng chứng số học của đúng checkpoint/hardware đã chọn.
- Đối với mô hình **không sửa cấu trúc**, successor sẽ xác minh converter thuộc `ggml-org/llama.cpp` tại commit được pin, tokenizer parity (special IDs/chat template), full/logit parity tại F32/FP16 tùy backend và seeded greedy generation trên bộ prompt thử nghiệm; sau đó mới nói đến Ollama Modelfile.
- Đối với **backbone + Cross-Attention**, exporter vanilla không mặc nhiên hỗ trợ tensor mới, mask, fusion, external embedding và adapter. Nghiên cứu semantic fusion nên bắt đầu với `transformers/PyTorch` làm reference; `FUSED_GGUF_EXPORT=UNESTABLISHED` và `OLLAMA_FUSED_SERVING=UNESTABLISHED`.
- **PagedAttention** là quản lý KV self-attention của inference. Đường paged/dense vẫn là thí nghiệm performance riêng và phải giữ checkpoint, prompt, dtype/hardware; không mượn P07 TTM đang `PAUSED_PRESERVE` để tuyên bố kernel Qwen/Pythia đạt tăng tốc.
- Qwen đã dùng GQA gốc; nó **không** cung cấp đối chứng cùng-trọng-số MHA-vs-GQA. Pythia MHA và Qwen GQA có quá nhiều khác biệt để so thời gian/độ chính xác và kết luận phần chênh do GQA.

Nguồn kiểm tra kiến trúc và converter:
- https://github.com/ggml-org/llama.cpp/blob/master/gguf-py/gguf/constants.py
- https://github.com/ggml-org/llama.cpp/blob/master/gguf-py/gguf/tensor_mapping.py
- https://github.com/ggml-org/llama.cpp/blob/master/convert_hf_to_gguf.py

## 7. R_gold: tiêu chí năng lực trước khi bỏ công nghiên cứu adapter

`R_gold` là phép kiểm **cùng một backbone** với prompt `R0` (không evidence) và `R_gold` (evidence đúng hợp lệ, vừa context) trên **VALID hoặc diagnostic riêng**, không phải công cụ sử dụng nhãn TEST để điều chỉnh.

**Đường kiểm đề xuất (chưa chạy):**
1. Chuẩn bị một tập QA có câu trả lời ngắn, rõ, có phân nhóm tài liệu, bằng chứng văn bản đúng, không nằm trong dữ liệu train của adapter, với nguồn/quyền được duyệt.
2. Mỗi cặp R0/R_gold dùng cùng question, same target text. Scoring là **answer-only teacher-forced NLL** trên cùng token IDs của mô hình đó; có thể bổ sung forced-choice hoặc Exact Match.
3. Khóa negative controls: evidence sai/không liên quan; answer withheld; order permutation không lộ nhãn; prompt template pin. Không lợi dụng gold evidence để chọn retrieved passages trên TEST.
4. `MINIMUM_COMPETENCE_THRESHOLD` và `N_samples` chưa khóa: nếu không cải thiện theo ngưỡng đã duyệt, gắn `MODEL_CAPABILITY_GAP`; không phân loại Gemini Embedding 2 hay Cross-Attention là FAIL.
5. Không dùng cùng ngưỡng NLL/token xuyên hai tokenizer; báo cáo **riêng Qwen và Pythia**. Qwen được thử trước vì instruction-tuned; Pythia có thể FAIL R_gold và vẫn hữu dụng để nghiên cứu learning dynamics.

**Admission logic:** `R_GOLD_PASS + SOURCE_RIGHTS_PASS + FREE_TIER_QUOTA_PASS + DATA_LEAKAGE_QA_PASS + CAPACITY_PASS + SCIENCE_PREREG_PASS` mới là cơ sở xem xét từng authorization cho D1/D2. Một PASS của R_gold **không** cấp quyền huấn luyện adapter tự động.

## 8. Gemini Embedding 2 Standard Free Tier

- Dùng `gemini-embedding-2`, mục tiêu `GEMINI_API_COST_USD=0`, **không** fallback Paid/Batch trả phí.
- Trước bất kỳ API request successor phải xác minh tài khoản/project **thực sự có Free Tier**, quota và điều kiện dừng; xác minh tính hợp pháp của dữ liệu được gửi lên Google, Free Tier có điều kiện xử lý dữ liệu khác trả phí. Không dùng API key ở pha design.
- Đối với RAG Text vs Vector: retrieval phải chọn **cùng doc IDs** cho R3/R4/V1, pin query/document template, dimensions, chunker, index và embed response hash; nếu model endpoint thay đổi vector, báo cáo giới hạn reproducibility.
- Benchmark có thể cần các corpus ngoài TinyStories; license của backbone không phê duyệt corpus. Không tự lấy nguyên bộ TinyStories T1 hoặc đưa lên Gemini bằng quyền pilot cũ.
- Đối chứng `R4` sử dụng text-conditioned frozen representation nên không nhất thiết cần gọi Gemini để đánh giá năng lực backbone/R_gold; tuy nhiên các study so sánh V1/R3 đều cần quyền API/cached vectors riêng.

Nguồn: https://ai.google.dev/gemini-api/docs/pricing ; https://ai.google.dev/gemini-api/docs/rate-limits ; https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2

## 9. Ma trận phán quyết thiết kế (không là science)

| Gate | Phán quyết trên chứng cứ metadata/design | Bước còn thiếu |
|---|---|---|
| `MODEL_SOURCE_AND_LICENSE` | `PASS_DOCUMENTARY_SCOPED` | Pin HF revision/weights/tokenizer + license file exact, chưa download |
| `PYTHIA_ARCHITECTURE` | `PASS_DOCUMENTARY_SCOPED` | Runtime tensor count và tokenizer parity |
| `QWEN_GQA_ARCHITECTURE` | `PASS_DOCUMENTARY_SCOPED` | Runtime readback, dtype và numerical behavior |
| `ADAPTER_INTERFACE` | `DESIGN_PLAUSIBLE` | Chốt vị trí fusion/mask/weights/gradient/path |
| `COLAB_T4_MEMORY` | `WEIGHTS_ESTIMATE_ONLY` | Capacity smoke zero-science sau quyết định riêng |
| `VANILLA_GGUF_CONVERSION` | `ARCHITECTURE_FAMILY_PRESENT_NOT_VERIFIED` | Pin converter và thực hiện tensor/tokenizer/logit parity |
| `FUSED_GGUF` | `NOT_ESTABLISHED` | Runtime/backend hỗ trợ kiến trúc mở rộng, không nằm trong D1 |
| `R_GOLD` | `DESIGN_ONLY_NOT_EXECUTED` | Dataset/threshold/capability preflight |
| `GEMINI_FREE_TIER` | `DESIGN_ZERO_COST_TARGET` | Quota, data rights, terms và project readback |
| `R3_R4_V1_FAIRNESS` | `A1_REVIEW_PENDING` | Independent A1 review và scientific prereg riêng |
| `TTM_SMALL_T4` | `INDEPENDENT_PRIORITY_UNCHANGED` | Theo PR #12, không sửa/khẳng định khoa học hoàn thành |
| `D1_D4` | `NOT_AUTHORIZED` | Cổng phụ thuộc của từng D và quyết định riêng |

**Phán quyết ứng dụng:** `KEEP_QWEN_PRIMARY_CANDIDATE`, `KEEP_PYTHIA_RESEARCH_CONTROL`, `REJECT_CROSS_MODEL_NLL_COMPARISON`, `HOLD_RUNTIME_ADMISSION`. Đây là sự lựa chọn *thiết kế có điều kiện*, không phải chứng minh mô hình nào sẽ cải thiện Gemini-RAG.

## 10. Quản trị Git và bước thực hiện tiếp theo

- Chỉ **thêm tệp đánh giá** trên nhánh Gemini; không sửa các tài liệu A0/A1/Free Tier trước đây, không sửa mã P02, P07, TTM-Small PR #12, `lineage.md`, checkpoint, dữ liệu, Worktree.
- Tài liệu/mốc khoa học append-only: chỉ `lineage.md` khi có phán quyết khoa học thật PASS/FAIL; hồ sơ chỉ thiết kế không được ghi vào scientific lineage.
- Tuyến ưu tiên chính: TTM-Small T4 science-lock/one-shot và T5/T6 theo điều kiện đã duyệt.
- Không tự động cho phép download, API, GGUF conversion, QA động, fine-tune, gradient, D1–D4, hoặc merge.

**Bước thực hiện tiếp theo:** `TTM_EMBEDDING2_BACKBONE_AND_A1_INDEPENDENT_ADMISSION_REVIEW_READONLY` — đọc chéo A1 và tài liệu này, kiểm mâu thuẫn về frozen backbone/R4, tokenization, R_gold, capacity/precision, GGUF và Free Tier; đưa phán quyết `DESIGN_ACCEPT/REVISE/HOLD` chỉ cho giao thức; **không cấp thực thi**. Sau đó mới tính bước successor technical preflight theo phê duyệt cụ thể, không cản tiến độ TTM-Small T4.
