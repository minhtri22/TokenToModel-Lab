# TTM-Small-4M D1 Bridge R1 — Phản biện độc lập construct validity, structural OOD và sealed EVAL custody

**Operation:** `TTM_SMALL4M_D1_R1_32_BLUEPRINT_CONSTRUCT_VALIDITY_AND_SEALED_EVAL_CUSTODY_DISTINCT_INDEPENDENT_SOURCE_REVIEW_SINGLE_GO_HOLD`  
**Ngày:** 2026-11-14  
**Reviewer:** ChatGPT / GPT-6, `INDEPENDENT_AI_SCIENTIFIC_SOURCE_REVIEWER` (phản biện AI khác lượt tạo blueprint; không phải human/custodian độc lập về mặt tổ chức).  
**Chế độ:** `READ_ONLY_REVIEW · DESIGN_ONLY · SOURCE_ONLY · NO_GPU · NO_TRAINING · NO_INFERENCE · NO_PRIVATE_GOLD`  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Frozen scientific HEAD:** `dd52804685d186c17e600221ffb16ce78aea12ea`  
**V6 R1/R3 custody:** `553f1d6db9c2d5572a7e664b64a32e9eaf977f88`  
**Source evidence commit được phản biện:** `1394e0abe3eae29a905b2cfe0537d4b0b9521b2b`  
**Quyết định duy nhất:** **`HOLD_REVISE_BEFORE_PREREG`**  
**Science release:** `HOLD`; **sealed EVAL custody:** `CUSTODY_NOT_EXECUTED`.

## 1. Nguồn, chain of custody và phương pháp

Ba commit SHA đều được xác minh là Git commit thực sự qua GitHub read-only. Commit `1394e0a...` có **parent trực tiếp** `553f1d6...`. Toàn bộ bảy tệp bắt buộc được truy xuất bằng GitHub `fetch_file` với `ref` cố định bằng SHA commit, không đọc `main` di động. Đọc thêm contract V6 JSON, hai báo cáo V6 và prereg V1 ở **cùng source evidence commit** để đối chiếu protocol. Không mở private EVAL hoặc TEST.

| Source path tại commit `1394e0a...` | SHA-256 độc lập trên nội dung UTF-8 truy xuất |
|---|---|
| `artifacts/research/ttm-small4m-fact-conditioning/evidence_d1_r1_32_typed_source_20261114/TTM_D1_R1_TYPED_32_SOURCE_BLUEPRINTS_20261114.json` | `83f9cce35639dd676ffe3ac31ed4983b2de2a30a008290798cb8c39f3c78047c` |
| `tools/pilot_t4/fc01/d1_r1_32_typed_source_20261114/independent_32_oracle_checker.py` | `0ad537bbdcde0e8d92f6d15e5c59387e1419d9f3ec60e45f786a31f71ed1fdc8` |
| `tools/pilot_t4/fc01/d1_r1_32_typed_source_20261114/build_32_blueprints.py` | `331f57e395bcb643f127e16b47234ea1ff3a8663ec7b1a2e415446a78f520c14` |
| `tools/pilot_t4/fc01/d1_r1_32_typed_source_20261114/adversarial_32_source_qa.py` | `2e6fe1f81858a90915ed3f1479d8fa7f947ee4dff2f711c34516229a6fcc1602` |
| `artifacts/research/ttm-small4m-fact-conditioning/evidence_d1_r1_32_typed_source_20261114/TTM_D1_R1_32_INDEPENDENT_CHECKER_RECEIPT_20261114.json` | `460d76ca026cbc0344d1c2199f7f2acba822bd3f231fbb1ca7278b05b2137bd5` |
| `artifacts/research/ttm-small4m-fact-conditioning/evidence_d1_r1_32_typed_source_20261114/TTM_D1_R1_32_NEGATIVE_AND_GRAPH_QA_RECEIPT_20261114.json` | `6ea174e113e73e1fb8bc405da0791b731faced49e133a7e56f2fa768e6789336` |
| `docs/research/ttm-small4m-fact-conditioning/TTM_D1_R1_32_SINGLE_ADJUDICATION_HANDOFF_20261114.md` | `5b34343cb852823561471bf343b8df07aa6e0920b19e200dfcf197a686d67187` |

