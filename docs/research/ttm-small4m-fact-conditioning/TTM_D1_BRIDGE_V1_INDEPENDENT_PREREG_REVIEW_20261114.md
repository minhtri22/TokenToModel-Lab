# TTM D1 Bridge V1 — Independent Scientific Preregistration Review

**Operation:** `TTM_SMALL4M_D1_BRIDGE_SOURCE_ONLY_INDEPENDENT_PREREG_REVIEW_AND_GO_HOLD_NO_GPU`  
**Ngày:** 2026-11-14  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Frozen scientific input commit:** `25a19daea9f664e14f83d7df2cf8265ffaea4ecd`  
**Handoff commit:** `1f16f18d52382af8773a0e763da0090ae0472af3`  
**Vai trò:** `INDEPENDENT_NEW_CHAT_AI_SELF_ATTESTED` — phản biện giao thức khoa học AI, không phải phản biện con người.  
**Phạm vi:** `READ_ONLY · DESIGN_ONLY · SOURCE_ONLY · NO_GPU · NO_TRAINING · NO_PRIVATE_GOLD`.  
**Quyết định tích hợp duy nhất:** **`HOLD_REVISE_BEFORE_PREREG`**.  
**Bất biến:** `D1_BRIDGE_SCIENCE=HOLD`, `D1_EXISTING=HOLD_UNMODIFIED`, `TEST_Q1Q2=SEALED`, `FC02=NOT_OPENED`, `MAIN=UNCHANGED`.

## 1. Câu hỏi và phương pháp phản biện

Câu hỏi H1 là liệu bổ sung contrastive objective (arm C) trên cùng tập phản thực và thứ tự episode của arm B có làm tăng tỷ lệ *sinh tự do hành động đúng trong cả hai điều kiện A/B* trên cấu trúc ngữ nghĩa mới, so với counterfactual MLE (arm B), hay không. Arm A là đối chứng hiệu ứng dữ liệu thứ cấp. Mẫu được dự định gồm 4 category, 16 skeleton OOD, 256 paired families, 5 seed và 3 arm; chưa được tạo trong operation này.

Người phản biện đọc trực tiếp HANDOFF ở commit `1f16f18d…` và **đủ sáu tài liệu ở đúng** frozen commit `25a19dae…`, so Git blob SHA GitHub trả về với danh sách đã khóa. Các SHA phía dưới là **Git blob SHA-1 của đối tượng Git**, không phải hash SHA-256 của byte cục bộ. Chưa tiến hành phép băm độc lập trên bản tải local; vì thế tuyên bố xác minh được giới hạn ở **commit-qualified GitHub contents SHA**, không phải second-channel byte-custody audit. `INDEPENDENCE_NOT_VERIFIED` ngoài phạm vi tự xác nhận chat mới.

| Nguồn | Git blob SHA-1 tại frozen commit | Kết quả |
|---|---|---|
| [S1] D1 Bridge V1 — protocol | [`a5cd0dbd4167bdc53454847a25afcf317c94226b`](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/docs/research/ttm-small4m-fact-conditioning/TTM_FC01_D1_BRIDGE_STRUCTURAL_OOD_FREEGEN_MULTISEED_PREREG_DESIGN_V1_20261113.md) | VERIFIED_GITHUB_CONTENTS_BLOB_SHA |
| [S2] D1 Bridge V1 — machine-readable | [`8bc9cf0fa45ada52150094a24259514f51ee2a28`](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_D1_BRIDGE_PREREG_V1_MACHINE_READABLE_DESIGN_HOLD_20261113.json) | VERIFIED_GITHUB_CONTENTS_BLOB_SHA |
| [S3] Source-only QA 26/26 | [`e29a994a9d3d9bf368380aeb858f0626ec6558ed`](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_ARCHIVE_D1_BRIDGE_V1_SOURCE_ONLY_INTEGRATED_QA_20261113.json) | VERIFIED_GITHUB_CONTENTS_BLOB_SHA |
| [S4] FC01 terminal archive | [`dab622ba088ee3def4c0994dd2f068938fd47bc2`](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_EXPLORATORY_FINAL_ARCHIVE_MANIFEST_AND_D1_BRIDGE_DESIGN_HOLD_20261113.json) | VERIFIED_GITHUB_CONTENTS_BLOB_SHA |
| [S5] D1 existing — blind handoff | [`b6abdab37b5220fc7a861de940e28313ebe1c316`](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/docs/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_INDEPENDENT_CHATGPT_BLIND_RATER_HANDOFF_20261112.md) | VERIFIED_GITHUB_CONTENTS_BLOB_SHA |
| [S6] lineage.md — L0016 | [`dc97f833dfd764bce29675919604f3ebb97bf8e8`](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/lineage.md) | VERIFIED_GITHUB_CONTENTS_BLOB_SHA |

