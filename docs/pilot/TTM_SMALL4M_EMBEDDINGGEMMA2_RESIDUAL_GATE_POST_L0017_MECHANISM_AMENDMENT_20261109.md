# TTM-Small-4M × EmbeddingGemma 2 — Tiếp tục nghiên cứu cơ chế bằng residual/gated embedding sau L0017

**Ngày:** 09/11/2026  
**Loại:** Bổ sung thiết kế khoa học (scientific design amendment), KHÔNG phải thực thi nghiên cứu mới.  
**Trạng thái:** `RESIDUAL_GATE=DESIGN_READY_FOR_SEPARATE_32_STEP_EXPLORATORY_EXECUTION`; `SCIENCE32=NOT_EXECUTED` · `GPU=NOT_USED` · `GGUF=NOT_OPENED`.  
**Mã dự kiến:** `TTM_SMALL4M_EMBEDDINGGEMMA2_ZERO_GATE_RESIDUAL_32_STEP_CPU_PROBE`.

## 1. Vì sao cần bổ sung báo cáo gốc thay vì sửa lại lịch sử

Báo cáo cơ chế ở commit `79355701e56ca6e7f34bd4f0585f4935184f2a00` đưa ra `STOP_NAIVE_DIRECT_TOKEN_SWAP_AND_GO_ZERO_INIT_RESIDUAL_GATE_DESIGN_ONLY` dựa trên hai lượt frozen và thích nghi **64 bước**. Kết quả lúc đó: C vẫn kém A/B trên VALIDATION, nhưng tốt hơn D. Kết luận âm theo hợp đồng cũ vẫn đúng đối với **64 bước** (L0014).

Bằng chứng đến sau **không được phép bỏ qua**:
- L0015: tại 1.024 bước thêm, ưu thế C chưa được thiết lập so với A/B (VAL).
- L0016: tại 2.048 bước, C có tín hiệu dương trên VAL cũ, phạm vi thăm dò.
- **L0017**: lượt CPU xác nhận 320 truyện, 75.798 nhãn, bốn checkpoint cố định bước 2.048. NLL A=`3.3414141970`, B=`3.3581664488`, C=`3.3086025043`, D=`3.4265771699`; cả ba cận dưới CI95 cho A−C, B−C và D−C đều **dương**. Phán quyết: `PASS_FIXED_CHECKPOINT_NEW_HOLDOUT_ALL_THREE_CONTRASTS`.

Vì vậy, **không còn được mô tả naïve direct swap là một thất bại nói chung**: nó đã đạt PASS ở phạm vi checkpoint cố định sau 2.048 bước. Quyết định STOP lịch sử là quyết định thiết kế hợp lý tại thời điểm 64 bước; không xóa hoặc sửa văn bản cũ. Residual gate tiếp tục là một **giả thuyết cơ chế mới**: bảo tồn không gian embedding đã học có thể giúp tiếp nhận tín hiệu donor ở ngân sách thích nghi nhỏ, với đối chứng hoán vị.

**Không đánh đồng hai câu hỏi:** G/R gate từ baseline gốc bước 1.024 **không thể giải thích nhân quả** vì sao C direct-swap 2.048 bước vượt A/B/D. Phép thử 32 bước chỉ kiểm chứng câu hỏi về hiệu chỉnh có cổng trên một backbone cố định riêng.

## 2. Hợp đồng kiến trúc và nguyên nhân cần kiểm chứng

Với token `t` trong 2.048 ID của TTM:

\[
E_G(t) = E_0(t) + \tanh(a)\odot \Delta_G(t),\qquad
\Delta_G(t)= \begin{cases} P_G Z_G(t)-E_0(t) & t\in\mathcal V\\0&t\notin\mathcal V\end{cases}
\]

