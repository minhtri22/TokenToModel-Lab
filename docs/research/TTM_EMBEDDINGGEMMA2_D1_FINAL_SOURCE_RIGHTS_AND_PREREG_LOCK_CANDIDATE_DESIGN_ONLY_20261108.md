# TTM — EmbeddingGemma 2 D1: Hồ sơ G1–G4 cuối và phán quyết khóa tích hợp

**Mã công việc:** `TTM_EMBEDDINGGEMMA2_D1_FINAL_SOURCE_RIGHTS_AND_PREREG_LOCK_CANDIDATE_DESIGN_ONLY`  
**Ngày thẩm định:** 2026-11-08  
**Phán quyết duy nhất:** **`HOLD_WITH_FINITE_GAPS`**; `LOCK_READY=NO`; `PREREG_LOCK=NOT_ISSUED`; `D1_D4=NOT_AUTHORIZED`; `SCIENCE_EXECUTION=NONE`.  
**Tuyến chính:** TTM-Small-4M T4 ưu tiên trước; nhánh EmbeddingGemma 2 chỉ thiết kế, không tranh tài nguyên hay thay đổi kiến trúc TTM.  
**Repository:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh tài liệu:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108` (tên di sản; **model đúng là `google/embeddinggemma-2`, không phải Gemini API**).  
**HEAD trước tài liệu:** `2958f68e0b37ee23bc08495eccb0442952b24905`.  
**Main được xác minh:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.  
**Căn cứ chính (giữ nguyên):** `TTM_EMBEDDINGGEMMA2_D1_SOURCE_RIGHTS_AND_PREREG_CONSOLIDATED_LOCK_DRAFT_20261108.md`, Git blob `2ba46db5622a42b656c9c3f26589bd7aaa5f73f6`; A2, thiết kế D1 và các biên bản trước vẫn nguyên trạng.

> **Ranh giới:** Đây là hồ sơ thiết kế + phán quyết kiểm tra tài liệu, **không phải xác nhận độc lập của một người phản biện bên ngoài** và chưa là tiền đăng ký khoa học đã khóa. Chỉ ghi thêm tài liệu, không sửa `main`, PR #12, `lineage.md`, mã TTM, P00–P12, P07 hoặc nhánh pilot. Không tải model/weights/dataset, không tải hoặc chạy thư viện, không Colab, API, model inference, `R_gold`, retrieval, TEST, huấn luyện, merge, dọn repo/worktree.

## Quyết định tổng hợp: điều gì đã giải quyết, điều gì vẫn thiếu

| Gói | Điều đã hoàn thành trong một hồ sơ | Giới hạn có thật | Kết quả |
|---|---|---|---|
| G1 Nguồn/phiên bản | Hai HF commit SHA40 cụ thể; kiểm metadata model, Apache-2.0, quy tắc FP32, danh mục cần hash | Bản quyền/usage-policy tại exact revision cần receipt đầy đủ; downloaded-file SHA256 chỉ có sau khi tải được phép | `SOURCE_REVISIONS_IDENTIFIED / NOT_FULLY_FILE_QUALIFIED` |
| G2 Quyền dữ liệu | Chọn **ứng viên cụ thể** SQuAD và tuyến R_gold tự biên soạn; hợp đồng attribution/cache/split rõ | Chưa có corpus vật lý, quyết định quyền và manifest nhóm; không được tự gán quyền cho SQuAD hoặc corpus giả định | `DATA_RIGHTS_HOLD` |
| G3 R_gold | Có candidate cohort, một primary metric, candidate ngưỡng/CI, negative controls, masking, quy tắc STOP | 48 nhóm/12 nhóm âm tính **chưa sinh**, không có source-split SHA và chưa duyệt sức mạnh thống kê/threshold | `R_GOLD_LOCK_CANDIDATE / NOT_LOCKED` |
| G4 R1/R2/R3 | Cùng source/corpus, top-k, metric, paired group, prompt rules, tách retrieval khỏi generation, thứ tự D1 hợp lệ | Chưa có actual doc/query/gold mapping, tokenizer BM25 cụ thể và split manifest; no TEST authorization | `RETRIEVAL_LOCK_CANDIDATE / NOT_LOCKED` |

**Nguyên tắc không tăng thủ tục:** Một quyết định khóa từ G1–G4; nếu còn dữ liệu thiếu, chỉ điền đúng các trường thiếu trong cùng packet rồi quyết định lại **một lần**, không cấp phép riêng cho từng manifest/QA con. Quyền download/Colab và khoa học là hai quyết định tiếp theo có thẩm quyền khác, không được gộp vào việc viết tài liệu.

---

## G1 — Nhận diện và quyền mô hình: kết quả đối chiếu

### G1.1. Nguồn và revision được kiểm

| Vai trò | Repository | Revision HF SHA40 ứng viên để pin | License công bố | Chức năng |
|---|---|---|---|---|
| Embedding | `google/embeddinggemma-2` | `f9972ac22e696a105c482202646979e33e4b5a1e` | Apache-2.0 theo model card | Embedding cục bộ, text-only, `768d`, FP32 |
| Frozen Qwen | `Qwen/Qwen2.5-0.5B-Instruct` | `7ae557604adf67be50417f59c2c2f167def9a775` | Apache-2.0 và tệp LICENSE tại revision | `R0/R_gold/R3` |
| Pythia | `EleutherAI/pythia-160m-deduped` | Không pin trong D1 | Apache-2.0 theo card | Đối chứng kế tiếp, không dùng D1 |

- Google SHA đã mở và ghi nhận là **commit xác thực công khai**: https://huggingface.co/google/embeddinggemma-2/commit/f9972ac22e696a105c482202646979e33e4b5a1e . Không thể suy ra hash của `model.safetensors` từ hash commit; một số đường xem tệp của HF trả lỗi truy cập; ghi đúng `FILE_HASHES_NOT_VERIFIED`.
- Qwen revision với `LICENSE` có thể đọc tại https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/blob/7ae557604adf67be50417f59c2c2f167def9a775/LICENSE và danh mục file tại https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/tree/7ae557604adf67be50417f59c2c2f167def9a775 .
- Tài liệu Google: https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2 — text-only khoảng 270M/đa phương thức khoảng 740M, native output 768, context embedding 8192; từ model card: **không sử dụng float16**, vì NaN hoặc sai ngầm; Colab Tesla T4 thiết kế `torch.float32` cho encoder, `bfloat16` chỉ nếu thực sự có phần cứng native (không giả định T4).
- Model card Google công bố Apache-2.0 **và** yêu cầu tuân thủ `Gemma Prohibited Use Policy`: https://ai.google.dev/gemma/prohibited_use_policy . Cần kiểm đúng điều khoản áp dụng cho nguồn tại thời điểm sử dụng; không được suy diễn giấy phép mô hình thành quyền nội dung corpus. Qwen Apache-2.0 có nghĩa vụ lưu license và attribution khi phân phối.
- Chỉ dùng `revision=SHA40` cho model/tokenizer/config trong tương lai; không dùng `main` thay cho khóa chính thức. Phải pin `python, torch, transformers, sentence-transformers, tokenizers, safetensors`, các mã file `config, README/license, modules/pooling/normalize, tokenizer, weight shards`, prompt template và I/O precision. **Không tải trong công việc này.**

### G1.2. Phân ranh tiền kiểm và tiền đăng ký

**Phải xác thực trước khi LOCK_READY:** repo+SHA40, license/policy áp dụng, danh sách file/size và phương pháp có thể kiểm LFS/Xet hash, model/dtype/embedding dimension, ghi rõ giới hạn sử dụng, không cần **SHA256 thực của byte chưa tải**. Tải byte và so SHA256 là một phần **tiền kiểm kỹ thuật tích hợp sau khi có phép download**, không bắt làm điều không thể ở bước chỉ tài liệu.

**Một điểm còn thiếu trước khi LOCK_READY:** bản ghi rà soát giấy phép/chính sách *theo hai revision đã ghim*, đối chiếu mô hình Qwen và Google với mục đích D1; có thể hoàn tất read-only khi thực hiện gói quyền dữ liệu G2.

---

## G2 — Chọn đường dữ liệu cụ thể và quyền sử dụng

### G2.1. Lựa chọn một nguồn ứng viên, chưa nhận quyền tự động

**Nguồn retrieval được đề nghị:** `rajpurkar/squad` (SQuAD, text QA trên đoạn văn Wikipedia), https://huggingface.co/datasets/rajpurkar/squad . Metadata Hugging Face công bố **`cc-by-sa-4.0`** cho dataset, với nguồn bài viết Wikipedia. Vì dữ liệu chứa bài Wikipedia có quyền/tuyên bố nguồn riêng, **chưa coi metadata license của dataset là quyền đầy đủ để xử lý mọi đoạn, nhúng, tạo cache, công bố lại**. Cần rà soát provenance Wikipedia, CC BY-SA attribution/share-alike, điều kiện giữ/không giữ dữ liệu riêng và quyền chuyển đổi/cached vector trước khi chấp nhận.

**Vì sao chọn SQuAD:** văn bản chứng cứ và cặp câu hỏi/đáp án đã tồn tại để xây baseline R3; không cần suy diễn đáp án từ SciFact (nhiệm vụ kiểm chứng claim khác). Không dùng `mteb/scifact` thay thế ngầm vì metadata của mteb/scifact nêu `license:unknown`. Nguồn SQuAD chỉ là **ứng viên** cho R1/R2/R3, không là TEST đã được cấp phép.

**R_gold tách riêng:** câu chuyện ngắn *hư cấu do dự án chủ động tạo mới* với các thực thể và thuộc tính bịa đặt (không PII); chỉ dùng sau khi tác giả/chủ dự án xác nhận quyền sử dụng, nguồn công cụ tạo (nếu có), và có danh mục mẫu được QA. Không chép dữ liệu TinyStories pilot hoặc chọn câu trả lời dựa trên nhãn TEST.

### G2.2. Hợp đồng cohort và split có thể tái lập

- `R_GOLD_POSITIVE`: **48 nhóm độc lập**, 2 câu hỏi/group gồm 1 trực tiếp và 1 paraphrase, tổng **96** câu answered. Mỗi nhóm có một bằng chứng ngắn với đáp án đã ghi và kiểm chứng; tài liệu/tiêu đề không chứa nhãn giấu.
- `R_GOLD_NEGATIVE`: **12 nhóm độc lập** khác, 2 câu hỏi/group, tổng **24** câu không có đáp án trong evidence. Không trộn denominator 24 vào NLL positive.
- `RETRIEVAL`: nhóm theo **Wikipedia article/source document**, không chia ngẫu nhiên theo câu hỏi; danh mục passage index cho R1/R2 là như nhau. Gold `doc_id` dẫn tới đoạn có answer text nguyên bản; một bài có nhiều đoạn/answer cần khóa `gold_doc_ids` một cách nhất quán.
- Khai báo trước index có bao gồm tài liệu eval (được phép nếu mô phỏng corpus truy vấn sẵn có) và nhãn đánh giá nằm riêng/không vào embedding/queries. Tiêu chí phân nhóm/split cần tránh cùng bài hoặc paraphrase xuyên TRAIN/VAL/TEST; tránh nhầm split có sẵn SQuAD là chống leakage đủ.
- Manifest tối thiểu mỗi hàng: `source_uri, upstream_license, license_snapshot_sha, owner_or_attribution, allowed_embedding_and_cache, pii_status, article_group_id, passage_doc_id, passage_sha256, question_id, question_sha256, answer_id_hash, annotation_source, split, split_sha256, chunker_hash, duplicate_policy`.
- Dữ liệu R_gold/QA và index phải được materialize và hash **ở bước được cho phép sau này**, không trong nhiệm vụ chỉ thiết kế này. Quyền phải có quyết định minh thị trước khi tải corpus, không suy luận từ tên repo.
- Nếu chỉ dùng dữ liệu tự tạo, giới hạn kết luận `SYNTHETIC_DIAGNOSTIC_ONLY`; không được nói RAG thực tế được xác nhận.

**Phán quyết G2:** `DATASET_CANDIDATE_SELECTED` nhưng `DATA_RIGHTS_AND_MANIFEST=HOLD`; đây là **blocker thực sự** với `LOCK_READY`, không thể khắc phục bằng điền SHA giả định.

---

## G3 — Tiền đăng ký `R_gold`: phiên bản ứng viên cuối cho xét khóa

**Chỉ Qwen đã ghim; không dùng EmbeddingGemma hay huấn luyện.** `R0`: cùng câu hỏi, không evidence; `R_gold`: cùng question+answer target với evidence đúng nguyên văn; `R_wrong`: đoạn nhiễu khác group có độ dài gần tương đương, được chọn bằng quy tắc không nhìn nhãn/tác dụng lên mô hình. `R_wrong` là negative evidence control, không là đối chứng có đáp án cạnh tranh không định nghĩa.

### Primary estimand

Với 2 câu hỏi trong mỗi source group, tính trung bình NLL đã chuẩn hóa trên số token answer **trong từng câu**; tính `d_g = mean_{i in group g}[NLL_R0,i - NLL_Rgold,i]`; thống kê `mean_g d_g`, dương tốt.

- `N_GROUP=48`, `N_QA=96`; nhóm âm tính 12/24 riêng. Độ lệch giữa hai paraphrase trong cùng group không được tính như hai quan sát độc lập.
- `R_gold` không được dùng để lựa chọn Qwen prompt, seed hoặc template sau khi nhìn kết quả; `Qwen` checkpoint/tokenizer/cấu hình decoding bị khóa trước khi đánh giá.
- **Ứng viên ngưỡng khoa học rõ nghĩa (chưa có phê duyệt chính thức):** `DELTA_MIN=0.10 nats / answer token` và `95% CI lower bound > 0.10` từ **10.000 lần paired group bootstrap** resample 48 source groups with replacement; `bootstrap_seed=20261108`. Điều kiện này, nếu sau này đạt, mới có căn cứ 95% CI một phía hữu ích cho mức vượt 0.10; khác với điều kiện cũ `mean_delta>=0.10 && CI_lower>0` chỉ có bằng chứng hiệu ứng dương và chênh trung bình quan sát >=0.10.
- Phụ trợ **không thay primary**: `ExactMatch(R_gold) >= 0.60` và `ExactMatch(R_gold) - ExactMatch(R0) >= 0.10` điểm tỷ lệ tuyệt đối. Cần định nghĩa trước normalize case/whitespace/punctuation/Unicode và cách chấm multiple acceptable answers.
- `R_wrong`: `mean_group[NLL_Rwrong - NLL_Rgold] > 0` là kiểm định chẩn đoán reliance; nếu không đạt, đánh dấu `EVIDENCE_RELIANCE_INCONCLUSIVE`, không đánh đồng improvement do model đọc evidence.
- Nhóm không đáp án: định nghĩa gold output cố định `UNKNOWN`/từ chối, exact rubric và chấm `24` quan sát từ 12 group; báo `false-answer rate`, **không gộp vào primary NLL**. Đề xuất guardrail không quá 6/24 câu trả lời bịa (ngưỡng cần reviewer duyệt), nhưng **n=12 group** không đủ để khẳng định an toàn ngoài phạm vi chẩn đoán.
- Nếu group/câu bị lỗi token/truncation hay thiếu quyền: không xóa lặng lẽ hoặc bổ sung sau khi xem kết quả. Quy tắc ứng viên: `0` mẫu không đủ evidence hoặc hết context; trường hợp không đạt => `INCONCLUSIVE_DATA_INTEGRITY`/STOP trước TEST, không tăng dữ liệu theo kết quả.

**Answer-only NLL contract:** dùng pinned Qwen `apply_chat_template(add_generation_prompt=True)` cho prefix, một lựa chọn cố định xây `input_ids = prefix_ids + answer_ids + eos_ids`; **không** giả định BPE của toàn chuỗi tương đương ghép hai phần. `logits[t]` dự đoán `input_ids[t+1]`; target-label mask `-100` cho prompt, mọi target token thuộc answer được chấm đúng tại vị trí logit trước nó; không chấm prompt; toàn answer phải nằm trong `L_eff`. Report per sample/paired group/CI, không chỉnh sau TEST. Nếu đầu answer cùng delimiter làm khác tokenization, phải khóa chính sách token-ID ngay từ source/config và kiểm trên synthetic fixture trước inference.

**Thẩm định thống kê:** ngưỡng 0.10 và EM 0.60 vẫn là **quyết định ứng viên** không có dữ liệu hiệu chuẩn/power. Nếu reviewer không chấp nhận CI bound >0.10 với 48 nhóm, phải quyết định **trước run**, bằng lập luận sensitivity/power mô phỏng lý thuyết được phép hoặc thay đổi `N_GROUP` trong hồ sơ tiền đăng ký; không đánh giá 0.10 hậu nghiệm. Chỉ người có thẩm quyền mới có thể khóa.

**Luồng phán quyết nếu thực hiện sau này:** `PASS_COMPETENCE` chỉ khi đáp ứng primary, EM và evidence-reliance cùng integrity; `FAIL_MODEL_CAPABILITY` chỉ khi dữ liệu hợp lệ, đủ mẫu và tiêu chí năng lực không đạt; `INCONCLUSIVE` nếu thiếu dữ liệu, CI không xác lập, missing/capacity/rights. Thất bại R_gold **không** chứng minh EmbeddingGemma kém.

**G3 hôm nay:** `METRICS_AND_THRESHOLDS_CANDIDATE_FIXED_IN_TEXT`; `REVIEWER_APPROVAL=NOT_PRESENT`; `ACTUAL_COHORT=NOT_CREATED`; `PREREG_LOCK=NOT_ISSUED`.

---

## G4 — Tiền đăng ký R1/R2/R3: nhiệm vụ và quyền suy luận tách biệt

### G4.1. Retrieval R1/R2 (paired trên cùng tập tài liệu)

| Nhánh | Định nghĩa | Chỉ số |
|---|---|---|
| `R1` | BM25 lexical top-k, `same corpus/docs/chunks/query_ids`, tokenizer/case/stopword/tie-break được pin | `Hit@3` hoặc `Recall@3`, `MRR@3` nếu có gold relevance |
| `R2` | EmbeddingGemma2 text-only FP32, local; query `QuestionAnswering`, docs `Document`/title; normalized 768d cosine top-k | **Cùng** các metric và nhãn như R1 |
| `R3` | Qwen frozen chỉ nhận **source text** của chính `R2.doc_ids` đã khóa, không dùng vector trong model | Answer-only NLL, Exact Match, evidence coverage/truncation |

- `TOP_K_PRIMARY=3`; `TOP_K_SECONDARY=5` chỉ descriptive. `R2-R1` đo **paired group-level retrieval quality**; group theo article, không xem câu hỏi hay token là sample độc lập. Nếu có một gold document/query, `Hit@3` chính bằng `Recall@3`; nếu nhiều gold docs, định nghĩa macro Recall@3 trên full gold set, không trộn denominator.
- **Ứng viên metric chấp nhận retrieval:** `Delta_Recall@3 = mean_group(Recall_R2 - Recall_R1)`, mean positive và 95% paired group-bootstrap lower >0. Đây là chứng cứ ứng viên cho retrieval gain trong corpus D1, **không** là cổng để kết luận semantics chung, và chưa thể khóa khi số nhóm/gold policy chưa quyết.
- `N_source_groups`, mỗi group bao nhiêu queries, số distractor, cách xây index trên SQuAD, exact/near-duplicate, threshold/CI, BM25 stemming/stopwords và language mix cần chọn **trước khi mở D1**, được điền vào manifest sau khi có quyền corpus. Không tự biến ví dụ `N=48` của R_gold thành cỡ mẫu retrieval.
- Query template Google: `prompt_name="QuestionAnswering"`; document không title `prompt_name="Document"` `title:none`; document có title tự nhiên `title: {title} | text: {chunk}`, không lấy title từ nhãn/câu trả lời. Full embedding input (prefix + content) không quá 8192 token; một chunk → một vector, hash vector/cache/revision/template. `EmbeddingGemma 2 FP16=FORBIDDEN`; `FP32` cho Colab Tesla T4; cosine trên vector `normalize_embeddings=True`.
- BM25 và embedding **cùng** candidate set, doc IDs, chunk bytes, snapshot, cùng điều kiện được nhìn corpus. R1 là baseline retrieval **chứ không tự có generation arm**; R2 chỉ tạo danh sách doc IDs, R3 mới là generation arm. **Không đếm R2 và R3 thành hai lần Qwen trả lời độc lập**.
- Trong R3 có thể phân loại `S_SHORT` nếu full evidence + Qwen chat prefix + full answer fit `L_eff`, `S_LONG` nếu không; primary generation chỉ phân tích S_SHORT, S_LONG báo riêng và có source-truncation rule cố định không nhìn nhãn. Cấm lấy `R_gold` label để chọn passages ở R2 hay tune R3.
- `Answer-only NLL` và `Exact Match` của R3 chỉ so với đối chứng sinh văn bản có **cùng frozen Qwen/tokenizer và target** (chẳng hạn R0/R_gold dưới protocol tương ứng), không trực tiếp so NLL với điểm BM25/cosine.

### G4.2. Trạng thái khi chưa có corpus

`R1_R2_R3_RETRIEVAL_PROTOCOL=DOCUMENTED`; `CORPUS_AND_INDEX_MANIFEST=MISSING`; `GOLD_DOC_LABELS=MISSING`; `BM25_TOKENIZATION=NOT_PINNED`; `RETRIEVAL_GROUP_COUNT=UNSET`; `STATISTICAL_LOCK=NOT_ISSUED`. Đây là **đúng bốn trường cần đóng cùng G2**, không mở một quy trình mới.

---

## Quyết định khóa tiền đăng ký: một lần và có lý do

**Phán quyết:** `HOLD_WITH_FINITE_GAPS`, **không** `LOCK_READY`, vì:

1. **G2:** Chưa có quyền được thẩm định cho một corpus thực sự, chưa có hàng dữ liệu/group IDs, manifest split hay provenance nhãn. SQuAD CC BY-SA-4.0 là **ứng viên nguồn có metadata**; chưa đủ chứng minh quyền mọi nội dung Wikipedia hoặc cached vectors.
2. **G3:** Các ngưỡng/dự kiến số mẫu đã được làm rõ nhưng cần quyết định tiền đăng ký có thẩm quyền và nhóm R_gold thực tế; không thể cấp `PASS_SCIENCE` cho các ví dụ chưa được tạo hoặc reviewer chưa duyệt.
3. **G4:** Chưa có số lượng query/group thực, index, gold doc ids, BM25 policy, do đó không thể khóa phép so R1 vs R2 trên held-out; tránh ép sử dụng TEST trước khi phê duyệt.
4. **G1:** Đã có 2 revision được nhận diện công khai; việc chi tiết file SHA256 sau download là **preflight**, không phải blocker logic của prereg. Cần receipt license/usage policy đúng revision trước khi cho phép tải.

### Bốn đầu vào thiếu, gom vào một packet bổ sung (không lập thủ tục con)

| ID | Người/nguồn bổ sung | Receipt bắt buộc để quyết định `LOCK_READY` |
|---|---|---|
| `CLOSE-G1` | Documenter/checker | License/usage snapshot tại pinned HF SHAs, file listing/expected remote hash strategy, quyền sử dụng mô hình trong D1; ghi nhận không có local weights |
| `CLOSE-G2` | Chủ dữ liệu/người chuẩn bị nguồn | Corpus cụ thể có quyền (SQuAD sau quyền nguồn/attribution, hoặc hoàn toàn tự biên soạn); `source+rights+split+annotation manifest`, nhóm và SHA các tệp dữ liệu nếu có quyền materialize |
| `CLOSE-G3` | Prereg author + independent protocol reviewer | Quy tắc 48/12 groups, nguồn mẫu, NLL/CI/EM/abstention, kết luận duyệt hoặc bác 0.10 và cỡ mẫu, signed scientific prereg source pin |
| `CLOSE-G4` | Retrieval protocol owner | Actual retrieval corpus/index/gold policy, số query/source groups, tokenization BM25, top-k/Recall metrics, paired bootstrap và freeze; chặn TEST peek |

**Không được thay thế missing evidence bằng giá trị đoán hoặc 'PASS' do tài liệu tự viết.** Nếu mẫu chưa materialize do owner chưa cấp quyền, gói đóng có thể chứa tuyên bố quyền và kế hoạch xác định tập sealed, nhưng không được khẳng định split/hash hiện hữu.

**Quy tắc ra quyết định tiếp theo (một lần):**
- Nếu cả `CLOSE-G1..G4` có receipts hợp lệ và reviewer xác nhận không có leakage, khóa corpus, mẫu, ngưỡng và phương pháp: `LOCK_READY` (chỉ là **prereg design lock**).
- Nếu một receipt thiếu, quyền bất hợp lệ hoặc ngưỡng chưa được chấp thuận: `HOLD_WITH_FINITE_GAPS` và ghi đúng ID thiếu. Không tạo thêm nhiệm vụ QA/permit lẻ.
- **`LOCK_READY` không tự cấp quyền download/Colab/D1**. Sau khi có quyền tài nguyên riêng mới **một lần** preflight tích hợp Tesla T4, kiểm exact weights SHA256, cấu hình/FP32, tokenizer, CUDA, memory/Drive, shape/finite/norm/abort trên zero-science fixture, receipt independent. Sau preflight hợp lệ mới có quyết định mở D1; bên trong D1 chạy `R_gold` đầu, nếu `R_gold` PASS mới chuyển R1–R3 trong cùng quyền, không micro-permit.
- TTM-Small T4 luôn đi trước về ưu tiên GPU/Colab/Drive. Mọi kết quả khoa học PASS, FAIL, INCONCLUSIVE được ghi `lineage.md` **append-only sau thực nghiệm**, không ghi review thiết kế hay QA kỹ thuật.

**Trạng thái cuối:** `G1=SOURCE_METADATA_VERIFIED_WITH_FILE_QA_DEFERRED`; `G2=DATA_RIGHTS_HOLD`; `G3=PREREG_CANDIDATE_NOT_APPROVED`; `G4=RETRIEVAL_DATA_DEPENDENT_HOLD`; `SINGLE_ADJUDICATION=HOLD_WITH_FINITE_GAPS`; `D1_D4=NOT_AUTHORIZED`; `DOWNLOADS=NONE`; `API_CALLS=NONE`; `SCIENCE_RUNS=NONE`; `TTM_SMALL_T4=PRIORITY_FIRST`.

**Bước thực hiện tiếp theo duy nhất:** `TTM_EMBEDDINGGEMMA2_D1_CLOSE_G1_G4_WITH_REAL_CORPUS_AND_ONE_LOCK_DECISION` — chỉ tập hợp bốn receipt `CLOSE-G1..G4` trong cùng hồ sơ (đặc biệt chọn/duyệt corpus và R_gold cohort); sau đó ra **một quyết định khóa** mới. Chưa tải model, không chạy Colab trước quyền riêng.
