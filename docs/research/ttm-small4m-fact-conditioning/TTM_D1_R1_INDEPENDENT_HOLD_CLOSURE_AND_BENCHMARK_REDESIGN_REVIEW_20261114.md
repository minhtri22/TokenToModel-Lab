# TTM-Small-4M D1 Bridge R1 — Independent HOLD Closure & Benchmark Redesign Review

**Operation:** `TTM_SMALL4M_D1_R1_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_DECISION_SINGLE_GATE`  
**Ngày:** 14/11/2026  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Evidence HEAD:** `49513729b1893f33be77ecd31554d2e9377925ea`  
**Parent evidence:** `d24c50ad8a9e377264dd8fa073bcc553824f8992`  
**Frozen scientific HEAD:** `dd52804685d186c17e600221ffb16ce78aea12ea`  
**Reviewer:** Independent AI source reviewer (khác receipt tác giả; không phải ký duyệt con người)  
**Chế độ:** READ_ONLY · DESIGN_ONLY · SOURCE_ONLY · NO_SCIENCE_EXECUTION  
**Phán quyết duy nhất:** **`GO_CLOSE_R1_FORMULATION_DESIGN_ONLY`**  
**Science release:** `HOLD`

## 1. Nguồn, SHA và tính độc lập

Đọc toàn bộ báo cáo closure, receipt, prospective semantic contract, admission matrix, paired probe, readiness/custody và ba chương trình nguồn bằng kết nối GitHub **tại chính commit cố định**, không dùng `main`. Phép compare commit xác nhận `49513729b189…` đi trước `d24c50ad8a9e…` đúng một commit; merge base là parent (ahead 1, behind 0).

Manifest: `artifacts/research/ttm-small4m-fact-conditioning/evidence_d1_r1_minimal_constructive_20261114/TTM_D1_R1_SOURCE_PACKET_SHA256_MANIFEST_20261114.json`. Tự tính SHA-256 trên byte UTF-8 của 11 tệp trả về; đồng thời tính lại SHA-1 có tiền tố Git blob `blob <length>\0` và đối chiếu SHA GitHub. Phép hash SHA-256 được tự kiểm bằng vectors rỗng và `abc`. **11/11 SHA-256 PASS; 11/11 Git blob SHA-1 PASS.** Không kiểm tra các tệp nằm ngoài manifest. Blob V6 `c6ac330c40e31035116add165ef30fa58af59639` đã truy xuất và đối chiếu định nghĩa AM01 về mặt nội dung.

| Tệp (tên rút gọn) | SHA-256 đã xác minh | Git blob SHA-1 |
|---|---|---|
| `TTM_D1_R1_32_CONSTRUCTIVE_ADMISSION_MATRIX_20261114.json` | `45ec74069975b37725f8daf01a75ec074a81d8fa87d477d551333a9029afeedc` | `73246abe741e5330211ebc343a79a4943443a026` |
| `TTM_D1_R1_BOUNDED_CONSTRUCTIVE_SEARCH_RECEIPT_20261114.json` | `da9bc0865c0be149544a12db62d378db536fd12492b803b8031b04732248ecfe` | `ab3e527328def788a9b187e2290f8beea5c826f6` |
| `TTM_D1_R1_BOUNDED_PAIRED_CONSTRUCTIVE_PROBE_20261114.json` | `b6347f8ca2ec0c1e10d44bf87d98b01ebf61042ff70d465fc4057040c7335b95` | `378a223118781a6082928e2d862c3d9513b4b11a` |
| `TTM_D1_R1_CONSTRUCTIVE_INDEPENDENT_REVIEW_HANDOFF_20261114.md` | `437d4979a421039957328f99c42675a30cf2ffc748df799628f323950f2f862a` | `b2e07f1becf593de1757a53d03358662b30d8a90` |
| `TTM_D1_R1_CONSTRUCTIVE_SHORTCUT_RENDER_CUSTODY_GATES_20261114.json` | `abfd3e53a24431d76312feab4e60f82546d98035d77d3aecf842385a7c82fd64` | `a5f43969ba5192b28050bdbc8a368b7eaee26e5f` |
| `TTM_D1_R1_CONSTRUCTIVE_SINGLE_GATE_ADJUDICATION_RECEIPT_20261114.json` | `db1fecb0fb8b574d7864dc1075c6c164de4c043e11cf63cf301c2e742878b27d` | `970f95ee0483b438c281a90c9cf081301e826c6e` |
| `TTM_D1_R1_MINIMAL_CONTRACT_CONSTRUCTIVE_FEASIBILITY_REPORT_20261114.md` | `e7a34a5ab89b81b3cb232ad9993bc08d5f81a294b617a758f7736641337ae72b` | `3b133e7fda086f6fc511f923f2917d43138da33d` |
| `TTM_D1_R1_PROSPECTIVE_MINIMAL_SEMANTIC_CONTRACT_FREEZE_20261114.json` | `dcf2ec3af62f1f3a738b945fe332df171ffb3ecf8b8517ba1f12cde47cebd091` | `d142938352f5b4149d5440614939dc173dade2ea` |
| `constructive_search.py` | `ba38165ff6baba142980f9b4af3178c9feb53ab3002207dc063dcc7512b51b1c` | `e7fda84fed9e27a772d38b76d5f68846404e3fc4` |
| `pairwise_constructive_probe.py` | `7c9f7ada68bb9d7047dc484a9c1009d962921dd46c0873d8cf48ba61f848f8db` | `4f385415125142f2be7f9b48edcab4c8f42a96e6` |
| `prepare_closure.py` | `ed8dd8813050b099d5606f3d77f65fb6e21e44a57332a9689fdc879cfdb89616` | `f4434a87b14c60f43b4f9a2e2ed11881105c3afd` |

