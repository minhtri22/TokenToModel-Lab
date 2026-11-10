# TTM T5 — Phán quyết GELU_ERF (discovery) và khóa xác nhận C01–C04

Ngày: 2026-11-10  
Trạng thái: `DISCOVERY=PASS_2_OF_2` · `CONFIRMATORY_NATIVE=NOT_EXECUTED` · `PR16=DRAFT_HOLD` · `MAIN=UNCHANGED`.

## 1. Bằng chứng thực nghiệm native Windows

Nguồn chính: owner receipt `_tmp/ttm_t5_exact_root_discovery_recovery_v2_20261110/RECOVERY_V2_RECEIPT.json`, SHA256 `1f01b2991d0faae4e93c7faff8ab59cf53268f68c36085460949ff3402669bf1`.

- A `trace_only`: dùng lại chính 2 kết quả native D01/D02 của lượt đầu; không chạy lại. Audit V1 lỗi shape, giữ nguyên receipt FAIL kỹ thuật. Auditor V2 được sửa theo shape thật `[1,w]` và `[w,1,1,1]`, 8/8 unit tests Windows PASS. Audit A SHA256 `a24be0043337dc9f78a6cef0714a2fa977f823481599d238553ccb90ebe2a07f`.
- B `GELU_ERF`: MSVC build và self-check PASS, chạy đúng D01/D02 lần đầu; kiểm toán signed tensor V2 PASS. `actual_B_ERF_node_captures=2` chứng thực node `ffn_gelu_erf-0` thật, không chỉ đổi tên stage. Audit B SHA256 `ca99f1c01eb5e3c9467e05a98eeded43a84294cba4480e187ef2fb4713762ea7`; native B EXE SHA256 `61534651ec37baf622a76616aa60d152143411b4c1683790d8f1f312c28e4fb4`.
- Cùng tham chiếu P02 CPU F32 bước 1024 SHA256 `9cc5fc2db1f95e7e863a285eb279b28b7a383b81a4f890d7ec0f79b788b995e0`, checkpoint pin `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, GGUF pin `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`. Tất cả dùng KV F32, Flash OFF.

| Fixture | A GELU gốc — max abs logits | B GELU_ERF — max abs logits | B / PASS ở 0,001 |
|---|---:|---:|---|
| D01 (1 token) | 0,001790996255 (FAIL) | 0,000002861143 | PASS |
| D02 (5 token) | 0,000916451229 (PASS) | 0,000002865801 | PASS |

- Giảm sai số logits cuối: D01 **625,97×**, D02 **319,79×**.
- Điểm đầu tiên vượt ngưỡng *chẩn đoán* `1e-5` trong A trên cả hai fixture là `ffn_gelu-0`; ở B không còn điểm nào vượt `1e-5` trên các stage đã kiểm.
- Trước GELU (`inpL` → `ffn_up_b-0`), **toàn bộ thống kê signed/max/mean của A và B giống nhau** ở hai fixture (không tuyên bố từng tensor bitwise nếu chưa băm so toàn bộ).
- Stage `ffn_gelu-0`: D01 từ `6,881361239e-4` xuống `3,580413208e-7`; D02 từ `9,428212711e-4` xuống `5,942962646e-7`.
- Đối chiếu lại receipt và hai audit theo 18/18 phép kiểm chéo PASS; native A không tái chạy; B chạy đúng 2 lần (D01/D02), không TEST, không train.

**Kết luận:** Khác biệt toán tử `LLM_FFN_GELU` (đường GGML GPT-2) so với `nn.GELU()` dạng erf của PyTorch P02 là **nguồn sai số chủ đạo đã được can thiệp và chứng minh trong hai fixture khám phá**. Đã xác nhận sửa đúng hướng và giảm sai số đủ để B strict PASS 2/2.

**Giới hạn:** đây không phải PASS trên toàn miền đầu vào hay tái phân xử 8 fixture lịch sử / 32 lượt đã FAIL. Đặc biệt, trace lịch sử từng cho thấy sai khác pre-GELU ở mức chẩn đoán; điều đó không bị xóa hay phủ nhận. Kết luận root cause cho các bộ khác phải đợi phép xác nhận held-out. `lineage.md` không được cập nhật kỹ thuật; kết quả gốc `FAIL_7/8` và `FAIL_32/32` bất biến.

## 2. Khóa xác nhận độc lập bốn fixture chưa dùng

**Tiền đăng ký gốc không sửa**: Git blob `82fdd9fe716579181db648caa69170fb63d115a6`, gồm `C01` (2 token), `C02` (4), `C03` (11), `C04` (17). Các token ID đã được định sẵn trước discovery; không chọn lại theo hiệu năng.

**Tham chiếu P02 F32 thật mới khóa:** đã dùng checkpoint bước 1024 `cb985751...`, mã P02 blob `9762343...`, `torch 2.10.0+cpu`, `load_state_dict(strict=True)`. Mỗi fixture có đúng 2.048 logits finite; không training, không TEST. Chưa chạy bất cứ lượt GGML/native nào cho C01–C04.

- Tệp người dùng giữ riêng: `TTM_T5_C01_C04_P02_FP32_FROZEN_REFERENCE_20261110.zip`, SHA256 **`e5d522bd5234c46af77dbb85990779bd09e25d35be587538cec577ee486c5996`**.
- Raw JSONL bên trong: SHA256 **`dbebd9e5261ad4857b72ff16cf9383ce243dab9ca72ade5332e8325ea2c48e25`**.
- Receipt tạo reference `b1d0755a289b243c43775fc08afdc8d26c6bad8a7f751fe9557332ef924b4be5`. Raw reference derived từ checkpoint không được công khai lên GitHub; chỉ đưa vào lưu trữ riêng của owner.

### Nguồn chờ xác nhận (đã khóa trước lượt C native)

- C++ only-C01..C04, Git blob `f14f4e8eaecba273a5fe314d04e8498c40c76655`, inherited from isolated proven B `GELU_ERF`. CPU 1 thread, F32 K/V, Flash OFF, 2.048 finite logits/fixture, callback yêu cầu nút `ffn_gelu_erf-0` thật, không chạy D hoặc lịch sử.
- CMake source blob `9e829fbdc0415582a81e9d64c2b3da689cfd6b12`. **Chỉ build executable C mới**, dùng lại B llama.cpp source và các DLL/lib đã pin. Không rebuild checkpoint hoặc thay GGUF.
- Independent auditor source blob `b38c09278588c3e8bf40208cbbacf8448bfdd97e`; đọc ZIP P02 pinned, 4 native records × 2.048 logits, strict max abs `≤ 0.001` *cho từng fixture*, top-1 chỉ phụ; xác nhận 4 graph nodes `GELU_ERF` thật. FAIL khoa học vẫn lưu receipt và dừng, **không tự retry**.
- 12 unit/negative source tests trước native: `test_confirmatory_static_and_negative_cases.py`, Git blob `afad6dde4cbebddb469c71b3e7de45c2f08ef0e7`.
- Source-bound once-only runner: `run_c01c04_gelu_erf_confirmatory_once.py`; PowerShell 5.1 wrapper: `Invoke-TTM-T5-C01C04-GELU-ERF-Confirmatory-Once-PS51.ps1`. Scripts ở `tools/pilot_t5/exact_root_v1/confirmatory_v1/`.

## 3. Các cổng khoa học

`DISCOVERY_CAUSAL_PASS=2/2` **không đủ** để gỡ `MERGE_HOLD`. Cổng xác nhận:

1. Windows QA nguồn, biên dịch candidate từ source SHA ghim, self-check chính xác 4 C và runtime DLL/GELU node PASS.
2. Chạy native **một batch duy nhất 4 fixture C01–C04**, kiểm toán raw signed 2.048 logits/fixture với reference P02 F32 đã khóa, strict `max_abs≤0.001` cho **cả 4/4**.
3. Độc lập phân xử source/binary/evidence PASS, ghi nối tiếp scientific PASS hoặc FAIL vào `lineage.md` theo quy tắc và không xóa kết quả cũ.
4. Nếu C01–C04 FAIL hoặc không đầy đủ: **HOLD** PR16, giữ evidence; không sửa fixture/ngưỡng, không tự chạy lại. Nếu PASS: trình chủ dự án duyệt điều kiện merge lần cuối; **không tự merge main**.

**Bước thực hiện tiếp theo:** `TTM_T5_C01_C04_LOCKED_GELU_ERF_CONFIRMATORY_ONE_SHOT_AND_INDEPENDENT_ADJUDICATION`. Source đã stage; chưa có native C hoặc Windows QA mới.
