# TTM-Small-4M — Tổng đối chiếu hậu CF1: học ngôn ngữ, tiếp nối nội dung và khoảng trống năng lực

**Ngày:** 2026-11-11  
**Task:** `TTM_SMALL4M_POST_CF1_FROZEN_O0_ORIGINAL_LANGUAGE_VAL_AND_FRESH_CONTINUATION_GAP_RECONCILIATION_DESIGN_ONLY_NO_NEW_TOY`  
**Trạng thái:** `DESIGN_ONLY_EVIDENCE_RECONCILIATION_COMPLETE`. Tất cả dữ kiện trong báo cáo đều là **kết quả lịch sử đã được commit/niêm phong**. Không tạo đầu vào, prompt, mô hình hay khoa học mới.  
**Nguồn nhận dạng O0:** P02 decoder-only, 3.749.376 tham số, vocab T1 BPE 2.048, context 256, original step1024 checkpoint SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, Git blob P02 `9762343e06cf800b50574c2871ae1ed58537fb18`.  
**Biên nhận máy:** [Evidence ledger / machine-readable reconciliation](../../artifacts/qa/ttm-small4m-post-cf1/TTM_SMALL4M_ORIGINAL_LANGUAGE_FRESH_CF1_EVIDENCE_RECONCILIATION_20261111.json).  
**Quản trị:** Nhánh nghiên cứu độc lập từ review CF1 commit `d725c39094a5a584fd76386145db21ca6dc5eaf6`; không merge, không sửa `main`, PR13, `lineage.md`. Không đọc raw TEST/Q1Q2/FRESH12/CF1 hoặc giải mã FINAL.

## 1. Câu hỏi nghiên cứu — tách ba năng lực

1. **Học phân bố token (next-token language modeling):** O0 có dự đoán token tiếp theo trên TinyStories VAL tốt hơn bigram TRAIN-only theo phép đo đã tiền đăng ký? **Có** trong phạm vi VAL.
2. **Tạo tiếp nối có liên quan (prompt-conditioned generation):** O0 có giữ nhân vật, vật thể, nhiệm vụ và diễn biến khi tự sinh nhiều token? **Đang yếu/chưa chứng minh** theo các lần chấm thăm dò FRESH12 và quality ablation.
3. **Đảo ưu tiên khi sự kiện thay đổi (counterfactual preference switching):** O0 có ưu tiên các kết quả đúng khác nhau trong hai ngữ cảnh phản thực CF1? **Không đạt 0/36 cặp** trên public DEV, nhưng chính bài thử CF1 có shortcut và confound.

Đây là **ba phép đo khác nhau**, không lấy kết quả khoa học VAL để phủ nhận một lỗi bám prompt, cũng không suy từ CF1 rằng mọi năng lực suy luận của P02 đều thất bại. Không tính trung bình hay gộp điểm NLL/AI rubric/pairwise-sign thành một số `quality`.

## 2. Bảng đối chiếu mức bằng chứng

