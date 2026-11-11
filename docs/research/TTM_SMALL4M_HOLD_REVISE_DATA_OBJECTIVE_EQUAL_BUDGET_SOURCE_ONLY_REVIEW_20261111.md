# TTM-Small4M — Rà soát source-only dữ liệu × mục tiêu học và chọn một đối chứng ngang ngân sách

- Ngày: 2026-11-11 (Asia/Bangkok).
- Nhiệm vụ: `TTM_SMALL4M_HOLD_REVISE_DATA_OBJECTIVE_EQUAL_BUDGET_SOURCE_ONLY_REVIEW`.
- Loại: **INTEGRATED_SOURCE_ONLY_REVIEW / CANDIDATE_PRIORITIZATION**, không phải một thực nghiệm khoa học mới.
- Kết luận: **`SELECT_A_VS_C_OBJECTIVE_ONLY_DESIGN_CANDIDATE`**; `SCIENCE=HOLD_NOT_AUTHORIZED`, `TRAINING=NOT_EXECUTED`, `INFERENCE=NOT_EXECUTED`.
- Repo: `minhtri22/TokenToModel-Lab`. Main đọc ở lượt này: `5d52e32f20021e36f08f284ef9864d3ba36dbead`. Nhánh thiết kế được rà soát trước commit: `ed2cfcd3b8676e1a6a959d2f90aade35269ee117`. PR #13 hiện hữu: `72cbf73c3adb78f9d4111f702de71fa10f713533`, DRAFT/HOLD.
- Ranh giới: không sửa `main`, `lineage.md`, P02, tokenizer, private pack, checkpoint, consumed FRESH12/Q1/Q2/TEST/OOD256; không mở branch/PR mới, không merge, không tạo science CLAIM, không chạy Colab hay Ollama.

## 1. Câu hỏi nghiên cứu và tình trạng bằng chứng

**Vấn đề:** tại sao NLL được cải thiện nhưng sinh văn bản bám nhân vật/vật thể/mục tiêu yếu?

- T4 gốc: 3.749.376 tham số, BPE 2048, context 256, 2.048 TRAIN stories, 2.691 TRAIN windows, 498.287 valid TRAIN labels trong pack, checkpoint step 1024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. T4 VAL NLL = 3.5223388517 so với bigram 3.9972314170, giảm 11.880537% theo hồ sơ khoa học gốc; TEST gốc đã tiêu thụ.
- FRESH12 trên PR13 (one AI scorer Codex, không human): 48 outputs, 35/48 adherence=0/3; trung bình adherence baseline/trimming đều 0.291667, delta = 0; không có cải thiện ngữ nghĩa theo gate ứng viên. FRESH12 và Q1/Q2 đã tiêu thụ, không chấm hay sinh lại.
- Root-cause trước đây chứng minh trailing ASCII space làm lệch xác suất token đầu sang newline; đã kiểm nguyên nhân định dạng, nhưng bỏ space không tạo cải thiện bám ngữ nghĩa đã chứng minh. Không có lỗi x/y shift hoặc P02 CPU forward trên các probe đã đối chiếu.
- Ba giả thuyết chưa phân biệt: **H-DATA** (dữ liệu hẹp/reuse/lấy mẫu), **H-OBJECTIVE** (phân bổ loss trên các vị trí trong cửa sổ), **H-CAPACITY** (số tham số/context). `next-token CE` có điều kiện trên prefix và **không phải mục tiêu sai**; thiếu bằng chứng cho nguyên nhân duy nhất.

Nguồn: `lineage.md` L0011–L0012 trên main; PR13 `docs/pilot/ttm-small4m-source-of-truth/TTM_FRESH12_OWNER_CONTROLLED_UNBLIND_AND_SCOPED_QUALITY_ADJUDICATION_20261110.md`; `docs/pilot/TTM_SMALL4M_PROMPT_ADHERENCE_ROOT_CAUSE_READONLY_DIAGNOSTIC_20261109.md`.

## 2. Kiểm kê thiết kế kế thừa — không tái thiết kế toàn bộ

