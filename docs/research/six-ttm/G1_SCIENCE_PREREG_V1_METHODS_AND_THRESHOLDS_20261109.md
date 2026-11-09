# SIX × TTM — G1: hợp đồng tiền đăng ký khoa học định lượng (ứng viên khóa v1)

**Ngày:** 2026-11-09  
**Trạng thái:** `SCIENCE_PROTOCOL_SPECIFIED / CONDITIONAL_FREEZE_CANDIDATE / INDEPENDENT_REVIEW_PENDING / SCIENCE_EXECUTION_HOLD`  
**Nhánh nguồn:** `research/ttm-six-cross-model-representation-transfer-20261109`. **Không** được dùng tài liệu này để tự động chạy khoa học, huấn luyện, hoặc đồng bộ `main`.  
**Machine-readable contract:** `docs/research/six-ttm/G1_SCIENCE_PREREG_V1_CONTRACT_CANDIDATE_20261109.json` (tệp JSON là nguồn giá trị định lượng; nếu có xung đột phải sửa cả hai trước science và ghi phiên bản mới).  
**Tham chiếu bất biến:** SIX source pin G0, hợp đồng G1/G3 draft, bằng chứng technical G1 v3 PASS kỹ thuật (`docs/research/six-ttm/G1_V3_COLAB_TECHNICAL_SMOKE_PASS_OWNER_RECEIPT_QA_AND_G1_GATE_20261109.md`). Không xóa hoặc làm sạch các STOP v1/v2.

## 1. Vấn đề khoa học chính và phát biểu giới hạn

**RQ-G1:** Từ trạng thái ẩn `h_S(x)` của Qwen3-0.6B (source), có thể học ánh xạ `A` sang không gian `h_T(x)` của Qwen3-1.7B (target) trên các tiền tố văn bản giống nhau về bytes, sao cho vector căn chỉnh giữ đủ thông tin để dự báo **phản ứng chức năng** của 1.7B trước một tập 8 cặp câu tiếp nối được xác định **trước khi chạy** hay không?

- **H0 (null):** phép căn chỉnh không vượt được đối chứng tráo cặp/đối chứng trung bình trên các câu chuyện giữ riêng.
- **H1 (đánh giá feasibility có giới hạn):** phép căn chỉnh dự báo thành phần phản ứng chức năng Qwen3-1.7B trên TEST tốt hơn các đối chứng âm tính theo tiêu chí khóa trước, cùng với CKA có bằng chứng căn chỉnh hình học.
- Không được tuyên bố bất biến phổ quát, SIX BASIS15 cần thiết, hoặc lợi ích huấn luyện TTM. Bài G1 **không** so sánh output distillation vs SIX functional transfer trên TTM; đó là G3.
- Phép đối chiếu trực tiếp `source hidden -> target functional response` là đối chứng **quan trọng**, không chỉ đối chứng tráo nhãn. G1 có thể cho kết quả chuyển thông tin hữu ích nhưng **chưa chứng minh phương pháp SIX ưu việt** hơn một linear probe thông thường.

## 2. Mô hình, phiên bản, quyền

**Model A:** `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca`; 28 lớp, hidden=1024. Trọng số SHA-256 `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b`. Colab T4 technical smoke 29 hidden states `[2,39,1024]`, PASS theo biên bản owner và kiểm toán tính nhất quán 11/11. **Không chạy lại** lượt đã tiêu thụ.

**Model B:** `Qwen/Qwen3-1.7B@70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`; 28 lớp, hidden=2048; file trọng số ở pinned revision là **hai shard** `model-00001-of-00002.safetensors`, `model-00002-of-00002.safetensors`, và `model.safetensors.index.json`. Đã xác nhận danh sách file trên model repo, **chưa tải và chưa tính SHA-256 thực tế của model B, chưa smoke hidden states 1.7B**. Model B là điều kiện bắt buộc cho bài thử cross-model này, không được âm thầm thay bằng hai layer của 0.6B hoặc claim đã PASS kỹ thuật.

