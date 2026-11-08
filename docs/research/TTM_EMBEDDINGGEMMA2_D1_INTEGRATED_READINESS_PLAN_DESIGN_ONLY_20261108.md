# TTM — D1: Kế hoạch tích hợp chuẩn bị đánh giá EmbeddingGemma 2 cục bộ

**Mã công việc:** `TTM_EMBEDDINGGEMMA2_D1_INTEGRATED_READINESS_PLAN_DESIGN_ONLY`  
**Ngày lập:** 2026-11-08  
**Trạng thái:** `PLAN_WRITTEN_DESIGN_ONLY / READINESS_NOT_EXECUTED / D1_NOT_AUTHORIZED`  
**Kho GitHub:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh nghiên cứu:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`  
**Base nghiên cứu trước tài liệu:** `f4a682a943f2584d1b287f36fcb9d3bc6f14b7ae`  
**Base `main` khi đọc:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`  
**Tài liệu nguồn được chấp nhận trong phạm vi thiết kế:** `TTM_EMBEDDING2_A1_BACKBONE_CONTRACT_AMENDMENT_A2_DESIGN_ONLY_20261108.md`, Git blob `a70a1b957ad47934172804065c7322c3008c3c0d`. Vòng thẩm định A2 bên ngoài repository kết luận `DESIGN_ACCEPTED_SCOPED`; không được diễn giải là permit thực nghiệm.

> **Cam kết của bước này:** chỉ lập kế hoạch trên GitHub; không download trọng số, dataset, phần mềm hoặc container; không tạo/notebook chạy, không gọi Gemini API; không chạy `R_gold`, retrieval, GPU, TEST, embedding hay Adapter; không đổi mã nguồn, `lineage.md`, `main`, P00–P12, P07, TTM-Small T1–T7/PR #12, và không merge. TTM-Small T4 vẫn là ưu tiên điều phối tài nguyên.

## 1. Mục tiêu D1 và những gì không được nhầm với D1

**D1 trong tài liệu này là giai đoạn kiểm chứng ban đầu (External Retrieval Sanity / Baseline Competence), không phải thí nghiệm Adapter.**

Phạm vi **chỉ có thể được xem xét sau khi cấp quyền riêng**:
1. `R0`/ `R_gold`: Qwen checkpoint có khả năng khai thác một đoạn bằng chứng đúng cho câu trả lời hay không? Tách năng lực đọc bằng chứng khỏi chất lượng embedding.
2. `R1`/ `R2`: BM25 và `google/embeddinggemma-2` text-only có chọn được tài liệu liên quan từ cùng corpus hợp lệ hay không? Đo Recall@k/MRR hoặc Hit@k theo quy tắc đã khóa, không dùng nhãn TEST để chỉnh retrieval.
3. `R3`: Với evidence IDs do R2 lựa chọn cố định, cung cấp **văn bản nguyên bản** cho Qwen frozen; đo Answer-only NLL/độ đúng và log truncation/latency.
4. Tính khả thi **tài nguyên** và tính đúng số học của bộ tạo vector EmbeddingGemma 2 FP32 cục bộ, gồm kiểm finite/shape/normalization/repeatability trên fixture kỹ thuật *không phải bằng chứng hiệu năng khoa học*.

**Ngoài phạm vi D1:** `R4`, `V1`, `V2a/V2b`, `V3` và huấn luyện Adapter/Cross-Attention; mở D2–D4; GQA-vs-MHA hay Paged-vs-Dense; GGUF có fusion, Ollama triển khai; thay GPT TTM-Small hoặc dùng kết quả Qwen làm chứng cứ T4.

**Điểm chốt:** `R_gold` là positive control có bằng chứng được biết trước để đánh giá năng lực; **không** được dùng làm kết quả retrieval và không thay bộ chọn tài liệu R2.

## 2. Bảng nguồn mô hình, phiên bản và điều kiện khóa

