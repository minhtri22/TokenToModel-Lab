# TTM R3 — Thiết kế nghiên cứu truy vết trạng thái quan hệ nhiều bước (DESIGN ONLY)

**Thời điểm:** 2026-11-11 · **Nguồn:** R1 GPT-2/Llama 4/TTM, R2/R2A và phản biện Codex `dbf2c5389358e3989c1cb4a691bb981c32ecaf45`.  
**Phân xử:** [R2A owner-scoped adjudication](TTM_R2A_CODEX_INDEPENDENT_INTERNAL_REVIEW_OWNER_ADJUDICATION_20261111.md): `DESIGN_R3_BEFORE_O1`, `O0_PRESERVED_HOLD`, `O1=DEFER`.  
**Phạm vi chính:** *đặc tả có thể bác bỏ* cho R3, chưa tạo dữ liệu/runner R3, chưa TRAIN/inference/GPU, chưa cấp quyền science, không mở TEST/Q1Q2.

## 1. Câu hỏi khoa học và phân loại bằng chứng

**H-SYMBOLIC-FEASIBILITY:** Một hệ quy tắc độc lập có thể đọc các câu chuyện ngắn, cập nhật trạng thái thực thể/mục tiêu, và trả lời đúng câu hỏi truy vết nhiều bước. Đây là phép thử đúng-sai **trên mã toy**, không phải thử mô hình neural.

**H-NEURAL-COMPOSITION:** Transformer decoder-only TTM-Small4M P02, nếu được huấn luyện trên dữ liệu phù hợp, có thể học quy tắc cập nhật và tổng quát hóa sang **đồ thị sự kiện chưa thấy**. *Phản chứng:* điểm không vượt các heuristic có cùng input trên motif OOD, kể cả khi train loss giảm.

**H-O1-INCREMENTAL:** Thêm giám sát/biểu diễn state/goal giúp hiệu quả trên graph-held-out so với O0 **khi kiểm soát thông tin TRAIN, tham số hoạt động và FLOPs**. *Phản chứng:* hiệu quả biến mất khi so với O0 có cùng thông tin giám sát/capacity, không tái lập theo seeds hoặc chỉ thắng grammar quen. Đây **không** phải hệ quả trực tiếp của Wittgenstein/DRT/Schank/Abelson mà là một giả thuyết được cảm hứng từ các lý thuyết ấy.

**Không coi** việc rule interpreter giải đúng 100% là FAIL phân biệt; interpreter là **oracle upper bound**. Một neural model hoàn toàn có thể học quy tắc mà không cần module trạng thái explicit. `STATE_TRACKING_PERFORMANCE` khác `EXPLICIT_STATE_MODULE_NECESSITY`.

## 2. Ontology tối thiểu và quy tắc cập nhật đóng băng

Định nghĩa trạng thái trừu tượng `S_t=(H_t,G_t,A_t)`:
- `H_t[item] = holder`: người đang giữ đối tượng trên sổ ghi nhận (không dùng tri thức vật lý để đoán).
- `G_t[person] = active_goal | NONE`: mục tiêu đã cam kết, đã chuyển giao, thay đổi hoặc hủy.
- `A_t[alias] = entity`: bảng tham chiếu tên thay thế; alias phải được gán **rõ ràng và đơn nghĩa**.

Các sự kiện là toán tử diễn ngôn có **tiền điều kiện** và **hậu điều kiện**:

| Event | Tiền điều kiện (precondition) | Cập nhật trạng thái |
|---|---|---|
| `INIT_HOLDER(item,p)` | item chưa được khởi tạo | `H[item]=p` |
| `HANDOFF(item,p,q)` | `H[item]=p`, `p≠q` | `H[item]=q` |
| `DEFINE_ALIAS(name,p)` | p tồn tại, name chưa gán hoặc gán đúng p | `A[name]=p` |
| `SET_GOAL(p,g)` | `G[p]=NONE` | `G[p]=g` |
| `DELEGATE_GOAL(p,q,g)` | `G[p]=g`, `G[q]=NONE`, `p≠q` | `G[p]=NONE, G[q]=g` |
| `CHANGE_GOAL(p,g,h)` | `G[p]=g`, `g≠h` | `G[p]=h` |
| `CANCEL_GOAL(p,g)` | `G[p]=g` | `G[p]=NONE` |

