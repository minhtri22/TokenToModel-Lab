# SM4M-Q001 — Q3 Distinct Independent Architecture & Causal Evidence Review

**Operation:** `SM4M_Q001_DISTINCT_INDEPENDENT_ARCHITECTURE_SOURCE_EVIDENCE_ADMISSION_REVIEW_Q3_SINGLE_GATE`  
**Ngày review:** 2026-11-15  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Draft PR:** `#21`  
**Exact candidate HEAD:** `3c53d062c7c6ff4218d80177253dd1c061ac6362`  
**Baseline main HEAD:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`  
**Reviewer role:** `DISTINCT_INDEPENDENT_SCIENTIFIC_ARCHITECTURE_AND_EVIDENCE_REVIEW_SESSION`  
**Mode:** `READ_ONLY · SOURCE_AND_DESIGN_REVIEW · NO_SCIENCE_EXECUTION`

## 1. Phán quyết

**`HOLD_Q3_REMEDIATION`**

Q2 đúng ở ba kết luận cốt lõi:

- `KEEP_HISTORICAL_REFERENCE_ONLY` — **AFFIRMED**.
- `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE` — **AFFIRMED**.
- `ROOT_CAUSE_NOT_IDENTIFIED` — **AFFIRMED**.

Không tìm thấy source defect đã xác nhận trong Transformer/trainer T4 ở phạm vi public source. Tuy nhiên candidate hiện tại chưa đủ điều kiện nhận `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED` vì có hai sai lệch material:

1. machine-readable admission matrix hoãn `AD-03`/`AD-06` đến trước scoring dù đây là điều kiện tạo/freeze benchmark;
2. `ACTIVE_RESEARCH_GATE.md` tự mâu thuẫn về trạng thái Q2/Q3 và đưa hai “single next step” khác nhau.

Đây là **HOLD để sửa gói quản trị/thiết kế**, không phải FAIL khoa học, không phải yêu cầu sửa architecture, và không cấp quyền tạo dữ liệu hay chạy model.

## 2. Independence declaration và phạm vi

Review này đọc exact candidate bằng commit pin, không dùng branch HEAD động. PR #21 được xác nhận `open · draft`, head đúng `3c53d062c7c6ff4218d80177253dd1c061ac6362`, base đúng `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`, 10 changed files, candidate ahead baseline 1 commit và behind 0.

Không train, inference, GPU, rescore, unblind, private checkpoint reacquisition, TEST/FINAL replay, code patch, merge hay `lineage.md` update.

## 3. Exact input integrity — 7/7 PASS

| Input | Git blob SHA-1 | Raw SHA-256 | Q3 verify |
|---|---|---|---|
| `docs/governance/sm4m-q001/SM4M_Q001_INTEGRATED_ARCHITECTURE_AUDIT_20261115.md` | `b289f1056a9c0bb862a4813cbf0d2189b34c233d` | `4973ad744f5d2e2e9e89f46e7890a37833c43cd99fdb82405be2148a580bce06` | **PASS** |
| `artifacts/governance/sm4m-q001/SM4M_Q001_AUDIT_RECEIPT_20261115.json` | `74023311e224e552c46899a7547eb5f73deddc52` | `9fbfb2b185043685b5d24e352eb7b029b6fc36098f5a735cd699b9b5f2261f4a` | **PASS** |
| `docs/governance/sm4m-q001/SM4M_Q001_Q2_AUTHOR_ADVERSARIAL_QA_LITERATURE_TRIAGE_20261115.md` | `380582a4f1260dfda28d39e0cb56be2fc02709c5` | `34c553d10250b8403a4d2e7170ce6f0329fa14284ea5018f59de35af94622d36` | **PASS** |
| `artifacts/governance/sm4m-q001/SM4M_Q001_AUTHOR_ADVERSARIAL_LITERATURE_QA_RECEIPT_20261115.json` | `c984ca474c112494bfe472d4293c2da7e4a6eefb` | `5254fbb557c2074d95d7aa65e14e6c2924e8da1979e12f6fe4b1340958303a65` | **PASS** |
| `docs/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_ADMISSION_LOCK_20261115.md` | `d82202778fe3bc620335af18b0fa7ea1fec4094c` | `b34ad81e81e90ba5873cb1c8207592f8b078023aba60f2e57cd7ef1229376a8e` | **PASS** |
| `artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_20261115.json` | `b7e87dbdd31c6624387f9943d7ff7db8efa8663a` | `306d32086fa1e19a910070577e0f9fbd7d0a130d792ff225e1f35768237a105b` | **PASS** |
| `artifacts/governance/sm4m-q001/SM4M_Q001_Q2_AUTHOR_ADVERSARIAL_QA_RECEIPT_20261115.json` | `a3a22b0cc8515979c9034d02e497ecf8f7b1fee4` | `ed0bc795c3d129cdf4c99761f96cb04888a0c9cebfb83010c0463c712be4e403` | **PASS** |

Tất cả 7 blob SHA-1 và 7 raw SHA-256 được tính/đối chiếu độc lập từ nội dung exact candidate và khớp manifest owner. Không có finding byte-integrity ở packet Q2.

## 4. Architecture traceability

| Requirement | Exact source | Checkpoint/config relation | Q3 judgment |
|---|---|---|---|
| Decoder-only Transformer | `src/p02/transformer_core.py` blob `9762343e06cf800b50574c2871ae1ed58537fb18` | T4 dùng `P02Config(**CONFIG)`, không dùng default P02 | **MATCHED** |
| T4 config | `tools/pilot_t4/integrated/t4_capacity_smoke.py` blob `c9a6f256ba975228683ee7de2a1090e649110e97` | vocab 2048, context 256, emb 256, 4 blocks, 4 heads | **MATCHED** |
| Unique parameters | P02 + T4 config | arithmetic độc lập = **3,749,376** unique params, head tied | **MATCHED** |
| Position | `transformer_core.py` | learned absolute position `[256,256]` | **MATCHED** |
| Attention | `transformer_core.py` | causal triangular mask, 4 heads × 64-dim | **MATCHED** |
| Block topology | `transformer_core.py` | pre-LN residual; FFN 256→1024→256, GELU | **MATCHED** |
| Output tying | `transformer_core.py` | `head.weight = tok.weight` | **MATCHED** |
| Real T4 loss path | `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py:L92-L103` | `model(xx)` then external CE, `ignore_index=-100`, reduction sum / 4096 | **MATCHED** |
| Training budget | trainer + T4 config | 1024 steps × 4096 valid targets = **4,194,304 target exposures**, không phải independent tokens | **MATCHED** |
| Split | `tools/pilot_t4/integrated/t1_source_split_tokenizer.py:L26-L29,L138-L183` | 2048 TRAIN, 256 VAL, 64 TEST | **MATCHED** |
| BPE fit | `t1_source_split_tokenizer.py:L187-L213,L256-L263`; `ttm_gpt2_bpe2048.py` | 768 TRAIN stories; vocab 2048, EOS=256, 1791 merges | **MATCHED** |
| Data pack | `tools/pilot_t4/integrated/t4_data_pack.py` | pack TRAIN/VAL only, no TEST arrays | **MATCHED** |
| Evaluator | `tools/pilot_t4/integrated/t4_eval.py` | bigram fit TRAIN; bootstrap 256 story clusters | **MATCHED** |
| Historical checkpoint | prior T4 adjudication | SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` | **HISTORICAL PROVENANCE ONLY; NOT PRIVATE-BYTE REVERIFIED IN Q3** |

