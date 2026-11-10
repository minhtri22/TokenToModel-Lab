# TTM T5 — lỗi stage 12, phục hồi V2 không chạy lại discovery A

Ngày 2026-11-10. Lượt `TTM_T5_EXACT_ROOT_CAUSE_FIRST_DIVERGENT_OPERATOR_AND_CORRECTIVE_ABLATION_INTEGRATED`.

## 1. Kết quả đọc trực tiếp máy Windows

Owner chạy one-shot gốc và nhận:

```
T5_STAGE=trace_only_10_no_model_constants
T5_NATIVE_ONE_SHOT=trace_only D01_D02
T5_STAGE=trace_only_11_native_two
DISCOVERY_STATUS=HOLD_DISCOVERY_FAILED_OR_PARTIAL_NO_RERUN
DISCOVERY_RECEIPT_SHA256=e2cbc797e133a7e4fc4d949293dd9bd847b881e18b39f3c72bcfa9debfbc8e96
```

Đã đọc trực tiếp:

- `_tmp/ttm_t5_exact_root_discovery_run_v1_20261110/DISCOVERY_RUN_RECEIPT.json` với trạng thái `HOLD_DISCOVERY_FAILED_OR_PARTIAL_NO_RERUN`, SHA của owner như trên.
- `trace_only/09_build_probe.log`: compile MSVC **exit 0**.
- `trace_only/10_self_check.log`: PASS exact D01, D02, F32 KV, Flash OFF; không tải model ở self-check.
- `trace_only/11_native.log`: **exit 0**, marker `T5_FIRST_OP_DISCOVERY_COMPLETE_ROWS_2`. Hai dòng logits và 38 stage trace đã được lưu trên Windows, chưa được chạy lại.
- `trace_only/12_independent_audit.log`: **exit 2** với lỗi duy nhất đã báo `FIRSTOP_AUDIT_FAIL_CLOSED:FINAL_STAGE_SHAPE_NOT_ALIGNED:result_norm`.

**Phân loại lỗi:** `AUDITOR_SHAPE_CONTRACT_FAIL`, **không phải lỗi compile hay native decode**. `trace_gelu_erf` đã có isolated source, nhưng **chưa build, chưa chạy native**. `C01..C04` confirmatory **chưa dùng**.

## 2. Nguyên nhân kỹ thuật của stage 12

Phép tham chiếu PyTorch `model.final_ln(x)[:,-1,:]` vẫn có trục batch đơn `[1,256]` và logits `[1,2048]`. GGML ghi hai tensor tương ứng dưới dạng `ne=[256,1,1,1]` và `ne=[2048,1,1,1]`.

Mã auditor V1 `independent_firstop_signed_tensor_audit.py` (Git blob `cf6a39f5e763b428fefd0d4c1bd5d0683cd78997`) chỉ chấp nhận reference `[256]` và `[2048]`. Đây là **lỗi giả định shape** của auditor; không phải bằng chứng P02/GGML sai số.

V2 là **mã mới**, không ghi đè auditor V1, cho phép chính xác `[w]` hoặc `[1,w]` **chỉ khi** GGML có `ne=[w,1,1,1]`, với `w=256/2048`. Không đổi bất cứ tensor, threshold `0.001`, thứ tự dữ liệu, hay thuật toán so sai số có dấu.

Một nguồn lệch tên node được sửa **trước** lượt B: llama.cpp với `LLM_FFN_GELU_ERF` gọi `ffn_gelu_erf-0` thay vì `ffn_gelu-0`. Probe B mới có **node name thật** `actual_node_name` và nhãn chuẩn `ffn_gelu-0` để so trên cùng tensor đầu vào, đồng thời require node `ffn_gelu_erf-0` thật phải xuất hiện đúng hai lần trong trace D01/D02.

## 3. Đối chiếu có dấu từ trace đã ghi, không infer lại

Đã đọc các stage ngắn của D01 qua connector và trừ **GGML − PyTorch** tại cùng chỉ số.

| Stage D01 | Max-abs tensor |
|---|---:|
| `inpL` | `4.99933e-11` |
| `attn_norm-0` | `2.43021e-7` |
| `wqkv_b-0` | `2.38763e-7` |
| `kqv_out-0` | `2.08215e-7` |
| `attn_wo_mm-0` | `1.03848e-7` |
| `attn_wo_out-0` | `1.04134e-7` |
| `ffn_inp-0` | `1.04606e-7` |