Câu hỏi chỉ yêu cầu `WHO_HOLDS(item)`, `ACTIVE_GOAL(person)` hoặc `IS_ACTIVE(person,g)`. Lời đáp với `NONE` phải được định nghĩa rõ; trường hợp tiền điều kiện sai / tên mơ hồ / đại từ nhiều antecedent là **`INVALID/AMBIGUOUS`**, không gán đáp án suy đoán.

**Về đại từ (coreference):** bước đầu chỉ cho phép tên thay thế được giới thiệu tường minh (`DEFINE_ALIAS`) và đại từ duy nhất antecedent theo một luật cú pháp **đóng băng, không dựa tri thức người đọc**. Cases nhiều antecedent ngang hàng phải tạo negative fixture `AMBIGUOUS_REFERENCE`. Không nói R3 đã giải diễn ngôn tự nhiên tổng quát.

Bộ sinh làm việc trên chuỗi **event structs**, bộ kiểm độc lập **chỉ parse visible text** để replay cùng luật công khai (không import generator, không dùng `source_events` hay `answer` để tính đáp án).

## 3. Ba họ cấu trúc R3 (candidates, không phải dữ liệu đã sinh)

| ID | Graph family | Yêu cầu tối thiểu | Điều kiện chấm |
|---|---|---|---|
| T1 | `MULTI_HOP_HOLDER` | ≥3 handoff hợp lệ nối tiếp cho một item; ≥2 item nhiễu, ≥6 sự kiện | Theo owner sau 3–5 bước; sự kiện cuối không luôn thuộc key hỏi |
| T2 | `GOAL_DELEGATION_CANCEL` | `SET→DELEGATE→CHANGE/CANCEL`; ≥2 người có goal song song | Kết luận goal hiện hành, NONE, và ai đang nắm nhiệm vụ |
| T3 | `ALIAS_CROSS_ENTITY` | Ít nhất một alias rõ nghĩa được dùng trong handoff/delegation; ≥3 entities | Liên kết tên thay thế với người thực, cập nhật đúng key bất kể nhiễu |

Gộp mỗi family ở dạng truyện **6–12 sự kiện**, có ≥3 key hoặc thực thể, trộn các sự kiện nhiễu, cân bằng vị trí câu đầu/cuối và số lần xuất hiện tên. Exact counts/word multiset matching được kiểm **khi thiết kế cặp cho phép**, không gượng ép khi đảo thứ tự làm vi phạm tiền điều kiện.

**Quy tắc quan trọng về phản thực:** Với chuỗi `A→B→C`, đảo hai handoff có thể gây `PRECONDITION_FAIL`. Không được đổi thứ tự bất chấp luật chỉ để tạo lexical matching; thay bằng **can thiệp một edge hay goal hợp lệ** với độ dài/token budget trong cùng bin, kiểm replay cả hai nhánh. Việc cặp không cùng word-bag phải được báo cáo, không tuyên bố đạt H-ORDER-bag như R2A nếu không có.

## 4. Ma trận phản thực 2×2 đủ bốn ô — tránh R2A-05

Mỗi nhóm bản ghi có một **đồ thị sự kiện gốc**, một can thiệp hợp lệ tại đúng key mục tiêu, và hai câu hỏi theo key:

| Ô | Trạng thái can thiệp | Câu hỏi | Ý nghĩa |
|---|---|---|---|
| `A,T` | Graph A gốc | Target key | Đáp án target ban đầu |
| `B,T` | Graph B thay một sự kiện/edge/goal hợp lệ | Target key | **Phải đổi đáp án so với A,T** |
| `A,D` | Graph A gốc | Distractor key | Đáp án distractor |
| `B,D` | Graph B | Distractor key | **Phải giữ nguyên đáp án so với A,D** |

**Bất biến:** `answer(A,T)≠answer(B,T)`, `answer(A,D)=answer(B,D)`; trên cùng graph, hai câu hỏi cho hai đáp án khác nhau khi thiết kế. Mỗi ô chỉ có input `story` + `question`; không ID, variant, split, answer, events, oracle hay nhãn ngoài schema.

**Mục tiêu toy R3 dự kiến:** 3 families × 32 groups = **96 nhóm, 384 input** (4 ô/nhóm), **chưa sinh**. Nhóm chứa toàn bộ 4 ô, aliases và hậu duệ can thiệp; không bao giờ chia mỗi ô vào split khác nhau. Không tuyên bố kích cỡ này đủ power cho science; cần phân tích sau data-generation QA.

