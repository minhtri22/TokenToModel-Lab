# TTM-Small-4M D1 Bridge V3 — Phản biện AI độc lập về nguồn và giao thức tiền đăng ký

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V3_DISTINCT_NEW_CHAT_PREREG_SOURCE_REVIEW_SINGLE_GO_HOLD_NO_GPU`  
**Ngày:** 2026-11-14  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Handoff commit:** `e186eb334f7a48a2e513f2ac80454ebb40405ef1`  
**Scientific frozen HEAD:** `8f0714b29c98ca9be7c7444f964267faea4efb76`  
**Reviewer:** `INDEPENDENT_NEW_CHAT_AI_SELF_ATTESTED_NOT_HUMAN_NOT_EXTERNALLY_VERIFIED`  
**Mode:** `READ_ONLY / DESIGN_ONLY / SOURCE_ONLY / NO_GPU / NO_TRAIN / NO_INFERENCE / NO_PRIVATE_EVAL_GOLD / NO_TEST_Q1Q2`  
**Single design verdict:** **`HOLD_REVISE_BEFORE_PREREG`**.  
**Science:** `D1_BRIDGE_SCIENCE=HOLD`.

## 1. Xác minh nguồn (source custody) — 7/7

Đã đọc bảy tài liệu bắt buộc bằng GitHub connector, tại **đúng frozen commit**; Git blob SHA-1 trả về khớp SHA-1 kỳ vọng cho cả bảy. Đây là đối chiếu metadata/content GitHub qua một kênh, **không** phải byte-level SHA-256 tái tính độc lập trên bản tải gốc. Không xem golden labels, private EVAL, output của model hay các nhánh TEST Q1/Q2. Không chỉnh sửa GitHub.

| Ref | Tài liệu tại frozen HEAD | Expected / observed Git blob SHA-1 | Status |
|---|---|---|---|
| S1 | [V3 design Markdown](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_PREREG_DESIGN_AND_OWNER_HOLD_20261114.md) | `50556c367844e9f9c8aa3bf1a97e394fd74c37f1` | PASS_METADATA |
| S2 | [V3 machine JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_D1V2_01_11_DESIGN_HOLD_20261114.json) | `927e7931ee044c70db4354db43330ae93f11331d` | PASS_METADATA |
| S3 | [V3 same-author QA JS](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/tools/pilot_t4/fc01/ttm_d1_bridge_v3_source_only_contract_qa_20261114.js) | `0d5ffa42e57344692e48ffcb2e134e921a9d8f95` | PASS_METADATA |
| S4 | [V3 QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_SINGLE_PACKET_SOURCE_ONLY_QA_AND_OWNER_HOLD_20261114.json) | `d6dd1cd2c8e78677c81ba01b26851d933d5f82a5` | PASS_METADATA |
| S5 | [V2 distinct review MD](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_DISTINCT_AI_SOURCE_REVIEW_20261114.md) | `3191c5427354b7239602fcb66b92202554084c30` | PASS_METADATA |
| S6 | [V2 distinct review JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_DISTINCT_AI_REVIEW_RECEIPT_20261114.json) | `7b7074ad0166b43f20ca8e10d9bf8ac4e96001fd` | PASS_METADATA |
| S7 | [lineage.md — L0018](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/lineage.md) | `ddff96dbf8f52ab8f13ce169d9e264a1a05dd3bc` | PASS_METADATA |

Các SHA-256 của review V2 (`f482d9855b16bed2bc764e63c2d986259b8f94bd9bb1f65e30b145f5e5e23cae` và `52168ae7c523d1999388e9a2de211e10a940050b15b935a856c383c62c12c04f`) được nêu trong S1/S2/S4/S6; **không được tái kiểm bằng byte gốc trong lượt này**. Tình trạng AI độc lập chỉ tự khai báo, không xác minh identity/ACL/custodian.

## 2. Ma trận phản biện R1–R6

| Trục / Amendment | Verdict thiết kế | Risk cao nhất | Vấn đề quyết định | Must-fix trước khi chấp nhận V3 |
|---|---|---|---|---|
| **R1 / AM01** | **HOLD** | **CRITICAL** | Strong labeled bisimulation đang dùng quá nhiều nhãn quan sát; khác nhãn guard/priority/event không nhất thiết là mới lạ *liên quan đến nhiệm vụ*, nên có nguy cơ `false OOD`. Ý nghĩa determinism/observability chưa định nghĩa đủ để làm proof. | Định nghĩa phép chiếu hành vi liên quan đến đáp án (task-relevant observable quotient), quy tắc handling nội bộ/inert transitions và fixture cùng policy nhưng khác trace; khóa chứng cứ OOD có ý nghĩa, không chỉ non-isomorphic/non-bisimilar |
| **R2 / AM02** | **HOLD** | **CRITICAL** | `action_record` có `time_id` nhưng grammar `AGENT VERB TARGET (QUALIFIER)?` không chứa TIME minh định; `wrong_time` là lỗi reject: surface→tuple có thể không đơn trị. Cùng với policy từ chối paraphrase có thể đo compliance định dạng thay vì prompt-following ngữ nghĩa. | Grammar/time serialization hoặc chứng minh time suy được duy nhất; khóa canonical mapping, chấp nhận/reject đối với paraphrase và ngưỡng sensitivity/specificity độc lập trước EVAL |
| **R3 / AM03** | **PASS** (source-math only) | **HIGH, điều kiện tương lai** | Signed integer và kiểm định dấu đã nhất quán; giới hạn suy luận fixed 16 skeleton được nêu. Seed stream độc lập về thực nghiệm vẫn **NOT_VERIFIED**, không được suy rộng ra cấu trúc mới. | Giữ exact test, chứng minh root/stream derivation, xác định nguồn ngẫu nhiên thực sự thay đổi trajectory; report seed-level checks và luôn fail-closed khi thiếu seed (future preexec) |
| **R4 / AM04** | **PASS** (decision arithmetic only) | **MEDIUM** | Ngưỡng integer chính xác, pilot-informed được công khai. 3/4 category có cải thiện vẫn có thể bị một skeleton dễ thống trị; không thể diễn giải `uniform` hay mọi skeleton đều tốt hơn. | Khóa bảng reporting theo skeleton/category; giữ diagnostic không thành ngưỡng hậu nghiệm; chỉ dùng nhãn fixed-skeleton seed-directional, không gọi uniform across structures |
| **R5 / AM05** | **HOLD** | **CRITICAL** | `EVAL_AST_ONLY` không mặc nhiên không chứa gold. Typed AST khai báo goal, canonical action và transition semantics; auditor đủ thông tin để so đầy đủ rất có thể nhìn được cấu trúc xác định đáp án. Ranh giới leakage/trust chưa nhất quán. | Minh định trusted auditor có thể xử lý dữ liệu answer-determining nhưng không được phát tán; hoặc chứng minh phép chiếu được redaction vẫn đủ cho kiểm nonoverlap. Thiết kế threat model, ACL, key custody, receipt và noninterference tests |
| **R6 / AM06** | **HOLD** | **HIGH** | C dùng negative examples/extra forward và có thể nhận thêm tín hiệu giám sát so với B; dù `same TRAIN bytes` và `same updates`, đây **không đơn thuần là objective-only effect**. Chưa chốt negative construction, loss, LR và tính khả thi 36 Free-T4 arm-runs. | Đổi diễn giải thành hiệu ứng **objective + contrastive supervision/compute** hoặc bổ sung đối chứng matching exposure; khóa toàn bộ sampler/loss trước khoa học; yêu cầu one-packet resume/resource QA |

**Điểm phân biệt:** `AST_REAL_CHECKER`, `PARSER_RUNTIME_QA`, `ACL_ACTUAL`, `ADAMW_RESUME_QA`, `T4_FEASIBILITY` vẫn `NOT_EXECUTED/NOT_VERIFIED` theo đúng design-only scope. Chỉ riêng việc chưa code không buộc design HOLD; phán quyết HOLD ở đây do các **mâu thuẫn và bất định trong chính hợp đồng thiết kế**, phải xử lý trước khi mã hóa protocol.

## 3. Rà soát đủ 11 issue gốc

Các vị trí dưới đây trỏ đến [S2 JSON tại frozen HEAD](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_D1V2_01_11_DESIGN_HOLD_20261114.json). Trạng thái chỉ nói về **mức đủ chặt của design**, không chứng nhận runtime.

| Issue | AM | Status | Severity | Exact frozen source pointer | Must-fix / điều kiện đóng issue |
|---|---|---|---|---|---|
| `D1V2-01` | AM01 | **HOLD** | CRITICAL | `S2.AM01_structural_OOD.equivalence_algorithm.stage3–stage5` | Phân biệt observable decision semantics với khác biệt nhãn nội bộ; đặc tả checker và witness nhất quán |
| `D1V2-02` | AM01 | **HOLD** | HIGH | `S2.AM01_structural_OOD.split` | Định nghĩa criterion novelty/task relevance, scope TRAIN/VAL–EVAL, kiểm alpha-renaming, không cherry-pick |
| `D1V2-03` | AM02 | **HOLD** | CRITICAL | `S2.AM02_parser_oracle.ontology.action_record; output_surface_contract.grammar_ebnf` | Đồng bộ `time_id` với output, freeze unambiguous grammar & surface→typed action |
| `D1V2-04` | AM02 | **HOLD** | HIGH | `S2.AM02_parser_oracle.ontology.gold_proof_requirement; minimum_QA_preexec` | Chứng minh gold A/B unique, bảo toàn witness kín, prelock parser validation metric, no oracle leak |
| `D1V2-05` | AM03 | **PASS** | HIGH (historical) | `S2.AM03_statistics.D_s_definition; seed_positive; seed_tie; exact_sign_test` | Đã sửa strict integer tie; kiểm runtime equivalence sau này là gate khác |
| `D1V2-06` | AM03 | **PASS** (scoped) | HIGH | `S2.AM03_statistics.independence; hypothesis; crossed_bootstrap_exploratory` | Thiết kế inference đúng fixed-skeleton; vẫn phải chứng minh stochastic seed traces ở preexec |
| `D1V2-07` | AM04 | **PASS** (scoped) | MEDIUM | `S2.AM04_category_and_conflicts.integer_gates; skeleton_diagnostics_no_new_hidden_threshold` | Ngưỡng integer đúng; bắt buộc disclosure shortcut/heterogeneity, không claim uniform |
| `D1V2-08` | AM05 | **HOLD** | HIGH | `S2.AM05_custody_rights.roles; overlap_protocol.step1–step6` | Chứng minh AST projection không lộ đáp án **hoặc** chính thức coi auditor là trusted gold-adjacent processor với separation kỹ thuật |
| `D1V2-09` | AM05 | **HOLD** | HIGH | `S2.AM05_custody_rights.rights; anti_leakage_preexec; actual_acl` | Cụ thể hóa responsible custodian/key, legal provenance/PII, deny-probe và signed evidence |
| `D1V2-10` | AM06 | **HOLD** | HIGH | `S2.AM06_runner_resource.freeze_required_before_science; resume_QA` | Freeze loss/negative-sampler/FLOPs target, verify resume+bad checkpoint after implementation |
| `D1V2-11` | AM06 | **HOLD** | HIGH | `S2.AM06_runner_resource.T4_free_paid_cost_zero; all_arm_runs` | Định nghĩa trần thời gian và scope fallback tiền đăng ký; đo 3 arms trên Free T4 sau gate thích hợp |

## 4. Các phát hiện mới ngoài 11 issue

### `D1V3-N01` — CRITICAL — False structural OOD via observation labels

**Source:** [S1, AM01](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_PREREG_DESIGN_AND_OWNER_HOLD_20261114.md#L24-L34), S2 `AM01_structural_OOD.typed_AST.event_observable_label` và `equivalence_algorithm`. Hai máy có thể ra cùng action cho mọi state/condition nhưng khác event label, guard bookkeeping hoặc bước self-transition không ảnh hưởng nhiệm vụ; nếu tất cả là observable thì checker sẽ báo khác trace và đánh dấu OOD mới giả. Phép `strong bisimulation` đủ mạnh cho equivalence theo nhãn **đã chọn**, không tự chứng minh tính liên quan của nhãn với tác vụ.

**Must-fix:** Tiền đăng ký một danh sách observable labels có cơ sở task semantics, quy tắc tau/inert events hoặc tuyên bố rõ chỉ `trace-OOD` chứ không phải `decision-OOD`; fixture đối kháng “same decision policy, different irrelevant trace” phải **không** được gắn nhãn task-structural novelty. Nếu hệ thực sự deterministic total, phải định nghĩa input/action alphabet và chứng minh điều đó thay vì dựa vào diễn giải tự do. Không kết luận chung rằng non-bisimilar luôn có distinct trace nếu có branching nondeterministic.

### `D1V3-N02` — CRITICAL — Grammar và trường thời gian bất nhất

**Source:** [S2 AM02, ontology và grammar](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_D1V2_01_11_DESIGN_HOLD_20261114.json#L207-L281). `time_id` xuất hiện trong typed canonical action, trong khi EBNF không có `TIME`. Nếu hai action khác thời gian nhưng chung surface `AGENT VERB TARGET`, parser không thể ánh xạ đơn trị bằng output. Việc dùng gold/prompt để lấp time có thể biến scorer thành oracle bổ sung thay vì đo model output.

**Must-fix:** Quyết định rõ whether time is scored/output-visible; hoặc thêm vị trí `TIME` và fixtures, hoặc bỏ time khỏi scored tuple với rationale; chứng minh injective surface→scored canonical tuple cho các action được phép. Chốt chính sách paraphrase, confidence-free exact parser và ngưỡng độc lập về false positive/negative.

### `D1V3-N03` — CRITICAL — AST-only projection vẫn có thể chứa gold

**Source:** [S2 AM05](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_D1V2_01_11_DESIGN_HOLD_20261114.json#L417-L510). AST được mô tả chứa goal/canonical action và transitions; đủ ngữ nghĩa để chứng minh nonoverlap thường đủ để suy ra action/gold hoặc condition labels. `DENY EVAL_GOLD` không phải đảm bảo bí mật gold nếu `EVAL_AST` có thông tin tương đương. Ngoài ra receipt `PASS/FAIL/UNKNOWN` có thể là channel tiết lộ thông tin trong các lần probe chọn lọc.

**Must-fix:** Coi auditor là một **trusted enclave/party chịu quyền gold-adjacent** (không gọi AST là không tiết lộ) hoặc thiết kế phép kiểm đủ thông tin mà không lộ đáp án; chỉ một lần sealed audit trên batch frozen, chống adaptive queries; return minimal receipt với binding của inputs/checker phiên bản, evidence riêng và deny-probe. Không cần thực tế truy cập private data trong lượt này.

### `D1V3-N04` — HIGH — Objective-only attribution bị nhiễu bởi negative-supervision budget

**Source:** [S1 AM06](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_PREREG_DESIGN_AND_OWNER_HOLD_20261114.md#L92-L100); S2 `scientific_question` và `AM06_runner_resource`. C khác B vừa ở loss, vừa ở việc sử dụng contrastive negatives và số forward passes. Cùng byte TRAIN không đảm bảo cùng **effective supervised information** nếu C nhìn negative labels/tuples mà B không có. Mức causal attribution phải tương ứng gói can thiệp thực tế.

**Must-fix:** Định nghĩa contrast C như *contrastive training package* (objective + negative supervision/compute), hoặc bổ sung một control exposure-matched để kiểm định objective-only; không sửa primary hypothesis sau outcome. Freeze negative provenance (TRAIN-only), label construction, pairs, coefficient, seed streams, scheduler.

### `D1V3-N05` — HIGH — Seed p-value cần mô hình lặp lại có biến thiên thật

**Source:** S2 `AM03_statistics.independence`, `hypothesis`, `exact_sign_test`. 12 số seed khác nhau không chứng minh 12 run có biến thiên huấn luyện độc lập. Shared fixed evaluation task **không tự làm hỏng** suy luận *conditional* theo seed nếu stream độc lập, nhưng training deterministic giống hệt nhau dù đổi seed sẽ phá ý nghĩa p-value. Với same parent/corpus, inference phải giới hạn đúng nguồn randomness được ngẫu nhiên hóa.

**Must-fix:** Chốt seed→PRNG derivation/stream namespaces, train shuffle, dropout/augmentation/negative sampling stochasticity; preexec có trace/hash kiểm khác nhau ở intended source và reproducible khi cùng seed, không tuyên bố iid đã được chứng minh chỉ nhờ số seed. Nếu randomness population mơ hồ, giữ thống kê mô tả thay vì confirmatory p-value.

### `D1V3-N06` — MEDIUM — Same-author mutation suite không xác nhận semantic checks

**Source:** [S3 QA source](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/tools/pilot_t4/fc01/ttm_d1_bridge_v3_source_only_contract_qa_20261114.js#L11-L93), [S4 receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/8f0714b29c98ca9be7c7444f964267faea4efb76/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_SINGLE_PACKET_SOURCE_ONLY_QA_AND_OWNER_HOLD_20261114.json). Các T01–T57 đọc field/chuỗi/giá trị của JSON và MD; 13 mutations chủ yếu đổi chính các field đó. Vì vậy kết quả scoped 57/57, 13/13 có giá trị kiểm **tính hiện diện và nhất quán hợp đồng**, không kiểm đúng sai của semantics, parser, gold security hay thông lượng T4.

**Must-fix:** Giữ `PASS_SCOPED_SAME_AUTHOR` không nâng thành chứng nhận độc lập; trong gói implementation sau thiết kế phải có executable independent positive/negative fixtures kiểm thực nghĩa.

## 5. Kiểm toán toán học độc lập (source-only)

- Đơn vị `success` là family đúng **cả hai** condition A và B. `D_s = Σ_{f=1}^{256}(success_C(s,f)−success_B(s,f))` là **số nguyên có dấu**, `d_s=D_s/256`. Seed dương iff `D_s>0`; `D_s=0` là nonpositive, không dùng epsilon.
- Exact one-sided sign test `H0: P_seed(D_s>0)≤.5` với `n=12` độc lập lý tưởng: tại `k=9`, `p=299/4096=.072998046875`; `k=10`, `p=79/4096=.019287109375`; `k=11`, `p=13/4096=.003173828125`; `k=12`, `p=1/4096=.000244140625`. **Chỉ k≥10 qua alpha=.05**.
- Power riêng sign-gate với q=.7/.8/.9 (Bernoulli iid giả định): **25.2815348% / 55.8345748% / 88.9130022%**. Tất cả gate kết hợp có power không cao hơn sign-gate. Đây không phải empirical power.
- Global threshold: `ceil(12×256×.10)=308`; category 5pp: `ceil(12×64×.05)=39`; C absolute 25% trên mỗi category: `12×64×.25=192`. Số học **đúng**. 3/4 categories vượt +5pp và 4/4 không âm **không chứng minh** lợi ích đồng đều trên 16 skeleton.
- 12 seed × 3 arm × 256 updates = **9216 updates**; 12 seed × 3 arm × 256 family × 2 condition = **18432 generated outputs**. Kế hoạch này **không** là bằng chứng Free T4 khả thi.
- One-sided test chỉ bác bỏ null về **xác suất seed cho cải thiện dương trong fixed skeleton design**; không kiểm mean effect ≥10pp, không suy rộng general OOD, không đánh giá ``unseen relative to all pretraining``. Crossed bootstrap chỉ mang tính mô tả/độ nhạy.

## 6. Phán quyết và biện pháp duy nhất

### Verdict: `HOLD_REVISE_BEFORE_PREREG`

**Lý do:** AM01 chưa khóa điều gì là khác biệt *liên quan đến tác vụ*; AM02 có mâu thuẫn trực tiếp giữa `time_id` và EBNF; AM05 chưa giải quyết rò rỉ cấu trúc quyết định đáp án qua `EVAL_AST`; AM06 chưa thống nhất causal estimand khi thêm negatives/compute cho C. Các điểm này cần sửa ở **mức thiết kế**, không thể đơn thuần giao cho người triển khai parser/checker tự chọn.

**Không kết luận `FAIL_INVALID_DESIGN`**, vì có phương án sửa nhất quán qua một V4 prospective amendment. **Không kết luận `HOLD_SOURCE_UNAVAILABLE`**, vì 7/7 nguồn được đọc, Git blob SHA-1 khớp. **Không cấp `GO_DESIGN_ONLY`** cho V3 hiện tại.

**Trạng thái bảo toàn:** `D1_BRIDGE_SCIENCE=HOLD`; `D1_EXISTING=HOLD_UNMODIFIED`; `TEST_Q1Q2=SEALED`; `FC01_EXPLORATORY=CLOSED_PASS_SCOPED`; `FC02=NOT_OPENED`; `GPU=NO`; `TRAINING=NO`; `INFERENCE=NO`; `MAIN=UNCHANGED`; `V1/V2/V3=IMMUTABLE`; `RIGHTS=NOT_VERIFIED`; `PRIVATE_GOLD_ACCESS=FALSE`.

**Bước thực hiện tiếp theo duy nhất:**

`TTM_SMALL4M_D1_BRIDGE_V4_SINGLE_PACKET_TASK_RELEVANT_OOD_PARSER_AUDITOR_AND_CONTRAST_CONTROL_PREREG_SOURCE_AMENDMENT_NO_GPU`

Tạo **một** V4 source-contract amendment giải quyết đồng thời N01–N05, giữ ngưỡng/thống kê V3 đúng đã khóa, lập fixtures synthetic đối kháng ở mức thiết kế; sau đó mới giao reviewer riêng đọc frozen V4 để đưa **một** GO/HOLD design. Không sinh EVAL/gold, không chạy GPU/training/inference, không mở TEST hay micro-permits. Gói này chỉ có thể được xem xét cho implementation/source QA sau GO thiết kế độc lập; các preexec execution gates vẫn ở HOLD cho đến khi kiểm chứng thực tế.

**Reviewer self-attestation:** Tôi đã đọc bằng GitHub connector, không chạy mã JS V3 hoặc science runner, không truy cập EVAL/gold, không tự nhận human review, không tự nhận quyền truy cập dữ liệu/custodian, không tự nhận xác minh cryptographic byte custody độc lập. Các phép toán trong mục 5 được tính lại độc lập bằng arithmetic; các QA khác là phân tích tĩnh/logic từ nguồn. Không ghi hoặc commit GitHub trong lượt này.
