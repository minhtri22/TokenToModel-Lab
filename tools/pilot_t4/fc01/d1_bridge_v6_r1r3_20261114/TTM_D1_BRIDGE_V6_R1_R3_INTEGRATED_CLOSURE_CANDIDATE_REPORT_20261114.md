# TTM-Small-4M — D1 Bridge V6: tổng hợp hai phản biện và gói sửa R1/R3 tích hợp

**Ngày:** 2026-11-14  
**Phạm vi:** `SOURCE_ONLY / DESIGN_ONLY / PUBLIC_SYNTHETIC_QA / NO_GPU / NO_TRAIN / NO_INFERENCE / NO_PRIVATE_AST_OR_GOLD / NO_TEST_Q1Q2`  
**Frozen input Git HEAD:** `dd52804685d186c17e600221ffb16ce78aea12ea`  
**Loại kết quả:** đề xuất sửa hợp đồng và executable synthetic QA, **không** phải scientific outcome, prereg mới, owner approval hoặc independent production certification.

## 1. Tiếp nhận và phân xử bất đồng của hai reviewer

Đã đọc 4 artifact (2 MD, 2 JSON), SHA-256 cục bộ:

| Reviewer | MD SHA-256 | JSON SHA-256 |
|---|---|---|
| ChatGPT review trước | `6e203c7e2fcc834dd77f72700009085b926e48a34a1e55536e21cfd8e4620195` | `db7e8202df5e9532d2e173bc64adcd6d64a2966b223ccba550fb0f70b4e4d56a` |
| Agent đính kèm | `65f1579569657eebc4296fe96041ae62b3f506277ef75d94ee0785bb08e86bd9` | `9486542d35d6e31bd60a19fe018cb46a20c3dc435d80112ad4be7ab627b799d6` |

Cả hai cho `HOLD_REVISE_BEFORE_PREREG`. Điểm khác: reviewer đầu gắn R3=PASS kế thừa; reviewer thứ hai phát hiện `V6-R3-FROZEN_SEED_DRIFT`. Đã **tự truy xuất lại** S8 (V5) và S2 (V6) bằng GitHub connector tại đúng frozen HEAD; các blob SHA-1 `f4103f571ea80f909d59b1d9fe5f426702f53fa4` và `c6ac330c40e31035116add165ef30fa58af59639` khớp handoff. Mảng seed:

- `S8.AM03_stats.seed_values`: `20261120...20261130, 20261201` (12 phần tử).
- `S2.AM03_stats.seeds`: `20261120...20261130, 20261131` (12 phần tử).
- Đây là **drift có thật**: `20261131 != 20261201`. Tuyên bố inherited unchanged trong V6 không chính xác; QA S3 check `16_STATS_UNCHANGED` **không** so mảng seed liên phiên bản.

Vì vậy sửa kết luận reviewer đầu, chấp nhận phát hiện R3 của reviewer thứ hai. Hai reviewer đều là AI độc lập theo cuộc trò chuyện (self-attested), không phải QA nhân sự khoa học độc lập có chain-of-custody xác minh bên ngoài.

### Ma trận phân xử V6 gốc (bất biến)

| Trục | Kết luận | Chứng cứ/giới hạn |
|---|---|---|
| R1/AM01 | **HOLD (HIGH)** | `WAIT` không cưỡng chế clock/defer; `RETAIN` có thể rút ngắn protection; `CARRY` có thể làm lệch holder-location; các fixture CAT03/CAT04 thiếu trạng thái/goal-controlled witness; chưa có 32 skeleton cấu trúc thật |
| R2/AM02 | PASS_SCOPED_DESIGN | Grammar/TIME kế thừa; parser 64+/64− chưa chạy |
| R3/AM03 | **HOLD (HIGH)** | Frozen seed thứ 12 bị đổi `20261201` thành `20261131`; sign-test tail `79/4096` không sai nhưng không cứu lỗi seed |
| R4/AM04 | PASS_SCOPED_DESIGN | Global/category integer gates không thay đổi |
| R5/AM05 | PASS_SCOPED_DESIGN | Ledger root + 2 HMAC + custodian-attested AST bytes + Ed25519 receipt được đặc tả, **dựa trên tin cậy custodian**; production ACL/keys chưa chạy |
| R6/AM06 | PASS_SCOPED_DESIGN | FC01 hyperparameter provenance và full contrastive-package estimand còn nguyên |

**One verdict cho V6 frozen:** `HOLD_REVISE_BEFORE_PREREG` — 4/6 PASS thiết kế có phạm vi, 2/6 HOLD, 0 FAIL. Không đổi verdict khoa học đã khóa.