**Phạm vi bằng chứng:** [S1] §1–§8 là hợp đồng tác giả đề xuất; [S2] cung cấp trường máy; [S3] tự ghi `SELF_AUTHORED_ARITHMETIC_AND_SOURCE_REFERENCE_CONSISTENCY_NOT_INDEPENDENT_SCIENTIFIC_REVIEW`; [S4] xác định FC01 là exploratory; [S5] xác định D1 hiện hữu là một giao thức riêng; [S6] L0016 bảo toàn lịch sử. Không coi 26/26 self-QA là chứng nhận khoa học, không mở dataset/gold/private mapping, không xem kết quả D1 sealed.

### Đối chiếu số học độc lập

- TRAIN: `4 × 4 × 32 = 512` paired families; VAL: `4 × 4 × 8 = 128`; OOD EVAL: `4 × 4 × 16 = 256`.
- EVAL mỗi arm/seed: `256 × 2 = 512` generations; 5 seed × 3 arm = **7.680 generations**.
- Optimizer: `5 × 3 × 256 = 3.840` steps. Giới hạn chuỗi `224 + 32 = 256` là nhất quán về số học nhưng còn phụ thuộc BOS/EOS, token thực và phép xử lý special tokens.
- Các seed khai báo: `20261120`, `20261121`, `20261122`, `20261123`, `20261124`. Việc được liệt kê cố định **không tự chứng minh** tính độc lập của các lần huấn luyện.

## 2. Ma trận adjudication

| Trục | Kết luận | Rủi ro cao nhất | Vấn đề quyết định |
|---|---|---|---|
| R1 Structural OOD | **HOLD** | **CRITICAL** | Định nghĩa AST/graph/canonical equivalence chưa có hiện thực/fixtures |
| R2 Parser & primary | **HOLD** | **CRITICAL** | Chưa có parser thật và oracle kiểm hành động có điều kiện |
| R3 Statistics & power | **HOLD** | **HIGH** | Sign-flip n=5 có giả định chưa chứng minh; power thấp; bootstrap sai cấu trúc phụ thuộc tiềm tàng |
| R4 Category gates | **HOLD** | **MEDIUM** | Ngưỡng có động cơ FC01, thiếu calibration về false-positive/false-negative và quy tắc diễn giải |
| R5 Rights, leakage, custody | **HOLD** | **HIGH** | Role separation chưa phải permission separation; rights và pretrain/template leakage chưa chứng thực |
| R6 Reproducibility & resources | **HOLD** | **HIGH** | Actual resume AdamW và ngân sách/khả năng T4 chưa có chứng cứ |

**Phân biệt trạng thái:** `HOLD` nghĩa là thiết kế có thể sửa hoặc thiếu bằng chứng phải hoàn thiện trước prereg science; `NOT_EXECUTED` chỉ từng kiểm thử/biện pháp chưa thực hiện; đây không phải `FAIL` của mô hình đã chạy.

## R1 — Structural OOD: **HOLD / CRITICAL**

**Chứng cứ:** [S1] §3 nêu `semantic_skeleton_id`, 4 train và 4 OOD skeleton/category, yêu cầu không đẳng cấu đổi tên; [S2] `structural_splits.semantics`, `anti_leakage_requirements`; [S3] `unverified_items` xác nhận AST/gold chưa tồn tại; [S4] `known_limitations` công nhận FC01 chỉ đổi lexical worlds trên shared templates.

