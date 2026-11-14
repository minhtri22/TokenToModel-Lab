# D1 Bridge V4 — Gói sửa đổi tiền đăng ký duy nhất sau phản biện V3

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V4_SINGLE_PACKET_TASK_RELEVANT_OOD_PARSER_AUDITOR_AND_CONTRAST_CONTROL_PREREG_SOURCE_AMENDMENT_NO_GPU`  
**Ngày:** 14/11/2026  
**Loại:** `NEW_VERSION_SOURCE_CONTRACT_DESIGN_ONLY`; V1/V2/V3 giữ nguyên.  
**Phán quyết owner:** **`V4_DESIGN=HOLD_PENDING_DISTINCT_V4_SOURCE_REVIEW`**, **`D1_BRIDGE_SCIENCE=HOLD`**.  
**Machine-readable hợp đồng:** `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_SINGLE_PACKET_TASK_RELEVANT_OOD_PARSER_AUDITOR_CONTRAST_PREREG_DESIGN_HOLD_20261114.json`.

## 1. Bảo toàn kết quả phản biện, không chỉnh sửa hậu nghiệm

Reviewer V3 đã đọc 7/7 Git blob metadata tại frozen scientific HEAD `8f0714b29c98ca9be7c7444f964267faea4efb76`, kết luận **`HOLD_REVISE_BEFORE_PREREG`**: R1/R2/R5/R6 HOLD, R3/R4 PASS **mức thiết kế**, tổng **2 PASS / 4 HOLD / 0 FAIL**. Sáu phát hiện mới `D1V3-N01`, `D1V3-N02`, `D1V3-N03`, `D1V3-N04`, `D1V3-N05`, `D1V3-N06`, cộng 11 issue `D1V2-01`…`D1V2-11` đã được giữ nguyên trong machine contract V4.

Chứng cứ V3 do reviewer mới tạo (GitHub đã lưu **trùng byte** so với tệp được nhận): Markdown SHA-256 `e806d03741c50d75a5e0ad910a1700c511c8057450384a5cad22cc94a96fd441`, JSON SHA-256 `1a7421f992d80e778152f0a03434c358a4251f66716c5e910aefb890ded530c7`. Tương ứng ở `docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_DISTINCT_INDEPENDENT_PREREG_SOURCE_REVIEW_20261114.md` và `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json`.

**Đây là thay đổi prospective trước mọi kết quả D1 Bridge**. V4 không sinh TRAIN/VAL/EVAL/gold; không inference, GPU, training, chỉnh old D1 hoặc mở TEST. Một thiết kế PASS sau này không đồng nghĩa permission chạy khoa học.

## 2. AM01 — Tính mới OOD liên quan đến nhiệm vụ, không phải nhãn trace (D1V3-N01)

Thay tiêu chuẩn V3 `strong labeled bisimulation của mọi internal event` bằng **task-relevant decision-policy semantics**. Tập quan sát định nghĩa trước gồm đúng `agent, verb, target, time, qualifier, goal_satisfaction, condition_dependent_decision` sau typed role canonicalization. Nhãn log/bookkeeping, guard-evaluation không làm đổi quyết định, id sự kiện tùy ý và self-loop trơ **không** được coi như khác biệt nhiệm vụ.

Với mỗi skeleton TRAIN/VAL/EVAL dự kiến tạo hệ chuyển trạng thái **hữu hạn, total và deterministic** trên tập *admissible initial states × condition A/B* đã khóa. So theo cùng input alphabet, typed variable alignment và observable action/goal policy. Bất kỳ khó khăn về ánh xạ domain, trạng thái khả đạt chưa chứng minh, sự ngẫu nhiên không khai báo hoặc trường hợp undecidable đều `UNKNOWN→HOLD`.

**Chứng minh khác biệt task-relevant cần đồng thời**: (i) canonical causal-dependency skeleton không isomorphic chỉ bởi alpha rename/literal đổi tên; (ii) tìm được **reachable counterexample** làm đổi canonical action/time hoặc goal satisfaction dưới cùng một input đã căn chỉnh; (iii) witness do thay đổi priority/causal/temporal/guard thực sự, không chỉ thay action word. `same final decision policy + different inert trace` bắt buộc **REJECT_OOD**. Khác biệt chỉ trên unreachable states cũng không đạt chứng minh.

Kiểm TRAIN–EVAL và VAL–EVAL ở toàn bộ bốn nhóm × bốn EVAL skeleton = **16 cấu trúc dự kiến**. Chưa sinh skeleton, chưa có checker thật; `ACTUAL_NONOVERLAP=NOT_EXECUTED`. Fixtures synthetic ngoài EVAL phải bao phủ alpha rename, log-only trace, self-loop trơ, priority flip reachable, temporal/action-time flip reachable, negation và incomplete finite domain. QA thực được khóa trước EVAL về sau; không chấm PASS theo mô tả chữ.

**Giới hạn diễn giải:** đây là *task-policy structural OOD* tương đối với controlled TRAIN/VAL grammar; không tuyên bố khái quát toàn bộ suy luận hoặc chưa gặp trong pretraining P02.

## 3. AM02 — Parser chấm hành động có TIME tường minh (D1V3-N02)

V3 ghi `time_id` trong scored ontology nhưng thiếu vị trí TIME trong EBNF. V4 chọn **giữ `time_id` và buộc model sinh TIME**. Một câu trả lời hợp lệ có dạng giới hạn:

`ACTION ::= AGENT SP VERB SP TARGET SP TIME (SP QUALIFIER)? TERMINAL?`

`TIME ::= FROZEN_TIME_PHRASE` từ lexicon typed SHA-pinned. Kể cả canonical time `NONE` cũng phải có **một cụm từ TIME tường minh**, không suy thời gian từ gold hay prompt để cứu model output. Mọi accepted surface phải ánh xạ **duy nhất một tuple chấm** `(agent_id, verb_id, target_id, time_id, qualifier_id)`; ambiguity→0. Gold A/B duy nhất và khác nhau có proof từ sealed task AST, witness chỉ thuộc metadata kín, không yêu cầu model lặp witness.

Parser phải từ chối phủ định, quote-only, wrong agent/target/time/condition, nhiều hành động, contradiction, prompt echo, EOS rỗng, truncation, special tokens sai và synonym ngoài lexicon. Normalization/từ đồng nghĩa và JSON grammar có SHA khóa trước test; không substring match, không dùng AI-rater override. Greedy `prompt≤224` token bao gồm special, `generated≤32` token gồm EOS, context 256. Family đúng chỉ khi **hai điều kiện A và B** đều sinh đúng; invalid→0, cố định 256 family per arm per seed.

**Tên phép đo không được quảng cáo quá mức:** `CANONICAL_ACTION_CONSTRAINED_GENERATION_ACCURACY` (độ chính xác sinh biểu thức hành động giới hạn), **không phải open-ended natural-language generation**. Báo parser compliance và các lỗi riêng. Với paraphrase: chỉ những biến thể được khai báo trước trong bounded grammar/synonym lexicon mới được nhận, các dạng khác tính 0 và trình bày là hạn chế. Fluency nếu chấm mù về sau chỉ secondary.

**Future source QA định lượng tối thiểu:** synthetic non-EVAL ≥64 legal canonical/synonym positives và ≥64 negatives đối kháng, **64/64 positive đúng**, **0 false accepts trên ≥64 negatives**, không ambiguity surface→canonical. Các con số này là *acceptance criterion khi lập parser*, không phải chứng cứ parser đã chạy. Phải QA độc lập, không tune trên real EVAL/gold. `PARSER_REAL=NOT_IMPLEMENTED`.

## 4. AM03–AM04 — Giữ nguyên PASS có phạm vi từ V3

Không thay đổi `12 seed`, không đổi giả thuyết fixed 16 skeleton, không đổi composite integer gates. `D_s=Σ_{256}(success_C−success_B)` là số nguyên có dấu; seed dương iff `D_s>0`, `D_s=0` không dương; exact one-sided sign test `k≥10/12`, `p(k=10)=79/4096≈0.019287`. `mean(d_s)≥.10` là **gate mô tả** chứ không phải inferential test của hiệu ứng +10pp.

Bảo toàn `Σ_s D_s≥308`, category C−B≥0 cả 4/4, ≥39 delta count ở ≥3/4, C correct≥192 trên mỗi category. Heterogeneity/cue shortcut theo từng skeleton bắt buộc báo cáo, nhưng không thêm ngưỡng posthoc và không suy ra cải thiện đồng đều trên 16 skeleton. Giả định 12 stream ngẫu nhiên độc lập **chưa có bằng chứng runtime**, nên `SEED_IID=NOT_VERIFIED`.

## 5. AM05 — Auditor xử lý AST như dữ liệu nhạy cảm gần gold (D1V3-N03)

V4 loại bỏ tuyên bố `EVAL_AST_ONLY` mặc nhiên không tiết lộ đáp án. Nếu AST chứa goal, transition hoặc canonical action, **auditor có khả năng suy ra gold** và bắt buộc được xem như một bên tin cậy có quyền *gold-adjacent*. Owner/trainer **không được** đọc EVAL_AST, EVAL_RAW/GOLD, mapping hoặc witness; auditor không trả counterexample cho trainer.

Luồng dự kiến **một batch được khóa, một phép audit**, không mở giao diện query overlap tương tác hay lặp lại tùy ý: chủ TRAIN xuất commitment TRAIN/VAL AST; custodian độc lập xuất commitment EVAL AST; trusted isolated auditor chỉ được đọc hai nguồn này dưới ACL riêng, dùng checker AM01 đã khóa SHA; witness có thể lưu riêng trong kho của auditor nhưng owner chỉ nhận **PASS/FAIL/UNKNOWN + source/checker commitments + authenticated signature**. Không đưa individual match counts, raw AST, gold, mapping hoặc trace ra owner/GitHub; bảo vệ chống side-channel từ adaptive queries. Signature (dự kiến Ed25519) phải có key public được pin **trước** khoa học; hiện **chưa tạo khóa, chưa xác minh ACL/chữ ký**.

Mọi ambiguity, overlap, quyền đọc quá mức, mất custody, không có signed receipt hoặc không thể chứng thực key đều `HOLD`. Cần proof quyền TinyStories và dữ liệu synthetic mới, PII/copyright negative QA, kiểm denied reads, nguồn shared templates; **không** tuyên bố ACL đã PASS.

## 6. AM06 — Đổi đối tượng quy kết: contrastive *training package* (D1V3-N04/N05/N06)

Chọn **một trong hai phương án mà reviewer đề nghị**: **không bổ sung arm thứ tư**, giữ A/B/C và 36 planned arm-runs, nhưng sửa **primary estimand**:

`C_CONTRASTIVE_TRAINING_PACKAGE_MINUS_B_CF_MLE`

Package C bao gồm **loss contrastive + negative supervised pairs + extra forward/compute**. B/C cùng parent, dữ liệu TRAIN cơ sở, thứ tự episode, số optimizer updates, nhưng **không** được gọi equal supervised information / equal compute. Không có bằng chứng phân lập *loss-only* hoặc causal effect riêng của một yếu tố; muốn claim đó phải mở nghiên cứu khác với exposure-matched control và prereg mới, không mượn kết quả D1 Bridge.

V4 yêu cầu khóa trước future science: nguồn negative **chỉ TRAIN**; mỗi negative phải có provenance family/condition, cách tạo label, sampler, tỉ lệ negatives, contrast coefficient, LR/schedule, PRNG seeds riêng per-domain, log `negative_exposures,forward_passes,tokens,FLOPs,walltime,GPU_seconds`. Những mã/float SHA mới **chưa có** và là future fail-closed gate.

Giữ nguồn tham chiếu P02 STEP1024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` và T1 BPE manifest SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; **không tự thay bằng corpus/checker V3**. 12 seed ×3 arm ×256 updates = **9216 optimizer steps**, 256 family ×2 conditions ×3×12 = **18432 generations**, đều chỉ dự kiến.

