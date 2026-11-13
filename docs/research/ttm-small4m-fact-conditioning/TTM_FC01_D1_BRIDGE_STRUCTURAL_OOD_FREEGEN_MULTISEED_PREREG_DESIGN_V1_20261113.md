# TTM-Small-4M — FC01 → D1 Bridge: đề cương tiền đăng ký xác nhận V1

**Operation:** `TTM_SMALL4M_FC01_POSTHOC_EVIDENCE_ARCHIVE_AND_D1_BRIDGE_PREREG_DESIGN_ONLY_NO_GPU`  
**Ngày lập:** 2026-11-13  
**Phân loại:** `PREREG_DESIGN_CANDIDATE_FROZEN_FOR_SOURCE_INDEPENDENT_REVIEW` · **`D1_BRIDGE_SCIENCE=HOLD_NOT_AUTHORIZED`**.  
**Không phải** `TTM_SMALL4M_D1` hiện hữu và không thay protocol 512 văn bản/rubric chấm mù ngày 12/11/2026.  
**Nguồn động cơ, không phải dữ liệu xác nhận:** FC01 V2 đã khóa A/B/C 768/768 updates; EVAL64 C=38/64 so với B=3/64 và A=4/64 trên shared templates. Secondary greedy C=8/32, B=4/32, A=4/32; đúng đầy đủ chỉ ở `rule_constraint`. Không dùng 96 kết quả này để chọn checkpoint/điều chỉnh ngưỡng sau test.

## 1. Câu hỏi xác nhận và phạm vi phát biểu

**H1 chính duy nhất:** Trong một tập bài toán phản thực có **cấu trúc ngữ nghĩa chưa xuất hiện ở TRAIN**, huấn luyện cùng dữ liệu nhưng bổ sung contrastive objective (C) tăng tỷ lệ *sinh văn bản đúng ở cả hai điều kiện dữ kiện* so với counterfactual MLE (B), trên các seed độc lập, không chỉ cải thiện điểm teacher-forced candidate margin.

**H0:** Không có mức tăng bền vững C−B trên phép đo sinh tự do OOD đã khóa.

Mọi kết quả chỉ áp dụng cho mô hình Small4M / nguồn T1, thiết kế bốn dạng công việc xác định dưới đây. Không gọi là suy luận rộng khắp hoặc OOD tự nhiên.

## 2. Can thiệp một biến và đối chứng

| Arm | Corpus | Mục tiêu |
|---|---|---|
| A_BASE_MLE | condition-singleton có cân bằng nhãn/cue, ngân sách bằng B/C | MLE chuẩn |
| B_CF_MLE | cùng byte cặp counterfactual TRAIN với C | MLE chuẩn |
| C_CF_CONTRAST | **cùng byte** với B ở TRAIN và thứ tự episode | MLE + contrastive objective đã định nghĩa |

- **Giữ cùng parent P02 step1024**, tokenizer T1 BPE2048, core TinyStories train-only, optimizer, precision FP32, 256 updates/arm/seed, số microbatch và token slots, quy tắc checkpoint STEP256, max length, model parameter count như FC01 trong phần nào tương thích.
- **Các khác biệt mới cần thiết** cho benchmark cấu trúc OOD (corpus/structural grammar, free-generation prompt, parser) bắt buộc có phiên bản độc lập, SHA pin và QA *trước bất kỳ run*; không ngầm dùng bộ FC01 V2 cũ để gọi OOD.
- A vs B chỉ là **secondary data-effect**. Primary là **C vs B** để cô lập objective-only, không sửa loss coefficient/hyperparameter theo EVAL mới. B/C data equality là gate bắt buộc.
- Không chọn checkpoint theo EVAL; chỉ chấm đúng STEP256, không best-checkpoint selection. Không có TEST/Q1Q2 lịch sử hoặc dữ liệu D1 cũ trong scoring.

## 3. Cấu trúc dữ liệu và cô lập bộ đánh giá mới

Bốn category: `entity_location`, `causal_reasoning`, `rule_constraint`, `goal_persistence`.

**Đơn vị cấu trúc:** một `semantic_skeleton_id` quy định quan hệ biến, thứ tự bằng chứng/ngoại lệ và hướng chuyển trạng thái; **không** phải thay tên đồ vật, màu, tính từ, hoặc diễn đạt lại cùng một câu.