**Phát hiện:**

1. **F01 / CRITICAL / MUST-FIX:** `semantic_skeleton_id` hiện là mô tả, không phải đặc tả thao tác. Không có schema typed AST, toán tử ngữ nghĩa, cạnh thời gian/nhân-quả/ưu tiên, phép chuẩn hóa biến, tương đương cấu trúc hoặc distance criterion. Đổi tên biến, hoán vị tên đối tượng hay đảo cú pháp có thể khiến một skeleton “mới” nhưng cùng quy tắc suy luận. Graph-isomorphism thuần túy cũng chưa đủ nếu phép biến đổi bảo toàn lời giải nhưng không bảo toàn graph thô. **Non-overlap = NOT_EXECUTED**, tuyệt đối không thể báo PASS.
2. **F02 / HIGH / MUST-FIX:** Chỉ **4 OOD skeleton/category**; 16 lexical worlds/skeleton và 5 seed không làm tăng số cấu trúc độc lập lên 320 hay 1.280. Tuyên bố chỉ được giới hạn ở **16 cấu trúc cụ thể**, trừ khi có kế hoạch sampling/độ đa dạng được prereg. Cũng cần đối chiếu overlap với VAL và mọi template training/validation đã dùng để lựa chọn thiết kế.

**Điều kiện sửa V2:** Định nghĩa typed semantic AST có toán tử và các ràng buộc chuyển trạng thái; chuẩn hóa alpha-renaming, literal normalization, commutative reorder được phép, và semantic entailment equivalence. Đóng băng luật split *trước sinh EVAL*: independent checker kiểm **TRAIN–EVAL và VAL–EVAL** không tương đương về AST/ngữ nghĩa, còn **TRAIN–VAL** được phép dùng chung train skeleton theo V1 nhưng phải tách lexical worlds/families và loại trùng prompt/episode; kiểm exact và near-equivalence theo đúng từng cặp split. Quy định reject toàn bộ batch nếu một OOD skeleton trùng/tương đương; không thay mẫu hậu nghiệm. Tài liệu đặc tả cần ít nhất bốn lớp kiểm thử ở **mức mô tả, không sinh EVAL thật**: cùng cấu trúc/đổi từ, cùng nghĩa/đổi biến, khác cấu trúc/cùng từ, và thay thứ tự ưu tiên khiến hành động khác. Có positive controls (isomorphic phải bị chặn) và negative controls (thực sự khác cấu trúc phải được giữ).

**Ranh giới:** Không thể chứng minh “OOD so với toàn bộ pretraining của TinyStories”; chỉ có thể chứng minh OOD **theo tập cấu trúc tác vụ TRAIN/VAL được kiểm soát**, với giới hạn đã công bố.

## R2 — Parser, decoder và primary: **HOLD / CRITICAL**

**Chứng cứ:** [S1] §4 quy định greedy, `max_new_tokens=32`, parse `agent/action/target` và `both_conditions_correct`; [S2] `decoder_and_primary`; [S3] thừa nhận “real decoder parser code” và test chưa có.

**Phát hiện:**

1. **F03 / CRITICAL / MUST-FIX:** “Frozen deterministic parser” mới là lời hứa; chưa có implementation, coverage và adversarial negative QA độc lập. Chỉ whitelist synonym có thể đánh tụt câu đúng (false-negative), hoặc match token hành động nằm trong phủ định/tường thuật/câu trái nghĩa (false-positive). Một parser chỉ so `action/target` mà bỏ điều kiện tiền đề sẽ không đo chính xác suy luận phản thực.
2. **F04 / HIGH / MUST-FIX:** Chưa quy định oracle `gold_A`, `gold_B` phải duy nhất theo ontology nào, xử lý nhiều hành động hợp lệ, trường hợp hai điều kiện dẫn tới cùng một hành động, tiền đề thiếu/mâu thuẫn, và trường hợp đề bài chứa nhiều tác tử. Nếu `gold_A` và `gold_B` giống nhau trên family, bài kiểm “đúng cả hai” không phân biệt được tính nhạy phản thực. Chưa quy định output chứa một câu đúng rồi một câu sai xử lý thế nào ở mức parse canonical.
3. `success(m,f)=1` nếu đúng A và B, denominator 256 cố định và invalid→0 là cấu trúc primary **hợp lý**, nhưng **scorer validity = NOT_EXECUTED**. Cách xử lý `EOS`, truncation, exact tokenizer T1, role delimiter, padding, special tokens, empty output, và câu đúng sau token thứ 32 phải khóa.