| Vai trò | Nguồn đúng | Giấy phép công bố | Cấu hình dự kiến | Revision/thẩm quyền hiện tại |
|---|---|---|---|---|
| Embedding text | `google/embeddinggemma-2` — https://huggingface.co/google/embeddinggemma-2 | Apache-2.0; kiểm thêm Gemma Prohibited Use Policy | `SentenceTransformer`, **text-only** qua `config_kwargs={"vision_config":None,"audio_config":None}`, vector 768, `torch.float32` trên T4 | Repo/model card kiểm tra được; **chưa pin exact 40-char HF SHA hoặc tệp trọng số** |
| Backbone sinh câu trả lời | `Qwen/Qwen2.5-0.5B-Instruct` — https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct | Apache-2.0 | Qwen2, 24 layer, `d_model=896`, 14 query / 2 KV heads, vocab 151936, chat template theo revision; frozen | **Chưa pin revision, tokenizer/chat template và checkpoint SHA** |
| Đối chứng bổ sung, không phải điều kiện D1 | `EleutherAI/pythia-160m-deduped` — https://huggingface.co/EleutherAI/pythia-160m-deduped | Apache-2.0 | GPT-NeoX, 12 layer, `d_model=768`, MHA, pretrained | **Để sau**, không dùng tài nguyên D1/T4 để kiểm riêng Pythia |
| Dữ liệu | Corpus ứng viên tự tạo có quyền rõ ràng; sau đó bộ tài liệu công khai được thẩm định | Chưa phê duyệt corpus cụ thể | Text, không nhạy cảm, chia nhóm nguồn | `DATA_SOURCE_AND_LICENSE=HOLD` |

**Trước bất kỳ download về sau:** lưu manifest `repo_id`, `commit_sha40`, tệp `config.json`, tokenizer/special tokens/chat template, license/usage policy, file list/size, weight shard IDs + checksums, `transformers`, `sentence-transformers`, `torch`, Python/CUDA version và quy tắc tải model qua `revision=<sha>`. Metadata trên `main` động **không phải khóa reproducibility**. Thiết kế hiện tại **không tự khẳng định các SHA này đã được pin**; nhiệm vụ xác minh metadata read-only và chuẩn bị danh sách size/rights được gom vào bước kế tiếp.

**Nguồn chính thức cho quy tắc kỹ thuật:** https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2 ; https://ai.google.dev/gemma/docs/embeddinggemma/inference-embeddinggemma-with-sentence-transformers ; https://huggingface.co/docs/transformers/main/model_doc/embedding_gemma2 .

## 3. Dữ liệu, quyền sử dụng và tránh rò rỉ (một hồ sơ tổng hợp)

### 3.1. Hai lớp dữ liệu không được trộn nhãn

- **Diagnostic `R_gold` ứng viên:** Bộ tài liệu sự kiện ngắn do dự án tạo/được cấp phép minh bạch, mỗi tài liệu gồm một tình huống, tên định danh không gợi đáp án, một số thuộc tính giả định mới, câu hỏi có đáp án xác định từ bằng chứng. Cần thêm mẫu không có đáp án trong tài liệu, mẫu gây nhiễu và câu hỏi biến đổi cách viết để tránh đo đơn thuần trí nhớ câu mẫu.
- **D1 retrieval corpus:** Tập đoạn văn có nguồn gốc/giấy phép và attribution cụ thể, có gold `doc_id` độc lập cho đánh giá retrieval; có câu hỏi, nhóm nguồn, bản quyền, manifest SHA. Corpus thiên về dữ liệu giả lập không đủ chứng minh áp dụng RAG thực tế; nếu không có tài liệu công khai hợp pháp phù hợp, ghi `DATA_RIGHTS_HOLD` thay vì đánh giá khoa học.
- Sử dụng nguồn `TinyStories` thuộc pilot TTM-Small **không tự được chuyển quyền** cho D1; không tái dùng TRAIN/VAL/TEST, tokenizer hoặc phiên chạy của PR #12.
- Tài liệu mới (nếu sau này có) phải chỉ từ nguồn được phép, không chứa PII, khóa bí mật hay dữ liệu khách hàng; embedding chạy **local inference**, không mặc nhiên gửi nội dung tới Google. Tuy nhiên phải audit telemetry, hosted service và chính sách cài đặt môi trường.

### 3.2. Dự kiến phân tách và bằng chứng bắt buộc

Một `dataset_rights_and_split_manifest` cần chứa: `source_id, license_uri, license_evidence, attribution, permitted_use_scope, group_id, doc_sha256, question_sha256, answer_sha256, chunk_id, tokenizer_id, split, near_duplicate_rule, pii_review_status`.

