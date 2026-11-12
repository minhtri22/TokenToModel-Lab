# TTM-Small-4M — Lưu kết quả âm FINAL24 và thiết kế nghiên cứu kế nhiệm

**Operation:** `TTM_SMALL4M_POST_FINAL24_NEGATIVE_RESULT_ARCHIVE_AND_NEW_HYPOTHESIS_DESIGN`  
**Ngày:** 2026-11-12 · **Mode:** `ARCHIVE_AND_DESIGN_ONLY`  
**Nguồn ghim:** `minhtri22/TokenToModel-Lab`, nghiên cứu A/C tại `16d00b23d9190a1331058a5b407700b6cb3c3a20`, `lineage.md` mục `L0015`.  
**Nhánh mới:** `research/ttm-small4m-post-final24-negative-archive-hypotheses-20261112`  
**Kết luận:** `FINAL24_CLOSED_CONSUMED`; `NEW_EVAL_DEV12_FINAL24_FROZEN_SOURCE_ONLY`; `NEW_SCIENCE=HOLD_NOT_AUTHORIZED`.

## 1. Mục đích và ranh giới

Đóng gói chứng cứ thí nghiệm A/C đã hoàn tất, không sửa điểm chấm hoặc thay đổi kết quả âm; giải thích đúng mức những dấu hiệu chất lượng thấp; chọn **một** giả thuyết kế nhiệm có thể bị bác bỏ, ưu tiên chẩn đoán không huấn luyện. Chuẩn bị 12 DEV + 24 BLIND_FINAL **hoàn toàn mới**, cam kết SHA-256 trước bất kỳ lần suy luận nào.

Không thực hiện: training mới, inference mới, rescore, mở lại FINAL24/FRESH12, chạy TEST/Q1/Q2/OOD, copy private key, xóa checkpoint hoặc merge lên `main`. Không tự cấp quyền Colab/GPU. Mọi quyền sử dụng nguồn và người chấm độc lập của nghiên cứu kế nhiệm cần xác nhận riêng.

## 2. Bằng chứng thực nghiệm đã kiểm chứng

**Lịch sử thực nghiệm:** P02/T4 3.749.376 tham số, context 256, BPE 2048; TinyStories TRAIN 2.048 truyện, 2.691 cửa sổ, 498.287 nhãn độc lập trong pack. A và C cùng parent checkpoint bước 1.024, cùng draw IDs, cùng 128 optimizer steps (đến 1.152), 524.288 target presentations mỗi arm. Chỉ thay **uniform valid-token CE** thành **suffix-position weighted CE 1:3** (các vị trí từ 32 trở đi có hệ số 3). Không đổi dữ liệu, tokenizer, kiến trúc, số token tiêu thụ. Source: `TTM_SMALL4M_HOLD_REVISE_DATA_OBJECTIVE_EQUAL_BUDGET_SOURCE_ONLY_REVIEW_20261111.md` và FINAL24 adjudication.

**Kết quả FINAL24 một người chấm GPT-6 (AI, tự khai blind), một seed:** 24 prompt, 48 continuations, 144 điểm và 24 note đã đóng băng; 107/107 kiểm toán hậu giải mù theo code path riêng PASS. Trung bình adherence A = C = **0,6667/3**, C−A = **0,0000**; C thắng 1, A thắng 1, hòa 22. Coherence A=C=1,25, consistency A=C=1,6667; VAL NLL A=3,5112859126, C=3,5123888919 (regression ~0,0314%). Cổng hiệu quả ứng viên tiền đăng ký thất bại. Đây **không** phải chứng minh hai mô hình tương đương.

**Quan sát bổ sung chỉ đọc trên 48 đầu ra đã khóa**, không là bằng chứng causal hoặc một bộ test mới:
- 4/24 cặp có văn bản A/C giống hệt từng byte.
- 19/24 đầu ra A và 20/24 đầu ra C chạm hạn mức **64 BPE token**; không được hiểu tự động là EOS sai vì decoder chủ động cắt tại giới hạn.
- Số điểm adherence A: 9 lần 0, 14 lần 1, 1 lần 2; C: 10 lần 0, 12 lần 1, 2 lần 2. Không có điểm 3.
- Tỷ lệ **lặp 3-gram từ** mô tả, tính riêng mỗi văn bản rồi lấy trung bình: A ~0,272; C ~0,310. Thuật toán mô tả: tách `\b\w+\b` ở bản `lower`, `1−unique_3grams/total_3grams`, chọn 0 nếu không đủ ba từ. Chỉ số này chưa tiền đăng ký cho FINAL24, **không** là so sánh suy luận chính thức của A/C.
- Văn bản thường rời nhân vật/mục tiêu rồi lặp các cụm chuyện quen thuộc; điểm thấp không tự chỉ ra nguyên nhân của vòng lặp.

