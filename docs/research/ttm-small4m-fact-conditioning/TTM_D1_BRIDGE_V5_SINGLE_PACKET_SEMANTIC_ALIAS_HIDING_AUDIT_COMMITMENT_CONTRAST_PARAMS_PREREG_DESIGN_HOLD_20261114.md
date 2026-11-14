# TTM-Small-4M — D1 Bridge V5: một gói sửa đổi sau phản biện V4

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V5_SINGLE_PACKET_SEMANTIC_ALIAS_HIDING_AUDIT_COMMITMENT_CONTRAST_PARAMS_PREREG_SOURCE_AMENDMENT_NO_GPU`  
**Ngày:** 2026-11-14  
**Loại:** SOURCE ONLY · DESIGN ONLY · **V5 mới, không sửa V1–V4**  
**Owner decision:** `V5_DESIGN=HOLD_PENDING_DISTINCT_V5_SOURCE_REVIEW` · `D1_BRIDGE_SCIENCE=HOLD`  
**Machine contract:** `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V5_SINGLE_PACKET_SEMANTIC_ALIAS_HIDING_COMMITMENT_CONTRAST_PARAMS_SOURCE_CONTRACT_20261114.json`

## 1. Evidence intake, frozen origins

Reviewer V4 tại frozen HEAD `1c923c0dc1a064411190392612e9d2475486bd2c` đã kiểm tra metadata 7/7 Git blob và kết luận **`HOLD_REVISE_BEFORE_PREREG`** (R1/R5/R6 HOLD, R2/R3/R4 PASS phạm vi thiết kế, 0 FAIL). Cụ thể có `D1V4-N01` action aliases, `D1V4-N02` commitment bí mật, `D1V4-N03` replay, `D1V4-N04` tham số package; kế thừa 17 issues đã kiểm từ V2/V3.

Tệp review đính kèm đã được owner kiểm SHA-256 **trên byte gốc**, commit đúng Git blob sau khi giữ cả LF cuối: báo cáo `8fd3ff6469403c9abb4cdc7672f9206c29329adf29388e8ca78fbb0df0eec47f`, JSON receipt `2bdb82bb4e585c158c291c7b48838985249a7063a588af71b8e32f333dcedd94`. Lưu riêng `docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_DISTINCT_INDEPENDENT_SOURCE_REVIEW_20261114.md` và `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json`. Đây là AI review ở chat độc lập **tự khai báo**, không phải kiểm định nhân sự độc lập ngoài hệ thống.

V5 chỉ giải quyết các blocker thiết kế; **chưa tạo TRAIN/VAL/EVAL/gold, AST checker, parser, sampler/runner code hoặc một khoa học run nào**.

## 2. AM01 — Canonical action ontology và surface aliases (`D1V4-N01`)

Hai khái niệm phải được giữ **riêng**:
- **Canonical task action** là một ID hành động với typed precondition/postcondition trên world-state và TIME/goal; tên action không phải biến đồng nghĩa.
- **Surface alias** là cách diễn đạt bằng văn bản ánh xạ **duy nhất** tới một canonical ID, không được dùng semantic similarity tự đoán.

Ứng viên ontology V5, trước khi sinh dữ liệu: `RELOCATE` (đổi location, không đổi holder), `CARRY` (holder về agent và di chuyển cùng item), `TRANSFER` (đổi holder về recipient), `RETAIN` (duy trì holder qua interval), `WAIT` (hoãn cho tới trigger), `ACTIVATE` (đổi trạng thái device). Mỗi action kèm domain, agent/target, thời gian, typed state effects trong JSON. Aliases khóa:
- `RELOCATE ← {move, relocate}`; `CARRY ← {carry}`
- `TRANSFER ← {give, hand over}`; `RETAIN ← {keep, retain}`
- `WAIT ← {wait, defer}`; `ACTIVATE ← {activate, turn on}`.

Đây là **bộ từ vựng ứng viên** của V5, không phải ontology đã được QA. Bất kỳ overlap giữa các ID hoặc từ đa nghĩa đều phải `UNKNOWN/HOLD`; không silently mở lexicon sau khi có EVAL. Biến đổi alpha-rename thực thể và **alias trong cùng một ID** là tương đương; khác ID **chưa đủ** là OOD. Chỉ chứng nhận task-relevant structural OOD nếu checker có **reachable counterexample** dưới cùng input/state/condition A/B cho thấy action/goal/time khác do **causal/temporal/priority/guard dependency**, không phải đổi nhãn từ.

Fixtures synthetic ngoài EVAL: `move↔relocate` cùng ID phải REJECT_OOD; `give↔hand over` cũng vậy; `move↔carry` chỉ DIFFERENT khi có witness reachable cho khác biệt holder/state; đổi event log, self-loop trơ hoặc khác unreachable states không đủ; động từ ambiguous phải HOLD. Mọi TRAIN/VAL–EVAL equivalence không chắc chắn → HOLD toàn batch, không thay EVAL sau outcomes.

**Hạn chế:** miền tác vụ phải biểu diễn được trong ontology cố định; nếu một category cần action mới, phải amendment trước data freeze, không vá hành động trong runtime.

## 3. AM02–AM04 — Giữ những nội dung đã PASS thiết kế

**AM02:** Primary là `CANONICAL_ACTION_CONSTRAINED_GENERATION_ACCURACY`, không phải viết văn tự do. Tuple chấm `agent,verb,target,time,qualifier`; grammar `AGENT VERB TARGET TIME (QUALIFIER)?`, **TIME tường minh** trong chính generated text, không điền bằng gold. Parser dùng typed lexicon/aliases AM01, không substring matching, alias đa nghĩa reject. Greedy, prompt ≤224 special-inclusive, generation ≤32 special-inclusive, 256 context. Một family đúng iff cả điều kiện A/B đúng; mọi invalid→0, mẫu số 256. Independent parser QA **chưa thực hiện**, khi triển khai phải có ≥64 synthetic positives đúng 64/64 và ≥64 adversarial negatives với 0 false accepts, các giới hạn rõ bằng SHA.

**AM03:** 12 seed `20261120…20261201`, `D_s` integer signed, positive iff `D_s>0`, tie 0 nonpositive. Exact one-sided sign test `k≥10/12`, p tại k=10 `79/4096` (α=.05), phạm vi chỉ seed randomness trên **16 fixed OOD skeletons**. Seed iid/variance **chưa được chứng minh** và không kiểm định riêng mean≥10pp.

**AM04:** Global `ΣD_s≥308`; category C−B≥0 cả 4/4, ít nhất 3/4 đạt Δcount≥39; C correct≥192/category. Ngưỡng mô tả được khóa trước outcome, skeleton heterogeneity báo cáo từng skeleton, **không** tuyên bố 16/16 skeleton đều cải thiện.

## 4. AM05 — Hiding commitment, audit session và chống replay (`D1V4-N02/N03`)

**Threat model:** EVAL AST là **gold-adjacent và có thể entropy thấp**. Raw `SHA256(EVAL_AST)` hay plaintext AST không thể công khai như chứng cứ kín: người ngoài có thể thử dictionary các AST khả dĩ. Người giữ gold (eval custodian) và isolated auditor là **trusted parties** tách quyền khỏi trainer; không gọi AST projection là non-sensitive.

**Hiding construction (đặc tả, chưa tạo khóa):**
- Dữ liệu AST chuẩn hóa typed schema, không float/NaN, Unicode NFC, sắp xếp records cố định và tạo bytes canonical bằng **RFC 8785 JCS**.
- Custodian tạo khóa HMAC-SHA256 **32 byte CSPRNG riêng tư** và `audit_id` ngẫu nhiên 16 byte (hex) cho **một batch đã khóa**.
- `EVAL_AST_commit = HMAC_SHA256(secret_key, DOMAIN || uint32_BE(len(audit_id)) || audit_id || uint64_BE(len(canonical_AST_bytes)) || canonical_AST_bytes)`, DOMAIN = `TTM_D1_V5_AST_COMMIT_V1` với delimiter byte 0x00; actual byte encoder và vectors phải được QA độc lập.
- Công khai **chỉ** digest keyed, ID phiên và thông tin metadata không nhạy cảm đã được cho phép; không công khai khóa, raw SHA-256, AST, gold, mapping, counterexample hoặc per-family match counts. Nếu key bị lộ, tính giấu của commitment **không còn được đảm bảo**; không gọi đây là zero-knowledge proof.

**One-batch/one-shot audit:** trước khi auditor đọc private AST, khóa append-only ledger với `audit_id, protocol HEAD, TRAIN_VAL_AST commitment, EVAL_AST keyed commitment, checker SHA`. Một batch duy nhất, một phép audit kiểm TRAIN–EVAL và VAL–EVAL; không phát hành API query tham số hóa. Duplicate session, replay, thay version/checker/batch, crash, UNKNOWN hoặc chữ ký không hợp lệ đều **HOLD**; không tự retry bằng batch khác. Muốn mở lại phải amendment trước outcome và owner decision nguyên gói, không micro-permit.

**Authenticated receipt:** auditor ký Ed25519 trên JCS các trường public (trừ `signature`). Public key/identity được pin **trước** khi mở private EVAL; check signature, `audit_id`, key, checker/source binding và replay state. `decision` chỉ `PASS/FAIL/UNKNOWN`, signed UNKNOWN vẫn **HOLD**; tuyệt đối không đổi FAIL thành PASS. Private counterexample chỉ nằm trong custody của auditor. **Hiện tại HMAC key, Ed25519 key, ACL/deny-probes và chữ ký đều `NOT_CREATED/NOT_EXECUTED`**.

## 5. AM06 — Khóa tham số `contrastive training package` (`D1V4-N04`)

**Estimand bất biến:** C−B là hiệu ứng **gói huấn luyện** gồm loss contrastive, nhãn giám sát âm TRAIN-only và thêm compute. B/C cùng parent, TRAIN bytes nền, episode order, số bước optimizer và CE token-slot; **không** khẳng định objective-only, equal-FLOPs hoặc equal-supervised-information. Không thêm arm thứ tư.

Để loại bỏ việc lựa hyperparameter sau khi có outcomes, V5 **sao chép minh bạch các tham số đã được prereg FC01 ngày 12/11/2026**, source Git blob `af80eddfb2175b58a90c2a9761f0ed339e03678a`:

| Trường | Đề xuất khóa V5 |
|---|---|
| Optimizer | AdamW, `lr=1e-4`, betas `(0.9,0.95)`, weight decay `0.1`, grad clip `1.0` |
| Schedule | warmup 16 updates → cosine xuống `1e-5` ở step256; không VAL-based checkpoint picking |
| Batch | 16 ×256 tokens/update, accumulation 4 microbatch ×4 seq; core 12, synthetic 4 |
| Numeric / budget | FP32; 256 optimizer steps/arm/seed; 1.048.576 LM token-slots/arm/seed |
| Contrast C | `lambda=0.2`, `tau=1.0`, 4 positive pairs/step, **1 TRAIN negative đối nghịch mỗi pair** |
| Candidate log probability | mean logprob/token trên completion, không tính prompt |
| Negative exposure | 4 extra negatives/update C, 1024/seed C; B không có extra negative contrast term |
| Negative source | continuation của **điều kiện fact đối nghịch trong cùng TRAIN family**; cấm VAL/EVAL/TEST |
| Failure | thiếu negative chuẩn, sai equal BPE length, NaN/OOM, seed/rights error → `HOLD`, không tự đổi giá trị |

Công thức ứng viên: `L_C = L_CE + 0.2 × mean_i softplus(−(mean_logp(y+|x)−mean_logp(y−|x))/1.0)`, `i=1..4` mỗi update. Các con số **có nguồn từ FC01**, nhưng sự phù hợp với cấu trúc OOD và source runner V5 cần reviewer độc lập; chúng **chưa được triển khai hoặc chạy**.

**RNG derivation rõ byte:** cho `seed` tám chữ số ASCII và namespace trong bảng cố định, lấy SHA256 của bytes UTF8 `TTM_D1_BRIDGE_V5_RNG_V1|` nối ASCII seed, ký tự `|` và namespace; lấy 8 byte đầu (big-endian), mask 63 bit, zero→1. Namespaces: `shared_B_C_sampler`, `contrast_negatives_C`, `dropout_B_C`, `augmentation_if_present`, `initialization_if_present`. Các stream giữ trạng thái riêng, không để sampler âm làm dịch B/C episode order. Future source QA cần cùng seed→64 quyết định sampler giống SHA và khác seed→stochastic trajectories thực sự khác; nếu không có biến thiên ngẫu nhiên thật, **HOLD suy luận sign-test**. Không tuyên bố các seed iid chỉ vì khác số.

**Future implementation:** parent P02 STEP1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, T1 BPE manifest `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; runner/negative-sampler/parser/new-data SHA chưa có. Phải QA gradient/negative construction, resume **nonzero AdamW moments**, RNG/order, atomic snapshot và fail-closed bad SHA. Kế hoạch 12 seed×3 arms =36 arm-runs, **9.216 optimizer updates, 18.432 generations**, Free T4 / paid USD 0 **chưa chứng minh khả thi**.

