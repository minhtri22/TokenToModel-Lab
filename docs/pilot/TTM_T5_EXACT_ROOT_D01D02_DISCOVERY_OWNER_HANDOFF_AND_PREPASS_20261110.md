# TTM T5 — Exact first-op diagnostic: D01/D02 + one-factor GELU correction

Ngày: 2026-11-10. Task: `TTM_T5_EXACT_ROOT_CAUSE_FIRST_DIVERGENT_OPERATOR_AND_CORRECTIVE_ABLATION_INTEGRATED`.

## 1. Tình trạng thực chất

**Đã thực hiện:** tiền đăng ký mới với 2 fixture khám phá D01/D02 và 4 fixture xác nhận C01–C04 được khóa nhưng chưa dùng; sinh dữ liệu PyTorch P02 FP32 thực từ checkpoint1024; đo độc lập trên cùng tensor GELU erf/tanh và làm tròn V qua F16; tạo 42 tensor trace/reference; tạo source C++/CMake và một runner owner-local để đo GGML hai biến thể. Đối chiếu tĩnh GitHub 38/38 source/protocol assertions **PASS** (không phải dynamic Windows build/QA).

**Chưa thực hiện:** biên dịch probe C++ mới bằng MSVC, chạy native GGML D01/D02, đối chiếu số thực GGML-vs-P02 từng tensor, chứng minh cơ chế nhân quả, thử xác nhận C01–C04 hoặc xác nhận strict PASS. RemoteDesktop `run_command` trả `managed mode requires task_job_submit`; không phát lệnh model/compile được từ connector trong lượt này.

PR #16: `DRAFT / HOLD`, `MERGE=BLOCKED_UNTIL_EXACT_CAUSE_AND_STRICT_PASS`. `main`, `lineage.md` L0013 và 8/32 kết quả cũ bất biến.

## 2. Bằng chứng CPU thực (không phải mô phỏng random)

P02 `src/p02/transformer_core.py` Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; checkpoint1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. `torch 2.10.0+cpu`, 3.749.376 tham số, `load_state_dict(strict=True)`, model `eval/inference_mode`. Forward phân rã từng layer **bitwise giống** `GPT.forward` cho cả D01, D02.

| Phép đo cùng trọng số / cùng input | D01 (1 token) | D02 (5 token) |
|---|---:|---:|
| GELU erf vs tanh toàn 4 block, max-abs logits | 0,001018524 | 0,001211166 |
| GELU erf vs tanh trên tensor đầu vào block 0, max-abs | 0,000233106 | 0,000232100 |
| V làm tròn F16 → F32, khác biệt `ffn_inp-0`, max-abs | 0,0000759214 | 0,0000645518 |

Các đối chứng này **chỉ dùng PyTorch**, không lấy làm phép đo GGML thực. Chúng chứng minh GELU variant có thể đủ tạo ra sai khác logits vượt strict 0,001 và F16 V có thể gây sai khác pre-GELU; **chưa quy gốc sai số GGML cho bất kỳ nguyên nhân duy nhất nào**.

Reference raw `TTM_T5_D01D02_P02_TRUE_SIGNED_TRACE_20261110.jsonl`: **42 dòng** tensor; SHA256 `9cc5fc2db1f95e7e863a285eb279b28b7a383b81a4f890d7ec0f79b788b995e0`, 1.014.684 bytes. ZIP của file: SHA256 `8e289485e9af2ae3de3aa8d8e19150b4d062dad395189540483ecb424be4bc10`, 435.513 bytes, không kèm checkpoint. Raw ZIP được bàn giao trong cuộc trò chuyện để owner đặt vào `_tmp` project. GitHub chỉ lưu checksum và biên bản để tránh public raw checkpoint-derived tensors khi chưa đánh giá rights/custody.

## 3. Phân biệt từng phép toán

Giữ nguyên checkpoint, GGUF F32 SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, llama.cpp commit `372dc5ca157276beb6c67b2e92477e8d662e964a`, CPU, threads=1, **KV F32, Flash OFF**.

