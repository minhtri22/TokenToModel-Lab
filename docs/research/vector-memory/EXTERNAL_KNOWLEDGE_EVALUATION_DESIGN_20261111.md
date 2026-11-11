# TTM Vector Memory — Thiết kế đánh giá tri thức ngoại sinh v1

**ID:** `TTM_VECTOR_MEMORY_EXTERNAL_KNOWLEDGE_EVALUATION_DESIGN`  
**Ngày:** 2026-11-11  
**Nhánh duy nhất:** `research/ttm-vector-memory-architecture-20261111` (ngoài P00–P12).  
**Trạng thái:** `DESIGN_AND_FIXTURE_STATIC_QA_ONLY` — **chưa huấn luyện adapter, chưa inference khoa học, chưa có YES/NO về năng lực mô hình**. `main` không thay đổi; không merge.

## 1. Tại sao phải thiết kế lại bài toán?

L0015 chứng minh khả năng cất bảng embedding/head ra ngoài bằng truy xuất chính xác, không chứng minh tri thức tăng thêm. L0016–L0019 cho thấy truy xuất hidden state/next-token từ TRAIN có tương quan với nhãn nhưng những cơ chế kết hợp thử trước **không làm giảm NLL** so với backbone. Riêng Gated Cross-Attention dùng memory value là **next-token embedding đã có trong dữ liệu TRAIN**; không phải sự kiện bên ngoài mà model cần đọc. Đánh giá cũ dùng VAL nhiều lần, nên không hợp lệ để xác nhận mô hình mới.

**Câu hỏi v1:** Khi quan hệ giữa *thực thể tưởng tượng ↔ nhãn truy cập* được gán ngẫu nhiên **sau khi khóa checkpoint**, chỉ có trong bộ nhớ ngoài và **không hiện diện trong câu hỏi**, liệu frozen TTM-Small-4M với một bộ đọc bộ nhớ train-only có sử dụng đúng sự kiện đó hay không?

Đây là **bài toán kiểm tra cơ chế đọc sự kiện (external-fact binding toy task)**, **không** khẳng định hiểu ngữ nghĩa thế giới thực, thực hiện RAG tổng quát, hoặc tăng kiến thức ngôn ngữ. Giá trị là chữ giả lập từ tập 16 nhãn, còn khóa là mã thực thể tưởng tượng độc nhất theo truyện. Model có thể đã biết các chuỗi chữ riêng lẻ; điều không thể biết từ checkpoint hoặc câu hỏi là *ánh xạ mới được gán ngẫu nhiên*.

## 2. Hợp đồng dữ liệu mới theo từng truyện

Một case = 1 truyện = 1 mục tiêu dự đoán; **không tái sử dụng bất kỳ truyện/cửa sổ VAL lịch sử nào**. Schema `ttm.vector_memory.external_knowledge.fixture.v1`.

| Trường | Ý nghĩa / ràng buộc |
|---|---|
| `case_id`, `split` | ID truyện; TRAIN/DEV/TEST disjoint |
| `question` | Câu hỏi chứa khóa thực thể, **không có nhãn trả lời** |
| `answer` | Một nhãn trong 16 mã giả lập, được gán ngẫu nhiên và cân bằng theo split |
| `correct_memory` | 3 bản ghi `{key,value,text}`; đúng 1 record có `key` trùng thực thể trong câu hỏi và mang gold label |
| `wrong_memory` | Cùng 3 keys, thứ tự và số bản ghi; **chỉ thay value** của record target bằng nhãn sai hợp lệ; không chứa gold ở các record khác |
| `none_memory` | Danh sách rỗng và `no_memory_mask_all=true`; đường memory bắt buộc tắt/mask nhưng giữ nguyên toàn bộ backbone và adapter parameters |
| `target_record_rank` | Vị trí record đúng thay đổi theo truyện (0/1/2), tránh shortcut chọn dòng đầu tiên |

Ví dụ **minh họa, không phải dữ liệu khoa học TEST**:

- Câu hỏi: `For archive object objabcd..., what is its assigned access tag? Answer:`
- Memory đúng: `objabcd... → mipor`; cùng lúc có 2 thực thể gây nhiễu.
- Memory sai: **vẫn** `objabcd...` nhưng đổi nhãn sang `navek`; giữ nguyên hai record gây nhiễu.
- Không memory: không cung cấp record nào, attention mask hoàn toàn, không thay prompt.
- Gold answer: `mipor`. Nếu không có memory, gold không thể suy ra một cách có hệ thống từ question vì mapping được gán ngẫu nhiên.

