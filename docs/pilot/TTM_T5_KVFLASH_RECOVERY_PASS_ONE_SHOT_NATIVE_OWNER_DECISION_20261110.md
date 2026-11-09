# TTM T5 — Đóng QA chuẩn bị và phán quyết một lượt native 32 SYN mới

**Ngày:** 2026-11-10. **Phán quyết:** `TECHNICAL_READY_FOR_OWNER_DECISION`, `NATIVE_EXECUTION_NOT_AUTHORIZED_OR_STARTED`.

## 1. Đọc lại nguồn bằng chứng thật

Biên bản nhận từ owner tại `_tmp/ttm_t5_kvflash_loader_recovery_v1_20261110/RECOVERY_RECEIPT.json` SHA-256 **`2648b84558a503de66a2e2a0e09094561123d64578eefa82b26bf85fcfdc1be2`**.

Trợ lý đã đọc trực tiếp JSON và ba log từ máy Windows, đồng thời tái tính SHA-256 từ nội dung dòng CRLF nguyên bản của receipt: **khớp chính xác** SHA owner công bố. Nguồn đọc file trả về chuỗi chuẩn hóa LF và bỏ xuống dòng cuối; phép băm lại đã phục hồi CRLF cuối theo cách Python Windows đã ghi. Đây là kiểm định độc lập trên bytes đã dựng lại, không phải chỉ so sánh chuỗi SHA trong report.

| Thành phần | Bằng chứng cụ thể | Kết luận |
|---|---|---|
| MSVC build | Lần stage cũ `13_cmake_build.log`, return 0; EXE SHA256 `0da91785a0882dd1b5a04cce4dc050886b54e0fe0f17e66f66802638b3760537` | PASS |
| Synthetic unit tests | `11_synthetic_python_qa.log`, 13 test OK, return 0 | PASS 13/13 |
| Runtime dependencies | 4 DLL trong `_tmp/ttm_t2/build/bin/Release`, SHA riêng trong receipt | PASS |
| No-model self-check | `01_compiled_self_check.log`, `ttm_t5_kvflash_probe.exe --self-check`, exit 0, `model_loaded=false`, `native_inference=false` | PASS |
| Compiled constants | `02_compiled_constants.log`, return 0, `PASS_COMPILED_CONSTANTS_SCOPED`; 8 fixtures × 4 arms | PASS |
| F32 PyTorch reference | `03_independent_reference.log`, return 0, 8×2048, SHA256 `d6f367269df610a4e1c93edbff9a4dcffb7f0e0b6bd5f77247c5c90394de176c` | PASS |
| Native 2×2 | Chưa gọi chế độ model-loaded decode; `native_2x2=0_OF_32_NOT_EXECUTED` | HOLD CHỜ OWNER |

Bằng chứng nguồn: `artifacts/qa/ttm-t5-parity/TTM_T5_WINDOWS_KVFLASH_RECOVERY_PASS_INDEPENDENT_READBACK_AND_NATIVE_OWNER_GATE_20261110.json`.

## 2. Phân biệt READY với PASS khoa học

**READY kỹ thuật** chỉ có nghĩa các đầu vào, cấu hình, binary, thư viện và reference đã qua gate có thể kiểm tra *mà không thực hiện thí nghiệm*. Nó **không** cam kết S0/S1/S2/S3 đều tạo logits thành công, không cam kết dưới `max_abs 0.001`, không chứng minh K/V F16 gây 7/8 FAIL, và không sửa FAIL trước.

Cổng tiếp theo chỉ là **một quyết định của owner** để cấp quyền chạy đúng một batch 32 suy luận tổng hợp mới, không training/TEST/Q1Q2. Không cần quay lại Preview, caller supplement, biên dịch MSVC, 13 synthetic tests hoặc tạo reference.

Để tránh sinh một chuỗi permit kỹ thuật, một runner đã được ghi lên GitHub:
`tools/pilot_t5/kv_flash_precision_v1/run_exact_one_frozen_32_native_batch.py`, Git blob SHA1 **`61c1cf9c31bc3514f4982509655990110aaf56ed`**. Kiểm toán tĩnh các ranh giới khóa đã PASS **25/25**, nhưng chương trình runner chưa được thực thi/QA động.

Runner này:
- Chỉ cho phép chủ máy chủ động truyền chính xác `--approve-one-frozen-batch I_APPROVE_ONE_TTM_T5_FROZEN_NEW_32_NATIVE_BATCH`.
- Pin EXE `0da91785...`, 4 DLL hashes, GGUF F32 `5bdc904e...`, reference `d6f36726...`, recovery receipt `2648b845...`, original worktree SHA `888adde8...`, prereg blob `3b12cc1...`.
- Một tiến trình llama.cpp native duy nhất để tạo đúng 32 dòng (8 SYN × S0–S3), time limit, viết vào `_tmp/ttm_t5_kvflash_frozen_new_32_native_one_shot_v1_20261110`. Từ chối chạy lại nếu thư mục đã tồn tại.
- Chạy evaluator `audit_new_native_results.py` đóng băng, nguyên ngưỡng 0.001, ghi lại pass counts của 4 arms và log/biên bản. Kết quả **`COMPLETED_UNADJUDICATED`** chờ diễn giải khoa học; nếu ERROR hoặc partial thì `HOLD_ONE_SHOT_FAILED_OR_PARTIAL_DO_NOT_RERUN`.
- Không cập nhật `lineage.md` hoặc `main`, không thay checkpoint, không sử dụng 8 fixture lịch sử, không tự động merge PR #13.

## 3. Quyết định vận hành hiện tại

`BINARY=PASS_SHA_PINNED` · `DLL_LOADER=PASS` · `COMPILED_CONSTANTS=PASS_8X4` · `REFERENCE_F32=PASS_8X2048` · `OLD_STAGE=HOLD_PRESERVED` · `NATIVE_32=NOT_EXECUTED` · `OWNER_RUN=APPROVAL_PENDING` · `ROOT_CAUSE_EXACT=NOT_PROVEN`.

**Bước thực hiện tiếp theo:** owner chỉ cần xác nhận `Đồng ý chạy một batch 32 SYN TTM T5 mới`. Sau đó chạy đúng một lệnh owner-local trỏ vào runner GitHub đã ghim, đọc lại receipt và phán quyết kết quả 2×2. Không chạy thí nghiệm nếu chưa có owner approval.