### Architecture conclusion

`SOURCE_IMPLEMENTATION_MATCHED_SCOPED`. Không có căn cứ source-only để nói attention, FFN, embedding, layer count hoặc head count là root cause. PASS source architecture **không** kéo theo PASS measurement validity hay causal identification.

## 5. Ten-study evidence matrix

| Study | Source result verified | Historical use | Hypothesis use | Root-cause use |
|---|---|---|---|---|
| T4 VAL | NLL 3.5223388517 vs bigram 3.99723141696; ~11.88%; 1 seed | YES | Learned next-token distribution | NO |
| T4 TEST64 | 64 stories, 14,669 targets; NLL 3.48359107334 vs 3.97360374532; consumed | YES | Corroborates token-distribution result | NO |
| FRESH12 | adherence mean 0.291667 each arm; candidate gates 4 PASS/4 FAIL | YES | No demonstrated semantic gain | NO |
| FRESH16 V2 | H1 0/16; H2 0/8; S1/S2 are different judging tasks | YES | Scoped failure under frozen protocol | NO |
| CF1 DEV36 | 0/36 context-driven preference switches | YES | Evidence against switching in exact DEV; evaluator position confound exists | NO |
| D1 EXP32 | greedy 0/32, nucleus 0/32 grade≥2; repetition improved; rater bytes unverified | QUALIFIED | Weakens decoder-only rescue | NO |
| A/C FINAL24 | absolute A=C=0.6667/3; C−A=0; 1/24 strict C win | YES | Falsifies tested C efficacy | NO |
| H-DATA-S1 | H0=H1=0 primary; one blind AI rater | YES | Falsifies tested H1 data intervention efficacy | NO |
| FC01 | A4/64, B3/64, C38/64; rule 16/16, entity-location 1/16 | EXPLORATORY | Refutes universal incapacity; narrow task/objective interaction | NO |
| D1 R1 | ontology/admission closure; 0/16 admitted TRAIN, 0/16 admitted OOD | DESIGN ONLY | Benchmark-design evidence | NO |