**Khối lượng v1 đã cố định:** 256 TRAIN / 64 DEV / 64 TEST story-level. Tập 16 nhãn chung qua splits để mô hình học *cách đọc* chứ không buộc sinh token chưa từng có; thực thể và mapping của mỗi truyện không trùng qua split. Mỗi split cân bằng 16 nhãn: TRAIN mỗi nhãn 16 lần, DEV/TEST mỗi nhãn 4 lần. Hai biến thể câu hỏi được chọn theo seed, không cho câu hỏi và fact cùng đứng trong input text GPT.

**TEST hiện tại chưa được tạo và chưa SEALED.** Bộ sinh từ chối tạo TEST nếu thiếu `TTM_VM_TEST_SECRET` (tối thiểu 24 ký tự) và yêu cầu tệp TEST chỉ nằm dưới `/_private/` của root dự án. Khi chuyển sang thí nghiệm, người giữ TEST độc lập phải tạo secret **trước khi train**, khóa commitment SHA-256 riêng tư, tạo TEST đúng một lần và giữ bí mật nội dung cho đến lúc đóng băng cấu hình/seed/code/checkpoint. Không được dùng `NON_SCIENCE_QA_ONLY_DO_NOT_USE_AS_TEST_SEED` trong kiểm thử khoa học. Chỉ commit tổng số, SHA commitment và các thống kê aggregate phù hợp, không công khai secret hoặc TEST rows trước adjudication.

## 3. Ba nhánh chính và chẩn đoán tách lỗi

Cả ba nhánh **cùng frozen checkpoint P02**, cùng token/position embedding, 4 Transformer blocks, LayerNorm, tied output head; cùng số tham số trainable của Memory Reader, cùng prompt/input-length và seed. Không được sửa checkpoint.

- **A — NO_MEMORY:** cùng adapter nhưng all-memory attention mask/bypass, không đưa factual value; frozen-backbone baseline và parameter-matched no-memory control ghi tách riêng.
- **B — CORRECT_MEMORY:** tra thực thể từ question và cấp record đúng (cùng 2 distractors) cho Memory Reader; không đặt fact trong prompt GPT; reader nhận thông tin qua kênh cross-attention riêng.
- **C — WRONG_MEMORY:** cùng keys và rank/record count với B, thay duy nhất target value bằng một nhãn sai; không dùng gold để tạo query/retrieval.

**Tách hai chế độ:** `ORACLE_LOOKUP` tìm record qua khóa thực thể trực tiếp **không dùng gold**, làm positive-control chỉ ra tầng reader/gate có thể học đọc thông tin hay không. `RETRIEVED_TOPK` tìm bằng frozen/learned query embedding dựa trên question, chỉ từ keys và cùng các distractor; báo riêng recall@k, MRR, answer NLL. Không lấy kết quả oracle để claim retrieval ngữ nghĩa.

Nếu **oracle pass nhưng actual retrieval fail**, ưu tiên sửa retriever; nếu **oracle fail**, ưu tiên sửa reader/tokenizer/gate; nếu B không hơn C, kiến trúc chưa chứng tỏ dùng đúng fact; nếu B hơn C nhưng không hơn A, có thông tin có điều kiện nhưng chưa cải thiện dự đoán.

## 4. Đường tính toán và kiểm soát công bằng

`Question → Frozen P02 → h`; song song `Question → query encoder → external key retrieval → K/V records → Memory Reader Cross-Attention → gated residual → same tied output head`.

- Gate per-query có đường bypass zero-effect; `W_o` hoặc gate khởi tạo sao cho lúc chưa train dự đoán trùng backbone (up to numerical tolerance).
- Memory value phải có **key identity + encoded value**, không thay bằng `next-token embedding` đơn độc; giữ riêng tối đa 3 record/nhóm, không gộp một vector trước attention. Nếu có position encodings hoặc negative examples, cả B/C dùng chung.
- Reader chỉ train trên TRAIN (tối đa 128 optimizer steps trong pilot kế tiếp; CPU FP32, batch 16, seed prereg mới). Giữ frozen backbone; không fine-tune tokenizer/TTM weights.
- Mỗi story TRAIN chỉ có fact của story đó trong đúng chỗ memory; không dùng gold/target label để tìm hàng; không để answer rò qua prompts, metadata hoặc token selection.
- Trước chạy inference, bắt buộc QA tokenizer T1 BPE trên cả label; đo số token câu hỏi + answer và ngưỡng context 256; **không được loại truyện dựa theo nhãn/DEV**. Wrong value cùng 5 ký tự với right, nhưng có thể khác số BPE tokens: phải ghi như một hạn chế và kiểm từng trường hợp, không giả định bằng nhau.
- Nếu so sánh tốc độ/chi phí, tính thêm số tham số reader, RAM vector-index, latency retrieval; kết quả NLL không tự suy ra lợi ích triển khai.

