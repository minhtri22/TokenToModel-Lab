# TTM T5 — XÁC NHẬN KHOA HỌC C01–C04: PASS 4/4, 2026-11-10

**Phán quyết hiện hành:** `PASS_HELDOUT_STRICT_LOGIT_PARITY_4_OF_4_SCOPED_GELU_ERF`. C01/C02/C03/C04 mới tiền đăng ký đạt `max_abs≤0.001` trên đủ 2.048 logits mỗi fixture; 4/4 top-1 trùng, 4/4 node GELU_ERF xác thực. Receipt chủ dự án SHA256 `95ed3c419e42df493dc314abeb42e47afa1bf72fcb90d2c7246ff4c55d645e88`; độc lập auditor SHA256 `1d5e050e9aefbeb5720a5f86986ecbcffe2a51a8c7605d07c85467553b8b8887`; run một lần, không train hoặc TEST.

[Biên bản độc lập 4/4 PASS](../../../artifacts/qa/ttm-t5-parity/TTM_T5_C01C04_GELU_ERF_HELDOUT_STRICT_4_OF_4_INDEPENDENT_ADJUDICATION_20261110.json) · [Báo cáo khoa học và review merge](../../../docs/pilot/TTM_T5_GELU_ERF_C01C04_HELDOUT_STRICT_PASS_INDEPENDENT_ADJUDICATION_AND_PR16_MERGE_REVIEW_20261110.md).

**Quan trọng về nguồn/merge:** Kết quả PASS này áp dụng cho binary **llama.cpp được patch GELU_ERF ở checkout tách biệt**, CPU, KV F32, Flash OFF. PR #16 chứa mã chẩn đoán tạo bản patch và chứng cứ, **không tự cập nhật llama.cpp production hoặc làm model GGUF gốc tự tương thích**. Source V1 lỗi cú pháp và auditor V1 lỗi shape được giữ để truy vết, tuyệt đối không tái chạy; recovery V2 cũng là one-shot đã tiêu thụ, không dùng chạy lại. Đối với source production, cần áp dụng/đóng gói sửa GELU riêng theo quy trình phát hành, không đánh đồng merge research với triển khai runtime.

**`SCIENCE=PASS_4/4` · `PR16=DRAFT_HOLD_FINAL_SOURCE_REVIEW_AND_OWNER_DECISION` · `MERGE=NOT_EXECUTED`**. L0013 FAIL 32/32 bất biến; L0014 PASS mới được nối tiếp trong `lineage.md`, không thay thế FAIL cũ.

---

# C01–C04 2026-11-10 — SỬA LỖI CÚ PHÁP TRƯỚC NATIVE, CHƯA TIÊU THỤ ONE-SHOT

**Không chạy lại launcher V1** `Invoke-TTM-T5-C01C04-GELU-ERF-Confirmatory-Once-PS51.ps1`: checker trong V1 mắc `SyntaxError: unmatched ')'` tại dòng 99 và đã dừng trước mọi phép native C01–C04. Source lock V1 và lỗi được giữ nguyên; `main`, TEST và `lineage.md` không đổi. Sửa chính xác dấu ngoặc và pin SHA trong source mới.

**Dùng duy nhất** `tools/pilot_t5/exact_root_v1/confirmatory_v1/Invoke-TTM-T5-C01C04-Confirmatory-SourceRecovery-V2-PS51.ps1`. V2 kiểm đủ 5 blob V1, chép ba file không thay đổi vào một source lock V2 mới, tải hai file sửa đúng Git SHA, kiểm cú pháp và chạy 12 negative tests **trước khi** tạo thư mục thực thi native one-shot. Chỉ chạy C01–C04 trên nguồn đã khóa khi toàn bộ các cổng trước native PASS.

[Biên bản kỹ thuật fail-closed và phục hồi V2](../../../artifacts/qa/ttm-t5-parity/TTM_T5_C01_C04_PRE_NATIVE_SYNTAX_FAIL_CLOSED_AND_SOURCE_RECOVERY_V2_20261110.json).

**`C_CONFIRMATORY_NATIVE=NOT_EXECUTED` · `MERGE=HOLD` · `PR16=DRAFT`**.

---

# TTM T5 — CẬP NHẬT DISCOVERY GELU_ERF 2026-11-10

**Kết quả mới nhất:** `GELU_ERF_CAUSAL_DISCOVERY=PASS_2_OF_2`, trên fixture mới D01/D02. Trước GELU các thống kê tensor không đổi giữa đối chứng A và B; A có chênh lệch đầu tiên >1e-5 tại `ffn_gelu-0`; B chỉ thay toán tử thành `GELU_ERF`, giảm max-abs logits D01 626×, D02 320× và đạt strict `≤0.001` 2/2. **Chưa có confirmatory native C01–C04**, vì vậy **`PR16=DRAFT_HOLD`, `MERGE=BLOCKED`**. Không được coi discovery PASS là PASS trên các 8 fixture lịch sử hoặc 32 phép đo cũ, đều giữ nguyên FAIL.

