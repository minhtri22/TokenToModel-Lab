# TTM R2A → O0/O1 — Thiết kế đối chứng công bằng về giám sát, tham số và tính toán

**Ngày:** 2026-11-10 · **Trạng thái:** `DESIGN_ONLY_INTERNAL_OWNER_WEB_CODEX`, chưa tiền đăng ký science mới, chưa có phản biện Codex R2A, không huấn luyện hay suy luận neural.  
**Dự án:** `minhtri22/TokenToModel-Lab`, nhánh `research/ttm-small4m-semantic-state-goal-toy-r2-20261110`. R2A gốc đến `d7128812ce7f98eb0c6087b4649822bc999d1088`; tất cả dữ liệu 384 input và 256+128 bản ghi oracle đã được commit nguyên byte **sau commit R2A gốc**, có [manifest](../../artifacts/qa/ttm-r2-semantic-toy/r2a/R2A_COMPLETE_GITHUB_CUSTODY_MANIFEST_20261110.json). Không sửa PR13 hoặc nhánh 2×2.

## 1. Phân biệt 4 mệnh đề trước khi xem xét kiến trúc

- **H-ORDER:** cặp R2A A/B có cùng tập từ nhưng đảo hai cập nhật nên predictor chỉ dựa bag-of-words trên mỗi cặp ≤50%. Đây là **hệ quả tổ hợp**; mô hình Transformer có vị trí có thể giải được.
- **H-BINDING:** câu hỏi nêu thực thể nào; cùng một truyện hỏi thực thể khác cho đáp án khác. R2A có 128 probes, nhưng quy tắc `latest value for queried key` đạt 256/256 mà không cần learned persistent slot. Đây là **cơ chế đúng của toy**, chưa chứng minh kiến trúc.
- **H-STATE:** duy trì trạng thái biến đổi, ràng buộc thực thể/goal qua nhiều bước/đại từ, chuyển giao gián tiếp, xóa/thay mục tiêu có thể giúp so với ghi nhớ n-gram/position. **Chưa kiểm định với TTM**.
- **H-LEARNING:** đầu phụ trạng thái (O1) cải thiện chất lượng, đạt hiệu quả tham số và khả năng tổng quát hóa so với decoder-only O0. **CHƯA có bằng chứng, phải bác bỏ được.**

**R2A public dataset không phải tập TEST kín.** `R2A_ORACLE_DATASET.json` chứa câu trả lời công khai, và thứ tự hàng tương ứng 384 `story/question`. Không dùng tập này làm scientific held-out hoặc để chọn `O1` theo hậu nghiệm. Reviewer được đọc oracle để QA **mã**, không được gọi đó là blind semantic review.

## 2. Những lối tắt cần Codex phản biện

1. Template `DEV` và `CHALLENGE` có định dạng khác nhau nhưng **cả hai đã công khai**; không phải unseen syntax sau khi xem mã.
2. Một quy tắc không có learned latent state nhưng dùng `question-key + latest relevant assignment` đạt 100%; do đó vị trí cân bằng **không đủ** để buộc neural model tạo module trạng thái riêng.
3. Thực thể có hai cập nhật trong truyện 4 câu; luôn có đúng hai keys, mỗi key hai cập nhật và 4 giá trị khác nhau. Bài toán có thể giải bằng bộ tìm kiếm token cục bộ với độ phức tạp thấp.
4. `model-input-only` về cấu trúc chỉ có `story/question`, nhưng nhãn oracle **cùng public GitHub**; yêu cầu phân lập dữ liệu khi dùng ở bất kỳ thử nghiệm learning nào.
5. Probes chỉ thay câu hỏi trên variant A của từng cặp; Codex cần đo khả năng khai thác nhịp A/B, frequency và bias theo schema, không tự suy là đã cân bằng hết.
6. Tách đánh giá năng lực suy luận logic văn bản khỏi phát biểu bản thể về *ý thức*, *hiểu ngữ nghĩa nội tại* hay các quy luật vật lý. R2A không chứng minh các mệnh đề đó.