## 2. Gói sửa prospective duy nhất (không overwrite V1–V6)

Gói `TTM_D1_BRIDGE_V6_R1_R3_INTEGRATED_CORRECTION_SPEC_20261114.json` mô tả sửa R1 + R3 trong **một lần**, đi cùng chương trình kiểm toán Python 3.12. Những thay đổi dưới đây chỉ được áp dụng vào **candidate file mới** sau khi nguồn V5/V6 cục bộ được truy xuất `git show` tại frozen HEAD và **Git blob SHA-1 tự tái băm khớp**. Không làm `git add`, `git commit`, `git checkout`, `git fetch` hay push.

### R1 — Typed transitions, clock, protection, holder, event

1. **TIME**: với `RELOCATE`, `CARRY`, `TRANSFER`, `RETAIN`, `ACTIVATE`, bắt buộc `time_id=current_time`. Riêng `WAIT` dùng `time_id` của trigger được lên lịch **trong tương lai**. `WAIT` là bước **atomic advance**: ghi `defer_until`, tiến clock đến thời điểm đích, xử lý sự kiện theo thứ tự đã khóa, không cho xen hành động của agent trước trigger. Hệ thống không bịa clock jump cho hành động khác. `time_id=NONE` được bảo lưu như ký hiệu ontology nhưng **không hợp lệ** với sáu chuyển trạng thái trong ứng viên này; parser phải được QA lại trước khi dùng thật.
2. **RETAIN**: sửa `protected_until := max(old_protected_until, requested_until)`. Khoảng bảo vệ **inclusive**; `TRANSFER` chỉ hợp lệ khi `protected_until < current_time`. Từ chối mọi diễn giải cho phép rút ngắn protection đã nhận.
3. **CARRY**: khi agent đổi location, **mọi** item đã có `holder=item→agent` phải cùng di chuyển, cộng target mới được nhặt. Nếu chỉ đổi location(target), world có từ 2 item sẽ phá invariant `holder(i) ⇒ location(i)=location(holder(i))`.
4. **Trigger/exogenous event**: `ACTIVATE` có thể fire linked trigger sớm; lần fire ở lịch sau đó là idempotent. Ở mỗi thời điểm sau `WAIT`, scheduled trigger được xử lý trước, yêu cầu transfer ngoại sinh (nếu có) được xử lý sau và bị `protected_until` ưu tiên chặn. Đây là **ngữ nghĩa đề xuất** cần độc lập phản biện về độ phù hợp khoa học, không phải cơ chế V6 đã có.
5. **Full typed toy fixtures**: CAT01–CAT04 có đủ các trường bắt buộc, với `location(holder)` nhất quán. CAT03 giữ mục tiêu chuyển giao nhất quán giữa A/B, thay duy nhất protection; CAT04 đưa distractor từ lời mô tả thành sự kiện có type ở T1. Các tình huống này chỉ chứng minh reachability ở *mini-world tổng hợp*, **không chứng minh unique-gold hoặc sự khác nhau cấu trúc TRAIN/EVAL**.

**Giới hạn bổ sung:** Các quy tắc synthetic có thể chấp nhận để tiếp tục hoàn thiện source, nhưng không được tự suy rằng chúng là ontology tối ưu hay đầy đủ của `entity_location`, `causal_reasoning`, `rule_constraint`, `goal_persistence`. Cổng `4 TRAIN + 4 STRUCTURAL_OOD` skeleton mỗi category, real AST-isomorphism, reachable oracle độc lập, gold uniqueness, rights và nonoverlap đều `NOT_EXECUTED`.

### R3 — Exact frozen seeds

Khôi phục **nguyên mảng** `[20261120, 20261121, 20261122, 20261123, 20261124, 20261125, 20261126, 20261127, 20261128, 20261129, 20261130, 20261201]`, không chỉ sửa nhãn documentation. Candidate builder đối chiếu toàn mảng với `S8.AM03_stats.seed_values` và chỉ chấp nhận source V6 đã biết có last-seed `20261131`; nếu các byte source khác thay đổi hoặc upstream đã sửa, **HOLD**, không tự rebase/áp lại không điều kiện. Không đổi `D_s`, `k>=10/12`, `p=79/4096`, `ΣD>=308`, threshold 39/192 hoặc bổ sung ngưỡng hậu nghiệm.

### R2/R4/R5/R6 — Preservation

Candidate builder giữ nguyên bản sao JSON của bốn trục đã PASS, so sánh **deep equality** trước khi ghi output, và giữ nguyên `gates.SCIENCE=HOLD`. Không sửa V5 hay V6 frozen; không tạo TRAIN/EVAL hoặc private gold mới. R5 chỉ PASS thiết kế theo trust model, không được gọi `SECURITY_RUNTIME_PASS`.

