# TTM — Đánh giá khả thi Gemini Embedding 2 + GQA + PagedAttention

**Mã công việc:** `TTM_GEMINI_EMBEDDING2_GQA_PAGEDATTENTION_FEASIBILITY_DESIGN`  
**Ngày:** 2026-11-08  
**Trạng thái:** `DESIGN_ONLY / FEASIBILITY_REVIEW / SCIENCE_NOT_AUTHORIZED`  
**Repository:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh riêng:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`  
**Base exact `main` đã đọc:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`  
**Quan hệ với công việc hiện hữu:** PR #12 (`research/ttm-small-4m-colab-pilot-prereg-20261108`) tiếp tục độc lập; không đưa thay đổi của nhánh này vào pilot T1–T7.

> **Ranh giới công việc:** Chỉ lập tài liệu đánh giá khả thi. Không sửa mã nguồn hoặc kiến trúc TTM hiện tại; không tạo checkpoint, không gọi Gemini API, không tải dữ liệu, không chạy huấn luyện/kiểm định khoa học, không thay đổi P00–P12, không mở P07/P08/P09/P10/P11, không hợp nhất nhánh, không chạm `lineage.md`, không truy cập hoặc dọn worktree Windows. Mọi PASS kỹ thuật của T1–T3 không được tái diễn giải thành kết quả khoa học T4.

## 1. Câu hỏi khoa học và giới hạn khẳng định

**Câu hỏi khoa học ưu tiên:** Với cùng một checkpoint GPT nhỏ đã khóa, cùng nguồn bằng chứng được phép và ngân sách thông tin đầu vào được định nghĩa công bằng, phương án cung cấp các vector do **Gemini Embedding 2** tạo ra qua bộ chuyển đổi có thể học (Adapter) và chú ý chéo (Cross-Attention) có giảm sai số dự đoán/cải thiện độ đúng tác vụ so với cung cấp **văn bản bằng chứng truy xuất trực tiếp** vào prompt hay không?

- **H0 (giả thuyết không):** Cấu hình vector + Adapter/Cross-Attention không cải thiện hiệu năng có ý nghĩa so với đối chứng văn bản trên cùng bộ câu hỏi/bằng chứng được kiểm soát.
- **H1 (giả thuyết thay thế):** Cấu hình vector + Adapter/Cross-Attention cải thiện kết quả trên tập giữ riêng vượt ngưỡng giá trị thực tiễn `delta_min` được khóa trước chạy khoa học, đồng thời không vượt chi phí/tài nguyên cho phép.
- **Định nghĩa chênh lệch ưu tiên (đề xuất, chưa khóa):** `delta_NLL = mean(answer_token_NLL_Text) - mean(answer_token_NLL_Vector)`. Dương nghĩa là phương án vector có NLL thấp hơn; tính theo mẫu/tài liệu, không xem token cùng một mẫu là các quan sát độc lập.
- **Chỉ số thứ cấp:** độ chính xác câu trả lời (Exact Match), độ chính xác theo loại câu hỏi, lỗi bịa dữ kiện, số token, thời gian xử lý lần đầu/tiếp theo, dung lượng bộ nhớ, thời gian tạo embedding và chi phí API.
- **Điều kiện khoa học:** Phải có độ bất định (ví dụ, bootstrap theo tài liệu/nhóm tình huống), phân tách TRAIN/VAL/TEST và quy tắc sử dụng TEST một lần. `delta_min`, ngưỡng thống kê, số seed, ngân sách huấn luyện, kích thước mẫu và bộ chấm phải được tiền đăng ký trước mọi chạy khoa học. Không tự gán PASS từ bản thiết kế này.

**Hai câu hỏi phụ tách biệt**, tuyệt đối không nhập vào H1:
1. GQA thay MHA có cải thiện hiệu quả KV Cache/độ trễ ở cùng ràng buộc chất lượng hay không?
2. PagedAttention/Paged KV thay Dense KV có duy trì tương đương số học và cải thiện cấp phát/batching trong workload xác định hay không?

## 2. Bằng chứng hiện hành và điều kiện mở nghiên cứu

