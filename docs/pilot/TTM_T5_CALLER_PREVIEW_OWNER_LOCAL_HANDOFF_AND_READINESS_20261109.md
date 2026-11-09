> **Bổ sung sửa lỗi ngày 09-11-2026:** Lệnh Preview đầu tiên của owner thất bại `CallDepthOverflow` vì cả wrapper và preflight đều dùng hàm tên `Git` gọi lại `git` (PowerShell không phân biệt hoa/thường). Đã sửa thành `Invoke-TTMGit -Items/-GitArgs` với `git.exe` dạng Application. Blob wrapper đã sửa `6af5f236a4a8ef219b348c1becdefbcc2251ab0a`; blob preflight đã sửa `e79fc53233d9a3d46d3d297ac18320fb6ca6cccd`. Kết quả QA đọc nguồn PASS 18/18, PowerShell 5.1 thực thi chưa kiểm. Lượt lỗi dừng trước khi tạo Preview receipt/worktree theo kiểm tra từ xa, vì vậy không xem là Preview đã tiêu thụ. Xem `artifacts/qa/ttm-t5-parity/TTM_T5_PS51_CALL_DEPTH_OVERFLOW_REPAIR_STATIC_QA_20261109.json`.

# TTM T5 — Owner-local Preview: handoff và trạng thái sẵn sàng 2×2 (2026-11-09)

**Task** `TTM_T5_PRIOR_CALLER_OWNER_LOCAL_SOURCE_ATTESTATION_AND_NEW_2X2_SINGLE_RUN_READINESS`.

**Phán quyết hiện tại:** `REMOTE_PREVIEW=BLOCKED_MANAGED_JOB_ADMISSION`; `OWNER_LOCAL_PREVIEW=NOT_EXECUTED`; `CALLER_TYPE_K_V=UNKNOWN`; `NEW_BINARY=NOT_COMPILED`; `NEW_REFERENCE=NOT_EXECUTED`; `OWNER_RUN=HOLD`. Giữ `T5_STRICT=FAIL_7/8`, ngưỡng `0.001` và nguồn cũ.

## A. Đã thực hiện thông qua kết nối Windows — đọc-only, không chạy model

1. Đọc trực tiếp `_tmp/ttm_t5_numeric_localization_v1/build/CMakeCache.txt` và xác nhận
   `ttm_t5_layer_probe_SOURCE_DIR:STATIC=C:/Users/minht/Downloads/TTM_T5_F32_NUMERIC_LOCALIZATION_PS51_PRECLAIM_RECOVERY_V2_20261108`.
2. Liệt kê được executable probe cũ `_tmp/ttm_t5_numeric_localization_v1/build/Release/ttm_t5_layer_probe.exe`, nhưng **chưa tính được SHA-256 executable qua công cụ từ xa**. Trạng thái chỉ là `FILE_EXISTS`, không phải source/binary attestation.
3. Đọc log cũ `_tmp/ttm_t5_numeric_localization_v1/fixture_0/native_run.log`, có `FLASH_ATTN_EXT`. Log không ghi nguyên gốc `type_k/type_v`.
4. Kiểm tra `Downloads` qua kết nối remote bị từ chối với `Đường dẫn nằm ngoài workspace`. Không dùng đường tắt để vượt phạm vi.
5. Thử lệnh không phá hoại `git --version` qua `RemoteDesktop.run_command`; backend từ chối `managed mode requires task_job_submit`. Vì máy cũng chưa checkout nhánh T5 thành worktree, **không gọi/không ghi nhận bất kỳ lần chạy Preview nào**.
6. GitHub source-of-truth: nhánh `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109` chứa preflight gốc và wrapper owner-local mới. Wrapper được kiểm tra **12/12 static guards** bằng đọc lại GitHub; **chưa kiểm tra PowerShell parser/dynamic trên Windows**.

## B. Cách chạy *một lần duy nhất* trên máy của owner (PowerShell 5.1)

**Source canonical của wrapper** (GitHub blob `6af5f236a4a8ef219b348c1becdefbcc2251ab0a`):
`tools/pilot_t5/kv_flash_precision_v1/Invoke-TTM-T5-OwnerLocal-Preview-Once-PS51.ps1`.

