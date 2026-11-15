# SM4M-Q001 — Back to Basics: Kiểm toán nền tảng Small-4M trước F0–F2

**Question ID:** `SM4M-Q001`  
**Operation:** `SM4M_Q001_ARCHITECTURE_DOC_SOURCE_EVIDENCE_TRACEABILITY_SINGLE_GATE`  
**Chính sách:** `TTM-GOV-QF-20261115-V1` (đã khóa trên `main` commit `80b1cd260dcec38ec4a9b66f6ff387931de638e6`).  
**Đề nghị owner:** 15/11/2026, back-to-basics architecture-first, không mở F0–F2 trước khi Q001 có đáp án và Q4 owner closure.  
**Trạng thái ngay khi đăng ký:** `Q1_QUESTION_REGISTERED · Q2_NOT_COMPLETED · Q3_NOT_REVIEWED · Q4_OWNER_NOT_DECIDED · NO_BRANCH · NO_SCIENCE`.  
**Đối tượng:** Chỉ TTM-Small-4M T4 baseline/checkpoint bước 1024 và **các nhánh khoa học Small-4M liên quan trực tiếp**. Hai chương trình **EmbeddingGemma 2** và **Vector Memory** nằm ngoài phạm vi; không dùng kết quả của hai chương trình này để quyết định Q001.

## 1. Một câu hỏi phải trả lời

**Kiến trúc và implementation thực tế tạo ra checkpoint TTM-Small-4M T4 step1024 (tokenizer → data → Transformer → training → checkpoint → generation → evaluation) có khớp với tài liệu và bằng chứng khoa học được khóa, có đủ tính đúng và tính hợp lệ làm baseline cho phân tích NLL–factual/prompt adherence F0–F2 hay không? Nếu có điểm không phù hợp, nguyên nhân/giả thuyết nào đã có bằng chứng, và phải giữ, sửa tối thiểu, thay hướng hay dừng trước khi tiếp tục?**

**Đáp án quyết định được:** `KEEP_BASELINE_FOR_F0_F2_REVIEW`, `HOLD_BASELINE_SOURCE_OR_MEASUREMENT_INSUFFICIENT`, `SIMPLIFY_NEXT_DIAGNOSTIC`, `PIVOT_CONSTRUCT`, `STOP_CURRENT_PATH`. Đây là **quyết định thiết kế và source trust**, không phải science execution permit; chỉ Q4 owner closure mới cho phép kế hoạch F0–F2 kế nhiệm. Không đặt trước phương án thắng.

**Đơn vị quyết định:** hiện trạng source và từng giả thuyết; không dùng `QA_PASS` của một test để gán `SCIENTIFIC_PASS` cho toàn kiến trúc. `ROOT_CAUSE_IDENTIFIED=NO` cho đến khi có đối chứng nhận diện thực sự; kiểm toán này không tạo đối chứng mới.

## 2. Phạm vi mã và nguồn pinned (tài liệu khác implementation thật)

**Baseline main đã đọc:** `80b1cd260dcec38ec4a9b66f6ff387931de638e6`; policy commit cũng là baseline Q001. Reviewer phải re-read HEAD của `main` khi nhận handoff, giữ nguyên exact pin ở đây.

