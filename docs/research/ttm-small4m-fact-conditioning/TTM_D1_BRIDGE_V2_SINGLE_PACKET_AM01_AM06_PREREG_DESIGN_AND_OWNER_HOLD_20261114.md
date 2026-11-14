# D1 Bridge V2 — Gói sửa đổi tiền đăng ký AM01–AM06 duy nhất

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V2_SINGLE_PACKET_PREREG_AMENDMENT_SOURCE_QA_AND_OWNER_GO_HOLD_NO_GPU`  
**Ngày:** 14/11/2026  
**Phân loại:** `DESIGN_ONLY_V2_AMENDMENT_AFTER_INDEPENDENT_V1_HOLD`.  
**Quyết định chủ dự án về khoa học:** `HOLD_D1_SCIENCE`. V2 **không** thay thế/tự sửa V1. Không tạo source TRAIN/EVAL/gold, không GPU, không inference/train.

## 1. Nguồn sửa đổi và ranh giới độc lập

V1 đã cố định tại `25a19daea9f664e14f83d7df2cf8265ffaea4ecd`. Reviewer AI tại phiên khác trả **`HOLD_REVISE_BEFORE_PREREG`**, 6/6 trục HOLD, F01–F12, AM01–AM06. Chứng cứ nhận trực tiếp ngày 14/11/2026:

- `TTM_D1_BRIDGE_V1_INDEPENDENT_PREREG_REVIEW_20261114.md`, **SHA-256 `7369882b5615785628bd93b006157423f2b8377e265e3c3098429eabd60ab97c`**.
- `TTM_D1_BRIDGE_V1_INDEPENDENT_REVIEW_RECEIPT_20261114.json`, **SHA-256 `21c1e07b13ce1cd39d77200247b5f1a6c9fbbd49fffa7f90821c9a429f28034b`**.
- Bằng chứng được lưu theo bản gốc, không thay outcome: `docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V1_INDEPENDENT_PREREG_REVIEW_20261114.md` và `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V1_INDEPENDENT_REVIEW_RECEIPT_20261114.json`.
- Reviewer tự nhận `INDEPENDENT_NEW_CHAT_AI_SELF_ATTESTED`; bên ngoài **chưa xác minh độc lập danh tính/quyền**. 6 Git blob tại V1 khớp theo GitHub contents, không phải phép băm thứ hai của tệp đã tải.

**Thay đổi được phép** trong V2: giới hạn tuyên bố xác nhận, diễn đạt estimand, thủ tục đo, số seed, nguồn sai số và các biện pháp chống leakage. **Không được dùng FC01 EVAL64/BLIND96 để điều chỉnh ngưỡng sau khi nhìn D1 outcomes**. Giữ nguyên FC01 exploratory và D1 hiện hữu 512 outputs, không mở TEST/Q1Q2.

## 2. AM01 — Typed semantic AST và “structural OOD” có ý nghĩa thao tác

**F01 CRITICAL / F02 HIGH.** Định nghĩa một ngữ pháp đánh giá có hạn định:

- Typed nodes: `entity, state_variable, event, precondition, transition, condition_branch, ordered_dependency, priority_rule, goal_state, action`. Typed edges: `temporal_before, causes, requires, overrides, changes_state, binds_agent_target`.
- Mỗi skeleton phải mang tập hữu hạn các trạng thái được phép, hai biến điều kiện phản thực và một hàm chuyển trạng thái→hành động đầy đủ; các ràng buộc thứ tự/thời gian/ngoại lệ phải thể hiện trong AST.
- Quy tắc canonicalization cho phép **alpha-renaming** biến cùng loại, đổi tên literal không mang nghĩa và sắp xếp toán tử giao hoán thật sự. **Không** cho phép bỏ negation, priority, precondition, edge temporal hay đồng nhất hai tác tử.
- Bên cạnh graph-isomorphism, checker so **bảng hành động trên toàn bộ trạng thái hữu hạn và cả hai điều kiện**, cùng goal constraints. Những trường hợp ngoài miền hữu hạn hoặc không quyết định được tương đương phải trả `UNKNOWN→HOLD`, không coi là non-overlap.
- TRAIN/VAL có thể dùng cùng bốn skeleton TRAIN/category như V1 nhưng **không** trùng lexical family/episode/prompt; TRAIN/EVAL **và VAL/EVAL** phải không tương đương AST/semantics; kiểm exact, alpha-rename, near-equivalence; nếu vi phạm thì **HOLD toàn bộ**, không thay mẫu sau khi xem kết quả.
- Bốn cấu trúc OOD/category, 16 cấu trúc cả bộ, vẫn là **fixed-skeleton confirmatory scope**; 16 lexical worlds ×12 seed không trở thành 192 cấu trúc độc lập. Không tuyên bố OOD so với toàn bộ TinyStories pretraining.

**Source QA trong operation này:** chỉ kiểm bản đặc tả. **Không có generator AST, dataset, checker tương đương hoặc proof non-overlap thực tế**; các cổng đó `NOT_EXECUTED`.

## 3. AM02 — Oracle hành động và parser tất định

**F03 CRITICAL / F04 HIGH.** V2 yêu cầu `canonical_semantic_action` với các trường typed `agent_id, action_verb, target_id, qualifier, time_context, condition_witness`; mỗi condition phải có **một hành động hợp lệ duy nhất** theo ontology và preconditions; `canonical_gold_A != canonical_gold_B`. Family có hai gold trùng nhau, nhiều hành động hợp lệ hoặc câu hỏi mơ hồ phải **loại trước khi đóng băng EVAL**; không thay sau outcomes.

Giữ greedy `argmax`; câu trả lời một hành động ngắn. Prompt ≤224 token T1 và phần sinh ≤32 token, **gồm cả BOS/EOS/special tokens** trong context 256; không vượt và không sửa postprocess theo output.

Parser cần một grammar giới hạn, phiên bản và danh sách từ đồng nghĩa có SHA; không substring-match. Phải phát hiện negation, wrong-agent/target, inverse-condition, wrong time/priority, multiple actions, contradiction, prompt echo, unsupported synonym, early EOS/truncation, empty output; **mọi ambiguous/invalid→0** và giữ mẫu số 256 family/arm/seed.

Primary family `success=1` **chỉ khi cả điều kiện A và B đều có đúng hành động có điều kiện**, cùng input/prompt giữa các arm, không lọc ca lỗi parser. Scorer AI/human chỉ secondary, **không override primary**.

Chương trình parser và độc lập adversarial QA tương lai phải có positive + known-synonym và negative fixtures *không thuộc EVAL* trước khi khóa SHA. **Hiện tại chỉ thiết kế contract, `PARSER_SOURCE_QA=NOT_EXECUTED`**; tuyệt đối không dùng mô tả này như chứng nhận độ nhạy/đặc hiệu.

## 4. AM03 — Sửa estimand, 5→12 seed, power và crossed bootstrap

**F05/F06 HIGH.** Reviewer xác định phép sign-flip 5 seed chỉ có thể đạt alpha=.05 khi cả 5 seed dương; với giả định xác suất seed dương q=.8, power chỉ 32,77% (bỏ qua các gate khác). V1 cũng chưa chứng minh sign symmetry.

**V2 chủ động tạo một giao thức ứng viên mới trước D1 Bridge outcomes:**
- **12 seed được khai báo trước**: 20261120–20261201 (bao gồm hai đầu), không có optional stopping, loại seed không thuận lợi, thay seed hay rerun tự động.
- Mỗi seed nhận cùng parent P02/T1 và shared EVAL 16 skeleton. `d_s=(1/4) Σ_c mean_f(success_C−success_B)` trên mỗi 64 family/category, điều kiện A/B gộp ở family.
- Giả thuyết thống kê khả kiểm: `H0: P_seed(d_s>0)≤0.5` vs `H1: >0.5`, **có điều kiện trên 16 fixed OOD skeleton**. Đơn vị kiểm là 12 seed-level paired differences, **không** phải 256 family hay 15 arm-runs.
- Thay magnitude sign-flip bằng **one-sided exact binomial sign test**: `k=#(d_s>0)`, `p=Σ_{j=k}^{12} C(12,j)2^{-12}` cho `k>6` (với k≤6 cho p theo công thức đầy đủ, ≥.5). `d_s=0` tính **không dương**. Ở alpha=.05, cần **k≥10**: k=9→299/4096=.072998; k=10→79/4096=.019287. Không yêu cầu phân phối độ lớn hiệu ứng đối xứng, nhưng giả định các stochastic training streams độc lập/đại diện cho xác suất seed dương **vẫn phải được chứng minh**.
- Ngưỡng `mean(d_s)≥+0.10` là **decision gate mô tả**, **không** là kiểm định có mức ý nghĩa cho mean effect >+0.10. Nếu chỉ thỏa sign test mà mean <.10 thì **không được gắn nhãn xác nhận hiệu ứng +10pp**.
- Sensitivity minh họa dưới giả định Bernoulli seed độc lập (không rút từ FC01): q=.7→25,28%; q=.8→55,83%; q=.9→88,91% cơ hội đạt k≥10. Đây là **power của sign component**, không tính thêm category/magnitude/resource gates, nên power toàn bộ ≤ các mức đó. Nếu external stats reviewer coi power này không đủ, `HOLD` hoặc giảm phạm vi thành pilot bằng một amendment khác **trước outcomes**.
- Bootstrap 10.000 vòng, seed `20261202`, chỉ hỗ trợ mô tả. Đánh chỉ số seed **một lần cho toàn bộ nhóm**, skeleton **một lần/category dùng chung giữa seed**, lexical family **một lần/skeleton dùng chung giữa seed**, giữ cùng B/C và cặp A/B; đây là **crossed design**, không bootstrap lồng độc lập theo từng seed. Chỉ báo độ nhạy trên fixed 16 skeleton, không diễn giải population OOD.

