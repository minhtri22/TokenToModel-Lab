# TTM — Bảng tổng quan các nhánh nghiên cứu (Research Portfolio Status)

**Ngày chốt snapshot:** 2026-11-11. **Nguồn:** GitHub `minhtri22/TokenToModel-Lab`, nhánh `research/ttm-t5-ollama-full-logits-20261111`. **Trạng thái tài liệu:** `PORTFOLIO_STATUS_UPDATED_SNAPSHOT` — tổng hợp kết quả đã có, **không** phải thử nghiệm, tiền đăng ký hay phê duyệt nghiên cứu mới.

**Khóa kiểm kê:** `main` tại `5d52e32f20021e36f08f284ef9864d3ba36dbead`; nhánh Ollama full logits đã đóng tại commit khoa học `bef5a4dcb3f2930dea1ed5f0e2ad50bba8ac5e12`. Báo cáo này nằm **trên nhánh nghiên cứu chưa hợp nhất**, không làm kết quả dưới đây xuất hiện trên `main`. Trạng thái của các nhánh khác được dẫn từ **tài liệu gốc của chính nhánh đó**, không suy diễn rằng chúng đã merge hoặc tất cả đã có QA đồng mức.

## 1. Kết quả khoa học và kỹ thuật TTM đang có

| Hướng / nhánh nguồn | Trạng thái được phép ghi | Bằng chứng cụ thể | Giới hạn bắt buộc |
|---|---|---|---|
| TTM-Small-4M T4 — huấn luyện và VAL, dòng chính | `PASS_H1_CONFIRMATORY_VAL_SCOPE` | `lineage.md` L0011 trên `main`; step 1.024, NLL VAL model 3.5223388517 vs bigram 3.9972314170 | Một seed, điều kiện pilot; không suy ra chất lượng sử dụng |
| TTM-Small-4M T4 — TEST niêm phong, dòng chính | `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED` | `lineage.md` L0012; 64 truyện TEST, NLL 3.48359107334 vs bigram 3.97360374532 | TEST đã tiêu thụ một lần, không đánh giá/tune lại |
| T5 — strict logits F32, **lịch sử âm tính** | `FAIL_7_OF_8_PRESERVED` và `FAIL_STRICT_LOGITS_32_OF_32_SCOPED_SYNTHETIC` | `lineage.md` L0013 (32/32 ở 4 cấu hình KV/Flash), báo cáo T5 frozen-32 | Không xóa/viết lại FAIL khi có phiên bản GELU_ERF cải tiến; là cấu hình/bộ fixture lịch sử khác |
| T5 — sửa đúng biến thể GELU, xác nhận native C01–C04 | `PASS_HELDOUT_STRICT_LOGITS_4_OF_4_SCOPED_GELU_ERF` | `lineage.md` L0014; 4 × 2.048 logits, `max_abs≤0.001`, Top-1 4/4 | Native llama.cpp đã sửa, CPU/KV F32/Flash OFF; không phủ định L0013 |
| T5 — nhập GGUF và sinh từ Ollama v5 | `PASS_SCOPED` — tương thích runtime | Commit `main` `5d52e32f20021e36f08f284ef9864d3ba36dbead`; v5 frozen Windows F32 | Lượt T5 v5 **không** đo full logits, không thay bằng kết quả của nhánh mới |
| **Ollama full raw logits — FL01–FL04** (`research/ttm-t5-ollama-full-logits-20261111`) | **`PASS_SCOPED_CLOSED_UNMERGED`** | Phán quyết `PASS_SCOPED_OLLAMA_CHILD_FULL_RAW_LOGITS_4_OF_4`; `lineage.md` **L0015 trên nhánh này**; 8.192/8.192 logits, Top-1 4/4, max abs **9.5367431640625e-6** so PyTorch P02, ngưỡng 0.001; rehash + so sánh độc lập | **Ollama runner tùy chỉnh**, Windows CPU, KV F32/Flash OFF, 4 prompt; không chứng minh Ollama nguyên bản, GPU, Flash ON, F16, bitwise parity phổ quát hoặc chất lượng sản phẩm |
| TTM-Small-4M — chất lượng tiếp nối FRESH12 (`research/ttm-small4m-q1q2-quality-single-batch-20261109`) | `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED` | 24 cặp, 48 output, 144 điểm từ reviewer AI; cổng ứng viên `PASS_4_FAIL_4` sau giải mù | Không có bằng chứng cải thiện chất lượng bằng xử lý dấu cách cuối; không coi là đánh giá độc lập bởi con người |
| TTM × EmbeddingGemma 2 — OOD256 WikiText-2 (`research/ttm-small4m-embeddinggemma2-ood-design-20261111`) | `PASS_SCOPED_OOD_RESIDUAL_TRANSPORT` | Phán quyết độc lập trên nhánh OOD: 3 seed × 4 arm × 256 bài, 12/12 SCORE receipts PASS; `lineage.md` **L0021 của nhánh OOD**, không phải L0021 trên main | Dấu hiệu chuyển cấu trúc residual trong **một miền OOD**, không cô lập tác động nhân quả riêng của semantic pretraining, donor overlap chưa biết |
| TTM × SIX — thí nghiệm 3 nhánh A/B/C (`research/ttm-six-functional-transfer-ttm4m-three-arm-design-20261110`) | `SOURCE_IMPLEMENTED / CPU_QA_PASS_20_OF_20 / GPU_NOT_RUN` | Runner và notebook 3-arm, 20/20 QA nguồn + synthetic CPU, chưa preflight checkpoint gốc trên Drive | Chưa có tín hiệu khoa học thật từ pilot 3 nhánh; không dùng QA CPU như kết luận DEV/TEST |
| Bộ nhớ vector ngoài (External Vector Memory; `research/ttm-vector-memory-architecture-20261111`) | `FAIL_EXPLORATORY` contextual retrieval; `NO_SCOPED_EXPLORATORY` adapter | 128 VAL targets: NLL A 3.408361, C 3.607639, đối chứng đảo giá trị D 3.586965; adapter không cải thiện NLL theo pilot | Là kết quả âm tính theo cấu hình đã thử, **không** chứng minh mọi dạng retrieval/cross-attention đều thất bại |
| P07 — GPU PagedAttention (`feature/p07-paged-attention-kernel-design-20261107`) | `PAUSED_PRESERVE` | XPU Intel Arc 140V canary tính toán thực PASS; lượt GPU one-shot tổng thể FAIL/HOLD do vượt ngân sách con 6 GiB; SYCL native page-table kernel NOT_EXECUTED | Không phải P07 numerical parity hoặc GPU speedup PASS; P08 chưa mở |

