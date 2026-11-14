# TTM-Small-4M D1 Bridge R1 — Minimal semantic contract và bounded constructive feasibility

**Operation:** `TTM_SMALL4M_D1_R1_MINIMAL_SEMANTIC_CONTRACT_FREEZE_AND_CONSTRUCTIVE_FOUR_CATEGORY_FEASIBILITY_SINGLE_REVIEW_GATE`  
**Input evidence:** GitHub exact commit `d24c50ad8a9e377264dd8fa073bcc553824f8992`  
**Frozen science:** `dd52804685d186c17e600221ffb16ce78aea12ea`  
**Scope:** SOURCE-ONLY, không tạo EVAL/gold, không GPU/TRAIN/INFERENCE.  
**Single design adjudication:** **`HOLD_ONTOLOGY_FEASIBILITY`**.

## 1. Hợp đồng ngữ nghĩa đã được *freeze* ở phạm vi thử nghiệm nguồn

Đã tạo `TTM_D1_R1_PROSPECTIVE_MINIMAL_SEMANTIC_CONTRACT_FREEZE_20261114.json`: lựa chọn **physical co-located TRANSFER**, CARRY target có thể đang được holder giữ và lan truyền tọa độ của mọi item đang giữ, WAIT xử lý clock và event theo từng tick, RETAIN tăng protection và không ưu tiên horizon theo nhãn gold, T0 cho phép custody ban đầu theo initialization axioms và từ chối request ở T0. Shortest path theo số hành động tối đa 3 cho goal reachability; goal persistence đánh giá pure safety đến T2 và tất cả action một bước, không có cost/tie break tự phát.

**Đây là versioned candidate freeze để truy nguyên phép tìm kiếm, không phải phê duyệt sửa frozen V6.** Frozen V6 không có `TRANSFER` co-location, không có exogenous-request fluent trong AM01, `WAIT` chỉ ghi defer ở hợp đồng gốc, `CARRY` gốc yêu cầu target unheld. Các khác biệt là material amendments. Không thể dùng source QA mới để ký `V6_ACCEPTED`.

## 2. Tìm kiếm hữu hạn thực sự đã chạy

`constructive_search.py` dùng Python standard library và **không import generator/checker lịch sử**. Duyệt tích Descartes khai báo tường minh trong source, sinh toàn bộ world T0 hợp lệ trong từng subgrammar, áp dụng sáu transition, BFS giữ **mọi first action** cùng độ dài ngắn nhất (depth <=3, edge cap 3500); persistence dùng pure safety qua event. `pairwise_constructive_probe.py` xét cặp world cùng goal, khác đúng một typed state fluent và hành động đầu tiên thực sự khác.

| Category | World+goal thử | Unique first action | Cặp A/B một fluent, khác hành động | Motif proxy thô |
|---|---:|---:|---:|---:|
| entity_location | 96 | 20 | 2 | 1 |
| causal_reasoning | 54 | 16 | 1 | 1 |
| rule_constraint | 108 | 52 | 29 | 3 |
| goal_persistence | 72 | 6 | **0** | **0** |
| **TOTAL** | **330** | **94** | **32** | — |

12/12 phép kiểm **mới của chính engine nguồn** PASS (co-location, protection, held CARRY propagation, WAIT/clock, genesis, T0 request, RETAIN no-tiebreak). Không chạy lại historical 13/13 hoặc 12/12.

**Giới hạn có ý nghĩa:** Ở goal_persistence, sáu ca unique đều là một motif `RETAIN i0 T0 T2` khi request tại T2, target và người nhận cùng vị trí, và task đồng thời yêu cầu item giữ nguyên vị trí. Thay đổi holder i1 hay protection T0/T1 không tạo dependency topology mới. Các ca request tại T1 hoặc không có request tạo đa nghiệm do nhiều hành động bảo toàn safety. Không tìm được A/B counterfactual một fluent có unique **và** khác hành động trong subgrammar này.

Trong `causal_reasoning`, motif một-fluent hợp lệ duy nhất của search là đổi lịch WAIT, chưa phải action-causal structural OOD. Trong `rule_constraint`, ba motif chỉ là **proxy** sau bỏ nhãn role/time, không phải chứng minh độc lập 3 topology. Nhiều unique world không chứng minh có bốn OOD mới.