Thiết kế 2×2 gốc trên chính nhánh này đã ghim bốn arm:
- A: `ORIGINAL_REPLAY_SAMPLER_WINDOWS` + `UNIFORM_VALID_TOKEN_CROSS_ENTROPY`.
- B: `FIRST_STORY_WINDOW_COUNT_MATCHED_REPLACEMENT` + `UNIFORM_VALID_TOKEN_CROSS_ENTROPY`.
- C: `ORIGINAL_REPLAY_SAMPLER_WINDOWS` + `SUFFIX_POSITION_WEIGHTED_CROSS_ENTROPY`.
- D: `FIRST_STORY_WINDOW_COUNT_MATCHED_REPLACEMENT` + `SUFFIX_POSITION_WEIGHTED_CROSS_ENTROPY`.

Nguồn `artifacts/qa/ttm-small4m-prompt-conditioning/TTM_SMALL4M_EQUAL_BUDGET_2X2_DESIGN_CANDIDATE_20261110.json`, `docs/research/TTM_SMALL4M_PROMPT_CONDITIONING_TRAIN_OBJECTIVE_EQUAL_BUDGET_2X2_DESIGN_20261110.md`.

Bằng chứng source-only trước: synthetic 72/72 PASS, real checkpoint parent CPU restore PASS, 42/42 CPU QA, 34/34 arithmetic/source audit, matched draw metadata PASS. **Đây là các PASS kỹ thuật đã ghi ở lượt trước; không có native/GPU QA mới ở lượt này.** Lịch A=C khóa digest `b4082178bac4c7830645661f31b2ba16a5743d324ac46000b5f9dffc289f4fe3`. A/C: 128 bước, 2.928 cửa sổ forward/arm, 749.568 tensor token slots/arm, 524.288 target labels/arm. Dữ liệu B/D làm giảm số truyện độc nhất được chọn từ 1.493 (A/C) xuống 1.363 (B/D), nên **B không phải phép tăng đa dạng dữ liệu thuần**.

Trạng thái gần nhất của chính thiết kế 2×2: `artifacts/qa/ttm-small4m-prompt-conditioning/real_readiness/OWNER_SINGLE_GO_HOLD_DECISION_20261110.json`: **`HOLD_FREE_T4_NOT_AUTHORIZED`**; thiếu xác nhận quyền của owner, reviewer riêng, resume READY khi bị ngắt, FP16 GPU T4 gate và new science lock. 12 DEV/24 BLIND_FINAL prompt source-only đã biên soạn, BPE roundtrip 36/36, nhưng chưa chạy.

## 3. Phương án đơn biến được chọn: A vs C (OBJECTIVE ONLY)

**Biến can thiệp duy nhất:** trọng số CE theo vị trí token, không đổi chuỗi đầu vào, tokenizer, danh sách window, labels, source train hay capacity.

| Trường | A — Control | C — Treatment |
|---|---|---|
| Checkpoint ban đầu | Cùng step1024 frozen | Cùng step1024 frozen, clone độc lập |
| Model | P02 3.749.376 param | Không đổi |
| TRAIN và mẫu từng bước | Replay original sampler | **Exact same window IDs/order/valid target counts** |
| Loss | Tất cả nhãn hợp lệ weight 1 | Vị trí 0..31 weight 1; từ 32 weight 3 |
| Chuẩn hóa loss | Sum CE / valid count | Sum(weight×CE) / sum(weight), trên **toàn** optimizer step |
| Nhãn pad `-100` | Không tính | Không tính |
| AdamW/scheduler/RNG/scaler/seed/dtype | Khôi phục từ cùng parent; FP16 candidate | Giữ nguyên và clone độc lập |
| Bước optimizer | 128 (1025–1152) | 128 (1025–1152) |
| Target labels/bước | 4.096 | 4.096 |
| Tổng target presentations | 524.288 | 524.288 |
| Forward windows | 2.928 | 2.928 |
| Forward slots | 749.568 | 749.568 |