**Lưu ý quản trị:** các ký hiệu `L0015` của Ollama và `L0021` của EmbeddingGemma thuộc **lịch sử từng nhánh riêng**. Không ghép những ID này thành một dòng thời gian chung của `main`, không gán trạng thái của một nhánh cho các nhánh khác.

## 2. Kết quả âm tính phải được bảo toàn độc lập

| Kết quả âm tính | Kết luận nguyên bản cần giữ | Không được diễn giải thành |
|---|---|---|
| T5 F32 strict 8 fixture | `FAIL_7_OF_8_PRESERVED` | PASS hồi tố nhờ runner mới |
| T5 native KV/Flash 8 × 4 = 32 fixture | `FAIL_STRICT_LOGITS_32_OF_32_SCOPED_SYNTHETIC` (L0013) | Bằng chứng KV F32/Flash OFF luôn đúng trên mọi fixture |
| FRESH12 quality A/B | `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED` | Đã chứng minh tác động của prompt trimming có lợi |
| Vector memory contextual retrieval | `FAIL_EXPLORATORY` theo cấu hình C vs A/D; adapter `NO_SCOPED_EXPLORATORY` | Mọi loại memory/retrieval/attention có điều kiện đều vô ích |
| P07 enablement | `FAIL_OR_INCONCLUSIVE_NO_AUTORERUN` tổng lượt XPU do resource guard | GPU không hoạt động (XPU canary riêng vẫn PASS) |

Không chỉnh sửa biên bản gốc, không chuyển các FAIL thành `PASS` vì một phép đo mới trên đối tượng/cấu hình khác. **QA kỹ thuật, PASS khoa học và mức sẵn sàng sản phẩm là các quyết định độc lập.**

## 3. Mốc đối chứng kỹ thuật (Technical Baseline) từ Ollama full logits