## 5. Chống shortcut, leakage và giao thức QA

### 5.1 Các đối chứng bắt buộc

1. `BAG_OF_WORDS` (mất order); chỉ đo ceiling 50% khi thật sự đối cặp bag-matched.
2. `FIXED_POSITION` (sentence-1/2/3/last), `LAST_SENTENCE_GLOBAL` và `FREQUENCY`.
3. `KEYED_LATEST_DIRECT_ASSIGNMENT`: baseline R2A, kỳ vọng FAIL ít nhất trên những trường hợp chỉ có **handoff/delegation/alias không có direct reassignment**.
4. `LOCAL_NGRAM/LEXICAL`: không parse graph, đo ngữ cảnh ngắn/định dạng.
5. `GENERAL_SYMBOLIC_INTERPRETER`: parse đầy đủ luật và trạng thái; expected 100% trên valid toy, reject negative toy. Đây là oracle upper bound, **không phải O1**.
6. `FROZEN_P02`/O0 khi có science authorization **riêng**; không gọi model trong vòng thiết kế R3.

Kết quả chấp nhận `TOY_DISCRIMINATION_READY` chỉ khi parser đạt 100%, tất cả negative mutants bị từ chối, đồng thời shortcut **keyed latest direct assignment** không đạt 100% trên các cấu trúc yêu cầu truy vết gián tiếp. Heuristics khác phải đo thực tế; **không đặt mục tiêu làm general parser thất bại**.

### 5.2 Kiểm định schema đầu vào nghiêm ngặt (khắc phục R2A-01/02)

- `type(model) is dict` và `set(model)=={'schema','records'}` **trước khi** gọi model.
- `type(records) is list`, mỗi `record` là `dict` có **đúng** `{'story','question'}`, cả hai là string giới hạn byte/length; không có trường lạ, JSON key duplicate hoặc top-level metadata.
- Validation từ **raw JSON bytes** (phát hiện duplicate keys), kiểm SHA-256 và exact Git blob với dữ liệu public. Khi cần FINAL kín, GitHub chỉ có ciphertext + SHA; không để plaintext labels cạnh model inputs.
- `oracle.declaration` literal public toy chính xác; `labels_public=true`, `sealed_final=false`. Chặn `sealed` giả và các loại `answer_vector/oracle/split` top-level.
- Negative tests: chèn answer/root oracle/split, thay declaration, duplicate keys, ID leak, source_events/answer/split trong từng record, đổi counts, đổi quartet ID, phá group split, story leak across splits, sai tiền điều kiện, reference mơ hồ và câu hỏi thiếu referent.
- Bản R2A đã FAIL phải được **giữ nguyên**; tạo validator kế nhiệm R3 hoặc bản hardened kế nhiệm, không ghi đè receipt PASS cũ.

### 5.3 Tách dữ liệu theo motif graph, không theo hàng

- Canonical motif signature `sig(graph)`: thứ tự loại event, topology cạnh, mối quan hệ alias, cập nhật/cancel, và phụ thuộc truy vấn; **canonical hóa bỏ entity names và text template**, không loại bỏ cạnh hành động.
- `group_id`: mọi `A,T`, `B,T`, `A,D`, `B,D` và các bản diễn đạt alias cùng một nhóm.
- Mọi `group_id` ở đúng **một split**; sig(graph) trong hai split phải **disjoint** cho đánh giá OOD nghiêm ngặt. Chặn both exact-story duplicate, normalized near-duplicate và event-graph duplicate.
- **Dữ liệu toy public:** chỉ QA và demo, gồm code + oracle + model-input + receipt trên GitHub. Chỉ tạo một FINAL blind **mới, độc lập**, có nhãn riêng được escrow/commit hash trước mọi training khoa học, không đưa raw labels public trước scoring.
- Không gọi `CHALLENGE` cũ hoặc R2A public là blind holdout; không đọc TEST/Q1Q2 gốc TTM.

## 6. Ma trận kiến trúc 6 nhánh A–F — sửa R2A-07