Không pool mẫu số hay metric giữa các study.

## 6. Causal hypothesis review

| Hypothesis | Q3 verdict | Reason |
|---|---|---|
| `H-METRIC` | `NOT_IDENTIFIABLE_FROM_EXISTING_EVIDENCE` | Measurement-risk signals exist, but no proof the actual AI rater is globally wrong. |
| `H-OBJECTIVE` | `NOT_IDENTIFIABLE_FROM_EXISTING_EVIDENCE` | A/C negative and FC01 narrow positive do not isolate next-token objective as root cause. |
| `H-DATA` | `NOT_IDENTIFIABLE_FROM_EXISTING_EVIDENCE` | Exposure reuse ≠ unique coverage; H-DATA negative and FC01 selective. |
| `H-DECODER` | `CONTRADICTED_AS_SOLE_EXPLANATION / HYPOTHESIZED_AS_MEDIATOR` | Nucleus improves repetition but factual grade remains 0/32. |
| `H-CONTEXT` | `NOT_TESTED` | No matched fact-distance/truncation control on context256. |
| `H-CAPACITY` | `NOT_TESTED` | No capacity-only controlled evidence. |
| `H-IMPL` | `NO_CONFIRMED_SOURCE_BUG · RUNTIME_PRIVATE_BYTES_NOT_REVERIFIED` | Public source/config consistent; runtime/private bytes not reopened. |

**Root cause identified:** `false`.

## 7. Admission gates AD-00…AD-08

| Gate | Q3 assessment | Timing / veto |
|---|---|---|
| AD-00 | Necessary; Q2 partial status is appropriate | Public exact sources verified; do not self-upgrade. |
| AD-01 | Necessary but over-bundled | Rights before data access/authoring; tokenizer identity before token-length freeze; checkpoint bytes before model execution. |
| AD-02 | Hard veto before authoring | Construct must be decidable prospectively. |
| AD-03 | **Hard veto before authoring/freeze, not merely before scoring** | Visible evidence must support gold before production benchmark is frozen. |
| AD-04 | Hard veto before scoring | Rater calibration may follow authoring, but gold specification is prospective. |
| AD-05 | Hard veto before authoring/freeze | Shortcut/leakage controls are design properties. |
| AD-06 | **Hard veto at design/freeze** | One-variable paired identifiability/equal information budget must be designed before production freeze. |
| AD-07 | Necessary before generation/scoring | Direction, ties, normalization and failure rule must be frozen. |
| AD-08 | Necessary governance sequence | Owner acceptance is not AD-08 PASS; Q4 remains owner-only. |

### Hidden gold / hidden state

Nếu gold chỉ tồn tại trong hidden `E_core` và không thể suy ra từ evidence model/rater được phép thấy, rater-based adherence metric phải `HOLD_MEASUREMENT`.

Hai phương án hợp lệ về nguyên tắc:
1. hidden annotation chỉ là derivation metadata của fact có thể chứng minh từ visible source; hoặc
2. dùng exact programmatic oracle với scoring contract riêng, trong đó oracle input, information budget và provenance được preregister; không gọi đó là rater-visible gold parity.

Không được dùng state mà model không nhận làm căn cứ kết luận model “sai fact”.

## 8. Minimum discriminating test — design-only

`Teacher-forced fact discrimination vs free generation` là **FEASIBLE_CONDITIONALLY**, nhưng **NOT_ADMISSION_READY**.

Có thể phân biệt:
- conditional preference đã có nhưng rollout/generation làm mất fact;
- conditional preference chưa có ngay dưới teacher forcing.

Không tự tách được objective vs data vs representation/capacity, và không tự chứng minh decoder là root cause.

Remaining confounds: gold validity, tokenizer-length asymmetry, lexical cues, candidate prior, prompt position, truncation, rater validity của secondary endpoint, motif reuse, checkpoint identity.

**Length normalization:** phải preregister. Nếu exact target-token counts bằng nhau, summed log-likelihood có thể so trực tiếp. Nếu khác, phải freeze normalization policy (ví dụ per-token mean NLL/log-prob) hoặc exact token-count matching trước khi xem outcome.

## 9. Literature verification — 13 works

