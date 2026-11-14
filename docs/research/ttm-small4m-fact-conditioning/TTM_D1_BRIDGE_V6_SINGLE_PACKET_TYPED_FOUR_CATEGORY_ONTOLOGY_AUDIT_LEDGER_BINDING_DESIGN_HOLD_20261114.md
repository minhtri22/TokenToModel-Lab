# TTM-Small-4M D1 Bridge V6 — Một gói sửa đổi ontology bốn nhóm và ràng buộc ledger–receipt

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V6_SINGLE_PACKET_FOUR_CATEGORY_TYPED_ONTOLOGY_AND_LEDGER_TO_RECEIPT_AUDIT_BINDING_SOURCE_AMENDMENT_NO_GPU`  
**Ngày:** 14/11/2026 · **Mode:** `SOURCE_ONLY / DESIGN_ONLY / NO_GPU / NO_TRAIN / NO_INFERENCE / NO_PRIVATE_GOLD`  
**Owner one decision:** `V6_DESIGN=HOLD_PENDING_DISTINCT_V6_SOURCE_REVIEW` · `D1_BRIDGE_SCIENCE=HOLD`  
**Machine source contract:** `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V6_SINGLE_PACKET_TYPED_FOUR_CATEGORY_ONTOLOGY_AUTHENTICATED_LEDGER_SOURCE_CONTRACT_20261114.json`.

## 1. Đóng tiếp nhận V5, không sửa V1–V5

Reviewer V5 đọc 8/8 Git blob tại frozen HEAD `0b7205093e70cc6473244a23d2a20ead568452c1`; **`HOLD_REVISE_BEFORE_PREREG`**, R1/AM01 và R5/AM05 HOLD, R2/AM02, R3/AM03, R4/AM04, R6/AM06 PASS **mức thiết kế**, 0 FAIL. Hai issue mới là `D1V5-N01` (ontology→4 category/action slot không đầy đủ) và `D1V5-N02` (thiếu binding giữa pre-read ledger và signed receipt, HMAC xác minh AST, crash không signer).

Hai tệp độc lập đã được lưu **nguyên byte** trên GitHub (Git blob SHA-1 đối chiếu với bytes upload):
- `docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V5_DISTINCT_INDEPENDENT_SOURCE_REVIEW_20261114.md`; uploaded SHA-256 `4dd7c89592ce6dad9c1617b0afd28b7ea7fe48d78ae3b35bce20db0a38f59f86`, Git blob `e8f95443e2db80ad95e7f698a0499e968ca3086b`.
- `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V5_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json`; uploaded SHA-256 `32ec96b36df27b122deda36513810d46aadf2d62b2e7ba13910d739c722c7c73`, Git blob `ea56f20c7784db6aa8bf2bb99af36ae61ba55c95`.

Bốn category **chính xác từ thiết kế D1 Bridge V1**, không suy đoán tên mới: `entity_location`, `causal_reasoning`, `rule_constraint`, `goal_persistence`, source Git blob SHA-1 `a5cd0dbd4167bdc53454847a25afcf317c94226b`. V6 là phiên bản **mới**, không overwrite V1–V5, không chỉnh frozen source hoặc TEST.

## 2. AM01 — Ontology hành động có type, miền trạng thái hữu hạn, từng category và scoring slots

**Điều khoản mới:** so sánh lexical aliases phải diễn ra **sau** khi mỗi action có type, precondition, postcondition, temporal guard và goal predicate rõ ràng. Hệ trạng thái hữu hạn ứng viên V6 có:
- Agent `a0,a1`, item `i0,i1`, location `l0,l1`, device `d0,d1`, trigger `g0,g1`; thời gian có thứ tự `BEFORE_T0<T0<T1<T2` cùng marker `NONE` (không bị lẫn với T0).
- Fluents typed: `location(agent)`, `location(item)`, `holder(item)`, `power(device)`, `trigger_fired`, `scheduled_at`, `linked_trigger`, `protected_until`, `defer_until`, `current_time`.
- Invariant `holder(item)!=NONE ⇒ location(item)=location(holder(item))`; clock/event total deterministic, không có causal link tự phát.
- Quy tắc priority: protection interval **chặn TRANSFER**; nếu hai action xung đột cùng priority, không có một action hợp lệ duy nhất hoặc không chứng minh được state reachability → `INVALID_ORACLE_HOLD`.

**Sáu action IDs V5 bảo toàn**, nhưng từ mô tả lời đã chuyển sang typed preconditions và effects trong machine contract:

| Action | target_id | qualifier_id | Điều kiện và tác động |
|---|---|---|---|
| `RELOCATE` | item | destination location | Item đang unheld và tại agent; dời location, holder giữ nguyên |
| `CARRY` | item | destination location | Item unheld tại agent; đưa holder về agent và di chuyển agent/item đến destination |
| `TRANSFER` | item | recipient agent | Chỉ khi item do agent giữ và protection đã hết; đổi holder sang recipient |
| `RETAIN` | item | until time | Agent đang giữ item; thiết lập protected_until ít nhất bằng thời gian kết thúc |
| `WAIT` | trigger | không có qualifier | Trigger chưa xảy ra và có lịch tương lai; hoãn action đến lúc đó |
| `ACTIVATE` | device | không có qualifier | Device đang OFF; chuyển ON, kích hoạt linked trigger nếu đã khai báo |

Tất cả cùng tuple `(agent_id,verb_id,target_id,time_id,qualifier_id)`; mỗi action có **type và slot schema riêng**. `time_id` luôn biểu diễn trong **generated text**, không trích từ gold để điền chỗ thiếu. Với qualifier absent, dùng canonical `NONE` ở tuple, parser cần quy định khi nào surface không chứa qualifier và từ đồng âm đa token không được gây nhầm vị trí. V6 không tự nhận đã có parser thực.

**Ma trận 4 category, 4 EVAL skeleton/category, cố định 16 OOD skeleton:**

| Category (nguồn V1) | Canonical actions hợp lệ | Task-relevant khác biệt cần kiểm |
|---|---|---|
| `entity_location` | RELOCATE, CARRY, TRANSFER | Item location vs holder/recipient; qualifier là destination hoặc recipient |
| `causal_reasoning` | ACTIVATE, WAIT | Device→trigger causal chain vs hoãn đến scheduled trigger |
| `rule_constraint` | TRANSFER, WAIT, RETAIN | Protection guard và priority quyết định action có thể thực thi ngay |
| `goal_persistence` | RETAIN, WAIT, CARRY | Duy trì mục tiêu qua thời gian/distracting transfer, không làm mất TIME |

**Bốn fixture synthetic, KHÔNG thuộc TRAIN/EVAL/gold:** `CAT01` same initial world nhưng goal chuyển từ item-at-destination-unheld sang item-at-destination-held-by-agent, oracle RELOCATE/CARRY và holder effect khác; `CAT02` device OFF, causal ACTIVATE vs WAIT tới trigger đã scheduled; `CAT03` protected_until T1 chặn transfer ở T0, WAIT vs TRAIN-only counterfactual protection hết trước T0 cho TRANSFER; `CAT04` giữ holder qua T2 với distracting request vs WAIT khi chỉ có pending trigger. Mỗi fixture trong JSON chứa input state, A/B, expected canonical tuple, reachable witness dạng mô tả. Chúng **chưa phải chứng cứ checker đã xác minh**.

Alias hợp lệ `move≡relocate`, `give≡hand over`; `move` và `carry` khác semantics **chỉ khi** có cùng input/cùng states mà khác reachable task-policy/goal/time do causal dependency. Action ID khác nhau **không đủ** thành structural OOD; inert event label và unreachable change không đủ. Nếu category không thể được biểu diễn bởi ontology đã khóa, **HOLD TOÀN D1**, không được bỏ một category rồi vẫn tuyên bố gate 4/4.

**Cổng thực thi còn thiếu:** typed action oracle code, model checker, đủ 4 TRAIN+4 OOD skeleton mỗi category, nonoverlap, fixture positive/negative QA, unique gold A/B và parser grammar độc lập. Tất cả `NOT_IMPLEMENTED / NOT_EXECUTED`.

## 3. AM05 — Chứng minh liên kết AST↔ledger↔receipt theo ranh giới tin cậy đã khai báo

**Threat model:** EVAL AST có thể mã hóa gold và entropy thấp; TRAIN/VAL AST cũng không phát raw hash khi chưa đánh giá quyền. V6 không cố biến HMAC thành zero-knowledge proof: hai custodian và auditor là **trusted parties** với quyền cách ly thực tế sẽ phải chứng minh ở preexec.

**Commitments (dự kiến, không dùng khóa thật trong V6):**
- Một batch `audit_id`: **16 random bytes → đúng 32 ký tự ASCII hex lowercase**, 32 UTF-8 bytes khi nối message, không phải 16.
- Mỗi bên TRAIN/VAL và EVAL có **khóa HMAC-SHA256 ngẫu nhiên 32 byte khác nhau**, custodian giữ kín, không reuse.
- AST bytes typed finite → Unicode NFC → RFC8785 JCS; cấm floats/NaN và field không biết, thứ tự entry ổn định.
- Message HMAC byte-exact: `ASCII("TTM_D1_V6_AST_COMMIT_V1") || 0x00 || uint32_BE(32) || ASCII_HEX(audit_id) || uint64_BE(len(AST_JCS_bytes)) || AST_JCS_bytes`. Tính digest riêng cho `TRAIN_VAL_AST` và `EVAL_AST`.
- Không công khai raw AST SHA, key, private witness, per-example match/error counts hoặc gold. Định danh signer phải pin trước khi audit.

**Pre-audit manifest và ledger root:** khi chưa mở AST private cho auditor, phát hành một immutable public manifest gồm ít nhất `protocol_version, source_commit, audit_id, train_val_ast_hmac, eval_ast_hmac, checker_sha256` và các key IDs ký của custodian/auditor. Tính `ledger_root_sha256=SHA256(JCS(immutable_public_manifest))`, anchor append-only độc lập và kiểm readback **trước** một audit. V6 không khẳng định đã tồn tại ledger bất biến.

**Private exact-AST binding để auditor kiểm được mà không giữ HMAC key:** mỗi custodian ký **private attestation** gắn `audit_id, ledger_root, side, HMAC, private_SHA256(AST_JCS), JCS byte_count, custodian signer ID` bằng Ed25519. Auditor nhận **đúng byte AST** qua kênh riêng, xác minh chữ ký và danh tính custodian, recompute SHA256(AST bytes) **trong enclave**, đối chiếu byte_count/private hash, bảo đảm HMAC trong attestation trùng public manifest/ledger. Trên cơ sở **tin tưởng custodian tính HMAC đúng từ cùng AST bytes**, auditor có thể chấp nhận binding mà không được cấp secret HMAC. Đây là *authenticated custodian assertion*, **không phải public cryptographic proof of HMAC correctness**. Nếu custodian không được tin cậy, `HOLD`.

**Auditor signed terminal receipt:** biên nhận public phải chứa đầy đủ `audit_id, protocol_version, source_commit, checker_sha256, ledger_root_sha256, train_val_ast_hmac, eval_ast_hmac, audit_schema_version, signer_key_id, decision=PASS/FAIL/UNKNOWN` và chữ ký Ed25519 phủ lên JCS payload **ngoại trừ signature**. Public verifier xác minh chữ ký, pinned key, ledger root readback, tất cả trường khớp manifest đã anchor. Thiếu ledger root hoặc một trong hai HMAC → `HOLD`.

**State machine đóng:** `DRAFT → FROZEN_PREAUDIT_LEDGER → IN_PROGRESS_SINGLE_AUDIT → SIGNED_PASS / SIGNED_FAIL / SIGNED_UNKNOWN`. Ngoài ra `ABORT_NO_SIGNER_NO_RECEIPT` là terminal **HOLD**: nếu máy hỏng hay khóa signer không hoạt động, **không được giả tạo signed UNKNOWN**. Trong mọi trường hợp, **không có signed terminal receipt hợp lệ = HOLD**. Duplicate/replay, thay manifest, adaptive query, tự đổi batch hoặc retry mà không có prospective amendment → HOLD.

### Synthetic crypto vectors (không phải dữ liệu nghiên cứu)

V6 JSON có test vector hoàn toàn công khai với HMAC key giả lập `00 01 ... 1f`, audit ID `00112233445566778899aabbccddeeff` và AST JCS giả `{"entries":[],"schema":"V6_SYNTHETIC_TEST"}`.

- HMAC-SHA256 vector: `0836503a52f9c9eca5178d16c11fc120ae4ad17a99045d1f4cec9609f7c0acdb`
- Ledger-root SHA256 vector: `57dfb51345d52fba88566be6882ad64650ca7a5c8694609dce1a25d4c7d21e42`
- Ed25519 public-key và signature hex đầy đủ nằm trong JSON. **Khóa của vector được công khai, tuyệt đối không dùng trong audit thật.**

Vector là minh họa tối giản cho encoding/signing ở lớp source contract, **không chứng nhận** hệ custody, ACL hoặc crypto runtime. Test vectors full production schemas, key lifecycle, manifest anchoring, tampering, replay, deny-probes và failure/absent-receipt vẫn là **future independent QA**.

## 4. AM02, AM03, AM04, AM06 giữ nguyên V5 PASS có phạm vi

Không sửa tính đo primary canonical-action constrained generation có TIME; parser ≥64 positives đúng/≥64 negatives không false-accept vẫn là **future QA**. Giữ **12 seed** `20261120..20261201`; `D_s=Σ_{256}(success_C−success_B)` nguyên có dấu, tie zero **không dương**, exact sign test `k≥10/12`, `p(k=10)=79/4096`, không suy ra mean effect ≥10pp hay population-wide OOD.

Giữ integer category gates: `Σ_s D_s≥308`, tất cả bốn category C−B≥0, ít nhất ba category ≥39 delta, mỗi category C correct≥192. Không tự thiết kế hidden gate theo từng skeleton; báo đầy đủ heterogeneity.

Giữ `B_CF_MLE` vs `C_CF_CONTRAST` là **contrastive training package** gồm loss + TRAIN-only negative supervision + extra compute, không phải loss-only/equal FLOPs. Candidate tham số V5 có nguồn FC01 `λ=.2, τ=1, K=4`; AdamW `lr=1e-4, betas .9/.95, decay .1, grad_clip1`, warmup16 cosine xuống `1e-5`, 256 steps/arm/seed. Kế hoạch 36 arm-runs, **9216 optimizer updates**, **18432 generations**; Free T4 $0 chưa xác minh. Không sửa tham số sau outcome, không thêm nhánh đối chứng thứ tư.

## 5. Source-only matrix và một phán quyết

| Gate | Trạng thái |
|---|---|
| V5 reviewer 8/8 Git blob matching, HOLD R1/R5 | `ACCEPTED` |
| V6 typed category/slot coverage + synthetic witnesses | `NEW_SOURCE_CONTRACT` |
| V6 authenticated ledger root + both HMAC bindings + absent-receipt policy | `NEW_SOURCE_CONTRACT` |
| AM02/03/04/06 | `UNCHANGED_V5_DESIGN_PASS_SCOPED` |
| Actual AST checker, parser, custodians, crypto keys/ACL/ledger | `NOT_IMPLEMENTED/NOT_EXECUTED` |
| Data rights/PII/nonoverlap, stochastic seed QA, resume, Free T4 | `NOT_VERIFIED` |
| V6 distinct independent source/design review | `PENDING` |
| Science/GPU/TEST Q1Q2 | **`HOLD / NO_GPU / SEALED`** |

**Owner single design decision** `V6_DESIGN=HOLD_PENDING_DISTINCT_V6_SOURCE_REVIEW`; `D1_BRIDGE_SCIENCE=HOLD`. Chưa tạo data mới, chưa train, chưa model inference, chưa khóa public/private ledger thật, chưa merge main. V1–V5 và toàn bộ nghiên cứu FC01 exploratory được giữ nguyên.

**Bước thực hiện tiếp theo duy nhất:** `TTM_SMALL4M_D1_BRIDGE_V6_DISTINCT_NEW_CHAT_SOURCE_ONLY_INDEPENDENT_DESIGN_REVIEW_SINGLE_GO_HOLD_NO_GPU` — một reviewer khác đánh giá R1/R5 và các phần PASS kế thừa trước khi quyết định GO/HOLD thiết kế; design GO không phải science GO.