**Mô hình khóa:** TTM P02 decoder-only, 3.749.376 tham số, step 1.024; checkpoint SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; GGUF F32 SHA-256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`. Mỗi vector gồm 2.048 next-token raw F32 logits trước sampling/softmax. Bộ runner tùy chỉnh có SHA-256 `818fec27008b0a8555ecbae09c8c95e6a076d2b2fa4c26377b8bdb248232210a`.

| Phép đo khóa | Giá trị thực tế |
|---|---|
| Đầu vào (fixtures) | FL01 `abc`; FL02 `hello`; FL03 `a\nb`; FL04 `Xin chào` |
| Cấu hình | Windows CPU, 1 luồng, context 256, K/V F32, Flash OFF, `raw=true` |
| So sánh | `max_abs(ollama_logits − p02_logits)≤0.001` từng fixture và Top-1 4/4 |
| Quan sát | 8.192 giá trị, 4/4 strict PASS, sai số tối đa 9.5367431640625 × 10⁻⁶ |
| Provenance | Ollama cha sinh đúng một `llama-server.exe` con; kiểm tra recorded-CIM PID/command line, log chạy và cleanup |
| Dữ liệu gốc | `_tmp/fl3/` trên máy chủ dự án, **không công khai** raw tensor/checkpoint |
| Phạm vi sử dụng | Mốc đối chứng số học và nguồn gốc **cho cấu hình trên**, không phải thang chất lượng hay benchmark hiệu năng |

**Bằng chứng bất biến của nghiên cứu này:** [đóng nghiên cứu có phạm vi](pilot/TTM_OLLAMA_FULL_LOGITS_FL01_FL04_FINAL_SCIENCE_CLOSEOUT_20261111.md) · [phán quyết JSON](../artifacts/qa/ttm-ollama-full-logits/TTM_OLLAMA_FULL_LOGITS_FL01_FL04_FINAL_SCIENCE_ADJUDICATION_20261111.json) · [L0015 trên nhánh này](../lineage.md).

## 4. Áp dụng mốc đối chứng cho hướng nghiên cứu tương lai (không tự cấp quyền chạy)

| Hướng | Mốc TTM có thể tái sử dụng | Điều kiện mới cần được chứng minh riêng |
|---|---|---|
| Attention — P05/P06/P07 | Checkpoint, token IDs, reference F32, quy trình audit raw logits | Đối chiếu cùng workload và từng đường Dense/Paged KV, kiểm soát cache và kernel, quan sát đúng attention; không dùng 4 fixture cũ như held-out độc lập |
| MoE (Mixture of Experts) | Cách khóa source, đối chứng mô hình nền và đo sai số inference | MoE thay kiến trúc/huấn luyện, cần thiết kế, ngân sách và đối chứng ngang bằng; Ollama full logits 4/4 **không** cho phép kết luận MoE tốt hơn |
| GPU, Flash, F16, SYCL | Mốc numeric CPU F32 đã khóa để xác định sai lệch trong thí nghiệm mới | Các dtype/hardware/kernel có sai số và hành vi mới: tiền đăng ký riêng, phép đo riêng, giữ P07 `PAUSED_PRESERVE` cho tới cổng gốc |
| Tối ưu suy luận (Inference Optimization) | Phương thức ghi exact binary, parent/child runtime, tensor và cấu hình | Phải đo TTFT/TPOT, thông lượng, RAM/VRAM và tính đúng với workload ngang bằng; 4/4 logits PASS không chứng minh tăng tốc |
| Chất lượng ứng dụng (Use-case Quality) | Một pipeline checkpoint → GGUF → Ollama vận hành được trong phạm vi | Cần bài toán cụ thể, kiểm định chất lượng, safety/quyền dữ liệu, chi phí và trải nghiệm; **chưa** có chứng nhận sẵn sàng thương mại |

**Cảnh báo:** việc tái dùng mốc đối chứng không phải giấy phép chạy lại four-fixture science one-shot hoặc sửa ngưỡng/nguồn. Bất kỳ mở rộng khoa học nào cần tiền đăng ký riêng, không sử dụng TEST đã tiêu thụ.

## 5. Trạng thái quản trị và phạm vi snapshot

- **Nhánh `research/ttm-t5-ollama-full-logits-20261111`: `PASS_SCOPED_CLOSED_UNMERGED`**. Đã phân xử khoa học và ghi L0015 append-only trong nhánh; chỉ bổ sung bảng tổng quan ở lượt này.
- **Main:** `5d52e32f20021e36f08f284ef9864d3ba36dbead` tại thời điểm kiểm tra; không được sửa trong lượt này.
- **Không** merge/cherry-pick/force push, xóa nhánh, thay đổi checkpoint, dữ liệu, `lineage.md`, sổ gốc, T5 v5, P00–P12, hoặc một cổng science.
- Danh mục này chọn **những hướng có bằng chứng và liên quan đến quyết định kỹ thuật**; không tuyên bố là danh sách đầy đủ tất cả Git refs và không thay thế trạng thái độc lập trong các nhánh khác.
- Do các nhánh nghiên cứu có thể có `lineage.md` khác nhau, tránh kết hợp số thứ tự science lineage giữa các nhánh khi lập báo cáo chung. 
- **Merge decision:** `HOLD_NOT_REQUESTED` — nhánh đã đóng phạm vi nghiên cứu nhưng chưa qua quyết định merge riêng; bảng này không tự quyết định hợp nhất.

**Bước thực hiện tiếp theo:** `TTM_PORTFOLIO_PRIORITY_REVIEW_NO_SCIENCE_REPLAY` — dùng danh mục để chọn **một** hướng nghiên cứu mới theo giá trị/khoảng trống chứng cứ; thiết kế hợp đồng khoa học mới trước mọi phép đo. Không chạy lại bộ 4 fixture Ollama và không mở P07/P08 chỉ từ kết quả này.

## 6. Kết quả đánh giá ưu tiên sau khi đóng Ollama Full Logits (2026-11-11)

**Operation:** `TTM_PORTFOLIO_PRIORITY_REVIEW_NO_SCIENCE_REPLAY`. Phân loại: **quyết định sắp xếp nghiên cứu chỉ dựa vào bằng chứng hiện hữu** (`DESIGN_AND_PORTFOLIO_REVIEW_ONLY`). Không chạy mô hình, không chọn checkpoint mới, không mở TEST, không thêm phán quyết khoa học hay thay đổi cổng P00–P12. `lineage.md` giữ nguyên.

### 6.1. Ma trận ưu tiên (đánh giá giá trị thông tin, không phải phép đo benchmark)

| Thứ tự | Hướng nghiên cứu | Bằng chứng hiện hữu | Khoảng trống cụ thể | Quyết định |
|---|---|---|---|---|
| **1 — ưu tiên cao nhất** | **TTM-Small-4M: chẩn đoán khả năng tiếp nối ngữ cảnh và chất lượng sinh văn bản (generation quality/continuation)** | T4 VAL NLL hơn bigram, TEST descriptive PASS; FRESH12 có **35/48** đoạn bám prompt = 0, phép thử trimmed vs baseline không chứng minh cải thiện | Chưa xác định rõ mô hình tạo truyện có mạch lạc/tuân theo ngữ cảnh đủ để phát triển tiếp hay nguyên nhân do dữ liệu, context 256, vocab BPE 2048, checkpoint hoặc đánh giá | **`NEXT_RESEARCH_DESIGN_PRIORITY`**. Thiết kế đối chứng chất lượng mới; không dùng lại 64 truyện TEST và không tái chạy FRESH12. Không train trước khi có mục tiêu và cổng mới |
| 2 | EmbeddingGemma 2 residual/semantic transfer, kiểm tra cơ chế | OOD256: `PASS_SCOPED_OOD_RESIDUAL_TRANSPORT`, 3 seed, 12 arms, hai co-primary CI dương | Chưa cô lập semantic pretraining khỏi cấu trúc hình học, hình thái token, chuẩn vector; chưa kết luận lợi ích trong sản phẩm | `SECONDARY_DESIGN_PRIORITY`; không chạy lại OOD256; nghiên cứu nhân quả khác nếu cần |
| 3 | Attention/Dense/Paged KV đúng số học, sau đó tối ưu inference | L0014 và L0015 xác nhận logits F32 phạm vi nhỏ; P07 XPU canary PASS nhưng SYCL kernel chưa chạy | Chưa có **native PagedAttention GPU parity** hay benchmark ngang workload/VRAM, TTFT/TPOT | `DEFER_NEW_EXECUTION`, chỉ dùng baseline CPU làm tham chiếu; giữ P07 `PAUSED_PRESERVE` |
| 4 | Bộ nhớ vector ngoài, adapter/cross-attention | Exact lookup bitwise PASS; contextual retrieval và adapter đã có kết quả âm tính ở cấu hình thử | Chưa có bằng chứng cải thiện NLL tăng thêm qua memory; thiết kế attention tích hợp mới vẫn là giả thuyết | `PAUSED_PENDING_NEW_HYPOTHESIS`; giữ các FAIL |
| 5 | MoE (Mixture of Experts), tăng quy mô và GPU serving | Mô hình 4M chạy được và so logits; chưa có thí nghiệm MoE cùng ngân sách hoặc tín hiệu quality gain | Thay kiến trúc tăng chi phí, rủi ro sai đối chứng và độ phức tạp vận hành khi mô hình nền còn hạn chế chất lượng | `DEFER`, không mở P09/P10/P11 hoặc điều chỉnh kiến trúc từ PASS kỹ thuật |

**Lý do ưu tiên:** chênh lệch logits rất thấp chứng minh tuyến triển khai đúng về số học trong phạm vi giới hạn; nó không giải quyết câu hỏi mô hình có sinh được nội dung hữu ích. Trước khi đầu tư vào GPU, MoE, PagedAttention hoặc scaling, cần một kết luận định lượng/mô tả hợp lệ về chất lượng của chính mô hình đã huấn luyện, đủ khả năng phân biệt `QUALITY_NO_SIGNAL` và `QUALITY_CANDIDATE`.

### 6.2. Hướng duy nhất được chọn để chuẩn bị kế hoạch kế tiếp

**`TTM_SMALL4M_FRESH_CONTINUATION_QUALITY_GAP_REVIEW_DESIGN_ONLY`**

- **Câu hỏi khoa học:** mô hình TTM-Small-4M đã huấn luyện có tạo tiếp nối truyện giữ thực thể, sự kiện và quan hệ nhân quả trên prompt mới hay không, trong cấu hình cố định? Không tráo câu hỏi thành instruction-following của chat model.
- **Nguồn phải giữ nguyên:** checkpoint(s), tokenizer và nguồn đào tạo đã xác minh; ngưỡng/chi tiết dự kiến cần *khóa trước* một nghiên cứu mới. Không sử dụng TEST 64 truyện đã tiêu thụ hoặc tái sử dụng FRESH12 như tập xác nhận mới.
- **Thiết kế ưu tiên:** tập prompt mới do dự án tự viết và khóa hash trước khi sinh; rubric chấm bám ngữ cảnh, liên tục thực thể, nhân quả, tỷ lệ lặp; có đối chứng thích hợp, ghi ai là người chấm; không gọi một reviewer AI là đánh giá con người độc lập. Chốt unit of analysis, tiêu chí PASS/FAIL, giới hạn CPU/Colab và số lượt trước execution.
- **Điểm dừng hữu hạn:** kết thúc ở tài liệu thiết kế và đề nghị một quyết định khoa học hợp nhất nếu chủ dự án sau này chọn chạy. **Không mở quyền inference, GPU, Colab hoặc huấn luyện trong lượt này.**
- **Khi thiếu tín hiệu:** ưu tiên giả thuyết dữ liệu, vocab, context, mục tiêu và số lần lặp TRAIN, không tự chuyển ngay sang MoE, scaling hoặc cài kernel GPU.
- **Khi có tín hiệu:** đưa sang giai đoạn đối chứng hiệu năng/lưu trữ cùng checkpoint, không dùng logits parity 4/4 để claim chất lượng hay tốc độ.

### 6.3. Quyết định đóng và lưu trữ nhánh Ollama

- Kết quả khoa học L0015 và hồ sơ chứng cứ vẫn ở nhánh gốc. `PASS_SCOPED_CLOSED_UNMERGED` là quyết định **kết thúc nghiên cứu**, không phải quyết định hợp nhất source runner vào `main`.
- Bản báo cáo ưu tiên này chỉ bổ sung tài liệu quản trị. Kết quả âm tính L0013, FRESH12, vector memory và fail P07 vẫn được dẫn chiếu, không sửa.
- Bản snapshot sẽ được **đóng băng** bằng ref `archive/ttm-ollama-full-logits-scoped-20261111` trỏ **exact final commit** chứa cả báo cáo ưu tiên. Nhánh gốc `research/ttm-t5-ollama-full-logits-20261111` sẽ không được dùng cho công việc tiếp; xóa ref gốc chỉ sau khi kiểm chứng archive và đúng SHA, nếu có công cụ có quyền xóa. Không đụng Git worktree/dữ liệu trên Windows, không force.
- `MAIN_SHA`: `5d52e32f20021e36f08f284ef9864d3ba36dbead`; `MERGE_DECISION=NOT_MERGEABLE_WITHOUT_SEPARATE_REVIEW`; `SCIENCE_REPLAY=FORBIDDEN`; `LINEAGE=NO_CHANGE`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_FRESH_CONTINUATION_QUALITY_GAP_REVIEW_DESIGN_ONLY` chỉ là hướng được đề xuất cho một công việc nghiên cứu tương lai. **Không khởi chạy công việc đó trong lượt ưu tiên này.**
