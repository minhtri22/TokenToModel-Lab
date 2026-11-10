# TTM T5 — Owner override: MERGE=HOLD cho tới exact causal root và strict PASS

**Ngày:** 2026-11-10  
**Phán quyết đang có hiệu lực:** `MERGE=HOLD` · `PR16=DRAFT` · `SCIENCE_STRICT=FAIL_32/32` · `ROOT_CAUSE=NOT_PROVEN`.

## 1. Quyết định mới của chủ dự án

> Chưa merge, cần Xác định chính xác nguyên nhân sai số, chỉ merge khi PASS.

Lệnh này **phủ quyết phán quyết MERGE của lượt review trước**; biên bản `TTM_T5_PR16_INDEPENDENT_SOURCE_EVIDENCE_FINAL_MERGE_ADJUDICATION_20261110.json` được **giữ nguyên như lịch sử**, không sửa/ghi đè. Trạng thái được điều chỉnh bằng biên bản nối tiếp `TTM_T5_OWNER_OVERRIDE_PR16_HOLD_EXACT_CAUSAL_ROOT_AND_STRICT_PASS_GATE_20261110.json`. `lineage.md` không được ghi quản trị HOLD; vẫn giữ L0013 khoa học FAIL hợp lệ.

`Git mergeable`, `SOURCE_QA=20/20`, `EVIDENCE_QA=16/16`, `TOP1=32/32` **không phải** điều kiện đủ để merge. Không merge khi root cause còn UNKNOWN hoặc strict FAIL, dù đã đóng gói một kết quả âm tính hợp lệ.

## 2. Các phát hiện có bằng chứng: nguồn sai số không được đồng nhất hóa

| Bằng chứng | Điều kết luận được | Điều KHÔNG kết luận được |
|---|---|---|
| GGUF F32 từ checkpoint1024, 52 tensor, readback bitwise | Không thấy mất mát ở đường lưu tensor F32 đã kiểm | Chưa chứng minh runtime matmul bitwise parity |
| Original 8 fixture × 35 stages: `inpL` sai số 0, đầu tiên > 1e-5 tại `ffn_inp-0`, khoảng 6.2e-5 đến 2.1e-4 | Sai khác bắt đầu trong/đầu ra attention-residual block 0 trước GELU | Không gán duy nhất cho V, WO, FMA, LayerNorm hoặc cache |
| 32 synthetic S0–S3: S1 F32 cache và Flash OFF vẫn FAIL 8/8 tại 0.001 | KV precision + Flash **không đủ** sửa strict parity | Không chứng minh chúng không góp sai số |
| P02 `src/p02/transformer_core.py`: `nn.GELU()` default erf; llama.cpp pin `src/models/gpt2.cpp`: `LLM_FFN_GELU` → `src/llama-graph.cpp`: `ggml_gelu`, cạnh nhánh riêng `LLM_FFN_GELU_ERF` | **Khác biệt toán tử GELU cụ thể có thể sửa/đối chứng** | Không chứng minh GELU là nguyên nhân duy nhất hoặc đủ vượt 0.001 |

### Nguồn mã được ghim

