# TTM Small-4M — Phân xử roadmap tích hợp Repair-First × Karpathy V2 × ABC main

**Operation:** `TTM_PM_SMALL4M_REPAIR_FIRST_KARPATHY_V2_ABC_MAIN_INTEGRATED_ROADMAP_ADJUDICATION_SINGLE_GATE`  
**Ngày:** 2026-11-17 · **PM adjudication:** `PASS_INTEGRATED_ROADMAP_DESIGN_SCOPED_WITH_AMENDMENTS` · **Runtime:** `HOLD_NO_MODEL_RUN`  
**Source of truth:** `minhtri22/TokenToModel-Lab`; `main=e102d2ed3c885756b6e4354189ccbece36b75eb8`; Claude design branch `6b1ebc2e3103ebed066b1caa2a135ea2b760a159`.  
**Mục tiêu duy nhất:** tiến tới một GPT baseline từ nguồn đã tích hợp, tái lập được và có thước đo năng lực hợp lệ trước khi phân xử data, compute, objective, capacity. **Không** mở Question Gate mới, chạy checkpoint/model/GPU/TEST, đổi frozen science, sửa `lineage.md` hay cấp quyền I2/SFT.

## 1. Quan hệ của ba roadmap và hiện trạng có thẩm quyền

1. [`docs/PHASE_PLAN.md`](../../docs/PHASE_PLAN.md) là **kiến trúc dài hạn P00–P12**; P07/P08 không tự mở vì P02–P06 có QA; Pilot T1–T7 ưu tiên train-first nhưng không tự mở P09/P10/P11.
2. [Repair-First roadmap cũ](https://github.com/minhtri22/TokenToModel-Lab/blob/1e44678de2736e3a2785fe55b51fdae62fdf8717/docs/roadmap/TTM_GLOBAL_REPAIR_FIRST_ROADMAP_20261116.md) và [RF backlog](https://github.com/minhtri22/TokenToModel-Lab/blob/1e44678de2736e3a2785fe55b51fdae62fdf8717/docs/roadmap/TTM_GLOBAL_REPAIR_FIRST_BACKLOG_20261116.md) là **snapshot 16/11 trên nhánh kế hoạch khác, chưa có trên `main`**. Các dòng `RF-00=HOLD_I1...` và `RF-01=WAIT_RF-00` đã lỗi thời ở phần I1 sau `main` L0030. **Không viết lại lịch sử 16/11**; xem snapshot rebase mới ở JSON đi cùng OnePack.
3. [Claude STEP0–STEP6 v2](https://github.com/minhtri22/TokenToModel-Lab/tree/6b1ebc2e3103ebed066b1caa2a135ea2b760a159/docs/research/ttm-small4m-incontext-probe-roadmap) có **bảy tài liệu**, là bảy blob mới trên một nhánh *đã đưa main làm tổ tiên*, **chưa merge ngược vào main**. Claude tự đánh dấu `DESIGN_PROPOSAL_NOT_AUTHORIZED` và `INDEPENDENT_REVIEW_NOT_PERFORMED`. PM review trong OnePack này là phân xử thiết kế, không tuyên bố đã có QA runtime độc lập.
4. `main` sau PR [#39](https://github.com/minhtri22/TokenToModel-Lab/pull/39) và [#40](https://github.com/minhtri22/TokenToModel-Lab/pull/40): **76 Git blobs B/BC/C đã merge, six-job CI Win/Linux PASS**; `lineage.md` L0000–L0035. A-I1 measurement `PASS_SCOPED`, A V4 `DESIGN_ACCEPT_SCOPED`, A-I2 `HOLD_NOT_EXECUTED`. B M3 engineering `PASS_SCOPED_WITH_HISTORICAL_NATIVE_DISSENT`. C M4 design `PASS_SCOPED`. B/C synthetic engineering `PASS_SCOPED`. `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED`. **Không** có real T4-to-BC adapter, real SFT hay owner science GO.
5. [`ACTIVE_RESEARCH_GATE.md`](../../docs/governance/ACTIVE_RESEARCH_GATE.md) cũ là snapshot 16/11, có `I1_I4=NOT_EXECUTED` và `lineage=UNCHANGED`; trạng thái hiện thời **được supersede bởi addendum chính xác trong PR docs này**. Question `TTM-SM4M-DIAG-Q001` đã đăng ký engineering, Q4 release/run chưa được mở; `TTM-P0A-MEAS-Q001` đóng `CLOSED_HOLD_EVIDENCE_INSUFFICIENT`, không mở lại ontology.
6. Theo [Question-First policy](../../docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md), `lineage` không phải task board. OnePack thiết kế này không append lineage, không mở nghiên cứu thứ hai, và không biến PASS QA thành science PASS. Những entry kỹ thuật đã tồn tại L0030–L0035 **không bị chỉnh hồi tố**.

## 2. Ma trận phán quyết 7 tài liệu Claude — exact Git blob

| Step | Git blob SHA-1 tại `6b1ebc2e...` | Phán quyết PM về thiết kế | Không được suy ra |
|---|---|---|---|
| STEP0 Sanity/Reference | `470e0956ea4023f6aa6939c5b45218faab2240de` | `ACCEPT_PRIORITY_WITH_REQUIRED_CORRECTIONS`; **đầu việc kỹ thuật đầu tiên**, gồm kiểm tra nguồn tĩnh và hợp đồng negative QA; chưa chạy | `STEP0_RUNTIME_PASS`, checkpoint/optimizer authorized |
| STEP1 Data×Compute Curve | `1d61b0d735c5b0b764c45f675cf59f0be80702cd` | `ACCEPT_PROSPECTIVE_DESIGN_REVISE_CLAIM`: ratio 12 và ~44.04M token là **planning horizon**, không chứng nhận compute-optimal | `GO_T44`, đủ fresh independent tokens, ngân sách ~13 phút đã xác minh |
| STEP2 Teacher-forced & ending controls | `479a4455b77706d63b83942e77ee9df4f885f88b` | `ACCEPT_CONTRACT_DESIGN_WITH_NEGATIVE_CONTROLS`, thiết kế hợp đồng đo song song STEP0 | `GO_M1024_FORWARD`, nguồn weights có thể đọc, probe đã hiệu chuẩn |
| STEP3 Free-form measurement scale | `4e8054e5d0aa2b704818a66426cdcc341e109ffa` | `DEFER_SECONDARY_ENDPOINT`; ưu tiên programmatic/likelihood trước, giữ provenance và positive controls | AI rater đã được chứng nhận, dùng lại FINAL24/FRESH16 |
| STEP4 One-factor architecture ablations | `d56243a0f3f7a668dca3bcf37856b89410908402` | `DEFER_UNTIL_BASELINE_AND_PROBE_VALID`; điều khiển FLOPs/token & changes one at a time | RoPE/Muon/RMSNorm tự nhiên tốt hơn |
| STEP5 Objective/capacity ladder | `467c67f444d5b34d8a2f8e2f870fa4e1606f01a6` | `DEFER_CONDITIONAL_SCALE_AND_SFT`; d4/d6/d8/d12 là ước tính, real SFT HOLD | tokenizer/checkpoint hiện tại tự động dùng được cho SFT |
| STEP6 Rights/checkpoint custody | `b413bdd8a6bb15e1ca62cd299374aca9a57ed4b3` | `ACCEPT_PARALLEL_DOCUMENTARY_CUSTODY_PLAN`, tập trung đúng hành động: local inference, fresh pretrain, release khác nhau | giấy phép mã/weights đã đủ, hash trên máy đã được verify |

**Thứ tự được PM áp dụng:** `STEP6 documentary evidence` chạy **song song** với **STEP0 source-only contract**; thiết kế fixture/metric STEP2 song song nhưng **runtime STEP2 chỉ sau admission riêng**. **STEP0 technical validation thực thi** → nếu PASS mới xem xét **STEP1 candidate dữ liệu × compute**, kết hợp STEP2 probes trên mới/đúng nguồn. STEP3 phụ thuộc nhu cầu sinh tự do. STEP4/STEP5 tùy kết quả phân tích data/compute/probe; không mở tất cả đồng thời.

## 3. Finding cần sửa trước khi coi STEP0 đã sẵn sàng thực thi

| ID | Phát hiện, căn cứ và sửa bắt buộc | Phân xử |
|---|---|---|
| `PM-F01` | STEP0 trộn kiểm toán nguồn, overfit mới, quét LR, decode checkpoint và so logits M1024 trong một bảng. **Tách scope theo thẩm quyền**: đọc/thiết kế được thực hiện ngay; thử synthetic cần Q4 scoped implementation; truy cập real checkpoint hay huấn luyện thật cần witness/owner exact GO. **Không tạo micro-permit cho từng phép thử.** | `HOLD_STEP0_RUNTIME` |
| `PM-F02` | Ngưỡng `abs(init_nll-ln(2048))<=0.05` chỉ có ý nghĩa nếu logits đầu ra gần uniform dưới init TTM thật. Tied embedding & init có thể lệch; chấp nhận làm **sanity expectation**, không **hard FAIL** trước khi dẫn xuất expected distribution bằng reference. | `AMEND_INIT_ORACLE` |
| `PM-F03` | STEP0 `loss<=0.05/600 steps` và `loss<=0.3/2000` không dựa trên calibration; định nghĩa overfit một batch tối thiểu, finite loss, loss giảm, gradient/update khác 0 và terminal capability phải phù hợp toy fixture. Ngưỡng cứng, seed, dtype, device, optimizer + budget chỉ freeze sau independent review. | `AMEND_OVERFIT_THRESHOLDS` |
| `PM-F04` | “`-100` label không sinh gradient” phải diễn đạt chính xác: **không có đóng góp loss trực tiếp của target bị mask**, nhưng token input ở vị trí đó có thể ảnh hưởng logits của target **về sau**, vì causal context. QA phải kiểm contribution/derivative ở output bị mask, không bắt mọi embedding gradient tại input token phải bằng 0. | `CORRECT_MASK_SEMANTICS` |
| `PM-F05` | Causal logits <= t không được phụ thuộc tokens >t trong eval deterministic; tolerance FP32 cần khóa theo actual reference/kernel. Tách **label-shift correctness** (input x[t] → target y[t]=next token) khỏi causal-masking probe; không dùng historical TEST để tuning. | `KEEP_NEGATIVE_QA` |
| `PM-F06` | T4 actual source `t4_data_pack.py` encode(truyện)+EOS, cửa sổ 256, masked -100, không mang EOS làm input theo cách dựng được đọc. Phải kiểm source/pack actual ở scope đã được cấp, không giả định phục hồi duy nhất từ prose. STEP2 bỏ prefix EOS khỏi synthetic story probe là sửa đúng về thiết kế. | `ACCEPT_CONDITIONAL` |
| `PM-F07` | STEP0 “reference parity” cần **cùng kiến trúc/tie/position/norm/activation/weights** trước logits strict parity; reference nanoGPT/nanochat cấu hình khác không chứng minh lỗi chỉ vì metric lệch. Phân biệt kiểm toán gradient synthetic, exact weights readback và đường học nhiều seed. | `AMEND_REFERENCE_COMPARABILITY` |
| `PM-F08` | STEP0 0.8 LR sweep, 0.9 sample generations và STEP1 R0–T88 là **công việc runtime/new study**, không được ngầm ghép vào approval source-only. VAL-TUNE mới phải được xác minh độc lập, không reuse original VAL/TEST. | `HOLD_NEW_STUDY` |
| `PM-F09` | STEP1 dùng tham số scaling ~3,670,016, T4 unique total 3,749,376 và 4,194,304 **exposures** vs 498,287 **TRAIN targets**. Tỉ lệ nanochat 12 không chứng minh compute optimum trên TinyStories/T4; cần đo hai trục **distinct training bytes/token diversity** × **seen tokens / measured FLOPs**. Theo source chưa chứng minh 74s/1024 đại diện full-session T44. | `RENAME_TO_CANDIDATE_HORIZON` |
| `PM-F10` | `val_bpb` phải dùng full-vocabulary NLL (nats) của **valid UTF-8 text targets** chia cho `ln(2)*valid_bytes` đúng byte-span, exclusion stop/protocol khỏi cả numerator và denominator. Không chia NLL cho fractional BPE segment và không map T4 BPE merges 257–2047 sang B/C special IDs 257–262. A `a_gold_nll` vẫn nats cho một gold next-token, không phải bpb. | `ABC_MEASUREMENT_LOCK` |
| `PM-F11` | STEP2 Probe A/B/C fixture có **gold lập trình** dù không cần AI rater; cần counterbalance name/order/length, gold-blind scorer, constant logits & context-blind negative, shuffling+swapped unrelated entities, no answer leakage. Candidate 4-token log-prob scoring cần quy định sum/mean theo byte/token cho lựa chọn nhiều token; primary nên cùng độ dài/đơn token, reporting chance accuracy. Các threshold 0.3nat, 2nat, 0.60 mới chỉ proposal. | `HOLD_PROBE_VALIDATION` |
| `PM-F12` | STEP6 mã băm M1024/M1280 là **historical recorded**, không phải bytes đã được read lại trên máy owner; A-I2 gate và new checkpoint tests vẫn HOLD. TinyStories external license/rights phải quyết định theo **hành động**; chứng nhận local inference không cho phép phân phối weights hay pretrain corpus mới. | `HOLD_REAL_CUSTODY` |
| `PM-F13` | `ACTIVE_RESEARCH_GATE.md` 16/11 ghi I1_NOT_EXECUTED; sau PR39/40, lineage L0030 xác nhận `I1_CLOSED_PASS_SCOPED` còn `I2_HOLD`. RF-00 `HOLD_I1_SCORER_LABEL_LEAKAGE` là finding lịch sử đã sửa ở phạm vi scorer I1; **không** tự xoá R5 runtime owner-signer/race/ledger hay nâng R8. | `REBASE_STATUS_ONLY` |

**Chú ý phạm vi nguồn:** mã `src/p02/transformer_core.py` ở `main` (blob `9762343e06cf800b50574c2871ae1ed58537fb18`), `tools/pilot_t4/integrated/t4_data_pack.py` (blob `cdce219f2a2df27e25579f069238d4327c1d7d91`), `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py` (blob `76c4d0155cd0736919f41682f240b47ad3d7c428`), `src/ttm_track_b/bc_sft_interface.py` (blob `636a7d695e49802e3d8d80ab0ef06f25ef7d8322`) đã đọc qua GitHub. **Không** chạy mã, đối chiếu raw private weights, tokenizer runtime hay packet riêng trên máy owner.

## 4. Hợp đồng nghiệm thu STEP0 — gói đầu tiên, không chia micro-permit

**Tên duy nhất khi được owner cho phép sau Q4:** `TTM_SMALL4M_STEP0_EXACT_BASELINE_SANITY_REFERENCE_AND_SOURCE_CUSTODY_ONEPACK`.

### 4.1. Ngay bây giờ: `STEP0_CONTRACT_READY_SOURCE_DESIGN_SCOPED` (được phép ở mức tài liệu)

**Một bộ deliverable đã xác định:** (a) exact P02/T4/BC/C source manifest + status already PASS; (b) ma trận input/tokenizer/label-shift/EOS/byte-coverage source-only; (c) bộ test-oracle được thiết kế và negative-case/positive-case có quy tắc no-leak; (d) định nghĩa NLL/token + `val_bpb` exact UTF-8 (with stop-token exclusion); (e) danh sách fixture synthetic/VAL-TUNE *proposed* với source permission và group split; (f) reference implementation matching grammar and exact tested source interface; (g) owner resource/checkpoint/R5 witness *missing listed*, không tự gọi thành PASS.

**Review criterion để chấp nhận hợp đồng:** reviewers xác nhận mỗi target xác định được nguồn, output, oracle, negative case, test-scope và bằng chứng kiểm toán, không có alias T4↔BC hay historical TEST. Một freeze hành động nếu owner đồng ý, không 9 permit.

### 4.2. Tương lai có điều kiện: `STEP0_EXECUTION_HOLD`

Chỉ khi active `TTM-SM4M-DIAG-Q001` đạt đúng Q4 owner scoped GO, source/code/runtime witness R0–R8 áp dụng đã được QA, mới có thể thực thi các phép synthetic gradient, actual checkpoint inference, micro-overfit, LR sweep hoặc train/samples theo phạm vi thực. **Thiết kế không cam kết mọi phép STEP0 phải chạy cùng ngày/permit**; nếu đòi thay đổi câu hỏi, scope hoặc dữ liệu thì phải prospective closure theo Question-First trước chứ không lén mở nhánh khác. Hướng chủ đạo là **đầu tiên một gói chẩn đoán tối thiểu đủ phân biệt**; không tự đòi 3 seed × 1,024 steps hay 600/2,000 batch steps trước khi có chứng minh resource.

**Tiêu chí PASS thực thi tương lai:** exact source+fixture/target byte pin & no leakage; causal/shift/mask negative QA theo oracle; seeded synthetic gradient and overfit capability calibrated; exact checkpoint strict load/no alias nếu run truy cập real weights; full-token NLL/bpb parity trên fresh authorized VALIDATION; distinct QA và bounded host/GPU resource; owner decision, all persisted with SHA. **FAIL/HOLD** nếu lệch hoặc thiếu, không sửa output history.

## 5. Điều kiện bắt đầu STEP1 và STEP2 — nêu một lần, không xin permit rời rạc

| Tiêu chí | STEP1 — prospective data×compute | STEP2 — prospective teacher-forced probes |
|---|---|---|
| Phụ thuộc trên STEP0 | `PASS_STEP0_EXACT_BASELINE_EXECUTION_SCOPED` **hoặc** xác nhận được minimum baseline subset hợp lệ cho study mới, được owner quyết định rõ | `PASS_STEP0_SCORER_AND_TOKEN_BOUNDARY_SCOPED` trước runtime probes |
| Dữ liệu/byte | quyền TinyStories/new data, distinct independent TRAIN token counts, family/group-disjoint splits, fresh VAL2, no used TEST | fixture source-anchored synthetic with deterministic oracle, gold-blind evaluator, tokenization single-token validity |
| Model | fixed T4 cfg/checkpoint lineage, new checkpoint scheme if training from scratch; freeze optimizer/seed/clock | M1024/M1280 SHA actual verified on owner host, strict source/config load, no alias, random-init controls as defined |
| Measurement | `val_bpb` complete byte denominator; primary + secondary frozen; R0/R1 equal compute and T11/T22/T44 staged resource feasibility | A/B/C positive and negative probes, constant-logit & context-blind falsifiers, paired counterfactual and exact score normalization |
| Compute/budget | actual measured FLOPs/step+IO+eval and memory, no extrapolated 13min GO; freeze stopping rules | bounded forward calls, no training, no uncontrolled access to consumed TEST |
| Governance | 1 prospective question, original Question Gate closure status handled, owner GO scope, independent source QA, distinct science review | owner GO for exact checkpoint/fixture; independent probe validity and exact QA |
| Current status | **`HOLD_STEP1_NEW_TRAINING`** | **`DESIGN_ONLY_PROBE_CONTRACT; HOLD_M1024_MODEL_FORWARD`** |

**Nội dung STEP1 có thể xem xét sau admission:** trước hết so R0 repeat-vs-R1 new-unique at equal compute 4,194,304 exposures; thí nghiệm T11/T22/T44 chỉ là các option phụ thuộc quality/budget. Không giả định T44 toàn bộ là token mới duy nhất nếu corpus inventory không đủ; không dùng TEST/FINAL24.

**STEP2 được chốt ở mức khung đo song song STEP0:** Probe A induction/copy, Probe B binding via teacher forcing, Probe C candidate ending. Sử dụng full-vocab logits và scoring không phụ thuộc gold; đủ negative controls để loại estimator gold-leak. Các threshold không được frozen chỉ vì tác giả đề xuất.

## 6. Một hợp đồng ABC thống nhất cho hướng phát triển tiếp theo

- **PM** giữ *một* source-pins + versioned science/engineering manifest, owner decision, merge policy, nhận định PASS/HOLD; không tạo chain micro-ticket.
- **A / Measurement**: metric contract `a_gold_nll` vs `val_bpb`, causal/label shift, negative estimator falsifiers và boundary R5, không tự vượt owner I2 HOLD.
- **B / Runner**: cấu hình T4 3,749,376 params và core mới đã merge, runtime/test fixtures tài nguyên có điều kiện; không lẫn special ID B/C synthetic vào BPE T4.
- **C / Data & Science**: rights/family split/fresh heldout, gold-blind probe oracle, TRAIN-only tokenizer and no TEST contamination, prereg equal measured compute.
- **Nhất quán:** A/B/C chỉ làm trên **cùng một schema/sha/revision** do PM freeze; mỗi bên ACK chính exact revision trước khi triển khai. Nếu chỉ là thiếu evidence, ghi HOLD một lần, không tự chạy nguồn riêng hoặc sửa hợp đồng lén.

### Phân loại cải thiện trong tương lai

(1) `ENGINEERING_VALIDITY`: source/CI/negative QA có thể PASS mà không nâng science. (2) `SCIENTIFIC_EFFECT`: chỉ khi prereg, actual run, controls, fresh data, confidence/uncertainty và distinct adjudication; ghi science outcome đúng chính sách hiện hành. (3) `APPLICATION_READINESS`: SFT thật, serving/KV GPU và phát hành có admission riêng; không suy theo một loss tốt.

## 7. Quyết định và phạm vi hợp nhất

**PASS của operation:** `PASS_INTEGRATED_ROADMAP_DESIGN_SCOPED_WITH_AMENDMENTS`. Đây là PASS cho **bản roadmap tích hợp mới**, không đồng nghĩa 7 tài liệu gốc của Claude được tự động merge hoặc cả 7 proposal thresholds đã được reviewer hiệu chuẩn.

**Trạng thái khóa:** `ABC_MAIN_MERGED · A_I1_CLOSED_PASS_SCOPED · A_I2_HOLD · REAL_SFT_HOLD · STEP0_SOURCE_DESIGN_FIRST · STEP0_EXECUTION_HOLD · STEP1_NEW_TRAINING_HOLD · STEP2_CONTRACT_DESIGN_ONLY · STEP4_STEP5_DEFER · NO_NEW_QUESTION · NO_MODEL_RUN · NO_TEST · NO_GPU · LINEAGE_UNCHANGED`.

**Merge decision hiện tại:** `HOLD_MERGE_REVIEW` cho candidate governance docs. Nhánh Claude là nguồn tham khảo bất biến, chưa merge ngược. Các tài liệu mới của PM được giữ trên governance review branch. Chỉ sau PR QA và owner chấp nhận mới cập nhật `main`; không mở research/implementation branch mới trong lượt này.

**Bước thực hiện tiếp theo — duy nhất sau khi owner xét hồ sơ:** quyết định **chấp nhận hoặc HOLD bản roadmap tích hợp và hợp đồng STEP0 source-only** trên đúng revision GitHub PM, với một PR docs-only; nếu chấp nhận, STEP0 engineering sẽ được đưa vào **Question Gate hiện hành** để xét Q4 phạm vi thực thi một lượt, không tự GO. Không lặp QA I1, B M3, C M4 hoặc BC V2 đã PASS.