Nguồn giả ngẫu nhiên phải được khai báo: seed→root qua hash protocol + namespaces `sampler,negative_sampler,dropout,augmentation,init`. Khi preexec, cùng seed phải tạo synthetic trajectory digest giống nhau, seed khác phải thực sự đổi intended stochastic update stream; nếu deterministic mọi run/streams correlated không chứng minh iid, **HOLD inferential sign-test**. Chưa thực hiện QA này.

Resume AdamW với nonzero moments phải đối chiếu uninterrupted vs interrupted sau ít nhất một step, optimizer moments, schedule, CUDA/CPU RNG, sampler cursor và bad SHA checkpoint fail-closed. T4 Free/paid $0 chưa đo throughput/VRAM/Drive quota; không mặc định 36 arm-runs khả thi, không mua GPU. **`REAL_RESUME=NOT_EXECUTED`, `T4=NOT_VERIFIED`**.

## 7. Một quyết định owner và phạm vi tiếp theo

| Gate | Trạng thái |
|---|---|
| V3 reviewer 7/7 source, 2 PASS 4 HOLD | `REVIEW_ACCEPTED` |
| V4 xử lý 6 findings mới + 11 inherited issues | `DRAFT_CREATED` |
| V4 source-only consistency QA | `PENDING` |
| Reviewer độc lập V4 | `PENDING` |
| Task-OOD checker actual, parser actual | `NOT_IMPLEMENTED` |
| AST nonoverlap, parser adversarial QA | `NOT_EXECUTED` |
| Gold-adjacent ACL, rights, signature | `NOT_VERIFIED` |
| AdamW resume, random seed proof, Free T4 resources | `NOT_EXECUTED/NOT_VERIFIED` |
| D1 Bridge science | **`HOLD`** |
| D1 existing; TEST Q1Q2 | **`HOLD_UNMODIFIED` / `SEALED`** |

**Owner single design decision:** `HOLD_PENDING_DISTINCT_V4_SOURCE_REVIEW`. Không training/GPU/inference/gold, không sửa V1/V2/V3, không merge main.

**Bước thực hiện tiếp theo duy nhất:** `TTM_SMALL4M_D1_BRIDGE_V4_DISTINCT_NEW_CHAT_TASK_RELEVANT_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU`. Reviewer chỉ đọc 7 file frozen, kiểm ngữ nghĩa task OOD, parser time injectivity, gold-adjacent security và package effect, trả GO/HOLD thiết kế. Dù GO thiết kế, **không cấp science GO**.