**V2 không mở science để đo power/tuning**. `STATISTICAL_INDEPENDENT_REVIEW=REQUIRED` và không có bằng chứng 12 random seed là các replicate độc lập ngoài điều kiện giả lập.

## 5. AM04 — Ngưỡng category và thứ tự phân xử

**F07 MEDIUM.** Giữ các gate định hướng từ V1, **ghi rõ ảnh hưởng của FC01 pilot**, khóa trước D1 Bridge outcomes, không gọi là hoàn toàn độc lập dữ liệu pilot:

1. `k_positive_seeds≥10/12`, one-sided sign p≤.05.
2. `mean(d_s)≥+.10` quan sát.
3. Trung bình `Δ_C−B` không âm ở **4/4 category**; ít nhất **3/4 category ≥+.05**; C đạt accuracy tuyệt đối `≥.25` trong **mỗi category**. Các category guard này mô tả, không phải bốn hypothesis tests.
4. Mọi seed, checkpoint, rights, data/oracle/parser SHA, integrity và independent custody đầy đủ.

**Thứ tự quyết định bất biến:** thiếu quyền, mất dữ liệu, leakage, fail parser hoặc mất seed → `HOLD_INVALID_PROTOCOL` trước; sign test không qua → `NO_CONFIRMED_DIRECTIONAL_GAIN`; sign qua nhưng magnitude/category không qua → `SCOPED_GAIN_NOT_UNIFORM_CONFIRMATION`; chỉ khi mọi gate qua mới `CONFIRM_CONDITIONAL_FIXED_TASK_SEED_ROBUSTNESS`, **không** `GO_GPU` và không tuyên bố OOD tự nhiên rộng. Ngưỡng chính xác/boundary `d_s>0` phải chốt epsilon/tolerance trước outcome; chưa có mã số thực.

