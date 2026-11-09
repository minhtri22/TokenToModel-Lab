# SIX × TTM — Tiền đăng ký nháp cho thử nghiệm chuyển giao biểu diễn liên mô hình

**Ngày:** 2026-11-09  
**Trạng thái:** `G0_PREREG_DESIGN_DRAFT / NOT_SCIENCE_LOCKED / NO_MODEL_LOAD / NO_TRAIN`  
**Nhánh:** `research/ttm-six-cross-model-representation-transfer-20261109`  
**Phụ thuộc:** `UPSTREAM_SIX_PINS_AND_CHARTER_20261109.md`, `G0_PIN_AUDIT_AND_QWEN_FEASIBILITY_20261109.md`.  
**Bảo toàn:** `main` tiếp tục TTM-Small-4M. PR #12 tiếp tục theo chủ sở hữu; không chỉnh sửa, merge hoặc mở lại phase TTM. Tài liệu này là **đề cương định lượng**, chưa phải giấy phép thực nghiệm.

## 1. Câu hỏi khoa học và phạm vi

**RQ1:** Trên cùng tập tiền tố văn bản, biểu diễn ẩn của hai mô hình Qwen3 khác quy mô có thể được căn chỉnh ngoài tập TRAIN, vượt qua đối chứng tráo cặp và ngẫu nhiên, hay không? Tương quan hình học không tự chứng minh tính đủ theo nhiệm vụ.

**RQ2:** Một biểu diễn **hành vi theo các phép dò cố định (functional response to a probe bank)** lấy từ mô hình nguồn có thể tạo tín hiệu huấn luyện hữu ích cho TTM-Small-4M hơn chưng cất chuỗi đầu ra và chưng cất trạng thái ẩn trực tiếp hay không? Sau huấn luyện, TTM phải tự chạy, không cần teacher.

**H0 chính (G3, chưa khóa ngưỡng):** bổ sung tín hiệu biểu diễn SIX không giúp hạ NLL trên các truyện giữ riêng so với cả hai đối chứng chưng cất thông thường trong điều kiện tài nguyên tương đương.  
**H1:** D (SIX-functional transfer) đạt NLL thấp hơn B (sequence-level distillation) **và** C (generic feature distillation), đồng thời tốt hơn A/E trong phạm vi ngân sách được khóa và không tăng phụ thuộc teacher khi suy luận.

Cần tránh các kết luận vượt bằng chứng:
- `BASIS15` của SIX chỉ là một ứng viên phương pháp, **không** đặt cứng mọi LLM phải có 15 chiều.
- `SIX OW1` đã cho thấy phép chuyển subspace thẳng có thể FAIL dưới dịch chuyển phân phối.
- Kết quả R1/R2 (so khớp biểu diễn) không đồng nghĩa TTM cải thiện; chỉ G3 mới trả lời RQ2.

## 2. Hợp đồng mô hình, dữ liệu và tài nguyên

| Thành phần | Khóa ứng viên hiện có | Còn thiếu để science lock |
|---|---|---|
| Teacher A | `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca` | Hash file tải, version `transformers/torch`, readback shape/numeric smoke |
| Teacher B (chỉ đối chiếu RQ1) | `Qwen/Qwen3-1.7B@70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` | Như trên; có thể để sau nếu không đủ VRAM |
| Student | TTM-Small-4M ứng viên P02 3,749,376 tham số, 4 layer, width 256, 4 head, context 256, vocab 2048 | Commit và checkpoint **đã train** từ pilot T4, exact tokenizer/checkpoint SHA, các bài kiểm tra model parity |
| Corpus | Ưu tiên cùng miền TinyStories pilot; subset đã xác minh 2048 TRAIN / 256 VAL / 64 TEST truyện | Quyền/chế độ dùng corpus cho nghiên cứu mới, subset manifest exact, near-dup limitation, split test seal |
| Thiết bị | Free Colab GPU (ứng viên), Google Drive READY-last | Runtime, GPU loại thực tế, quota VRAM/RAM, thời gian tối đa, storage manifest, capacity smoke |
| Phiên bản | Python, PyTorch, Transformers, NumPy, tokenizer, adapter | Lock file và SHA source; reproducibility manifest |
| Seed | Cùng seed đối chứng mỗi lượt; ít nhất 1 feasibility run, xác nhận nhiều seed nếu có nguồn lực | Giá trị seed và số lượt khóa trước science; 1 seed chỉ cho pilot, không đủ khẳng định ổn định |

**Quy tắc:** không dùng data/model teacher từ Hugging Face `main` động; không dùng dữ liệu TEST để huấn luyện tokenizer, chọn probe, chọn rank, chọn layer, chọn loss weight, chọn checkpoints hay chưng cất teacher. Qwen và TTM có tokenizer khác nhau; không KL trực tiếp theo vocabulary ID.

## 3. Phép thử đầu tiên — G1 khả năng căn chỉnh biểu diễn (readiness → science sau lock)