- `TRAIN/VAL/TEST` tách **theo nhóm tài liệu/sự kiện** trước khi lập chỉ mục. Exact/near-duplicate xuyên nhóm, biến thể cùng nội dung, title/file-name leak và chunk-overlap phải được kiểm soát. Không để answer annotation hoặc TEST label tham gia query/template retrieval/prompt calibration.
- Index có thể chứa văn bản nguồn của TEST **chỉ khi hợp đồng benchmark là retrieval từ corpus có sẵn trong triển khai thực tế**; điều này khác đưa nhãn TEST vào index. Phải khóa phạm vi index/split và không tuning trên kết quả TEST. Không được ngầm dùng TEST corpus để chọn hard negatives hoặc threshold.
- Chính sách chunking và phân tích token phải khóa trước evaluation: `chunker_version`, `chunk_size`, `overlap`, `title_rule`, `max_embedding_tokens=8192 including task prefix`; một chunk → một vector; mọi truncation phải log, không âm thầm cắt.
- Embedding query/doc chuẩn dự kiến: `prompt_name="QuestionAnswering"` cho query và `prompt_name="Document"` cho document không title hoặc format `title: {title} | text: {content}` cho tài liệu có title, theo Google model card. Query/document dùng cùng revision, dimension và normalization. Cần pin chính xác prompt/formatter sau khi kiểm phiên bản thư viện.
- `top_k`, cỡ bộ, phương pháp BM25, cosine, normalization, tie-break, duplicate handling, mismatch policy đều phải tiền đăng ký. Không đổi retrieval IDs theo hiệu quả R3 sau khi xem TEST.

**Kết luận hiện tại:** quyền dữ liệu **chưa được chứng minh**; hồ sơ chỉ mô tả cách lấy bằng chứng quyền, không được tự gán PASS.

## 4. `R_gold` trên Qwen: thiết kế chẩn đoán tối thiểu

**Đối chứng `R0` vs `R_gold` vs `R_wrong`:** cùng frozen `Qwen2.5-0.5B-Instruct` checkpoint, tokenizer, question, answer và chính sách giải mã; chỉ đổi bằng chứng: không có / bằng chứng đúng nguyên văn / đoạn không liên quan hoặc chứa thông tin đánh lạc hướng. Không tune trên TEST.

**Số mẫu đề xuất để lập kế hoạch, chưa khóa:** thí điểm diagnostic gồm khoảng 48 nhóm tài liệu độc lập, 2 dạng câu hỏi/nhóm (~96 cặp câu hỏi). Đây **không phải tính toán power hay tiền đăng ký**, cần review năng lực/độ khó và nguồn trước khi ấn định số lượng.

**Kỹ thuật đo:** answer-only teacher-forced NLL trên **cùng answer token IDs trong một Qwen backbone**, không cộng prompt loss; kiểm boundary token/chính sách chat template/đúng shift và mask. Thêm forced-choice accuracy hoặc Exact Match, đo `NLL_R0-NLL_Rgold`, `NLL_Rwrong-NLL_Rgold`, tỷ lệ câu đủ evidence; bootstrap paired ở mức `group_id`. Tính đúng phải kiểm trên fixture kỹ thuật trước khi nhìn kết quả held-out.

**Minimum competence:** Trước khi chạy khoa học phải ấn định `N_samples`, mức cải thiện tối thiểu thực tiễn, khoảng tin cậy, rule PASS/FAIL/INCONCLUSIVE và ngưỡng accuracy, không đặt hậu nghiệm. Nếu Qwen không học được dùng evidence dù được đưa đúng thì `MODEL_CAPABILITY_GAP`; không kết luận EmbeddingGemma/Adapter FAIL. Nếu PASS chỉ cho phép **xem xét mở D1**, không tự mở.

**Cấu hình câu hỏi:** Bảo đảm `S_SHORT` theo context thực tế của Qwen trên Colab, bao gồm chat template, toàn bộ evidence, question và answer, không dùng `256` của TTM-Small làm giới hạn bắt buộc. Log số token, tránh đưa answer tương lai vào vector hoặc prompt.

## 5. Môi trường EmbeddingGemma 2 FP32 và hợp đồng kỹ thuật Colab T4

**GPU mục tiêu:** NVIDIA Tesla T4 16 GiB-class (theo hãng 16 GB GDDR6); Colab cung cấp thiết bị theo từng phiên, **không bảo đảm T4 luôn sẵn có**.

