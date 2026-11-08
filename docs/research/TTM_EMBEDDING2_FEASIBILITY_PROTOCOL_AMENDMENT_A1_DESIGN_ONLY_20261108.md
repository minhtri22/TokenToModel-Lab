# TTM — Phụ lục A1: Sửa hợp đồng đối chứng Gemini Embedding 2 / Text / Adapter

**Công việc:** `TTM_EMBEDDING2_FEASIBILITY_PROTOCOL_AMENDMENT_A1_DESIGN_ONLY`  
**Ngày:** 2026-11-08  
**Trạng thái:** `A1_DESIGN_WRITTEN_REVIEW_PENDING` — **chưa là tiền đăng ký khoa học đã khóa, chưa cấp quyền D1**  
**Kho:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`  
**Base nhánh nghiên cứu trước A1:** `9855a44105c38ca4f4954a15da9ae3490b8e58a5`  
**Base `main` khi xác minh:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`

## 0. Phạm vi và thẩm quyền

Đây là **phụ lục bổ sung, không sửa hồi tố** ba tài liệu đã có trên nhánh:

1. `TTM_GEMINI_EMBEDDING2_GQA_PAGEDATTENTION_FEASIBILITY_DESIGN_20261108.md` — thiết kế ban đầu; blob `10c4818abcf154e67244c0cc289c468f42b1fbf0`.
2. `TTM_EMBEDDING2_FEASIBILITY_INDEPENDENT_DESIGN_REVIEW_20261108.md` — phản biện A0, kết luận `REVISE_REQUIRED`, `CAUSE_ATTRIBUTION_PROTOCOL=FAIL`; blob `9e6cd37cb83efdc52622aa49abf68bfbf8db1cc8`.
3. `TTM_EMBEDDING2_FREE_TIER_DESIGN_CORRECTION_20261108.md` — `FREE_TIER_FIRST`, mục tiêu chi phí API $0; blob `6198a17cb57fe9124aed2d74a3d0fdc44d754e2d`.

**A1 chỉ làm rõ thiết kế, chưa chứng minh khắc phục thành công lỗi đối chứng cho đến khi có thẩm định lại.** Không triển khai runner, không thay P02/P00–P12, không huấn luyện, không lấy checkpoint, không gọi API hoặc tạo embedding, không mở D1–D4, không ghi `lineage.md`, không sửa PR #12, không merge, không dọn Git refs/Worktree.

## 1. Hai đại lượng cần ước lượng (Estimands) — không đánh đồng

### E_SYS — Giá trị của hệ thống kết hợp

- So sánh `R3` (GPT đóng băng + văn bản từ cùng evidence IDs) với `V1` (GPT **cùng checkpoint đóng băng** + vector Gemini Embedding 2 + Adapter/Cross-Attention được học).
- Trả lời: **Toàn bộ giải pháp vector + thành phần học mới có đáng giá hơn text-RAG theo chất lượng/chi phí không?**
- Không được suy ra ưu thế riêng của embedding, Attention hoặc thông tin khi so E_SYS, vì V1 có thêm năng lực học và kênh điều kiện ngoài ngữ cảnh.

### E_REPR — Giá trị biểu diễn có điều kiện trên cơ chế kết hợp đã giữ cố định

- So sánh `R4` (GPT đóng băng + **bằng chứng văn bản được mã hóa bằng đường nội bộ không dùng Gemini** + Adapter/Cross-Attention được huấn luyện) với `V1` (cùng checkpoint, cấu trúc Adapter/Cross-Attention, dữ liệu/train budget, nhưng nguồn biểu diễn Gemini).
- Trả lời: **Trong cơ chế fusion và ngân sách học xấp xỉ ngang nhau, việc sử dụng biểu diễn Gemini thay nguồn biểu diễn văn bản nội bộ có ích không?**
- Kết luận vẫn là so sánh **hai pipeline biểu diễn**; không chứng minh thuần túy kiến trúc Cross-Attention tốt hơn văn bản gốc hoặc embedding Google ưu việt do riêng kiến trúc. Cần `V3` để cô lập hiệu ứng cross-attention, báo cáo độ lệch năng lực bộ mã hóa tiền huấn luyện.
- Nếu R4 không khớp tham số, huấn luyện, evidence IDs, mục tiêu chấm hay điều kiện truy cập thông tin: gắn `ATTRIBUTION_LIMITED` hoặc `INCONCLUSIVE`, **không** tuyên bố nhân quả.