**Không suy diễn kết quả tìm kiếm thành định lý bất khả thi toàn bộ ontology**: fixed role names, goal forms, chỉ một external request, time T0–T2, depth≤3 và các lựa chọn domain cụ thể. Không duyệt tất cả goal/horizon/causal transition graph khả dĩ trong V6.

## 3. Tình trạng 16 TRAIN + 16 OOD và 64-pair admission

**0** new science-admissible TRAIN, **0** new science-admissible OOD. `TTM_D1_R1_32_CONSTRUCTIVE_ADMISSION_MATRIX_20261114.json` giữ đủ 32 slot ở `HOLD_NOT_PROVEN`. Không tạo thêm blueprint tô nhãn TRAIN/OOD từ kết quả subgrammar chỉ để cho đủ 4+4/category. **64 cặp chứng nhận nonoverlap mới: `NOT_EXECUTED_NO_32_ADMITTED_INPUTS`.** 64 cặp nguồn cũ ở commit `d24c50ad...` vẫn là negative controls: 5 direct và 9 swapped exact worlds, 55/64 coarse proxy trùng, không chứng minh novelty dương. Không cộng các proxy.

Các ca illustrative có nguồn và oracle trong receipt `TTM_D1_R1_BOUNDED_CONSTRUCTIVE_SEARCH_RECEIPT_20261114.json` **không** được coi là skeleton scientific-admissible hoặc gold.

## 4. Source shortcut, renderer/parser và EVAL custody

Renderer production, parser T1, tokenizer SHA và grammar test 64+/64− **chưa thực hiện** vì chưa có AST được chấp nhận. Baseline category+side 10/32 và shallow 64/64 của blueprint cũ chỉ là số liệu kế thừa; không được dùng làm PASS cho candidate mới. Khi nào có AST mới hợp lệ, phải có matched-world, goal-only, field-cue, lexical leakage và action-frequency baselines trước design GO.

Custody mới ở mức protocol: quyền nguồn/PII theo nguồn và split, custodian độc lập/2-party trust roles, canonical JSON domain-separated HMAC private AST+gold, signed ledger root, ACL denial/replay/tamper, opaque scoring IDs, unseal sau khi khóa parser/model/outputs. **CUSTODY_NOT_EXECUTED, RIGHTS_NOT_VERIFIED, PRIVATE_EVAL_NOT_CREATED, GOLD_NOT_CREATED.** Public exploratory examples không được tái sử dụng làm blind gold.

## 5. Kết luận và khuyến nghị nghiên cứu

**`HOLD_ONTOLOGY_FEASIBILITY`.** Trong phạm vi exploratory grammar hữu hạn đã duyệt không có bộ 4 OOD category nào được chứng nhận; đặc biệt `goal_persistence` không có cặp A/B distinct-first-action một fluent đạt tiêu chí. Không tự khẳng định ontology toàn cục vô nghiệm. Với yêu cầu R1 4 OOD/category và bốn category bắt buộc, **dừng sản xuất blueprint theo công thức D1 Bridge hiện hành**. Muốn tiếp tục hướng khoa học, cần thiết kế lại benchmark/ontology một cách công khai, hoặc giảm phạm vi giả thuyết theo prereg amendment riêng; không nâng source demo thành confirmatory science.

### Các gate bảo toàn

`D1_BRIDGE_SCIENCE=HOLD`, `D1_EXISTING=HOLD_UNMODIFIED`, `TEST_Q1Q2=SEALED`, `FC02=NOT_OPENED`, `GPU=0`, `TRAINING=0`, `INFERENCE=0`, `FROZEN_V6=UNCHANGED`, `MAIN=UNCHANGED`, `lineage.md=UNCHANGED`.

## Bước thực hiện tiếp theo — duy nhất

`TTM_SMALL4M_D1_R1_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_DECISION_SINGLE_GATE`

Giao reviewer độc lập đánh giá liệu giới hạn tìm kiếm và lựa chọn prospective physical semantics có đủ thuyết phục để **đóng D1 Bridge R1 theo thiết kế hiện tại** và mở đề xuất benchmark kế nhiệm (design-only, không science permit), thay vì tiếp tục vòng sinh 32 blueprint. Nếu reviewer bác bỏ phạm vi tìm kiếm, yêu cầu một phản ví dụ *constructive* thực sự: 4 OOD/category, per-OOD canonical action-causal graph nonoverlap và matched-world witnesses, với unique oracle dưới semantics được ghi nhận. Chỉ một GO/HOLD về thiết kế; không chạy mô hình.