**Chứng cứ lịch sử:** PR #13 root-cause chỉ ra dấu cách ASCII cuối prompt làm lệch token đầu sang `\n` ở 16/16 đầu ra thử cũ và biến đổi logits mạnh. FRESH12 bỏ dấu cách cho adherence delta 0/3, nên sửa serialization **không chứng minh đã giải quyết bám ngữ nghĩa**. FINAL24 mới đã chuẩn hóa không trailing space nhưng vẫn đạt trung bình ~0,667/3. Nghiên cứu Q1/Q2/TEST/OOD lịch sử không được tái dùng để đánh giá mô hình mới.

## 3. Phân tích nguyên nhân: không đồng nhất tương quan với nhân quả

| Giả thuyết | Dấu hiệu hỗ trợ | Điều CHƯA chứng minh | Mức ưu tiên |
|---|---|---|---|
| **H-DEC:** suy luận greedy thúc đẩy vòng lặp token/cụm | nhiều đoạn lặp; 19–20/24 đụng 64 token; n-gram repetition cao | đổi decoding có thực sự giảm lặp mà không làm mất bám prompt? | **1: thử rẻ, không training** |
| **H-DATA:** nguồn 2.048 truyện và cách chọn cửa sổ chưa đủ đa dạng ngữ cảnh mục tiêu | mô-típ phổ biến, tên lạ hiếm; model học NLL nhưng kém tiếp nối tình huống | cần phép can thiệp dữ liệu có kiểm soát; B/D first-story cũ còn *giảm* số truyện độc nhất 1493→1363, nên không đại diện cho diversity | 2: thiết kế sau H-DEC |
| **H-LOSS:** weighted CE theo vị trí chưa phù hợp mục tiêu giữ nhân vật/quan hệ | FINAL24 C−A=0 với 128 bước | các loại loss khác có hiệu quả không? không suy từ C thất bại ra toàn bộ CE | 3: cần tín hiệu riêng và nhãn hợp lệ |
| **H-CAPACITY:** model 3,75M / BPE 2048 / dữ liệu nhỏ giới hạn khả năng conditional continuation | VAL NLL tốt hơn bigram nhưng quality kém | chưa loại trừ data/decoding/objective, chưa có matched-capacity study | yếu tố nhiễu, không quy trách nhiệm |

Do FINAL24 đã tiêu thụ, mọi nhận xét trên là **hình thành giả thuyết (hypothesis generation)**; chúng không có giá trị chứng minh trên FINAL24 lần thứ hai.

## 4. Giả thuyết được chọn cho kế nhiệm — H-DEC-R1

**Câu hỏi phản chứng:** Trên **cùng checkpoint A bước 1.152**, cùng prompt, cùng giới hạn sinh, liệu một cơ chế **repetition penalty** cố định có làm giảm vòng lặp so với greedy thuần mà không làm giảm chất lượng bám prompt hay không?

**Biến độc lập duy nhất:** decoder.

| Thành phần | D0 — Control | D1 — Treatment |
|---|---|---|
| Checkpoint | A bước 1.152 SHA256 `ae9f05c5234ac98e3f9150e3f27501d217c1942a381650bec5aef91a1f56196b` | **Chính checkpoint ấy**, không finetune |
| Tokenizer | BPE 2048 gốc, SHA manifest `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` | giống D0 |
| Prompt | cùng 12 DEV và 24 FINAL, không trailing ASCII space | giống D0 |
| Sinh | greedy argmax | greedy argmax sau repetition penalty `1,15` |
| Budget | tối đa 64 token BPE mới, dừng EOS | giống D0 |
| Sampling/temperature | Không | Không |
| Dữ liệu, loss, kiến trúc | không thay đổi | không thay đổi |

**Định nghĩa D1 cố định (source specification):** Ở bước sinh thứ `t`, lấy logits dự đoán token kế tiếp từ mô hình. Với **mỗi token ID riêng biệt đã xuất hiện trong continuation tính đến trước bước `t`**, áp penalty đúng một lần: logit > 0 thì chia 1,15; logit < 0 thì nhân 1,15; logit bằng 0 giữ nguyên. Không áp penalty lên token chỉ có trong prompt. Sau đó argmax; khi đồng điểm dùng token ID nhỏ nhất. Nếu sinh EOS thì dừng. Không thay đổi logits ở bước đầu, vì chưa có token continuation. Không tự thử các penalty 1,05/1,10/1,20 rồi chọn tốt nhất trên FINAL. Không “repair” văn bản hay lọc output hậu nghiệm.