**Đo đạc từ author-side shortcut audit mới:** `sentence1=0/256, sentence2=48/256, sentence3=80/256, sentence4=128/256`; `last relevant queried key=256/256`. Log/mã: [audit](../../artifacts/qa/ttm-r2-semantic-toy/r2a/R2A_AUTHOR_SHORTCUT_AUDIT_20261110.json). Đây không phải kết quả Codex.

## 3. Ma trận đối chứng prospective — không tự chạy

Mục tiêu tách ba nguồn lợi ích khác nhau:
- **Dữ liệu/nhãn ngữ nghĩa có giám sát** (`supervision effect`);
- **Đầu ra và inductive bias của kiến trúc** (`architecture effect`);
- **Thêm dung lượng và FLOPs** (`capacity/compute effect`).

| Arm | Backbone & kiến trúc | Giám sát (TRAIN only) | Vai trò |
|---|---|---|---|
| **A — O0-CE** | P02 decoder-only gốc | CE dự đoán token, không state labels | Baseline văn bản |
| **B — O0-STATE-TEXT** | P02 gốc, không state head | CE trên văn bản + nhãn state/goal biểu diễn bằng token từ **cùng tokenizer đóng băng** | Đối chứng **có thêm giám sát ngữ nghĩa** nhưng không đổi kiến trúc |
| **C — O1-TRUE** | P02 + state/goal auxiliary head | Cùng nhãn state/goal đúng mà B nhận, nhưng thông qua auxiliary head | Ứng viên biểu diễn trạng thái |
| **D — O1-SHUFFLED** | Kiến trúc/hàm loss như C | Nhãn state/goal bị hoán vị ngẫu nhiên **có kiểm soát, khóa trước**, giữ histogram | Kiểm tra head/regularization khi nhãn mất quan hệ đúng |
| **E — O0-CAPACITY** | P02 + adapter/head dung lượng phụ **không được dùng nhãn state** | CE văn bản như A | Kiểm soát số tham số huấn luyện và chi phí thêm |

### So sánh không được đánh đồng

- **B vs A:** tác động của *giám sát bổ sung bằng văn bản*, chưa phải chứng minh biểu diễn tốt hơn.
- **C vs B:** kiến trúc auxiliary head có khác với giám sát state bằng token không? Chỉ kết luận nếu số nhãn, data exposure, params/compute đã match hoặc chênh lệch có công bố và đối chứng.
- **C vs D:** nhãn đúng có tạo tín hiệu liên kết state-key hay chỉ thêm regularization? Hoán vị nhãn cần khóa seed và không rò split.
- **E vs A:** tác động tăng dung lượng *không có nhãn state*.
- **C vs E:** lợi ích tổng hợp do supervision + architecture dưới quy mô/compute tương đương; không cô lập architecture nếu thiếu B/D.

**Cảnh báo quan trọng:** B có chiều dài output supervision và entropy token khác với head phân lớp của C. **Không thể tuyên bố budget bằng nhau chỉ vì số nhãn oracle bằng nhau.** Trước bất kỳ science run phải xác nhận hai chế độ báo cáo: (i) **matched text-token and oracle-example exposures**; (ii) **matched measured FLOPs/GPU-time budget**, với các thỏa hiệp được nêu trước. Nếu không có match, chỉ báo cáo so sánh có điều kiện, `FAIR_SUPERVISION=HOLD`.

### Budget candidate (chỉ để lập kế hoạch, không cấp T4)