- P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18` — [P02 Transformer](https://github.com/minhtri22/TokenToModel-Lab/blob/9762343e06cf800b50574c2871ae1ed58537fb18/src/p02/transformer_core.py).
- llama.cpp commit `372dc5ca157276beb6c67b2e92477e8d662e964a` — [GPT-2 graph](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/models/gpt2.cpp#L106-L126); [GELU vs GELU_ERF branches](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-graph.cpp#L2087-L2111).
- T5 old trace Git blob `bd49a995e7407172274948a3cd8c5794d4877536`; `ffn_inp-0` là khác biệt đầu tiên ở ngưỡng chẩn đoán (10^{-5}), **không** phải strict acceptance threshold 0.001.
- One-shot 32 raw hiện có SHA-256 `544df628802591bcdda7ca9d6de4779d5e2872ee8b409c6710ede5bbf8ac19b8`, giữ bất biến; kết quả strict FAIL 32/32.

## 3. Một đợt chẩn đoán nhân quả tích hợp — không thêm chuỗi permit kỹ thuật

`TTM_T5_EXACT_ROOT_CAUSE_FIRST_DIVERGENT_OPERATOR_AND_CORRECTIVE_ABLATION_INTEGRATED`

### A. Khóa trước nguồn, fixture và điểm đo

Dùng checkpoint1024, GGUF F32 và llama.cpp commit đã pin. Sinh **fixture tổng hợp mới, chưa dùng trong 8 fixture lịch sử hay batch 32 đã tiêu thụ**, gồm 1 token để làm đối chứng attention đơn giản (softmax chỉ có 1 key) và ít nhất 2 token để kiểm attention thực. Các fixture được niêm phong *trước* phép đo, không lựa sau khi nhìn logits.

Ở nhánh **F32 KV + Flash OFF** (loại cache F16/Flash), đối chiếu tại cùng input và cùng độ chính xác F32:

1. Token/position embeddings và `inpL`.
2. LayerNorm đầu và fused QKV, sau đó tách từng Q, K, V.
3. QK, mask, softmax, tích `weights @ V`.
4. Attention output projection `WO` và `ffn_inp-0` trước GELU.
5. `ffn_up` trước GELU, **GELU exact (erf) đối chiếu GELU approximate**, `ffn_down`, residual.
6. Các layer tiếp theo, final LayerNorm và toàn bộ 2048 logits.

Chỉ cần ghi các tensor đủ để xác định **điểm sai khác đầu tiên**; không lập lại bộ 35 stage × 8 fixture trừ khi phép đo tối thiểu không phân biệt được.

### B. Thử sửa đúng một thành phần và làm ablation

Thử đối chứng GELU `ggml_gelu` vs `ggml_gelu_erf` trên **cùng tensor đầu vào đã ghi**. Nếu sai khác đã xuất hiện ở `ffn_inp-0`, phải tiếp tục định vị trong `V → attention → WO` và/hoặc phép cộng residual, phép nhân ma trận hoặc rounding F32. Không được sửa GELU rồi tuyên bố nguyên nhân đã được cô lập nếu sai khác pre-GELU vẫn tồn tại.

**Không chỉnh sửa original llama.cpp checkout và không viết lại GGUF/checkpoint đã khóa.** Mọi patch ứng viên dùng build nguồn/tệp mới với Git/SHA độc lập, có đối chứng trước–sau và cùng input; xác minh đúng binary thực thi.

### C. Điều kiện giải quyết nguyên nhân và xét MERGE

Chỉ đặt `ROOT_CAUSE=PROVEN` nếu đồng thời:

1. Xác định được **toán tử sai khác đầu tiên** với tensor FP32 có dấu và độ lớn cụ thể, không chỉ sai số scalar cuối.
2. Truy ngược tới nguồn mã/kiểu dữ liệu/thứ tự toán học cụ thể và xác minh cùng một thao tác trên input giống nhau.
3. Có thử nghiệm **can thiệp nhân quả (ablation)**: áp dụng riêng sửa đổi loại bỏ hoặc giảm sai số đầu tiên đúng dự đoán, hoàn nguyên sửa đổi tái xuất hiện sai số; không dùng fixture đã tiêu thụ để hợp thức hóa lần chạy lại.
4. Có một **bộ xác nhận độc lập mới, đăng ký trước**, tách khỏi dữ liệu được dùng để lựa chọn patch. Strict 2048-logit max-abs ≤ **0.001** trên *mọi* fixture đã khóa cho candidate đã xác định (không nới threshold, không chỉ xét top-1), cùng chứng thực exact checkpoint, GGUF, source và binary.
5. QA độc lập và quyết định cuối của owner đều PASS. Chỉ khi đó mới trả `MERGE`, nếu không là `HOLD` hoặc `FAIL`.

**Lưu ý:** Kết quả FAIL 7/8 lịch sử và FAIL 32/32 đã hoàn tất **vĩnh viễn được giữ nguyên**; không cần biến chúng thành PASS hồi tố. PASS mới là kết quả trên protocol confirmatory và candidate sửa lỗi được khóa trước chạy, không sử dụng các fixture cũ làm thước đo được lựa chọn sau khi thấy kết quả.

### Thực thi

Không chạy lại 32 lượt cũ, không huấn luyện, không động tới TEST/Q1Q2, không push/merge main. Đợt chẩn đoán tiếp theo mới được chuẩn bị mã/trình chạy, kiểm tra tĩnh rồi chạy **một gói hữu hạn** trên tập fixture mới, không chia thành nhiều cấp phép cho phép thử kỹ thuật nhỏ.

**Trạng thái hiện tại:** `OWNER_MERGE_GATE=LOCKED_HOLD` · `CONCRETE_GELU_OPERATOR_MISMATCH=SOURCE_VERIFIED` · `FIRST_PRE_GELU_ATTENTION_DIVERGENCE=TRACE_VERIFIED` · `EXACT_TOTAL_CAUSAL_ROOT=UNRESOLVED` · `NEW_CONFIRMATORY_PASS=NOT_EXECUTED` · `PR16=DRAFT` · `MAIN=UNCHANGED`.
