# TTM-Small-4M — O0-only: Thiết kế một lượt thử năng lực học neural trên corpus mới

**Ngày:** 2026-11-11 · **Task:** `TTM_O0_ONLY_SMALL_NEURAL_FEASIBILITY_NEW_DIAGNOSTIC_CORPUS_DESIGN_AND_SINGLE_OWNER_GO_NO_GO`  
**Trạng thái:** `DESIGN_COMPLETE_CANDIDATE` · `SCIENCE_NOT_EXECUTED` · **quyết định tổng hợp hiện tại: `HOLD_T4_NOT_AUTHORIZED`**  
**Nguồn sự thật:** nhánh `research/ttm-o0-only-neural-feasibility-diagnostic-design-20261111`, bắt đầu tại commit phân xử R3A `815541c6f8ed2e275d12ae67780b9a95228e490f`. Không ghi `main`, PR #13 hoặc `lineage.md`.  
**Máy hợp đồng:** [TTM_O0_ONLY_NEW_DIAGNOSTIC_CORPUS_AND_SINGLE_RUN_DESIGN_CANDIDATE_20261111.json](../../artifacts/qa/ttm-o0-neural-diagnostic/TTM_O0_ONLY_NEW_DIAGNOSTIC_CORPUS_AND_SINGLE_RUN_DESIGN_CANDIDATE_20261111.json)

## 1. Vì sao không huấn luyện O1 ngay?

**Dữ kiện đã xác minh:** kiểm định R3A theo mã đã ghim cho thấy một chương trình nhìn `story/question`, lập alias dictionary rồi đọc từ cuối bằng regex giải **384/384**. Kiểm tra original R3A generator/validator qua CPU đã PASS theo phạm vi nguồn, nhưng **khả năng phân biệt heuristic nông với state reasoning FAIL_SCOPED**. R3A không làm FINAL mù vì oracle có trên GitHub; FRESH12 đã dùng để tạo giả thuyết. Phân xử hiện tại là `R3A_DEMO_ONLY`, `O0=HOLD`, `O1=DEFER`.

**Câu hỏi được mở lần này (rất hẹp):** P02 GPT-like 3,75M, bắt đầu từ checkpoint *đã huấn luyện* step 1024, có học được một nhiệm vụ mới về thực thể/mục tiêu và tổng quát hóa sang câu hỏi/cấu trúc mới hay không? Không tìm cách chứng minh model dùng module state ẩn, hiểu nghĩa nội tại hay hơn O1. Không chọn kiến trúc từ một tập toy vừa biết kết quả.

## 2. Kiến trúc và điểm nguồn bất biến