| Arm | Kiến trúc | TRAIN supervision | Vai trò |
|---|---|---|---|
| **A — O0-CE** | P02 gốc | Next-token CE, không state labels | Mốc baseline |
| **B — O0-STATE-TEXT** | P02 gốc | CE + cùng state/goal oracle biểu diễn text | Giám sát thêm trong O0 |
| **C — O1-TRUE** | P02 + state/goal head | CE + đúng các state/goal labels của B | Ứng viên O1 |
| **D — O1-SHUFFLED** | Giống C | Nhãn oracle hoán vị **TRAIN-only**, giữ histogram | Đối chứng mất liên hệ đúng |
| **E — O0-CAPACITY** | P02 + adapter hoạt động | CE thuần không state labels | Ảnh hưởng tham số/compute |
| **F — O0-CAPACITY+STATE-TEXT** | Giống E | CE + state/goal oracle dạng text như B | **Đối chứng dung lượng và thông tin** so với C |

**Các contrast có thể giải thích**:
- `E−A`: hiệu ứng adapter/compute khi chỉ text; `B−A` và `F−E`: hiệu ứng thêm supervision **cộng** token/entropy/compute.
- `C−D`: tác dụng thông tin gắn đúng key trong head nhưng cũng có nguy cơ shuffled-label gây hại; không đủ một mình khẳng định O1.
- `F−B`: effect capacity ở cùng text-label supervision, khi adapters và compute được kiểm soát.
- `C−F`: cùng nguồn oracle label/capacity mục tiêu nhưng **objective text-token khác class head**, nên tối đa suy ra khác biệt của **gói kiến trúc+mục tiêu giám sát dưới điều kiện đã khớp**, không chứng minh pure architecture.

**Hai sổ ngân sách phải khóa**:
1. *Information/supervision ledger*: cùng TRAIN source/split, tokenizer, checkpoint/trunk nếu khả dụng, số semantic facts được cung cấp, số text targets và số state target examples; nếu serialized text thêm token, ghi chênh lệch và không gọi exact token exposure equal một cách giả.
2. *Compute/capacity ledger*: total/trainable/active params, forward slots, tính FLOPs thật/profiler, optimizer updates, GPU seconds, VRAM, seed và state restore. Đặt dung sai định lượng **trước GPU**; nếu không match thì `FAIR_SUPERVISION=HOLD` hoặc chỉ claim so sánh có điều kiện.

**Thực tế ngân sách:** 6 arms có thể nặng hơn hạn mức Free T4; nếu phải thu hẹp còn 4 arms, quyết định tập con và giới hạn claim **trước khi xem bất kỳ kết quả**. Không hạ hậu nghiệm. **Không cho phép `oracle_at_inference>0`**; label oracle chỉ TRAIN-only. Không tự thêm state labels vào dữ liệu TinyStories gốc.

## 7. Gate kết thúc của DESK DESIGN và tiêu chí đưa R3 vào thử nghiệm

**Giai đoạn này đóng khi**: (i) phân xử R2A bảo toàn FAIL/PASS đúng nghĩa; (ii) ontology và 4-cell counterfactual định nghĩa đủ; (iii) bảng 6 arm và budget/claim constraints nhất quán; (iv) commit/readback GitHub. Đây là **source/design PASS**, không phải science PASS.

**Để mở bước R3 CPU tiếp theo** (chưa T4): hiện thực generator, checker riêng biệt, strict input prevalidation; chạy một **batch tích hợp** trên 96×4 candidate public toy, negative mutation, independent source readback và shortcut baselines; nếu grammar/split không khả thi thì `FAIL/HOLD` và sửa design trước prereg, không giả mạo PASS.

**Để mở science sau đó:** cần quyền dữ liệu, TEST/holdout độc lập có SHA/escrow, bộ đánh giá blind và người chấm nội bộ scoped, số tham số/compute/supervision ledger, lịch huấn luyện/seed và owner authorization một lần; không dùng lại permit cũ. `O1=DEFER`, `O0=HOLD_PRESERVED`, `COLAB=NOT_AUTHORIZED`.

**Bước thực hiện tiếp theo:** `TTM_R3_STRICT_INPUT_VALIDATOR_AND_STRUCTURAL_GRAPH_TOY_IMPLEMENTATION_SINGLE_CPU_QA`, rồi phân xử O0-only hay R3/O1 prospective ablation từ bằng chứng thật, không thêm chuỗi micro-gates.