- [Báo cáo khám phá và nguồn xác nhận đã khóa](../../../docs/pilot/TTM_T5_D01D02_GELU_ERF_CAUSAL_DISCOVERY_AND_C01C04_CONFIRMATORY_FREEZE_20261110.md)
- [Biên bản khoa học discovery đã kiểm toán](../../../artifacts/qa/ttm-t5-parity/TTM_T5_D01D02_TRUE_GELU_ERF_FIRST_OPERATOR_SCOPED_CAUSAL_DISCOVERY_PASS_20261110.json)
- [Bằng chứng QA trước confirmatory 46/46](../../../artifacts/qa/ttm-t5-parity/TTM_T5_C01_C04_CONFIRMATORY_FROZEN_SOURCE_46_46_STATIC_QA_AND_RUN_HOLD_20261110.json)

Bốn fixture C01–C04, reference PyTorch F32 và source ứng viên `GELU_ERF` đã khóa SHA; không chạy confirmatory cho đến khi owner thực thi batch one-shot, kiểm định độc lập và phân xử khoa học. Các báo cáo MERGE/HOLD cũ bên dưới là lịch sử và không thay thế lệnh owner **chỉ merge khi strict PASS**.

---

# OWNER_OVERRIDE_2026_11_10 — MERGE HOLD CHỜ XÁC ĐỊNH NGUYÊN NHÂN VÀ STRICT PASS

**Quyết định có hiệu lực mới nhất của owner:** `PR16=DRAFT_HOLD` · `MERGE=BLOCKED` cho tới khi **nguồn sai số được chứng minh bằng can thiệp nhân quả** và **một kiểm định strict logits mới đạt PASS ở ngưỡng 0,001**. QA nguồn PASS, top-1 PASS và Git mergeable **không đủ** để merge.

**Đã xác minh tĩnh:** `nn.GELU()` PyTorch P02 (erf) không trùng lựa chọn `LLM_FFN_GELU`/ `ggml_gelu` của GPT-2 GGML; nhưng trace lịch sử đã có khác biệt trước GELU tại `ffn_inp-0`, do vậy chưa được quy cho một nguyên nhân duy nhất. Trạng thái `ROOT_CAUSE=UNRESOLVED`.

**Quyết định MERGE của biên bản review trước chỉ có giá trị lịch sử, đã bị owner phủ quyết**. Xem [bản khóa mới](../../../docs/pilot/TTM_T5_PR16_OWNER_HOLD_EXACT_CAUSAL_ROOT_STRICT_PASS_PROTOCOL_20261110.md). Không chạy lại 8 fixture cũ hoặc 32 phép đo mới đã tiêu thụ; giữ nguyên FAIL 7/8 và FAIL 32/32 cùng `lineage.md` L0013.

---

# CẬP NHẬT 2026-11-10 — Kết quả one-shot T5 đã phân xử

**Kết quả mới nhất:** `NATIVE_32=EXECUTED_ONCE_PASS_PROTOCOL` · **`STRICT_LOGITS=FAIL_32_OF_32`** · `TOP1=PASS_32/32` · `EXACT_ROOT_CAUSE=UNRESOLVED`. Đây là kết quả khoa học âm tính hợp lệ: thay đổi riêng F16/F32 KV cache và Flash ON/OFF **không đủ** đạt strict parity `max_abs≤0.001`. Không chạy lại 32; giữ nguyên strict FAIL lịch sử 7/8. Chủ dự án chỉ yêu cầu **xem xét merge**, chưa cho phép merge main.

**Nguồn thẩm định hiện hành:** [báo cáo khoa học FAIL và rà soát merge](../../../docs/pilot/TTM_T5_FROZEN_32_NATIVE_NEGATIVE_SCIENCE_ADJUDICATION_AND_MERGE_REVIEW_20261110.md), [biên bản phân xử 32](../../../artifacts/qa/ttm-t5-parity/TTM_T5_FROZEN_32_NATIVE_STRICT_PARITY_NEGATIVE_SCIENCE_ADJUDICATION_20261110.json), mục `L0013` trong `lineage.md` (append-only). Raw 32 JSONL và các log giữ ở `_tmp/ttm_t5_kvflash_frozen_new_32_native_one_shot_v1_20261110` trên Windows; SHA được pin trong biên bản.

