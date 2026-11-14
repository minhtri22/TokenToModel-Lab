# TTM-Small-4M D1 Bridge — V3 integrated source-contract remediation (11 issues)

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_REMEDIATION_AND_SINGLE_INDEPENDENT_PREREG_REVIEW_NO_GPU`  
**Date:** 2026-11-14  
**Scope:** `READ_SOURCE / DESIGN_ONLY / NO_GPU / NO_TRAINING / NO_INFERENCE / NO_EVAL_GOLD`.  
**One owner decision:** **`HOLD_PENDING_V3_INDEPENDENT_REVIEW`** for design; **`D1_BRIDGE_SCIENCE=HOLD`**.  
**Machine contract:** `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_D1V2_01_11_DESIGN_HOLD_20261114.json`.

V1 và V2 đã được đóng băng **không sửa tại chỗ**. Phản biện V2 tại frozen HEAD `750533c1c2945594d827c886aaa275c49fb980d7` kết luận `HOLD_REVISE_BEFORE_PREREG` (11 issue, AM01–AM06; 7/7 Git blob metadata matching). Hai tệp phản biện gốc SHA-256:

- Review Markdown `f482d9855b16bed2bc764e63c2d986259b8f94bd9bb1f65e30b145f5e5e23cae`.
- Review JSON `52168ae7c523d1999388e9a2de211e10a940050b15b935a856c383c62c12c04f`.

Hai tệp đã được lưu nguyên byte trên nhánh nghiên cứu, **không sửa kết luận HOLD**. Reviewer chỉ là AI độc lập giữa các phiên, danh tính/độc lập bên ngoài chưa xác minh.

## A. Hợp đồng nghiên cứu không thay đổi

So sánh B (`B_CF_MLE`) với C (`C_CF_CONTRAST`) trên **cùng byte dữ liệu TRAIN**, thứ tự episode, cùng parent P02 STEP1024, tokenizer T1 BPE2048 và số optimizer updates; khác thành phần contrastive objective. A là đối chứng data effect thứ cấp, không làm tăng số primary hypotheses.

Cấu trúc kế hoạch **chưa tạo**: bốn category, bốn TRAIN skeleton/category, bốn OOD EVAL skeleton/category, 16 lexical worlds/skeleton, 256 paired families = **512 prompt per arm and seed**. Tập 16 OOD skeleton và family là *cố định* giữa **12 seed**, không thay thành 192 skeleton độc lập. Dự kiến 36 arm-runs, 9.216 optimizer steps, 18.432 generations; hoàn toàn **chưa thực thi**.

Khẳng định tối đa khi thành công: **hiệu quả C−B có hướng dương qua ngẫu nhiên huấn luyện trên đúng 16 cấu trúc OOD đã xác định**, không phải trên toàn bộ suy luận hay “unseen relative to TinyStories pretraining”. Ngưỡng magnitude +10pp là **cổng quyết định mô tả**, không phải phép thử chứng minh mean effect ≥10pp.

## AM01 — Reachable-state trace semantics / Structural OOD (D1V2-01, D1V2-02)

Lỗi V2: so `final action + goal` không đủ để phân biệt hai tiến trình ngữ nghĩa khác nhau. V3 yêu cầu:

1. Typed AST gồm agent/entity, finite world state, premise/guard, condition A/B, causal transitions, event priorities, temporal order, state effects, goal, final canonical action và **observable transition trace**.
2. Chuẩn hóa chỉ các phép **alpha-renaming cùng type, literal identity không có nghĩa và commutative reorder hợp lệ**; tuyệt đối không xoá negation, thời gian, priority, precondition, agent hoặc event. Domain trạng thái phải có hạn và khai báo đầy đủ tập initial states.
3. Từ mỗi initial state hợp lệ và điều kiện A/B, dựng **hệ chuyển trạng thái có nhãn (labeled transition system)** cho toàn bộ trạng thái khả đạt. Nhãn quan sát chứa event type, điều kiện guard, priority decision, thứ tự thời gian, ảnh hưởng state và action. So **strong labeled bisimulation sau chuẩn hóa và type-preserving renaming**; chỉ trả `DIFFERENT` nếu tồn tại **reachable counterexample trace** có hành vi ngữ nghĩa quan sát được khác. Nếu miền chưa đầy đủ, vòng lặp vô hạn, không phân biệt được, hoặc checker không thể chứng minh: `UNKNOWN→HOLD`.
4. Cùng final action nhưng reachable temporal/causal trace khác → **có thể** khác cấu trúc; khác biệt chỉ ở **unreachable states** không đủ là OOD. Graph-isomorphism thô và bảng hành động cuối đều không phải proof đầy đủ.
5. Bộ auditor phải kiểm TRAIN–EVAL và VAL–EVAL `NONEQUIVALENT`; TRAIN–VAL có thể cùng train skeleton theo V1 nhưng tách lexical family và prompt. Nếu một ca EVAL trùng hoặc checker không chắc: **HOLD toàn bộ batch, không thay mẫu sau outcome**.

**Synthetic fixture contracts không thuộc EVAL:** alpha rename phải bị chặn; same final action/different *reachable* trace phải được phân biệt; priority flip, temporal flip, negation flip, unreachable-only difference và incomplete domain phải có expected behavior cố định. **Chưa có actual checker, actual skeleton hoặc overlap proof**: `NOT_EXECUTED`, không được báo PASS.

## AM02 — Typed action oracle / deterministic parser (D1V2-03, D1V2-04)

- Oracle chứa `agent_id,verb_id,target_id,qualifier_id,time_id` và **semantic witness nằm trong gold metadata** (`world_state_id,condition_id,precondition_trace,AST_proof_sha`). Witness **không bắt model lặp lại trong văn bản sinh** nếu giao thức yêu cầu đúng một câu hành động.
- Giữ `gold_A != gold_B` theo canonical typed action, **một hành động hợp lệ duy nhất ở mỗi condition**; trường hợp hai gold trùng nhau, mơ hồ/multiple valid actions hoặc không có proof oracle phải bị reject **trước** EVAL freeze.
- Grammar ứng viên: `ACTION := AGENT SPACE VERB SPACE TARGET (SPACE QUALIFIER)? TERMINAL?`. Các terminal và lexicon/synonyms có version + SHA; không dùng substring-match hoặc model-rater override.
- Parser phải từ chối quote-only, phủ định, hai hành động, mâu thuẫn, sai agent/target/time/condition, echo prompt, unsupported synonyms, output rỗng, early EOS/truncation, special tokens không hợp lệ. Chỉ chuẩn hóa Unicode NFC, whitespace ngoài, punctuation cuối và casefold trong lexicon đã khóa.
- Greedy argmax, **≤224 prompt tokens kể cả special tokens** + **≤32 generated tokens kể cả EOS**, tổng 256. `success(m,f)=1` chỉ khi parser đúng **cả hai điều kiện A và B**; invalid→0, denominator luôn 256 family/arm/seed.
- Cần parser code, ontology+lexicon SHA, fixtures positive/negative nguồn-only và **independent sensitivity/specificity** trên synthetic non-EVAL fixtures trước khi một future source GO. Trạng thái **`PARSER_RUNTIME_QA=NOT_EXECUTED`**; hợp đồng này không giả rằng parser đã được lập trình hay đạt QA.

## AM03 — Exact integer sign-test và giới hạn inference (D1V2-05, D1V2-06)

Định nghĩa **nguyên có dấu** `D_s = Σ_{f=1}^{256} [success_C(s,f)−success_B(s,f)]`, với `success∈{0,1}` theo family (đúng cả hai điều kiện). `d_s = D_s/256`. **Chỉ `D_s>0` được tính là positive; `D_s=0` là nonpositive**, không có epsilon hoặc `inclusive_ge`.

Danh sách 12 seed cố định `20261120…20261201`; cùng 16 skeleton/256 family qua toàn bộ seed. Các stream sampler, dropout, negative sampler, init/augmentation (nếu có) tách domain và pin schema seed/hash; **numeric seed khác không tự chứng minh iid**. Nếu thiếu một seed, crash hoặc tính toán không tái lập: `HOLD_ALL`, không loại seed/reseed/chạy lại chọn lọc.

**H0 duy nhất:** `P_seed(D_s>0)≤0.5` có điều kiện trên fixed 16 skeleton, không suy ra population structural OOD hoặc `E[d_s]≥.10`. Kiểm định dấu nhị thức chính xác một phía `p = 2^{-12} Σ_{j=k}^{12} C(12,j)`, `k=#seeds with D_s>0`, `α=.05`; PASS thống kê khi **k≥10**.