**Điều kiện sửa V2:** Phát hành hợp đồng `semantic_action` có typed entities, preconditions, action semantics, allowed-action multiplicity và **condition discriminability**; reject trước khi đóng băng những family không có cặp oracle đủ thông tin. Parser phải xác định phủ định, điều kiện, thời điểm, mâu thuẫn và multiple-action; không substring-match. Lập gold-independent parser QA bằng câu tổng hợp không thuộc EVAL, với positive/paraphrase, negation, wrong-agent/target, dual-action, condition-inversion, contradiction, answer-string echo, early EOS/truncation. Báo riêng sensitivity/specificity trên tập adversarial độc lập trước khi khóa parser SHA; không tự sửa parser từ EVAL. Denominator giữ 256 kể cả parser invalid. Không chấm bằng LLM để override primary.

**Ưu điểm giữ lại:** Family là đơn vị chấm đúng (không tách prompt A và B thành hai đơn vị độc lập), cùng greedy decoding, một STEP256 checkpoint và no best-EVAL-selection.

## R3 — Thống kê, exact paired sign-flip và power: **HOLD / HIGH**

**Chứng cứ:** [S1] §5; [S2] `statistical_gate`. V1 **đã ghi đúng** rằng `mean(d_s)≥0.10` chỉ là decision gate, không phải kiểm định cho H0: Δ≤0.10. Không được coi đây là lỗi tác giả còn che giấu; cần làm rõ cách diễn giải khoa học.

**Phát hiện:**

1. **F05 / HIGH / MUST-FIX:** Đơn vị để sign-flip là **năm seed-level paired deltas**, không phải 256 family, 512 prompts, 16 skeleton hay 15 arm-runs. Năm seed dùng chung parent, dataset và EVAL làm hiệu ứng có phụ thuộc theo nội dung; chỉ RNG huấn luyện có thể tạo replicate khác nhau. Exact sign-flip hữu hiệu nếu các `d_s` độc lập/đối xứng theo dấu dưới null thích hợp (hoặc cơ chế randomization hợp lệ). H0 “mean ≤0” nói chung **không tự suy ra** sign symmetry; V1 chưa ghi lý do xác lập giả định này. Cố định seed trước test hạn chế chọn lọc nhưng không thay thế giả định phân phối.
2. **Power:** Với 5 delta đều khác 0, một-sided sign-flip có `2^5=32` tổ hợp. Muốn `p≤0.05` phải có mức p tối thiểu `1/32=0.03125`, tức năm delta đều dương. Chỉ một delta âm hoặc bằng 0 thì p ít nhất `2/32=0.0625` (đếm dấu đảo và ties bảo thủ). Nếu xác suất một seed dương là `q`, xác suất đạt gate thống kê (bỏ qua các gate khác) xấp xỉ `q^5` theo mô hình seed Bernoulli độc lập: q=.8→32,77%; q=.9→59,05%. Đây là **bảng nhạy cảm giả định**, không phải ước lượng từ FC01 hay power thực nghiệm. Power thực cần simulation trên các giả định biến thiên seed và cấu trúc, **không dùng kết quả FC01 để hiệu chỉnh threshold**.
3. **F06 / HIGH / MUST-FIX:** Bootstrap `seed → skeleton → family` mô tả hierarchy lồng nhau, nhưng **cùng 16 skeleton/families được đánh giá ở cả 5 seed** (crossed design). Resample skeleton **riêng bên trong mỗi seed** phá cấu trúc common-task coupling. Bootstrap phải giữ nguyên cặp B/C, hai điều kiện, category và có phương án xử lý **seed × skeleton crossed dependence**; nếu tính trên fixed 16 skeleton thì CI có diễn giải có điều kiện, nếu suy rộng sang cấu trúc mới thì n=4 skeleton/category quá ít. 10.000 draws không bù được mẫu cluster nhỏ.
4. Missing/failed run: V1 HOLD toàn bộ, thích hợp. Cần nêu tie policy và exact p construction (đếm `>=` observed, zero included), fixed sample denominator, all 32 sign vectors; không áp dụng phương pháp loại seed có p thuận lợi.

