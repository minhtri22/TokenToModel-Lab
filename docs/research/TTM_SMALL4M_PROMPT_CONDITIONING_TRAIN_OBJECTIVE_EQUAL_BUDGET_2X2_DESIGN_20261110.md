# TTM-Small-4M — Phân tích nguyên nhân bám prompt yếu và thiết kế ablation ngang ngân sách

**Task:** `TTM_SMALL4M_PROMPT_CONDITIONING_TRAIN_OBJECTIVE_ROOT_CAUSE_AND_EQUAL_BUDGET_ABLATION_DESIGN`  
**Ngày:** 2026-11-10 · **Mức hoàn thành:** `DESIGN_ONLY_NOT_SCIENCE_PREREG_APPROVED`  
**Repository:** `minhtri22/TokenToModel-Lab` · **nhánh nghiên cứu riêng từ main** `research/ttm-small4m-prompt-conditioning-objective-design-20261110`  
**Main ghim (đọc thực tế):** `b57b44e7287f842e81050c1faee337f636333dd0`  
**PR #13 đánh giá FRESH12 (đọc thực tế):** `8399406cfca7855626a20e031d1cfb3c767d606f` — OPEN / DRAFT / UNMERGED.

**Trạng thái cổng:** Chỉ thiết kế trên GitHub. Không chạy huấn luyện, không tạo dữ liệu TRAIN mới, không sửa tokenizer/architecture/checkpoint, không sinh thêm văn bản, không đọc TEST/Q1Q2, không chỉnh `main`/`lineage.md`. Đây **chưa phải** tiền đăng ký huấn luyện được chủ dự án phê duyệt; thông số candidate cần source QA, quyền nguồn, reviewer và quyết định tài nguyên riêng trước khoa học.

## 1. Nguồn gốc — sự kiện đã đo khác với giả thuyết

### 1.1 Sự kiện trên nguồn GitHub

