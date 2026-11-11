# TTM-Small-4M — Phân xử thất bại N1 và chuyển hướng nghiên cứu (không vá toy)

**Ngày:** 2026-11-11 · **Task:** `TTM_O0_DIAGNOSTIC_N1_FAILED_GATES_OWNER_RESEARCH_REDIRECT_NO_MORE_HEURISTIC_PATCHES`  
**Loại công việc:** Phân xử nguồn và thiết kế nghiên cứu nội bộ; không huấn luyện/suy luận mô hình mới.  
**Nhánh:** `research/ttm-o0-n1-failed-gates-natural-narrative-redirect-20261111`, tách tại commit N1 `6497699a13e42470015ddecc100e10f4a8ba61f9`. GitHub là nguồn sự thật. **Không ghi `main`, `lineage.md` hoặc PR #13**.

## 1. Nguồn đã kiểm định và các kết luận không thể trộn

**Đọc trực tiếp GitHub trên exact commit N1:**
- [Biên bản tích hợp N1](../../docs/research/TTM_O0_N1_NEW_DIAGNOSTIC_CORPUS_INTEGRATED_CPU_PREFLIGHT_AND_SINGLE_OWNER_HOLD_20261111.md), blob `c05abcbac2a444a72acfea662a13fb9f088d81ed`.
- [Quyết định HOLD tổng hợp](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_INTEGRATED_SINGLE_OWNER_HOLD_DECISION_20261111.json), blob `990886f572557e59bb672b02e7858ca70342d016`.
- [Kiểm toán can thiệp/split](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_SINGLE_INTERVENTION_AND_STRUCTURAL_SPLIT_AUDIT.json), blob `6416197e71609a9d3c015a253e5b7b128de0e8ea`.
- [Đối chứng shallow alias aware](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_SHALLOW_ALIAS_HEURISTIC_BASELINE.json), blob `1e8d0c906064ef08d10fa8c3281b932070c1a8ba`.
- [BPE2048 length QA](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_EXACT_T1_BPE2048_LENGTH_READONLY_QA.json), blob `d6016322fbd7749a801ecefb094cd1458b23fcf1`.
- [FINAL owner escrow QA](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_FINAL_SEED_ESCROW_REPRODUCTION_QA.json), blob `3946f88546326cb25788e1566afb29a7d35a748a`.
- [Thiết kế O0 nguồn trước N1](TTM_O0_ONLY_NEW_DIAGNOSTIC_NEURAL_FEASIBILITY_SOURCE_EVAL_BUDGET_AND_SINGLE_GO_NO_GO_20261111.md): chỉ source-design, không phải giấy phép science.

| Nội dung đã chạy | Kết quả được bảo toàn | Giới hạn phát biểu |
|---|---|---|
| 4.608 public TRAIN/DEV model-input, 1.152 quartet | `PASS_SCOPED` về sinh dữ liệu/nhãn theo grammar | Dữ liệu public, không phải mù |
| Checker từ văn bản | 4.608/4.608; negative semantic 13/13; JSON fail-closed 16/16 | Kiểm đúng chương trình, không chứng minh học neural |
| BPE T1 gốc 2048, 1.791 merges | 0/4.608 prompt >224 hoặc train >256; max 177/182 | Chưa kiểm BPE cho N1 FINAL kín |
| CPU restore checkpoint gốc step 1024 | `PASS_CPU_SYNTHETIC_RESTORE` hai bước giả lập | Không phải 128-step science, FP16/T4 resume chưa QA |
| FINAL AES-256-GCM escrow | Tái dựng 512/512 và khóa riêng do owner giữ; plaintext FINAL không có trên GitHub | FINAL thiếu độc lập cấu trúc, **không mở chấm** |
| **Heuristic alias-aware last-event** | **4.608/4.608** không replay graph/state | `SCIENTIFIC_DISCRIMINATION=FAIL_SCOPED` |
| **Can thiệp chính xác một sự kiện** | **556/1.152 PASS; 596/1.152 FAIL** do câu nhiễu cũng thay đổi | Không gọi toàn bộ 1.152 nhóm là minimal-pair valid |
| **FINAL độc lập motif** | **FAIL: 4/4 họ cấu trúc thô trùng DEV_STRUCT** | Không chấp nhận claim OOD/confirmatory |
| Phân phối giám sát answer | **15.162/637.010 token TRAIN ≈2,38%** | Objective CE thường bị loãng tín hiệu answer; không tự tăng loss sau xem kết quả |

