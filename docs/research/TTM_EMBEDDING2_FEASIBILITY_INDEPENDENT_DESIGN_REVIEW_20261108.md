# TTM — Biên bản phản biện thiết kế độc lập theo tiêu chí (Architecture Feasibility Review)

**Mã công việc:** `TTM_EMBEDDING2_FEASIBILITY_INDEPENDENT_DESIGN_REVIEW`  
**Ngày:** 2026-11-08  
**Kết luận:** `REVISE_REQUIRED_DESIGN_PRESERVED` ; `D0_REVIEW_COMPLETED_WITH_FINDINGS` ; `D1_D4=HOLD` ; `SCIENCE_NOT_AUTHORIZED`  
**Kho GitHub:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`  
**Đối tượng được đọc lại nguyên trạng:** `docs/research/TTM_GEMINI_EMBEDDING2_GQA_PAGEDATTENTION_FEASIBILITY_DESIGN_20261108.md`, Git blob SHA-1 `10c4818abcf154e67244c0cc289c468f42b1fbf0`, branch tại thời điểm thẩm định `f2393973814f8442e409539714fc487bf86443ef`.  
**Base chính:** `main@1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`  
**Mã nguồn đối chiếu:** `src/p02/transformer_core.py`, blob `9762343e06cf800b50574c2871ae1ed58537fb18`.  
**Tuyến thực thi gốc:** PR #12 DRAFT, tách biệt; T1–T3 PASS kỹ thuật có giới hạn, T4 `SCIENCE_LOCK=HOLD`, chưa có checkpoint huấn luyện/đánh giá được công bố trong hồ sơ đã đọc.

**Ý nghĩa "độc lập" trong phạm vi này:** Đối chiếu yêu cầu của tài liệu thiết kế với mã nguồn TTM, các tiêu chí so sánh/nguồn công khai và lập ma trận phản biện riêng, không dựa vào kết luận của người thiết kế làm bằng chứng. **Không** tuyên bố có hội đồng, tác giả bên thứ ba hoặc bộ kiểm định khoa học độc lập đã chạy; đây là phản biện tài liệu do trợ lý thực hiện, cần một reviewer khác nếu quy trình yêu cầu độc lập về nhân sự.

**Ranh giới:** Không chạy thử API, GPU, mô hình, checkpoint, QA động, corpus, TEST hoặc huấn luyện; không truy cập máy Windows; không sửa tài liệu thiết kế gốc hoặc `lineage.md`; không merge/đóng PR; không thay P00–P12/P07.

## 1. Phán quyết tổng hợp

**Quyết định:** `KEEP_ARCHITECTURE_HYPOTHESIS; REVISE_PROTOCOL_BEFORE_D1`.

- **PASS — Nội dung định hướng:** Đã tách Gemini retrieval, semantic fusion, GQA và Paged KV thành các câu hỏi khác nhau; có dự kiến frozen checkpoint, cảnh báo data leakage, kiểm soát gate=0 và tình trạng one-shot.
- **FAIL — Tính quy kết nhân quả của đối chứng R3/V1 như đang viết:** R3 dùng frozen GPT + text; V1 dùng cùng GPT nhưng có module *được huấn luyện thêm*, side-channel vector, tham số và ngân sách ngữ cảnh khác. V1 thắng R3 không chứng minh nguyên nhân riêng là embedding hay Cross-Attention.
- **HOLD — Tính khả thi khoa học trên TTM-Small:** 3.75M và context 256; TinyStories next-token training không tự xác lập khả năng hỏi đáp/đọc bằng chứng. Chưa có checkpoint T4 đã được thẩm định.
- **HOLD — Nguồn/quyền/chi phí:** API được xác nhận hiện diện, nhưng data rights, billing/quota, dữ liệu được đưa lên dịch vụ, quyền sử dụng/cache embedding cho downstream train và chi phí thí nghiệm chưa chốt.
- **HOLD — Adapter/GGUF:** Chưa định nghĩa đầy đủ phép huấn luyện, vị trí fusion, output scoring, cách xuất/serve Cross-Attention, kiểm soát budget.
- **PASS_SCOPED — Tách GQA/PagedAttention:** Hai hướng là tối ưu cấu trúc/tài nguyên riêng, không thuộc bằng chứng cho chất lượng ngữ nghĩa.

Không có dữ liệu khoa học nên **không** ghi `EXPERIMENT_PASS`/`EXPERIMENT_FAIL`; bản ghi là đánh giá thiết kế, không append vào `lineage.md`.

## 2. Ma trận phản biện bắt buộc

| ID | Chủ đề | Phán quyết | Lỗ hổng/vấn đề | Biện pháp bắt buộc trước D1/D2 |
|---|---|---|---|---|
| F01 | So sánh nhân quả text/vector | **FAIL_PROTOCOL** | R3 không train; V1 train Adapter/Cross-Attention, có extra parameters và semantic side-channel; `same checkpoint` chỉ đúng *backbone*. | Tách ước lượng giá trị **hệ thống** (R3 vs V1) khỏi giá trị **biểu diễn** (matching trainable capacity); thêm text-side trainable control như soft-prefix/text-adapter `R4` với ngân sách/frozen backbone tương ứng, thêm ablation vector random/shuffled và linear-only. |
| F02 | Ngân sách thông tin | **HOLD_FAIRNESS** | 768 chiều không tương đương 768 token; vector có thể mã hóa đoạn > cửa sổ 256, text buộc cắt. | Hai strata: `S_SHORT` cùng evidence chunk đủ lọt context ở text path; `S_LONG` nhiều thông tin vượt window nhưng báo là **architectural side-channel advantage**, không gộp với S_SHORT. Ghi doc IDs, chunk bytes, model-token IDs, m, dimensions, latency/cost; paired scoring. |
| F03 | Năng lực checkpoint GPT | **HOLD_BASELINE** | TTM 4M TinyStories language modeling không có bảo đảm instruction-following/QA; T4 chưa science-locked. | Sau T4/T5/T6 chọn **minimum competence**: closed-book negative; oracle gold-evidence short-context positive control; forced-choice/answer-token NLL với cùng target; nếu không vượt baseline được khóa thì `MODEL_CAPABILITY_GAP`, không mở D1 kết luận chất lượng generation. |
| F04 | Leakage | **PASS_CONCEPT / HOLD_CONTRACT** | Nguyên tắc chỉ nêu chung; chưa có split truy xuất theo nhóm và artifact. | Cấm đưa TEST/answer label vào tập train, index tuning, adapter updates; group-split theo nguồn/biến thể, duplicate/near-dup; query online chỉ từ câu hỏi/trạng thái tiền tố hợp lệ; training loss mask chỉ ở answer tokens; các nguồn bằng chứng có thể chứa câu trả lời **một cách hợp lệ** nếu nó được cung cấp cho cả hai đường; tách label annotation khỏi content. |
| F05 | Gemini API semantics | **PASS_SCOPED / HOLD_PINNING** | Đúng model stable `gemini-embedding-2`, không dùng `task_type`. Vector có thể là aggregated input; không có token hidden states. | Khóa cách format query/document, 1 embedding/chunk, dimension=768 là **ứng viên**, input truncation guard, output vector checks, model/version/timestamp/hash; nếu chuyển `gemini-embedding-001` phải re-embed toàn bộ và không trộn vector space. |
| F06 | Giá và quyền dữ liệu | **HOLD_RIGHTS_AND_COST** | Không có cost cap, số lượng token/API request; tier miễn phí có quy định xử lý dữ liệu khác tier trả phí. | Phê duyệt corpus/license, PII và điều khoản API/downstream derivative, xác minh có được lưu/reuse embedding; khóa `N_docs, avg_tokens_doc, N_queries, avg_tokens_query, retry_factor, cache_hit, tariff, max_USD`; không gửi dữ liệu thật khi chưa phép. |
| F07 | Adapter learning/causal design | **HOLD_IMPL_SPEC** | Model chỉ có LM objective, chưa có QA supervision; chưa biết vị trí chèn cross output, gradient/gate và vị trí scoring. | Freeze GPT thật; khóa cross-attn vị trí, head/shapes, padding mask, residual scale, gate, `m=0,1,>1` cases; `gate=0` parity; gradients có tín hiệu; control frozen random; training seed/steps/capacity, checkpoint resume và held-out. |
| F08 | GQA riêng | **PASS_SCOPE / HOLD_EXPERIMENT** | P02 code có `nn.Linear(d,3*d)` cho MHA; chưa có `n_kv_heads`, không thể đổi flag trên frozen weights. | Tách GQA successor với conversion/uptraining hợp lệ hoặc matching-budget train; log KV memory, prefill/decode và quality; không sửa P02 baseline. |
| F09 | PagedAttention riêng | **PASS_SCOPE / HOLD_EXPERIMENT** | P00 paged CPU tập hợp lại K/V; P07 direct-page kernel PAUSED; chưa thể claim GPU speedup. | Dùng cùng checkpoint/hardware/tokens, kiểm numerical parity/no-cross-request mix; so đo long context, concurrent requests, fragmentation; không gộp cache K/V Cross-Attention với self-attn theo ngầm định. |
| F10 | Tương thích GGUF/llama.cpp | **HOLD_EXPORT** | T2 chỉ chứng minh GPT2-like F32 untrained, không chứng minh network mới có Cross-Attention chạy trong llama.cpp/Ollama. | Baseline đường PyTorch cho scientific fusion; exporter/runner mới là scope successor; không sửa T2/T5. |
| F11 | Mốc khoa học | **HOLD_PREREG** | Chưa khóa `delta_min`, sample size/power, seed, CPU/GPU cost, bootstrap unit, OOD/robustness và thang đo. | Design prereg độc lập sau D1, paired doc-group bootstrap; định trước `NLL_Text-NLL_Vector` (dương tốt cho vector), CI, threshold, cost ceiling, negative controls và FAIL/INCONCLUSIVE. |

## 3. Hợp đồng đối chứng tối thiểu sau hiệu chỉnh

### 3.1. Hai estimands riêng, không trộn

1. **Giá trị giải pháp end-to-end (system value):** cùng frozen backbone, cùng câu hỏi và evidence IDs; `Text-RAG R3` đối chiếu `Vector+trained Adapter V1`. Đây là phép đo kỹ thuật hợp lệ về hiệu năng tổng hệ thống dưới budget *được báo cáo*, nhưng không quy kết cơ chế riêng.
2. **Giá trị riêng của vector/Attention (mechanistic attribution):** `Text-conditioned trainable control R4` với gần tương đương trainable params/steps, cùng checkpoint và data train; đối chiếu `V1`; cộng `V2` (shuffled/random vectors, kiểm soát leakage/capacity), `V3` (linear/additive adapter). Báo cáo lệch tham số và FLOPs nếu không thể match chính xác; nếu không match thì chỉ suy ra limited attribution.

Đề nghị bổ sung `R_gold`: bằng chứng đúng được cung cấp trực tiếp từ oracle *chỉ như positive control* sau khi chọn/khóa benchmark; **không** dùng oracle để chọn mô hình trên TEST. R_gold kiểm tra `TTM can actually use evidence` tách khỏi chất lượng retrieval; không sử dụng làm tuyên bố triển khai oracle.

### 3.2. Quy tắc scoring

- Cùng bộ câu hỏi, cùng tokenized answer target; tính `answer-only teacher-forced NLL`, loại các token prefix khỏi loss; báo cáo theo câu hỏi và nhóm tài liệu. Không dùng perplexity trên prompt khác nhau làm primary.
- VALID có thể dùng để lựa chọn khi prereg cho phép; TEST held-out một lượt, `No TEST peek`.
- Với `S_SHORT`: chứng minh nguyên văn các nguồn mà vector nhận đã nằm trong giới hạn `T<=256` cho R3, tính cả question và answer prefix; nếu không, chuyển mẫu sang `S_LONG`.
- Với `S_LONG`: không gọi `same information budget`; đưa số token nguồn của vector, token text và API cost vào báo cáo; S_LONG trả lời câu hỏi lợi ích của đường condition ngoài cửa sổ, không phải khả năng biểu diễn tốt hơn trên thông tin ngang bằng.

### 3.3. Kịch bản ngăn rò rỉ

- Các chunk nguồn được xây trước train/test; không nhúng nội dung có được từ full target answer tương lai vào `evidence_vectors`.
- Ngăn metadata/filenames chứa đáp án hoặc split labels, chỉ dùng doc IDs vô nghĩa; kiểm exact và near-duplicate trong corpus, câu hỏi và paraphrases theo nhóm.
- Đáp án xuất hiện trong **bằng chứng tự nhiên được cung cấp hợp lệ** không phải leakage; đó là tác vụ retrieval-augmented QA. Leakage xảy ra khi nhãn/TEST/target tương lai không được cấp hợp lệ được đưa vào query/vector/training.
- Lưu `query_hash`, `doc_hash`, `embedding_request_fingerprint`, `embedding_output_hash`, `split_manifest_sha`; nếu không có quyền lưu vector thì thiết kế phương án log metadata tối thiểu theo chính sách.

## 4. Gemini Embedding 2: kết quả kiểm tra công khai

- Tài liệu Google xác nhận `gemini-embedding-2`, stable, giới hạn văn bản 8192 token, output 128–3072 chiều, khuyến nghị 768/1536/3072.
- Google xác nhận `task_type` không hỗ trợ trên Embedding 2; query/document là **asymmetric prompt templates**. Hướng dẫn chính thức: question answering query `task: question answering | query: {content}`, document `title: {title} | text: {content}`. Cần pin templates.
- Embedding 2 tổng hợp nhiều input trong một request nếu không tách `Content` riêng; cần 1 vector/chunk, chống việc vô tình chỉ tạo 1 vector cho nhiều chunk. Không trộn `gemini-embedding-001` và `gemini-embedding-2` vì không tương thích không gian.
- Trên tài liệu giá API công khai khi thẩm định: **text input Standard paid = USD 0.20 / 1M tokens; Batch paid = USD 0.10 / 1M**; ghi giá tham khảo **không phải báo giá cố định hoặc cho phép phát sinh phí**. Free tier có thể $0 cho token nhưng chính sách dữ liệu khác, quota phải được duyệt riêng. Trang giá ghi `Used to improve our products: Free yes, Paid no` cho cấu hình hiện công bố.
- Công thức ước lượng text-only: `cost_usd = ((N_doc * avg_doc_tokens * (1-cache_hit_doc)) * batch_rate + (N_query * avg_query_tokens * (1-cache_hit_query)) * online_rate) / 1e6 * retry_factor`. Tách các token task prefix/title; `retry_factor` chỉ nhân số lần được tính phí, phải xác nhận billing API.
- **Minh họa không phải workload đã duyệt:** 5000 chunk × 256 tokens + 1000 queries × 24 tokens = 1.304M input tokens; chạy all online với rate 0.20 sẽ ~USD 0.2608; corpus qua batch 0.10 và queries online 0.20 sẽ ~USD 0.1328, **chưa** tính train GPT/adapter, token bổ sung từ template, latency/transfer/traffic, storage, retry và giá thay đổi. Không được dùng minh họa này làm `COST_CAP_APPROVED`.

Nguồn tài liệu công khai:
- https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2
- https://ai.google.dev/gemini-api/docs/embeddings
- https://ai.google.dev/gemini-api/docs/pricing
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/embeddings/get-multimodal-embeddings
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference

## 5. Rủi ro kiến trúc ngoài sơ đồ đẹp

- **Gradient/biểu diễn:** Nếu cross-attn đặt một lần ở cuối frozen GPT, hidden states tối hậu có thể không học sử dụng external memory hiệu quả; cấu hình vị trí fusion phải chọn bằng phép thử kỹ thuật *trước* prereg science; không chỉnh hậu nghiệm sau TEST.
- **Khả năng sinh token:** 4M TinyStories không tương đương model hỏi đáp. Một QA fail không khẳng định Gemini embedding kém hay Cross-Attention vô dụng.
- **Causal masking:** Cross-attn to external docs có thể không dùng causal mask trên doc index, nhưng self-attn bắt buộc causal và tất cả docs phải hợp lệ cho mẫu/tiền tố tại thời điểm dự đoán.
- **KV Cache:** Key/value của self-attn và cross-attn có vòng đời khác nhau; quản lý trang cho self-attn không mặc nhiên cung cấp cache cross-attn; không đưa tuyên bố bộ nhớ/tốc độ của nhánh kia vào H1.
- **MHA/GQA:** Chuyển số KV heads làm đổi kích thước tham số; so GQA/MHA cùng checkpoint không hợp lệ trừ khi có thuật toán chuyển và đánh giá rõ.
- **API tái lập:** Không pin được trọng số nhà cung cấp bằng Git SHA. Cần khóa snapshot vector có quyền sử dụng hoặc ghi nhận giới hạn tái lập.

## 6. Quyết định giữ/sửa/bỏ

| Nhánh thiết kế | Quyết định | Lý do |
|---|---|---|
| A — External retrieval | **KEEP, D1_HOLD** | Đơn giản, không đổi checkpoint; phải đợi model đủ năng lực, nguồn và API hợp lệ. |
| B — Trainable semantic adapter + Cross-Attention | **REVISE, D2_HOLD** | Có câu hỏi nghiên cứu chính đáng nhưng protocol attribution hiện FAIL và thiếu supervision/budget. |
| C — GQA | **KEEP_SEPARATE** | Phù hợp engineering, không chứng minh Semantic Fusion; chưa implement. |
| D — PagedAttention | **KEEP_SEPARATE** | Nằm trong lộ trình P05–P08, tránh trùng nghiên cứu và bypass P07. |
| "Đã cải thiện TTM" | **REJECT_CLAIM** | Không có kết quả mô hình/QA động hay thực nghiệm. |

### Hành động cần sửa, theo thứ tự

1. **Protocol Amendment A1:** Tách `system value` và `mechanistic attribution`, thêm R4 và R_gold, S_SHORT/S_LONG, chuẩn hóa answer-only NLL.
2. **Admission A2:** Chốt năng lực tối thiểu checkpoint T4 từ QA ngắn có oracle evidence; nếu không đạt, chờ mô hình phù hợp thay vì bắt đầu D1 với mô hình không làm được tác vụ.
3. **Data/API A3:** Thẩm định corpus và điều khoản dịch vụ; giới hạn token/request, version/template/dimensions, ước lượng ngân sách và điều kiện lưu vector.
4. **Training A4:** Khóa kiến trúc adapter, gate, masks, trained parameter budget, optimizer, seeds, checkpoints, paired estimator và độc lập QA trước run.
5. **Thẩm định sửa đổi:** Review riêng bản amendment; chỉ khi mọi blocker của D1 được giải quyết mới đưa quyết định D1. Không yêu cầu permit cho từng phép kiểm nhỏ.

## 7. Trạng thái và giới hạn thẩm định

`DESIGN_REVIEW=COMPLETED`  
`DESIGN_DISPOSITION=REVISE_REQUIRED`  
`CAUSE_ATTRIBUTION_PROTOCOL=FAIL`  
`MODEL_CAPABILITY=HOLD`  
`DATA_RIGHTS_AND_API_BUDGET=HOLD`  
`ADAPTER_TRAINING_READINESS=HOLD`  
`D1=NOT_AUTHORIZED`  
`D2_D4=NOT_OPENED`  
`SCIENTIFIC_RESULT=NONE`  
`SCIENCE_LINEAGE=UNCHANGED`  
`MAIN/PR12/P07=UNCHANGED_BY_REVIEW`

**Không có tuyên bố đã thực hiện kiểm định bởi reviewer thứ ba.** Đây là một biên bản thẩm định thiết kế tách khỏi tài liệu ban đầu, chưa phải phản biện nhân sự độc lập hoặc kết quả thí nghiệm khoa học.

**Bước thực hiện tiếp theo:** `TTM_EMBEDDING2_FEASIBILITY_PROTOCOL_AMENDMENT_A1_DESIGN_ONLY` — tạo bản amendment mới (không ghi đè tài liệu đã thẩm định) cho R4/R_gold, S_SHORT/S_LONG, answer-only NLL và đối chứng cùng năng lực học; sau đó thẩm định lại thiết kế. Tuyến TTM T4 science-lock vẫn ưu tiên thực thi riêng; không triển khai, không gọi API, không mở D1–D4, không merge.
