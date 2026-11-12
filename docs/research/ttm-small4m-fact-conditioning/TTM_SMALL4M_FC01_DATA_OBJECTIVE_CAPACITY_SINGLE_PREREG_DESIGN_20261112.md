# FC01 — TTM-Small-4M: Học điều kiện hóa dữ kiện bằng dữ liệu phản thực và mục tiêu huấn luyện

**Operation:** TTM_SMALL4M_FACT_CONDITIONING_DATA_OBJECTIVE_CAPACITY_SINGLE_RESEARCH_DESIGN  
**Ngày thiết kế:** 12/11/2026  
**Dự án:** minhtri22/TokenToModel-Lab · TTM-Small-4M / P02 3.749.376 tham số  
**Loại:** Thiết kế thí nghiệm khám phá có đối chứng (controlled exploratory design); không phải điều chỉnh D1 confirmatory  
**Quyết định:** DESIGN_FROZEN_SCOPED · TRAINING_NOT_AUTHORIZED · DATA_BYTES_NOT_FROZEN · SCIENCE_NOT_EXECUTED

## 0. Căn cứ đã được phân xử, không tính lại

- DEV32 đã đóng: CLOSED_EXPLORATORY_SCOPED_PROVISIONAL_INPUT_PROVENANCE. Teacher-forced cả hai điều kiện đúng S=1/16; prior-adjusted S'=2/16.
- Hai bộ đầu ra 32 greedy và 32 nucleus đều có **0/32** điểm tuân thủ dữ kiện ≥2. Nucleus có ít cửa sổ 3-token lặp và nhiều điểm 1 hơn, nhưng không cứu điểm ≥2.
- Rater GPT-6 đã chấm 64/64, điểm và SHA được xác minh; 64/64 ID đúng. Tuy nhiên, **nội dung input dán trong phiên chấm không được chứng nhận byte-identical** với BLIND64. Kết quả vẫn chỉ exploratory/provisional.
- Checkpoint **step1024** SHA-256 \`cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b\`; tokenizer T1 BPE2048 manifest SHA-256 \`cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc\`; P02 Git blob \`9762343e06cf800b50574c2871ae1ed58537fb18\`, context 256.
- **KHÔNG** chạy lại DEV32, không chấm lại, không chọn seed khác, không tái sử dụng DEV32 như tập điều chỉnh hyperparameter. **KHÔNG** mở D1 512, TEST/Q1Q2, FRESH16 private, source rater raw hoặc mapping. D1 confirmatory HOLD giữ nguyên.
- Kết quả DEV32 **không nhận dạng được nguyên nhân**. FC01 đưa ra một phép kiểm tra can thiệp mới, không gắn nhãn data/objective/capacity đã là nguyên nhân.

## 1. Câu hỏi và giả thuyết phân biệt

**Câu hỏi chính:** Khi giữ nguyên mô hình P02, checkpoint ban đầu, tokenizer, số update và số token huấn luyện, liệu (a) **độ phủ cặp phản thực A/B trong dữ liệu** và (b) **mục tiêu huấn luyện phân biệt đáp án** có tăng độ nhạy lựa chọn hành động theo dữ kiện ở *nhóm gia đình mới chưa thấy*?

**H_D (data intervention):** đưa cả hai biến thể A/B của cùng family vào 25% dữ liệu bổ trợ giúp tăng tỷ lệ chọn cả hai ứng viên đúng so với dữ liệu singleton có phân phối nhãn và số token tương đương.

**H_O (objective intervention):** trên **cùng dữ liệu A/B** và thứ tự batch, thêm contrastive answer-choice objective giúp tăng lựa chọn đúng so với next-token objective đơn thuần.

**H_CAP (capacity, nghiên cứu sau có điều kiện):** nếu các kiểm tra H_D/H_O không đủ, đề xuất so sánh dung lượng mô hình với *pretraining exposure* tương đương. **KHÔNG tạo, huấn luyện hay đánh giá mô hình lớn trong FC01.**

Không giả định một trong ba giả thuyết đúng. Hiệu ứng objective có thể phản ánh supervision có định hướng hơn cũng như hình thức loss; không gọi đó là thay đổi objective hoàn toàn không tăng thông tin gradient.

## 2. Ba nhánh huấn luyện — duy nhất một nghiên cứu có đối chứng

Cả ba nhánh đều tiếp tục **từ đúng cùng checkpoint step1024**, cùng P02 ~3,75M, vocab 2048, context 256, optimizer reset cùng cấu hình và số bước. Không tiếp tục huấn luyện tuần tự A → B → C.

| Nhánh | 75% core TinyStories | 25% tập bổ trợ mới | Objective | Phép đối chiếu |
|---|---|---|---|---|
| **A / BASE_MLE** | Chung, thứ tự giống nhau | D0: singleton cân bằng A/B; hai paraphrase của một điều kiện/family | Next-token CE | Đối chứng |
| **B / CF_MLE** | Chung, thứ tự giống A | D1: cặp A và B cùng family, hai văn phong tương ứng | Next-token CE | B − A: độ phủ phản thực |
| **C / CF_CONTRAST** | Chung, thứ tự giống A/B | **Đúng cùng byte D1, schedule và target như B** | Next-token CE + fact-choice contrastive | C − B: objective |

**D0/D1 được xây từ cùng tập 256 family TRAIN**, cân bằng 4 category: 64 family/category. D0 trong mỗi family chứa 2 bài paraphrase với **cùng** một fact; 128 family dùng A, 128 dùng B, cân bằng trong từng category. D1 trong mỗi family có 1 bài fact A và 1 bài fact B, cùng mẫu paraphrase đã khóa. Mỗi nhánh 512 bài task; tổng số A/B ở **cấp corpus** cùng 256/256, nhưng D1 thêm sự đổi fact **trong family**. Đây là can thiệp vào *within-family counterfactual coverage*, không phải giữ nguyên nội dung corpus. Các khác biệt về phrasing và redundancy còn có thể góp phần vào hiệu ứng dữ liệu; báo điều này trong phân xử.

B và C có **cùng byte văn bản, nhãn đúng, candidate đúng/sai, lịch batch, token và mọi tham số**. Candidate âm của C là continuation của biến thể đối nghịch đã có trong D1; không được sinh negative từ bên ngoài hoặc chọn hậu nghiệm.

**Model capacity** giữ cố định toàn bộ FC01. Mô hình lớn hơn nếu có chỉ là FC02 đề xuất riêng, không được coi là nhánh thứ tư đã cấp phép.

## 3. Nguồn dữ liệu, tách tập và bằng chứng quyền

**Nguồn common 75%:** TinyStories original TRAIN từ bộ gốc đã pin của TTM. Không dùng bản V2 hoặc TEST bí mật; trước khi thực thi bắt buộc xác nhận chính xác source SHA và phạm vi quyền sử dụng trong nghiên cứu. Dataset card upstream hiện công bố giấy phép CDLA-Sharing-1.0; điều này **không thay** cho kiểm tra provenance/điều kiện công bố của bản copy cục bộ. Chỉ TRAIN được dùng để cập nhật trọng số; validation không dùng train.

**Nguồn bổ trợ 25%:** family/câu chuyện tiếng Anh **mới** do owner tạo ra theo hợp đồng và quyền được xác nhận; không dùng lại family/tên/tình huống/văn bản hoặc mapping của D1, FRESH16, AC, CF1, Q1Q2, TEST; không đưa PII, bản quyền không đủ điều kiện. Tập source mới được chốt SHA trước training. Đổi một fact quyết định và đảo đúng hành động, giữ dài/loại từ/độ khó cân bằng.

**Split theo family và template lineage, trước khi tạo dataset train:**

| Split | Families | Phân bố (4 categories) | Mục đích |
|---|---:|---:|---|
| TRAIN | 256 | 64/category | Tạo D0 và D1 |
| VAL_FC01 | 64 | 16/category | QA và theo dõi, không chọn checkpoint hậu nghiệm |
| EVAL_FC01_HOLDOUT | 64 | 16/category | Khóa private trước training; chỉ mở scorer khi A/B/C đã hoàn tất và frozen |
| **Tổng** | **384** | **96/category** | Không overlap gia đình hoặc nguồn |

Mỗi family EVAL có fact A/B, 2 completions yA/yB và một neutral x0; mỗi completion ≤12 BPE, dài cặp cân bằng chính xác BPE; prompt+answer ≤256 BPE; phân phối độ dài/vị trí cue khóa trước training. Thay đổi duy nhất giữa fact A/B phải là fact quyết định và các sửa nối ngữ pháp bắt buộc, được log. Không để nhãn ẩn qua tên thực thể, vị trí candidate, định dạng, punctuation hoặc độ dài. EVAL không xuất ra chat rater trước khi score model đã khóa.

**Admission sources:** kiểm per-source SHA, quyền và PII, unique-family/group split, tính trùng normalized SHA, 5-gram và so khớp ngữ nghĩa trong phạm vi nguồn hợp pháp, kiểm leak với DEV32 public/scoped, FRESH16/CF1/AC và TEST/Q1Q2 **chỉ nếu chủ sở hữu đã có index niêm phong được phép đọc**. Không tự mở niêm phong vì FC01. Nếu không thể chứng minh nguồn holdout riêng sạch, ghi rõ \`GENERALIZATION_CLAIM=SCOPED_UNCERTIFIED\`, **không giả tạo chứng chỉ**.

## 4. Ngân sách tính toán cố định và đối xử công bằng

Đây là **trần thiết kế**, chưa có benchmark thời gian/VRAM thực tế.

| Tham số | Khóa đề xuất |
|---|---|
| Model đầu vào | P02 step1024 SHA cố định, 3.749.376 parameters, **3 nhánh độc lập** |
| Nền tảng | Google Colab **T4 miễn phí**, PyTorch FP32; không tự chuyển qua GPU trả phí |
| Steps mỗi nhánh | **256 optimizer updates**, không early-stop theo validation |
| Batch hiệu dụng | **16 sequence × 256 token**, accumulation 4 × microbatch 4 |
| Scheduler trong mỗi step | 12 sequence core TinyStories + 4 sequence synthetic |
| Token-slot mỗi nhánh | **1.048.576** = 256×16×256 (786.432 core + 262.144 synthetic) |
| Tổng ba nhánh | **768 updates**, **3.145.728 token-slot** LM; ghi riêng valid-target-token và padding |
| AdamW reset | lr 1e-4, betas 0.9/0.95, weight_decay 0.1, grad clip 1.0 |
| LR schedule | Warmup 16 updates, sau đó cosine tới 1e-5 ở step 256 |
| Randomness | Một TRAIN_SEED **20261112**, một BOOTSTRAP_SEED **20261113**, chọn trước run; không seed shopping |
| Numeric | FP32, cùng backend, Torch deterministic nếu có hỗ trợ, no stochastic autocast |
| Compute cap | **≤3 T4 GPU-hours tổng cộng**, hoặc thấp hơn nếu Free Colab không cho phép; không khởi chạy nếu dự tính không đủ |
| Monetary cap | **$0 trả phí**; không mua credits/upgrade để vượt gate |
| Disk persistence | Google Drive riêng nghiên cứu FC01, có checkpoint+optimizer+RNG+sampler cursor và SHA |
| Local Windows | Chỉ nhận về checkpoints/receipts sau nghiên cứu, không cần train lớn trên Arc GPU |

**Không thể đồng thời tuyên bố FLOPs và số token bằng nhau:** C dùng thêm forward/backward cho các candidate âm; token-slot next-token chính **bằng nhau**, nhưng compute thực tế C có thể lớn hơn. Phải báo GPU-seconds, FLOPs ước tính và số candidate-token phụ; kết luận objective mang giới hạn **TOKEN_MATCHED_NOT_FLOP_MATCHED**. Không được bớt steps của C sau khi xem kết quả để cân chi phí.

Với ba nhánh, artifact khoa học bao gồm checkpoint cuối **step256 của continuation**, không dùng best-VAL checkpoint; SHA kiểm model/optimizer/RNG. Lưu trạng thái tại 0/64/128/192/256 vào Drive theo atomic write + checksum, không nhân bản file thiếu kiểm soát. Ngắt Colab được phép **resume đúng cùng logical run** từ checkpoint có hash và exact RNG/order (không khởi chạy lại theo seed mới, không fork hay lựa checkpoint đẹp). Nếu mất custody/resume không tái lập, ghi \`INCOMPLETE\` thay vì chạy lại theo biến thể khác.

Nếu không có Free T4, thiếu dung lượng, CUDA/CPU version mismatch, source mismatch, không có quyền dữ liệu hoặc trần 3 GPU-hours không đủ theo preflight: \`HOLD_INFRA_OR_RIGHTS\`, không tự bypass.

## 5. Objective khóa trước run

Với các dữ liệu **chung** và task examples, hai nhánh A/B dùng masked token next-token cross entropy (CE). C dùng đúng CE của B cộng thêm term contrastive trên 4 synthetic sequences mỗi update.

Với prompt x và candidate đúng y+ / sai y-, định nghĩa \(\ell(y\mid x)\) là **mean log probability/token** theo teacher forcing trên toàn completion, không dùng logits của prompt hoặc generation sampling. Define \(\Delta=\ell(y+\mid x)-\ell(y-\mid x)\). Objective C:

\[
L_C=L_{\rm CE}+\lambda \frac{1}{K}\sum_{i=1}^{K}\operatorname{softplus}\left(-\frac{\Delta_i}{\tau}\right),
\quad \lambda=0.2,\quad\tau=1,\quad K=4.
\]

Tất cả arms có cùng LM contexts/answers và masking; gradient objective chỉ khác ở nhánh C. Candidate y- được lấy từ correct continuation của fact còn lại trong cùng family. Candidate lengths y+/y- bằng nhau theo BPE. Không label smoothing, không score thresholding sau quan sát. **Nếu loss không ổn định/NaN hoặc OOM**: không tự chỉnh \(\lambda\), batch, LR, seed; dừng và đánh dấu failure-infra của nhánh, không gọi science negative.

## 6. EVAL: outcome chính không phụ thuộc decoder

**Primary outcome:** 64 family EVAL_FC01, mỗi family có xA, xB, x0 và 2 completions yA/yB. Mỗi model chấm **64×6=384 candidate scores**, ba model tổng **1.152 scores**. Không sinh văn bản để xác định primary.

Tính từ logits checkpoint final step256:

\[
m_A = \ell(y_A\mid x_A)-\ell(y_B\mid x_A),\quad
m_B = \ell(y_B\mid x_B)-\ell(y_A\mid x_B).
\]

Primary family success = \(\mathbf 1[m_A>0\land m_B>0]\). \`S_ARM\` = tổng /64, không dùng token-level independence.

Neutral baseline \(d_0=\ell(y_A\mid x_0)-\ell(y_B\mid x_0)\); adjusted margins \(m'_A=m_A-d_0,\,m'_B=m_B+d_0\) báo secondary (không thay outcome sau khi xem).

**Estimands trước khóa EVAL:**
- **H_D:** \(\Delta_D=S_B-S_A\) (data effect trong phạm vi can thiệp).
- **H_O:** \(\Delta_O=S_C-S_B\) (objective conditional on D1).
- Báo S riêng cả A/B/C, delta theo category, mean signed margins, neutral-adjusted S', và general validation NLL trên tập common hợp lệ.
- Confidence intervals 95% cho từng delta bằng **10.000 paired stratified family bootstrap**: resample 16 family có hoàn lại trong mỗi category, giữ cặp model của cùng family. Seed BOOTSTRAP_SEED 20261113; báo cả số chênh dưới dạng family count, không gọi CI này là chứng nhận confirmatory hoặc giải thích causal toàn mô hình.

**Tiêu chí tín hiệu khám phá đáng theo đuổi (được khóa trước chạy):**
- \(\Delta\ge 0.125\) (tăng ít nhất 8/64 family), *và* cận dưới percentile bootstrap 95% > 0, *và*
- Mỗi category không giảm quá 2/16 family, *và*
- General VAL next-token NLL không xấu hơn nhánh đối chứng tương ứng quá **+0,05 nats/token**.

Nếu không đồng thời thỏa các điều kiện: \`NO_STRONG_EXPLORATORY_SIGNAL\` hoặc \`INCONCLUSIVE\`, vẫn công bố đầy đủ hiệu ứng/CI và thước đo tradeoff. Với ba arms, không có phép ước lượng tương tác data×objective; **không gán dấu cộng hai delta là sự cộng tác nhân quả tuyến tính**. Nếu cả hai âm tính cũng không kết luận giả thuyết không thể đúng ở quy mô khác.

**Secondary rollout:** chọn 16 family EVAL_FC01 đã khóa theo family index trước training, 4/category; mỗi family hai fact A/B, **greedy** thống nhất (max 32 token/EOS=256). 32 outputs/model, tổng 96 outputs và tối đa 3.072 token mới. Đảo thứ tự rater bằng SHA; chấm mù AI 0–3 và khóa input+scores SHA **trước** nối tên arm. \`adherence≥2\`, pair-success và mức lặp là secondary; nếu chưa có reviewer provenance đủ, ghi \`ROLLOUT_RATER_HOLD\` chứ không làm thay primary.

## 7. Kiểm chứng chống tự lừa và rủi ro khoa học

- Chỉ dùng **family-group split**, cấm cùng template-lineage, nhân vật thực thể, tổ hợp rule và paraphrase liên hệ vượt splits; scanner exact + near-duplicate kèm log. Nếu template gốc quá giống, tuyên bố khả năng khái quát ở **phạm vi cụm template**, không tự nâng thành novel reasoning.
- Token-level data/label budget minh bạch. D0 và D1 khác **within-family pairing**, nhưng không thể hoàn toàn loại trừ sự khác biệt redundancy/phân phối cấu trúc; H_D là hiệu ứng của **gói thay đổi dữ liệu D0→D1** đã định nghĩa, không phải hiệu ứng một yếu tố ngôn ngữ độc lập.
- L_C có negative gradients nên compute và cách truyền tín hiệu khác; không dùng nó làm bằng chứng loss architecture thuần túy độc lập supervision.
- Chính sách VAL: được log NLL mỗi 64 bước, **không chọn step/learning rate/λ** theo VAL. Nếu có lỗi hạ tầng, receipt \`INCOMPLETE\` và xin quyết định xử lý sau, không tự rerun theo seed khác.
- Không đưa bất kỳ đặc điểm/score/seed riêng tư của DEV32, FRESH16, Q1Q2/TEST vào mô hình huấn luyện hoặc generator. Có thể dùng **kết luận tổng hợp** DEV32 để đặt câu hỏi mới; không dùng bản ghi thất bại để tinh chỉnh family.
- Giữ bản ghi truy xuất SHA/rights/PII, paper reference và source provenance. Public GitHub chỉ chứa docs/code/aggregate SHA; raw TRAIN, EVAL holdout, checkpoint nếu có quyền, model outputs, reviewer packets private trên Drive/owner Windows.

## 8. Capacity: nhánh conditional FC02, không mở

Không đưa mô hình 8M vào ba nhánh trên. Chỉ **xem xét thiết kế FC02** nếu FC01 đã có kết quả đầy đủ, khóa trước followup và có lý do mô hình 4M bị giới hạn bởi representation/optimization thay vì data/labels.

Ứng viên kiến trúc *giả thuyết* để feasibility: cùng P02 interface, vocab/context/BPE, width 384, layers 4, heads 6 (xấp xỉ 8M, **chưa verify parameter count**). Bản lớn **không có checkpoint step1024 tương đương**, nên không được so fresh initialization với 4M continued pretrained và kết luận do capacity. FC02 phải tạo hoặc chỉ định hai checkpoint có pretraining exposure/budget tương đương hoặc báo rõ confound; so theo token-matched và compute-matched **hai trục khác nhau**, trần chi phí riêng. \`FC02=NOT_OPENED\`.

## 9. One integrated readiness gate, không chuỗi micro-permit

**Một lượt source/runner/rights/compute QA trước khi có owner science GO/HOLD**, chứa:

1. Exact checkpoint/T1 manifest/source SHA và P02 param count, device/VRAM/cost ceiling và resume custody, FP32 reproducibility smoke không cập nhật weights khoa học.
2. 384 family mới: 256 TRAIN + 64 VAL + 64 EVAL locked, raw private SHA, rights/PII, template lineage split, D0/D1 corpus balance, candidate BPE and no label leakage. TinyStories local train rights/provenance pin.
3. Check A/B/C equal primary LM token-slot update schedule and starting weights; C extra candidate compute flagged; objective gradient mathematical correctness/unit tests, no silent hyperparameter changes; independent static QA checklist.
4. Exact EVAL family list and primary formula, bootstrap/threshold/rollout blind rubric, one-shot resume state and artifact output paths frozen. No access to D1 confirmatory sealed data.
5. **Một** quyết định GO/HOLD của owner cho **cả batch ba nhánh**. Nếu chưa có các bytes/rights/runner, \`HOLD_PREEXEC\`. Không yêu cầu từng micro-permit và không mở CPU/GPU chạy huấn luyện trong bước thiết kế.

**Google Drive đề xuất:** \`MyDrive/TTM/ttm-small-pilot/ttm_small4m_fc01_fact_conditioning_20261112/\`, private packages, snapshots và sha receipts; local Windows nằm trong \`D:\WORK\RESEARCH\TokenToModel-Lab\` mà thôi. Colab Free T4 phải có thật lúc chạy; không giả vờ đã cài môi trường hay upload checkpoint.

## 10. Phán quyết thiết kế và bằng chứng dẫn chiếu

**Overall:** \`GO_DESIGN_FREEZE_ONLY\`. Đã chốt một nghiên cứu 3-arm, fixed budget và phép đo; **chưa có family bytes/corpus source/runner release**, nên **\`SCIENCE_EXECUTION=HOLD_PREEXEC\`**, \`NEW_TRAINING=NO\`, \`NEW_INFERENCE=NO\`, \`GPU_PERMIT=NOT_GRANTED\`, \`D1_CONFIRMATORY=HOLD_UNCHANGED\`, \`TEST_Q1Q2=SEALED\`, \`DEV32=ARCHIVED_UNCHANGED\`, \`LINEAGE=UNCHANGED\`, \`MAIN=UNCHANGED\`. Việc khép các trường source SHA còn thiếu phải làm bằng **một batch readiness** chứ không thay outcome hay siết thêm micro gate.

**Bước thực hiện tiếp theo (khi owner yêu cầu triển khai):** \`TTM_SMALL4M_FC01_ONE_PACKET_DATA_RIGHTS_CORPUS_RUNNER_SOURCE_QA_SINGLE_OWNER_GO_HOLD_NO_GPU\`: tạo dữ liệu mới có quyền, runner train/eval và test QA độc lập **một lần**, khóa byte và tính sẵn sàng, ra đúng một owner GO/HOLD. Không cấp phép training/GPU ở bước thiết kế này.

**Liên kết dự án nội bộ:** \`TTM_SMALL4M_D1_EXP32_TERMINAL_EXPLORATORY_CLOSEOUT_AND_NEXT_RESEARCH_DIRECTION_20261112.md\`; \`TTM_SMALL4M_D1_EXP32_TERMINAL_EXPLORATORY_CLOSEOUT_OWNER_SINGLE_ADJUDICATION_20261112.json\`; \`TTM_SMALL4M_D1_FIXED_CHECKPOINT_FACT_CONDITIONING_VS_DECODING_FROZEN_DESIGN_20261111.md\`.

**Tài liệu ngoài tham khảo (lý do chọn can thiệp, không phải chứng minh TTM sẽ cải thiện):**
- Qiu et al., ACL 2024, *PairCFR: Enhancing Model Training on Paired Counterfactually Augmented Data through Contrastive Learning*. https://aclanthology.org/2024.acl-long.646/
- Nguyen et al., Findings EMNLP 2024, *LLMs for Generating and Evaluating Counterfactuals: A Comprehensive Study*. https://aclanthology.org/2024.findings-emnlp.870/
- Hüyük et al., ICLR 2025, *Reasoning Elicitation in Language Models via Counterfactual Feedback*. https://proceedings.iclr.cc/paper_files/paper/2025/file/bf145010b30dc5f14fa87dc152074e4d-Paper-Conference.pdf
- TinyStories upstream dataset card, license field cdla-sharing-1.0 (rights check still required): https://huggingface.co/datasets/roneneldan/TinyStories