**Phương sai và ngưỡng khoa học:** chưa khóa `delta_min`, tập mẫu, seed, khoảng tin cậy, số lượt bootstrap, ngân sách huấn luyện. Phải tiền đăng ký trước D3; A1 **không** cấp quyền tự xác định chúng từ TEST hoặc sau khi xem kết quả.

## 2. Ma trận A/B sửa đổi

| ID | Dữ liệu điều kiện | GPT backbone | Fusion / tham số mới | Vai trò |
|---|---|---|---|---|
| `R0` | Không có evidence | frozen TTM | Không | Năng lực cơ sở |
| `R1` | Lexical/BM25 → văn bản gốc | frozen TTM | Không | Retrieval cổ điển |
| `R2` | Gemini retrieval → văn bản gốc | frozen TTM | Không | Giá trị retrieval của Gemini, không phải fusion |
| `R3` | **Cùng evidence IDs đã chốt** → văn bản vào prompt | frozen TTM | Không | Text-RAG đối chứng triển khai cho `E_SYS` |
| `R4` | **Cùng evidence IDs** → text encoder frozen không dùng Gemini → các vector theo chunk | frozen TTM | **Adapter + cùng Cross-Attention/gate** được học như V1 | Đối chứng có học cho `E_REPR` |
| `V1` | **Cùng evidence IDs** → Gemini Embedding 2 theo từng chunk | frozen TTM | **Adapter + Cross-Attention/gate** | Phương án nghiên cứu |
| `V2a` | Thay vector đúng bằng vector tráo/random **khi đánh giá V1** | frozen TTM | Giữ nguyên V1 đã học | Kiểm tra V1 có thực sự dùng dữ liệu evidence |
| `V2b` | Vector ngẫu nhiên/tráo được cung cấp **khi huấn luyện từ đầu** | frozen TTM | Cùng số tham số/budget như V1 | Đối chứng năng lực học/độ nhạy dữ liệu |
| `V3` | Vector Gemini đúng theo chunk | frozen TTM | Phép chiếu/gộp đơn giản có capacity được báo cáo, **không Cross-Attention** | Tác dụng riêng của cơ chế fusion |
| `R_gold` | Bằng chứng **đúng do bộ benchmark chỉ rõ**, đưa trực tiếp bằng văn bản | frozen TTM | Không | **Kiểm tra năng lực GPT**, không phải đường sản phẩm hay oracle retrieval |
| `I1/I2` | Evidence như R3 | Cache dense/paged; MHA/GQA ở thí nghiệm riêng | Không lẫn với V1 | Tối ưu hiệu năng, ngoài E_SYS/E_REPR |

**Quy trình chọn bằng chứng:** Bộ doc IDs của R3/R4/V1/V2/V3 được xác lập **một lần** theo retrieval policy, snapshot/corpus/index cố định trước đánh giá; không điều chỉnh top-k theo nhãn. Với E_REPR, buộc cùng số chunk và cùng source bytes; nếu `R2` chọn evidence bằng Gemini, cần ghi rõ cả R3/R4/V1 cùng hưởng lợi từ bộ chọn này, và không quy hiệu quả retrieval cho fusion.

## 3. Hợp đồng R4: có học tương ứng và điều kiện so sánh