**Lưu ý khi review merge:** Phần README từ tiêu đề `DESIGN_ONLY` trở xuống là **ảnh chụp thiết kế gốc tại thời điểm đóng băng**, các chữ `chưa chạy/chưa biên dịch/OWNER APPROVAL NOT ISSUED` trong phần lịch sử **không còn là trạng thái hiện tại**. Các script preview/supplement gốc được bảo toàn để tái dựng lịch sử kỹ thuật, **không phải runner khuyến nghị**. Bộ chạy final one-shot đã tiêu thụ, không chạy lại. Trường `descriptive_contrasts` chỉ trừ số max-abs error giữa các arm, không phải 2×2 per-logit causal attribution.

---

# TTM-T5 KV F16/F32 × Flash ON/OFF — single synthetic discrimination (DESIGN_ONLY)

**Ngày khóa:** 2026-11-09 · **Source of truth:** nhánh GitHub `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109`. **Không phải giấy phép chạy native.** Mọi nội dung ở đây là mã ứng viên chưa được biên dịch hoặc chạy trên máy đích.

## 1. Bất biến tuyệt đối

- Không mở TEST/Q1Q2, không TRAIN, không đổi checkpoint T4 1024, trọng số GGUF F32, mã P02, llama.cpp pinned; không sửa/xóa 8 fixtures hay báo cáo FAIL 7/8 lịch sử.
- Model step1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; GGUF SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`.
- P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; llama.cpp `372dc5ca157276beb6c67b2e92477e8d662e964a`. Đúng bản `llama.h` có `type_k`, `type_v`, `flash_attn_type`, và enum ENABLED/DISABLED.
- Ngưỡng strict logits cố định **0.001** (max-abs vs checkpoint F32-P02); chỉ dùng trên **8 fixtures mới** trong đo mới. Bằng chứng T5 cũ **FAIL 7/8** không bị hồi tố sửa thành PASS.

## 2. Thiết kế đã niêm phong

Canonical: [PREREG JSON](../../../artifacts/qa/ttm-t5-parity/TTM_T5_KV_FLASH_2X2_FRESH_SYNTHETIC_PREREG_20261109.json).

- Fixture IDs: `SYN01..SYN08` có độ dài 1,2,4,6,9,12,20,31; các ID cụ thể đã ghim trong JSON, không trùng **nguyên chuỗi** với 8 fixtures cũ và không phải dữ liệu TEST.
- Arms: `S0=F16/Flash ENABLED`, `S1=F32/Flash DISABLED`, `S2=F32/Flash ENABLED`, `S3=F16/Flash DISABLED`. **Cả bốn arm là bắt buộc** để tách yếu tố cache khỏi flash (2×2).
- Tối đa **32 phép decode** (8×4) trong **một lượt độc lập**, 2048 logits cho mỗi phép đo. Mỗi phép tạo context mới, threads=1, CPU-only, không sampling, context 256, n_batch/n_ubatch 256.
- Reader tham chiếu PyTorch F32 chạy **riêng trên cùng checkpoint**, 8 dãy synthetic mới; SHA tệp và Torch/P02 version được ghim trước khi phân tích.
- S0 được đặt tên **old-like**, KHÔNG được nhận là tái hiện chính xác đường cũ khi chưa chứng thực được `type_k/type_v` từ mã caller đã build lần trước.
- Kiểm tra trace flash **theo toán tử thật** bằng `cb_eval`, không chỉ tin vào lời khai cấu hình. Nhánh Flash ON phải thấy `FLASH_ATTN_EXT`; OFF phải bằng 0.

### Phân tích dự kiến (không phải khoa học PASS)

`E(S)` = max-abs logits so với P02 F32, cùng fixture. So sánh `S3−S1` (KV effect khi Flash OFF), `S2−S1` (Flash path khi KV F32), `S0−S3` (Flash path khi KV F16). Tương tác 2×2 được báo cáo mô tả. Bản Flash có thể **cast K/V F32 thành F16** dù chọn cache F32; do đó S2 không đảm bảo đường attention F32 toàn phần.

Nếu S1 cũng FAIL >0.001, chưa kết luận F16 là nguyên nhân đầy đủ; cần xét matmul/projection/residual. Nếu S1 cải thiện, đối chiếu S2/S3 để phân biệt. **Không nâng ngưỡng 0.001 để lấy PASS.**

## 3. Trình tự hữu hạn khi chủ dự án cấp quyền sau

1. **Owner Preview:** xác minh CMakeCache của probe lịch sử chỉ tới `C:\Users\minht\Downloads\TTM_T5_F32_NUMERIC_LOCALIZATION_PS51_PRECLAIM_RECOVERY_V2_20261108`. Giao `-OriginalCallerSource` là **file C++ chính xác** trong thư mục đó (chỉ đọc từ Downloads, không copy/upload source ra GitHub). Kiểm SHA, các phép gán `type_k/type_v`, `flash_attn_type` và bằng chứng build; nếu thiếu/không khớp → `HOLD`.
2. Chuẩn bị worktree riêng **nằm trong chính project root**, ghim commit GitHub; không sửa `main`. Cần đúng checkpoint và GGUF bản gốc đã ghim **trong project**, không lấy từ TEST hay ghi dữ liệu ngoài project.
3. **Source-only QA:** Python 3.12 chạy `test_kvflash_protocol.py` trên fixtures mô phỏng; sau đó xác minh biên dịch ứng viên trong **worktree** bằng đúng pinned Windows MSVC libs. Chưa khởi chạy native.
4. Chuẩn bị F32 PyTorch reference bằng `f32_p02_reference_candidate.py` sau khi các input sha đều đúng; ghi file mới trong project, tuyệt đối không overwrite. Đây là inference **mới** trên các ID synthetic, không phải training/test.
5. PowerShell 5.1 `Invoke-TTM-T5-KVFlash-OwnerPreflight-PS51.ps1 -Mode OwnerGate` chỉ cấp trạng thái `READY_FOR_ONE_NEW_SYNTHETIC_BATCH_NOT_EXECUTED` nếu **toàn bộ** pin, source caller, binary SHA, reference, owner signoff đều đạt. Chính script **không gọi native runner**. Dùng một quyết định owner tổng hợp, không chia cấp phép kỹ thuật vi mô.
6. **Chỉ sau khi owner phê duyệt thực thi**, gọi ứng viên C++ đúng một lần để sinh 32 bản ghi JSONL trong project; lập tức pin SHA256 của output thô, rồi `audit_new_native_results.py` trên cùng reference và prereg. Kiểm toán độc lập FAIL/PASS theo bằng chứng và ghi GitHub. Khi kết quả không xác minh được, HOLD, không chạy lại one-shot tự động.

### PowerShell để xem trước, chưa chạy model

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
# Đã checkout/fetch nhánh ở worktree dự án; tuyệt đối không dùng main để sửa.
$worktree = Join-Path $root '.worktrees\ttm-t5-kvflash-20261109'
$script = Join-Path $worktree 'tools\pilot_t5\kv_flash_precision_v1\Invoke-TTM-T5-KVFlash-OwnerPreflight-PS51.ps1'
# Người dùng cần cung cấp đường dẫn chính xác của source C++ caller gốc từ CMakeCache.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -Mode Preview `
    -ProjectRoot $root -WorktreePath $worktree