Đọc trực tiếp:
- `src/p02/transformer_core.py` Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`. `P02Config(vocab_size=2048,max_seq_len=256,n_embd=256,n_layer=4,n_head=4,norm_type=layernorm)`; **3.749.376 tham số**; GPT decoder-only, learned positions, causal 4-head attention, tied LM head.
- `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py` Git blob `76c4d0155cd0736919f41682f240b47ad3d7c428`: next-token CE trên **4.096 target thực/step**, AdamW, clip norm 1, scheduler/state và checkpoint READY-last. Đây là **nguồn tham khảo**, **không được chạy lại** science lock lịch sử.
- `tools/pilot_t4/integrated/t4_data_pack.py` Git blob `cdce219f2a2df27e25579f069238d4327c1d7d91`: độc lập theo story, không nối truyện; mask `-100`; đúng BPE2048.
- `tools/pilot_t4/integrated/t4_eval.py` Git blob `bef006bdff173fba6d8ba4aa0ef687a1732fd7c4`: original TinyStories VAL next-token NLL, bootstrap theo story.
- `tools/pilot_t4/integrated/t4_capacity_smoke.py` Git blob `c9a6f256ba975228683ee7de2a1090e649110e97`: ví dụ đo T4 synthetic capacity, không chứng minh chi phí của pipeline nghiên cứu mới.
- Checkpoint bước **1024** SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` theo [pin của nghiên cứu 2×2](https://github.com/minhtri22/TokenToModel-Lab/blob/ed2cfcd3b8676e1a6a959d2f90aade35269ee117/artifacts/qa/ttm-small4m-prompt-conditioning/TTM_SMALL4M_EQUAL_BUDGET_2X2_DESIGN_CANDIDATE_20261110.json). BPE manifest file SHA `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. **Checksum lúc này mới là pin từ GitHub, không phải readback vật lý checkpoint trong lượt này.**

Không thay checkpoint gốc, tokenizer, P02 hay các tập TEST/Q1Q2. Không tự cho rằng tiếp tục từ step 1024 với *optimizer mới* là một phần one-shot T4 cũ: đây là **thử nghiệm mới với warm-start weights**, kết quả không so sánh trực tiếp với `step1280` lịch sử.

## 3. Corpus mới D-N1: dữ liệu có nguồn tự tạo, khác R3A

**Chỉ có thiết kế. Dataset/generator/checker mới **CHƯA được sinh hoặc triển khai**.** Sẽ sử dụng câu chuyện ngắn do một grammar tự viết mới, không lấy hàng, nhãn hoặc template nguyên văn từ R2/R2A/R3/R3A và không dùng TinyStories làm nguồn synthetic. Người nghiên cứu nội bộ có quyền dùng grammar tự tạo, không cần thuê reviewer hoặc cấp phép riêng cho từng file nhỏ; vẫn phải ghi nguồn đầy đủ.

**Bốn family ứng viên**:
1. `N1` — chuỗi alias và thay đổi liên kết ban đầu, hai truyện có cùng câu handoff cuối nhưng đáp án khác.
2. `N2` — ủy quyền/hủy/chuyển mục tiêu; bao gồm nhãn `NONE` và mục tiêu được kế thừa gián tiếp.
3. `N3` — vai trò hoặc tham chiếu có phạm vi, phải xác định khóa truy vấn dưới quy tắc cú pháp rõ ràng; mơ hồ là INVALID, không đoán.
4. `N4` — nhiều đối tượng xen kẽ; can thiệp chỉ đổi mục tiêu truy vấn, đáp án nhiễu không đổi.

Mỗi nhóm có **4 ô** (`A_TARGET,A_DISTRACTOR,B_TARGET,B_DISTRACTOR`) với hai câu chuyện A/B, câu hỏi mục tiêu và nhiễu. Trạng thái trước/sau phải hợp lệ, A/B chỉ thay một sự kiện tác động đúng key và đáp án mục tiêu bắt buộc đổi; đáp án nhiễu giữ nguyên. Yêu cầu ít nhất **25% nhóm** có cùng hai câu cuối ở A/B nhưng đáp án mục tiêu khác do một sự kiện trước đó; không được gọi đó là bằng chứng loại mọi lối tắt. Bảo đảm tối thiểu 25% trường hợp có answer `NONE` hoặc câu trả lời không hiện trực tiếp ở sự kiện cuối, với phân bố cân bằng khi sinh.

| Split prospective | Nhóm × 4 | Số `story/question` | Mục đích |
|---|---:|---:|---|
| `TRAIN` | 1.024 × 4 | **4.096** | Học tiếp O0 |
| `DEV_IID` | 64 × 4 | **256** | Kiểm tra khái quát mẫu cùng họ cấu trúc |
| `DEV_STRUCT` | 64 × 4 | **256** | Kiểm tra motif khác TRAIN |
| `BLIND_FINAL_STRUCT` | 128 × 4 | **512** | Một lần đánh giá OOD mới sau khóa output |
| **Tổng** | **1.280 nhóm** | **5.120** | **CANDIDATE**, chưa sinh |

Tách theo **group_id và graph dependency có xét câu hỏi**, không theo từng hàng, tên nhân vật, độ dài hay một signature toàn sự kiện đơn giản. `TRAIN` và `DEV_STRUCT` và `FINAL_STRUCT` phải không trùng motif; `DEV_IID` được cùng họ motif TRAIN nhưng không cùng sự kiện và không near-duplicate. Chiều dài câu chuyện / token BPE / số lần xuất hiện tên phải được cân bằng hoặc báo cáo định lượng, vì lần trước split bị lộ qua độ dài. Nếu motif budget hoặc cân bằng không khả thi, **HOLD** trước science lock thay vì giả tạo chỉ số `0 overlap`.

**Input model contract:** tại inference chỉ có `story,question`. Không `answer`, `source_events`, `group_id`, `split`, oracle, nhãn hoặc metadata phụ. Parser JSON phát hiện trùng khóa trước chiếu input. Mỗi prompt **≤224 BPE token** theo tokenizer gốc, answer **≤16 token**, toàn bộ chuỗi train có EOS và **≤256 context token** (không silent truncation). Mẫu text ứng viên: `Story:\n...\nQuestion: ...\nAnswer: ...\n`. Với generation chỉ đưa đến `Answer:`, không bao gồm đáp án.

**FINAL thật sự kín:** không đưa plaintext FINAL oracle hoặc seed riêng lên GitHub công khai. GitHub giữ **ciphertext/commitment + SHA256 + thống kê**; khóa, seed FINAL và mapping do owner giữ ngoài repo public. Không giải mã/score trước khi model outputs và metric scripts khóa. Public generator code chỉ tạo được TRAIN/DEV nếu không có private FINAL seed; nếu code vô tình tái tạo được FINAL từ commit thì gate FAIL.

## 4. Chỉ một lượt train O0 và các đối chứng không huấn luyện

| Arm | Nguồn mô hình | Mục tiêu | Bước train mới |
|---|---|---|---:|
| **Z — Frozen O0** | Weights checkpoint 1024, bất biến | Zero-shot/frozen baseline trên cùng prompt | **0** |
| **A — Adapted O0** | Clone đúng weights checkpoint 1024 | Causal next-token CE trên **TRAIN-N1 mới**, không state-head | **128** |
| Heuristic predeclared | word-order-free, last-write, alias-aware regex, n-gram, direct answer prior | Kiểm tra nguồn lợi ích từ quy tắc nông | 0 neural |
| Symbolic interpreter | Replay tất cả luật grammar mới | Positive-control upper bound; phải giải valid fixture | 0 neural |

**Ngân sách A ứng viên:** 128 optimizer steps × **4.096 target có nhãn/step = 524.288 lượt dự đoán token** (bao gồm văn bản và đáp án; **không** coi tất cả là answer-target), context256, batch/microbatch kiểm sau, seed `20261111` cho phiên prospective. Weights 1024 được copy; **AdamW mới** (LR `1e-4` constant, betas `0.9/0.95`, weight decay 0.1, grad clip 1.0), không giả làm resume optimizer lịch sử. Mọi tham số P02 vẫn trainable, không có head phụ hoặc information oracle tại inference. Chỉ **một arm có cập nhật gradient**, không sáu arm. Mọi tensor/batch phải được log để biết số nhãn ANSWER thực — nếu tỷ lệ thấp, kết quả có thể không có tín hiệu vì objective CE quá loãng; không được thay loss hậu nghiệm trong cùng lượt.

**Checkpoint mới** trong thư mục run ID riêng, `step64` và `step128`, READY ghi cuối với SHA readback. Resume phải khôi phục model, optimizer, scheduler, scaler, sampler và RNG cùng step/index; không replay từ 0. Kết quả chỉ dùng checkpoint cuối step128 để quyết định, không lựa chọn best checkpoint sau khi xem DEV.

**Chi phí:** 524.288 lượt mục tiêu là ngân sách đếm được, **không phải dự báo chính xác FLOPs, GPU giây hoặc chắc chắn sẽ vừa T4 Free**. Cần capacity + exact-resume smoke mới. Nếu không đạt capacity, `HOLD` không tự giảm steps hoặc đổi FP16.

## 5. Đánh giá — phân biệt học task và nhu cầu kiến trúc

**Primary (FINAL OOD một lần):** exact-match answer accuracy, cặp `A−Z` theo **nhóm bốn ô** làm đơn vị bootstrap (10.000 lần, seed 20261111). Phải vượt **+10 điểm phần trăm**, CI95 dưới >0 và vượt *heuristic nông tốt nhất đã ghi trước* ít nhất +5 điểm phần trăm, không làm original TinyStories VAL NLL xấu đi quá 5% so với checkpoint1024. Nếu một baseline nông giải 100%, kết luận `STATE_SPECIFIC_DISCRIMINATION_FAIL` và không claim learned state; việc model học một task nhỏ vẫn có thể được mô tả riêng.

**Bộ lọc DEV (chỉ đánh giá một lần sau step128):** trên `DEV_STRUCT`, A phải hơn frozen ít nhất +5 điểm phần trăm; nếu không, **không mở FINAL** và ghi `NO_LEARNING_SIGNAL_SCOPED`, không huấn luyện lại cùng prereg. `DEV_IID` là chỉ số phụ về học mẫu.

**Secondary:** tỷ lệ đúng trọn bộ 4 ô, lật đáp án khi can thiệp, bất biến nhiễu, độ chính xác theo motif/family/answer NONE/dependency length, answer-only NLL, invalid-answer/early-EOS, và VAL NLL gốc. Decoding greedy ≤16 tokens, so exact canonical answer; không sửa tên/key/threshold sau kết quả. Blind labels chưa được tạo; reviewer nội bộ có thể là Codex AI khi cần, nhưng **không cần external human reviewer** và không được claim external independence.

**Ranh giới:** Một seed + một parent checkpoint + dữ liệu grammar nhân tạo chỉ cho phép `EXPLORATORY_CANDIDATE`. Không chứng minh triết học ý nghĩa, graph neural cần thiết, hay O1 hơn O0. Thử nghiệm từ checkpoint 1024 khác from-scratch, khác knowledge-transfer TinyStories hoặc kết quả R3A public.

## 6. Quyết định tổng hợp GO/NO-GO

**Quyết định hiện tại:** `HOLD_T4_NOT_AUTHORIZED__GO_SOURCE_ONLY_INTEGRATED_CPU_PREFLIGHT`.

| Điều kiện cho science | Tình trạng hiện tại |
|---|---|
| P02/checkpoint/tokenizer ghim từ nghiên cứu gốc | Source pins có, physical runtime readback **chưa thực hiện trong lượt này** |
| New synthetic source grammar + strict validator | **NOT_IMPLEMENTED** |
| 1.280 group và graph motif disjoint + length-matched QA | **NOT_GENERATED/NOT_TESTED** |
| New blind FINAL, ciphertext/hash, owner-only key | **NOT_CREATED** |
| Huấn luyện O0 128 steps + exact-resume runner | **DESIGN_ONLY**, chưa CPU/GPU QA |
| Phân phối answer-target, shortcut baselines | **NOT_MEASURED** |
| T4 FP16 capacity và VRAM/giây | **NOT_MEASURED_NEW_RUN** |
| Owner science permission | **NOT_GRANTED** |

Không chia nhỏ thành nhiều lần cấp phép. **Một batch tích hợp CPU** sẽ sinh TRAIN/DEV, kiểm motif/shortcut/strict schema/BPE length, chốt bí mật FINAL với owner, kiểm runner O0 source-only và exact-resume. Sau đó trình chủ dự án **một** hồ sơ gồm rights (dữ liệu tự tạo), capacity, QA, seed, ngân sách và final escrow để quyết định T4 GO/HOLD. **Chưa thực hiện batch này trong lượt thiết kế.**

**Bước thực hiện tiếp theo:** `TTM_O0_NEW_DIAGNOSTIC_CORPUS_GENERATOR_STRICT_CHECKER_SHORTCUT_AUDIT_AND_ONE_CPU_PREFLIGHT_SINGLE_OWNER_DECISION`.

**Bảo toàn:** `R3A=DEMO_ONLY`, `O0=HOLD`, `O1=DEFER`, `NEW_TRAINING=NO`, `GPU=NO`, `TTM_TEST_Q1Q2=UNTOUCHED`, `PR13=DRAFT_HOLD`, `MAIN=NOT_WRITTEN`, `LINEAGE=NOT_WRITTEN`.