**Đường R4 dự kiến:**
```text
same evidence text chunks
   -> frozen TTM tokenizer
   -> deterministic frozen text representation per chunk
      (candidate: mean-pool token embeddings OR frozen GPT chunk encoder)
   -> fixed, non-trainable dimensional bridge if needed
   -> same trainable projection / normalization / cross-attention / gated fusion as V1
   -> same frozen GPT / LM head; same answer-only targets
```
- Chọn **một** bộ mã hóa text cố định và công bố độ mạnh của nó trước thí nghiệm; token-embedding mean pooling là đối chứng yếu, không được gọi là tương đương sức biểu diễn Gemini. Có thể thêm frozen contextual text encoder như kiểm tra độ nhạy, không đổi sau khi xem TEST.
- Đầu vào adapter cho cả R4/V1 dự kiến `[B,m,768]` (768 là **ứng viên, chưa khóa**). R4 có thể từ biểu diễn `[B,m,256]` dùng phép biến đổi cố định (ví dụ zero-padding theo quy tắc pinned) để thành 768; không cho phép thêm trainable projection cho chỉ một đường rồi coi tham số đã match. Khóa cùng `m`, cùng evidence/source.
- **Cùng** checkpoint GPT backbone, optimizer/scheduler, training examples, answer targets, number of updates, effective tokens/steps, seed list, early-stop policy và checkpoint/resume; chỉ khác nguồn biểu diễn. Báo cáo chính xác `trainable_parameter_count`, FLOPs/step, số token xử lý cho text encoder và embedding API.
- Nếu không đạt tương đương sức học trong ngưỡng thiết kế được khóa, so sánh chỉ đủ để đưa ra kết luận hệ thống hoặc mang tính khám phá.
- Cả R4 và V1 **được huấn luyện độc lập** (cùng cấu hình/seed ban đầu cho các module đồng cấu trúc, không dùng cùng trọng số adapter đã học); GPT backbone luôn frozen. Không vô tình cập nhật LayerNorm/LM head/backbone hoặc vector API.
- Một vector trên mỗi chunk; với `m=1`, softmax cross-attn chỉ có một vị trí khóa, **không thể thử lựa chọn evidence bằng Attention**; cần case `m>1` trước khi tuyên bố chọn lọc bằng Attention.

## 4. R_gold — cổng năng lực tối thiểu của checkpoint (positive control)

**Mục đích:** xem GPT thực sự tận dụng được bằng chứng ngắn trong ngữ cảnh, trước khi bỏ thời gian/chi phí để so embedding với adapter. `R_gold` là phép kiểm dựa trên câu trả lời đã biết từ tập benchmark được chuẩn bị hợp lệ, **không được dùng nhãn TEST để chọn cấu hình, prompt hoặc retrieval**.

- Đối chứng cặp: `R0` không bằng chứng và `R_gold` có chính xác bằng chứng gốc chứa thông tin để trả lời. Ghi paired `answer-only NLL` và độ đúng/forced-choice với cùng answer targets.
- Chỉ kiểm `S_SHORT` đã có đủ chỗ trong 256 token; không cắt câu hỏi hoặc bằng chứng gold để vừa chỗ rồi gọi positive control thành công.
- Năng lực tối thiểu `minimum_competence` phải có **định nghĩa định lượng và ngưỡng khóa trước** (ví dụ mức cải thiện NLL có ý nghĩa so với R0 và độ chính xác tối thiểu trên VALID/diagnostic riêng). A1 không bịa con số PASS.
- Nếu mô hình T4 đã train chỉ là TinyStories next-token LM và không làm được hỏi đáp: ghi `MODEL_CAPABILITY_GAP`, trì hoãn D1; không tự nhận Gemini/Adapter thất bại. Không dùng TEST để sửa thành mô hình QA giỏi hơn.
- Việc có checkpoint **đúng loại** và đủ năng lực có thể cần một task/corpus/scale khác; đây phải là quyết định successor không sửa ngầm T4.

## 5. S_SHORT / S_LONG — hai tầng câu hỏi khác nhau

**Định nghĩa trước khi thử:** với mỗi mẫu, lấy `T_max` từ checkpoint TTM (ứng viên 256), `Q` token câu hỏi và khuôn trả lời, `D` token **toàn bộ cùng evidence text** và `Y` token đáp án cần scoring. Dùng *đúng tokenizer TTM*.