Hai SHA đầu trùng đúng handoff đã khóa; phương pháp SHA-256 riêng bằng JavaScript chuẩn (đã self-test với vector `abc`). Các digest khác được tính cùng phương pháp trên chuỗi UTF-8 do GitHub trả về; không khẳng định đã clone Git repository hay thử thực thi Python trên host của owner. Git blob SHA-1 tương ứng JSON là `6701f1b98a60ed22b49464f039155afdc97c1ba9`, checker là `c5525295fda95521951f046b052cfd5047313b06`.

Phép kiểm **mới**, không gọi checker/generator lịch sử: phân tích trực tiếp tất cả 32 AST, thực hiện trình thông dịch Boolean độc lập trên `nodes/edges`, kiểm 16-input truth table cho từng graph, xác lập output A/B, so sánh các goal/tuple đã công bố, và thử **baseline chỉ ghi nhớ một cặp canonical action từ mỗi category TRAIN** để dự đoán toàn bộ OOD. Đây là kiểm toán construct/shortcut ở mức nguồn, **không phải** mô phỏng đầy đủ độc lập mọi transition của sáu động từ và không phải science inference. Không chạy lại 13/13, 12/12 hoặc bộ QA trước đó.

Đường dẫn nguồn cố định: [JSON 32](https://github.com/minhtri22/TokenToModel-Lab/blob/1394e0abe3eae29a905b2cfe0537d4b0b9521b2b/artifacts/research/ttm-small4m-fact-conditioning/evidence_d1_r1_32_typed_source_20261114/TTM_D1_R1_TYPED_32_SOURCE_BLUEPRINTS_20261114.json); [checker](https://github.com/minhtri22/TokenToModel-Lab/blob/1394e0abe3eae29a905b2cfe0537d4b0b9521b2b/tools/pilot_t4/fc01/d1_r1_32_typed_source_20261114/independent_32_oracle_checker.py); [generator](https://github.com/minhtri22/TokenToModel-Lab/blob/1394e0abe3eae29a905b2cfe0537d4b0b9521b2b/tools/pilot_t4/fc01/d1_r1_32_typed_source_20261114/build_32_blueprints.py); [V6 ontology](https://github.com/minhtri22/TokenToModel-Lab/blob/1394e0abe3eae29a905b2cfe0537d4b0b9521b2b/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V6_SINGLE_PACKET_TYPED_FOUR_CATEGORY_ONTOLOGY_AUDIT_LEDGER_BINDING_DESIGN_HOLD_20261114.md).

## 2. Phân định ba cấp độ kết luận

| Cấp độ | Kết luận độc lập |
|---|---|
| **Source correctness** | Tài liệu nguồn báo 32/32 typed, 16/16 TRAIN/OOD, 64 graph-pair semantic witnesses, 64 nonisomorphic và 12/12 negative. Cấu trúc/count, 8 truth table/category và A/B policy flip được **đối chiếu** từ JSON; toàn bộ 6-verb state transitions **chưa được chứng minh bằng model checker độc lập ngoài tác giả**. `PASS_SOURCE_SCOPED_REPORTED_AND_PARTIALLY_CROSSCHECKED`. |
| **Construct validity** | **Chưa đạt**: bài toán đã biến thành Boolean gate chọn giữa hai goal được biết trước; có shortcut giải trọn bộ OOD mà không suy luận graph. `NOT_ESTABLISHED`. |
| **Science readiness** | Chưa có sealed EVAL/independent custodian, rights/PII/ACL/ledger, parser và production audit. `HOLD_NOT_EXECUTED`. |

## 3. R1-A — Construct validity và tương thích ontology sáu verb

Bốn nhóm dùng **chính xác tám công thức F** (`TR01..TR04`, `OD01..OD04`); mỗi công thức có dạng `AND(x0, expression(x1,x2,x3))`. `x0=power(d1)==ON` là **can thiệp duy nhất** của A/B. Generator chọn trước bộ `x1..x3` khiến mọi A đều có `policy=true`, mọi B đều `policy=false`. Với từng category, tám AST đều có **một goal_when_true chung và một goal_when_false chung**. Vì thế nhánh hành động canonical của mỗi category là một cặp bất biến, bất kể công thức TRAIN hay OOD.

**Đối chứng shortcut độc lập từ JSON và receipt:** ghi nhớ chỉ bốn ví dụ TRAIN `TR01` (một cho mỗi category), tạo từ điển `(category, A/B)→tuple`, sau đó so với các tuple đã khóa trong receipt. Kết quả **64/64 phía A/B trên 32 skeleton**, gồm **32/32 phía A/B của 16 OOD**, chính xác tuyệt đối. Đây **không phải accuracy của mô hình**; chỉ là chứng minh tồn tại một thuật toán không đọc graph nhưng giải toàn bộ bộ đề đã công khai.

| Category | A (x0 ON) | B (x0 OFF) | Vấn đề construct |
|---|---|---|---|
| `entity_location` | `CARRY i0 T0 l1` | `RELOCATE i0 T0 l1` | Cả hai chuyển i0 sang l1; goal chọn holder. Các predicate khác liên quan i1/g1, không tác động quan hệ i0. |
| `causal_reasoning` | `ACTIVATE d0 T0 NONE` | `WAIT g0 T1 NONE` | Quan hệ causal thật là `d0→g0`; can thiệp là d1, với `linked_trigger(d1)=NONE`, không kiểm thay đổi causal chain. |
| `rule_constraint` | `WAIT g1 T2 NONE` | `TRANSFER i0 T0 a1` | Priority guard được gán cho **i1**, không phải i0. i0 đã được giữ bởi a0, protection i0 đã hết trước T0, nên transfer i0 ngay hợp lệ trong cả A/B; A chỉ đòi clock=T2. |
| `goal_persistence` | `RETAIN i1 T0 T2` | `RETAIN i1 T0 T1` | External transfer chỉ xảy ra **T1**; cả hai hạn bảo vệ đều đủ để giữ i1 qua sự kiện. Gold khác do yêu cầu exact `protected_until`, không do khác biệt thành bại duy trì mục tiêu. |

V6 có sáu động từ typed và category/task-specific effects, nhưng chính các chứng cứ nguồn không cho thấy Boolean graph này là diễn giải hợp lệ của nhiệm vụ ngôn ngữ/phản thực đã tiền đăng ký. Nó là **amendment mục tiêu mới**, không phải diễn đạt lại vô hại của ontology hiện hữu. `ACTIVATE d1` có thể khác về legal action giữa hai side, nhưng d1 không gắn với goal actions của bốn category; sự khác biệt đó không cứu được construct validity.

## 4. R1-B — Structural OOD và phản ví dụ

Đã phân biệt bốn mức độ: (i) đồ thị không đẳng cấu, (ii) khác truth table, (iii) khác hành động nếu cưỡng bức đánh giá hai graph trên một **world được checker tái dựng**, và (iv) **mới về cơ chế nhân quả hành động**. Nguồn có chứng cứ cho (i)–(iii) trong Boolean-policy layer; **không chứng minh (iv)**.

**Phản ví dụ tối thiểu về novelty:** `ENTITY_LOCATION_TR01` và `ENTITY_LOCATION_OD01`. Trên vector quan sát `(x0,x1,x2,x3)=(1,0,0,1)`:

```text
TR01 = x0 AND x1 AND x2 AND x3                 = 0
OD01 = x0 AND (x1 OR (x2 XOR x3))              = 1
```

Hai graph có truth table khác và chọn goal khác ở cùng vector, nhưng **sáu precondition/effect của action không thay đổi**; category, action semantics và mục tiêu location/holder vẫn như cũ. Khác biệt hành động là hệ quả của một **policy Boolean điều khiển goal**, không phải quan hệ action-causal OOD. Quan trọng hơn, trên **chính A/B được lưu trong mỗi blueprint** thì không graph nào tạo khác biệt decision mapping: tất cả `A→CARRY` và `B→RELOCATE` cho category này. Witness trên world tái dựng không phải chứng cứ performance hay novelty của cặp EVAL thực.

Có nguy cơ shortcut split bởi `skeleton_id` chứa `TR/OD`, `split_design`, hình dạng graph, độ sâu, số gate và lựa chọn x1..x3. Nếu các trường này có mặt trong text prompt, chúng có thể tạo leakage trực tiếp; **chưa kiểm tra prompt thực tế**, nên phân biệt là *nguy cơ*, không phải leakage đã quan sát. Một phép thử OOD hợp lệ phải kiểm định novelty tại đồ thị dependency của **action effects, temporal priority, goal persistence và causal links**, sau khi chuẩn hóa alias/relabel, đồng thời dùng baseline không xem graph, kiểm matched worlds cùng x0 khác cấu trúc và kiểm holdout theo semantic mechanisms.

## 5. R1-C — Unique oracle/reachability: có gì được và chưa được chứng minh

`independent_32_oracle_checker.py` kiểm đủ fluents typed, bất biến location/holder, liệt kê sáu verb, áp dụng protection priority vào `TRANSFER`, advance thời gian nguyên tử và exogenous request. Nó bắt buộc **một action** thỏa goal đã được Boolean policy chọn ở mỗi side và `gold_A != gold_B`. Đó là một phép kiểm hợp lý nhưng **có điều kiện trên goal nhân tạo**, không chứng minh task goal tự nó đúng về khoa học. Không dùng receipt để khẳng định một model checker độc lập thứ ba đã chứng minh toàn bộ world reachability.

**Phản ví dụ về oracle do goal chế tạo:** `RULE_CONSTRAINT_TR01` có `holder(i0)=a0`, `protected_until(i0)=BEFORE_T0`, `protected_until(i1)=T1`, `current_time=T0`. Goal A là `holder.i0=a0 ∧ current_time=T2`, dẫn đến `WAIT(g1,T2)`; goal B là `holder.i0=a1 ∧ current_time=T0`, dẫn đến `TRANSFER(i0,a1)`. Do protection chỉ trên **i1**, không có va chạm priority buộc WAIT cho **i0**. Định nghĩa `current_time=T2` tạo ra uniqueness. Vì vậy oracle là duy nhất **theo postcondition đã lựa**, không phải duy nhất do rule-priority reasoning.

**Phản ví dụ về persistence:** `GOAL_PERSISTENCE_TR01` có `external_transfer_request=(at=T1,item=i1,recipient=a1)`, `holder(i1)=a0` ở T0. Hai action `RETAIN(i1,T1)` và `RETAIN(i1,T2)` đều chặn request đúng T1 bởi điều kiện `protected_until >= t`; không có request tại T2. Dù checker xác nhận tuple gold khác, hai lựa chọn **đều đáp ứng tiêu chí duy trì holder qua distraction duy nhất đã mã hóa**. Đây là sự khác biệt về deadline do goal đặt ra, không phải khác biệt nhân quả có thể kiểm qua outcome.

**Cảnh báo về state-level reachability:** Có **8/32 blueprint** (mỗi blueprint cùng một vấn đề ở A và B) có `trigger_fired(g)=true` tại `current_time=T0`, trong khi `scheduled_at(g)` là T1/T2 và **không có thiết bị ON nào linked với g**. Ví dụ `CAUSAL_REASONING_TR01`: `trigger_fired(g1)=true`, `scheduled_at(g1)=T2`, `linked_trigger(d1)=NONE`, `linked_trigger(d0)=g0`, `power(d0)=OFF`, tại `T0`. Checker chỉ xét bất biến type, không chứng minh trace tạo ra trạng thái này từ một genesis/state admissibility policy đã khóa. **Chưa thể kết luận trạng thái là bất khả đạt tuyệt đối**, vì V6 chưa cấm prehistory tùy ý; đây là lỗ hổng proof obligation, cần nguồn gốc sự kiện hoặc explicit admissible initial-state contract. Số trường hợp 8 là phát hiện trực tiếp từ JSON, không phải chạy Python checker.

Giới hạn khác: oracle chứng minh **next action một bước**, không chứng minh plan tổng quát hoặc năng lực free-generation trong prompt thực. Checker và generator độc lập đường mã nhưng chia sẻ định nghĩa world/goal và assumption có trước; 12 negative mutations kiểm mã bắt sai hư hỏng kỹ thuật, **không bắt được shortcut và mục tiêu sai construct**.

## 6. R1-D — Sealed EVAL custody, source rights và blind independence

**Trạng thái thực:** `CUSTODY_NOT_EXECUTED`; `RIGHTS_NOT_VERIFIED`; `INDEPENDENT_GOLD_CUSTODIAN_NOT_APPOINTED`; `TRAIN_VAL_EVAL_SEMANTIC_NONOVERLAP_NOT_PROVEN`; `PARSER_RUNTIME_NOT_VERIFIED`. Toàn bộ 32 AST và predicate/goal công khai; **không được dùng chúng làm sealed EVAL hoặc gold bí mật**. Các source-only blueprint không phải dataset TRAIN/VAL/EVAL đã được chấp nhận.

**Phương án khả thi cần tiền đăng ký (không thực hiện trong review):** owner/preregistrar khóa định nghĩa novelty và rubric, custodian EVAL riêng tạo EVAL AST/gold **ngoài vùng truy cập trainer/rater**, đóng băng cấu trúc trước outcome; reviewer independent xem thiết kế/nonoverlap mà không có quyền thay data; duy trì manifest SHA-256 cho tệp có thể công bố, HMAC-SHA256 riêng phía TRAIN/VAL và EVAL cho AST bí mật, anchor ledger_root trước audit, private Ed25519 attestation gắn AST/HMAC/audit_id, chữ ký auditor trên terminal receipt theo AM05 V6. Rights/PII/license được chứng thực per-source, binding source→derivative, quyền dùng TRAIN/EVAL được ghi riêng. Khoá mapping `(opaque_id→gold)` và schema parser riêng; evaluator chỉ nhận prompt/output opaque; mở gold chỉ **sau** khi protocol, parser SHA, output SHA, tập evaluation, seed và terminal commitment đã khóa. Cấm thay skeleton sau khi xem outcome; audit FAIL/UNKNOWN hoặc mất signed terminal receipt → HOLD. Có thể phê chuẩn *thiết kế custody* mà không tạo gold ngay; **không thể chấm `CUSTODY_PASS` hiện tại**.

Theo V6 AM05, HMAC binding là **authenticated custodian assertion dưới trust boundary**, không phải zero-knowledge/public proof; phải có xác minh role/ACL/signer và denial probes khi triển khai. Không tự giả định một tên người giữ khóa hoặc một quyền đã có.

## 7. R1-E — Protocol compatibility

- **Giữ đúng** bốn category `entity_location`, `causal_reasoning`, `rule_constraint`, `goal_persistence` và sáu verb `RELOCATE`, `CARRY`, `TRANSFER`, `RETAIN`, `WAIT`, `ACTIVATE` ở lớp typing; nhưng **không đạt** ràng buộc *task-relevant structural OOD*, protection-priority/causal-chain và construct validity của ontology V6. Boolean graph là **AMENDMENT MỚI**, phải có định nghĩa giả thuyết, task condition và pre-registered exclusion/inclusion trước data, không được nhập lặng vào frozen V6.
- **Không thay đổi** đơn vị primary `paired-family`; mọi A/B chỉ là một family đúng khi cả hai prompt đúng. Giữ đúng lịch frozen correction R3 với **12 seeds** `20261120..20261130,20261201` của V6; không quay về 5 seeds của V1 hay chỉnh seed theo kết quả.
- **Không thay** fixed denominators, V6 sign-test `k≥10/12` và `p(k=10)=79/4096`, signed integer `Σ D_s≥308`, category gates hoặc A/B/C contrastive parameters. Không mở lại FC01.
- `TEST_Q1Q2=SEALED`, `D1_EXISTING=HOLD_UNMODIFIED`, `D1_BRIDGE_SCIENCE=HOLD`, `FC02=NOT_OPENED`, `OWNER_PERMIT=NOT_GRANTED`. Không chạy mô hình/huấn luyện hay sửa frozen scientific commit/`lineage.md`.

## 8. Danh sách phát hiện được định danh

| ID | Severity | Bằng chứng và tác động |
|---|---|---|
| `R1-F01` | **CRITICAL** | `(category, A/B)` lookup từ 4 TRAIN TR01 dự đoán **32/32 OOD action sides**; graph không cần thiết để trả lời. Construct shortcut có thể triệt tiêu nội dung kiểm định chính. |
| `R1-F02` | **CRITICAL** | 64 truth-table/graph witnesses chứng minh Boolean-goal divergence, **không** chứng minh action-causal structural novelty. Cùng action semantics và cùng mapping A/B cho mỗi category. |
| `R1-F03` | **HIGH** | `rule_constraint` guard i1 không chặn `TRANSFER i0`; `goal_persistence` cả T1/T2 đều giữ i1 qua cùng request T1. Chênh goal/time tạo gold duy nhất nhưng không tạo bài toán mục tiêu đúng. |
| `R1-F04` | **HIGH** | `causal_reasoning` can thiệp d1 (`linked_trigger=NONE`) không biến đổi chuỗi d0→g0; `entity_location` dùng cues i1/g1 để chọn goal i0; category chỉ khác goal template. |
| `R1-F05` | **HIGH** | 8 blueprint có fired event trước thời điểm scheduled, thiếu historical trace/admissible genesis proof; typed invariant không đồng nghĩa world reachable. |
| `R1-F06` | **HIGH** | Không có private sealed EVAL, independent custodian/rights/PII/ACL hoặc blind gold mapping. Đây là `NOT_EXECUTED`, không phải thất bại thí nghiệm. |
| `R1-F07` | **HIGH** | Task-goal selector Boolean là amendment ngoài V6 frozen ontology; chưa được chấp nhận prospective trước khoa học. |
| `R1-F08` | **MEDIUM** | `split_design`, IDs và độ sâu/số gate có thể lộ split nếu được render vào prompt; chưa chứng minh có leakage thực tế. |
| `R1-F09` | **MEDIUM** | Checker/generator và mutation suite dùng cùng semantics, không đủ làm independent formal verification của genesis/goal correctness. |

## 9. Phán quyết tích hợp và một gói sửa đổi tối thiểu

**Một phán quyết: `HOLD_REVISE_BEFORE_PREREG`.** **KHÔNG chấp nhận Boolean policy graph hiện tại làm cấu trúc tiền đăng ký cho D1 Bridge.** Nó chỉ cho thấy kỹ thuật triển khai một policy graph với one-step oracle unique trong world typed. Nó không cung cấp phép đo xác nhận rằng mô hình học **suy luận nhân quả hành động** hay generalization đến OOD semantic mechanisms. Điều kiện 1, 2, 4, 5 và 6 của gate GO chưa được chứng minh; unique oracle chỉ PASS theo goal self-defined, không khắc phục các thiếu sót đó.

**Gói sửa đổi tích hợp duy nhất:** `TTM_SMALL4M_D1_R1_ACTION_CAUSAL_STRUCTURAL_OOD_ORACLE_AND_SEALED_CUSTODY_SINGLE_AMENDMENT_SOURCE_GATE`.

Nội dung bắt buộc trong **một** prospective amendment trước bất kỳ dữ liệu/outcome khoa học: (i) định nghĩa task-goal và sáu verb trên cùng nguồn V6, bỏ công tắc toàn cục `x0` hoặc chứng minh counterfactual thật sự tác động causal path của đúng category; (ii) thay 32 blueprint bằng **32 thiết kế R1 chỉ ở source-only** với action-causal dependencies, 4 TRAIN/4 OOD mỗi category, matched control để baseline category+x0 **không giải OOD**, có witness cùng-world về **khác hành động do causal mechanism** chứ không chỉ goal rewriting; (iii) checker độc lập xác minh genesis/event histories, full typed transition, WAIT atomic advance, protection priority, legal action uniqueness và functional nonoverlap theo semantic equivalence; (iv) pre-register renderer/parser/cue masking, không có identifier/split label trong prompt, category balance; (v) custody plan riêng cho EVAL có role, HMAC/attestation/ledger, source rights, independent reviewer và gold unseal order, **không tạo/không mở gold trong gói review**; (vi) giữ nguyên prereg statistical thresholds, seeds và freeze logic. Một lần QA nguồn độc lập và một GO/HOLD, không chia micro-permit, không chạy lại 13/13 hoặc 12/12 không đổi.

**Bước thực hiện tiếp theo — duy nhất:** giao một agent thực hiện gói amendment tích hợp trên nhánh mới tách biệt (source-only), sau đó phản biện độc lập một lần. Không cấp quyền GPU, EVAL creation, science run hoặc merge.

**Evidence custody:** Hai artifact của review này chỉ được tạo trong sandbox và bàn giao owner. **`GITHUB_WRITE_NOT_AUTHORIZED_IN_THIS_REVIEW`**, `EVIDENCE_COMMIT=NOT_CREATED`, `MAIN=UNCHANGED`, `lineage.md=UNCHANGED`.