- Lộ trình `docs/PHASE_PLAN.md` có P00–P12 và phụ lục ADR-0001 ngày 08/11/2026: ưu tiên **train-first** rồi mới quay lại P07/P08.
- Thí điểm ứng viên TTM-Small khoảng 3.749.376 tham số: vocab 2048, context 256, 4 layers, `d_model=256`, 4 attention heads, learned positional embedding, LayerNorm và weight tying. Đây là cấu hình thiết kế của PR #12, **không phải mô hình đã huấn luyện thành công**.
- Theo hồ sơ PR #12 đọc ngày 08/11: T1 PASS giới hạn trong tập pilot, T2 GGUF F32/llama.cpp PASS kỹ thuật, T3 Colab Tesla T4/Drive synthetic resume PASS độc lập; lượt T3 lỗi RNG đầu tiên vẫn bảo toàn; F16 BLOCKED tùy chọn; **T4 science LOCK=HOLD, NOT_EXECUTED**. Không dùng model untrained như baseline năng lực câu hỏi/đáp.
- **Điều kiện bắt đầu định lượng:** T4 đã có checkpoint thực tế và phán quyết khoa học; T5 đối chiếu checkpoint đã train và T6 baseline/đo suy luận đạt điều kiện riêng; benchmark truy xuất có tác vụ mà mô hình nền có thể thực hiện ở mức tối thiểu. Nếu mô hình 4M/context 256 không đáp ứng năng lực đọc bằng chứng, dừng ở `MODEL_CAPABILITY_GAP` thay vì ngụy kết luận vector/Cross-Attention thất bại.
- Việc mở nhánh **không cấp quyền** huấn luyện bổ sung, truy cập API trả phí hoặc đọc dữ liệu từ T1 ngoài hợp đồng cũ. Tuyến nghiên cứu nối tiếp cần prereg độc lập.

## 3. Phạm vi kỹ thuật Gemini Embedding 2

- Model ID công khai: `gemini-embedding-2` (không nhầm `gemini-embedding-001` hoặc `gemini-embedding-2-preview`). Hỗ trợ vector embedding kích thước 128–3072, đề xuất chính thức 768/1536/3072, đầu vào văn bản, hình ảnh, âm thanh, video và PDF; giới hạn text 8192 token theo thông tin nhà cung cấp. **Pha đầu chỉ dùng văn bản**, không mở đa phương thức.
- API trả vector biểu diễn **nội dung yêu cầu**, không cam kết trả chuỗi token-level hidden states để thay token embedding của GPT. Mỗi đoạn bằng chứng cần embedding riêng; không đưa nhiều phần vào cùng một `contents` rồi tưởng nhận nhiều vector, do cơ chế tổng hợp có thể cho một vector.
- Với `gemini-embedding-2`, văn bản có thể dùng chỉ dẫn tác vụ trong chuỗi nhập, **không dùng `task_type` như `gemini-embedding-001`**. Khóa rõ template query/document, số chiều, chế độ chuẩn hóa, số đoạn, chunker và truy xuất.
- Embedding 2 tự chuẩn hóa vector sau khi cắt bớt số chiều theo tài liệu Google; ghi và kiểm tra chuẩn số trong tiền kiểm, không giả định khác phiên bản là tương đương.
- **Không thể pin chắc chắn trọng số dịch vụ như model local:** log model ID, thời điểm, API/SDK version, tham số, request fingerprint và hash vector phản hồi; lưu cache embedding có điều kiện theo quyền/điều khoản. Nếu nhà cung cấp thay đổi mô hình hoặc không tái lập được các vector đã khóa, kết luận có giới hạn hoặc dừng.
- Chưa phê duyệt lưu/chia sẻ vector hoặc chuyển nội dung tài liệu sang Google. Trước API call phải xác minh điều khoản, quyền dữ liệu, PII, ngân sách/giá/giới hạn, cơ chế retry/rate-limit và đường lưu an toàn. Không commit API key hay dữ liệu riêng tư lên GitHub.