**Phân biệt logic:** Mọi ngữ nghĩa toy hữu hạn có thể có một thuật toán quy tắc giải đúng; điều đó không ngăn ta kiểm tra neural có học được một task. Nhưng **100% của heuristic nông trên N1 cộng lỗi intervention và split** loại bỏ khả năng dùng N1 như bằng chứng đặc hiệu của biểu diễn trạng thái hoặc tổng quát hóa cấu trúc. Không suy ra P02/GPT-2 thiếu năng lực. `NEURAL_O0=NOT_TESTED`; `O1_SUPERIORITY=NOT_TESTED`.

## 2. Một quyết định chuyển hướng — chỉ một chương trình nghiên cứu

**Phân xử:** `N1_PUBLIC_DEMO_AND_ENGINEERING_QA_ONLY` + **`SELECT_NEW_NATURAL_NARRATIVE_CONDITIONAL_LIKELIHOOD_DESIGN`**. Giữ N1, R3A, R3/R2A bất biến làm ví dụ về lỗi benchmark/QA; **không sửa thêm heuristic/toy hậu nghiệm, không train N1 để lấy khoa học**.

Hai phương án được cân nhắc:
- **A — N1 task-learning demo:** Có thể chạy quick learning demo trong tương lai để minh họa O0 học được quy tắc deterministic; chỉ có claim **engineering/demo**, sử dụng public TRAIN/DEV, cấm dùng N1 FINAL, cấm claim state module cần thiết. Không được chọn làm đường science chính ở lượt này vì chi phí neuron mới không trả lời câu hỏi về biểu diễn ngữ nghĩa, objective answer chỉ 2,38% và N1 lỗi minimal-pair.
- **B — Benchmark scientific exploratory mới:** Truyện ngắn ngôn ngữ tự nhiên do nội bộ tự biên soạn; đo tính nhạy của mô hình **O0 đã đóng băng** với thay đổi quan hệ/ngữ cảnh bằng xác suất tiếp nối; không train, không dùng tập toy cũ, không mở dữ liệu TEST/Q1Q2. Giải quyết một câu hỏi khoa học hẹp với chi phí ít hơn training.

**Chọn B làm đường nghiên cứu đang hoạt động.** A chỉ lưu trong danh mục demo tùy chọn, không mở job/nhánh đào tạo đồng thời. Đây là **quyết định hướng nội bộ**, không phải sự chứng nhận của người phản biện ngoài, không cấp phép inference/GPU trong lượt này.

## 3. Thiết kế benchmark kế nhiệm: NARRATIVE-CF1 (thiết kế, chưa tạo dữ liệu)

**Câu hỏi:** Với checkpoint O0-Small4M hiện có, việc đảo một quan hệ sự kiện trong cùng ngữ cảnh tự nhiên có thay đổi **ưu tiên xác suất** giữa hai tiếp nối hợp logic và bất hợp logic hay không?

**Không có** nhãn đầu phụ trạng thái, không dùng prompt câu hỏi/đáp án theo grammar N1, không biến bài kiểm tra thành chạy regex rồi claim semantic memory. Cơ sở ngữ nghĩa là **quan hệ giữa tham chiếu thực thể, mục tiêu và chuỗi sự kiện** trong văn cảnh; vật lý chỉ là nội dung truyện, không làm tiền đề phương pháp.

### 3.1 Các nhóm nội dung và quy mô *ứng viên*

- Nhóm `C1` — thay đổi người giữ hoặc được giao nhiệm vụ qua diễn ngôn tự nhiên; phải xác định referent đúng.
- Nhóm `C2` — mục tiêu, cam kết, ủy quyền, thay đổi quyết định; cùng một hành động cuối có diễn giải khác theo thông tin trước.
- Nhóm `C3` — lời nói, ý định hoặc thông tin mà nhân vật đã biết/chưa biết; kiểm tiếp nối phản ánh góc nhìn/trạng thái tri thức đã nêu tường minh.

Tổng **108 cặp ngữ cảnh phản thực** = 36 cặp DEV (12/cụm) + **72 cặp BLIND FINAL** (24/cụm). Mỗi cặp gồm **2 ngữ cảnh A/B** và **2 tiếp nối ứng viên cố định x/y**, tạo bốn điểm log-likelihood `P(x|A),P(y|A),P(x|B),P(y|B)`. Các số 108/72/432 là **kế hoạch**; chưa biên soạn text, chưa được đảm bảo độ đa dạng/mù.

**Soạn bài bằng ngôn ngữ tự nhiên độc lập**, đa dạng địa điểm/tình huống/nhịp văn, tránh lặp template/truyện R2–N1. Do owner/ChatGPT Web biên tập; Codex AI có thể phản biện chất lượng và lỗi đơn nghĩa theo exact SHA, không tự gán human external validation. Câu chuyện khoảng 50–120 từ, nhưng **giới hạn bắt buộc là BPE2048**: context ≤224 token, một tiếp nối ≤16 token, toàn sequence ≤256. Nếu không đáp ứng: chỉnh *trước prereg freeze*, không cắt silently.