- `E_0`: bảng token đầu vào TTM gốc đã huấn luyện tại **checkpoint T4 bước 1.024**, SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- `Z_G`: ánh xạ các hàng token EmbeddingGemma 2 **không có ngữ cảnh** 512 chiều; chỉ 1.917/2.048 token hợp lệ, cùng 130 fragment UTF-8 lỗi và 1 EOS fallback như báo cáo gốc. Không gọi encoder donor trong đường suy luận.
- `P_G`: phép chiếu ridge 512→256, tham số ridge `0.01`, học **từ bảng embedding TTM gốc và donor đã khóa**, không sử dụng TRAIN labels, VAL hoặc TEST.
- `a`: vector **256 tham số trainable duy nhất** cho mỗi nhánh G/R; `a=0` ở bước đầu; `g=tanh(a)` là cổng có dấu, đạo hàm tại 0 bằng 1.
- `\Delta(t)=0` cho EOS/token không map. Không huấn luyện `E0`, donor, `P`, bộ giải mã Transformer, vị trí hoặc **untied output head**.
- Ngay tại step0: logits phải **trùng chính xác** giữa B, G và R trên cùng chuỗi token. Mọi sai khác là lỗi hợp đồng, không phải hiệu ứng khoa học.

Sự khác biệt ba nhánh:

| Nhánh | Input | Trạng thái |
|---|---|---|
| **B** | Untied baseline từ T4 bước 1.024, `E0` gốc | Đóng băng 100%; chỉ đối chứng |
| **G** | `E0 + tanh(a_G)·Δ_real` với EmbeddingGemma 2 map đúng token | Chỉ học `a_G`, 256 tham số |
| **R** | `E0 + tanh(a_R)·Δ_perm`, donor hoán vị token hợp lệ bằng seed 20261109; chiếu ridge **refit** trên bảng donor hoán vị, giữ cùng valid mask | Chỉ học `a_R`, 256 tham số |

R dùng cách xây donor-hoán vị và refit ridge giống đối chứng D lịch sử. Nó kiểm tra sự liên hệ giữa **gán token donor** với hiệu quả điều chỉnh, nhưng không cô lập tuyệt đối đóng góp ngữ nghĩa pretrained, và không bảo đảm các phân phối `||Δ_G||` / `||Δ_R||` bằng nhau; cần báo cáo cả hai thống kê trên **bảng token**, không lựa chọn mô hình theo chúng.

## 3. Một phép thử nhỏ trên CPU — hợp đồng đề xuất, chưa được thực thi

- **Một RunID mới** và chỉ một lượt claim/execute, không tiếp tục/checkpoint/replay từ một lượt science đã tiêu thụ. **Không dùng lại** checkpoint C/D hay bộ 320 truyện đã phục vụ L0017 để huấn luyện/chấm.
- **Nguồn:** T1 đã khóa: TRAIN 2.048 truyện / VALIDATION 256 truyện; BPE2048 TRAIN-only. Dùng private T4 TRAIN/VAL pack đã SHA-pin, không mở TEST 64 truyện cũ. Pack SHA-256 theo báo cáo 64 bước: `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`.
- **Hai nhánh G và R:** mỗi nhánh **32 optimizer steps × đúng 512 nhãn TRAIN hợp lệ/bước = 16.384 nhãn exposure**; cùng lịch mẫu đã quyết định trước khi chấm; đề xuất seed lịch `2026110902`, seed hoán vị `20261109`; không tạo seed mới theo kết quả. B không huấn luyện. Không mở vòng tăng ngân sách 64/128/256 khi âm tính.
- **Optimizer đề xuất để ghim trước CLAIM:** AdamW chỉ với `a`, LR cố định `3e-3`, `betas=(0.9,0.95)`, `eps=1e-8`, `weight_decay=0`, global grad clip `1.0`, CPU FP32; 32 bước, không warmup/tune/sweep. Lý do lựa chọn LR khác LR=1e-4 của mô hình toàn phần: 32 cập nhật với LR `1e-4` có tổng thang bước chỉ ~`0.0032`, có nguy cơ cổng hầu như chưa mở, làm phép thử âm tính khó diễn giải. Từ kết quả hình học đã công bố trước VAL lần này, RMS `||Δ||/||E0||≈0.658`, LR `3e-3` trên 32 bước chỉ là mức kích hoạt khiêm tốn theo heuristic `32×LR≈0.096`, **không** phải bảo đảm cận chặt của AdamW. Không sử dụng VAL để hiệu chỉnh LR.
- **Chỉ chấm sau bước 32** trên 256 truyện VALIDATION T1 đã dùng nhiều lần, theo NLL token-weighted và tổng loss theo từng truyện. **1.000 lần bootstrap ghép cặp theo truyện**, `numpy.default_rng(20261109)`, CI phân vị hai phía 95%. Đối chứng trước đăng ký: **B−G** và **R−G**; cả hai cận dưới >0 là tín hiệu thăm dò dương; dữ liệu hợp lệ nhưng thiếu một cận dưới dương là kết quả âm đúng phạm vi.
- **Không có lựa chọn checkpoint/seed/LR theo VALIDATION**; không mở lại 320 holdout đã tiêu thụ; không tuyên bố đây là thử nghiệm xác nhận mù (blind confirmatory), kể cả khi cả hai CI dương.
- Giới hạn cần ghi riêng: G/R tối ưu đều 256 tham số và cùng lịch TRAIN, nhưng refit ridge của R không loại hết nhiễu do đặc tính hình học; thí nghiệm không trực tiếp chứng minh cơ chế ở C2048 và chưa là lặp training seed độc lập.
- Nếu đạt tín hiệu dương: kết luận **`EXPLORATORY_GATED_DONOR_ALIGNMENT_SIGNAL`**, chỉ cho phép **thiết kế** tiếp một kiểm định nhân quả chặt hơn (seed/backbone mới, đối chứng chuẩn hóa Δ, holdout mới) trong tác vụ riêng. Nếu không đạt: **`GATED_32_STEP_SIGNAL_NOT_ESTABLISHED`**, không tự tăng ngân sách hoặc thay tham số dựa trên VAL. Ghi vào `lineage.md` chỉ sau khi chạy và độc lập phân xử PASS/FAIL science.

