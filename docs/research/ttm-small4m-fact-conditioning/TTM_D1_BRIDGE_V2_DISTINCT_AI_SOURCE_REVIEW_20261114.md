# TTM D1 Bridge V2 — Distinct Independent AI Source-Only Scientific Design Review

**Ngày:** 2026-11-14  
**Operation:** `TTM_SMALL4M_D1_BRIDGE_V2_DISTINCT_AI_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU`  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Frozen V2 source HEAD:** `750533c1c2945594d827c886aaa275c49fb980d7`  
**Handoff HEAD:** `47d26d018098687628af30e2fcfdd92ad7391ae1`  
**Vai trò:** `INDEPENDENT_NEW_CHAT_AI_SELF_ATTESTED_NOT_HUMAN_NOT_EXTERNALLY_VERIFIED`.  
**Chế độ:** `READ_ONLY / SOURCE_ONLY / DESIGN_ONLY / NO_GPU / NO_TRAIN / NO_INFERENCE / NO_EVAL_GOLD / NO_PRIVATE_MAPPING`.  
**Một quyết định thiết kế:** **`HOLD_REVISE_BEFORE_PREREG`**.  
**Bất biến:** **`D1_SCIENCE_RELEASE=HOLD`**, `D1_EXISTING=HOLD_UNMODIFIED`, `TEST_Q1Q2=SEALED`, `FC01=CLOSED_PASS_SCOPED`, `MAIN=UNCHANGED`.

## 1. Nguồn và giới hạn xác minh

Đọc đúng 7/7 tệp nguồn được handoff chỉ định theo pinned HEAD; so SHA-1 của Git blob do GitHub connector trả về với pin trong handoff. Tất cả 7/7 khớp. Đọc thêm V1 protocol + V1 JSON tại frozen V1 HEAD `25a19daea9f664e14f83d7df2cf8265ffaea4ecd` và cũng đối chiếu hai SHA-1 theo báo cáo V1. Không tạo bản tải local để recompute Git object hash; không tự nhận byte custody độc lập/second channel hoặc xác minh danh tính tác giả/custodian.

| Ref | Nguồn tại V2 pinned HEAD | Git blob SHA-1 | Kết quả |
|---|---|---|---|
| S1 | [TTM_D1_BRIDGE_V2_SINGLE_PACKET_AM01_AM06_PREREG_DESIGN_AND_OWNER_HOLD_20261114.md](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_SINGLE_PACKET_AM01_AM06_PREREG_DESIGN_AND_OWNER_HOLD_20261114.md) | `354291ec54803bd9764728ee858abd83a71ca4b6` | `PASS_GITHUB_BLOB_METADATA` |
| S2 | [TTM_D1_BRIDGE_V2_AM01_AM06_SINGLE_PACKET_PREREG_DESIGN_HOLD_20261114.json](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_AM01_AM06_SINGLE_PACKET_PREREG_DESIGN_HOLD_20261114.json) | `66ce607eb13e4c64994fecd4a40a2c3da94d19dc` | `PASS_GITHUB_BLOB_METADATA` |
| S3 | [ttm_d1_bridge_v2_source_only_contract_qa_20261114.js](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/tools/pilot_t4/fc01/ttm_d1_bridge_v2_source_only_contract_qa_20261114.js) | `7ee503f19613899ecd9bbe788dd995ad10415575` | `PASS_GITHUB_BLOB_METADATA` |
| S4 | [TTM_D1_BRIDGE_V2_SINGLE_PACKET_SOURCE_ONLY_QA_AND_HOLD_20261114.json](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_SINGLE_PACKET_SOURCE_ONLY_QA_AND_HOLD_20261114.json) | `2f468a743b3e44ef5d307810b70ab74000ce0a61` | `PASS_GITHUB_BLOB_METADATA` |
| S5 | [TTM_D1_BRIDGE_V1_INDEPENDENT_PREREG_REVIEW_20261114.md](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V1_INDEPENDENT_PREREG_REVIEW_20261114.md) | `8fd942d60e79e5b78cc342505d92a4dbcaefc540` | `PASS_GITHUB_BLOB_METADATA` |
| S6 | [TTM_D1_BRIDGE_V1_INDEPENDENT_REVIEW_RECEIPT_20261114.json](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V1_INDEPENDENT_REVIEW_RECEIPT_20261114.json) | `580e7269f66e900b8fe40584fd73d5ce0f001566` | `PASS_GITHUB_BLOB_METADATA` |
| S7 | [lineage.md](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/lineage.md) | `34a59b7ee76bf6cab5a7abfcdf687a38a6dc3d7d` | `PASS_GITHUB_BLOB_METADATA` |