## 6. AM05 — Quyền nguồn, chống rò và phân quyền thực tế

**F08/F09 HIGH.** Thiết kế ACL role-based:
- `owner_trainer`: chỉ TRAIN/VAL/source/rights, **không** EVAL/gold/mapping.
- `independent_eval_custodian`: sealed EVAL/gold và hash, không dùng checkpoint để tuning.
- `parser_source_qa`: code + synthetic fixtures *không thuộc EVAL*, không gold.
- `blind_rater`: blind packet riêng, không arm/seed IDs, gold/mapping, kết quả primary tổng hợp.

**Gate thực tế trước science:** riêng storage ACL/key owner, logs+SHA đóng băng trước release, bằng chứng train environment không mount EVAL/gold, scoring SHA trước unblind, receipt quyền TinyStories/synthetic và PII. Cần kiểm các cue swaps, permutations, gold-string prompt echo, near-isomorphic AST và shared grammar. Không thể chứng minh không trùng toàn bộ pretraining: claim OOD giới hạn ở fine-tuning grammar do ta kiểm soát.

**Ở V2 DESIGN:** `ACL_ACTUAL=NOT_VERIFIED`, `RIGHTS_ACTUAL=NOT_VERIFIED`, `GOLD_NOT_CREATED`, `DATA_NOT_CREATED`.