- Cùng tokenizer BPE2048, cùng dữ liệu văn bản được phép, cùng nguồn checkpoint P02 nếu thêm head không thay hình dạng trunk; mọi head/adapter mới khởi tạo bằng seed ghim, không làm thay đổi checkpoint gốc. Nếu đổi kiến trúc trunk không thể kế thừa checkpoint cùng cách thì đặt **trận so sánh từ đầu riêng**, không gọi chung warm-start.
- Ở nhánh có nguồn TRAIN label oracle: source graph/statement label sinh **chỉ từ TRAIN**; không cung cấp oracle state hoặc đáp án ở input suy luận. `oracle_at_inference=0` cho tất cả arm.
- Freeze `N_text_target`, `N_state_example`, steps, context, batch schedule, valid token exposures, seed, params (trainable/total), optimizer state, token-slot count, FLOPs ước lượng và VRAM trước khi chạy.
- Khi cần neutralize overhead: E có thêm adapter tham số trainable được sử dụng trong forward (không phải tham số chết/dummy) để match C. B có thể được chạy kèm giới hạn compute giống C hoặc giữ thành một **stratum riêng**; không ép B/C match giả tạo bằng cách tùy ý bỏ dữ liệu của arm khác.
- Giới hạn triển khai đề nghị ở thí nghiệm đầu: synthetic-only và tokenizer fixtures; **không mở GPU**, giữ TTM-Small4M và 2×2 hiện hữu.

## 4. Phép thử R3 khó hơn trước khi quyết định mở O1

R2A đã kiểm key-binding dưới 4 câu với phép gán trực tiếp. Bài toán phân biệt hơn cần:
1. Chuyển giao nhiều bước `A → B → C`, ít nhất 3 keys và sự kiện nhiễu; câu hỏi yêu cầu liên kết **đúng vật thể**, không chỉ tìm lần gán đơn giản.
2. **Tham chiếu gián tiếp (coreference)**, tên gọi thay thế/đại từ đã khóa nghĩa, kiểm logic ngược và các ca cố tình mơ hồ phải có nhãn `AMBIGUOUS`, không gán bừa oracle.
3. **Thay đổi/hủy bỏ mục tiêu**: cùng câu chuyện, thay một hành động nhỏ làm trạng thái cuối đổi; kiểm cả thứ tự và mục đích.
4. Chia theo **đồ thị sự kiện/quan hệ (structural split)**, không chỉ khác diễn đạt. Đặt một bộ FINAL tương lai *khóa SHA/escrow* chưa phát hành nhãn trước khi science; R2A public chỉ dùng QA.
5. Các đối chứng: bag-of-words, absolute-position, recency-with-key, lexical lookup, shallow parsing/rule interpreter, P02 frozen; **quy tắc hoàn hảo vẫn không suy ra model học được**.
6. Failure criteria: nếu heuristic không cần state đạt 100% trên mọi bài hoặc nếu oracle leak qua metadata, không dùng kết quả đó để kết luận O1 cần thiết.

## 5. Quyết định R2A tạm thời

`R2A_FULL_GITHUB_EVIDENCE=PASS` · `POSITION_FIXED_SCOPED` · `H-ORDER=FORMAL_SCOPED` · `H-BINDING=TOY_SCOPED` · `H-STATE=NOT_LEARNED` · `O1=DEFER` · `O0=HOLD_PRESERVED` · `TRAINING=0` · `GPU=0` · `CODEX_R2A_REVIEW=NOT_EXECUTED`.

Đã hoàn thành công việc **tác giả thiết kế**. Mời Codex (AI nội bộ) phản biện với quyền đọc đầy đủ GitHub và tạo bằng chứng riêng theo lịch sử SHA. Không gọi Codex là external human reviewer. **Chưa có quyết định mở T4**, không hủy O0, không merge `main` hay PR #13.

**Bước thực hiện tiếp theo sau Codex:** `TTM_R2A_CODEX_REVIEW_ADJUDICATE_THEN_R3_STRUCTURAL_STATE_TRACING_SCIENCE_DESIGN_OR_KEEP_O0`. Quyết định 1 lần chọn `O0-only` hoặc `O0 + O1` với bộ đối chứng A–E công bằng; nếu Codex tìm bypass mới, sửa fixture trước khi khoa học.