**Bảng tính giả lập, không phải EVAL/science data:**

| Vector d_s (giả lập) | Mean Δ | Exact one-sided p (32 flips) | Kết luận thống kê |
|---|---:|---:|---|
| (.08,.11,.12,.13,.16) | .120 | 1/32=.03125 | Qua p và +10pp |
| (.08,.11,.12,.13,-.01) | .086 | 2/32=.06250 | Trượt p và +10pp |
| (.08,.11,.12,.13,0) | .088 | 2/32=.06250 | Trượt p và +10pp |

**Điều kiện sửa V2:** Chốt estimand (hiệu ứng theo randomness huấn luyện có điều kiện trên 16 OOD skeleton, hay suy rộng sang phân phối skeleton), null và giả định sign symmetry; cung cấp exact enumeration/tie/missing policy đã tiền đăng ký. Lập **power/sensitivity design analysis độc lập không dùng FC01**; nếu 5 seed không đủ power cho confirmatory claim, phải điều chỉnh thiết kế hoặc hạ loại kết quả thành scoped pilot. Định nghĩa crossed-cluster bootstrap với category-preserving resampling và báo wide-uncertainty warning; CI chỉ hỗ trợ, không quyết định gate. Bất kỳ bổ sung seed nào phải nằm trong amendment **trước outcomes** và kèm resource budget.

## R4 — Category gates và diễn giải: **HOLD / MEDIUM**

**Chứng cứ:** [S1] §5, [S2] `statistical_gate`; [S4] và [S6] L0016 cho biết FC01 free generation đúng đầy đủ tập trung tại `rule_constraint`.

**Phát hiện:**

1. **F07 / MEDIUM / MUST-FIX:** Gate kết hợp `p≤.05`, mean≥.10, 4/4 category mean≥0, ít nhất 3/4 category mean≥.05, C absolute≥.25 ở tất cả 4 category là **logical conjunction nhất quán**; category safety guards hạn chế tuyên bố gain chỉ nhờ một nhóm. Tuy nhiên mức +10pp/+5pp/+25% có thể bị chọn bởi tín hiệu FC01 exploratory. Đây là **pilot-informed protocol**, không phải confirmatory threshold hoàn toàn độc lập với pilot. Cần khai báo nguồn chọn ngưỡng và chứng minh chúng đã khóa trước *D1 Bridge outcomes*, không được nói chúng “được lựa chọn trước mọi dữ liệu liên quan”.
2. Gate category không có kiểm định riêng: `Δ_category≥0` là bất đẳng thức **ước lượng**, không chứng minh hiệu ứng không âm của quần thể. Chỉ 4 OOD skeleton/category làm false-positive qua shortcut hoặc false-negative do một skeleton khó trở nên đáng kể. Mean +.10 có thể đạt dù một category phụ thuộc lexical cue; C absolute 25% có thể qua bằng một skeleton rất dễ ×16 lexical worlds.
3. **Phân loại đã có ở V1 là hữu ích**: `POSITIVE_AGGREGATE_SCOPED_NOT_FOUR_CATEGORY` nếu p và magnitude qua nhưng category trượt; `NO_CONFIRMED_FREEGEN_GAIN` nếu p/magnitude trượt; `HOLD_INVALID_PROTOCOL` khi thiếu chứng cứ. Cần quy tắc precedence nếu đồng thời lỗi nguồn và statistical gates: **INVALID_PROTOCOL/HOLD luôn ưu tiên**, không được báo thành tích từ bộ run hỏng. Không đặt tên `CONFIRM_PRIMARY_GO` theo nghĩa cấp GPU/science release; đó chỉ là *outcome label* sau một science GO riêng.