## 5. Thước đo và tiêu chí khóa trước khoa học

**Primary:** `answer-only NLL`, chỉ các token thuộc nhãn trả lời theo tokenizer T1 gốc, không chấm phần câu hỏi hoặc văn bản memory. Báo micro NLL trên token và **mean per-story answer NLL** (metric phán quyết) để tránh bias bởi nhãn tách thành nhiều token. Gold tokenizer không được thay đổi giữa arms.

**Secondary:** exact-match của câu trả lời (greedy, không constrained) và 16-way candidate-rank accuracy (được ghi rõ đây là constrained); tỷ lệ lookup target hit@k / MRR; memory-copy error; gate-mean và bypass-parity; paired-difference per story.

**Quy tắc `YES_SCOPED` trong TEST mới, chỉ khi tất cả đồng thời:**

1. `RETRIEVED_TOPK` đạt recall@3 **ít nhất 95%** trên 64 truyện TEST, do khóa thực thể hiện tường minh; nếu không => `RETRIEVER_FAIL`, không chốt reader YES/NO.
2. `B_CORRECT` giảm **mean per-story answer NLL** ít nhất `0.05 nats/token` so với cả `A_NO_MEMORY` và `C_WRONG_MEMORY` (paired differences).
3. Paired bootstrap theo truyện (`n=1000`, seed độc lập khóa trước) có cận dưới 95% của **A−B và C−B đều >0**; đây là ngưỡng sàng lọc pilot, không phải kiểm định confirmatory phổ quát.
4. Đối chứng đúng fact/foil có cùng số record, key IDs, question, frozen weights và cùng đường tính toán; backbone unchanged, TEST chưa bị dùng tune, SHA evidence đầy đủ.

Nếu các điều kiện dữ liệu/QA/nguồn lỗi, phân loại `INVALID_OR_NOT_EXECUTED`. Nếu điều kiện hợp lệ, retrieval pass nhưng không đạt cải thiện => `NO_SCOPED`; không biến thất bại thành yêu cầu chạy GPU tiếp. Phải báo cả chênh lệch NLL B−A, B−C và độ bất định, ngay cả khi FAIL.

**DEV chỉ để sửa lỗi công cụ và chọn một cấu hình reader đã tiền đăng ký trước khi mở TEST; không lựa chọn seed/hyperparameter bằng nhiều lượt.** TEST 64 truyện chỉ chấm **một lần** sau khi khóa mã, checkpoint, tokenizer và mọi lựa chọn. Đừng nhầm CHECK PASS tĩnh với kết luận khoa học.

## 6. Bằng chứng thiết kế hiện có / các cổng chưa thực thi

| Hạng mục | Hiện tại |
|---|---|
| Generator deterministic TRAIN/DEV | PASS_SOURCE_STATIC_QA |
| QA chống rò câu hỏi/đáp án; đúng/sai/không memory | PASS_SOURCE_STATIC_QA |
| TRAIN 256 / DEV 64 fixtures | GENERATED_SYNTHETIC_DESIGN_ONLY |
| TEST 64, secret và seal | `NOT_MATERIALIZED_NOT_SEALED` |
| Tokenizer T1 label audit | NOT_EXECUTED |
| Frozen P02 + external-fact adapter integration | DESIGN_ONLY |
| TRAIN adapter, retrieval, NLL, TEST | **NOT_EXECUTED** |
| GPU | **NOT_USED** |
| `main`, P00–P12 | UNCHANGED |
| `lineage.md` | UNCHANGED — chưa có khoa học PASS/FAIL mới |

Tệp: `tools/research/vector-memory/external_knowledge_fixture.py`, `test_external_knowledge_fixture.py`, fixtures TRAIN/DEV trong `artifacts/research/vector-memory`, QA JSON `TTM_EXTERNAL_KNOWLEDGE_DESIGN_STATIC_QA_20261111.json`. Không commit checkpoint hoặc dữ liệu TinyStories riêng tư; không tạo/test mã thực thi science trong bước DESIGN_ONLY.

## 7. Bước thực hiện tiếp theo

`TTM_VECTOR_MEMORY_EXTERNAL_FACTS_ORACLE_READER_CPU_PILOT_READINESS`

Chỉ sau khi có khóa TEST độc lập, kiểm tra tokenizer và frozen bypass, chuẩn bị một source-only runner tích hợp cho ba nhánh. Chưa cấp GPU; không huấn luyện thêm cho đến khi các điều kiện nguồn/đối chứng sẵn sàng. Chưa merge `main`.