| Nguồn đã khóa | Kết quả xác thực theo nguồn | Phạm vi / giới hạn |
|---|---|---|
| **T4 VAL H1** | **1.024 optimizer steps**, seed duy nhất; 256 truyện VAL, 61.122 targets; model NLL **3.5223388517** vs TRAIN-only bigram **3.9972314170**, cải thiện **11,880537%**; story-bootstrap95 của lợi thế tuyệt đối **[0.45818675,0.49406158]**; CPU độc lập tính lại | **`PASS_H1_CONFIRMATORY_VAL_SCOPE`**. Học mô hình ngôn ngữ, **không** suy ra bám prompt hoặc sinh truyện |
| **TEST lịch sử đã tiêu thụ** | 64 truyện, model NLL **3.48359107334** vs bigram **3.97360374532**, giảm 12,3316944% | **`PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED`** từ receipt cũ; không mở dữ liệu, không chấm/kiểm per-token lần nữa |
| **Lượt 1024→1280 lịch sử** | VAL NLL **3.522339 → 3.498089**; trong 8 prompt/2 decoders, adherence 0.375→0.375/3, điểm tổng 1.375→2.0625/9; 1280 thắng 6, thua 2, hòa 8 cặp | `NO_DEMONSTRATED_QUALITY_GAIN_SCOPED` theo ngưỡng +1.5/9 và 10/16 thắng; một reviewer AI, scoring sau khi thấy text A/B, không so sánh nhân quả data/loss |
| **Prompt serialization hậu nghiệm** | Bỏ một ASCII space cuối làm first newline **29/32→0/32**, keyword hit **0/32→3/32**; điểm bám ngữ nghĩa không được xác nhận | Xác minh ảnh hưởng token mở đầu, **không** xác minh mô hình giữ dữ kiện và mục tiêu |
| **FRESH12 đã hoàn thành** | 12 prompt, 48 đoạn, 24 cặp, 144 điểm Codex AI; **35/48 adherence=0**, mean 0.291667/3 ở cả baseline và trimmed, Δ=0; 95% descriptive CI [−0.208333,+0.166667] | Reviewer AI đơn lẻ, không phải human/external science; `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED`, không tiếp tục chấm bộ này |
| **Q1/Q2 historical partial** | V2 5/74 requests, 283 token; có tiếp nối lạc mục tiêu ở E01/E02; Q2 0/24 | Claim V1/V2 đã tiêu thụ; không tính thành benchmark tốc độ/chất lượng hoàn chỉnh; **không dùng lại** |
| **CF1 frozen-O0 DEV36** | Đúng cả hai ngữ cảnh **0/36**, A 1/36, B 35/36, **0/36 đổi lựa chọn**; 35/36 ưu tiên `y` ở cả A/B; mean D **−0.0004280**; 95% pair-bootstrap [−0.0075893,+0.0063098] | 144 teacher-forced likelihood thật; **`FAIL_SCOPED_CONTEXT_SWITCHING`**. Bài thử có lexical shortcut 36/36 và gold-position A=x/B=y 36/36 → không phải thước đo riêng năng lực state reasoning |
| **FRESH16 chưa thực thi** | 16 prompt, 8 cặp; native BPE/context/source SHA PASS; H1≥12/16, H2≥6/8 đã ghi trong ứng viên | **`SCIENCE_NOT_EXECUTED`**, `REVIEWER_CUSTODY=UNASSIGNED`, one-shot chưa cấp. Không được coi tiêu chí ứng viên là kết quả |
| **AC data/loss đề xuất** | Thiết kế can thiệp selection-vs-loss theo budget; receipt final pre-exec ghi `NO_GO_PREEXEC_EXTERNAL_AND_NATIVE_GATES_OPEN` | **Không có kết quả training can thiệp**; không được suy là data hay objective đã hiệu quả |

**Mốc huấn luyện:** TRAIN gốc 2.048 truyện, 498.287 vị trí nhãn riêng, tổng 1.024×4.096 = **4.194.304 target exposures**, tương đương **~8,417 lần** theo số vị trí nhãn riêng (không phải epoch/cross-document coverage đầy đủ). Hệ thống chỉ dùng CE next-token; không có head giám sát độc lập cho entity/goal/state.

### Đường dẫn nguồn cố định đã đọc