**Nguồn kỹ thuật (được tra cứu 08/11/2026):**
- https://ai.google.dev/gemini-api/docs/models/gemini-embedding-2
- https://ai.google.dev/gemini-api/docs/embeddings
- https://developers.googleblog.com/en/building-with-gemini-embedding-2/
- https://ai.google.dev/gemini-api/docs/pricing
- TTM: `docs/ARCHITECTURE.md`, `docs/PHASE_PLAN.md`, `docs/GOVERNANCE.md`, `docs/COMPARISON_PROTOCOL.md`, `docs/decisions/ADR-0001_TRAIN_FIRST_COLAB_AND_BRANCH_CLEANUP_20261108.md`.
- Pilot độc lập PR #12: `docs/pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md`.

## 4. Kiến trúc đề xuất và hợp đồng I/O (chưa implement)

### A — Truy xuất ngoài (RAG; không đổi trọng số GPT)
```text
query --(embedding query)--> cosine similarity --> evidence IDs (top-k)
corpus chunks --(embedding each chunk)----------------------^
evidence IDs --> fetch ORIGINAL TEXT --> truncate under TTM prompt budget
TTM tokenizer --> frozen GPT checkpoint --> answer / answer-token NLL
```
- Nguồn sự thật cho đáp án phải nằm trong **đoạn văn bản bằng chứng gốc**, không nằm trong vector nhúng.
- Corpus có manifest SHA, loại câu hỏi, factual answer, nguồn/chủ quyền; tách tài liệu/nhóm tình huống giữa TRAIN, VAL, TEST để chặn leakage.
- Retrieval lựa chọn thông tin có thể được kiểm tra trước, nhưng kiểm tra năng lực trả lời yêu cầu checkpoint T4 thực tế.
- Lộ trình QA kỹ thuật zero-science có thể dùng fixture tổng hợp không nhạy cảm, nhưng không được diễn giải thành hiệu quả khoa học.

### B — Vector Adapter + Cross-Attention (thay đổi kiến trúc trong mô hình kế thừa)
```text
Documents -> Gemini Embedding 2 -> E: [B, m, d_e]       (e.g. d_e=768)
E -> trainable projection/normalization -> Z: [B, m, d_model=256]
Input token IDs -> frozen TTM GPT -> H: [B, T, d_model=256]
Cross-Attention: Q=H Wq, K=Z Wk, V=Z Wv
cross_output -> gated residual fusion -> hidden state -> LM head
```
- `m` là số **embedding độc lập của các đoạn** bằng chứng, không phải số token Google. `m=1` khiến softmax Cross-Attention chỉ có một khóa, không thể học lựa chọn tài liệu trong head đó; ghi nhận điều này khi thiết kế.
- Tensor contract dự kiến: `token_ids: int64[B,T]`; `attention_mask/causal_mask` riêng của GPT; `evidence_vectors: fp32[B,m,d_e]`; `evidence_valid_mask: bool[B,m]`; `doc_ids` có mapping về nguồn gốc; output `logits: [B,T,vocab]`.
- Query của GPT được mask nhân quả; evidence vectors được tạo chỉ từ **nguồn độc lập đã có trước thời điểm câu trả lời**, không từ full target answer hoặc đoạn tương lai của chuỗi đang dự đoán. Truy xuất từ chính đoạn văn bản chứa nhãn/đáp án cần bị chặn hoặc được định nghĩa rõ là điều kiện có bằng chứng hợp lệ.
- Adapter chính: tuyến tính/MLP nhỏ, normalization, residual gate. Khởi tạo gate nhỏ hoặc zero để bảo toàn hành vi nền ở bước đầu; kiểm tra parity `gate=0` với frozen baseline. Chi tiết số lớp/hàm kích hoạt và vị trí fusion phải được khóa sau design review.
- **Training primary:** freeze toàn bộ GPT checkpoint T4; chỉ huấn luyện Adapter + Cross-Attention + gate trên TRAIN, không cho phép update embedding API; VALID để chọn mô hình. Cấu hình fine-tune GPT toàn phần là nghiên cứu riêng, không là đối chứng cùng checkpoint.
- Cần kiểm soát chênh lệch capacity: báo cáo số tham số bổ sung; đối chứng trainable adapter với vector ngẫu nhiên/tráo; đối chứng cùng-capacity nếu đánh giá tác dụng biểu diễn riêng. Không gọi mọi lợi ích của model mới là do Gemini embedding.