**Tính độc lập:** phiên ChatGPT mới là independent AI review ở mức phương pháp luận/tài liệu, không phải independently executed source suite hoặc human scientific audit. QA 44/44 + 9/9 do cùng tác giả V2 tự soạn được xem là bằng chứng kiểm tra contract, **không** được dùng để nâng AST/parser/rights/compute sang PASS. Không truy xuất EVAL/gold hoặc private mapping.

## 2. Đánh giá AM01–AM06 (verdict thuộc thiết kế V2)

| Amendment | Verdict | Highest risk | Issue IDs | Evidence | Kết luận |
|---|---|---|---|---|---|
| AM01/R1 | **HOLD** | **CRITICAL** | D1V2-01, D1V2-02 | S1, S2, S3, S4, S5 | AST equivalence/structural OOD chưa khả kiểm |
| AM02/R2 | **HOLD** | **CRITICAL** | D1V2-03, D1V2-04 | S1, S2, S3, S4, S5 | Parser/oracle chưa có mã và tính hợp lệ thực |
| AM03/R3 | **HOLD** | **HIGH** | D1V2-05, D1V2-06 | S1, S2, S3, S4, S5, S6 | Exact test đúng, tie-policy và independent inference chưa khóa |
| AM04/R4 | **HOLD** | **MEDIUM** | D1V2-07 | S1, S2, S3, S5 | Guards có nguồn nhưng boundary/heterogeneity chưa khóa |
| AM05/R5 | **HOLD** | **HIGH** | D1V2-08, D1V2-09 | S1, S2, S4, S5, S7 | ACL không đủ luồng độc lập để proof overlap |
| AM06/R6 | **HOLD** | **HIGH** | D1V2-10, D1V2-11 | S1, S2, S4, S5, S7 | Nonzero-moment resume và Free T4 chưa chứng minh |

### Phát hiện và must-fix

#### AM01 / R1: HOLD — CRITICAL (D1V2-01, D1V2-02)

**Bằng chứng:** S1, S2, S3, S4, S5; **tương ứng V1:** F01, F02.

**Nhận định:** Công thức tương đương trong AM01 coi hành động cuối trên trạng thái hữu hạn + goal constraints là tiêu chuẩn chính; không đảm bảo tương đương tiến trình chuyển trạng thái, điều kiện ưu tiên/nhân quả/temporal. Nếu checker chỉ so bảng hành động, hai cơ chế khác nhau có cùng outcome có thể bị gộp (loại nhầm OOD); nếu miền trạng thái không đầy đủ, khác biệt chỉ ở trạng thái bất khả đạt lại có thể được chấp nhận là mới. 4 OOD skeleton/category chưa hiện hữu; actual non-overlap là NOT_EXECUTED.

**Must-fix (nếu sửa → V3):** Trong V3 định nghĩa một bộ quyết định nhất quán giữa MD và JSON: chuẩn hóa typed AST có trace/transition semantics, reachable-state coverage, counterexample/bisimulation hoặc quy tắc conservative UNKNOWN→HOLD; đóng băng quy trình tạo 4 OOD structures/category và các kiểm exact, alpha-rename, negation, priority, temporal order, unreachable-state, near-equivalence trên fixture không thuộc EVAL. Không gọi PASS khi chưa có checker độc lập.

#### AM02 / R2: HOLD — CRITICAL (D1V2-03, D1V2-04)

**Bằng chứng:** S1, S2, S3, S4, S5; **tương ứng V1:** F03, F04.

**Nhận định:** Action ontology đã có fields nhưng chưa định nghĩa grammar chạy được, mapping surface→canonical, grammar cho condition_witness (bắt buộc có trong output hay suy từ prompt), hoặc policy phân xử quote/negation/2 clauses/early EOS cụ thể. So sánh gold_A != gold_B theo canonical là đúng hướng nhưng chưa chứng minh tính duy nhất/khả phân biệt của từng world. Không có parser code hay sensitivity/specificity từ independent fixtures.

**Must-fix (nếu sửa → V3):** Trong V3 pin ontology/action grammar và synonym SHA, tách semantic witness của gold khỏi biểu thức output nếu câu trả lời chỉ có 1 action; xác định output contract và unique-oracle proof trước EVAL. Parser deterministic với fixture nguồn-only đối kháng: quoted answer, negation, inverse condition, wrong agent/target/time, multi-action/contradiction, echo, EOS/truncation và special tokens. Giữ invalid→0, 256 family denominator.