**Điều kiện sửa V2:** Đưa rationale và provenance cho từng ngưỡng; định nghĩa mặt định lượng của category average (seed-balanced vs family-balanced), tie boundary và precedence; lập bảng scenario giả lập để thử interpretation (bao gồm “aggregate gain nhưng một nhóm âm”, “mọi nhóm tốt nhưng p fail”, “accuracy C thấp”); diễn giải guard là descriptive. Thực hiện sensitivity analysis mô phỏng pre-outcome, không retune threshold hậu nghiệm.

## R5 — Data rights, leakage và custody: **HOLD / HIGH**

**Chứng cứ:** [S1] §3, §6–§8; [S2] `independence_and_custody`, `anti_leakage_requirements`; [S3] `unverified_items`; [S4] `privacy_custody`; [S5] §2, §5 yêu cầu phân quyền thực tế, không chỉ tự khai báo.

**Phát hiện:**

1. **F08 / HIGH / MUST-FIX:** Sơ đồ owner TRAIN/VAL, role khác giữ EVAL/gold, blinded reviewer giữ scores là **thiết kế phân vai**, chưa có ACL, key ownership, access logs, ciphertext/hash receipts hoặc bằng chứng tách quyền thực tế. Tách phiên AI không đủ để chứng nhận độc lập; reviewer primary là deterministic parser, nên independent scorer audit quan trọng hơn optional fluency rater.
2. **F09 / HIGH / MUST-FIX:** Rò rỉ có thể qua grammar/generator shared, AST canonicalizer dùng chung, fixed lexical facts, cue–answer correlation, gold fields trong training logs, early parser tuning trên EVAL, negative-sample construction, hyperparameter choice trên VAL có nhìn phân phối EVAL, hoặc pretraining TinyStories chứa cấu trúc tương tự. Shared parent làm một dạng “pretrained prior exposure” không thể loại trừ hoàn toàn; cần đóng giới hạn claim OOD là **novel relative to controlled fine-tuning grammar**, không khẳng định chưa từng gặp trong toàn bộ pretraining.
3. Quyền sử dụng corpus T1, checkpoint parent, synthetic/source spans và PII/attribution cho **nguồn thật** chưa được chứng thực trong chính review này; FC01 archive hashes chỉ xác minh khai báo provenance lịch sử, không tự cấp rights cho data mới.

**Điều kiện sửa V2:** Thiết lập access matrix (owner TRAIN/VAL; custodian giữ sealed EVAL/gold; scorer QA xem synthetic fixtures, không xem EVAL gold trước freeze; reviewer blind chỉ xem blind packet); receipts/ACL và SHA trước release; audit không có file EVAL public hoặc trong trainer env. Negative leakage probe ở mức preexec: cùng lexical cue nhưng đảo condition/gold, hoán đổi nhãn, và cố ý chèn “answer-like string” vào prompt để checker buộc đánh rớt shortcut. Thực hiện independent anti-leakage QA trên source/manifest không lộ gold. Owner cung cấp rights/provenance receipt theo từng nguồn và xác nhận không đưa PII/private dữ liệu lên repo.

**Không thực hiện:** Không đọc private mapping, generator private hay EVAL gold; vì vậy `RIGHTS_ATTESTED=NOT_VERIFIED`, `CUSTODY_ACL=NOT_VERIFIED`, `NONOVERLAP=NOT_EXECUTED`.

## R6 — Reproducibility, feasibility, resources: **HOLD / HIGH**