| Thành phần | Nguồn đã pin / Git blob SHA-1 | Trách nhiệm kiểm toán |
|---|---|---|
| Model architecture implementation | `src/p02/transformer_core.py` · `9762343e06cf800b50574c2871ae1ed58537fb18` | `P02Config`, `GPT`, weight tying, pre-LN, causal mask, FFN, forward/loss API |
| T4 real configuration | `tools/pilot_t4/integrated/t4_capacity_smoke.py` · `c9a6f256ba975228683ee7de2a1090e649110e97` | 2048/256/256/4/4, 3,749,376 parameters; **không dùng P02 defaults 2048/64/64/2/4 làm model trained** |
| T4 actual science trainer | `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py` · `76c4d0155cd0736919f41682f240b47ad3d7c428` | 1024 optimizer steps, seed 20261108, AdamW, mask `ignore_index=-100`, exact 4096 valid targets/step, AMP FP16, scheduler/checkpoint |
| T4 private data pack creation | `tools/pilot_t4/integrated/t4_data_pack.py` · `cdce219f2a2df27e25579f069238d4327c1d7d91` | Source split rights, TRAIN/VAL windowing, EOS, 256-token context, no TEST pack, story integrity |
| TRAIN-only BPE source | `tools/pilot_t1t3/source_t2/ttm_gpt2_bpe2048.py` · `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6` | Byte BPE 2048, EOS ID256, train-only fit, expected text/UTF-8 roundtrip |
| VAL metrics evaluator | `tools/pilot_t4/integrated/t4_eval.py` · `bef006bdff173fba6d8ba4aa0ef687a1732fd7c4` | Proper token masking/NLL, bigram TRAIN-only baseline, bootstrap resampling by stories |
| T4 initial prereg manifest | `tools/pilot_t4/integrated/T4_PREREG_INTEGRATED_CANDIDATE_20261108.json` · `3ab7a439f79594e02c7598b1e5dca7168b923bcc` | Historical candidate status, don't confuse prereg candidate `science_lock:HOLD` with separately authorized completed T4 one-shot |
| VAL independent science receipt | `evidence/pilot/t4-science/T4_A2_FINAL_INDEPENDENT_SCIENCE_ADJUDICATION.json` · `84cb94647c403ea358d8c991090bf56adc11f128` | `PASS_H1_CONFIRMATORY_VAL_SCOPE` only, no new checkpoint private byte rehash |
| Foundation architecture doc (prior author baseline) | Branch `research/ttm-small4m-foundation-first-single-gate-20261115` exact HEAD `9b55596f580b36b436cf6bdb2ed5a4e45c6992de`: `01_SMALL4M_ARCHITECTURE_COMPONENT_SPEC_20261115.md` Git blob `22e823b0a9069f07a6d6912b6425762528e2f655` | Check claims against original source, never elevate author doc to verified code |
| Foundation evidence matrix (prior author baseline) | Same branch HEAD, `02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md` Git blob `853411064bcdc58f5c6bad713b85237f2828182e` | Map hypotheses to original branch adjudications, preserve exact scope |
| Foundation scope-isolation source | Same branch HEAD, `04_SMALL4M_SCOPE_ISOLATION_DECISION_20261115.md` Git blob `4c3f3c000096dfe31d05e1fb2765e180276ddc76` | Explicitly exclude EmbeddingGemma 2 and Vector Memory |