#### AM03 / R3: HOLD — HIGH (D1V2-05, D1V2-06)

**Bằng chứng:** S1, S2, S3, S4, S5, S6; **tương ứng V1:** F05, F06.

**Nhận định:** Xác minh độc lập exact sign k≥10/12 và các power ví dụ là đúng. Nhưng JSON AM04.tie_boundary ghi đồng thời "inclusive_ge_for_positive_d" và "strict_positive_d>0", xung đột với AM03 zero=NONPOSITIVE; chưa khóa ước lượng error/tolerance. 12 seed numeric khác nhau chưa chứng minh iid training streams; kiểm định nhắm P_seed(d_s>0), không nhắm mean>0 hoặc mean≥0.10. Crossed bootstrap có thể là sensitivity nhưng không cung cấp CI xác nhận tổng thể 16 skeleton.

**Must-fix (nếu sửa → V3):** Trong V3 bỏ xung đột tie policy bằng signed integer D_s=#paired_correct_C−#paired_correct_B trên 256 family, d_s=D_s/256; D_s=0 là nonpositive, không cần epsilon. Pin RNG stream/sampler/negative sampler, độc lập thống kê và cùng test set. Công khai sign test đơn biến (k≥10), power q=.7/.8/.9, giới hạn suy luận chỉ fixed skeleton, bootstrap exploratory ghi nhãn riêng; +0.10 là descriptive composite decision gate.

#### AM04 / R4: HOLD — MEDIUM (D1V2-07)

**Bằng chứng:** S1, S2, S3, S5; **tương ứng V1:** F07.

**Nhận định:** Thứ tự HOLD_INVALID_PROTOCOL trước outcome đúng và ngưỡng được khai là FC01-pilot-informed. Tuy vậy numeric thresholds chưa khóa biểu diễn integer/boundary, không có phương án kiểm tra shortcut/heterogeneity giữa 4 skeleton/category; 16 lexical worlds tạo cảm giác ổn định giả nếu cùng một skeleton dễ.

**Must-fix (nếu sửa → V3):** Trong V3 chốt phân xử ranh giới bằng đếm nguyên: mean≥.10 trên 12 seed ↔ Σ_s D_s≥308; category mean≥.05 trên 12×64 family ↔ Δcount_category≥39; C absolute≥.25 ↔ correct_C_category≥192. Khóa bảng tình huống conflict và các robustness controls theo skeleton/lexical cue trước outcome; không báo những guards này là hypothesis tests.

#### AM05 / R5: HOLD — HIGH (D1V2-08, D1V2-09)

**Bằng chứng:** S1, S2, S4, S5, S7; **tương ứng V1:** F08, F09.

**Nhận định:** ACL mới chỉ nêu role; chưa có chứng cứ permission/key. Đáng chú ý, owner_trainer chỉ được đọc TRAIN/VAL còn eval_custodian chỉ được đọc sealed EVAL; parser_source_qa chỉ xem synthetic. Không role được mô tả có quyền đủ để so sánh actual TRAIN/VAL AST với EVAL AST, nên proof non-overlap chưa có luồng kiểm toán khả thi và không lộ gold. Rights/PII, parent/TinyStories/template leak vẫn unverified.

**Must-fix (nếu sửa → V3):** Trong V3 định nghĩa trusted isolated overlap auditor hoặc sealed two-party protocol nhận AST không kèm gold, xác minh TRAIN–EVAL + VAL–EVAL và chỉ xuất signed pass/fail+hash (không tiết lộ mapping); pin storage ACL, key-owner, audit logs và env mount proof; kiểm cue swaps/template/gold-echo, receipts license/provenance/PII. Không tuyên bố OOD đối với toàn bộ pretraining.

#### AM06 / R6: HOLD — HIGH (D1V2-10, D1V2-11)

**Bằng chứng:** S1, S2, S4, S5, S7; **tương ứng V1:** F10, F11, F12.

**Nhận định:** Nguồn đã thừa nhận equal data/token/updates không bằng equal FLOPs/negative exposures. Tuy nhiên vẫn chưa có exact T1/parent SHA trong V2 machine, deterministic negative sampling contract, checkpoint resume actual nonzero AdamW QA hoặc đo throughput/storage/quota Free T4 để chạy 36 arm-runs. 44/44 tự kiểm chỉ test chuỗi JSON/arithmetics, không test runner.