Đọc SHA cuối của nhánh T5 từ GitHub trong câu trả lời bàn giao (không đoán HEAD). Sau đó chạy:

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$pin = '<EXACT_GITHUB_T5_HEAD_40_HEX>'
$scriptPath = Join-Path $root '_tmp\Invoke-TTM-T5-OwnerLocal-Preview-Once-PS51.ps1'
$url = 'https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/' + $pin +
       '/tools/pilot_t5/kv_flash_precision_v1/Invoke-TTM-T5-OwnerLocal-Preview-Once-PS51.ps1'
Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $scriptPath
$blob = (& git -C $root hash-object $scriptPath).Trim()
if ($blob -ne '6af5f236a4a8ef219b348c1becdefbcc2251ab0a') {
    throw 'WRAPPER_GITHUB_SOURCE_BLOB_MISMATCH'
}
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $scriptPath -ExpectedCommit $pin -ProjectRoot $root
if ($LASTEXITCODE -ne 0) { throw 'OWNER_LOCAL_PREVIEW_FAILED_CLOSED' }
```

Wrapper chỉ fetch GitHub vào project-local metadata, tạo một worktree `worktrees/ttm-t5-kvflash-preview-20261109` nếu chưa có, khớp đúng commit, xác minh GitHub blob preflight, tìm **một** file `.cpp` có SHA đã ghim **trong thư mục Downloads gốc (chỉ đọc, không sao chép)**, tính SHA binary cũ/CMakeCache/log, kiểm tra GGUF cũ, rồi gọi preflight `-Mode Preview` một lần. Không gọi compiled probe, không chạy Torch reference, không thay checkpoint, không TEST/Q1Q2, không dọn worktree.

Ghi nhận hai JSON **trong project**:
- `_tmp/ttm_t5_f32_kvflash_owner_gate_20261109/TTM_T5_KVFLASH_Preview_*.json` từ preflight;
- `_tmp/ttm_t5_f32_kvflash_owner_gate_20261109/OWNER_LOCAL_PREVIEW_SINGLE_20261109.json` từ wrapper, gồm SHA bản cũ và điểm HOLD. Marker này ngăn chạy lặp lại vô tình.

**Lưu ý:** preflight Preview được thiết kế để **HOLD** khi chưa có new candidate binary, reference hoặc checkpoint project-local. Đây là kết quả đúng; không phải lỗi để rerun. Nếu file caller không trùng SHA, không gán được K/V tĩnh hoặc bị đổi nhánh, cũng HOLD.

## C. Kiểm toán bước tiếp theo sau khi có receipt thực

Sau khi chủ máy cung cấp **chỉ** `RESULT_SHA256`, bản JSON biên bản (không chứa private checkpoints) hoặc GitHub evidence commit, phân xử một gói:
- Source caller `.cpp` SHA đúng `62fda558309502fdef9c736243b9a6194262fe0b5667949a0872fbe5c33e4de2`; khớp build-directory CMake và `type_k/type_v` không nhập nhằng; nếu caller dùng default thì ghi `DEFAULT`, không biến thành runtime attestation tuyệt đối.
- SHA old executable mới đo phải được liên kết với build receipt, không chỉ tồn tại. Đừng dùng SHA của source C++ để thay cho binary.
- New C++ candidate vẫn phải được **biên dịch đúng pinned llama.cpp**, kiểm SHA binary; 13 Python tests phải chạy thật.
- 8 logits PyTorch reference từ chính checkpoint bước 1024 phải có schema, fixture IDs và SHA; **chưa sinh trong Preview**.
- Tất cả các bằng chứng trên cần PASS, cộng một xác nhận owner cho **một batch 32 native decodes mới**. Không cấp READY khi thiếu, không tự chạy runner.

## D. Phán quyết và bảo toàn

`PREREG_2X2=FROZEN` · `HISTORICAL_STRICT=FAIL_7/8_PRESERVED` · `F32_GGUF=UNCHANGED` · `CALLER=SOURCE_PATH_FOUND_SHA_PENDING` · `OLD_EXE=EXISTS_HASH_PENDING` · `REFERENCE=NOT_GENERATED` · `NEW_BINARY=UNCOMPILED` · `WINDOWS_PREVIEW=NOT_EXECUTED_REMOTE_BLOCKED` · `OWNER_RUN=HOLD` · `MAIN=UNCHANGED` · `LINEAGE=UNCHANGED`.

**Bước thực hiện tiếp theo:** owner chạy đúng một lần script đã pin trong PowerShell 5.1 và trả JSON/RESULT_SHA256; sau đó kiểm toán gộp với binary và reference, chỉ khi đủ mới mở batch native 32 mới.