### 3.2 Counterfactual 2×2 và phép đo

Viết `L(c,a)` = trung bình **log-probability theo token** của cùng tiếp nối a, được chấm teacher forcing khi có context c. Hai tiếp nối x/y ở mỗi cặp dùng **chính các chuỗi token giống nhau** khi đối chiếu A/B, khuyến nghị cùng độ dài BPE; nếu lệch độ dài vượt điều kiện pin trước thì loại trước khóa, không normalize để chữa outcome. Nhãn đúng đảo giữa A/B nhưng nguồn câu chuyện/nhân vật chủ đạo tương đương về độ dài và từ vựng.

- `m_A = L(A,x) - L(A,y)`: x phải có ưu thế ở A.
- `m_B = L(B,y) - L(B,x)`: y phải có ưu thế ở B.
- `D = m_A+m_B`: hiệu ứng **thay đổi ưu tiên theo ngữ cảnh**; D>0 **một mình không đủ** để gọi giải đúng.
- **Chính (primary):** `PAIR_BOTH_CORRECT = (m_A>0 and m_B>0)`. Hòa ở 0 được ghi TIE/FAIL (không làm tròn để thành PASS).
- **Phụ:** D, hai margin riêng, độ nhạy đảo câu/đổi tên, chênh lệch theo C1/C2/C3, token length, entropy và rate không hợp lệ.

Cùng tokenizer/weights/forward và không update model; mỗi cặp chấm bốn log-probabilities với greedy-free teacher forcing, không ép mô hình trả lời theo định dạng Q/A chưa học. Nếu mô hình vượt heuristic yếu, kết luận tối đa là **context sensitivity trên corpus cụ thể**, không phải biết state logic nói chung.

### 3.3 Baselines và phản chứng phải ghi trước khi nhìn score O0

1. `CONTEXT_BLIND_PRIOR`: cùng câu trả lời luôn ưu tiên, không thể đúng đồng thời trên hai ngữ cảnh đảo nhãn.
2. `LAST_MENTION`, `ALIAS_LOOKUP`, `KEYED_LATEST_EVENT`: áp dụng nếu tự nhiên có phép xác định ngữ nghĩa rõ; báo cáo coverage và abstain, không ép parser giải mọi câu.
3. `BAG_OF_WORDS`, `RECENCY`, `LEXICAL_NGRAM`, `ANSWER_FREQUENCY`: đối chứng học bề mặt.
4. `HUMAN_CODEX_SEMANTIC_VALIDATION`: hai cách đọc độc lập nội bộ trước khóa, xử lý tranh cãi, không để đáp án chủ quan đi vào dữ liệu model scoring.
5. `RANDOM_PRIOR`: mô phỏng trả lời ngẫu nhiên hai ô, công bố làm tham chiếu trực quan, không thay thế CI.

**Trần suy luận:** nếu heuristic mới đạt 100%, vẫn có thể mô tả O0 có/không có context sensitivity; **không** dùng nó làm bằng chứng bắt buộc cần O1 hoặc causal state module. Cấm sửa benchmark bằng kết quả mô hình sau khi xem. Nếu hơn heuristic chỉ do câu chuyện/template bị lộ, phán quyết NO_SIGNAL_SCOPED.

### 3.4 Chia DEV và FINAL mù

- Cụm cặp/sơ đồ quan hệ nằm trọn một split; không cùng truyện, tái diễn tên, bản dịch hoặc chỉnh sửa một cảnh giữa DEV và FINAL.
- Cân độ dài **BPE thực**, số sự kiện, tần suất đáp án x/y, vị trí từ khóa và độ khó về tham chiếu; không lập split bằng cố định số câu như R3A.
- Tự kiểm exact và normalized-near-duplicate với các hàng public R3A/N1 cùng các prompts FRESH12/Q1Q2 *chỉ bằng pin/ID có sẵn*, không đọc Q1Q2/TEST sealed. Không claim full semantic non-overlap nếu thiếu bằng chứng.
- DEV có thể công khai **sau khi khóa** để QA code nhưng **FINAL có oracle/nhãn không đưa plaintext lên public GitHub**. Commit SHA-256/ciphertext (không seed/key), đáp án chấm một lần sau khi đóng băng model + scorer; một người owner giữ khóa ngoài GitHub và trong phạm vi project.
- Blind FINAL không phải dataset original TTM TEST; hoàn toàn mới. Nếu có lỗi câu mơ hồ do internal reviewer xác nhận thì sửa trước scoring/freeze, nếu phát hiện sau freeze thì báo excluded reason và không tự thay thế.