**Chứng cứ:** [S1] §2, §4, §5, §7; [S2] `frozen_parent_constraints`, `future_one_packet_owner_release_requires`; [S4] `known_limitations` nêu “actual resume from step 64 not experimentally demonstrated”.

**Phát hiện:**

1. **F10 / HIGH / MUST-FIX:** Có SHA parent step1024 và T1 BPE lịch sử, nhưng chưa có proof cho **new D1 Bridge runner**: load đúng checkpoint FP32, deterministic sampler across B/C, đầy đủ AdamW optimizer *moment tensors/step*, scheduler, RNG Python/NumPy/Torch CPU/CUDA, sampler cursor, batch boundaries, gradient accumulation, and actual pause/resume **sau khi moments khác 0**. Snapshot zero-step không phải bằng chứng khôi phục training tương đương bitwise. Không có lý do coi 15 science runs có thể resumable khi chưa QA.
2. **F11 / MEDIUM / MUST-FIX:** 15 run, 3.840 updates, 7.680 generations là arithmetic đúng; nhưng T4 miễn phí và yêu cầu chi phí $0 chưa có phép đo allocated GPU memory, throughput, Drive quota, runtime disconnect behavior, retry/resume overhead hay lịch thực thi. **Feasibility on free T4 = NOT_VERIFIED**. Không cam kết thời lượng/khả năng có T4 hoặc tính phí 0 khi không có receipt.
3. **F12 / MEDIUM / MUST-FIX:** B/C cùng byte dữ liệu, episode order, step và token slots tạo đối chứng mạnh cho **data equality**, nhưng C có contrastive objective có thể cần additional negatives/forward passes và compute khác B. Cần chốt *estimand objective-at-fixed-data-and-updates* và report FLOPs/walltime/negative exposure; không gọi là “same compute” nếu chưa đo và cân bằng. A singleton tuy balanced labels/cues vẫn có distributional difference, chỉ báo secondary.
4. Nhóm 224+32 token chỉ vừa 256 về đại số; cần test true T1 tokenization, BOS/special tokens, output EOS/truncation, pad. FP32 trên T4 có thể là trade-off compute/memory, không đủ căn cứ tuyên bố preflight PASS.

**Điều kiện sửa V2:** Lock code/env/dependency hashes, parent/tokenizer exact bytes, dataset manifests, update/optimizer-step semantics, sampler permutations, per-seed pairwise input SHA và paired checkpoint policy. Actual positive-moment resume fixture: (a) uninterrupted K steps, (b) interrupted after nonzero moments then resumed to K, compare model/optimizer/scheduler/sampler/RNG and final outputs under prereg tolerance; negative cases corrupted/partial checkpoint and wrong SHA must fail-closed. One-shot run record có preflight T4 free allocation, vRAM RAM disk/runtime/storage/quota measured, retry/abort rules, atomic writes, hashes, preservation of partial/failed evidence, cost=0 guard. Không cấp science GO trong review này.

## 3. Đánh giá tính xác nhận và lỗi phân loại

**Có thể giữ:** H1 C-vs-B objective-only khi data thực sự identical; primary family-level both-conditions; greedy deterministic; STEP256 not selected by EVAL; seed fixed; category guard; no replacement after failed OOD overlap; D1 existing immutable.

**Chưa thể công nhận:** “Unseen structural OOD verified”, parser validity, five-seed confirmatory statistical power, rights/custody pass, actual nonzero-moment resume, fixed-$0 T4 feasibility. Tất cả mới là requirements hoặc `NOT_EXECUTED`, không thể chuyển thành PASS từ tự kiểm 26/26.

**Không xác định `FAIL_INVALID_DESIGN`:** H1 là câu hỏi kiểm nghiệm có thể thiết kế để falsify; dữ liệu hiện không chứng tỏ hypothesis bất khả thi. Những lỗ hổng nghiêm trọng là sửa được bằng V2 và independent source QA. Không sử dụng kết quả FC01 để kết luận gain của D1.

## 4. Một gói amendment tập trung trước prereg