| k seed dương | p exact | Đạt α=.05 |
|---|---:|---|
| 9 | 299/4096 = 0.072998046875 | Không |
| 10 | 79/4096 = 0.019287109375 | Có |
| 11 | 13/4096 = 0.003173828125 | Có |
| 12 | 1/4096 = 0.000244140625 | Có |

Power *riêng sign gate* với q=.7/.8/.9 độc lập giả định lần lượt khoảng **25.28%/55.83%/88.91%**. Power của **toàn bộ** conjunction (sign, magnitude, category, source QA) không lớn hơn; chưa có empirical power hoặc bằng chứng thực tế về iid training streams. Bootstrap chỉ là descriptive sensitivity: resample seed một lần cho toàn bộ task, skeleton theo category dùng chung seed và lexical family cùng block cho mọi seed; giữ B/C và A/B điều kiện ghép cặp. Không gọi CI confirmatory trên phân phối OOD skeleton ngoài 16 skeleton.

## AM04 — Integer category thresholds và shortcut heterogeneity (D1V2-07)

**Ngưỡng V1/V2 có nguồn từ pilot FC01**, được giữ để review *trước D1 Bridge outcomes*, không tuyên bố independent of prior pilot. Dùng **đếm nguyên** cho tất cả ranh giới:

| Composite decision gate | Số học nguyên |
|---|---|
| Positive seed sign test | `k ≥10/12` |
| Mean C−B ≥10pp across all seed×family | `Σ_s D_s ≥ ceil(12×256×.10)=308` |
| 4/4 category C−B không âm | `Δcount_category ≥0` |
| Ít nhất 3/4 category C−B ≥5pp | `Δcount_category ≥ceil(12×64×.05)=39` |
| C correct absolute ≥25% trên cả 4 category | `correct_C_category ≥12×64×.25=192` |