**Thiết kế tối thiểu dự kiến (chưa tạo dữ liệu):**
- Với **mỗi** category: 4 skeleton TRAIN + 4 skeleton `STRUCTURAL_OOD_EVAL` có graph/AST khác nhau. EVAL giữ sealed từ trước khi dựng TRAIN; không tái sử dụng id hoặc skeleton đẳng cấu đổi nhãn.
- TRAIN: 4 category × 4 train skeleton × 32 lexical worlds = **512 paired families**, hai điều kiện A/B mỗi family; lượng sampled episodes mỗi arm phải bằng nhau theo ngân sách khóa, không tự suy rằng A được xem cả hai.
- VAL: 4 category × 4 train skeleton × 8 lexical worlds riêng = **128 paired families**; VAL chỉ điều chỉnh khả năng code/source readiness *trước test*, **không** chọn lại weights, training updates hay hyperparameter.
- EVAL xác nhận: 4 category × 4 **novel structural** skeleton × 16 lexical worlds = **256 paired families**, mỗi family có hai prompt đối nghịch A và B = **512 prompt/arm/seed**. Mỗi category có 64 family/arm/seed. Tập EVAL giống tuyệt đối giữa ba arm và năm seed.
- Kiểm chứng độc lập đối với *graph isomorphism*, overlap theo AST/semantics, answer leakage, span/rights, split family, A/B counterfactual symmetry và B/C byte equality. Nếu một skeleton bị phát hiện gần trùng TRAIN: **HOLD toàn bộ**, không thay bằng bài mới sau khi nhìn outcome.
- Owner quản lý TRAIN/VAL; custodian khác role phát hành EVAL và answer keys sau SHA-custody lock. **Không tạo EVAL hay mở gold trong bước DESIGN này**. Reviewer blind chỉ có prompt/outputs và opaque ID; mapping không ở chung quyền truy cập với reviewer.

**Ví dụ minh họa không thuộc dataset/không được dùng làm fixture:** location với cập nhật vị trí theo thời gian; causal với chuỗi 2 bước có đảo chiều; rule với quy tắc ưu tiên khi xung đột; goal với mục tiêu duy trì qua một distracting instruction. Chúng chỉ mô tả **loại biến đổi cấu trúc**, không phải template/fixtures đã đóng băng.

## 4. Primary — free-generation paired exact semantic action

- Mỗi arm nhận riêng prompt không kèm `yA/yB` hay danh sách candidate. Greedy decoding **temperature không áp dụng, argmax token**, EOS hoặc tối đa **32 new tokens**, prompt ≤224 token để dành tối đa 32 new tokens trong context window 256, kiểm bằng tokenizer T1 thật. Không thêm postprocess để cứu output.
- Output yêu cầu **một câu hành động ngắn**. Scorer độc lập, *deterministic parser phiên bản được khóa trước test*, chuẩn hóa chỉ UTF-8, whitespace, punctuation và danh sách synonym cố định; trích `agent`, `action`, `target` và ràng buộc điều kiện. Những câu thiếu hành động, lặp vô nghĩa, mâu thuẫn, nhiều đáp án, thiếu phân biệt tình huống hoặc parser ambiguous = **0**, không gọi LLM rater để sửa primary.
- Với family `f` và arm `m`, định nghĩa `success(m,f)=1` **chỉ khi cả prompt điều kiện A và B đều được sinh câu đúng với gold riêng**; một câu đúng/ một câu sai → 0. Chấm ở mức family, không xem hai điều kiện là hai đơn vị độc lập.
- Primary estimator per seed `d_s = mean_f(success_C - success_B)`, category-weighted đều 4 nhóm. Hiệu ứng xác nhận = `mean_s d_s` trên năm seed.
- Ambiguous/invalid parser không loại mẫu; giữ denominator cố định 256 family/seed/arm, báo thêm `invalid_rate`, `early_eos_rate`, `truncation_rate`.
- Kiểm định độc lập parser bao gồm test fixture tích cực/âm, paraphrase-neutral/contrast negatives, các câu mâu thuẫn, nhãn sai, leakage. **Phiên bản parser phải khóa SHA trước khi EVAL gold/mapping được phép đọc**.

## 5. Seed, thống kê, ngưỡng và gate xác nhận

**Năm seed đóng băng trước dữ liệu:** `20261120`, `20261121`, `20261122`, `20261123`, `20261124`. Mỗi seed chạy đủ A/B/C từ **cùng parent checkpoint**; lịch sampler giữa B/C tương ứng và cùng ngân sách, khác loss. Không loại seed xấu; nếu một lượt thất bại kỹ thuật không có recovery đã tiền đăng ký thì **HOLD toàn bộ** chứ không cherry-pick hay thay seed.

**Một phép thử chính:** exact paired sign-flip một phía trên năm giá trị `d_s`, dưới H0 C−B ≤0, `alpha=0.05`, không kiểm định nhiều metric chính. Với năm seed, p nhỏ nhất theo kiểm định sign-flip một phía là `1/32=0.03125`; vì vậy đây là gate nghiêm ngặt và **không** nên diễn giải mức `+10pp` như ngưỡng đã có kiểm định riêng.