| ID | Verified primary claim | TTM scope |
|---|---|---|
| P01 TinyStories | sub-10M models can be coherent on purpose-built simple data | refutes deterministic capacity-only claim |
| P02 Scaling Laws | cross-entropy depends on model/data/compute in studied regimes | plausibility only |
| P03 Chinchilla | compute-optimal balance of parameters/tokens in 70M–16B experiments | not a 3.75M threshold |
| P04 InstructGPT | instruction/human-feedback fine-tuning can improve intent following | objective/task plausibility only |
| P05 Holtzman | maximization-based decoding can degenerate; nucleus can improve open generation | supports decoder diagnostic |
| P06 Lost in the Middle | context position can affect use of long contexts | nuisance hypothesis only |
| P07 LLM-as-a-Judge | strong judges can align with humans but show position/verbosity/self-enhancement biases | supports calibration |
| P08 Not Fair Evaluators | response order can bias pairwise LLM evaluation | supports order balancing |
| P09 SummEval | multi-axis automatic/human evaluation with expert/crowd annotations | evaluator protocol analogy |
| P10 Emergent Mirage | discontinuous metrics can create apparent sharp emergence | supports continuous prospective metrics |
| P11 HANS | heuristic shortcuts can pass familiar data and fail controlled counterexamples | supports hard negatives |
| P12 CLUTRR | held-out rule combinations diagnose systematic relational generalization | benchmark-design analogy |
| P13 ProPara | entity state/location/existence tracking with explicit annotations | state-grounded gold analogy |

Không bài nào đo exact T4 checkpoint, 2048 TRAIN, context256 và same prompts/rater. External literature **không xác nhận root cause TTM**.

## 10. Findings

### Q3-F01 — HIGH — blocks Q3 PASS
`artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_20261115.json:L393-L407` đặt AD-03/AD-04/AD-06 trong `conditions_before_scoring`. Nhưng AD-03 và AD-06 là design/freeze properties; Q2 prose cũng yêu cầu evidence parity, matched tokenization/candidate length và source-visible gold trước fixture thực tế (`...ADMISSION_LOCK...:L63-L71,L75-L91`).

**Impact:** có thể author/freeze benchmark không identifiable rồi mới phát hiện sau.  
**Minimal amendment:** tách `BEFORE_DESIGN_OR_AUTHORING`, `BEFORE_FREEZE`, `BEFORE_SCORING`, `BEFORE_MODEL_EXECUTION`; chuyển AD-03 và design-identifiability của AD-06 lên trước authoring/freeze.

### Q3-F02 — HIGH — blocks Q3 PASS
`docs/governance/ACTIVE_RESEARCH_GATE.md:L13-L16,L55-L61` nói Q2 completed/owner accepted và Q3 authorized, nhưng `L45-L53` vẫn ghi `Q2_NOT_COMPLETED; Q3_NOT_REVIEWED` và đưa next-step cũ.

**Impact:** active governance state không đơn trị nếu merge.  
**Minimal amendment:** một sửa tích hợp trên cùng packet để loại status/next-step stale. Sau HOLD, canonical state phải phản ánh Q3 remediation, Q4 undecided, science HOLD.

### Q3-F03 — MEDIUM
AD-01 gộp source/data rights với private checkpoint-byte custody và áp full gate trước authoring.

**Impact:** over-veto/deadlock pure design.  
**Minimal amendment:** tách subconditions/timing; không hạ yêu cầu rights/custody.

### Q3-F04 — LOW
Literature triage line 65 gọi Holtzman là “Max-likelihood decoding”; chính xác hơn là “maximization-based decoding”.

**Impact:** terminology only; không đổi causal verdict.

## 11. Baseline disposition

- `KEEP_HISTORICAL_REFERENCE_ONLY`: **AFFIRMED**.
- `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`: **AFFIRMED**.
- `ROOT_CAUSE_NOT_IDENTIFIED`: **AFFIRMED**.
- Architecture patch: **NOT JUSTIFIED**.
- New data/test/scorer: **NOT AUTHORIZED**.
- F0–F2: **PAUSED**.
- Q4: **NOT DECIDED**.

## 12. Final verdict và một bước tiếp theo duy nhất

**Overall:** `HOLD_Q3_REMEDIATION`.

**Bước thực hiện tiếp theo — duy nhất:**

`SM4M_Q001_Q3_INTEGRATED_GOVERNANCE_AND_ADMISSION_SEQUENCING_REMEDIATION_SINGLE_GATE`

Chỉ sửa **cùng governance packet PR #21** để:
- làm timing của AD-01/03/06 nhất quán với prose và causal identifiability;
- loại status/next-step stale trong `ACTIVE_RESEARCH_GATE.md`;
- sửa thuật ngữ Holtzman trong cùng amendment;
- freeze candidate HEAD mới rồi thực hiện **một** independent Q3 readback/re-review.

Không mở branch nghiên cứu mới, không tạo dataset/gold/scorer, không train/inference, không Q4 trước re-review, không merge PR #21 trong trạng thái HOLD.