Guards này **không phải 4 kiểm định giả thuyết**. Precedence: **INVALID_SOURCE / RIGHTS / ACL / AST / PARSER / MISSING_SEED ⇒ HOLD_INVALID_PROTOCOL** trước; tiếp đến sign k<10 ⇒ NO_CONFIRMED_DIRECTIONAL_GAIN; sign qua nhưng magnitude/category trượt ⇒ SCOPED_DIRECTIONAL_GAIN_NOT_UNIFORM; chỉ mọi gate qua mới `CONFIRM_CONDITIONAL_FIXED_SKELETON_SEED_DIRECTIONAL_ROBUSTNESS_ONLY` (outcome label, không phải GPU permission).

Báo riêng từng skeleton×seed: số đúng và delta, tỉ lệ đóng góp từ skeleton dễ nhất, cue swaps, worst-skeleton và early-EOS/truncation. **Không tạo hidden extra pass threshold** sau outcome; báo heterogeneity như limitation dù global gate PASS.

## AM05 — Trusted isolated overlap auditor, ACL và quyền nguồn (D1V2-08, D1V2-09)

Thiết kế mới **có luồng kiểm chứng structural overlap**, không đòi trainer đọc gold:

- `trainer_owner`: đọc TRAIN/VAL, TRAIN_VAL_AST, source/rights; **deny** EVAL_RAW/GOLD/MAPPING và EVAL_AST private.
- `eval_gold_custodian`: giữ sealed EVAL_RAW, GOLD, EVAL_AST và nguồn SHA.
- **`isolated_overlap_auditor`**: chỉ có phiên làm việc hạn chế quyền đọc **AST projection không chứa raw prompts, gold hoặc mapping** từ cả TRAIN/VAL và EVAL; thực hiện exactly the AM01 trace/equivalence checker. Không được xem model outputs, arm IDs hay raw EVAL gold.
- `parser_source_QA`: chỉ code và **synthetic non-EVAL fixtures**.
- `blind_rater`: chỉ blind packet, không có mapping, gold, seed/arm hoặc aggregate primary.