**Private-source constraint:** T4 step1024 checkpoint SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` is **historical prior audit pin**, not byte-reverified in Q001. Raw data/weights/token IDs/TEST are not accessible to this source-only gate and must not be fabricated, published or re-run. TEST64 is consumed.

## 3. Preliminary mapping from Small-4M branch evidence to exact architecture layer

All entries are **preliminary source observations**, *not new source QA or validated root cause*. Independent reviewer must inspect original exact HEAD/file and reconcile same-task/sample/metric before signing.

| Known evidence (original scoped source) | Observed result | Mapping question at architecture/source level | Must NOT conclude |
|---|---|---|---|
| T4 VAL science (`main` evidence receipt `84cb...`) | Model VAL NLL `3.5223388517` vs TRAIN bigram `3.9972314170`; `PASS_H1_CONFIRMATORY_VAL_SCOPE` | Are T4 tokenizer, masked target accounting, effective train exposures and story-bootstrap baseline coherent and reproduced as source logic? | NLL PASS proves story fact fidelity |
| T4 consumed TEST64 (`main` `lineage.md` L0012) | Model NLL `3.48359107334` vs bigram `3.97360374532`; descriptive PASS | Confirm original source claim and one-shot boundaries; **do not rescore TEST** | TEST NLL validates generation adherence |
| T4 step1024→1280 and FRESH12: source branch `research/ttm-small4m-q1q2-quality-single-batch-20261109` snapshot HEAD `72cbf73c3adb78f9d4111f702de71fa10f713533`, FRESH12 adjudication Git blob `1862a39ed54cdc80c39213b615a3f7c4a4526d65` | VAL NLL step1280 reported lower (~3.498089 vs 3.522339), but FRESH12 candidate `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED`; 35/48 grade 0 and prereg gate 4 PASS/4 FAIL | Does extra training/serialization change semantic outcomes? Separate 1024/1280 and evaluator vs tokenizer/rendering effects | More steps improve reasoning or FRESH12 is broad confirmatory failure |
| FRESH16 V2: source branch `research/ttm-small4m-prompt-adherence-continuation-design-20261111` HEAD `0ec28d44587fde9ad4acba8cccae65648e367181`; adjudication blob `ae8ded5bb03a595f9af4f333ef96271ed3991d7d` | H1 adherence>=2 `0/16`; H2 paired counterfactual `0/8`, `FAIL_SCOPED` | Align checkpoint/decoding task/score rubric to source output; S1/S2 are **different rater roles**, not inter-rater agreement on same items | Attention or model size caused failure |
| CF1 DEV36: independent review source `d725c39094a5a584fd76386145db21ca6dc5eaf6`, blob `d6a094b2a9d0977728d5d2f13c7c945d7cb8ee96` | Preferred candidate switch `0/36`; scope DEV | Separate retrieval of fact context vs immutable candidate prior; possible position/prompt confounds | Universal failure of conditional inference |
| D1 EXP32 decoder comparison: source branch `research/ttm-small4m-prompt-adherence-continuation-design-20261111` HEAD `0ec28d44587fde9ad4acba8cccae65648e367181`, terminal review blob `f53da235027be331682bf1a5b86b0d1e94cd5373` | Greedy and nucleus each `0/32` grade≥2; nucleus showed secondary repetition advantage | Distinguish decoder-induced repetition from stable fact/prompt condition failure | Nucleus is sufficient or greedy alone is root cause |
| A/C FINAL24: source branch `research/ttm-small4m-post-final24-negative-archive-hypotheses-20261112` HEAD `37165ce6eea0bb4b04d316e2998da579c91d13cf`, adjudication blob `1af1b6d3743f5e986edcc3ef1e737b0f05188d3c` | Absolute A=C `0.6667/3`, C−A=0; C strict wins1/24; candidate efficacy FAIL | Contrast objective change against data/decoder/evaluator; must keep **absolute score distinct from delta** | A=C absolute 0 or all objectives fail |
| H-DATA-S1 FINAL24: branch `research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113` exact snapshot HEAD `ef4cc05037f98129082cd429a75092b8cc822efb`, adjudication blob `9cfb02e86c3893b2f927b1529c637bba797f40ae` | Primary 24 paired cases; 48 continuations primary actor/object/goal all score 0; H1−H0=0; no demonstrated benefit | Does apparent score floor arise in measurement, actual output, or conditional structure? Requires discriminating evidence, not rescoring | Evaluator broken, or only data insufficient |
| FC01 A/B/C source `b5dd5890b73a29744530ed3a1ffbc0dc7ae5195a`, adjudication blob `0a425cbadfaf644a117693fce1c9b80b069185a7` | A4/64, B3/64, C38/64 (lexical family), entity_location C1/16; exploratory PASS scoped | Objective/data can matter in restricted family, template/stratum heterogeneity needs controls | Broad reasoning/OOD gain or objective universally optimal |
| Q1/Q2 pending quality/performance: `tools/pilot_q1q2/frozen_inputs_20261109/README_VI.md` at main Git blob `fbda8296e4bed94a86f5aa84908c4ccd5095509b` and PR #13 Draft | Frozen protocol/run matrix is not completed science proof; partial/HOLD states per F1 | Separate model quality from backend/serving context-length performance | Q1/Q2 run matrix is a completed science result |
| D1 R1 source on `main`, blob `43fa3aed1a802dde05511cf76afba6737eb47aa3` | `GO_CLOSE_R1_FORMULATION_DESIGN_ONLY`, source constraint/admission HOLD | Test construct validity of gold and task-conditional labels before designing another benchmark | Any T4 failure caused by ontology or D1 validates F2 |
| F2 source/design latest `9b55596f580b36b436cf6bdb2ed5a4e45c6992de` | 82/82 author source QA only; two earlier independent HOLDs; third distinct review pending | Is extensive M0X schema needed to answer original Small4M question? **Review only after Q001 architecture gate closes** | Author 82/82 proves measurement or gold validity |

**Additional baseline-source boundary to inspect:** `P02Config` default vocab2048/context64/embedding64/2blocks/4heads is NOT T4; `src/p03/train_loop.py` synthetic training is NOT T4. `GPT.forward(tokens, targets)` performs its own default cross-entropy, whereas actual T4 trainer calls `model(xx)` without targets and computes **masked external loss** with `ignore_index=-100`. This is a potential **API misuse risk for other runners**, **not a demonstrated T4 science bug**. T4 windows reset effective position and prior context across 256-token segments; assess relevance only if task/word-distance actually uses this boundary.

## 4. Framework lựa chọn theo đúng vấn đề — không phải checklist

- **5W1H trước tiên**, áp dụng riêng cho BPE/source corpus, T4 GPT topology, token-window pack, objective/optimizer/checkpoint, decoding, evaluator. Output mỗi thành phần: `WHY` component, `WHAT` scientific requirement, `WHO` owns source and QA, `WHERE` exact files/HEAD, `WHEN` actually trained/used, `HOW` its implementation realizes intended function. Chỗ không xác định: `UNVERIFIED`.
- **Document-to-code traceability** là phương pháp lõi: requirement/docs claim → exact code class/function/line → config/receipt/checkpoint pin → branch outcome → limitation/mismatch. Ưu tiên giải quyết source mismatch trước nguyên nhân giả thuyết. Không viết thay mã khi chưa có Q4.
- **FMEA/risk-based implementation review** cho rủi ro default-vs-trained topology, masked loss/API mismatch, split/fit leakage, data reuse, context truncation, target accounting, checkpoint identity, decoding/rater confounds. Severity × detectability × evidence confidence; tránh tạo RPN giả định như là số đo.
- **5 Whys chỉ cho GAP đã xác minh**, ví dụ NLL PASS vs adherence FAIL. Mỗi WHY phải phân biệt `OBSERVED` / `HYPOTHESIZED` / `FALSIFIABLE_BY` / `NOT_TESTED`. Không kéo chuỗi vì-sao đến câu trả lời "capacity nhỏ" hoặc "attention hỏng" nếu chưa có chứng cứ.
- **SWOT và Pugh/MCDA có điều kiện:** dùng khi **đã xác định ≥2 kiến trúc hoặc đường chẩn đoán thật sự khả thi** sau audit. Khóa tiêu chí, trọng số/sensitivity và hard veto trước chấm; đừng mặc định phải xây bảng MCDA để chọn một baseline đã có. Phương án benchmark gold không thể suy từ visible evidence ⇒ hard veto.
- **Falsification:** phải nêu điều kiện nào xác nhận lỗi thuộc source/implementation, evaluator/construct, objective/data, decoding/context, hoặc bác bỏ giả thuyết. Không được lấy một kết quả scoped của study khác làm phép phân biệt nếu không same evidence budget.

## 5. Gói kiểm toán tối thiểu và điều kiện hoàn tất câu hỏi

Một reviewer đọc nguồn tài liệu và code thật **read-only**, tạo **một** báo cáo tích hợp và một receipt (chưa phải science data):

1. **Architecture Component Necessity & Implementation Matrix** — từng component kèm lý do tồn tại, các trục cấu hình T4 thật, exact paths/blob, mismatch, alternative tối giản chỉ nếu cần. Trạng thái `SOURCE_MATCHED` / `SOURCE_MISMATCH` / `NOT_VERIFIABLE_FROM_PUBLIC_SOURCE`.
2. **Small4M Branch-to-Failure Traceability Matrix** — tất cả nguồn Small4M liên quan trực tiếp từ bảng §3; thống nhất study/metric/denominator/model/decoding/rater/custody. Sai khác cần giữ nguyên thay vì pool. Outcome `SCIENTIFIC_PASS_SCOPED` / `SCIENTIFIC_FAIL_SCOPED` / `DESIGN_HOLD` theo **nguồn gốc**, không tự cấp verdict mới.
3. **Architecture Risk & Hypothesis Falsification** — chỉ căn cứ defect đã quan sát; ưu tiên chẩn đoán có thể làm thay đổi lựa chọn. Đề xuất *minimum next evidence* nhưng không thực hiện thí nghiệm/gold.
4. **One Answer & Disposition** — `KEEP` / `SIMPLIFY` / `PIVOT` / `STOP` / `HOLD_EVIDENCE_INSUFFICIENT`, cần có một câu trả lời cho Q001, mức chứng cứ và điều kiện thay đổi. Distinct reviewer đánh giá và owner ghi Q4 closure trước bất kỳ F0–F2 restart.

**Hard veto:** sai nguồn topology/checkpoint; không có audit được của metric chính; nguồn cần private bytes nhưng lại tuyên bố verified; source/rights chưa admitted; dùng TEST64 hoặc FINAL24 đã niêm phong để tái đánh giá; trộn AI rater độc lập với human gold; lấy technical QA thành science PASS.

**Stop rule:** nếu có hard veto không thể giải quyết trong chỉ-đọc, ghi `HOLD_BASELINE_SOURCE_OR_MEASUREMENT_INSUFFICIENT` với exact chứng cứ và dừng. Nếu không phân biệt được hypothesis bằng nguồn hiện có, ghi `HOLD_EVIDENCE_INSUFFICIENT`; không mở thực nghiệm mới để vá thiếu hụt. Chỉ khi Q4 có câu trả lời/owner closure mới được **thiết kế lại thứ tự F0–F2**; không tự mở F3/F4.

## 6. Exclusions and custody boundaries

**OUT OF SCOPE:** EmbeddingGemma 2, Vector Memory, TTM × SIX hay các model ngoài Small-4M; P07/P08/T5/T6 infra chỉ tham chiếu ở chỗ giúp loại trừ lỗi backend, không coi là science head của Small-4M. Không tải model, không GPU, không chạy inference/training/eval, không tạo gold, không mở checkpoint private, không chỉnh sửa source, không tạo nhánh mới, không merge, không sửa `lineage.md`.

**CURRENT:** `QUESTION_REGISTERED_ONLY · ARCHITECTURE_REVIEW_NOT_COMPLETED · OWNER_Q4_NOT_GRANTED · ROOT_CAUSE_IDENTIFIED=NO · F0_F2_REVIEW_PAUSED_PENDING_Q001 · SCIENCE_HOLD · NO_GPU · F3_F4_NOT_OPENED · MERGE_NOT_AUTHORIZED`.

**Bước thực hiện tiếp theo — duy nhất:** hoàn thành *một* báo cáo kiểm toán kiến trúc từ tài liệu đến mã, mapping Small4M branches, independent Q3 review và owner Q4 closure. **Không mở F0–F2 trong lượt Q001.**
