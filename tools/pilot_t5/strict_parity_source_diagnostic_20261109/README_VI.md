# TTM T5 — Bộ chẩn đoán strict logits F32 chỉ đọc (không rerun)

Nguồn chuẩn tại GitHub: nhánh `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109`.

## Mục đích

Phân tích lại **biên bản sẵn có**, giữ nguyên `T5_STRICT_LOGITS=FAIL_7/8`, không chạy lại T5 native one-shot, không đọc TEST/Q1Q2, không tải/re-export checkpoint, không chạy huấn luyện hoặc Ollama. Có thêm một thí nghiệm **số học tổng hợp** chỉ để kiểm tra cơ chế sai số F16 trong phép chiếu V.

## Cách dùng trên Windows (PowerShell 5.1)

Chỉ **đọc** trong workspace dự án, in stdout. Không viết vào C: root và không ghi đè các receipt cũ.

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$folder = Join-Path $root 'tools\pilot_t5\strict_parity_source_diagnostic_20261109'
$trace = Join-Path $root 'evidence\pilot\t5-trained\T5_F32_NUMERIC_LOCALIZATION_UNADJUDICATED.json'
if (-not (Test-Path -LiteralPath $py) -or -not (Test-Path -LiteralPath $trace)) {
    throw 'PYTHON_OR_TRACE_NOT_FOUND'
}
& $py (Join-Path $folder 'test_trace_diagnostic.py')
if ($LASTEXITCODE -ne 0) { throw 'SYNTHETIC_TEST_QA_FAILED' }
& $py (Join-Path $folder 'diagnose_existing_trace.py') $trace
if ($LASTEXITCODE -ne 0) { throw 'TRACE_RECHECK_FAILED' }
```

Câu lệnh bổ sung *tùy chọn* (không có checkpoint):

```powershell
& $py (Join-Path $folder 'synthetic_f16_v_projection.py')
if ($LASTEXITCODE -ne 0) { throw 'SYNTHETIC_DEMO_FAILED' }
```

Để xác nhận log gốc **mà không chạy lại native binary**:

```powershell
$log = Join-Path $root '_tmp\ttm_t5_numeric_localization_v1\fixture_0\native_run.log'
if (-not (Test-Path -LiteralPath $log)) { throw 'ORIGINAL_LOG_MISSING' }
(Select-String -LiteralPath $log -Pattern 'FLASH_ATTN_EXT').Count
```

## Các mốc bắt buộc

- Checkpoint 1024 SHA `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- Trained GGUF F32 SHA `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`.
- llama.cpp pinned `372dc5ca157276beb6c67b2e92477e8d662e964a`.
- Ngưỡng full logits `0.001`, 7/8 FAIL được bảo toàn.
- Read-only QA: `artifacts/qa/ttm-t5-parity/TTM_T5_STRICT_F32_SOURCE_TRACE_AND_FLASH_KV_QA_20261109.json`.
- Diễn giải kỹ thuật: `docs/pilot/TTM_T5_F32_STRICT_LOGIT_PARITY_ROOT_CAUSE_DIAGNOSTIC_20261109.md`.

## Ranh giới khoa học

PASS unit tests không phải PASS native parity. Default KV cache F16 và FlashAttention casting F32→F16 là **đường tính toán hợp lệ**, không mặc nhiên là bug. Log cũ xác nhận `FLASH_ATTN_EXT` có được dùng, nhưng **không ghi rõ giá trị params.type_k/type_v tại native caller**. Tìm nguyên nhân chính xác cần đối chứng mới được xác thực, trước khi kết luận `ROOT_CAUSE_PROVEN`.

**Bước thực hiện tiếp theo:** chuẩn bị một batch mới sử dụng fixture synthetic mới, với khác biệt duy nhất `KV F16/Flash ON` vs `KV F32/Flash OFF`, và chỉ thực thi nếu quyền native được mở riêng. Không lách one-shot cũ.