**Must-fix (nếu sửa → V3):** Trong V3 pin exact parent/T1/artifact SHA và nguồn contrastive negatives; freeze loss coefficients and RNG per arm; yêu cầu one-packet actual nonzero AdamW K vs K-resume equivalence và negative corrupt/wrong SHA/partial restore fail-closed; profile cả 3 arm (RAM/vRAM/disk, elapsed, FLOPs, quota, Drive I/O, restart) để quyết định paid USD 0 khả thi; nếu không thì HOLD hoặc scoped pilot theo amendment mới trước outcome.

## 3. Kiểm chứng toán học nguồn-only, không dùng FC01/D1 outcomes

Với 4 category × 64 family, `success_B,s,f, success_C,s,f ∈ {0,1}`. Đặt **`D_s=∑_{f=1}^{256}(success_C,s,f-success_B,s,f)`** là số nguyên có dấu; **`d_s=D_s/256`**, nên `D_s=0` là tie chính xác; `D_s>0` mới là seed dương. Tính toán này tránh hoàn toàn epsilon đối với primary sign test, vì category weighted đều 64 family.

- `H0: P_random_training_seed(D_s>0) ≤ 1/2` so với `H1: > 1/2`, có điều kiện trên 16 fixed structural skeleton; **không** kiểm định mean effect >0 hay ≥+.10.
- Với 12 seed và null Bernoulli iid bảo thủ, `p(k)=∑_{j=k}^{12} C(12,j)/4096`. Kiểm tra độc lập:

| k dương/12 | Exact p | Qua alpha=.05? |
|---|---:|---|
| 9 | 299/4096 = 0.072998046875 | Không |
| 10 | 79/4096 = 0.019287109375 | Có |
| 11 | 13/4096 = 0.003173828125 | Có |
| 12 | 1/4096 = 0.000244140625 | Có |

- Với `q=P_seed(D_s>0)` và giả định 12 Bernoulli độc lập, power **chỉ của sign component** `P(K≥10)`: q=.7 → 25.2815%; q=.8 → 55.8346%; q=.9 → 88.9130%. Power của conjunction với magnitude, categories, integrity và resources **không lớn hơn** các số này. Đây là sensitivity minh họa, không ước lượng từ FC01.
- Gate `mean_s(d_s)≥0.10` ⇔ `∑_{s=1}^{12} D_s ≥308` (vì 12×256×.10=307.2). `category mean Δ≥0.05` ⇔ signed net count trên 12×64 ≥39. `C category absolute≥.25` ⇔ ≥192 successes/768 per category. Các quy đổi là số học của planned denominators, chưa có dữ liệu thực.
- Khóa chính xác tie/p-value trong machine schema, do `AM04.tie_boundary` đang dùng cả `inclusive_ge_for_positive_d` và `strict_positive_d>0`. Hợp lệ duy nhất: **strict D_s>0**, zero nonpositive. Có thể giữ ≥ cho magnitude/category guards.
- Crossed bootstrap seed/skeleton/family là sensitivity mô tả. Resampling skeleton dù chỉ 4/category không tạo cơ sở để suy rộng OOD ngoài 16 cấu trúc cố định. Nếu estimand điều kiện trên 16 skeleton, không diễn giải bootstrap skeleton như CI xác nhận mean effect của một population OOD.

## 4. Các fixture nguồn-only đề nghị trước khi triển khai (không sử dụng EVAL)

1. **AST alpha-rename:** đổi tên tác tử/biến cùng loại nhưng giữ toàn bộ quan hệ → phát hiện equivalence, reject OOD.
2. **AST priority/temporal:** đảo ưu tiên hoặc thời điểm sao cho cùng final action trong vài trạng thái nhưng trace/điều kiện khác → phải đánh giá đủ reachable-state/trace, nếu bất quyết `UNKNOWN→HOLD`.
3. **AST impossible state:** tạo khác biệt chỉ trên trạng thái bất khả đạt → không coi là chứng minh cấu trúc mới có hành vi OOD.
4. **Gold canonical collision:** hai surface synonyms diễn giải cùng một canonical action tại A/B → reject family là không phân biệt phản thực.
5. **Parser negative:** output “Do not move the crate” trong khi gold là “move crate” → 0.
6. **Parser quoted:** output “She said ‘move the crate’, but did not move it” → 0.
7. **Parser multi-action:** output có một hành động đúng và một hành động sai → 0.
8. **Parser boundary:** EOS rỗng, truncation, BOS/EOS special tokens và đủ 224+32 tokens bằng tokenizer T1 thật → quyết định rõ ràng, không cứu output.
9. **Custody/ACL:** thử một audit path có thể đối chiếu TRAIN–EVAL AST mà không để owner xem EVAL raw/gold; log deny khi owner cố đọc forbidden store.
10. **Resume:** sau ít nhất một update có nonzero AdamW moments, đối chiếu uninterrupted và resumed; corrupt checkpoint/wrong SHA phải fail-closed.