### C — GQA (thí nghiệm kiến trúc riêng, không dùng làm bằng chứng H1)
- TTM-Small có `n_head=4`; ứng viên GQA `n_query_heads=4`, `n_kv_heads=2`, head dim 64. Đây là ví dụ, **không thay checkpoint TTM ngay**.
- Thay MHA thành GQA thay tensor K/V và số tham số; không được bật/tắt bằng một flag trên cùng checkpoint mà tự nhận so sánh công bằng. Muốn định lượng: (i) chuyển đổi uptraining có tiêu chí hợp lệ hoặc (ii) huấn luyện hai phiên bản ngân sách ngang nhau. Giữ đối chứng riêng và ghi sai số chất lượng.
- Đo footprint KV cache, TPOT, throughput, peak VRAM, không suy luận tốc độ từ giảm head count; với 4M/context 256 hiệu ứng có thể quá nhỏ.

### D — PagedAttention (thí nghiệm serving/inference riêng)
- Paged KV / PagedAttention quản lý lưu trữ và truy cập cache, không thay biểu diễn ngữ nghĩa hoặc logic Cross-Attention. TTM P00 đường phân trang CPU hiện gom K/V trước tính toán, P07 GPU trực tiếp vẫn PAUSED; không giả định đã có kernel GPU đạt tăng tốc.
- Đối chứng `no-cache` / `dense KV` / `paged KV` trên **cùng checkpoint, token IDs, dtype, hardware, concurrency, prompt/decoding policy**. Phép đo bắt buộc: logits parity, TTFT, TPOT, throughput, peak RSS/VRAM, fragmentation, OOM và request isolation.
- GQA và PagedAttention chỉ được ghép thành cấu hình kết hợp sau khi từng thành phần vượt kiểm tra độc lập.

## 5. Ma trận đối chứng độc lập (A/B)

| ID | Embedding/truy xuất | GPT và Attention | Bộ nhớ suy luận | Huấn luyện mới | Trả lời câu hỏi gì? |
|---|---|---|---|---|---|
| R0 | Không truy xuất | TTM checkpoint, MHA | Dense | Không | Mức năng lực nền |
| R1 | Truy xuất lexical/BM25; đưa văn bản gốc | Cùng checkpoint MHA | Dense | Không | Giá trị của bằng chứng truy xuất đơn giản |
| R2 | Gemini Embedding 2 retrieval; đưa **cùng văn bản gốc** | Cùng checkpoint MHA | Dense | Không | Gemini có chọn evidence tốt hơn lexical không? |
| R3 | Evidence IDs **cố định giống R2**; đưa văn bản gốc | Cùng checkpoint MHA | Dense | Không | Đối chứng văn bản chính cho H1 |
| V1 | **Cùng evidence IDs R3**; đưa vector riêng từng chunk | Frozen GPT + trainable Adapter/Cross-Attention | Dense | Chỉ adapter/cross-attn | Giá trị của biểu diễn vector + fusion so với R3 |
| V2 | Vector tráo giữa mẫu/đối chứng ngẫu nhiên | Cùng capacity và train protocol V1 | Dense | Chỉ adapter/cross-attn | Kiểm tra phụ thuộc thông tin đúng |
| V3 | Vector Gemini, nhưng adapter linear/non-attention cùng ngân sách tham số | Frozen GPT + adapter đơn giản | Dense | Adapter | Cross-Attention hơn phép chiếu đơn giản không? |
| I1 | Truy xuất cố định như R3 | MHA baseline | Paged KV | Không | Tối ưu cache có parity/throughput không? |
| I2 | Truy xuất cố định như R3 | GQA candidate đã được train/convert hợp lệ | Dense rồi Paged | Có thể cần training khác | GQA có tradeoff đáng giá không? |