## 3. QA thực thi tại môi trường hiện tại

File `ttm_d1_bridge_v6_r1_r3_integrated_qa_20261114.py` đã **thực sự chạy Python** (không phải chỉ mô tả kiểm thử) trên public synthetic mini-world, kết quả:

| QA | Kết quả |
|---|---|
| Positive synthetic invariants/fixtures/seed and mock candidate patch | **13/13 PASS** |
| Negative guards/mutations (seed drift, shortening protection, absent state, future action, premature transfer, old CARRY invariant, WAIT faults) | **12/12 PASS** |
| Valid finite `RELOCATE/CARRY` transitions checked against holder-location invariant | **128** |
| CAT01–CAT04 | 4 complete synthetic A/B executable traces |
| Full input V5/V6 source bytes locally loaded in this execution | **NOT_EXECUTED** (GitHub connector inspected exact objects, but local runtime cannot download full source bytes) |
| Candidate applied to exact frozen source on user machine | **NOT_EXECUTED** |
| Real four-category 32 semantic skeletons, unique oracle, nonoverlap | **NOT_EXECUTED** |
| GPU, training, inference, TEST Q1Q2 | **NOT_EXECUTED** |

**Không nhầm lẫn** 128 finite transition checks với 128 parser cases theo R2: chúng kiểm invariant mini-world, **không phải** parser QA 64 positives + 64 negatives. Và 13/13 + 12/12 là independent implementation by current assistant, nhưng **không** là kiểm định ngoài độc lập cho science hoặc source đầy đủ. `TTM_D1_BRIDGE_V6_R1_R3_INTEGRATED_QA_RECEIPT.json` có `source_status=NOT_LOADED_SELFTEST_ONLY`.

## 4. Cách thực hiện trên Windows, không cần micro-permit

Đặt ba tệp `*.py`, `*.ps1`, `CORRECTION_SPEC.json` trong một thư mục thuộc `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\` rồi chạy **một** lệnh PowerShell 5.1:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\Invoke-TTM-D1-V6-R1R3-Integrated-PS51.ps1'
```

Wrapper sử dụng Python 3.12 đường dẫn đã định; Python sẽ gọi `git show <frozen commit>:<source path>` cho V5 và V6, tự băm **Git blob SHA-1 trên raw bytes**, so mảng seed, xây candidate trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_D1_V6_R1_R3_CANDIDATE_20261114`, và ghi biên nhận JSON kèm SHA-256. Nếu commit gốc không có trong local Git object database, **HOLD** (không auto-fetch). Không tự sửa branch, không commit, không thêm phase hay permit.

## 5. Quyết định tích hợp cuối

**Gói sửa R1/R3 prospective:** `CREATED_LOCAL`, source candidate generation `READY_FOR_EXACT_FROZEN_LOCAL_READBACK`, independent QA on candidate and real structural AST **PENDING**.

**V6 frozen verdict vẫn là** `HOLD_REVISE_BEFORE_PREREG`. Sau khi xác minh đúng byte và kiểm tra candidate từ local Git, phải có một quyết định thiết kế GO/HOLD độc lập dành cho candidate, không lấy PASS mini-world để mở science. Nếu không thể biểu diễn **đủ 4 categories và 4+4 skeleton/category**, giữ `HOLD_WHOLE_D1_BATCH`, không thay bằng ba category hoặc bỏ skeleton.

**Bước thực hiện tiếp theo — duy nhất:** chạy một lần `TTM_D1_BRIDGE_V6_R1_R3_SINGLE_INTEGRATED_PROSPECTIVE_CORRECTION_SOURCE_QA` trên local frozen Git objects để sinh candidate SHA-256 và receipt; một người kiểm tra độc lập đánh giá cả sửa guard/seed lẫn category skeleton admission, sau đó trả **một GO/HOLD thiết kế**. Không tạo handoff/commit hoặc chạy thí nghiệm khi chưa có owner decision.

**Khóa bảo toàn:** `D1_BRIDGE_SCIENCE=HOLD` · `D1_EXISTING=HOLD_UNMODIFIED` · `TEST_Q1Q2=SEALED` · `FC01_EXPLORATORY=CLOSED_PASS_SCOPED` · `FC02=NOT_OPENED` · `GPU=0` · `TRAINING=0` · `INFERENCE=0` · `MAIN=UNCHANGED` · `LINEAGE=L0021_UNMODIFIED`.