**Phạm vi độc lập:** phản biện trực tiếp logic mã nguồn, đối chiếu frozen V6 và receipt tác giả. Không chạy engine/QA mới, không chạy lại lịch sử 13/13 và 12/12; 12/12 test mới là *source self-test được báo cáo*, không phải independent execution của reviewer. Không claim external human attestation.

## 2. Kiểm toán 330 tình huống

| Category | Tình huống | Unique first action | A/B cùng goal, một fluent khác, first action khác | Motif proxy | Admitted OOD |
|---|---:|---:|---:|---:|---:|
| `entity_location` | 96 | 20 | 2 | 1 | 0 |
| `causal_reasoning` | 54 | 16 | 1 | 1 | 0 |
| `rule_constraint` | 108 | 52 | 29 | 3 | 0 |
| `goal_persistence` | 72 | 6 | 0 | 0 | 0 |
| **Tổng** | **330** | **94** | **32** | — | **0** |

Đây là số ghi trong source receipts đã đối chiếu và rà soát thuật toán, **không phải số tái chạy độc lập**. `constructive_search.py` khai báo các tích Descartes theo category, BFS reachability tối đa **3 action** (`edge_cap=3500`) và giữ các first action đồng độ dài ngắn nhất. `pairwise_constructive_probe.py` chỉ xét cặp unique, goal bằng nhau, trạng thái khác đúng **một typed leaf** và first action tuple khác nhau; motif chỉ là proxy gộp tên field và cặp verb.

### Giới hạn diễn giải kết quả

- **Không tìm thấy** đủ cấu trúc mới trong subgrammar đã duyệt: đúng.
- **Không đủ admission**: đúng, 0/16 TRAIN và 0/16 OOD được chứng nhận; ma trận 64 cặp TRAIN–OOD mới chưa chạy.
- **Ontology V6 bất khả thi toàn cục**: **không được chứng minh**. Search giới hạn role, state, goal, thời gian T0–T2, một exogenous request và 3 bước; sử dụng prospective P1 **khác frozen V6**.

## 3. Expressive capacity theo category

**`entity_location` (96 / 20 / 2):** chứng minh được một vài khác biệt hành động `CARRY`–`TRANSFER` khi đổi holder. Cặp duy nhất một fluent và một coarse motif không chứng minh bốn action-causal topology OOD. Đồng thời physical TRANSFER làm miền hợp lệ hẹp hơn V6 gốc.

**`causal_reasoning` (54 / 16 / 1):** unique actions chủ yếu `WAIT` (13) so với `ACTIVATE` (3). Một paired motif `scheduled_at` với `WAIT`–`WAIT` phản ánh lịch/chỉ số thời gian hơn là chuyển cấu trúc nhân quả. Deadline trong task goal có thể mang cue không liên quan đến graph novelty.

**`rule_constraint` (108 / 52 / 29):** 29 pairs nhưng chỉ 3 proxy sau chuẩn hóa thô; không đồng nghĩa 3 independent causal graphs. Đặc biệt `shortest()` sử dụng `actions()` **không lọc allowed verbs theo category**, dẫn tới 18 unique-first `CARRY`, trong khi frozen V6 category `rule_constraint` chỉ liệt kê `TRANSFER`, `WAIT`, `RETAIN`. Vì vậy phép đếm không được nâng thành khả thi category đúng nguyên thiết kế.