R0/R1/R2 chỉ kiểm tra **retrieval/generation**; R3/V1/V2/V3 là bộ so sánh **semantic fusion**; I1/I2 là bộ đo **hiệu suất inference**. Không lấy thắng lợi của một nhóm để kết luận cho nhóm khác.

## 6. Ngân sách thông tin công bằng — tránh ngộ nhận

**Không thể ép vector 768 chiều bằng đúng số token GPT** rồi coi hai đường có cùng lượng thông tin. Số chiều vector, byte tải và token ngữ cảnh là đại lượng khác nhau.

Để tạo đối chứng khả diễn giải, phải khóa và báo cáo đồng thời:
1. **Same evidence provenance:** cùng danh sách `doc_ids` và cùng các chunk nguồn, thứ tự, thời điểm truy xuất cho R3 và V1 (không để retrieval khác làm nhiễu kết quả fusion).
2. **Same source-text budget:** chunking/chiều dài/giới hạn thông tin nguồn trước embedding giống nhau; đo token Google và TTM riêng. Không so sánh trực tiếp 768 vector dims với 768 tokens.
3. **Context budget declared:** đường text có cửa sổ GPT `T<=256` (bao gồm câu hỏi, bằng chứng, phần sinh); đường vector đưa bằng chứng qua cross-attention có **side channel** ngoài cửa sổ GPT. Báo cáo đây là lợi thế kiến trúc/capacity có thể có, không gọi là đồng nhất ngân sách.
4. **Compute/cost accounting:** vector generation/indexing/lookup, trainable params, training FLOPs/budget, token context, inference latency, VRAM, chi phí API, cache và yêu cầu ngoại tuyến phải được ghi riêng. So sánh `quality` và `quality per cost` là hai kết luận khác nhau.
5. **Leakage control:** Embedding query từ câu hỏi hợp lệ; document embedding không chứa nhãn/đáp án do người chấm tạo sau truy xuất; các bản khác nhau của cùng tài liệu không phân tán giữa TRAIN/VAL/TEST. Không dùng TEST để chọn `k`, thresholds, prompt hay adapter.
6. **Cross-condition answer target:** Cùng đáp án chuẩn, tokenizer, scoring suffix/answer tokens và chính sách decode; kiểm tra việc thay prompt có làm thay đổi số token chấm hay không.

Nếu không đạt những điều kiện này, kết quả phải ghi `INCONCLUSIVE_UNFAIR_COMPARISON`, không là H1 PASS/FAIL.

## 7. Tiêu chí chấp nhận và loại bỏ (sẽ khóa trước science)

**Tiền kiểm (technical preflight):**
- Mã nguồn/checkpoint/tokenizer và sha/revision của corpus có provenance rõ; không sử dụng checkpoint T4 chưa tồn tại.
- Mặt nạ nhân quả và không rò rỉ TEST; `gate=0` parity với GPT nền trên cùng prompt; vector shape/device/dtype, NaN/Inf, mask padding/empty-evidence, test nguồn sai/tráo nhãn đều được kiểm tra.
- Vector/cache có checksum và metadata; một đoạn một vector, không trộn phiên bản embedding; API quota/cost/terms được duyệt.
- Adapter training có resume state và log; no partial READY checkpoint. Tránh đổi số hạt giống/kích thước sau xem TEST.

**Kết luận science (chưa phải ngưỡng đã khóa):**
- `EXPERIMENT_PASS` chỉ khi V1 vượt R3 trên primary metric, vượt `delta_min`, độ bất định đủ mạnh theo chuẩn khóa trước, và vượt các negative/capacity controls phù hợp; không vượt chi phí trần.
- `EXPERIMENT_FAIL` khi đủ phép đo nhưng không đạt tiêu chí đã khóa; không chỉnh hậu nghiệm để đổi kết luận.
- `INCONCLUSIVE` khi năng lực GPT nền, retrieval fidelity, nguồn/quyền, ngân sách tương đương, chi phí hoặc công suất Colab không đáp ứng.
- Nếu V1 không vượt R3 nhưng V1 vượt R0, chỉ kết luận **có ích so với không có bằng chứng**, chưa chứng minh lợi ích riêng của Cross-Attention so với text RAG.
- Không khẳng định cải tiến TTM kiến trúc nói chung nếu chỉ đạt trên tập fixture nhỏ một seed.

