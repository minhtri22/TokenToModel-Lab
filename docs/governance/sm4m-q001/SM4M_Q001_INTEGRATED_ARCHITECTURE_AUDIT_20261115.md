# SM4M-Q001 — Kiểm toán tích hợp nền tảng Small-4M: tài liệu → source code → bằng chứng nghiên cứu

**Operation:** `SM4M_Q001_ARCHITECTURE_DOC_SOURCE_EVIDENCE_TRACEABILITY_SINGLE_GATE`  
**Ngày:** 15/11/2026 · **Tác giả:** Source/architecture audit (không phải independent reviewer)  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Exact main HEAD dùng để đối chiếu:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`  
**Question contract:** [`SM4M-Q001` trên main](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/docs/governance/SM4M_Q001_BACK_TO_BASICS_ARCHITECTURE_DOC_CODE_EVIDENCE_20261115.md) · Git blob `27b8337aea9c9e82bfe98657170e592fcb3ad941`  
**Owner governance:** [`TTM-GOV-QF-20261115-V1`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md) · Git blob `af1a879a2552f100c6669cb9ab6dc98c930d2e19`.

**Loại báo cáo:** `Q2_AUTHOR_ARCHITECTURE_AUDIT_COMPLETED_SOURCE_ONLY`, **không** phải `Q3_INDEPENDENT_PASS` hoặc `Q4_OWNER_DECISION`. Không dùng GPU, không tạo dữ liệu/gold, không chạy mô hình, không động tới TEST/FINAL đã tiêu thụ, không sửa mã, không mở nhánh, không sửa `lineage.md` hoặc merge.

## 1. Câu hỏi Q001 và trả lời có giới hạn

**Câu hỏi:** Kiến trúc và implementation thực sự tạo checkpoint T4 step1024 có nhất quán với thiết kế, đủ vững để làm baseline cho phân tích chênh lệch next-token NLL và factual/prompt adherence hay không; lỗi nào đã được xác lập, và có cơ sở đổi kiến trúc ngay không?

**Trả lời Q2 của tác giả:**

- **Có — trong phạm vi tham chiếu kỹ thuật đã ghim nguồn:** Decoder-only Transformer T4, cấu hình huấn luyện, tạo cửa sổ token, masked next-token loss, VAL NLL và cơ chế checkpoint có logic source phù hợp tài liệu. Không tìm được **bằng chứng trực tiếp về lỗi cấu trúc Transformer/T4 trainer** đủ để yêu cầu sửa code ngay. Đây là đánh giá mã tĩnh, không xác nhận lại toàn bộ runtime.
- **Không — nếu xem baseline này là phép đo đã chứng minh factual adherence hoặc cơ chế lỗi:** T4 đạt NLL tốt hơn bigram, nhưng đó không phải phép đánh giá cùng construct với các thí nghiệm fact-conditioned; các thang đo AI-rater, task và denominator giữa nhánh khác nhau. `ROOT_CAUSE_IDENTIFIED=NO`.
- **Khuyến nghị thiết kế duy nhất:** `KEEP_BASELINE_FOR_F0_F2_REVIEW` **chỉ với nghĩa giữ nguyên exact checkpoint/source làm đối chứng khoa học đã đóng**; **HOLD thực thi, thay kiến trúc, tái thiết kế F2 và mọi diễn giải nguyên nhân** cho đến khi Q3 independent review và Q4 owner closure. Khi Q4 cho phép xem xét F0–F2, ưu tiên phép đo tối thiểu phân biệt rõ lỗi evaluator/construct so với lỗi model thay vì mở full M0X schema ngay.
- Không có chứng cứ đủ để khẳng định `ATTENTION_CAUSED_FAIL`, `CAPACITY_TOO_LOW`, `DATA_ONLY_CAUSED_FAIL`, `NEXT_TOKEN_OBJECTIVE_IS_ROOT_CAUSE`, `DECODING_ONLY_CAUSED_FAIL` hoặc `AI_RATER_BROKEN`.

**Chất lượng kết luận:** `SOURCE_SUPPORTED_PARTIAL`; không có independent code review của lượt Q001 và không mở private checkpoint/corpus mới. Q2 không tự đóng Q001; trạng thái Q3/Q4 vẫn pending.

## 2. Kiến trúc thật: 5W1H + Document-to-Code Traceability

| Thành phần / WHY tồn tại | WHAT/HOW ở T4 thật, exact mã nguồn | Điều đã xác nhận / điểm chưa biết | Phán quyết Q2 |
|---|---|---|---|
| **Tokenizer —** đổi UTF-8 thành token ID có chi phí từ vựng giới hạn | Byte BPE 2.048 ID, EOS ID256; 1.791 merge; fit 768 TRAIN stories. [`ttm_gpt2_bpe2048.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/tools/pilot_t1t3/source_t2/ttm_gpt2_bpe2048.py) blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`; [`t1_source_split_tokenizer.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/tools/pilot_t4/integrated/t1_source_split_tokenizer.py) blob `3ef500ddd8259153e7e3d4602915a51b7060a40f`. | Source có kiểm TRAINVAL split, lựa chọn deterministic/hash và train-only tokenizer; bản private raw bytes/manifest không được tái đọc trong Q001. | `SOURCE_LOGIC_MATCHED · BYTE_NOT_REVERIFIED` |
| **Input embedding/position —** biểu diễn token và thứ tự | Learned token embedding `[2048,256]` và learned absolute positions `[256,256]`, cộng trực tiếp tại đầu vào. [`transformer_core.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/src/p02/transformer_core.py) blob `9762343e06cf800b50574c2871ae1ed58537fb18`. | Không phải RoPE/ALiBi. Khi tạo cửa sổ mới, position từ 0; chưa có so sánh kiểm soát riêng context-distance. | `SOURCE_MATCHED · CAUSAL_EFFECT_UNKNOWN` |
| **Causal self-attention —** cho token hiện tại dùng quá khứ, không dùng tương lai | QKV linear, 4 heads × 64 dimensions, triangular mask, scaled softmax, output projection. Nằm trong 4 pre-LN residual blocks. | Source có causal mask. Không có phép thử attention attribution hoặc khả năng truy xuất fact theo distance trên checkpoint thật. | `SOURCE_MATCHED · ATTENTION_ROOT_CAUSE_NOT_ESTABLISHED` |
| **FFN/GELU —** biến đổi theo vị trí sau attention | MLP `256→1024→256`, GELU; 2 LayerNorm và residual/block, tổng 4 blocks. | Đúng mô tả và chiều tensor; **không** có kết quả chứng minh FFN là bottleneck hay cần MoE. | `SOURCE_MATCHED · NO_OPTIMIZATION_JUSTIFICATION` |
| **Weight tying/output —** dự đoán phân phối token | `head.weight = tok.weight`; output logits `[B,T,2048]`, không có task-specific classification/contrastive head ở T4 gốc. | Hợp lý cho autoregressive LM; không đồng nghĩa mục tiêu giữ actor/object/goal đã được dạy. | `SOURCE_MATCHED · OBJECTIVE_TASK_GAP_POSSIBLE` |
| **Train/VAL/TEST —** kiểm soát leakage và phép đo | T1 chọn 2.048 TRAIN, 256 VAL, 64 TEST; BPE học 768 TRAIN. [`t4_data_pack.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/tools/pilot_t4/integrated/t4_data_pack.py) blob `cdce219f2a2df27e25579f069238d4327c1d7d91`: chỉ pack TRAIN/VAL, EOS, cửa sổ 256 token, nhãn -100 ở padding. | Mã nguồn bảo vệ split/hash và không xuất TEST pack; Q001 **không** xác minh lại toàn bộ dữ liệu riêng tư, near-duplicate hay quyền nguồn. | `SOURCE_LOGIC_MATCHED · PRIVATE_RIGHTS_BYTES_NOT_REVERIFIED` |
| **Optimization —** học next-token distribution | T4 **không phải** synthetic `src/p03/train_loop.py`. [`t4_train_science_a2.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py) blob `76c4d0155cd0736919f41682f240b47ad3d7c428`; AdamW peak LR 3e-4, weight decay 0.1, 32 warmup + cosine, FP16 option, clip1, seed 20261108, 1.024 steps ×4.096 labeled targets. | `GPT.forward()` mặc định có CE khi truyền targets, nhưng **runner T4 gọi model không targets** và tính masked external `ignore_index=-100`, `sum/4096`. Không có chứng cứ lỗi loss/step from static inspection. | `TRAIN_PATH_MATCHED · NO_NEW_RUNTIME_QA` |
| **Checkpoint/custody —** tính tiếp nối và bảo toàn model thật | State chứa model, optimizer/scheduler, sampler/RNG/scaler; checkpoint SHA readback và READY last. Prior T4 step1024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. | Source có fail-closed source/lock hashes. Checkpoint chỉ **được xác minh tại audit T4 lịch sử**; Q001 không tái mở weights. | `HISTORIC_VERIFIED · NOT_BYTE_REVERIFIED_Q001` |
| **VAL H1 —** nhận biết learned token distribution | [`t4_eval.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/tools/pilot_t4/integrated/t4_eval.py) blob `bef006bdff173fba6d8ba4aa0ef687a1732fd7c4`; NLL theo valid targets; bigram TRAIN-only; bootstrap theo 256 **story clusters**, không phải token independent. | Gate H1 ưu tiên lợi thế NLL so bigram ≥5% và CI lower >0; đây **không** là factual/gold score. | `EVAL_SOURCE_MATCHED · METRIC_SCOPE_NLL_ONLY` |