Giấy phép của cả hai model: metadata `Apache-2.0`; cần giữ LICENSE/notices. Không suy diễn giấy phép model giải quyết quyền corpus. Dữ liệu ứng viên là `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, metadata `CDLA-Sharing-1.0` — **không phải Apache**. TTM pilot T1 đã kiểm tra nguồn và chia tập có giới hạn; điều này không phải chứng từ phê duyệt cho việc sử dụng TinyStories để xuất các teacher features và kiểm thử mới. Quyền nghiên cứu G1 của chủ sở hữu và điều kiện giữ/không công bố corpus/derived outputs vẫn **HOLD**.

### Quy tắc dữ liệu nghiêm ngặt

Chỉ lấy từ **2.048 truyện thuộc TTM pilot TRAIN** tại manifest T1 (`sha256=9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`); SHA file nguồn TRAIN gốc `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`. **Không đọc TTM pilot VAL (256) / TEST (64)**. Không đọc hoặc tiết lộ bản raw trên GitHub. Chưa có readback actual manifest bytes trong lane này, nên danh mục đủ 256 sample **chưa được xác minh**.

- Phân chia G1: **TRAIN 128 truyện, DEV 64 truyện, TEST 64 truyện**; tối đa một prefix/truyện, zero exact-overlap toàn ba phần. TEST G1 là *khác* TEST của TTM.
- Duyệt tối đa 2.048 TRAIN theo source_row_index, chuẩn hóa story Unicode NFC, CRLF/CR→LF, trim mép và thay newline bằng dấu cách, không lowercase. Tạo prefix bắt đầu từ ký tự đầu cho tới **dấu câu kết thúc câu đầu tiên** có offset Unicode nằm từ 80 tới 192 inclusive; không có thì dùng khoảng trắng đầu tiên ở offset từ 128 tới 192; loại không thỏa. Hai tokenizer Qwen được chạy riêng, `add_special_tokens=False`; loại nếu số token của model nào ngoài [8,96]. Không cắt token riêng từng model.
- Mã khóa lựa chọn: `SHA256(UTF8('TTM_SIX_G1_V1|' + source_row_index + '|' + sha256(story_NFC_UTF8)))`. Sắp thứ tự từ điển tăng dần trên các candidate hợp lệ; lấy 128 TRAIN / tiếp 64 DEV / tiếp 64 TEST. Các giá trị seed khác không được đổi sau xem kết quả. Nếu số mẫu hợp lệ <256 → **HOLD_PRE-SCIENCE**, không đổi âm thầm ngưỡng.
- Ghi `source_row_index`, SHA story, SHA bytes prefix, offset Unicode, split, số token mỗi tokenizer và mã phiên bản preprocessing. Không ghi raw truyện. So sánh exact cross-story SHA; near-duplicate gốc chỉ có audit có giới hạn, không nhận là full-corpus proof. Các nhóm leakage diagnostics dùng metadata đã niêm phong, không chọn model dựa trên TEST.

## 3. Cặp input liên mô hình và tensor xuất

Một hàng = `(source_row_index, prefix_utf8_sha256, prefix_end_offset)`. **Cùng chuỗi Unicode/UTF-8** được cung cấp cho cả hai teacher, nhưng tokenized **riêng**; không cặp theo chỉ số token. Model `eval()`, `torch.inference_mode()`, `use_cache=False`, `output_hidden_states=True`, `return_dict=True`, `dtype=float16` trên T4.

- Trạng thái chính: `hidden_states[28][row,last_nonpad_position,:]`. 0.6B `[1024]`; 1.7B `[2048]`. Không lấy `hidden_states[0]` làm positive control vì input cuối giống nhau có thể gây trùng embedding.
- Layer 14 là **diagnostic only**, không được dùng chọn kết quả có lợi sau nhìn DEV/TEST. Mask phải đúng với left/right padding; batch science pin = **1** để tránh padding khác biệt và giảm VRAM.
- Model không huấn luyện; extract tuần tự để tránh nạp 2 teacher cùng lúc. Model B tải đúng 2 shard & index tại revision, SHA từng tệp trước khi load; file hashes và tokenizer/CONFIG/Licenses của B phải pin trước science. Lưu embedding/score trong artifact riêng private, có SHA và mapping story_id; không đưa tensor hàng loạt lên GitHub.

## 4. Phép dò chức năng cố định (functional probe bank)

Mỗi prefix `x` được chấm 8 cặp continuation dưới từng teacher bằng `r_{m,j}(x) = logP_m(a_j|x)/bytes(a_j) - logP_m(b_j|x)/bytes(b_j)`. Các câu tiếp nối chỉ dùng để tạo **phản ứng của mô hình**, không lấy câu trả lời đúng từ truyện, không sinh văn bản.

| j | Continuation A | Continuation B |
|---|---|---|
| 1 | ` The child smiled.` | ` The child cried.` |
| 2 | ` Everyone felt safe.` | ` Everyone felt afraid.` |
| 3 | ` The toy was found.` | ` The toy was lost.` |
| 4 | ` She told the truth.` | ` She told a lie.` |
| 5 | ` He shared the toy.` | ` He kept the toy.` |
| 6 | ` They stayed home.` | ` They went outside.` |
| 7 | ` The door was open.` | ` The door was closed.` |
| 8 | ` The story ended happily.` | ` The story ended sadly.` |

**Token boundary contract:** tokenize prefix riêng và continuation riêng với `add_special_tokens=False`, rồi nối **token IDs** (không tokenize lại chuỗi text x+c). Tính likelihood từng token continuation theo causal shift trên prompt IDs; không áp chat template, EOS, thinking markers, generation hoặc sampling. Chia tổng `log P` cho số byte UTF-8 **positive** của continuation, không chia số token để tránh phụ thuộc riêng từng tokenizer. `r_T(x)` của Qwen1.7B là **đầu ra chức năng đích**. Mean/std của các chiều `r_T` chỉ tính từ TRAIN; áp lại DEV/TEST, `epsilon=1e-6`.

**Giới hạn:** 8 cặp câu ứng viên là một mẫu phản ứng hành vi hẹp, có thể chứa thiên lệch về prior/ngữ pháp/số byte; không suy ra causal knowledge, reasoning, compositional invariance hoặc semantic correctness chỉ từ bank này. Không tune các câu dựa trên kết quả.

## 5. Ánh xạ, đối chứng, lựa chọn trước TEST

Đối với từng `x`: `s=h_{0.6}(x)∈R^1024`, `t=h_{1.7}(x)∈R^2048`, `r=r_{1.7}(x)∈R^8`.

**Pipeline chính (G1-A):** huấn luyện `A: s -> t` bằng ridge multioutput TRAIN-only (dual form), và `P: t -> r` bằng ridge TRAIN-only. Dự báo `r_hat=P(A(s))`. Chuẩn hóa mỗi chiều vector trên TRAIN (mean/std + `epsilon=1e-6`), lưu mọi mean/std; intercept từ TRAIN. Không fine-tune teacher.

**Đối chứng và chức năng:**
- `B-direct`: một ridge `s -> r` trên TRAIN, lựa chọn cùng grid để kiểm tra phương pháp căn chỉnh có thực sự bổ sung hay kém một linear probe thường.
- `C-oracle`: ridge `t -> r`, positive-control kiểm tra bank dự đoán được từ target hidden; nếu control FAIL, thí nghiệm về chuyển giao **INCONCLUSIVE** chứ không đổ lỗi cho SIX.
- `D-shuffle`: tráo ngẫu nhiên cặp `s_i↔t_i` ở TRAIN 1.000 permutation với seed cố định; `P` và mọi TEST input target giữ chuẩn, không thay dữ liệu ngoài split.
- `E-mean`: dự báo trung bình TRAIN của `r_T`.
- `F-random`: random orthogonal projection của `s` với cùng số chiều/nguồn train, seed cố định; báo cáo phụ. CKA raw/shuffle và retrieval@1 cũng là diagnostics về mặt hình học.

`alpha ∈ {1,10,100}`; chọn bằng **DEV macro functional R²** sau khi chạy tất cả ứng viên; hòa điểm chọn alpha lớn hơn. Một khi chọn xong, không đổi alpha/layer/bank/cách tokenize trên TEST. Tuyệt đối không dùng TEST để fit, chọn rank, chọn ánh xạ, debug hoặc quyết định rerun.

## 6. Chỉ số và quy tắc khoa học định lượng

**Primary scalar:** `macro_R2` qua 8 cặp continuation trên **TEST 64 truyện**, tính `R² = 1 - SSE/SST` với SST so với trung bình TRAIN (không fit thêm trung bình TEST). `gain = R2_aligned - percentile_95(R2_shuffled_null)`. `p_perm = (1 + #{null>=observed})/(1001)`. Thực hiện 2.000 bootstrap theo **story_id** (paired) cho **ΔR²_aligned−TRAIN_mean** với seed riêng `20261111`; dùng cùng danh sách story IDs trong mỗi lần lấy mẫu cho cả aligned và mean. Phân vị 95% của 1.000 null fits chỉ tính **một lần** trên TEST niêm phong, không lặp 1.000 null permutations trong mỗi bootstrap. Mọi negative fitted model được chọn alpha bằng DEV theo **cùng grid và quy tắc** như aligned model. CKA primary layer 28 có kiểm định shuffle riêng 1.000 lượt.

**Các ngưỡng ứng viên khóa trước TEST** (xem cùng giá trị trong JSON):

1. `R²_aligned ≥ 0.10`.
2. `gain_aligned_vs_95th_shuffle ≥ 0.10`.
3. `p_perm ≤ 0.01`, paired-bootstrap 95% lower bound của **ΔR²_aligned−TRAIN_mean** > 0. Không tráo lẫn CI so với mean và ngưỡng hiệu lực so với shuffle.
4. `p_CKA_perm ≤ 0.01` (chỉ hình học, không thay functional).
5. `R²_target_oracle ≥ 0.20` để đủ khả năng kết luận; nếu oracle không đạt, trạng thái `INCONCLUSIVE_CONTROL_UNQUALIFIED`.

Báo cáo **B-direct** đầy đủ: nếu mapping A yếu hơn đáng kể B, không được gọi lợi ích riêng của SIX, dù có PASS kỹ thuật/functional. Cần **hai cổng functional và geometric** cùng đạt; thống kê phụ có nhiều phép kiểm không tự nâng thành PASS. Không dùng ngưỡng G3 (NLL, 2%, A–E student) làm kết quả G1. Không có kết luận về ứng dụng công nghiệp.

**Định nghĩa và cổng ổn định số học được đóng băng:** Với mỗi probe j, `R²_j=1 - [Σ_TEST(rhat_ij-r_ij)^2]/[Σ_TEST(r_ij-mu_TRAIN_j)^2]`, `macro_R2=mean_j R²_j` trên **đủ cả 8 chiều**, không loại chiều sau khi thấy TEST. Trước khi đọc TEST, nếu **bất kỳ** probe nào của teacher 1.7B có `population std_TRAIN <1e-5` thì kết luận `INCONCLUSIVE_CONTROL_DEGENERATE_PRETEST`, **không** thay probe hoặc bỏ chiều. Trên TEST mở một lần, nếu bất kỳ `SST_j <1e-8` thì `INCONCLUSIVE_DEGENERATE_TEST`, không dùng mẹo đổi mẫu/TEST. Các đặc trưng ẩn khác chuẩn hóa TRAIN-only, dùng denominator `max(std,1e-6)`. Các ngưỡng này là chọn trước science, không phải số đo thực nghiệm.

**Giới hạn chồng lấn tiền huấn luyện:** Mẫu TEST của G1 chỉ được giữ riêng khỏi việc fit các ridge trong G1. Không có bằng chứng Qwen3 chưa từng thấy TinyStories lúc tiền huấn luyện, vì vậy không gọi đây là phép thử chống contamination ở cấp dữ liệu tiền huấn luyện mô hình lớn.

**Hạn chế power:** `n_TEST=64` là một thử nghiệm feasibility nhỏ, chưa có mô hình power 80% được hiệu chuẩn từ effect-size độc lập. G1 chỉ là *scoped feasibility*, không phải kiểm định xác nhận tính phổ quát. Không được diễn giải `p>0.01` là chứng minh không chuyển được. Nếu thiếu power hoặc positive control không đủ → `INCONCLUSIVE`; chỉ adjudicate `FAIL_SCOPED` khi contract đủ điều kiện và âm tính có sức phân biệt. Bất kỳ tuyên bố confirmatory rộng hơn đều cần bổ sung nghiên cứu power trước khoa học và thẩm định riêng.

## 7. Điều kiện một lượt science admission (không chia nhỏ giấy phép)

- Quyền TinyStories dùng riêng trong G1 được chủ sở hữu chấp thuận; thông báo `CDLA-Sharing-1.0`, phương án lưu trữ derived features và attribution chốt; không tự phát tán corpus. Đối chiếu SHA/source T1 pilot thực tế.
- G1 manifest TRAIN-only, 128/64/64, zero exact split overlap, no TTM VAL/TEST access, eligible đủ 256 được tạo và ghi SHA, nhưng **không chạy science hoặc xem functional outputs** trong readiness.
- Qwen3-1.7B hai shard, index, tokenizer, config, LICENSE đều pin SHA-256 bytes thật; trên T4 một capacity smoke zero-science giới hạn xác nhận 29 tensors/shape/finite/VRAM; **không** coi 0.6 smoke PASS thay thế.
- `Python=3.13.x stable` ghi patch thực; `torch=2.14.1+cu130`, `transformers=5.22.1`, `huggingface-hub=1.33.0`, `tokenizers=0.23.3`, `safetensors=0.8.0`. T4 FP16, batch=1, prompt<=96 tokens, total free GPU>=11GiB, free disk>=12GiB, cap peak GPU<=12GiB, **max wall 60 phút/mô hình, 120 phút tổng**, không dùng GPU trả phí. Tải/đọc model tuần tự, dọn bộ nhớ CUDA khi đổi teacher.
- Có runner khoa học đọc đúng manifest và phân vùng, xuất receipts, kiểm âm tính rò rỉ, thực hiện ONE-SHOT sau độc lập QA. Chưa có runner này.
- Hợp đồng dữ liệu, probe bank, sampling, metric, thresholds, kiểm soát thống kê và power đủ để reviewer độc lập nhận xét và chủ sở hữu ra quyết định rõ `AUTHORIZE / HOLD`.

**Trạng thái hiện tại:** `DESIGN_CANDIDATE_SPECIFIED`; `SCIENCE_LOCK=HOLD`; `G1_FIRST_SCIENCE_RUN=NOT_AUTHORIZED`. QA khoa học độc lập chưa hoàn tất chỉ bằng việc tác giả tự đọc lại thiết kế. Không bổ sung `lineage.md` vì chưa có kết quả thực nghiệm khoa học.

## 8. Bước thực hiện tiếp theo

`TTM_SIX_XMODEL_G1_DATA_RIGHTS_SOURCE_MANIFEST_AND_QWEN17_READINESS_INTEGRATED_GATE`: kiểm định một lượt quyền dữ liệu, manifest TRAIN-only và Qwen1.7B sharded checksum/smoke giới hạn; sau đó **một** review khoa học độc lập & phán quyết khóa G1. Không chạy lại kỹ thuật Qwen0.6B đã PASS và không chặn tuyến TTM-Small-4M.