**`goal_persistence` (72 / 6 / 0):** sáu unique đều là `RETAIN(i0,T0,T2)`, trong phạm vi task safety đến T2, request cuối kỳ và điều kiện stationary. Không có cặp một-fluent đổi hành động đầu tiên. Chỉ chứng minh tính đơn điệu motif trong subgrammar, **không chứng minh** V6 không thể biểu diễn persistence OOD.

### Hai điểm kỹ thuật ảnh hưởng độ tin cậy của *negative evidence*

1. `persistence()` sau một hành động trực tiếp gọi `events_between(out,through)` để chạy đồng hồ tới T2, kể cả khi không có `WAIT` hợp lệ. Trong khi đó `WAIT` ở `step()` cần một trigger đã schedule. Nếu model thời gian là passive clock, phải ghi rõ tiên đề và hành động quan sát; nếu `WAIT` độc quyền tiến đồng hồ thì đó là semantic inconsistency. Vì thế không thể coi kết quả `persistence` là oracle quỹ đạo thời gian đầy đủ.
2. `pairwise_constructive_probe.py` đếm diff theo leaf. Một thay đổi có nghĩa từ `external_transfer_request=NONE` sang một yêu cầu cụ thể có thể thay **cả `at`, `item`, `recipient`**, nên bị loại bởi điều kiện `len(delta)==1`. Số 0 pairs của `goal_persistence` không phải cận trên cho mọi matched-world intervention có ý nghĩa.

Những phát hiện này **không** tạo constructive GO, vì không cung cấp một bộ 32 AST được chứng nhận. Chúng làm rõ tại sao closure chỉ là **quyết định dừng R1 hiện tại**, không phải phủ định khả năng nghiên cứu khác.

## 4. Phản biện hợp đồng ngữ nghĩa P1 với frozen V6

| Chủ đề | Đánh giá reviewer | Yêu cầu nếu nghiên cứu kế nhiệm |
|---|---|---|
| `TRANSFER` | Co-located hợp lý trong thế giới vật lý, nhưng V6 thiếu tiền điều kiện này; chuyển từ xa trong V6 có thể là mô hình chuyển giao logic, cần định nghĩa rõ. | Chọn physical hoặc logical transfer; amendment minh bạch. |
| `CARRY` | Hỗ trợ vật đã giữ và đồng bộ mọi held item là hợp lý, nhưng V6 yêu cầu unheld target. | Phê duyệt preconditions/effects mới trước khi tìm AST. |
| `WAIT` | Tiến tick, xử lý trigger trước request và protection inclusive là ứng viên tốt; `persistence` lại cho tự nhảy đồng hồ. | Khóa duy nhất cơ chế tiến clock, external events, priority và replay semantics. |
| `RETAIN` | Không được chèn gold-conditioned tie-break. Pure safety khiến nhiều first actions cùng đúng; sáu unique chỉ là một motif phụ thuộc tình huống hẹp. | Thiết kế goal thời gian đo được / objective có căn cứ, kiểm uniqueness không bằng ưu tiên tùy tiện. |
| `GENESIS T0` | Initialization axioms cho trạng thái có sẵn holder là chấp nhận được trong mô hình Markov nếu công khai; không phải chứng minh đã từng diễn ra `CARRY`. | Kiểm mọi invariant và phân biệt `valid initial state` với `reachable from previous history`. |

P1 prospective là **material amendment chưa phê duyệt**, tuyệt đối không đổi frozen V6 theo cách suy diễn. `EXOGENOUS` còn là fluent mới không có trong V6 AM01.

## 5. Constructive counterexample và điều kiện veto closure

**Không có phản chứng constructive đủ mạnh** trong chứng cứ đã thẩm định và reviewer không tạo bộ 32 AST mới. Các ví dụ unique hoặc một OOD riêng lẻ không thể chứng minh 4 TRAIN + 4 OOD cho **từng** category; cũng thiếu canonical graphs, 64 so sánh nonoverlap, matched-world witnesses, independent equivalence/genesis/shortcut, render/parser, và quyền dữ liệu. Không dùng oracle proxy hoặc output mô hình để chọn skeleton.

Kết quả vẫn để ngỏ khả năng một ontology/goal/clock mới có nghiệm, nhưng việc đó đòi hỏi một **đề xuất prereg amendment** riêng được owner xét, không phải lý do tiếp tục bơm blueprint vào R1.

## 6. Construct validity, shortcut, renderer và custody