**Lý do chọn:** Chạy inference ngắn trên 1 checkpoint đã có — tiết kiệm hơn huấn luyện 128 bước × 2 arm; nếu không giảm vòng lặp, bác bỏ hướng decoder này sớm. Nếu giảm lặp nhưng adherence vẫn thấp, không được nói đã sửa semantic prompt following. Khi đó mới xem xét H-DATA theo một hợp đồng riêng.

## 5. Bộ đánh giá mới — đã khóa nội dung, chưa mở FINAL

- File gốc **owner-private**: `TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json`, 18.076 byte, SHA256 `9480ba73cbbe425fc9b61cc3253df81b32d52b0c35127d6e4392e5b5d6b0d54f`.
- `TTM_SMALL4M_NEXT_EVAL_DEV12_PUBLIC_20261112.json`: 12 DEV công khai, SHA256 `5d24d4ad9a5cb4c7d0db9efa9fbddbb2d34f321d67df602d2f4b6bca3d183193`.
- `TTM_SMALL4M_NEXT_EVAL_FINAL24_PUBLIC_SHA_COMMITMENT_20261112.json`: chỉ có 24 ID, cohort, stratum và SHA của prompt FINAL; SHA256 tệp `3c6d484d40eba4cbdf0d122d032e228b02fa67af48647830a273f93a54f32060`. **Không công bố 24 prompt FINAL rõ chữ** vào GitHub.
- Cơ cấu: 4 strata × (3 DEV + 6 BLIND_FINAL) = 36 prompt; `object_custody`, `social_relation`, `causal_obstacle`, `temporal_rule`. ID mới `ND01..ND12`, `NF01..NF24` (không tái dùng `R/Q/F` cũ).
- Quyền nguồn: 36 prompt **mới do trợ lý tự viết**, không trích TinyStories hoặc văn bản ngoài. Không thể xác nhận chưa từng có câu tương tự ở mọi nguồn bên ngoài; kiểm trùng chỉ trong phạm vi công khai được mô tả dưới đây.
- QA tính trên text: 0 trùng nguyên văn với 24 FINAL24 cũ và 12 FRESH12 cũ; max word-trigram Jaccard giữa 36 prompt mới **0,043478**, giữa mới và 36 prompt công khai cũ **0,057143** (tách từ `re.findall('[a-z]+', lower_text)`). **Không truy cập TRAIN, TEST, Q2/OOD** để so trùng. Không tuyên bố bảo đảm zero leak ở mọi tập chưa kiểm.
- Tất cả prompt mới đều có trường nhân vật/vật thể/mục tiêu do tác giả ghi sẵn cho **phân tích sau khi freeze**, không cấp các trường này cho người chấm mù. Exact-token BPE round-trip và số token context <=256 **chưa chạy**, giữ thành tiền điều kiện trước science release.

**Bất biến:** Chỉ DEV có thể được kiểm formatting/runner sau owner GO; BLIND_FINAL chỉ được đưa vào *một lượt đánh giá khoa học* khi điều kiện release đầy đủ. Nếu đã xem outcome trên FINAL, không được điều chỉnh decoder hoặc thay prompt rồi công bố là cùng phép thử xác nhận. Không mở TEST gốc.

## 6. Chỉ tiêu và cổng ứng viên ĐỀ XUẤT — chỉ dùng cho nghiên cứu mới

**Endpoint chính:** `mean_over_24_prompts(repeat_fraction_D1 − repeat_fraction_D0)` trên BLIND_FINAL mới. `repeat_fraction` = `0` nếu có ít hơn 3 token-word, ngược lại `1 − unique_word_trigrams / total_word_trigrams`. Quy tắc tách từ công khai và khóa cho phép kiểm toán: `re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", output.lower())` với 3-gram chồng lấp. Đây là metric mới **không hồi tố** áp vào FINAL24 cũ; khác chuẩn tách `\w` chỉ đọc ở mục 2. Chốt lại chính xác routine trước khi chạy.

**Ngưỡng ứng viên cố định cho H-DEC-R1 (đề xuất, chưa owner science GO):**
1. `mean(D1−D0)` ≤ **−0,10** điểm tỷ lệ lặp (mức giảm ≥10 điểm phần trăm).
2. D1 giảm lặp chặt ở **≥16/24 prompt** (hòa không tính thắng).
3. Upper 95% CI bootstrap cặp trên 24 prompt nhỏ hơn 0: resample index 24 cặp có hoàn lại, **20.000** resamples bằng NumPy `default_rng(20261112)`, percentile quantile 0,025/0,975; khóa exact NumPy version khi source QA.
4. Chất lượng guardrails (người chấm mù 3 trục 0–3, 144 điểm +24 ghi chú): mean adherence `D1−D0 >= −0,25`, coherence `>=−0,25`, consistency `>=−0,25`.
5. Chống lách ngưỡng bằng đầu ra quá ngắn: số đoạn D1 dưới **8 từ** không được vượt D0 (cùng regex tách từ). Báo tỷ lệ EOS thực, số BPE token và output ở cap, không đổi ngưỡng sau kết quả.