**Ranh giới cấu hình quyết định:** `P02Config` mặc định là vocab2048/context64/embedding64/2 layers/4 heads — mô hình CPU reference khác với T4 dùng `P02Config(**CONFIG)` vocab2048/context256/embedding256/4 layers/4 heads. T4 source tính đúng tổng **3.749.376 tham số duy nhất** (gồm weight tying, không đếm đôi output head). 1.024×4.096 = **4.194.304 lần tiếp xúc target**, không phải 4.194.304 target độc lập; T4 receipt báo 498.287 target TRAIN độc lập, reuse khoảng 8,417 lần. Đừng suy lượng token exposure thành độ đa dạng dữ liệu.

## 3. Bản đồ nghiên cứu Small-4M: outcome → layer/giả thuyết

**Quy tắc:** Study khác nhau không được cộng/pool mẫu số hoặc chấm lại cùng sealed set; các outcome dưới đây là *bằng chứng đã đóng*, không phải kết quả khoa học mới của Q001.

| Study / exact nguồn gốc | Kết quả và phạm vi đúng | Mapping và khả năng suy luận |
|---|---|---|
| **T4 VAL H1** — [`science adjudication`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/docs/pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md), blob `c1a471087ae30f31a696fbf786230eff3773a0d1` | Model VAL NLL **3,5223388517**, bigram **3,99723141696**, cải thiện tương đối **11,8805%**; `PASS_H1_CONFIRMATORY_VAL_SCOPE`, 1 seed. | Chứng minh học token distribution trong pilot; không chứng minh factual adherence. |
| **T4 TEST64** — [`sealed TEST one-shot`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/docs/pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md), blob `cf2bcb1c48d172afacb6b1f7406320851bfcbf65` | 64 truyện TEST, 14.669 target, model NLL **3,48359107334**, bigram **3,97360374532**; `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED`; đã tiêu thụ. | Giữ nguyên; không chạy lại/đổi metric/re-score. |
| **FRESH12** — [`owner unblind`](https://github.com/minhtri22/TokenToModel-Lab/blob/72cbf73c3adb78f9d4111f702de71fa10f713533/docs/pilot/ttm-small4m-source-of-truth/TTM_FRESH12_OWNER_CONTROLLED_UNBLIND_AND_SCOPED_QUALITY_ADJUDICATION_20261110.md), blob `1862a39ed54cdc80c39213b615a3f7c4a4526d65` | 48 outputs theo cặp checkpoint 1024/1280 và xử lý serialization, mean adherence 0,291667 mỗi arm, Δ=0; candidate gates 4 PASS/4 FAIL, `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED`. | Bổ sung bước/loại bỏ ký tự không chứng minh semantic gain. AI rater đơn; scope pilot. |
| **FRESH16 V2** — [`frozen adjudication`](https://github.com/minhtri22/TokenToModel-Lab/blob/0ec28d44587fde9ad4acba8cccae65648e367181/docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCIENTIFIC_ADJUDICATION_20261111.md), blob `ae8ded5bb03a595f9af4f333ef96271ed3991d7d` | H1 adherence≥2 **0/16** (threshold ≥12/16); H2 counterfactual **0/8** (≥6/8); `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED`. | S1/S2 hai **nhiệm vụ chấm khác nhau**, không phải agreement của 2 raters trên cùng items. Đặt câu hỏi về model/task/eval; không định vị được nguyên nhân. |
| **CF1 DEV36** — [`paired context`](https://github.com/minhtri22/TokenToModel-Lab/blob/d725c39094a5a584fd76386145db21ca6dc5eaf6/docs/research/TTM_CF1_DEV36_ONE_SHOT_INDEPENDENT_SCORE_READBACK_AND_SCIENCE_ADJUDICATION_20261111.md), blob `d6a094b2a9d0977728d5d2f13c7c945d7cb8ee96` | Preferred-candidate switch **0/36** trên DEV; BLIND FINAL chưa mở. | Không đảo ưu tiên A/B trong task cụ thể; có confound prior/position; chưa phải root-cause attention. |
| **D1 EXP32** — [`exploratory closeout`](https://github.com/minhtri22/TokenToModel-Lab/blob/0ec28d44587fde9ad4acba8cccae65648e367181/docs/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_EXP32_TERMINAL_EXPLORATORY_CLOSEOUT_AND_NEXT_RESEARCH_DIRECTION_20261112.md), blob `f53da235027be331682bf1a5b86b0d1e94cd5373` | Greedy/nucleus đều **0/32** đạt grade≥2; nucleus cải thiện repetition secondary; `RATER_INPUT_BYTE_PROVENANCE_NOT_VERIFIED`. | Decoder giúp một số thuộc tính bề mặt nhưng không giải quyết factual grade trong đo này; rater-byte không xác minh là giới hạn quan trọng. |
| **A/C FINAL24** — [`formal adjudication`](https://github.com/minhtri22/TokenToModel-Lab/blob/37165ce6eea0bb4b04d316e2998da579c91d13cf/docs/research/TTM_AC_FINAL24_INDEPENDENT_QA_AND_FORMAL_ADJUDICATION_20261112.md), blob `1af1b6d3743f5e986edcc3ef1e737b0f05188d3c` | **Điểm tuyệt đối A=C=0,6667/3**, hiệu C−A=0; strict wins C 1/24. `FAIL_CANDIDATE_EFFICACY_GATE_NO_DEMONSTRATED_C_GAIN` (128 updates/arm). | Cấu hình objective C **riêng thí nghiệm này** không thắng; tuyệt đối không diễn giải A=C=0 hoặc pool với H-DATA. |
| **H-DATA-S1 FINAL24** — [`owner unblind`](https://github.com/minhtri22/TokenToModel-Lab/blob/ef4cc05037f98129082cd429a75092b8cc822efb/docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_FINAL24_OWNER_UNBLIND_FORMAL_ADJUDICATION_20261114.md), blob `9cfb02e86c3893b2f927b1529c637bba797f40ae` | 24 pairs/48 continuations, cả 48 được chấm actor/object/goal=0; H0=H1=0/3; 3 primary gates FAIL, H1−H0=0. | Có thể là model yếu, task khó hoặc floor/rater issue — **chưa phân biệt**. One AI rater không phải human gold. |
| **FC01 A/B/C** — [`one-shot scoped review`](https://github.com/minhtri22/TokenToModel-Lab/blob/b5dd5890b73a29744530ed3a1ffbc0dc7ae5195a/docs/research/ttm-small4m-fact-conditioning/TTM_FC01_ABC_ONE_SHOT_INDEPENDENT_SCIENTIFIC_REVIEW_AND_SINGLE_SCOPED_ADJUDICATION_20261113.md), blob `0a425cbadfaf644a117693fce1c9b80b069185a7` | A=4/64; B=3/64; C contrastive=38/64 trên lexical holdout family; `entity_location` C chỉ **1/16**; `PASS_SCOPED_EXPLORATORY_FC01_NO_CONFIRMATORY_RELEASE`. | Hỗ trợ **giả thuyết** objective/data/task interaction, nhưng 4 template semantics, 1 seed và lệch theo strata; không có OOD/general reasoning proof. |
| **D1 R1** — [`independent HOLD closure`](https://github.com/minhtri22/TokenToModel-Lab/blob/6cab3b8e8430628aa5c944a494ccc08d8f8783fc/docs/research/ttm-small4m-fact-conditioning/TTM_D1_R1_INDEPENDENT_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_REVIEW_20261114.md), blob `43fa3aed1a802dde05511cf76afba6737eb47aa3` | `GO_CLOSE_R1_FORMULATION_DESIGN_ONLY`, `D1_BRIDGE_SCIENCE=HOLD`, admitted OOD=0 trong search hữu hạn. | Construct/ontology/shortcuts có thể làm benchmark không đo đúng nhiệm vụ; không chứng minh model reasoning FAIL hoặc toàn bộ ontology là không thể. |
| **Q1/Q2/T5/T6** — infra/serving source trên `main`, frozen Q1/Q2 matrix | Không có kết quả fact reasoning mới được xác lập bằng sự phù hợp backend/caching/parity. | Dùng loại trừ bug hệ thống khi có chứng cứ, **không** trộn vào science gate. |

**Loại trừ đúng scope:** EmbeddingGemma 2 và Vector Memory là hai chương trình độc lập, không được nhập kết quả/nhãn/checkpoint/bằng chứng vào Small-4M Q001. `SM4M-F0/F1/F2` cũ chỉ là tài liệu và thiết kế/source QA lịch sử; chưa được tái chấp thuận trong Q001.

## 4. FMEA có chọn lọc: lỗi nào đã chứng minh, lỗi nào chỉ là khả năng

| ID | Mức cần chú ý | Failure mode / trạng thái chứng cứ | Biện pháp bằng chứng nhỏ nhất; không tự thực hiện |
|---|---|---|---|
| `QF-01` | **HIGH** | Nhầm NLL H1 PASS với fact/prompt PASS. Đây là **lỗi suy luận measurement construct**, có thể xác nhận bằng định nghĩa metric/code + kết quả các study. | Khóa tách endpoint token NLL / teacher-forced context switch / generation factual score / rater reliability. |
| `QF-02` | **HIGH** | Rater/gold chưa được xác nhận cùng visible evidence ở nhiều phép đo; riêng D1 EXP32 ghi rõ `RATER_INPUT_BYTE_PROVENANCE_NOT_VERIFIED`, H-DATA một AI-rater và FRESH16 hai rater roles khác nhau. Không suy từ đó mọi score là sai. | Trước kiến trúc M0X, chỉ thiết kế một kiểm tra tối thiểu khả năng phân biệt đúng/sai và thẩm quyền nguồn; **không tự tạo gold trong Q001**. |
| `QF-03` | **HIGH** | Khả năng phân biệt yếu giữa model/data/objective/decoder: NLL vs adherence, FC01 restricted positive, H-DATA/A-C scoped negative; cùng hoặc khác nhiệm vụ, ngân sách, metric. | Ma trận hypotheses–expected signatures và baseline/equal-information-budget trước mọi new training. |
| `QF-04` | **MEDIUM** | BPE 768 TRAIN, model 2.048 TRAIN stories; 4.194.304 target exposures nhưng ~498.287 độc lập được dùng lại. **Có thể** gây giới hạn bao phủ, chưa chứng minh là root cause. | Mô tả exposure/dedup/corpus, đối chiếu task coverage từ nguồn hiện hữu; không tự đổi DATA. |
| `QF-05` | **MEDIUM** | Context 256 với learned absolute positions; đóng cửa sổ dữ liệu thành các mảnh 256-target, reset positions. Có thể cắt quan hệ dài, chưa có ablation fact distance. | Chỉ khi Q4 cho phép, thiết kế contrast length/distractor nhỏ nhất; hiện giữ `NOT_TESTED`. |
| `QF-06` | **MEDIUM** | Dễ nhầm default P02 hoặc synthetic P03 với trainer T4 A2. Source chứng minh đúng đường T4, không có lỗi được phát hiện trong đường pinned. | Mọi reviewer phải sử dụng exact T4 config/source/checkpoint hashes; flag sai source là `HOLD_SOURCE_MISMATCH`. |
| `QF-07` | **HIGH** | D1 ontology/construct có shortcut/khả năng nhận diện chưa chứng minh, admitted OOD=0; FC01 lợi ích theo template lệch strata. Đây là **rủi ro benchmark validity**, không phải lỗi Transformer. | Hard veto nếu benchmark/gold không phản ánh nhiệm vụ; không tạo 2³ combinations chỉ vì hợp đồng dễ chấm. |
| `QF-08` | **MEDIUM** | Raw TRAIN/VAL private bytes, original checkpoint weights và rights chưa được tái xác minh ở Q001; có historical SHA/receipts. | Mọi phép thực thi tương lai phải có source/private byte/custody admission riêng; không đòi tái tạo TEST ở Q001. |
| `QF-09` | **LOW** | Các văn bản legacy mô tả “mỗi thay đổi một branch” hoặc cho phép đưa QA vào lineage, có thể xung đột với policy 15/11/2026. | Dùng chính sách mới `TTM-GOV-QF-20261115-V1` ưu tiên; không sửa lineage lịch sử. |

Mức HIGH/MEDIUM/LOW ở đây là **ưu tiên nghiên cứu và mức ảnh hưởng đến quyết định**, không phải xác suất lỗi đo được hay một điểm FMEA RPN. Không có `SOURCE_CODE_DEFECT_CONFIRMED` trong các kiểm tra mã tĩnh đã thực hiện; điều này **không** chứng minh source không có lỗi.

## 5. 5 Whys có giới hạn + khả năng bác bỏ (Falsification)

**Gap quan sát:** `T4 VAL/TEST next-token NLL PASS` cùng tồn tại với `FRESH16/CF1/D1 EXP32 factual continuation thấp`, trong khi FC01 có kết quả dương theo template.

1. **WHY1 — Vì sao không mâu thuẫn?** Hai loại endpoint khác nhau: next-token likelihood trên TinyStories và factual instruction compliance/conditional switching trên prompt/rubric khác nhau. **OBSERVED (nguồn và mã)**.
2. **WHY2 — Vì sao next-token learner có thể không đạt fact task?** Mục tiêu MLE không cung cấp explicit target cho actor/object/goal retention; dữ liệu ít/khác phân phối, finite context, decoder prior, năng lực nhỏ và evaluator có thể cùng đóng góp. **HYPOTHESIZED, NOT_TESTED as causal attribution**.
3. **WHY3 — Tại sao mục tiêu là ứng viên?** FC01 contrastive arm C thắng trong lexical family, nhưng A/C FINAL24 không có lợi ích và FC01 entity_location yếu. **MIXED evidence**; chưa có xác nhận OOD/equal-budget trên cùng construct.
4. **WHY4 — Vì sao chưa phân biệt được evaluator vs model?** FRESH16 có hai vai chấm khác nhau; H-DATA có một AI-rater; D1 EXP32 thiếu xác minh nguyên byte input reviewer; các study không dùng cùng core/gold và metric. **OBSERVED limitations**, không chứng minh evaluator sai.
5. **WHY5 — Nguyên nhân gốc là gì?** **UNKNOWN/NOT_IDENTIFIED.** Dừng 5 Whys tại ranh giới nguồn. Không điền một nguyên nhân võ đoán để đủ năm câu trả lời.

**Phép chứng cứ phân biệt nhỏ nhất đề xuất, CHƯA THỰC HIỆN:** bắt đầu bằng phân tích cấu trúc hiện có (prompt–continuation–rater-visible information–gold claim) và xác nhận một bộ đối chứng/negative control có khả năng phân biệt true pass vs true fail; chỉ tiếp tục nếu đảm bảo rights/custody và Q4 scope. Sau đó mới xét teacher-forced conditioning (cùng checkpoint/task) trước free-generation/rater hay can thiệp kiến trúc. Không sửa score các set đã tiêu thụ và không mở test mới chỉ bằng đề xuất này.

## 6. Có cần SWOT hoặc MCDA ngay?

**Chưa.** Q001 đang kiểm tra **độ đáng tin của baseline**, chưa có hai phương án architecture mới đủ định nghĩa, gold/construct và cùng information budget để chấm điểm công bằng. SWOT có thể dùng tóm tắt rủi ro ở Q3, nhưng MCDA lúc này chỉ tạo điểm số dựa trên giả định. FMEA + 5W1H + traceability + 5 Whys có kiểm soát là các framework tối thiểu đủ ích lợi cho câu hỏi Q001.

Các giải pháp có thể nghiên cứu **sau** closure (không cấp phép tại đây): giữ baseline và đơn giản hóa phép đo, sửa objective/task alignment bằng controlled study, hoặc đổi benchmark construct nếu không có gold đáng tin. Không có căn cứ source-level để tự động thêm RoPE, MoE, thêm head/layer, hay mở GPU scaling.

## 7. Gate outcome, review handoff và closure boundaries

| Điều kiện Q001 | Trạng thái |
|---|---|
| Q1 — câu hỏi đã đăng ký trên `main` | `PASS_EXISTING` |
| Q2 — author source + evidence audit (báo cáo này) | `COMPLETED_AUTHOR_SOURCE_ONLY` |
| 38 kiểm tra static source/receipt assertions | `PASS_38_OF_38_AUTHOR_ONLY` |
| Exact Git source blobs | `PASS_EXPECTED_PINS_FOR_INSPECTED_SOURCES` |
| Private corpus/checkpoint/rights byte reread | `NOT_EXECUTED` |
| Runtime T4/model/QA/TEST | `NOT_EXECUTED` |
| Independent Q3 architecture + science interpretation | `PENDING` |
| Owner Q4 conclusion | `NOT_GRANTED` |
| New Small-4M F0–F2/research implementation | `HOLD` |
| `lineage.md` | `UNCHANGED`; không có kết quả khoa học mới để append |
| Merge source/code/historical branch | `NOT_AUTHORIZED` |

**Lý do chưa nhập báo cáo vào `main`:** Chính sách sau commit bootstrap đòi thay đổi qua review/PR và owner decision; Q2 author source audit **chưa là closure Q4**. Báo cáo và receipt được gửi nguyên gói cho independent reviewer, sau khi có Q3/Q4 mới đồng bộ quyết định lên `main`. Không mở branch mới chỉ để lưu báo cáo tác giả.

**Independent Q3 reviewer cần phản biện bốn điều:** (a) Pin source đúng và có bỏ sót execution path T4 thật? (b) FMEA có bỏ qua implementation defect hoặc hard veto nào? (c) Phân loại `SCOPE` và denominator ở những nhánh khác đúng hay không? (d) Có đủ căn cứ để giữ baseline **chỉ làm đối chứng lịch sử** trong khi phép đo vẫn HOLD không? Nếu phát hiện HIGH source/construct discrepancy, trả `HOLD_REVISE_Q2` với một gói sửa tích hợp; không tự chạy science.

**Phán quyết tác giả (Q2 only):** `KEEP_BASELINE_FOR_F0_F2_REVIEW — SOURCE_REFERENCE_SCOPED; HOLD_MEASUREMENT_AND_ARCHITECTURE_CHANGES; ROOT_CAUSE_IDENTIFIED=NO`. Chờ Q3 độc lập và owner Q4; không phải quyết định GO của owner.

**Bước thực hiện tiếp theo — duy nhất:** giao **report + JSON receipt Q001** cho reviewer độc lập để phản biện ở Q3, rồi trình owner Q4 closure. Chỉ sau đó mới xét quay lại F0–F2.