**Thiết kế:** dùng các tiền tố văn bản giống nhau ở cấp chuỗi ký tự, được mã hóa độc lập bởi tokenizer mỗi mô hình. Định nghĩa một mẫu quan sát là `(story_id, prefix_end_char_offset, raw_text_sha256)`; không tạo cặp theo chỉ số token.

- Đầu vào ứng viên: 128 TRAIN prefixes từ truyện tách biệt và 64 VAL prefixes từ truyện khác, cùng length cap theo bytes/chars khóa trước; các số này là **ứng viên**, không dùng nếu xung đột quyền/tập dữ liệu.
- Frozen teachers `model.eval()`, forward `output_hidden_states=True`, no grad, `use_cache=False`. Đo last nonpadding token hoặc masked mean pooling; cách lấy cố định trước khi xem VAL. Báo cáo layer index và tensor shape (Qwen 0.6B width 1024; Qwen 1.7B width 2048). Không xuất toàn bộ tensor hàng loạt.
- Fit căn chỉnh linear/orthogonal hoặc ridge **trên TRAIN**; chọn mức regularization và layer bằng một VAL phụ được quy hoạch trước, không dùng TEST; có đối chứng random orthogonal, shuffled pairs, shuffled prompts, dimensionality-matched PCA, và nhãn story để chống nhận dạng cùng câu chuyện.
- Chỉ số: held-out CKA (trên cùng sample IDs), retrieval@1 trong tập ứng viên được kiểm soát, linear predictive probe cho đặc trưng nhiệm vụ định sẵn; báo cáo permutation/null distribution và khoảng bất định phù hợp. CKA cao tự nó không đủ PASS chức năng.
- G1 chỉ đủ điều kiện đi G2 nếu hình học và ít nhất một **task-functional check** cải thiện trên dữ liệu chưa dùng fit so với negative controls; cổng định lượng và số mẫu phải khóa trước khi mở science. Nếu không, `G1_FAIL_OR_INCONCLUSIVE`, không tiến G3 theo phép biến đổi chưa kiểm định.

**Kiểm thử kỹ thuật trước G1 science:** chỉ một `offline/zero-science integrated smoke` để đọc config/revision, xác nhận `hidden_states` số lượng, shape, finite, masking, GPU/RAM, seed determinism trên synthetic prefix; không cần quy trình cấp phép độc lập cho từng subcheck.

## 4. Cơ chế SIX ứng viên, phân biệt với chưng cất đặc trưng thường

Chưng cất trạng thái ẩn trực tiếp: teacher tensor `h_T(x)` → adapter tuyến tính `P_T(h_T)` → loss so với student `P_S(h_S)`. Phép này có thể học được nhưng **không tự gọi là đóng góp SIX**.

**SIX-functional candidate:** định nghĩa trước một bank các phép dò chức năng (fixed probe bank) trên cùng ngữ cảnh, ví dụ một số cặp continuation ngắn có ý nghĩa và có độ dài kiểm soát; điểm số là hiệu số log-likelihood teacher của hai continuation được so sánh, có chuẩn hóa độ dài phải khóa trước. Với mỗi tiền tố x, tạo vector kết quả `r_T(x)`; fit phép chiếu từ tập TRAIN `R_T(x) = U_k^T (r_T(x) - mu_train)`. Rank k ứng viên `4/8/15`, chỉ chọn theo TRAIN/VAL, không coi 15 là rank thực nghiệm phổ quát. Teacher score phải lấy từ logits/likelihood đúng theo tokenizer Qwen và input prefix, không dùng oracle privileged hoặc đánh giá TEST.

Loss student ứng viên:
`L_D = L_next_token + lambda * distance(g_theta(h_TTM(x)), stopgrad(R_T(x)))`.
`g_theta` chỉ dùng trong quá trình huấn luyện và **không cần tại suy luận**. Cần kiểm tra không rò rỉ nhãn (target leakage) và thông tin khép kín qua probe bank. Chọn `lambda`, rank, bank, norm, loss function qua TRAIN/VAL trước khi TEST; mọi candidate bị loại phải ghi lại.

**Điều kiện để gọi là hiệu quả của SIX:** D phải vượt **C = chưng cất đặc trưng trực tiếp cùng mức tham số adapter** và B = chưng cất đầu ra thường, chứ không chỉ vượt mô hình gốc A. Nếu D tốt hơn A/B nhưng không hơn C, kết luận chỉ là feature distillation hữu ích, chưa quy công cho SIX.

## 5. G3 — Thử nghiệm phân biệt với chưng cất thông thường (chờ TTM baseline)

