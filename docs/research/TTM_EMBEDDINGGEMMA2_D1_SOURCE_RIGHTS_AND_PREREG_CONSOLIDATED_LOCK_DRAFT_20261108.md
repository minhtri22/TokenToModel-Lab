# TTM — D1: Hồ sơ hợp nhất nguồn, quyền dữ liệu và tiền đăng ký (bản dự thảo khóa)

**Mã công việc:** `TTM_EMBEDDINGGEMMA2_D1_SOURCE_RIGHTS_AND_PREREG_CONSOLIDATED_LOCK_DRAFT`  
**Ngày:** 2026-11-08  
**Tình trạng:** `CONSOLIDATED_LOCK_DRAFT_ONLY / NOT_SCIENCE_PREREG_LOCKED / D1_NOT_AUTHORIZED`  
**Kho:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh tài liệu:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108` (tên lịch sử; model thực là **`google/embeddinggemma-2`**, không phải Gemini API).  
**HEAD trước tài liệu:** `6f63b4ca7b02ac58777f82e294d28cad2fef8777`; **`main` đã đọc:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.  
**Căn cứ:** A2 `docs/research/TTM_EMBEDDING2_A1_BACKBONE_CONTRACT_AMENDMENT_A2_DESIGN_ONLY_20261108.md` (blob `a70a1b957ad47934172804065c7322c3008c3c0d`); kế hoạch D1 `docs/research/TTM_EMBEDDINGGEMMA2_D1_INTEGRATED_READINESS_PLAN_DESIGN_ONLY_20261108.md` (blob `0997577b54f5f5d1ed30ddc9f4dc456026d3b069`); thẩm định chỉ đọc D1 ngày 2026-11-08: `DESIGN_DIRECTION_ACCEPTED / PREREG_REVISE_REQUIRED / D1_ADMISSION_HOLD`.

> **Giới hạn:** Chỉ soạn hồ sơ, kiểm metadata có sẵn trên web, không tải mô hình/weights/tokenizer/corpus, không chạy script, notebook, Colab, GPU, R_gold, R1/R2/R3, adapter hay TEST; không gọi Google API; không ghi `lineage.md`; không sửa mã, `main`, PR #12, TTM-Small T1–T7, P00–P12, P07 và không merge. Không nhận `PASS` khoa học từ tài liệu này.

## 1. Quyết định phạm vi và quan hệ với TTM-Small

**Mục tiêu D1 khi được cho phép trong tương lai:** (i) Qwen2.5-0.5B-Instruct frozen có sử dụng được bằng chứng đúng (R_gold) hay không; (ii) BM25 (R1) so với EmbeddingGemma 2 **chạy cục bộ** (R2) có truy xuất bằng chứng hợp lệ tốt hơn hay không; (iii) Qwen có trả lời với **chính văn bản gốc** được R2 truy xuất (R3) hay không.

- **Ngoài D1:** `R4/V1/V2/V3`, huấn luyện Adapter/Cross-Attention, PagedAttention, GQA-vs-MHA, fused GGUF/Ollama, D2–D4. Cơ chế Adapter chỉ là mục tiêu nghiên cứu sau D1.
- **TTM-Small-4M T4:** ưu tiên thực thi chính trên nhánh/PR riêng; không dùng quyền, tokenizer, corpus, namespace, Colab quota hoặc checkpoint của TTM-Small cho EmbeddingGemma 2.
- **Pythia-160M:** giữ là đối chứng nghiên cứu riêng, **không** nạp hoặc yêu cầu quyền/tài nguyên cho D1.
- **Đầu ra lần này:** một gói tài liệu tích hợp có **nguồn revision đề xuất và điều kiện khóa, quyền dữ liệu chưa chứng minh, tiền đăng ký ứng viên, trình tự sửa, các trạng thái HOLD minh bạch**.

## 2. Nguồn mô hình và revision chính xác: đã xác minh metadata, chưa pin toàn bộ tệp

| Vai trò | HF repository | Commit 40 ký tự được quan sát tại HEAD công khai ngày 2026-11-08 | License từ model card | Mức xác thực |
|---|---|---|---|---|
| Embedding | `google/embeddinggemma-2` | `f9972ac22e696a105c482202646979e33e4b5a1e` | `apache-2.0`; Google model card còn yêu cầu tuân thủ Gemma Prohibited Use Policy trong triển khai | `REVISION_IDENTIFIED / FILE_HASHES_NOT_VERIFIED` |
| LLM frozen | `Qwen/Qwen2.5-0.5B-Instruct` | `7ae557604adf67be50417f59c2c2f167def9a775` | `apache-2.0` theo model card và LICENSE trong repository | `REVISION_IDENTIFIED / FILE_HASHES_NOT_VERIFIED` |
| Pythia (ngoài D1) | `EleutherAI/pythia-160m-deduped` | `NOT_PINNED_FOR_D1` | Apache-2.0 công bố | `DEFERRED` |

**Nguồn revision có thể đọc lại:**
- https://huggingface.co/google/embeddinggemma-2/commit/f9972ac22e696a105c482202646979e33e4b5a1e
- https://huggingface.co/google/embeddinggemma-2/tree/f9972ac22e696a105c482202646979e33e4b5a1e
- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/commit/7ae557604adf67be50417f59c2c2f167def9a775
- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/tree/7ae557604adf67be50417f59c2c2f167def9a775

**Danh mục tệp ứng viên được đọc trên giao diện HF; chưa tải/kiểm tra byte:**
- Google: `README.md`, `config.json`, `config_sentence_transformers.json`, `modules.json`, `1_Pooling/`, `2_Normalize/`, `model.safetensors`, `tokenizer.json`, `tokenizer.model`, `tokenizer_config.json`, các config processor và `chat_template.jinja`. File toàn bộ `model.safetensors` khoảng 1.49 GB theo danh mục web; **không** nhầm với trọng số 270M sau khi chỉ nạp text-only.
- Qwen: `LICENSE`, `README.md`, `config.json`, `model.safetensors` (~988 MB web), `tokenizer.json`, `tokenizer_config.json`, `vocab.json`, `merges.txt`, `generation_config.json`. Bộ mã hóa/role/chat template phải trích từ **đúng commit**.
- Tuyến khoa học chỉ dùng `revision=<commit_sha40>`; nếu thay đổi commit sau review phải ghi successor và thẩm định tác động, không cập nhật âm thầm.

**Chưa hoàn tất `SOURCE_EXACT_PIN`:** cần `file_path, file_size, git_lfs_oid/xet_id (nếu có), sha256_of_downloaded_file`, phiên bản `sentence-transformers/transformers/torch/tokenizers`, thông số config sau load, quyền phân phối/cached-model. **Không tự tạo hoặc suy đoán SHA256 của tệp từ commit git hoặc from Xet size**. Thông tin trên web chứng minh tồn tại revision/tệp, không chứng minh tải đúng byte.

**Thông số theo nguồn Google:** text-only ~270M, full multimodal ~740M; đầu ra `768d`, context embedding 8192 (bao gồm instruction prefix), hỗ trợ MRL 512/256/128 sau chuẩn hóa lại; chỉ phase text. Google yêu cầu **FP32 hoặc BF16, cấm FP16** vì có thể NaN hoặc sai vector âm thầm. Colab Tesla T4: đề xuất **FP32 EmbeddingGemma**, Qwen FP16/FP32 sau preflight độc lập; không chọn BF16 native mặc định trên T4.

Nguồn thiết kế: https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2 ; https://developers.googleblog.com/embeddinggemma-2-the-developer-guide/ ; https://qwen.ai/blog?id=qwen2.5-llm .

## 3. Quyền dữ liệu: mô hình, corpus và cache là ba hợp đồng khác nhau

**Quyền mô hình:** `MODEL_LICENSE_METADATA=PASS_SCOPED`; `LICENSE_TERMS_AT_PINNED_REVISION=REVIEW_NEEDED`; `GEMMA_PROHIBITED_USE_POLICY=REVIEW_NEEDED`. Apache-2.0 theo metadata **không** cho quyền dùng mọi corpus, không miễn nghĩa vụ attribution/notice, và không thay review chính sách sử dụng.

**Quyền corpus D1 = HOLD:** Chưa có corpus đã lựa chọn, chủ sở hữu và giấy phép được kiểm định; do đó **không có data SHA, split SHA hay quyền cache**. Đề xuất hai phần có ranh giới rõ:
1. `R_GOLD_DIAGNOSTIC`: 48 nhóm tình huống **hư cấu được dự án tự soạn**, tên và thuộc tính không thuộc kiến thức phổ biến, 2 câu hỏi có đáp án/nhóm. 12 nhóm âm tính riêng, 2 câu hỏi không có đáp án/nhóm. Đây chỉ là **quy mô dự thảo**, dữ liệu **chưa được tạo**; chủ dự án phải xác nhận quyền sở hữu hoặc giấy phép của văn bản được dùng, cách gán tác giả và khả năng xuất bản/lưu tập.
2. `D1_RETRIEVAL_CORPUS`: phải chọn một tập tài liệu công khai có quyền rõ (ứng viên tài liệu tự soạn hoặc bộ công khai được cấp phép) cùng gold `doc_id` do quy trình chú giải độc lập tạo. Không dùng “mô hình mở” làm bằng chứng quyền bộ dữ liệu. **Không tái dùng** TinyStories TTM-Small hoặc tài liệu có nguồn không xác định chỉ vì đã được download ở dự án khác.

**Manifest bắt buộc trước khi tạo index/training/science:**
`source_id`, `owner`, `license_uri` hoặc `self_authored_declaration`, `license_snapshot_sha`, `allowed_uses` (local inference / vector derivation / caching / evaluation / redistribution), `attribution`, `pii_status`, `doc_id`, `doc_sha256`, `group_id`, `query_id`, `answer_annotation_sha`, `index_membership`, `split_id`, `split_manifest_sha`, `near_duplicate_rule`, `chunker_version`, `annotation_provenance`.

**Điều kiện chống rò rỉ:**
- Chia theo `group_id` nguồn/tình huống và paraphrase, không theo từng hàng; exact/near-duplicate xuyên TRAIN/VAL/TEST; no answer-containing filenames/titles; nhãn TEST không dùng để chọn `k`, chunker, template, negative samples, model hoặc ngưỡng.
- Index gồm tài liệu TEST chỉ nếu benchmark mô phỏng corpus sẵn có trong triển khai (được mô tả và khóa trước); **gold answer/gold doc labels TEST không** tham gia embedding/query/index features. Nếu corpus nhãn là “ẩn” không công khai, không được dùng để xây index.
- Với corpus **synthetic only**, kết luận giới hạn `SYNTHETIC_DIAGNOSTIC_ONLY`; không tuyên bố chất lượng RAG ngoài đời. Nếu quyền corpus không chứng minh: `DATA_RIGHTS_HOLD`, không cấp thực thi.

## 4. Tiền đăng ký R_gold — ứng viên định lượng để reviewer có thể khóa

### 4.1. Cấu trúc và tách nhiệm vụ

- `BACKBONE=Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`, frozen; **không** Adapter, không fine-tune, không Gemma embedding ở R_gold.
- **Tập có đáp án (answerable):** `N_GROUPS_CANDIDATE=48`, `QUESTIONS_PER_GROUP=2`, `N_QA=96`. Mỗi nhóm là tình huống hư cấu riêng, một câu hỏi trực tiếp và một paraphrase; văn bản có bằng chứng chứa đúng câu trả lời ngắn, không đánh lừa bằng tên/tiêu đề. Bảo đảm các nhóm độc lập từ nguồn tạo/QA; phân bố loại thuộc tính được xác định trước tạo dữ liệu.
- **Tập không có đáp án:** `N_NEGATIVE_GROUPS_CANDIDATE=12`, 2 câu/nhóm, 24 câu riêng; gold response `UNKNOWN`/định dạng từ chối được xác định bằng protocol. **Không đưa 24 câu này vào NLL target answered pool hoặc mẫu số 96**; chấm đúng từ chối riêng, theo định nghĩa nhãn và cách nhận biết được prereg.
- Các câu hỏi và chứng cứ không được tạo bằng cách dùng TEST labels hoặc dồn các paraphrase cùng sự kiện qua nhiều split. TEST của study D1 được giữ sealed riêng; R_gold diagnostic có thể dùng một cohort chuyên biệt nhưng phải có khóa trước và không dùng để chọn cấu hình sau khi nhìn kết quả.
- **Ba điều kiện paired:** `R0` = không bằng chứng; `R_gold` = nguyên văn bằng chứng đúng; `R_wrong` = một đoạn tương đương độ dài nhưng không liên quan/sai theo rule xác lập từ group khác, không leak answer. Cùng Qwen checkpoint, tokenizer, target, decoding, length accounting.

### 4.2. Cách chấm và tiêu chí khả năng tối thiểu (ứng viên, CHƯA KHÓA)

**Primary:** `delta_gold_i = NLL_answer_only(R0,i) - NLL_answer_only(R_gold,i)`; dương tốt cho `R_gold`. Tính NLL token theo **chính Qwen tokenizer** và template frozen, cùng answer token IDs cho mỗi cặp; trung bình theo 2 câu trong nhóm rồi tính trung bình 48 nhóm.

**Candidate lock choices — chỉ để reviewer thẩm định, tuyệt đối không tự coi đã được khóa khoa học:**
- `DELTA_MIN_CANDIDATE=0.10` **nats / answer token** (cải thiện thực tiễn cần đánh giá trước duyệt; đây là giả định thiết kế, không phải kết quả pilot).
- `CI_CANDIDATE=95% paired group-bootstrap`, `BOOTSTRAP_REPLICATES_CANDIDATE=10000`, seed riêng cho QA thống kê `20261108`; candidate criterion `mean_delta >= 0.10 AND CI_lower > 0`.
- `EXACT_MATCH_GOLD_CANDIDATE >= 0.60` **và** `EXACT_MATCH_GOLD - EXACT_MATCH_R0 >= 0.10` (điểm tỷ lệ tuyệt đối, không phải tăng tương đối). Exact-match quy chuẩn hóa khoảng trắng/case/dấu câu theo rule pin; không cho chỉnh normalization sau xem kết quả.
- `R_WRONG_DIAGNOSTIC`: với cùng gold target, R_gold phải có mean NLL thấp hơn R_wrong (delta `NLL_wrong - NLL_gold > 0`); nếu R_wrong làm tốt ngang R_gold, phải xem xét cue/leakage/memorization. Có thể đưa CI hoặc threshold phụ vào prereg chính thức trước chạy.
- Chấm nhóm không có đáp án với exact match/rubric từ chối riêng, kèm tỷ lệ hallucination, **không** dùng chúng làm positive NLL answered; threshold từ chối `TBD_BY_REVIEW`.

**Trạng thái:** `THRESHOLDS_PROPOSED_NOT_APPROVED`. Reviewer phải khóa hoặc bác bỏ *trước thực nghiệm*, nêu lý do liên hệ công suất mẫu và năng lực 0.5B. Không điều chỉnh ngưỡng sau R_gold hoặc xem TEST; một ngưỡng tùy ý không tự tạo tính đúng khoa học.

**Scoring contract:** Tokenize prompt thông qua pinned Qwen chat template với assistant generation prefix; tokenize answer và EOS theo một chính sách ghép token-ID cố định tránh BPE merge qua biên; logits vị trí cuối prompt dự đoán token đáp án đầu tiên, mask `-100` cho prompt, kiểm full-answer fits `L_eff`. Các mẫu invalid/missing có ngưỡng dừng và phải báo số lượng, không chỉ xóa mẫu khó. Không so absolute token-NLL giữa Qwen và Pythia.

**Trạng thái kết luận:** `R_GOLD_PREREG_DRAFT_COMPLETE`; `R_GOLD_SAMPLES_NOT_GENERATED`; `R_GOLD_EXECUTION=NO`. Nếu một trong primary, evidence reliance, data integrity hoặc negative criteria không đạt khi thực hiện: `MODEL_CAPABILITY_GAP / INCONCLUSIVE` theo mẫu đã khóa, **không** diễn giải thành EmbeddingGemma thất bại.

## 5. Tiền đăng ký R1/R2/R3 — bỏ chồng nghĩa

| ID | Đầu vào và thao tác | Mục tiêu đo | Lưu ý không đếm trùng |
|---|---|---|---|
| `R1` | BM25/lexical chọn top-k từ **cùng corpus** | Baseline retrieval: `Recall@k, MRR@k, Hit@k` | Không ngầm tạo một RAG generation arm |
| `R2` | EmbeddingGemma 2 **text-only FP32 local**, query/doc prompts → cosine rank → khóa `doc_ids` | Retrieval semantic trên đúng corpus/query với R1 | **Không** chấm R2 như lần sinh GPT riêng nếu dùng cùng văn bản R3 |
| `R3` | Lấy nguyên văn bằng chứng của chính `doc_ids` R2 đã cố định rồi đưa vào frozen Qwen | Answer-only NLL/Exact Match theo Qwen và lỗi nguồn | Đây là **một** text-RAG generation baseline; không thêm Adapter |

**Candidate retrieval policy, sẽ cần khóa corpus/schema để hợp lệ:**
- `TOP_K_PRIMARY_CANDIDATE=3`, `TOP_K_SECONDARY_CANDIDATE=5`, giữ cùng retrieval candidate set/chunking/title/dedup/tie-break và `query_ids` cho R1/R2.
- Primary retrieval metric `mean_query(Recall@3)` khi `gold_doc_ids` có đủ thông tin; nếu mỗi query có một gold document, bổ sung `Hit@3` và `MRR@3` (không báo “Recall tăng” mà thiếu labels). `R2-R1` tính theo paired query/source groups, CI cùng group-level. Positive QA checkpoint **không** là thước đo retrieval.
- Khóa `chunker`, `source_uuid`, `index membership`, `query and doc prompt templates`, title policy, token budget và top-k **trước** held-out; vector 768d, L2-normalize, một chunk một vector, chưa mở Matryoshka ablation.
- Query prefix Google: `prompt_name="QuestionAnswering"` ⇒ `task: question answering | query: {question}`; tài liệu không title dùng `prompt_name="Document"` (tương đương `title: none`), tài liệu có title thực dùng `title: {title} | text: {content}` theo quy tắc khóa. Cấm lộ đáp án qua metadata/title.
- Truncation: `embedding_input <= 8192` **bao gồm prefix**, `Qwen_L_eff` gồm chat template + toàn văn evidence + target. `S_SHORT` đầy đủ evidence vừa context; `S_LONG` bị cắt evidence theo quy tắc không dùng nhãn. R3 chỉ tính Answer-only NLL trên suffix answer, không gồm prompt loss.
- Chi phí Google **API=0** vì không gọi API; Colab GPU/Drive/storage/download/energy vẫn phải kiểm tổng chi phí; không tự suy quyền corpus từ metadata mô hình.

**Chưa khóa:** corpus, actual gold doc labels, số query độc lập, độ lớn index và tỉ lệ hard negatives, quy tắc BM25 tokenizer/stopwords và retrieval significance/CI threshold; tất cả `HOLD_PREREG_LOCK`, không “lấp” bằng số đoán.

## 6. Trình tự một cửa, đã sửa vòng phụ thuộc

| Thứ tự | Giai đoạn | Hoạt động được phép sau quyết định riêng | Điều kiện kết thúc |
|---|---|---|---|
| 0 | **Design packet hôm nay** | Metadata read-only; soạn hồ sơ nguồn/quyền/prereg, không chạy | `DRAFT_COMMITTED / SCIENCE_NOT_AUTHORIZED` |
| 1 | **Một review thiết kế hợp nhất** | Thẩm định model SHA candidates, quyền corpus có chứng cứ, thresholds/metric/splits; ký khóa nếu đạt | `SOURCE_RIGHTS_PREREG_LOCKED` hoặc `HOLD` |
| 2 | **Một preflight kỹ thuật tích hợp riêng** | Chỉ sau khi quyền download/compute được duyệt: Colab env + disk/RAM/VRAM, pinned download, FP32 embedding sanity, Qwen frozen tokenizer/mask, synthetic fixture no-science, receipt FAIL preserved | `TECHNICAL_PREFLIGHT_PASS` hoặc `HOLD/FAIL` |
| 3 | **Một quyết định mở D1** | Hội tụ evidence và khoa học prereg; **không đòi R_gold PASS trước cấp quyền D1** | `D1_AUTHORIZED_ONCE` hoặc `HOLD` |
| 4 | **D1: R_gold chạy đầu tiên** | Chỉ positive/negative controls đã prereg, ghi kết quả kể cả FAIL | `R_GOLD_PASS` ⇒ xem xét R1–R3 *trong permit D1 cũ*; nếu FAIL/GAP/INCONCLUSIVE ⇒ STOP |
| 5 | **D1: R1/R2/R3** | Chỉ khi R_gold PASS và source/split đúng, giữ TEST sealed/timing theo prereg | Retrieval + generation verdict; **không** mở D2–D4 |
| 6 | **Đóng kết quả** | Independent QA khoa học, append-only `lineage.md` cho PASS/FAIL/INCONCLUSIVE khoa học; báo cáo | Quyết định kế tiếp độc lập |

**Quan trọng:** R_gold là kết quả khoa học nằm **bên trong D1**, không phải điều kiện phải đạt trước khi **cấp quyền D1**. Preflight kỹ thuật dùng fixture không khoa học, không đọc label của R_gold/TEST. Không thêm permit lẻ cho các kiểm tra kỹ thuật nhỏ. Nếu không có quyền dữ liệu/capacity/preflight: STOP, không tự kéo dài thực nghiệm.

## 7. Tài nguyên, môi trường và quyền tài nguyên: vẫn HOLD

- **GPU:** Colab Tesla T4 nếu có, 16 GB-class; Colab tài nguyên thay đổi theo session. `EmbeddingGemma 2 text-only FP32` ~270M×4B ≈ 1.08 GB chỉ trọng số, `Qwen FP16` ~0.49B×2B ≈ 0.99 GB chỉ trọng số; **không** kết luận peak VRAM hay nguồn download từ phép nhân này.
- T4 không giả định hỗ trợ BF16 native; EmbeddingGemma 2 `float16=FORBIDDEN` theo model card. Dùng text-only `vision_config=None,audio_config=None`, cache 768d có hash, chạy tuần tự (encode/cache ⇒ unload encoder ⇒ Qwen) để không giữ hai model cùng GPU. Nếu code loader bỏ sót config phải STOP thay vì silently load full model.
- **Khi được phép riêng mới** pin package versions, evaluate exact `SentenceTransformer` load args, CUDA/PyTorch/transformers, dtype policy, prompt names, `model_sha`, GPU runtime, disk/Drive cache/VRAM, outbound network/telemetry và abort thresholds. Thời gian huấn luyện Adapter/GGUF fusion ngoài scope D1.
- `TTM_SMALL_T4_RESOURCE_PRIORITY=FIRST`, không chiếm Colab quota/Drive hay thay pilot branch; chỉ xét D1 theo lịch sau ưu tiên T4.
- `MAX_COST_GOOGLE_API_USD=0`; không dùng API key, Gemini API Free Tier là chuyện của hồ sơ cũ không còn áp dụng. Local model vẫn có chi phí máy/đĩa/Colab.

## 8. Danh sách đóng hữu hạn và phán quyết tài liệu

| Mã | Cần trước kết luận “source-rights-prereg locked” | Trạng thái sau khi soạn |
|---|---|---|
| `L01` | 2 HF commit 40-char xác thực + danh mục file | `PASS_OBSERVED_SHA`, chưa tải byte |
| `L02` | File SHA256/licence+policy đúng revision, reproducible Python env | `HOLD_EXACT_FILES_AND_ENV` |
| `L03` | Đúng corpus, quyền (bao gồm biến đổi/cache vector), PII, attribution/splits | `HOLD_DATA_RIGHTS` |
| `L04` | Actual R_gold group manifests, no-answer plan, thresholds/CI/power independent review | `DRAFT_THRESHOLDS_NOT_LOCKED` |
| `L05` | R1/R2/R3 disjoint estimands, frozen retrieval policies/index/labels | `DESIGN_SCOPED / DATA_MISSING` |
| `L06` | Quy trình D1 preflight và R_gold-first không vòng phụ thuộc | `DESIGN_FIXED` |
| `L07` | T4 resource priority, Colab FP32 / local rights, no FP16 | `DESIGN_FIXED / CAPACITY_NOT_VERIFIED` |
| `L08` | Integrated reviewer verdict on actual receipts; no premature PASS | `NOT_ADJUDICATED` |

**Kết luận:** `CONSOLIDATED_DRAFT=WRITTEN`; `HF_REVISIONS=OBSERVED_NOT_FULLY_FILE_PINNED`; `DATA_RIGHTS=HOLD`; `R_GOLD_PREREG=LOCK_CANDIDATE_ONLY`; `R1_R2_R3_PREREG=LOCK_CANDIDATE_ONLY`; `SOURCE_RIGHTS_PREREG_FINAL_LOCK=NOT_ISSUED`; `D1_D4=NOT_AUTHORIZED`; `SCIENCE_EXECUTION=NONE`. Không tự ghi `lineage.md` cho tài liệu thiết kế.

**Bước thực hiện tiếp theo:** `TTM_EMBEDDINGGEMMA2_D1_CONSOLIDATED_PACKET_SINGLE_INTEGRATED_REVIEW_READONLY`: một lượt thẩm định duy nhất để xác nhận hai HF revision, xem xét ngưỡng R_gold và các lỗ hổng quyền corpus, kết luận `LOCK_READY` hoặc `HOLD_WITH_FINITE_GAPS`. Không chạy preflight T4 cho đến khi source/rights/prereg thích hợp được chấp nhận và có quyền download/compute riêng. TTM-Small T4 vẫn ưu tiên.