- Novelty không được xác nhận chỉ bằng verb khác, role khác hay time khác. 64 cặp nonoverlap mới là `NOT_EXECUTED_NO_32_ADMITTED_INPUTS`.
- Baselines cũ category+side 10/32 và shallow 64/64 là **inherited negative controls**, không chứng nhận skeleton mới.
- Matched-world witness cùng goal, một can thiệp có ý nghĩa, action delta có chứng minh nhân quả chưa được cung cấp cho OOD mới.
- Renderer/parser/tokenizer T1, positive/negative grammar 64+/64−, lexical cues và rights/PII chưa kiểm. Private EVAL/gold chưa tạo, custody ledger/HMAC chưa chạy.
- Chi phí Small-4M chưa phải nút thắt chính: **bài toán đo lường hành động nhân quả chưa xác lập được benchmark hợp lệ**. Chạy GPU lúc này chỉ tạo số liệu không thể diễn giải chắc chắn.

## 7. So sánh hướng benchmark kế nhiệm (chỉ đề xuất)

| Lựa chọn | Construct validity | Thiết kế oracle | Khả thi Small-4M | Đánh giá |
|---|---|---|---|---|
| **A. Giữ sáu verb, sửa task goals, clock, events và ontology bằng amendment** | Cao **nếu** chứng minh được graph/witness | Trung bình; khó nhất persistence và unique goal | Tương đối tốt, action alphabet giữ nguyên | **Ưu tiên đề xuất**, chưa cấp phép |
| **B. Mở rộng ontology với event/agent motion/custody verb mới** | Có tiềm năng cao với mục tiêu persistence thật | Trung bình–khó vì state/transition mới | Tốn dữ liệu và độ phức tạp hơn với 4M | Dự phòng nếu A không đủ biểu đạt |
| **C. Thu hẹp hypothesis vào category chứng minh được** | Tốt cho giả thuyết mới hẹp hơn, **không** giữ được claim gốc | Dễ kiểm hơn | Nhẹ nhất | Phương án cuối, cần sửa prereg/hypothesis |

**Khuyến nghị:** A chỉ là `DESIGN_PROPOSAL_NOT_AUTHORIZED`. Hãy yêu cầu owner phê duyệt hướng nghiên cứu riêng nếu muốn tiếp tục; không tự khởi tạo phase, không đổi giả thuyết đã khóa và không tự tạo permit. Một benchmark tốt phải có 4+4/category **với canonical graph và witnesses độc lập trước khi định nghĩa gold kín**; không tạo AST cho đủ hạn ngạch.

## 8. Phán quyết độc lập — duy nhất

**`GO_CLOSE_R1_FORMULATION_DESIGN_ONLY`**. Chấp thuận đóng công thức D1 Bridge R1 tại `HOLD_ONTOLOGY_FEASIBILITY`, ngừng tạo 32 blueprint thay thế theo công thức hiện hành, giữ đủ lịch sử và evidence, và chỉ khuyến nghị benchmark redesign. Chưa có phản chứng theo tiêu chuẩn 4C để bác bỏ closure. **Không suy diễn thành impossibility của V6, không có Science GO**.

## 9. Preservation / closure gates

| Gate | Giữ nguyên |
|---|---|
| `D1_BRIDGE_SCIENCE` | `HOLD` |
| `D1_EXISTING` | `HOLD_UNMODIFIED` |
| `TEST_Q1Q2` | `SEALED` |
| `FC02` | `NOT_OPENED` |
| `GPU` | `0` |
| `TRAINING` | `0` |
| `INFERENCE` | `0` |
| `FROZEN_V6` | `UNCHANGED` |
| `MAIN` | `UNCHANGED` |
| `lineage.md` | `UNCHANGED` |
| `EVAL_CUSTODY` | `NOT_EXECUTED` |
| `OWNER_SCIENCE_PERMIT` | `NOT_GRANTED` |

Không thay đổi GitHub `main`, V6, `lineage.md`, PR, TEST hay EVAL; không commit artifact này. Báo cáo và receipt chỉ tồn tại trong output làm việc để owner lưu về sau nếu muốn.

## Bước thực hiện tiếp theo — duy nhất

`TTM_SMALL4M_D1_R1_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_DECISION_SINGLE_GATE` — **đã đánh giá xong tại commit cố định**. Kết quả closure là `GO_CLOSE_R1_FORMULATION_DESIGN_ONLY`; không có lệnh triển khai hoặc science task kế nhiệm được cấp quyền trong review này.