Tổng candidate **256 optimizer steps**, **1.048.576 target-token presentations**, **1.499.136 forward token slots** trên cả hai arm — **50% số arm/target budget** so với thiết kế 2×2 bốn arm (không đồng nghĩa 50% wall-clock do startup và eval). Không đánh đồng lượt nhãn với số token mới hoặc FLOPs. Nguồn gốc: mã `tools/pilot_t4/prompt_conditioning_2x2/ttm_2x2_colab_runner_candidate.py`, hàm `loss_step` đã kiểm source: denominator weighted tính ở scope toàn bước, pad được zero, không đổi nhãn. Với loss C, **trọng số gradient khác** là hiệu ứng can thiệp được dự định; không được nói effective weighted supervision bằng nhau.

**Giới hạn định danh:** A vs C chỉ kiểm tra whether *suffix-position-weighted CE* có tạo tín hiệu lợi ích so với uniform CE trong **128 bước tiếp tục từ cùng một parent**; không chứng minh trực tiếp khả năng nhớ thực thể, chất lượng corpus, lợi ích của SFT hoặc giới hạn mọi 4M model. A/C dùng một parent và một lịch sampler → bất định qua các seed huấn luyện không được ước lượng. Nếu C không đạt, không chứng minh rằng các objective khác đều vô ích.

**Phạm vi B/D:** bảo toàn thiết kế gốc, nhưng không thực thi trong phase candidate này. Nếu muốn nghiên cứu H-DATA riêng, phải trình nguồn đa dạng hóa dữ liệu và matched-control **khác**, không dùng nhãn “first-window” để thay cho “more diverse data”.

## 4. Chỉ tiêu thành công duy nhất, dữ liệu đánh giá và quy tắc chốt

**Primary outcome (một chỉ tiêu):** `Δ_prompt_adherence = mean_{24 BLIND_FINAL prompts}[score_C − score_A]`, điểm bám prompt trên thang 0–3, chấm theo rubric đã có. Ngưỡng **đề xuất** `Δ≥+0.5/3`, giữ nguyên từ candidate 2×2 gốc; cần owner khóa **trước** khi có kết quả. Báo kèm paired prompt-cluster bootstrap CI95 (theo 24 prompt, không phải token); CI lower >0 là điều kiện tin cậy cho candidate PASS, không phải một endpoint khác. Nêu số cặp thắng/hòa/thua mô tả, không chọn ngưỡng hậu nghiệm.

**Guardrails không thay primary:** không giảm trung bình coherence/consistency quá 0.25/3, không làm VAL NLL tăng quá 5% tương đối so với A; các giới hạn này từ candidate cũ cần owner giữ nguyên hoặc freeze hợp lệ trước run. Bảo lưu tất cả negative results. 12 DEV chỉ phục vụ QA chấm/định dạng, không chọn hyperparameter, không điều chỉnh checkpoint; 24 BLIND_FINAL đã ghi SHA là tập đánh giá mới, chỉ dùng một lần. Prompt không có trailing ASCII space, greedy max 64 BPE token, cùng EOS/context cho A,C. Tái dùng **nội dung** 24 FINAL đã khóa của thiết kế chưa thực thi là hợp lý vì chưa có output, nhưng **không** dùng khóa Latin-square 4-arm chưa được cấp để giả tạo 2-arm blinding; cần lập/niêm phong lịch A/B 12/12 và người chấm độc lập nhận packet không có nhãn. Không dùng FRESH12, Q1/Q2, T4 TEST hoặc OOD256 làm tập xác nhận mới.

**Nếu đạt:** `OBJECTIVE_SUFFIX_WEIGHTING_EXPLORATORY_CANDIDATE_PASS`, chỉ trên 24 prompt với một parent và rater thực tế; không kết luận đã chứng minh nhân quả tổng quát hay thương mại. **Nếu không đạt:** `NO_DEMONSTRATED_GAIN_SCOPED`, bảo toàn FAIL và chuyển sang đánh giá giả thuyết dữ liệu theo hợp đồng mới, không tự tăng tham số. **Nếu thiếu quyền/runner/reviewer:** `HOLD_NOT_EXECUTED`, không thay threshold để cứu nghiên cứu. Các nhãn PASS/FAIL chỉ mang tính *dự kiến*, chưa phát sinh.