- `S_SHORT`: toàn bộ `Q + D + Y` (kể cả separator/special tokens và prefix để teacher force) thỏa `T_max`; **không được cắt bằng chứng** ở R3. Các đường R3/R4/V1 có cùng source bytes, doc IDs, số chunk; V1/R4 vẫn có side-channel nhưng không có lợi thế do vượt giới hạn cửa sổ so với text path.
- `S_LONG`: `Q+D+Y>T_max`. R3 áp dụng **một quy tắc truncate cố định, không nhìn nhãn**, ví dụ cắt các đoạn cuối theo thứ tự đã khóa và dành đủ vùng cho `Q+Y`; V1/R4 có thể xem đầy đủ chunks qua side-channel. Đây là phép thử lợi thế **kiến trúc/context capacity**; **không** kết luận mức thông tin đầu vào ngang bằng.
- Nếu `Q+Y>T_max` dù không có D, mẫu không hợp lệ để chấm bằng checkpoint, cần loại theo quy tắc định trước, không ngầm bỏ mẫu có kết quả xấu.
- `S_SHORT` và `S_LONG` phải định tuyến bằng độ dài và manifest **trước khi có kết quả**; không di chuyển mẫu theo dự đoán đúng/sai. Báo cáo riêng; primary inferential comparison đề xuất `S_SHORT`; `S_LONG` là mục tiêu phụ riêng.
- Kích thước embedding (ví dụ 768 chiều) và số token không phải các đơn vị thông tin tương đương. Ngoài token văn bản cần báo cáo `m`, byte/chunk, token gửi Google, token TTM, training FLOPs, GPU memory, latency và chi phí.

## 6. Answer-only NLL: định nghĩa phép chấm để tái lập

**Quy tắc chấm bắt buộc trong thiết kế (chưa chạy):**
- Mỗi mẫu có câu hỏi `q_i`, evidence `e_i` được khóa, chuỗi đáp án chuẩn `y_i` **được token hóa bằng đúng tokenizer TTM**, bất biến giữa R3/R4/V1; luật thêm EOS và separator phải được khóa.
- Với R3: prompt `P_i^text = format(q_i, source_text(e_i))`. Với V1/R4: prompt `P_i^side = format(q_i)`, evidence được cung cấp qua side-channel tương ứng. Định nghĩa khuôn cố định riêng cho từng đường; chỉ khác đường conditioning.
- Cho `y_1,…,y_n`, tính log-prob bằng teacher forcing **đúng vị trí shift**: token đích `y_t` được dự đoán từ `P + y_{<t}`; không tính loss trên `P`, không chấm riêng các token mà phương án nào được thấy trước qua mặt nạ sai.
- `NLL_i = -(1/n_i) * sum_{t=1..n_i} log p(y_t | P_i, y_{<t}, evidence_i)`. Báo cáo cả total NLL và token count `n_i`. Chỉ báo cáo trung bình **theo mẫu** rồi bootstrap theo **nhóm tài liệu/nguồn** để không coi các token hoặc paraphrase cùng nguồn là mẫu độc lập.
- `Delta_SYS_i = NLL_i(R3)-NLL_i(V1)`; `Delta_REPR_i = NLL_i(R4)-NLL_i(V1)`. Dương thuận cho V1. Bootstrap paired trên cùng `group_id`, khóa CI/threshold trước D3; báo cáo phân tầng S_SHORT/S_LONG.
- Không so PPL trên hai tokenizer khác nhau (tất cả dùng tokenizer TTM cho answer); không lấy **prompt loss** hay retrieval metric làm thay thế cho answer-only NLL.
- Nếu prompt dài khiến **một phần answer không được chấm** dưới giới hạn context, dùng quy tắc cửa sổ/position được tiền đăng ký hoặc đánh dấu không hợp lệ; tuyệt đối không bỏ token khó để làm đẹp số.
- Thước đo tác vụ bổ sung: Exact Match / forced-choice accuracy / factual groundedness theo rubric cố định; NLL thấp hơn **không tự bảo đảm** đáp án thực tế tốt hơn. Quy tắc FAIL/PASS khoa học phụ thuộc tiêu chí đã khóa trước.

## 7. Hợp đồng chống rò rỉ thông tin (Leakage Prevention)