- [T4 VAL: adjudication + CPU independent recompute](https://github.com/minhtri22/TokenToModel-Lab/blob/d725c39094a5a584fd76386145db21ca6dc5eaf6/evidence/pilot/t4-science/T4_A2_FINAL_INDEPENDENT_SCIENCE_ADJUDICATION.json), Git blob `84cb94647c403ea358d8c991090bf56adc11f128`. [TEST one-shot: report lịch sử](https://github.com/minhtri22/TokenToModel-Lab/blob/d725c39094a5a584fd76386145db21ca6dc5eaf6/docs/pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md), blob `cf2bcb1c48d172afacb6b1f7406320851bfcbf65`.
- [1024/1280 quality review](https://github.com/minhtri22/TokenToModel-Lab/blob/72cbf73c3adb78f9d4111f702de71fa10f713533/docs/pilot/TTM_SMALL4M_1024_VS_1280_BLIND_QUALITY_SCOPED_ADJUDICATION_20261109.md), blob `27d6240839b5a8f70c26ee527bf3be9707e6d40d`; [prompt serialization](https://github.com/minhtri22/TokenToModel-Lab/blob/72cbf73c3adb78f9d4111f702de71fa10f713533/docs/pilot/TTM_SMALL4M_PROMPT_SERIALIZATION_POSTHOC_ABLATION_RESULT_20261109.md), blob `38c66ff40add58a32897a1923629ed80323c2d57`.
- [FRESH12 owner-scoped unblinding](https://github.com/minhtri22/TokenToModel-Lab/blob/72cbf73c3adb78f9d4111f702de71fa10f713533/artifacts/qa/ttm-original1280/fresh12/adjudication/FRESH12_OWNER_PUBLIC_SCOPED_ADJUDICATION_20261110.json), blob `3a88e28e4d9b07b30e3ea4baecbf55402b8e9ca3`; [Q1/Q2 old PARTIAL5](https://github.com/minhtri22/TokenToModel-Lab/blob/72cbf73c3adb78f9d4111f702de71fa10f713533/docs/pilot/TTM_Q1Q2_V2_PARTIAL5_QUALITY_AND_HOLD_ADJUDICATION_20261109.md), blob `4a3165168252b9ead4d866e89a7f59ca9f60605f`.
- [CF1 DEV36 độc lập tính lại 144 điểm](https://github.com/minhtri22/TokenToModel-Lab/blob/d725c39094a5a584fd76386145db21ca6dc5eaf6/artifacts/qa/ttm-narrative-cf1/reviews/CF1_DEV36_INDEPENDENT_GITHUB_SOURCE_SCORE_AUDIT_AND_ADJUDICATION_20261111.json), blob `b3f524472a4b980bc9e93aa10daaeab25829b565`, dựa trên **one-shot immutable commit** `cf6a37e5e9709ab0613918dc03ee70efa79f893f`.
- [FRESH16 source readiness](https://github.com/minhtri22/TokenToModel-Lab/blob/1583c5b475407799bfca75b503ddf359de7fda69/artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_NATIVE_OFFLINE_QA_READBACK_AND_EXECUTION_GATE_20261111.json), blob `c0fdba15918200944fbb007a68a22c7364045a34`; [AC pre-exec HOLD](https://github.com/minhtri22/TokenToModel-Lab/blob/837289fda82b41653a61b74e476f76a0b4c4137c/artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_SMALL4M_AC_FINAL_PREEXEC_SINGLE_DECISION_AND_SOURCE_READBACK_20261111.json), blob `0c83b23c13c588a7787dd64a6c3d9ed5da22c5ce`.

## 3. Phân tích: vì sao không mâu thuẫn?

**T4 VAL H1 = dự đoán token; FRESH12 = sinh tự hồi quy; CF1 = so xác suất tiếp nối có điều kiện.** T4 đo trung bình `−log P(token_t | prefix)` trên văn bản tham chiếu 61.122 nhãn, nên có thể giảm loss khi học cấu trúc câu, mô-típ phổ biến, tokenization và vị trí mà vẫn không giữ chủ thể/mục tiêu khi phải tự sinh 64 token. CF1 cố tình yêu cầu **đảo dấu ưu tiên giữa hai ứng viên** theo một sự kiện đã thay: mô hình có thể có phân bố nhạy ngữ cảnh nhưng sự thay đổi quá yếu để lật ưu tiên.

Số liệu CF1 đặc biệt rõ: `mean(|D|)=0.0123437`, còn `mean` ưu thế tuyệt đối x/y là `0.3091527`; tỷ số **~0.040**. Tuy nhiên 20/36 hiệu ứng `D>0` và 16/36 `D<0` **không đồng nghĩa** có/không có toàn bộ năng lực sử dụng ngữ cảnh. FRESH12 cũng có reviewer 1 AI và thang mạch lạc bằng 1 cho mọi mẫu; điểm Δ=0 không chứng minh hai format tương đương trên mọi prompt.

Một phép chẩn đoán trước đây cho thấy biến thiên tổng TV giữa full prompt và bốn BPE token cuối **0.2395** ở 1024, nhưng cắt ngữ cảnh làm đổi cả vị trí: chỉ xác nhận *logits phản ứng với input dài hơn*, **không** chứng minh nắm nhân vật/sự kiện.

### Các yếu tố nhiễu không được xóa hậu nghiệm

- **Vị trí câu trả lời CF1:** toàn bộ cặp vàng là A=x/B=y. Một evaluator được nhìn nhãn vị trí có thể đạt 36/36, nhưng đó không phải baseline model-only hợp lệ. Cộng với heuristic nông 36/36, độ phân biệt state reasoning CF1 kém. FINAL đã HOLD phải **giữ niêm phong**.
- **FRESH12:** 35/48 adherence=0 cho thấy mức chất lượng thấp trên tập được chấm, nhưng AI rubric đơn lẻ không có reliability giữa người chấm. Cổng trimmed-win/candidate FAIL là kết luận đúng phạm vi, không phải không thể cải thiện bằng bất kỳ objective khác.
- **1024→1280:** thay bước huấn luyện đã được tiêu thụ, không phải phép so sánh data-vs-loss công bằng; chấm một người và có format confound. Δ NLL nhỏ không được gắn với một nguyên nhân riêng.
- **T4 TEST / Q1Q2:** chỉ nhắc lại thống kê lịch sử; trong lượt này không truy xuất input, token windows, score raw, hoặc chạy lại bất kỳ lệnh nào.

## 4. Khoảng cách năng lực và thứ tự ưu tiên

| Mức kết luận | Điều đã biết | Điều chưa biết / nguyên nhân chưa cô lập |
|---|---|---|
| **Ngôn ngữ thống kê** | Có lợi thế VAL NLL thực và TEST held-out mô tả | Khả năng tổng quát ngoài TinyStories hẹp, nhiều seed |
| **Bám premise và diễn biến** | FRESH12 điểm bám prompt thấp; dữ liệu Q1/Q2 nhỏ cùng xu hướng | Phân bố TRAIN, objective, prompt novelty, capacity đóng góp bao nhiêu mỗi yếu tố |
| **Tham chiếu/nhân quả** | CF1 DEV không lật ưu tiên trong 36 cặp | State reasoning thực sự chưa có phép đo đáng tin: CF1 bị lối tắt và label-order leakage |
| **Hiệu ứng định dạng** | Trailing space làm thay đổi mạnh token đầu | Chỉnh serialization không bảo đảm tăng coherence/adherence |
| **Sửa bằng dữ liệu** | TRAIN 2.048 truyện, nhãn lặp ~8,417×, mô-típ phổ biến | Chưa kiểm định can thiệp selection/coverage cùng ngân sách |
| **Sửa bằng loss** | Original CE đều mọi token, không state/goal label riêng | Chưa có so sánh CE vs continuation-weighted loss đủ khoa học |
| **Mở rộng O1/attention/MoE** | Chưa có đối chứng cùng data/tokenizer/budget | Không có bằng chứng thay kiến trúc là giải pháp tốt nhất |

**Đề xuất thứ tự:**
1. **Đánh giá trung thực trước:** ghi đúng `PASS_TOKEN_DISTRIBUTION`, `PROMPT_ADHERENCE_WEAK_SCOPED`, `CF1_SWITCHING_FAIL_SCOPED` mà không phủ định lẫn nhau. Khi có phép đánh giá tiếp nối mới, chuẩn hóa prompt, khóa rubric/split và chấm mù.
2. **Ưu tiên so sánh *dữ liệu vs mục tiêu học* (data selection vs objective weighting) ở mức thiết kế:** sử dụng nhánh AC đã có và trạng thái `NO_GO_PREEXEC` hiện hành. Giữ chung weights P02/BPE/context, budget next-token, không dùng step1280 lịch sử làm arm đối chứng. Việc bám premise phải là thước đo chính trên holdout mới và rater phù hợp.
3. **HOLD mọi huấn luyện mới trong lượt này.** Hiện chưa có kết quả AC và chưa đủ owner/reviewer/escrow/native readiness theo biên bản. Không nhân bản FRESH16 hoặc mở toy mới nhằm đánh bại heuristic.
4. **DEFER thay kiến trúc:** trước khi thay attention/MoE/O1, cần chứng minh data/loss có hay không có hiệu ứng trên chính O0 theo ngân sách ngang bằng. Ngược lại sẽ không biết lợi ích đến từ kiến trúc hay nhiệm vụ/dữ liệu.

**FRESH16** (16 prompt, 8 cặp) là bộ đánh giá chất lượng được soạn trước, kiểm nguồn/BPE PASS nhưng chưa chạy science vì `REVIEWER_CUSTODY=UNASSIGNED`. Nếu owner sau này muốn có thêm bằng chứng chưa tiêu thụ, dùng **đúng kế hoạch đã khóa** thay vì lập benchmark toy mới; yêu cầu một quyết định cho cả reviewer và một lượt CPU, không cấp micro-permits rời rạc. Việc này **không được thực thi trong lần đối chiếu hiện tại**.

## 5. Một quyết định tổng hợp

`HOLD_NEW_TRAINING_AND_NEW_NEURAL_EVAL__GO_SOURCE_ONLY_NEXT_DECISION_DESIGN`.

- **Có:** O0-Small4M gốc học ngôn ngữ theo NLL trên TinyStories pilot tốt hơn bigram; không phủ nhận PASS gốc.
- **Chưa chứng minh:** mô hình tiếp nối truyện bám nhân vật, mục tiêu hoặc quan hệ phản thực ổn định; FRESH12 và CF1 chỉ cho kết quả yếu theo phạm vi riêng.
- **Không kết luận:** tăng tham số, attention mới, MoE, O1 hoặc huấn luyện thêm trên dữ liệu cũ là lời giải.
- **Hướng khả thi nhất để thiết kế tiếp:** một gói so sánh dữ liệu/loss ngang ngân sách dựa trên AC **đang HOLD**, cộng việc rà soát FRESH16 đã khóa; không sửa dữ liệu/đổi ngưỡng hoặc thực thi ngay.
- **Không mở:** FINAL CF1, R3A/N1, original TEST/Q1Q2, FRESH12 cũ, OOD256 biến thể EmbeddingGemma2; đó không phải nguồn chứng cứ cho phép O0 architecture gain.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_DATA_OBJECTIVE_EXISTING_AC_AND_FRESH16_SINGLE_INTEGRATED_SCIENCE_READINESS_GAP_REVIEW_DESIGN_ONLY`. Chỉ xác định các điều kiện khoa học thực sự còn thiếu trong hai thiết kế đã có, những so sánh hợp lệ và tiêu chí quyết định hữu hạn. **Không** tự lên lịch train, không tái đánh giá lịch sử và không chạy inference.

**Bảo toàn:** `ONE_SHOT_CF1=CONSUMED_COMPLETE` · `FRESH12=CONSUMED` · `TEST=CONSUMED_UNREOPENED` · `Q1Q2=CONSUMED_UNREOPENED` · `FRESH16=NOT_EXECUTED` · `AC_SCIENCE=NOT_EXECUTED` · `NEW_TRAINING=NO` · `GPU=NO` · `MAIN/PR13/LINEAGE=NOT_WRITTEN`.
