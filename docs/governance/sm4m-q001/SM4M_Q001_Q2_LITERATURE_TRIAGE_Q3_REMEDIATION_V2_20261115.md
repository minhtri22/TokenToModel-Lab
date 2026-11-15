# SM4M-Q001 — Tự QA đối kháng và đối chiếu văn liệu khoa học để khoanh vùng thất bại Small-4M

> **Q3 versioned correction (F04) · 2026-11-15 · author amendment only:** replaces one P05 decoding term with “Maximization-based decoding”; no revised scientific claim, paper interpretation, source reference, test, or acceptance gate. Original document remains immutable at Git blob `380582a4f1260dfda28d39e0cb56be2fc02709c5` in candidate `3c53d062c7c6ff4218d80177253dd1c061ac6362`. This v2 is a re-review candidate, not a revised original Q2 receipt or Q3 PASS.


**Operation:** `SM4M_Q001_AUTHOR_ADVERSARIAL_QA_AND_SCIENTIFIC_LITERATURE_CAUSAL_TRIAGE_SINGLE_GATE`  
**Ngày:** 15/11/2026 · **Tư cách:** tác giả tự QA (author adversarial review), không phải independent Q3  
**Repository:** `minhtri22/TokenToModel-Lab` · **main đã khóa:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`  
**Câu hỏi:** `SM4M-Q001` · [question gate nguồn chính](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/docs/governance/SM4M_Q001_BACK_TO_BASICS_ARCHITECTURE_DOC_CODE_EVIDENCE_20261115.md) · Git blob `27b8337aea9c9e82bfe98657170e592fcb3ad941`  
**Báo cáo được tự QA:** `SM4M_Q001_INTEGRATED_ARCHITECTURE_AUDIT_20261115.md` · SHA-256 nguyên tệp `4973ad744f5d2e2e9e89f46e7890a37833c43cd99fdb82405be2148a580bce06`  
**Receipt gốc:** `SM4M_Q001_AUDIT_RECEIPT_20261115.json` · SHA của báo cáo đã đối chiếu khớp.  
**Quy tắc:** không tạo nghiên cứu khác, không đọc private weights/data, không dùng TEST/FINAL sealed, không khởi chạy inference/train, không sửa mã hoặc các nguồn kết quả khoa học đã khóa, không append `lineage.md`, không merge. **Không mở nhánh; không sửa `lineage.md`; không sử dụng, không tái chạy TEST/FINAL đã niêm phong**. Đây là đối chiếu source/literature, không phải thực nghiệm mới. Loại trừ hoàn toàn EmbeddingGemma 2 và Vector Memory.

## I. Quyết định tự QA: sửa cách diễn giải, KHÔNG cấp GO kiến trúc

**Trạng thái mới đề nghị:** `PASS_AUTHOR_SOURCE_PIN_QA_SCOPED · Q2_CAUSAL_TRIAGE_COMPLETED · HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE · ROOT_CAUSE_NOT_IDENTIFIED · Q3_NOT_EXECUTED · Q4_NOT_DECIDED`.

- **KEEP_REFERENCE_ONLY:** giữ nguyên checkpoint T4 step1024 và đường source pinned làm **đối chứng lịch sử bất biến**, không tạo hoặc sửa checkpoint.
- **HOLD_BASELINE_ADMISSION:** không nói rằng T4 đã “đủ vững” cho phép thử factual mới chỉ vì source và VAL NLL đã qua QA; construct/gold, rater, task condition, public/private provenance và khả năng phân biệt giả thuyết cần xác minh riêng khi được owner cho phép.
- **NO_ARCHITECTURE_PATCH:** nguồn hiện kiểm tra không xác lập lỗi causality/attention/FFN/loss/tie/architecture đủ căn cứ vá. Đây là **không tìm thấy lỗi qua kiểm tra tĩnh**, không phải chứng nhận code hoàn hảo.
- **NO_CAUSAL_ROOT:** bài báo trên những mô hình và benchmark khác chỉ xác minh **cơ chế có thể xảy ra**, không xác minh nguyên nhân thực tế của TTM-Small-4M. Không chấm số xác suất chủ quan thành bằng chứng.

**Điều chỉnh đối với Q2 gốc, bắt buộc ghi để không tái sử dụng kết luận quá rộng:**

| Mã | Kết luận ban đầu / thiếu sót | Tự QA và hiệu chỉnh | Mức |
|---|---|---|---|
| `AQ-01` | `KEEP_BASELINE_FOR_F0_F2_REVIEW` dễ bị hiểu là baseline đã admitted cho phép thử mới | Tách `KEEP_REFERENCE_ONLY` khỏi `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`; owner Q4 chưa ban hành | HIGH |
| `AQ-02` | “5 Whys” trình bày năm lời giải không cùng chuỗi nhân quả nối tiếp | Chuyển thành **causal hypothesis / fault tree**. 5 Whys chỉ dùng đặt câu hỏi sau khi đã có một failure mode đo được; không suy root cause từ đủ năm câu | HIGH |
| `AQ-03` | 38/38 source assertion QA dễ bị hiểu là đã QA mọi failure mode | 38/38 chỉ là kiểm mã nguồn/cấu hình, không kiểm source-run equivalence, private checkpoint, gold/rater, dataset domain shift hoặc đánh giá nhân quả | HIGH |
| `AQ-04` | Nhãn FMEA HIGH/MEDIUM/LOW nhưng chưa chấm occurrence/detection | Gọi đúng là **risk triage theo mức ảnh hưởng**, không gọi là FMEA định lượng. Không gán RPN giả định | MEDIUM |
| `AQ-05` | Chưa có đối chiếu bài báo nào | Thêm literature map có URL nguyên bản, phạm vi kết quả, tương đồng/khác với T4 và điều kiện bác bỏ | HIGH |
| `AQ-06` | Thiếu ranh giới between `0/32`, `0/16`, `0/36`, và NLL | Khóa nghiên cứu, task, checkpoint, denominator, rater role và không pool. D1 EXP32 ghi nguyên byte input rater **NOT_VERIFIED** | HIGH |
| `AQ-07` | Phần negative control/phép chẩn đoán đề xuất có thể thành micro-permit | Chỉ đóng băng **thứ tự thiết kế**, không tạo dữ liệu/fixture/score; mọi phân biệt mới phải sau Q3/Q4 và một owner-authorized packet riêng | MEDIUM |
| `AQ-08` | Thiếu giới hạn ngoại suy từ lý thuyết scaling, long-context và LLM-judge | Nghiêm cấm suy các phát hiện trên mô hình lớn thành root cause của 3.75M T4; thiếu matched evidence => `NOT_IDENTIFIED` | HIGH |

**Kết luận QA:** Q2 trước đó **không phải FAIL kỹ thuật toàn phần**; hai khẳng định nguồn đúng quan trọng vẫn giữ: (1) cấu hình thực T4 không phải mặc định P02; (2) source trainer T4 gọi `model(xx)` và tính loss riêng, bỏ padding `-100`. Nhưng suy luận kiến trúc phải bảo thủ hơn: `SOURCE_MATCHED_PARTIAL` **khác** `BASELINE_SCIENCE_ADMISSION_PASS`.

## II. Nguồn địa phương và sự kiện khoa học đã được khóa — không thêm phép đo

| Tầng / bằng chứng | Chứng cứ đã quan sát | Không được suy ra |
|---|---|---|
| **Architecture** | P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; T4 config `c9a6f256ba975228683ee7de2a1090e649110e97` — 2.048 vocab, context256, emb256, 4 layers, 4 heads, **3.749.376 tham số** | Năng lực actor/object/goal được bảo đảm bởi 4×4 attention |
| **Tokenization & data** | T1 split source blob `3ef500ddd8259153e7e3d4602915a51b7060a40f`; BPE `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`: tokenizer fit 768 TRAIN; model sử dụng 2.048 TRAIN; pack `cdce219f2a2df27e25579f069238d4327c1d7d91` | Dữ liệu có đầy đủ quan hệ hành động, thông tin phản thực hoặc chuyển trạng thái |
| **Optimization** | A2 real trainer blob `76c4d0155cd0736919f41682f240b47ad3d7c428`; 1.024 optimizer steps × 4.096 valid targets = **4.194.304 target exposures**; receipt lịch sử 498.287 vị trí target duy nhất, reuse≈8,417 | Có 4.194.304 mẫu thông tin độc lập; token/parameter ratio tương đương các công trình scaling khác |
| **VAL H1** | Evaluator source `bef006bdff173fba6d8ba4aa0ef687a1732fd7c4`; model NLL 3,5223388517 vs TRAIN bigram 3,99723141696, cải thiện ~11,8805%; science `PASS_H1_CONFIRMATORY_VAL_SCOPE` | Bám prompt, theo dõi entity, reasoning hay truthfulness đã đạt |
| **TEST64** | `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED`, 64 stories /14.669 targets, đã tiêu thụ | Được phép chạy/chấm lại, đổi cutoff hoặc chọn mô hình từ TEST |
| **FRESH12** | `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED`, adherence delta 0, 35/48 grade0; one AI-rater / pilot candidate gates | Tương đương science confirmatory của mọi task |
| **FRESH16 V2** | `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED`, H1 adherence≥2 **0/16**, H2 matched counterfactual **0/8**; S1 chấm output, S2 chấm pair, **không** phải hai rater làm cùng việc | “Inter-rater agreement=0” hoặc xác định lỗi attention |
| **CF1 DEV36** | `FAIL_SCOPED_0_OF_36`, completion preference không đảo theo A/B trên exact DEV | Không thể làm fact-switch trên mọi prompt mới, hoặc phép đo FINAL72 được mở |
| **D1 EXP32** | Greedy/nucleus đều **0/32** grade≥2, nucleus thay đổi repetition; `RATER_INPUT_BYTE_PROVENANCE_NOT_VERIFIED` | Chứng minh mọi decoder tương đương hoặc absolute scores chắc chắn hợp lệ ở mức raw byte |
| **A/C FINAL24** | Primary candidate C-A=0, C strict 1/24; **absolute adherence trung bình 0,6667/3** | Absolute score=0, hoặc training objective vô tác dụng trên mọi nhiệm vụ |
| **H-DATA-S1** | Mean primary H0=H1=0 trong 24 pairs, một AI-rater, scoped exploratory; 7 PASS /4 FAIL gates | Dataset modification luôn vô hiệu hoặc human-gold confirmatory |
| **FC01** | A4/64, B3/64, C38/64 **lexical-family exploratory**, `entity_location` C1/16, `rule_constraint` C16/16 | OOD transfer hoặc reasoning tổng quát: chỉ có tín hiệu phụ thuộc template/stratum |
| **D1 R1** | `GO_CLOSE_R1_FORMULATION_DESIGN_ONLY`, OOD admissible 0/16, `D1_BRIDGE_SCIENCE=HOLD` | Một benchmark construct/gold đã hợp lệ để thử mô hình |

**Exact historical review refs:** main `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`; FRESH12 `72cbf73c3adb78f9d4111f702de71fa10f713533`; FRESH16 & D1 EXP32 `0ec28d44587fde9ad4acba8cccae65648e367181`; CF1 `d725c39094a5a584fd76386145db21ca6dc5eaf6`; A/C `37165ce6eea0bb4b04d316e2998da579c91d13cf`; H-DATA `ef4cc05037f98129082cd429a75092b8cc822efb`; FC01 `b5dd5890b73a29744530ed3a1ffbc0dc7ae5195a`; prior Foundation F0/F1 `9b55596f580b36b436cf6bdb2ed5a4e45c6992de`. **Git blob SHA-1 khác SHA-256 của tệp.** Source GitHub public không cho phép xác minh byte weights/data private trong Q001.

## III. Đối chiếu bài báo khoa học — cơ chế ngoại sinh, KHÔNG xác định nguyên nhân nội sinh

Tất cả nguồn sau là **bài nghiên cứu bên ngoài**, không phải receipt Q001. Mỗi trường có ba phần bắt buộc: kết luận được bài báo hỗ trợ; mức chuyển giao sang T4; dự đoán cần phân biệt.

| ID / nghiên cứu gốc | Kết luận được nguồn hỗ trợ | Liên hệ Small-4M và giới hạn ngoại suy | Dự đoán phân biệt cho nghiên cứu mới (CHƯA CHẠY) |
|---|---|---|---|
| **P01** Eldan & Li, 2023, [*TinyStories: How Small Can Language Models Be and Still Speak Coherent English?*](https://arxiv.org/abs/2305.07759) | Các LM dưới 10M tham số có thể sinh truyện mạch lạc khi được huấn luyện trên miền đơn giản và dữ liệu được thiết kế phù hợp | **Phản biện** kết luận “3,75M chắc chắn không thể”; không chứng minh T4 với 2.048 truyện học đủ fact adherence. TinyStories corpus/recipe của bài khác T4 | Cùng capacity, dữ liệu/coverage đúng construct và scoring hợp lệ có tạo gain không? Không thay capacity trước khi phân biệt |
| **P02** Kaplan et al., 2020, [*Scaling Laws for Neural Language Models*](https://arxiv.org/abs/2001.08361) | LM cross-entropy phụ thuộc kích thước model, lượng dữ liệu, compute, và overfitting | Hỗ trợ việc xem xét sample diversity/reuse; **không** có scaling law riêng chứng minh 4M thất bại prompt adherence | Trước thử scaling, kiểm train/val gaps, tính độc lập của target, task coverage |
| **P03** Hoffmann et al., 2022, [*Training Compute-Optimal Large Language Models*](https://arxiv.org/abs/2203.15556) | Compute-optimality phụ thuộc cân bằng số tham số và training tokens trong miền thực nghiệm mô hình lớn | Không áp `~20 tokens/param` hoặc công thức từ 70M–16B trực tiếp làm tiêu chí PASS/FAIL T4 3,75M/0,5M targets unique | Cần phép kiểm phụ thuộc data-vs-capacity **tách biến**, không tính 4,19M exposures thành unique tokens |
| **P04** Ouyang et al., 2022, [*Training language models to follow instructions with human feedback*](https://proceedings.neurips.cc/paper_files/paper/2022/hash/b1efde53be364a73914f58805a001731-Abstract.html) | Instruction training/human feedback có thể cải thiện user-intent adherence so với LM nền | Mạnh cho **objective/task alignment là cơ chế khả dĩ**. Không cho phép suy TTM cần RLHF hoặc objective là root cause; mô hình/corpus rất khác | Gold và cùng prompt/response: teacher-forced conditional margins vs free generation; sau đó mới cân nhắc objective |
| **P05** Holtzman et al., 2020, [*The Curious Case of Neural Text Degeneration*](https://mlanthology.org/iclr/2020/holtzman2020iclr-curious/) | Maximization-based decoding có thể dẫn đến lặp/degeneration; nucleus sampling cải thiện chất lượng sinh mở | D1 EXP32 của TTM ghi nucleus cải thiện repetition nhưng **không** cứu grade≥2. Văn liệu ủng hộ kiểm decoding, nhưng scoped local evidence chống giả thuyết **decoder-only rescue** | Nếu teacher-forced conditional discrimination tốt nhưng rollout fail, decoder có thể là trung gian. Nếu cả hai fail thì không đổ lỗi chỉ cho decoder |
| **P06** Liu et al., 2024, [*Lost in the Middle: How Language Models Use Long Contexts*](https://aclanthology.org/2024.tacl-1.9/) | Nhiều LM lớn phụ thuộc vị trí thông tin trong ngữ cảnh dài | Gợi ý “position/distance” là nuisance. **Không** suy kết quả trên long-context LLM sang T4 context256; trước tiên xác minh fact nằm trong cửa sổ T4 | Same fact/prefix tại vị trí gần/xa, giữ toàn bộ trong context256 để phân biệt utilization vs outright truncation |
| **P07** Zheng et al., 2023, [*Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*](https://arxiv.org/abs/2306.05685) | LLM-judge có thể tương quan human preferences nhưng chịu position/verbosity/self-enhancement bias | Không chứng minh AI-rater của TTM sai; chỉ chứng minh không thể mặc định ground truth từ một AI-rater | Benchmark source-visible ground truth + blind item-level sensitivity/specificity, provenance, same-task inter-rater agreement |
| **P08** Wang et al., 2024, [*Large Language Models are not Fair Evaluators*](https://aclanthology.org/2024.acl-long.511/) | Positional bias trong so sánh hai response có thể đảo thứ hạng evaluator | Đặc biệt liên quan pairwise A/C, H-DATA; nhưng chưa chứng minh lỗi rater của nghiên cứu cụ thể | Trước triển khai, prereg cân bằng thứ tự hiển thị trong cùng gold và rater task; không đổi score đã niêm phong |
| **P09** Fabbri et al., 2021, [*SummEval: Re-evaluating Summarization Evaluation*](https://aclanthology.org/2021.tacl-1.24/) | Expert/crowd judgments khác nhau; multi-axis chất lượng khó tách nếu người chấm không hiểu rubrics như nhau | Nhiệm vụ tóm tắt khác Small4M, nhưng hỗ trợ cần calibration theo từng axis và human evidence | Kiểm khả năng rater phân biệt consistency vs fluency, actor/object/goal; có UNKNOWN hợp lệ và không dùng score mơ hồ |
| **P10** Schaeffer et al., 2023, [*Are Emergent Abilities of Large Language Models a Mirage?*](https://papers.neurips.cc/paper_files/paper/2023/hash/adc98a266f45005c403b8311ca7e8bd7-Abstract-Conference.html) | Thang đo phi tuyến/discontinuous có thể làm xuất hiện bước nhảy giả trong performance | `0/32` hay `0/16` theo cutoff không đồng nghĩa mô hình không có tín hiệu liên tục; không tự thay đổi endpoint cũ | **Prospective** theo dõi continuous fact-switch margin và binary threshold song song; không rescoring TEST/FINAL |
| **P11** McCoy et al., 2019, [*Right for the Wrong Reasons: Diagnosing Syntactic Heuristics in NLI*](https://aclanthology.org/P19-1334/) | Heuristics lexical overlap có thể thành công trên benchmark quen thuộc nhưng fail dưới đối chứng có chủ đích | Mạnh để diễn giải FC01 C38/64 nhưng entity-location1/16; **không** chứng minh C thật dùng shortcut trong TTM | Paired hard negative đổi quan hệ fact giữ lexical/budget; hold-out theo template/causal motif; kiểm tương phản independent |
| **P12** Sinha et al., 2019, [*CLUTRR: A Diagnostic Benchmark for Inductive Reasoning from Text*](https://aclanthology.org/D19-1458/) | Có thể thiết kế kiểm tra suy luận quan hệ bằng tổ hợp quy tắc giữ lại và nhiễu kiểm soát | Gợi ý thiết kế actor/object/goal/relationship benchmark với held-out rule composition; không phải bằng chứng TinyStories T4 reasoning | Chỉ chọn feasible semantic contrasts và witness-proven gold; nếu construct thay nhau phụ thuộc thì không ép 2³ |
| **P13** Dalvi et al., 2018, [*Tracking State Changes in Procedural Text*](https://aclanthology.org/N18-1144/) | Theo dõi trạng thái entity/location và thay đổi qua đoạn văn là nhiệm vụ có annotation fact trạng thái, khó do quan hệ nhân quả ngầm | Hỗ trợ đo state transitions có căn cứ nguồn, khác TinyStories và không là benchmark được admission hiện tại | Mỗi item cần initial state/event/final state + proof source-visible; so object-location với control và UNKNOWN |

**Phân loại tổng hợp:** P01 phản biện capacity-only; P02–P03 hỗ trợ data/compute là yếu tố có thể tác động nhưng không cấp tiêu chí numeric; P04 objective/task; P05–P06 decoder/context; P07–P10 tính hợp lệ evaluation; P11–P13 benchmark/shortcut/state. **Không có bài báo nào vừa đo đúng checkpoint T4, đúng 2.048 TRAIN, đúng 256 context và cùng các prompt/rater của Q001** ⇒ `EXTERNAL_CAUSAL_VERIFICATION=NOT_ESTABLISHED`.

## IV. Cây giả thuyết nhân quả (Cause/Fault Tree), không phải năm câu WHY kết luận nguyên nhân

**Quan sát cần giải thích:** cùng một baseline T4 có VAL next-token NLL tốt hơn bigram **và** xuất hiện nhiều kết quả fact continuation/fact-switch âm tính (khác task), trong khi FC01 có kết quả dương hẹp theo lexical templates.

| Giả thuyết nguyên nhân | Dữ kiện TTM thực sự hỗ trợ | Văn liệu ngoài gợi ý cơ chế | Thông tin phản chứng còn thiếu | Độ chắc nguyên nhân TTM |
|---|---|---|---|---|
| `H-METRIC`: gold/rater/construct khiến độ bám dữ kiện bị đo thiếu/không cùng mục đích | D1 EXP32 rater input bytes NOT_VERIFIED, FRESH16 roles khác, H-DATA one judge, D1 R1 OOD admitted0 | P07–P10, P12–P13 | Cùng visible prompt+continuation, blind independent gold, calibrator kiểm true-0/true-1/UNKNOWN; không thay score cũ | **UNRESOLVED · PRIORITY 1** |
| `H-OBJECTIVE`: MLE không đủ để duy trì điều kiện actor/object/goal | VAL NLL PASS nhưng FRESH16/CF1 FAIL; FC01 C narrow positive, A/C no gain | P04, P11 | Same-baseline same-case **teacher-forced paired conditional margin** và controls; sau đó mới matched-budget objective study | **UNRESOLVED · PRIORITY 2** |
| `H-DATA`: 2.048 story TRAIN/768 BPE-fit quá hẹp hoặc distribution không chứa target logic | 498.287 unique targets reused ~8,417; H-DATA-S1 negative, FC01 selective | P01–P03, P11 | Corpus construct coverage, near-duplicates, entity/state patterns; matched data-only comparison | **UNRESOLVED · PRIORITY 2** |
| `H-DECODER`: generation method làm hỏng lời đáp dù model có latent fact preference | D1 nucleus giảm lặp nhưng vẫn 0/32 adherence grade≥2 | P05 | Teacher-forced fact preference pass nhưng free generation fail, with same case and visible gold | **WEAKENED AS SOLE EXPLANATION · PRIORITY 3** |
| `H-CONTEXT`: 256 window, reset positions hoặc use-of-position hạn chế fact | T4 source context256, segmentation; chưa có fact-distance contrast | P06 | Prompt lengths, fact span/source visibility; near vs far **within** 256 và truncation separable | **UNRESOLVED · PRIORITY 3** |
| `H-CAPACITY`: 3,75M params thiếu biểu diễn | Không có capacity-only controlled study; FRESH16 negative nhưng FC01 positive theo template | P01 phản biện tất định; P02–P03 scaling phụ thuộc điều kiện | Sau khi metric valid + objective/data diagnosis, same data/objective compare capacity under equal information and compute | **NOT ISOLATED · PRIORITY 4** |
| `H-IMPL`: logic training/attention/decoder/source bug | 38 source checks matched; thực tế checkpoint/private bytes chưa reverified | Không có paper riêng chứng minh lỗi TTM | Chỉ khi xuất hiện mismatch source/custody/runtime mới xác định & lập sửa; tránh rerun TEST | **NO CONFIRMED BUG · CONTINGENT** |

**Quy tắc không suy diễn:** `PRIORITY` là thứ tự **thu thập chứng cứ / tránh lãng phí**, không phải xếp hạng xác suất Bayes. Một hypothesis không được nâng thành `CONFIRMED_CAUSE` trừ khi có can thiệp đối chứng hoặc bằng chứng trực tiếp cô lập cơ chế trên **chính Small-4M**. Một negative result của một study không “bác bỏ” các giả thuyết ở study khác nếu khác base/task/denominator.

## V. Tối ưu chẩn đoán: chưa chạy và chưa vá, chỉ prereg thứ tự quyết định

**Gate 0 — Source/measurement provenance từ hồ sơ đã tồn tại (read-only, được làm trong Q001):** xác minh exact frozen model/config/tokenizer provenance, task/prompt/continuation visible evidence, rater role và outcome. Gán `ADMISSIBLE_FOR_CAUSAL_INTERPRETATION` hoặc `HOLD` **cho mỗi claim**, không sửa verdict gốc. Nếu thiếu byte/prompt/gold mà không thể read-only chứng minh, ghi rõ `NOT_VERIFIED`, dừng đường chẩn đoán đó.

**Gate 1 — Kiểm định tính hợp lệ của phép đo (CHỈ THIẾT KẾ, chưa thực hiện):** một bộ **đối chứng tối thiểu** có rater-visible source, gold xác định 0/1/UNKNOWN, negative controls tránh lexical/global-valence, blind rater độc lập chấm **cùng nhiệm vụ**. Chỉ chọn test sẽ phân biệt `rater cannot distinguish` vs `model fails`; không tự mở M0/M0X/M0U 216 items, không tạo gold/dataset trong Q001. Nếu không chứng minh được gold từ visible evidence => **hard veto** mọi score-based causal claim.

**Gate 2 — Phân biệt model preference và generation (CHỈ ĐỀ XUẤT cho tương lai):** sau owner Q4 + authorization riêng, dùng **fresh task**, cùng source/checkpoint/prompt/info budget, so sánh teacher-forced log-probability margin của hai continuation chỉ khác một fact (matched length/lexical cues) với generation-based factual outcome. Không tái chạy FINALS. `margin correct + generation fail` ưu tiên decoder/rollout; `margin incorrect + valid gold` ưu tiên objective/data/representation; **không** xác nhận ngay root cause chỉ bằng một tương quan.

**Gate 3 — Can thiệp tối thiểu khi có bằng chứng (CHƯA MỞ):** nếu đo hợp lệ, quyết định xem data-only, objective-only, context-position hay capacity ablation có **dự đoán tách biệt**. Chỉ cho phép một can thiệp trong một nhánh sau câu hỏi mới đã Q4-closed. Khóa sample unit/seed/data rights/matched budget/negative controls để không biến một thất bại thành chuỗi sửa vô hạn.

**Các lựa chọn bị bác bỏ tại Q001:** không tăng layer/head/embedding vì “4M quá nhỏ”; không thêm RoPE/MoE vì attention “đáng nghi”; không dùng chung metric FC01/A-C/H-DATA vì đều “adherence”; không dùng `0/32` để chứng minh không có tín hiệu xác suất; không làm 2³ full factorial chỉ vì dễ tạo schema; không dùng một rater AI không có gold làm chân lý tuyệt đối.

## VI. 5W1H/ FMEA / SWOT / MCDA — áp dụng đúng điểm ra quyết định

- **5W1H** đã sử dụng để đối chiếu WHY/WHAT/HOW của BPE–data–Transformer–trainer–checkpoint–evaluator. `WHO`=owner/custodian/reviewer, `WHERE`=exact blob/ref, `WHEN`=step1024/dated receipts. Còn thiếu private data rights/Q4 admission ⇒ không đánh PASS.
- **FMEA định tính:** chỉ risk/failure-mode triage, chưa có occurrence/detectability thực đo ⇒ không có RPN hay risk score giả. High vì có thể làm vô nghĩa phép thử; không kết luận high probability model bug.
- **5 Whys:** không giả tạo chuỗi 5 tầng. Dừng sau “vì sao NLL≠factual endpoint” (OBSERVED). Các nhánh sau đưa vào causal hypothesis tree §IV (HYPOTHESIZED), xác định điều kiện bác bỏ ở §V.
- **SWOT/MCDA:** chỉ có ích khi có ít nhất hai candidate có construct/gold/rights hợp lệ và matched budget, khác biệt đo được; hiện chưa đủ admission, **không chọn phương án kiến trúc nhờ điểm số**.

## VII. Quy tắc QA trước khi giao agent khác

**Tác giả phải tự kiểm bằng chứng, không chỉ đếm dòng:**

1. Đối chiếu exact report gốc và receipt hash; 38/38 cũ chỉ là source assertions và có giới hạn đã ghi, không tự nâng thành science QA.
2. Kiểm số liệu NLL improvement, model param và exposure reuse bằng phép tính độc lập; không lặp 4,19M là independent samples.
3. Từng nghiên cứu phải có scoped outcome và ref; đặc biệt D1 EXP32 input bytes `NOT_VERIFIED`, FRESH16 S1/S2 khác nhiệm vụ, A/C absolute>0 trong khi delta=0, H-DATA absolute0, FC01 38/64 theo template không phải OOD.
4. Từng bài báo phải có URL nguyên bản, năm và đúng cơ chế; ngoại suy được mô tả là `SUPPORTS_PLAUSIBILITY_ONLY`, không `CONFIRMED_SMALL4M_CAUSE`.
5. Không chứng nhận baseline mới, Q3, Q4, merge, lineage, source private rights, runtime hoặc science khi chưa có bằng chứng.
6. Tất cả dự đoán tương lai là **thiết kế chưa thực hiện**, không biến thành permit, không tạo branch và không áp metric mới lên sealed data.

**Author verdict:** `PASS_AUTHOR_ADVERSARIAL_QA_AND_LITERATURE_TRIAGE_SCOPED_ONLY; HOLD_NEW_SCIENCE_BASELINE_ADMISSION; CAUSAL_ROOT_CAUSE=NOT_IDENTIFIED`.

**Q1:** đã đăng ký trên main. **Q2:** đã bổ sung tự QA và literature triage trong hồ sơ local, **chưa** là Q3. **Q3:** NOT_EXECUTED, **không bàn giao ở lượt này**. **Q4:** NOT_DECIDED. **F0–F2:** PAUSED. **lineage.md:** UNCHANGED. **Implementation/merge:** NOT_AUTHORIZED.

**Bước thực hiện tiếp theo — duy nhất:** đóng gói và khóa **bản Q2 đã tự QA** (báo cáo + receipt + literature matrix) với trạng thái `HOLD_BASELINE_ADMISSION`; chỉ xem xét independent Q3 sau khi các self-QA findings đều có bằng chứng và owner quyết định chuyển gate, tuyệt đối không mở experiment/vá kiến trúc trước.