## 8. Kế hoạch hữu hạn và quyết định đi tiếp

| Gate | Thời điểm/điều kiện | Đầu ra | Trạng thái |
|---|---|---|---|
| D0 — Architecture feasibility | Ngay bây giờ; tài liệu riêng | Câu hỏi, tensor contract, đối chứng, hạn chế API, ranh giới phase | `DESIGN_ONLY` |
| D1 — External retrieval sanity | Sau khi T4 có checkpoint đủ năng lực và T5/T6 baseline rõ | Chọn benchmark, lexical vs Gemini retrieval trên văn bản gốc; log cost/no-leakage | `NOT_AUTHORIZED` |
| D2 — Adapter preregistration | Chỉ khi D1 cho kết quả diễn giải được | Freeze GPT, thiết kế adapter/cross-attn và negative controls, seed/budget/thresholds | `NOT_OPENED` |
| D3 — One-shot research | Sau prereg/rights/capacity độc lập PASS | R3 vs V1/V2/V3; giữ mọi PASS/FAIL | `NOT_AUTHORIZED` |
| D4 — Inference engineering | Chỉ sau khi giả thuyết semantic fusion được kết luận; hoặc theo kế hoạch P05–P08 độc lập | GQA vs MHA và Dense vs Paged KV; numerical parity/benchmark | `NOT_OPENED` |

**Ranh giới đặc biệt:** Việc ghi D0 không có nghĩa D1–D4 được mở. Không gộp kịch bản GQA/Paged với H1 ở đợt one-shot đầu. Nếu phải đổi lõi P02 hoặc backend GGUF để chạy Cross-Attention, làm trên nhánh successor/kiến trúc riêng sau quyết định, không sửa chứng cứ checkpoint/base hiện tại. Mô hình dùng Cross-Attention **chưa có cam kết hỗ trợ** trên llama.cpp/Ollama chỉ nhờ exporter GPT-2 F32.

## 9. Quy trình quản trị và bàn giao

- Mọi chỉnh sửa thiết kế tạo commit mới trên nhánh này; không merge vào `main` khi chưa review độc lập phạm vi thiết kế. GitHub PR riêng nếu chủ dự án yêu cầu; tuyệt đối không can thiệp PR #12.
- `lineage.md` **append-only cho kết quả/phán quyết khoa học thật**, không ghi nhận thiết kế, QA công cụ, lỗi infrastructure. Không sửa lịch sử PASS/FAIL.
- Không tạo worktree ngoài `D:\WORK\RESEARCH\TokenToModel-Lab`; không dọn nhánh/worktree khi chưa có quyết định riêng, không force push.
- Không tạo hoặc dùng API key; nếu cần API ở successor phải được cấp quyền/chi phí riêng, không đưa secrets vào commit.
- Review độc lập tối thiểu: nguồn Google/version; TTM baseline exact SHA; rò rỉ thông tin; fairness của so sánh; tensor-level causal masking; correctness của so sánh GQA/Paged; rủi ro tương thích xuất GGUF.
- **Trạng thái kết thúc bước này (dự kiến sau commit/readback):** `BRANCH_CREATED`, `ARCHITECTURE_DESIGN_WRITTEN`, `SCIENCE_NOT_EXECUTED`, `MAIN_UNCHANGED`, `PR12_UNCHANGED`; báo cáo chỉ khi có xác minh GitHub thật.

**Bước thực hiện tiếp theo:** `TTM_EMBEDDING2_FEASIBILITY_INDEPENDENT_DESIGN_REVIEW` — thẩm định độc lập tài liệu thiết kế (chỉ đọc), xử lý các điểm chưa khóa về mô hình nền, mức so sánh công bằng, benchmark, nguồn/quyền và API; không chạy retrieval/adapter/training hoặc mở science. Trong khi đó, tuyến ưu tiên thực thi chính vẫn là TTM-Small T4 science-lock/one-shot theo quản trị đã duyệt.