1. **Phân nhóm:** TRAIN/VAL/TEST được tách ở mức nguồn/tài liệu/biến thể gần trùng, không chỉ ở mức các cửa sổ token; pin group-ID, exact SHA và near-duplicate rule. Không sử dụng TEST để fit chunking, thresholds, embeddings selector, adapter, prompt, hyperparameters hoặc chọn tài liệu gold.
2. **Bằng chứng hợp lệ:** tài liệu gốc có thể chứa câu trả lời của tác vụ hỏi đáp — đó là **bằng chứng**, không phải rò rỉ nếu hai nhánh nhận cùng nguồn hợp lệ. Bị cấm là dùng answer annotations/target suffix chưa được phép trong embedding query, metadata, retrieved index, or training features.
3. **Nhân quả theo token:** vector và doc IDs chỉ được tạo từ thông tin có sẵn trước thời điểm dự đoán; không tính embeddings trên toàn chuỗi `prompt + target` rồi đưa lại cho GPT. Self-attn giữ causal mask; cross-attn có evidence-valid mask và không chứa thông tin tương lai bị cấm.
4. **Mã hóa corpus:** cùng `chunk_ids`, `document_hashes`, `index_snapshot_hash`, `retrieval_policy_hash` cho R3/R4/V1; khóa cutoffs, top-k, rerank, order và duplicate handling trước đánh giá.
5. **Negative controls:** shuffling vector trong cùng split/nhóm loại độ dài; random vectors chuẩn hóa tương đương; mismatched doc IDs phải được ghi nhận, không cho huấn luyện nhầm nhãn; kiểm `gate=0` parity và empty-document behavior.
6. **Blind TEST:** nguồn/test labels được giữ kín với huấn luyện và lựa chọn cấu hình; chỉ mở theo cổng khoa học riêng sau khi chọn cấu hình từ TRAIN/VAL. Không dùng `R_gold` trên TEST như một lối tắt để tune.
7. **Data-sharing:** không gửi dữ liệu có PII, dữ liệu nội bộ hoặc corpus không có quyền chia sẻ lên Gemini Free Tier. Cần xét khả năng dùng dữ liệu để cải thiện sản phẩm và quyền lưu/tái sử dụng embedding. Không ghi secrets hoặc vectors nhạy cảm trên GitHub.

## 8. Tính khả thi Adapter / tensor contract (thiết kế đề xuất)

- Backbone ứng viên từ TTM-Small: `vocab_size=2048, context=256, d_model=256, layers=4, n_head=4`; **mới là ứng viên**, không giả định có checkpoint T4 đã học/được chấp nhận.
- `tokens:[B,T]` int64; `target_tokens:[B,A]`; `evidence_vectors:[B,m,768]` float32 (ứng viên); `evidence_valid_mask:[B,m]` bool; `doc_ids:[B,m]` xác định nguồn; `hidden:[B,T,256]`; `logits:[B,T,2048]`.
- Adapter ứng viên có `projection(768→256)`, normalization, attention with `Q=hidden`, `K,V=projected_evidence`, output residual gate; một vị trí chèn vào decoder phải được quyết định sau static feasibility, trước prereg. Các module Cross-Attention trong R4/V1 phải có **cùng cấu trúc và tham số tương đương**.
- `gate=0` phải tái hiện logits frozen GPT trong ngưỡng số học đã đăng ký; `m=0` không NaN, `m=1` không ngụy nhận selection, `m>1` valid-mask độc lập; gradient không đổi backbone; capacity và cost được đo đúng.
- `R4` dùng frozen text representation rồi fixed bridge để đạt shape như V1; không tráo bộ mã hóa text có khả năng nhìn target hoặc train trên TEST.
- Colab/Drive resume phải lưu adapter optimizer/scheduler/sampler/RNG, cache references có hash và READY-last; thí nghiệm mới phải có ngân sách one-shot/QA độc lập riêng. Không mượn quyền của TTM T4.
- GGUF exporter T2 của GPT2-like chỉ chứng minh baseline; **chưa hỗ trợ Cross-Attention được xác nhận**. Không đổi mã T2/T5 hay nói Ollama phục vụ được V1 nếu chưa có successor runtime.
- GQA/PagedAttention không thuộc phép thử E_SYS/E_REPR. P07 vẫn `PAUSED_PRESERVE`, không mở P08.

## 9. Free Tier: giá trị và giới hạn phương án $0