- `src/p02/transformer_core.py` Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; T4 config `vocab_size=2048`, `max_seq_len=256`, `n_embd=256`, `n_layer=4`, `n_head=4`, `norm_type=layernorm`, **3.749.376 trainable params**.
- `tools/pilot_t4/integrated/t4_data_pack.py` Git blob `cdce219f2a2df27e25579f069238d4327c1d7d91` cắt từng truyện thành các cửa sổ độc lập tối đa 256 nhãn; `x=tokens[:-1]`, `y=tokens[1:]`, `-100` là padding không tính loss, EOS cuối mỗi truyện, không nối truyện.
- `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py` Git blob `76c4d0155cd0736919f41682f240b47ad3d7c428`: `AdamW`, `cross_entropy(ignore_index=-100, reduction='sum')/4096`, **4.096 nhãn thực/bước**. Sampler chọn cửa sổ ngẫu nhiên, **không đặt supervision riêng cho giữ nhân vật, đồ vật, mục tiêu hay tính nhân quả**.
- TRAIN/VAL private pack SHA-256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; 2.048 truyện TRAIN, 2.691 cửa sổ, 498.287 nhãn TRAIN riêng trong pack; 1.280 × 4.096 = **5.242.880** token-target exposures (tỷ số 10,52×, không phải epoch chính xác). Không công khai token pack.
- `tools/pilot_t4/original_1024to1280_20261109/ttm_t4_original_1024_to1280.py` Git blob `1f539aedd04d7097f2cb26b0220b14bd106c8b65`. Lượt gốc 1024→1280 **đã tiêu thụ**, giữ optimizer/scheduler/sampler, LR tại floor `3e-5`; không chạy lại one-shot cũ. 1024 SHA `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; 1280 SHA `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`.
- [Root-cause readonly report trên PR13](https://github.com/minhtri22/TokenToModel-Lab/blob/8399406cfca7855626a20e031d1cfb3c767d606f/docs/pilot/ttm-small4m-source-of-truth/TTM_SMALL4M_PROMPT_ADHERENCE_ROOT_CAUSE_READONLY_DIAGNOSTIC_20261109.md): prompt trailing ASCII space làm token đầu nghiêng sang `\n`; đối chiếu P02 CPU 16 ngữ cảnh/checkpoint exact match. Đây là confound định dạng, **không** là lỗi tokenizer/nhãn huấn luyện đã chứng minh.
- [FRESH12 owner-scoped adjudication](https://github.com/minhtri22/TokenToModel-Lab/blob/8399406cfca7855626a20e031d1cfb3c767d606f/docs/pilot/ttm-small4m-source-of-truth/TTM_FRESH12_OWNER_CONTROLLED_UNBLIND_AND_SCOPED_QUALITY_ADJUDICATION_20261110.md): Codex AI chấm 48 đoạn/24 cặp, **35/48** bám prompt = 0, `trimmed−baseline` adherence **0,000/3**, CI95 mô tả [−0,208; +0,167]. `SEMANTIC_GAIN=NO_DEMONSTRATED_SCOPED`, không kết luận tuyệt đối tương đương hoặc xác nhận độc lập bằng con người.

### 1.2 Giả thuyết CHƯA kiểm định nhân quả

| ID | Giả thuyết | Bằng chứng hỗ trợ hiện có | Điều chưa biết |
|---|---|---|---|
| H-DATA | Tần suất mẫu và cơ chế chọn cửa sổ khiến mô hình ít học quan hệ tình huống từ đầu truyện | 2.691 cửa sổ được lấy mẫu; không có sampling ưu tiên đầu truyện | Đổi phân bố đầu truyện có cải thiện giữ nhân vật/mục tiêu không? |
| H-LOSS | Cross-entropy đồng đều trên mọi vị trí chưa đủ nhấn mạnh phần tiếp nối có điều kiện | Chỉ next-token CE, không supervision nhiệm vụ; điểm FRESH12 thấp | Tăng trọng số suffix giúp conditional continuation không? |
| H-COVERAGE | Từ vựng/nhân vật/tình huống prompt mới ít trùng dạng TRAIN | 5 tên nhân vật riêng ở 8 prompt cũ không hiện diện trong TRAIN-only exact-word audit | Cần đo độ phủ theo cấu trúc/quan hệ, không suy từ tần suất tên riêng |
| H-CAPACITY | 3,75M tham số, context 256, số truyện ít có thể là giới hạn | T4 VAL NLL giảm nhưng chất lượng sinh yếu | Chưa thể tách capacity khỏi data/objective bằng các thử nghiệm đã có |
| H-FORMAT | Dấu cách cuối prompt ảnh hưởng token đầu mạnh nhưng không quyết định bám ngữ nghĩa | Root-cause và FRESH12 có kết quả khác nhau theo metric | Không tái dùng FRESH12 để tune hoặc chứng minh can thiệp mới |

**Không khẳng định H-DATA/H-LOSS/H-COVERAGE/H-CAPACITY là nguyên nhân đã được chứng minh.** Đặc biệt, `next-token` là mục tiêu chung hợp lệ để học mô hình ngôn ngữ; việc mô hình hiện tại không bám prompt có thể do nhiều yếu tố đan xen, không suy ra bản thân cross-entropy là sai.

## 2. Thử nghiệm tối thiểu đề nghị: 2 × 2 factor (DESIGN ONLY)

**Mục tiêu:** tách **cách chọn mẫu (data selection)** khỏi **phân bổ trọng số loss (objective emphasis)**; kiểm tra tương tác của hai thay đổi. Không tạo token mới hoặc thêm nhãn semantic thủ công trong lần này. Đây là **proxy continuation**, chưa phải instruction fine-tuning/P10.

| Arm | TRAIN window selection | Loss trong cùng 256 token | Câu hỏi khoa học |
|---|---|---|---|
| **A — baseline** | Replay sampler gốc từ checkpoint 1024 | CE đều cho mọi target hợp lệ | Đối chứng huấn luyện tiếp đúng budget mới |
| **B — DATA** | Thay từng cửa sổ bằng **cửa sổ đầu của truyện**, match số target hợp lệ | CE đều | Ưu tiên ngữ cảnh đầu truyện có lợi không? |
| **C — OBJECTIVE** | Chính xác window IDs/count/ordering như A | CE có trọng số: vị trí 0–31 = 1, từ vị trí 32 = **3**, chuẩn hóa tổng trọng số | Tập trung vào đoạn tiếp nối trong cửa sổ có lợi không? |
| **D — DATA + OBJECTIVE** | Chính xác window IDs/count/ordering như B | Cùng weighting như C | Có tương tác hoặc triệt tiêu không? |

**Tránh tự diễn giải:** Hệ số 1:3 theo vị trí token chỉ kiểm tra *suffix-position emphasis*, **không đồng nghĩa** giám sát giữ nhân vật hoặc mục tiêu nhân quả. Sau khi có kết quả mới mới quyết định có đáng thiết kế cặp `(nhân vật, đồ vật, mục tiêu) → tiếp nối` đã gắn nhãn từ nguồn được phép. Không giả định B hay D thay đổi số lượng truyện TRAIN gốc.

### 2.1 Ngân sách và khởi tạo ngang bằng

- **Chung checkpoint khởi đầu:** bản `step_1024` original đã khóa, **clone payload/optimizer/scheduler/sampler/RNG/scaler sang vùng chạy RIÊNG cho từng arm**, không bao giờ write-back checkpoint gốc. Không lấy `step_1280` lịch sử làm arm A: nó có **256 bước** và lịch sử đã thực thi khác.
- **Mỗi arm:** 128 optimizer steps **1025–1152**, 4.096 target hợp lệ/bước → **524.288 target exposures/arm**. **Bốn arm tổng cộng 2.097.152 exposures**. Đây là **đề xuất tối thiểu**, chưa được phê duyệt GPU.
- Cùng 3.749.376 weights khởi đầu, source P02/blob, BPE2048, context256, optimizer AdamW với state gốc, LR floor 3e-5 và scheduler state gốc, precision FP16, microbatch_windows=8 (nếu mọi kiểm tra checkpoint/môi trường phù hợp). Không reset optimizer, RNG hoặc reinitialize embedding cho mỗi arm. Cùng môi trường T4 Free và checkpoint READY-last, run IDs bất biến của từng arm khi thực thi sau này.
- **Kế hoạch lấy mẫu (step draw schedule):** trên CPU, chỉ sau science authorization, tạo `A/C` IDs/counts cho từng step **từ trạng thái sampler sao của step1024**, giữ nguyên 4.096 scored target labels/bước như mã `sample_exact_step`. `B/D` dùng **cùng số cửa sổ và vector target-count theo thứ tự** của A/C; thay từng chọn lựa bằng một **first-story window** có `count >= n`, do thuật toán sắp thứ tự SHA-256 theo `(seed, step, draw_index, candidate)`, và mask phần sau `n`; không chọn TEST/VAL, không cross-story stitch. Nếu bất kỳ vị trí nào không có ứng viên đủ dài, `MATCHING_FEASIBILITY=FAIL/HOLD`, không tự nới ngưỡng.
- Vì tensor đầu vào **đều [windows,256]**, số cửa sổ theo microbatch và số nhãn `n` mỗi bước bằng nhau, các arm có **cùng budget forward token slots và cùng 4.096 scored labels**. Arm C/D reweight nonzero loss, do đó **effective weighted contribution khác** — đó là tác động cần kiểm nghiệm. Tất cả 4 đều phải log actual FLOP estimate, GPU seconds, peak VRAM và batch IDs; không nói thời gian thực hay điện năng giống hệt.
- Loss weighted mỗi optimizer step: `L = (Σ_valid w_i * CE_i) / Σ_valid w_i`. Đối với A/B, `w_i=1`; đối với C/D, `w_i=1` khi `position<32`, ngược lại 3. Tất cả nhãn hợp lệ được tính **một lần trong mỗi lần rút cửa sổ**, không loại bỏ target nào. Chuẩn hóa ở **cả optimizer step**, không trung bình độc lập từng microbatch rồi cộng (sẽ gây lệch theo kích thước microbatch). `-100` phải luôn có weight=0.
- Dữ liệu gốc có 2.048 **first-story windows** trên 2.691 cửa sổ (**~76,1%** cửa sổ là đầu truyện) nên B/D chỉ thay đổi khoảng 24% cửa sổ phân loại nếu nhìn theo số window, nhưng vẫn có thể thay đổi tần suất/cấu trúc mục tiêu. Báo cáo **tỷ lệ first-story actual, số truyện độc nhất được rút, entropies, duplication ratio và số target IDs thực**, tránh coi đây là thay đổi dữ liệu lớn.
- **Caveat:** chỉ có 1 parent checkpoint và 1 science seed → nếu 4 arm sau này đạt PASS một lần, chỉ được `EXPLORATORY_CANDIDATE`, không phải xác nhận thống kê về mọi seed/model size. LR rất thấp (3e-5) sau 1024; tác dụng có thể nhỏ. Nghiên cứu này chủ yếu kiểm tra **khả năng sửa bằng 128 bước tiếp nối** chứ không chứng minh huấn luyện từ đầu đã tối ưu.

### 2.2 Ranh giới công bằng

A vs C: **cùng dữ liệu, token IDs, order và target counts**, chỉ khác weighting.  
A vs B: **cùng budget, shape, số lượt xử lý**, nhưng phân phối câu chuyện khác theo thiết kế; đó là tác động của data selection.  
C vs D: thêm thay đổi data trong cùng objective.  
B vs D: thêm thay đổi objective trong cùng data.  
Factorial interaction: `(D−B)−(C−A)` theo **cùng metric**; không dùng `D−A` một mình để quy hết lợi ích cho loss hoặc data.

Nếu dùng synthetic fixture đầu vào nhiều cửa sổ, kiểm negative: thiếu ứng viên first-window, target-count mismatch, window mang nhãn TEST/VAL, thay source SHA, token ID ngoài vocab, source window không liên tiếp phải **FAIL_CLOSED**.

## 3. Đánh giá chất lượng — không tái dùng FRESH12 như tập xác nhận

- **Trước mọi training:** tạo bộ **12 DEV prompt mới + 24 BLIND_FINAL prompt mới** (tất cả được biên soạn từ nguồn riêng và không đọc TEST/Q1Q2), SHA-256, trường nhân vật/đồ vật/mục tiêu tham chiếu gốc; kiểm khác P01–P08, F01–F12, exact/near-duplicate giữa DEV và BLIND_FINAL. Nếu chưa thể kiểm Q1/Q2 đã niêm phong, nói rõ phạm vi novelty.
- FRESH12 đã tiêu thụ làm cơ sở hình thành giả thuyết, **không được dùng chọn arm/threshold sau thực nghiệm**. `BLIND_FINAL` là holdout mới trong **nghiên cứu kế nhiệm**, **không** phải việc mở tập TEST gốc của T4.
- Giữ prompt format **không trailing ASCII space** nhất quán cho mọi arm; greedy 64 tokens/EOS theo FRESH12. Không đưa condition/arm/model label vào packet. Xếp 4 văn bản trên mỗi prompt theo Latin-square balanced 24 prompt (6 prompt/4 vị trí cho mỗi arm), seed/ánh xạ tách reviewer.
- **Chính:** điểm bám prompt 0–3, `mean(Arm−A)` trên 24 cụm BLIND_FINAL; phụ: mạch lạc, nhất quán, mất/lặp nhân vật-đồ vật-mục tiêu, tỷ lệ EOS sớm, 3-gram repetition, tỷ lệ xuống dòng đầu; không thay metric hậu nghiệm.
- **An toàn chất lượng:** VAL NLL trên đúng 256 truyện VAL và BPE đã khóa; so tương đối với Arm A; bootstrap theo **truyện**, không theo token; theo dõi khác biệt VAL NLL từng arm, train divergence. VAL không dùng để đổi hyperparameter trong một batch đã khóa. Tập TEST gốc không đọc/sinh/đánh giá.
- **Candidate gate đề nghị (chưa owner-freeze):** Arm X cải thiện `mean adherence ≥ +0,5/3` so với A; X thắng rõ adherence **≥16/24 prompt**; bootstrap CI95 theo 24 prompt có lower >0; VAL NLL regression không vượt **+5%** so với A; coherence và consistency không giảm quá 0,25/3. Đây là ngưỡng ứng viên chủ dự án cần xác nhận **trước** khi xem BLIND_FINAL; không được nới sau kết quả.
- Đánh giá tối thiểu từ **một reviewer AI độc lập theo phạm vi** + biên nhận khóa trước giải mù. Tốt hơn có một human rater thứ hai. Không gọi organizational independence nếu không có bằng chứng; reviewer nhất thiết không phải người tạo prompt, điều khiển training hoặc biết arm mapping.
- Một lần đào tạo/đánh giá được phê duyệt khi có science lock; nếu fail do hạ tầng, lưu FAIL đúng run, không rerun một-shot dưới tên cũ. Nếu fail ngưỡng, ghi `NO_DEMONSTRATED_GAIN_SCOPED` không thay corpus để cứu.

## 4. Những câu hỏi chẩn đoán riêng — không thêm GPU khi chưa cần

1. **TRAIN-only lexical/semantic coverage audit:** thống kê phân phối độ dài truyện, số context windows per story, first-window fraction, EOS, số prompt-anchor tokens có/không trong TRAIN (chỉ số tổng hợp). Dùng source/manifest riêng tư nhưng **không xuất raw văn bản lên GitHub**; không mở TEST.
2. **Boundary/label QA:** kiểm thống nhất `x/y` shift, mask `-100`, `windows_for_ids` không nối story, không drop continuation sau pad; kiểm lại bằng fixture, tránh ghi là lỗi đã tìm được khi chưa có.
3. **Sampling feasibility:** chứng minh B/D có thể match đầy đủ `n` cho mọi window trong kế hoạch A/C, không thay số lượt forward, đánh giá cấu trúc coverage; nếu không, sửa thiết kế trước science lock bằng amendment công khai.
4. **Objective semantics caveat:** xác định liệu suffix-position weighting có thực sự làm tăng gradient ở các phần giữ nhân vật/mục tiêu hay không. Nếu không, lựa chọn nghiên cứu kế nhiệm dùng **mẫu chuyện/continuation cặp rõ nghĩa có nguồn được phép**, không suy diễn từ dữ liệu chưa được gắn nhãn.

## 5. Quyền nguồn, QA, nhân lực và quyết định mở science

| Gate | Yêu cầu | Trạng thái hiện tại |
|---|---|---|
| DATA_RIGHTS | Kiểm lại quyền tính toán, yêu cầu attribution và mọi điều kiện tái sử dụng TinyStories train/valid; không dùng WP30/P01 F1 để train GPT | `DESIGN_HOLD_REVIEW_REQUIRED` |
| SOURCE_PIN | Mọi Git blob, checkpoint, TRAIN/VAL pack SHA, tokenizer merge SHA và dữ liệu split phải khớp chính xác; mọi input trong repo/Drive có nguyên gốc | `DESIGN_REFERENCES_PINNED_NOT_RUNTIME_AUDITED` |
| MATCHED_DRAW_PLAN | 128 × 4.096 target / arm, vector `n`, số forward windows và batch-size giống từng bước | `NOT_IMPLEMENTED_NO_DRAW_PLAN` |
| LOSS_QA | Fixed-fixture CE và weighted CE, denominator theo step, không gradient ở pad, reset states | `NOT_IMPLEMENTED` |
| FAIRNESS | Cùng initial model + optimizer/scheduler/scaler/RNG, cùng GPU precision, 128 steps, target counts, token slots | `DESIGN_SPECIFIED_NOT_EXECUTED` |
| EVAL_BOUNDS | 12 DEV + 24 FINAL prompt hoàn toàn mới, khóa rubric/rater/latin-square/threshold trước train | `NOT_CREATED` |
| SCIENCE_APPROVAL | Một batch research mới, owner explicit approval sau QA/source rights/Colab capacity; không tái sử dụng authorization 1024→1280 | `NOT_GRANTED` |
| P09_P10 | P09 scaling và P10 instruction training **chưa được mở**; đây chỉ là nghiên cứu pilot T4 | `NOT_OPENED` |

**Bằng chứng phải ở GitHub**: bản hợp đồng design, machine-readable arm matrix, source SHA pins, smoke QA reports và mọi PASS/FAIL thực tế. Checkpoints, token pack, raw eval và key A/B giữ riêng với SHA trên GitHub, không commit vào repository public. `lineage.md` append-only chỉ khi có khoa học PASS/FAIL formal và được adjudicate đúng, không ghi QA design.

## 6. Mốc kết thúc và công việc tiếp theo

**Lượt này đóng khi**: nguồn GitHub đối chiếu PASS, tạo nhánh độc lập từ `main`, bản thiết kế 2×2 có budget/causal contrast và dữ liệu quyền được mô tả, machine-readable candidate và kiểm tra tĩnh được commit/read-back. **Không** coi design QA là learning/semantic PASS.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_2X2_EQUAL_BUDGET_TRAIN_SAMPLER_LOSS_SYNTHETIC_PREFLIGHT_AND_OWNER_FREEZE`. Triển khai và kiểm định riêng **synthetic source-only** cho kế hoạch rút cửa sổ/masking/weighted loss/đối chiếu bytes và test negative; xác nhận quyền nguồn, ngưỡng và người chấm. Sau khi các cổng đủ PASS và chủ dự án phê duyệt mới được nghĩ tới **một** lượt Colab Free T4 mới theo run IDs hoàn toàn khác.

**Trạng thái:** `DESIGN_ONLY` · `NEW_TRAINING=NO` · `NEW_INFERENCE=NO` · `TRAIN_DATA=UNCHANGED` · `TEST_Q1Q2=UNTOUCHED` · `PR13=HOLD_DRAFT` · `MAIN=UNCHANGED` · `LINEAGE=L0017_UNCHANGED`.