D02 — QK raw có max-abs `1.42564e-6`, QK softmax `1.19678e-7`. Bộ đối chiếu QK chỉ lấy **5 key thật**, bỏ padding 256 của GGML.

**Giới hạn:** D01 trace trước GELU khớp rất gần, nhưng D02 có các dòng dài bị RemoteDesktop cắt; chưa có báo cáo stage-by-stage độc lập đầy đủ của D02, GELU hoặc logits cuối. **Chưa đủ để xác định nguyên nhân chính xác của strict FAIL.**

## 4. Một lượt phục hồi hữu hạn không tái thực nghiệm A

Các nguồn đã commit vào nhánh T5:

- Auditor V2: `tools/pilot_t5/exact_root_v1/independent_firstop_signed_tensor_audit_v2.py`, Git blob `c523c470f8ec69b4938992f44b16a4127c3d08ae`.
- 8 unit tests không model: `test_firstop_v2_shape_recovery.py`, blob `4b93a12784647701b578309bd925c04bc61c2674`.
- Probe chỉ cho B: `gelu_erf_probe/ttm_t5_firstop_trace_probe.cpp`, blob `bd7d408885703a80055c2baf296a44f3006462b7`; CMake blob `066fef8e2a248efcaf25c71443bebd13cfb27be6`.
- Runner V2: `recover_partial_discovery_audit_and_gelu_erf_once.py`, blob `34bfcf1d1ca0803bfd9b05beafd5214dc7ad8fe9`.
- PowerShell 5.1 bootstrap: `Invoke-TTM-T5-FirstOp-Partial-V2-Owner-PS51.ps1`, blob `875b8910c4908c52f4269a3268e00a4ff68f3766`.

**Quy trình duy nhất:**

1. Kiểm SHA của receipt fail cũ, reference P02, GGUF và source có sẵn, kiểm chính xác worktree ban đầu, kiểm B chưa chạy. Không động các file cũ.
2. Chạy 8 bài thử V2 không nạp model; kiểm toán lại **chính D01/D02 trace-only đã sinh** bằng auditor V2. **Không một lệnh gọi binary A mới.**
3. Nếu A audit PASS, biên dịch **chỉ** biến thể isolated `trace_gelu_erf` (chưa chạy) và một B-specific probe trong `_tmp`. Self-check và kiểm node GELU_ERF thật, sau đó chạy **2 D01/D02 native của B đúng một lần**, QA V2 độc lập.
4. Viết `_tmp/ttm_t5_exact_root_discovery_recovery_v2_20261110/RECOVERY_V2_RECEIPT.json`, SHA/log cho A và B. Nếu FAIL hay partial → `HOLD`, không retry, không overwrite. Không mở C01–C04.

**Bằng chứng/source QA:** `PASS_36_OF_36` kiểm tra tĩnh scoped trên GitHub. Chưa chạy 8 test V2 trên Windows, chưa biên dịch hay chạy B; không được đánh đồng với dynamic PASS.

## 5. Cổng khoa học và merge

Kết quả nguyên bản `STRICT_PARITY=FAIL_7/8` và 32 phép đo S0–S3 `FAIL_32/32` giữ nguyên. Stage thất bại V1 **không** được ghi vào `lineage.md` vì là lỗi kiểm toán kỹ thuật, không phải kết quả khoa học.

`ROOT_CAUSE=UNPROVEN` · `NEW_CONFIRMATORY=NOT_EXECUTED` · `PR16=DRAFT_HOLD` · `MAIN=UNCHANGED` · `LINEAGE=UNCHANGED`.

**Bước thực hiện tiếp theo:** `TTM_T5_D01D02_EXISTING_A_REAUDIT_V2_AND_ONLY_UNRUN_B_GELU_ERF_ONCE`. Sau khi có cả hai audit, xác định điểm lệch đầu tiên và tác động trước–sau GELU. Chỉ khi cô lập được cơ chế mới khóa candidate và mở C01–C04 trên ngưỡng strict 0.001; không merge khi chưa PASS.