## 6. Phân xử V5 và điều kiện tiếp theo

| Đầu mục | Trạng thái |
|---|---|
| Chứng cứ V4 reviewer 7/7 Git blob + SHA-256 upload | `PASS_SOURCE_CUSTODY` |
| V5 AM01 alias/ontology | `NEW_PROSPECTIVE_SOURCE_CONTRACT` |
| V5 AM05 hiding HMAC, one-shot audit, Ed25519 | `NEW_PROSPECTIVE_SOURCE_CONTRACT` |
| V5 AM06 exact numeric FC01-derived params / RNG | `NEW_PROSPECTIVE_SOURCE_CONTRACT` |
| AM02–AM04 | `UNCHANGED_V4_SCOPED_DESIGN_PASS` |
| V5 external independent source review | `PENDING` |
| Actual AST checker, parser, HMAC key/ACL, runner and $0 T4 | `NOT_EXECUTED/NOT_VERIFIED` |

**Owner decision:** `V5_DESIGN=HOLD_PENDING_DISTINCT_V5_SOURCE_REVIEW`, `D1_BRIDGE_SCIENCE=HOLD`. **Không tạo** TRAIN/VAL/EVAL/gold, không truy cập TEST/Q1Q2, không GPU, training, inference, không merge main. V1–V4 là các bản lịch sử bất biến.

**Bước thực hiện tiếp theo duy nhất:** `TTM_SMALL4M_D1_BRIDGE_V5_DISTINCT_NEW_CHAT_INDEPENDENT_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU`. Reviewer phải thẩm tra cross-action ontology, HMAC confidentiality/session state machine và nguồn gốc/khả năng tái lập exact contrast params; đưa **một GO/HOLD design**, không phải science release.
