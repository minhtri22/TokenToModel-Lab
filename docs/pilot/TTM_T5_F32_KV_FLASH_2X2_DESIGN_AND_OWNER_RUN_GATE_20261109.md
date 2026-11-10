# TTM-T5: KV F16/F32 × FlashAttention — thiết kế 2×2 và cổng chạy của owner

**Thời điểm:** 2026-11-09. **Phạm vi:** `TTM_T5_F32_KV_FLASH_PRECISION_SINGLE_SYNTHETIC_DISCRIMINATION_DESIGN_AND_OWNER_RUN_GATE`.  
**Source of truth:** GitHub, nhánh `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109` từ main `b57b44e7287f842e81050c1faee337f636333dd0`. Không chỉnh nguồn/weight/checkpoint, không TEST hoặc training.

## Tình trạng đã xác minh

1. 8 fixtures đã tiêu thụ vẫn là `T5_STRICT_LOGITS=FAIL_7/8`, threshold **0.001**, max |Δlogit| **0.003362178805176086**, top-1 8/8 trùng. **Không thực hiện replay**.
2. Đầu vào `inpL` của trace gốc khớp. Lệch đầu tiên vượt 1e-5 tại `ffn_inp-0` trong 8/8 fixture; vùng attention output + residual, chưa cô lập toán tử.
3. Native log cũ `_tmp/ttm_t5_numeric_localization_v1/fixture_0/native_run.log` có `FLASH_ATTN_EXT`. CMakeCache ghi mã caller build tại `C:/Users/minht/Downloads/TTM_T5_F32_NUMERIC_LOCALIZATION_PS51_PRECLAIM_RECOVERY_V2_20261108`. **Đường dẫn đó nằm ngoài RemoteDesktop workspace**, nên không đọc được toàn bộ C++ caller cũ và **không thể khẳng định** runtime `type_k/type_v` gốc.
4. Source llama.cpp ghim `372dc5ca157276beb6c67b2e92477e8d662e964a` đặt default `type_k=F16`, `type_v=F16`, Flash AUTO; nhánh FlashAttention có thể cast K/V F32→F16. Đây là **giả thuyết định lượng cần đối chứng**, không mặc nhiên là bug.

## Thiết kế mới được khóa

**[Tiền đăng ký JSON chính thức](../../artifacts/qa/ttm-t5-parity/TTM_T5_KV_FLASH_2X2_FRESH_SYNTHETIC_PREREG_20261109.json)**: 8 fixture SYN01–SYN08 mới, chiều dài token (1,2,4,6,9,12,20,31), không trùng 8 chuỗi token lịch sử; 4 điều kiện chạy trong **một** batch 32 decode, mỗi decode context mới.

| Arm | KV K/V | Flash | Vai trò |
|---|---|---|---|
| S0 | F16/F16 | ON | Giống đường cũ về lý thuyết, **không tự nhận exact historical** |
| S1 | F32/F32 | OFF | Đường hạn chế ép F16 |
| S2 | F32/F32 | ON | Tách ảnh hưởng Flash khi storage KV F32 |
| S3 | F16/F16 | OFF | Tách ảnh hưởng KV khi Flash OFF |

Lưu ý: Flash ON vẫn có thể ép K/V sang F16. Vì vậy đối chiếu là *đường thực thi* chứ không đơn thuần là thay một kiểu dtype độc lập.

Tất cả giữ nguyên checkpoint 1024 SHA `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; GGUF SHA `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`; P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`. Ngưỡng đầy đủ vẫn **0.001**, không sửa vì kết quả.

## Hiện vật sẵn có và cổng chưa đạt

- [Ứng viên native, PyTorch F32 oracle, phân xử output và 13 negative/positive QA](../..//tools/pilot_t5/kv_flash_precision_v1/README_VI.md), tất cả đều ở trạng thái source-only, **không biên dịch hoặc thực thi trên Windows**.
- [PowerShell 5.1 Owner Preview](../../tools/pilot_t5/kv_flash_precision_v1/Invoke-TTM-T5-KVFlash-OwnerPreflight-PS51.ps1) kiểm tra exact source pin, CMake source dir, caller C++ SHA, các phép gán context, checksum GGUF/checkpoint, branch, binary và reference; **không gọi binary**.
- [QA nguồn 33 điều kiện](../../artifacts/qa/ttm-t5-parity/TTM_T5_KVFLASH_2X2_DESIGN_STATIC_QA_AND_OWNER_GATE_HOLD_20261109.json): `PASS_33/33_STATIC`, không phải Python unit tests đã chạy, không phải PyTorch/native parity QA.

**Cổng chặn hiện tại:** `HOLD_CALLER_PARAM_PROVENANCE` và `HOLD_UNCOMPILED_CANDIDATE` — người dùng cần thực hiện Preview đọc-only bằng PowerShell trên máy local từ đúng tệp C++ caller trong Downloads, lưu receipt vào `D:/WORK/RESEARCH/TokenToModel-Lab/_tmp`, sau đó xác nhận build artifact + source pins + một phê duyệt owner cho batch 32 mới. Preview không cho phép tạo inference.

**Không được:** dùng 8 fixture cũ; chạy thêm GPU/Colab; thử TEST/Q1Q2; sửa `0.001`; ghi lại T5 legacy PASS; merge PR13; sửa `lineage.md`. Ghi FAIL thực tế nếu kiểm thử mới thất bại.

## Bước thực hiện tiếp theo

`TTM_T5_PRIOR_CALLER_OWNER_LOCAL_SOURCE_ATTESTATION_AND_NEW_2X2_SINGLE_RUN_READINESS`

Chủ dự án dùng PowerShell Preview xác nhận tệp source caller gốc và `type_k/type_v`. Khi có nhận diện SHA nguồn chính xác mới thẩm định lại source/compile/ref/binary một lần, quyết định `READY/HOLD`. Không khởi chạy batch mới trong bước thiết kế hiện tại.

**Phán quyết:** `PREREG=FROZEN` · `STATIC_QA=PASS_33/33` · `CALLER_KV=UNKNOWN` · `OWNER_RUN=HOLD` · `NEW_NATIVE_DECODE=0/32` · `PYTORCH_REFERENCE=NOT_EXECUTED` · `TRAIN=NO` · `TEST=UNTOUCHED` · `HISTORICAL_T5_STRICT=FAIL_7/8_PRESERVED` · `MAIN=UNCHANGED` · `LINEAGE=UNCHANGED` · `PR13=HOLD`.