**Đề xuất một gói duy nhất:** `TTM_D1_BRIDGE_V2_SINGLE_PACKET_PREREG_AMENDMENT` — tạo phiên bản mới, không ghi đè protocol V1, không thay D1 hiện hữu; cập nhật append-only provenance sau khi owner chấp thuận. Các hạng mục sau là **must-fix trước khi source QA/GO thiết kế mới**:

| ID | Nội dung V2 phải bổ sung | Đường dẫn/trường V1 bị ảnh hưởng | Tiêu chí đóng |
|---|---|---|---|
| AM01 | Formal typed AST, semantic equivalence, anti-isomorphism, structure-wise split/negative tests, claim scope | [S1] §3; [S2] `structural_splits` | Independent structural QA defined; OOD actual overlap vẫn `NOT_EXECUTED` cho tới khi có dữ liệu |
| AM02 | Typed action oracle A/B, discriminability, parser contract và positive/negative fixtures; ambiguity/EOS policy | [S1] §4; [S2] `decoder_and_primary` | Parser spec coherent; actual parser QA remains a future gate |
| AM03 | Estimand, sign symmetry assumption, exact p ties, power/sensitivity trước outcomes, crossed bootstrap và đúng giới hạn claims | [S1] §5; [S2] `statistical_gate` | Independent mathematical review; no posthoc FC01 calibration |
| AM04 | Justification và priority của category guards, reject/hold precedence, false-positive/negative scenarios | [S1] §5; [S2] `statistical_gate` | Decision table unambiguous |
| AM05 | Rights provenance, owner/custodian/scorer ACL matrix, sealed SHA/custody lifecycle, leakage negatives | [S1] §3/§6/§7; [S2] `independence_and_custody` | Access architecture specified; owner/source evidence later verified |
| AM06 | Full source/runner contract, optimizer-moment resume positive/negative QA, resource envelope, B/C exposure/compute accounting, T4 fail-closed | [S1] §2/§7; [S2] `future_one_packet_owner_release_requires` | Feasible one-packet preexec plan with explicit stop conditions |

**Optional, không thay thế must-fix:** Bổ sung robustness báo cáo từng skeleton (có uncertainty) và so sánh mô tả B−A; công khai độ nhạy theo chuẩn synonym/parser và category breakdown ở mức aggregate sau khi được phép. Không mở TEST/Q1Q2.

**Không nên** chạy science V1 “để xem dữ liệu trước” rồi chỉnh V2; mọi ngưỡng/seed/policy phải khóa trước outcome mới. Nếu V2 không chứng minh power khả dụng trong ngân sách T4 miễn phí, quyết định phù hợp là **HOLD hoặc scoped pilot**, không phải confirmatory GO.

## 5. Verdict tích hợp duy nhất

`D1_BRIDGE_DESIGN=HOLD_REVISE_BEFORE_PREREG`  
`D1_BRIDGE_SCIENCE=HOLD`  
`REVIEW_SOURCE_FILES_VERIFIED=6/6_GITHUB_BLOB_METADATA`  
`SOURCE_ONLY_REVIEW_COMPLETE=TRUE`  
`INDEPENDENCE=AI_SELF_ATTESTED_NEW_CHAT / NOT_EXTERNALLY_VERIFIED`  
`AST_NONOVERLAP=NOT_EXECUTED` · `PARSER_IMPLEMENTATION_QA=NOT_EXECUTED` · `RIGHTS_ACL=NOT_VERIFIED` · `GPU=0` · `NEW_TRAINING=0`.

**Bước thực hiện tiếp theo (duy nhất):** `TTM_SMALL4M_D1_BRIDGE_V2_SINGLE_PACKET_PREREG_AMENDMENT_SOURCE_QA_AND_OWNER_GO_HOLD_NO_GPU` — owner giao một packet V2 gồm AM01–AM06, reviewer khác kiểm lại hợp đồng và nguồn, rồi owner ra một GO/HOLD **chỉ cho bước triển khai kiểm chứng nguồn tiếp theo**, giữ science HOLD. Không chia micro-permits, không tạo gold/EVAL hay mở sealed TEST.