Auditor trả về **PASS/FAIL/UNKNOWN + SHA pins + signed/authenticated receipt**, nếu overlap thì counterexample witness phải giữ riêng tư và **không trả raw AST/gold cho trainer**. Chứng thực chữ ký/khóa, ACL thật, audit log, deny-probe, trainer environment mount inventory và quyền dữ liệu/PII là **future preexec gates**, **không được mặc định PASS**. Không gọi là độc lập nếu auditor và trainer dùng cùng credentials đọc EVAL.

Leakage probes thiết kế: cue giống nhau nhưng đảo condition/gold; label permutation; answer-like echo; AST near-isomorphism TRAIN/VAL–EVAL; template grammar overlap; quyền TinyStories và provenance của dữ liệu synthetic mới. Scope OOD **chỉ so với controlled fine-tuning task grammar**, không đảm bảo chưa từng xuất hiện trong pretraining parent.

## AM06 — Source pins, AdamW resume và Free T4 (D1V2-10, D1V2-11)

**Historical reference pins:** P02 parent STEP1024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; T1 BPE manifest SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. **Không có source SHA của V3 runner, dữ liệu OOD mới, negative sampler hoặc parser**; không được mượn SHA của runner/FC01 corpus cũ để tuyên bố V3 ready.

**Cố định:** FP32, 12 seed × 3 arms × 256 updates = **9.216 optimizer steps dự kiến**; 256 family×2 condition×3 arms×12 seed = **18.432 generated outputs dự kiến**. B/C cùng dữ liệu, order, token/update budget, nhưng contrastive C có thêm negative exposures/forward FLOPs. Estimand là **fixed data & optimizer steps**, không phải equal compute; report token slots, extra forward, negatives, FLOPs estimate, walltime, GPU seconds.

**Trước khoa học** phải chứng minh positive-moment AdamW resume: K cập nhật liên tục so với interrupted ở step có exp_avg/exp_avg_sq khác 0 rồi resume đến K, đối chiếu model, AdamW moments/step, scheduler, RNG (Python, NumPy, Torch CPU/CUDA), sampler cursor, gradient accumulation và atomic checkpoint. Negative corrupt SHA/partial checkpoint/wrong-parent fail-closed. Numeric/bitwise tolerance phải khóa **trước** QA. Chỉ dùng synthetic non-science fixture trong lần QA sau khi được phép tương ứng; **bước hiện tại không chạy**.

Đo riêng Free T4/GPU vRAM/RAM/disk, Drive quota, timeouts, throughput 3 arms, I/O/restart/owner paid USD=0. Không mặc định có GPU miễn phí hoặc 36 arm-runs khả thi. Nếu không khả thi, **HOLD** hoặc chuyển thành scoped pilot bằng **amendment mới trước outcomes**, không chạy paid GPU.

## Ma trận trạng thái sau V3 source-contract

| Gate | Kết quả |
|---|---|
| V2 external AI review accepted, 11 issues mapped | `PASS_SOURCE_ACCEPTANCE` |
| V3 AM01–AM06 machine + Markdown | `DESIGN_DRAFT_FOR_DISTINCT_REVIEW` |
| Integer statistics and budgets self-checked | `SOURCE_ONLY_QA_REQUIRED` |
| Actual AST equivalence checker and train/eval overlap | `NOT_EXECUTED` |
| Actual deterministic parser and independent adversarial QA | `NOT_EXECUTED` |
| Real ACL, rights, signed auditor receipt | `NOT_VERIFIED` |
| Actual optimizer-moment resume and Free T4 feasibility | `NOT_EXECUTED/NOT_VERIFIED` |

**Phán quyết owner cho operation này:** `V3_DESIGN=HOLD_PENDING_DISTINCT_INDEPENDENT_SOURCE_REVIEW`; `D1_SCIENCE=HOLD`. Không chỉnh V1/V2, không tạo TRAIN/VAL/EVAL/gold, không chạy GPU hoặc training, không mở TEST/Q1Q2.

**Bước thực hiện tiếp theo duy nhất:** `TTM_SMALL4M_D1_BRIDGE_V3_DISTINCT_NEW_CHAT_PREREG_SOURCE_REVIEW_SINGLE_GO_HOLD_NO_GPU`. Reviewer khác đánh giá khách quan V3 AM01–AM06, nhất là proof trace semantics, parser validity, sign-test power, separated overlap audit và 36-run feasibility. Nếu phát hiện lỗi trọng yếu, **HOLD với V4 amendment**; không overwrite V3.