## 4. QA tổng hợp kiến trúc đã thực hiện (không phải khoa học)

- Mã `ttm_gemma2_zero_gate_synthetic_contract_qa_20261109.py` SHA-256 `4424627a67e7516bbddbf84d290d4528933563b421c50d2749460c2b658e4519` dùng **P02 nguyên bản** SHA256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`, donor và token giả lập; CPU PyTorch 2.10.0+cpu.
- **37/37 checks PASS**: ba nhánh B/G/R logits và input embedding trùng chính xác tại step0, B untied, G/R chỉ 256 tham số `tok.a` được tính gradient, fallback EOS/fragment giữ nguyên sau một bước tối ưu giả lập; negative QA shape/EOS/NaN PASS; B không thay state.
- Biên bản `TTM_GEMMA2_ZERO_GATE_SYNTHETIC_CONTRACT_QA_20261109.json` SHA-256 `30e600ac0eb7ad914f15fc02d9d5479f5904346050a0260c79ddf91c14dfa205`.
- Không có donor, checkpoint thật, TRAIN/VAL/TEST, GPU hoặc điểm NLL khoa học mới trong 37 phép thử này. **Chỉ mô phỏng tính đúng của toán tử và đường gradient**, chưa phải runner science 32 bước trên dữ liệu thật.

## 5. Quản trị

- Không thay tài liệu cơ chế gốc tại commit 7935570…, cũng không sửa L0014–L0017; tài liệu này là amendment để giải thích bằng chứng **đến sau**.
- Không sửa branch `main`, PR #12, P02/T4 nguồn; không viết file ngoài project root trên máy Windows, không dọn/xóa worktree; không phát hành checkpoint/donor/raw story ra GitHub.
- Không GGUF/Ollama/product benchmarking, không GPU. Chỉ làm việc trên nhánh nghiên cứu hiện có; giữ kết quả khoa học L0017 và quyền một lượt TEST/holdout.
- **Bước tiếp theo duy nhất:** triển khai đúng **một gói runner CPU 32 bước B/G/R**, gắn nguồn thật + SHA, negative QA tổng hợp, niêm phong hợp đồng (seed, LR, dataset, source, CLI) và **sau đó mới** thực thi 1-shot theo quyền của chủ dự án. Không chia thành nhiều micro-permits; không chấm science khi chưa đóng runner/CLAIM.