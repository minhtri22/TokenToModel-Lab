# TTM T5 — F32 strict logits parity: xác định vùng nguyên nhân bằng chứng nguồn

**Ngày:** 2026-11-09 · **Nhánh:** `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109` từ main `b57b44e7287f842e81050c1faee337f636333dd0`.  
**Trạng thái:** `SOURCE_AND_NATIVE_LOG_AUDIT=PASS_SCOPED`, `ROOT_CAUSE_CANDIDATE=FLASH_ATTENTION_F16_KV_PRECISION`, `CAUSAL_PROOF=HOLD`. Không huấn luyện hoặc tái chạy 8 fixture đã tiêu thụ.

## 1. Giữ nguyên kết quả khoa học và kỹ thuật trước đó

- Checkpoint **gốc T4 bước 1.024**, SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Không dùng checkpoint 1280, EmbeddingGemma2, FRESH12 hoặc dữ liệu TEST.
- GGUF F32 SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`; 52 tensors, khoảng 15 MB; các phép kiểm tensor weight/readback trước đó đạt PASS.
- llama.cpp commit `372dc5ca157276beb6c67b2e92477e8d662e964a`.
- Kết quả strict final logits đã khóa: **7/8 fixture FAIL** tại ngưỡng `max_abs <= 0.001`, max final `0.003362178805176086`; **8/8 top-1** vẫn trùng. File gốc: `evidence/pilot/t5-trained/T5_TRAINED_LLAMA_CPP_PARITY_FAILED_ORIGINAL.json`.
- File trace 8 fixture × 35 stage mỗi fixture: `evidence/pilot/t5-trained/T5_F32_NUMERIC_LOCALIZATION_UNADJUDICATED.json` (Git blob `bd49a995e7407172274948a3cd8c5794d4877536`). File tiếp tục được giữ nguyên, không re-write; ngưỡng nhạy định vị `1e-5` **không** phải acceptance threshold.
- T5 Ollama import và 32-token generation PASS **compatibility only** trong phân xử riêng; không làm thay đổi kết luận strict logits FAIL.

## 2. Kết quả định vị độc lập từ 280 stage đã có

| Fixture | Token IDs | First sensitive stage (>|1e-5|) | Δ tại `ffn_inp-0` | Δ final logits | Strict |
|---:|---:|---|---:|---:|---|
| 0 | 1 | ffn_inp-0 | 0.000062287 | 0.000936747 | PASS |
| 1 | 3 | ffn_inp-0 | 0.000093281 | 0.001599312 | FAIL |
| 2 | 5 | ffn_inp-0 | 0.000096157 | 0.002269030 | FAIL |
| 3 | 4 | ffn_inp-0 | 0.000091620 | 0.001976013 | FAIL |
| 4 | 8 | ffn_inp-0 | 0.000064269 | 0.001823902 | FAIL |
| 5 | 16 | ffn_inp-0 | 0.000137821 | 0.001900882 | FAIL |
| 6 | 7 | ffn_inp-0 | 0.000079811 | 0.002775908 | FAIL |
| 7 | 32 | ffn_inp-0 | 0.000209689 | 0.003362179 | FAIL |

`inpL` = **0** sai khác cho cả 8 fixture; `attn_norm-0` và `wqkv_b-0` chỉ lệch thấp hơn ngưỡng nhạy. `ffn_inp-0` là vùng **attention output + residual** đầu tiên quan sát sai khác (>10^{-5}). Các LayerNorm/FFN tiếp theo tích lũy và có thể khuếch đại sai khác. Không có 280 vector tensor F32 byte-đầy-đủ hoặc trace ở từng `kq / softmax / kqv / projection` để quy trách nhiệm cho duy nhất một toán tử.

**Kiểm toán đọc lại source:** `artifacts/qa/ttm-t5-parity/TTM_T5_STRICT_F32_SOURCE_TRACE_AND_FLASH_KV_QA_20261109.json` ghi **PASS 12/12** source/runtime log checks; không phải PASS scientific hoặc new native parity.

## 3. Phát hiện source + runtime chưa được sử dụng trong phân xử cũ

**Log Windows cũ được đọc từ máy đích, không chạy lại:**
`_tmp/ttm_t5_numeric_localization_v1/fixture_0/native_run.log`

Trong log có **16 occurrence** `FLASH_ATTN_EXT` do các lần graph reserve, gồm node `24/56/88/120` tương ứng bốn khối attention và một graph ubatch **1 token**. Đây là xác nhận **FlashAttention path thực tế đã được sử dụng**, không chỉ là mặc định giả định.

**Mã llama.cpp đúng commit ghim:**

- [GPT-2 graph `src/models/gpt2.cpp` L83–129](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/models/gpt2.cpp#L83-L129) — attention `build_attn` rồi residual `ffn_inp=ggml_add(cur,inpL)`, sau đó FFN dùng `LLM_FFN_GELU`. Git blob `711a148a28bd1aa2c1dccf2e3b21803aac4a4185`.
- [`src/llama-context.cpp` L4260–4275](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-context.cpp#L4260-L4275) — context mặc định `type_k=GGML_TYPE_F16`, `type_v=GGML_TYPE_F16`, flash attention AUTO. Git blob `a450d8257c87706655022d962d1cc846adb2fb45`.
- [`src/llama-kv-cache.cpp` L230–235](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-kv-cache.cpp#L230-L235) — bộ nhớ KV cache tạo tensor dựa trên **`type_k/type_v` của context**, không dựa trên F32 weight GGUF. Git blob `a1ec67e2630b67d9c1fb4ec4e655ee2b3807b341`.
- [`src/llama-graph.cpp` L3060–3085](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-graph.cpp#L3060-L3085) — nhánh `FLASH_ATTN_EXT` có cast K/V **F32 → F16** nếu tensor đầu vào là F32, mặc dù trọng số GGUF F32. Git blob `9f99ba83e4d7aff29ec82c74f605df913144a021`.
- [`src/llama-graph.cpp` L3110–3157](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-graph.cpp#L3110-L3157) — đường attention **không flash** dùng `mul_mat(K,Q)`, `soft_max_ext`, `mul_mat(V,weights)`, là đối chứng phù hợp để loại riêng flash/KV precision.
- [`src/llama-graph.cpp` L2087–2107](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-graph.cpp#L2087-L2107) — `ggml_gelu` khác với `ggml_gelu_erf`. PyTorch P02 dùng `nn.GELU()` default exact; GELU là **ứng viên thứ cấp**, nhưng thử tham chiếu `tanh` cũ vẫn còn FAIL 7/8.

**Lý luận phân biệt:** fixture 0 dài đúng **1 token** có đầu vào `inpL` trùng nhưng tại `ffn_inp-0` đã lệch 6.2287e-5. Khi chỉ có một key trong ngữ cảnh, attention weights phải là 1 (trong thực thi chuẩn), nên khác biệt softmax phân bố phức tạp không thể giải thích riêng mẫu này. Vẫn còn khác biệt làm tròn V/cache, phép chiếu attention, phép cộng residual hoặc thư viện tính toán.

**Đối chứng tổng hợp riêng trên CPU (không dùng checkpoint):** vector V F32 dài 256 và ma trận chiếu random có cùng cỡ, làm tròn V qua F16 tạo sai khác đầu ra cực đại khoảng `0.0001066–0.0001649` trên 8 seed. Kết quả cùng **bậc cỡ** sai khác đầu tiên tại `ffn_inp-0`, chỉ xác nhận **cơ chế khả dĩ**, không chứng minh nguyên nhân trên trọng số TTM thật.

### Đánh giá nhân quả

`FLASH_ATTN_EXT_USED=CONFIRMED_BY_ORIGINAL_LOG`.  
`F16_KV_PATH_SUPPORTED_BY_PINNED_SOURCE=YES`.  
`ACTUAL_PROBE_CONTEXT_TYPE_K_V=NOT_YET_ATTESTED` (bản source native caller thuộc nơi khác ngoài workspace cho phép đọc; không tự suy đoán biến đã override).  
`F16_CONTRIBUTION_TO_7_OF_8_FAIL=NOT_QUANTIFIED`.  
`EXACT_CAUSAL_ROOT_PROOF=HOLD`.

**Nghi vấn mạnh nhất:** đường tính toán attention chứa precision F16 trong một phép đo gọi là *F32 strict logits*, sau đó sai khác được tích lũy qua các block. Không được dùng tình trạng này để sửa FAIL đã khóa hoặc tuyên bố BUG trong llama.cpp: F16 KV cache có thể là thiết kế phục vụ hợp lệ.

## 4. Phép phân biệt nguyên nhân tối thiểu kế tiếp (CHƯA CHẠY)

Không chạy lại 8 fixture tiêu thụ. Khi chủ dự án cho phép một batch mới với **fixture synthetic mới chưa đo**, thực hiện **cùng một GGUF F32 / llama.cpp commit / ID fixtures / context positions / CPU threads** nhưng ghi nhận điều kiện:

| Probe | KV cache K/V | Flash attention | Mục đích |
|---|---|---|---|
| S0 | F16/F16 (default) | AUTO/ON | đối chứng cùng loại đường cũ; không tuyên bố replay lịch sử |
| S1 | F32/F32 explicit | **DISABLED** | đo toàn bộ sai khác khi loại cả hai nguồn ép F16 |
| S2 | F32/F32 explicit | ENABLED | xác minh flash vẫn ép/có sai số nửa chính xác dù KV storage F32 |
| S3 (khi cần) | F16/F16 explicit | DISABLED | tách precision cache khỏi flash |

**Các điểm trace tối thiểu trong block 0:** `attn_norm-0` → Q/K/V sau Linear → (QK^T) → softmax → (WV) → output projection `wo` → `ffn_inp-0`, rồi `result_norm` và logits cuối. Không cần các 35×N tensor ở mọi layer nếu block 0 phân biệt đủ. Giữ ngưỡng cuối `0.001` và tuyệt đối không thay threshold để 'lấy PASS'.

**Cách phân xử tiếp theo:** Nếu S1 khôi phục sai số về dưới ngưỡng hoặc thu hẹp mạnh từ tầng 0 trong khi S0 fail, có bằng chứng thực nghiệm cho **precision/flash branch**. Dùng S2/S3 để tách từng thành tố. Nếu S1 vẫn fail thì xét WO/projection FMA/matmul, phép cộng residual, LayerNorm/F32 CPU, và chỉ sau đó mới GELU. Khi chưa có native A/B có manifest và SHA độc lập thì chỉ đưa **root-cause candidate**, không đưa `ROOT_CAUSE_PROVEN`.

## 5. Công cụ và trạng thái

- Source-only validator: `tools/pilot_t5/strict_parity_source_diagnostic_20261109/diagnose_existing_trace.py` — đọc 8×35 stage cũ, kiểm tra provenance và threshold, in JSON stdout; **không ghi lại** tệp gốc.
- Synthetic negative QA: `tools/pilot_t5/strict_parity_source_diagnostic_20261109/test_trace_diagnostic.py`. Kiểm tra bị đổi threshold, source pin, stage, fixture, FAIL count, scope TEST. Đây là unit test, không xác nhận native parity.
- Một tiện ích chỉ đọc để soi nguyên bản caller / runtime params sẽ là bổ sung riêng khi source caller nằm trong workspace; hiện mã native probe từng build từ `C:\Users\minht\Downloads\TTM_T5_F32_NUMERIC_LOCALIZATION_PS51_PRECLAIM_RECOVERY_V2_20261108` **ngoài workspace**, nên quyền đọc bị chặn. Không dùng lối tắt đường dẫn để vượt ranh giới.
- `RemoteDesktop.run_command` trên gateway hiện yêu cầu managed `task_job_submit` nên **không có native job mới được chạy** trong lượt này. Log đọc được qua hành động chỉ đọc; không mở science job mới, không chỉnh file runtime.

**Phán quyết:** `SOURCE_ROOTCAUSE_LOCALIZATION=PASS_SCOPED` · `FLASH_F16_KV_PRECISION=PRIMARY_HYPOTHESIS` · `EXACT_CAUSAL_PROOF=HOLD` · `FROZEN_T5_STRICT=FAIL_7/8` · `T5_COMPATIBILITY_PASS=SEPARATE_PRESERVED` · `TRAIN=NO` · `TEST=UNTOUCHED` · `GGUF=UNCHANGED` · `MAIN=UNCHANGED` · `LINEAGE=UNCHANGED`.

## Bước thực hiện tiếp theo

`TTM_T5_F32_KV_FLASH_PRECISION_SINGLE_SYNTHETIC_DISCRIMINATION_DESIGN_AND_OWNER_RUN_GATE` — chỉ tạo một thí nghiệm phân biệt mới bằng dữ liệu synthetic, ghi trước kiểu KV/flash và phép đo điểm nội bộ; chỉ thực thi native khi có nguồn mã caller trong workspace và quyền chạy chính xác. Không tái dùng 8 fixtures lịch sử, không sửa llama.cpp gốc, không mở huấn luyện mới.