**Phân tách bộ mã hóa với mô hình sinh:**
- EmbeddingGemma 2 text-only ~270M params × 4 byte/FP32 ≈ **1.08 GB** chỉ trọng số, chưa bao gồm buffer, activation, tokenizer, CUDA context hoặc disk download; bản đầy đủ ~740M cần nhiều hơn.
- Qwen 0.5B ~494M params × 2 byte/FP16 ≈ **0.988 GB** trọng số ở FP16; Qwen có thể có BF16 config nhưng T4 không có BF16 native thích hợp. FP32 Qwen là phương án dự phòng kiểm tính đúng.
- **Không bao giờ ép EmbeddingGemma 2 sang FP16**: Google cảnh báo NaN hoặc embedding âm thầm bị suy giảm. `torch.float32` là hợp đồng text encoder trên T4; BF16 chỉ khi thiết bị thực tế hỗ trợ native và đã duyệt riêng.
- `SentenceTransformer("google/embeddinggemma-2", config_kwargs={"vision_config":None,"audio_config":None}, model_kwargs={"torch_dtype":torch.float32}, revision="<pinned_sha>")` là **đề xuất cấu hình**, phải đối chiếu API chính xác tại revision thư viện đã pin trước chạy. Không giả vờ câu lệnh đã kiểm trên T4.
- `encode(query, prompt_name="QuestionAnswering", normalize_embeddings=True)`; `encode(doc, prompt_name="Document", normalize_embeddings=True)` nếu document không title, title có thật phải format rõ. Giữ 768 chiều ban đầu, không tự chọn 256/128 vì tác động đến retrieval/adapter.
- Trước khi chạy cần xác minh phiên bản `python, torch, cuda, transformers, sentence-transformers, tokenizers, safetensors, huggingface_hub`, disk/Drive free, HF cache path, nguồn model SHA và giới hạn download. **Không chạy `pip` hoặc download trong bước plan.**

**Chiến lược tiết kiệm bộ nhớ đề nghị cho bước kỹ thuật successor:** Encode/cached corpus với EmbeddingGemma 2 FP32 trước, ghi vector/cache hash; giải phóng bộ mã hóa; sau đó nạp Qwen frozen và chạy R_gold/RAG, không bắt cả hai resident GPU nếu không cần. `R_gold` bản thân không yêu cầu EmbeddingGemma. Cache gồm `model_sha`, `encoder_config_sha`, `prompt_template_sha`, `source_chunk_sha`, `dtype`, `embedding_dim`, `L2norm`, `vector_sha`. Giữ quyền dataset và quy tắc không đưa data riêng tư vào repo.

**Mẫu trình tự kỹ thuật sau khi có quyền, KHÔNG thực hiện hiện tại:**
`(a) metadata/rights check → (b) CPU static fixtures, no model → (c) Colab environment/disk/gpu preflight → (d) exact pinned model load and FP32 finite-vector sanity → (e) vector cache/manifest → (f) Qwen load and frozen-backbone R_gold diagnostic → (g) retrieval R1/R2/R3 baseline with pre-registered source/test policy`.

**Giới hạn huấn luyện:** D1 không huấn luyện Adapter. Capacity/gradient của Cross-Attention train **thuộc D2/D3**, không được tuyên bố PASS từ `R_gold` hay lần load model.

## 6. Tài nguyên tổng hợp — giới hạn và kiểm tra một lần

Trước bất kỳ thực thi Colab thật trong successor phải khóa:
- `GPU_ID, total/free_VRAM, dtype_policy, cuda/driver, memory_peak_limit, RAM_free, Drive_free, cache_directory, disk_download_upper_bound, time_budget, network_access_scope, abort_behavior`.
- Tách ước tính `weight_bytes` khỏi `peak_load_and_inference_bytes`. Đo peak GPU/CPU cho encoder FP32 và Qwen trên fixtures; không khẳng định load cả hai dưới T4 16 GB chỉ từ tính tổng bytes trọng số.
- Lượt capacity chạy bằng **fixture kỹ thuật không tiêu thụ câu hỏi khoa học**, với microbatch 1 và chuỗi ngắn trước; kiểm NaN/Inf/zero norm, token-truncation, embedding shape, cosine normalization, deterministic repeated encoding, tokenizer boundaries, Qwen frozen no-update và graceful OOM/abort.
- Không đăng ký lại nhiều lần nếu lỗi; lưu FAIL cùng tiền đề, đề xuất sửa riêng. **Một preflight tích hợp** và **một quyết định D1 admission** là đủ; không đòi permit nhỏ cho mỗi kỹ thuật con.
- Kết quả QA kỹ thuật không được tự đổi `lineage.md` thành PASS khoa học.

**Giới hạn vận hành:** Colab có thể hết session/quota; nhánh này không sử dụng đồng thời quota với TTM-Small T4 khi ảnh hưởng ưu tiên chính. Không dùng remote TPU/GPU thuê trả phí nếu chưa có quyết định riêng.

## 7. Ma trận cổng hữu hạn để xem xét D1 admission