### 3.5 Điều kiện trước một lượt chạy model mới

**SOURCE:** P02 code blob `9762343e06cf800b50574c2871ae1ed58537fb18`, config `vocab_size2048/context256/embd256/layers4/heads4`; nguồn checkpoint bước 1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; BPE T1 TRAIN-only với manifest SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. Các pin là lịch sử/QA N1 đã báo; *chưa có model readback mới trong lượt này*.

**EXECUTION:** Bộ chấm teacher forcing không cập nhật gradient, có strict input allowlist, phụ thuộc đúng cặp x/y, byte-level source pin, output READY-last và SHA readback, có negative tests đổi đáp án/trao split/metadata và test lật dấu margin. **Không cần T4 huấn luyện:** ưu tiên kiểm năng lực frozen O0 trên CPU batch nhỏ (đo memory/time), nếu không phù hợp mới trình một quyết định tài nguyên. Không tự chạy inference ở lượt chuyển hướng này.

**EVALUATION:** Chấm một lần DEV rồi một lần FINAL sau khi đóng băng mọi code/checkpoint và loại mọi chọn ngưỡng hậu nghiệm; bootstrap 95% theo cặp, báo effect size + CI; cỡ mẫu nhỏ = **exploratory**, không dùng p-value đơn lẻ để claim universal. Gate đề xuất để quyết định có đáng mở một **nghiên cứu tiếp theo**: ≥50% cặp FINAL cả hai ngữ cảnh đúng, ít nhất +10 điểm phần trăm so với đối chứng lexical tốt nhất có coverage ngang, và CI bootstrap của chênh lệch >0; phải được freeze trước chạy. Nếu không đạt: ghi FAIL/INCONCLUSIVE, không đổ lỗi cho triết học hay tuyên bố O1 vô ích.

## 4. Một quyết định GO/HOLD hiện tại, không tạo chuỗi micro-permit

**Phán quyết duy nhất trong lượt này:**
- `RESEARCH_DIRECTION=GO_DESIGN_NARRATIVE_CF1`: chấp nhận *hướng thiết kế & nghiên cứu nguồn*, chưa tạo corpus/scorer.
- `N1=DEMO_AND_QA_ONLY`, không dùng N1 FINAL khoa học, không mở lại ciphertext/seed.
- `O0_NEW_NEURAL_INFERENCE=HOLD`, `O0_TRAINING/T4=HOLD`, `O1=DEFER`.
- `R3A=DEMO_ONLY`, `ORIGINAL_Q1Q2/TEST=UNTOUCHED`, `PR13=DRAFT`, `MAIN/LINEAGE=NOT_WRITTEN`.

**Vì sao HOLD thay vì chạy ngay?** NARRATIVE-CF1 chưa có văn bản/nhãn/escrow, chưa kiểm BPE và giá trị tham số trên CPU, chưa có bộ chấm/logit scorer, chưa có baselines hoặc độc lập chấm. Không có bằng chứng để cấp GO đánh giá model mới hoặc chạy huấn luyện.

**Bước thực hiện tiếp theo (một batch):**
`TTM_O0_NARRATIVE_CF1_NATURAL_MINIMAL_PAIRS_SOURCE_SCORER_CPU_PREFLIGHT_AND_BLIND_EVAL_READINESS`. Biên soạn, kiểm định và pin DEV + FINAL ciphertext, triển khai teacher-forced pairwise scorer với frozen P02 checkpoint, kiểm CPU ở fixtures **không phải corpus FINAL**, chạy baselines trên DEV một lần, làm QA độc lập/phản biện nội bộ và **trình một quyết định GO/HOLD để chấm O0 thật**. Không quay lại sửa N1/R3A heuristic hoặc mở O1/GPU.

## 5. Đánh dấu ranh giới quản trị

Mọi sự kiện R2A/R3/R3A/N1 đã ghi vẫn bất biến; không sửa PASS/FAIL cũ hoặc `lineage.md` cho design-only. Owner + ChatGPT Web + Codex AI khi cần là tổ chức thực hiện nội bộ, không claim peer-reviewed external. Không xuất khóa FINAL, TinyStories private TRAIN/VAL tokens, raw checkpoint hay original TEST/Q1Q2 lên GitHub. Không tạo Git worktree hay file trên Windows ngoài project root.

**Câu trả lời một dòng:** Dừng N1 ở mức demo, không vá toy; chọn **frozen O0 + phản thực trong truyện ngôn ngữ tự nhiên** làm chẩn đoán khoa học kế nhiệm — chưa train, chưa model inference, chưa GO T4.
