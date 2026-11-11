# TTM-Small-4M — Hậu FRESH16: phân định khoảng cách NLL / tuân thủ prompt và quyết định kế nhiệm

**Operation:** `TTM_SMALL4M_POST_FRESH16_NEGATIVE_RESULT_SCIENCE_GAP_RECONCILE_DESIGN_ONLY`  
**Ngày:** 2026-11-11 · **Chế độ:** `READ_ONLY_REVIEW + DESIGN_ONLY`  
**Nhánh ghi tài liệu:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111`. Không ghi đè nhánh thiết kế AC/hậu CF1 đang do nghiên cứu khác quản lý.  
**Phán quyết điều phối:** `GO_NEXT_CAUSAL_DIAGNOSTIC_DESIGN_ONLY` / `HOLD_ALL_NEW_SCIENCE_EXECUTION` / `HOLD_SUCCESSOR_TRAINING` / `O1_DEFER`.

## 1. Kết luận đã biết, nguồn và giới hạn nhận dạng nguyên nhân

| Trụ bằng chứng | Kết quả đã khóa | Điều phép đo **không** chứng minh |
|---|---|---|
| T4 bước 1024 / VAL (256 truyện) | NLL 3,5223388517 so với bigram TRAIN-only 3,9972314170; cải thiện 11,880537%; `PASS_H1_CONFIRMATORY_VAL_SCOPE` | Không khẳng định tuân thủ prompt/sự kiện khi tự sinh |
| T4 TEST 64 truyện lịch sử | NLL 3,48359107334 so với bigram 3,97360374532; cải thiện 12,3316944%; `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED` | Không được dùng lại TEST để chọn can thiệp hoặc xác nhận độc lập lần hai |
| FRESH12 lịch sử | 35/48 đầu ra adherence=0; không chứng minh tăng chất lượng ngữ nghĩa sau sửa serialization | AI rater đơn, không đủ định vị dữ liệu/loss/scale |
| CF1 DEV36 đã tiêu thụ | 0/36 cặp đảo preference; 35/36 cặp thiên về cùng completion y; chênh ưu tiên ngữ cảnh nhỏ hơn lexical prior trong phép đo | Có confound lexical và gold position nên không phải phép chứng minh mô hình không có hiểu biết tình huống |
| FRESH16 V2 hoàn tất | CPU one-shot 32/32; S1 28×1 + 4×0, không ai ≥2; S2 16/16 H2=0; bước 1024 chính: H1=0/16, H2=0/8, 4 nhóm đều 0; `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED` | Không nhận dạng riêng nguyên nhân nào; checkpoint 1280 chỉ `DESCRIPTIVE_ONLY` |

Nguồn cuối FRESH16: commit `4c3731573f3091300d3dd00dc67f4e2940aec4a3`, tally SHA256 `64ec345fef6ef2f1c8b08e847047e3d3ac53f7bcca83fe39ae10d27e69b6f181`. S1 SHA `d08d59a9fe9738ef798aa2e0449345cb76e5c9f24f825a37685f928052028d35` (Git `5fd1d923de52d18709a39332400e3e98e6dfb31d`); S2 SHA `517643feba73c96003334a1e8a9095ebd091aaff3e764ddd87faf91dbf78b31b` (Git `9c02e0f3c7d3073e742de7fc75a08e5a48ec9afe`). Giữ nguyên runner HEAD `c05872354d892a9656f8f98642866f7eebfd0f50`, runner blob `f069f2bdaa2d9691a1ce6c9746ff8f2923beb1d8`.

**Phân biệt H2 bắt buộc:** quy tắc H2 yêu cầu cả hai S1 adherence≥2. Do cả 32 đầu ra không đạt, mọi H2=0 trong FRESH16 là hệ quả tất yếu của cổng S1. Vì thế H2 không phải bằng chứng độc lập rằng mô hình đã tạo được các hành động đúng nhưng thất bại ở phân biệt phản thực. Đây là **floor/gating effect**, cần đo độ nhạy dữ kiện riêng, không cộng H1 và H2 như hai phép chứng minh nguyên nhân độc lập.

**Giới hạn cửa sổ thật:** runner E0 `validate_inputs` kiểm BPE prompt dài 1..192 token và `P02Config.max_seq_len=256`; vòng sinh tối đa 64 token, ở mỗi bước dùng đúng `ids+generated`, `torch.argmax` rồi dừng khi EOS=256. Tổng chiều dài lớn nhất không vượt 256. Vì thế giả thuyết **cắt prompt do overflow tại chính FRESH16** không phù hợp mã đã khóa; song mô hình có thể chưa học cách sử dụng facts trong context hoặc vị trí cues, không loại trừ hạn chế attention/capacity. Greedy làm tăng nguy cơ tự lặp/chuyển chủ đề nhưng **chưa được so với decoder khác trên bộ mới**.

Bằng chứng bên ngoài chỉ hỗ trợ cơ chế khả dĩ, **không gán nguyên nhân cho TTM**: Arora et al., ACL Findings 2022 (perplexity không nắm lỗi tích lũy khi free-running; https://aclanthology.org/2022.findings-acl.58/); Holtzman et al., ICLR 2020 (degeneration phụ thuộc decoder, https://arxiv.org/abs/1904.09751); Eldan & Li, TinyStories 2023 (mô hình dưới 10M vẫn có thể sinh truyện khá mạch lạc nếu chế độ dữ liệu/train phù hợp, https://arxiv.org/abs/2305.07759).

## 2. Ma trận giả thuyết và phép phân biệt có giá trị

| Cơ chế ứng viên | Bằng chứng hiện có | Can thiệp/đối chứng có sức phân biệt | Giới hạn kết luận |
|---|---|---|---|
| `H_DATA`: corpus ít/không đủ đa dạng kiểu nhiệm vụ và dữ kiện | 2.048 truyện TRAIN, 498.287 vị trí nhãn riêng, 4.194.304 lượt nhãn (~8,417 lượt/vị trí), lặp kiểu công viên/cây/chó trong FRESH16 | Giữ checkpoint gốc + loss + steps, đổi **chính sách chọn cửa sổ TRAIN** B−A và D−C trong thiết kế A/B/C/D hiện có | Chỉ nhận dạng tác động của first-story-window sampling, **không** tách được corpus size, factual supervision hay quality khỏi vị trí |
| `H_OBJECTIVE`: uniform next-token CE không ưu tiên giữ mục tiêu/sự kiện | NLL đạt nhưng S1 0/32≥2; phù hợp gap, chưa nhân quả | A/C có sẵn: cùng parent/source/draw, chỉ đổi `suffix_position_weighted_CE`; so C−A trên FINAL24 mù đã khóa | Kiểm **trọng số loss theo vị trí**, không kiểm trực tiếp goal/role auxiliary supervision |
| `H_CAPACITY`: mô hình 3.749.376 tham số quá nhỏ/thiếu train tối ưu | Chỉ một family/seed; dữ liệu bên ngoài chứng minh không phải mọi mô hình dưới 10M đều bất lực | Chỉ phép train **hai scale** với corpus, objective, curriculum, budget có đối chứng, nhiều seed; hoặc bounded training-curve evidence | Không tách capacity khỏi compute/sample efficiency bằng FRESH16/AC; chi phí lớn, `DEFER` |
| `H_CONTEXT`: không gắn dữ kiện qua vị trí/độ dài | FRESH16 không vượt context256; vẫn có thể phụ thuộc vị trí/distance | Giữ text/target facts, tạo short/long **đều ≤256**, cân bằng vị trí cue và filler, chấm margin phản thực + adherence | Long filler cũng đổi phân phối/ngữ nghĩa; phải log BPE lengths, giữ nội dung có nghĩa và counterbalance |
| `H_DECODING`: greedy argmax gây generic repetition / rollout drift | FRESH16 chỉ greedy, nhiều output generic; prompt-format cũ đổi token đầu nhưng không tạo semantic gain đã được chứng minh | **Cùng checkpoint và prompt mới**, teacher-forced fact-choice margin + greedy vs seeded sampling, chấm mù bằng cùng rubric và repetition | Sampling có stochastic variance, không tự chứng minh fact binding; forced-choice ≠ tự sinh sự kiện; không được dùng FRESH16/TEST để thử lại |
| `H_TOKENIZER_SERIALIZATION` (nhiễu ngang) | BPE2048; prompt là câu dang dở; ablation lịch sử đổi first-token lexical mà chưa có gain semantic | Giữ exact prompt bytes khi test decoding; nếu so format, thay *một* thành phần và cân bằng tính cùng nghĩa, không lén chỉnh rubric | Từ tiếp theo có thể thay đổi chỉ vì ký tự chốt, không đại diện semantic capability |

**Kết luận nhân quả đến hiện tại:** có bằng chứng rõ về **năng lực điều kiện hóa dữ kiện yếu trong sinh tự do**; chưa đủ dữ liệu thực nghiệm để xếp hạng H_DATA/H_OBJECTIVE/H_CAPACITY. Greedy là biến ngoại sinh trong FRESH16 chứ không được xác nhận là nguyên nhân. Không dùng NLL PASS để phủ định kết quả này.

## 3. Phương án đối chứng phân biệt nguyên nhân — thiết kế hai lớp, chưa cấp quyền chạy

### D1 — `FIXED_CHECKPOINT_FACT_SENSITIVITY_VS_ROLLOUT_DIAGNOSTIC` (ưu tiên thiết kế)

**Mục tiêu:** xác định liệu mô hình vốn có xác suất có điều kiện ưu tiên hành động gắn đúng fact nhưng không triển khai được khi free-running, hay cả tín hiệu conditional preference cũng yếu. D1 là **đánh giá checkpoint cũ**, không train mới, không thay P02, BPE hay TEST. Đề xuất sử dụng các prompt DEV chưa tiêu thụ từ kho đã có nếu phù hợp hợp đồng riêng và tạo **một tập DEV cặp phản thực mới tiền đăng ký trước khi chạy**; không dùng lại FRESH16/FRESH12/CF1/Q1Q2/TEST hoặc 24 FINAL blind của AC làm sân thử. Các tệp AC DEV12 hiện có *có thể* dùng để phân tích định dạng, **không tự coi là bộ pair có khả năng nhận dạng nhân quả**.

**Ứng viên cấu trúc tối thiểu để đóng băng ở bước kế tiếp, không phải quyết định số liệu/hypothesis mới:** 4 category × 4 independently worded pair families = **16 cặp mới** (32 facts/prompt variants); đối xứng điều kiện, cân bằng tên, thứ tự, độ dài ứng viên và nguồn, cố định mỗi cặp chỉ đổi một fact trung tâm. Đơn vị phân tích = **cặp**, không 32 ví dụ độc lập. Các đối chứng phải bao gồm:
1. **Counterfactual teacher-forced preference:** cùng prompt A/B, hai continuation candidates phù hợp A/B với action/actor/recipient/patient xác định trước; đo cả raw total log-likelihood, length-normalized và lexical-prior-adjusted score, tránh thiên vị completion y như CF1. Đòi hai dấu margin đúng: `m_A = log P(y_A|x_A) − log P(y_B|x_A) > 0` và `m_B = log P(y_B|x_B) − log P(y_A|x_B) > 0`; report paired switches, sign và bootstrap CI theo family. Cân bằng lexical tokens, không chỉ đọc một score kiểu label letter A/B. Đây là khả năng **phân biệt lựa chọn ứng viên**, không phải suy luận tự do.
2. **Context robustness:** mỗi cặp tạo phiên bản short và long trong 256 token, facts và targets bất biến; filler/độ xa/cue-position được counterbalance, không overflow; đối chiếu giảm margin và adherence trên **cùng family**. Nếu short+pass, long+fail một cách hệ thống -> context-use/distance đáng ưu tiên; nếu đều fail -> chưa thể quy cho độ dài.
3. **Free-running decoder contrast:** cùng frozen checkpoint/prompt exact bytes, greedy 64 token so với nucleus `top-p=0.9, temperature=0.8` theo **ba seed công khai, cố định trước** (các tham số là ứng viên chứ chưa phải phép thử thực thi). Giữ cùng ngân sách token/context, log EOS, repetition, actor/object/goal và score độc lập không biết decoder. Một kết quả sampling may mắn không được xem là causal success chung; báo paired distributions/cost.
4. **Cắt trạng thái tại slot vs sau rollout:** lưu logits tại điểm bắt đầu sinh và diễn biến theo bước, đối chiếu factual first-action preference với việc trôi ngữ cảnh sau khi mô hình tự tiếp nối; phân biệt preference đầu không có và drift sau vài token. Không đọc TEST và không sửa checkpoint.

**Diễn giải dự kiến đã đặt trước (falsification oriented):**

| D1 quan sát tương lai | Điều nên ưu tiên tiếp | Điều *chưa* đủ chứng minh |
|---|---|---|
| Cả hai counterfactual margins đúng, greedy fail nhưng stochastic nhiều seed giúp tăng adherence có hệ thống | Decoder/rollout đáng nghiên cứu trước khi train | Sampling không đồng nghĩa reasoning nhân quả |
| Margins đúng ở short và suy giảm ở long, không overflow | Khả năng dùng cue / distance có hiệu ứng, kiểm position stress | Không thể tuyên bố attention architecture fail |
| Margins không phản ứng đúng ở short **và** long, greedy/sampling đều yếu | Thiếu fact-conditioning là vấn đề trước decoder; xem nhánh training A/C/2×2 | Không phân biệt thiếu data vs loss vs model capacity |
| Conditional preference đổi đúng, nhưng free outputs chỉ cloze hoặc lệch goal | Giao diện giữa xác suất câu đúng và sinh tiến trình, thử mục tiêu/event supervision (design sau) | Không tự kết luận loss vị trí là nguyên nhân |
| Chỉ đổi format whitespace làm từ đầu phù hợp hơn, vẫn không tạo event mới | Lexical serialization effect; giữ nguyên verdict ngữ nghĩa | Không gọi đây là quality rescue |

**Tiêu chí khóa D1 trước khi chạy:** novelty đối với historical prompts, exact source pins, split independent from TEST/Q1Q2/AC FINAL24, prompt/answer semantic audit trước sinh, token lengths/overflow=0, matched candidate BPE budgets, fixed seeds/decoders, pre-declared score fields, paired bootstrap by family, independent rater custody và single owner GO. D1 hiện ở `DESIGN_ONLY_NOT_PREREGISTERED_NOT_EXECUTED`; không tạo ngay prompts, không tự động cấp phép. Độ rộng 16 family chỉ cho suy luận khám phá có sai số; **không hứa causal identification mức tổng quát hoặc statistical power xác nhận**.

### D2 — `EXISTING_AC_A_C_THEN_OPTIONAL_2X2` (chỉ khi D1 không xác định được decoder/context effect)

Không xây từ đầu: sử dụng thiết kế huấn luyện đã có trên nhánh `research/ttm-small4m-prompt-conditioning-objective-design-20261110`, HEAD đối chiếu `837289fda82b41653a61b74e476f76a0b4c4137c`.

- **A/C đang có:** parent checkpoint T4 bước1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, 128 optimizer steps/arm × 4096 target labels = 524.288 lượt nhãn/arm; A uniform CE, C suffix-weighted CE (index≥32 trọng số 3, trước đó 1), cùng replay draws. So sánh `C−A` chỉ kiểm can thiệp **trọng số mục tiêu theo vị trí**; không trộn với FRESH16 H1/H2.
- **B/D trong 2×2:** first-story-window replacement, matching target count; `B−A`, `D−C` tương phản chính sách dữ liệu, `C−A`, `D−B` hiệu ứng loss, tương tác `(D−B)−(C−A)`. Cần toàn bộ lịch matched draws và đánh giá mù mới trước khi mở B/D. Việc tăng first-window không đo hiệu ứng corpus coverage/size riêng rẽ; số story phân biệt và gradients phải được báo, không nói “cùng số nhãn = cùng thông tin”.
- **Đánh giá AC đang chuẩn bị:** DEV12 / FINAL24, candidate gate cải thiện adherence mean≥0.5/3, ≥16/24 thắng nghiêm ngặt, lower paired bootstrap >0, VAL NLL regression≤5%, coherence/consistency không giảm quá 0.25. Đây là **quy tắc ứng viên của AC**, không phải kết quả đã PASS hoặc phép cộng của FRESH16.
- **Điều kiện HOLD AC hiện hành:** owner private-pack rights, secret escrow owner custody, independent rater, Windows Python312/native readback, T4 fp16 zero-step và interrupted-resume parity, một science GO. Theo receipt `TTM_SMALL4M_AC_FINAL_PREEXEC_SINGLE_DECISION_AND_SOURCE_READBACK_20261111.json`, `NO_GO_PREEXEC_EXTERNAL_AND_NATIVE_GATES_OPEN`; **không tự nâng lên READY/GO** từ báo cáo này. FRESH16 FAIL không tự cấp phép thực thi AC.

### D3 — capacity/architecture (DEFER)

Chỉ xét nếu D1 cho thấy thiếu conditional signal và D2 không cho cải thiện có điều kiện trong khi quyền/compute đủ. Muốn phân biệt capacity phải giữ data, objective, token budget, evaluations, seeds và đo compute/memory; không so checkpoint step1280 lịch sử với mô hình mới như thể matched control. Không có cơ sở ngay để triển khai MoE, attention mới, O1, hay train lớn trên máy dev. Không dùng kết quả khác (EmbeddingGemma2/SIX/T5) làm đối chứng trực tiếp.

## 4. Quyết định GO/HOLD một lần, không micro-permit

- **`GO_NEXT_CAUSAL_DIAGNOSTIC_DESIGN_ONLY`**: câu hỏi khoa học kế nhiệm có sức phân biệt tốt nhất là **conditional fact-preference vs free rollout/decoding** trên checkpoint gốc với DEV mới, không giả định nguyên nhân trước khi đo. Đây là lựa chọn **hướng nghiên cứu** và thiết kế, **không** phải GO chạy một batch token mới.
- **`HOLD_ALL_NEW_SCIENCE_EXECUTION`**: D1 chưa có protocol/prompt/owner-run-lock cụ thể; **`NO_NEW_INFERENCE`**, `NO_NEW_TRAINING`, `GPU_NO` trong lượt này.
- **`HOLD_SUCCESSOR_TRAINING`**: AC A/C đã có nhưng còn `NO_GO_PREEXEC`; B/D chỉ thiết kế; không cấp phép train từ FRESH16 FAIL.
- **`O1_MOE_ATTENTION_CAPACITY_UPGRADE=DEFER`**; không có phép đối chứng đã chạy để chọn thay kiến trúc.
- Giữ tất cả verdict T4 VAL/TEST, FRESH12, CF1, FRESH16 bất biến. TEST và Q1Q2 đã tiêu thụ/giữ nguyên trạng thái tương ứng; không tái mở. Không append `lineage.md` vì đây là thiết kế, không có kết quả PASS/FAIL khoa học mới. Không merge, không cleanup worktree.

**Bước thực hiện tiếp theo (một gói duy nhất):** `TTM_SMALL4M_D1_FIXED_CHECKPOINT_FACT_CONDITIONING_VS_DECODING_NEW_DEV_SINGLE_FROZEN_DESIGN_OWNER_GO_HOLD` — soạn một hợp đồng D1 đầy đủ có candidates/counterbalancing, nguồn mới không lộ TEST, ngưỡng phân tích, chi phí và single owner GO/HOLD; **không thực thi science cho tới quyết định riêng**. Nếu owner ưu tiên huấn luyện thay D1, dùng nguyên A/C hiện hành và đóng các điều kiện còn thiếu trong *một* owner review, không thêm toy hay micro-permit.