## 7. AM06 — Runner/AdamW resume, nguồn tính toán và Free T4

**F10 HIGH, F11/F12 MEDIUM.** Giữ parent exact, T1 BPE, FP32, 256 steps/arm/seed, B/C cùng byte TRAIN và thứ tự episode, sampler/optimizer/checkpoint khi phù hợp. C vẫn có thêm compute/negative exposure do contrastive: phải log và phân tích `forward_calls, negative_exposures, tokens, walltime, FLOPs estimate`. **Không gọi B/C equal-compute**; estimand là **đổi objective ở fixed data + fixed optimizer steps**.

Trước science phải có preexec QA thực cho:
- checkpoint chứa **nonzero AdamW moments**, scheduler, optimizer steps, RNG Python/NumPy/Torch CPU/CUDA, sampler cursor, gradient accumulation/batch boundary;
- test `K uninterrupted` so với `K interrupted+resumed`, so tensors/optimizer/scheduler/RNG/cursors theo tolerance đã khóa, negative corrupt/wrong SHA/partial checkpoint fail-closed;
- profiling Free Tesla T4: vRAM/RAM/disk, throughput cả 3 arm, quotas Drive, timeout, restart/cost/rate/overhead, atomic writes, one-shot failure receipts.

**Ngân sách ứng viên thay đổi vì n=12:** 36 arm-runs, **9.216 optimizer updates**, **18.432 generated outputs** trên 256 paired families ×2 conditions ×3 arms ×12 seeds. Đây chỉ là phép đếm — **T4 free-tier capacity và paid USD 0 chưa được chứng minh**, nên không cấp GO science. Nếu không thực tế, chỉ được đổi thành scoped pilot qua amendment tiếp theo trước outcomes.

## 8. Một decision owner cho V2 design

Trạng thái ở thời điểm lập V2:

| Gate | Kết quả |
|---|---|
| Tiếp nhận reviewer V1; 12 findings và 6 amendments | `PASS_SOURCE_ACCEPTANCE` |
| V2 document và JSON mới, V1 nguyên vẹn | `PASS_VERSIONED_V2_DRAFT` |
| AM01 AST thực và overlap non-EVAL | `NOT_EXECUTED` |
| AM02 parser thực và independent negative QA | `NOT_EXECUTED` |
| AM03/AM04 independent mathematical review | `PENDING` |
| AM05 owner rights/ACL receipt | `NOT_VERIFIED` |
| AM06 nonzero-moment resume + T4 resources | `NOT_EXECUTED` |

**Quyết định duy nhất:** `D1_BRIDGE_V2_DESIGN=HOLD_PENDING_EXTERNAL_INDEPENDENT_SOURCE_REVIEW`, `D1_BRIDGE_SCIENCE=HOLD`. **Không có quyền chạy 36 arm-runs**, không micro-permit, không tạo gold.

Bằng chứng machine-readable V2: `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_AM01_AM06_SINGLE_PACKET_PREREG_DESIGN_HOLD_20261114.json`.

**Bước thực hiện tiếp theo duy nhất:** `TTM_SMALL4M_D1_BRIDGE_V2_DISTINCT_AI_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU` — reviewer AI/human tách phiên kiểm AM01–AM06, đặc biệt lựa chọn 12 seed/sign test và hạn chế fixed-skeleton; đóng đúng **một design GO/HOLD**, vẫn không cấp science.