Các fixture này chỉ là đề xuất kiểm thử âm/tích cực ở mức thiết kế; **chưa thực thi**, chưa có kết quả sensitivity/specificity và không tạo EVAL/gold.

## 5. Kiểm toán source-only QA 44/44 và 9/9 negatives

Đọc tĩnh mã JS [S3], receipt [S4]. T01–T44 là các khẳng định về fields/chuỗi/giá trị của JSON và sự hiện diện của tên AM01–AM06 trong Markdown, không gọi AST generator, equivalence checker, parser hay runtime resume. Ví dụ: T16 chỉ kiểm `224+32=256` và cờ `special_token_count_must_be_included`; T18/T19 kiểm số seed/đầu-cuối; T24 chỉ kiểm power q=.8; T26 chỉ kiểm chuỗi hướng dẫn bootstrap; T35 kiểm tên nonzero moments và trạng thái NOT_EXECUTED. 9 negative mutations đều chỉ thay **JSON in-memory** để thử checker nội bộ; không đo false acceptance/false rejection của parser/AST. Receipt [S4] còn ghi execution same-author cùng hàm trong V8, không phải independent Node CLI. Vì vậy chỉ công nhận **`SELF_AUTHORED_SPEC_CONSISTENCY=PASS_SCOPED_REPORTED`**; độc lập xác minh cấu trúc/test thực vẫn `NOT_EXECUTED`.

## 6. Kết luận tích hợp và ranh giới

**Một design verdict:** `HOLD_REVISE_BEFORE_PREREG` — không phải `FAIL_INVALID_DESIGN`: câu hỏi C vs B có thể kiểm nghiệm và V2 sửa đúng nhiều lỗi V1, nhưng contract còn xung đột/thiếu luồng kiểm chứng để đưa ra GO thiết kế xác nhận. **Tất cả sửa đổi nội dung phải là V3; không overwrite V1/V2.** Không cấp quyền science/GPU. Không coi 44/44 tự QA là chứng minh AST/parser hoặc statistical validity.

| Gate | Trạng thái review |
|---|---|
| V2 pinned GitHub source metadata | `PASS_7_OF_7_GITHUB_BLOB_SHA1` |
| Independent source reasoning / math | `COMPLETE_SCOPED_AI_REVIEW` |
| V2 design freeze | `HOLD_REVISE_BEFORE_PREREG` |
| AST_NONOVERLAP | `NOT_EXECUTED` |
| PARSER_RUNTIME_QA | `NOT_EXECUTED` |
| STATISTICAL_ASSUMPTIONS | `HOLD` |
| ACL_ACTUAL, RIGHTS_ACTUAL | `NOT_VERIFIED` |
| NONZERO_ADAMW_RESUME_QA | `NOT_EXECUTED` |
| FREE_T4_FEASIBILITY | `NOT_VERIFIED` |
| D1_SCIENCE_RELEASE | `HOLD` |
| TEST_Q1Q2 | `SEALED` |
| GPU/TRAIN/EVAL access by reviewer | `NONE` |

## Bước thực hiện tiếp theo (duy nhất)

`TTM_SMALL4M_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_REMEDIATION_AND_SINGLE_INDEPENDENT_PREREG_REVIEW_NO_GPU`

Owner tạo **một V3 source-only packet** xử lý đồng thời D1V2-01…D1V2-11: AST reachable-state/trace, parser grammar/oracle, strict integer sign + exact thresholds, audit custody khả thi, và nguồn runner/resource/resume. Chạy một lượt kiểm tra độc lập source/design sau khi đóng băng V3; đưa đúng một GO/HOLD thiết kế. Không micro-permit; giữ D1 khoa học HOLD, TEST sealed, không tạo TRAIN/EVAL/gold, không train hoặc cấp GPU trong lượt này.