- `MODEL_ID=gemini-embedding-2`; `API_PLAN=STANDARD_FREE_TIER_FIRST`; `TARGET_GEMINI_API_SPEND_USD=0`; `PAID_FALLBACK=FORBIDDEN`; `BATCH_PAID=FORBIDDEN`.
- Chưa kiểm tra dự án Google AI Studio cụ thể đang được cấp quota/free-tier hay không. Trước khi gọi API trong một nhiệm vụ được cho phép sau này: xác minh model access, quota hiện hành, tài khoản billing, quyền corpus và chính sách dữ liệu, khả năng lưu vector, request/token budget và giới hạn dừng.
- Nếu không xác minh được Free Tier cho dự án hoặc nhận quota exceeded: `HOLD_NO_API_CALL` / `FREE_QUOTA_BLOCKED`, không tự kích hoạt thanh toán/chuyển project/key/model. Free Tier không có nghĩa vô hạn.
- **$0 chỉ là mục tiêu chi phí Gemini API**, không khẳng định miễn phí Colab, GPU, lưu trữ, điện và mọi dịch vụ khác.
- Chi tiết giá tham khảo và cảnh báo chính sách nằm trong tài liệu đính chính đã ghim: `TTM_EMBEDDING2_FREE_TIER_DESIGN_CORRECTION_20261108.md`; nguồn Google: https://ai.google.dev/gemini-api/docs/pricing và https://ai.google.dev/gemini-api/docs/rate-limits. Không đặt hạn mức cố định khi chưa có bằng chứng từ project.

## 10. Điều kiện chấp nhận A1 ở vòng review kế tiếp

| Mã | Điều kiện review (chỉ thiết kế) | Trạng thái A1 |
|---|---|---|
| A1-01 | Phân biệt E_SYS và E_REPR; không quy kết V1 hơn R3 là do Gemini thuần túy | **DOCUMENTED — REVIEW_PENDING** |
| A1-02 | R4 có học, gần ngang năng lực tham số/steps với V1; có kiểm soát điểm yếu encoder text | **DOCUMENTED — REVIEW_PENDING** |
| A1-03 | R_gold chỉ làm positive control năng lực checkpoint, không dùng TEST để tuning | **DOCUMENTED — REVIEW_PENDING** |
| A1-04 | S_SHORT và S_LONG được chia theo token TTM trước khi biết kết quả | **DOCUMENTED — REVIEW_PENDING** |
| A1-05 | Answer-only NLL teacher-forced, đúng shift, cùng answer IDs, paired groups | **DOCUMENTED — REVIEW_PENDING** |
| A1-06 | Dữ liệu/query/index/adapter không nhìn nhãn hoặc tương lai | **DOCUMENTED — REVIEW_PENDING** |
| A1-07 | Free Tier $0, không tự Paid, quyền dữ liệu/quotas còn HOLD | **DOCUMENTED — REVIEW_PENDING** |
| A1-08 | GQA/Paged độc lập, checkpoint/phase TTM không đổi | **DOCUMENTED — REVIEW_PENDING** |

### Các cổng còn HOLD dù review A1 đạt

`T4_SCIENCE_CHECKPOINT=NOT_VERIFIED_FOR_THIS_STUDY`; `QA_MINIMUM_COMPETENCE=NOT_EXECUTED`; `CORPUS_RIGHTS=HOLD`; `GEMINI_PROJECT_FREE_TIER_QUOTA=NOT_VERIFIED`; `ADAPTER_CONFIG_AND_TRAIN_BUDGET=NOT_PREREG_LOCKED`; `TEST_SEALED_FOR_NEW_STUDY=NOT_ESTABLISHED`; `D1/D2/D3/D4=NOT_AUTHORIZED`.

**Quyết định đề nghị:** `KEEP_WITH_REVIEW_REQUIRED`. Không gọi việc viết phụ lục là đã vượt cổng khoa học; chưa có thử nghiệm hoặc dữ liệu kết quả nào.

**Bước thực hiện tiếp theo:** `TTM_EMBEDDING2_A1_INDEPENDENT_PROTOCOL_READONLY_REVIEW` — thẩm định riêng A1 đối chiếu trực tiếp văn bản với mã nguồn TTM và hai biên bản gốc, tập trung fairness R4/V1, giới hạn S_SHORT, correctness Answer-only NLL, leakage và điều kiện Free Tier. Chỉ khi design review đạt mới cân nhắc một quyết định admission D1 **riêng** sau checkpoint T4 có năng lực và quyền API/dữ liệu. Tuyến ưu tiên TTM chính vẫn là T4 science-lock; **không** huấn luyện/gọi Gemini API trong bước này.