**Quyết định `CONFIRM_PRIMARY_GO` phải đạt đồng thời:**
1. Exact sign-flip `p_one_sided ≤0.05`.
2. Hiệu ứng quan sát `mean_s d_s ≥+0.10` (**≥+10 điểm phần trăm**).
3. **Không có category** nào có C−B trung bình âm; ít nhất **3/4 category** có C−B ≥+0.05, **và** accuracy tuyệt đối của C ≥25% trên **cả bốn category**. Đây là guard về hiệu quả đồng đều, tránh FC01 chỉ đạt tại `rule_constraint`.
4. Đủ 5/5 seed, đủ 256/256 family ×2 điều kiện mỗi arm/seed, tất cả checkpoint/rights/parser SHA và blind custody PASS.

Nếu 1–2 đạt nhưng 3 không đạt, chỉ có thể báo `POSITIVE_AGGREGATE_SCOPED_NOT_FOUR_CATEGORY`, **không** `CONFIRM_PRIMARY_GO`. Nếu không đạt 1/2 thì `NO_CONFIRMED_FREEGEN_GAIN`. Nếu thiếu chứng cứ hoặc lỗi protocol thì `HOLD/INVALID_PROTOCOL` chứ không tự bỏ qua.

**CI hỗ trợ (không thay gate):** percentile 95% bootstrap phân cấp seed→semantic skeleton→lexical family, 10.000 vòng, RNG seed `20261201`; báo cả per-category estimate+CI và per-seed d_s. Không coi 512 prompt cùng template là 512 mẫu độc lập.

## 6. Secondary, đo chất lượng và điều kiện độc lập

- Secondary (không quyết định GO): B−A `freegen_pair_success`; teacher-forced C−B margin trên cùng structural OOD; VAL NLL (report only); consistency A/B, parser invalid/earlyEOS/truncation; phân bố output duy nhất và theo category.
- Chấm mù AI/human riêng cho semantic acceptability và fluency, chỉ sau khi outputs và score rubric được khóa; **không override primary deterministic**. Reviewer thực sự fresh session/human, không nhận primary results, source code, mapping, seed hay lịch sử FC01; custodian giữ map riêng. Nếu không đạt độc lập, `RATER_INDEPENDENCE=LIMITED`, không đổi primary.
- Không tiếp tục sử dụng rubric FC01 posthoc 0–3 như thước đo xác nhận. Nếu dùng rubric từ D1 hiện hữu, phải chỉ rõ phiên bản và hợp đồng liên kết **trước khi phát hành data**, không chỉnh sửa D1 cũ.

## 7. One-packet GO/HOLD trước khi nghiên cứu mới

**Trạng thái design hiện tại:** `DESIGN_CANDIDATE_FROZEN_FOR_REVIEW`. **Không có D1 Science GO**.

Để quyết định một lần cho toàn bộ 5×3 arms ở giai đoạn tương lai, phải có cùng **một packet**: source+rights and license, 8 skeleton/category AST non-overlap QA, parser tests source QA, blinded gold sealed, five seed list and equal token budgets, locked code SHA, checkpoint and T1 pins, runtime readiness/actual resume behavior, free T4 + paid $0 resource feasibility and termination policy, independent reviewer GO/HOLD. **Không** làm 15 micro-permit; nếu một gate FAIL thì toàn batch HOLD và giữ nguyên khóa.

**Cấm trong operation này:** tạo dữ liệu TRAIN/EVAL mới, sửa checkpoint FC01, train, GPU, inference, chấm lại FC01, truy xuất TEST/Q1Q2/D1 sealed, ký science GO hoặc xem D1 gold. Mọi cải tiến thiết kế sau review phải là **amendment trước khi phát sinh outcomes** và lưu trace append-only; không cập nhật lặng lẽ bản V1.

## 8. Giao diện với D1 hiện hữu

Handoff `docs/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_INDEPENDENT_CHATGPT_BLIND_RATER_HANDOFF_20261112.md` đã định nghĩa một giao thức khác cho 512 generated outputs và rubric; **giữ nguyên file đó, không dùng nó như bằng chứng D1 đã được cấp GO**. D1 Bridge này là **đề cương độc lập để reviewer xem xét**, không cấp phép chuyển nội dung/nhãn từ D1 cũ sang nghiên cứu mới.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_D1_BRIDGE_SOURCE_ONLY_INDEPENDENT_PREREG_REVIEW_AND_GO_HOLD_NO_GPU`. Đánh giá thiết kế/hợp lý của template-split, parser và power/alpha; đưa **một quyết định design GO/HOLD**, chưa chạy science. Quyết định hiện tại **`GO_FC01_ARCHIVE_AND_D1_BRIDGE_DESIGN_ONLY; HOLD_D1_SCIENCE`**.