| ID | Bằng chứng phải có ở bước sau | Tiêu chí quyết định | Trạng thái hôm nay |
|---|---|---|---|
| `D1-R01` | Exact HF SHA/repo/license/config/weights/tokenizer/file list, no moving `main` | Nguồn kiểm chứng, bản quyền và model IDs đúng | `NOT_VERIFIED_EXACT` |
| `D1-R02` | Corpus rights, PII, attribution, source/group split/dedup/index policy | Không quyền hoặc có leakage => HOLD | `HOLD` |
| `D1-R03` | Qwen `R_gold` prereg diagnostic: samples/rubric/thresholds | Có positive+negative controls, không TEST peek | `DESIGNED_NOT_RUN` |
| `D1-R04` | Colab T4/Drive local resource and pinned Python/PyTorch env; FP32 encoder | Disk/RAM/VRAM thuận; encoder FP16 bị chặn | `PAPER_ESTIMATE_ONLY` |
| `D1-R05` | Static and zero-science dynamic preflight/smoke, bound run budget | Shape, finite, L2norm, prompt, tokenizer, abort verified | `NOT_EXECUTED` |
| `D1-R06` | R1/R2/R3 exact retrieval/answer-only NLL split contract | Paired IDs, no leakage, no tuning on TEST | `DESIGNED_NOT_PREREG_LOCKED` |
| `D1-R07` | TTM T4 separate capacity reservation and no branch interference | Không cạnh tranh tài nguyên với pilot ưu tiên | `INDEPENDENCE_DOCUMENTED` |
| `D1-R08` | Reviewer đọc một packet tích hợp: receipt, config, SHA, quyền, preflight verdict, cost/risks | `ALL_PASS` => **xem xét** permit D1; bất kỳ blocker => HOLD | `ADMISSION_NOT_ISSUED` |

**Chuẩn quyết định:** `D1_READY_FOR_ADMISSION_REVIEW` chỉ khi R01–R07 có bằng chứng thực và độc lập kiểm tra; chỉ thẩm quyền được phép mới quyết định D1. Không dùng một tài liệu design để gắn `PASS` cho những phép chưa chạy.

## 8. Sản phẩm cần bàn giao và lịch một tuyến, không micro-gates

Đầu ra bắt buộc của các công việc successor (chưa được triển khai):
1. `D1_SOURCE_AND_RIGHTS_MANIFEST.md/json`: exact model snapshots, license/corpus authority, split/index design.
2. `D1_R_GOLD_AND_RETRIEVAL_PREREG.md`: predefined diagnostic samples, primary/secondary metrics, negative controls, sample thresholds, sequential run/split discipline, abort/fail/inconclusive rules.
3. `D1_COLAB_T4_TECHNICAL_PREFLIGHT_REPORT.json`: actual HW/sw versions, RAM/disk, FP32 model-load/embedding numerical sanity and Qwen frozen baseline smoke, NO SCIENCE.
4. `D1_INDEPENDENT_ADMISSION_DECISION.md`: một phán quyết tích hợp `PASS_TO_CONSIDER_D1` / `HOLD`; mọi FAIL được bảo toàn; **không** tự mở science.
5. Khi và chỉ khi có permit khoa học D1: thực hiện baseline R_gold/retrieval theo prereg, lưu evidence, phán quyết khoa học vào `lineage.md` append-only nếu thực sự có PASS/FAIL/INCONCLUSIVE khoa học.

**Bước thực hiện tiếp theo đề nghị:** `TTM_EMBEDDINGGEMMA2_D1_SOURCE_RIGHTS_AND_R_GOLD_PREREG_DESIGN_REVIEW_READONLY` — gom rà soát nguồn/giấy phép và hợp đồng chẩn đoán R_gold/R1-R3 thành **một vòng rà soát tài liệu**, không tải model và không chạy. Sau đó mới đề nghị **một lượt** preflight kỹ thuật trên T4 riêng, tránh ảnh hưởng TTM-Small T4.

## 9. Quản trị trạng thái cuối

`PLAN_STATUS=WRITTEN_DESIGN_ONLY`; `MODEL_TARGET=google/embeddinggemma-2`; `BACKBONE_PRIMARY=Qwen/Qwen2.5-0.5B-Instruct`; `D1_READINESS=NOT_EVIDENCED`; `D1_D4=NOT_AUTHORIZED`; `SCIENTIFIC_EXECUTION=NONE`; `API_CALLS=NONE`; `MODEL_DOWNLOADS=NONE`; `TRAINING=NONE`; `MAIN/PR12/P07/LINEAGE=UNTOUCHED_BY_THIS_DOCUMENT`. Pythia vẫn là ứng viên nghiên cứu riêng; TTM-Small-4M T4 tiếp tục ưu tiên.