| Nhóm | Training loss / tín hiệu | Chức năng |
|---|---|---|
| A — baseline | Chỉ `L_next_token` trên TRAIN đã khóa | Đối chứng TTM chuẩn |
| B — output distillation | `L_next_token` cộng dữ liệu/continuations teacher tạo **chỉ từ TRAIN**, kiểm soát tổng token và nguồn | Đối chứng chưng cất chuỗi đầu ra |
| C — generic hidden-state distillation | `L_next_token` + tín hiệu trạng thái ẩn trực tiếp từ teacher, projection width 256 | Đối chứng chưng cất biểu diễn thông thường |
| D — SIX-functional | `L_next_token` + tọa độ functional-response/probe basis của teacher do SIX-inspired method xác định | **Giả thuyết nghiên cứu chính** |
| E — shuffled target | Tương tự D nhưng tráo cặp `x -> R_T(x')` giữa truyện/tiền tố TRAIN, với cùng ngân sách | Đối chứng âm tính |

B phải dùng cùng split và `student tokenizer` với A/C/D/E; không đối chiếu KL thô giữa 151936 vocab Qwen và 2048 vocab TTM. C và D phải có **số tham số bổ sung tương đương** hoặc ghi rõ phép hiệu chỉnh cho chênh lệch; tất cả nhóm báo cáo student compute, teacher extraction compute, wall time, số token gốc/gia tăng, VRAM, checkpoint byte size, và inference compute của student độc lập. Nếu bất khả thi trong một ngân sách, dừng để sửa **thiết kế trước khoa học**, không âm thầm đổi sau khi thấy kết quả.

**Primary metric:** story-level validation/test NLL tính theo **TTM tokenizer thống nhất** và trên cùng câu chuyện. Primary contrast là `NLL_D < min(NLL_B, NLL_C)` trên giữ riêng, có kiểm tra chênh lệch story-level bằng paired bootstrap hoặc phương pháp đã khóa; yêu cầu D cũng vượt negative control E. Báo cáo learning curve/sample efficiency và teacher cost như secondary, không biến metric phụ thành PASS chính.

**Ngưỡng thiết kế ứng viên, CHƯA KHÓA:** D tốt hơn đối chứng mạnh nhất B/C tối thiểu 2% về VAL NLL tương đối, paired bootstrap 95% CI cho gain không bao gồm 0, và kết quả cùng chiều qua nhiều seed confirmatory. Chỉ một seed pilot hoặc 64 truyện TEST có thể thiếu power; phải tính khả năng phát hiện hiệu ứng trước khi đóng băng điều kiện PASS. Nếu không đủ lực kiểm định, báo cáo `INCONCLUSIVE`, không cưỡng ép PASS/FAIL.

**Quy tắc TEST:** Chỉ sau chốt tất cả phiên bản, thuật toán, hyperparameters và lựa chọn bằng VAL; dùng một lần chính thức. Không rerun vì kết quả không như kỳ vọng, không chuyển threshold sau xem TEST. Ràng buộc thời gian/VRAM kết thúc STOP theo ngưỡng đã khóa, giữ receipt.

## 6. Hành động và tiêu chí đóng hữu hạn

**G0 (lượt này):** audit pins, nguồn Qwen, soạn prereg → `DESIGN_COMPLETE` nếu tài liệu đủ; không có science lock.  
**G1 readiness:** khóa đường loader/model, một smoke synthetic, quyền dữ liệu, dataset/probe/layer/seed/budget/negative controls; thẩm định tập trung **một lần** trước science.  
**G1 science:** căn chỉnh teacher-to-teacher theo contract đã khóa, đọc kết quả và adjudication PASS/FAIL/INCONCLUSIVE.  
**G2:** kiểm tra chức năng held-out và khả năng chuyển qua teacher → student không dùng TEST.  
**G3:** chỉ khi TTM-Small-4M checkpoint đã train/QA/lock, chạy nhóm A–E và phán quyết khoa học độc lập.

**Các HOLD bắt buộc:** `QWEN_RUNTIME_HIDDEN_STATES=NOT_TESTED`; `QWEN_FILES_SHA=NOT_PINNED`; `MODEL_LICENSE_ATTRIBUTION_AND_DATA_RIGHTS=REVIEW_PENDING`; `PROBE_BANK_EXACT=NOT_FROZEN`; `BUDGET_AND_METRIC_THRESHOLDS=NOT_FROZEN`; `TTM_T4_TRAINED_BASELINE=NOT_AVAILABLE`; `G1/G3_SCIENCE_AUTHORIZATION=NOT_GRANTED`.

Không ghi vào `lineage.md` ở G0, không merge PR, không thay `main`, không tạo worktree hoặc xóa file. Kết quả lỗi khoa học tương lai vẫn ghi `lineage.md` append-only sau QA và phán quyết độc lập; kỹ thuật vào `docs/qa` hoặc receipt riêng.

**Bước thực hiện tiếp theo:** `TTM_SIX_XMODEL_G1_ZERO_SCIENCE_QWEN_HIDDEN_STATE_SMOKE_SPEC_AND_INTEGRATED_LOCK_REVIEW`. Thiết kế và kiểm tra thông số để chỉ sau đó chạy một smoke kỹ thuật synthetic có kiểm soát; không tự bắt đầu huấn luyện TTM hoặc Qwen.