- D01 **1 token**: attention softmax chỉ có một key, giúp cô lập V, phép chiếu WO, cộng bias/residual mà không dùng phân bố attention nhiều token.
- D02 **5 token**: thêm Q/K, QK, causal mask, softmax, tích attention × V.
- Trích đúng `inpL`, `attn_norm-0`, `wqkv_b-0`, Qcur/Kcur/Vcur, `kq-0`, `kq_soft_max-0`, `kqv-0`, `kqv_out-0`, **`attn_wo_mm-0`**, **`attn_wo_out-0`**, `ffn_inp-0`, `ffn_up_b-0`, `ffn_gelu-0`, `result_output`.
- C++ callback lưu **giá trị FP32, ne/stride, chữ ký stage và fixture**, fail closed nếu F16/nonfinite/thiếu required stage.
- Auditor độc lập tính **delta native minus P02 từng phần tử có dấu**, chỉ số peak, max/mean abs; đối với QK có thể padding, chỉ so các cột key thật; không che giấu hình dạng khác nhau.
- Isolated source variant A: **trace_only**, thêm callback `attn_wo_mm` và `attn_wo_out`, không thay toán học. Variant B: cùng patch trace + đúng một sửa `LLM_FFN_GELU → LLM_FFN_GELU_ERF`. Được tạo từ Git worktree ở `_tmp` dự án, tuyệt đối không sửa clone nguyên bản.
- A và B đều đo D01/D02 theo đúng một batch tích hợp; sau đó **HOLD để phân xử first-op**. Không tự động chạy 4 confirmatory fixtures.

## 4. Gói owner Windows một lần duy nhất

**Đầu vào:** tệp ZIP raw ký hiệu trên, đặt tại
`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_T5_D01D02_P02_TRUE_SIGNED_TRACE_20261110.zip` và xác minh SHA trước khi gọi runner.

**Runner:** `tools/pilot_t5/exact_root_v1/run_owner_discovery_two_variants_once.py`. Nó sẽ:

1. Fail nếu stage đã tồn tại, nếu project/remote/worktree không đúng, nếu ZIP hoặc GGUF sai SHA.
2. Chỉ `git fetch` nhánh T5 rồi `merge --ff-only FETCH_HEAD` trên worktree T5 sạch. **Không cập nhật main**.
3. Chạy 16 static/unit tests read-only **trước** mọi sửa source/build.
4. Dựng hai isolated vendor Git worktree trong project, từ **pinned llama commit**, kiểm blob nguyên bản, thêm một patch trace / một patch GELU biến thể.
5. Dựng các thư viện và probe MSVC x64 hai lần, kiểm compiled `--self-check` không load model; tiền kiểm đúng 2 fixture/1 arm.
6. Chỉ gọi **hai** binary mới (mỗi variant một tiến trình, 2 discovery fixtures), dùng đúng DLL trong từng build, rồi chạy signed tensor auditor.
7. Viết bất biến `_tmp/ttm_t5_exact_root_discovery_run_v1_20261110/DISCOVERY_RUN_RECEIPT.json`; nếu partial/timeout thì **HOLD**, không tự retry, giữ toàn bộ log và raw.

**Lưu ý:** Hai build MSVC và callback mới chưa được Windows kiểm chứng; `SOURCE_STATIC=PASS_38/38` **không thể thay thế** native QA. Không chạy lại batch one-shot cũ 32 hoặc sửa `lineage.md` vì kỹ thuật chưa được phân xử.

## 5. Phân xử tiếp theo (đã tiền đăng ký)

Chỉ khi discovery có trace signed PASS mới xác định điểm lệch đầu tiên. Nếu `WO`/residual đã lệch trước GELU thì không thể nhận `GELU` là toàn bộ root. Nếu bản B GELU_ERF sửa đúng chênh lệch FFN nhưng phần trước GELU vẫn lệch, phải tiếp tục thử can thiệp đúng toán tử đầu tiên theo hướng matmul/float accumulation.

Sau khi xác định được một bản vá cô lập bằng **ablation sửa → hoàn nguyên**, mới khóa Git SHA binary/source mới và chạy **một lần** C01–C04 (confirmatory độc lập) với ngưỡng **max-abs ≤ 0,001 trên toàn bộ 2.048 logits của từng fixture**. Nếu bất cứ fixture nào FAIL thì `MERGE=HOLD`, không nới ngưỡng hoặc thay data.

**Bước thực hiện tiếp theo:** `TTM_T5_FIRSTOP_DISCOVERY_WINDOWS_OWNER_ONE_BATCH_AND_SIGNED_TRACE_ADJUDICATION`. Không yêu cầu lặp lại bước đã PASS, không tự chạy confirmatory.