## 5. Cổng hành động và chi phí trước khi có thể chạy

Để thay hợp đồng 2×2 thành 2-arm candidate cần **amendment trước thực nghiệm**, không sửa hồi tố prereg/candidate đã lưu:
- Người sở hữu xác nhận quyền tính toán trên private TinyStories pack và điều kiện CDLA-Sharing 1.0; không đăng lên GitHub raw corpus/token/checkpoint; không suy ra quyền phân phối từ QA nội bộ.
- Lấy đúng mã nguồn 2-arm kế thừa rồi điều chỉnh run matrix/specific run IDs, khóa SHA runner mới + nguồn/optimizer/scaler/sampler + recipe; QA kỹ thuật gộp, negative fixtures và độc lập trên source. **Không chạy runner 4-arm nguyên trạng mà quảng bá là 2-arm.**
- Đảm bảo Colab T4 FP16 preflight và interrupted checkpoint READY/resume parity; hiện **NOT_EXECUTED/HOLD**. Không bypass cổng chính vì CPU QA 42/42 PASS.
- Niêm phong assessor independence, rubric, 24 FINAL, 2-arm pair mapping 12/12 trước bất kỳ token nào; nếu chỉ có một AI chấm, kết luận tối đa exploratory scoped.
- Một science owner authorization chính xác sau khi đủ các cổng, thay vì nhiều micro-permits; mọi science one-shot phải dùng run ID mới và không đụng run cũ.

**Chi phí lượt review này:** 0 GPU seconds, 0 optimizer steps, 0 model-forward/inference, 0 TEST/OOD reads. **Ngân sách nếu sau này được duyệt:** 2 × 128 optimizer steps + 2 × 24 × tối đa 64 = tối đa 3.072 generated tokens ở final (ngoài 12 DEV/arm, VAL eval và overhead). Chưa có log T4 hiện hành để ước lượng chính xác phút Colab, USD hoặc RAM; miễn phí Colab không được bảo đảm tài nguyên.

## 6. Phán quyết / main merge

- `DESIGN_SELECTION=PASS_SCOPED_SOURCE_REVIEW`: chọn A vs C và một outcome; không có science pass.
- `SCIENCE_EXECUTION=HOLD_NOT_AUTHORIZED`: giữ quyết định HOLD của nghiên cứu 2×2 trước đó; không huấn luyện.
- `ORIGINAL_HYPOTHESIS_H_DATA=OPEN`; `H_OBJECTIVE=TESTABLE_NOT_TESTED`; `H_CAPACITY=NOT_ISOLATED`.
- `CHANGE_SCOPE=ONE_DOC_ON_EXISTING_RESEARCH_BRANCH`; `MAIN=UNCHANGED`; `PR13=UNCHANGED`; `LINEAGE=APPEND_ONLY_UNTOUCHED`; `MERGE_DECISION=HOLD` — đây là quyết định rà soát, không phải nhánh implementation cần merge ngay.
- `NEXT_MERGE_ACTION`: xem xét source-only design document trên nhánh hiện hữu, chờ gate science riêng; không merge các kết quả sang main khi chưa thẩm định phạm vi.

## Bước thực hiện tiếp theo

`TTM_SMALL4M_A_VS_C_OBJECTIVE_ONLY_PREEXEC_INTEGRATED_SOURCE_QA_RIGHTS_REVIEWER_RESUME_GATE`

Một lượt **tích hợp tiền thực thi** trên chính nhánh đã có: amendment A/C, hoàn thiện runner 2-arm và READY/resume QA, kiểm rights/reviewer, khóa 24 paired prompts/rubric; chỉ khi đầy đủ PASS mới trình **một quyết định thực thi khoa học**. Không chạy GPU/training/inference, không mở nhánh hoặc thay checkpoint trong lượt tiền kiểm.