if ($LASTEXITCODE -ne 0) { throw 'T5_PREVIEW_SCRIPT_FAILED' }
```

**Preview** thường sẽ báo HOLD vì chưa cung cấp bản source caller, checkpoint, reference và binary mới. Đây là kết quả đúng; không có execution.

### Những mã đã chuẩn bị

- `ttm_t5_kvflash_probe_candidate.cpp`: 32 calls native, output logits F32 và counter FlashAttention; **chưa biên dịch/chạy**.
- `CMakeLists.txt`: cấu hình Windows x64 MSVC, header/libs từ đúng pinned llama.cpp.
- `f32_p02_reference_candidate.py`: đọc đúng checkpoint P02 F32 để tạo 8 logits tham chiếu; **chưa chạy**.
- `audit_new_native_results.py`: phân xử 32 arm vs 8 ref, cờ vượt ngưỡng, counters, tương tác; **chưa có dữ liệu thật**.
- `test_kvflash_protocol.py`: 13 test dương/âm synthetic (không load trọng số).
- `Invoke-TTM-T5-KVFlash-OwnerPreflight-PS51.ps1`: kiểm toàn bộ điều kiện và tạo receipt nội bộ, **không gọi native**.

## 4. Trạng thái chặn và bàn giao

`CALLER_SOURCE_CONFIG=HOLD_NOT_ATTESTED` · `NATIVE_CANDIDATE=SOURCE_ONLY_UNCOMPILED` · `REFERENCE=NOT_EXECUTED` · `OWNER_RUN_APPROVAL=NOT_ISSUED`. Đây là **một** gate tổng hợp, không yêu cầu nhiều permit nhỏ.

**Bước thực hiện tiếp theo:** xác minh nguyên vẹn file C++ caller lịch sử qua owner-local Preview, rồi một lần thẩm định source/compiled binary/reference có SHA để xác định có thể mở một lượt native 2×2 hay không. Không tự động chạy khi chỉ mới nhận status Preview.