Điều kiện 1–5 phải đồng thời đạt mới gọi **`H_DEC_R1_EXPLORATORY_CANDIDATE_PASS`**. Nếu không: **`H_DEC_R1_NO_DEMONSTRATED_SCOPED_BENEFIT`**. Bản đăng ký này đủ cụ thể để thiết kế và khóa eval, nhưng **chưa phải permission khoa học**: mã decoder, bộ kiểm tra, reviewer, AES escrow và rights/checkpoint custody phải có byte/source lock, static + runtime QA và owner GO trước inference. Không tự xem các threshold chưa chạy là một kết quả.

**Hạn chế đo:** 3-gram lặp từ không phản ánh đầy đủ semantic adherence; 24 prompt và một reviewer AI chỉ cho kết luận thăm dò. Giảm lặp có thể làm nội dung ít ngữ pháp hơn; guardrail chất lượng là bắt buộc. Không sử dụng xác suất p-value xác nhận ngoài protocol.

## 7. Quy trình one-shot và bàn giao

1. **Thiết kế/nguồn (lượt này):** archive immutable A/C; freeze 12 DEV + 24 FINAL bằng SHA; công bố commitment không tiết lộ FINAL; lưu kết quả âm và cổng mới vào GitHub nhánh riêng. **Không có GPU**.
2. **Pre-exec QA một cổng:** xác minh file private đúng SHA, BPE roundtrip và context budget, checkpoint A-1152, code D0/D1, negative tests (prompt không bị penalty; token đã sinh bị penalty đúng một lần; dấu logits âm/0; EOS; ties), sampler/counter, room Drive checkpoint, rights/reviewer, AES 12/12 và run_id mới; owner GO/HOLD một lần.
3. **Một lượt inference nếu được GO:** 12 DEV chỉ dành QA định dạng đã khóa, sau đó 24 FINAL × 2 decoder một lượt; cache raw và SHA owner-only. Không sinh lại khi kết quả xấu; không chạy C để tìm lời giải thích hậu nghiệm.
4. **Blind evaluation:** D0/D1 được mã LEFT/RIGHT cân bằng, mapping AES owner-only, một người chấm phiên khác, đóng 144 score + 24 note + SHA trước giải mù; độc lập chỉ tự khai AI nếu đúng trường hợp. Tính lại endpoint trên byte nguyên và adjudicate, lineage append-only theo cổng khác.
5. **H-DATA nếu thất bại:** thiết kế so sánh matched-budget từ cùng parent nhưng với nguồn/trình chọn cửa sổ đa dạng hơn (không dùng first-story B cũ như đại diện diversity); cần **NEW FINAL** sau H-DEC, không tái sử dụng `NF01..NF24` để tuyên bố confirmatory lần thứ hai.

## 8. Sự kiện phạm vi và kết luận quản trị

Trong lần khám phá nguồn cho bước này, đã **đọc một tệp GitHub công khai chứa các prompt Q1 lịch sử** khi kiểm kê; đây là một lần **đọc metadata prompt**, không phải chạy inference, chấm lại, huấn luyện hoặc xem TEST. Điều này vượt cách hiểu chặt của cam kết "không truy cập Q1" nên được ghi công khai như **`READ_ONLY_Q1_PUBLIC_PROMPT_METADATA_SCOPE_DEVIATION`**. Nội dung Q1 **không được dùng** làm prompt mới, nguồn huấn luyện hoặc tham gia tính novelty ở mục 5; không đọc thêm Q1/Q2/TEST/OOD. Cần giữ sự kiện trong hồ sơ thay vì khẳng định "no Q1 read" tuyệt đối.

**Quyết định:**
- `AC_FINAL24_ARCHIVE=PASS_MANIFEST_PINNED`;
- `AC_EFFICACY=FAIL_CANDIDATE`, giữ nguyên trong lineage L0015;
- `NEW_EVAL=FROZEN_SOURCE_ONLY_PRIVATE_FINAL_PUBLIC_SHA`;
- `H_DEC_R1=SELECTED_PREREG_DESIGN_ONLY`;
- `NEXT_SCIENCE=HOLD_SOURCE_QA_AND_OWNER_GO_REQUIRED`;
- `TRAINING=0`, `NEW_INFERENCE=0`, `TEST_Q2_OOD_REUSE=NONE`, `MAIN/EXISTING_LINEAGE=UNCHANGED`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_H_DEC_R1_INTEGRATED_SOURCE_QA_BPE_CONTEXT_CHECK_RIGHTS_REVIEWER_AND_SINGLE_OWNER_GO_HOLD_PREEXEC_NO_INFERENCE`.
